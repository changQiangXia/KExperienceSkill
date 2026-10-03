# 按比赛类型找人（前 50 选手经验层）

> 快照 2026-10-04，来源 KStarter `99501882bd14`；复现度 = 具体技法标签 × 同领域 × 独立证据单位（同队合并）；标注 `严 N` 的是技法组合级复现（同领域另一单位同时复现 ≥2 个具体技法），优先采纳。
> 完整断言与逐字引用见 KStarter `people/claims/gm_claims.csv`；领域 playbook 见 `analysis/people/playbooks/`。
> 查询：`python scripts/gm_claim_search.py --domain cv --strict-units 2`。

## 视觉 CV

**先找人**：[@christofhenkel](https://www.kaggle.com/christofhenkel)（18 条）、[@ren4yu](https://www.kaggle.com/ren4yu)（14 条）、[@tascj0](https://www.kaggle.com/tascj0)（10 条）、[@cdeotte](https://www.kaggle.com/cdeotte)（7 条）、[@conjuring92](https://www.kaggle.com/conjuring92)（5 条）、[@philippsinger](https://www.kaggle.com/philippsinger)（5 条）

**复现决策项（按证据单位数）**：
- **后处理/校准**（12 单位 / 严 10）：7 折按 experiment 划分；每 epoch 在验证 experiment 上网格搜索类阈值；7 折后取 OOF，用其他 6 折拟合每折阈值，再平均 f4 曲线取最优阈 —— @christofhenkel｜A｜[原文](https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561510)
- **损失设计**（11 单位 / 严 10）：总损失为三项加权和：Aesthetic Predictor 负分（最大化美观）+ SigLIP 余弦相似度（渲染 SVG 与目标位图）+ MSE（与初始位图）；Adam + c —— @cnumber｜B｜[原文](https://www.kaggle.com/competitions/drawing-with-llms/discussion/581024)
- **数据增广**（10 单位 / 严 6）：增广在缩放前做：vflip、hflip、transpose、shift、scale、rotate、grid distortion、affine；缩放后只做 grid shuff —— @christofhenkel｜A｜[原文](https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/391208)
- **TTA**（8 单位 / 严 6）：发现 polygon 转 binary mask 时最左点未包含而最右点包含，导致图像与 mask 错位；给出原始、普通翻转、正确翻转三种图文序列对照 —— @tascj0｜A｜[原文](https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430479)
- **时间/分组切分**（7 单位 / 严 5）：匹配 patch 高宽、只沿深度滑窗：快 4 倍；用高 overlap 0.875 与更多 TTA；边缘预测用 roi_weight_map 降权（中间 40% 权重 1.0， —— @brendanartley｜A｜[原文](https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583143)

## 文本 NLP

**先找人**：[@cdeotte](https://www.kaggle.com/cdeotte)（32 条）、[@philippsinger](https://www.kaggle.com/philippsinger)（16 条）、[@conjuring92](https://www.kaggle.com/conjuring92)（14 条）、[@tascj0](https://www.kaggle.com/tascj0)（13 条）、[@wowfattie](https://www.kaggle.com/wowfattie)（7 条）、[@darraghdog](https://www.kaggle.com/darraghdog)（6 条）

**复现决策项（按证据单位数）**：
- **集成权重选择**（16 单位 / 严 6）：用 hill climbing（从最好单模开始，逐轮尝试所有模型与 -0.5 到 0.5 的权重）选模型并定权；允许负权重 —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/feedback-prize-english-language-learning/discussion/369609)
- **损失设计**（14 单位 / 严 10）：蒸馏损失：0.15×有标注 BCE 加 0.15×教师伪标签 BCE 加 0.7×未标注伪标签 BCE；文献与学生超过教师的可能性支持该设计 —— @conjuring92｜A｜[原文](https://www.kaggle.com/competitions/nbme-score-clinical-patient-notes/discussion/322832)
- **长序列/上下文**（13 单位 / 严 7）：两阶段检索：先让模型找相关单测文件，再给这些文件的函数/类骨架，让它挑要看的类/函数/方法；同时提取 imports；5 个候选中 1 个给全 context、1 个只给 im —— @arc144｜A｜[原文](https://www.kaggle.com/competitions/konwinski-prize/discussion/568884)
- **后处理/校准**（11 单位 / 严 8）：自定义阈值（如 1/2 用 1.7、5/6 用 4.9）同时：过拟合标签、纠正不平衡误差、优化 QWK；阈值随 seed 波动大，必须用 3 seeds 算，用 scipy P —— @ferdinandlimburg｜A｜[原文](https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2/discussion/516791)
- **合成/生成数据**（10 单位 / 严 5）：训练 seq2seq T5-large：输入为效果标签加 discourse 类型加 prompt 加左右上下文，输出为 discourse 文本；生成样本按 0-50% 比例 —— @conjuring92｜A｜[原文](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347433)
- **外部数据**（9 单位 / 严 3）：对抗验证 train vs test AUC 0.65 到 0.675；本地用 51% persuade 加 18% non-persuade 训练、31% non-persu —— @tascj0｜A｜[原文](https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2/discussion/516639)
- **检索/RAG**（9 单位 / 严 7）：早期单 DeBERTa-v3-large 加多条 RAG pipeline；发现新增 RAG 比加 DeBERTa 更提分 → 加速 RAG 加 DeBERTa：GPU Fai —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/kaggle-llm-science-exam/discussion/446318)
- **伪标签/自训练**（9 单位 / 严 3）：对相关 misconception 聚类（如 linear 系列），让 Claude 生成更多例子并附 5 到 8 个相关 MCQ；先用竞赛数据微调两个 72B 点式模型并集成 —— @conjuring92｜A｜[原文](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics/discussion/551402)

## 表格/结构化

**先找人**：[@cdeotte](https://www.kaggle.com/cdeotte)（50 条）、[@hydantess](https://www.kaggle.com/hydantess)（7 条）、[@aerdem4](https://www.kaggle.com/aerdem4)（5 条）、[@arc144](https://www.kaggle.com/arc144)（5 条）、[@takoihiraokazu](https://www.kaggle.com/takoihiraokazu)（5 条）、[@jsday96](https://www.kaggle.com/jsday96)（4 条）

**复现决策项（按证据单位数）**：
- **集成权重选择**（9 单位 / 严 3）：2×XGB 加 3×TabM 加 2×XGB（stacked over 3×TabM）共 7 模型 hill climbing；TabM 变体含对原始生成函数预测残差的版本；另 —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/playground-series-s5e10/discussion/614079)
- **损失设计**（8 单位 / 严 6）：主损失用 GaussianNLLLoss（同时预测均值与方差，自动降低大方差样本权重，优于 SmoothL1；帧级加权无益）；辅助损失对预测 xy 的一阶/二阶差分（速度/加速 —— @chack3｜B｜[原文](https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/651604)
- **时间/分组切分**（7 单位 / 严 5）：核心是 groupby(COL1)[COL2].agg(STAT)：COL1 可用现有列、round 分箱或列拼接；COL2 常用 target（必须 nested folds —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/playground-series-s5e2/discussion/563743)
- **数据增广**（5 单位 / 严 3）：增广：特征级 random zero 加序列级 random mask；验证用最后 k 段（k=100、200、300） —— @hydantess｜A｜[原文](https://www.kaggle.com/competitions/ubiquant-market-prediction/discussion/338561)
- **伪标签/自训练**（4 单位 / 严 4）：用 BERT、Uni-Mol、AutoGluon、D-MPNN 集成给 PI1M 的 5 万个假想聚合物打伪标签；再用性质高低成对比较的排序分类任务预训练（相似对忽略 loss —— @jsday96｜A｜[原文](https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025/discussion/607947)
- **分组聚合特征**（4 单位 / 严 3）：核心是 groupby(COL1)[COL2].agg(STAT)：COL1 可用现有列、round 分箱或列拼接；COL2 常用 target（必须 nested folds —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/playground-series-s5e2/discussion/563743)

## 时间序列

**先找人**：[@cdeotte](https://www.kaggle.com/cdeotte)（7 条）、[@hydantess](https://www.kaggle.com/hydantess)（7 条）、[@aerdem4](https://www.kaggle.com/aerdem4)（5 条）、[@w5833946](https://www.kaggle.com/w5833946)（4 条）、[@takoihiraokazu](https://www.kaggle.com/takoihiraokazu)（3 条）、[@chack3](https://www.kaggle.com/chack3)（3 条）

**复现决策项（按证据单位数）**：
- **集成权重选择**（10 单位 / 严 7）：GRU + StratifiedGroupKFold by Subject + BCEWithLogits + AdamW 与 linear warmup（比 cosine C —— @takoihiraokazu｜A｜[原文](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction/discussion/416057)
- **时间/分组切分**（7 单位 / 严 4）：CNN 沿时间卷积学运动特征，再接 cross（agent-target）与 self（同鼠部件）注意力；用 2/4/8/16 秒四种滑窗（64/128/256/512 帧，s —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/MABe-mouse-behavior-detection/discussion/663029)
- **损失设计**（7 单位 / 严 7）：主损失用 GaussianNLLLoss（同时预测均值与方差，自动降低大方差样本权重，优于 SmoothL1；帧级加权无益）；辅助损失对预测 xy 的一阶/二阶差分（速度/加速 —— @chack3｜B｜[原文](https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/651604)
- **伪标签/自训练**（4 单位 / 严 4）：全 5 产品共训 15 epochs cosine；加 30 个假日 bool；用 2017/2018 的首轮预测做伪标签训第二轮、再训第三轮；5 seeds 取中位数；不用  —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/playground-series-s5e1/discussion/560549)
- **数据增广**（4 单位 / 严 4）：增广：特征级 random zero 加序列级 random mask；验证用最后 k 段（k=100、200、300） —— @hydantess｜A｜[原文](https://www.kaggle.com/competitions/ubiquant-market-prediction/discussion/338561)

## 语音/音频

**先找人**：[@cpmpml](https://www.kaggle.com/cpmpml)（5 条）、[@nikitababich](https://www.kaggle.com/nikitababich)（5 条）、[@christofhenkel](https://www.kaggle.com/christofhenkel)（5 条）、[@cdeotte](https://www.kaggle.com/cdeotte)（2 条）

**复现决策项（按证据单位数）**：
- **知识蒸馏**（2 单位 / 严 2）：即使同 backbone 换 head 或 label 设计也重新蒸馏；蒸馏 loss 非零带来差异 —— @nikitababich｜B｜[原文](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)

## 生物/医疗

**先找人**：[@cdeotte](https://www.kaggle.com/cdeotte)（20 条）、[@ren4yu](https://www.kaggle.com/ren4yu)（14 条）、[@christofhenkel](https://www.kaggle.com/christofhenkel)（13 条）、[@cpmpml](https://www.kaggle.com/cpmpml)（7 条）、[@aerdem4](https://www.kaggle.com/aerdem4)（6 条）、[@nikitababich](https://www.kaggle.com/nikitababich)（5 条）

**复现决策项（按证据单位数）**：
- **集成权重选择**（17 单位 / 严 14）：GRU + StratifiedGroupKFold by Subject + BCEWithLogits + AdamW 与 linear warmup（比 cosine C —— @takoihiraokazu｜A｜[原文](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction/discussion/416057)
- **损失设计**（17 单位 / 严 14）：蒸馏损失：0.15×有标注 BCE 加 0.15×教师伪标签 BCE 加 0.7×未标注伪标签 BCE；文献与学生超过教师的可能性支持该设计 —— @conjuring92｜A｜[原文](https://www.kaggle.com/competitions/nbme-score-clinical-patient-notes/discussion/322832)
- **后处理/校准**（12 单位 / 严 10）：7 折按 experiment 划分；每 epoch 在验证 experiment 上网格搜索类阈值；7 折后取 OOF，用其他 6 折拟合每折阈值，再平均 f4 曲线取最优阈 —— @christofhenkel｜A｜[原文](https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561510)
- **TTA**（11 单位 / 严 6）：增广：随机 resize 768 到 1536、flip、Rot90、亮度对比、HSV；TTA：resize 1024 与 1536 加 hvflip；集成同时作用于 regi —— @ren4yu｜A｜[原文](https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/428295)
- **时间/分组切分**（10 单位 / 严 7）：CNN 沿时间卷积学运动特征，再接 cross（agent-target）与 self（同鼠部件）注意力；用 2/4/8/16 秒四种滑窗（64/128/256/512 帧，s —— @cdeotte｜A｜[原文](https://www.kaggle.com/competitions/MABe-mouse-behavior-detection/discussion/663029)
- **伪标签/自训练**（9 单位 / 严 5）：二级训练用大 batch 128；策略一：每 batch 加 48×4=192 个带伪标签的 soundscape clip；策略二：每 batch 随机加 128 个伪标签样 —— @cpmpml｜A｜[原文](https://www.kaggle.com/competitions/birdclef-2024/discussion/511905)
- **数据增广**（7 单位 / 严 6）：增广在缩放前做：vflip、hflip、transpose、shift、scale、rotate、grid distortion、affine；缩放后只做 grid shuff —— @christofhenkel｜A｜[原文](https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/391208)

## 强化学习/博弈

**先找人**：[@pressman1](https://www.kaggle.com/pressman1)（6 条）、[@dipamc77](https://www.kaggle.com/dipamc77)（5 条）、[@yiheng](https://www.kaggle.com/yiheng)（4 条）、[@takoihiraokazu](https://www.kaggle.com/takoihiraokazu)（3 条）、[@cnumber](https://www.kaggle.com/cnumber)（3 条）、[@ferdinandlimburg](https://www.kaggle.com/ferdinandlimburg)（3 条）

**复现决策项（按证据单位数）**：
- **时间/分组切分**（7 单位 / 严 3）：level group 0-4 与 5-12 各一个模型（含目标特征、单模型），13-22 每个 target 单独模型；特征为每 session 的类别计数、数值统计量与下一 —— @takoihiraokazu｜A｜[原文](https://www.kaggle.com/competitions/predict-student-performance-from-game-play/discussion/420077)
- **混合精度/量化**（4 单位 / 严 3）：用 BF16 权重跑 GCG 生成候选，用 ridge 模型重排，再只在小子集上用真实 GGUF 评估；最终候选按真实 KV-cache 顺序评测；初始 margin 极大（G —— @xiaoz259｜A｜[原文](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/discussion/739181)

## 科学研究

**先找人**：[@jeroencottaar](https://www.kaggle.com/jeroencottaar)（8 条）、[@cdeotte](https://www.kaggle.com/cdeotte)（8 条）、[@tascj0](https://www.kaggle.com/tascj0)（7 条）、[@christofhenkel](https://www.kaggle.com/christofhenkel)（5 条）、[@dipamc77](https://www.kaggle.com/dipamc77)（5 条）、[@w5833946](https://www.kaggle.com/w5833946)（5 条）

**复现决策项（按证据单位数）**：
- **时间/分组切分**（7 单位 / 严 6）：12 个异步生成；前 5 个里 4 个答案一致就取消其余；完成 10/12 也提前停；每题基础 350 秒，剩余时间进共享池，下一题最多借 210 秒（共 560 秒） —— @darraghdog｜A｜[原文](https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-2/discussion/574765)
- **数据增广**（6 单位 / 严 2）：发现 polygon 转 binary mask 时最左点未包含而最右点包含，导致图像与 mask 错位；给出原始、普通翻转、正确翻转三种图文序列对照 —— @tascj0｜A｜[原文](https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430479)
- **贝叶斯/概率模型**（4 单位 / 严 4）：用多个 squared-exponential kernel 组合的 GP（按长度尺度调 sigma）；光谱漂移用 KISS-GP 稀疏化（否则 100k × 100k 稠密矩 —— @jeroencottaar｜A｜[原文](https://www.kaggle.com/competitions/ariel-data-challenge-2024/discussion/543853)
- **TTA**（3 单位 / 严 2）：发现 polygon 转 binary mask 时最左点未包含而最右点包含，导致图像与 mask 错位；给出原始、普通翻转、正确翻转三种图文序列对照 —— @tascj0｜A｜[原文](https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430479)

