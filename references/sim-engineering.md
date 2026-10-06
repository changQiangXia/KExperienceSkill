# 模拟赛 / RL 工程手册（外部来源蒸馏）

> 来源：[kei-kochiya/kaggle-skills](https://github.com/kei-kochiya/kaggle-skills)（MIT）的
> `kaggle-rl-simulation` 技能与 `Handbook/reinforcement-learning/`（Kaggriculture / Orbit Wars / Maze Crawler /
> simulation-competition-starter）。数字为原文自述的**历史样例**，换游戏/硬件必须重新测量。
> 案例级深讲见 [case-books/sim-agent.md](case-books/sim-agent.md)（kore/lux/pokemon/neurogolf 等）。

## 0. 先选路线：启发式、搜索、BC、RL 都能赢

- **Maze Crawler 反例**：1st 是启发式 BFS（jump-aware + arrival-time `sbd` 计分），3rd 才是 PPO 自对弈——
  说明"更重的 RL"不是默认答案；同场总结的 **Homogeneous Self-Play Trap**（纯自对弈产生"刷能量"盲区）是经典坑。
- 选型表（来自其 starter）：规则/录像已能打 → 改进启发式或 BC；短视野规划便宜 → 有界搜索；
  好教师+稀疏奖励 → 小 BC + 完整对局验证，再上 RL 探针；动作简单奖励信息量大 → 直接 RL。
- **合同先行**：先跑通官方 starter 一整局，记录 replay/延迟/终局；对局语义（非法动作、执行顺序、随机性）钉死后再谈训练。

## 1. 模拟器加速（先测量，再动引擎）

优先级（低 → 高）：

1. 基线：官方 Python 引擎约 **50–200 steps/sec**；
2. 原生重写（Rust PyO3 / C++ pybind11）+ 融合 `step-obs-reset` 循环、预分配内存、去 GC 抖动；
3. 算法剪枝：AABB 宽相位过滤、分段线性扫掠碰撞、整数 ID 几何；
4. 向量化多线程（Rayon / OpenMP / JAX）与零拷贝 pinned 内存；
5. JAX `lax.scan` + 单次 `jit` 把 rollout+SGD 编进一张图，单卡可达"数十万 steps/sec"级（原文自述）。

**硬要求：parity harness**——拉官方 tournament 对局 JSON，逐步重放，与新引擎做 bit-for-bit 对比；
吞吐收益必须大于重写成本（先 profile：模拟 / 编码 / 推理 / 传输 / 更新分别测）。

## 2. 网络架构（多实体、可变数量、部分可观测）

- **统一多实体注意力** + 全局 scratch token（汇总全局信息）；实体/关系分别编码（relational edge attention）。
- **单次多玩家前向**：一 pass 评估 2–4 个玩家（原文称 2–4× 加速），但要严格隔离每个玩家的私密观测——
  共享 pass 不能泄露他人私有信息。
- **多头动作解耦**：Bernoulli 发射头 + scaled dot-product 目标注意力头 + **截断离散 logistic 混合头**
  （连续动作参数化）；多玩家 value head 用 softmax 语义。
- 空间任务可加 **2D RoPE**；小模型（2M–5M）在推理成本敏感的场景可与 50M+ 模型竞争（原文自述）。

## 3. 训练稳定性与联赛

- PPO 参考配置（原文"gold standard"，按游戏重测）：rollout 64；`n_envs` 2048–8192；**PPO epochs=1**（多智能体易过拟合近期数据）；
  clip 0.20；GAE λ=0.95；γ 按任务（固定赛季 Kaggriculture 用 1.0）；lr 1e-4 → 1e-5（10M warmup + cosine）；
  Muon（大 2D 注意力矩阵）+ AdamW（embedding）；entropy 0.01 → 0.001 退火；teacher KL 0.10。
- **联赛对局**：2 人零和也非传递（石头剪刀布），minimax 不保证自对弈收敛；对手池要含历史策略/启发式/exploiter。
- **checkpoint promotion**：教师/学生用明确的晋级规则（胜率、对局数、回归保护），避免"自我感觉良好"式晋级。
- 常见坑：折扣因子与停摆 bug（stalling）、动作 mask 策略性过滤、BC warm-start 后直接切 RL 的分布断裂。

## 4. 提交与部署（<100MiB、CPU、1s 级）

- **NF4-LSQ 分组量化**：200M 参数 fp32（约 800MiB）→ **90.7MiB** artifact（group 128 + 最小二乘 refinement）；
  5M fallback 模型 fp16 → 10.1MiB；打包 <100MiB。
- **流式反量化**：逐张量加载，避免一次性 materialize 800MiB state-dict（防 OOM）。
- **动态 int8**：`torch.ao.quantization.quantize_dynamic(..., torch.qint8)` 把 CPU 单步延迟 2500ms → 450ms（原文自述）。
- **断路器兜底**：监控 `obs["remainingOverageTime"]`，超支风险时自动切 5M fallback；观测压缩（如过滤舰队 <3 艘）。
- 打包前本地过：入口脚本、依赖、目标文件名、CPU 预算；本地跑通 ≠ 官方运行时通过（时间口径可能不同）。

## 5. 开赛 48 小时清单（可裁剪）

- [ ] 规则/源码/配置/提交约束读完并记录版本
- [ ] 官方 starter 或启发式打完整局 + 保存 replay 与延迟
- [ ] 可复现评估器（多对手家族、换座、留出场景面板）
- [ ] 分别测模拟/编码/推理/传输/更新成本，外推墙钟
- [ ] 最后一步：最小提交包本地验证（入口/依赖/大小/超时）

## 链接索引（来源佐证）

- 来源仓库：https://github.com/kei-kochiya/kaggle-skills （MIT）
- 新赛 kickoff：https://github.com/kei-kochiya/kaggle-skills/blob/main/Handbook/reinforcement-learning/simulation-competition-starter.md
- 模拟器加速：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-rl-simulation/references/simulator_acceleration.md
- 网络架构：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-rl-simulation/references/model_architectures.md
- 训练稳定性/联赛：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-rl-simulation/references/rl_training_stability.md
- 量化与部署：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-rl-simulation/references/submission_quantization_serving.md
- Kaggriculture（BC→PPO）：https://github.com/kei-kochiya/kaggle-skills/blob/main/Handbook/reinforcement-learning/kaggriculture.md
- Maze Crawler（启发式胜 RL）：https://github.com/kei-kochiya/kaggle-skills/blob/main/Handbook/reinforcement-learning/maze-crawler.md
