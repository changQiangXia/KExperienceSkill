# 用编码 Agent 打 Kaggle（vibe coding → agentic engineering）

> 定位：这是**生产工程层**，不是决策层。人负责路线、验收与合规；agent 负责实现、实验与记录。
> 证据来源：KStarter 264 场深读（Tier A/B）+ 50 名 GM 断言层；每个数字都带 slug 与 topic，自述证据单独标注。
> 配套：[assets/agent_spec_template.md](../assets/agent_spec_template.md)（任务规格模板）、
> [assets/agent_workflow_checklist.md](../assets/agent_workflow_checklist.md)（开跑/收官检查清单）。

## 0. 三条硬结论

1. **vibe coding 换的是速度，不是判断。** 2026 赛季的冠军级用法是"人写规格与验收，agent 写全部代码"：
   s6e3 冠军 60 万行代码全由 LLM 写（850 模型、4×A100），但路线仍是人定的（"人类定 playbook + agent 执行"）。
2. **合规是红线，不是风险提示。** birdclef-2026 第 101 名用 Claude Code 搭全自动求解器（自动实验 + 邮件授权提交），**被取消资格**；
   同场裁决给出的安全区是"**人做 idea + agent 做工程**"。
3. **agent 的增益必须过同折对照与泄漏审计。** rogii 的教训是 agent 会把公开代码/数据划分不一致变成泄漏（7th 明确记录）；
   s6e2 的 ChatGPT 全自动方案（69th）赛后复盘发现一个模型的目标编码在 KFold 外计算，剔除后私榜反而更好（top20）。

## 1. 决策表：你的场景 → 拓扑

| 你的场景 | 推荐拓扑 | 先决条件 | 证据 |
| --- | --- | --- | --- |
| 单场代码密集 / 迁移往届脚本 / 补公开 notebook | **T1 单 agent 会话** | 规格清楚、可回滚、人工复核提交 | s6e4 2nd：Claude Code 一天迁移 150+ 脚本 → 第 3 天私榜第一（0.98160） |
| 需要大量并行实验（FE/调参/多样性） | **T2 双 agent 竞争** 或 **T4 调度器+worker** | GPU 常开、本地排行榜文件、事务门 | s6e8 1st：单 agent 4 天 380 模型 → 双 agent 对战产出单模夺冠；s6e5 2nd：Codex 自主循环 218 模型 |
| 代码高尔夫 / 程序合成 / 有自动评估器 | **T3 群体并行采样** | 可自动打分、沙箱隔离 | code-golf 2025 4th：98% 代码 LLM 生成，每轮 N=4 并行取最短有效 |
| 需要"新范式"洞察（不是调参） | **人主导 + agent 侦察** | 讨论区/论文检索能力、2 小时级分包 | s6e8 1st 用 ChatGPT Pro 并行"数据包"发现新 FE；s6e3 的 FE 清单来自 LLM 研究 |
| 评审制 / hackathon（产品+叙事） | 人主导叙事，agent 做产品 | rubric 透明、提交链路可验证 | gemini-3：评审延期、AI 评委信任危机；"wow factor" 优先于技术深度 |
| 规则禁止自动化提交 / 要求披露 | **禁用自动链路**，只留人审 | 先读规则与 FAQ | birdclef-2026 101st 被取消资格（48 票帖） |

> 通用前提：agent 提速的是"局部迭代"；**路线判断、配额与最终提交永远归人**（KStarter `playbook/00-通用方法论.md` §10.5）。

## 2. 四种拓扑（按自主度递增）

### T1 会话式副驾（人写规格，agent 写代码）

- 做法：人指定"模型 + 损失 + 训练配置 + 要加的模块"，agent 实现并交付可运行代码。
- 证据：cdeotte s6e2（ChatGPT 写全部代码，6 模型集成，CV 0.95583 / 公 0.95396 / 私 0.95532）；
  cdeotte vesuvius（让 ChatGPT 在公开 notebook 上加 nnUNet/骨架 loss/深监督/1000 epochs，0.552 → 0.581）；
  s6e4（Claude Code 一天迁移 150+ 脚本）。
- 门槛：规格要具体到"加什么、验收什么"；**agent 不会替你发现 top 方案**（cdeotte 原话：它不能自己提出思路，但实现极强）。
- 失败模式：过早放弃复杂重构、整本 notebook 重写导致配额被锁（s6e5 1st/2nd 共同反馈）。

### T2 双 agent 竞争（同一目标，两条独立路线）

- 做法：两个 agent 各自攻一个单模/一条路线，落后方获得领先方提示后反超；产出可比较的 CV/LB。
- 证据：s6e8 1st 第二阶段（GPT-5.6 Sol vs Claude Fable 5），产出单模 RealMLP CV 0.97070 / LB 0.97174，直接夺冠（18 个月来首次单模夺冠）。
- 门槛：统一折文件与评估口径，否则两个 agent 的分数不可比。
- 收益：多样性 + 并行探索；**单模价值回归**（FE 决定上限）。

### T3 群体并行采样（代码高尔夫 / 程序合成）

- 做法：同一任务并行采样 N 个候选 → 自动评估 → 取最优/最短；用规则化提示（AST 检查：有循环提示改递归、`def` 提示 `lambda`）。
- 证据：code-golf 2025 4th（98% LLM 生成；`codex exec` + Docker 沙箱 + SQLite 日志；约 15 个 Codex Cloud 会话并行；
  最后两周让 LLM 优化"压缩友好代码"）；9th 的并行采样借鉴了这条路线（neurogolf）。
- 门槛：必须有**自动评估器**与干净沙箱；每轮留日志（否则无法定位回归）。
- 收益：搜索空间里的"吞吐"归 agent，改变搜索空间归人。

### T4 调度器 + 持久 worker（长时无人值守）

- 做法：调度器管 N 个持久会话（`codex exec resume`），每题/每实验一个工作单元；事务门
  `backup → experiment → validate → promote/restore`；在线回归用**差分提交二分定位**。
- 证据：neurogolf 2026 9th：5 天无人值守 7516.01 → 7575.78（+59.77），271 题改动、256 题严格降本、零回归；
  s6e8 1st 第四阶段：把 ~150 个 LLM 组织成"分布式智能"（最终 449 模型、公榜 0.97206）。
- 门槛：预算硬上限、worker 硬目标（如 +1.5/题）、预烘焙任务笔记、共享 cookbook、可回滚产物。
- 失败模式：没有事务门 → 一夜之间回归无法定位；没有硬目标 → agent 空转烧 token。

## 3. 工作流骨架（可直接套用）

1. **规格先行（Spec-Driven）**：行为规格/验收标准是真源，生成代码是可弃产物。
   官方 5 日课（Kaggle×Google）把这条定为主张：Unit1 意图驱动 vibe coding → Unit5 规格为真源 + 自动评审 agent + 策略护栏。
2. **环境与日志**：Docker 沙箱 + `codex exec` + SQLite/台账；每个实验可回滚（备份→实验→验证→晋级/还原）。
3. **实验协议**：本地排行榜文件（`local_leaderboard.md`）+ 共享折文件 + 密封折；任何增益先过同折对照
   （协议见 [experiment-protocol.md](experiment-protocol.md)）。
4. **事务门与二分定位**：在线名次波动必须能二分到具体提交；技巧经在线确认后才合并进 `tricks.md`。
5. **接力与复核**：交接用 notes-as-baton（把决策、死因、下一步写进文件，而不是留在会话里）；
   重要提交人工复核，agent 产物按"可弃代码"对待。

## 4. 可量化案例表（同一赛季，不同拓扑）

| 场次 | 名次 | 拓扑 | 关键数字 | 证据等级 |
| --- | --- | --- | --- | --- |
| playground-series-s6e8 | 1st | T2+T3+T4 | 单 agent 4 天 380 模型 → 双 agent 对战 → ChatGPT Pro → ~150 LLM；单模 RealMLP CV 0.97070/LB 0.97174 夺冠；最终 449 模型公榜 0.97206 | A（自述+图，无法独立复现） |
| playground-series-s6e3 | 1st | T1 | 60 万行代码全 LLM 写、850 模型、50 个 EDA 脚本、4×A100；最终 150 模型 | A |
| playground-series-s6e4 | 2nd | T1 | Claude Code 一天迁移 150+ 脚本 → 第 3 天私榜第一（0.98160）；最终 Claude+Codex 双集成 | A |
| playground-series-s6e5 | 2nd | T4 | Codex 自主循环 218 模型（37 类）logits 融合；输 0.00001；记录"过早放弃/整本重写"失败模式 | A |
| google-code-golf-2025 | 4th | T3 | 98% 代码 LLM 生成；每轮 N=4 并行、AST 规则提示、约 15 会话并行 | A |
| neurogolf-2026 | 1st / 9th | T3 / T4 | 1st"永远先找更好架构"（重写 +0.5/题 vs 局部 +0.05/题）；9th 五天无人值守 +59.77、零回归 | A |
| rogii-wellbore-geology-prediction | 36th（GM） | T1 | `codex --yolo` 两周 + 2×L4；每晚人工给次日方向；1st/2nd/7th/36th 均由 agent 承担实现 | A（自述） |
| orbit-wars | 1st | T4 | 200M transformer、15B steps、2400 B200h、纯 agentic 开发 | A（自述） |

## 5. 失败模式与红线（按后果排序）

1. **合规取消**：自动化提交/自动跑实验前先读规则与 FAQ；birdclef-2026 101st 的前车之鉴。
2. **数据泄漏**：agent 常把"公开代码 + 本地划分不一致"当成正常数据（rogii 7th）；目标编码必须嵌套在折内（s6e2 赛后复盘）。
3. **伪增益**：agent 自报的 LB/CV 必须重算；没有同折对照的增益按 0 计（skill 硬规则）。
4. **工程失控**：整本 notebook 重写锁配额、过早放弃复杂重构（s6e5）；提示要有硬目标与停止条件。
5. **工具幻觉**：gemini-3 场有参赛者记录"Gemini 3 Pro 谎称改了代码"（13 票帖）；交付前做 diff 级验证。
6. **评审制陷阱**：AI 评委与 rubric 不透明会引发信任危机（gemini-3：69 票延期公告 + 207 评论）；
   这类赛道留可验证 demo/开源链接，别把命运交给黑箱评审。

## 6. 预算与 KPI（把 agent 当 worker 管理）

- **验收**：每个 worker 有硬目标（如 +1.5/题、CV 提升 ≥ 0.0005）与 kill 标准（连续 N 轮无改善即停）。
- **预算**：token/GPU/时间上限写进规格；失败预算（可接受烧掉多少算探索成本）提前定。
- **回归门**：任何 overnight 改动必须"零回归"才能晋级；用差分提交二分定位。
- **记录**：台账 + `tricks.md` + 决策日志；会话可丢，文件不可丢。

## 7. 现成检索（在 skill 里直接用）

```bash
# GM 断言层里的 agent 工作流条目（实测命中 3 条：rogii#733181-01 / neurogolf#726653-05 / eedi#551402-04）
python scripts/gm_claim_search.py --query "codex|claude|chatgpt|双流水线|自主" --min-units 1

# 放宽到 agent/LLM 主题（实测 23 条，多数是"比赛主题是 LLM"，需人工筛掉）
python scripts/gm_claim_search.py --query "agent|llm" --min-units 1 --limit 20

# 案例书里的深讲
# tabular.md：s6e3 / s6e4 / s6e5 / s6e6 / s6e8
# sim-agent.md：google-code-golf-2025（4th）/ neurogolf-2026（1st/9th）
# audio.md：birdclef-2026（101st 取消资格 = 合规反例）
# science 案例：rogii-wellbore-geology-prediction（agent 参与 + 泄漏教训）
```

## 链接索引（来源佐证）

- s6e8 1st（127 票）：https://www.kaggle.com/competitions/playground-series-s6e8/discussion/738592
- s6e3 1st：https://www.kaggle.com/competitions/playground-series-s6e3/discussion/686686
- s6e4 2nd：https://www.kaggle.com/competitions/playground-series-s6e4/discussion/696169
- s6e5 2nd：https://www.kaggle.com/competitions/playground-series-s6e5/discussion/703615
- s6e6 25th：https://www.kaggle.com/competitions/playground-series-s6e6/discussion/716748
- s4e10 全自动实验（top 21%）：https://www.kaggle.com/competitions/playground-series-s4e10/discussion/543734
- code-golf 2025 4th：https://www.kaggle.com/competitions/google-code-golf-2025/discussion/614124
- neurogolf 2026 9th：https://www.kaggle.com/competitions/neurogolf-2026/discussion/726653
- neurogolf 2026 1st 总述：https://www.kaggle.com/competitions/neurogolf-2026/discussion/726654
- rogii 36th（cdeotte）：https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/733181
- orbit-wars 1st：https://www.kaggle.com/competitions/orbit-wars/discussion/724268
- birdclef-2026 101st（取消资格，48 票）：https://www.kaggle.com/competitions/birdclef-2026/discussion/704391
- birdclef-2026 Claude-Code 讨论（142 票）：https://www.kaggle.com/competitions/birdclef-2026/discussion/681146
- gemini-3 官方欢迎帖：https://www.kaggle.com/competitions/gemini-3/discussion/651844
- gemini-3 评审延期（69 票 / 207 评论）：https://www.kaggle.com/competitions/gemini-3/discussion/667609
- gemini-3 代码改动幻觉（13 票）：https://www.kaggle.com/competitions/gemini-3/discussion/655429
- 5-Day AI Agents 课程 Day1（4217 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708280
- 5-Day AI Agents 课程 Final（1254 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/709464
- cdeotte s6e2「69th Place - ChatGPT Vibe Coding!」：https://www.kaggle.com/competitions/playground-series-s6e2/discussion/679367
- cdeotte vesuvius「Bronze Medal - ChatGPT Vibe Coding!」：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/679221
- KStarter 深读原文：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s6e8.md
