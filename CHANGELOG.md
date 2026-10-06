# Changelog

## v2.0.0 — 2026-10-06（工程化：P0–P2）

### P0 可用性
- 新增 `scripts/doctor.py`：结构/引用/schema/脚本冒烟/链接库存/provenance/生成器确定性与新鲜度，一条命令出 PASS/WARN/FAIL。
- 新增 GitHub Actions `check`：push/PR 自动跑 doctor（含生成器新鲜度）。
- 新增 `scripts/recommend.py`：比赛卡 → 文档/案例/技法/GM/脚本的统一路由（BM25 + 先验）。
- SKILL.md 新增「阅读协议」：token 预算 + 渐进披露，禁止整本读案例书。

### P1 决策纪律
- 新增 `scripts/plan_tracker.py`：预注册台账（MDE/kill/折胜数），自动判定 PROMOTE/KILL/INCONCLUSIVE，事后修订标记。
- 新增 `scripts/lb_noise.py`：LB 标准误、名次反转概率、最小可检测提升（MDL）。
- `scripts/oof_report.py` 扩展：多假设 BH-FDR、`--looks` 多次偷看校正、配对 bootstrap 重构。

### P2 覆盖与自证
- 新增 `scripts/skill_eval.py`：留一法回顾式自评（严格/宽松双层真值 + 基线对比），产出 `assets/skill_eval_latest.json`。
- 新增 `references/undercovered-domains.md`：推荐/排序、优化/黑箱、时间序列三个方向的补强入口。
- 新增 `assets/provenance.json`、`THIRD_PARTY.md`、`LICENSE`、本 CHANGELOG；doctor 校验 provenance。

## v1.2.0 — 2026-10-06
- 接入外部题解层：4732 条链接、冠军方案索引、案例卡/案例书内联（kaggle-solutions, MIT）。
- 新增 agent 范式层：`agent-kaggle-playbook.md`、规格模板、检查清单、`agent_audit.py`（kei-kochiya/kaggle-skills, MIT）。
- 新增 GM 可泛化流程：`gm-generalized-process.md`（KStarter 生成器聚合 551 条断言）。

## v1.1.0 — 2026-10-04
- 选手经验层：GM 断言快照（364 条）、`people-routing/evidence/tensions`、`gm_claim_search.py`、双口径复现度。

## v1.0.0 — 2026-10
- 初版：264 场案例书/案例卡、40 技法迁移地图、思路库/机制/边界/实验协议/收官清单等。
