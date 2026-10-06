# Agent 提示词模板（表格/审计/规格）

> 来源：蒸馏自 [kei-kochiya/kaggle-skills](https://github.com/kei-kochiya/kaggle-skills)（MIT）
> 的 `Handbook/workflows/llm-agentic-kaggle-workflow.md`；已按本 skill 的证据纪律改写。
> 配套：[agent-kaggle-playbook.md](../references/agent-kaggle-playbook.md)（拓扑与护栏）、
> [agent_spec_template.md](agent_spec_template.md)（总规格）、[agent_workflow_checklist.md](agent_workflow_checklist.md)。
> 用法：把 `<...>` 换成当前比赛的值；每个模板都要求 agent 产出**可检查文件**，而不是口头结论。

## 模板 1：生成器逆向（合成数据取证）

```markdown
你是 Kaggle Grandmaster，正在分析一个合成数据集。
- 合成训练集：<rows> 行，列：<columns>
- 原始参考数据：<path/original.csv>（<rows> 行）

任务：写一个独立 Python 脚本，并输出 generator_artifacts_report.csv：
1. 对每个连续列做 snap 匹配：在原始数据里找最近邻，记录匹配数/命中率。
2. 计算扰动 delta = synthetic - snap，并用 ROC-AUC 检验 delta 与目标的相关性。
3. 提取小数尾数（小数部分；对 1/2、1/4、1/5、1/10 的残差）与模 10 位分解，同样做 AUC 检验。
4. 做 Benford 筛查（首位数字分布 vs log10(1+1/d)），报告偏离最大的列。
5. 抽查重复行、四舍五入痕迹与类别×数值的组合规则；确定性规则（100% 精确行）单独列表。
6. 所有检验必须在训练折内做嵌套（内层 5 折），禁止跨折统计。
约束：只写脚本 + 报告文件；每个结论必须带数字与文件名；不确定的写"未验证"。
```

## 模板 2：PyTorch 模型合成（单模，可复现）

```markdown
实现一个干净、模块化的 5 折 StratifiedKFold 训练管线，模型族：<TabM/RealMLP/...>。
要求：
1. 特征处理：数值列 <PLR embedding + RobustScaler>；类别列 <entity embedding, dim=min(16, ceil(sqrt(cardinality)))>。
2. 结构：<加法路径 + 双线性交互块；k=32 basis>；输入/输出维度写静态断言。
3. 训练：seed=42；BCE（label_smoothing=0.01）；AdamW lr=1e-3, wd=1e-4 + CosineAnnealingLR；早停 patience=15（看验证 AUC）。
4. 产物：oof_<name>.npy（长度 <N_train>）、pred_<name>.npy（长度 <N_test>）；打印每折 AUC 与 honest OOF AUC。
5. 禁止：任何跨折的目标统计；NaN/长度断言必须写在脚本里。
交付：脚本路径 + 运行日志尾部（含断言输出）。如果任何一步失败，报告失败原因，不要伪造结果。
```

## 模板 3：GPU 前向爬山堆叠器

```markdown
写一个 GPU 加速的前向贪心选择 + 堆叠脚本（cuDF/cuML 或等价实现）：
1. 扫描目录里所有成对的 oof_*.npy / pred_*.npy，记录文件名与长度校验。
2. 从空集成开始：每轮尝试加入每个未用模型，按真实标签 y 算 ROC-AUC。
3. 提升 > 1e-5 才锁定；平台期或选满 <150> 个模型即停。
4. 过滤规则：与当前集成 Spearman ρ > 0.998 的候选直接跳过。
5. 用选中模型的 logit 特征拟合 L2 逻辑回归（C=0.01，clip logit 到 ±30，tol=1e-4，失败回退 lbfgs）。
6. 对测试预测做折内序数秩校准；输出 submission_logitstack.csv + 选择报告（每轮加入谁、增益多少、成本）。
约束：每个数字都要能从脚本重算；报告里附最终集成的成员清单与 OOF。
```

## 模板 4：独立审计 Agent（跨家族只读）

```markdown
你是独立审计 agent，只读（read-only）检查另一个 agent 的产物，模型家族必须不同（如 Codex 审 Claude）。
输入：<提交文件/脚本/台账目录>。
逐条给出证据（文件+行号）与 PASS/FAIL：
1. 特征里是否包含标签泄漏（含折内嵌套的目标编码/统计特征）。
2. 打分折是否被用于选择（scored-fold selection bias）。
3. OOF 与测试预测长度、顺序、NaN 是否一致。
4. 行序是否保持（与 sample_submission/训练索引对齐）。
5. 堆叠嵌套是否完整（meta 折是否用同一折协议）。
6. 是否有公榜反馈泄漏（用 public LB 调过权/挑过提交）。
7. 伪标签来源是否有 OOF teacher 隔离。
8. 折哈希/种子是否与台账一致。
输出：8 项结论 + 需要人工复核的风险清单；禁止修改任何文件。
```

## 模板 5：两段漏斗实验请求（先快后严）

```markdown
假设：<一句话机制假设>；预期增益 ≥ <MDE>。
第 1 段（快筛）：只在 Fold 0 上对照基线；通过则 Fold 1 复核。两折都正 → 进入finalist。
第 2 段（严筛）：完整 5 折 + 嵌套 meta；要求 ≥4/5 折为正且均值增益 > 0；
              通过全部 8 条审计后再生成提交。
输出：每阶段的结果表（折、ΔAUC、成本）+ 停止原因；任何阶段失败都要记录，不允许只报成功路径。
```

> 证据与出处：多 LLM 角色分工、7 阶段工作流、8 条审计门与两段漏斗的原始描述见
> [llm-agentic-kaggle-workflow.md](https://github.com/kei-kochiya/kaggle-skills/blob/main/Handbook/workflows/llm-agentic-kaggle-workflow.md)（MIT）。
