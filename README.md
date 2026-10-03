# KExperienceSkill：按比赛类型找对策的 Kaggle 上分技能

把 264 场 Kaggle 比赛经验做成一套可检索的技能：**先判断你的比赛类型，再找同类型的案例与对策**，
最后产出有证据、可证伪的改进方案（Improvement Plan）。

> `SKILL.md` 是给 agent 用的操作入口；本 README 是给人看的导航。

## 核心思想：什么类型的比赛，就看什么类型的经验

| 你的比赛类型 | 先读案例书 | 思路库（症状） | 常用技法 |
| --- | --- | --- | --- |
| 表格 / 合成数据（Playground） | `references/case-books/tabular.md` | S6、S12–S18 | 中位数后处理、档位吸附、清洗三件套、异质集成 |
| CV 分类 / 细粒度 | `references/case-books/cv.md` | S17、S19 | 高分辨率、IBN/直方图、ArcFace、身份辅助任务 |
| 检测 / 分割 / 计数 / 检索 | `references/case-books/cv.md` | S24 | 密度分层阈值、OSD 未知类、阈值后处理、检索 vs logits |
| NLP / LLM | `references/case-books/nlp.md` | S25 | 约束测试、TIR/大候选投票、蒸馏、输出解析 |
| 时序 / 金融 / 在线 | `references/case-books/tabular.md` + `science.md` | S5 | 时间切分+purge、在线学习、组合/风险层 |
| 模拟对战 / RL Agent | `references/case-books/sim-agent.md` | S26 | 规则基线、课程+热启动、对手多样性、拐点早停 |
| 评审制 / 研究 / Hackathon | `references/case-books/science.md` + `other.md` | S28 | 评审闭环写作、复现演练、消融与失败路径 |
| Agent-Config / LLM 应用赛 | `references/case-books/nlp.md` + `sim-agent.md` | S25、S28 | schema 本地校验、预算工作流、模型挂载保护 |
| 优化 / 黑箱 / 安全 | `references/case-books/sim-agent.md` + `science.md` | S27 | 代理评分器、结构探测、最弱环分析 |

**规则**：同类型优先（CV 先看 CV、NLP 先看 NLP）；跨类型迁移必须给出反例与证伪实验，不能只凭相似。

## 三步用法

1. **归类**：写下任务/指标/数据结构/评测约束，对照上表找到你的类型。
2. **检索**：从同类型案例里挑 3–5 场，读它们的深讲解与题解链接。
3. **出方案**：生成计划骨架 → 填假设（机制/证据/证伪实验/kill 标准）→ 用协议验证。

```bash
# 按类型/指标找类比案例（--deep 会检索完整案例卡）
python scripts/case_search.py --theme cv --tag segmentation --limit 5
python scripts/case_search.py --query "MedAE 中位数 后处理" --deep

# 看某一场的完整案例卡（含关键数字、裁决、失败学、题解链接）
python scripts/case_card.py --slug playground-series-s3e25

# 按技法查支持案例与反例
python scripts/technique_lookup.py --technique 伪标签

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
scripts/                     检索、计划、实验、校验工具（见上）
assets/                      案例索引/案例卡/技法地图/台账/收官清单
```

## 两条纪律

- **证据分级**：官方 > 图证 > 原文数字 > 自述；矛盾项标注。每个案例都附 Kaggle 讨论题解链接与 KStarter 深读链接（全库 1002 条链接已校验）。
- **可证伪**：每条建议都有 kill 标准与第一步实验；一次只改一个变量；连续两轮无 OOF 增益就回到诊断。

## 数据来源与致谢

经验来自 [KStarter](https://github.com/changQiangXia/KStarter) 的 264 场 write-up 深读（Tier A 60 + Tier B 204）
与四件套（THEORY / claims / lineage / limitations）；本仓库只做提炼与检索，深读原文以 KStarter 为准。
