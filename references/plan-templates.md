# 改进方案模板（按赛型）

> 用法：选一个赛型模板，套 `improvement-plan-protocol.md` 的假设表；默认实验是**起点**，不是全部。

## 1. 表格回归（RMSE/MAE/MedAE/分位）

```text
Competition Card：指标结构（均值/中位数/分位）｜目标离散度｜实体/时间切分｜提交限制
默认实验 1：metric 单测 + 目标唯一值/分位统计（30min）
默认实验 2：两端样本权重 / 档位吸附（OOF 对照）
默认实验 3：清洗三件套（哨兵值/重复/近常数）+ OOD 频率编码
默认实验 4：GBDT 基线 + 跨家族多样性（线性/核）
关键检查：随机目标检验（合成赛）｜CV-LB 样本量｜分组 CV
常用案例：s3e25 / s3e14 / s5e9 / s3e9 / s3e8
```

## 2. 表格分类（AUC/F1/LogLoss）

```text
Competition Card：类别分布/阈值型还是排序型｜多标签还是多分类｜实体键
默认实验 1：指标实现 + 阈值/先验口径
默认实验 2：分层/多标签 CV + 实体分组审计
默认实验 3：类别不平衡策略对照（损失/采样/阈值）
默认实验 4：跨家族集成 + 校准（若 LogLoss）
关键检查：头部子群分数｜阈值附近样本｜重复实体
常用案例：s3e18 / s3e22 / amex / feedback-prize
```

## 3. 时序 / 金融 / 在线

```text
Competition Card：预测窗口/评测频率/在线训练限制｜非平稳性｜指标（Sharpe/capture/zero-mean R²）
默认实验 1：复刻评测窗口的时间 CV（含 gap）
默认实验 2：简单基线（Lag/GBDT/MLP）+ "截至当前"滚动特征
默认实验 3：在线更新 vs 不更新的对照
默认实验 4：组合/风险层（若指标是 Sharpe）
关键检查：时间穿越｜时延预算｜分布漂移
常用案例：jane-street / optiver / hull / amex
```

## 4. CV 分类 / 细粒度

```text
Competition Card：域差（采集/设备/光照/掩码）｜分辨率｜类间相似度｜长尾
默认实验 1：分辨率阶梯（224→384→512）
默认实验 2：域适应单项（IBN/直方图/颜色归一化）
默认实验 3：度量损失（ArcFace/subcenter）+ 分类头
默认实验 4：域内预训练权重对照
默认实验 5：TTA / 多折 / 多骨干融合
关键检查：掩码/遮挡分布｜长尾归并｜外部数据许可
常用案例：sorghum / hotel-id / herbarium / planttraits
```

## 5. CV 检测 / 分割 / 计数 / 检索

```text
Competition Card：指标（AP/F1/MAE/拓扑/容差）｜GT 可得性｜阈值/后处理空间
默认实验 1：指标结构分类（体素/拓扑/容差/计数）
默认实验 2：后处理链（去小连通/补洞/裁剪/阈值分层）
默认实验 3：检测/分割/计数多阶段系统
默认实验 4：检索路线对照（logits/embedding+kNN）
关键检查：密度分层｜OOD/未知类｜图像 I/O 与数据版本
常用案例：vesuvius / hubmap / iwildcam / fathomnet / hotel-id
```

## 6. NLP / LLM

```text
Competition Card：任务形态（理解/生成/检索/推理/工具）｜评测约束（token/时延/格式）｜可否微调/工具
默认实验 1：约束测试套件 + 输出解析
默认实验 2：强基线（微调或大候选 + 投票）
默认实验 3：弱项类别表 + 合成数据（若可验证）
默认实验 4：蒸馏/校准（若推理受限）
默认实验 5：后处理（强制格式/拒绝采样/阈值）
关键检查：引用核验｜泄漏/私有数据｜推理预算
常用案例：aimo / nemotron / lmsys / AI4Code / feedback-prize
```

## 7. 模拟对战 / RL Agent

```text
Competition Card：终局规则/结算｜动作空间｜可否本地模拟｜提交 slot 限制
默认实验 1：终局规则表 + 规则基线（评分函数/兵力计算）
默认实验 2：快模拟器或轻量自对弈
默认实验 3：课程 + 热启动
默认实验 4：对手多样性 + 镜像对局
默认实验 5：KL/资源/胜率曲线早停
关键检查：环境一致性｜随机种子｜提交 slot 策略
常用案例：lux / maze / kore / santa
```

## 8. 评审制 / 研究 / Hackathon / Agent-Config

```text
Competition Card：rubric/评审流程｜交付格式（字数/页数/视频/模型）｜可复现要求｜预算/配额
默认实验 1：rubric → 交付清单映射
默认实验 2：陌生环境冷启动复现
默认实验 3：消融 + 失败路径 + 图表
默认实验 4：叙事/视频/文档整合
默认实验 5：预算/配额/提交保护（提前 48h）
关键检查：公开可访问｜私有依赖｜作者归属/资格
常用案例：pokemon-strategy / bigquery / gpt-oss / med-gemma / geolifeclef
```

## 链接索引（来源佐证）

> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 3 条）+ KStarter 深读原文。

- **fathomnet-out-of-sample-detection**（cv/Research｜FathomNet 2023）
  - [4th 方案（5 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/413092)
  - [标签错误讨论（6 票 / 2 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/407400)
  - [metric 修复与重算（3 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/404769)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/fathomnet-out-of-sample-detection.md)
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
- **AI4Code**（nlp/Featured｜AI4CodeKendallTau）
  - [领域理解（328905）](https://www.kaggle.com/competitions/AI4Code/discussion/328905)
  - [2nd（343659）](https://www.kaggle.com/competitions/AI4Code/discussion/343659)
  - [11th Nested Transformers（343680）](https://www.kaggle.com/competitions/AI4Code/discussion/343680)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/AI4Code.md)
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
- **maze-crawler**（sim-agent/Playground｜crawl）
  - [1st 方案（11 票 / 4 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717120)
  - [3rd 方案（1 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/718158)
  - [7th 方案（3 票 / 0 评论）](https://www.kaggle.com/competitions/maze-crawler/discussion/717177)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/maze-crawler.md)
- **santa-2021**（sim-agent/Featured｜Santa's Superpermutations 2021）
  - [3rd（39 票）](https://www.kaggle.com/competitions/santa-2021/discussion/300509)
  - [4th by hand](https://www.kaggle.com/competitions/santa-2021/discussion/300543)
  - [解析解与背景（49 票）](https://www.kaggle.com/competitions/santa-2021/discussion/288124)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2021.md)
- **santa-2022**（sim-agent/Featured｜Santa's Print Shop 2022）
  - [1st（80 票）](https://www.kaggle.com/competitions/santa-2022/discussion/379167)
  - [2nd（81 票）](https://www.kaggle.com/competitions/santa-2022/discussion/379086)
  - [4th（73 票）](https://www.kaggle.com/competitions/santa-2022/discussion/379080)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2022.md)
- **santa-2023**（sim-agent/Featured｜Santa 2023 Metric）
  - [1st（125 票）](https://www.kaggle.com/competitions/santa-2023/discussion/472405)
  - [上手帖（98 票）](https://www.kaggle.com/competitions/santa-2023/discussion/462236)
  - [4th 仓库与分数（64 票）](https://www.kaggle.com/competitions/santa-2023/discussion/472386)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2023.md)
- **santa-2024**（sim-agent/Featured｜Santa 2024 Metric）
  - [批量困惑度（92 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548249)
  - [1st（85 票，正文仅 repo 链接）](https://www.kaggle.com/competitions/santa-2024/discussion/560560)
  - [SA 总论 255.9（59 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548476)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2024.md)
- **santa-2025**（sim-agent/Featured｜Santa 2025 Metric）
  - [SA Tips（terry_u16，114 票）](https://www.kaggle.com/competitions/santa-2025/discussion/640894)
  - [1st（Jeroen Cottaar，111 票）](https://www.kaggle.com/competitions/santa-2025/discussion/672465)
  - [1st 预览（84 票）](https://www.kaggle.com/competitions/santa-2025/discussion/671058)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2025.md)
- **amex-default-prediction**（tabular/Featured｜Amex Custom Gini And X% Percentage Capture）
  - [1st](https://www.kaggle.com/competitions/amex-default-prediction/discussion/348111)
  - [2nd](https://www.kaggle.com/competitions/amex-default-prediction/discussion/347637)
  - [3rd](https://www.kaggle.com/competitions/amex-default-prediction/discussion/349741)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/amex-default-prediction.md)
- **hull-tactical-market-prediction**（tabular/Featured｜Hull Competition Sharpe）
  - [4th（39 票）](https://www.kaggle.com/competitions/hull-tactical-market-prediction/discussion/718664)
  - [2.6 公榜方案（663043）](https://www.kaggle.com/competitions/hull-tactical-market-prediction/discussion/663043)
  - [61st（715547）](https://www.kaggle.com/competitions/hull-tactical-market-prediction/discussion/715547)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/hull-tactical-market-prediction.md)
- **jane-street-real-time-market-data-forecasting**（tabular/Featured｜Jane Street Zero-Mean R2）
  - [私榜 8th（295 票）](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting/discussion/556542)
  - [公榜 17th（57 票）](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting/discussion/556541)
  - [私榜 162nd（11 票）](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting/discussion/589829)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/jane-street-real-time-market-data-forecasting.md)
- **optiver-realized-volatility-prediction**（tabular/Featured｜Root Mean Square Percentage Error）
  - [1st](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/discussion/274970)
  - [消融研究](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/discussion/302626)
  - [15th](https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/discussion/276137)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/optiver-realized-volatility-prediction.md)
- **optiver-trading-at-the-close**（tabular/Featured｜Mean Columnwise Mean Absolute Error）
  - [1st（338 票）](https://www.kaggle.com/competitions/optiver-trading-at-the-close/discussion/487446)
  - [9th（66 票）](https://www.kaggle.com/competitions/optiver-trading-at-the-close/discussion/486868)
  - [特征加速（54 票）](https://www.kaggle.com/competitions/optiver-trading-at-the-close/discussion/451735)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/optiver-trading-at-the-close.md)
- **playground-series-s3e14**（tabular/Playground｜Mean Absolute Error）
  - [1st（133 票 / 57 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/410627)
  - [后处理技巧（80 票 / 18 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/407327)
  - [4th hillclimbers（50 票 / 16 评论）](https://www.kaggle.com/competitions/playground-series-s3e14/discussion/410639)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e14.md)
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
