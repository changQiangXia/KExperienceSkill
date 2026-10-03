# 顶层规律速查（60 条）

> 从 KStarter 的 264 场深读 + L1–L133 + T1–T37 中挑出对"上分"最直接可用的 60 条。
> 用法：开赛/卡分时从上往下扫，找当前症状对应的条目；每条后的 slug 可回原仓库核对。

## A. 验证与榜单（15 条）

1. CV 与 LB 不同向时，先修验证再调模型（s3e9）。
2. CV 5407 vs 公榜 721：CV 是测量，公榜是随机变量；提交 ≤2 次（s3e9）。
3. 公榜只占 10% 测试时，以验证分选模（geolifeclef）。
4. 分带极窄（26.38–26.41）时，LB 微差无信息量（s5e9）。
5. 实体整体落在 train 或 test 时，GroupKFold 才诚实；分数更低≠更差（scrabble）。
6. 同 hospital_number 会死多次：实体键可能是合成伪影（s3e22）。
7. 合成赛先做随机目标 z 检验；原数据无信号就转生成痕迹（s5e9，z=-0.83）。
8. 原数据合并前先对抗验证（s3e18）。
9. 指标实现要自己单测；官方 metric 也可能有 bug（fathomnet）。
10. 逐列 AUC vs 堆叠 GINI 口径不同，选模结论会反转（s3e18）。
11. 公榜高私榜崩时，用提交组合对冲（s3e22 七区域）。
12. 前 11 名有 7 队只提交 1–2 次：少而准的提交是纪律（s3e22）。
13. public LB 是测量仪，不是目标函数（T3/T10）。
14. 探榜是测量不是得分；随机种子探针通常只测噪声（T11）。
15. CV-LB 相关性未建立前，所有"LB 提升"都先当噪声。

## B. 指标与后处理（10 条）

16. MedAE 只看中位数那个样本；两端降权 + OOF 扫描阈值可 +0.03（s3e25）。
17. 9 档 ±0.25 覆盖 89.5%；猜对约 56% 即 0.25（s3e25）。
18. 已知偏差方向时先试单参数 logit 平移（Nov2022 −1.17，CV 0.6476→0.5281）。
19. 小数据上 isotonic 易过拟合阶梯，单参数校准更稳（T2）。
20. 排序指标用秩平均/校准不变融合（L14）。
21. 分组合法性裁剪比"清洗训练数据"更有效（S3E8 +1.1）。
22. 目标有物理界时先 clip；但确认模型是否已在压缩极值（s3e8）。
23. 阈值型指标在 OOF 上搜阈值 + 先验校正（L22/L25）。
24. 容差型指标可做 target 整形/两极化流水线（L37）。
25. 后处理阈值用 public LB 搜 = 私榜高风险。

## C. 数据与特征（10 条）

26. 先查实体/时间/重复三件事，再做特征（L2/L116）。
27. 哨兵值/坏值（-666、-1、空串）先扫描再建模（s3e18）。
28. test 端 OOD 类别用频率编码，不硬编码（s3e18）。
29. 缺失可能携带信息（NaN 与目标相关时不能均值填补）（s4e12）。
30. 粗标签传播/邻域换标可解决 presence-only 病态（geolifeclef-2022 +2%）。
31. 长尾"什么都不做"可能最好——先确认测试分布（geolifeclef-2022）。
32. 极端长尾可把 <N 图类别归并 unknown（herbarium/fathomnet）。
33. 高分辨率 + 域适应（IBN/直方图）+ 度量损失是视觉组合拳（sorghum）。
34. 遮挡/掩码要按测试分布增强（hotel-id BlendFlip +0.03–0.04 mAP）。
35. 大模型 embedding + GBDT 是低算力高性价比路线（planttraits 9th 0.51238）。

## D. 模型、集成与调参（8 条）

36. 低信号场次堆大集成会过拟合；设"够了就停"预算（s5e9/T28）。
37. 集成必须跨家族：6 树 + 1 非树（s3e23 0.79220 > 单模 0.79136）。
38. 爬山权重允许负值，且只在 OOF 上调（s3e23 #2）。
39. Optuna 参数换 KFold 种子后不存活 = 伪最优（s3e9）。
40. 多目标先做"拆 vs 合"实验：EC1 树模型、EC2 Bagged KNN 排序反转（s3e18）。
41. 身份辅助任务（物种/聚类）能显著提升群体均值回归（planttraits）。
42. 微调用分层学习率：头高 LR 早 warmup，骨干逐层降（planttraits）。
43. 伪标签只在同折 CV 对照下启用；低信号场次收益不可证（s5e9/T30）。

## E. 提交、平台与收官（9 条）

44. 列顺序必须与 sample_submission 完全一致（planttraits）。
45. zip/PostProcessorKernel/schema 先做最小提交演练（gan/autonomous-agent）。
46. 提交按钮会失效；提前 48h 提交并截图留凭证（bigquery）。
47. 平台能力配给（额度/配额/挂载/地区）是第一约束（gemini/bigquery/makersuite）。
48. LLM 预算（$2/60min）要写进 agent 计划（autonomous-agent）。
49. Agent schema 用官方校验器本地过一遍再消耗提交（autonomous-agent）。
50. 模型-工具兼容表先读：单工具/无工具/温度参数限制（autonomous-agent）。
51. 最后 48h 不引入新方法，只做选择/对冲/格式（收官协议）。
52. 冻结前重跑一次端到端推理链路，确保提交与候选一致。

## F. Agent/LLM 与安全（8 条）

53. LLM 给的引用/来源必须逐条核验（openai-to-z 幻觉）。
54. LLM 辅助环境移植需要人工验证语义（maze 3rd）。
55. CoT 可被伪造；工具/通道可能出现拒绝不一致（gpt-oss）。
56. 大量漏洞只在 reasoning_effort=low 复现，high 正常拒绝（gpt-oss）。
57. 红队/安全赛按"增量危害"评估，而不是攻击成功率（gpt-oss）。
58. 评审制赛道按"观察→改动→验证"闭环写作（pokemon-strategy）。
59. 评审不公开分项时，交付要自包含、可复现（T36）。
60. 规则含社区投票时，早发布 + 维护比后期拉票有效（kaggle-measuring-agi）。

## 张力速记（每题选边）

- T1 单模 vs 大集成：按候选可用性与预算分层。
- T2 单参数 vs 灵活校准：已知结构用单参数。
- T3/T10/T31 信 CV vs 信 LB：先证明 CV 无泄漏与相关性。
- T28 随机目标 vs 合成痕迹：先检验，再决定投入。
- T29 多目标拆 vs 合：先做目标级模型选择实验。
- T30 伪标签增益 vs 不可证：没有同折对照就不认。
- T32 主动终局 vs 被动 tiebreak：规则明确时主动构造。
- T33 规则型 vs RL：先规则基线，再局部 RL。
- T34 LLM 加速器 vs 风险源：输出当不可信输入。
- T35 API 成本 vs 额度/自部署：赛前做成本模型。
- T37 窄分带信号 vs 噪声：分带≈噪声时不用 LB 选模。

## 链接索引（来源佐证）

> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 3 条）+ KStarter 深读原文。

- **fathomnet-out-of-sample-detection**（cv/Research｜FathomNet 2023）
  - [4th 方案（5 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/413092)
  - [标签错误讨论（6 票 / 2 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/407400)
  - [metric 修复与重算（3 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/404769)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/fathomnet-out-of-sample-detection.md)
- **geolifeclef-2022-lifeclef-2022-fgvc9**（cv/Research｜MeanBestErrorAtK）
  - [1st 方案（11 票 / 5 评论）](https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/327055)
  - [2nd 方案（4 票 / 0 评论）](https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/328637)
  - [working note 与纪律（3 票 / 0 评论）](https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/325984)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/geolifeclef-2022-lifeclef-2022-fgvc9.md)
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
- **sorghum-id-fgvc-9**（cv/Research｜Categorization Accuracy）
  - [3rd 方案（12 票 / 7 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/328593)
  - [2nd 方案（5 票 / 0 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329414)
  - [1st 方案（6 票 / 4 评论）](https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329049)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/sorghum-id-fgvc-9.md)
- **bigquery-ai-hackathon**（nlp/Featured｜）
  - [获奖与评审流程（8 票 / 12 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/612730)
  - [云额度支持（13 票 / 37 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/598576)
  - [官方欢迎（24 票 / 49 评论）](https://www.kaggle.com/competitions/bigquery-ai-hackathon/discussion/598594)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/bigquery-ai-hackathon.md)
- **gemini-3**（nlp/Featured｜）
  - [官方欢迎帖（49 票 / 84 评论）](https://www.kaggle.com/competitions/gemini-3/discussion/651844)
  - [write-up 观感（44 票 / 89 评论）](https://www.kaggle.com/competitions/gemini-3/discussion/662567)
  - [评审时间线更新（69 票 / 207 评论）](https://www.kaggle.com/competitions/gemini-3/discussion/667609)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/gemini-3.md)
- **gemini-long-context**（nlp/Community｜）
  - [获奖公布（19 票 / 33 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/552419)
  - [起步指引（13 票 / 27 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/541152)
  - [Save&Run All 挂载提醒（22 票 / 1 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/541420)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/gemini-long-context.md)
- **kaggle-measuring-agi**（nlp/Featured｜）
  - [获奖公布（22 票 / 43 评论）](https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion/724918)
  - [收官说明（25 票 / 41 评论）](https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion/692562)
  - [社区投票权重质疑（28 票 / 5 评论）](https://www.kaggle.com/competitions/kaggle-measuring-agi/discussion/683674)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/kaggle-measuring-agi.md)
- **openai-gpt-oss-20b-red-teaming**（nlp/Featured｜）
  - [获奖公布与评审说明（24 票 / 91 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608537)
  - [攻击方法分层分类（4 票 / 5 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608997)
  - [官方欢迎帖（39 票 / 50 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/596882)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/openai-gpt-oss-20b-red-teaming.md)
- **autonomous-agent-prediction-beta**（sim-agent/Playground｜Autonomous Agent Prediction Beta Metric）
  - [3rd 方案（6 票 / 2 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/737407)
  - [官方失败原因清单（9 票 / 11 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/723907)
  - [$2 预算讨论（11 票 / 7 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/723806)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/autonomous-agent-prediction-beta.md)
- **maze-crawler**（sim-agent/Playground｜crawl）
  - [1st 方案（11 票 / 4 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717120)
  - [3rd 方案（1 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/718158)
  - [7th 方案（3 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717177)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/maze-crawler.md)
- **playground-series-s3e18**（tabular/Playground｜Roc Auc Score）
  - ["不是多标签，而是两场比赛"（39 票 / 14 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/420127)
  - [EC2 最佳单模型 Bagged KNN（30 票 / 24 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/420822)
  - [中期总结（41 票 / 2 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/421462)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e18.md)
- **playground-series-s3e22**（tabular/Playground｜F1 Score）
  - [Onboarding materials（62 票 / 28 评论）](https://www.kaggle.com/competitions/playground-series-s3e22/discussion/438603)
  - [兽医 AI/Cox 文献（32 票 / 4 评论）](https://www.kaggle.com/competitions/playground-series-s3e22/discussion/438620)
  - [Inferring the LB shakeup（36 票 / 11 评论）](https://www.kaggle.com/competitions/playground-series-s3e22/discussion/444654)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e22.md)
- **playground-series-s3e23**（tabular/Playground｜Roc Auc Score）
  - [胜利说明书（117 票 / 49 评论）](https://www.kaggle.com/competitions/playground-series-s3e23/discussion/445245)
  - [#2 八模型集成（95 票 / 42 评论）](https://www.kaggle.com/competitions/playground-series-s3e23/discussion/450315)
  - [爬山集成教程（48 票 / 19 评论）](https://www.kaggle.com/competitions/playground-series-s3e23/discussion/444784)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e23.md)
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
- **playground-series-s4e12**（tabular/Playground｜Root Mean Squared Logarithmic Error）
  - [1st（230 行处）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/554328)
  - [NAN 与目标（126 票）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/552165)
  - [Rank2 暴力集成（27 票）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/554505)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s4e12.md)
- **playground-series-s5e9**（tabular/Playground｜Mean Squared Error）
  - [随机目标检验（64 票 / 29 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/604028)
  - [MIR 领域背景（28 票 / 4 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/603307)
  - [26th FE+伪标签+残差（16 票 / 10 评论）](https://www.kaggle.com/competitions/playground-series-s5e9/discussion/610264)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s5e9.md)
- **scrabble-player-rating**（tabular/Playground｜Root Mean Squared Error）
  - [赛后复盘与 CV 问题（3 票 / 2 评论）](https://www.kaggle.com/competitions/scrabble-player-rating/discussion/372554)
  - [公开 kernel 清单（9 票 / 1 评论）](https://www.kaggle.com/competitions/scrabble-player-rating/discussion/362744)
  - [官方欢迎（16 票 / 3 评论）](https://www.kaggle.com/competitions/scrabble-player-rating/discussion/362735)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/scrabble-player-rating.md)
- **tabular-playground-series-nov-2022**（tabular/Playground｜Log Loss）
  - [1st](https://www.kaggle.com/competitions/tabular-playground-series-nov-2022/discussion/369674)
  - [3rd](https://www.kaggle.com/competitions/tabular-playground-series-nov-2022/discussion/370126)
  - [7th](https://www.kaggle.com/competitions/tabular-playground-series-nov-2022/discussion/369731)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/tabular-playground-series-nov-2022.md)
