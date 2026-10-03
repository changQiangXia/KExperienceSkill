# 完整样例：Improvement Plan（可照抄的推理过程）

> 5 个虚构但贴近真实的新比赛场景，展示"Competition Card → 匹配案例 → 假设表 → 执行顺序 → 收官"的完整输出。
> 表中的数字来自 KStarter 案例，用于估计量级；本场必须先做同折实验验证。

## 样例 A：表格回归，指标 MedAE，1500 队，小数据

**Competition Card**

- 任务：回归（表格，~15k 行）；指标 MedAE；public/private 20/80。
- 数据：无实体键；目标离散（约 30 个档位）；train/test 同分布（待验证）。
- 约束：每天 5 次提交；无外部数据限制说明。
- 现状：无 baseline；CV 口径未建立。

**匹配案例**

- `playground-series-s3e25`：MedAE 只取决于中位样本；两端降权 CV +0.03；9 档整形。
- `playground-series-s3e14`：目标 776 唯一值 → 吸附 +0.3。
- `playground-series-s5e9`：合成/低信号时用随机目标检验与分布决策。
- `playground-series-s3e9`：CV 5407 vs LB 721；只信 CV。

**候选假设**

| # | 假设 | 机制 | 类比证据 | 证伪实验 | 期望收益 | 成本 | 风险 | Kill 标准 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 目标档位吸附 | MedAE 对档位内误差不敏感 | s3e14 吸附 +0.3；s3e25 9 档 | OOF：吸附 vs 不吸附 | 0.05–0.3 | 1h | 测试连续时失效 | OOF 无提升 |
| 2 | 两端样本降权 | 只让中位样本主导梯度 | s3e25 降权 +0.03 | OOF 扫阈值/权重 | 0.01–0.03 | 2h | 分布不同构 | ΔOOF<1e-4 |
| 3 | 随机目标检验 | 判低信号，调整预算 | s5e9 z=-0.83 | 100 次打乱对照 | 决策价值 | 0.5h | 只判原数据 | — |
| 4 | 分组合法性裁剪 | 预测贴回训练分位区间 | s3e8 上/下界 +1.3 | OOF 分组裁剪 | 0.01–0.1 | 2h | 分组样本不足 | OOF 无提升 |
| 5 | 异质集成（GBDT+线性/核） | 跨家族多样性 | s3e9 GB+RF+Ridge 12.03 | OOF 对比单模 | 0.001–0.01 | 4h | 低信号过拟合 | 相关性>0.99 |

**执行顺序**：① metric 单测 + CV 口径（0.5h）；② 假设 3 随机目标检验（0.5h）；③ 假设 1/2 后处理（3h）；④ 假设 4 裁剪（2h）；⑤ 假设 5 集成（4h）；⑥ 提交组合：CV 最优 + 保守候选各一。

**收官**：submission_guard + endgame checklist；每天 ≤2 次提交，保留最后 2 次。

## 样例 B：CV 细粒度分类，训练与测试来自不同采集域

**Competition Card**

- 任务：细粒度图像分类（~500 类）；指标 Macro F1。
- 数据：训练 A 域、测试 B 域（光照/设备不同）；类间相似度高。
- 约束：单卡 16GB；无外部数据（或需申请）。
- 现状：ResNet50@224 基线 CV 0.73。

**匹配案例**

- `sorghum-id-fgvc-9`：直方图均衡 +0.03、IBN +0.05、ArcFace +0.015、512→1024 +0.04、伪标签 +3.2。
- `hotel-id-to-combat-human-trafficking-2022`：掩码/遮挡按测试分布增强 +0.03–0.04 mAP。
- `herbarium-2022-fgvc9`：多级 CE + subcenter-ArcFace；长尾不重采样。
- `planttraits2024`：域内预训练 + 分层 LR；身份辅助任务。

**候选假设**

| # | 假设 | 机制 | 类比证据 | 证伪实验 | 期望收益 | 成本 | 风险 | Kill 标准 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 提高分辨率（224→384/512） | 细粒度纹理需要像素 | sorghum +0.04；herbarium +0.017 | 分辨率阶梯 OOF | 0.02–0.08 | 4h | 显存不足 | OOF 无提升 |
| 2 | IBN + 直方图均衡 | 吸收采集域风格差 | sorghum IBN +0.05/HE +0.03 | 单项消融 | 0.03–0.08 | 3h | 域差不在颜色 | ΔOOF<0.005 |
| 3 | ArcFace/subcenter 度量损失 | 类间相似 → 增大类间距离 | herbarium +0.017；hotel-id 2nd | 损失替换对照 | 0.01–0.03 | 4h | 小类不足 | OOF 无提升 |
| 4 | 域内/外部预训练权重 | 起点决定上限 | planttraits（PlantCLEF）；sorghum FGVC8 | 2–3 权重对照 | 0.01–0.05 | 6h | 许可/下载成本 | CV 无提升 |
| 5 | 测试分布对齐增强（掩码/光照/旋转） | 缩小 train/test 外观差 | hotel-id BlendFlip +0.03–0.04 | 增强方案对照 | 0.01–0.04 | 3h | 增强过度 | OOF 无提升 |

**执行顺序**：① 数据分布可视化（2h）；② 假设 1 分辨率（4h）；③ 假设 2/3 组合（6h）；④ 假设 4 权重（6h）；⑤ 伪标签（同折对照后启用）；⑥ TTA + 多折集成；⑦ 提交格式与候选对冲。

**收官**：优先"CV 最强 + 保守（无伪标签版）"两个候选。

## 样例 C：LLM 受限推理（小模型、限时、结构化输出）

**Competition Card**

- 任务：用给定小模型解推理题（整数/结构化答案）；T4×2、单次限时。
- 评测：vLLM temp=0、max_tokens 限制、答案格式固定；不能联网/不能跑程序（待确认）。
- 现状：无微调基线，零样本准确率低。

**匹配案例**

- `ai-mathematical-olympiad-prize`：TIR 工具推理 + 大候选投票；3rd 不微调 120–160 候选。
- `nvidia-nemotron-...`：类别解出率表 + 数据合成；crypt 7.9% 是弱项。
- `lmsys-chatbot-arena`：把大模型判断力蒸馏进 9B。
- `feedback-prize-effectiveness`：伪标 + 两级集成 + 校准。

**候选假设**

| # | 假设 | 机制 | 类比证据 | 证伪实验 | 期望收益 | 成本 | 风险 | Kill 标准 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 约束测试套件先行 | 评测器限制决定方案 | nemotron/lmsys 约束清单 | 写测试并跑通 | 避免 0 分 | 1h | — | 任一约束失败 |
| 2 | 工具集成推理（如允许） | 用执行器替代算术 | aimo 1st TIR；3rd 大候选 | 有/无工具对照 | 大幅 | 4h | 评测禁止 | 规则不允许 |
| 3 | 大候选 + 投票/打分 | 降低单次采样方差 | aimo 3rd 120–160 候选 | 候选数 16/64/160 | 0.05–0.2 | 3h | 时延超限 | 超时或 OOF 无提升 |
| 4 | 按类别合成数据 | 弱项类别单独补 | nemotron（crypt 7.9%） | 类别解出率前后对照 | 0.05–0.2 | 8h | 合成质量差 | 弱项无提升 |
| 5 | 输出格式与解析 | 解析失败=0 分 | aimo `\boxed{}` | 解析失败率统计 | 防 0 分 | 1h | — | 失败率>1% |
| 6 | 蒸馏 + 校准 | 压缩大模型判断力 | lmsys 9B | 教师软标签对照 | 0.02–0.1 | 6h | 蒸馏数据泄漏 | OOF 无提升 |

**执行顺序**：① 约束测试 + 输出解析（2h）；② 基线候选投票（3h）；③ 弱项类别表 + 合成（8h）；④ 蒸馏/微调（6h）；⑤ 端到端时延压测；⑥ 提交与回退版本。

## 样例 D：模拟对战 / 自对弈 Agent

**Competition Card**

- 任务：1v1 或多人对战，提交 agent；ELO/积分排名；有提交 slot 限制。
- 环境：可本地模拟但官方有随机性；终局由积分/碰撞/生存决定。
- 现状：只有随机/规则基线。

**匹配案例**

- `maze-crawler`：终局构造 + 评分函数 BFS；镜像鲁棒性。
- `lux-ai-season-2-neurips-stage-2`：课程 + 热启动 + 行动掩码 + 拐点早停。
- `kore-2022-beta`：规则七模块打败 RL 尝试。
- `santa-2024`：黑箱昂贵评分的局部搜索。

**候选假设**

| # | 假设 | 机制 | 类比证据 | 证伪实验 | 期望收益 | 成本 | 风险 | Kill 标准 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 终局规则表 + 主动构造 | 结算规则可被策略影响 | maze（tiebreak 矿工） | 规则模拟 + 对局统计 | 大幅 | 3h | 规则随机 | 无稳定收益 |
| 2 | 规则基线（评分函数） | 可解释、可快速迭代 | kore 七模块；maze 1st | 对随机基线胜率 | 中–大 | 8h | 环境复杂 | 胜率<60% |
| 3 | 快模拟器/向量化 | 采样效率决定 RL 上限 | lux Jux；maze JAX | 与官方对局一致性 | 中 | 2–5 天 | 移植成本 | 一致性<99% |
| 4 | 课程 + 热启动 | 复杂环境先易后难 | lux 16→32→64 | 小图→大图迁移 | 中 | 2–3 天 | 小图过拟合 | 大图无提升 |
| 5 | 对手多样性/镜像调参 | 防偏科 | maze 53/47；3rd 反思 | 历史版本 + 镜像对局 | 中 | 1–2 天 | 评估噪声 | 无显著提升 |
| 6 | 拐点早停 | 有效步数远小于预算 | lux KL>0.02、金属<100 | KL/资源/胜率曲线 | 省预算 | 持续 | 指标误判 | 曲线无拐点 |

**执行顺序**：① 规则/结算表（3h）；② 规则基线（1 天）；③ 快模拟器或轻量自对弈（2–5 天）；④ 课程/对手池；⑤ 提交 slot 策略（保留探索位）；⑥ 镜像对局回归测试。

## 样例 E：评审制 / 研究 / Hackathon

**Competition Card**

- 任务：交付应用/研究/分析报告，评审制；有 rubric（可能不公开分项）。
- 约束：字数/页数/视频/可复现；结果延迟数周。
- 现状：技术 demo 可跑，但交付叙事未整理。

**匹配案例**

- `pokemon-tcg-...-strategy`：观察→改动→验证闭环；消融 + 失败路径 + 少而精图表。
- `bigquery-ai-hackathon`：必须公开可访问、评委逐一复现；缺 artifact 过滤。
- `openai-gpt-oss-20b-red-teaming`：高召回初筛 + 深度复现 + 盲样 QA。
- `med-gemma-impact-challenge`：部署与提交物流是主要门槛。
- `geolifeclef-2024`：working note 时间线 + 可复现。

**候选假设**

| # | 假设 | 机制 | 类比证据 | 证伪实验 | 期望收益 | 成本 | 风险 | Kill 标准 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 按 rubric 映射交付 | 评审按公布维度打分 | pokemon Model/Deck/Report | 自查表逐项打分 | 中–大 | 2h | rubric 不公开 | 有维度缺证据 |
| 2 | 陌生环境冷启动复现 | 不可复现直接过滤 | bigquery；gpt-oss | 新账号按说明跑 | 防 0 分 | 2h | 私有依赖 | 任一步失败 |
| 3 | 消融 + 失败路径 | 评审欣赏完整闭环 | pokemon 官方总结 | 补 1 消融 + 1 失败方案 | 中 | 4h | 时间不够 | 无对照 |
| 4 | 交付叙事与图表 | 降低评审阅读成本 | pokemon；nfl-bdb | 让第三方 5 分钟复述 | 中 | 3h | 图表堆砌 | 读者仍困惑 |
| 5 | 预算/配额/提交保护 | 平台事故直接淘汰 | bigquery（按钮失效）；med-gemma（提交错过） | 提前 48h + 截图 | 防 0 分 | 1h | — | 未提交成功 |

**执行顺序**：① rubric → 交付清单（2h）；② 冷启动复现演练（2h）；③ 补消融/失败路径（4h）；④ 重写叙事与图表（3h）；⑤ 提前 48h 提交 + 凭证；⑥ 结果期保持产物可访问。

## 链接索引（来源佐证）

> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 3 条）+ KStarter 深读原文。

- **geolifeclef-2024**（cv/Research｜F-Score Beta (Micro)）
  - [working note 邀请（8 票 / 4 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/506431)
  - [新手门槛吐槽（20 票 / 3 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481283)
  - [ClimateClef 数据集（20 票 / 4 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481485)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/geolifeclef-2024.md)
- **herbarium-2022-fgvc9**（cv/Research｜F-Score (Macro)）
  - [1st 方案（5 票 / 1 评论）](https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/329299)
  - [上手 notebook 合集（15 票 / 7 评论）](https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/323794)
  - [往届 notebook（38 票 / 18 评论）](https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/307745)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/herbarium-2022-fgvc9.md)
- **hotel-id-to-combat-human-trafficking-2022-fgvc9**（cv/Research｜MAP@{K}）
  - [1st：BlendFlip + 5 模型集成（30 票 / 8 评论）](https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328281)
  - [2nd 方案（11 票 / 0 评论）](https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328345)
  - [公开/私榜 3rd（16 票 / 8 评论）](https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328237)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/hotel-id-to-combat-human-trafficking-2022-fgvc9.md)
- **planttraits2024**（cv/Research｜R2 Score）
  - [1st PlantHydra（29 票 / 13 评论）](https://www.kaggle.com/competitions/planttraits2024/discussion/510393)
  - [6th AutoGluon（9 票 / 4 评论）](https://www.kaggle.com/competitions/planttraits2024/discussion/510143)
  - [9th DINOv2+CatBoost（9 票 / 1 评论）](https://www.kaggle.com/competitions/planttraits2024/discussion/510188)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/planttraits2024.md)
- **sorghum-id-fgvc-9**（cv/Research｜Categorization Accuracy）
  - [3rd 方案（12 票 / 7 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/328593)
  - [2nd 方案（5 票 / 0 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329414)
  - [1st 方案（6 票 / 4 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329049)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/sorghum-id-fgvc-9.md)
- **ai-mathematical-olympiad-prize**（nlp/Featured｜Accuracy Score）
  - [1st（191 票）](https://www.kaggle.com/competitions/ai-mathematical-olympiad-prize/discussion/519303)
  - [2nd（352 行处）](https://www.kaggle.com/competitions/ai-mathematical-olympiad-prize/discussion/518964)
  - [3rd（72 票）](https://www.kaggle.com/competitions/ai-mathematical-olympiad-prize/discussion/517206)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/ai-mathematical-olympiad-prize.md)
- **bigquery-ai-hackathon**（nlp/Featured｜）
  - [获奖与评审流程（8 票 / 12 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/612730)
  - [云额度支持（13 票 / 37 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/598576)
  - [官方欢迎（24 票 / 49 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/598594)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/bigquery-ai-hackathon.md)
- **feedback-prize-effectiveness**（nlp/Featured｜Multiclass Loss）
  - [1st（141 票）](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347536)
  - [更多教训（107 票）](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347425)
  - [2nd（94 票）](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347359)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/feedback-prize-effectiveness.md)
- **lmsys-chatbot-arena**（nlp/Research｜Log Loss）
  - [16th（Chris Deotte）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527596)
  - [1st（sayoulala）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527629)
  - [2nd（tascj）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527685)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/lmsys-chatbot-arena.md)
- **med-gemma-impact-challenge**（nlp/Featured｜）
  - [HAI-DEF 基础模型清单（28 票 / 4 评论）](https://www.kaggle.com/competitions/med-gemma-impact-challenge/discussion/667677)
  - [评分透明性请求（3 票 / 8 评论）](https://www.kaggle.com/competitions/med-gemma-impact-challenge/discussion/685138)
  - [获奖延期（30 票 / 17 评论）](https://www.kaggle.com/competitions/med-gemma-impact-challenge/discussion/684112)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/med-gemma-impact-challenge.md)
- **nvidia-nemotron-model-reasoning-challenge**（nlp/Featured｜NVIDIA Nemotron Metric）
  - [进度奖（huikang，241 票）](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689915)
  - [1st（140 票）](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/709231)
  - [2nd](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/711703)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nvidia-nemotron-model-reasoning-challenge.md)
- **openai-gpt-oss-20b-red-teaming**（nlp/Featured｜）
  - [获奖公布与评审说明（24 票 / 91 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608537)
  - [攻击方法分层分类（4 票 / 5 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608997)
  - [官方欢迎帖（39 票 / 50 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/596882)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/openai-gpt-oss-20b-red-teaming.md)
- **kore-2022**（sim-agent/Featured｜kore_fleets）
  - [1st（49 票）](https://www.kaggle.com/competitions/kore-2022/discussion/340035)
  - [20th 经济模型（23 票）](https://www.kaggle.com/competitions/kore-2022/discussion/339972)
  - [13th 模仿学习（38 票）](https://www.kaggle.com/competitions/kore-2022/discussion/337476)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/kore-2022.md)
- **kore-2022-beta**（sim-agent/Playground｜kore_fleets）
  - [1st 方案（58 票 / 24 评论）](https://www.kaggle.com/competitions/kore-2022-beta/discussion/317737)
  - [DQN tf.js 基线（14 票 / 1 评论）](https://www.kaggle.com/competitions/kore-2022-beta/discussion/317289)
  - [社区反思（11 票 / 0 评论）](https://www.kaggle.com/competitions/kore-2022-beta/discussion/317955)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/kore-2022-beta.md)
- **lux-ai-season-2-neurips-stage-2**（sim-agent/Featured｜lux_ai_s2）
  - [PPO using Jux 方案（4 票 / 4 评论）](https://www.kaggle.com/competitions/lux-ai-season-2-neurips-stage-2/discussion/459891)
  - [上手资源汇编（16 票 / 0 评论）](https://www.kaggle.com/competitions/lux-ai-season-2-neurips-stage-2/discussion/442050)
  - [基线/数据/公开代码（3 票 / 3 评论）](https://www.kaggle.com/competitions/lux-ai-season-2-neurips-stage-2/discussion/438939)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/lux-ai-season-2-neurips-stage-2.md)
- **maze-crawler**（sim-agent/Playground｜crawl）
  - [1st 方案（11 票 / 4 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717120)
  - [3rd 方案（1 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/718158)
  - [7th 方案（3 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717177)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/maze-crawler.md)
- **pokemon-tcg-ai-battle**（sim-agent/Featured｜cabt_bo1）
  - [引擎裁定请求（103 票）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/711737)
  - [引擎源码发布（127 票）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/717141)
  - [分享时机（16 票）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/discussion/733137)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/pokemon-tcg-ai-battle.md)
- **pokemon-tcg-ai-battle-challenge-strategy**（sim-agent/Featured｜）
  - [获奖与评审说明（19 票 / 6 评论）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/742692)
  - [官方欢迎（25 票 / 6 评论）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/708588)
  - [迟报名资格求助（6 票 / 3 评论）](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/discussion/735276)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/pokemon-tcg-ai-battle-challenge-strategy.md)
- **santa-2024**（sim-agent/Featured｜Santa 2024 Metric）
  - [批量困惑度（92 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548249)
  - [1st（85 票，正文仅 repo 链接）](https://www.kaggle.com/competitions/santa-2024/discussion/560560)
  - [SA 总论 255.9（59 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548476)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2024.md)
- **playground-series-s3e14**（tabular/Playground｜Mean Absolute Error）
  - [1st（133 票 / 57 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/410627)
  - [后处理技巧（80 票 / 18 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/407327)
  - [4th hillclimbers（50 票 / 16 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/410639)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e14.md)
- **playground-series-s3e25**（tabular/Playground｜Median Absolute Error）
  - [样本权重调优（74 票 / 35 评论）](https://www.kaggle.com/competitions/playground-series-s3e25/discussion/455888)
  - [数据分箱事实（54 票 / 42 评论）](https://www.kaggle.com/competitions/playground-series-s3e25/discussion/457631)
  - [起步参考（43 票 / 13 评论）](https://www.kaggle.com/competitions/playground-series-s3e25/discussion/455241)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e25.md)
- **playground-series-s3e8**（tabular/Playground｜Root Mean Squared Error）
  - [8th（26 票 / 7 评论）](https://www.kaggle.com/competitions/playground-series-s3e8/discussion/392860)
  - [2nd（27 票 / 10 评论）](https://www.kaggle.com/competitions/playground-series-s3e8/discussion/392828)
  - [3rd（26 票 / 11 评论）](https://www.kaggle.com/competitions/playground-series-s3e8/discussion/392824)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e8.md)
- **playground-series-s3e9**（tabular/Playground｜Root Mean Squared Error）
  - [1st：CV 与多样性赢（89 票 / 50 评论）](https://www.kaggle.com/competitions/playground-series-s3e9/discussion/394592)
  - [12th：六步流程（20 票 / 4 评论）](https://www.kaggle.com/competitions/playground-series-s3e9/discussion/394600)
  - [44th：LinearRegression 派生特征（8 票 / 0 评论）](https://www.kaggle.com/competitions/playground-series-s3e9/discussion/394641)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e9.md)
- **playground-series-s5e9**（tabular/Playground｜Mean Squared Error）
  - [随机目标检验（64 票 / 29 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/604028)
  - [MIR 领域背景（28 票 / 4 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/603307)
  - [26th FE+伪标签+残差（16 票 / 10 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/610264)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s5e9.md)
