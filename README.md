# KExperienceSkill：按比赛类型找对策的 Kaggle 上分技能

把 264 场 Kaggle 比赛经验 + 50 名 Grandmaster 的 551 条公开断言做成一套可检索的技能：
**先判断你的比赛类型，再找同类型的案例、找对人、抄对决策**，最后产出有证据、可证伪的改进方案（Improvement Plan）。

> `SKILL.md` 是给 agent 用的操作入口；本 README 是给人看的导航。

## 核心思想：什么类型的比赛，就看什么类型的经验

| 你的比赛类型 | 先读案例书 | 思路库（症状） | 常用技法 |
| --- | --- | --- | --- |
| 表格 / 合成数据（Playground） | `references/case-books/tabular.md` | S6、S12–S18 | 中位数后处理、档位吸附、清洗三件套、异质集成；进阶：CIR 校准、FFT-AUC 融合、base_margin 残差（`tabular-advanced-recipes.md`） |
| CV 分类 / 细粒度 | `references/case-books/cv.md` | S17、S19 | 高分辨率、IBN/直方图、ArcFace、身份辅助任务 |
| 检测 / 分割 / 计数 / 检索 | `references/case-books/cv.md` | S24 | 密度分层阈值、OSD 未知类、阈值后处理、检索 vs logits |
| NLP / LLM | `references/case-books/nlp.md` | S25 | 约束测试、TIR/大候选投票、蒸馏、输出解析 |
| 时序 / 金融 / 在线 | `references/case-books/tabular.md` + `science.md` | S5 | 时间切分+purge、在线学习、组合/风险层 |
| 模拟对战 / RL Agent | `references/case-books/sim-agent.md` | S26 | 规则基线、课程+热启动、对手多样性、拐点早停；工程层：模拟器加速、联赛、NF4 量化部署（`sim-engineering.md`） |
| 评审制 / 研究 / Hackathon | `references/case-books/science.md` + `other.md` | S28 | 评审闭环写作、复现演练、消融与失败路径 |
| Agent-Config / LLM 应用赛 | `references/case-books/nlp.md` + `sim-agent.md` | S25、S28 | schema 本地校验、预算工作流、模型挂载保护 |
| 优化 / 黑箱 / 安全 | `references/case-books/sim-agent.md` + `science.md` | S27 | 代理评分器、结构探测、最弱环分析 |
| **任意类型：想用编码 agent / vibe coding 提效** | `references/agent-kaggle-playbook.md` | — | 四种拓扑（副驾/双 agent/群体/调度器）、合规红线、事务门与泄漏审计 |

**规则**：同类型优先（CV 先看 CV、NLP 先看 NLP）；跨类型迁移必须给出反例与证伪实验，不能只凭相似。

## 找谁 + 该类型的复现决策项（前 50 选手经验层）

上表解决"看哪些案例"；这张表解决"找哪些人、先抄哪个决策"。全部数据来自 152 条 ≥50 票 GM 主题帖
（551 条断言 → 364 条可检索快照，其中技法组合级复现 184 条）。`严` = 同领域其他选手独立复现了
**≥2 个相同具体技法**的证据单位数，严越高越该优先采纳；完整列表见 `references/people-routing.md`，
口径见 `references/people-evidence.md`，冲突裁决见 `references/people-tensions.md`。

| 你的比赛类型 | 先找人（快照条数） | 高复现决策项（严=组合级复现单位数） | 规模 |
| --- | --- | --- | --- |
| 视觉 CV | @christofhenkel(18)、@ren4yu(14)、@tascj0(10) | 集成权重选择（严10）、后处理/校准（严10）、损失设计（严10） | 83 条 / 严 43 |
| 文本 NLP | @cdeotte(32)、@philippsinger(16)、@conjuring92(14) | 集成权重选择（严10）、损失设计（严10）、长序列/上下文（严8） | 120 条 / 严 63 |
| 表格 / 结构化 | @cdeotte(50)、@hydantess(7)、@aerdem4(5) | 集成权重选择（严6）、损失设计（严6）、后处理/校准（严6） | 87 条 / 严 34 |
| 时间序列 | @cdeotte(7)、@hydantess(7)、@aerdem4(5) | 集成权重选择（严7）、时间/分组切分（严7）、损失设计（严7） | 37 条 / 严 13 |
| 语音 / 音频 | @cpmpml(5)、@nikitababich(5)、@christofhenkel(5) | 损失设计（严2）、外部数据（严2）、伪标签/自训练（严2） | 17 条 / 严 9 |
| 生物 / 医疗 | @cdeotte(20)、@ren4yu(14)、@christofhenkel(13) | 集成权重选择（严14）、损失设计（严14）、后处理/校准（严11） | 97 条 / 严 57 |
| 强化学习 / 博弈 | @pressman1(6)、@dipamc77(5)、@yiheng(4) | 时间/分组切分（严6）、集成权重选择（严6）、损失设计（严4） | 29 条 / 严 11 |
| 科学研究 | @jeroencottaar(8)、@cdeotte(8)、@tascj0(7) | 集成权重选择（严8）、后处理/校准（严8）、时间/分组切分（严7） | 53 条 / 严 29 |

每条断言都带原文链接（Kaggle 讨论区）与 `claim_id + replication/严 + 等级(A/B)`，可回链核对；
团队成绩按"比赛+队名"合并为 1 个证据单位，不归因个人。

## 三步用法

1. **归类**：写下任务/指标/数据结构/评测约束，对照上表找到你的类型。
2. **检索**：从同类型案例里挑 3–5 场，读它们的深讲解与题解链接。
3. **出方案**：生成计划骨架 → 填假设（机制/证据/证伪实验/kill 标准）→ 用协议验证。
   若要交给编码 agent 执行：先读 `references/agent-kaggle-playbook.md` 选拓扑，套 `assets/agent_spec_template.md`
   与 `assets/agent_prompt_templates.md`（取证/建模/堆叠/审计模板），并按 `assets/agent_workflow_checklist.md` 过合规与验收。

```bash
# 按类型/指标找类比案例（--deep 会检索完整案例卡）
python scripts/case_search.py --theme cv --tag segmentation --limit 5
python scripts/case_search.py --query "MedAE 中位数 后处理" --deep

# 看某一场的完整案例卡（含关键数字、裁决、失败学、题解链接）
python scripts/case_card.py --slug playground-series-s3e25

# 按技法查支持案例与反例
python scripts/technique_lookup.py --technique 伪标签

# 按类型找人：同领域的 GM 复现断言（严=技法组合级复现；--min-units 放宽到广义复现）
python scripts/gm_claim_search.py --domain cv --strict-units 2 --limit 5
python scripts/gm_claim_search.py --tag 后处理/校准 --level A --min-units 3

# 生成改进方案骨架（Competition Card + 匹配案例 + 假设表）
python scripts/plan_builder.py --task "tabular regression" --metric "MedAE" \
    --tags "tabular,synthetic" --notes "1500 队，小数据，public 20%"

# 实验与验证
python scripts/experiment_harness.py --data train.csv --target y --strategy stratified --n-splits 5
python scripts/oof_report.py --oof oof.csv --target y --pred base --pred2 new --metric auc
python scripts/submission_guard.py --submission submission.csv --sample sample_submission.csv
```

## 目录速览

```text
SKILL.md                     agent 操作入口（核心循环 / 快速决策 / 资源路由）
references/
  case-books/<类型>.md       264 场逐场深讲解（按 tabular/cv/nlp/science/sim-agent/audio/other 分册）
  case-deep-dives.md         精选 ~40 场深案例（场景/机制/数字/配方/失效条件）
  cross-case-playbook.md     13 个跨场对比专题（条件化裁决）
  technique-transfer.md      40 个技法：何时用/支持案例/反例/第一步/kill
  idea-playbook.md           28 类症状 → 可执行思路
  mechanisms.md              机制推演（为什么有效，M1–M27）
  boundaries.md              边界与反例（何时失效，B1–B26）
  experiment-protocol.md     实验协议（MDE/方差/配对/bootstrap/决策规则）
  improvement-plan-protocol.md  改进方案生成协议（含 agent 分工）
  worked-plans.md            5 个完整方案样例
  plan-templates.md          8 个赛型模板
  top-rules.md / validation-to-lb.md / metric-arbitrage.md / submission-portfolio.md ...
  people-routing.md          按比赛类型找人：8 领域 → 先找人 + 高复现决策项（严格复现优先）
  people-evidence.md         选手经验层的证据分级 / 复现度双口径 / flags 说明
  people-tensions.md         12 组选手间冲突裁决（谁在什么条件下对）
  champion-solutions.md      冠军方案索引（187 场覆盖场内，按主题 + 历史精选 + 代码/Notebook 参考）
  agent-kaggle-playbook.md   用编码 agent 打 Kaggle：决策表 / 四种拓扑 / 失败模式 / 预算 KPI
  tabular-advanced-recipes.md  表格赛高级配方：生成器取证 / 嵌套 TE / CIR+Ridge / FFT-AUC / base_margin / Fréchet / lexrank
  sim-engineering.md         模拟赛工程：加速层级 / 多实体架构 / PPO+联赛 / NF4 量化与部署兜底
scripts/                     检索、计划、实验、校验工具（见上）；gm_claim_search.py 查 GM 断言快照
assets/                      案例索引/案例卡/技法地图/台账/收官清单 + gm_claims_snapshot.csv（364 条）
                             / external_solution_links.csv（4768 条外链）/ people_manifest.json
                             / agent_spec_template.md（任务规格）+ agent_workflow_checklist.md（开跑/收官清单）
                             / agent_prompt_templates.md（取证/建模/堆叠/审计提示词）
tools/                       sync_people_layer.py（同步选手经验层）；import_external_links.py（导入外部题解索引）
```

## 两条纪律

- **证据分级**：官方 > 图证 > 原文数字 > 自述；矛盾项标注。每个案例都附 Kaggle 讨论题解链接与 KStarter 深读链接（全库 1002 条链接已校验）；`case_card.py` 还会列出该场未收录过的外部高排名题解（前 8 条）。
- **agent 自述重算**：agent/LLM 相关的名次与增益多为自述（如 s6e8 的 agent 编排），引用前按 `agent-kaggle-playbook.md` 的证据等级与 `experiment-protocol.md` 复核。
- **可证伪**：每条建议都有 kill 标准与第一步实验；一次只改一个变量；连续两轮无 OOF 增益就回到诊断。

## 数据来源与致谢

经验来自 [KStarter](https://github.com/changQiangXia/KStarter)：264 场 write-up 深读（Tier A 60 + Tier B 204）
与四件套（THEORY / claims / lineage / limitations）；选手经验层来自 50 名 GM 的 152 条 ≥50 票主题帖
（551 条断言、94 份 dossier、40 份决策画像、8 本领域 playbook，快照时点 KStarter commit `9950188`）。
外部题解层来自 [faridrashidi/kaggle-solutions](https://github.com/faridrashidi/kaggle-solutions)（MIT License,
Farid Rashidi）：721 场 / 4768 条链接中，264 场覆盖场内 2402 条；本仓库只保留链接与元数据派生，
未收录过的前 8 条已内联进案例卡（`assets/external_solution_links.csv` 为全量）。
本仓库只做提炼与检索，深读原文以 KStarter 为准。
