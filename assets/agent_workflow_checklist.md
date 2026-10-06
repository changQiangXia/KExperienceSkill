# Agent 打 Kaggle：开跑 / 收官检查清单

> 配套：[references/agent-kaggle-playbook.md](../references/agent-kaggle-playbook.md)（范式与案例）、
> [assets/agent_spec_template.md](agent_spec_template.md)（任务规格）。

## A. 开跑前（合规与环境）

- [ ] 读过比赛规则/FAQ：agent 生成代码、自动实验、自动提交、外部 API 是否允许
- [ ] 提交权限只留在人手里（除非规则明确允许自动化）
- [ ] Spec 写完（目标/验收/kill/预算/交接），折文件固定
- [ ] 沙箱镜像可复现；密钥不入库、不进 prompt 日志
- [ ] 回滚机制就绪（备份/版本/产物目录）

## B. 数据与验证

- [ ] 目标编码、分组统计等全部嵌套折内（反例：s6e2 的 KFold 外 TE）
- [ ] 外部数据/公开代码列出许可与来源；核对划分一致性（反例：rogii agent 引入的泄漏）
- [ ] 对抗验证或分布检查跑过；CV 与 LB 关系有样本量判断
- [ ] 每个增益有同折对照（同折同种子）；没有对照的按 0 计

## C. 运行中（agent 管理）

- [ ] 每个 worker 有硬目标与 kill 标准；无改善按预算停
- [ ] 事务门：backup → experiment → validate → promote/restore
- [ ] 台账 `local_leaderboard.md` 逐轮记录（配置/CV/成本/决策）
- [ ] 重要节点人工给方向（"每晚简短对话定次日方向"是已验证的用法）
- [ ] 记录失败模式：过早放弃 / 整本 notebook 重写 / 幻觉改代码
- [ ] 生成提交前跑 `scripts/agent_audit.py`（长度/NaN/行序/折哈希/平局/泄漏烟雾）；FAIL 不提交

## D. 收官

- [ ] 重要提交人工复核（diff/行数/格式）
- [ ] 提交组合与对冲（见 `submission-portfolio.md`）
- [ ] 冻结协议 + 格式体检（`assets/endgame_checklist.md`、`scripts/submission_guard.py`）
- [ ] 复盘写入：技术结论 + agent 工作流结论（哪些拓扑有效、成本多少、下次改什么）
- [ ] 若使用自动化：确认披露与合规无遗漏
