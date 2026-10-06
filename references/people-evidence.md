# 前 50 选手经验层：证据与口径

> 快照 2026-10-06 ｜ 来源 KStarter `c13b2797e13686cf400333be627d572ffbfb7e34` ｜ 快照断言 364 条。

## 数据形态

- `assets/gm_claims_snapshot.csv`：364 条断言（A 264 / B 100），来自 152 条 ≥50 票 GM 主题帖全量抽取（551 条）中"带 ≥1 个具体技法标签"的 A/B 断言；其中广义复现 ≥2 单位 363 条，技法组合级复现（strict ≥2）184 条。
- 每条断言 = 条件 → 动作 → 机制 → 结果 + 证据等级 + 原文链接；不含逐字引用（引用与 topic id 校验见 KStarter `scripts/people/verify_claims.py`）。
- 标签与证据单位来自 KStarter `people/claims/gm_claim_tags.csv`；复现度只统计**具体技法标签**（见 `tools/sync_people_layer.py` 的 SPECIFIC_TAGS），并限制在同领域。

## 证据规则

- 等级：A = 原文可复算数字 + 名次/团队背书；B = 有数字无独立背书；C 不进快照。
- 复现度两口径（都用**独立证据单位**；`team_evidence` 按（比赛 + 队名）合并，同队多人只算 1 个单位）：
  - `replication`（广义）：同领域内使用该断言**任一**具体技法标签的单位数上限；≥3 可当"跨人复现"，=2 视为"弱复现"。
  - `strict_replication`（严格）：同领域内**同时**复现该断言 ≥2 个具体技法标签的单位数（含自身单位；统计跨全部证据等级、含 C 级——它证明"技法被复现"，增益可信度仍看断言自身等级）；≥2 说明技法组合被独立复现，采纳优先级最高。
- 口径旗标（flags）：
  - `lb_unusable`：Kaggle 冻结榜（分数全 0），名次不可用；
  - `lb_public_misleading`：公开榜名次与最终/私有结果背离（含泄漏争议场次）；
  - `team_evidence`：团队成绩，不归因个人；
  - `leak_usage` / `test_self_training` / `evaluator_exploit`：需要先确认比赛规则；
  - `negative_result`：负结果（反例证据）。
- 引用断言时标注 `claim_id + replication/strict + level`；先采纳 strict ≥2，再考虑广义复现高的；并查 `people-tensions.md` 是否有相反裁决。

## 已知边界

- 抽取/审计为同一模型完成；30 条分层审计见 KStarter `people/claims/AUDIT.md`（机器校验 100%，语义抽检 30/30 pass）。
- 快照只覆盖 KStarter 归档的 94 场（有 ≥50 票 GM 主题帖的比赛），不是选手完整生涯。
- 旗标统计（快照内）：single_source 363, team_evidence 111, lb_public_misleading 79, lb_unusable 19, negative_result 14, evaluator_exploit 3, leak_usage 2, test_self_training 1
