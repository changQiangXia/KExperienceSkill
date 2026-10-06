# 案例书：cv（52 场）

> 由 KStarter 深读文档生成：每场含一句话重述、全量数字账、逐方案对照矩阵、共识/分歧与裁决全文、证据分级、悬案与失败学、图证路径、出处与外部题解。
> 用途：为新比赛找结构类比时，先读本册，再回 KStarter 深读原文核对。

## UBC-OCEAN — UBC-OCEAN 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Balanced Accuracy Score ｜ 队伍 1326 ｜ 截止 2024-01-03 ｜ Tier B ｜ 标签 cv,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/UBC-OCEAN.md
> 材料基础：`digests/UBC-OCEAN.md`（6 篇正文：1st Owkin 466455 / 13th 465358 / 8th 465382 / 基线 452165 / PNG 格式 452027 / 病理学家视角 445804；80 条主题索引）+ 7 张图

### 一句话重述
卵巢癌病理切片（WSI/TMA）五亚型 + Other 分类。真正的考点是**病理基础模型（Phikon/CTransPath/LUNIT）特征 + MIL 聚合 + 离群检测**；数据工程（PNG/分辨率/放大倍率）与 "Other 类" 是最大障碍。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（Owkin，65 票） | 流程：matter detection（Otsu/HSV）→ 切片（WSI 224px；TMA 448→224 对齐 20×）→ **Phikon 768 维特征** → Chowder MIL（50 模型/折集成）→ 校准 + 模型筛选 → 65 模型均值；**高熵预测判 Other**（公榜 0.59→0.64，Other 值 16.6 分）；获胜提交公/私 0.64/0.66（最佳私 0.68）；**微调 Phikon**（6.5M patches + iBOT + register tokens，2.5 天/epoch/2×P100）作多样性；发现 **8% 切片分辨率错误（×12 而非 ×20），LGSC 中 20% 受影响**；CV 0.8–0.9 vs LB 0.64–0.68（跨中心泛化差距） | 1st |
| 8th（49 票） | "先理解数据再设计方法"：WSI/TMA 分开处理；TMA 降采样 2× 对齐 WSI 物理尺度；TMA 用官方 mask 切片 + ArcFace 检索（覆盖 ~60% TMA）+ 6 分类模型兜底；healthy/dead 当 Other | 8th |
| 13th（48 票） | WSI 模型：10× 降采样 + Otsu + CTransPath/LUNIT-DINO 特征 + MIL（CLAM/DSMIL/加权和）；TMA 模型：ArcFace + ArcMargin 子中心 + Faiss 检索；**双重离群检测**（嵌入距离 + 概率分布）；不做颜色归一化 | 13th |
| 数据问题 | PNG 非金字塔（内存/时间灾难）；mpp/ICC 元数据被剥离；数据质量投诉帖（57 票）；病理学家视角（112 票） | 主题索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 8th | 13th |
| --- | --- | --- | --- |
| 特征 | Phikon（+微调版） | ArcFace 检索 + 多模型 | CTransPath + LUNIT-DINO |
| 聚合 | Chowder MIL（50/折） | 6 分类模型 + 检索 | CLAM/DSMIL/加权和 |
| WSI/TMA | 统一 20× 对齐 | 分开处理、2× 降采样对齐 | 分开处理、10× 降采样 |
| 离群 | 预测熵阈值 | ArcFace 距离 + healthy/dead | 嵌入距离 + 概率分布双阈值 |
| 颜色归一化 | 试过无效 | — | 不做（文献支持） |
| 私榜 | 0.66（最佳 0.68） | 8th | 13th |

### 共识 / 分歧 / 裁决
**共识一：病理领域基础模型 + MIL 是标准配方（3/3）**
Phikon / CTransPath / LUNIT-DINO 特征 + Chowder/CLAM/DSMIL/MeanPool 聚合；1st 甚至只留 Phikon+Chowder 就夺冠（Occam's razor）。**裁决**：数字病理已进入"FM 特征 + MIL"范式；不需要大量自训骨干（除非做领域微调）。置信度：高。

**共识二：离群/Other 类是最大单项（3/3）**
Other 值 16.6 分；1st 的熵阈值 +0.05 公榜；8th 的 ArcFace 检索；13th 的双阈值。**裁决**：balanced accuracy 下"不预测 Other"直接封顶；离群检测必须是独立模块，且阈值要校准（1st 无真 Other 样本只能用公榜/内部测试校准——风险点）。置信度：高。

**共识三：WSI 与 TMA 必须对齐物理尺度或分开建模（3/3）**
WSI 20×/TMA 40×；1st 把 TMA 448→224 对齐 20×；8th 降采样 2×；13th 分开。**裁决**：跨放大倍率是首要预处理；用一个模型吃两种输入需要显式对齐。置信度：高。

**共识四：颜色归一化收益否证（1st/13th）**
Vahadane/Reinhard 无提升（与文献一致）。**裁决**：在强 FM 特征下，染色归一化不是优先项。置信度：中高。

**分歧一：特征模型与 MIL 选择**
1st：Phikon 单特征 + Chowder；13th：多特征 + CLAM/DSMIL；8th：检索 + 多模型。**裁决**：都能进前列；差异主要在离群检测与集成策略，而非单点模型。置信度：中高。

**分歧二：超参调优 vs LB**
1st 的 Ray Tune 调参"CV 升、公榜降"→ 弃用；并强调模型筛选比全量集成有效。**裁决**：该场 CV 与 LB 脱节（跨中心），调参容易拟合训练中心；以提交反馈做轻量筛选更稳。置信度：高（1st 明证）。

**事件/数据质量**
PNG 非金字塔 + 元数据缺失 + 8% 分辨率错误 + 数据质量投诉（57 票）——**主办方数据工程缺陷**是本场的一大主题。**裁决**：参赛者需自行做"元数据考古"（分辨率为一等特征）。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的管线/分数/数据缺陷发现 | 自述 + 图 + 代码 + UMAP | 中高 |
| 8th/13th 的方法与分数 | 自述 + 图 | 中高 |
| Other 16.6 分与熵阈值 +0.05 | 自述（机制清晰） | 中高 |
| 颜色归一化无效 | 两队独立 + 文献 | 中 |
| 病理学家视角/数据质量 | 高票帖（未入库） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 病理学家视角（112 票）、数据质量投诉（57 票）、PNG 格式帖（45 票）未细读——医学先验与官方回应缺失。
- 2nd–7th 方案未收录；"Other" 类的官方真值与评分细节不完整。
- 微调 Phikon 的收益未单独消融（1st 只给合并提交分数）。

### 图证（KStarter 仓库内路径）
- ../../intel/UBC-OCEAN/bodies/466455_img/01.png — 1st 的流程总览

### 出处
- 1st Owkin（65 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/466455
- 13th（48 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/465358
- 8th（49 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/465382
- 基线（86 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/452165
- PNG 格式（45 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/452027
- 病理学家视角（112 票）：https://www.kaggle.com/competitions/UBC-OCEAN/discussion/445804

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465410
- rank 3｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465527
- rank 4｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465811
- rank 5｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/466017
- rank 6｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465379
- rank 7｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465697
- rank 9｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465815
- rank 10｜description：https://www.kaggle.com/c/UBC-OCEAN/discussion/465455

---

## asl-fingerspelling — Google ASL Fingerspelling 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 PostProcessorKernelDesc ｜ 队伍 1314 ｜ 截止 2023-08-24 ｜ Tier B ｜ 标签 cv,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/asl-fingerspelling.md
> 材料基础：`digests/asl-fingerspelling.md`（6 篇正文：1st 434485 / 2nd 434588 / 5th 434415 / 3rd 434393 / Silver 434353 / 上届冠军 409438；80 条主题索引）+ 13 张图

### 一句话重述
从 MediaPipe 关键点序列（双手+姿态+面部）解码手语拼写短语。真正的考点是**"语音识别范式迁移"：encoder-decoder/CTC、序列增广、效率与部署约束（tf-lite 40MB）**；1st 的 242 票方案把"每个效率改进都换成更深模型"写成方法论。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（242 票） | 130 关键点（21×2 手 + 6×2 姿态 + 76 面）；改进 Squeezeformer 编码器（**Llama RoPE 替相对位置编码：训练 2×、tf-lite 3×、参数 -20%**；去 time reduction；可学习 scaling 代 Macaron）+ 2 层 Transformer 解码器 + **反转序列辅助损失**；4096→400 epochs、fp16、时间掩码；**置信度头**（归一化 Levenshtein）→ <0.15 或 <15 帧替换为 dummy 短语 "2 a-e -aroe"（+0.006）；增广：CutMix/FingerDropout/FacePoseDropout（各 +0.005）、解码输入掩码 +0.003；4 折按 signer；tf-lite 仅 39988KB、2 seed 集成 | 1st |
| 3rd（434393） | 17 层 Squeezeformer + time reduce + RoPE；输入 769 维（原始+归一化+绝对位置/1000）；不丢无手帧；训练数据+补充数据（权重 0.1）400 epochs + AWP（adv_lr 0.2）；blank index 规则后处理 | 3rd |
| 5th（434415） | Vanilla Transformer + conv stem + RoPE；**Data2vec 2.0 预训练**；3D 关键点正确旋转（去归一化→旋转→再归一化；y 缩放 1.898）；姿态+嘴唇辅助输入防过拟合；CTC 分割 + CutMix；KD | 5th |
| 2nd / Silver / 上届 | 2nd：ASR 算法对比；Silver "两行代码"达 0.770（98 票）；上届冠军方案 | 材料 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 5th |
| --- | --- | --- | --- |
| 编码器 | 14× Squeezeformer+RoPE | 17× Squeezeformer+RoPE+time reduce | Vanilla Transformer+conv stem+RoPE |
| 解码 | 2 层 Transformer + 反转辅助 | CTC/blank 规则 | CTC + KD |
| 预训练 | — | — | Data2vec 2.0 |
| 输入 | 130 点 | 769 维特征 | 3D 点+姿态+嘴唇 |
| 增广 | CutMix/FingerDropout/FacePoseDropout | 时间缩放/掩码/affine | 3D 旋转/CutMix/掩码 |
| 部署 | tf-lite fp16（40MB 限制） | — | — |
| 名次 | 1st | 3rd | 5th |

### 共识 / 分歧 / 裁决
**共识一：这是"sign-language ASR"——语音识别的工具箱直接迁移（3/3）**
encoder-decoder/CTC、CTC 分割/CutMix、RoPE、Data2vec 预训练、KD、beam search 取舍——全部来自 ASR。**裁决**：跨模态序列任务优先查同构领域的成熟范式。置信度：高。

**共识二：效率改进 = 更深模型的预算（1st 的方法论）**
1st 把 RoPE（2-3×）、fp16、时间掩码、解码缓存逐项换算成"可以加深模型"的增益（每项 +0.003~0.005）；3rd 用 17 层 + time reduce。**裁决**：在部署约束（tf-lite/内存/时间）下，效率优化与架构创新等价。置信度：高。

**共识三：时空增广是防过拟合核心（3/3）**
1st：CutMix/FingerDropout/FacePoseDropout/时间掩码；3rd：时间缩放+重掩码+affine；5th：3D 旋转+掩码。**裁决**：关键点序列的增广要覆盖"丢手指、丢模态、时间伸缩、空间仿射"四个维度；丢模态增广还能提升泛化。置信度：高。

**共识四：辅助输入（姿态/嘴唇）有效（1st/3rd/5th）**
5th 明确"只用手几周 0.757，加入姿态+嘴唇后更好且防过拟合"；1st/3rd 用全 130 点/769 维。**裁决**：手语拼写并非只看手；面部/姿态提供韵律与上下文。置信度：高。

**分歧一：解码器路线（Transformer decoder vs CTC）**
1st：**Transformer decoder 优于 CTC**（即使效率重要）；3rd 用 CTC+blank 规则；5th 用 CTC+分割。**裁决**：自回归解码上限更高，CTC 更省算力；在时间/内存受限时取舍不同。置信度：中高。

**分歧二：补充数据价值**
1st：补充数据仅 +0.001（50k 样本但只有 500 短语→模型学会分类而非解码；按短语分组每 epoch 加 1 个样本）；3rd：补充数据权重 0.1 用于训练。**裁决**：补充数据的短语多样性不足时收益有限；采样策略比数据量重要。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的架构/增广消融/效率换算 | 自述 + 图 + 代码 + 公开权重 | 高 |
| 3rd 的 17 层/特征/训练细节 | 自述 + 代码 | 中高 |
| 5th 的 Data2vec/3D 旋转/CTC | 自述 + 代码 | 中高 |
| Silver 两行代码 0.770 | 自述（趣味帖） | 中 |
| 补充数据有限收益 | 1st 分析 | 中 |

### 悬案与失败学
**失败学（1st）**
编辑距离作损失、CTC 辅助、label smoothing、AWP（fp16 NaN）、TTA（翻转/拉伸）、hidden mixup、beam search（太贵）均无效。**裁决**：ASR 里的部分正则/搜索技巧在此任务不迁移；fp16 下要避开 AWP。置信度：中高。

**5. 悬案与缺口（登记）**
- 2nd 的 ASR 对比细节未细读；上届冠军方案（409438）未细读。
- 指标 PostProcessorKernelDesc 的精确计算未入库；tf-lite 40MB 规则的官方说明缺失。
- 1st 的置信度头目标（OOF Levenshtein）训练细节只简述。

### 图证（KStarter 仓库内路径）
- ../../intel/asl-fingerspelling/bodies/434485_img/01.png — 1st 的模型架构

### 出处
- 1st（242 票）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434485
- 2nd（434588）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434588
- 5th（434415）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434415
- 3rd（434393）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434393
- Silver（98 票）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434353
- 上届冠军（91 票）：https://www.kaggle.com/competitions/asl-fingerspelling/discussion/409438

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434983
- rank 9｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434871
- rank 11｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434475
- rank 12｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/436457
- rank 17｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434364
- rank 19｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434795
- rank 20｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434658
- rank 22｜description：https://www.kaggle.com/c/asl-fingerspelling/discussion/434680

---

## benetech-making-graphs-accessible — Benetech - Making Graphs Accessible 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 Benetech Mixed Data Type Matching Score ｜ 队伍 608 ｜ 截止 2023-06-19 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/benetech-making-graphs-accessible.md
> 材料基础：`digests/benetech-making-graphs-accessible.md`（6 篇正文：1st 418786 / 2nd 418430 / 3rd 418420 / 7th 418510 / 6th 418466 / 13th 418321 等；80 条主题索引）+ 10 张图

### 一句话重述
从图表图片里抽出结构化的 (x, y) 数据序列。真正的考点是**"没有单一模型能覆盖所有图表类型"**：scatter/dot 用目标检测更稳、line/bar 用图表转文本模型（DePlot/Matcha）更强；顶配解法都是**"图表类型分类 + 按类型分支的混合管线"**，并把大量精力投在**合成数据与外部图表数据的清洗/重标注**上。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（418786） | 两步：**图表类型分类 + 分类型的数据序列推断**；Bar/Line/Dot 用**按类型分别训练的 DePlot**（端到端），**Scatter 用目标检测**；分项（public/private）：Overall 0.86/0.72、Scatter 0.10/0.30、Dot 0.00/0.01、Line 0.32/0.13、VBar 0.39/0.26、HBar 0.05/0.01；数据三块：① 竞赛数据（extracted+generated，剔除约 100 张噪声标注）② **ICDAR**（1406 有标注 + 1903 无标注——有标注的逐张核对并按竞赛规则手工修正；无标注的先肉眼筛、再用 DePlot 打伪标签、再逐张复核修正）③ **自造约 6.5 万张合成图**（补 comp_generated 缺失的变化，如 histogram）；训练：**多阶段**——先在"全类型"数据（12 万图、8 epoch、bs 2、Adafactor lr 1e-5、warmup 4000、高斯模糊/噪声/颜色增强）上训，再用其结果做**类型专属二次训练**（vertical_bar 两次、line 一次；horizontal_bar 因数据少反而变差就用全类型模型；dot 只有生成数据、无法验证，不二次训练）；还处理了"竞赛标注与 DePlot 原始定义的 x/y 轴概念相反"——按 DePlot 原定义训练、推理时交换 | 418786 |
| 2nd（418430） | 全部基于 **google/matcha-base** 的图转文模型，**两阶段训练**（图 1）：① **adaptation**——用大量合成图把骨干适配到本任务（datamix1 → matcha-benetech-mga，兼作图类型分类）；② **specialization**——用**过采样的真实/抽取图**分成 **scatter 与非 scatter 两个专用模型**（datamix2/3），理由是 scatter 的散点预测难度显著更高；输出模板含 chart_type、点数（n_x|n_y）、x/y 序列（科学计数法 `"{:.2e}"`），并额外加 histogram 类在后处理里转成 vertical_bar；公开推理 notebook 与 GitHub | 418430 |
| 3rd（418420） | 团队内部两条路线（end-to-end vs 目标检测+OCR）互补：**分类 + 分类型**；scatter/dot 用检测、line/bar 用 **Matcha**；分项 public/private：Overall 0.87/0.71、Scatter 0.09/0.28、Line 0.33/0.13、VBar 0.39/…；自评"公榜 0.86+ 的队伍都有机会夺冠" | 418420 |
| 7th（418510，"no external data"） | 只用 Kaggle 数据，走**多模型流水线**而非端到端：图表分类 + 文本检测（找 x/y 标签）+ 文本识别（预训练不微调）+ 目标检测（刻度、散点、横/竖条）+ 目标分割（折线、以及判断竖条是否为 histogram）+ 兜底用预训练 DePlot（559 个 CV 文件里只触发 1 次）；CV/LB 0.871/0.86、私榜 0.67 | 418510 |
| 6th/13th | 6th 用 DePlot + UNet 后处理；13th 另一套方案（digest 有正文） | 418466/418321 |
| 社区 | "**为什么 Pix2Struct/MatCha/DePlot 训不起来**"（42 票 / 133 评论）——全场共同的技术坑；"规则更新"（30 票）；"DePlot 介绍"（28 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 7th |
| --- | --- | --- | --- | --- |
| 总体结构 | 分类 + 分类型（DePlot/检测） | 两阶段（适配+专精）Matcha | 分类 + 检测/Matcha | 全流水线（分类/检测/分割/OCR） |
| scatter | **目标检测** | scatter 专用 Matcha | 检测 | 目标检测 |
| line/bar | 分类型 DePlot | 非 scatter Matcha | Matcha | 分割/检测 |
| 外部数据 | ICDAR + 6.5 万合成 | 合成 + 过采样真实图 | — | **无（只用 Kaggle 数据）** |
| priv | 0.72 | — | 0.71 | 0.67 |

### 共识 / 分歧 / 裁决
**共识一：单一端到端模型不够，必须"分类 + 分类型分支"（1st/2nd/3rd/7th）**
四队都先分类再分类型处理；2nd 进一步把分支定为 scatter vs 非 scatter（散点最难）；1st 更细（每类一个 DePlot + scatter 检测）。**裁决**：图表理解的类型异质性极强，"按图表类型路由"是标配；散点类必须用检测/分割（模型看不到隐含的 y 值坐标）。置信度：高。

**共识二：训练数据的清洗/重标注与合成是主要工程量（1st/2nd + 42 票帖）**
1st 为 ICDAR 做了"逐张肉眼核对 + 伪标签 + 再复核"；自造 6.5 万合成图补变化；2nd 用过采样真实图做专精；社区 133 条评论的帖子在讨论"为什么 Pix2Struct/MatCha/DePlot 训不起来"（标注规则/格式问题）。**裁决**：图表赛的瓶颈在数据管线（格式、坐标定义、噪声），模型选择是第二步。置信度：高。

**共识三：公榜与私榜差距大，分项分数极不均衡（全员）**
1st 的 public 0.86 → private 0.72，且 dot 两项仅 0.00/0.01；3rd 0.87→0.71；7th 0.86→0.67。**裁决**：本场是"高公榜、低私榜"的典型；选择提交要看分项（尤其 dot/scatter 这类几乎未解的类别）与验证稳定性，而非总体公榜。置信度：高。

**分歧一：端到端 vs 图像处理流水线**
2nd 完全端到端（Matcha）；7th 完全流水线（无外部数据）；1st/3rd 混合。**裁决**：端到端对 line/bar 强、流水线对 scatter/dot 强；顶配是"混合路由 + 各自最强工具"。置信度：高。

**事件：x/y 轴概念反置的"坑"（1st）**
竞赛标注规则与 DePlot 原始定义的 x/y 概念相反；1st 按 DePlot 原定义训练、推理时交换值。**裁决**：外部预训练模型与竞赛标注口径不一致时，优先"按预训练口径训练 + 推理端转换"，而不是强行改标注。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的两步管线、数据清洗与多阶段训练 | 自述 + 多张图 + 分项分数 | 高 |
| 2nd 的两阶段 Matcha（适配+专精） | 自述 + 管线图 + 公开代码 | 高 |
| 7th 的"无外部数据"流水线与 0.67 私榜 | 自述（细节完整） | 中高 |
| 3rd 的混合路线与分项分数 | 自述 + 图 | 中高 |
| "Pix2Struct 等训不起来" | 长讨论帖（133 评论） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th/5th/8th–12th/14th 的方案未细读；"规则更新"（30 票）与"如何着手"（1046 行处）未细读；
- 1st 的目标检测（scatter）细节未展开；
- dot 类几乎无人解出（0.00–0.01），其失败原因未系统整理；
- 归档 10 图：2nd 的两阶段管线图（图 1）、3rd 的分类图为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/benetech-making-graphs-accessible/bodies/418430_img/01.png — 2nd 的两阶段训练管线

### 出处
- 1st（60 票）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/418786
- 2nd（64 票）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/418430
- 3rd（54 票）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/418420
- 7th（51 票）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/418510
- 6th（40 票）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/418466
- Pix2Struct 训不起来（42 票 / 133 评论）：https://www.kaggle.com/competitions/benetech-making-graphs-accessible/discussion/406250

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418604
- rank 5｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418477
- rank 13｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418321
- rank 14｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418323
- rank 20｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418389
- rank 28｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418705
- rank 40｜description：https://www.kaggle.com/c/benetech-making-graphs-accessible/discussion/418331

---

## biohub-cell-tracking-during-development — Biohub - Cell Tracking During Development 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 CZI Biohub Zebrafish 133605 ｜ 队伍 3947 ｜ 截止 2026-09-29 ｜ Tier B ｜ 标签 cv,wildlife
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/biohub-cell-tracking-during-development.md
> 材料基础：`digests/biohub-cell-tracking-during-development.md`（6 篇正文：1st 744801 / 3rd 744484 / 5th 744549 / 14th 744486 / 12→95 名复盘 744912 / 欢迎帖 716062；80 条主题索引）+ 30+ 张图

### 一句话重述
在斑马鱼胚胎的 3D 时序影像里追踪细胞并识别分裂。真正的考点是**"标注极稀疏（仅约 2.8% 的细胞被标）下，把检测、分裂识别与连线评分都学出来"**：1st 用"检测器 + **Soon Net（分裂状态 + 占用图）** + 学习式 linker + 贪心解码"；3rd/5th 走"检测 + 光流 + 图优化/ILP"；同时全场用规则/图修复兜底，并互相印证"训练数据里存在重复帧与漂移帧"这一数据缺陷。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（744801，76 票，solo gold） | 四段式（图 1）：① **检测**：3D U-Net（~3.1M）+ Cellpose 风格头（前景 + 指向中心的流场），**轻量 MAE 预训练**（50% 掩码但每块仅 2×4×4 体素，"不让模型去幻觉整细胞"）→ 用**手工标注 1800 个细胞 + GT 节点上的 4.305µm 印章**微调 → **伪标签重训**（5 折平均 + 4× flip TTA，用公共 twoPass 追踪器过滤 min length>3）；② **Soon Net**（236K CNN + 508K transformer）：看每个细胞 t−1/t/t+1 的三帧裁剪，预测**分裂状态（interphase / soon-to-divide / just-divided）**与**占用图**（continuation/division 两类，"它在哪里、要到哪里去"）；训练技巧：大 FOV 抖动（z ±3、xy ±16）防"只看中心"、时间步增广（t±2/3）、错误类型图在 top-512 体素上加 BCE 防幽灵斑、硬负例挖掘（2492 个难 interphase）、**把分裂样本从 GT 的 151 个扩到 515 个**；③ **学习式 linker**（transformer，LightGlue 启发）：对 t→t+1 的边打分并判定分裂；④ 贪心解码（division refractory、缺口回填、直线拟合）；5 折严格 OOF；自评"soon-to-divide 单点把公榜从 ~0.925 抬到 ~0.963" | 744801 |
| 3rd（744484） | 六段式：① **检测集成**（2.5D U-Net 热图 + 3D SegResNet，占 55% 运行时间）② **稠密 3D 光流**（帧间位移场）③ 用运动校正后的位置匹配细胞 ④ **分裂识别**（原始图 + 运动对齐图，另有"分裂前/后阶段"辅助模型）⑤ **谱系图优化**（联合选择普通边与分裂事件）⑥ 后处理（补短缺口、删小连通域、精修节点坐标）；CV 0.977801（division Jaccard 0.540107），公榜 0.977（0.52），私榜 0.967（0.47） | 744484 |
| 5th（744549） | 三段式：3D U-Net 检测 + **Transformer linker** + **多阶段 ILP 追踪**（整数规划构轨迹）；5 折 + 8 TTA；**关键发现**：训练数据里有"**重复帧**（与下一帧逐字节相同）"与"**漂移帧**（整幅图跳 14µm）"；在验证中剔除这些帧的边后 CV 大涨但 LB 不变 → **隐藏测试集没有大漂移**（这解释了很多人 CV-LB 不匹配）；训练时去掉重复帧并纠正漂移能让同一折模型私榜 +0.011，但公榜下降，最终未采用 | 744549 |
| 12→95 名复盘（744912） | 稀疏标注的处理：把"模型预测但非 GT"的位置**排除在检测损失之外**（pseudo-unlabeling，而非当作正样本），使负样本权重能从 0.01 提到 0.1，训练更快更准；最终用多 checkpoint 加权混合 + 专家 edge 头 + 整数规划构谱系（每细胞 ≤1 父 ≤2 子）+ 图修复（补缺口/重连/删短轨）+ **XY 网格原点 +2 体素校正**；公榜 0.969 → 私榜 0.929 的对照说明榜面波动 | 744912 |
| 社区侧 | "**规则法意外地强？**"（48 票，7 名、无学习）；"**当心 GT 轨迹里的跳跃**"（42 票）；"**Division Metric 的漏洞与补丁**"（36 票）；"18.5GB 全标注合成 3D 显微数据（含 16.5 万次分裂）"（65 票）；"focus3d：最好的 3D 细胞分割之一"（40 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 5th | 12→95 |
| --- | --- | --- | --- | --- |
| 检测 | 3D U-Net（Cellpose 头）+ 轻量 MAE + 伪标签 | 2.5D U-Net + 3D SegResNet 集成 | 3D U-Net（5 折 + 8 TTA） | 复用公共管线 + 微调 |
| 分裂建模 | **Soon Net（状态 + 占用图）** | 独立的"分裂前/后阶段"辅助模型 | — | 分裂分类器否决 |
| 连线 | 学习式 transformer linker | 图优化（联合选边与分裂） | **ILP** | 整数规划 + 图修复 |
| 数据缺陷 | 伪标签+人工复核 | — | **重复帧/漂移帧诊断** | pseudo-unlabeling |
| 指标 | edge Jaccard + 0.1×div Jaccard | 同 | 同 | 同（+2 体素原点校正） |

### 共识 / 分歧 / 裁决
**共识一：检测是上限，但稀疏标注要求"宽容的损失/伪标签"（1st/3rd/12→95）**
3rd 说"检测占 55% 运行时间、下游全靠它"；1st 花一个半月攻检测；12→95 用 pseudo-unlabeling 防止把未标注细胞当背景。**裁决**：稀疏标注赛里，检测目标必须显式处理"未标注≠负样本"（掩掉预测点或用印章式弱监督），否则负样本权重永远上不去。置信度：高。

**共识二：分裂是独立子问题，要单独建模（1st/3rd/12→95）**
1st 的 Soon Net 把分裂识别做成"状态 + 占用图"（并说它单独就把公榜从 0.925 抬到 0.963）；3rd 有专职的分裂前后辅助模型；12→95 用分裂分类器否决可疑分裂。**裁决**：分裂事件的样本量极小（GT 仅 151 次）→ 必须用挖掘/增广扩充，并放在独立的模型/判别器里。置信度：高。

**共识三：训练数据本身有系统性缺陷（5th/42 票帖/36 票帖）**
5th 定位了重复帧与 14µm 漂移帧；社区帖提醒"GT 轨迹有跳跃"、并讨论"分裂指标的漏洞与补丁"。**裁决**：3D 追踪赛先做数据审计（逐帧一致性、漂移、GT 连续性）；训练/验证要一致地剔除这些污染帧，否则 CV-LB 会脱钩。置信度：高（多队独立发现）。

**分歧一：端到端学习 vs 图优化/ILP**
1st 的学习式 linker + 贪心解码；3rd 的图优化联合选边；5th 的 ILP；12→95 的整数规划 + 图修复。**裁决**：两者互补——学习式打分负责"边/分裂的局部概率"，图优化负责"全局约束（每细胞 ≤1 父 ≤2 子）"；顶配方案是"学习打分 + 全局求解"。置信度：高。

**事件：规则法能到第 7（48 票帖）**
有队伍用**无学习的规则法**拿到第 7（gold zone）。**裁决**：说明本场的"几何/强度/速度手作特征"依然强（1st 也说细胞追踪领域不用大模型、靠 handmade 特征），学习方法的价值在于补上"分裂识别"与"难例"。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的四段管线、Soon Net 细节与 +0.038 公榜 | 自述 + 总览图 + 多图/GIF | 高 |
| 3rd 的六段式与 CV/公榜/私榜三档分数 | 自述 + 管线图 | 高 |
| 5th 的重复帧/漂移帧诊断（CV 涨 LB 不变） | 自述 + 漂移图 | 中高 |
| 12→95 的 pseudo-unlabeling 与图修复细节 | 自述 | 中高 |
| 规则法第 7 | 社区帖（48 票） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/4th/6th–11th/14th 的方案未细读；"Division Metric exploit"（36 票）与"18.5GB 合成数据"（65 票）未细读；
- 1st 的 Soon Net 独立评分（0.9270/0.9288）与最终集成分数的完整链路未给全；
- 私榜与公榜的洗牌幅度（12→95 等）未系统整理；
- 归档 30+ 图（1st 的 10 张、3rd/5th 的管线与漂移图等）为图证来源。

### 图证（KStarter 仓库内路径）
- ../../intel/biohub-cell-tracking-during-development/bodies/744801_img/01.png — 1st 的四段式追踪管线

### 出处
- 1st（76 票）：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744801
- 3rd：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744484
- 5th：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744549
- 12→95 名复盘：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744912
- 规则法第 7（48 票）：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/716952
- 分裂指标漏洞（36 票）：https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/727154

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/1st-place-solution
- rank 2｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/2nd-place-solution
- rank 3｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/3rd-place-solution
- rank 4｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/4th-place-solution
- rank 5｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/5th-place-3d-u-net-transformer-linker-multi-s
- rank 6｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/6th-place-solution
- rank 7｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/7th-place-solution
- rank 9｜description：https://www.kaggle.com/c/biohub-cell-tracking-during-development/writeups/9th-place-solution-own-detectors-public-tracker

---

## blood-vessel-segmentation — Blood Vessel Segmentation（SenNet + HOA）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Surface Dice Metric ｜ 队伍 1149 ｜ 截止 2024-02-06 ｜ Tier B ｜ 标签 cv,segmentation
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/blood-vessel-segmentation.md
> 材料基础：`digests/blood-vessel-segmentation.md`（6 篇正文：lb0.870 122 / 1st 100 / 3rd 69 / 4th 68 / 2nd 33 / 相似赛汇总；80 条主题索引）+ 11 张图

### 一句话重述
肾脏 3D 血管分割（Surface Dice）。本场的真正考点是**评测集的隐藏分辨率/成像域偏移**：训练与公开测试均为 50 µm/voxel，私有测试为 **63 µm/voxel**（官方披露），且公私测试切片分布不同——**按公开榜优化 = 私榜赌博**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st | 2 个 2.5D convnext-tiny UNet（3 通道）；同模型加**随机 3D 旋转增广**：私 0.682→**0.830/0.835**（公 0.889→0.888）；被选集成私 0.744/0.774；推理 3072/动态 3200、阈值 0.4；torch.compile 2× | 1st |
| 2nd | 公榜 **0.43（1052 名）→ 私榜 0.7568（第 2 名）**；U-Net3D 128³×32 + 体积比阈值 + 去小连通块；自述"我的假设（3D 更好）可能是错的" | 2nd+图 2/3 |
| 3rd | 纯 2D；消融：仅分辨率/训练技巧 0.818/0.586 → 全数据 0.857/0.633 → **模拟放大倍率 0.849/0.652** → 稀疏→稠密标签精修 **0.846/0.727**；最终单模与 4 模型集合同为私 0.727；SeResNext 单模私 0.753 更高但未选 | 3rd |
| 4th | 2D 0.878/0.714 + 3D 0.869/0.694 → ROI 后处理 0.881/0.701 → 2D+3D 集成 0.884/0.712；Canny 后处理公 0.892/**私 0.313**（雪崩） | 4th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 4th |
| --- | --- | --- | --- | --- |
| 维度方案 | 2.5D 多视角 | 3D U-Net | 纯 2D | 2D+3D 集成 |
| 关键增广 | **随机 3D 旋转切片** | 随机旋转/位置 | 放大倍率模拟（scale 中心 0.8、0.55–1.05） | CutMix + 稀疏度加权采样 |
| 标签 | 全量含 kidney_1_voi | sparse only | **稀疏→稠密精修**（稠密训 → 伪标 → 续训） | HOA 伪标（剔除重叠集防泄漏） |
| 损失 | focal+dice+boundary+自定义 | binary focal | — | **BoundaryDOULoss** |
| 后处理 | 阈值 0.4 | 体积比阈值 + 去小连通块 | 阈值稳定性优先 | 2D ROI × 3D 预测 |
| 私榜结果 | 单模 0.835 / 被选集 0.774 | **0.7568（2nd）** | 0.727 | 0.712 |

### 共识 / 分歧 / 裁决
**共识一：2.5D（多视角）> 3D 在本评测域成立（1st/3rd 强证据）**
1st 全 2.5D；3rd 纯 2D 拿到 0.727；4th 的 3D 单模（0.694）低于其 2D（0.714）；2nd 用 3D 且自认假设可能错。**裁决**：私有集分辨率更低（63µm）时，2.5D 的输入尺度更鲁棒；3D 模型对插值/尺度更敏感。置信度：高。

**共识二：随机 3D 旋转切片增广是决定性技巧（1st 实证）**
同一模型，仅加"任意平面 3D 旋转切片"：私榜 0.682→0.830/0.835，公榜几乎不变（0.889→0.888）。**裁决**：它迫使模型学习各向异性/分辨率变化下的血管结构，直接对冲 50→63µm 的域移。置信度：高（单队受控对照）。

**共识三：公开榜在这场比赛里几乎无信息量**
2nd 公 0.43（1052 名）→ 私 0.7568（第 2）；4th 的 Canny 后处理公 0.892 → 私 0.313；1st 被选集成（公 0.898）私 0.744，而未入选的单模私 0.835。**裁决**：公/私切片分布+分辨率双偏移下，**提交选择要按"跨域鲁棒性"而非公开分**；赛后 2nd 的"What's happened?"是本场最佳注脚。置信度：高。

**共识四：边界感知损失 + 后处理有稳定收益**
4th 的 BoundaryDOULoss 是主损失；1st 用 focal+dice+boundary+自定义（对齐 Surface Dice）；2nd 用体积比阈值 + 连通性去噪。**裁决**：Surface Dice 类指标需要边界/拓扑感知（损失、阈值、连通块）。置信度：中高。

**共识五：稀疏标签的处理是数据侧第一杠杆**
3rd 的"稀疏→稠密精修"消融私榜 0.652→0.727；4th 用外部 HOA 伪标（并剔除与 kidney_3 重叠的数据防泄漏）；1st/2nd 未用伪标。**裁决**：条件性有效，关键在防泄漏与比例校准（3rd 按官方标注比例选阈值）。置信度：中高。

**分歧一：损失与外部数据**
4th：BCE/Focal 失败、BoundaryDOU 胜；1st：外部数据与伪标"不工作"；3rd：标签精修是核心。**裁决**：外部数据的效果因清洗方式不同而反转（4th 剔除重叠后有效；1st 未成功）；损失则一致偏向边界感知。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 公/私反转（2nd 0.43→0.7568；4th Canny 0.892→0.313） | 截图 + 自述 | 高（现象层面） |
| 1st 的 3D 旋转消融（0.682→0.830） | 自述 + 图 | 中高 |
| 3rd 的消融表（0.586→0.727） | 自述表 | 中高 |
| 官方分辨率披露（50/63µm） | 3rd 引用官方披露 + 相关主题帖 | 高 |
| 4th 的 ROI 后处理 0.869→0.881 | 自述 | 中 |
| 外部数据/伪标的增益 | 各队结论互相矛盾 | 低–中（条件性） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 5th+ 方案未收录；Surface Dice 的精确实现（容差）只在 `33 票` 帖中，未入库细节。
- "Important Information about the Hidden (Test) Datasets"（43 票）与 magnification 披露帖未收录正文——隐藏集偏移的官方细节缺失。
- 1st 未选 0.835 单模而选集成（公榜导向）的决策复盘缺失；4th 的 Canny 私榜雪崩机制未解释。
- 外部数据许可/合规（HOA）与重叠判定流程未展开。

### 图证（KStarter 仓库内路径）
- ../../intel/blood-vessel-segmentation/bodies/475522_img/01.png — 1st 的随机 3D 旋转切片
- ../../intel/blood-vessel-segmentation/bodies/475657_img/03.png — 2nd 的公/私切片分布
- ../../intel/blood-vessel-segmentation/bodies/475657_img/01.png — 2nd 的提交分数截图

### 出处
- 1st（100 票）：https://www.kaggle.com/competitions/blood-vessel-segmentation/discussion/475522
- 3rd（69 票）：https://www.kaggle.com/competitions/blood-vessel-segmentation/discussion/475074
- 4th（68 票）：https://www.kaggle.com/competitions/blood-vessel-segmentation/discussion/475052
- 2nd（33 票）：https://www.kaggle.com/competitions/blood-vessel-segmentation/discussion/475657
- lb0.870 实验帖（122 票）：https://www.kaggle.com/competitions/blood-vessel-segmentation/discussion/456118
- 缺口登记：475657 的完整榜单讨论、hidden test 信息帖（43 票）、Surface DSC 帖（33 票）

### 外部题解（kaggle-solutions）
- rank 5｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475288
- rank 6｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475252
- rank 7｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475964
- rank 9｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475080
- rank 12｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/476457
- rank 13｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475117
- rank 14｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475260
- rank 24｜description：https://www.kaggle.com/c/blood-vessel-segmentation/discussion/475090

---

## byu-locating-bacterial-flagellar-motors-2025 — BYU - Locating Bacterial Flagellar Motors 2025 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 BYU_BioPhysics_91249 ｜ 队伍 1136 ｜ 截止 2025-06-04 ｜ Tier B ｜ 标签 cv,science
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/byu-locating-bacterial-flagellar-motors-2025.md
> 材料基础：`digests/byu-locating-bacterial-flagellar-motors-2025.md`（6 篇正文：1st 583143 / 3rd 583380 / 4th 583411 / 20th 583128 / 369th 583133 / 数据理解 567360；80 条主题索引）+ 18 张图

### 一句话重述
在冷冻电子断层扫描（CryoET）体数据里找细菌鞭毛马达的位置。指标**对定位误差宽容、对"有无"敏感**——于是全场的核心结论是"**别把力气花在精确坐标上**"：有人干脆把解码器删掉只做 3D 分类，有人把热图降采样 8–16 倍，有人用分位数阈值决定"这张 tomogram 有没有马达"。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（583143，146 票） | 3D U-Net（编码器 = 预训练 ResNet200/101，随机 dropout + 梯度检查点；解码器仅 1 个反卷积块）；**标签 = 高斯热图、分辨率降 8 倍**（"指标对距离宽容，预测像素精确不重要"）；损失 = SmoothBCE 三项（主头 + 倒数第二特征图深监督 + **主头 maxpool(4) 的池化损失**——鼓励马达邻域概率高、容忍小定位误差）；重增强（mixup/rescale/rot90/轴翻转/轴交换 100%，coarse dropout 50%…）可训 400 epoch（250 后 LB 无提升）；推理：只沿深度滑窗（宽高对齐）→ 高重叠 0.875、边缘 logits 权重 0.001、中间 40% 权重 1.0；8 seed 集成（logits 相加），推理 ~10 小时；**分位数阈值**：按 max 预测值给全部 tomogram 排序、删掉最低分位（pub 最优 0.565 / priv 0.560）——固定阈值不稳定；还手工补标了缺失马达 | 583143 |
| 4th（583411，42 票） | 洞察"指标对定位宽容"后**直接删掉解码器**：3D ResNet18（从头训）输入 96×160×160 → 特征图 512×3×5×5 → 展平成 **75 个空间类 + 1 个"无马达"类 = 76 类分类**（CrossEntropy）；推理滑窗 overlap 0.5，取 75 类里最大值所在 patch + 3×5×5 网格偏移定位；**单模型 pub 0.875（相当于第 5 名）**；预处理统一 15.6Å 体素、int8 存盘；按体素大小/数据集 id 分 4 折（CV-LB 相关性差，主要看 LB）；MixUp 定制为"混合 patch 内最多 1 个马达"、正样本过采样至 12.5%；与 MONAI 检测模型集成 + jit/TensorRT 加速 | 583411 |
| 3rd（583380，42 票） | 3D/2D 混合 UNet 集成（3D ResNeXt50 / DenseNet121 / X3D-M + 2D MaxViT / CoaT）；3D patch 224×448×448、2D 384–896² 以获全局上下文；热图 stride=16、sigma=200Å；简单 FPN 融合低层特征；**只用 BCE 最好**（MSE/L1/加权 BCE/Focal/Tversky/多损失组合都不行）；统一重采样到 16Å 体素 + 滑窗；**WBF 融合多模型/TTA 预测**；伪标签（人工复核）；最终 PB 0.866 | 583380 |
| 20th（583128，38 票） | **关键点 + 双图（GNN）**路线：YOLO11 的 C3K2 特征图当节点特征（低 conf=0.05 生成大量候选点）→ **RandomWalkPE 位置编码是"缺失的关键成分"**（加入后分数立涨）→ 用"半径内 + 特征相似"定义正标签（承认单点无法表达语义、指标给了半径容差）；还提到 VLM few-shot 的经验（在另一项目用 20 张图训出异常检测） | 583128 |
| 369th（583133） | YOLO 路线 PB 0.840 的公开 notebook（说明检测器路线也能到 0.84 档） | 583133 |
| 数据侧 | "理解比赛数据"（69 票）、"train_labels.csv 可能不一致"（60 票）、"负样本 tomogram 里也有马达样结构"（35 票）、"测试域漂移技巧"（49 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 4th | 20th |
| --- | --- | --- | --- | --- |
| 形态 | 3D U-Net + 热图 | 3D/2D UNet 集成 | **无解码器 76 类分类** | 关键点 + GNN |
| 输出分辨率 | 热图降 8× | 热图 stride 16 | 3×5×5 网格分类 | 点分类 |
| 阈值策略 | **分位数阈值** | WBF + 逐模型 | 类 argmax + 偏移 | 图推理 |
| 集成 | 8 seed | 5 模型 + WBF | 检测器 + jit/TensorRT | — |
| 关键洞察 | 池化损失容忍定位误差 | 只用 BCE | 删解码器足够 | RandomWalkPE |

### 共识 / 分歧 / 裁决
**共识一："有无"比"在哪"值钱（1st/3rd/4th）**
指标对距离宽容：1st 把热图降 8 倍并用池化损失（"鼓励马达邻域高概率、减小小误差惩罚"）；4th 直接用 3×5×5 粗网格分类（无解码器）也能 0.875 pub；3rd 用 stride-16 热图 + WBF。**裁决**：先读指标的距离容忍度，据此决定输出分辨率与损失——本场的最优输出远粗于体素级。置信度：高（多队 + 4th 的极端简化）。

**共识二：固定阈值不稳定，要用分位数/相对阈值（1st + 社区）**
1st 明确"固定阈值不稳定"，改用**按 max 预测值排序的分位数阈值**（pub 0.565 / priv 0.560，见提交记录 0.56→0.879）；社区帖也强调"按类设阈值"。**裁决**：当"存在性"依赖单点最大概率时，用分布分位而不是绝对值。置信度：高。

**共识三：域漂移/噪声要靠增强 + 外部数据 + 手工清洗（全员）**
统一重采样到 15.6–16Å、重增强（mixup/旋转/轴操作）、外部 CryoET Data Portal 数据、手工补标（1st）、伪标签人工复核（3rd）。**裁决**：医学/生物影像的域移，最省事的组合是"统一体素尺度 + 强增强 + 外部同域数据"。置信度：高。

**分歧一：U-Net 分割 vs 纯分类 vs 关键点/GNN**
1st/3rd 用分割式；4th 用分类式（更简单、更快、单模 0.875）；20th 用关键点 + GNN（另类）。**裁决**：指标宽容时，"分类 + 粗定位"在性价比上胜过精细分割；关键点/GNN 需要位置编码才能工作（RandomWalkPE）。置信度：中高。

**事件：数据质量与标注不一致（社区）**
train_labels.csv 的不一致（60 票）、负样本里存在马达样结构（35 票）——1st 用 Napari 手工补标，3rd 用伪标签+人工复核。**裁决**：小样本 3D 任务的标注审计是必要工作，公开外部数据可显著改善。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的分位数阈值与提交记录（0.56→0.879） | 自述 + 提交截图 + 公开数据/代码 | 高 |
| 4th 的 76 类分类与单模 0.875 | 自述 + 架构说明 + 代码片段 | 高 |
| 3rd 的"只用 BCE 最好"与 WBF | 自述 + 多张图 | 中高 |
| 20th 的 RandomWalkPE 增益 | 自述（单队） | 中 |
| 数据不一致/负样本结构 | 多条高票讨论 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/5th–19th 的方案未入库；"测试域漂移技巧"（49 票）与"理解数据"（69 票）未细读；
- 1st 未给"池化损失/深监督"的逐项消融；分位数阈值在私榜的有效性只由一次提交证明；
- 20th 的 GNN 完整结构与 VLM few-shot 的迁移细节未展开；
- 归档 18 图：1st 的提交记录图（分位数阈值效果）、模型/损失图，4th 的架构图为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/byu-locating-bacterial-flagellar-motors-2025/bodies/583143_img/04.JPG — 分位数阈值下的提交分数

### 出处
- 1st（146 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583143
- 3rd（42 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583380
- 4th（42 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583411
- 20th（38 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583128
- 369th YOLO 基线（37 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/583133
- 数据理解（69 票）：https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025/discussion/567360

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/584980
- rank 6｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/587410
- rank 9｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/583242
- rank 13｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/583164
- rank 17｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/583144
- rank 21｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/583289
- rank 44｜description：https://www.kaggle.com/c/byu-locating-bacterial-flagellar-motors-2025/discussion/583294

---

## czii-cryo-et-object-identification — CZII CryoET Object Identification 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 CZI_CryoET_ 84969 ｜ 队伍 931 ｜ 截止 2025-02-05 ｜ Tier B ｜ 标签 cv,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/czii-cryo-et-object-identification.md
> 材料基础：`digests/czii-cryo-et-object-identification.md`（6 篇正文：1st OD 561440 + 1st 分割 561510 / 2nd 561568 / 3rd 561417 / 4th 561401 / 9th 561431 等；80 条主题索引）+ 11 张图

### 一句话重述
在 3D CryoET 体数据里找五类粒子（apo-ferritin/beta-galactosidase/ribosome/thyroglobulin/VLP）。真正的考点是**"分割 vs 点检测的路线选择 + 推理时延工程"**：1st 的冠军是**分割模型 + 点检测模型两条路线合并**（单独各只到 Top-5），而点检测路线的关键收益来自"降低输出分辨率 + TensorRT"这类纯工程手段。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st-OD（561440，BloodAxe） | 基线是 SegResNet 热图分割（0.740 LB）→ 主动放弃改做**anchor-free 点检测**（SegResNet/DynUnet + 自定义点检测头）；用 **OKS 式点-点 IoU**（`exp(-mse/(2r²))`）当 IoU 代理；损失仿 PP-YOLO（Top-K 分配 + varifocal 分类 + IoU 距离回归）；**输出 stride=2 的类别图与偏移图**（stride1 仅好 0.002 但慢一半；stride2+4 双头无额外收益；大颗粒自然迁移到 stride4）；4×3090 单折 2 小时、单折首提交 0.752 LB；**TensorRT 200% 加速 + 2×T4 并行**；滑窗 192×128×128、1×9×9 块、边界降权加权平均；后处理：CenterNet 式 NMS → top-16K → 逐类置信度阈值 → 贪心 NMS → 像素转 Å；集成 5×OD-SegResNet + 5×OD-DynUnet；**1st 与队友各是 Top-5，合并后直接第 1** | 561440 |
| 1st-分割（561510，Christof） | 7 折（按 experiment 切）；逐类阈值网格搜索 + 用 OOF 交叉拟合阈值曲线再取最优；标准归一化（630×630×184）；MONAI 增强 + 自研 MixUp；核心发现：**倒数第二层特征图比最后一层更准**（"部分 U-Net"即可）、**框回归几乎无增益**（同类型粒子大小一致）、用低类权 + 单像素目标就无需高斯热图；FlexibleUnet(resnet34/effnet-b3)；**6 个检查点 <2 小时即可拿 LB 第 7**；不用任何外部/模拟数据 | 561510 |
| 2nd（561568） | 轻量分割模型集成（873K–14.2M 参数）：UNet3D/VoxResNet/VoxHRNet/SegResNet/DenseVNet；**大模型易过拟合、更差**；发现 MONAI UNet 的 **InstanceNorm3d + PReLU 比 BatchNorm3d + ReLU 训练更稳定**（5 次对照）；CC3D 求质心 + 按体素数过滤小簇；按公榜选模型 | 561568 |
| 3rd（561417） | 3D UNet + CE（7 类粒子）+ cc3d 后处理；res101 骨干 4 折（7 KF）集成；**公私榜同为 0.783** | 561417 |
| 4th（561401） | 热图法（姿态估计思路）；2.5D-UNet（2D 骨干 + 深度方向池化，**优于 strided 3D 卷积**）；σ=6 或按粒子尺寸；**坐标换算应加 1.0 而不是 0.5**（像素中心 vs 角点）；承认 CV-LB 不相关 → 用 LB 做方法取舍 | 561401 |
| 9th（561431） | 3D ConvNeXt 类分割 + 尽量多模型集成；**按粒子类别调整掩码半径**（如 r/2、r/3）→ 公榜 +0.02~0.04；CC3D + DBSCAN 净化质心 | 561431 |
| 社区 | "卡在 benchmark.csv 以下读这篇"（98 票）、"用合成数据构建 CryoET 基础模型（lb 0.748）"（81 票）、"本地 CV 0.35–0.75 但提交几乎 0 分"（38 票）、"网格原点其实是第一个像素的中心"（37 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st-OD | 1st-分割 | 2nd | 4th | 9th |
| --- | --- | --- | --- | --- | --- |
| 路线 | 点检测（OKS 代理 IoU） | 部分 U-Net 分割 | 轻量分割集成 | 2.5D 热图 | 3D ConvNeXt 分割 |
| 关键工程 | **stride2 + TensorRT + 双 T4** | 部分 U-Net + OOF 阈值 | InstanceNorm+PReLU | 深度池化替代 3D 卷积 | 按类调掩码半径 |
| 后处理 | CenterNet NMS/逐类阈值 | 逐类阈值曲线 | CC3D + 小簇过滤 | 坐标 +1.0 | CC3D + DBSCAN |
| 结论 | 与分割合并→1st | 与检测合并→1st | 2nd | 4th | 9th |

### 共识 / 分歧 / 裁决
**共识一：这是一场"推理时延"比赛（1st-OD/4th/2nd）**
12 小时跑 500 个扫描 ≈ 1.5 分钟/扫描；1st 用 stride2 输出（50% 提速）+ TensorRT（200%）+ 双 GPU 并行才装得下 10 模型集成；4th 用 2.5D 骨干也是为了吞吐。**裁决**：限时推理的 3D 赛要把"模型吞吐"当一等指标；降低输出分辨率是收益最高的工程手段。置信度：高。

**共识二：分割与点检测是互补路线，冠军是两者的合并（1st 两篇）**
1st 自述"我单独是 Top-5、队友单独也是 Top-5，合并后立刻第 1"；1st-OD 也承认分割是最容易实现且强的基线（0.740）。**裁决**：当两条范式的错误模式不同（高斯热图 vs 点回归），跨范式集成是最有效的提升方式。置信度：高。

**共识三：小模型 + 好损失 > 大模型（1st-分割/2nd）**
1st-分割："相对小的模型表现很好，**损失设计最重要**"（6 个检查点 <2h 到第 7）；2nd："大参数量易过拟合，反而更差"，且发现 InstanceNorm+PReLU 更稳。**裁决**：3D 医学小数据赛优先把损失/归一化调对，深度与宽度是次要变量。置信度：高。

**分歧一：目标表示（高斯热图 vs 单像素 vs 点检测）**
1st-分割发现"热图不必要，低类权 + 单像素目标即可"，并把监督放在倒数第二层；1st-OD 直接回归点 + 偏移；4th 仍用 σ=6 的高斯热图；9th 用半径可调的掩码。**裁决**：三种都能进前列；热图的 σ/半径是需要按类调的超参（9th 的 +0.02~0.04 即此项），而"部分 U-Net（倒数第二层）"是低成本等价替代。置信度：中高。

**分歧二：CV 还能不能用**
4th 明确"CV-LB 不相关，只用 CV 选检查点、用 LB 决定方法"；1st-分割用 7 折 f4 均值（与 LB 有良好相关）并做 OOF 阈值重标定；2nd 按公榜选模型。**裁决**：本场 CV 与 LB 的关系依赖切分（按 experiment vs 随机）；切分方式本身要先验证相关性。置信度：中高。

**事件：坐标系细节（4th/37 票帖）**
"粒子坐标 +1.0 还是 +0.5""网格原点是首像素中心"——直接影响定位精度与本地-榜一致性（38 票帖：本地 CV 0.35–0.75 但提交近 0）。**裁决**：3D 数据坐标系约定要写成单元测试并交叉验证。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的双路线合并与 TensorRT/stride2 细节 | 自述 + 公开代码/权重 + 图 | 高 |
| 1st-分割的"倒数第二层更准/框回归无增益" | 自述 + 图 | 中高 |
| 2nd 的 InstanceNorm+PReLU 对照 | 自述 + 5 次实验对比图 | 中高 |
| 9th 的按类掩码半径 +0.02~0.04 | 自述 | 中 |
| 坐标 +1.0 的结论 | 自述 + notebook + 社区讨论 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 5th–8th 的方案未入库；"卡在 benchmark 下"（98 票）与"合成数据基础模型"（81 票）未细读；
- 1st 的合并权重与逐模型贡献未量化（只有"合并即第 1"）；
- 12 小时限时的具体推理预算分配（TTA/集成规模）未完整给出；
- 归档 11 图：1st-OD 的逐类阈值曲线（图 1）、1st-分割的部分 U-Net、2nd 的稳定性对照为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/czii-cryo-et-object-identification/bodies/561440_img/01.png — 1st-OD 的逐类阈值曲线

### 出处
- 1st-OD（561440）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561440
- 1st-分割（103 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561510
- 2nd（44 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561568
- 3rd（53 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561417
- 4th（68 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561401
- 9th（51 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/561431
- "卡在 benchmark 下"（98 票）：https://www.kaggle.com/competitions/czii-cryo-et-object-identification/discussion/547350

### 外部题解（kaggle-solutions）
- rank 5｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561580
- rank 6｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561518
- rank 7｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561447
- rank 8｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561515
- rank 10｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561844
- rank 11｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561837
- rank 12｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561607
- rank 13｜description：https://www.kaggle.com/c/czii-cryo-et-object-identification/discussion/561422

---

## fathomnet-out-of-sample-detection — FathomNet 2023（Out-of-Sample Detection）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 FathomNet 2023 ｜ 队伍 69 ｜ 截止 2023-05-23 ｜ Tier B ｜ 标签 cv,detection,wildlife
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/fathomnet-out-of-sample-detection.md
> 材料基础：`digests/fathomnet-out-of-sample-detection.md`（6 篇正文：4th 413092 / 新手入门 397069 / 标签错误 407400 / 往届相似赛 397024 / metric 修复 404769 / 组队 397070；29 条主题索引）+ 2 张归档图

### 一句话重述
海洋生物图像任务：既要把样本分到已知类别，又要判断它是否**超出已知类别（Out-of-Sample Detection）**。数据极端长尾且标签噪声大（290 个类别中 **157 个没有对应图像**，同族/属/目名称混乱）；4th 的方案非常"轻"：把少于 10 张图的类别并入 zero class，用 EfficientNetV2B0 + label smoothing 0.1 训练 6 模型集成，**OSD 分数 = 1 − max(类概率)，再叠加 5× 各类预测标准差**。赛程中还出现过 metric 的 AUC 部分计算 bug，官方修复并重新计分——提醒大家**必须自己核对评测实现**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与任务 | **69 队**；290 个类别（其中 **157 个无语料图像**）；分类 + OSD；FGVC10/CVPR 相关 | 398752 / 索引 |
| 4th 预处理 | 把**少于 10 张图**的类别并入 zero class（unknown），只留数据充足的类别训练/验证 | 413092 |
| 4th 训练 | EfficientNetV2B0（ImageNet 预训练）+ 128 维 Dense + 输出层；输出层按正负样本不均衡初始化；两阶段微调（先冻结 base，再解冻 2 个顶层）；**label smoothing 0.1** 在噪声标签下最好；6 模型集成 | 413092 |
| 4th 推理 | 类别：6 模型概率平均后取 **>0.4**；OSD：每模型 `1 − max(prob)`，最终 = **平均 OSD + 5×平均标准差** | 413092 |
| 数据/标签问题 | 类别名称层级错误（如 Acanthascinae/Rossellidae、Careproctus 属下三种、Lyssacinosida 目）；团队用 FathomNet API + marinespecies.org 交叉核验并回馈重标注 | 407400 |
| 评测问题 | metric 的 **AUC 部分有 bug**，官方修复后重新计分；另有 MAP@20 与评测代码不一致、评测报错、null 提交等帖 | 404769 / 410140 / 401858 |
| 上手门槛 | 图片需从源站下载且慢；官方 `download_images.py` 参数报错；submit 格式/规则（额外数据集）问题多 | 397071 / 410908 / 410430 / 407096 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 4th（分类 + 不确定度） | 社区数据线 |
| --- | --- | --- |
| 类别 | 长尾并入 unknown | 用 API/外部站补稀有类 |
| 模型 | EfficientNetV2B0 ×6 + 标签平滑 | — |
| OSD | 1−max(prob) + 5×std | — |
| 风险 | 阈值/权重经验化 | 标签错误与规则限制 |

### 共识 / 分歧 / 裁决
**共识一：OSD 可以用"置信度补集 + 集成不确定度"做基线（413092；置信度中高）**
`1 − max(prob)` 给出 OOD 直觉分数；叠加集成预测标准差把"模型间分歧"变成 OSD 信号。**裁决**：先做该基线，再考虑专门 OOD 方法（energy/Mahalanobis/生成式）；所有阈值在 OOF 上定。置信度：中高。

**共识二：极端长尾 + 噪声标签要"归并 + 平滑"（413092 / 407400 / 398487；置信度中高）**
<10 图类别归 unknown、label smoothing 0.1 是 4th 的显式选择；社区另帖讨论标签噪声处理。**裁决**：先统计每类样本数与层级一致性，把不可学类别并入 unknown；标签平滑/噪声鲁棒损失作为默认项。置信度：中高。

**事件一：评测实现必须自行核对（404769 / 410140 / 401858；置信度中高）**
官方修过 AUC 部分的 bug；选手也发现 MAP@20 与评分代码不一致。**裁决**：下载官方 metric 实现，用构造样本做单元校验；分数突变先怀疑评测而非模型。置信度：中高。

**事件二：数据获取与规则是结构性门槛（397071 / 410908 / 407096；置信度中）**
图片来源分散、下载慢、脚本参数报错、外部数据集边界模糊。**裁决**：先用官方下载脚本/公开打包数据建最小集，再按规则补充；外部数据先发帖确认。置信度：中。

**事件三：竞赛文化（最后一周不公开高分 notebook）（397069；置信度中）**
官方说明最后一周禁用公开 notebook 发布，鼓励此前分享。**裁决**：把关键 notebook 在截止前保留；学习阶段多读已公开的 EDA/入门帖。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 4th 的完整配方 | 自述 + 2 张图（413092） | 中高 |
| 290 类 / 157 类无图 | 社区统计帖（398752） | 中高 |
| 标签层级错误 | 社区帖（407400） | 中 |
| metric bug 与重算 | 官方帖（404769） | 高 |
| 下载/规则问题 | 多帖（397071 等） | 中高（现象） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st–3rd 方案未归档，4th 是唯一可读方案；
- OSD 的官方定义与最优阈值策略无归档说明（411135 在问）；
- 类别重标注是否被官方采纳未归档；
- 外部数据集/规则澄清答复未归档；
- **图证缺口**：无（2 张图，本深读内嵌 2 张）。

### 图证（KStarter 仓库内路径）
- ../../intel/fathomnet-out-of-sample-detection/bodies/413092_img/01.png — 预处理后的类别分布
- ../../intel/fathomnet-out-of-sample-detection/bodies/413092_img/02.png — OSD 概率分布

### 出处
- 4th 方案（5 票 / 0 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/413092
- 标签错误讨论（6 票 / 2 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/407400
- metric 修复与重算（3 票 / 0 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/404769
- 157/290 类无图（2 票 / 1 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/398752
- 往届相似赛（19 票 / 2 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/397024
- 新手入门（9 票 / 3 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/397069
- MAP@20 不一致（2 票 / 2 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/410140
- 下载脚本参数报错（2 票 / 10 评论）：https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/397071

---

## gan-getting-started — I'm Something of a Painter Myself（GAN Getting Started）轻量深读（Tier B）

> 主题 cv ｜ 类别 Getting Started ｜ 指标 PostProcessorKernel ｜ 队伍 0 ｜ 截止 2026-06-30 ｜ Tier B ｜ 标签 cv,generative
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/gan-getting-started.md
> 材料基础：`digests/gan-getting-started.md`（6 篇正文：GAN 资源大全 178253 / GAN 常见问题 180515 / 往届 GAN 赛经验 178182 / 基础阅读 178185 / 官方欢迎 178166 / 十大论文 185910；80 条主题索引）+ 1 张归档 GIF

### 一句话重述
Kaggle 首个生成式 Getting Started 赛：**生成 Monet 风格画作**（可从零生成或做照片风格迁移），官方明确这是学习资源——**无奖励、无截止、无私有排行**，重点是 CV/生成模型/TPU/TFRecords 四件事；官方提供 CycleGAN 教程，允许加入外部数据，但**提交真实 Monet 画作或其变换被禁止**。材料几乎全是"GAN 学习地图"：资源大全、论文十篇、常见问题、往届 Generative Dogs 的 BigGAN 冠军方案与 GAN hacks。真正要动手时，瓶颈在**提交流程（images.zip / PostProcessorKernel）与 GAN 训练稳定性**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 赛制定位 | 无奖励、无截止、无私有榜，长期开放；目标是熟悉 CV、生成模型、TPU、TFRecords；官方 CycleGAN 教程；禁止提交真实 Monet 或其变换 | 178166 |
| 资源大盘（24 票） | 书籍（Goodfellow DL ch20、Chollet ch8、GANs in Action）；模型族（GAN/DCGAN/cGAN/SS-GAN/InfoGAN/ACGAN/WGAN/WGAN-GP/LSGAN/Pix2Pix/CycleGAN/BigGAN/PG-GAN/StyleGAN/StackGAN/3DGAN/BEGAN/SRGAN/DiscoGAN/SEGAN）；实现库（PyTorch-GAN、Keras-GAN）；往届 Kaggle Generative Dogs top5；Jason Brownlee 稳定训练清单 | 178253 |
| 稳定训练清单 | stride 卷积下采样/上采样、LeakyReLU、BatchNorm、高斯权重初始化、Adam、图像缩放到 [-1,1]、高斯潜空间、真假 batch 分开、label smoothing、noisy labels | 178253 |
| GAN FAQ（49 票 / 11 评论） | 论文清单（GAN 总览/大规模研究/正则与归一化综述/医学影像综述）、课程、书籍与教程 | 180515 |
| 往届经验（29 票） | Generative Dogs：GAN/DCGAN 入门、latent walk、Autoencoder、RaLSGAN、ACGAN、BigGAN（冠军）等 notebook + "GAN 会记忆还是泛化 / All you need is GAN Hacks" 等帖 | 178182 |
| 其他入口 | 十大论文（23 票）；基础阅读（25 票）；CUT（5 票，比 CycleGAN 更快更轻）；Stable Diffusion 讨论（5 票）；GAN Hacks 代码帖（9 票）；"SOTA GANs in fewest lines"（8 票）；TPU Star 奖励活动（19 票） | 索引 |
| 提交/评测坑 | zip 里没有图片、Evaluator 找不到 images.zip、output file not found、如何提交预测、PyTorch 是否可用/是否必须 TPU；有 starter 报告 LB 61.3 | 232028 / 182394 / 546881 / 179933 / 249028 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 官方 CycleGAN 路线 | 替代生成路线 | 资源学习路线 |
| --- | --- | --- | --- |
| 输入 | 照片域 → Monet 域 | CUT/其他 image translation；Stable Diffusion | 论文/课程/往届 notebook |
| 优势 | 官方教程、直接对齐评测 | 更快/更新 | 建立直觉与调参能力 |
| 风险 | 训练不稳定、模式坍缩 | 规则/风格合规风险 | 不动手则学不到 |
| 交付 | images.zip + PostProcessorKernel | 同 | — |

### 共识 / 分歧 / 裁决
**共识一：这是"学习型比赛"，产出标准是跑通端到端生成管线（178166 / 178253；置信度高）**
无奖励、无截止、无私有榜；官方把它定义为 CV/生成模型/TPU/TFRecords 的练习场。**裁决**：目标定为"复现 CycleGAN 并提交一次合法 images.zip"，再谈分数与风格创新。置信度：高。

**共识二：先抄稳定训练 checklist，再改架构（178253；置信度中高）**
资源帖给出 10 条 GAN 训练技巧（stride conv、LeakyReLU、BN、Adam、[-1,1]、label smoothing 等）。**裁决**：任何新架构先在 checklist 基础上消融，别一上来改损失/加模块。置信度：中高。

**事件一：往届 Generative Dogs 是最佳模板库（178182；置信度中高）**
DCGAN/BigGAN/RaLSGAN/ACGAN/latent walk 等 notebook 与"记忆 vs 泛化"讨论可直接迁移到 Monet 生成。**裁决**：先复现其中一个 notebook 的训练/采样流程，再替换成 CycleGAN。置信度：中高。

**事件二：提交流程是新手第一道坎（232028 / 182394 / 546881；置信度中高）**
zip 结构、images.zip 路径、output file not found 等问题反复出现。**裁决**：先用官方 sample/最小模型提交一次，确认 zip 结构与 PostProcessorKernel 通过后再投入训练。置信度：中高。

**分歧：是否用更新的扩散模型/替代 GAN（523260 / 180742；置信度中）**
社区讨论 Stable Diffusion 与 CUT（比 CycleGAN 更快更轻）。**裁决**：技术上任选，但必须满足"不得提交真实 Monet 或其变换"的规则；若用外部预训练模型生成，注意风格来源与合规声明。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 赛制定位与允许/禁止项 | 官方欢迎帖（178166） | 高 |
| GAN 资源与稳定训练清单 | 高票社区帖（178253） | 中高（外部资料汇总） |
| 往届 notebook 与冠军方案 | 社区帖 + 链接（178182） | 中高 |
| 提交格式问题 | 多帖（232028 / 182394 等） | 中高 |
| CUT/Stable Diffusion 讨论 | 低票帖（180742 / 523260） | 中低 |
| 评测分数（61.3 等） | 单帖 starter（249028） | 中低 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 无官方排行榜/获奖方案（Getting Started 定位如此）；
- PostProcessorKernel 的评分细节与最优分数无系统归档；
- 外部数据与预训练生成模型在"Monet 变换"规则下的边界无官方澄清；
- 数据集重复与个别图片异常（189404 / 196946）未定论；
- **图证缺口**：唯一归档图是 GAN Lab 演示 **GIF（2.5MB）**，按规则不内嵌；已登记。

### 出处
- 官方欢迎与规则（53 票 / 40 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/178166
- GAN 资源大全（24 票 / 3 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/178253
- GAN 常见问题（49 票 / 11 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/180515
- 往届 GAN 赛经验（29 票 / 4 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/178182
- 基础阅读（25 票 / 5 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/178185
- 十大论文（23 票 / 7 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/185910
- 如何提交预测（3 票 / 5 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/232028
- CUT 替代方案（5 票 / 1 评论）：https://www.kaggle.com/competitions/gan-getting-started/discussion/180742

---

## geolifeclef-2022-lifeclef-2022-fgvc9 — GeoLifeCLEF 2022（LIFECLEF/FGVC9 物种分布预测）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 MeanBestErrorAtK ｜ 队伍 52 ｜ 截止 2022-05-24 ｜ Tier B ｜ 标签 cv,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/geolifeclef-2022-lifeclef-2022-fgvc9.md
> 材料基础：`digests/geolifeclef-2022-lifeclef-2022-fgvc9.md`（6 篇正文：2nd 328637 / 1st 327055 / 资源汇编 312283 / working note 说明 325984 / .tif 处理 311983 / 往届挑战 312112；23 条主题索引）+ 2 张装饰性归档图

### 一句话重述
给定位置 + 遥感影像 + 环境协变量，预测该处最可能出现的 **30 个物种**（17,034 类，presence-only 单标签）。两条获奖路线互补：1st 走**多模态集成**——两条 CNN（NIR+RGB / RGB+NIR，ResNet34 与 MobileNetV3）接环境向量 + 坐标 + 土地覆盖编码，再加一个 **Random Forest（81 特征）**，三模型概率平均 + TTA；2nd 只用遥感影像双分支 CNN，但提出关键的 **spatial block-label swap**（同 0.01° 网格内以 10% 概率换邻居标签）解决"未观测 ≠ 不存在"的标签病态问题，单项 +2%。官方特别提醒：**公榜只占 10% 测试数据，噪声大，应以验证分为准**；且赛后必须提交可复现的 working note，否则成绩可能从正式发表中移除。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与任务 | **52 队**；17,034 个物种（top-30 误差）；近 200 万数据点；presence-only 单标签；公榜仅 **10%** 测试数据 | 327055 / 328637 / 325984 |
| 1st 集成 | ① ResNet34 双模态（NIR+G+B）+ 3 层 FCN（环境向量 + lat/lon + country + 海拔均值/极差 + landcover "dothot" 编码）→ 17k 分类层；② MobileNetV3-large（R+G+B+NIR）+ 同款 FCN + 2048 维 Linear/dropout/ReLU；③ **Random Forest（32 树、深度 12、81 特征**：环境 + 坐标 + landcover dothot + R/G/B/NIR 的 25/50/75 分位），并把验证集加入训练；TTA 5 次随机变换，三模型概率平均 | 327055 |
| 2nd 单模配方 | 两条不共享参数的 CNN 分支：RGB；海拔+NIR+NDVI → concat → **dropout 0.45** → 17,034 类 softmax CE；Inception-v4 比 ResNet-50 约 **+2%**；ImageNet 预训练 > MoCo-v2 自监督/MAML/ANIL/从头训；**spatial block-label swap（10% 概率）单项 +2%**；10 模型按 TTA 置信度方差做伪置信度集成再 **+2%** | 328637 |
| 无效尝试 | 2nd：环境协变量与 GPS 直接入 CNN（坐标 MLP 各种编码都欠拟合）、taxonomy 辅助任务、直方图密度预测、长尾专门处理（**"什么都不做"最好**，因为测试集同样长尾）；1st：多标签聚合、其他骨干、无迁移学习、三骨干分工、GBDT（17k 类约需 TB 级内存） | 328637 / 327055 |
| 核算力 | 2nd 用 2×RTX 3090 工作站 + V100 HPC，PyTorch 1.9；1st 用 RTX 3090（24GB）×2 + 大内存跑 RF | 328637 / 327055 |
| 学术交付 | CLEF working note **强制**：6/1 截止，轻审后 6/13 反馈、7/1 终稿；收入 CEUR-WS 并分配 DOI；**无法复现的 run 可能从正式结果中移除** | 325984 |
| 数据/格式 | `.tif` 读取方案（tifffile / PIL / cv2）；环境向量列名编码问题；GDAL 资源；往届 2017–2021 挑战与论文链接 | 311983 / 313558 / 312250 / 312112 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st（多模态集成） | 2nd（双 CNN + 标签松弛） |
| --- | --- | --- |
| 影像分支 | ResNet34(NIRGB) + MobileNetV3(RGBNir) | ResNet50→Inception-v4(RGB; Alt+NIR+NDVI) |
| 表格/协变量 | FCN/随机森林吃环境向量、坐标、landcover、分位数 | 尝试入 CNN 失败（承认对手用 RF 更对） |
| 标签处理 | 单标签 + 验证集加训 | **block-label swap（10%）** |
| 集成 | 3 模型概率平均 + TTA | 10 模型伪置信度集成 + TTA |
| 关键结论 | 结构化/非结构化各用合适骨干再融合 | 长尾"不处理"最好；ImageNet 预训练最实用 |

### 共识 / 分歧 / 裁决
**共识一：presence-only 单标签是病态问题，需要标签松弛或概率融合（328637 / 325767 / 327055；置信度中高）**
2nd 的 block-label swap 明确针对"未观测≠不存在"，+2%；1st 提到同一地点可有数百个正确标签、存在理论 top-30 下限。**裁决**：先用网格邻域标签松弛/温度 softmax/多标签聚合等手段建模不确定性，并在验证集上对比；不要用硬 CE 直接拟合单标签。置信度：中高。

**共识二：图像与环境协变量要用各自合适的模型族（327055 / 328637；置信度中高）**
1st 的 RF 在环境协变量上贡献被 2nd 明确认可；2nd 把协变量塞进 CNN 全部失败。**裁决**：遥感影像走 CNN/预训练骨干，环境/坐标走树模型或自注意力；在最终层或概率层融合，避免强行端到端。置信度：中高。

**事件一：长尾"不处理"反而最优（328637；置信度中）**
由于测试集与训练同样长尾，加权稀有类会伤害整体 top-30 误差。**裁决**：先确认评测集的类别分布再决定是否重加权；top-K 指标下"分布匹配"比"均衡"更重要。置信度：中（单一强自述 + 解释合理）。

**事件二：公榜只占 10%，必须信验证分（325984；置信度高）**
官方直接提醒公榜噪声大、私榜可能翻盘。**裁决**：模型选择以本地验证（与官方 top-30 口径一致）为准，公榜只做格式 sanity check。置信度：高。

**事件三：working note 是"成绩是否被承认"的门槛（325984；置信度高）**
CLEF 要求可复现的技术报告，未通过可能被移出正式结果；同时提供 DOI 与检索。**裁决**：把 working note 当第二交付物，从第一天维护可复现的实验日志。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的三模型集成细节 | 冠军自述（327055） | 中高（无分数表） |
| 2nd 的 +2%/+2% 消融与失败清单 | 亚军自述（328637） | 中高 |
| working note 强制与 DOI | 官方帖（325984） | 高 |
| 公榜 10% 提醒 | 官方帖（325984） | 高 |
| .tif 读取方法 | 社区帖（311983） | 中高（技术常识） |
| 标签病态问题 | 2nd + 讨论帖（328637 / 325767） | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st/2nd 的私榜分数未在正文给出；完整技术报告在站外；
- 多标签聚合的最优实现（1st 尝试失败）仍未解决；
- 环境协变量与坐标的最优融合方式（2nd 建议进一步研究）未定论；
- 本场没有 3rd 及以后方案的归档正文；
- **图证缺口**：归档图仅 2 张装饰性图片（Kaggle 毛衣与风景照），无分析证据，未内嵌；分析图证缺口已登记。

### 出处
- 1st 方案（11 票 / 5 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/327055
- 2nd 方案（4 票 / 0 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/328637
- working note 与纪律（3 票 / 0 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/325984
- 资源汇编（8 票 / 2 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/312283
- .tif 处理（11 票 / 3 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/311983
- 往届挑战与论文（10 票 / 1 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/312112
- 单标签误导讨论（3 票 / 6 评论）：https://www.kaggle.com/competitions/geolifeclef-2022-lifeclef-2022-fgvc9/discussion/325767

---

## geolifeclef-2024 — GeoLifeCLEF 2024 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 F-Score Beta (Micro) ｜ 队伍 51 ｜ 截止 2024-05-24 ｜ Tier B ｜ 标签 cv,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/geolifeclef-2024.md
> 材料基础：`digests/geolifeclef-2024.md`（6 篇正文：working note 邀请 506431 / 新手门槛吐槽 481283 / Discord 规则 480782 / 论文推荐 480732 / ClimateClef 数据 481485 / FGVC11 其他赛 486162；21 条主题索引）+ 1 张归档图

### 一句话重述
GeoLifeCLEF 2024：用**卫星时序 + 气候/环境栅格 + 图像**预测物种分布（F-Score Beta Micro），属于 FGVC11 + LifeCLEF（CVPR/CLEF）研究赛。材料的两条主线非常清晰：① **研究赛的第二交付物是 working note**——6/7 截稿、6/21 通知、7/8 camera-ready，收入 CEUR-WS，优秀者进 LNCS 并获会议注册费；② **数据获取是最大门槛**——原始栅格在 Seafile，官方 `download.py` 让新手卡住，`GLC.plotting` 在 Kaggle 环境不可用，社区因此自行打包上传 **ClimateClef** 气候栅格数据。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与定位 | **51 队**；F-Score Beta (Micro)；官方称 LB **>0.4** 已是显著成绩；FGVC11（CVPR）+ LifeCLEF（CLEF）联合研究赛 | 506431 |
| working note 时间线 | 竞赛 5/24 截止 → **6/7 论文截稿** → 6/21 录取通知 → 7/8 camera-ready；CEUR-WS 出版，择优进 Springer LNCS，最佳论文获 CLEF 注册费 | 506431 |
| 数据访问 | PA 数据在 Kaggle；**原始栅格在 Seafile**，需分组下载 zip；官方建议 `python download.py --data output --raster --presence-only --all-variables` | 481283 |
| 社区补丁 | 选手自行上传 **ClimateClef**（气候环境栅格 zip）到 Kaggle 并给 Seafile 链接（20 票）；另有"图表/数据关系"等多帖答疑 | 481485 |
| 新手门槛（20 票） | `download.py` 语法错误/文件不存在；`GLC.plotting` 模块在 Kaggle 无法安装；首次加载数据 10 分钟；最后只画出 2 张欧洲植物分布图——作者呼吁研究赛更友好 | 481283 |
| 方法线索 | 推荐卫星图像分类综述与湿地物种多样性遥感论文；社区讨论"用 Transformer 融合多模态信息"；Landsat 时序、卫星 patch、PA/PO 关系、cube 维度等问题 | 480732 / 500432 / 497807 / 482176 |
| 周边 | FGVC11 其他 Kaggle 赛（数据格式相近，可多赛复用）；官方 Discord；CLEF 2025 是否会继续（9 评论） | 486162 / 480782 / 561689 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 官方路线 | 社区补丁路线 | 新手实际体验 |
| --- | --- | --- | --- |
| 数据 | Kaggle PA + Seafile 栅格 | ClimateClef 打包上传 | 下载/模块报错 |
| 方法 | 多模态（图像 + 遥感 + 气候） | 论文与 Transformer 融合探索 | 先能画图 |
| 交付 | 预测 + working note | notebook 分享 | 卡在环境 |

### 共识 / 分歧 / 裁决
**共识一：研究赛的完成标准包含"可复现论文"（506431；置信度高）**
官方明确要求 working note 提供足够复现最终 run 的信息，并有严格时间线（6/7 → 7/8）。**裁决**：从第一天就维护实验日志与数据版本；把论文写作排进赛程而不是赛后补。置信度：高。

**事件一：数据获取/工具链是本届最大门槛（481283 / 481485；置信度中高）**
Seafile 下载脚本对新手不友好、GLC 模块不可用、加载耗时；社区用 ClimateClef 直接绕开。**裁决**：优先用社区打包数据；下载流程写成脚本 + 校验和；提前在 Kaggle 环境验证依赖。置信度：中高。

**共识二：多模态融合（图像 + 遥感时序 + 环境栅格）是主线（480732 / 500432 / 497807 / 499314；置信度中）**
官方与社区都在讨论 satellite/Landsat/Transformer 融合。**裁决**：先复现单模态基线（图像分类 / 遥感特征），再用 Transformer 或双塔融合作增量；注意时间对齐（Landsat 时序）。置信度：中。

**事件二：低参赛量 + 数据复杂度 = 环境与文献成本高于建模（481283 / 506431；置信度中）**
51 队、研究赛属性；官方感谢"超过 0.4"的少数队伍。**裁决**：评估投入产出：如果目标是论文与会议，值得；如果只冲榜，先看数据获取成本。置信度：中。

**事件三：排名/作者归属等研究赛规则要提前问（507399 / 486171；置信度中）**
最终报告与排名、credit 归属被专帖询问。**裁决**：赛前确认作者顺序、团队注册与报告要求，避免赛后争议。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| working note 时间线与出版路径 | 官方帖（506431） | 高 |
| 数据访问方式与下载脚本 | 官方数据页引用（481283） | 高（存在问题） |
| ClimateClef 社区数据 | 资源帖 + 链接（481485） | 中高 |
| 新手门槛 | 高票吐槽帖（481283） | 中高（个人经历） |
| 方法文献线索 | 社区推荐（480732 / 500432） | 中 |
| FGVC11 赛群 | 官方帖（486162） | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 本赛 1st–10th 方案未归档（官方邀请所有参赛者写 working note，但 Kaggle 侧只有邀请帖）；
- 最终排名与获奖名单未归档；
- 数据下载脚本问题是否有官方修复未归档；
- CLEF 2025 是否续办未定（561689）；
- **图证缺口**：无（1 张图，已内嵌；仅为报错截图）。

### 图证（KStarter 仓库内路径）
- ../../intel/geolifeclef-2024/bodies/481283_img/01.png — download.py 报错截图

### 出处
- working note 邀请（8 票 / 4 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/506431
- 新手门槛吐槽（20 票 / 3 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481283
- ClimateClef 数据集（20 票 / 4 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481485
- Discord 规则（7 票 / 0 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/480782
- 论文推荐（4 票 / 3 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/480732
- FGVC11 赛群（5 票 / 0 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/486162
- 报告与排名问题（2 票 / 5 评论）：https://www.kaggle.com/competitions/geolifeclef-2024/discussion/507399

---

## google-research-identify-contrails-reduce-global-warming — Google Research - Identify Contrails 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 contrails_global_dice ｜ 队伍 954 ｜ 截止 2023-08-09 ｜ Tier B ｜ 标签 cv,retrieval,review
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/google-research-identify-contrails-reduce-global-warming.md
> 材料基础：`digests/google-research-identify-contrails-reduce-global-warming.md`（6 篇正文：1st 430618 / 2nd 430491 / 3rd 430685 / 5th 430549 / 9th 430479 / 失败实验帖 414344；80 条主题索引）+ 7 张图

### 一句话重述
在卫星红外假彩图上分割凝结尾迹（contrails），类像素占比 ~0.18%，细线状（数像素宽）→ **像素级精度 + 噪声标注 + 硬标签评测**三重叠加。真正的考点是**标签错位（0.5 像素平移）这个数据缺陷**：识别它的队伍解锁了 flip/rot90 增强与 TTA（+0.005~0.01），没识别的队伍被它锁死。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（430618） | U-Net + MaxViT-Tiny 编码器；**发现标签相对影像向右下偏移 0.5 像素**（用"旋转 180° 后预测出现蓝-绿-红条纹"诊断）；解法：训练**对称化标签 y_sym**（512² 双线性重采样）+ 5×5 stride-2 小卷积学 y_sym→y，推理端 8 模式 TTA（+0.006）；有增强可训 40–50 epoch（无增强仅 10–20）；两模型加权（阈值 ~0.45）：单时刻 t=4（1024²）与四时刻拼图（t=1–4 拼成 1024²，只把 H/2 四分之一喂解码器）。分数：单时 512 0.712 / 单时 1024 0.716 / 4 拼 0.722 / **集成 0.724 priv**（CV 0.706, pub 0.725） | 1st |
| 2nd（430491，111 票） | 软标签（标注者平均）+ **输入上采样 ×2/×4 与像素重排（pixel shuffle）解码**（细线任务的关键）；底座 CoaT（最佳单模 **0.7039 CV / 0.71790 priv**）/ NeXtViT / SAM-B / EffNetV2-s；**时序混合放在低分辨率特征图（res/32、res/16）**（云位移 10–30px，3D 卷积/VideoSwin 不可用），LSTM 最佳、多帧 +0.01；损失 BCE+dice-Lovasz（**放宽阈值最优区间**→减少私榜抖动）；PL（外采 GOES16）提升单模但降低集成多样性；**标准 K 折因瓦片空间重叠会高估 CV**，改用整训练集多 seed + 官方验证。8 模型集成 0.72574 pub / 0.72304 priv | 2nd |
| 3rd（430685） | 2.5D U-Net：把多帧塞进 batch 维跑 2D 底座，**3D 卷积插在 skip connection 各层级**（+0.02，优于只在 U-Net 末端加 3D）；小比例 flip/rot90 仍有小增益；伪标签按 0.25 离散化后预训练+原数据微调；**百分位阈值**（最优≈正像素比 0.16%）；dice 的启发式平滑（分子 +700000/分母 +1000000）；18 模型集成 priv 0.72233；最佳单模 maxvit_large 0.71629 pub——**因最后一天加入全量 flip/TTA 版本，与第 2 名只差 0.00001** | 3rd |
| 5th（430549） | EffNetV2L + 自研 3D U-Net（每帧同编码器、各层级 Conv3D 融合、UNet 解码）；双目标（1 通道 sigmoid 75% + 5 通道 softmax 按标注者比例 25%）；Lion 优化器；**自己标定出 x=0.408, y=0.453 的错位量**后 TTA8 可用（+0.005~0.01）；最佳单模 priv 0.71443 | 5th |
| 9th（430479，76 票） | 独立推断出错位来源：**多边形转掩码时最左点未计入、最右点计入**；给出两种修法：①训练用"一致翻转"的掩码 ②**影像整体平移 0.5 像素**（warpAffine 矩阵含 1.5 偏移，需标定）；选方案② | 9th |
| 失败实验帖（414344，112 票） | 早期"所有增强都掉分"、2.5D 掉分、MiT/SegFormer/DeepLab 更差、BCE+dice 组合无增益、辅助分类头失败；但"更大底座 + 更大分辨率 + 伪标签 + 阈值"把 0.61 → 0.67+；CV/LB 在后期失联 | 414344 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 5th | 9th |
| --- | --- | --- | --- | --- | --- |
| 错位处理 | y_sym + 小卷积映射 | 不用 flip/rot90（赛后才发现） | 小比例使用 | **自标定偏移量** | 图像平移 0.5px |
| 主干 | MaxViT-Tiny + U-Net | CoaT/NeXtViT/SAM/EffNetV2 | 多种（maxvit_large 最佳单模） | EffNetV2L + 3D U-Net | U-Net（强底座） |
| 时序 | 4 帧拼图（空间拼接） | **低分辨率特征 LSTM/Transformer 混合** | 3D 卷积进 skip | Conv3D per level（可换 ConvLSTM2D） | 不做 |
| 标签 | soft + y_sym | soft（标注者平均） | 平均掩码 + 离散伪标签 | 双目标（软 + 标注者分布） | 个体标注全用 |
| 阈值 | ~0.45（验证调） | 0.46–0.50（lovasz 让阈值更宽） | **百分位（≈正像素比）** | 后处理阈值 | — |
| priv | **0.724** | 0.72304 | 0.72305（差 0.00001 屈居第 3） | 0.71443（最佳单模） | — |

### 共识 / 分歧 / 裁决
**共识一：0.5 像素错位是本场的"元问题"（1st/5th/9th 独立发现）**
早期所有人都观察到"flip/rot90 一用就掉分"（414344 甚至说"所有增强都无效"）；1st 用旋转后的条纹诊断出标签右下偏移；5th 标定到 x=0.408/y=0.453；9th 从多边形转掩码的边界规则解释成因。**裁决**：数据缺陷无法从统计直觉推得，必须做"单点失效实验 + 可视化诊断"；发现后增强/TTA 变成免费增益（+0.005~0.01，3rd 靠它多活了 18 模型集成）。置信度：高（三方独立 + 图证）。

**共识二：细线分割必须提升"有效像素分辨率"（1st/2nd/3rd/5th）**
1st 直接把输入升到 1024²（0.712→0.716）；2nd 用输入上采样 ×2/×4 + pixel shuffle 解码（"substantial boost"）；5th 用大分辨率 + 大底座；3rd 加大解码器通道。**裁决**：对细结构，分辨率与解码器上采样方式比换更深的网络更有效。置信度：高。

**共识三：阈值选择影响不亚于模型（全队）**
1st 阈值 0.45 用验证调；2nd 的 dice-Lovasz 让阈值最优区间变宽（抗震）；3rd 用**百分位阈值**（≈0.16% 正像素比）；5th 后处理阈值重要。**裁决**：F1/Dice 型指标下阈值是把概率图变集合的关键参数，选择方法要抗分布漂移（百分位/宽最优区间）。置信度：高。

**共识四：时序信息只在低分辨率/浅层有效（1st/2nd/3rd/5th）**
2nd 明确 3D 卷积与 VideoSwin 无效（云位移 10–30px），只有 res/32、res/16 的特征混合有效（LSTM 最佳，多帧 +0.01）；3rd 的 3D 卷积插在 skip 各层（+0.02）；1st 的 3D/ConvLSTM 完全训不起来、改用 2×2 拼图；5th 用 Conv3D 逐层融合。**裁决**：帧间配准不可行时，把时序融合"降分辨率/后置"是对齐误差与信息量之间的折中。置信度：中高。

**分歧：伪标签（PL）**
3rd 用 PL 预训练 + 原数据微调，是 18 模型集成的组成部分；2nd 发现 PL 提升单模但**降低集成多样性**，平均后收益消失；1st 早停 PL（5 折平均后收益不显著）；5th/9th 未大规模使用。**裁决**：PL 在单模上"看起来很强"，但在集成层面常被同质化抵消；要不要用取决于最终提交形态。置信度：中高。

**事件：验证设计（2nd 的警告）**
2nd 指出标准 K 折因训练瓦片空间重叠而**高估 CV**，改为"整训练集多 seed + 官方验证集评估"；3rd 在后期也只信全量训练的验证分；414344 观察到 CV/LB 后期失联。**裁决**：瓦片/空间重叠的数据必须按空间分组验证，否则选择会被系统性误导。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 0.5 像素错位（诊断过程 + 修法） | 自述 + 图 + 三方独立复现 + 公开代码 | 高 |
| 1st 的各模型分数表与 TTA +0.006 | 自述 + 表 + notebook | 高 |
| 2nd 的时序融合位置结论（LSTM 最佳等） | 自述 + 架构图 + 分数表 | 高 |
| 3rd 的 3D 卷积插 skip +0.02 | 自述 + 伪代码 | 中高 |
| 5th 的偏移量 x=0.408/y=0.453 | 自述（与 1st/9th 互证） | 高（现象）/中（具体数值） |
| PL 的集成层面无效 | 2nd/1st 独立自述 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th/6th–8th 方案未入库；
- "Single Model CV-LB Thread"（413153，47 票）、"One month to go 总结"（420629，110 票）两条高票线未细读；
- 3rd 提到的"最后一天全量 flip+TTA 版本导致私榜掉分"只有一句解释（像素错位或波动），无法进一步验证；
- 归档图 7 张中 4 张为方法图（1st 的错位诊断/拼图、2nd 的架构、5th 的 3D U-Net）。

### 图证（KStarter 仓库内路径）
- ../../intel/google-research-identify-contrails-reduce-global-warming/bodies/430618_img/01.png — 1st 的错位诊断
- ../../intel/google-research-identify-contrails-reduce-global-warming/bodies/430618_img/03.png — 1st 的四帧拼图输入
- ../../intel/google-research-identify-contrails-reduce-global-warming/bodies/430491_img/01.png — 2nd 的三类架构与时序混合位置

### 出处
- 1st（430618）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430618
- 2nd（111 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430491
- 3rd（48 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430685
- 5th（41 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430549
- 9th（76 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/430479
- 失败实验帖（112 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/414344
- 单模 CV-LB 线程（47 票）：https://www.kaggle.com/competitions/google-research-identify-contrails-reduce-global-warming/discussion/413153

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/432998
- rank 6｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/430581
- rank 7｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/430691
- rank 8｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/430543
- rank 11｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/432690
- rank 13｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/432254
- rank 14｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/430904
- rank 15｜description：https://www.kaggle.com/c/google-research-identify-contrails-reduce-global-warming/discussion/430483

---

## google-universal-image-embedding — Google Universal Image Embedding 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 PostProcessorKernelDesc ｜ 队伍 1022 ｜ 截止 2022-10-10 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/google-universal-image-embedding.md
> 材料基础：`digests/google-universal-image-embedding.md`（6 篇正文：1st 359316 / 2nd 359525 / 4th 359487 / 5th 359161 / 10th 635 行处 / 数据集帖 715 行处；80 条主题索引）+ 6 张图

### 一句话重述
训练一个**通用 64 维图像嵌入**并在隐藏检索基准上评测，**主办方不提供任何训练数据**——所有队伍必须自己找数据（且受商用许可约束，后来放宽为"论坛提到的公开数据集即可"）。真正的考点是"**预训练权重选择 + 数据组合 + 头部/骨干的训练顺序 + 嵌入空间对齐式集成**"。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（359316） | 完整时间线：① **预训练权重**——ImageNet-22K 权重 0.405；CLIP ViT-L 在 **LAION-400M 31ep 上 0.499**（试遍可用权重）；发现"只取嵌入向量的一部分算均值"可 **+0.010**（"平均太多值会让真实特征被稀释"），随机投影对弱权重有用、对强权重有害；② **训练**：GLDv2-clean + 线性头 + **ArcFace（m=0.5, s=30）**仅 6 epoch → 0.560；③ **迭代加数据**（Products-10k、Shopee、MET、Alibaba goods、H&M、GPR1200、GLDv2-Full、DeepFashion）→ 0.610（再加 epoch 无益）；④ **解冻骨干但用 10× 低学习率、只训 3 epoch，并冻结最后一层 FC**——作者从"线性投影权重 F(C, X) 的剧烈抖动反映类中心几何被破坏"推断这是过拟合根源；FC 加 dropout → **0.650–0.660**；⑤ 单独在 Products-10k 上精调 → **0.671**；⑥ **集成**：朴素集成无效（不同模型的类中心几何 F(C,X) 不同），两条解法：(a) model-soup 式（同 F(C,X)、不同超参/分辨率）224+280 → **0.680**；(b) **用一个线性变换对齐不同模型的 F(C,X) 空间**，从而集成差异更大的模型（更优） | 359316 |
| 2nd（359525） | 数据派：用了 **14 个数据集**（Aliproducts、Art_MET、DeepFashion、DeepFashion2(hard-triplets)、Fashion200K、LargeFineFoodAI、Food Recognition 2022、JD_Products_10K、Landmark2021、Grocery Store、rp2k、Shopee、Stanford_Cars、Stanford_Products），"量大但没做多少筛选"；骨干 **ViT-H/14-224**（open_clip），neck = fc + dropout 0.2 | 359525 |
| 4th（359487） | **两个 CLIP 模型的集成 + model soup**：共训 9 个模型（4×ViT-L-14-336 + 5×ViT-H-14），权重平均成 2 个"汤"；各出 512 维描述子 → **拼接成 1024 维 → PCA 降到 64 维**（图 1）；训练用 **sub-center ArcFace + 自适应 margin**；数据只用 **GLD2020 + Products-10k**（"商品与地标已覆盖本赛约 50% 的分布"），并明确**更多数据对精调无益** | 359487 |
| 5th（359161，"NS embedding"） | CLIP 视觉编码器（LAION-2B 预训练）；**只训头 + ArcFace**；强正则（weight_decay=0.1）；额外特征：**归一化的原始高/宽/长宽比**；TTA；`resize(antialias=True)`；数据：GLR2021（随机删掉 2000 类）、products10k、GPR1200（删 200 个 iNaturalist 类）、food101；公开代码与论文 | 359161 |
| 社区侧 | "自定义起步训练数据集"（110 票）、"**外部数据帖**"（108 票 / 102 评论）、"13 万张图（128/512）"（76 票）、"**预训练模型汇总**"（65 票）、"图像嵌入论文 I"（63 票）、"**数据集许可澄清**"（47 票）、"承认失败并公开 notebook"（38 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 4th | 5th |
| --- | --- | --- | --- | --- |
| 骨干 | CLIP ViT-L（LAION-400M） | ViT-H/14 | ViT-L-14-336 + ViT-H-14 | CLIP（LAION-2B） |
| 训练序 | 线性头 → 解冻骨干（10× 低 LR，3 epoch，**冻结最后一层 FC**） | 头部 + dropout | sub-center ArcFace + 自适应 margin | 只训头 + ArcFace |
| 数据 | GLDv2+Products-10k+…（迭代加） | 14 个数据集 | **只用 GLD2020+Products-10k** | GLR2021+products10k+GPR1200+food101 |
| 集成 | **同 F(C,X) 汤 + 跨空间线性对齐** | — | **2 汤拼接 → PCA 到 64** | TTA |
| 关键洞见 | 类中心几何 F(C,X) 决定集成可行性 | 数据量为王 | 少量高相关数据足够 | 强正则 + 原始尺寸特征 |

### 共识 / 分歧 / 裁决
**共识一：预训练权重（CLIP 系）是起点，且"选权重"比"改结构"重要（1st/4th/5th）**
1st 花大量精力试遍 CLIP/ImageNet 权重（0.405→0.499）；4th/5th 直接用 open_clip 的 LAION 权重。**裁决**：无数据赛先做"权重普查"（含各训练集/epoch 版本），结构改动风险高（"预训练权重对新增结构很脆弱"）。置信度：高。

**共识二：检索式指标下，集成必须在"嵌入空间"层面做（1st/4th）**
1st 明确指出朴素集成不行的原因是"各模型类中心几何 F(C,X) 不同"，给出两条路（同空间的 model soup；跨空间的线性对齐）；4th 用"两个模型拼接 → PCA"实现集成。**裁决**：度量学习模型的集成等价于"对齐/拼接嵌入空间"，不能直接平均预测。置信度：高。

**共识三：数据选择是核心竞争点（全员 + 108 票外部数据帖）**
1st 迭代加数据集（+0.05）；2nd 用 14 个数据集；4th 只用 GLD2020+Products-10k 也能第 4（并称"更多数据无益"）；社区外部数据帖 102 条评论、110 票的起步数据集帖。**裁决**：无数据赛的胜负主要在"数据组合与许可合规"，而不在模型；但"数据越多越好"不成立（4th 的反例）。置信度：高。

**分歧一：训练多少（头-only vs 解冻骨干）**
5th 只训头；1st 发现只训头很快到瓶颈（0.610），解冻骨干必须以 10× 低 LR、短训并冻结最后一层 FC 才有效；2nd/4th 也训骨干/多模型。**裁决**：强预训练权重 + 小数据时"只训头"最稳；要再提升必须用极保守的骨干微调（低 LR、短程、冻结投影层）。置信度：中高。

**分歧二：数据规模**
2nd 用 14 个数据集（量大不筛选）；4th 只用 2 个（覆盖约 50% 分布）且称更多无益；1st 迭代加入后收敛。**裁决**：数据要"匹配目标分布"（商品+地标占本赛一半），不是越多越好。置信度：中高。

**事件：许可与规则（47 票澄清帖）**
比赛禁止无商用许可的数据集，一度导致几乎所有队伍可能违规；1st 发帖询问后 host 放宽为"论坛提到的公开数据集可用"。**裁决**：无数据赛的规则边界要先问清（合规风险会直接影响方案）；登记本场治理演进。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的分数链（0.499→0.671→0.680）与 F(C,X) 论证 | 自述 + 公开代码 | 高 |
| 4th 的 2 汤 + PCA 与"更多数据无益" | 自述 + 管线图 + 开源仓库 | 中高 |
| 5th 的强正则与尺寸特征 | 自述 + 论文/代码 | 中高 |
| 2nd 的 14 数据集与 ViT-H14 | 自述 | 中 |
| 许可澄清 | 官方回复帖 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd/6th–9th 与 10th 的方案未细读；"预训练模型汇总"（65 票）与"承认失败并公开 notebook"（38 票）未细读；
- 1st 的"跨空间线性对齐"具体实现（求解方式与代价）未展开；
- 各队的 64 维降维方法（PCA/随机投影/线性层）比较分散；
- 归档 6 图：4th 的管线图（图 1）、5th 与另一队的 2 张图为图证。

### 图证（KStarter 仓库内路径）
- ../../intel/google-universal-image-embedding/bodies/359487_img/02.jpg — 4th 的双模型集成与降维

### 出处
- 1st（359316）：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359316
- 2nd（555 行处）：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359525
- 4th：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359487
- 5th（65 票）：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359161
- 外部数据帖（108 票）：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/337384
- 自定义训练集（110 票）：https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/336574

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359401
- rank 9｜code：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359351
- rank 10｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359271
- rank 12｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359497
- rank 13｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359341
- rank 18｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359490
- rank 25｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359410
- rank 28｜description：https://www.kaggle.com/c/google-universal-image-embedding/discussion/359618

---

## happy-whale-and-dolphin — Happywhale - Whale and Dolphin Identification 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 MAP@{K} ｜ 队伍 1588 ｜ 截止 2022-04-18 ｜ Tier B ｜ 标签 cv,audio,ranking,wildlife
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/happy-whale-and-dolphin.md
> 材料基础：`digests/happy-whale-and-dolphin.md`（6 篇正文：1st 320192 / 3rd 319896 / 19th 320298 / 往届方案 304504 / 降分辨率数据集 304686 / 裁剪数据集 319245 等；80 条主题索引）+ 7 张图

### 一句话重述
从任意角度/光照的鲸豚照片识别个体（长尾 + 开集）。真正的考点是**裁剪策略（多来源 bbox 混合）+ ArcFace 系度量学习 + knn/logit 双路后处理 + 伪标签**——本场是"伪标签改变名次"的标志性案例。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（320192，198 票） | sub-center ArcFace（k=2）+ 动态 margin（Optuna 在小模型 256px/effnet-b0 上调参）；**bbox 混合增强** fullbody:fullbody_charm:backfin:detic:none = 0.60:0.15:0.15:0.05:0.05（backfin 显著提分）；测试取两种 fullbody 预测均值；effnet_b5–b7/v2m/v2l（b7 最佳单模）；GeM p=3 + 头前 BN + 两级特征拼接；**头 lr = backbone lr ×10**；后处理 knn+logit 混合（knn_ratio 0.5→伪标后 0.8），`new_individual` 阈值设为"首预测为新个体的比例 = 0.165"；**两轮伪标签：0.88589/0.85959 → 0.89343/0.87062 → 0.89680/0.87579（pub/priv）**；最终 ~50 模型集成；赛后验证**只用两队的各 1 个最佳模型（0.89385/0.87336）也仍可夺冠** | 1st |
| 3rd（319896） | YOLOv5 显著鲸体检测器**迭代自标**（先标 5000 张 → 训练 → 全量预测 → 修正 box<0.4 或 box 数≠1 → 重训）；识别：tf_effnet_b7/b6 @768、NFNet-l2 @1024；BNNeck + ArcFace(s=30,m=0.3)/AdaFace；增强偏**纹理**（Sharpen/ToGray/CLAHE）+ mixup；逐技巧消融（new_id / not_new_id / CV 三列） | 3rd |
| 19th（320298，71 票） | **无伪标签单模型 LB 0.860**：6 个裁剪数据集（两家 fullbody + 两家 fin + detic + yolo）混合训练（20 epoch，每图见 120 次），双 ArcFace 头（species + individual，m=0.19/s=19）；推理时**逐数据集出 6 个嵌入 → 贝叶斯优化权重 → KNN**（图 1）；8 折 ×12 模型投票集成 → LB 0.868；赛后给 2 个模型加伪标签：**+0.009 pub / +0.016 priv** | 19th |
| 数据侧（社区） | 物种列修复（305574，176 票）、背鳍数据集（310153/309214）、降分辨率数据集（304686）、LB probing 与切分讨论（304633/308991 等）；两篇 CV 技巧帖合计 275 票 | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 19th |
| --- | --- | --- | --- |
| 裁剪 | 5 来源 bbox 按比例混合 | 自训 YOLOv5 迭代精修 | 6 个现成裁剪数据集 |
| 主干 | EffNet b5–b7 / v2m–l（1024） | EffNet b6/b7 + NFNet-l2 | EffNet b5–b7 / v2l–xl / ConvNeXt-L |
| 头部 | sub-center ArcFace + 动态 margin；species 二头 | BNNeck + ArcFace/AdaFace；species 二头 | 双 ArcFace（m=0.19, s=19） |
| 检索 | knn+logit 混合（0.5→0.8） | KNN | 6 嵌入贝叶斯加权 + KNN |
| 伪标签 | **两轮，+0.006~0.011** | 未强调 | 无（赛后验证 +0.009/+0.016） |
| 成绩 | 0.89343/0.87062 → 0.89680/0.87579 | 3rd | 0.859（单模）→ 0.868（集成） |

### 共识 / 分歧 / 裁决
**共识一：裁剪来源的多样性本身就是性能（三家）**
1st 用 5 种 bbox 按比例混合（含 15% backfin 专治"只露背鳍"的图）；3rd 自训检测器迭代精修；19th 直接混合 6 个公开裁剪数据集并逐数据集出嵌入。**裁决**：细粒度开集识别里，"主体如何被框出来"对分数的影响大于主干选择——多来源裁剪既是数据增强也是分布覆盖。置信度：高。

**共识二：ArcFace 系头部 + 检索式评估是主线（三家）**
1st 用 sub-center ArcFace（k=2）+ 动态 margin（并指出上届"翻转当新类"在本届不适用，因为拍摄角度多变）；3rd 用 BNNeck+ArcFace/AdaFace；19th 用双 ArcFace 头（物种 + 个体）。**裁决**：MAP@5 的检索式指标与度量学习头部天然匹配；物种辅助头是稳定的小增益。置信度：高。

**共识三：伪标签是最大单点增量（1st/19th 独立验证）**
1st 两轮伪标签把 pub/priv 从 0.88589/0.85959 提到 0.89680/0.87579，且赛后"2 模型也能夺冠"；19th 赛后给 2/12 模型加伪标签即 +0.016 priv，自评"足以进金牌区"。**裁决**：极端长尾 + 开集场景里，伪标签是性价比最高的动作（远超换主干/调参）。置信度：高。

**分歧一：knn vs logit 的权重**
1st 观察到 knn 在 CV 上更好但公榜优势小（长尾导致 knn 偏向样本多的类），于是固定 knn_ratio=0.5，伪标后提到 0.8；19th 纯 KNN（多嵌入加权）。**裁决**：knn/logit 差异来自"训练分布 vs 测试分布"的偏置；混合比例应随伪标签/分布校正调整。置信度：中高。

**分歧二：开集阈值怎么定**
1st 用"首预测为 `new_individual` 的比例 = 0.165"反推阈值（基于验证/试提交）；19th 在 CV 上调 `new_individual` 阈值。**裁决**：开集阈值应按"目标新个体比例"校准，而不是纯分数阈值。置信度：中高。

**事件：社区数据整理的价值**
物种列问题修复（176 票）、背鳍/全身裁剪数据集、降分辨率数据集——1st/19th 都直接使用了社区数据集。**裁决**：数据整理帖是细粒度赛的"隐形基建"，善用可省数周。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的伪标签分数链与"两模型也能夺冠" | 自述 + 完整数字 + 公开代码 | 高 |
| 3rd 的检测器迭代与技巧消融表 | 自述 + 表 + 代码 | 中高 |
| 19th 的 6 嵌入贝叶斯加权与伪标签复验 | 自述 + 图 + 赛后更新 | 高 |
| bbox 混合比例（0.60/0.15/0.15/0.05/0.05） | 单队自述（1st） | 中（比例可复现，收益未给单变量消融） |
| 社区数据集质量 | 多队使用 + 票数 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd 与 4th–18th 的 write-up 未入库；"9 CV Tricks"（168 票）与"7 More CV Tricks"（117 票）两帖未细读；
- "Miracle of Coincidence"（136 票）与 LB probing（304633）涉及榜面异常，未细读；
- 1st 的 Optuna 动态 margin 具体分布未公布（只有调参流程）；
- 3rd 的 180px 宽流程图无法作为证据（本场归档图仅 2 张可用）。

### 图证（KStarter 仓库内路径）
- ../../intel/happy-whale-and-dolphin/bodies/320298_img/04.png — 19th 的六数据集嵌入加权
- ../../intel/happy-whale-and-dolphin/bodies/320298_img/02.png — 19th 的六种裁剪示例

### 出处
- 1st（198 票）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/320192
- 3rd（319896）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/319896
- 19th（71 票）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/320298
- 物种列修复（176 票）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/305574
- 背鳍数据集（142 票）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/310153
- 9 CV 技巧（168 票）：https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/310105

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/320502
- rank 3｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/319789
- rank 3｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/320191
- rank 4｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/320040
- rank 6｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/319829
- rank 7｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/320026
- rank 8｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/319868
- rank 8｜description：https://www.kaggle.com/c/happy-whale-and-dolphin/discussion/319894

---

## herbarium-2022-fgvc9 — Herbarium 2022（FGVC9 植物标本细粒度分类）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 F-Score (Macro) ｜ 队伍 134 ｜ 截止 2022-05-30 ｜ Tier B ｜ 标签 cv,agriculture
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/herbarium-2022-fgvc9.md
> 材料基础：`digests/herbarium-2022-fgvc9.md`（6 篇正文：上手 notebook 合集 323794 / 可解释细粒度与 machine teaching 308406 / 1st 329299 / 往届 notebook 307745 / JSON→Pandas 307804 / 往届获奖 307624；39 条主题索引）+ 0 张归档图

### 一句话重述
**83.9 万张**植物标本图的超细粒度分类（Macro F1，长尾极重）。1st 方案把增益拆得非常干净：**多级分类损失（family/genus/species）→ 更高学习率 → 5-crop 多尺度 → subcenter-ArcFace 动态 margin → 额外 CE 头 → Swin 增强 → 384 分辨率 → 冻结层渐进解冻 → SwinV2**，单模 private 从 0.78442 一路推到 **0.86282**，再用 8 个骨干按公榜分数融合到 **0.87662**。值得注意的负结果：**class-aware sampling 与 data cleaning 都没用**——长尾问题靠损失/度量学习解决，而不是重采样。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模 | **839,772 张**训练图；134 队；Macro F-Score；长尾分布；CVPR FGVC9 workshop | 307615 / 索引 |
| 1st 单模消融（private） | Swin-B224 基线 **0.78442** → +多级 CE（family/genus/species）**0.79544** → LR 2e-4→5e-4 **0.80501** → +5crop **0.80981** → subcenter-ArcFace 动态 margin **0.82267** → +额外 CE 头 **0.82929** → +Swin 式增强 **0.83554** → SwinB384 **0.85245** → +5crop（384）**0.85654** → 冻结层 100→0 **0.86055** → square resize **0.86201** → SwinV2 **0.86282** | 329299 |
| 骨干对比（private） | swinv2-B 0.86282 > swin-B 0.86055 > convnext-B 0.85956 > swin-L 0.85607 > cswin-L 0.8501 > deit-iii B 0.8495 > efficient-B6 0.84321 > resnest-101 0.83838 | 329299 |
| 融合 | 用**公榜分数**做权重：3 模型 0.8679 → 5 模型 0.87185 → 8 模型 **0.87662**（private） | 329299 |
| 训练设置 | batch 512（大模型 256）、100 epoch、torch.amp；ImageNet22k 预训练；先冻结部分层放大 batch 再全参训练；后处理 +0.001 | 329299 |
| 无效项 | **class-aware sampling、data cleaning 均无效**；另有帖子报告图像重复（数据泄漏）问题 | 329299 / 323906 |
| 社区设施 | 往届 notebook 合集 38 票；JSON→Pandas 数据框 18 票；往届获奖 18 票；可解释细粒度 + machine teaching 综述 16 票 | 307745 / 307804 / 307624 / 308406 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st（损失/分辨率/融合） | 社区起步线 |
| --- | --- | --- |
| 骨干 | SwinV2-B 主 + 8 骨干融合 | ResNet50 / EfficientNet / TresNet / Flax-Jax KFold |
| 损失 | 多级 CE + subcenter-ArcFace（动态 margin）+ CE 头 | 单 CE |
| 分辨率 | 224 → 384（+5crop、square resize） | 224 |
| 长尾 | 损失与度量学习 | WeightedRandomSampler（讨论） |
| 融合 | 按公榜分数加权 | 单模/简单平均 |

### 共识 / 分歧 / 裁决
**共识一：长尾细粒度分类用"度量损失 + 多级监督"而非重采样（329299；置信度中高）**
subcenter-ArcFace 动态 margin 一步 +0.0172（private），多级 CE +0.011；class-aware sampling 无效。**裁决**：先上 ArcFace/子中心等度量损失与层级标签监督，再把重采样作为备选而非常规动作。置信度：中高（单一冠军自述，但消融链完整）。

**共识二：分辨率与多尺度测试是稳定的第二杠杆（329299；置信度中高）**
224→384 单项 +0.03；两次 5crop 各 +0.005–0.007。**裁决**：细粒度植物/标本数据在显存允许时直接冲 384+，并用多尺度 crop 做 TTA。置信度：中高。

**事件一：多骨干融合按公榜加权有效但过拟合公榜（329299；置信度中）**
8 模型融合 private 0.87662（+1.4），但权重来自公榜分数。**裁决**：融合权重用 OOF/公榜各做一版对比；公榜加权需要留出私榜验证空间，别把权重搜到公榜最优。置信度：中。

**事件二：数据重复/泄漏是这类大型标本库的隐性风险（323906；置信度中低）**
有帖报告 image duplicates，直接影响 CV 可信度。**裁决**：先做近重复检测（embedding/pHash）与分组 CV；至少确认 val/test 无重复泄漏。置信度：中低（单帖，未见官方结论）。

**事件三：领域侧关注"人机协作与可解释"（308406 / 307851 / 308258；置信度中）**
FGVC workshop 的主题包含 human-in-the-loop、machine teaching 与可解释模型；社区给了系统综述。**裁决**：评审制/workshop 赛道把"可解释性/人机协作"写进叙事是加分项，但本场实际排名仍由分类精度主导。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的逐项消融与骨干/融合表 | 自述 + 三张表（329299） | 高（本场最可复算的收益分解） |
| 839,772 张训练图 | 社区统计帖（307615） | 中高 |
| 无效尝试（重采样/清洗） | 1st 自述 | 中 |
| 数据重复/泄漏 | 个案帖（323906） | 低—中 |
| 可解释/machine teaching 主题 | 文献综述（308406） | 中高（文献可查） |
| 往届获奖与 notebook | 社区合集（307745 / 307624） | 中高（链接可查） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 除 1st 外的前排方案未归档（2nd/3rd 无正文）；
- 数据重复问题的规模与官方处理未归档；
- 融合权重按公榜搜索的过拟合风险未量化；
- Competitive wrap-up（329802）没有正文；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- 1st 方案（5 票 / 1 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/329299
- 上手 notebook 合集（15 票 / 7 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/323794
- 往届 notebook（38 票 / 18 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/307745
- 往届获奖方案（18 票 / 9 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/307624
- JSON→Pandas（18 票 / 8 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/307804
- 可解释细粒度与 machine teaching（16 票 / 2 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/308406
- 训练图规模（11 票 / 17 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/307615
- 数据重复/泄漏（0 票 / 7 评论）：https://www.kaggle.com/competitions/herbarium-2022-fgvc9/discussion/323906

---

## hotel-id-to-combat-human-trafficking-2022-fgvc9 — Hotel-ID to Combat Human Trafficking 2022（FGVC9）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 MAP@{K} ｜ 队伍 82 ｜ 截止 2022-05-30 ｜ Tier B ｜ 标签 cv,ranking
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/hotel-id-to-combat-human-trafficking-2022-fgvc9.md
> 材料基础：`digests/hotel-id-to-combat-human-trafficking-2022-fgvc9.md`（6 篇正文：1st 328281 / 公开私榜 3rd 328237 / 往届资源 313362 / 2nd 328345 / 奖牌争议 314885 / 往届实效提问 316799；29 条主题索引）+ 0 张归档图

### 一句话重述
用房间/酒店照片做**同一酒店检索**（反人口贩卖取证），FGVC9/CVPR workshop 赛。核心难点是测试/查询图有**大面积遮挡掩码**，而训练图没有；三条获奖路线分别用三种方式处理这个域差：1st 造了 **BlendFlip** 遮挡增强（+0.03–0.04 mAP）+ 5 模型嵌入集成；2nd 用**统计掩码生成 + 50K 外部数据 + 子中心 ArcFace**；3rd 干脆改用 **logits 分类**绕开检索。赛事另一条主线是社会公益赛的关注度问题：无奖牌/奖金，参赛仅 82 队，"往届成果有没有真的用于反贩卖"被公开追问但无归档答复。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与机制 | **82 队**；代码赛（MAP@{K}）；无奖牌/积分/奖金/周边；获奖者去 CVPR workshop 展示 | 314885 |
| 1st（328281） | 5 模型集成（1024×1024 与 384×384 两种尺寸），**ArcFace** 训练，嵌入 1536D → 拼接后 **PCA 到 3072D（保留 99% 方差）** → KNN；无后处理/重排；**BlendFlip 贡献约 0.03–0.04 mAP**（作者称 CVPR 论文将补消融）；BlendFlip = 取遮挡区上下/左右最大可用邻域翻转填充，再 50/50 混合 | 328281 |
| 2nd（328345） | 50K+FGVC9；按 **md5 去重**（同 md5 不同类别删除）后保留 **45,769 个类别**；方向模型把图旋正；先全量 10–20 epoch，再对 FGVC9 的 **3116 类微调 40 epoch（+0.03）**；**sub-center ArcFace（k=3，动态 margin）**；swin-base-384 私榜 0.688、swin-large-384 0.692、eca_nfnet_l1 0.688，**集成私榜 0.717 / 公榜 0.732**；FGVC8 伪标签失败 | 328345 |
| 3rd（328237） | 多骨干（Swin、ConvNeXt、ResNet200D、EfficientNet + DOLG，尺寸 384–1024）；用 FGVC8 外部数据 + KNN 伪标签 + 均值聚合；**logits 优于 KNN**；推理约 2 小时；最佳单模 ConvNeXt XLarge 512 私榜 0.672 | 328237 |
| 数据/平台坑 | 重复图（324699）；外部数据规则问询（317922）；掩码用法（313547，12 评论）；notebook 里测试图只挂出 `abc.jpg`（322383）；提交表头要用 `image_id` 而非 `image`（324704）；Hotel-50K 来源（319203） | 索引 |
| 社会影响力追问 | 26 票"这么严肃的议题为什么没有奖牌/积分/奖金"；16 票"往届方法有没有被生产化用于反贩卖"；往届资源汇编 16 票 | 314885 / 316799 / 313362 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st（检索 + 新增强） | 2nd（分类 + 度量损失） | 3rd（分类 + 外部数据） |
| --- | --- | --- | --- |
| 遮挡处理 | **BlendFlip 增强**（训练 50% 概率，测试全量） | 统计测试掩码分布生成训练掩码 | 用 logits 规避训练/测试掩码不一致 |
| 训练数据 | 竞赛数据 | 50K + 去重 + 方向校正 | 竞赛 + FGVC8 伪标签 |
| 损失/嵌入 | ArcFace，1536D | sub-center ArcFace（k=3，动态 margin） | — |
| 推理 | 拼接嵌入 → PCA → KNN | logits | logits |
| 私榜 | — | **0.717（集成）** | 0.672（最佳单模） |

### 共识 / 分歧 / 裁决
**共识一：遮挡/掩码域差是本场第一问题（328281 / 328345 / 328237；置信度高）**
三队都用不同方式正视"训练无掩码、测试有掩码"：BlendFlip、统计掩码、logits 规避。**裁决**：检索类比赛先量化 train/test 的遮挡差；增强要与评测分布对齐（测试掩码统计），不要只做通用增强。置信度：高。

**分歧：检索（KNN）vs 分类（logits）（328281 vs 328237 / 328345；置信度中高）**
1st 用 PCA 嵌入 + KNN 拿冠军（BlendFlip 收益可量化）；2nd/3rd 都报告 logits ≥ 检索，更省事。**裁决**：两条路都要在本地建"带掩码"的验证集对比；若遮挡占主导，嵌入检索更稳；若类别多且掩码可控，logits 更快。置信度：中高。

**事件一：外部数据与伪标签有效但需验证（328237 / 328345；置信度中）**
3rd 用 FGVC8 + 伪标签（KNN 匹配、阈值 <0.5 的样本入训、均值聚合）取得前排；2nd 的 FGVC8 伪标签失败、Hotel50K 也没用上。**裁决**：外部数据先做类别映射与去重审计，再小规模对照 CV；失败案例说明"同源数据"假设要验证。置信度：中。

**事件二：数据清洗（去重/方向/掩码统计）直接换分（328345；置信度中高）**
2nd 的 md5 去重（同图不同类别的冲突删除）、方向模型旋正、3116 类微调 +0.03 都是可复现的工程收益。**裁决**：先做重复图与冲突标签审计，再做方向/掩码分布对齐。置信度：中高。

**事件三：社会公益赛的关注度与影响力缺口（314885 / 316799；置信度中）**
无奖牌与奖金导致参赛规模小（82 队），社区直接质疑"往届方法有没有被生产化"，归档无证据回答。**裁决**：参与此类比赛可积累检索/遮挡方法，但不要假设评审或传播机制完善；若关心影响力，把产出写成可复用工具而不是只交榜。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st BlendFlip 与集成细节 | 1st 自述 + 4 张示意图（328281） | 中高（待 CVPR 消融复核） |
| 2nd 分数表与微调收益 | 2nd 自述 + 表格（328345） | 中高 |
| 3rd 外数据/伪标签流程 | 3rd 自述 + 表格（328237） | 中高 |
| 无奖牌与参赛规模 | 官方赛制 + 讨论帖（314885） | 高 |
| 生产化影响力 | 提问帖（316799） | 低（无答复） |

### 悬案与失败学
**事件三：社会公益赛的关注度与影响力缺口（314885 / 316799；置信度中）**
无奖牌与奖金导致参赛规模小（82 队），社区直接质疑"往届方法有没有被生产化"，归档无证据回答。**裁决**：参与此类比赛可积累检索/遮挡方法，但不要假设评审或传播机制完善；若关心影响力，把产出写成可复用工具而不是只交榜。置信度：中。

**5. 悬案与缺口（登记）**
- 1st 的 CVPR 论文与完整消融未归档（BlendFlip 增益为自述）；
- 竞赛私有测试集，完整复现不可能；各队验证口径未统一；
- 往届成果是否被反贩卖实务采用：无归档证据（316799）；
- 外部数据（FGVC8/Hotel50K）许可与规则细节未归档；
- **图证缺口**：本场 0 张归档图（目录为空），已登记。

### 出处
- 1st：BlendFlip + 5 模型集成（30 票 / 8 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328281
- 2nd 方案（11 票 / 0 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328345
- 公开/私榜 3rd（16 票 / 8 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/328237
- 奖牌/奖金争议（26 票 / 8 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/314885
- 往届实效提问（16 票 / 3 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/316799
- 往届资源汇编（16 票 / 1 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/313362
- 掩码用法讨论（6 票 / 12 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/313547
- 重复图（5 票 / 3 评论）：https://www.kaggle.com/competitions/hotel-id-to-combat-human-trafficking-2022-fgvc9/discussion/324699

---

## hubmap-hacking-the-human-vasculature — HuBMAP Vasculature 深读：噪声标注利用 × bbox-first × dilation 之谜

> 主题 cv ｜ 类别 Research ｜ 指标 OpenImagesObjDetectionSegmentationAP ｜ 队伍 1021 ｜ 截止 2023-07-31 ｜ Tier A ｜ 标签 cv,segmentation,detection
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/hubmap-hacking-the-human-vasculature.md
> 材料基础：`digests/hubmap-hacking-the-human-vasculature.md`（6 篇正文：3rd/1st/9th/7th + 上届冠军索引帖 + GM 心情帖；80 条讨论索引）+ 9 张图（428447×4 / 429060×1 / 430242×4）

### 一句话重述
题面是"肾活检 WSI 中检测并分割血管（blood_vessel / glomerulus / 其他）"，实际被考的是**三件与模型无关的事**：
1. **dataset2 是带噪数据**：比赛提供"干净小数据（dataset1，wsi1/2 全标注）+ 噪声大数据（dataset2，wsi3/4，标注不全且系统性偏小）"；如何利用 dataset2 是分水岭——3rd 用"多阶段预训练→微调"（+4–6% LB），1st 用"混合 batch + EMA"，9th 重标 dataset2 的 bbox，7th 用伪标签 + 膨胀标注。
2. **bbox 主导指标**：1st 明说"AP 主要靠 bbox，mask 影响次要"，并把精力集中在检测；9th 用 160 个检测结果 + 4 个分割模型的两阶段结构。mask 监督不仅不亏，还能反哺 bbox（1st 对照表 +0.006–0.010）。
3. **dilation 之谜**：公榜显示 mask 膨胀能涨分，但它的本质是补偿 dataset2 的标注尺度偏差——9th 用 dataset1 训练的重标器修正 dataset2 后，dilation 红利消失；7th 曾怀疑这是"对 LB 过拟合"；1st 靠最后一天运气保留了对照提交。
一句话：**这是一场"噪声标注利用 + 检测优先 + 后处理辨伪"的比赛**——名次差距来自对 dataset2 的用法，而非 backbone。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 多阶段增益（3rd） | 验证 +2–3%；LB **+4–6%** | 3rd |
| 3rd 单模型 | ViT-Adapter-L 公榜 0.600 / 私榜 0.589（全场最佳单模型）；CBNetV2 0.567；DetectoRS 0.573 / ResNet50 0.558 | 3rd |
| 3rd 后处理 | erode + 单次 dilate：CV/LB **+0.005** | 3rd |
| 1st mask 监督对照（bbox mAP） | 无 mask 0.424 → 仅随机旋转重算框 0.434 → mask 头 0.430（segm60 0.68）→ 两者 0.432（0.688） | 1st |
| 1st 验证划分差异 | random：bbox 0.47 / segm60 0.72；i-split：0.43 / 0.68 | 1st |
| 1st batch 混比 | 8 = 3 张 ds1 + 5 张 ds2 | 1st |
| 1st 单模型 | 单折无 TTA 私榜 0.565+（足够金牌） | 1st |
| 1st 集成 | 私榜 0.589 / 公榜 0.317（原文如此；公榜值异常低，疑为笔误，待核） | 1st |
| 9th 集成规模 | 10 检测模型 × 16 TTA = **160** 结果 WBF（校验：8 flip/rot × 2 尺度 = 16 ✓） | 9th |
| 9th 阈值 | 单模型 NMS IoU 0.6；WBF IoU 0.7；分割二值化 0.5 | 9th |
| 9th ds2 重标条件 | IoU > 0.4 且 FP/(TP+FP) > 0.1；重标后 bbox 变大、数量不变 | 9th |
| 9th 双提交 | 带 3% dilation：0.580/0.549；不带：0.572/0.560 | 9th |
| 7th dilation 差距 | 首版有/无差 **0.1** → 伪标签+膨胀 ds2 后差 **0.02**（双榜带 dilation 仍更好） | 7th |
| EMA 动量对照 | 图 1：momentum 1.0（无 EMA）波动 0.36–0.42；0.001 快升后衰减；0.0005 峰值 ~0.425；0.00025 慢升峰值 ~0.43 | 1st（图 1） |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd Nischay | 7th | 9th |
| --- | --- | --- | --- | --- |
| 主模型 | RTMDet-x（bbox 优先） | 2×ViT-Adapter-L + CBNetV2 + DetectoRS-ResNeXt101 + ResNet50（MMdet） | Mask R-CNN（Swin backbone + HTC RoI） | 检测：YOLOv5x6/v7x/v8l/v8x；分割：EffB1/B2-Unet |
| dataset2 用法 | 混合 batch（3 张 ds1 + 5 张 ds2） | **两阶段**：ds2 预训练（~10 epoch，LR 0.02+，轻增广）→ ds1 微调（15–25 epoch，低 LR 至 1e-7，重增广、高分辨率） | 先 ds1 训 5 折 → 给 ds2/ds3 打伪标签 → 用 ds1+ds2+ds3 重训（ds2 同时保留原膨胀标注与伪标签） | 用 ds1 训练检测器**重标 ds2 的 bbox**（IoU>0.4、FP 比>0.1）后再用 |
| 验证策略 | i-split（按 location 'i' 划分，0.43/0.68） | 折内 ds1 | 5 折 | 2 折按 wsi 交换（wsi1↔wsi2） |
| 增广/TTA | 强几何增广（旋转 ±180、scale 0.1–2.0）；无 TTA | 轻/重两套（stage1/stage2）；flip TTA | resize 1024/1536 + hvflip | 16 TTA = 8 组合（h/v flip、rot90）× 2 尺度 |
| 集成 | WBF：3×RTMDet + YOLOX-x + Mask R-CNN（bbox）；mask 用 Mask R-CNN 头 1440 | WBF（TTA 用 NMS）；5 架构异构 | RPN + RoI head 双层集成 | WBF：10 模型 × 16 TTA = **160 检测结果**（NMS 0.6 / WBF 0.7）；分割 4 模型平均 |
| 分割来源 | Mask R-CNN 头（bbox 统一） | 各模型 mask head（loss ×2/×4） | HTC mask 头 | 检测框 + 4ch（RGB+框 mask）输入 UNet，**不用检测结果当 mask 框** |
| 后处理 | 无 dilation（另一提交带） | erode → dilate（+0.005） | dilation、去小 mask、去含 glomerulus 的 mask | 3% bbox dilation（+0.005；另一提交不带） |
| 报告成绩 | 单模型私榜 0.565+；集成私榜 0.589（公榜 0.317，原文如此） | 最佳单模型公榜 0.600 / 私榜 0.589；多阶段 +4–6% LB | 有/无 dilation 差距 0.1 → 0.02 | 带 dilation 0.580/0.549；不带 0.572/0.560 |
| 失败清单 | — | 伪标签（ds3）无增益 | test 伪标签、Mendeley 外部数据、YOLOv8、Puzzle 提交 | ds3 半监督无效 |

### 共识 / 分歧 / 裁决
**共识一：dataset2 是"噪声大数据"，必须换一种用法（4/4）**
3rd：先预训练再微调，把 ds2 当弱监督表示来源（+4–6% LB）；
1st：batch 内 3:5 混合，配 EMA 稳定训练；
9th：不直接用 ds2 标注，先用 ds1 模型重标 bbox；
7th：用伪标签替代/补充 ds2 的原始标注。

**裁决**：dataset2 的价值在"数据量与尺度先验"，其标注不能与 ds1 等价对待；三族有效解——**阶段性使用（预训练/微调分离）、修正后使用（重标）、替代性使用（伪标签）**。直接把 ds1+ds2 混在一起监督训练会引入标注尺度/完整性偏差。置信度：高（4 队独立 + 数字）。

**共识二：bbox 决定分数，mask 是次要项且能反哺 bbox（1st 明说，9th 结构佐证）**
1st："AP 主要靠 bbox；mask 精度影响小"——因此集中优化 bbox，mask 交给 Mask R-CNN 头；其对照表显示 mask 监督让 bbox mAP 从 0.424 → 0.430–0.434。
9th：检测用 160 个结果的大集成，分割只 4 个模型、TTA 都不用（运行时约束）。
3rd：HTC 系模型给 mask head loss ×2/×4 权重。

**裁决**：实例分割 AP 的资源分配顺序 = bbox > mask；mask 监督作为 bbox 的正则化项有效（形状边界迫使特征更锐利）。置信度：中高（1st 数字 + 9th 结构 + 3rd 权重）。

**共识三：WBF 集成 + 异构模型是标准操作（4/4）**
3rd：NMS 用于 TTA、WBF 用于集成（分工明确）；CNN + Transformer 混合增加多样性。
9th：160 结果 WBF（NMS 0.6 / WBF 0.7）。
1st：5 模型 WBF（3×RTMDet + YOLOX + Mask R-CNN）。
7th：RPN + RoI head 双层集成（引 Sartorius 方案）。

**裁决**：分割/检测赛的最后 1–2 分来自集成；WBF 比 NMS 更适合跨模型融合，异构比同构有效。置信度：高。

**分歧一：dilation 到底要不要用（本场核心张力）**
支持：公榜普遍显示 mask/bbox 膨胀涨分（3rd erode+dilate +0.005；9th 3% bbox dilation +0.005；7th 首版 +0.1）。
反对/修正：7th 发现 ds1-only 模型 dilation 有害 → 怀疑其来自 ds2 噪声、是 LB 过拟合；9th 重标 ds2 后"dilation 红利几乎消失、不用 dilation 也过 0.5"。
1st：直到最后一天才发现 dilation，最终保留有/无两个提交，"纯属运气"。

**裁决**：dilation 的增益不是模型能力，而是**标注尺度偏差的补偿**——它对"训练含 ds2"的模型有效、对 ds1-only 模型有害；修正 ds2 标注后增益消失（9th 的因果闭环）。纪律结论：对这类"后处理试纸"，必须保留一个不施加该后处理的对照提交（1st 的明示建议）；否则公榜红利会在私榜反噬。置信度：中高（3 队联合证据 + 机制一致）。

**分歧二：验证划分——要难而真，不要易而虚**
1st：i-split（按 location 'i' 划分）比随机划分难——bbox mAP 0.43 vs 0.47、segm 0.68 vs 0.72，但更接近测试分布；公开承认"验证分数更低"仍坚持使用。
9th：2 折按 wsi 交换（train wsi1 + updated-ds2 → val wsi2），直接模拟"新 WSI 泛化"。

**裁决**：本场测试来自未见 WSI，验证必须按 WSI/位置分组；随机划分的高分是虚高（与 L6/T3 一致）。置信度：高。

**分歧三：伪标签/半监督（dataset3）**
3rd：用 ds3 伪标签训练部分模型，**LB 无提升**；
9th：ds3 半监督"does not work"；
7th：用了 ds2/ds3 伪标签，但收益未量化，主要用于缩小 dilation 差距。

**裁决**：在本场，伪标签不是主杠杆；当核心矛盾是"标注尺度偏差"时，重标/多阶段比伪标签更直接（对照 T6：预训练式稳、混训险）。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 多阶段 +4–6% LB | 自述 + 流程图 + 开源代码 | 中高 |
| dataset2 标注偏小 | 三队独立行为证据（7th 怀疑/9th 重标/3rd 只在 ds1 上微调） | 中高（无官方声明） |
| mask 监督提升 bbox | 1st 对照表（0.424→0.434） | 中（单队、数字小） |
| i-split vs random 差异 | 1st 数字 | 中 |
| 9th 重标后 dilation 红利消失 | 9th 自述 + 流程图 + 条件定义 | 中高 |
| 公榜 dilation 增益 | 9th/7th/1st 的公榜数字 | 中低（公榜） |
| EMA 曲线 | 图 1 可视化 + 1st 自述 | 中（图为单次实验） |
| 伪标签无增益 | 3rd/9th 自述 | 中 |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **"Dilation increases the score, who understands why?"（416901，48 票）未收录**：本场核心谜题的社区讨论正文缺失；9th 的重标实验已给出机制，但官方/社区的最终解释未存档。
2. 2nd(429240)、4th(428994) 方案未收录——四强中两强的结构缺失，集成配方的全景不完整。
3. 428392 "public 9th / private 295th"（32 票）未收录——公榜过拟合的极端案例，与 dilation 之谜直接相关。
4. 1st 的公榜 0.317 与私榜 0.589 的巨大反差（原文如此）无法解释，疑为笔误，待核。

**失败学（跨队合集）**

- 半监督/伪标签：ds3 伪标签无增益（3rd）；ds3 半监督失败（9th）；test 图伪标签（7th）。
- 外部数据：Mendeley 数据集无效（7th）。
- 模型选择：YOLOv8 在 7th 处失败；Puzzle 提交不可行（7th）。
- 数据用法：ds1-only + dilation 有害（7th/9th）——**先把"训练集构成"与"后处理方向"对齐，再谈模型**。

### 出处
- 3rd（Nischay，61 票）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/430242
- 1st（82 票）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/429060
- 7th（63 票）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/428295
- 9th（43 票）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/428447
- 上届冠军索引（44 票）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/412307
- GM 心情帖（219 票，指向 3rd）：https://www.kaggle.com/competitions/hubmap-hacking-the-human-vasculature/discussion/428296
- 缺口登记（未收录正文）：2nd(429240)、4th(428994)、419143、**dilation 讨论(416901)**、428392(public 9th/private 295th)、412316 等

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/429240
- rank 4｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428994
- rank 8｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/429352
- rank 10｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428301
- rank 12｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428319
- rank 19｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428327
- rank 30｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428372
- rank 46｜description：https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature/discussion/428644

---

## hubmap-organ-segmentation — HuBMAP + HPA - Organ Segmentation 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Dice ｜ 队伍 1174 ｜ 截止 2022-09-22 ｜ Tier B ｜ 标签 cv,segmentation,generative
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/hubmap-organ-segmentation.md
> 材料基础：`digests/hubmap-organ-segmentation.md`（4 篇正文：3rd 354683 / 4th 354851 / 2nd 354857 / 往届总结 433 行处等；80 条主题索引）+ 2 张图

### 一句话重述
在 5 个器官（肾/大肠/肺/前列腺/脾）的 H&E 病理切片上分割组织结构的实例。真正的考点是**域偏移（domain shift）**：测试用 HuBMAP 的 H&E 染色，训练大量来自 HPA 的 DAB 染色；host 明说"用不同协议准备的数据也能工作，是本届的核心挑战"。因此顶级方案围绕**染色归一化/直方图匹配 + 多分辨率重采样 + 器官专属建模**展开。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 3rd（354683） | 先剔除一批"疑似错标"的肺（后经 host 澄清是"肺泡的另一种切法"，仍因样本太少而丢弃，**之后用伪标签把它们加回**）；**统一重采样到 HuBMAP 目标分辨率**（原始尺度从 6.3µm/px 的前列腺到 0.2µm/px 的大肠），并按器官加额外降/升采样；同时保留一份 HPA 原始尺度数据；**CutMix 只在同一器官类内做**（p=0.5、α=1.0）；CNN 用 512 裁剪、SegFormer 用 1024（"SegFormer 在小裁剪上明显更差；CNN 加大裁剪反而伤 LB"）；非空掩码采样概率 0.5；重度几何/颜色/形变增强（"让模型知道颜色不重要"）；**直方图匹配**所有训练图到 H&E 的 GTEX/HuBMAP 参考；外部数据：GTEX（约 140 张，H&E）+ HPA（每器官 5.7–6.1 万张 DAB），全部用自集成打伪标签（集成在 HuBMAP 0.59、在 HPA+HuBMAP 0.81） | 354683 |
| 4th（354851，"Stain Normalization is all you need"） | 不用伪标签与外部数据；**双流模型**（肺单独一模型，其余器官另一模型——"其他器官学到的知识与肺冲突"）；编码器 coat-lite-medium / mit(SegFormer) / mpvit + daformer+unet 解码器；**训练时把 HPA 图随机用 Reinhard 或 Vahadane 归一化到那一张 HuBMAP 测试图**，让模型同时学两个特征空间；推理端也做染色归一化 | 354851 |
| 2nd（354857） | "重编码器 + 大分辨率"更有效：3 个 CNN（effnet_b7、convnext_large、tf_effnetv2_l）+ 1 个 Transformer（coat_lite_medium，**单模最好但 CNN 集成更强**）；3 种输入分辨率（768/1024/1472）× 5 折；**辅助输出 organ 与 pixel_size**（pixel_size 按重采样后输入计算、随增强变化）→ 更鲁棒；增强：随机裁剪/填充、缩放、旋转、翻转、颜色、模糊/噪声、饱和度/亮度/对比度、弹性形变；另用外部数据 | 354857 |
| 社区侧 | "**HPA 数据与 HuBMAP 数据会不会有问题？**"（78 票）、"一些洞察"（89 票）、"切片厚度如何影响染色强度的可视化"（56 票）、"外部数据源"（55 票）、"让病理模型对域偏移鲁棒（作者 Heather Couture）"（47 票）、"往届 HuBMAP 方案总结"（50 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 3rd | 4th | 2nd |
| --- | --- | --- | --- |
| 域偏移对策 | **按器官重采样 + 直方图匹配 + 外部数据伪标签** | **双流模型 + 训练时染色归一化（Reinhard/Vahadane）** | 多分辨率 + 器官/像素尺度辅助头 |
| 模型 | CNN（512）+ SegFormer（1024） | coat-lite / SegFormer / mpvit + daformer-unet | effnet_b7/convnext_l/effnetv2_l + coat_lite |
| 外部数据 | GTEX ~140 + HPA 5.7–6.1 万/器官（伪标签） | 无 | 有 |
| 关键细节 | CutMix 仅同器官；非空掩码采样 0.5 | 肺单独建模 | pixel_size 随增强变化 |

### 共识 / 分歧 / 裁决
**共识一：域偏移（HPA→HuBMAP）是本场主问题（3rd/4th + 社区高票帖）**
host 明确点题：4th 的标题直接是"染色归一化就是全部"；3rd 用直方图匹配 + 双尺度数据；社区 78 票帖专门质疑 HPA/HuBMAP 数据兼容性，56 票帖可视化切片厚度对染色的影响。**裁决**：病理赛先做"染色/协议审计"，把颜色空间对齐（归一化或强颜色增强）当作模型的一部分。置信度：高。

**共识二：多分辨率与像素尺度必须显式处理（3rd/2nd）**
3rd 按器官重采样到目标分辨率（尺度跨 30 倍）；2nd 用 3 档分辨率并在训练中跟踪 pixel_size 作为辅助目标。**裁决**：像素尺度差异大时，重采样到统一物理尺度 + 多分辨率训练/集成优于单一分辨率。置信度：高。

**共识三：肺（lung）是特殊子分布（3rd/4th）**
3rd 专门处理肺（丢弃再伪标加回）；4th 直接给肺单独一条流（"其他器官的知识会伤害肺"）；社区基准表也显示 lung 分项显著低于其他器官。**裁决**：当某器官/类别与其余数据的特征冲突时，**分组建模**（多流/多头）比强行共享主干更稳。置信度：高（多队独立 + 分项分数）。

**分歧一：外部数据/伪标签的收益**
3rd 用 GTEX+HPA 数万张伪标签（并在 HPA 上 0.81），4th 完全不用仍拿第 4。**裁决**：外部数据不是必需；当主问题是"染色域偏移"时，归一化+增强可能比堆数据更划算。置信度：中高。

**事件：重编码器与大分辨率的收益（2nd + 基准表）**
2nd 结论"重编码器 + 更大分辨率更好"；社区基准表（图 1）显示 `convnext_l`/`swin` 等在 lung 上明显优于 resnet101d。**裁决**：病理分割里主干容量与分辨率是主要杠杆，但要注意"加大 CNN 裁剪伤 LB"（3rd）——训练裁剪尺度要与推理/域特性匹配。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 3rd 的完整管线（重采样/直方图匹配/同器官 CutMix/伪标签） | 自述 + 分数 | 高 |
| 4th 的染色归一化与双流 | 自述（标题结论强、细节完整） | 中高 |
| 2nd 的多分辨率与辅助头 | 自述 | 中高 |
| 社区基准表（各主干×器官×折） | 图（可复核） | 中高 |
| HPA/HuBMAP 兼容性担忧 | 高票讨论 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- **1st place（356201，48 票）的方案未入库**（本场材料缺口最大的一处）；"Some Insights"（89 票）与"Let's share CV"类帖未细读；
- 3rd 的伪标签集成权重与 HPA 数据规模（5.7 万/器官 vs 训练集）未给出精确收益；
- 4th 未报告"不做归一化"的对照，标题结论的强度来自经验；
- 归档 2 图均来自 332941（基准表），为图证。

### 图证（KStarter 仓库内路径）
- ../../intel/hubmap-organ-segmentation/bodies/332941_img/01.png — 各主干在 5 器官上的逐折基准

### 出处
- 3rd（70 票）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/354683
- 4th（50 票）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/354851
- 2nd（56 票）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/354857
- HPA/HuBMAP 数据质疑（78 票）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/332714
- 外部数据源（55 票）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/333886
- 1st（未入库，待补）：https://www.kaggle.com/competitions/hubmap-organ-segmentation/discussion/356201

### 外部题解（kaggle-solutions）
- rank 7｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/354859
- rank 11｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/354701
- rank 20｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/354590
- rank 25｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/354744
- rank 26｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/354671
- rank 27｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/355213
- rank 48｜description：https://www.kaggle.com/c/hubmap-organ-segmentation/discussion/355509

---

## image-matching-challenge-2022 — Image Matching Challenge 2022 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Image Matching Challenge pose mAA ｜ 队伍 642 ｜ 截止 2022-06-02 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/image-matching-challenge-2022.md
> 材料基础：`digests/image-matching-challenge-2022.md`（5 篇正文：1st 329131 / 2nd 329317 / 4th 328798 / 9th 328796 / 10th 328903 等；80 条主题索引）+ 15 张图

### 一句话重述
给定同一场景的多张照片，估计相机位姿（mAA）；每对图像要算基础矩阵 F。真正的考点是**"后处理与集成"而不是训练**：主办方明说目标是发现更好的后处理技术（9th 转述），前列队伍全部使用**预训练模型 + 多分辨率集成 + 关键点筛选/裁剪**，只有少数尝试微调 LoFTR。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（329131） | 两阶段：① 多分辨率匹配（LoFTR@840；SuperPoint+SuperGlue@840/1024/1280）→ 拼接关键点 → **DBSCAN 保留 80~90% 的匹配点簇 → 裁剪共视区（mkpt_crop）**；② 在裁剪图上重匹配（LoFTR@1280、DKM@840、SuperGlue@1024/1280/1536）→ 与阶段①关键点拼接 → RANSAC 求 F；全部预训练、无微调；mkpt_crop 同时**过滤外点 + 复用阶段①关键点**（"lean & efficient"）；Mask2Former 分割裁剪更差（无法判断"两图共视"）；对小块共视区会被裁掉的缺陷，用原始图匹配点补充 | 329131 |
| 2nd（329317） | 自研 transformer 匹配器单模 **0.833/0.838（pub/priv）无 TTA**；与其他强匹配器集成后：+QuadTree 0.854/0.848；对比：LoFTR 单模 0.783/0.772、SuperGlue+8k SuperPoint 0.724/0.728；提出 transformer 匹配器的**归一化位置编码**；明确"不做 TTA/多分辨率/前后处理"也能靠单模强度进前列 | 329317 |
| 4th（328798） | 全员土木背景、零基础起步；纯预训练 + 多尺度集成（LoFTR 长边 1000/1200/1400；SuperGlue 1200/1600/2000/2800；DKM 按面积归一 346800）+ 关键点回缩放到原图 + MAGSAC；**因 SuperGlue 许可证不允许获奖，专门准备"去 SuperGlue"路线**（LoFTR+QuadTree+DKM 私榜 0.843），最终提交 0.852 | 328798 |
| 9th（328796） | "后处理为王"；从公开 notebook 起步；正确回缩关键点 + 简单集成/TTA → 0.833/0.824；**DKM 采样改造**（绝对置信度 >0.8、每窗口随机 200 点、800×600）→ 0.838/0.836；**把 MAGSAC 放到并行线程 + 预取数据**后能加更多 TTA + 置信度阈值（LoFTR 0.3/SG 0.4）+ 迭代 25 万 → 0.845/0.842；**SuperGlue 的正确 TTA 方式**（每张 TTA 只跑一次 SuperPoint，SuperGlue 做 N² 交叉配对，坐标在 SuperGlue 后回缩）→ 0.847/0.848；有一次私榜 0.851（相当于第 5）但未选 | 328796 |
| 事件 | "Sudden 30+ positions leaps on top of the LB"（43 票）质疑榜面跳变；LoFTR 微调帖（70 票）为少数训练路线；官方提供 LoFTR/DISK/DKM 示例 notebook 与学习材料 | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 4th | 9th |
| --- | --- | --- | --- | --- |
| 训练 | 无（全预训练） | 自研模型（未开源） | 无 | 无 |
| 多分辨率 | 是（7 个组合） | 否 | 是（三模型多尺度） | 是（TTA） |
| 关键点筛选 | **DBSCAN+共视区裁剪** | QuadTree | 多尺度拼接 | 置信度阈值 + DKM 采样 |
| 求解器 | RANSAC | — | MAGSAC | **MAGSAC 25 万次迭代** |
| 工程优化 | 复用阶段①关键点 | — | — | MAGSAC 并行线程 + 预取 |
| priv | 1st | 0.838（单模） | 0.852（提交） | 0.848 |

### 共识 / 分歧 / 裁决
**共识一：本赛考"后处理 + 集成"，预训练模型够用（1st/2nd/4th/9th）**
四队都不用微调；9th 转述主办方"目标是更好的后处理"；1st/4th 的全部增益来自匹配器组合、分辨率与筛选。**裁决**：特征匹配赛的 ROI 排序 = 集成 > 关键点筛选/裁剪 > 求解器调参 > 模型训练。置信度：高。

**共识二：多分辨率是"免费多样性"（1st/4th/9th）**
1st 用 7 个（模型×分辨率）组合并显式指出"不同分辨率得到不同匹配点 → 多样性"；4th 每模型 3–4 档尺度；9th 的 TTA 也以分辨率/翻转/旋转为主。**裁决**：同一预训练模型在不同输入尺度下的输出近似"不同模型"，是零成本的集成来源。置信度：高。

**共识三：关键点必须回缩放到原图坐标（9th 明确指为公共 bug）**
9th 指出"所有公开 notebook 都没把匹配点正确回缩放"，修好后集成/TTA 才能正确拼接。**裁决**：多尺度管线里坐标变换是最容易错的环节，值得写单元测试。置信度：高。

**分歧一：要不要裁剪/筛选关键点**
1st 用 mkpt_crop（DBSCAN 簇 + 共视区裁剪）拿第 1，并说"裁剪后重匹配"显著增益；2nd 的基线**不做任何前后处理**仍拿 0.838（其 QuadTree 版 0.854）；9th 只做置信度阈值与 DKM 采样。**裁决**：裁剪的收益取决于匹配器质量与场景类型——它同时是筛选器与"再匹配的聚焦器"，但对小共视区有风险（1st 自己也补了原始图匹配点）。置信度：中高。

**分歧二：单模强度 vs 大规模集成**
2nd 用单模 0.838（无 TTA）证明模型本身的强度；1st/4th/9th 靠集成与后处理。**裁决**：两条路都能到前列；若无法训新模型（本赛多数队伍），集成与工程是唯一路径。置信度：中高。

**事件：许可证影响选型（4th）**
SuperGlue 的许可证不允许获奖 → 4th 专门准备"去 SuperGlue"的提交路线。**裁决**：代码赛选型前先核对许可证（与"是否可获奖"绑定），并准备合规备选提交。置信度：中高（单队自述，但有官方规则背景）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的 mkpt_crop 框架与多分辨率组合 | 自述 + 框架图 | 高 |
| 9th 的分数链（0.833→0.848）与工程细节 | 自述 + 逐项数字 | 高 |
| 2nd 的单模 0.838 与各匹配器对照 | 自述 + 表 | 中高（自研模型未开源） |
| 4th 的许可证路线与 0.843/0.852 | 自述 + 公开 notebook | 中高 |
| 榜面跳变质疑 | 论坛帖 | 低/现象 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd/5th–8th/10th 的方案未细读；LoFTR 微调帖（70 票）与"Experiments with pretrained models"（51 票）未细读；
- 2nd 的自研匹配器细节因论文双盲未公开，无法复核；
- 1st 未给出逐项消融（mkpt_crop 单独贡献多少未量化）；
- 归档 15 图中 2 张（1st 的框架图与 mkpt_crop 示意）为关键证据，另有 9th/10th 的流程与可视化图。

### 图证（KStarter 仓库内路径）
- ../../intel/image-matching-challenge-2022/bodies/329131_img/01.png — 1st 的两阶段匹配框架

### 出处
- 1st（329131）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/329131
- 2nd（45 票）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/329317
- 4th（43 票）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/328798
- 9th（51 票）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/328796
- 基础矩阵科普（94 票）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/316975
- LoFTR 微调（70 票）：https://www.kaggle.com/competitions/image-matching-challenge-2022/discussion/320219

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/329540
- rank 6｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/328805
- rank 7｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/329015
- rank 10｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/328903
- rank 11｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/328887
- rank 14｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/329566
- rank 17｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/328803
- rank 18｜description：https://www.kaggle.com/c/image-matching-challenge-2022/discussion/328982

---

## image-matching-challenge-2023 — Image Matching Challenge 2023 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 imc2023 ｜ 队伍 494 ｜ 截止 2023-06-12 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/image-matching-challenge-2023.md
> 材料基础：`digests/image-matching-challenge-2023.md`（6 篇正文：1st 417407 / 2nd 416873 / 5th 416816 / 3rd、4th、6th 等节；80 条主题索引）+ 15 张图

### 一句话重述
从多视角照片重建相机位姿。2023 届的战场从"配对匹配质量"转向**SfM 系统本身**：1st 解决"检测器无关（detector-free）匹配器的**多视角不一致**"，2nd 与"**COLMAP 结果的随机性**"搏斗，5th 用 kNN 短名单 + 旋转纠正。**旋转图片**（如 cyprus 场景）是本届最大的公共坑。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（417407，ZJU/DFSfM） | 框架：**"稀疏+稠密匹配 → 置信度引导合并 → 粗 SfM → 迭代精化"**；多阶段匹配（NetVLAD 检索 → 四方向旋转检测 → 重叠区裁剪 + 尺度对齐 → 稀疏 SPSG 与 dense 匹配拼接）；**置信度引导合并**：对每张图聚合所有匹配点、做 NMS（窗口 5）压成局部最高置信点、超过阈值取 top-10k——把检测器无关匹配器的"成对依赖碎片化轨迹"变成一致的 2D 点；粗 SfM 用 COLMAP（**跳过几何验证**，因为匹配阶段已做 RANSAC；**注册图像 >40 后才启用 PBA 并行 BA**，避免 PCG 不精确解破坏初始化）；**迭代精化**：Transformer 多视角匹配器 → 几何 BA + 轨迹拓扑调整（补全/合并/过滤）；消融（私榜）：SPSG 0.482 → +LoFTR 0.526 → +精化 0.570 → **+DKMv3+精化 0.594** | 417407 |
| 2nd（416873，49 票） | 主题即"**战胜 COLMAP 的随机性**"；关键动作：① **穷举所有图像对**（放弃检索排序），匹配数 <100 的对丢弃；② SP/SG 无上限关键点（kpt 阈值 0.005、match 0.2、Sinkhorn 20 轮）+ 半精度 + 关键点/匹配缓存；③ TTA 多尺度 [1088,1280,1376] 拼接；④ **旋转检测**（RotNet 失败；采用另一方案后 cyprus 场景 0.02→0.55）；⑤ 显式选定初始重建图像（配对最多/匹配最多）；⑥ **重复跑 match_exhaustive 取"10 次出现 8 次"的稳定匹配**；⑦ **用不同阈值 [100,125,75,100] 多次从头重建，按注册图像数与 3D 点数选最优**（仅对 <40–45 张图的场景）→ 最后一天把 0.497/0.542 提到 0.506/**0.562** | 416873 |
| 5th（416816，44 票） | 匹配部分沿用 2022 冠军思路（DBSCAN 裁剪 + 多尺度集成），新增：① **kNN 短名单**——不用全局描述子的固定阈值，而是先跑轻量 SPSG（关键点数限 512）按内点数取 k 近邻，再"补全"保证每张图至少 k 个邻居；② **旋转纠正**（准备 4 个旋转版本、统一 840×840 批处理匹配，解决 cyprus）；③ 并行执行提速 | 416816 |
| 3rd/4th/6th | 3rd 主题是"显著降低随机性带来的波动"；4th 与 6th（AffNetHardNet8+AdaLALA）给出不同特征组合的对照 | 417191/416918/417045 |
| 社区 | "SfM 完全新手的材料"（75 票）、"奖牌贩子一直都在"（51 票，治理争议）、"CVPR2023 新论文"（42 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 5th |
| --- | --- | --- | --- |
| 图像对 | NetVLAD 检索 | **穷举全部对**（匹配数阈值 100） | **kNN 短名单（按内点数）+ 补全** |
| 匹配器 | SPSG + LoFTR/DKMv3 | SP/SG 多尺度 TTA | 轻量 SPSG（512 点）+ DBSCAN 裁剪多尺度 |
| 一致性处理 | **置信度引导合并（NMS+top10k）** | 重复匹配取 8/10 稳定者 | — |
| 重建 | COLMAP + PBA（>40 图启用） | 多次重建选最优（<45 图） | COLMAP |
| 精化 | **Transformer 轨迹精化 + 几何 BA + 拓扑调整** | — | — |
| 旋转 | 四方向旋转检测 | 旋转检测（cyprus 0.02→0.55） | 4 旋转批量匹配 |
| priv | 0.594（+DKMv3） | 0.562 | — |

### 共识 / 分歧 / 裁决
**共识一：旋转图片是本届公共坑，不处理直接毁场景（1st/2nd/5th）**
2nd 的 cyprus 场景从 0.02 跳到 0.55；5th 专门准备 4 个旋转版本；1st 把旋转检测写进多阶段匹配。**裁决**：IMC 系列（2022 起）中"去 EXIF 的旋转图"是必须显式处理的环节，四方向枚举是最稳做法。置信度：高。

**共识二：匹配器只是原料，SfM 系统决定成败（1st/2nd/5th）**
1st 的主贡献是粗到精的重建框架（+0.112 私榜，从 0.482→0.594）；2nd 的分数提升全来自对 COLMAP 流程的操控（稳定化+多次重建）；5th 也在管线上做短名单与并行。**裁决**：IMC 2023 之后，"换更强匹配器"的边际 < "把匹配变成一致轨迹并稳定重建"。置信度：高。

**共识三：随机性要正面治理（1st/2nd/3rd）**
2nd 用"重复匹配取众数 + 多阈值多次重建选优"；3rd 的主题即"显著降低波动"；1st 也用 NMS 合并降噪。**裁决**：SfM 管线的随机性（RANSAC/BA 初始化/初始图像选择）需要工程化对冲（固定初始图像、阈值扫描、重复实验取稳定子集）。置信度：高。

**分歧一：图像对穷举 vs 检索**
2nd 直接穷举（并明确"删掉相似图检索模块"）在 494 队规模与每场景 ≤250 图的设定下可行且更稳；1st 仍用 NetVLAD（并说"检索方法差别不大"）；5th 用 kNN 短名单。**裁决**：图像数少时穷举最稳；图像多时用"轻量匹配器 + 内点 kNN"做短名单比全局描述子阈值更鲁棒。置信度：中高。

**事件：奖牌贩卖争议（51 票帖）**
社区帖讨论"奖牌贩子一直都在"。**裁决**：结算类竞赛需要治理机制；登记为现象，不进入方法论。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的框架图与消融（0.482→0.594） | 自述 + 论文级图 + 消融表 | 高 |
| 2nd 的随机性治理细节（8/10 稳定匹配、多阈值多重建） | 自述 + 架构图 + 分数 | 高 |
| 5th 的 kNN 短名单与旋转纠正 | 自述 + 图 | 中高 |
| cyprus 旋转修复 0.02→0.55 | 2nd/5th 独立佐证 | 高 |
| 奖牌贩卖争议 | 论坛帖 | 低/现象 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd/4th/6th/9th/39th 的方案未细读（digest 有正文）；"SfM 新手材料"（75 票）未细读；
- 1st 的迭代精化训练细节（MegaDepth 预训练 + 具体损失）未展开；
- 2nd 的多阈值重建只在 <45 图场景使用，大场景的替代方案未给；
- 归档 15 图：1st 的管线总图（图 1）与 2nd 的架构图为核心图证。

### 图证（KStarter 仓库内路径）
- ../../intel/image-matching-challenge-2023/bodies/417407_img/01.png — 1st 的粗到精 SfM 框架

### 出处
- 1st（417407）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/417407
- 2nd（49 票）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/416873
- 5th（44 票）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/416816
- 3rd（29 票）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/417191
- 6th（29 票）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/417045
- SfM 学习材料（75 票）：https://www.kaggle.com/competitions/image-matching-challenge-2023/discussion/401497

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/416918
- rank 9｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/416842
- rank 12｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/420471
- rank 16｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/417002
- rank 30｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/417186
- rank 39｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/416847
- rank 42｜description：https://www.kaggle.com/c/image-matching-challenge-2023/discussion/416777

---

## image-matching-challenge-2024 — Image Matching Challenge 2024 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 mAA-on-camera-centers-with-registration ｜ 队伍 929 ｜ 截止 2024-06-03 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/image-matching-challenge-2024.md
> 材料基础：`digests/image-matching-challenge-2024.md`（6 篇正文：1st 510084 / 2nd 510499 / 3rd 510338 / 4th 510611 / 5th 510603 / 8th 509902；80 条主题索引）+ 12 张图

### 一句话重述
IMC 2024 在 2022 版基础上引入了两个新难点：**透明/反光物体场景**与**被旋转的图片**。真正的新考点是**"分场景处理"**：常规场景继续卷特征匹配与 SfM 工程，透明场景则靠"图像排序 + 把相机摆到圆周上"这种几何先验直接拿分。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（510084） | 常规场景：ALIKED(n16)+LightGlue 高分辨率（1280/2048，原图+裁剪）匹配集成、**按匹配数过滤图像对**（单检测器 ≥30、全集成 ≥100）、**逐图 DBSCAN 裁剪**（与 IMC2022 的逐对裁剪不同）、每对图旋转 0/90/180/270 取匹配最多者、缓存关键点、多 GPU+混合精度、重复建图 + Horn 对齐合并多解；透明场景：**DIP 模块**——用光流/像素差/SSIM/匹配数构造距离矩阵 → TSP 排序 → 按圆周均匀布相机；**透明 trick 提升 LB +0.03**；最佳私榜是 ALIKED+LG 与 OmniGlue 的合并（未选）；密集匹配器（LoFTR/DKM/RoMa/OmniGlue/XFeat/SIFT 等）、检索 CNN（NetVLAD/DINO-SALAD）、PixSFM/DFSFM 精化、3D RANSAC、去模糊等均未奏效 | 510084 |
| 4th（510611） | ALIKED-n16+LightGlue；旋转图按 4 个角度缓存关键点；匹配阈值 100/125；透明场景：**用 DINOv2 Segmenter 的 VOC2012 第 5 类（"bottle"）当前景掩码**，在原尺度 1024×1024 网格内只检测前景关键点、且只在与对应网格间匹配；**穷举所有图像对**；**使用 images 文件夹里所有图像（不限于 submission.csv）**——消融表：baseline priv 0.149 → +透明 trick 0.184 → +穷举 0.186 → +全量图像 **0.197**（pub 0.136→0.171→0.176→0.194；val 0.26→0.32→0.34→0.43） | 510611 |
| 2nd（510499） | 常规：**MST 骨架 + 迭代加入冗余关联**的 SfM 优化；透明：同样的"排序+圆周布相机"思路；**自研全局描述子**（ALIKED 点特征 + DINO 块特征 → 一对一对应 → 聚类 + VLAD）：NetVLAD 0.241/0.230 vs 自研 **0.245/0.247**；局部特征集成（Dedode v2+双 softmax / DISK+LightGlue / SIFT+NN）；旋转检测（<10% 判旋转则保留原方向）、同尺寸时共享内参、用图像间平均差异判断透明场景；基于 IMC2023 第 7 名 RMD-3DV 的开源代码 | 510499 |
| 3rd（510338） | **VGGSfM**：全帧跑 mAA +0.04（但 16GB 显存会 OOM）→ 拆成三条增量：① 用 VGGSfM track predictor 给 pycolmap 补充 2D 匹配（N=5 近邻，本地 +3%、LB ~0.17→0.18）② **用 VGGSfM 精化 pycolmap 的 SfM track**（31×31 patch，只精化重投影误差最大的 4096 条 track，Church 重投影误差 0.64→0.55；LB ~0.18→0.20）③ 用 VGGSfM 重定位未注册图像 + Umeyama 对齐 | 510338 |
| 8th（509902） | ALIKED+LightGlue；因旋转会降低关键点数，**先 4 向旋转找点 → 用 Homography 校正两图方向 → 再匹配**；pycolmap 分别以 simple-radial×2 + simple-pinhole×1 跑三次、取最大模型；双线程提点 + 双进程 COLMAP，T4×2 各绑一块 GPU | 509902 |
| 事件 | "Strange Behavior in IMC?"（35 票）与"推断榜单与末期洗牌"（29 票）；"LightGlue vs SuperGlue"（28 票）；IMC2023 冠军代码公开（27 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 4th | 8th |
| --- | --- | --- | --- | --- | --- |
| 匹配器 | ALIKED+LightGlue（高分辨集成） | 三种局部特征集成 | ALIKED+LG + VGGSfM tracks | ALIKED+LG | ALIKED+LG |
| 图像对 | 匹配数阈值过滤 | MST 骨架 | NetVLAD/DINO 近邻 | **穷举** | 4 向旋转 + Homography 校正 |
| 透明场景 | **TSP 排序 + 圆周布相机** | 同上 + 自研全局描述子 | — | **DINOv2 bottle 分割 + 网格匹配** | — |
| 图像池 | 提交列表 | 提交列表 | 提交列表 | **images 全量** | 提交列表 |
| 关键增量 | 透明 trick +0.03 | 全局描述子 +0.004~0.017 | VGGSfM 三条增量 +0.03 | 全量图像 +0.011 | 旋转鲁棒 + 多模型 |

### 共识 / 分歧 / 裁决
**共识一：透明场景必须单独处理（1st/2nd/4th）**
SfM 在透明/反光物体上直接失效；1st/2nd 用"排序 + 圆周布相机"的几何先验（+0.03 LB），4th 用前景分割 + 网格内匹配。**裁决**：新场景类别出现时，先问"这个类别的物理结构能否直接给位姿约束"，而不是继续调匹配器。置信度：高。

**共识二：ALIKED+LightGlue 是本届的性价比之王（1st/4th/8th）**
三队主力都是 ALIKED+LightGlue；1st 试过 LoFTR/DKM/RoMa/OmniGlue/XFeat/DISK/SIFT 后仍选择它（理由：密集匹配器跨图重复性差、噪声高）。**裁决**：工具换代（IMC2022 的 LoFTR/SuperGlue → IMC2024 的 ALIKED/LightGlue）要跟着社区最新验证走。置信度：高。

**共识三：工程（缓存、并行、多解合并）决定能否用满时间预算（1st/3rd/8th）**
1st 缓存关键点描述子、双 GPU 并行、重复建图 + Horn 合并；3rd 把 VGGSfM 拆成"补匹配/精化/重定位"以适应 16GB 限制；8th 用 2 线程 + 2 进程跑满 T4×2。**裁决**：9 小时限时的代码赛里，"能否把方案跑完"与"方案有多好"同等重要。置信度：高。

**分歧一：图像对怎么选**
1st 用"匹配数阈值"而不是检索模型；2nd 用 MST 骨架 + 自研全局描述子；4th 直接穷举（"场景图像数本来就不多"）；8th 用旋转校正。**裁决**：当每场景图像数少时穷举最稳；图像多时再上检索/骨架。检索模型的收益只在候选对质量成为瓶颈时体现（2nd 的 NetVLAD vs 自研差距仅 0.004~0.017）。置信度：中高。

**事件：用"提交列表之外的图像"（4th）**
4th 发现 test 的 images 文件夹里有 submission.csv 未列出的图像，把它们纳入重建后 LB +0.011。**裁决**：代码赛要审计"数据目录 vs 提交清单"的差异；这类"白送的数据"往往被忽视。置信度：中高（有消融表）。

**事件：旋转鲁棒性（4th/8th）**
主办方去掉了 EXIF、可能故意旋转图像；4th 缓存 4 个角度的关键点，8th 先旋转找点再用 Homography 校正后重匹配。**裁决**：无 EXIF 的图像匹配要显式处理旋转（枚举角度或校正后再匹配）。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的透明 trick +0.03 与各模块细节 | 自述 + 公开代码 | 高 |
| 4th 的四行消融表（0.149→0.197） | 自述 + 表（含三个场景的 val） | 高 |
| 3rd 的 VGGSfM 三条增量与耗时 | 自述 + 代码 | 中高 |
| 2nd 的全局描述子对照（NetVLAD vs 自研） | 自述 + 表 | 中高 |
| 8th 的双 GPU 编排 | 自述 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 5th（定制场景匹配，31 票）与 6th/7th 的方案未细读；"Strange Behavior in IMC?"（35 票）与"榜单推断"（29 票）未细读；
- 1st 的"最佳私榜合并 OmniGlue 未选"提示 OmniGlue 价值可能被低估，无进一步证据；
- 透明场景的官方评测阈值与类别定义未在材料中展开；
- 归档 12 图：1st 的 8 张（管线/裁剪/透明圆周/数据集）、4th 的 6 张（分割与关键点可视化）为主要图证。

### 图证（KStarter 仓库内路径）
- ../../intel/image-matching-challenge-2024/bodies/510084_img/01.png — 1st 的参考管线
- ../../intel/image-matching-challenge-2024/bodies/510084_img/05.png — 1st 的透明场景相机圆周假设

### 出处
- 1st（510084）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/510084
- 2nd（44 票）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/510499
- 3rd（31 票）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/510338
- 4th（46 票）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/510611
- 5th（31 票）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/510603
- 8th（58 票）：https://www.kaggle.com/competitions/image-matching-challenge-2024/discussion/509902

### 外部题解（kaggle-solutions）
- rank 6｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/511291
- rank 10｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/515089
- rank 12｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/510673
- rank 13｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/510295
- rank 16｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/509883
- rank 26｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/509918
- rank 39｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/510373
- rank 48｜description：https://www.kaggle.com/c/image-matching-challenge-2024/discussion/511507

---

## image-matching-challenge-2025 — Image Matching Challenge 2025 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 IMC 2025 Metric ｜ 队伍 943 ｜ 截止 2025-06-02 ｜ Tier B ｜ 标签 cv,retrieval
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/image-matching-challenge-2025.md
> 材料基础：`digests/image-matching-challenge-2025.md`（6 篇正文：1st 583058 / 4th 582959 / 10th 582898 / 11th 583097 / 理论入门 573183 / 往届方案 571280；70 条主题索引）+ 15 张图

### 一句话重述
IMC 2025 的技术分水岭是**3D 几何基础模型（MASt3R/VGGT）**：1st 用 MASt3R 的半稠密匹配直接替换 ALIKED+LightGlue 类检测器方案，并指出"**在本场上，MASt3R 的局部特征头显著优于检测器系**"；其余队伍的主战场转向**图像对选择（短名单/聚类分类器/动态 top-k）**——因为错误的图像对会把不同场景混进同一次重建。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（583058） | 简单 MASt3R 管线：**短名单 = 多种检索结果的并集**（MASt3R-ASMK `n=10,k=25`、MASt3R-SPoC、DINOv2、ISC）；用 MASt3R 做半稠密匹配，**同时把其他检测器的关键点也交给 MASt3R 匹配**；再用通用 COLMAP 管线建图；自述"把 MASt3R 当半稠密匹配器接进 COLMAP 就有公榜 42–45，**加大图像对数量后到约 50**"；预聚类（基于 MASt3R 匹配的连通扩展）最终未采用（"用 MASt3R 匹配后，聚类与否差别不大"）；理由：MASt3R 精度高（错误匹配少），在检测器系失效的脏场景也能匹配 | 583058 |
| 4th（582959） | RDD（可变形 Transformer 检测器/描述子，CVPR 2025）+ 基准 DINOV2+ALIKED+LightGLUE；**旋转纠正**用 check_orientation 但加 **0.9 置信度阈值**过滤误报；**图像对同场景二分类器**：线性 Transformer 训练"两图是否同场景"，用 MegaDepth 扩充训练集（验证 99% 准确率），用于剪掉错误对；**但直接剪会掉公榜分**（也剪掉真对）→ 用 NetVLAD 检索对补偿：每场景至少 20 对、最多 0.12×n 对 | 582959 |
| 10th（582898） | 团队（含 tmyok1984）重点全在**图像对选择**：**动态 top-k**（按数据集/场景调整 k，避免 fbk_vineyard 这类"视觉混淆场景"的错误配对把不同簇混在一起）；配对后就是"ALIKED-LightGlue + pycolmap"的朴素管线；自述"私榜洗牌是因为配对策略恰好适配" | 582898 |
| 11th（583097） | 另一套前排名方案（digest 有正文） | 583097 |
| 社区 | "**开始做图像匹配所需的所有理论**"（57 票）、"公榜与本地分数"（52 票，讨论 CV-LB 结构）、"往届顶级方案汇总"（42 票）、"内存高效的 VGGT 跟踪 + 位姿精化"（28 票）、"12th：把 COLMAP 推到极限"（26 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 4th | 10th |
| --- | --- | --- | --- |
| 匹配器 | **MASt3R（半稠密 + 稀疏关键点）** | RDD + ALIKED/LightGlue 基准 | ALIKED-LightGlue |
| 图像对 | 4 种检索并集（ASMK/SPoC/DINOv2/ISC） | **同场景二分类器剪枝 + NetVLAD 补偿（≥20 对，≤0.12n）** | **动态 top-k** |
| 旋转 | — | check_orientation + 0.9 阈值 | — |
| 重建 | 官方 COLMAP 管线 | COLMAP | pycolmap |
| 结论 | 3D 基础模型 > 检测器系 | 配对剪枝要防"剪真对" | 配对策略决定名次 |

### 共识 / 分歧 / 裁决
**共识一：图像对选择是 IMC 2025 的主战场（1st/4th/10th）**
1st 明确"**配对数量越多分数越高**（42–45→50），所以如何在小算力内加对子很关键"；4th 专门训二分类器剪掉错误对；10th 把全部精力押在动态 top-k。**裁决**：当匹配器足够强（MASt3R 级）时，瓶颈转移到"选哪些对"；而选对子的目标函数是"覆盖真实共视 + 剔除跨场景混淆"。置信度：高。

**共识二：3D 几何基础模型改变了匹配范式（1st + 社区 VGGT 帖）**
1st 说 MASt3R 的局部特征头"显著优于 ALIKED+LG"（原因：3D 几何特征 + 在 MegaDepth 之外还训练了一批物体中心数据集）；社区另有"内存高效 VGGT 跟踪 + 位姿精化"帖（28 票）。**裁决**：IMC 2025 起，"匹配器换代到几何基础模型"是确定趋势；检测器系方案退为基线与多样性来源。置信度：高。

**共识三：剪枝错误的图像对必须留"补偿机制"（4th）**
4th 的二分类器准确率 99%，但直接剪枝**掉了公榜分**（剪掉真对）→ 加 NetVLAD 对补偿后才涨。**裁决**：配对剪枝要设计"下限保证"（至少 N 对/最多比例），不能纯靠分类器。置信度：中高（单队但机制清晰）。

**分歧一：要不要预聚类**
1st 试了基于 MASt3R 匹配的预聚类，最终弃用（"用 MASt3R 后聚类与否差别不大"）；4th/10th 走"分类器剪枝/动态 top-k"的轻量路线。**裁决**：当匹配器精度足够高时，聚类是冗余的；当匹配器弱时，聚类/剪枝是必需。置信度：中高。

**事件：公榜与本地分数结构（52 票帖）**
社区专门讨论本场"公榜 vs 本地分数"的关系；10th 说私榜洗牌来自配对策略的适配。**裁决**：SfM 赛的本地验证要复刻"场景内配对图 + 重建注册率"的分布，否则与榜面脱钩。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的 MASt3R 管线与 42–45→50 的观察 | 自述 + 管线图 + 公开 notebook | 高 |
| 4th 的二分类剪枝 + 补偿（99% 验证准确率） | 自述 + 图 | 中高 |
| 10th 的动态 top-k 与私榜洗牌自评 | 自述 + 图 | 中 |
| VGGT 跟踪帖 | 社区帖（28 票） | 中 |
| 往届方案汇总 | 社区整理 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/3rd/5th–9th/12th–15th 的方案未入库；"开始做图像匹配所需的所有理论"（57 票）未细读；
- 1st 未给 MASt3R 与其他匹配器的量化对照（只有"显著更好"与总分区间）；
- 4th 的 RDD 与基准的逐项消融未展开；
- 归档 15 图：1st 的 MASt3R 管线图（图 1）、4th 的剪枝示例、10th 的动态 top-k 图为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/image-matching-challenge-2025/bodies/583058_img/01.png — 1st 的 MASt3R 管线

### 出处
- 1st（583058）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/583058
- 4th（35 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/582959
- 10th（32 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/582898
- 11th（33 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/583097
- 理论入门（57 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/573183
- 往届方案（42 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/571280
- VGGT 跟踪（28 票）：https://www.kaggle.com/competitions/image-matching-challenge-2025/discussion/582968

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583683
- rank 3｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583401
- rank 5｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583711
- rank 6｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583076
- rank 7｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583184
- rank 8｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/582844
- rank 9｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583464
- rank 12｜description：https://www.kaggle.com/c/image-matching-challenge-2025/discussion/583185

---

## isic-2024-challenge — ISIC 2024 深读：GBDT 元模型 × 图像 OOF 特征 × 患者内相对化

> 主题 cv ｜ 类别 Research ｜ 指标 ISIC pAUC-aboveTPR ｜ 队伍 2739 ｜ 截止 2024-09-06 ｜ Tier A ｜ 标签 cv,ranking
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/isic-2024-challenge.md
> 材料基础：`digests/isic-2024-challenge.md`（6 篇正文：1st/2nd/9th/12th + 296 票数据帖 + 67 票增广帖；80 条讨论索引）+ 10 张图（533196×5 / 532642×2 / 517141×3）

### 一句话重述
题面是"3D-TBP 皮肤病变裁剪图 + 元数据 → 恶性二分类"，实际被考的是**极端不平衡下的表格-图像融合排序赛**：
1. **正样本约 0.1%**：训练集 393 张恶性 vs 40 万+ 良性（约 1:1000）；指标 pAUC 只统计高 TPR 区间 → "在最可疑样本上的排序"决定一切，阈值与校准无关。
2. **标准结构 = GBDT 主模型 + 图像模型 OOF 分数当特征**：四队全部沿用同一骨架，差异在特征工程、采样、噪声注入与集成细节；图像模型单独只有 ~0.15，融合后到 ~0.18（9th/12th 数字）。
3. **患者内相对化（ugly duckling）是领域先验**：临床判读看"该病变对这名患者是否异常"，1st 的 LOF、2nd 的患者内标准化、12th 的 KNN(k=5) 都在把绝对特征转成相对特征。
4. **外部/合成数据的边界**：往届 ISIC 数据直接混训失败（2nd 的域分类器 AUC 0.99 证明分布差异），但预训练式使用有效（1st 私榜 +0.002）；SD 合成数据提升单模型却对最终集成无增益。
一句话：**这是一场"元模型工程"比赛**——树模型是主体，图像模型是特征源，患者是归一化单位，CV 纪律决定公私榜排名。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 训练集正负比 | **393 恶性 vs 40 万+ 良性**（≈1:1000，0.1%） | 515356 |
| 往届数据集 | ISIC2020 32542/584；ISIC2019 20809/4522；ISIC2018 8197/785（裁剪到 224/256） | 515356 |
| 1st GBDT 规模 | CatBoost/LGBM/XGB × 5 fold × 10 seed = **150 模型**（基础 45 模型无显著差异）；全部训练 < 20 分钟；rank 平均 | 1st |
| 1st 特征准入 | 10 seed 配对 t 检验；只测最重要改动（多重比较）；后期阈值降到 p<0.2 | 1st |
| 1st LOF 增益 | CV 0.18149 → 0.18185 | 1st |
| 1st 往届预训练 | CV 0.1756→0.1760；公榜 0.180→0.182；**私榜 0.163→0.165** | 1st |
| 1st 合成数据（个体均值） | base vs synthetic：CV 0.1559→**0.161**；私榜 0.1318→**0.1346**；公榜 0.1498→**0.1508** | 1st（图 3） |
| 1st 合成数据（集成） | 合成模型集成私榜 0.140 vs 基线 0.142、公榜 ~0.157；加入最终集成无增益 | 1st |
| 1st OOF 噪声 | σ 测试 0.02/0.05/0.08/0.12，最终 **0.1**（LB 探针选定）；标准化预测 p1=−0.44 / p99=4.99 | 1st |
| 2nd GBDT 规模 | 每算法 18 变体 × 3 算法 = 54 模型；全量数据 seed 平均 n=5；num_boost_round 200–300 | 2nd |
| 2nd 图像模型 CV | resnext50 0.1515（最佳）～ swinv2_small 0.1612（最差）；eva02/deit3 0.1534–0.1537 | 2nd |
| 2nd 域差异 | ISIC2018 vs 2024 域分类器 **AUC 0.99** | 2nd |
| 9th pipeline | CV 0.177/0.175/0.175；LB 0.183/0.183/0.180；首次 blend +0.3 → 0.186；最终 CV 0.182 / LB 0.187 | 9th |
| 9th 图像模型 | effnet_b0 LB 0.155 与 0.158（TTA 0.161）；swinv2_tiny 0.159；convnextv2_tiny 0.158 | 9th |
| 9th 采样/预算 | 5% 负样本 + 正样本 ×10；**3 epoch**；lr 1e-4；BCE | 9th |
| 9th Resize bug | A.Resize 在增广列表开头 → 移到归一化前：LB 0.148 → 0.154–0.155 | 9th |
| 12th 结构 | GLCM + KNN(k=5) + 高斯噪声；4 GBDT（含 1 个无图像特征）× 15 fold × 5 seed；best LB 0.183/0.171（CV 0.1804） | 12th |
| 12th 图像模型 | EfficientViT-v2 0.156/0.153；EdgeNeXT 0.156/0.155；EffB2 0.1493/0.154；EffB0 0.151/0.144；EVA02 0.154/0.154 | 12th |
| 12th FTTransformer | CV 0.178 / LB 0.179 / 私榜 0.165（未采用） | 12th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 9th | 12th |
| --- | --- | --- | --- | --- |
| 主结构 | GBDT 集成 + 图像 OOF 特征 | GBDT 集成 + 图像 OOF 特征 | 3 条 tabular pipeline + 3 图像模型 → hill-climb | 4 GBDT + 图像 OOF + GLCM/KNN 特征 |
| 表格特征 | 公共 notebook + 患者内 LOF + 病变面积（总/按部位） | 公共 notebook 特征 + 患者内标准化（按 location/location_simple/anatom_site）+ Tabular Ugly Ducklings | 上下文统计（z-score/range/skew/kurtosis/max 比值）+ rank/groupby | GLCM + KNN(k=5) + age 差分 + 分位数 |
| 图像模型 | EVA02-small + EdgeNeXt-base（1:1 batch） | 9 个模型 / 5 设置：eva02_small、deit3_small、beitv2_base、convnextv2_tiny/nano、swinv2_small、resnext50、swin_tiny | effnet_b0 ×2、swinv2_tiny、convnextv2_tiny | EfficientViT-v2、EdgeNeXT-base、EffNet-B2/B0、EVA02 |
| 图像→表格 | 每模型标准化 OOF（p1 −0.44 / p99 4.99）+ 相对患者均值比率 + 高斯噪声 σ=0.1 | 0–3 个图像特征作 meta（数量做多样性） | 每 pipeline 用 1 个 backbone 的预测 | 5 模型 OOF + 高斯噪声 |
| 不平衡 | 每 batch 1:1 平衡 | 每 epoch 1:3 / 1:5 undersampling | 只用 5% 负样本、正样本 ×10 | 正上采样 + 负下采样 |
| 训练预算 | 200 epoch 上限、早停（容忍 10 次）；验证频率递增进 | 50–200 epoch，**不用早停** | **3 epoch** | 15 fold × 5 seed |
| CV 协议 | 5-fold Stratified Group + 10 seed t 检验（p 值准入） | Triple Stratified Leak-Free KFold | 5-fold SGKF + 5 seed 预筛 + LB 确认 | Triple Stratified |
| 集成 | 150 模型 rank 平均 → GBDT | 54 模型 × seed 平均 | hill-climb 权重 | 4 GBDT mean |
| 外部/合成 | 往届 3 类预训练（+0.002 私榜）；SD1.5 合成 6000 张（个体更好、集成未用） | 往届数据放弃（域分类器 AUC 0.99） | — | 往届数据、伪标签均失败 |
| 报告成绩 | 公榜 ~0.185→更好、私榜 0.173→略差 | 图像 CV 0.1515–0.1612 | 3 pipeline LB 0.183/0.183/0.180 → blend 0.186 → 最终 CV 0.182 / LB 0.187 | best LB 0.183/0.171；best CV 另训 |
| 失败清单 | hard negative 采样、往届数据混训、多增广平均预测、聚类 z-score（私榜无效） | 往届数据混训（含直方图匹配）；域差异未识别 | hard negatives、focal loss、mixup 进集成、stacking、**0.5 缩放/rank 集成、Dullrazor、发丝增广、lesion-id 权重、scratch 训练 | 往届数据、伪标签；FTTransformer（CV 0.178/LB 0.179/私 0.165）不如 GBDT |

### 共识 / 分歧 / 裁决
**共识一：图像模型的正确用法是"OOF 分数当特征"，不是直接加权（4/4）**
四队都以 GBDT 为主模型；图像模型只通过 OOF 预测进入表格特征（1st 还做 per-model 标准化 + 相对患者均值比率）。**图像单模型 LB ~0.15 vs 融合后 ~0.18**（9th/12th）——表格线是主力，图像线是增量。

**裁决**：GBDT 能条件化图像分数（不同部位/年龄/图像质量下分数含义不同）并学习交互；直接加权平均做不到。前提是 OOF 必须无泄漏（患者隔离）。置信度：高（4 队同构 + 数字层级差）。

**共识二：患者内相对特征是领域先验（3/4 明确、2nd 体系化）**
1st：LOF 分数（CV 0.18149→0.18185）；2nd：患者内标准化（按 location/location_simple/anatom_site）+ Tabular Ugly Ducklings；12th：KNN(k=5) 近邻特征。临床逻辑：恶性判读的显著线索是"这颗痣对该患者不正常"。

**裁决**：医学筛查赛把绝对特征转成"患者内相对特征"是低成本高确定性的增益来源；pAUC 的头部排序区尤其受益。置信度：高（三队独立采用）。

**共识三：极端不平衡的采样强度决定训练预算（3/4 有明确数字）**
1st：batch 内 1:1；2nd：每 epoch 1:3–1:5 undersampling（50–200 epoch）；9th：5% 负样本 + 正样本 ×10（**只训 3 epoch**）；12th：正上采样 + 负下采样。

**裁决**：采样比率与 epoch 数是同一枚硬币的两面——每 epoch 见到的正样本越多，需要的 epoch 越少（9th 3 epoch vs 2nd 200 epoch）。选型应同时决定，不可分开调。置信度：中高。

**分歧一：往届 ISIC 数据——混训失败 vs 预训练有效**
支持方：515356 发布的高质量数据集获 296 票（社区大量使用）；1st 用往届数据训 3 类模型（bkl/melanoma/nevus）做预训练，CV 0.1756→0.1760、公榜 0.180→0.182、**私榜 0.163→0.165**。
反对方：2nd 直方图匹配后仍无提升，训练域分类器区分 ISIC2018 vs 2024 轻松达到 **AUC 0.99** → 放弃；12th 明确"use of past data"失败；515356 评论区也报告"用外部正样本混训导致 train pAUC 虚高、验证不涨"。

**裁决**：与 T8 既有结论完全一致——**预训练式（只迁移表示）有效，直接混训（改变训练分布/先验）失败**；且往届数据集阳性率 1.8%–18%，与本届 0.1% 的先验相差 1–2 个数量级，混训等于改变任务。域分类器 AUC 是量化"能不能混"的标准工具（0.99 → 不能）。置信度：高（三队 + 定量证据）。

**分歧二：合成数据——个体有效 vs 集成无效**
1st：SD1.5 在正样本上微调（50 epoch，batch 8，128×128）→ 生成 6000 张（2 分辨率 × 2 scheduler × 多 prompt）；合成模型在 CV/公榜/私榜上全面略优（图 3：CV 0.1559→0.161、私榜 0.1318→0.1346、公榜 0.1498→0.1508），合成数据模型集成单独看私榜 0.140 vs 真实 0.142；**但加入最终集成无增益 → 未采用**。

**裁决**：合成数据的价值要分两层看——"提升单个模型"与"提升模型集合多样性"不是一回事；若合成模型与真实模型误差高度相关（同 backbone/同数据配方），边际集成收益≈0。判断标准应是"合成模型是否覆盖真实模型的失败区"。置信度：中（单案例，但有完整数字与图证）。

**分歧三：CV 纪律 vs 公榜依赖（本场最强张力）**
1st：前中期用 10-seed 配对 t 检验（多重比较只测最重要改动）；**后期卡在 0.185–0.186 时降低阈值到 p<0.2 并主要靠公榜** → 最终公榜更好、私榜略差（自述的直接代价）。
2nd：自建 Triple Stratified Leak-Free CV（患者隔离 + 恶性比例分层 + 患者图像数分箱）。
9th：每个特征先过 5 seed 组合，再上 LB，最后 CV 0.182/LB 0.187 一致。
12th：同样 Triple Stratified。
未收录的 7th/8th/13th 标题（"A good CV is all you need"/"Trust your CV"/"God Bless CV"）进一步印证本场社区共识。

**裁决**：小提升（≤0.002）在多 seed 噪声内，必须用配对检验/leak-free CV 才可信；t 检验要控制多重比较；公榜可以确认但不能替代 CV——1st 的后期转向是"公榜过拟合"的教科书自述。置信度：中高（1st 亲历 + 三队协议 + 标题证据）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 393 正 vs 40 万+ 负 | **数据帖 + 官方规模** | 高 |
| 1st 合成数据个体更优 | **自述 + 图 3 柱状图** | 中高（有图证） |
| 1st 往届预训练 +0.002 私榜 | 自述（代码公开） | 中高 |
| 域分类器 AUC 0.99 | 2nd 自述（方法标准、结论方向由两队佐证） | 中高 |
| 9th Resize bug 0.148→0.154 | 自述（A.Resize 位置可复现） | 中 |
| 12th FTTransformer 数字 | 自述 | 中 |
| 1st 用 LB 探针选 σ=0.1 | 自述（无 CV 支撑；LB probing 是本场已登记的争议话题 517139） | 中低 |
| 7th/8th/13th "CV 至上" | 仅标题（正文未收录） | 低（方向性佐证） |

### 悬案与失败学
**分歧一：往届 ISIC 数据——混训失败 vs 预训练有效**
支持方：515356 发布的高质量数据集获 296 票（社区大量使用）；1st 用往届数据训 3 类模型（bkl/melanoma/nevus）做预训练，CV 0.1756→0.1760、公榜 0.180→0.182、**私榜 0.163→0.165**。
反对方：2nd 直方图匹配后仍无提升，训练域分类器区分 ISIC2018 vs 2024 轻松达到 **AUC 0.99** → 放弃；12th 明确"use of past data"失败；515356 评论区也报告"用外部正样本混训导致 train pAUC 虚高、验证不涨"。

**裁决**：与 T8 既有结论完全一致——**预训练式（只迁移表示）有效，直接混训（改变训练分布/先验）失败**；且往届数据集阳性率 1.8%–18%，与本届 0.1% 的先验相差 1–2 个数量级，混训等于改变任务。域分类器 AUC 是量化"能不能混"的标准工具（0.99 → 不能）。置信度：高（三队 + 定量证据）。

**8. 悬案与失败学**
**悬案**

1. **未收录的 3rd/4th/7th/8th/13th 方案（正文缺口）**：其中 7th "A good CV is all you need"、8th "Trust your CV"、13th "God Bless CV" 三连标题与 1st"后期转向公榜、私榜变差"的自述构成同题张力；补读后可作为 T3 的强证据。
2. **Public 1st / Private 24th（532564，81 票）未收录**：公榜过拟合的极端案例，与 1st 的轻微版本同源；机制未明。
3. **LB probing（517139，130 票）未收录**：1st 明确用探针选 σ，但探针方法与合规边界未在已收录材料里展开。
4. 合成数据为何"个体更好、集成无用"：缺少误差相关性/失败区覆盖分析（本文 M7 为机制推演，非实证）。
5. 2nd 的图像模型 CV 0.1515–0.1612 与最终 GBDT 融合分数之间缺少消融表（哪些设置贡献最大未量化）。

**失败学（跨队合集）**

- 数据侧：往届数据混训（2nd/12th）；外部正样本混训致 train pAUC 虚高（515356 评论区）；伪标签（12th）；hard negative 采样/挖掘（1st/9th）。
- 训练侧：focal loss 劣于 BCE（9th）；scratch 训练（9th）；mixup 个体可用但进集成常拖后腿（9th）。
- 融合侧：**0.5 缩放/rank 集成、ExtraTrees/LR stacking（9th）；多增广平均预测（1st）**。
- 特征侧：聚类 z-score 无私榜增益（1st）；Dullrazor 去毛、发丝增广、lesion-id sample weight（9th）；FTTransformer 不如 GBDT（12th）。
- 工程侧：A.Resize 位置错误（9th，+0.006 LB）——**增广顺序是容易被忽视的高性价比检查项**。

### 图证（KStarter 仓库内路径）
- ../../intel/isic-2024-challenge/bodies/533196_img/01.png — 1st 的合成数据生成管线：SD1.5 → 6000 张 → 训练（topic 533196）
- ../../intel/isic-2024-challenge/bodies/533196_img/02.png — 真实恶性病变 vs Derm-T2IM 合成 vs 1st 自产合成（512/128）（topic 533196）
- ../../intel/isic-2024-challenge/bodies/533196_img/03.png — 合成 vs 基线个体的 CV/公榜/私榜对比（topic 533196）
- ../../intel/isic-2024-challenge/bodies/532642_img/01.png — 12th 的 best LB 模型结构：GLCM + KNN + 加噪 OOF + 4 GBDT（topic 532642）
- ../../intel/isic-2024-challenge/bodies/517141_img/03.png — microscope 增广示例：正/负样本（topic 517141）

### 出处
- 1st（149 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/533196
- 2nd（71 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/532704
- 9th（81 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/532577
- 12th（65 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/532642
- 数据帖（296 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/515356
- 增广帖（67 票）：https://www.kaggle.com/competitions/isic-2024-challenge/discussion/517141
- 缺口登记（未收录正文）：3rd(532919) / 4th(532760) / 7th(532687) / 8th(532728) / 11th(532595) / 13th(532654) / 54th(532644) / Benchmarking(527023) / LB probing(517139) / Public1st-Private24th(532564) 等

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532919
- rank 4｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532760
- rank 5｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/533056
- rank 6｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532868
- rank 7｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532687
- rank 8｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532728
- rank 10｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/533179
- rank 11｜description：https://www.kaggle.com/c/isic-2024-challenge/discussion/532595

---

## iwildcam2022-fgvc9 — iWildCam 2022（FGVC9 野生动物计数）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Mean Absolute Error ｜ 队伍 24 ｜ 截止 2022-05-30 ｜ Tier B ｜ 标签 cv,wildlife
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/iwildcam2022-fgvc9.md
> 材料基础：`digests/iwildcam2022-fgvc9.md`（6 篇正文：9th 328526 / 往届参考 314736 / 起步 notebook 323139 / 1st 328965 / DeepMAC 掩码公告 316483 / DeepMAC 数据询问 315980；16 条主题索引）+ 0 张归档图

### 一句话重述
从相机陷阱**序列**里数动物（MAE 越低越好），官方提供 **MegaDetector V4** 检测与 **DeepMAC** 实例掩码，但没有训练所需的 GT 计数。1st 的答案出人意料地"反工程"：**不训练、不跟踪，只做检测过滤 + 每序列取最大计数**——按物体密度分两类图片分别调阈值/NMS，把 public MAE 做到 **0.247**；9th 走"检测器 + 融合 + 帧间跟踪"的重工程路线（public/private 0.275/0.265），并诚实报告了帧间计数在全集上无法兑现。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与任务 | **24 队**；统计序列内动物数量；MAE；FGVC9/CVPR workshop；无 GT（评测不可本地复算） | 索引 / 328965 |
| 1st（不训练） | 基于 MegaDetector 检测过滤；观察"阈值 0.95 会**高密度图少算、低密度图多算**"，以**每图 8 个预测**为界分两类：高密度图用**置信度 0.0 + NMS(IoU=0.2) + 抑制小框**（public 0.253）；低密度图按"无重叠框 0.98 / 有重叠框 0.8"，再对剩 1–2 个框的图做第二轮 0.98 过滤 → **public 0.247**；最终对序列取最大计数 | 328965 |
| 9th（重工程） | MegaDetector v4 检测 → 训练 **YOLOv5** 第二检测器 → **WBF 加权框融合**（public/private **0.275/0.265**，高于 2021 冠军基线）→ 对 8 类群居物种（白唇西貒 2、领西貒 8、野山羊 70、家牛 71、绵羊 72、非洲象 90、黑斑羚 96、单峰驼 256）做**帧间个体跟踪**：DeepMAC 掩码质心取小图 → 自编码器 **512 维**潜向量 + (X,Y,area,ΔT) 做检测级匹配；全集上未能带来收益 | 328526 |
| 官方数据资产 | DeepMAC 实例掩码（对 MegaDetector V4 框）随赛程发布，可用竞赛数据页或 GitHub 下载，配可视化 notebook | 316483 |
| 数据问题 | 重复数据（324436）；序列乱序（324425）；sample submission 格式疑问（317140）；wrap-up 截止 6/10（328927） | 索引 |
| 社区参考 | 往届 Wildcam（2019–2021）热门 notebook 与获奖方案合集（16 票）；起步 notebook 5 个（CNN、数据提取、DeepMAC 掩码可视化、GPS 聚类、TF starter） | 314736 / 323139 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st（纯过滤） | 9th（检测+跟踪） |
| --- | --- | --- |
| 模型 | 无训练（仅过滤 MegaDetector） | YOLOv5 + MegaDetector |
| 融合 | NMS + 密度分层阈值 | WBF |
| 时序 | 每序列取最大计数 | 自编码器潜向量帧间匹配 |
| 结果 | public **0.247** | public/private 0.275/0.265 |
| 结论 | 无 GT 时先榨干检测器 | 跟踪在全集难兑现 |

### 共识 / 分歧 / 裁决
**共识一：没有 GT 的检测赛，先做"过滤与聚合"而不是训练（328965 / 328526；置信度中高）**
1st 明确不使用训练（用检测器当训练数据会误差传播且难以超越 MegaDetector）；9th 的 WBF 融合也是"后处理换分"。**裁决**：先用检测器置信度分布 + NMS/密度分层 + 序列聚合（max/median）建立强基线，再考虑训练。置信度：中高。

**事件一：密度分层是可复用的后处理套路（328965；置信度中高）**
同一阈值在高/低密度图上偏差相反，按"每图 >8 个框"切换策略后 MAE 明显改善。**裁决**：计数任务先画"密度 vs 误差"曲线，按密度分桶设阈值/NMS；不要用单一阈值通吃。置信度：中高。

**事件二：帧间跟踪理论优、工程难（328526；置信度中）**
9th 用 DeepMAC 掩码选 chip + 自编码器特征做个体匹配，小范围/视频有效，但扩到全集无法稳定收益；方向估计也不可靠。**裁决**：跟踪作为加分项，必须在全量验证上与"max 聚合"对照；先保住过滤基线。置信度：中。

**事件三：DeepMAC 掩码的正确用法是"选像素"（328526 / 316483；置信度中）**
用掩码质心取 chip 优于整框或框中心（排除遮挡/腿间背景）。**裁决**：实例分割掩码优先用于裁剪与特征提取，而不是直接当计数输入。置信度：中。

**事件四：序列乱序/重复会影响计数聚合（324425 / 324436；置信度中低）**
有帖报告序列顺序异常与重复数据。**裁决**：聚合前先校验 frame/sequence 顺序与重复；否则 max/跟踪都会被污染。置信度：中低（单帖）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的密度分层与阈值 | 冠军自述（328965） | 中高（有 public 分阶段数字） |
| 9th 的 WBF/跟踪与分数 | 自述（328526） | 中高 |
| DeepMAC 掩码可用性 | 官方帖（316483） | 高 |
| 往届参考与起步 notebook | 社区整理（314736 / 323139） | 中高 |
| 数据重复/乱序 | 低票帖（324436 / 324425） | 低—中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 本场没有官方/私榜完整结果归档；1st 只给 public 0.247；
- 私榜分数与最终排名未归档；
- 帧间跟踪为何在全集失效未定论（9th 自述仍在调查）；
- DeepMAC 是否被前排普遍使用无数据；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- 1st 方案（4 票 / 0 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/328965
- 9th 方案（3 票 / 0 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/328526
- 往届参考合集（16 票 / 0 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/314736
- 起步 notebook（5 票 / 3 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/323139
- DeepMAC 掩码公告（5 票 / 1 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/316483
- 数据重复（0 票 / 3 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/324436
- 序列乱序（0 票 / 4 评论）：https://www.kaggle.com/competitions/iwildcam2022-fgvc9/discussion/324425

---

## mayo-clinic-strip-ai — Mayo Clinic STRIP AI 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Weighted Multiclass Loss ｜ 队伍 888 ｜ 截止 2022-10-05 ｜ Tier B ｜ 标签 cv,classification
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/mayo-clinic-strip-ai.md
> 材料基础：`digests/mayo-clinic-strip-ai.md`（5 篇正文：1st 357892 / 2nd 358089 / 5th 358029 + 秘方 357877 / 25th 357898 等；80 条主题索引）+ 3 张图

### 一句话重述
从脑卒中血栓的全切片图像（WSI）判断病因类型（CE/LAA/Other）。这是个**信号极弱**的比赛：多数队伍打不过 sample submission，公榜只有 20 个样本。真正的考点是**"承认低信号 + 用正确 CV 与正确的分数尺度去对齐 log-loss 型指标"**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（357892） | tiling 后取**最暗的 16 块**；swin_large_patch4_window12_384 + **attention pooling**（CV 0.69→0.66，五折均值）；**MoCo-v3 预训练使五折 CV 方差 0.30→0.15**；损失/指标严格按赛题实现；5 折 StratifiedGroupKFold（按类分层、按 patientid 分组）；swin + coat_lite_medium 集成仅 0.662→0.658；无效：更多 tile、其他预处理、按像素方差选 tile、染色归一化；自述"公榜样本太少，只能靠 CV；同时优化 CV 均值与方差" | 357892 |
| 2nd（358089） | **只训 513 个参数**：EfficientNet-B0 冻结 + 单 FC 层；流程：图缩 1/24 → 28×28 块"行间像素差"判血液/背景 → 224×224 stride28 取块 → **去除交叠>50% 的重复块** → 随机 20 块；不做颜色归一化（改用强 color jitter）；**按诊所分组 CV**（训练集只有 18 家诊所中的 11 家，小诊所合并到每组 ≥90 例）；6 折模型集成；batch 64；BCELoss；无 tile 的图给 0.5；自述"一切都取决于正确的验证与无视公榜" | 358089 |
| 5th（358029 + 357877） | 背景色归一化（r = background/255）→ 去白块 → 去重 → 最长边 1024；三个小模型（ResNet10t 0.661 / EffNet-b0 0.671 / 简化版 0.662 AUC）；class-balanced BCE + label smoothing（故意欠拟合）；4 flip TTA；**指标对齐**：log-loss 对"自信的错"惩罚极重 → **把输出线性缩放到 [0.15,0.85] 再截断到 [0.25,0.75]** → CV 0.640 / pub 0.733 / priv 0.666；明说"只比随机（0.69）低 0.05 左右，这大概是这份数据能到的最低点了" | 358029/357877 |
| 25th（357898） | 自建 MIL（timm 底座）+ 预计算实例：JPEG q100、最长边 20000、非重叠块、按像素和降序取 16 块；指出公开 notebook 把特征图按高度拼接"很怪"，改用不同 pooling/聚合；自述与 RSNA-MICCAI 脑瘤赛的高度相似（低信号） | 357898 |
| 社区侧 | "如何对付 WSI/RAM 爆炸"（58 票）、"你确定数据里有信号吗"（58 票）、"All you need is MIL"（39 票）、"我手工标了 2 万块（血栓 vs 背景）"（34 票）、多份切块数据集 | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 5th | 25th |
| --- | --- | --- | --- | --- |
| 选块 | 最暗 16 块 | 行间差+去重+随机 20 | 去白/去重 | 像素和 top-16（预计算） |
| 模型 | swin-large + attention pooling | **冻结 EffNet-B0 + 1 FC（513 参数）** | 3 个小模型集成 | 自研 MIL |
| 预训练 | MoCo-v3（降方差） | ImageNet | ImageNet | ImageNet |
| CV | StratifiedGroupKFold(patient) | **按诊所分组** | — | — |
| 指标处理 | 按赛题实现损失 | 赛题指标 (0.5,0.5) 权重 | **[0.15,0.85] 缩放 + [0.25,0.75] 截断** | — |
| priv | 1st | 2nd | 0.666 | — |

### 共识 / 分歧 / 裁决
**共识一：公榜不可用，一切靠分组 CV（1st/2nd/5th）**
公榜只有 20 个样本（5th 明说"公榜是随机的"）；1st 靠 patientid 分组、2nd 靠诊所分组（并处理小诊所样本量）、5th 干脆放弃公榜。**裁决**：低信号 + 极小公榜的赛题，CV 设计（分组维度 = 潜在域偏移来源：病人/诊所）是唯一可信的决策依据。置信度：高。

**共识二：log-loss 型指标必须处理"自信惩罚"的不对称（5th 讲得最清）**
权重 log-loss 对"自信且错"的惩罚远大于自信且对的奖励（图 1）；5th 用缩放+截断把输出压进"安全区"，2nd 用 label smoothing/欠拟合/小模型达到同一效果。**裁决**：当模型判别力弱（AUC ~0.67）时，**校准输出尺度**是与建模同等重要的一步；这一步能白拿分数。置信度：高（有图 + 多队实践）。

**共识三：WSI 的标准管线 = 切块筛选 → MIL/注意力 → 分组 CV（全员 + 社区）**
1st/2nd/25th 都做"块筛选 + 池化/注意力聚合"；社区有 WSI 内存教程与手工标注的血块/背景数据集。**裁决**：WSI 任务先解决"哪几块有信号"（血块 vs 背景），再谈分类器容量；块的选择策略（暗/方差/像素和）是独立的设计维度。置信度：高。

**分歧一：模型容量与预训练**
1st 用 swin-large + MoCo-v3 且强调降方差；2nd 反其道而行，冻结 B0 只训 513 参数拿第 2；5th 用三个小模型。**裁决**：数据信号弱、样本少时，**大模型的收益主要体现在稳定性（方差）而非均值**；小模型 + 强正则同样是合法解。置信度：中高。

**分歧二：染色/颜色归一化**
1st 明确"染色归一化没用"；5th 用背景色归一化赢在预处理；2nd 用 color jitter 代替归一化。**裁决**：颜色处理的收益依数据采集差异而定，应用 CV 验证后再定；不能把病理学惯例直接照搬。置信度：中。

**事件：低信号赛的预期管理**
5th 自述最终 CV 0.640，仅比随机（~0.69 的样本提交）低 0.05，"大概是这份数据能到的最低点"；"你确定数据里有信号吗"（58 票）成为高票帖。**裁决**：当数据本身接近无信号时，最优策略是"稳健的欠拟合 + 指标校准"，而非追求区分度。置信度：中高（多队共识 + 现象）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的 attention pooling/MoCo-v3 消融 | 自述 + 具体数字 | 中高 |
| 2nd 的诊所分组 CV 与 513 参数模型 | 自述（细节完整） | 中高 |
| 5th 的缩放/截断（0.640/0.733/0.666） | 自述 + log-loss 图 | 中高 |
| 25th 的 MIL 实现与预计算数据集 | 自述 + 公开代码 | 中 |
| "数据里信号极弱" | 多队 + 高票讨论 + 分数分布 | 高（现象） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd/4th/6th 的方案未入库；"Image Classification Checklist"（173 行处的高票长文）与 25th 的完整 pooling 对比未细读；
- 1st 的 5 折 CV 绝对值（0.66 档）与 2nd/5th 的口径不可比（分组方式不同）；
- 公榜/私榜的洗牌幅度与随机基线（样本提交 ≈0.69）的具体数值未在材料中给出；
- 归档 3 图：5th 的数据管线图与 log-loss 惩罚/奖励图（图 1）为关键证据；另有 1 个 SVG（335726）未展开。

### 图证（KStarter 仓库内路径）
- ../../intel/mayo-clinic-strip-ai/bodies/358029_img/02.png — log-loss 的惩罚/奖励分区

### 出处
- 1st（67 票）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/357892
- 2nd（358089）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/358089
- 5th（33 票）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/358029
- 5th 秘方（357877）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/357877
- 25th MIL（357898）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/357898
- "数据里有信号吗"（58 票）：https://www.kaggle.com/competitions/mayo-clinic-strip-ai/discussion/336260

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/mayo-clinic-strip-ai/discussion/358187
- rank 4｜description：https://www.kaggle.com/c/mayo-clinic-strip-ai/discussion/364466
- rank 6｜description：https://www.kaggle.com/c/mayo-clinic-strip-ai/discussion/359562
- rank 7｜description：https://www.kaggle.com/c/mayo-clinic-strip-ai/discussion/358130
- rank 13｜description：https://www.kaggle.com/c/mayo-clinic-strip-ai/discussion/358203

---

## neurips-2023-machine-unlearning — NeurIPS 2023 Machine Unlearning 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 56167-unlearn-metric ｜ 队伍 1188 ｜ 截止 2023-11-29 ｜ Tier B ｜ 标签 cv,education
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/neurips-2023-machine-unlearning.md
> 材料基础：`digests/neurips-2023-machine-unlearning.md`（6 篇正文：6th 458740 / 2nd 458721 / 5th 458531 / 12th 458648 / 论文合集 438660 / 奖牌争议 438567；80 条主题索引）+ 8 张归档图

### 一句话重述
给一个预训练图像分类模型（及 retain/forget 子集定义），产出"已遗忘"的模型：既要让 forget 集不再是成员（抗 MIA 检查），又要保住 retain 集性能。本届的实践结论是**"简单重置/蒸馏/微调"打败论文里的 SOTA 遗忘算法**——6th 重置首末层 + KL 蒸馏 + 三损失微调（最保守的一版私榜 0.07831）；2nd 用"1 轮 KL 打平 logits + 8 轮对抗微调"（CosineAnnealingLR 把公榜 0.084 抬到 0.091）；而 5th 报告 RelaxLoss、SCRUB、class weights 等全部无效。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 6th（458740） | 选择性参数重置（**第一层 conv1 + 最后一层 fc**）+ 验证集 KL 蒸馏预热 + 微调（硬 CE + 软 CE + KL）；两版提交：全类预热 公 0.08383 / 私 **0.07219**；仅前两类（forget 集只含 0/1 类）预热 公 0.08324 / 私 **0.07831**（私榜更优）；CIFAR-10 上 conv1/fc 的权重余弦相似度约 **-0.03 / -0.014**（方向相反）；fine-tune、eu-k、cf-k、bad teaching、SCRUB 均未超过基线微调；class weights 无效 | 458740 |
| 2nd（458721） | 两阶段：1 轮"KL→均匀分布"遗忘 + 8 轮对抗微调（forget 轮 = 实例级监督对比损失，温度 1.15；retain 轮 = CE）；retain batch 256 + 8 轮公榜最佳；forget 轮加 **CosineAnnealingLR**：公榜 0.084 → **0.091** | 458721 |
| 5th（458531） | 两路模型集成：(1) **Conv2D 权重整体转置**后重训 3 轮（等效于翻转输入、保特征）；(2) 伪标签微调（用重训模型的错误做伪标签）；组合 246+266 / 266+246 → 私榜 0.078518 / 0.075631；失败清单：class weights、LLRD/init-freeze、softmax/KL、**RelaxLoss、SCRUB**；自述"指标太严苛，光防 MIA 不够" | 458531 |
| 12th 公榜（458648） | Similarity-Based Sampling Bad Teaching：好教师（全模型）+ 坏教师（仅 retain 预训练）+ 学生 KL 对齐（retain→好、forget→坏）；retain 按与 forget 的相似度采样（α 比例）+ 加权遗忘 + "先破坏后重建"的批构造；**最终因超时未进最终榜** | 458648 |
| 赛事治理 | 不给积分/奖牌（50 票 / 34 评论）；公开 notebook 与官方 starter 高度雷同（23 票 / 8 评论）；提交成功但评分失败（14 票 / 12 评论）；"少 epoch 反而更好"（16 票 / 13 评论）；"一致性是关键"（14 票 / 9 评论）；指标复现帖（13 票） | 索引 |
| 9th（索引） | 不依赖 forget set 的方案拿到公榜第 3（11 票） | 主题索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 6th | 2nd | 5th | 12th（公榜） |
| --- | --- | --- | --- | --- |
| 核心机制 | 重置首末层 + KL 蒸馏 + 微调 | 打平 logits + 对抗微调 | 权重转置重训 + 伪标签 | 双教师 KL + 相似度采样 |
| 用 forget set？ | **不需要** | 需要（对抗轮） | 间接（伪标签） | 需要 |
| 关键超参 | 高温度、CosineAnnealing | 温度 1.15、batch 256、8 轮 | 3 轮重训、模型数配比 | α 采样比例、加权 W |
| 最好私榜 | 0.07831（前两类预热） | — | 0.078518 | 超时未上最终榜 |
| 对论文方法的态度 | 全部不如基线微调 | 借鉴 bad teaching 思路 | RelaxLoss/SCRUB 失败 | 改造 bad teaching |

### 共识 / 分歧 / 裁决
**共识一：本场指标严苛且离线复现困难，必须自建评测（12th 超时、6th/2nd/5th 的细微差异、社区帖；置信度中高）**
6th 的两版提交公榜几乎相同（0.08383 vs 0.08324）但私榜差 0.006；12th 公榜很高却因超时失去成绩；社区有"指标复现"专帖与"提交成功但评分失败"的长帖。**裁决**：先把官方 metric（含 MIA 部分）在本地复现，并用多次提交检查顺序稳定性，再做模型选择。置信度：中高。

**共识二：简单可控的"重置/蒸馏/微调"优于论文 SOTA 算法（6th、2nd、5th；置信度中高）**
6th 的一串对照实验显示 eu-k、cf-k、bad teaching、SCRUB 等都不优于基线微调；5th 也报告 RelaxLoss、SCRUB 无效；而 6th/2nd 的简单两阶段/三损失方案拿到前列。**裁决**：该赛道的公开方法在比赛指标下迁移性差，工程化的简单方案 + 充足调参更可靠。置信度：中高（多队独立报告）。

**共识三：小技巧收益明确——CosineAnnealingLR、高温度、少 epoch（2nd、6th、441318；置信度中高）**
2nd 在 forget 轮加 CosineAnnealingLR 直接 +0.007 公榜；两方都用高温度；社区热帖"少 epoch 反而更好"。**裁决**：本任务的训练动力学与传统分类不同，轮数与调度是首要超参。置信度：中高。

**分歧一：是否依赖 forget set（6th vs 2nd/12th；置信度中）**
6th 明确"方法不需要 forget set"，还能拿到私榜前列；2nd/12th 则围绕 forget 集设计对比损失/双教师。**裁决**：两条路线都能得分，但不能归因于某一方——评估指标与模型选择比方法族差异更大。置信度：中。

**事件：无积分奖牌 + 公榜同质化 + 超时风险（438567、442946、442093、458648；置信度中高）**
官方以"探索性强、风险高"为由不授积分/奖牌（50 票 / 34 评论）；社区观察到公开 notebook 与 starter 高度相似（23 票）；提交评分失败与超时案例多起，12th 因此丢分。**裁决**：Research 类比赛的参与成本与回报需提前评估；工程稳健性（超时、评分）与技术同等重要。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 6th 的重置首末层依据（余弦相似度图）与分数 | 自述 + 3 张图 | 中高 |
| 2nd 的对比损失设计与 +0.007 增益 | 自述 + 公式图（OCR 不全） | 中 |
| 5th 的转置重训 + 伪标签 + 失败清单 | 自述 + 开源 notebook | 中高 |
| 12th 的双教师机制与超时 | 自述 + 架构图 | 中 |
| "SOTA 算法未超基线" | 两队一致自述 | 中 |
| 无奖牌/同质化/超时事件 | 高票帖 + 官方帖 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st/3rd/4th 方案未收录；7th/9th 只有索引标题；
- 官方 metric 的精确公式未整理（仅能确认含 MIA 与 retain 性能）；
- 2nd 的公式图 OCR 缺失，温度/损失细节需回看原帖；
- 归档 8 图，本深读内嵌 3 张；
- **图证缺口**：无（8 张归档图充足）。

### 图证（KStarter 仓库内路径）
- ../../intel/neurips-2023-machine-unlearning/bodies/458740_img/04.png — 6th 的两阶段流程
- ../../intel/neurips-2023-machine-unlearning/bodies/458740_img/01.png — 层间权重余弦相似度
- ../../intel/neurips-2023-machine-unlearning/bodies/458648_img/01.png — 双教师 bad teaching 流程

### 出处
- 6th（13 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/458740
- 2nd（35 票 / 17 评论）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/458721
- 5th（30 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/458531
- 12th 公榜 / 相似度采样 bad teaching（14 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/458648
- 相关论文与代码合集（45 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/438660
- 无积分/奖牌争议（50 票 / 34 评论）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/438567
- 公开 notebook 同质化（23 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/442946
- 提交评分失败（14 票 / 12 评论）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/442093
- 少 epoch 更好（16 票 / 13 评论）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/441318
- 指标复现（13 票）：https://www.kaggle.com/competitions/neurips-2023-machine-unlearning/discussion/453735

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/neurips-2023-machine-unlearning/discussion/459200
- rank 4｜description：https://www.kaggle.com/c/neurips-2023-machine-unlearning/discussion/459334
- rank 5｜description：https://www.kaggle.com/c/neurips-2023-machine-unlearning/discussion/459148
- rank 8｜description：https://www.kaggle.com/c/neurips-2023-machine-unlearning/discussion/459095
- rank 9｜description：https://www.kaggle.com/c/neurips-2023-machine-unlearning/discussion/458715

---

## nfl-big-data-bowl-2023 — NFL Big Data Bowl 2023 轻量深读（Tier B）

> 主题 cv ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2023-01-09 ｜ Tier B ｜ 标签 cv,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2023.md
> 材料基础：`digests/nfl-big-data-bowl-2023.md`（6 篇正文：历届获奖 361175 / finalists 公告 382941 / 官方 demo 360659 / 选题清单 365497 / 官方欢迎 359079 / film review 362714；47 条主题索引）+ 0 张归档图

### 一句话重述
第五届 BDB，主题是**锋线球员（OL/DL）评估**：用 2021 赛季**第 1–8 周的 dropback pass plays** 追踪数据（snap 到出手）+ PFF 球探数据，讲清楚传球保护/冲传表现。赛道从两条扩到**三条**：Metric、Undergrad、以及新增的 **Coaching**；近 300 份提交、400+ 参与者创纪录，8 名 finalist 在印第安纳 Combine 现场决赛（额外 $20,000 奖金）。本场的高价值材料是**官方 demo（edge rusher get-off）+ 21 票选题清单 + 前两届获奖全名单**，基本把"怎么选题、怎么做图、评委爱看什么"都摊开了。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模 | **近 300 份提交 / 400+ 参与者**（analytics 赛记录）；**8 名 finalist**（Coaching 2 / Undergrad 2 / Metric 4）+ 9 个 HM；Combine 现场决赛、额外 **$20,000** 奖金 | 382941 |
| 数据 | 2021 赛季 Weeks 1–8、dropback pass plays；从 snap 到出手的球员追踪（位置/速度/加速度/方向）+ PFF scouting 字段 | 359079 |
| 官方 demo | Tom Bliss 的 edge rusher get-off 分析 notebook：数据探索、play 动画、基础图表——官方强调"这不是提交模板" | 360659 |
| 选题清单（21 票） | 进攻：锋线策略分类（Man Duel/Slide/Empty）、强弱侧判断、跑卫路线 vs 保护、姿势与内外侧、出手后站位、pre-snap→post-snap 保护指派变化、false start/开球时机、主客场 snap count；防守：识别 stunt/twist、pre-snap 冲传概率、吸引包夹的球员、blitz 策略、offside 率、主客场倾向 | 365497 |
| 领域活动 | 与两届超级碗冠军 Kevin Boothe 的 film review；新兵/OL-DL 技术视频与论文清单（14 票）；"linemen and the Matthews family" 故事帖 | 362714 / 359945 / 361504 |
| 争议/口径 | `pff_positionLinedUp` 含义（8 评论）、`pff_passCoverage*` 字段（5 评论）、screen pass 是否排除、frame 长度、周数据缺失、timestamp 修正；"bias concerns" 18 评论与"unfair competition" 公开信 12 评论 | 369849 / 373948 / 364365 / 359781 |
| 提交/规则 | 附录是否计分、GUI applet 是否可行、图像失效、外部/比赛影片可用性；有人遇到"evaluation system not configured" | 375499 / 370682 / 377798 / 376730 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | Metric 赛道 | Undergrad 赛道 | Coaching 赛道 |
| --- | --- | --- | --- |
| finalist 主题 | STRAIN（sacks/tackles/rushing aggression index）、IDPI 情境化冲传指标、球员影响分布、Completions Added through Pressure Suppression | 压力如何测量（Toronto）、空间生存概率（UChicago） | blitz 策略（使用数据决定）、xPassRush（pre-snap 识别冲传者） |
| 产出 | 新指标 + 验证 | 学术化分析 | 教练可用的战术洞察 |
| 评审口味 | 可解释、可复现的指标 | 方法严谨 | 战术落地性 |

### 共识 / 分歧 / 裁决
**共识一：选题先用"官方素材三件套"（360659 / 365497 / 382941；置信度高）**
官方 demo（get-off）给出数据操作与可视化范例；选题清单直接列了 20+ 个可做方向；历届获奖名单给出"什么样的故事能赢"。**裁决**：开局顺序 = 读数据字典 → 复现 demo → 从清单挑一个窄题（某位置 × 某战术）→ 对照往届获奖结构写报告。置信度：高。

**共识二：三赛道共享数据但评审口味不同（382941；置信度中高）**
Metric 要新指标，Coaching 要战术洞察，Undergrad 看学术规范；finalist 题目已验证这一点。**裁决**：先定赛道再定方法——同一份分析，Metric 版强调指标定义与稳健性，Coaching 版强调战术结论与可执行建议。置信度：中高。

**事件一：PFF 字段口径必须锁死（369849 / 373948 / 364365；置信度中高）**
`pff_positionLinedUp`、`pff_passCoverage*`、screen pass 是否排除等被反复提问。**裁决**：所有派生指标先写出"字段 → 官方定义 → 例外"的口径表；不确定的字段不要用于核心结论。置信度：中高。

**事件二：数据/参与公平性有争议（359200 / 366229 / 460361；置信度中）**
"bias concerns"（18 评论）与"不公平竞赛"公开信（12 评论）以及"追踪数据有限"帖说明数据范围（仅 Weeks 1–8）引发部分参与者不满。**裁决**：在报告里显式声明数据范围与局限；这是评审制比赛的加分项而非减分项。置信度：中。

**事件三：交付细节（附录/交互/图片）需要提前验证（375499 / 370682 / 377798；置信度中）**
附录是否计分、能否放 GUI、notebook 图片失效等都被问到。**裁决**：把正文控制在主指标上，交互/动画作为附件并提前渲染验证；提交前在 Kaggle 环境重跑一次。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 规模、赛道、finalist 与奖金 | 官方帖（382941） | 高 |
| 数据范围与主题 | 官方帖（359079） | 高 |
| 官方 demo 与选题清单 | 官方帖（360659 / 365497） | 高 |
| 历届获奖名单 | 社区整理（361175） | 中高（链接可查） |
| PFF 字段问题 | 多帖（369849 等） | 中（答复未归档） |
| 公平性争议 | 讨论帖（359200 / 366229） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2023 获奖作品正文未随归档保存（仅链接与公告）；
- PFF 字段官方答复与 screen pass 口径未归档；
- "bias concerns"/公平性公开信的官方回应未归档；
- 最终 8 名 finalist 的现场排名未归档；
- **图证缺口**：本场 0 张归档图（官方 demo 的 ExamplePlay.gif 未归档），已登记。

### 出处
- 官方欢迎（72 票 / 70 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/359079
- finalists 公告（18 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/382941
- 官方 demo notebook（18 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/360659
- 选题清单（21 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/365497
- 历届获奖方案（23 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/361175
- film review（25 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/362714
- NFL/ML 论文清单（14 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/359945
- bias concerns（-1 票 / 18 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2023/discussion/359200

---

## nfl-big-data-bowl-2024 — NFL Big Data Bowl 2024 轻量深读（Tier B）

> 主题 cv ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2024-01-08 ｜ Tier B ｜ 标签 cv,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2024.md
> 材料基础：`digests/nfl-big-data-bowl-2024.md`（6 篇正文：术语表 447174 / 擒抱技术 448833 / 进攻球员评估与 EPA 447660 / 生态工具与历史冠军 446946 / 赛后总结 468229 / 官方欢迎 446943；80 条主题索引）+ 1 张归档图

### 一句话重述
第六届 Big Data Bowl，主题是**擒抱（tackling）**：用 NGS 追踪数据 + tackles 数据研究"防守方如何把持球人放倒"。延续系列传统：**先补领域知识**（阵型/位置/统计口径/擒抱技术），再谈分析；同时本场给足了"指标体系"素材——nflWAR 论文的 EP/WP/EPA/WPA 建模、Next Gen Stats 的 xRY/RYOE、The Zoo 的"22 人相对位置+速度、不依赖人工特征"的经典冠军范式。评审由 NFL 各队分析部门打分，**分数不公开**，赛后只公布 finalist 与总结。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与赛道 | 第六届 BDB；**约 300 份提交（同比 +15%，创 analytics 赛记录）**；Metric / Undergrad / Coaching 约 **45 / 30 / 25** 分布；由 NFL 球队分析人员评审 | 468229 |
| 时间线 | 1/8 截止 → finalist 公告（2024-01，14 票 / 20 评论）→ 摘要称 finalist 预计 2 月初；**规则与最终分数不公开** | 472712 / 472752 |
| 术语与口径 | 阵型（Shotgun/Singleback/I/Empty/Pistol/Jumbo/Wildcat）、位置缩写、球衣号码规则、传球统计口径；擒抱类型（In Line / Open Field / Engaged / Last Chance）与 solo/assist/total 计数 | 447174 / 448833 |
| 指标体系 | nflWAR：多项式 logistic 估 EP → GAM 估 WP → 多水平模型算 WAR；传球拆"空中/接球后"分摊给传球者/接球者/防守；冲球拆 QB/非 QB；xRY、RYOE、RYOE/Att、ROE、首攻概率、达阵概率 | 447660 / 446946 |
| 历史范式 | The Zoo（BDB 2020 冠军）：**只用 22 名球员相对位置与速度、不用预造特征**，因此可迁移到任意 play/时刻 | 446946 |
| 数据质量问题 | "Is there a Data Discrepancy?"（14 票 / 6 评论）；preSnap 胜率列命名错位（447011）；部分 play 位置"滞后"；tackles 数据不一致；追踪数据缺失；passresult 缺失；ball_snap 事件缺失；gameId 2022091808 缺失；plays/tracking 不一致 | 447639 / 447011 / 448035 / 461347 / 451985 / 451804 / 452944 / 459352 / 460396 |
| 交付/合规 | 2000 词限制讨论；GIF/SVG 动画提交报错（多个帖）；外部数据（StatsBomb 公开仓库、All-22 影片）合法性被问；NFL Vision 新版公告；简历投递通道 | 464862 / 466521 / 450982 / 461515 / 470693 / 478371 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 领域口径线（447174 / 448833） | 指标体系线（447660 / 446946） | 数据工程线（多帖） |
| --- | --- | --- | --- |
| 内容 | 阵型/位置/擒抱技术/助攻口径 | EP→WP→EPA/WPA→WAR；xRY 家族 | 缺失值、命名错位、tracking 滞后 |
| 产出 | 能正确标注一次擒抱/一次错失 | 可解释的球员/战术价值 | 可信的分析底表 |
| 风险 | 口径理解错 → 结论错 | 直接回归"下一次得分"不稳 | 脏数据导致假结论 |

### 共识 / 分歧 / 裁决
**共识一：评审制分析赛先统一"统计口径"（447174 / 448833 / 447710；置信度高）**
什么算 solo/assist、什么算 missed tackle、play 何时算擒抱——这些定义直接决定标签质量；技术帖给出教练视角的四类擒抱与计数规则。**裁决**：开赛先写"口径备忘"（数据列 ↔ 官方定义 ↔ 例外），再建派生指标。置信度：高。

**共识二：EP/WP 类指标要按事件概率建模（447660；置信度中高）**
nflWAR 的做法是先多项 logistic 估各得分事件概率再求期望（EP），把 EP 作为 GAM 特征估 WP，再取前后差得 EPA/WPA；比"直接回归下一次得分"更稳、更可解释。**裁决**：做 play 估值时走"事件概率→期望→差分"链；传球/冲球按子模型拆分信用。置信度：中高。

**事件一：追踪数据必须先做一致性与缺失审计（447639 / 448035 / 451985 / 452944 / 459352；置信度中高）**
数据差异、位置滞后、缺失 tracking/ball_snap/整场数据等被反复报告。**裁决**：任何 play 级派生（速度、距离、相对位置）前，先做事件对齐与缺失图；把剔除规则写进 notebook。置信度：中高。

**事件二：公开生态（nflverse/cfbfastR/xRY）是低成本起点（446946；置信度中高）**
R 生态能直接取 play-by-play、EP 模型教程与可视化；Next Gen Stats 公开了 xRY/RYOE 的定义。**裁决**：先复现公开 EP 模型与 xRY 口径，再叠加追踪数据做增量。置信度：中高。

**事件三：交付格式是常见翻车点（464862 / 466521 / 466257 / 465620；置信度中）**
2000 词限制、GIF/SVG 嵌入、submission notebook 报错在这个社区赛里占据大量帖子。**裁决**：提前用最小 notebook 验证动画/图片渲染与提交流程；字数按最保守口径统计。置信度：中。

**分歧：外部数据与影片的合规边界（450982 / 461515；置信度中）**
StatsBomb 公开数据与 All-22 影片是否可用被公开询问，官方答复未归档。**裁决**：外部数据先用官方允许的公开来源（nflverse 等），影片只在明确允许时使用；有疑问赛前发帖确认。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 约 300 提交与 45/30/25 分布 | 官方总结帖（468229） | 高 |
| 术语/擒抱口径 | 高票社区整理（447174 / 448833） | 中高 |
| nflWAR 指标体系 | 论文引用 + 长帖（447660） | 高（论文可查） |
| The Zoo / xRY 范式 | 官方链接与历史帖（446946） | 中高 |
| 数据质量问题 | 多帖（447639 等） | 中高（现象密集） |
| 规则与分数不公开 | 官方帖（472752） | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 最终分数/规则说明不公开，获奖作品正文未归档；
- 数据差异与 tracking 滞后的官方修复结论未归档；
- 外部数据/影片合规边界无归档答复；
- 赛道（metric/undergrad/coaching）之间的评分差异未公开；
- **图证缺口**：无（1 张图，已内嵌）。

### 图证（KStarter 仓库内路径）
- ../../intel/nfl-big-data-bowl-2024/bodies/448833_img/01.webp — Types of Tackles

### 出处
- 官方欢迎（19 票 / 18 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/446943
- 术语表（20 票 / 3 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/447174
- 擒抱技术与计数口径（19 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/448833
- 进攻球员评估与 EPA（16 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/447660
- 生态工具与历史冠军（17 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/446946
- 赛后总结（16 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/468229
- finalist 公告（14 票 / 20 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/472712
- 规则与分数不公开（3 票 / 3 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/472752
- 数据差异（14 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/discussion/447639

---

## nfl-big-data-bowl-2025 — NFL Big Data Bowl 2025 轻量深读（Tier B）

> 主题 cv ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2025-01-06 ｜ Tier B ｜ 标签 cv,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2025.md
> 材料基础：`digests/nfl-big-data-bowl-2025.md`（6 篇正文：上手资源 539795 / 历届方案 539785 / 官方欢迎与建议 539921 / 直播 539775 / 赛季数据疑问 539822 / 获奖公布 560137；72 条主题索引）+ 0 张归档图

### 一句话重述
第七届 Big Data Bowl，主题是 **pre-snap（开球前）**：用追踪 + 事件数据研究开球前的阵型、运动/换位（motion/shift）、audible 等如何预示开球后的结果。官方建议非常直接：**别试图一次解决整个橄榄球**——选一个小切口（一个位置/一类战术/一种阵型）做深；足球语境 + 编码能力的组合最容易出成果。本场数据比 2024 版**新增 66 个特征、删除 7 个特征**，讨论区大量问题围绕 `line_set`/`motionSinceLineset`/`inMotionAtBallSnap` 等新事件口径；另有"notebook spam"与提交格式/字数限制等社区摩擦。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 赛制 | 第七届年度赛；pre-snap 主题；无排行榜/评审制；获奖名单以附件公布；截止 2025-01-06 | 539921 / 560137 |
| 官方三建议 | ① 保持简单，选小切口（位置/战术/体系）② 足球语境越多越好 ③ 有足球背景的人 + 会编码的人组队成功率更高 | 539921 |
| 数据变化 | 2025 vs 2024：**新增 66 个特征、删除 7 个**；unique seasons 仍是 2022（数据滞后问题被专帖吐槽） | 539787 / 539822 |
| 新手口径问题 | `line_set` 事件（7 评论）；motionSinceLineset vs inMotionAtBallSnap（多帖）；pre-snap adjustments/audibles；passers other than QB；PFF 数据问题；球员朝向测量；absoluteYardlineNumber >100；WinProbabilityAdded；负 expectedPoints | 541143 / 548627 / 541223 / 543658 / 541889 / 552655 / 548437 / 552417 / 541000 |
| 数据质量 | football tracking inaccuracies；"Where is the football in this play?"；data disagreement between inputs；plays.csv issue；missing birthdays 修正；特勤组识别口径 | 551782 / 551328 / 543709 / 543119 / 546315 / 542111 |
| 社区摩擦 | "Notebook spam is unreal"（8 票 / 9 评论）；"Ideally it's useless"（4 票 / 7 评论）；现场直播/连麦复盘；青少年参赛资格；coaching track 提交格式 8 评论；2000 词附录是否计入 | 540670 / 552318 / 539775 / 541080 / 548189 / 555070 |
| 结果 | 赛后"提交评审中"（6 票 / 8 评论）→ 获奖公布（9 票 / 8 评论）；Feedback on Submissions 3 票 | 555499 / 560137 / 568911 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 官方建议路线 | 社区上手动线 | 数据现实 |
| --- | --- | --- | --- |
| 选题 | 一个位置/战术/体系做深 | 复用往届 EDA/动画 notebook | pre-snap 新事件口径不熟 |
| 交付 | 2000 词 + 图表/动画，评审可读 | notebook 直接改写成报告 | 格式/字数规则细节多 |
| 价值 | 足球语境 + 编码结合 | 追踪可视化/派生指标 | 球轨迹与部分事件不可靠 |

### 共识 / 分歧 / 裁决
**共识一：小切口 + 足球语境是评审制 BDB 的长期制胜法（539921；置信度高）**
官方明确"别一次解决整个运动"，并强调足球背景与编码能力的组合。**裁决**：选题限定到"某位置在某类阵型下的某一步运动"，用领域假设驱动指标设计；报告按"问题—证据—结论—对球队的建议"组织。置信度：高。

**事件一：新特征/新事件口径是本届主场（539787 / 541143 / 548627 / 541223；置信度中高）**
66 个新特征 + pre-snap 事件（line-set、motion、audible）需要先做数据字典与口径统一，否则派生特征会错。**裁决**：先写"事件时间线"（line_set → ball_snap 等）并可视化验证，再建运动/阵型特征。置信度：中高。

**事件二：追踪数据质量仍需审计（551782 / 551328 / 543709 / 543119；置信度中高）**
球的位置/轨迹不准、输入数据互相矛盾、plays.csv 有问题被逐帖报告。**裁决**：任何涉及球位置/速度的结论先做一致性抽检；必要时以事件数据为准而不是球轨迹。置信度：中高。

**事件三：提交格式与赛道规则是常见淘汰点（548189 / 555070 / 555197 / 555366；置信度中高）**
coaching track 的图表/幻灯片规则、2000 词附录计法、提交失败等被反复询问。**裁决**：把"格式合规"当独立 checklist；提前用草稿提交验证流程，别在截止前两小时试。置信度：中高。

**分歧：公开 notebook 的价值与噪声（540670 / 554993 / 552318；置信度中）**
有人抱怨 notebook spam 与低质公开作品，也有人做"最有竞争力 notebook"盘点与直播复盘。**裁决**：以数据问题与领域假设为筛选标准，不追热度；公开作品用于对照口径而非直接套用。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 官方三建议与赛制 | 官方帖（539921） | 高 |
| 66 新增 / 7 删除特征 | 社区对比帖（539787） | 中高（可核对） |
| 新事件口径问题 | 多帖（541143 / 548627 等） | 中高 |
| 数据质量个案 | 多帖（551782 / 551328 等） | 中 |
| 获奖方案 | 仅公告附件（560137） | 低（正文未归档） |
| 社区摩擦 | 讨论帖（540670 / 552318） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 获奖作品正文与最终评审细节未归档（560137 只有附件公告）；
- 66 个新特征的官方文档更新说明未归档；
- 球追踪不准确的官方结论/修复未归档；
- 各赛道（metric/undergrad/coaching）的评审权重未公开；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- 官方欢迎与建议（17 票 / 17 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/539921
- 上手资源汇编（22 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/539795
- 历届方案索引（9 票 / 1 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/539785
- 2025 vs 2024 特征变化（6 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/539787
- 赛季数据疑问（14 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/539822
- notebook spam（8 票 / 9 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/540670
- coaching track 提交格式（0 票 / 8 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/548189
- 获奖公布（9 票 / 8 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/discussion/560137

---

## nfl-big-data-bowl-2026-analytics — NFL Big Data Bowl 2026 – Analytics Track 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标  ｜ 队伍 277 ｜ 截止 2025-12-17 ｜ Tier B ｜ 标签 cv,review,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2026-analytics.md
> 材料基础：`digests/nfl-big-data-bowl-2026-analytics.md`（6 篇正文：起步与 Discord 609278 / 2025 冠军 AMA 与补充数据 614950 / 官方欢迎 609370 / 结果延期询问 670213 / 编辑已提交 writeup 663242 / 获奖公布 670745；41 条主题索引）+ 0 张归档图

### 一句话重述
第八届 BDB 的 Analytics 赛道：主题是**球在空中这段时间里球员怎么移动**（从 snap 到出手决策的传球进攻演化），官方希望产出新的进攻/防守球员指标。系列赛的"就业管线"在本场被再次验证：2025 冠军 Vishakh Sandwar 借比赛进入 SumerSports，并**开源生产数据补充（帧级防守覆盖 + 球员级覆盖细节）与 man/zone 分类的 Transformer 代码**，成为本届最热的社区资源。与此同时，讨论区显示数据口径问题（ball_land、player_to_predict、frame、朝向、加速度）与提交流程（"evaluation system not configured"、编辑 writeup）是主要摩擦点。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与机制 | **277 队**；Analytics 赛道（评审制，另有 Broadcast Visualization 赛道）；截止 2025-12-17；原定 2026-01-20 出结果，1/26 仍在等（16 票帖） | 609370 / 670213 / 索引 |
| 主题 | 球在空中阶段的球员移动；官方希望形成新的进攻/防守球员统计，理解"从 snap 到出手决策"的传球演化；强调 BDB→体育分析就业管线 | 609370 |
| 冠军生态资源 | 2025 冠军 @VishakhSandwar 的开源补充：**帧级 coverage scheme + 球员级 coverage 细节**数据集；基于 Udit Ranasaria & Pavel Vabishchevich 的 Transformer 改造成 **man vs zone** 分类 notebook；SumerSports 博客；作者在讨论区持续 AMA | 614950 |
| 社区选题讨论 | "novel data analytics you can do"（4 票）；"Describe a Play. Find Similar Ones."（4 票）；Safety Range Visualizer（2 票）；Broadcast Visualization 提交讨论；用 Gemini 3 做可视化（1 帖） | 索引 |
| 数据口径问题 | `ball_land` 不一致（4 评论）；`player_to_predict` 澄清；每 play 球员数；`frame_id`；朝向；加速度值；字段名；dropback 距离；球落点数据；team coverage type；data subset/requirements/outside data | 610834 / 613454 / 612717 / 614459 / 613468 / 657011 / 610026 / 639412 / 656536 / 656945 / 651738 |
| 提交/资格摩擦 | "Cannot submit – evaluation system has not been configured"（3 评论）；编辑已提交 writeup（663242）；notebook 提交与上传问题；非美学生资格；2027 预告 | 663170 / 663242 / 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 官方期待 | 社区提供 | 风险 |
| --- | --- | --- | --- |
| 选题 | 空中阶段的新球员指标 | 相似 play 检索、安全范围可视化、覆盖分类 | 与 2024/2025 主题重复 |
| 数据 | NFL 追踪/事件数据 | 2025 冠军的 coverage 补充数据 | 字段口径不一致 |
| 交付 | Analytics writeup + 图表 | 开源 notebook/Transformer 基线 | 提交系统与资格问题 |
| 回报 | 奖项 + 就业管线 | AMA + 博客 + 开源 | 结果周期长 |

### 共识 / 分歧 / 裁决
**共识一：系列主题逐年收窄，复用公开生态是最快起手（609370 / 614950 / 609278；置信度中高）**
2024 擒抱 → 2025 pre-snap → 2026 球在空中；冠军补充数据与开源模型直接可用。**裁决**：先读近三届主题与往届方案，再决定"新指标/新可视化"切口；优先复用公开 coverage/Transformer 基线。置信度：中高。

**事件一：数据字段口径要在建模前锁死（610834 / 613454 / 614459 / 613468；置信度中高）**
ball_land 不一致、player_to_predict/frame/orientation/acceleration 等被逐条提问。**裁决**：开赛先做字段字典与异常抽检（尤其球落点与帧对齐），把口径写进 notebook。置信度：中高。

**事件二：提交流程与赛道规则要先验证（663170 / 663242 / 662658；置信度中高）**
有人遇到"未配置评测系统"、writeup 编辑方式不明。**裁决**：提前用草稿跑通提交链路，确认赛道（Analytics vs Broadcast Visualization）与编辑规则；留出结果延迟的预期。置信度：中高。

**事件三：就业与传播价值是这类赛的重要回报（609370 / 614950；置信度中高）**
官方直言"简历管道很深"，2025 冠军进入 SumerSports 并反哺社区。**裁决**：把 writeup 当作品集（可公开、可复现、有业务结论），赛后继续运营开源产物。置信度：中高。

**事件四：结果公布经常延期（670213 / 670745；置信度中）**
原定 1/20，1/26 仍在询问，最终获奖以附件公布。**裁决**：不要把结果时间写进求职/发表计划；提交后保持 notebook 可访问。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 主题、赛道与就业定位 | 官方帖（609370） | 高 |
| 冠军补充数据与开源模型 | 冠军自述 + 链接（614950） | 高（资源可查） |
| 结果延期 | 讨论帖（670213） | 中高 |
| 数据口径问题 | 多帖（610834 等） | 中高 |
| 提交系统问题 | 个案帖（663170） | 中低 |
| 获奖名单 | 附件公告（670745） | 中（无正文） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 获奖 writeup 正文与评审细节未归档；
- Analytics 与 Broadcast Visualization 两赛道的评分权重未公开；
- ball_land 等数据不一致的官方结论未归档；
- 2027 预告内容未归档；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- 官方欢迎（8 票 / 12 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/609370
- 2025 冠军 AMA 与补充数据（5 票 / 1 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/614950
- 结果延期询问（16 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/670213
- 获奖公布（8 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/670745
- 编辑已提交 writeup（0 票 / 1 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/663242
- ball_land 不一致（1 票 / 4 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/610834
- 提交系统未配置（0 票 / 3 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-analytics/discussion/663170

---

## nfl-big-data-bowl-2026-prediction — NFL Big Data Bowl 2026 - Prediction 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 NFL_2025 ｜ 队伍 1899 ｜ 截止 2026-01-06 ｜ Tier B ｜ 标签 cv,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2026-prediction.md
> 材料基础：`digests/nfl-big-data-bowl-2026-prediction.md`（6 篇正文：1st 651604 / 3rd 668048 / 4th-5th 651814 / 5th 1059 行处 / 33rd 651530；80 条主题索引）+ 7 张图

### 一句话重述
给定一次传球进攻的追踪数据，预测指定球员未来 48 帧的位置。真正的考点是**"小数据下的增强 + 损失函数设计 + 时空架构"**：1st 只用竞赛数据就夺冠（靠**高斯 NLL 损失**与强增强）；3rd 则把官方允许的 2018 追踪数据（NFL BDB 2021）按"事件链"重构成同构任务做预训练，再用**双路径（球员交互 + 个体运动）+ 时空注意力**微调。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（651604） | **只用竞赛数据**（数据集小 → 必须强增强 + 好损失 + 好架构）；特征：**传球前 20 帧动态特征**（每帧 10 维：x/y、sin(o)/cos(o)、sin(dir)·s/cos(dir)·s、相对落点的 x/y、相对接球手的 x/y）+ **12 维静态特征**（player_role 的 4 维 one-hot、预测帧数、输入帧数、传球者末帧坐标、落点坐标、球员末帧坐标）；**目标 = 相对最后一帧输入的位移 (Δx, Δy)**，最终轨迹=末帧坐标+预测位移；解码器：(256, player) → 1536 → reshape (32, 48) → 多个 Conv1d(k=3) → 投影出 2（xy）+ 4（辅助项）；验证：**按 game_id 分组的 5 折 × 3 次不同切分**；RAdam + **EMA(0.9995)**、210 epoch、每 6 epoch 评估；损失：**GaussianNLLLoss（同时预测均值与方差，方差用 `softplus(var)+1e-3` 约束为正）**——自动降低高方差样本的权重，优于 SmoothL1，且"逐帧加权无益"；辅助损失来自预测 xy 的速度（一阶差分）与加速度（二阶差分） | 651604 |
| 3rd（668048） | 完整工程：① **特征**：原始量（x/y/s/a/dir/o/落点/num_frames_output）+ 速度分解（velocity_x/y）+ 运动方向（angle_to_ball、dir_rad 等）；② **增强**：**沿中场线的水平翻转**、**180° 旋转**（进攻/防守标签不变、路线对称）、**随机球员丢弃**（从首帧统计有效球员，随机把 1–min(5, 有效−4) 名球员的 36 帧张量清零并置 mask=False）、**球内随机重排**（打破"slot 0=离 QB 最近"的偏置，迫使模型依赖几何特征）、**随机输入裁剪**（若 seq_len>12，从头部丢 2–6 帧、保留至少 7 帧尾帧后补零）；验证集禁用全部增强；③ **额外数据**：官方允许的 2018 追踪数据，按事件链 `ball_snap → pass_forward → pass_arrived` 过滤，输入=ball_snap 到 pass_forward、输出=pass_forward+1 到 pass_arrived，落点取 `event=pass_arrived & team=football` 的行，角色=QB 为传球者、接球手=pass_arrived 时离落点最近的主队进攻球员；④ **两阶段训练**：先用"小而可信"的特征集在 2018+2026 数据上预训练（离线验证 0.62–0.68），再**加一个小线性 bridge 层**加载权重、用完整特征集微调；⑤ **架构（图 1）**：双路径——**Player Interaction Path**（前 13 特征 → 投影 13→64 → 2 层 Transformer → 聚合）+ **Main Processing Path**（13→384 + 额外 26→384 → 拼接 → 时间位置编码 + 带 mask 的稀疏球员位置编码）→ **时空编码器（STEncoderBlock×2，时间注意力+空间注意力）** → **四个多任务头**（未来轨迹主输出 + 帧到帧预测 + 终点预测 + 全时序预测）；⑥ 训练细节：**所有模块 Dropout=0**（纯回归里 dropout 有害）、**宽而浅（hidden 384×2）优于窄而深（128×6）**、主损失用带**时间衰减权重 `e^(−0.03t)`** 的 TemporalHuber + 速度平滑项；另有 TTA 与集成章节、"什么没 help"清单 | 668048 |
| 社区/事件 | "**Model architectures**"（57 票 / 57 评论）、"**Online training / Structural data leakage**"（54 票 / 18 评论）——在线评测与结构性泄漏是全场焦点、"可视化 play 的代码"（45 票）、"防守方 player_to_predict 怎么选"（26 票）、"提交一度被禁用，后启用新评测 API"（36 票 / 49 评论）、"榜单最终确定"（25 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd |
| --- | --- | --- |
| 数据 | **只用竞赛数据** | 竞赛 + 2018 追踪数据（事件链重构） |
| 输入/目标 | 传球前 20 帧（10 维/帧）+12 静态维；目标=末帧位移 | 36 帧 ×22 球员 ×26 特征；多任务头 |
| 架构 | (256,player)→1536→(32,48)→Conv1d→2+4 输出 | **双路径 + 时空注意力 + 4 个输出头** |
| 损失 | **GaussianNLL（均值+方差）** + 速度/加速度辅助 | TemporalHuber（时间衰减 e^(−0.03t)）+ 速度平滑 |
| 增强 | 强增强（细节见其训练 notebook） | 翻转/旋转/球员丢弃/重排/裁剪 |
| 正则 | EMA 0.9995 | **Dropout=0、宽浅结构** |

### 共识 / 分歧 / 裁决
**共识一：损失函数是预测型赛的关键杠杆（1st/3rd）**
1st 用 **GaussianNLL**（同时学均值与方差、自动降权高方差样本）明确优于 SmoothL1；3rd 用带时间衰减的 TemporalHuber + 速度平滑。**裁决**：轨迹预测的误差分布异质（不同球员/时刻的确定性不同），"学不确定性并降权"或"按时间衰减加权"是比纯 L2 更合适的归纳偏置。置信度：高（1st 有对照）。

**共识二：小数据赛靠增强与外部同构数据（1st/3rd）**
1st 只用竞赛数据但强调"必须强增强"；3rd 用官方 2018 数据经**事件链重构**成同构任务并两阶段预训练（外加 small bridge 层适配）。**裁决**：先做"事件语义对齐"再谈迁移；bridge 层是低成本的特征空间重映射。置信度：中高。

**共识三：时空结构要显式建模（3rd）**
3rd 的双路径（球员交互 + 个体运动）+ 分离的**时间与球员位置编码** + 带 mask 的变长球员处理 + 时空注意力。**裁决**：多智能体轨迹预测的标准配方是"交互图/注意力 + 个体编码 + 位置/时间编码 + 掩码处理变长"。置信度：中高。

**分歧一：用不用外部（2018）数据**
1st 完全不用仍夺冠；3rd 用 2018 数据预训练。**裁决**：只要事件定义能对齐，外部同源数据可显著加速收敛；但冠军证明它不是必需。置信度：中。

**事件：在线评测与结构性泄漏（54 票帖）**
比赛改用了在线评测 API（可对新赛季比赛提交），社区专门讨论"在线训练/结构性数据泄漏"；提交一度被禁用后重启（36 票帖）。**裁决**：当评测是"在线滚动"时，要审计"输入里是否包含未来信息"（如 `num_frames_output`、落点坐标是否在推理时可得）；这类结构性泄漏是本赛的最大争议点。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的 GaussianNLL 与特征/训练细节 | 自述 + 公开 notebook/训练代码 | 高 |
| 3rd 的完整管线（增强/预训练/双路径/多任务） | 自述 + 架构图 + 图 | 高 |
| 在线评测与结构性泄漏 | 高票讨论（54 票） | 中高 |
| 33rd 的 Transformer + 增强技巧 | 自述（32 票） | 中 |
| 榜单/评测 API 变更 | 官方帖 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/4th（公榜第 5）/5th 的方案未细读；"Model architectures"讨论帖（57 票 / 57 评论）未细读；
- 1st 的"强增强"具体清单未在 write-up 展开（在训练 notebook 中）；
- 结构性泄漏争议无官方结论；
- 归档 7 图：3rd 的完整架构图（图 1）与 1st 的特征/掩码图为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/nfl-big-data-bowl-2026-prediction/bodies/668048_img/01.png — 3rd 的双路径时空模型

### 出处
- 1st（651604）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/651604
- 3rd（45 票）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/668048
- 4th/5th（43 票）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/651814
- 33rd（32 票）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/651530
- Model architectures（57 票 / 57 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/610240
- 在线训练/结构性泄漏（54 票）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction/discussion/612263

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/public-3rd-solution
- rank 2｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/2nd-place-solution
- rank 3｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/3rd-place-solution
- rank 5｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/5th-place-solution
- rank 19｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/th-place-solution
- rank 23｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/gru-solution
- rank 24｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/public-23rd-solution-data-augmentation
- rank 33｜description：https://www.kaggle.com/c/nfl-big-data-bowl-2026-prediction/writeups/relembedding-architecture-and-chiral-augmentation

---

## nfl-health-and-safety-helmet-assignment — NFL Helmet Assignment 深读：检测→几何映射→配准→跟踪四段式

> 主题 cv ｜ 类别 Featured ｜ 指标 NFL Helmet Identification ｜ 队伍 825 ｜ 截止 2021-11-02 ｜ Tier A ｜ 标签 cv,science,medical,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-health-and-safety-helmet-assignment.md
> 材料基础：`digests/nfl-health-and-safety-helmet-assignment.md`（6 篇：1st 327 票/欢迎 86/2nd 76/9th 64/10th 61/上届冠军索引 59；80 条讨论索引）+ 10 张图（可用 5：284940×3 / 284945×1 / 285112×6；1st 图未入库）

### 一句话重述
题面是"从比赛转播视频中检测头盔并把它分配到官方追踪数据里的具体球员"，实际被考的是**几何配准 + 跟踪工程**：
1. **检测只是入口**：主办方 baseline 检测会漏掉冲撞中的头盔——9th 用 YOLOv5x 修复，实测 +0.057；2nd 把小头盔上采样到 1664 训练；1st 用两阶段"先预测平均头盔尺寸→重采样→高分辨检测"把多尺度问题变成固定尺度问题。
2. **图像→2D 地图/坐标系 + 点集配准是主战场**：1st 用 U-Net 输出鸟瞰坐标（bottleneck 出全局位置、decoder 出残差、bbox attention），再用 **ICP 解 4 个参数**（xy 平移/旋转/缩放）；2nd 用**地面线**做解析几何变换（宽高比/梯形校正/旋转）；9th 用 **shape context** 描述子 + Hungarian + `findHomography`（LMEDS 修错配）迭代；10th 直接回归 **x/y mask**。
3. **辅助特征显著提升匹配**：球队分类（1st 的相似矩阵 ~97%、2nd 的 2 阶段 K-means 97→98%）、球员**朝向**预测、**头盔-传感器间隙**预测（站立 vs 蹲/倒地导致框偏移）——都直接进距离矩阵。
4. **跟踪是第二大增益**：跨帧累积与再分配把单帧噪声抹平（10th 的 CV 0.7→0.9；1st 的 IoU 跟踪按频率+置信+帧距加权重分配；9th 的 DeepSORT 票选标签）。
5. **集合要作用在"分配矩阵"层**：1st 把多模型/多帧的球员-分配矩阵加权平均后走 Hungarian（优于 box-level WBF），保证一一对应约束。
6. **速度是隐藏约束**：1st 强调"只用 `helmets.csv` 做映射与配准就有 ~0.8，且 GPU >10 帧/秒"——代码赛的双约束（精度+运行时间）要在架构期就设计。
一句话：**这是一场"配准 + 跟踪"的转播视频追踪赛**——检测决定下限，几何映射/配准与跨帧一致性决定名次。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 1st 模块与基线 | 6 模块；仅 `helmets.csv` 的映射+配准 ≈ **0.8**；GPU **>10 帧/秒** | 1st |
| 1st 球队分类 | 相似矩阵（同队/不同队）；ArcFace+伪标；验证 ~**97%** | 1st |
| 1st 集合 | 4 检测器；WBF 作用在球员-分配矩阵（加权平均+Hungarian） | 1st |
| 2nd 检测参数 | YOLOv5；1280→**1664** 上采样；仅用补充照片训练 | 2nd |
| 2nd 球队聚类 | 2 阶段 K-means（20 代表色→直方图）：**97% → 98%**（跟踪后处理） | 2nd |
| 2nd 辅助模型 | CenterNet 预测朝向 + 头盔-传感器 gap（站立/蹲/倒地修正） | 2nd |
| 9th 检测增益 | YOLO 版 vs baseline 晚提交：私 0.803/公 0.841，**+0.057** | 9th |
| 9th shape context | 旋转搜索 [0,2π] 步长 π/500；缩放 {0.5,1.25,3}；前 **60 帧**选最优 homography；ignore 数按代价改善 >10 自适应 | 9th |
| 9th DeepSORT | MAX_DIST 0.2874、MIN_CONF 0.4858、NMS 0.4397、MAX_IOU 0.7321、MAX_AGE 2、N_INIT 1、NN_BUDGET 30 | 9th |
| 10th 回归网 | EffNetB0+UNet；输入 2×256×256；输出 x/y 双通道；L1 仅在 tracking 点 + 分割辅助 | 10th |
| 10th 跟踪增益 | CV 0.7 → **0.9**（DeepSORT+SiamRPN）；公 0.85/私 0.86 | 10th |
| 上届共性 | 两阶段（2D 检测→3D 分类）；EffDet/YOLO；部分用追踪数据 | 263991 |
| 赛事 | 825 队；NFL Helmet Identification；80 帖 | 元数据 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 9th | 10th |
| --- | --- | --- | --- | --- |
| 检测 | 两阶段（尺寸归一→高分辨）4 检测器集成 | YOLOv5（补充照片，1664 上采样小头盔） | YOLOv5x（修 impact 漏检，+0.057） | YOLOv5（公共 notebook 优化） |
| 图像→坐标 | U-Net 鸟瞰图（全局+残差+attention） | 地面线解析变换（宽高比/梯形/旋转） | shape context + homography（LMEDS→ICP） | 回归 mask（x/y 通道） |
| 配准 | **ICP 4 参数**（平移/旋转/缩放）最小二乘 | 线性分配 + 候选裁剪（矩形切边界球员取最小距离） | Hungarian + findHomography 迭代（前 60 帧选优） | L1 回归（只在追踪点） |
| 辅助特征 | 球队相似矩阵（ArcFace+伪标 ~97%） | **球队聚类 + 朝向 + 头盔-传感器 gap** | 无（假阳性零行 + 自适应 ignore） | 分割辅助通道 |
| 跟踪 | IoU tracker（频率/置信/帧距加权） | SORT + 颜色阶跃特征 | DeepSORT 票选标签迭代 | DeepSORT + SiamRPN |
| 集合 | **分配矩阵 WBF** + Hungarian | — | 多帧 homography 选优 | — |
| 成绩 | 仅 helmets.csv 映射 ~0.8；>10fps GPU | — | YOLO 版 vs baseline 私 0.803/0.841（+0.057） | CV 0.7→**0.9**、公 0.85/私 0.86 |
| 失败清单 | —（图未入库） | — | FairMOT/ByteTrack/Tracktor++、YOLOX、运动数据、相机矩阵（局部极小） | — |

### 共识 / 分歧 / 裁决
**共识一：检测是入口，漏检必须修（1st/2nd/9th/10th）**
9th：baseline 漏掉冲撞中的头盔 → YOLOv5x 修复 **+0.057**；
2nd：小头盔检测差 → 上采样 1280→1664 训练；
1st：两阶段尺寸归一化（固定尺度目标更易检测）；
10th：直接用公共 YOLO 管线。

**裁决**：检测提升直接转化为分配分——**分配指标对漏检/假阳性都敏感**，检测质量与配准质量同等重要。置信度：高。

**共识二：几何映射/配准是主战场，四条路线都有效（4/4）**
1st：学习型 U-Net 鸟瞰 + ICP；2nd：地面线解析几何；9th：shape context+homography；10th：回归 mask。

**裁决**：问题本质是"图像点集 ↔ 已知追踪点集"的 2D 变换；**解析、点集配准、学习回归三类方法没有绝对优劣**，关键是鲁棒处理（场边人员/漏检/假阳性）。置信度：高。

**共识三：辅助特征（球队/朝向/gap）显著提升匹配（1st/2nd）**
2nd：2 阶段 K-means 球队聚类 97%→98%（跟踪一致性后处理）；朝向与 gap 模型直接进距离；1st：球队相似矩阵（ArcFace+伪标）参与配准。

**裁决**：配准的距离矩阵需要"同一人"的判别特征；颜色（队伍）排除跨队、朝向/gap 修正身体-头盔偏移。置信度：中高。

**共识四：跟踪与跨帧再分配是第二大增益（1st/2nd/9th/10th）**
10th：CV 0.7 → 0.9（DeepSORT+SiamRPN）；
1st：IoU 跟踪 + 频率/置信/帧距加权重分配；
9th：DeepSORT 票选标签迭代；
2nd：SORT + 阶跃颜色特征。

**裁决**：单帧分配的噪声由轨迹一致性抹平；**跟踪把"帧级匹配"升级为"身份级匹配"**。置信度：高。

**分歧一：相机/几何模型的显式程度**
9th：显式相机矩阵优化**失败**（局部极小，sideliner 多的视频更严重）→ 改 shape context；
2nd：用地面线做解析变换成功；
1st：完全数据驱动（CNN 鸟瞰图）。

**裁决**：复杂场景下显式相机模型脆弱；**鲁棒点集配准（LMEDS/shape context）或数据驱动映射更稳**。置信度：中高（9th 的对照 + 多路线成功）。

**分歧二：集合/跟踪的作用位置**
1st：在**分配矩阵**上做 WBF（优于对 boxes 做 WBF）；
9th/10th：DeepSORT 轨迹层；
2nd：SORT 轨迹层。

**裁决**：融合应作用在"球员-帧分配/身份"这一语义层，而不是原始检测框——保证一一对应约束（Hungarian）不被破坏。置信度：中高。

**分歧三：速度约束的实现**
1st：>10fps GPU，只用 helmets.csv 映射即 ~0.8；
10th：重跟踪（SiamRPN）也达标。

**裁决**：代码赛要在设计期平衡精度/运行时间；**"映射+配准"模块单独就是强基线**（可以脱离昂贵检测器先跑通）。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 六模块与 0.8/10fps | 自述 + 公开 inference 代码（图未入库） | 中高 |
| 9th YOLO +0.057 与 shape context 全流程 | 自述 + 3 张图 | 高 |
| 2nd 聚类/朝向/gap/地面线 | 自述 + 6 张图 | 高 |
| 10th CV 0.7→0.9 | 自述 + 架构图 | 中高 |
| 上届共性（2 阶段） | 社区索引帖（链接） | 中 |
| 1st/2nd 的"失败清单" | 未给出（1st 图未入库） | 低（缺口） |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **3rd/4th/5th 方案未收录**：3rd 的标题（YOLOv5+DeepSort+ICP+Hungarian）与 1st/9th 高度同构，缺正文无法三向对照。
2. **1st 的 6 张图（管线/消融）未入库**：其"WBF on assignment matrix"的消融数字缺失。
3. 2020 NFL Impact Detection 前 10 方案链接未展开——系列方法考古不完整。
4. 2nd 的失败清单未给出（只有成功项）。

**失败学（跨队合集）**

- 9th：FairMOT、ByteTrack、Tracktor++、YOLOX detector、速度/加速度/朝向数据、Jersey number（未尝试）、相机矩阵优化（局部极小）；yolo 训练无验证集。
- 1st/2nd/10th：未列出（缺口）。

### 出处
- 1st（327 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/284975
- 欢迎帖（86 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/263939
- 2nd（76 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/285112
- 9th（64 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/284940
- 10th（61 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/284945
- 上届冠军索引（59 票）：https://www.kaggle.com/competitions/nfl-health-and-safety-helmet-assignment/discussion/263991
- 缺口登记：3rd(285076)、4th(285007)、5th(285286) 未收录正文；1st 的 6 张图未入库

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285076
- rank 4｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285007
- rank 5｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285286
- rank 11｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285156
- rank 21｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285065
- rank 22｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285179
- rank 23｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285285
- rank 25｜description：https://www.kaggle.com/c/nfl-health-and-safety-helmet-assignment/discussion/285153

---

## nfl-player-contact-detection — NFL Player Contact Detection 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 Matthews correlation coefficient ｜ 队伍 939 ｜ 截止 2023-03-01 ｜ Tier B ｜ 标签 cv,detection,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-player-contact-detection.md
> 材料基础：`digests/nfl-player-contact-detection.md`（6 篇正文：2nd Hydrogen 391740 / 6th TK 391620 / 1st 391635 / 14th 391609 / 往届索引 370685 / 4th K_mat 391719；80 条主题索引）+ 8 张图

### 一句话重述
从端区+边线视频与追踪数据判断"球员-球员（PP）/球员-地面（PG）接触"（MCC）。真正考的是**视频时序表示 + 追踪特征编码进 CNN + 邻域时序后处理**；测试只有 61 个 play，验证要按 game_key 分组。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st | 三段式：弱 XGB 去易负样本（CV≈0.72）→ **resnet50-irCSN**（mmaction2 动作识别）→ XGB 后处理；PP 用 endzone+sideline+**追踪画成图像**（18 帧上限），PG 不用追踪（23 帧）；头盔头圈标记（保持 3 通道）；1 epoch 训练+4 seed 全量；后处理用邻域概率：PP ±10 → **+0.005 CV**，PG ±15（含 pre-xgb/cnn 概率）→ **+0.04 CV** | 1st |
| 2nd Hydrogen | 61 个测试 play → 按 game_key 的 StratifiedGroupKFold；blend CV 0.807 / 公 0.796 / 私 **0.796**；24 帧×双方向；端区+边线**横向拼接早融合**；**5 通道追踪编码**（灰度 ROI/框 mask/距离×128/同队标志/移动距离，uint8）；6 模型×3 seed；mixup；±3 帧抖动 + TTA；追踪 10→60Hz 线性插值 + 头盔框插值；stage2 LGBM（stage1 概率+距离/lag+step_pct+归一化坐标）+ 50:50 平滑原始预测 | 2nd |
| 6th / 14th / 4th | 6th TK&penguin46、14th、4th K_mat 的 CNN 可视化（391719） | 材料 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd Hydrogen |
| --- | --- | --- |
| 结构 | 预处理 XGB → CNN → 后处理 XGB | 单段 CNN（追踪通道编码）→ stage2 LGBM |
| 输入 | PP：视频+追踪图；PG：仅视频 | 视频+5 追踪通道（早融合） |
| 时序 | PP 18 帧 / PG 23 帧采样 | 24 帧×2 方向；±3 帧抖动 |
| 骨干 | resnet50-irCSN（动作识别） | EfficientNetV2-s/b3（2D+3D） |
| 后处理 | 邻域概率 → XGB | stage2 LGBM + 50:50 平滑 |
| 验证 | — | game_key 分组 CV；CV 0.807 与 LB 0.796 接近 |

### 共识 / 分歧 / 裁决
**共识一：把追踪数据编码进 CNN 是核心（1st/2nd）**
1st 把追踪画成"鸟瞰圆点图"当第三个视角；2nd 用 5 通道 uint8 编码（距离、同队、移动距离等），并指出"CNN 自己能学到的距离有限，所以直接给"。**裁决**：结构化先验（距离/队别）直接编码进视觉网络，比让 CNN 硬学更省样本。置信度：高。

**共识二：PP 与 PG 分开建模，且输入需求不同（1st 明证）**
PG 加追踪无增益；PG 因此能用更长时序（23 vs 18 帧）。**裁决**：两类接触的物理先验不同，分开建模并分别做超参/后处理。置信度：中高。

**共识三：邻域时序后处理稳定加分（1st + 2nd）**
1st 用前后 10/15 步概率喂 XGB（+0.005/+0.04）；2nd 用 stage2 LGBM + 平滑。**裁决**：接触是时序稠密事件，单帧判断必被邻域平滑修正。置信度：高。

**共识四：小测试集 → 分组验证至关重要（2nd）**
61 个 play、按 game_key 分组；CV 0.807 与 LB 0.796 仅差 ~0.01。**裁决**：体育视频事件赛要用"比赛级"分组 CV，否则同场泄漏。置信度：高。

**分歧一：单段 vs 两段**
2nd 明确"编码追踪后主要依赖单段，减少在 OOF CNN 预测上做 2 阶段的过拟合"；1st 仍是"XGB→CNN→XGB"三段。**裁决**：单段更简洁、泛化好；两段在易负样本多时省算力。融合两种思路可兼得。置信度：中高。

**分歧二：追踪插值/头盔框补全**
2nd 用线性插值把追踪 10→60Hz 并补头盔框（承认引入噪声但整体有益）；1st 未提。**裁决**：时间对齐误差大于插值噪声时，插值净收益；需以分组 CV 验证。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 2nd 的 CV/LB（0.807/0.796）与消融表 | 自述 + 图 | 中高 |
| 1st 的后处理增益（+0.005/+0.04） | 自述 | 中 |
| PP/PG 输入差异 | 1st/2nd 一致 | 高 |
| 61 个测试 play | 2nd 明示 | 高 |
| 追踪编码有效性 | 两队独立 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd/5th 方案未收录；MCC 阈值优化与类别不平衡处理细节缺失。
- 1st 的预处理 XGB 只给 CV≈0.72，未展开；PG 后处理 +0.04 的来源需更多验证。
- 往届 NFL 索引（370685）与 4th 的可视化（391719）未细读。

### 图证（KStarter 仓库内路径）
- ../../intel/nfl-player-contact-detection/bodies/391740_img/01.png — 2nd 的 CNN 架构

### 出处
- 2nd Team Hydrogen（391740）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/391740
- 6th TK&penguin46（391620）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/391620
- 1st（391635）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/391635
- 14th（391609）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/391609
- 往届索引（370685）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/370685
- 4th K_mat 可视化（391719）：https://www.kaggle.com/competitions/nfl-player-contact-detection/discussion/391719

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/392182
- rank 4｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/391761
- rank 5｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/392290
- rank 9｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/392402
- rank 16｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/391792
- rank 18｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/392162
- rank 19｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/394302
- rank 41｜description：https://www.kaggle.com/c/nfl-player-contact-detection/discussion/392226

---

## openai-to-z-challenge — OpenAI to Z Challenge（亚马逊考古发现）轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标  ｜ 队伍 225 ｜ 截止 2025-06-29 ｜ Tier B ｜ 标签 cv,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/openai-to-z-challenge.md
> 材料基础：`digests/openai-to-z-challenge.md`（2 篇正文：Starter materials 579189 / Who is paying for API? 579187；80 条主题索引）+ 0 张归档图

### 一句话重述
用 OpenAI 模型（o3/o4-mini、GPT-4.1 等）+ 公开遥感数据，**协助发现亚马逊雨林中可能被植被掩藏的考古遗址**；Kaggle 首届 hackathon（评审制、无排行榜）。归档材料把本场的真实矛盾暴露得很清楚：**技术主线是开放地理数据（LiDAR→DTM、DEM、NDVI、高光谱）＋ 文献推理，但社区最大热帖是"API 谁付钱"**——检查点与早提交奖励（$100 / $1000 API credits）只是部分对冲。此外，"OpenAI 源文件幻觉"（584626）提示 LLM 引用的文献必须逐条核验。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与机制 | **225 队**；截止 2025-06-29；**Kaggle 首届 hackathon**；评审制（社区追问"人工还是 LLM 评审"未获归档回答） | 579189 / 579068 / 580055 |
| 成本争议（最高热帖） | "Who is paying for API?" **48 票 / 23 评论**；"Can this competition have a low entry barrier?" 35 票 / 14 评论；"paywall feels off" 5 票；"Credits Are Needed!" 3 票；免费每日额度提示 11 票；Azure OpenAI 合规澄清 3 票 | 579187 / 579173 / 580595 / 579361 / 579237 / 579758 |
| 奖励/激励 | 检查点 $100 API credits（579362、579869）；6-14 前早提交 **5 × $1000 API credits**（579196、581140） | 索引 |
| 技术素材（社区） | NASA Amazon LiDAR 处理成 DTM（18 票）；"DEM is all you need"；高光谱影像；Major TOM embeddings 候选点搜索；RAG-LLM 方案；NDVI/土壤筛选交互地图 | 581299 / 587383 / 585543 / 579595 / 580234 / 585259 |
| 方法建议 | "别想一口吃成胖子：第一天就选一个小区域或一种特征类型"（14 票）；"Step 1: 文献综述 + 相关论文"（7 票）；官方 FAQ/关键日期 | 579267 / 579226 / 578995 / 581230 |
| 风险事件 | **OpenAI 源文件幻觉**（2 票 / 6 评论）；write-up 含私有 notebook 链接（可复现性）；未提交/迟到争议与"自动提交草稿"请愿 | 584626 / 589010 / 587369 / 587185 / 587186 |
| 结果 | Winners Announced（13 票 / 60 评论）+ Thank you & next steps（19 票 / 19 评论）；获奖方案正文未归档 | 602618 / 587178 |

### 逐方案对照矩阵
**2. 逐路线对照矩阵**
| 维度 | 文献 + LLM 推理线 | 遥感检测线 | 评审/交付线 |
| --- | --- | --- | --- |
| 代表帖 | Starter materials 579189；文献综述 579226；RAG-LLM 580234 | LiDAR→DTM 581299；DEM 587383；高光谱 585543；NDVI 地图 585259 | 获奖公布 602618；next steps 587178 |
| 输入 | 论文库、历史地名、考古假说 | LiDAR 点云、DEM、Sentinel/NDVI、高光谱 | write-up + 可复现产物 |
| 产出 | 候选遗址假设与证据链 | 候选点位、地形/植被异常图 | 获奖名单与后续计划 |
| 主要风险 | 幻觉来源（584626） | 数据覆盖/许可、算力、误报 | 评审口径与可复现性不透明 |

### 共识 / 分歧 / 裁决
**事件一：API 成本与可及性是本场第一约束（579187 / 579173 / 580595 / 579361 / 579237；置信度中高）**
最高票帖不是技术帖而是"谁付 API 钱"；官方用检查点/早提交的 credits 变相补偿，但选手仍反复担忧预算。**裁决**：以商业 API 为核心的比赛，第一步做成本模型（调用量 × 单价），优先用免费额度与 checkpoints 覆盖探索期，把付费调用留给最终证据链。置信度：中高（社区共识明确；官方回应未归档）。

**共识一：缩小范围 + 文献先行是官方与资深参与者的共同建议（579267 / 579226 / 578995；置信度中高）**
"别想一口吃成胖子，先选小区域或单类特征"是 14 票的方法论帖；文献综述被列为 Step 1。**裁决**：先锁定小 AOI + 一种目标特征（如几何地形的方形/环形结构），用文献建立可检验假说，再谈模型与扫描。置信度：中高。

**共识二：技术栈重心在开放地理数据，LLM 负责综合而非直接检测（581299 / 587383 / 585543 / 585259 / 579595；置信度中）**
社区实际动手的是 LiDAR→DTM、DEM、NDVI、高光谱与 embedding 检索；LLM 用于文献/RAG/推理。**裁决**：把 OpenAI 模型定位为"假设生成与证据整合器"，检测与验证交给遥感管线；每条模型来源都需人工核验（584626）。置信度：中。

**事件二：可复现性与提交纪律是评审制的隐性淘汰线（589010 / 587369 / 587185 / 587186；置信度中）**
出现 write-up 链接私有 notebook、未提交被打回、临截止提交被标迟到、请愿自动提交草稿等事件。**裁决**：截止前留出提交缓冲、确认状态为 Submitted、并保证 notebook/数据公开可复现。置信度：中。

**分歧：评审口径不透明（580055 + 602618 无 rubric；置信度中）**
社区公开询问评审是人工还是 LLM，归档中没有明确答复；获奖帖只公布名单与祝贺。**裁决**：按"人类评委可读的发现叙事 + 可复现证据"组织交付，别依赖单一评分信号。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 赛事机制、225 队、首届 hackathon | 官方帖 + 索引（579189 / 579068） | 高 |
| 成本争议与激励结构 | 多帖（579187 等）+ 索引 | 中高（社区侧证据充分） |
| 技术素材（LiDAR/DTM/DEM/NDVI/高光谱） | 社区帖（581299 等） | 中（未归档实际代码） |
| 幻觉风险 | 讨论帖（584626） | 中（单帖 + 评论） |
| 获奖方法与评审细节 | 未归档 | 低（只有名单） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 本场归档正文仅 2 篇（材料最薄的 Tier B 场次之一），获奖方案与评审标准完全缺失；
- 评审由人还是 LLM 执行，归档中无结论（580055）；
- 模型给出的考古发现是否经专业验证，未见归档记录；
- 私有 notebook/数据许可问题（589010）未解决；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- Who is paying for API?（48 票 / 23 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/579187
- Starter materials（38 票 / 12 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/579189
- Introducing Kaggle Hackathons!（19 票 / 6 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/579068
- 低门槛讨论（35 票 / 14 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/579173
- 别想一口吃成胖子（14 票 / 2 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/579267
- NASA Amazon LiDAR → DTM（18 票 / 5 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/581299
- DEM is all you need（2 票 / 3 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/587383
- OpenAI 源文件幻觉（2 票 / 6 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/584626
- RAG-LLM approach（4 票 / 2 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/580234
- Winners Announced（13 票 / 60 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/602618
- Thank you and Next Steps（19 票 / 19 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/587178
- 评审方式提问（3 票 / 2 评论）：https://www.kaggle.com/competitions/openai-to-z-challenge/discussion/580055

---

## petfinder-pawpularity-score — 深读：PetFinder Pawpularity（小信号回归里的"锚、头、辅、重"）

> 主题 cv ｜ 类别 Research ｜ 指标 Root Mean Squared Error ｜ 队伍 3537 ｜ 截止 2022-01-14 ｜ Tier A ｜ 标签 cv,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/petfinder-pawpularity-score.md

### 一句话重述
预测宠物照片的"可爱度"（1–100，RMSE）。目标主观、元数据弱、信号小（可学区间约 17–18）。**先立锚**：全预测 38.04（训练均值）的 RMSE=20.59——任何低于它的模型才算有预测力。
→ 任务降解为：**① 用预训练模型把图像变成"可回归的表征"；② 决定元数据是输入、辅助输出还是后处理；③ 在 1e-1 分差的名次带里做融合与选模。**

### 关键数字（数字账）
| 事实/动作 | 数字 | 备注 |
| --- | --- | --- |
| 均值锚 | **20.59**（全 38.04） | 有预测力的门槛 |
| 单模型 SVR（头部特征） | 17.56（effnet_l2_ns_475）… 18.52 | 1000 维头特征 |
| SVR 特征集 A/B/C | 17.029 / 17.148 / 16.997 | 爬山前向选择 |
| A+B+C 集成 | 本地 16.923 / 私榜 16.95 | 目标 clip@85 有小增益 |
| DL 五模型 | CV 17.38–17.75，权重 2–4 | 混合 backbone + 增强强度 |
| 6th 最佳 CV/LB 集成 | 私榜 16.90 / 17.01 | 最佳 CV 提交公开仅第 120 名 |
| 18th | CV 17.25（OOF 口径） | 单模 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 6th | Public1st/Private5th | 18th |
| --- | --- | --- | --- | --- |
| 元数据 | **完全弃用** | 辅助输出（猫/狗标签有用，自带元数据无用） | 仅对近重复样本用往届元数据做后处理 | 弃用 |
| 表征/模型 | timm top-1k 头 + CLIP 编码器 → SVR；5×DL 回归 | Swin/BeIT/ConvNeXt/EffNetB2-SVR | 14 个单模（全图像） | 单 Swin-L + 序数头 |
| 选模/融合 | 爬山前向选择特征集 A/B/C；A+B+C 集成 | 等权爬山（CV 组与 LB 组各一） | 4 折 BayesianRidge 栈 + 分 AdoptionSpeed 后处理 | 10 折单模 |
| 关键数字 | SVR 集 16.997–17.148；集成 priv 16.95 | 最佳 CV 集成 priv 16.90；单 BeIT priv 17.00 | — | CV 17.25 |

### 共识 / 分歧 / 裁决
**3. 共识、分歧与裁决**
**共识**：弃掉"元数据当输入"（太弱）；用预训练表征；BCE 当回归损失是社区主流选择；图像增强是主要增益来源。

**裁决表**：

| 争议 | 观点 A | 观点 B | 裁决 |
| --- | --- | --- | --- |
| 元数据怎么用？ | 1st：全弃 | 6th：当辅助输出（猫/狗标签好，自带元数据无效）；Public1st：往届元数据只对近重复样本后处理 | **三态并存**：输入态最弱；辅助输出态取决于标签质量（猫/狗 > 自带 12 列）；"外部元数据 + 近重复匹配"是第三种，但依赖跨届重叠 |
| 表征取哪层？ | 1st：**top-1k 分类头** | 常规做法：内部嵌入 | 本场头 > 嵌入（假设：1k 类含猫狗品种，头部与细粒度任务对齐）；置信度中高（1st 实测且冠军） |
| 损失用什么？ | 社区多数：**BCE 回归**（6th/1st 均用） | 18th：序数回归头（"我不同意 BCE"） | 两者都能到前列——**损失选择与模型家族耦合**；BCE 是更稳的默认 |
| CV 怎么算？ | 多数：折 RMSE 均值 | 18th：**OOF 全量 RMSE** | 后者更严格（折均值偏乐观）；报告 CV 时应写明口径 |

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 均值锚 20.59 与分布统计 | **可验证（数据统计）** | 均 38.04 / 标准差 20.59 |
| 单模型 SVR 全表（26 个架构） | **可复算（帖内表）** | 结构与 RMSE 齐全 |
| 爬山前向选择与 RAPIDS 速度 | **可复算（伪代码+论述）** | cuML 是使能条件 |
| 元数据多任务结论 | **对照（6th 自述）** | 自带 vs 猫狗标签同场对比 |
| 近重复 + 往届元数据 | **自述（强）** | 两个提交 notebook 公开 |
| 头特征 > 嵌入 | **自述（1st）** | 无表格对照（弱证据） |

### 悬案与失败学
**8. 悬案与失败学**
- 悬案 1：目标生成机制（官方 cuteness meter）不可复现，天花板的噪声不可量化；
- 悬案 2：猫/狗标签来源与质量（辅助任务增益的可持续性未知）；
- 失败学：伪标签外部图像（6th，无效）；往届数据全量预训练/特征（6th，无效）；自带元数据多任务（6th，无效）；把折均值当 CV（偏乐观）。

### 图证（KStarter 仓库内路径）
- ../../intel/petfinder-pawpularity-score/bodies/301015_img/04.png — multitask
- ../../intel/petfinder-pawpularity-score/bodies/301015_img/02.png — preprocess

### 出处
- 1st：https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/301686
- Tricks 汇编：https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/288896
- 6th 多任务：https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/301015
- Public1st/Private5th：https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/300928
- 18th：https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/300942

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/300938
- rank 2｜code：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/300929
- rank 3｜code：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/301044
- rank 4｜description：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/301072
- rank 9｜description：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/300947
- rank 12｜code：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/301191
- rank 13｜description：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/300969
- rank 14｜description：https://www.kaggle.com/c/petfinder-pawpularity-score/discussion/300941

---

## physionet-ecg-image-digitization — PhysioNet ECG Image Digitization 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Physionet ECG Signal Extraction Metric ｜ 队伍 1424 ｜ 截止 2026-01-22 ｜ Tier B ｜ 标签 cv
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/physionet-ecg-image-digitization.md
> 材料基础：`digests/physionet-ecg-image-digitization.md`（6 篇正文：1st 669584 / 2nd 669871 / 3rd 669668 / 6th 669562 / 7th 669548 / 设计贴 613540；80 条主题索引）+ 13 张图

### 一句话重述
从心电图扫描图重建数值波形，评测只看**重建信号 SNR**。真正的考点是**几何标定（校正/重映射）+ 坐标精度（子像素）+ 后处理（导联定律/重采样）**——模型只负责"轨道"，分数由管线两端决定。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（669584，73 票） | 沿用社区 hengck23 的 stage0/1 校正管线；两条输入路径（高分辨 homography 重映射 / 直接从旋转图重映射）；**Fourier 域重采样**（scipy.signal.resample 优于线性插值）；灰度图 + 坐标特征通道；三种"按高度切 4 段、横向扩 4×"的解码策略；后处理：取中段 1–2 万点重采样 + **按 Einthoven 定律做软混合**（II=I+III、aVR+aVL+aVF=0）；**TTA +0.07、导联定律修正 +0.06**；10 模型集成（convnextv2_tiny/base、effnetv2_m），验证 30 图 | 1st |
| 2nd（669871，36 票） | **把竞赛信号换回 PTB-XL 原始 500Hz**（竞赛数据被 host 重采样成 250–1025Hz）→ 单折 LB **21.67→22.49 dB**；**稀疏掩码**（每列 ≤2 像素、按小数部分分给相邻两格、重建时加权平均，往返可精确复原，见图 1）；双模型：whole（timm+MyCoordUnetDecoder, 1280×5600）+ series（2.5D 四导联融合，conv2d 融合最佳）；BCE pos_weight=20；**指标洞察：线性域平均 ⇒ 优先提升中高分图**；6 模型集成 pub 23.37 / priv 23.27 | 2nd |
| 3rd（669668，31 票） | 低分辨率算几何、**放大后直接作用于原图**的高分辨校正；1 像素宽掩码 + 故意"过拟合"出细而高置信波形；尺寸实验：2200×1700 → **24.22 dB**，4400×1700 → **31.23 dB**（宽度翻倍 = 采样点翻倍，量化误差骤降）；抛物线亚像素细化 | 3rd |
| 6th（669562，30 票） | **直接回归导联信号**，绕过"分割+后处理"以消除累积误差；重采样基准（FFT 最优，中段密度越高保真越好：10250 > 5120 > 2560）；自写 `resample_torch` 把重采样放进训练 | 6th |
| 7th（669548，48 票） | 五段流水线：旋转分类（HGNet-V2，检出 69 张需旋转）→ 导联检测（ConvNeXt，检测头 ≥128 通道）→ 导联分割 → 数字化（maxxvit+1D UNet，5 通道输入）→ **OOD 检测用于集成筛选**；用 ECG-image-kit + DTD 纹理合成训练数据；轻模型全折验证、重模型 100 图验证 | 7th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 6th | 7th |
| --- | --- | --- | --- | --- | --- |
| 目标形式 | 掩码/数值预测 + 后处理 | **稀疏掩码** + 加权重建 | 1px 掩码 + 亚像素 | **直接回归信号** | 分割 + 数字化 |
| 关键数据动作 | 高分辨重映射 | **换回 500Hz 原始信号** | 宽度 2200→4400 | 重采样基准 | 合成数据（ECG-image-kit） |
| 重采样 | Fourier | scipy.signal.resample | — | **FFT 验证 + torch 实现** | — |
| 导联关系 | **Einthoven 定律软混合 (+0.06)** | 2.5D 四导联特征融合 | — | — | 检测/分割 13 类导联 |
| TTA | gamma+裁剪/缩放 (+0.07) | 水平翻转 | — | — | — |
| priv | 1st | 23.27 | — | — | — |

### 共识 / 分歧 / 裁决
**共识一：几何校正与重映射是公共基座（1st/2nd/3rd/7th）**
1st/2nd/3rd 都建立在 hengck23 的 stage0/1 校正管线上（1st/2nd 致谢中明确），7th 另起 lead detection/segmentation 但同样是"先几何后信号"。**裁决**：图像→数值任务的公共解法是"先标准化版面，再数字化"；高分辨重映射（3rd：低分辨算参数、原图执行）是避免细节损失的通用技巧。置信度：高。

**共识二：子像素/采样密度直接换成 SNR（1st/2nd/3rd/6th）**
2nd 的稀疏掩码把 y 坐标的小数部分编码进相邻两格（图 1 展示 11.71→11.71 的精确往返）；3rd 把宽度从 2200 拉到 4400（24.22→31.23 dB）；6th 证明中间重采样密度 10250>5120>2560。**裁决**：目标是"位置精度"，任何提高横向采样密度或亚像素编码的动作都是直接增益。置信度：高（三队独立 + 数字）。

**共识三：FFT 域重采样优于线性插值（1st/2nd/6th）**
1st 用 scipy.signal.resample；2nd 对比三种方法后选 scipy；6th 做了系统基准并移植到 torch。**裁决**：信号域重采样别用图像插值（torch.interpolate 等价于线性），FFT/polyphase 保真更高。置信度：高。

**分歧一：掩码+后处理 vs 直接回归**
1st/2nd/3rd/7th 走"分割（掩码）→重建/后处理"；6th 明确改为**直接回归导联信号**，理由是避免后处理阶段累积误差。**裁决**：直接回归少了可解释的几何中间量（也就少了导联定律类修正的抓手）；两条路都能进前列，取决于你更擅长哪一端。置信度：中高。

**分歧二：掩码画多宽**
3rd 用 1 像素宽并故意过拟合细线（加高斯模糊变宽反而无益）；2nd 用"每列 ≤2 像素"的稀疏软标签；1st 未如此处理。**裁决**：在"位置回归"语义下，细而确定的目标优于模糊粗线——但需要亚像素重建来兑现精度。置信度：中高。

**事件：指标结构决定投入方向（2nd 的洞察）**
2nd 分析出"先线性域平均再转 dB"意味着**中高 SNR 图数量多、改进空间大**，于是放弃最难的 0015 型皱褶图（只少量混入训练），主攻中等难度。**裁决**：读指标时要做"分数贡献分解"（哪类样本贡献多少分差），再分配算力。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 2nd 的 500Hz 替换 +0.82 dB、稀疏掩码往返 | 自述 + 图 + 公开代码 | 高 |
| 1st 的 TTA +0.07 / 导联修正 +0.06 | 自述 + 模型表 | 中高 |
| 3rd 的宽度→SNR 表（24.22 vs 31.23） | 自述 + 图 + 公开代码 | 高 |
| 6th 的重采样基准 | 自述 + 图 + 公开代码 | 中高 |
| 7th 的检测头通道数/最小裁剪经验 | 自述（+0.2~3 的粗估） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th/5th/13th 的 write-up 未入库；"from lb 0.16 to 0.20"（39 票）未细读；
- 1st 未公布完整集成权重与验证曲线；合成数据的独立增益未量化；
- 7th 的 OOD 集成筛选细节、13th 的方案均缺失；
- 归档 13 图中 7 张为方法图（1st 的输入裁剪、2nd 的掩码往返/预测/模型图、3rd 的掩码尺寸对照）。

### 图证（KStarter 仓库内路径）
- ../../intel/physionet-ecg-image-digitization/bodies/669871_img/02.png — 2nd 的稀疏掩码往返
- ../../intel/physionet-ecg-image-digitization/bodies/669871_img/03.png — 2nd 的 OOF 预测叠加
- ../../intel/physionet-ecg-image-digitization/bodies/669584_img/01.png — 1st 的标准化输入

### 出处
- 1st（73 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/669584
- 2nd（36 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/669871
- 3rd（31 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/669668
- 6th（30 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/669562
- 7th（48 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/669548
- 设计讨论（40 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/613540
- open→secret sauce（39 票）：https://www.kaggle.com/competitions/physionet-ecg-image-digitization/discussion/624054

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/1st-place-solution
- rank 2｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/2nd-place-solution
- rank 3｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/3rd-place-solution
- rank 4｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/4th-place-solution
- rank 5｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/5th-place-solution
- rank 6｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/6th-place-solution
- rank 7｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/7th-place-solution
- rank 8｜description：https://www.kaggle.com/c/physionet-ecg-image-digitization/writeups/8th-place-solution

---

## planttraits2024 — PlantTraits2024（植物性状多目标回归）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 R2 Score ｜ 队伍 398 ｜ 截止 2024-06-02 ｜ Tier B ｜ 标签 cv,agriculture
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/planttraits2024.md
> 材料基础：`digests/planttraits2024.md`（6 篇正文：植物表型综述 473745 / 1st PlantHydra 510393 / 6th AutoGluon 510143 / 9th DINOv2+CatBoost 510188 / 测试集更新与重算 486503 / 提交列顺序 487985；58 条主题索引）+ 3 张归档图

### 一句话重述
从植物照片 + 气候/土壤元数据预测 **6 个性状均值**（R²）。三条获奖路线共同指向一句话：**"物种身份"是隐藏变量**——1st 把训练集按性状聚成 **17,396 个"物种"**，用回归 + 硬分类 + 软分类三个头融合；6th 用 AutoGluon 的多模态栈 + 标签链；9th 用 DINOv2 embedding + CatBoost。本场还有一次重大赛事事故：有选手利用 `sample_submission.csv` 刷榜，官方**更换测试集并重置排行榜**；另有"提交列顺序必须与 sample_submission 一致"这个致命细节。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与目标 | **398 队**；6 个目标列 `X4_mean/X11_mean/X18_mean/X50_mean/X26_mean/X3112_mean`；R²（官方只计 >0 的值） | 索引 / 481308 |
| 1st（PlantHydra） | 三头：回归头（归一化性状）+ 分类头（**17,396 个"物种"**）+ 软分类头（按 softmax 权重对物种性状加权求和），三头权重可训练；DINOv2 ViT-b/l + **PlantCLEF 2024 西南欧植物预训练**；元数据用 **Structured Self-Attention**（PCA 失败）；损失 = 回归 R²+cosine、分类 focal、最终未归一化 R²；骨干与头用不同 LR schedule；MoE 混合不同风味模型 | 510393 |
| 9th（DINOv2+CatBoost） | DINOv2 [giant] embedding + 表格 → **CatBoost 原生处理 embedding**（含降维）；public **0.51162** / private **0.51238**；2 阶多项式特征小增益；**不同 embedding 的模型融合无效** | 510188 |
| 6th（AutoGluon） | TIMM 图像特征 + 表格特征 → Transformer 融合（略优于 MLP）；**标签链**（按论文 R² 顺序逐个预测）；EVA 系列最强：`eva_large_patch14_336` private **0.483**、`eva02_large_patch14_448` **0.486**、vit_large_384 0.43、swin_large 0.419；再 stacking → **0.526（第 6）** | 510143 |
| 公开基线进展 | 纯表格 +0.02486（480563）；表格 + ImageNet 特征 ≈0.22（489515）；EfficientNetB0 仅正分 +0.08921（486973）；sample_submission + 表格 = 0.3584（483574，后因测试集更换失效） | 索引 |
| 赛事事故 | 有选手用 `sample_submission.csv` 提分 → 官方**更新测试集（图片+test.csv）并重置 LB**；`sample_submission.csv` 在新测试集上从正分变成 **-33.38** | 486503 / 483518 |
| 提交细节 | **列顺序必须与 sample_submission 一致**（不是表头匹配就行）：`['X4_mean','X11_mean','X18_mean','X50_mean','X26_mean','X3112_mean']` | 487985 |
| 数据质量争议 | 极端标签值处理（9 票 / 10 评论）；"Poor labeling"（7 票）；为何不给物种（7 票）；性状数 6 vs 聚合数据 33（5 票）；单位为题；负 X4；R² 只计正值的规则被质疑 | 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st PlantHydra | 6th AutoGluon | 9th DINOv2+CatBoost |
| --- | --- | --- | --- |
| 核心 | 回归+硬分类+软分类三头 | 多模态 AutoML + 标签链 + stacking | 大模型 embedding + GBDT |
| 图像侧 | DINOv2 ViT-b/l + 植物域预训练 | TIMM（EVA 最强） | DINOv2 giant |
| 表格侧 | Structured Self-Attention | FT-Transformer/MLP | 原样拼接 |
| 后处理 | 三头可训练权重融合 | 模型 soup + stack | 2 阶多项式 |
| 私榜 | 冠军（未报分数） | 0.526 | 0.51238 |

### 共识 / 分歧 / 裁决
**共识一：把"物种识别"显式建模是最大杠杆（510393 / 510143；置信度中高）**
1st 的三头里分类/软分类贡献核心；6th 的标签链也依赖性状相关性。**裁决**：多性状回归先做"物种/聚类身份"辅助任务（硬标签 + 软权重两条支路），再与直接回归融合；聚类数按性状唯一组合确定。置信度：中高。

**共识二：大模型 embedding + 轻量头部/GBDT 是性价比最高的起手式（510188 / 510143；置信度中高）**
9th 用 DINOv2+CatBoost 进前 10；6th 用 AutoGluon 多模态进前 6；两者都避免端到端大模型训练。**裁决**：算力有限时先冻结大骨干提 embedding，再上 CatBoost/stacking；端到端微调留给最后冲榜。置信度：中高。

**事件一：域内预训练模型显著加分（510393；置信度中）**
PlantCLEF 2024（Pl@ntNet 西南欧植物）预训练"显著提升"性状识别。**裁决**：生物/农业赛道优先找领域预训练权重，再考虑通用 ImageNet 权重。置信度：中（冠军自述）。

**事件二：分层学习率调度是微调成败关键（510393；置信度中）**
1st 用不同的 scheduler：头与融合权重高 LR + 早 warmup，backbone block 逐层降 LR，tokens 最低（图见下）。**裁决**：微调大骨干时按层组设置 LR/冻结解冻顺序，不要全网络单一 LR。置信度：中。

**事件三：赛事公平性与提交规范被两次事故教育（486503 / 487985；置信度高）**
sample_submission 刷榜导致换测试集+重置 LB；列顺序错位造成 CV/LB 大幅不一致。**裁决**：提交前核对列顺序与行数；发现"利用样例文件"的机会先报告而不是利用；本地 CV 与 LB 不一致时先查提交格式。置信度：高。

**分歧：多图/多模态增强是否值得（510143 vs 510393；置信度低）**
6th 用 5 张图/物种未提升；1st 靠元数据自注意力拿到核心增益。**裁决**：优先元数据融合与物种建模，多图策略在大规模算力下再试。置信度：低。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 三头架构与损失设计 | 冠军自述 + 调度图（510393） | 中高（无分数表） |
| 9th 的 0.51238 与 DINOv2+CatBoost | 自述 + notebook（510188） | 中高 |
| 6th 的分模型分数与 0.526 | 自述（510143） | 中（AutoML 细节依赖框架） |
| 测试集更换与 LB 重置 | 官方帖（486503） | 高 |
| 列顺序问题 | 官方样例 + 作者复盘（487985） | 高 |
| 数据质量争议 | 多帖（481726 / 478549 等） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st 未公开私榜分数与完整消融；"三头权重"具体数值未给；
- 官方为何选 6 个性状、R² 只计 >0 的规则依据未归档；
- 换测试集后旧提交的最终处理细节未归档；
- 多图/物种分类路线未充分验证；
- **图证缺口**：无（3 张图，本深读内嵌 1 张调度图；PlantHydra 的 DALL-E 蛇图与植物插画无分析价值，未内嵌）。

### 图证（KStarter 仓库内路径）
- ../../intel/planttraits2024/bodies/510393_img/02.png — PlantHydra 分层学习率调度

### 出处
- 1st PlantHydra（29 票 / 13 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/510393
- 6th AutoGluon（9 票 / 4 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/510143
- 9th DINOv2+CatBoost（9 票 / 1 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/510188
- 测试集更新与重算（13 票 / 13 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/486503
- 提交列顺序（13 票 / 3 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/487985
- 植物表型综述（37 票 / 13 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/473745
- R² 只计正值规则（3 票 / 1 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/481308
- 极端标签值处理（9 票 / 10 评论）：https://www.kaggle.com/competitions/planttraits2024/discussion/478549

---

## recodai-luc-scientific-image-forgery-detection — RECOD.ai-LUC Scientific Image Forgery Detection 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 RecodAI F1 ｜ 队伍 1564 ｜ 截止 2026-04-22 ｜ Tier B ｜ 标签 cv,detection
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/recodai-luc-scientific-image-forgery-detection.md
> 材料基础：`digests/recodai-luc-scientific-image-forgery-detection.md`（6 篇正文：1st 695702 / 2nd 694397 / 65th 694442 / 29th 694168 / 私榜 3rd 674890 / DCT 综述 613066；80 条主题索引）+ 12 张归档图

### 一句话重述
检测科研论文图像（Western blot、显微/宏观照片等）中的 copy-move 伪造：authentic 图预测对得 1.0、预测成伪造得 0；伪造图按匈牙利匹配的实例 F1 计分，且多预测实例会被惩罚。本场的核心结论是**"把检测重构成检索"**：前三名都是"面板切分 + 相似检索/特征匹配 + 几何验证"路线（1st 是嵌入检索 + 条带级匹配，2nd/私榜 3rd 甚至是纯经典 SIFT/SAM3 无训练），纯分割模型（65th、29th 的 DINOv2 segmenter）只能排在中游。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（695702） | 公榜推进（250+ 次提交）：0.327 → 0.341 → 0.353 → 0.370 → 0.375 → **0.431** → 0.456–0.458；**条带级（lane）匹配是主引擎（0.375→0.431）**，显微嵌入升级贡献 0.431→0.446；数据 = PubMed Central 约 200 万 tar.gz（14TB）→ 去重后 660 万 blot + 1630 万显微图；面板检测 11.3k–12.3k 标注图；条带检测标注 3,732 图 → 对 ~600 万 blot 生成 **2700 万** 框；匹配：显微 SIFT+LightGlue+RANSAC、blot ALIKED+LightGlue+MAGSAC；检索嵌入 SupCon（温度 0.07–0.09、nextvit_small）；无匹配时退回公共分割 kernel（+0.005–0.01）；最终私榜 0.550（选了公榜 0.450 那版，而非公榜 0.458/私榜 0.541 的版本） | 695702 |
| 2nd（694397） | 纯经典路线（无深度匹配）：YOLOv8-m 面板（3 类）与文本检测（~800 手标 + ~2000 合成，5 模型 WBF）；SIFT `contrast_threshold=0.001`（默认的 1/40）、<1024px 先 4× 放大；**G2NN（α=0.7）+ FLANN KDTree**（O(N²)→O(N log N)）；RANSAC 局部/全局 + HDBSCAN；按三类图像分别设 inlier 阈值；两阶段聚类合并（H 相似 <0.02、IoMin ≥0.3）；凸包 + H 误差细化掩码；公榜 3rd → 私榜 2nd；SURF/ORB/AKAZE/SuperPoint 与深度 CMFD 模型都失败 | 694397 |
| 65th（694442） | DINOv2-base（冻结 + 末 12 层解冻）+ 微型卷积解码器（768→384→192→96），518×518；两阶段训练（解码器预热 lr 1e-5 → 联合微调 backbone lr 5e-7）；翻转 TTA×3；**梯度增强掩码**（alpha=0.45）；面积/概率阈值网格搜索（AREA_MIN≈200、PROB_MIN≈0.20–0.22）；结论：copy-move 本质是"自相似"，DINOv2 自蒸馏特征天然匹配 | 694442 |
| 29th（694168） | DinoV2Segmenter（仅末 5 个 block + LayerNorm 可训）+ 卷积解码器；外部数据 RSIID（39,423 张篡改图 / 2,923 张原图）+ 反事实重构（co 对）→ 合计 51,489 样本（24,300 authentic / 27,189 forged）；StratifiedGroupKFold 5 折；BCE、50 epochs、8×TTA；**指标感知后处理**：q999≥0.95 gate、掩码阈值 0.3、只交单个合并掩码（避免超额实例惩罚）、按 split 跟踪 lift 选"每个 split 都为正"的最保守阈值 | 694168 |
| 私榜 3rd（674890） | 无训练：SAM3 文本提示切面板（两轮提示，第二轮找生物对象；无结果则注入固定切块）→ CLAHE + 文本/箭头遮除 → SIFT+FLANN+Lowe+RANSAC → 收紧到 inlier 包围盒；自述"在合成单图数据上训练的 NN 无法迁移到 figure 级补充测试" | 674890 |
| 文献（613066） | DCT 系数符号 + 元胞自动机特征 + KDTree 匹配的传统 CMFD，对 JPEG/噪声更稳健（38 票） | 613066 |
| 社区争议 | "指标极不公平"（10 票）、"掩码同时包含复制源与目标"（10 票 / 10 评论）、0.303 平台、CV/LB 严重落差、"train 与 supplemental 差异巨大"（7 票）、全 authentic 基线（6 票） | 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 65th | 29th | 私榜 3rd |
| --- | --- | --- | --- | --- | --- |
| 核心 | 检索 + 条带级匹配 | 经典 SIFT + G2NN | 分割（DINOv2 解码器） | 分割（DinoV2Segmenter）+ 指标工程 | SAM3 + SIFT（无训练） |
| 面板/文本预处理 | YOLO 面板检测 | YOLO 面板 + 文本检测 | 无 | 无 | SAM3 提示切分 + 文本遮除 |
| 外部数据 | 14TB PMC 自建（6.6M+16.3M 图） | 2,000 BioFors 图（合成训练） | 无 | RSIID 51k 样本 | 无 |
| 训练量 | 大（嵌入 + 检测器 + 匹配） | 小（YOLO only） | 中（两阶段） | 中 | 零 |
| 后处理 | 阈值 + 兜底 kernel | 聚类合并 + 掩码细化 | 梯度增强 + 阈值网格 | q999 gate + 单掩码 + per-split lift | inlier 包围盒 |
| 名次 | 1st | 2nd | 65th | 29th | 私 3rd |

### 共识 / 分歧 / 裁决
**共识一：copy-move 检测的本质是"自相似检索"，检索+几何验证 > 纯分割（1st、2nd、私 3rd；置信度高）**
前三名的共同结构都是"找重复/重叠区域 + 几何验证"；1st 明说 copy-move 要找的是"语义与纹理相同的两个区域"而非 OOD 物体；2nd/3rd 用纯经典匹配分别拿到私榜 2/3。**裁决**：这类任务的 SOTA 形态是检索匹配（嵌入 or 关键点），分割网络是补充/兜底而非主轴。置信度：高（名次 + 1st 的 +0.056 条带级增益）。

**共识二：面板/文本预处理是必要模块（1st、2nd、私 3rd；置信度中高）**
1st 用 YOLO 检测 blot/显微面板；2nd 用面板+文本双 YOLO（文本误匹配如 "10 mm" 的 "mm"）；3rd 用 SAM3 两轮提示切分并遮除文本/箭头。**裁决**：科研图像的版面结构（多面板、图注文字）会制造大量假匹配，先切分再匹配是标准前置。置信度：中高。

**共识三：指标感知的后处理/提交选择直接决定名次（1st、65th、29th；置信度高）**
authentic 图错报为伪造 = 1.0 直接归零；伪造图按实例 F1 且多预测要乘 `len(gt)/max(len(pred),len(gt))` 惩罚。1st 选了私榜 0.550 而放弃公榜 0.458 的版本；65th 网格搜索 AREA/PROB 阈值；29th 用 q999≥0.95 门控 + 单掩码 + 每个 split 都为正 lift 的保守阈值。**裁决**：在这类"错报代价极高"的指标下，保守判定 + 单实例提交 + 按 split 验证 lift 是必要动作。置信度：高。

**分歧一：数据驱动分割 vs 经典匹配（65th/29th vs 1st/2nd/3rd；置信度中高）**
65th（DINOv2+小解码器）与 29th（DinoV2Segmenter + 指标工程）代表分割路线，名次 65/29；1st/2nd/3rd 的检索匹配路线占据前三。**裁决**：纯分割在本任务的天花板更低（伪造=自相似，不是像素异常）；可行的组合是"检索为主 + 分割兜底"（1st 的公共 kernel 兜底仅 +0.005–0.01）。置信度：中高。

**事件：指标与标签的争议是主要风险（641092、613200、613694、657899；置信度中高）**
"指标极不公平"（10 票）、"掩码同时覆盖复制源与目标"（10 票 / 10 评论）、标签错误讨论、"train 与 supplemental 差异巨大"（7 票）说明评测口径与数据分布都需要自行校准。**裁决**：先精确复现指标（含惩罚项与 authentic 规则）再选模型；把不同数据 split 的 lift 分开跟踪。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的条带级增益（0.375→0.431）与最终 0.550 | 自述 + 分数截图 + 管线图 | 中高 |
| 2nd 的经典匹配全流程与失败清单 | 自述 + 开源代码 | 高 |
| 29th 的 RSIID 数据规模与指标感知框架 | 自述（含代码片段/表格） | 中高 |
| 65th 的 DINOv2 训练细节 | 自述 | 中 |
| 私榜 3rd 的 SAM3 流程 | 自述 | 中 |
| 指标定义（authentic/F1/惩罚） | 29th 转述官方 metric + 社区争议帖 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st 如何把 0.458 与 0.450 版本区分（内部 CV 细节）未展开；
- 官方 metric 文档未归档；社区"指标不公平"的具体诉求未细读；
- 2nd/3rd 的开源实现未运行核对；
- 归档 12 图仅内嵌 3 张（其余留待图像层）；
- **图证缺口**：无（12 张归档图充足）。

### 图证（KStarter 仓库内路径）
- ../../intel/recodai-luc-scientific-image-forgery-detection/bodies/695702_img/01.png — 1st 的三段式流程
- ../../intel/recodai-luc-scientific-image-forgery-detection/bodies/695702_img/02.png — 公私榜选择
- ../../intel/recodai-luc-scientific-image-forgery-detection/bodies/695702_img/11.png — 条带级掩码合并启发式

### 出处
- 1st（37 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/695702
- 2nd（15 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/694397
- 65th DINOv2（8 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/694442
- 29th 分割 + 指标工程（7 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/694168
- 私榜 3rd / 公榜 8th（7 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/674890
- DCT copy-move 文献（38 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/613066
- 指标争议（10 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/641092
- 掩码含源+目标说明（10 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/613200
- train vs supplemental 差异（7 票）：https://www.kaggle.com/competitions/recodai-luc-scientific-image-forgery-detection/discussion/657899

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/recodai-luc-scientific-image-forgery-detection/writeups/1st-place-solution
- rank 29｜description：https://www.kaggle.com/c/recodai-luc-scientific-image-forgery-detection/writeups/recod-ai-luc-scientific-image-forgery-detection

---

## rsna-2022-cervical-spine-fracture-detection — RSNA 2022 颈椎骨折深读：87 例掩码撬动 2k 例粗标签的标签工程

> 主题 cv ｜ 类别 Featured ｜ 指标 Weighted Mean Columnwise Log Loss ｜ 队伍 883 ｜ 截止 2022-10-27 ｜ Tier A ｜ 标签 cv,detection,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-2022-cervical-spine-fracture-detection.md
> 材料基础：`digests/rsna-2022-cervical-spine-fracture-detection.md`（6 篇：1st/1st-code/3rd/5th/6th + 数据详解帖；80 条讨论索引）+ 10 张图（340612×4 / 362607×4 / 362643×2）

### 一句话重述
题面是"颈椎 CT 逐椎骨 C1–C7 骨折二分类 + patient_overall"，实际被考的是**用极少分割掩码撬动大量粗标签的标签工程**：
1. **数据结构**：2019+ 例 study 只有"哪些椎骨骨折"的 study 级标签；仅 **87 例**有 3D 分割掩码；8 个预测列（C1–C7 + overall）。
2. **主骨架 = 三阶段标签传播**：① 在 87 例上训 3D/2D 分割（并伪标签全量 2k 例）→ ② 用掩码裁剪/可见性把 study 标签传播到切片或椎骨级，训练逐椎骨分类 → ③ 序列模型聚合成 8 列，并专门建模 patient_overall。四强全部如此。
3. **骨折 bbox 标签被全员弃用**：3rd 明说不用 fracture bounding boxes，只用分割的框与体积比——中间监督选择"覆盖广、可伪标"的分割，而非"语义最贴近"的骨折框。
4. **3D vs 2.5D 的实证分歧**：1st 在椎骨 cube 上训 3D CNN 失败 → 2.5D CNN+LSTM；6th 用 X3D-L（64×288×288，z-stride=1）成功。成败在**采样设计**（是否保 z 分辨率），不在"3D 行不行"。
一句话：**这是一场标签工程比赛**——分割、可见性、体积比都是为"把 8 列标签拆到可训练的粒度"服务的；模型差异其次。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 数据规模 | 2019+ studies（2k）；**仅 87 例**有 3D 分割；8 个预测列 | 数据帖/1st |
| 1st 样本扩张 | 2k × 7 = **14k** 椎骨样本；每椎骨 15 切片 ×5ch + 掩码通道 | 1st |
| 1st 分割 | 128³；resnet18d + effv2s，各 5 折；7ch 输出 | 1st |
| 1st 分类 | type1：effv2s(512²) 5 折、convnext-tiny(384²) 5 折；type2：convnext-nano(512²) 5 折、pico/tiny/nfnet-l0 各 2 折 | 1st |
| 1st 提交耗时 | **7.5 小时** | 1st |
| 3rd 传播 | ratio = 切片椎骨体积 / 该椎骨最大体积；× study 骨折标签 → 切片级标签 | 3rd |
| 3rd 训练 | 窗口 32×3；batch 48（accum 16）；~9h/折；长 study 压缩至 192×3 | 3rd |
| 3rd 集成/推理 | resnest50d×6 + seresnext50×4 权重；推理 **4.5h** | 3rd |
| 3rd 失败配置 | Transformer 无效（attention-over-RNN 有效）；undersampling 无效 | 3rd |
| 5th 速通 | 全流程 **11 天**；stage2 输入 (3,3,H,W)；推理放大 ≥1.125 + center crop | 5th |
| 5th stage3 增益 | 30-70 融合（stage2 max 聚合 vs stage3）→ **+2–3 LB** | 5th |
| 6th 伪标链 | (64,288,288) → (432,64,9,9) → (64,9,9) → (64,) → 原始切片数；阈值 0.5 | 6th |
| 6th CV | 3D CNN 7×432：0.3205；TD-CNN 7×256：0.3369；融合 7×688：**0.2962**；权重 0.25/0.25/0.5 | 6th |
| 6th 训练 | 分割 192³；3D 分类 64×288×288（z-stride=1）；2D 预训 288²；端到端 32×288×288 | 6th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st haqishen | 3rd darraghdog | 5th Speedrun | 6th i-pan |
| --- | --- | --- | --- | --- |
| 分割/定位 | 3D 语义分割 128³，r18d / effv2s + UNet，7ch；预测全量掩码 | EffNetV2 回归外接框 + have_bbox；study 级单框裁剪 512²（z 轴 rollmean） | 2D 可见性分类 + 2D 分割（87 例）；0.05/0.95 分位聚合 study 框 | 3D DeepLabV3+（X3D）192³；伪标全量 |
| 标签传播 | 掩码裁 7 椎骨 → 每椎骨单二值标签（2k×7=14k 样本） | 体积比回归（切片/最大体积）→ 乘 study 骨折标签得切片级标签 | 可见性×overall → 2D 切片伪标签 | CAS（分类激活序列）→ 切片伪标签；分割伪标 |
| 序列输入 | 每椎骨 15 切片均匀采样；每片 5ch（中心±2）+ 掩码=6ch | 32×3 切片窗口；study 单框；长序列压缩到 192×3 | 2.5D（3ch）+ 间隔帧 ±5 → (3,3,H,W) | 每椎骨 64 深 ×288×288；study=7 序列 |
| 逐椎骨/切片模型 | 2D CNN（effv2s/convnext-tiny）+ LSTM（type1） | 2.5D CNN+1D RNN（resnest50d/seresnext50）+ attention | 2.5D+3D 混合轻量 effv2 | X3D-L（z-stride=1）+ TD-CNN |
| patient_overall | type2：7×15=105 图联合输入（convnext nano/pico/tiny、nfnet-l0） | model3 study 级微调，直接用竞赛指标损失 | **stage3 FFN**（mean/min/max 输入，直接优化竞赛指标） | 3 段 Transformer：7×432 / 7×256 / 7×688 融合（0.25/0.25/0.5） |
| 集成 | 分割 2 系 ×5 折 + type1 2 系 + type2 4 系 | 10 权重（resnest50d×6 + seresnext50×4） | 30–70（stage2 max 聚合 vs stage3） | 三路输出加权 |
| 训练/推理成本 | 提交 7.5h | ~9h/折；推理 4.5h | 11 天完成全流程 | 2D 预训 288² → 冻结微调 → 端到端 32×288×288 |
| 失败清单 | 椎骨 cube 上的 3D CNN | Transformer、undersampling、骨折 bbox（弃用） | —（速通无消融） | mask 当通道、遮非分割区、切片级特征+2D CNN |

### 共识 / 分歧 / 裁决
**共识一：三阶段骨架（分割/定位 → 椎骨/切片分类 → study 聚合）4/4**
1st：3D 分割→椎骨裁剪→type1/type2；3rd：框→切片标签→model1/2/3；5th：可见性+分割→切片伪标签→聚合 FFN；6th：分割→3D CNN 特征→TD-CNN/Transformer。

**裁决**：8 列逐椎骨标签 + study 级粗标签的结构，要求显式引入"椎骨身份"作为中间变量；任何端到端 study 分类都缺归因路径。置信度：高（4 队结构一致 + 1st/3rd 明确失败例）。

**共识二：骨折 bbox 弃用、分割优先（3rd 明说，4/4 实际未用）**
3rd："I did not use the fracture bounding boxes, and only used high level data from the segmentation maps"；
1st/6th：用分割掩码裁剪/通道/伪标；5th：用分割框 ROI。

**裁决**：中间监督的选择标准是"覆盖面 × 可伪标性"而非"语义贴近度"——分割只有 87 例却可通过伪标签覆盖 2k 例，且提供形状先验；骨折 bbox 覆盖与质量不足以支撑全量训练。置信度：中高（四队一致，但 3rd 外无直接消融）。

**共识三：patient_overall 必须专门建模（4/4 结构差异，方向一致）**
1st：type2 把 7 椎骨×15 切片联合输入（105 图）学 overall；5th：stage3 FFN 直接优化竞赛指标（+2–3 LB）；6th：Transformer 输出 8 列；3rd：model3 用竞赛指标损失微调。

**裁决**：overall 不是 C1–C7 的 max/any 的简单函数（列 log-loss 需要校准的联合概率）；需要专门的聚合模型与损失。置信度：高（5th 有量化增益）。

**共识四：伪标签把 87 例扩到全量（3/4 明说）**
1st：预测全部 2k 掩码；5th：threshold 0.5 可见性 × overall；6th：分割伪标 + CAS 伪标（明确不用官方 image-level 标签）。

**裁决**：小标注子集 → 全量的伪标签扩张是标准操作；关键是伪标来源模型要足够干净（1st："87 例足够训练出好分割"）。置信度：高。

**分歧一：3D CNN vs 2.5D+RNN（本场最大实证分歧）**
1st：在椎骨 cube 上训 3D CNN"did not give satisfactory results" → 退回 2.5D（5ch 切片）+LSTM；
6th：X3D-L 3D CNN 直接成功（64 深 ×288×288，**z-stride 全部改为 1**）；
4th（未收录正文）：标题"CSN is all you need for 3D"；
3rd：2.5D+1D RNN + attention；5th：2.5D+3D 混合（近邻 3 帧 + ±5 间隔帧）。

**裁决**：这不是"3D 行不行"的问题，而是**采样设计**：6th 保 z 分辨率（stride=1）+ 高 xy 分辨率 + 64 深度；1st 的失败配置是小 cube 3D CNN。5th 的混合结构（不同 z 间距的多帧堆叠）是折中解。置信度：中（各队单点经验，但方向可解释）。

**分歧二：序列模型——RNN/attention vs Transformer**
3rd：attention 加在 RNN 输出上"helped a lot"，Transformer 无效；
1st：LSTM；
6th：study 级用 3 层 Transformer（三路融合，CV 0.2962 最佳）；
5th：stage3 FFN。

**裁决**：层级不同——切片/椎骨级序列（几十步、强局部性）用 RNN+attention；study 级 7 步序列（椎骨间关系）用 Transformer 有效。把两处结论互斥是"层级混淆"。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 全结构（分割/type1/type2） | **自述 + 全 notebook 公开** | 高（可复现） |
| 3rd 三模型 + 10 权重集成 | 自述 + 代码 + slides + 视频 | 中高 |
| 5th stage3 +2–3 LB | 自述 + 视频/代码 | 中高 |
| 6th 三路 CV（0.3205/0.3369/0.2962） | 自述 + 代码 | 中高 |
| "3D CNN 失败"（1st） | 单队经验（配置依赖） | 低-中（与 6th/4th 冲突） |
| attention 有效 / Transformer 无效（3rd） | 单队经验 | 低-中（层级混淆） |
| 数据帖的转置/翻转公式 | 社区验证 + 官方引文 | 中高 |
| 骨折 bbox 弃用 | 四队行为一致，3rd 明示 | 中（无消融） |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **4th "CSN is all you need for 3D"（364837）未收录**：与 1st"3D CNN 失败"直接冲突，是本场最重要的待裁决张力（3D 采样设计的又一个数据点）。
2. **2nd "Segmentation + 2.5D CNN + GRU Attention"（365115）未收录**：与本次四强的序列模型变体对照缺失。
3. metric weights 帖（340392，65 票）未收录：加权列 log-loss 的权重细节直接影响所有校准决策（3rd/5th 的损失设计）。
4. 8th/32nd 未收录；3D renderings/vertebrae detection 等工具帖未收录。

**失败学（跨队合集）**

- 模型类：椎骨 cube 上的 3D CNN（1st）；Transformer 替代 RNN（3rd）；切片级特征 + 2D CNN（6th）。
- 数据类：mask 当额外通道（6th 列为无效——与 1st 用 mask 通道有效相反，说明配置依赖）；遮掉非分割区（6th）；undersampling（3rd）；骨折 bbox（全员弃用）。
- 组织类：速通依赖复用；无复用则 11 天不可行。

### 出处
- 1st（haqishen，222 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/362607
- 数据详解（179 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/340612
- 1st code（147 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/362787
- 3rd（darraghdog，59 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/362643
- 6th（i-pan，59 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/362651
- 5th Speedrun（51 票）：https://www.kaggle.com/competitions/rsna-2022-cervical-spine-fracture-detection/discussion/363232
- 缺口登记（未收录正文）：2nd(365115)、4th(364837)、8th(362669)、32nd(362593)、metric weights(340392)、3D renderings(350244)、anatomy(340439)、vertebrae detection(348241)

### 外部题解（kaggle-solutions）
- rank 2｜code：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/365115
- rank 4｜code：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/364837
- rank 7｜code：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/364848
- rank 8｜code：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/362669
- rank 10｜description：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/362986
- rank 12｜description：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/362844
- rank 13｜description：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/362687
- rank 14｜description：https://www.kaggle.com/c/rsna-2022-cervical-spine-fracture-detection/discussion/362771

---

## rsna-2023-abdominal-trauma-detection — RSNA 2023 Abdominal Trauma Detection 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 RSNA Trauma Metric ｜ 队伍 1125 ｜ 截止 2023-10-15 ｜ Tier B ｜ 标签 cv,detection,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-2023-abdominal-trauma-detection.md
> 材料基础：`digests/rsna-2023-abdominal-trauma-detection.md`（6 篇正文：1st 447449 / 2nd 447453 / 10th 447450 / 3rd 447464 / 往届汇编 427233 / PNG 数据 427427；80 条主题索引）+ 7 张图

### 一句话重述
腹部 CT 多器官损伤检测（肝/脾/肾/肠/造影剂外渗，多标签 + 患者级）。真正的考点是**两段式：3D 分割 → 器官裁剪 → 2.5D+RNN 分类**，以及**用器官可见性做软标签/帧采样**来压制标签噪声。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（Team Oxygen） | 三部分：3D 分割出 masks/crops → 2.5D CNN+RNN（肾/肝/脾/肠）→ 另一路（肠+extravasation）；4 折 **患者级 GroupKFold**；384²；96 层 → (32,3,H,W) 2.5D；**软标签 = 患者级标签 × 器官可见度**；共享编码器 + 辅助分割损失（**+0.01~0.03**）；Coat Lite M/S + EffNetV2s + GRU；切片级 max 聚合；最佳单模 OOF **0.326**、集成 0.31x | 1st |
| 2nd（TheoViel） | 2D 模型 + RNN：先用 EffNetV2 判"每帧有哪些器官"来控制**帧采样**（正肠/外渗用帧级标签，其余随机）；器官 crop 模型（3D ResNet18 裁剪 → 2D CNN+RNN）；RNN 直接优化比赛指标（器官条件池化 + 每器官独立 logits）；11 类（肠/外渗 BCE + 肾/肝/脾 healthy/low/high CE）；重增广 + cutmix；`dicomsdl` GPU 流水线 <4h | 2nd |
| 3rd | 3D 分割（Qishen 代码）→ 器官 cube → 多配置 2.5D+3D 分类；**关键：肝 mask 输入、按器官分 batch 的 custom sampler、两种 crop 尺寸**；跨器官相关性用多类目标 | 3rd |
| 事件 | 截止延期引发 2nd 公开不满（"unjustified deadline extension"）；PNG 数据资源（174 票） | 2nd+主题索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd |
| --- | --- | --- | --- |
| 分割→裁剪 | 3D seg masks + 研究级 crop | 3D ResNet18 器官 crop + 2D 器官分类控帧 | 3D seg（res18/50 平均）+ 两档放大 crop |
| 2.5D 序列 | 96 层→32×3 通道 | 1/2 帧、≤600 层、3 邻帧 | 15 帧×3 通道、分辨率对齐 |
| 标签设计 | 患者标签×可见度软标签 | 可见性分类器 + 帧级标签 | 多类（跨器官相关性） |
| 聚合 | 切片 max → 患者 | RNN（Dense+LSTM+max/avg/attention）+ 每器官 logits | 多种 neck（pooling/LSTM/GRU） |
| 损失 | BCE + Dice（辅助） | BCE + CE（11 类） | 多目标 |
| 骨干 | Coat/EffNetV2 + GRU | MaxVit/ConvNextV2/CoatNet + RNN | ConvNext/SE-ResNeXt/MaxVit/CaFormer/XCiT |

### 共识 / 分歧 / 裁决
**共识一：分割→裁剪是标准骨架（3/3）**
1st 用 3D 分割做研究级 crop；2nd 用 3D ResNet18 裁器官并喂 crop 模型（"对肾/肝/脾提升明显"）；3rd 用分割 cube + 两档 crop。**裁决**：先把器官定位/裁剪，再做损伤分类——医学 3D 分类的通用降噪结构。置信度：高。

**共识二：用"器官可见性"处理切片级标签噪声（1st/2nd/3rd）**
1st：软标签=患者标签×可见度；2nd：可见性分类器控制帧采样；3rd：mask 输入（肝）与分器官 batch。**裁决**：多标签切片任务里，"这一帧里器官是否存在/可见"是必须建模的中间变量。置信度：高。

**共识三：2.5D + 序列聚合（RNN/GRU）优于纯 3D（3/3）**
三队都是"2D CNN + RNN/GRU/LSTM"为主，3D 只用于分割/裁剪。**裁决**：算力/数据条件下 2.5D+序列模型是性价比最优。置信度：高。

**共识四：辅助分割损失/多任务稳定训练（1st 明证）**
1st：共享编码器 + 辅助分割损失 +0.01~0.03；2nd/3rd 也训练分割与分类的多任务。**裁决**：辅助任务提供空间正则，是小数据医学赛的稳定器。置信度：中高。

**分歧一：聚合器设计**
1st 简单 max 聚合；2nd 用重调 LSTM + 器官条件池化直接优化指标；3rd 试多种 neck。**裁决**：简单聚合已很强，RNN 的增益来自"按器官条件化 + 直接优化指标"；复杂度需消融。置信度：中。

**分歧二/事件：规则变更（截止延期）**
2nd 公开抱怨延期改变竞争结果；1st 与 2nd 的竞争持续到最后一刻。**裁决**：规则中途变更对参赛者体验与结果可信度伤害大；登记为治理事件。置信度：高（事实）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的软标签/辅助损失/分数 | 自述 + 图 + 代码 | 中高 |
| 2nd 的帧采样/RNN 设计 | 自述 + 管道图 + 代码 | 中高 |
| 3rd 的关键三招（mask/sampler/crop） | 自述 | 中 |
| 截止延期争议 | 2nd 公开帖 | 高（事件） |
| 各队分数（0.31x/0.326） | 自述 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th–9th 方案未收录；"Clarification on Provided Labels/Annotations"（78 票）与"prompt based prediction"（85 票）未收录。
- 延期对最终名次的具体影响不可量化；2nd 的完整消融未细读。
- PNG 数据（174 票）与往届 RSNA 汇编（427233）未细读。

### 图证（KStarter 仓库内路径）
- ../../intel/rsna-2023-abdominal-trauma-detection/bodies/447453_img/01.png — 2nd 的两段式管线

### 出处
- 1st（447449）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/447449
- 2nd（447453）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/447453
- 10th（447450）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/447450
- 3rd（447464）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/447464
- 往届汇编（427233）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/427233
- PNG 数据（427427）：https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/discussion/427427

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447848
- rank 6｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/448208
- rank 7｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447549
- rank 8｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447706
- rank 9｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447506
- rank 12｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447539
- rank 14｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447553
- rank 16｜description：https://www.kaggle.com/c/rsna-2023-abdominal-trauma-detection/discussion/447448

---

## rsna-2024-lumbar-spine-degenerative-classification — RSNA 2024 腰椎 MRI 深读：两阶段定位 × 级联误差吸收 × 按条件拆模型

> 主题 cv ｜ 类别 Featured ｜ 指标 RSNA Lumbar Metric 71549 ｜ 队伍 1874 ｜ 截止 2024-10-08 ｜ Tier A ｜ 标签 cv,classification,generative,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-2024-lumbar-spine-degenerative-classification.md
> 材料基础：`digests/rsna-2024-lumbar-spine-degenerative-classification.md`（1st/2nd/3rd/4th 四篇完整方案 + starter 阅读清单 + 124 票实验占位帖；80 条讨论索引）+ 20 张图（539443×3 / 539452×3 / 539453×5 / 540091×9）

### 一句话重述
题面是"腰椎 MRI 每个椎间盘层面、每类病变的严重度三分类"，实际被考的是**一条级联流水线的系统工程**：
1. **解剖定位先于分级**：25 个评分列（5 层面 L1/L2…L5/S1 × [scs, nfn_l, nfn_r, ss_l, ss_r]）都锚定在"哪一层面、哪一侧、椎管在哪"上；四强全部采用"定位 → 裁剪 → 分级"两阶段，没有一队把 25 列当纯多标签问题硬训。
2. **第一阶段误差是第一风险**：1st 实测层面预测 ±0 只有 67–71%（sagt2/scs），约 30% 样本带 ±1 误差；因此收益最大的工程不是换更强分类器，而是让分级模型**见过定位误差**（1st 的 instance_number 随机位移 ±2 被作者称为 crucial；3rd/4th 用伪标签与关键点归一化压缩误差影响）。
3. **按条件拆模型**：SCS 的最佳视角（sagT2 + axial）、NFN（sagT1）、SS（axial）不同；"每个条件一组独立子模型 + 条件特异融合"是四强的共同形态（1st 三类 severity 模型、3rd Center/Side 双分类器、2nd 逐目标独立、4th condition-separated pooling）。
一句话：**这是一场"先修坐标、再修分级"的比赛**——分类器只是流水线的最后一环；分差主要来自定位鲁棒性、标注噪声处理与集成结构，而非 backbone 选择。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| instance_number 精度（sagt2/scs） | cls：±0 **71.08%** / ±1 27.04% / ±2 1.43% / >±2 0.44%；reg：67.48% / 30.59% / 1.61% / 0.31% | 1st |
| 1st 提升阶梯 | 2.5D 0.37 → attention MIL 0.35 → +bi-LSTM+aux+ensemble **0.33**（public LB） | 1st |
| 1st 误差吸收 | instance_number 位移 ±2（概率按误差分布）、xy ±10px、crop 后几何增强 p=0.5 | 1st |
| 1st 训练预算 | convnext-s **7 epoch** / effv2-s **14 epoch**；每任务 5 fold | 1st |
| 1st 裁剪配方（像素） | scs sagt2 96/32/40/40；nfn sagt1 96/64/32/32；axial 右 144/48/96/96、左 48/144/96/96；axial 加 ±20 抖动 | 1st |
| 2nd 噪声清洗 | ensemble OOF CV **0.3687**；阈值 \|Δ\|≥0.8；公/私榜各 **+1%** | 2nd |
| 2nd 后处理 | 每例 5 层面 spinal-severe 最大值 **×1.25** | 2nd |
| 3rd 集成 | 单模型 CV **0.3858** → 30 模型平均 **0.3643** | 3rd |
| 3rd 训练配置 | CE 权重 [1.0, 2.0, 4.0]；lr 2.5e-5 + OneCycleLR（warmup 3/10）；batch 2–8；drop_path 0.2/0.3 | 3rd |
| 3rd 输入 | sagT1/sagT2 各 15 片 + axial 10 片；数据倍率 5×（弃层面）/ 10×（再弃侧别） | 3rd |
| 3rd 后处理 | SCS 温度 **0.91**（图 6 另见第二参数 lr_t≈0.95–0.97） | 3rd |
| 4th 输入/融合 | 30×128×128 ×2 序列 + 5×128×128 ×2；每片 512 维；Nelder-Mead MLP + 每层 LGBM/XGB（输入维=模型数×3） | 4th |
| 1st CV/LB 背离 | MIL 的本地 CV 增益小于 LB 增益（无数字） | 1st 评论区 |
| 赛事规模 | 1874 队；25 个评分列 | 赛事元数据/结构 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st NANACHI | 2nd yujiariyasu | 3rd Moyasii | 4th tattaka+yu4u |
| --- | --- | --- | --- | --- |
| 总体结构 | 2 阶段 3 模型：instance_number→coordinate→severity | 轴/矢独立 + 每目标独立小模型（无共享定位网络） | 2 阶段：关键点定位+层面分配+crop → Center/Side 分类 | 关键点检测→裁剪→4 分级子模型→stacking |
| 定位方案 | sag：3D ConvNeXt 双任务（cls+reg）预测 instance_number；2D 回归坐标；axial 借 hengck23 | slice 分类（hengck23）+ YOLOX 区域（brendanartley 数据训练） | CenterNet：层面 EffNetB6+FPN、椎管 EffNetB4+FPN；世界坐标推 L1/S1 伪坐标 | 轴：2.5D+LSTM 分层面→UNet 左右关键点；矢：2.5D 找孔区左右切片 + 关键点；STIR 取中片 |
| 坐标标签源 | brendanartley 坐标数据集（预训练，优于 ImageNet 初始化） | brendanartley 共享数据训 YOLOX | 社区 Coordinate Pretraining Dataset + 伪标签全量化 + 人工审标 | 共享 Lumbar Coordinate Dataset |
| 分级输入 | 按条件裁剪 5 切片：scs=sagt2/axial，nfn=sagt1/axial，ss=axial | 5 切片 MIL；sag 以预测层面为中心，孔区用 spinal/subarticular 中间切片；axial ±2 切片 | sagT1/sagT2 各 15 片 + axial 10 片等间隔；axial 以椎管中心裁剪 | 多视角组：30 片组 + 5 片组；crop 边长=相邻关键点距×2 |
| 分级架构 | 1ch encoder→bi-LSTM→attention MIL；aux depth + 共享权重 aux class → concat 主头 | ConvNeXt-S + MIL(5 图) | 2D encoder + slice attention；Center/Side 双分类器（两组头结构做多样性） | 2D backbone→Transformer→condition-separated attention pooling + aux loss；单条件 2.5D CNN |
| 鲁棒化手段 | instance shift ±2（按各模型误差概率）+ xy ±10px + 几何增强 | label noise 剔除（\|Δ\|≥0.8）+ 左右半图统一 | Split LR 右翻转、弃层面/侧别独立样本（5×/10×）、伪标签、TTA | 关键点距离归一化、不足 30 片 padding、超 30 片插值 |
| 集成 | 5 fold × 2 任务；instance 用 median、coordinate 用 mean | 队员模型加权平均 | 30 模型平均（15 Center + 15 Side） | Nelder-Mead MLP + 每层独立 LGBM/XGB；nfn 输入拼接 scs/ss/nfn |
| 后处理 | — | spinal 最高 severe 值 ×1.25 | SCS logits 温度 0.91 | — |
| 报告数字 | 0.37→0.35→0.33（public LB） | OOF CV 0.3687；噪声清洗公/私榜各 +1% | CV：单模型 0.3858 → 30 模型 0.3643 | CV 与 LB 相关性好（未给数） |
| 失败清单 | Mamba/自注意力、aux 权重共享、错视角组合、长 epoch、大模型、ViT | 正文未列 | 一阶段、多层面多病种、按层面、按侧、3D-CNN、2.5D+Attn、2D+LSTM、Focal、长 epoch | 正文未列 |

**视角-条件匹配表（跨队归纳）**：scs→sagT2/STIR + axial；nfn→sagT1（+axial 侧向裁剪）；ss→axial。1st 明确验证"sagt1 给 scs、sagt2 给 nfn、sagt1+sagt2 给 ss"等组合无效。

### 共识 / 分歧 / 裁决
**共识一：两阶段"定位→裁剪→分级"（4/4）**
1st 把阶段一拆成 instance_number + coordinate 两类模型落盘 `test_label_coordinates.csv`；2nd 用 slice 分类 + YOLOX 区域；3rd 用两个 CenterNet 分别找层面与椎管；4th 用关键点检测 + 距离归一化裁剪。**没有队伍端到端直接出 25 列。**

**裁决**：多部位医学影像的第一性结构是"先解决在哪，再解决多严重"；端到端会让"层面身份"与"病灶程度"在特征空间中纠缠。置信度：高（4 队一致 + 1st/3rd 明确把一阶段列入失败清单）。**保留张力**：7th 标题宣称单阶段可行（未收录正文，T13 候选）。

**共识二：第一阶段误差必须被"吸收"，而不只是被压低**
1st：±0=67–71%、±1≈27–31% → 训练时按误差分布随机位移 instance_number（±2），作者称 crucial for robustness；
3rd：伪标签用尽全部数据 + 手工校标 + 世界坐标几何分配（伪算 L1/S1）；
4th：关键点回归 + 距离归一化裁剪，把个体尺度差从输入中消除；
2nd：slice 分类 + YOLOX 区域，用检测框兜住解剖结构。

**裁决**：级联系统的期望损失由 `P(定位误差) × 分级敏感度` 决定；只优化定位器会撞上标注与解剖的噪声上限。三族有效解：① 把误差分布注入训练（1st 位移增强）；② 用伪标签/多假设覆盖（3rd）；③ 用坐标归一化让分类器对误差不敏感（4th）。置信度：中高（1st 有数字，其余为结构性证据）。

**共识三：按条件拆子模型（4/4，粒度不同）**
1st：scs/nfn/ss 三套 severity 模型，输入通道不同（各条件专属裁剪表）；
3rd：Center Classifier（SCS）+ Side Classifier（NFN/SS），Split LR 统一左右；
2nd：逐目标独立模型，non-spinal 只用左/右半图；
4th：同一 backbone 上每条件独立 attention pooling 头 + 条件特异 stacking 输入。

**裁决**：多部位多任务的最优分解粒度≈标注/视角结构；统一多头会把不同视角的信息互相干扰（3rd 的"多层面多病种"失败清单）。置信度：高（4 队形态一致）。

**分歧一：MIL vs 2.5D vs Transformer——到底谁赢？**
1st：attention MIL 使 LB 0.37→0.35，2.5D 较差；但作者在评论中承认 **MIL 的本地 CV 增益小于 LB 增益**；
3rd：失败清单同时列 2.5D+Attention 与 2D+LSTM，但它自己的分类器是"2D encoder + slice attention"（单样本内 15+15+10 片聚合，不是跨示例 MIL bag）；
4th：两种并存——多视角 Transformer（条件分离 pooling）与单条件 2.5D CNN（作者称其他视角组合"no significant results"）。

**裁决**：争的不是"MIL 三个字母"，而是聚合三件套：**切片集合 → attention 聚合 → 辅助监督**。同一结构名在 3rd 失败、在 1st/4th 成功 → 成败绑定到实现配置（切片数、聚合位置、aux 头）。1st 的 CV/LB 背离提示 MIL 收益可能含公榜红利（对照 L6/T3），复现须先做 CV 无泄漏审计。置信度：中。

**分歧二：模型规模与训练时长——小模型共识**
1st：convnext-large < base < small；ViT 全面弱于卷积；7 epoch（effv2s 14）；
3rd：10–20 epoch；ResNet18/MNasNet/EffNet-B4/ConvNeXt-N/T/MaxViT-N 集成；长 epoch 进失败清单；
2nd：ConvNeXt-S；4th：tiny 级 backbone（caformer_s18 / convnext_tiny / resnetrs50 / swinv2_tiny / maxxvitv2_nano）。

**裁决**：数据规模 + 标注噪声限制了容量收益；小模型 + 强增强 + 异构大集成的期望分数更高。置信度：高（4 队一致）。

**分歧三：标注噪声的处理路径**
2nd：teammate 发现噪声 → 用 ensemble OOF（CV 0.3687）剔除 \|label−pred\|≥0.8 的样本（对 moderate/severe 加系数）→ 公/私榜各 +1%；
3rd：社区讨论暴露 label noise → 人工复查并修正全部标注。

**裁决**：噪声真实存在（两队独立确认），两条路径都有效；自动阈值更快，但会把"难而正确"的样本混入删除集；人工审查更干净但不可扩展。任何自动清洗都必须在 CV 与 LB 双侧验证（2nd 恰为双侧 +1%）。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 0.37→0.35→0.33（LB 阶梯） | 自述（notebook 公开，可复现） | 数字具体，但为 public LB；作者自认 CV 增益更小 |
| instance_number 误差表（71.08/67.48…） | 自述（细到 ±2 分桶，内部自洽） | cls/reg 双任务对比清晰 |
| 3rd 30 模型 CV 0.3643 / 单模型 0.3858 | 自述 + 代码开源 | 结构可复现 |
| 2nd 噪声剔除 +1% | 自述（无系数/占比细节） | 阈值 0.8 与类别系数的标定未公开 |
| 标注噪声存在 | 两队独立证词（2nd/3rd） | 中高，但"噪声占比"无数字 |
| Split LR（2×/10× 数据） | 3rd 自述 + pipeline 图 + 结构校验 | ✓ |
| 7th "单阶段可行" | 仅标题（正文未收录） | 低，登记悬案 |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **7th "Single Stage Model Wins!"（539439，35 票）与前三名"one-stage 失败"冲突**——正文未收录（不扩采约束），无法裁决：是单阶段配合了更强的内部定位头？还是两阶段蒸馏成单阶段？登记为后续选择性补读候选（同时登记 T13 候选张力）。
2. 1st 的 CV/LB 背离（MIL 的 CV 增益 < LB 增益）：是公榜过拟合还是 CV 划分差异？作者未解释 → 复现时须先做 CV 无泄漏审计（对照 L6/T3）。
3. 2nd 噪声清洗细节（系数/阈值标定/被删样本占比）未公开，+1% 不可复算。
4. 4th 的 stacking（Nelder-Mead MLP + 每层 LGBM/XGB）相对简单平均的增益无消融数字；评论区里的 CV 具体值在存档文本中丢失。

**失败学（跨队合集）**

- 结构类：一阶段、多层面多病种、多层面单病种、按层面专用、按侧专用（3rd）；Mamba/自注意力替代 bi-LSTM、aux 层权重共享、错视角输入组合（1st）。
- 训练类：长 epoch、Focal Loss（3rd）；大模型、ViT（1st）。
- 提示：同一结构名（2.5D+Attention、2D+LSTM）在 3rd 失败、却在 1st/4th 变体成功 → 失败学要记录到**配置级**（切片数、聚合位置、aux 拓扑），否则不可迁移。

### 图证（KStarter 仓库内路径）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/540091_img/01.png — 1st 的 3 模型 2 阶段总管线（topic 540091）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/540091_img/08.png — 1st 的 SCS 分级模型：bi-LSTM + Attention MIL + 双流 aux（topic 540091）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/539453_img/01.png — 3rd 的完整两阶段管线（topic 539453）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/539443_img/02.png — 4th 的多视角多条件模型：Transformer + condition-separated attention pooling（topic 539443）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/539452_img/01.png — 2nd 的轴向 YOLOX 区域检测（topic 539452）
- ../../intel/rsna-2024-lumbar-spine-degenerative-classification/bodies/539453_img/05.png — 3rd 的后处理参数搜索：Optuna slice plot（topic 539453）

### 出处
- 1st（NANACHI，105 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/540091
- 2nd（yujiariyasu，98 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/539452
- 4th（tattaka + yu4u，76 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/539443
- 3rd（Moyasii，65 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/539453
- Starter 阅读清单（137 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/503433
- [placeholder] 参考论文（124 票）：https://www.kaggle.com/competitions/rsna-2024-lumbar-spine-degenerative-classification/discussion/519628
- 未收录方案帖（缺口登记）：539472 / 539439 / 539486 / 539548 / 539690 / 539459 / 541279（7 条 write-up 候选，见 §8 悬案 1）

### 外部题解（kaggle-solutions）
- rank 5｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539472
- rank 6｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/541813
- rank 7｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539486
- rank 8｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539548
- rank 9｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539690
- rank 11｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539569
- rank 12｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/540001
- rank 13｜description：https://www.kaggle.com/c/rsna-2024-lumbar-spine-degenerative-classification/discussion/539510

---

## rsna-breast-cancer-detection — RSNA 乳腺 X 光筛查深读：不确定指标下的选择游戏

> 主题 cv ｜ 类别 Featured ｜ 指标 Probabilistic F-Score Beta (Micro) ｜ 队伍 1687 ｜ 截止 2023-02-27 ｜ Tier A ｜ 标签 cv,detection,medical,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-breast-cancer-detection.md
> 材料基础：`digests/rsna-breast-cancer-detection.md`（8 节：1st/2nd/4th/6th/9th + 乳腺影像入门 + 往届 RSNA 索引 + 硬件实验帖）+ 19 张图（含 3 张 SVG 结构图）

### 一句话重述
题面是"由乳腺 X 光预测癌症"，实际被考的是**在极端不平衡 + 不稳定的概率化指标下，把"数据侧工程 + 阈值/选择"做对**。降解为 5 步：
1. **数据侧工程决定天花板**：DICOM 窗宽窗位 → ROI 裁剪（YOLOX/Faster R-CNN/cv2）→ 分辨率与重采样方法（PIL-Lanczos）→ 多视角/多侧位组织；分辨率与外部正样本是两张大牌；
2. **极不平衡的训练配方**：正样本上采样/平衡采样（众数做法 1:7~1:8、保证每批 ≥1 正样本）+ BCE/EQL 损失 + drop 0.5~0.9 + EMA/大 batch；
3. **外部数据（正样本库）**：1st 用 5 个公开数据集把阳性率从 ~0.5% 拉到 7.38%，F1 +0.02；但 4th/6th 报告"无清晰收益"——用法（预训练 vs 混训）与数据质量决定成败；
4. **pF1 不稳定 → 用代理指标管实验**：PR_AUC/AUCPR/ROC/阈值曲线并行跟踪；损失用 AUCPR/EQL 等不平衡友好目标；
5. **最终选择游戏**：阈值网格（1st 的 0.27–0.40）、模型 vs 集成的取舍（2nd 选高分辨率单模、6th 把私榜最好方案留在场外）、稳 vs 高的取舍（9th 用投票版换稳定性）——**最后一次提交的决策与模型训练同样值钱**。
一句话：**这是一场"数据清洗 + 阈值选择"的比赛**——冠军自己说"简单流水线 + 简单决策 + 运气"，而四个落选的更好方案（2nd 的集成、4th 的 ROI 模型、6th 的私榜 0.53、9th 的高 LB 版）告诉后来者：**在这个指标下，选择纪律比模型上限更能决定名次**。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 外部数据消融（唯一严格对照） | 无外部：OOF 0.4921/0.4853、LB 0.60、PL 0.53；有外部：OOF 0.5161/0.5182、LB 0.58–0.61、**PL 0.55–0.56**（+0.02） | 1st |
| 外部数据规模 | 9,135 患者 / 34,341 样本 / 4,691 阳性（13.66%） | 1st 表 |
| 训练集阳性率 | 3 折竞品 + 全部外部 ≈ 5,560/75,400 = 7.38% | 1st |
| soft positive label vs label smoothing | 无清晰优劣（消融表 4 行对照） | 1st |
| 阈值网格（同模型 5 个阈值） | 0.27–0.40：OOF 0.4877→0.5187（0.34 峰）；LB 峰在 0.31（0.61）；PL 0.31/0.34 都为 0.55/0.53 | 1st |
| 组合选择（每折 3–7 ckpt） | 3×5×7×5 = 525 组合；OOF 最优 0.5187 vs 最差 0.4951（同一权重的选择带 = 0.024） | 1st |
| ROI 检测器对照 | YOLOX-nano 416 LINEAR：新 val AP 96.26 / Remek val 94.21（最佳权衡） | 1st |
| 分阶段分辨率（2nd） | 单视角：无外部 0.57/0.51 → 有外部 0.58/0.53；双视角 0.57/0.52；多侧位 0.52/0.53 | 2nd |
| 4th 重采样结论 | PIL-Lanczos/TF-antialias > cv2 系；全图 1152 + 训练随机裁 1024 | 4th |
| 6th 模型族对照 | MVF 1536×768 CV 0.525/公开 0.63；MV 1024×512 CV 0.493/公开 0.64；MVL 私榜 0.50（未选方案私榜 0.53） | 6th |
| 9th TTA/集成 | hflip 加权 TTA +0.03；集成 0.63/0.47；投票版 0.62/**0.50**（更稳） | 9th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st Đăng | 2nd sakaku | 4th Dieter | 6th RabotniKuma | 9th Remek&Andrij |
| --- | --- | --- | --- | --- | --- |
| 外部数据 | **5 个数据集混训**（9,135 患者/34,341 样本/4,691 阳性=13.66%） | 仅 1 阶段预训练（1280），2 阶段不用 | DDSM/VinDr **预训练无效** | 预训练/伪标签"无清晰提升" | **完全不用** |
| ROI | YOLOX-nano 416（Remek 472 框→自扩 571 图）；Otsu 兜底；全图兜底 | Faster R-CNN 紧框（去乳头）；**最终提交不裁** | 粗 CNN min-filter 去噪裁边 | 训练用 YOLOX 框（更小防过拟合）、推理用规则裁剪省时 | cv2.connectedComponents 裁框 |
| 分辨率流程 | ROI 后各向同性缩放+padding → 2048×1024 | 1280 → 1536（分阶段） | 全图压到 1152；训练随机裁 1024 | 2048 方形 → 2:1（1024×512/1536×768） | 1536×768 |
| 模型 | 4×ConvNeXt-small（4 折+外部） | ConvNeXtV1-small（mmcls）；单视角→双视角→多侧位 | EffNet B3-B5/V2S/V2M + 1D-CNN；SE-ResNeXt/ConvNeXt-tiny + DeiT（患者级） | ConvNeXt（MV/MVF/MVL 变体） | 3×ConvNeXt-small（avg/GEM 池化） |
| 损失/采样 | BCE + soft positive label（0.8/0.9）；正样本上采样 1/7，每批≥1 正 | **EQL loss** + 5 个辅助头（BIRADS/Density/困难负例/View/Invasive） | 辅助分割损失（YOLOv7/CBIS 掩码）+ 辅助分类 | AUCPRLoss + 辅助损失（age/biopsy） | BCE pos_weight 1.0–1.25；Balancer 采样 1:8 |
| 关键成绩 | OOF 最优组合 pF1 0.5187；最终阈值 0.31：LB 0.61 / 私榜 0.55 | 单视角 0.58/0.53；双视角 0.57/0.52 | 两版最高公开＝最高 CV；未披露名次 | 最佳私榜 0.53 未被选 | 集成 LB 0.63 / 私榜 0.47；投票版 0.62 / 0.50 |

### 共识 / 分歧 / 裁决
**共识一：正样本稀缺是首要矛盾，采样与损失必须围绕它设计（全员）**
1st：每 epoch 上采样正样本到 pos/neg=1/7，并**保证每批至少 1 个正样本**（"0.5 个/批时训练极不稳定"）；9th：Balancer 采样器（1:8）；2nd：EQL 损失（专为极端不平衡设计）；6th：AUCPRLoss + 平滑代理；4th：辅助损失加速收敛。**没有一家用朴素 BCE + 原始采样直接训**。

**裁决**：医学影像低阳性率场景，"每个 batch 见到正样本"是训练稳定性的底线。置信度高。

**共识二：pF1 不可直接跟踪，必须用代理指标组合（4/5 家显式）**
1st：并行跟踪 PR_AUC（稳定但对先验敏感）/ROC_AUC（稳定但乐观）/best_PF1/最佳阈值；6th：AUCPR 作代理 + AUCPRLoss；9th：probf1/ROC/精确率/召回/MCC 多指标 + 可视化误判；2nd：fold 0 的 pF1 与 CV/LB 强相关后只跑 fold 0。

**裁决**：概率化 F 指标（阈值敏感 + 类别极端不平衡）的实验管理必须靠"多代理指标 + 曲线"而非单一数字；否则每天都会在噪声里做决策。置信度高。

**共识三：ROI 裁剪是标配，但"怎么裁"分歧巨大**
1st：YOLOX-nano（小框、比例稳定），证明 DL 检测器优于规则；6th：训练用 YOLOX 小框（防过拟合），推理用规则（省时）；2nd：Faster R-CNN 紧到不含乳头；9th：cv2 连通域（因许可证从 YOLOv5 换掉）；**反方**：2nd 最终提交放弃裁剪（"乳腺大小本身是信号"，全图微涨且稳定）、4th"ROI-focused 训练无效"。

**裁决**：裁剪对训练效率与早期收益明确（省算力、聚焦纹理），但在足够大的输入下"整图/半整图"可能保留尺寸信号；是否裁剪应作为最终提交的对照实验。置信度中高。

**分歧一：外部数据到底有没有用？**
- 正方：1st 的消融（唯一严格对照）：同流水线同超参，外部数据 **OOF 与私榜都 +0.02**；2nd 用外部预训练把单视角私榜从 0.51→0.53；
- 反方：4th（DDSM/VinDr 预训练无效）、6th（伪标签/外部预训练无清晰提升）、9th（不用外部仍拿 LB 0.63）。

**裁决**：外部数据的收益取决于**用法与质量**——"混训 + 正样本丰富的病理库"（1st 的 5 库 4,691 阳性）有实证增益；"单库预训练"或"标签噪声大的库"收益不稳定。4th/6th 的负面与 1st 的正面并不矛盾（数据组合与阶段不同）。置信度中。

**分歧二：分辨率 vs 集成**
2nd 的最终选择：**放弃集成、押分辨率**（"resolution plays a crucial role"）；4th：更高分辨率"相似或更差 + 推理更慢"；6th：1536×768（MVF）私榜 0.48 vs 1024×512（MV）0.46——分辨率略优；1st：2048×1024 高分辨率 + 4 模型。

**裁决**：分辨率的收益是任务相关的（病灶像素占比极小 → 分辨率即信息量），但受限于显存/推理预算；在算力允许时"高分辨率单模 ≥ 低分辨率集成"（2nd 的明确偏好）。置信度中高。

**分歧三：平衡采样在"强模型"上失效？**
6th 明确指出："正样本加权/过采样/加权采样器……在弱模型上有效，但模型足够好后就不再有用"；1st/9th 仍把平衡采样作为配方核心；2nd 用损失层（EQL）替代采样。

**裁决**：采样与损失是同一问题的两种杠杆；当模型容量/数据质量足够时，收益从"采样"转移到"损失/后处理/阈值"。存在"弱模型靠采样、强模型靠校准"的阶段迁移。置信度中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 外部数据 +0.02（同流水线对照） | **自述（强）** | 唯一严格消融；4 行表 OOF/LB/PL 齐全 |
| 外部数据表加总 | **可复算** | 患者/样本/阳性三项加总全部吻合 |
| 阈值表与 525 组合选择带 | **可读取（帖内表）** | 同模型多阈值完整 |
| 6th 的 MV/MVF/MVL 对照 | **可读取（表）** | CV/公开/私榜三列 |
| 9th 的 TTA +0.03、集成/投票对照 | **自述** | 无重复实验 |
| 4th 的"重采样研究" | **二手文献 + 自述** | 引用论文结论 + 自家对比 |
| 2nd"分辨率 > 集成" | **自述（决策记录）** | 无消融数字 |
| 4th/6th 的外部数据无效 | **自述（负面）** | 与 1st 正面不矛盾（用法不同） |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **外部数据的收益边界**：1st 的 +0.02 是特定 5 库组合；4th/6th 的负面说明其条件性（库组合/阶段/标签口径）——没有系统消融；
2. **多视角/多侧位到底值多少**：2nd 的双视角略降公开（0.57）、多侧位私榜持平（0.53）；4th 的患者级 Transformer 与 6th 的 MVL 都没有决定性优势——"视角关系建模"的收益不稳定；
3. **阈值迁移的规律**：OOF 最优阈值与 LB 最优阈值系统性偏差方向未定论（1st 猜 LB 阈值更高，结果错在另一侧）。

**失败学（负面清单精选）**

| 失败 | 来源 | 教训 |
| --- | --- | --- |
| 正样本加权/过采样/加权采样器（强模型阶段） | 6th | 采样收益随模型变强而消失；弱模型配方不能惯性沿用 |
| Focal loss / label smoothing | 6th/9th | 分散了有效信号；vanilla BCE 够用 |
| Mixup | 2nd/6th | 影像任务无效 |
| 外部预训练（DDSM/VinDr 单库） | 4th/6th | 单库预训练收益不稳定 |
| 训练"聚焦 ROI"的模型 | 4th | 丢失乳腺整体信息；整图反而更稳 |
| 更高分辨率（无 ROI 支撑） | 4th | 相似或更差 + 更慢；分辨率收益需要 ROI/重采样配套 |
| 规则裁剪（cv2）替代检测器 | 2nd | 效果差于学习式裁剪（但推理可用作兜底） |
| 多侧位/双视角训练 | 2nd | 公开分略降；关系建模未成熟 |
| SWA/EMA、AdamW/SGD/NAdam/Lion/Lamb、层冻结、PatchGD、配对训练、元模型、伪标签、>2 视角选择…… | 9th（约 20 项） | 医学影像的"技术清单"大部分在本任务上无效；简单 CNN+TTA+集成就到 0.63 |

### 图证（KStarter 仓库内路径）
- ../../intel/rsna-breast-cancer-detection/bodies/392449_img/01.jpg — preprocess
- ../../intel/rsna-breast-cancer-detection/bodies/390974_img/03.svg — models

### 出处
- 1st（Đăng Nguyễn Hồng）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/392449
- 2nd（sakaku）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/391676
- 4th（Dieter）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/391208
- 6th（RabotniKuma 队）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/390974
- 9th（Remek & Andrij）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/390966
- 乳腺影像入门：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/369262
- 往届 RSNA 冠军索引（Radek Osmulski）：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/369103
- 硬件实验帖：https://www.kaggle.com/competitions/rsna-breast-cancer-detection/discussion/370333
- 未收录缺口（登记备查）：3rd/5th/7th/8th 等方案

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391725
- rank 5｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391979
- rank 7｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391125
- rank 8｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391041
- rank 10｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391378
- rank 16｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391133
- rank 18｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/390975
- rank 19｜description：https://www.kaggle.com/c/rsna-breast-cancer-detection/discussion/391341

---

## rsna-intracranial-aneurysm-detection — RSNA Intracranial Aneurysm Detection 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 Mean Weighted Columnwise AUCROC ｜ 队伍 1147 ｜ 截止 2025-10-14 ｜ Tier B ｜ 标签 cv,detection,ranking,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-intracranial-aneurysm-detection.md
> 材料基础：`digests/rsna-intracranial-aneurysm-detection.md`（3+ 篇正文：1st 611846 / 9th 611908 / 5th 611849 / 3rd 611856 / 4th 611893 / 临床背景 591648；80 条主题索引）+ 30+ 张图

### 一句话重述
从头部 CTA/MRA/MRI 体数据中判断"是否存在颅内动脉瘤"并给出 **13 个解剖位置**的概率（14 个独立二分类，指标是按列加权的 AUC）。真正的考点是**"用血管结构当先验，把巨大体数据压成一个位置感知的小 ROI 分类问题"**——血管分割/检测决定下限，ROI 分类器的位置建模决定上限。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（611846） | 三段式 coarse-to-fine：① **nnU-Net 粗定位**（1mm 间距、3 组血管区、Dice+CE）扫全图 → DBSCAN 去散点 → 以最大簇中心裁 140³ mm ROI；② 两个 nnU-Net 细分割（0.80×0.45×0.44mm，**Dice+CE+SkeletonRecall / Tversky+CE+SkeletonRecall(权重 3)**），仅在前景做**左-右镜像增强**（保留解剖不对称）；③ **ROI 分类器**（128×256×256）——backbone 直接用**预训练于血管分割的 nnU-Net**（比 timm 2.5D/3D 更准更快），简化解码器末块；**辅助任务：用解码器特征重建每个动脉瘤位置半径 5 像素的球**；**Vessel Region-Masked Pooling** 按 13 个血管掩码各取特征 + 全局 GAP → **Location-Aware Transformer** 建模位置间关系 → MLP；另有"整体存在性"头（全血管掩码并集池化）。**损失权重 1.0（球分割）/0.1（13 位置）/0.05（存在性）**——分类权重过大会过拟合；EMA + 4 折集成 + 左右翻转 TTA；失败兜底回退到 OOF 均值；处理时间：分割 10.65s/序列、训练 nnU-Net 14h（4090） | 611846 |
| 3rd（611856） | 两段：**YOLOv8n/m 检测血管区**（用矢状/冠状 MIP 生成的 2D axis-aligned 框，验证 mAP@0.5 >0.95；理由：动脉瘤在轴位 XY 上位置相对固定）→ 固定 3D 裁剪（90³ 或 120³ mm）→ 3D ResNet-18（timm-3d）+ **在特征图上做 14 类分类**（而非整卷池化）；默认 128³ 只得到 4×4×4 特征图、效果差 → **把部分卷积 stride 从 2 改 1** 以获得更大特征图 | 611856 |
| 4th（611893） | 14 天冲刺；分割模型学不动（Dice 卡 0.6）→ 改为 **DINOv3 ViT 回归 ROI 框坐标**（输入每患者 48 张等距切片 48×1×128×128，输出 x1/x2/y1/y2），保留 95%+ 动脉瘤位置；分类数据 54.5 万样本、正例仅 2.2k（1:250），14 标签 → 正例率约 1/1700 | 611893 |
| 9th（611908） | 三路互补：**YOLO 2.5D**（把切片 i−1/i/i+1 当 RGB；YOLOv11m 与 timm 底座自定义 YOLO）+ **3D CenterNet（2D EffNetV2-s 提取器）** + 三个元分类器（LGBM/XGB/CatBoost），最终平均；**13 个位置当作 13 个检测类**；**不做 Z 轴重采样**的 2.5D 反而 +0.02 CV（与直觉相反） | 611908 |
| 5th（611849） | 2.5D [t−1,t,t+1]；基于 host 的动脉瘤质心 ±10 切片**手工标注检测框**；YOLOv11x@1280 训练 5 折；公开全套代码 | 611849 |
| 数据侧 | 多帧 DICOM 问题（40 票）、血管分割与 NIfTI 方向相反（39 票）、两次数据更新（30/27 票）、提交变慢（33 票）——数据质量与运行时是本次额外战场 | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 4th | 9th | 5th |
| --- | --- | --- | --- | --- | --- |
| 定位方式 | **nnU-Net 分割 + DBSCAN ROI** | YOLOv8 检测（MIP 框） | **ViT 回归 ROI 坐标** | YOLO 2.5D + 3D CenterNet | 手工框 + YOLOv11x |
| 分类器 | nnU-Net backbone + 掩码池化 + Transformer | 3D ResNet-18（逐特征图分类） | ViT/DINOv3 | 元分类器集成 | YOLO 检测即分类 |
| 关键设计 | 辅助球重建（权重 1.0）+ 位置感知 | 检测框 → 大特征图 | 大 ROI 保召回 | 2.5D 不做 Z 重采样 | 质心 ±10 切片人工标注 |
| 定位精度 | 高（分割级） | mAP@0.5 >0.95 | 保留 95%+ | — | — |

### 共识 / 分歧 / 裁决
**共识一：先定位/分割，再分类（全员）**
动脉瘤只占极小体素比例且位置固定于血管；1st 的三级分割、3rd 的 YOLO 检测、4th 的 ROI 回归、9th/5th 的检测框架都是同一思路。**裁决**：3D 医学影像的多标签分类应当拆成"定位 → 局部判别"两段；端到端整卷分类在样本量/显存约束下不可行。置信度：高。

**共识二：位置信息要显式建模（1st/3rd/9th）**
1st 用 13 个血管掩码分别池化 + Location-Aware Transformer；3rd 把 14 类头挂在特征图上（保留空间对应）；9th 把 13 个位置当作 13 个检测类。**裁决**：当标签是"解剖位置"时，模型结构必须保留空间/位置对应关系，不能只做全局池化。置信度：高。

**共识三：极不平衡 + 弱信号 → 用辅助任务/检测式标签（1st/4th/5th）**
正例率低至 1/250（4th）到 1/1700（14 标签）；1st 用"重建动脉瘤球"辅助任务（权重 1.0 高于分类）避免过拟合；5th 手工补标注检测框；9th 用元分类器。**裁决**：正例稀少时，"辅助定位任务 + 检测式监督"比直接加权 BCE 更有效；分类损失权重要压低。置信度：高（1st 有明确权重实验）。

**分歧一：分割 vs 检测**
1st/3rd 走分割/检测 ROI；4th 直接回归 ROI 坐标；9th 用 YOLO+CenterNet。**裁决**：若分割模型能在时限内训好（1st 用 1000 epoch/14h），分割提供的掩码是分类器最强的结构性先验；否则 ROI 回归（4th）是更省时的替代。置信度：中高。

**分歧二：Z 轴要不要重采样**
9th 明确"不做 Z 轴重采样的 2.5D 反而 +0.02 CV"（他们花 1–2 周做 Z resize 结果更差）；1st 则把"模拟厚层"作为增强、并按间距统一处理。**裁决**：各向异性数据的"对齐 vs 忽略"需要实验裁决，直觉不可靠；把间距差异当增强是更稳的做法。置信度：中。

**事件：数据质量与运行时是隐形战场（社区）**
多帧 DICOM、方向反了的血管分割、两次数据更新、提交变慢——都被大量讨论；1st 直接剔除约 60 个问题序列并实现"异常兜底回退 OOF 均值"。**裁决**：医学影像赛要预留"数据清洗 + 失败兜底 + 推理时延"的工程量（1st 的分割单序列 10.65s，需在 2×T4 上跑完全部测试）。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的完整管线、损失权重与耗时 | 自述 + 6 张架构图 | 高 |
| 3rd 的 YOLO mAP>0.95 与 stride 修改 | 自述 + 图 | 中高 |
| 4th 的 ROI 回归与 1:250 正例率 | 自述（细节完整） | 中高 |
| 9th 的 2.5D 无 Z 重采样 +0.02 | 自述（单队反直觉结论） | 中 |
| 数据质量/运行时问题 | 多条高票讨论 | 高（现象） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/6th–8th 的方案未入库；临床背景帖（90 票）与数据更新帖未细读；
- 1st 的 13 位置 Transformer 具体超参与 4 折集成的逐项消融未给；
- 3rd 的 3D ResNet 多分辨率/多尺度集成细节未读完；
- 归档 30+ 张图：1st 的 6 张（分割流程、损失、模型总览、掩码池化、Transformer、朝向校正）为核心图证。

### 图证（KStarter 仓库内路径）
- ../../intel/rsna-intracranial-aneurysm-detection/bodies/611846_img/03.png — 1st 的 ROI 分类器结构

### 出处
- 1st（611846）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/611846
- 9th（47 票）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/611908
- 5th（54 票，含代码）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/611849
- 3rd（46 票）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/611856
- 4th（44 票）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/611893
- 临床背景（90 票）：https://www.kaggle.com/competitions/rsna-intracranial-aneurysm-detection/discussion/591648

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/1st-place-solution
- rank 2｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/2nd-place-solution
- rank 3｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/3rd-place-solution
- rank 4｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/4th-place-solution
- rank 5｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/5th-place-solution
- rank 6｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/6th-place-solution
- rank 7｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/7th-place-solution
- rank 8｜description：https://www.kaggle.com/c/rsna-intracranial-aneurysm-detection/writeups/8th-place-solution

---

## rsna-miccai-brain-tumor-radiogenomic-classification — RSNA-MICCAI Brain Tumor Radiogenomic Classification 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 Area Under Receiver Operating Characteristic Curve ｜ 队伍 1555 ｜ 截止 2021-10-15 ｜ Tier B ｜ 标签 cv,classification,science,medical,geospatial
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/rsna-miccai-brain-tumor-radiogenomic-classification.md
> 材料基础：`digests/rsna-miccai-brain-tumor-radiogenomic-classification.md`（6 篇正文：12th 279832 / 1st 281347 / 论文 252833 / 往届金牌 252838 / DICOM→PNG 253000 / 往届数据集 253056；80 条主题索引）+ 1 张图

### 一句话重述
从脑 MRI 预测 MGMT 启动子甲基化（AUC）。样本极少、信号极弱，本场真正的考题是**与验证/提交噪声作斗争**：同一模型重跑分数几乎随机，公榜大量高分是运气/作弊。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st 的噪声量化 | 同一 EF-b0 完全相同设置重训 100 次：CV 0.53–0.62；5 折平均后仍有 0.52–0.56 区间 | 1st |
| 1st 的两阶段筛选 | 每个想法先训 **100 模型（20 次×5 折）** → 前 5 想法各训 **250 模型（50 次×5 折，换折）** 排名 | 1st |
| 1st 的最终模型 | 3D ResNet10 + BCE；**无集成**；256²、bs 8、15 epochs；1 epoch≈1'20''（3090）；top1 用 4 模态、top2 仅 T1wCE | 1st |
| "最佳中心图"技巧 | 以"脑横截面最大"的切片为中心构建 3D 输入：CV +0.01~0.02（作者唯一 100% 成功的实验） | 1st |
| 12th | Task1 分割模型（SegResNet）→ 特征对分类无帮助，放弃；3D DenseNet121/169 × 每模态 × 5 折；val loss 0.66–0.67 的"幸运跑"才对应 AUC>0.6 | 12th |
| 事件 | DICOM→PNG 资源帖 369 票；Fake Accounts/Cheating 107 票；"The real winner…" 100 票 | 主题索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 12th |
| --- | --- | --- |
| 模型 | 3D ResNet10（无集成） | 3D DenseNet121/169（每模态×5 折） |
| 模态 | 4 模态（top2 为 T1wCE-only）；多数模型去掉 T2w | FLAIR/T1w/T1wCE/T2w 分别训练 |
| 输入技巧 | 最佳中心图（最大脑截面为中心） | 去空切片+按最长轴 resize 到 144³ |
| 验证 | 承认没有可靠验证；靠 100/250 模型的均值排序 | 5 折按 MGMT 分层；"重跑直到 lucky" |
| 分割辅助 | 未用 | 尝试 SegResNet → 特征无用，弃 |
| 结果 | **1st**（自述"公榜 0.5–0.6 却拿第一"） | 12th |

### 共识 / 分歧 / 裁决
**共识一：数据小+信号弱 → 验证噪声是第一敌人**
1st：同设置重跑 CV 0.53–0.62，任何"验证策略"都不可靠；12th：val loss 0.66–0.67 的幸运跑才相关；公榜上"随机预测也能 0.7+"。**裁决**：在这种赛制里，**单次训练结果无信息量**；必须用大规模重复（几十~几百次）估计均值/方差，并以方差而非单点分数做决策。置信度：高。

**共识二：简单模型 + 少特征/少模态反而更稳**
1st 的冠军模型是其"最早的简单 baseline"：ResNet10、BCE、无集成、无复杂增广；深网/大模型失败。12th 的 DenseNet 也只在"幸运跑"上到 0.6。**裁决**：小数据下大模型只是把噪声拟合得更彻底；选容量匹配的简单 3D CNN。置信度：高。

**共识三：公榜不可信，私榜 shakeup 是结构性的**
1st 事前判断"大多数公榜高分是随机，私榜必崩"并据此把预算压到 2 周；"random predictions 0.7+"帖；作弊/假账号帖（107 票）。**1st 最终靠"忘记选提交、自动选公榜最好的两个"夺冠**（运气成分的极端例证）。**裁决**：此类比赛应把目标定为"不被 shakeup 甩掉"，而不是追公榜。置信度：高。

**分歧一：集成 vs 单模**
1st：集成无增益、换折分数完全变；12th：大量单模态模型（预测相关性低）用于稳健性。**裁决**：由于噪声主导，集成的期望增益被方差吞掉；1st 的"简单单模 + 重复平均"与 12th 的"多模型平均"本质都是**在重复维度上平均噪声**，不是传统集成收益。置信度：中高。

**分歧二：分割（Task1）是否帮助分类（Task2）**
12th 认真做了 SegResNet 分割，但特征/掩码通道对分类无帮助，遗憾放弃；1st 未做。**裁决**：本场分割与分类信号不共享（肿瘤位置 ≠ 甲基化状态），分割辅助未证实。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的噪声量化与两阶段 250 模型筛选 | 自述（细节具体） | 中高 |
| 1st 的最佳中心图 +0.01~0.02 | 自述（唯一成功实验） | 中 |
| 12th 的逐折 AUC 与损失相关性 | 自述表格 | 中高 |
| 公榜随机性/作弊 | 多帖 + 1st 的经历 | 高（事实层面） |
| 分割对分类无帮助 | 12th 的失败记录 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd–11th 方案未收录；**Fake Accounts In Competition（269396，107 票）**的处置与 "The real winner…"（100 票）未入库——本场治理问题严重；MRI 拍摄方法差异（252843，99 票）也未细读。
- 数据集规模/官方基线未在材料中给全；AUC 的最终分数与 shakeup 幅度未量化。
- 1st 的 8 个初始想法清单只给了一半；"最佳中心图"为何有效的机制解释缺失。

### 图证（KStarter 仓库内路径）
- ../../intel/rsna-miccai-brain-tumor-radiogenomic-classification/bodies/279832_img/01.png — 12th 的预测相关性矩阵

### 出处
- 12th（279832）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/279832
- 1st（281347）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/281347
- 论文帖（252833）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/252833
- 往届金牌（252838）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/252838
- DICOM→PNG（253000）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/253000
- 往届数据集（253056）：https://www.kaggle.com/competitions/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/253056
- 未收录正文：269396（作弊账号）、252843（MRI 拍摄差异）、252838（往届金牌索引）

### 外部题解（kaggle-solutions）
- rank 2｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/280033
- rank 3｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/287713
- rank 4｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/280029
- rank 5｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/281911
- rank 6｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/280402
- rank 7｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/281374
- rank 8｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/280572
- rank 9｜code：https://www.kaggle.com/c/rsna-miccai-brain-tumor-radiogenomic-classification/discussion/279826

---

## sartorius-cell-instance-segmentation — Sartorius Cell Instance Segmentation 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 IntersectionOverUnionObjectSegmentation ｜ 队伍 1505 ｜ 截止 2021-12-30 ｜ Tier B ｜ 标签 cv,segmentation
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/sartorius-cell-instance-segmentation.md
> 材料基础：`digests/sartorius-cell-instance-segmentation.md`（5 篇正文：1st 298869 / 2nd 297988 / 3rd cellpose 297984 / 5th 298081 / 标注噪声 281205；80 条主题索引）+ 11 张图

### 一句话重述
在显微图像上做三分类细胞的实例分割（shsy5y/astro/cort），细胞只有 ~10×10 像素。真正的考点是**"先检测、后分割"的工程拆分 + 对标注噪声与指标缺陷的清醒认识**：高 IoU 阈值段（0.8–0.95）对这么小的细胞基本是抽签，因此检测框质量与阈值/后处理比"更花哨的 mask head"更值钱。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 标注/指标诊断（174 票） | 小细胞 ~10×10px，标注边界有 ~20px 歧义 → 同一预测的 IoU 可波动 **~0.2**；0.8/0.85/0.9/0.95 四档阈值"基本靠运气"，**约 40% 的评估是随机的**；建议按 GT 尺寸分档（<200px 用 0.5–0.75；<400px 用 0.5–0.85；≥400px 用 0.5–0.95） | 281205 |
| 1st（298869） | 明确"box-first"：**重点投在检测**，理由是 mask 质量受标注质量限制；验证用 COCO mAP（bbox AP[.5:.95] 0.396、segm 0.362）；检测器 **YOLOX（无需调参）** + 强特征提取器（CB DBS-FPN、EffDetD7、CSPDarknet-YOLOXPAFPN）、输入 1536、**LiveCell 预训练**（含 mixup 扩充上千实例的图）；为省显存用 CUDA 扩展优化 SimOTA；mask 侧 = 2 个 Mask R-CNN（CB-DBS，用 GT bbox/mask 训练）+ **4 个 UPerNet（Swin/ResNet101，LiveCell 预训练）**；训练细节：**ROIAlign 裁剪+网格采样回贴、mask 目标用双线性插值再阈值化**（跟随 Mask R-CNN mask head 的口径）；bbox 集成 → mask 头；**重排序 = bbox 分 × mask 平均分（astro mAP +0.01）**；后处理：阈值化、去重叠、丢小目标 | 298869 |
| 2nd（297988） | 2 检测器（yolov5x6、effdetD3）+ 1 UNet（EffNet-b5，裁块后预测"中心细胞 + 邻细胞"两类）+ 2 Mask R-CNN；检测框用 **WBF** 融合后送进各 mask 头；mask 用加权平均；训练流程 = LiveCell + 半监督数据多轮预训练 → 竞赛数据微调 | 297988 |
| 3rd（297984） | **cellpose（"flow mask"）路线**：不直接回归二值 mask，而是学"从像素指向细胞质心的流场"，用动力系统的不动点/吸引域还原实例——天然解决粘连细胞；模型仅 ~6M 参数（比 ResNet-18 小）；重增强 + 高倍放大 → 需要 300–500 epoch；遇到 dataloader/磁盘 IO 瓶颈自写 fast.ai 数据管线；**"diameter（细胞像素尺度）"是最大敏感超参**：试过按类别设常量、按范围 TTA、cellpose 的 size model、用检测器输出尺寸——最终用 10 模型集成，先用 size model 定初始 diameter，再按每步预测的 mask 重估 | 297984 |
| 5th（298081） | Mask R-CNN（Detectron2）先在剔除 shsy5y 的 LiveCell 上训练 → 竞赛数据 + LiveCell-shsy5y 微调 → **对 train_semi_supervised 打伪标签**再微调 → 用其预测生成 flow-x/flow-y + 语义分割作为额外通道训练 **Cellpose**（diameter=19） | 298081 |
| 社区侧 | "干净的 astro mask"共享帖（125 票）；"按类别设阈值"（85 票）；"Detectron2 教程"（83 票）；早期总结帖（154 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd | 5th |
| --- | --- | --- | --- | --- |
| 主路线 | **检测优先（YOLOX）+ 多 mask head** | 检测（WBF）+ UNet/MaskRCNN | **cellpose 流场** | MaskRCNN 伪标签 → cellpose |
| 检测器 | YOLOX + 3 种强骨干 | yolov5x6 + effdetD3 | 无（cellpose 自带） | MaskRCNN(RPN) |
| 预训练 | LiveCell | LiveCell + 半监督 | LiveCell | LiveCell（分阶段） |
| 关键细节 | ROIAlign + grid_sample；bilinear+阈值化；bbox×mask 重排序 | 中心/邻细胞两类分割；WBF | 流场不动点；diameter 自适应 | 伪标签 + flow 通道 |
| 后处理 | 阈值/去重叠/丢小 | 加权 mask | 按类型调后处理 | 按类型调 |

### 共识 / 分歧 / 裁决
**共识一：本赛实质是"检测 + 分块 mask"（1st/2nd/5th）**
三队都把检测框质量当成主战场（1st 明说"mask 受标注质量限制，不投入过多"），mask 阶段在裁剪块上做（含"邻细胞"辅助类）。**裁决**：小目标实例分割的 ROI 顺序应是"检测 → 分块精修 → 融合"，而不是整图端到端 mask。置信度：高。

**共识二：标注噪声/指标缺陷是必须正面处理的对象（174 票帖 + 3rd）**
174 票帖量化"高阈值段 40% 随机"；1st 直接把验证口径换成 COCO mAP 并靠阈值/后处理捞分；3rd 指出"高分 astro 极难"（流场输出漂亮也只有 0.155）。**裁决**：当指标的高阈值段不可达时，优化"检测召回 + 中低阈值段的精度"是更理性的目标；同时把评测口径（分档阈值）作为诊断工具登记。置信度：高。

**共识三：LiveCell 预训练是公共起点（1st/2nd/3rd/5th）**
四队都用 LiveCell（部分做法：先剔除某类细胞再训练，避免类别混淆）。**裁决**：领域内有大规模同域数据集时，"外部预训练 + 竞赛数据微调"是标准路径。置信度：高。

**分歧一：Mask R-CNN/UNet 系 vs cellpose 流场**
1st/2nd/5th 走检测框 + mask head/UNet；3rd 用 cellpose 的流场表示（对粘连细胞更自然，且模型更小）。**裁决**：流场表示在"细胞密集粘连"场景有结构优势，但引入 diameter 这个敏感超参；两条路线可在集成中互补（5th 正是把 cellpose 与 MaskRCNN 组合）。置信度：中高。

**分歧二：伪标签/半监督的用法**
2nd/5th 用 train_semi_supervised 打伪标签再训练；3rd 试过"用大集成标注未标注数据"但结论不明确。**裁决**：半监督数据可用，但必须经过"伪标签质量 + 集成同质化"的检验（与 S5E8/E6 的结论一致）。置信度：中。

**事件：社区数据共享（"干净的 astro mask"）**
astro 类标注最脏，有人整理出干净 mask 并公开（125 票）。**裁决**：数据清洗成果的公开共享能显著抬高全场下限——这在医疗图像赛里几乎成为惯例。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的检测/mask 双阶段与重排序 +0.01 | 自述 + COCO 分数表 + 公开代码 | 高 |
| 174 票的标注噪声量化（IoU ±0.2） | 自述 + 示例图 + 逻辑清晰 | 中高 |
| 3rd 的 cellpose 流程与 diameter 处理 | 自述 + 图 + 代码 | 中高 |
| 2nd 的 WBF + 中心/邻细胞两类分割 | 自述 + 图 | 中高 |
| 5th 的伪标签 + flow 通道 | 自述 + 流程步骤 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th/6th–10th 的方案未入库；"按类别设阈值"（85 票）与"早期总结"（154 票）未细读；
- 1st 未给"检测 vs mask"的逐项消融（只有最终 COCO 表）；
- cellpose 的 diameter 自动估计在生产中的误差分布未量化；
- 归档 11 图：174 票帖的 IoU 示例（图 1）、1st 的管线图、3rd 的流场输入/输出为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/sartorius-cell-instance-segmentation/bodies/281205_img/01.png — 同一预测在两种标注下的 IoU 差异

### 出处
- 1st（101 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/298869
- 2nd（146 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/297988
- 3rd "Go with the flow"（124 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/297984
- 5th（84 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/298081
- 标注噪声（174 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/281205
- 干净的 astro mask（125 票）：https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation/discussion/291371

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/298021
- rank 4｜description：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/298146
- rank 6｜code：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/297986
- rank 7｜code：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/298002
- rank 8｜code：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/297998
- rank 9｜description：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/297985
- rank 11｜code：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/298038
- rank 22｜description：https://www.kaggle.com/c/sartorius-cell-instance-segmentation/discussion/298030

---

## sorghum-id-fgvc-9 — Sorghum ID FGVC9（高粱品种细粒度分类）轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Categorization Accuracy ｜ 队伍 252 ｜ 截止 2022-05-30 ｜ Tier B ｜ 标签 cv,agriculture
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/sorghum-id-fgvc-9.md
> 材料基础：`digests/sorghum-id-fgvc-9.md`（6 篇正文：3rd 328593 / 2nd 329414 / 1st 329049 / 主办方 PhD 招募 320481 / 71GB→14GB JPEG 数据集 313266 / 求 top1% 代码 328477；38 条主题索引）+ 2 张归档图

### 一句话重述
高粱品种的**细粒度分类**（FGVC9/CVPR workshop）。本场难点被 3rd 总结得非常清楚：类间相似度高、光照/曝光差异大、**训练与测试来自两块不同田块（域适应）**、植株随生长期变化。三队不约而同给出同一条主线：**高分辨率 + 域适应/直方图均衡 + 伪标签/外部数据 + 集成**；其中分辨率与伪标签是最大的两个单项增益（2nd 从 512→960 私榜 84.1→91.9，伪标签再 +3.2）。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 3rd（328593） | 消融表：base（resnet50@512）0.73 → 直方图均衡 +0.03 → **IBN-ResNet +0.05** → bnn-neck +0.005 → 最后卷积 stride=1 +0.005 → **ArcFace(s=30,m=0.3) +0.015** → mixup +0.01 → cutmix +0.005 → AWP 对抗训练 +0.01 → **512→1024 +0.04** → FGVC8 数据 +0.03 → TTA +0.02 → 伪标签 +0.01 ≈ **0.957**（训练尺寸 1024） | 328593 |
| 2nd（329414） | 只用本届数据；RegNetY-16.0GF；960 从 1024 裁剪；private：base@512 **84.1** → 960 **91.9** → 伪标签 **95.1** → dropout **95.3** → 集成 **95.9**（public 96.2） | 329414 |
| 1st（329049） | ConvNeXt base；5 折集成；把竞赛数据与 FGVC8 合并成 **223 类**（原 100 类）；private：convb+100 类 0.952 → +223 类 0.954 → 集成 0.957 → +伪标签 0.962 → **+5 折 0.965** | 329049 |
| 数据工程 | PNG 71GB → JPEG **14GB**（社区数据集，13 票 / 11 评论）；测试图一度"找不到"（10 票 / 10 评论）；CSV 文件名与目录不匹配/坏图（6 票 / 7 评论）；Kaggle API 拉不到数据（4 票 / 10 评论）；缺失图与新类问题 | 313266 / 313438 / 313543 / 313691 |
| 学术产出 | 主办方（SLU 助理教授）公开招募 PhD/访问研究者；3rd 开源 CVPR2022-FGVC9 top3 代码 | 320481 / 328593 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 3rd（消融最全） | 2nd（只用本届数据） | 1st（外部数据 + 折集成） |
| --- | --- | --- | --- |
| 骨干 | ResNet50/IBN-ResNet | RegNetY-16.0GF | ConvNeXt base |
| 分辨率 | 1024 | 960（1024 裁） | 1024 |
| 域适应 | **直方图均衡 + IBN** | AutoAugment + 裁剪/翻转 | 外部数据扩类 |
| 损失 | ArcFace + CE | CE + dropout | CE |
| 增分器 | 伪标签 + TTA | **伪标签 + 集成** | **5 折 + 伪标签 + 223 类** |
| 私榜 | ≈0.957（消融合计） | 0.959 | **0.965** |

### 共识 / 分歧 / 裁决
**共识一：高分辨率是第一杠杆（328593 / 329414 / 329049；置信度高）**
2nd 512→960 私榜 +7.8；3rd 512→1024 +0.04；1st 全程 1024。**裁决**：细粒度农业/植物数据在算力允许下直接上 960–1024；低分辨率调模型是在浪费预算。置信度：高。

**共识二：域适应要用"田块差异"的物理原因选方法（328593；置信度中高）**
训练/测试来自两块田、光照与曝光差异大：3rd 用 **IBN-Net（浅层 IN+BN）**（+0.05）与**直方图均衡**（+0.03），2nd/1st 用常规增强+外部数据。**裁决**：先做 train/test 分布可视化（亮度/颜色/背景），再决定 IN 层、CLAHE/直方图均衡或颜色归一化；不要盲抄增强。置信度：中高。

**共识三：伪标签+集成是第二大杠杆（329414 / 329049 / 328593；置信度高）**
2nd 伪标签 +3.2、1st 伪标签 +0.5、3rd +0.01（其空间已小）；1st 5 折再加 0.3。**裁决**：当分辨率与域适应到位后，用高置信伪标签迭代 + 多折/多骨干集成；TTA 是低成本的收尾项（3rd +0.02）。置信度：高。

**分歧：外部数据是否必要（329414 vs 329049 / 328593；置信度中）**
2nd 只用本届数据拿到 95.9；1st/3rd 用 FGVC8（1st 扩到 223 类 +0.02）。**裁决**：外部数据是加分项不是必需项；若用，必须先做类别映射与图像拼接（FGVC8 480×480 拼 1024）并验证域兼容。置信度：中。

**事件一：数据获取与存储是实际门槛（313266 / 313438 / 313691 / 313543；置信度中高）**
71GB PNG 对 Kaggle 环境过大，社区转 JPEG 14GB；测试图/API/文件名问题频发。**裁决**：第一步把数据落成 JPEG 并校验 CSV↔文件一致性，否则训练脚本会随机崩。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 3rd 的逐项消融表 | 自述 + 两张结构图（328593） | 高（该场最可复算的收益分解） |
| 2nd 的分阶段分数表 | 自述 + 表格（329414） | 中高 |
| 1st 的 223 类扩类与 5 折 | 自述 + 表格（329049） | 中（粒度粗，无消融） |
| JPEG 数据集与数据问题 | 社区帖（313266 等） | 中高 |
| PhD 招募 | 官方/主办方帖（320481） | 高（事实） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 1st 的完整代码未在正文给出（仅 Kaggle notebook 路径）；"求 top1% 代码"（328477）无答复；
- 各队验证集划分不同，跨队分数不可直接比较；
- FGVC8 外部数据的拼接/扩类细节只有 1st 一段描述；
- 测试集标签申请（367217）无归档答复；
- **图证缺口**：无（2 张图，本深读内嵌 2 张）。

### 图证（KStarter 仓库内路径）
- ../../intel/sorghum-id-fgvc-9/bodies/328593_img/01.jpg — 3rd 方案管线
- ../../intel/sorghum-id-fgvc-9/bodies/328593_img/02.png — IBN-Net 变体结构

### 出处
- 3rd 方案（12 票 / 7 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/328593
- 2nd 方案（5 票 / 0 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329414
- 1st 方案（6 票 / 4 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/329049
- 71GB→14GB JPEG（13 票 / 11 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/313266
- 测试图缺失（10 票 / 10 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/313438
- CSV 与目录不匹配（6 票 / 7 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/313543
- Kaggle API 数据不可用（4 票 / 10 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/313691
- PhD/研究机会（15 票 / 1 评论）：https://www.kaggle.com/competitions/sorghum-id-fgvc-9/discussion/320481

---

## stable-diffusion-image-to-prompts — Stable Diffusion - Image to Prompts 轻量深读（Tier B）

> 主题 cv ｜ 类别 Featured ｜ 指标 MeanCosineSimilarity ｜ 队伍 1231 ｜ 截止 2023-05-15 ｜ Tier B ｜ 标签 cv,nlp,llm,retrieval,generative
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/stable-diffusion-image-to-prompts.md
> 材料基础：`digests/stable-diffusion-image-to-prompts.md`（6 篇正文：1st 411237 / 2nd 410606 / 3rd 410686 / 11th 765 行处 / 起步指南 831 行处 / 数据集帖；80 条主题索引）+ 1 张图

### 一句话重述
给一张 Stable Diffusion 生成的图，预测它对应的提示词——但由于指标只比较**句子嵌入的余弦相似度**，任务实际退化成"**预测句向量**"（预测文本的语法/顺序几乎不重要）。真正的考点是**自造大规模"提示词-图像"对 + 加速生成 + 用多 backbone 回归句向量**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（411237，121 票） | **约 860 万提示词生成约 1060 万张图**；加速链路：xFormers（15s→10s）→ FP16（→5s）→ 分辨率 768→512、采样步数 50→25（→**2s/图**）；数据：DiffusionDB-2M + 图像描述数据集（COCO Captions、VizWiz、Open Images、ADE20K、Flickr30K、TextCaps，去重相似度 >0.8）+ ChatGPT 生成提示词 → **PROMPTS_HQ（约 200 万高质量提示词，每条生成 2 张不同 seed 的图）**；COYO-700M 筛出约 660 万对做 **PROMPTS_LQ** 用于**预训练（+0.008~0.01）**；模型 = **ViT-Large、ConvNeXt-XXLarge、BLIP-2**（**去掉 BLIP-2 的 LLM 部分**——"语法与顺序不重要甚至有害"）；LoRA 微调底层；**在输出层前加一个大全连接层（Linear→BN→ReLU→Linear）对 CLIP 有显著提升**；两阶段训练（先 LQ 预训练、再 HQ 微调）；同提示词的多张图每 epoch 随机选一张；更大输入尺寸更好（用到 336）；CLIP 不用增强、BLIP-2 用默认增强；最终 = 三类模型嵌入的**加权集成** | 411237 |
| 2nd（410606，96 票） | 与公开 ViT 基线同源；**生成提速 4×**：调度器 DDIM→**DPMSolver++**（50→16 步）+ FP16 + xFormers；关键教训：**固定随机种子是错误**——每条提示词用不同 seed（`zlib.adler32(name, index)` 生成）后分数大幅提升；guidance 7.5 与 9.0 差异不大、3.0 明显更差；数据：DiffusionDB（约 180 万去重提示词）+ COCO（约 60 万 caption→50 万图）+ **Open Images 前 500 万自然图经 BLIP-2-flan-t5-xxl 生成 caption（用"链式生成"制造多句复杂提示）再喂 SD**；训练（图 1）：Dataset A 训 4 个视觉模型（ConvNeXt-xlarge/256、BLIP-2 vision/224、EVA02-L/336、EVA02-e/224）→ 在 A+B 上以更大分辨率（384/336/448/336）继续训练并冻结权重 → 每个模型接 Q-former 头 → 视觉模型与 Q-former 分别加权平均 → 最终平均 | 410606 |
| 3rd（410686） | CLIP 直接回归 384 维句向量；约 40 万数据；**关键数据集 = VizWiz caption（约 7 万，每条最多 5 个 caption 抽 3 个）**——"比 COCO 更描述性、更多样、更长"：加入后本地验证 0.5415 / LB 0.5309，不加则 0.5528 / **0.48765**（本地更高但 LB 大跌，说明泛化更好）；DiffusionDB 30 万（自生成 SD2 图，含 21 万提示词筛选 + 8 万用已训模型做**难例采样**）；COCO 2.5 万 | 410686 |
| 社区侧 | "**我上传了 DiffusionDB-2M**"（138 票）、"3 万对图像-提示词"（102 票）、"我分享 SD2 生成的图像"（81 票）、"Vlomme 的实验"（59 票）、"基于检索的工程方案"（53 票）、"ChatGPT 生成的图像-提示词对"（52 票）、"如何到 0.58+"（831 行处） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 3rd |
| --- | --- | --- | --- |
| 自造数据规模 | **~1060 万图 / 860 万提示词** | ~180 万提示词（+COCO+OID→BLIP-2 链式 caption） | ~40 万（VizWiz 为关键） |
| 生成加速 | xFormers→FP16→512/25 步（2s/图） | DPMSolver++ 16 步 + xFormers（4×） | — |
| 模型 | ViT-L / ConvNeXt-XXL / BLIP-2（去 LLM）+ 额外 FC 层 | 4 个视觉模型（两阶段放大分辨率）+ Q-former 头 | CLIP → 384 维 |
| 关键技巧 | 两阶段预训练（LQ→HQ）、LoRA、去 LLM | **每提示词不同 seed**、链式 caption | **VizWiz 提升泛化**、难例采样 |
| 集成 | 三类嵌入加权 | 双路加权平均 + 最终平均 | 单模 |

### 共识 / 分歧 / 裁决
**共识一：数据规模与多样性就是主赛道（1st/2nd/3rd + 社区数据帖）**
1st 生成 1060 万图；2nd 用 DiffusionDB+COCO+OID 转 caption；3rd 发现"更描述性的 caption 数据（VizWiz）"虽降低本地验证却大幅提升 LB。**裁决**：本场的模型架构是次要变量（ViT/ConvNeXt/CLIP 都能用），**数据来源与提示词分布**才是主变量；高描述性、长句、多样的 caption 数据能提升泛化。置信度：高。

**共识二：指标只比句向量 → 不需要生成文本（1st/2nd/3rd）**
三队都直接回归句向量（all-MiniLM-L6-v2 的输出）；1st 还专门去掉 BLIP-2 的 LLM 部分（"语法与顺序不重要甚至有害"）。**裁决**：先读指标——"图像描述生成"类任务若只比嵌入余弦，应把它当作"跨模态回归/检索"而非文本生成。置信度：高。

**共识三：生成数据的随机性细节会显著影响质量（2nd + 1st）**
2nd 明确"固定 seed 是大错"（每条提示词换 seed 后分数大涨）；1st 也每条提示词生成 2 张不同 seed 的图。**裁决**：自造数据时，多样性（seed/guidance/步数）既是数据增强也是分布覆盖，必须显式设计。置信度：高。

**分歧一：更大的模型 vs 更大的数据**
1st 用 3 类大 backbone + 10M 数据；3rd 用单 CLIP + 40 万数据拿到第 3。**裁决**：数据管线（尤其 caption 质量）能补偿模型规模；算力有限时应先投数据质量。置信度：中高。

**事件：公共数据集生态（138/102/81/52 票）**
DiffusionDB-2M 上传、3 万对数据、SD2 生成图、ChatGPT 生成对等帖子构成全场公共基础设施。**裁决**：无数据赛的"数据共享帖"等价于半条赛道；引用时要注意各数据集的生成模型/参数差异（SD1.x vs SD2）。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的数据规模、加速链路与模型细节 | 自述 + 消融表（文中称 table 1）+ 公开代码 | 高 |
| 2nd 的"seed 不同"教训与两阶段训练 | 自述 + 管线图 | 高 |
| 3rd 的 VizWiz 对照（0.5415/0.5309 vs 0.5528/0.48765） | 自述 + 数字对照 | 高 |
| 社区数据集的质量与规模 | 高票帖子 | 中高 |
| "去 LLM 的 BLIP-2 更好" | 1st 自述（机制解释合理） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 4th–10th 的方案未细读；"Vlomme 的实验"（59 票）、"基于检索的工程方案"（53 票）、"如何到 0.58+"（831 行处）未细读；
- 1st 的消融表（table 1）细节未在 digest 展开；
- 各数据集使用的 SD 版本差异（1.x/2.x）对结果的影响未系统整理；
- 归档 1 图：2nd 的两阶段训练管线（图 1）为关键图证。

### 图证（KStarter 仓库内路径）
- ../../intel/stable-diffusion-image-to-prompts/bodies/410606_img/01.png — 2nd 的两阶段训练与集成管线

### 出处
- 1st（121 票）：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/411237
- 2nd（96 票）：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/410606
- 3rd：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/410686
- DiffusionDB-2M（138 票）：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/388080
- 30K 图像-提示词对（102 票）：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/391500
- 如何到 0.58+：https://www.kaggle.com/competitions/stable-diffusion-image-to-prompts/discussion/398529

### 外部题解（kaggle-solutions）
- rank 4｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410798
- rank 5｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410688
- rank 6｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410768
- rank 7｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410618
- rank 11｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410611
- rank 12｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410657
- rank 33｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410610
- rank 36｜description：https://www.kaggle.com/c/stable-diffusion-image-to-prompts/discussion/410609

---

## tensorflow-great-barrier-reef — TensorFlow Great Barrier Reef 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 CSIROObjectDetectionFBeta ｜ 队伍 2025 ｜ 截止 2022-02-14 ｜ Tier B ｜ 标签 cv,detection
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/tensorflow-great-barrier-reef.md
> 材料基础：`digests/tensorflow-great-barrier-reef.md`（6 篇正文：往届检测冠军汇总 289999 / 3rd Hydrogen 307707 / Kaggle 教训 297863 / 1st "Trust CV" 307878 / 5th Poisson 308007 / YOLOv5 高分辨率 300638；80 条主题索引）+ 0 张归档图

### 一句话重述
水下视频中的海星（COTS）检测（F2，IoU 0.8 阈值对**框的松紧**极敏感）。真正考的是：**检测集成 + 二阶段重打分/多家族融合 + 跟踪/后处理**；而本场最著名的教训是**"训练框松、公榜框紧、私榜又不同"的标注松紧域偏移**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st "Trust CV" | 6×YOLOv5 集成 CV 0.716 → 分类重打分 0.727 → 分类集成 0.73+ → 注意力后处理 **0.74+**；3 折按 video_id；跟踪 +0.002 但弃用（多两个超参） | 1st |
| 1st 的 F2 事故 | 同一份 OOF：三名队员算出 F2=**0.62 / 0.66 / 0.68**；最终选用最低分实现评估全部模型 | 1st |
| 3rd（Hydrogen） | 5 种检测器（CenterNet+HRNet、FasterRCNN+NFNet、FCOS、EfficientDet、YOLOv5l-6 直优 F2）；WBF；轨迹置信度提升 +0.01；光流 +0.001 | 3rd |
| 3rd 的标注松紧 | 高分辨率推理→框更紧→公榜大涨；手动把框缩小 ~**3px**（训练框平均大 3px）；手标小样本微调也涨公榜；但**私榜全部失效** | 3rd |
| 5th | cut&paste + Poisson 融合 + 真假分类器；多模型多尺寸（YOLOv5 S/M/L6、YOLOX-L、YOLOR-P6、HRNet）；SuperPoint/SuperGlue 单应 + DeepSort；WBF 前丢弃 maxIoU<0.55 的框 | 5th |
| 公榜玄学 | "[LB 0.579] YOLOv5 高分辨率 is all you need"（300638） | 材料 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 3rd | 5th |
| --- | --- | --- | --- |
| 路线 | 2 阶段：检测→分类重打分→后处理 | 5 家族检测集成 + 轨迹置信提升 | 检测多模型 + Poisson 合成 + 跟踪 |
| 检测 | YOLOv5×6（全图 3648 / patch 1536） | CenterNet/FRCNN/FCOS/EffDet/YOLOv5 | YOLOv5/YOLOX/YOLOR/HRNet |
| 分类/重打分 | 7 个 IoU bin 的分类头（dropout 0.7/drop_path 0.5），均值当分数 | 无（直接融合） | 真假分类器筛合成样本 |
| 跟踪 | 注意力区域跨帧加分（+0.01 级）；tracking 方法 +0.002 弃用 | 中心距离轨迹 + 低置信框提到轨迹最大置信（**+0.01**）；光流 +0.001 | SuperPoint/SuperGlue 单应 + DeepSort |
| 验证 | 3 折视频；**只优化 CV** | 视频折+子序列折（公榜相关好，私榜失败） | 5 折按序列 |
| 关键姿态 | Trust CV | 追公榜的"框紧度"漏洞 → 私榜反噬 | 合成数据 + 跟踪 |

### 共识 / 分歧 / 裁决
**共识一：检测集成 + WBF/跟踪是基础盘（3/3）**
1st/3rd/5th 都做多检测器集成与跨帧信息；3rd 的 WBF 自动投票、5th 先丢孤立框再 WBF、1st 用跨帧注意力加分。**裁决**：视频检测的稳定增益来自"多模型 + 跨帧一致性"，而非单模调参。置信度：高。

**共识二：F2@IoU0.8 让"框的松紧"成为一等变量**
3rd 的证据链：高分辨率推理→框更紧→公榜大涨；手动缩小 3px 同样涨；训练框平均大 3px；手标小样本微调也涨。**裁决**：指标对框尺寸敏感时，**标注松紧是可测量、可利用、也可被私榜反噬的域变量**。置信度：高（多证据链，但私榜结论未明）。

**共识三：CV 必须按视频/序列分组，并统一实现（1st 的 F2 事故）**
1st 用 3 折按 video_id；3rd 用视频折+子序列折；5th 5 折按序列。1st 还发现同一 OOF 的 F2 在三人实现下差 0.06。**裁决**：分组 CV + **共享同一评测实现**是团队协作的硬要求；否则模型选择都在噪声上。置信度：高。

**分歧一：Trust CV 还是追公榜漏洞**
1st（冠军）"没有新东西，只从第一天到最后一天优化 CV"；3rd 发现并重仓公榜的"框紧度"调整，私榜失效。**裁决**：对"疑似测试集标注差异"的漏洞要**先对冲**（保留无漏洞版本），不能把提交全押在公榜反馈上。置信度：高。

**分歧二：跟踪是否值得**
1st：tracking +0.002 但引入两个超参 → 弃用；注意力后处理（无超参化）替代；3rd：轨迹置信提升 +0.01；5th：单应+DeepSort。**裁决**：跟踪有效但超参敏感；用"无额外超参"的跨帧后处理（注意力/轨迹置信提升）性价比最高。置信度：中高。

**分歧三：合成数据**
5th：Poisson 融合+真假分类器有效；GAN 生成逼真但不涨分（受限于独特海星数量）；其他人未用。**裁决**：合成数据的瓶颈是"目标多样性"而非真实感；copy-paste 需解决光照边界与位置合理性。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的 CV 提升链（0.716→0.74+） | 自述 | 中高 |
| F2 实现差异 0.62/0.66/0.68 | 自述（真实协作事故） | 高（事实性） |
| 3rd 的框紧度证据链 | 自述（公榜 A/B + 训练集统计） | 中高（公榜部分）；私榜结论开放 |
| 3rd 的轨迹置信 +0.01 | 自述 | 中 |
| 5th 的 Poisson/真假分类器 | 自述 | 中 |
| 指标实现细节（F2@IoU 0.8） | 1st 帖给出实现链接 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/4th 方案未收录；私榜为何与公榜标注不一致没有官方解释（3rd 的开放问题）。
- "框紧度"调整的私榜失效说明公榜反馈不可外推，但材料未给出各队最终分数明细。
- F2 的精确实现（1st 提供了自己的版本）与官方差异未核。
- 5th 的 GAN 受限于 unique 海星数量的假设未做受控实验。

### 出处
- 往届检测冠军汇总（289999）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/289999
- 3rd Team Hydrogen（307707）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/307707
- Kaggle 教训（297863）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/297863
- 1st Trust CV（307878）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/307878
- 5th Poisson（308007）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/308007
- YOLOv5 高分辨率（300638）：https://www.kaggle.com/competitions/tensorflow-great-barrier-reef/discussion/300638

### 外部题解（kaggle-solutions）
- rank 2｜code：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307760
- rank 4｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307626
- rank 6｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307619
- rank 7｜code：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307786
- rank 8｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307735
- rank 9｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307871
- rank 10｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307756
- rank 11｜description：https://www.kaggle.com/c/tensorflow-great-barrier-reef/discussion/307718

---

## uw-madison-gi-tract-image-segmentation — UWMGI 2022 深读：部分标注分层 × CLS 门控 × 2.5D/3D 融合

> 主题 cv ｜ 类别 Research ｜ 指标 Dice3DHausdorff ｜ 队伍 1548 ｜ 截止 2022-07-14 ｜ Tier A ｜ 标签 cv,segmentation
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/uw-madison-gi-tract-image-segmentation.md
> 材料基础：`digests/uw-madison-gi-tract-image-segmentation.md`（6 篇：MONAI-3D/资源汇总/1st/2.5D/5th/3rd；80 条讨论索引）+ 3 张图（337197×1 / 320060×2）

### 一句话重述
题面是"MRI 逐切片分割胃/小肠/大肠（3 类语义分割）"，实际被考的是**部分标注与空切片下的工程分层**：
1. **部分标注 + 错误标注**：大量切片没有器官、部分切片无标注、社区另有"错误 mask"大讨论（319963，70 票）；直接全量硬训会被负样本与噪声主导——1st 把数据分成"anno-only / 全量 / 排除肠末端 ambiguous 5 层"三种训练策略，分别喂给不同模型。
2. **空切片必须门控**：1st/3rd 用分类器先判"这一层有没有目标"（1st：阈值 0.6 且正像素 >12 才算正），负层直接输出零 mask；5th 用后过滤（<50px 丢弃）替代。
3. **2.5D vs 3D 是互补而非对立**：3D（MONAI/ SegResNet）给 z 方向一致性与更好的 Hausdorff；2.5D 给训练效率与多样性；冠军把两者 logits 按 0.4/0.6 融合（阈值 0.4），5th 用 9 个 2.5D（x/y/z 三轴切法）×3 个 3D 做多样性集成。
4. **指标中途改为 Dice + 3D Hausdorff**：MONAI 作者用新指标重新微调与选模（LB 0.860→0.872）；3rd 直接试 Hausdorff 损失失败——**指标换 ≠ 损失换，先换选模与后处理**。
一句话：**这是一场"数据分层 + 空切片门控 + 2.5D/3D 融合"的工程赛**——冠军结构里没有一个部件是单纯的模型选择。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 数据事实 | 每扫描 144（常见）/80（少）切片；case=1–5 天 → 144–720 图；4 种图像尺寸；首 1/末 ~8 切片无 mask | 资源帖 |
| 基线演进 | DeepLabV3+ 0.810（3 epoch）→ +ASPP+SE 0.817（7 epoch）→ EffNetB0 UNet（Dice+Focal）0.828 | 资源帖 |
| 1st CLS | 4 UNet（b4–b7）；阈值 0.6 + 正像素 >12 判正 | 1st |
| 1st SEG | 5 UNet（b4/2×b5/b6/b7）+ 2 UPerNet（convnext base/small）；三分层数据 | 1st |
| 1st 3D | 3 SegResNet（init_filters 12/20/32，PRELU+BN）；3D/2.5D logits 0.4/0.6；阈值 0.4 | 1st |
| 1st 2.5D | stride=2 ×3 切片；640/512 → RandomCrop 448；TTA +0.001–0.002；单模型 ~0.883、融合 0.889；fp16 省 ~50% 显存；BCE:Dice=1:3 | 1st 2.5D 帖 |
| 5th 集成 | 9×2.5D（x/y/z）+ 3×3D；单模型最高 0.875 → 平均+阈值 0.3 = 0.889 → <50px 丢弃 = **0.890** | 5th |
| 3rd 单折/5 折 | fold0：0.869–0.875（模型族）；5 折：0.873–0.879；cls+seg 0.877/0.886；seg+seg 0.879（未提交） | 3rd |
| 3rd 训练 | 检测器 256/5 epoch；分割 320–416、35 epoch（7 cycle）、lr 3e-4/5e-4；ComboLoss(bce .5/dice .5/lovasz 1) | 3rd |
| MONAI 版本链 | v1 160×160×80 dice+ce LB 0.817 → v2 224×224×80 0.840 → v3 dice+bce 0.857 → v4 新指标 0.860 → v5 multilabel 大 UNet 0.868 → v6 lr/损失 0.872 → 5 折 0.877 | MONAI |
| MONAI 局部分数 | v2 old-dice 0.8970 / new 0.8822；v3 old 0.9108 / new 0.8933（**旧指标选模高估 ~0.018**） | MONAI |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 5th | 3D MONAI (yiheng) | 3rd |
| --- | --- | --- | --- | --- |
| 总体 | CLS + 2.5D SEG + 3D，三组融合 | 9×2.5D(x/y/z) + 3×3D 全平均 | 纯 3D 单系（UNet→大 UNet） | 检测裁剪 → CLS+SEG（无 3D） |
| 空切片处理 | CLS 门控（0.6 + >12px） | 后过滤 <50px | 3D 体积整体预测 | CLS 分支 + 连续切片规则 |
| 数据分层 | 三分层：anno-only / 去 ambiguous 5 层 / 全量 | 未分层（全量+正样本） | public split（awsaf49） | SEG 只用正样本；检测器重标坏框 |
| 2.5D 构造 | stride=2，3 切片 | x/y/z 三轴各切一份（2.5Dx/y/z） | — | slice=3 与 slice=5 两族 |
| 3D 模型 | 3×SegResNet（12/20/32） | resnet-unet / effv2s-unet / effv2m-unet | 3D UNet；160×160×80 → 224×224×80 | — |
| 模型规模 | UNet b4–b7 + UPerNet convnext | effv2s/nfnet-l0/convnext-s/pvtv2b2/mitb2 等 | 由小到大逐步升级（v1→v5） | effb3–b7、effv2-l/m，320–416 |
| 损失 | dice-ce / ce / dice（分模型） | seg 常规（未展开） | dice+ce → dice+bce → 新指标微调 | ComboLoss（bce .5/dice .5/lovasz 1） |
| 指标感知 | 融合阈值 0.4 | 阈值 0.3 | v4 起用新指标（Dice+Hausdorff）微调/选模 | 选模用 TP/(TP+FP+FN)+Dice；Hausdorff loss 失败 |
| 融合/后处理 | 3D/2.5D = 0.4/0.6；阈值 0.4 | 全模型平均；<50px 丢弃 | 5 折权重集成 | 去 25px；连续 3 正/负切片定起止 |
| 成绩 | 榜首（未给总分） | pub 0.890 | 5 折 0.877 | 5 折 0.877/0.886 |
| 训练/推理 | — | 单模型最高 0.875 | 每版全流程公开 | 35 epoch/7 cycle；Kaggle GPU 两个月 + 租卡一个月 |

### 共识 / 分歧 / 裁决
**共识一：部分标注必须分层使用（1st 最精细，3rd/5th 方向一致）**
1st：UPerNet 用"去 ambiguous"数据（肠末端 5 层不参与），UNet 只用 anno-only，3D 用全量；
3rd：SEG 只用正样本，检测器阶段人工重标坏框；
5th：未显式分层，但用后过滤兜底。

**裁决**：部分标注场景有三类污染——**缺失标注（≠空）、错误标注、语义模糊区**；处理方式是把"数据子集×模型角色"配对（干净子集训精细模型、全量训鲁棒模型），并在图上/规则上排除模糊区（1st 的 5-layer ambiguous）。置信度：中高（1st 有图 + 社区错误 mask 帖佐证）。

**共识二：空切片要显式门控（1st/3rd 分类器，5th 后过滤）**
1st：CLS 先判正负（0.6 阈值 + >12 正像素），负数直接零 mask；
3rd：CLS+SEG 双分支，保留分类器判正的分割结果；
5th：不设 CLS，直接对小面积预测（<50px）丢弃。

**裁决**：空切片/负切片占比高时，CLS 门控同时节约算力与抑制假阳性；后过滤是廉价近似（但无法省算力）。两种路径都有效，选择取决于推理预算。置信度：高。

**共识三：2.5D 与 3D 互补，融合是上限最高解（4/4 中 3 队融合或双线）**
1st：3D SegResNet + 2.5D UNet/UPerNet，logits 0.4/0.6；
5th：9×2.5D(x/y/z) + 3×3D 全平均（单模型 0.875 → 集成 0.889）；
MONAI：纯 3D 单系到 0.877（5 折）；
3rd：无 3D（资源限制），但 0.877 说明 3D 非必需。

**裁决**：3D 提供 z 一致性与更优 Hausdorff；2.5D 提供多样性、可扩展性与训练效率。**预算允许时融合；预算受限时 2.5D+CLS 仍可进前列**（3rd）。置信度：高。

**分歧一：指标变更（加 3D Hausdorff）怎么应对**
MONAI：v1–v3 以旧 Dice 选模（local 0.8789→0.9108），新指标下只有 0.8933；v4 起改用新指标微调/选模，LB 0.860→0.872；
3rd：直接把 Hausdorff 当损失 → 失败（不可导 + 对离群点敏感）；
5th：用 3D 模型 + 小区域过滤稳边界。

**裁决**：指标换时，优先改**选模协议与后处理**，其次改微调目标；不要直接把新指标当损失（Hausdorff 类指标不可导/离群敏感）。MONAI 的 v4→v6 曲线是"选模指标对齐竞赛指标"的直接证据。置信度：中高。

**分歧二：集成规模与阈值**
1st：分组加权（CLS 门控 + 3D/2.5D 权重）；
5th：12 模型简单平均，阈值 0.3（+后处理 0.890）；
3rd：cls+seg 组合 0.877/0.886。

**裁决**：大集成下简单平均 + 重扫阈值已足够（5th）；但阈值与模型集耦合——每次换集成必须重扫（1st 0.4 vs 5th 0.3）。置信度：中高。

**补充共识：后处理的尺度与确定性**
所有队伍都有小幅确定性后处理：1st 的 >12px 门控、3rd 的去 25px + 连续切片规则、5th 的 <50px 丢弃；量级 0.001–0.003，但几乎无成本、无过拟合风险。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| MONAI 版本链数字 | **自述 + 全流程公开（数据/训练/推理 + 权重）** | 高（本场最可复现） |
| 1st 三分层 + CLS 门控 | 自述 + pipeline 图 | 中高 |
| 5th 0.875→0.889→0.890 | 自述（公开库链接） | 中高 |
| 3rd 0.877/0.886 与失败清单 | 自述 + inference 代码 | 中 |
| 资源帖数据事实与基线 | notebook 公开 | 中高 |
| 旧指标选模高估 ~0.018 | MONAI 对照表 | 中高（单队数字） |
| Hausdorff loss 失败 | 3rd 单队经验 | 低-中 |
| 错误标注规模 | 社区帖标题（正文未收录） | 低（登记） |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. 2nd place（337400）未收录，而 3rd 自称"similar to 2nd without 3D models"——四强中唯一缺失的结构。
2. **"Incorrect masks"（319963,70）+ 续帖（321979,43）未收录**：错误标注的规模、模式与修复方式未知；1st 的"without wrong annotated cases"只给结论。
3. **"LB could be wrong"（324934,47）+ "Hausdorff usage"（319215,40）未收录**：新指标实现与榜单行为争议——影响所有队伍的选模决策。
4. "2.5D Image Training"（322549,124）与 "MMsegmentation 模板"（323921,104）未收录：1st 的重要参考源（CarnoZhao/awsaf49 的公共资产）正文未存档。

**失败学（跨队合集）**

- 损失类：Hausdorff distance loss（3rd）；正负样本平衡（3rd）。
- 数据类：亮度调整（3rd，花了很多时间无收益）；外部 CT 数据（3rd，需 GAN 域适配）；"CenterCrop 去边"几乎无影响（1st 2.5D）。
- 资源类：无 3D（3rd 遗憾）；Kaggle GPU 两个月单模型仅 ~0.875（3rd 的自述曲线说明"大模型+租卡"阶段的必要性）。
- 隐藏提示：1st 明确"部分模型不用错误标注 case"——数据清洗是与架构同级的杠杆。

### 出处
- 3D MONAI（yiheng，162 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/325646
- 资源汇总（140 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/320060
- 1st（127 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/337197
- 1st 2.5D 部分（56 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/337217
- 5th（46 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/337268
- 3rd（45 票）：https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation/discussion/337468
- 缺口登记（未收录正文）：2nd(337400)、322549、323921、320692、329396、326035、Incorrect masks(319963/321979)、LB could be wrong(324934)、Hausdorff usage(319215)、330336 等

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337400
- rank 8｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337359
- rank 10｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337195
- rank 11｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337193
- rank 14｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337191
- rank 15｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337189
- rank 15｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337326
- rank 17｜description：https://www.kaggle.com/c/uw-madison-gi-tract-image-segmentation/discussion/337343

---

## vesuvius-challenge-ink-detection — Vesuvius 墨迹检测深读：深度不变性 × 几何对齐 × 校准

> 主题 cv ｜ 类别 Featured ｜ 指标 DiceFBeta ｜ 队伍 1249 ｜ 截止 2023-06-14 ｜ Tier A ｜ 标签 cv,detection
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/vesuvius-challenge-ink-detection.md
> 材料基础：`digests/vesuvius-challenge-ink-detection.md`（6 节：1st/2nd/6th/9th/11th + 自制碳化纸莎草帖）+ 18 张图

### 一句话重述
题面是"在碳化卷轴的 3D CT 中分割墨迹像素"，实际被考的是**三个几何/统计问题**：
1. **深度不变性**：墨迹所在的 CT 层深在不同残篇（fragment）间漂移——"把中间 16 层当通道"的 2.5D 做法让模型学"哪一层有墨"的捷径，换残篇即失效；正确姿态是"3D 特征 → 沿深度 max/pool → 2D 分割"（1st/2nd/11th 三家殊途同归）；
2. **几何对齐**：测试残篇被**旋转**（还有 A/B 可拼接结构）→ 旋转增强/TTA 是最大单步增益（6th：公开 0.58→0.74；1st：90° 旋转增强"至关重要"）；
3. **阈值与校准**：F0.5 对阈值极端敏感，且单模型最优阈值范围宽（1st 的日志里某模型 best_th=0.1）——**多模型平均把最优阈值压回 0.5**（1st），或用百分位阈值固定正例比例（6th/2nd）。
其余两件工程事：**大切块**（128<512<1024，且总像素不变→训练时间几乎不变，是"免费的上下文"）与**输出低分辨率化**（1/32 → 双线性上采样；粗分割比逐像素精确更稳，2nd 独立验证）。
一句话：**这是一场"把几何问题处理干净 + 把校准做对"的比赛**——模型架构（SegFormer/UNet）是公共件，分差全在深度聚合方式、旋转处理与阈值选择上。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 切块尺寸缩放（dice 曲线） | 128 < 512 < 1024；1024 收敛到 ~0.58、512 ~0.55、弱增强版 ~0.52 | 1st |
| 大切块的时间中性性 | 1024² 覆盖面积是 128² 的 64 倍 → 每 epoch 切块数 ~1/64；epoch/收敛时间几乎不变 | 1st（机制） |
| 最佳单模 | UNETR（32 通道）→ SegFormer b5：公开 0.82 / 私榜 0.67 | 1st |
| 9 模型集成分值带 | 公开 0.77–0.82（3d unet/cnn/unetr × b3/b5 × 512/1024） | 1st |
| 全量数据训练收益 | 验证通过后对全部残篇训练同 checkpoint：**+0.04** | 1st |
| stride 减半 | 1/4 → 1/8 stride：+0.01（但不如"多塞模型"） | 1st |
| 旋转修复（6th） | EfficientNet B4：公开 **0.58→0.74** | 6th |
| IR 图像（6th） | CV +0.01 / LB +0.01 | 6th |
| k 折增加（6th） | 5→7 折：公开 +~0.1（原文口径；存疑，登记待核） | 6th |
| 6th 最终两提交 | sub1 th 0.96：公开 0.8116 / 私榜 0.6613；sub2 th 0.95：公开 0.7996 / 私榜 0.6548 | 6th |
| 2nd 的百分位阈值 | 0.9 vs 0.93：预期 0.90 私榜更好，实际 **0.93 更好** | 2nd |
| 2nd 输出分辨率 | 标签 1/32 双线性降采样；输出 1/32 → 双线性上采样 | 2nd |
| 11th 推理 stride | 训练 112 → 推理 56（更细） | 11th |
| 后处理清理 | 连通域 <10k 像素剔除（本地最优阈值下调 + 清理至 25k） | 1st |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st ryches | 2nd tattaka 队 | 6th chumajin | 11th tk | 9th hengck23 |
| --- | --- | --- | --- | --- | --- |
| 深度处理 | 中 16 层 → 3D（CNN/UNet/UNETR）→ **沿 z 取 max** 成多通道 → 2D SegFormer | 2.5D 分组（5×7/3×9 层，取 65 层中段 35/27）+ 3D ResBlock → avg+max 池化 z | 三组层段（25-30/27-32/29-34）+ IR 图；CNN+Unet 与 SegFormer 双线 | 按 3 分组（z_len=img_num/3）→ 2D 编码 → avg pool z | 固定深度：32 层/16 层 |
| 切块/分辨率 | 1024 为主（对比 128/512） | 输入 256（2.5D）/192（3D）；**标签与输出都降采样到 1/32** | 480–1024（按 backbone） | 224；训练 stride 112、推理 56 | 256 / 384 |
| 测试几何 | 4× 旋转 TTA + 1/4 stride 窗口；旋转增强至关重要 | h/v flip TTA；按 stride 切换 | **A/B 拼接 + 顺时针旋转推理 + 逆时针还原**；百分位阈值 | 加入 RandomRotate90（推理旋转有效） | 常规 |
| 损失/正则 | dice+bce；SWA（应对 checkpoint 不稳） | bce + **global fbeta**；label smoothing 0.1；cutmix/mixup/manifold mixup；drop_path 0.2；EMA | SoftBCEWithLogitsLoss；20 epoch/早停 4 | bce+dice | — |
| 集成/阈值 | 9 模型；逐模型像素平均→sigmoid→再平均；**平均后阈值≈0.5** | 多成员各自模型；percentile 阈值 0.9/0.93 | 两提交：th 0.96 / 0.95（百分位） | 简单平均，th 0.5 | 2 折 × 2 模型 |
| 后处理 | 连通域清理（<10k 像素剔除；本地最优 25k） | 忽略输出边缘（红色有效区） | mask=0 区域跳过 | mask=0 跳过 | — |
| 成绩 | 最佳单模 UNETR→b5：公开 0.82 / 私榜 0.67 | 1/32 分辨率路线（未给总分） | 公开 0.8116 / 私榜 0.6613（sub1） | — | 第 9 |

### 共识 / 分歧 / 裁决
**共识一：深度不变性是本题的核心架构问题（三家独立收敛）**
1st 的诊断最清晰：2.5D 把层当通道 → 模型学"哪层有墨"，而**层深在残篇间漂移**；解法是 3D 特征 + **沿深度 max**。2nd 的 2.5D→3D 混合（avg+max 池化 z）与 11th 的 1D pool 是同一思想的不同实现。

**裁决**：3D 医学/成像任务中，"沿第三维做特征聚合"（max/pool）比"固定层切片"泛化好得多。置信度高（三家 + 1st 的机制论证）。

**共识二：旋转处理是最大单步（6th 量化，1st/11th 呼应）**
6th：把测试残篇拼接后顺时针旋转再推理（预测后逆时针还原）→ EfficientNet B4 **0.58→0.74**；11th：加入 RandomRotate90 因为"推理时旋转图像提升了公开榜"；1st：不确定测试是否旋转，但 90° 旋转增强"至关重要"，并用 4× 旋转 TTA。

**裁决**：当测试几何与训练不一致时，先做几何对齐（增强/TTA），收益可能数倍于架构调整。置信度高。

**共识三：阈值必须显式校准（三条不同路线都有成功案例）**
1. **平均即校准**（1st）：单模型最优阈值范围宽（日志中某模型 best_th=0.1），多模型平均后"几乎普遍居中 0.5"；
2. **百分位阈值**（6th/2nd）：按整图排名固定正例比例——与模型无关、与 GT 正例率有关；6th 公开最优 0.96，2nd 用 0.9/0.93；
3. **直接 0.5**（11th）：其 2.5D+1D 集成在 0.5 上工作良好。

**裁决**：校准路线取决于集成规模与分布假设；小公开榜下 1st 认为百分位"风险太大"（若测试墨迹占比不同就错），2nd/6th 接受该假设。置信度中高。

**分歧一：输出分辨率——高精度小图 vs 低分辨率粗图**
1st：SegFormer 输入 1024 输出 256，粗分类更容易（"第二名的 1/32 验证了低分辨率有帮助"）；2nd 实证：**标签降采样到 1/32**、decoder 无上采样、资源全给编码器；6th/11th 用较高分辨率输出。

**裁决**：F0.5 对像素级边界不敏感（粗分割上采样即可），低分辨率输出=更少的无效精度与更强的正则；这是本任务特有的"降维打击"。置信度高（1st 与 2nd 互证）。

**分歧二：外部/IR 数据（+0.01 vs 伤害）**
6th：**训练集加入 IR 图像** → CV/LB 各 +0.01；但 **IR 预训练** → LB 下降；EMNIST 外数据 → 也降。1st：试了多种数据准备只保留"中 16 层"。

**裁决**：同源配准的 IR 图像作为输入通道有效；跨域数据（EMNIST）或错误阶段（预训练）注入无效甚至有害。置信度中（单家消融）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 切块尺寸曲线（128/512/1024） | **可读取（图）** | 1st 训练日志（dice vs step） |
| 旋转推理 0.58→0.74 | **自述（强）** | 单变量改动；社区多人复现旋转重要 |
| 深度不变架构（3D→max→2D） | **自述 + 三家同构** | 机制论证清晰 |
| 平均后阈值居中 0.5 | **自述（含日志截图）** | 有阈值扫描原始日志（best_th=0.1 可见） |
| 6th 模型对照表 | **可读取（表）** | CV/公开/私榜三列 |
| 2nd 的 1/32 分辨率 | **自述 + 1st 互证** | 无单独消融数字 |
| 全量训练 +0.04 | **自述** | 未给方差 |
| k 折 5→7 公开 +0.1 | **自述（口径存疑）** | 疑似 0.01 或不同口径；登记待核 |
| 自制纸莎草 | **社区证据（无法评估）** | 无 CT，未用于建模 |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **测试旋转的确切规范**：1st 未证实（只做了不变性），6th 从榜分推断；官方是否旋转、旋转多少度（90° 倍数？）未定论；
2. **低分辨率输出的极限**：1/32 是否还够、1/64 会怎样——1st 猜测"更低或许也行"，未验证；
3. **多类输出（nothing/mask/ink）**：1st 说输出更干净但未充分评估——一个被时间截断的方向。

**失败学**

| 失败 | 来源 | 教训 |
| --- | --- | --- |
| 2.5D 当通道（学"哪层有墨"） | 1st | 深度漂移任务不能用固定层切片 |
| 花哨增强（噪声/模糊/粗丢/网格畸变等） | 1st | "旋转与翻转至关重要，其余都是非因素" |
| TTA 加翻转 | 1st | 对已旋转不变的任务无增量 |
| 百分位阈值（1st 未采用） | 1st | 分布假设太强，风险 > 收益（但他也承认自己保守） |
| ConvNext/Mask2Former/Swin+PSPNet/BeiT | 6th | CV/LB 都不稳定；EfficientNet/SegFormer 家族更稳 |
| SegFormer b5 等大模型 | 6th | 更大模型 CV 好但 LB 差（数据量不足过拟合） |
| IR 预训练 / EMNIST 外数据 | 6th | 同源输入有效 ≠ 同源预训练有效；跨域数据有害 |
| 训练 stride 75/56（yukke42） | 2nd | 训练窗口步长过小无效；推理才用更细 stride |
| 3D 编码器 / SegFormer / mixup / 更多层（11th 视角） | 11th | 与其 2.5D+1D pool+UNet 配方相比均无增益 |

### 图证（KStarter 仓库内路径）
- ../../intel/vesuvius-challenge-ink-detection/bodies/417496_img/01.png — crop size
- ../../intel/vesuvius-challenge-ink-detection/bodies/417496_img/05.png — threshold sweep
- ../../intel/vesuvius-challenge-ink-detection/bodies/417496_img/06.png — before

### 出处
- 1st（ryches，112 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/417496
- 6th（chumajin，84 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/417274
- 2nd（tattaka 队，76 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/417255
- 9th（hengck23，43 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/417361
- 11th（tk，33 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/417281
- 自制碳化纸莎草（136 票）：https://www.kaggle.com/competitions/vesuvius-challenge-ink-detection/discussion/407545
- 未收录缺口（登记备查）：417430（7th）｜417536（3rd）｜417779（4th）｜417642（5th）｜417448（top solutions 讨论）

### 外部题解（kaggle-solutions）
- rank 3｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417536
- rank 4｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417779
- rank 5｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417642
- rank 7｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417430
- rank 8｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417383
- rank 10｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417363
- rank 12｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/418921
- rank 13｜description：https://www.kaggle.com/c/vesuvius-challenge-ink-detection/discussion/417444

---

## vesuvius-challenge-surface-detection — Vesuvius Challenge - Surface Detection 轻量深读（Tier B）

> 主题 cv ｜ 类别 Research ｜ 指标 Vesuvius 2025 Metric ｜ 队伍 1391 ｜ 截止 2026-02-27 ｜ Tier B ｜ 标签 cv,detection
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/vesuvius-challenge-surface-detection.md
> 材料基础：`digests/vesuvius-challenge-surface-detection.md`（6 篇正文：5th 679360 / 1st 679238 / 4th 679222 / Bronze 679221 / placeholder 651532 / 3D Viewer 663144；80 条主题索引）+ 7 张图

### 一句话重述
古卷 CT 的"表面检测"：指标同时惩罚体素级错误与**拓扑错误（洞/隧道 H1）**。真正考的是**表示（SDF vs 二值）+ 全卷推理 + 拓扑后处理**三件事；公私榜脱钩严重。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（nnU-Net 集成） | 4 模型集成（patch 128/192/256 权重）；Set1 公 0.613/私 **0.620**（阈值 0.20）、Set2 公 0.606/私 **0.627**（阈值 0.26）；单模最好 0.587/0.613 | 1st |
| 1st 的后处理链 | 无 PP 0.572/0.596 → 去小连通 0.586/0.614 → 补小洞 0.598/0.622 → 高度图补大洞 0.601/0.625 → binary closing 0.606/**0.627** → fill_holes 持平 | 1st |
| 5th（SDF 路线） | SEResNeXt152+AttUNet；SDF 回归（加权 L1 + mass Dice）；160³ 训练/**320³ 全卷推理**；H1 隧道填充 0→13 轮 = 拓扑 +0.08（本地）；CV/公榜与私榜都不相关 | 5th |
| 4th/Bronze 等 | 未细读（4th 679222、Bronze 679221、placeholder 651532） | 材料 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 5th |
| --- | --- | --- |
| 表示 | nnU-Net 概率输出 + 阈值 | **SDF 回归**（负内正外，clamp[-100,5]） |
| 损失 | nnU-Net（概率） | 0.5×高斯加权 SDF L1（峰权 9.0@ -5 voxel）+ 0.5×SDF-mass Dice |
| 主干 | nnU-Net（patch 128/160/192/224/256） | 自研 SEResNeXt152+Attention UNet（+ResNet152 谱系） |
| 推理 | 滑窗/patch | **全卷 320³**（避免滑窗拓扑伪影）+ 2/8 flip TTA + 权重 NaN 安全 |
| 后处理 | 去小连通（<20K）/ binary closing r=3 / 高度图线性插值补大洞 / 1-voxel 洞查表修补 / binary_fill_holes | 阈值 0.3 / 去尘 / **迭代 H1 隧道填充**（持久同调 + 自适应半径 3.5–7 + 桥检测 + 组件数保护） |
| 私榜 | 0.627 | 5th |

### 共识 / 分歧 / 裁决
**共识一：拓扑感知的"软表示"优于纯二值（5th 强调；1st 的 nnU-Net 概率亦近之）**
SDF 天然编码距离信息，阈值扫描可在 Surface Dice 与拓扑间平滑权衡；BCE 二值模型在拓扑项一致更差；1st 用概率+阈值+后处理同样登顶。**裁决**：不要只学 0/1 mask；用 SDF/距离/概率这类连续表示 + 阈值搜索。置信度：中高。

**共识二：后处理是本场的最大单点增益（两队均称必需）**
1st：私榜 0.596→0.627（+0.031）全靠 5 步后处理；5th：0→13 轮隧道填充 = 拓扑 +0.08，且强调"桥检测/组件数保护"防止误填。**裁决**：在含拓扑项的指标下，后处理不是锦上添花而是主贡献；但每一步都要做"是否引入新洞/是否合并组件"的守卫。置信度：高。

**共识三：全卷推理避免滑窗伪影（5th）；patch 尺寸是多样性来源（1st）**
5th 明确"strided slices 产生的伪影对拓扑极有害"，坚持 320³ 整卷；1st 用不同 patch/训练轮数造集成。**裁决**：推理按整卷（或至少避免跨 sheet 的窗口拼接）；训练端用 patch 尺寸/轮数制造多样性。置信度：中高。

**共识四：公私榜脱钩 → 提交选择是运气成分最大的一环**
5th："本地 CV、公开榜与私榜相关性都差，最终提交选择很糟"；1st 被公榜误导（融合方式与阈值都选反）。**裁决**：融合用 logits、阈值偏大在私榜更好（1st 的教训）；但赛中没有可靠信号，应做多版本对冲。置信度：高（两队独立经历）。

**分歧一：SDF 回归 vs nnU-Net 概率**
5th 的 SDF 路线与 1st 的 nnU-Net 路线都进前 5；5th 自研架构+全卷推理，算力/工程门槛高；1st 依赖成熟 nnU-Net + 后处理。**裁决**：两条路都能赢；SDF 在拓扑项更稳，nnU-Net 在工程与迭代速度上更省。置信度：中高。

**分歧二：隧道填充 vs 几何补洞**
5th 用持久同调找 H1 隧道并球填充；1st 用高度图插值/查表补洞。**裁决**：前者更"拓扑正确"（对 H1 直接优化），后者更简单稳健；最强的组合可能是"几何补洞 + 迭代隧道填充"。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的后处理逐步分数表 | 自述 + 图 | 中高 |
| 5th 的 SDF 损失/隧道填充 +0.08 | 自述 + 图 + 代码（C++ 模块名） | 中高 |
| 公私榜脱钩 | 两队独立自述 | 高 |
| 单模分数/集成权重 | 自述 | 中 |
| "touching sheets" 未解决 | 1st 明示 | 高（问题存在） |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd/3rd 方案未收录；Vesuvius 2025 Metric 的精确定义（Surface Dice 容差 + VOI + topology 权重）未入库。
- "touching sheets"（相邻 sheet 粘连）无有效解法——本场的开放问题。
- 5th 的本地指标实现（GPU VOI/Betti matching）与 C++ 模块细节未展开。
- 4th/Bronze/placeholder 帖（含 651532 的图）未细读。

### 图证（KStarter 仓库内路径）
- ../../intel/vesuvius-challenge-surface-detection/bodies/679360_img/01.png — SDF 目标与高斯权重
- ../../intel/vesuvius-challenge-surface-detection/bodies/679238_img/01.jpg — 高度图补大洞

### 出处
- 5th（679360）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/679360
- 1st（679238）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/679238
- 4th（679222）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/679222
- Bronze（679221）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/679221
- placeholder（651532）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/651532
- 3D Viewer（663144）：https://www.kaggle.com/competitions/vesuvius-challenge-surface-detection/discussion/663144

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/1st-place-solution-for-the-vesuvius-challenge-su
- rank 2｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/2nd-place-solution-vesuvius-challenge-a-postproc
- rank 3｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/quick-preview-of-the-3rd-place
- rank 4｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/4-th-place-solution
- rank 5｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/5th-place-solution
- rank 7｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/7st-place-solution-for-the-vesuvius-challenge
- rank 8｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/8th-place-solution
- rank 9｜description：https://www.kaggle.com/c/vesuvius-challenge-surface-detection/writeups/9th-place-solution

---

## wikipedia-image-caption — Wikipedia Image/Caption Matching 轻量深读（Tier B）

> 主题 cv ｜ 类别 Playground ｜ 指标 NDCG@{K} ｜ 队伍 105 ｜ 截止 2021-12-09 ｜ Tier B ｜ 标签 cv,nlp,retrieval,ranking
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/wikipedia-image-caption.md
> 材料基础：`digests/wikipedia-image-caption.md`（6 篇正文：Shopee 相似赛方案总汇 283917 / 相似赛索引 272091 / 大数据图像处理 272204 / starter notebook 汇编 273309 / captioning 论文与实现 272172 / 官方欢迎 272023；32 条主题索引）+ 0 张归档图

### 一句话重述
把 Wikipedia 的图片与多语言描述/标题做**检索匹配**（NDCG@K）：数据规模巨大、跨语言、图片以 URL 形式给出。归档材料几乎全是"知识搬运"型：最高票帖子把 **Shopee Price Match**（商品图文匹配）从第 1 到第 161 名的方案全部列出来直接复用；另外就是大规模图片 I/O 的工程帖（URL 下载、feather/datatable、LMDB/HDF5、并发）与 captioning 论文/实现清单。本场的教训集中在"数据工程与评测口径"而非模型本身：test 图下不下来、内存不够、提交格式难、零分排查。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与任务 | **105 队**；NDCG@K；图像 ↔ 多语言标题/描述匹配；Playground；截止 2021-12-09 | 索引 / 272023 |
| 直接可复用方案库 | Shopee 图文匹配赛 **1st–161st** 方案链接总汇（含 1/2/4/5/6/7/8/10/11/14…名），作者本人是 Shopee 银牌 | 283917 / 272091 |
| 大规模图像 I/O（14 票） | 图片走 URL：`urlretrieve`、`nrows` 限行读表、Pillow；存储格式比较 LMDB/HDF5/磁盘；读写计时（`timeit`）与并发读取；配 Real Python"storing images in Python"教程 | 272204 |
| starter 汇编（17 票） | EDA、urllib 演示、加速下载、datatable 替代 pandas、I/O trick、直接读 Wikipedia 表；附往届相似赛获奖清单 | 273309 |
| 论文/实现（14 票） | awesome-image-captioning 仓库；Compositional Neural Module Networks、CapWAP、Scene Graph、Diverse Captioning 等；PyTorch ImageCaptioning、TF image_captioning、neuraltalk2、densecap 实现 | 272172 |
| 其他资源 | 文本-图像匹配论文 tl;dr（12 票）；多语言 BERT embedding 与图像 embedding 对齐（10 票）；易用版数据集（9 票）；可训练 PyTorch starter（7 票）；feather 化 TSV（6 票）；RapidFuzz/FuzzyWuzzy（5 票）；Rapids/Dask/Datatable/Feather/HDF5/Parquet 对比（5 票）；NFNets Keras 复现（4 票） | 索引 |
| 常见坑 | test 图片下载不了（5 票 / 6 评论）；内存不足；读 TSV 报错；binary classification 提交难；test embedding 疑似错误；为什么 0.0000 分；公开 notebook 分享公告（截止前一周限制） | 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 复用 Shopee 路线 | 多语言双塔路线 | 数据工程路线 |
| --- | --- | --- | --- |
| 输入 | 图像 embedding + 文本 embedding | 多语言 BERT + 图像编码器 | URL/feather/datatable |
| 匹配 | kNN/相似度 + 后处理 | 对比学习/检索 | 先解决下载与内存 |
| 风险 | 商品域 vs 百科域差异 | 多语言对齐难度 | 零分/评测口径 |

### 共识 / 分歧 / 裁决
**共识一：这是图文检索题，Shopee 方案可直接迁移（283917 / 272091；置信度中高）**
结构相同（query 文本 ↔ 图库检索，NDCG/召回类指标），Shopee 的 embedding + kNN + 重排 + 后处理经验齐全。**裁决**：先复现 Shopee top 方案的检索骨架，再替换域内编码器与多语言文本塔。置信度：中高。

**共识二：先解决 I/O 与内存，再谈模型（272204 / 273309 / 272531；置信度中高）**
URL 下载、TB 级表、内存不足、TSV 读错是最高票帖的共同主题。**裁决**：把数据落成 feather/parquet 或 LMDB，按行分批 + 并发下载；训练前只保留需要的字段与图像。置信度：中高。

**事件一：多语言文本塔是本题相对 Shopee 的增量（277601 / 273083；置信度中）**
社区明确试验"多语言 BERT embedding 与图像 embedding 对齐"，并赞叹数据多样性。**裁决**：文本塔用多语言模型（mBERT/XLM-R），用对比损失把同图多语言描述拉到同一嵌入邻域。置信度：中。

**事件二：评测/数据细节会直接吃掉分数（287955 / 272846 / 272294 / 286451；置信度中高）**
test 图下载失败、test embedding 疑似错误、提交格式难、大量 0.0000 分。**裁决**：先做"最小提交"验证管线（少量样本 → 生成提交 → 看是否有非零分），再规模化。置信度：中高。

**事件三：生成式 captioning 是参考而非主线（272172 / 272223；置信度中）**
论文清单是 captioning 方向，但本赛是匹配/检索；也有帖问"先生成 caption 再匹配"。**裁决**：captioning 用来做数据增强/解释可以，主指标仍靠检索式对比学习。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 任务与赛制 | 官方欢迎帖（272023） | 高 |
| Shopee 方案总汇可复用 | 社区长帖 + 链接（283917 / 272091） | 中高（外部方案，未逐条复核） |
| 大规模图像 I/O 方法 | 高票帖子（272204 / 273309） | 中高（技术常识 + 链接） |
| captioning 论文/实现清单 | 社区帖（272172） | 中高 |
| 数据/评测坑 | 多帖（287955 / 272846 / 272294） | 中 |
| 多语言 BERT 对齐 | 单帖（277601） | 中低 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 本赛没有夺冠方案归档（最高票是资源帖）；
- test embedding 是否有官方错误未在归档中确认；
- 公开 notebook 一周限制对最终名次的影响未知；
- 内存/数据集版本更新（272501）的影响未量化；
- **图证缺口**：本场 0 张归档图，已登记。

### 出处
- 官方欢迎（16 票 / 16 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272023
- Shopee 方案总汇（5 票 / 0 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/283917
- 相似赛索引（13 票 / 4 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272091
- 大规模图像处理（14 票 / 6 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272204
- starter 汇编（17 票 / 3 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/273309
- captioning 论文与代码（14 票 / 1 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272172
- 多语言 BERT + 图像 embedding（10 票 / 5 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/277601
- test 图下载问题（5 票 / 6 评论）：https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/287955

---
