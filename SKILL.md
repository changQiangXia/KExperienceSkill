---
name: kaggle-score-climb
description: Kaggle 上分决策与经验迁移。面对新比赛时，从 264 场已验证经验中检索结构类比，结合指标结构、验证设计与证据分级，产出有力、准确、可证伪的改进方案（Improvement Plan），再按期望收益排序执行。适用于打榜、评审制、研究/hackathon 赛道与 agent 协作；执行/管道细节配合执行型 skill 使用。
---

# Kaggle Score Climb（上分决策 + 经验迁移）

## 目标与边界

- 目标：在规则允许范围内，最大化**最终排行榜名次/奖项**；public LB 是测量工具，不是目标。
- 本 skill 的输出是**改进方案**：每条建议都有机制、类比证据、可证伪实验、成本与风险；没有证据的只写"假设"。
- 执行层（Kaggle CLI、GPU/TPU offload、producer/consumer notebook、提交重跑）交给执行型 skill（如 `agentic-kaggle-skill`）；本 skill 决定打什么、先打什么、何时停。
- 与编码 agent 协作时默认契约：**人定路线/验收/合规，agent 做实现与实验**（拓扑与护栏见 `references/agent-kaggle-playbook.md`）。
- **规则优先**：任何泄漏、探榜、外部数据或提交套利前先确认比赛规则；不合规的分数不算分数。

## 核心循环（每个新比赛都走一遍）

1. **建事实底座**：任务/指标实现/数据结构/评测约束/平台规则 → Competition Card（`references/improvement-plan-protocol.md` 阶段 1）。
2. **检索经验**：用 `scripts/case_search.py --deep`、`scripts/case_card.py` 与 `references/case-index.md` 找 3–5 个结构类比场次；读 `references/case-books/<theme>.md`（264 场逐场深讲解）、`references/case-deep-dives.md`（精选深案例）、`references/cross-case-playbook.md`（13 个跨场对比专题），以及在 KStarter 仓库（https://github.com/changQiangXia/KStarter）中的 `analysis/deep/<slug>.md` 原文。
   同时查**同类型选手经验层**：`references/people-routing.md`（8 领域 → 先找谁 + 该类型高复现决策项）与 `scripts/gm_claim_search.py`（364 条 GM 断言快照，`--strict-units 2` 只看技法组合级复现）；有选手间冲突时以 `references/people-tensions.md` 的条件化裁决为准。
3. **诊断现状**：指标数学结构（`references/metric-arbitrage.md`）、验证可信度（`references/validation-to-lb.md`）、当前 baseline 与 CV-LB 关系；先修测量，再做模型。
4. **生成假设**：从 `references/idea-playbook.md` 按症状（S1–S28）取 3–7 条候选，用 `references/technique-transfer.md` + `scripts/technique_lookup.py` 查技法的支持/反例与第一步实验，用 `references/mechanisms.md` 写清机制、用 `references/boundaries.md` 判断有效侧/失效侧；每条 = 机制 + 类比证据（slug+数字+证据等级）+ 证伪实验 + 期望收益 + 成本 + 风险 + kill 标准；可参考 `references/worked-plans.md` 的五个完整样例。
5. **排序执行**：按 expected gain / hour 排序（`references/score-gain-ladder.md`），一次一个变量；按 `references/experiment-protocol.md` 做配对实验（同折同种子、MDE、kill 标准），台账记录（`assets/experiment_ledger_template.csv`、`assets/experiment_card_template.md`）。用编码 agent 执行时：先按 `references/agent-kaggle-playbook.md` 选拓扑（T1–T4），填 `assets/agent_spec_template.md`，过 `assets/agent_workflow_checklist.md`；规则禁止自动化提交时禁用自动链路。
6. **输出 Improvement Plan**：按 `references/improvement-plan-protocol.md` 阶段 5 的模板交付；多 agent 协作按阶段 6 的角色与交接物执行。
7. **收官保护**：提交组合/对冲、格式体检、冻结协议（`references/submission-portfolio.md`、`assets/endgame_checklist.md`、`scripts/submission_guard.py`）。

## 上分阶梯（按 expected gain / hour）

1. 修验证/指标口径/提交格式 —— 最大且最便宜；
2. 指标结构后处理（clip/校准/档位/形态/阈值/秩）；
3. 数据红利（实体/重复/生成痕迹/OOD/原数据，合规前提）；
4. 强单模与多样性（跨家族、embedding+GBDT、域内预训练）；
5. 集成/栈（仅 OOF 有增量时）；
6. 调参与长尾（先过种子检验；低信号设预算上限）；
7. 提交策略与收官（组合对冲、冻结、格式保护）。

## 五条硬规则

1. 验证不可信时，一切模型结论作废：先修验证。
2. public LB 是带噪测量：用样本量判断信息量，不做 LB 微差选模。
3. 任何技巧必须过同折对照；没有对照的增益按 0 计。
4. 一次只改一个变量，记录 CV/LB/成本/决策。
5. 最后 48 小时不引入新方法，只做选择、对冲与格式保护。

## 快速决策

| 信号 | 动作 |
| --- | --- |
| CV 与 LB 方向不一致 | 查实体/时间泄漏与指标口径（`validation-to-lb.md`） |
| 分数扎堆（0.25 聚集、26.38–26.41） | 停止 LB 调参，回到指标结构与 OOF |
| 公榜高、私榜崩（shakeup） | 提交组合对冲（`submission-portfolio.md`） |
| MedAE/分位/容差型指标 | 先做样本权重与分布整形（`metric-arbitrage.md`） |
| top-K/AUC/NDCG | 排序与校准不变融合；追加预测可能白赚 |
| 公开方案饱和、大家分差不多 | 找差分：数据/后处理/验证口径（`public-intel-differential.md`） |
| 经验不敢直接迁移 | 按 `experience-book.md` §11 六问 + 证伪实验 |
| 想用编码 agent 迁移脚本/跑批量实验 | 先查 `agent-kaggle-playbook.md` 的决策表与合规红线，再按 T1–T4 选拓扑 + 事务门 |

## 资源路由

- 经验书（领域化总结，10 章） → `references/experience-book.md`
- 逐场深讲解（264 场 × 数字账/矩阵/裁决全文/证据/失败学） → `references/case-books/<theme>.md`（tabular/cv/nlp/science/sim-agent/audio/other）
- 深案例库（~40 场，场景/机制/数字/配方/失效条件） → `references/case-deep-dives.md`
- 跨场对比专题（13 章，条件化裁决） → `references/cross-case-playbook.md`
- 技法迁移地图（40 技法：支持/反例/第一步/kill） → `references/technique-transfer.md`；查询 → `scripts/technique_lookup.py`；数据 → `assets/technique_case_map.csv`
- 264 场经验索引 → `references/case-index.md`；检索脚本 → `scripts/case_search.py --deep`；案例卡 → `scripts/case_card.py`
- 思路库（28 类症状 → 可执行思路） → `references/idea-playbook.md`
- 机制推演（为什么有效，M1–M27） → `references/mechanisms.md`
- 边界与反例（何时失效，B1–B26） → `references/boundaries.md`
- 实验协议（MDE/方差/配对/bootstrap/决策规则） → `references/experiment-protocol.md`
- 改进方案生成协议（含输出模板与 agent 分工） → `references/improvement-plan-protocol.md`
- 完整样例（5 个赛型） → `references/worked-plans.md`；按赛型模板 → `references/plan-templates.md`；计划骨架生成 → `scripts/plan_builder.py`
- 指标结构套利与合法后处理 → `references/metric-arbitrage.md`
- 验证设计、CV↔LB 关系、探榜纪律 → `references/validation-to-lb.md`
- 实验阶梯、台账与 kill 标准 → `references/score-gain-ladder.md`
- 提交组合、shakeup 对冲、收官冻结 → `references/submission-portfolio.md`
- 公开情报差分 → `references/public-intel-differential.md`
- 顶层规律速查（60 条） → `references/top-rules.md`
- 40 项故障预检 → `references/failure-preflight.md`
- 选手经验层路由（8 领域：先找人 + 高复现决策项） → `references/people-routing.md`；断言检索 → `scripts/gm_claim_search.py --domain cv --strict-units 2`；数据 → `assets/gm_claims_snapshot.csv` / `assets/people_manifest.json`
- 选手经验层口径（证据等级 / 复现度双口径 / flags） → `references/people-evidence.md`；选手间冲突裁决（12 组张力） → `references/people-tensions.md`
- 外部题解层（kaggle-solutions：冠军/高排名 write-up 与 notebook，4768 条） → `assets/external_solution_links.csv`；冠军索引 → `references/champion-solutions.md`；案例卡已内联（`scripts/case_card.py` 显示每场未收录过的前 8 条）
- 编码 agent 打 Kaggle（vibe coding → agentic engineering） → `references/agent-kaggle-playbook.md`（决策表 / T1–T4 拓扑 / 失败模式 / 预算 KPI）；规格模板 → `assets/agent_spec_template.md`；检查清单 → `assets/agent_workflow_checklist.md`
- 提交 CSV 体检 → `scripts/submission_guard.py`
- 折文件/台账生成 → `scripts/experiment_harness.py`；OOF 指标 + bootstrap CI + 配对比较 → `scripts/oof_report.py`
- 台账/收官模板 → `assets/experiment_ledger_template.csv`、`assets/endgame_checklist.md`

> 佐证链接：各参考文档末尾附 `链接索引（来源佐证）`（自动生成，来源 `tools/add_links_appendix.py`），
> 每条链接是 Kaggle 讨论区题解原文 + KStarter 深读 GitHub 链接；`scripts/case_card.py` 与 `case_search.py --deep` 也会输出可点击链接。

## 证据分级（写方案时必须标注）

- **官方**：主办方帖子/规则/评审说明；
- **图证**：归档图/截图（可回图核对）；
- **原文数字**：高票帖写出的具体数字（未独立复算）；
- **自述**：作者声称的增益/最优；
- **矛盾**：与其他帖子冲突或口径不一致。

引用经验时写明来源 slug；跨领域迁移时必须给反例与失效条件。

引用选手断言（`people-*` / `gm_claim_search.py`）时额外标注复现度：`strict ≥2`（同领域另一单位复现了
≥2 个相同具体技法）优先采纳；只有广义 `replication ≥2` 的按"弱复现"处理，并先查 `people-tensions.md`
是否有相反裁决。C 级断言只作为"技法被使用"的旁证，不作为增益证据。

外部题解（`champion-solutions.md` / `assets/external_solution_links.csv`，来源 kaggle-solutions，MIT）
只作为**线索与佐证入口**：链接本身是证据，数字与机制仍要回 Kaggle 原文或 KStarter 深读核对后再引用。

## Definition of Done

- 交付一份 Improvement Plan：诊断 + 机制 + 类比证据 + 3–7 条带 kill 标准的假设 + 执行顺序 + 风险。
- 每个已执行实验有台账行与 Experiment Card；结论附 `scripts/oof_report.py` 的 bootstrap CI/配对结果；连续两轮无 OOF 增益则回到诊断而不是继续调参。
- 最终提交通过 `submission_guard.py` 与 `assets/endgame_checklist.md`，并记录选择理由与未选提交原因。
