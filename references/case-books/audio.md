# 案例书：audio（5 场）

> 由 KStarter 深读文档生成：每场含一句话重述、全量数字账、逐方案对照矩阵、共识/分歧与裁决全文、证据分级、悬案与失败学、图证路径与出处。
> 用途：为新比赛找结构类比时，先读本册，再回 KStarter 深读原文核对。

## bengaliai-speech — Bengali.AI Speech Recognition 轻量深读（Tier B）

> 主题 audio ｜ 类别 Research ｜ 指标 Word Error Rate ｜ 队伍 744 ｜ 截止 2023-10-17 ｜ Tier B ｜ 标签 audio
> 材料基础：`digests/bengaliai-speech.md`（6 篇正文：1st 447961 / 2nd 447976 / 3rd 447957 / 5th 448006 / 44th 450635 / 实验帖 425496；80 条主题索引）+ 6 张图

### 一句话重述
孟加拉语语音识别（低资源 + **未验证的噪声标注**）。真正的考点是**"标注噪声治理"**：Whisper/Wav2Vec 系模型对错误转写极其敏感，会去学"错误音频-文本对"——因此数据清洗（MOS/WER 过滤）、外部数据、伪标签与"用 LM/标点模型补上下文"是主线；模型结构本身几乎不创新。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（447961） | **Whisper-medium**（HF trainer，8×A6000，bs=8、lr=1e-5、50k 步）；增强：频谱抖动、时间/频率遮蔽、**16k→8k→16k 重采样**、libsonic 变速变调；推理 `max_length=260, num_beams=4, chunk_length_s=20.1`；数据：OpenSLR-37/53、MadASR、Shrutilipi、Macro、Kathbath、**GoogleTTS 合成 42 万条**、YouTube 伪标；**三轮过滤式自训练**（对 MadASR/Shrutilipi/Macro/Kathbath 推理、只留 WER<15% 的音频再训）→ Macro 验证 8% WER、公榜 ≈0.380；拼接短音频成长音频（~7 万条）→ 0.370；**自训 12k 词表孟加拉 tokenizer**（beam 8 + 20.1s chunk 的 7 小时内推理）→ 0.360；**4 模型标点集成** → 0.325；更多 YouTube 伪标 → **0.312 pub / 0.372 priv**；作者本职是低资源中亚语言 ASR，明说"**修标注噪声是本场最关键的事**" | 447961 |
| 2nd（447976） | ASR = **indicwav2vec_v1_bengali**；数据：竞赛 + Shrutilipi + MADASR + ULCA（部分链接失效）+ 噪声（MUSAN、DNS Challenge 2020）；**朗读语音重增强、自发语音轻增强**；**concat 增强**让训练长度分布贴近 OOD 测试；SpecAugment；先全量训练、再剔除 WER 最高 10% 重训；不冻结特征编码器；cosine + warmup restarts（5/3/3 epoch，峰值 lr 4e-5/3e-5/2e-5）；推理用 transformers pipeline 分块 + stride；外加 **6-gram KenLM**（IndicCorp v1+v2）与标点模型 | 447976 |
| 5th（448006） | 从 YellowKing 管线起步改 IndicWav2Vec + 重初始化 CTC；发现"**训练太久后本地 WER 与公榜脱钩**"——推测在学错误的音频/标注对；**剔除 MOS>2.0 的样本 → 0.472**；再用模型重新标注并去掉两侧 WER>0.5 的样本，本地-公榜相关性恢复；210k 步（bs16、lr8e-5）→ **0.452（无 LM）**；**集成法：把多个微调模型的最后一层隐状态拼接 → 加 Transformer 编码器 + CTC（冻结原模型，只训新头）**，全管线 0.355→**0.344**（仅 7k 步、bs8） | 448006 |
| 3rd（447957） | 见 digest（第 368 行起），以 Wav2Vec 系 + 语言模型为主 | 447957 |
| 44th（450635） | 低名次方案：说明"资源受限 + 基线微调"也能拿分 | 450635 |
| 社区侧 | "[LB 0.481] 我的实验结果"（52 票）；"**微调是关键**（LB 0.445）"（47 票）；"资源高效训练的数据集与检查点"（36 票）；"WER 的 S/I/D 分解 + 加数据太慢"（28 票）；"Wav2Vec2 + LM 基线（0.471）"（27 票） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 5th |
| --- | --- | --- | --- |
| 底座 | Whisper-medium | indicwav2vec_v1_bengali | IndicWav2Vec（重初始化 CTC） |
| 外部数据 | OpenSLR/MadASR/Shrutilipi/Macro/Kathbath + GoogleTTS + YouTube 伪标 | 竞赛+Shrutilipi+MADASR+ULCA | 竞赛 + YellowKing 管线 |
| 噪声处理 | **三轮自训练（WER<15% 过滤）** + 拼长音频 | **剔除 WER 最高 10%** | **MOS>2.0 过滤 + 双向 WER>0.5 清洗** |
| 增强 | 频谱抖动/遮蔽、重采样链、libsonic | audiomentations（分场景强度）+ concat + SpecAugment | — |
| 解码/后处理 | 自训 12k tokenizer + beam4 + 标点 4 模型集成 | 6-gram KenLM + 标点 | 外部 LM + 标点 |
| 集成 | 单模型为主 | 单模型 + LM | **隐状态拼接 + 新 Transformer/CTC 头** |

### 共识 / 分歧 / 裁决
**共识一：标注噪声是本赛的头号敌人（1st/2nd/5th）**
1st 明说"竞赛数据未验证、修标注噪声最关键"；5th 观察到"训练过久本地与公榜脱钩，疑似在学习错误的音频/标注对"；2nd 也剔除最高 WER 的 10%。**裁决**：低资源 ASR 的数据清洗（MOS/WER 过滤、重标注、伪标签筛选）是**先于建模**的工作；不做清洗，训练越久越糟。置信度：高（多队独立 + 机制自洽）。

**共识二：外部数据 + 合成语音 + 伪标签是主要扩容手段（1st/2nd/5th，社区帖子标题亦如此）**
1st 用 42 万条 GoogleTTS 合成语音、YouTube 伪标；2nd 用 Shrutilipi/MADASR/ULCA；社区教程强调"微调是关键"（Whisper-large-v3 微调帖 47 票）。**裁决**：低资源语音的容量扩展顺序 = 公开语料 → TTS 合成 → 伪标真实录音。置信度：高。

**共识三：LM/标点后处理是"最后一公里"（1st/2nd）**
1st 加 4 模型标点集成后公榜 0.360→0.325；2nd 配 6-gram KenLM + 标点模型。**裁决**：ASR 的 WER 里有一块来自格式（标点/大小写/数字），专门的后处理模型是独立增益点。置信度：高。

**分歧一：Whisper 还是 Wav2Vec2 系**
1st 选 Whisper-medium（"对 OOD 音频很鲁棒，甚至能转写歌词；但对标注噪声极敏感"）；2nd/5th 用 IndicWav2Vec + CTC。**裁决**：Whisper 的鲁棒性适合脏/OOD 数据，但需要更重的噪声治理；自监督 CTC 系在本地数据充分时更稳、更省算力。置信度：中高。

**分歧二：如何集成 ASR 模型**
5th 发现"直接平均 logits 不行（预测不对齐）"，改用**隐状态拼接 + 新 Transformer/CTC 头**（冻结原模型只训新头）→ 全管线 0.355→0.344；1st/2nd 主要靠单模型 + LM。**裁决**：异构 ASR 的融合要在"表示层"而不是"输出层"做。置信度：中高（有对照）。

**事件：本地与公榜脱钩（5th 的诊断）**
5th 给出可操作症状：本地 WER 继续降而公榜变差 = 在拟合错误标注；清洗后两者恢复相关（210k 步仍可训）。**裁决**：长训练前先做"本地-公榜一致性"体检；把这条作为噪声数据的标准诊断。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的三轮自训练分数链（0.380→0.312） | 自述 + 完整分数 + 公开权重/数据 | 高 |
| 5th 的 MOS/WER 清洗与本地-公榜脱钩诊断 | 自述 + 架构图 | 中高 |
| 2nd 的分场景增强与 KenLM | 自述 + 代码片段 | 中高 |
| 隐状态拼接集成的收益（0.355→0.344） | 自述（单次实验，全管线口径） | 中 |
| 社区教程"微调是关键" | 多帖共识 | 中高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 3rd 的方案未细读（digest 有正文）；44th 的具体做法未展开；
- 1st 未给"三轮自训练"的逐轮数据量与 WER 分布；
- 5th 的隐状态集成只在一个配置上验证，缺少多模型/异构（Whisper+HuBERT）证据；
- 归档 6 图：5th 的集成架构（图 1）、3rd 的 2 张图、实验帖的 1 张；1st/2nd 无图归档。

### 图证（KStarter 仓库内路径）
- ../../intel/bengaliai-speech/bodies/448006_img/01.png — 5th 的隐状态拼接集成

---

## birdclef-2022 — BirdCLEF 2022 深读：稀有类分组 × 损失分工 × 阈值校准

> 主题 audio ｜ 类别 Research ｜ 指标 Weighted Categorization Accuracy ｜ 队伍 801 ｜ 截止 2022-05-24 ｜ Tier A ｜ 标签 audio,wildlife
> 材料基础：`digests/birdclef-2022.md`（6 篇：抄袭举报 177 票/实验分享 156/1st models 63/public#1-private#2 59/3rd 56/起点帖 51；80 条索引）+ 3 张图

### 一句话重述
题面是"识别声景中的鸟鸣，但只对 21 个 scored birds 计分"，实际被考的是**稀有类分工 + 阈值校准**：
1. **类内极端不平衡**：21 个计分鸟中 14 种有 ≥10 条训练样本（Group1），7 种极少（Group2，最少的 `maupar` 只有 1 条，被拆成 5 份使用）。稀有类不能与常见类共用一套损失与阈值。
2. **损失分工是 3rd 的核心发现**：focal loss 对小类召回更友好但更"保守"，BCE 对大类更准——**按样本量把鸟分成两组，Group1 用 BCE（CNN+SED）、Group2 用 focal（SED）**，配合逐鸟阈值可带来 0.02–0.03 提升（其对照：SED-BCE 私 0.7563 vs SED-focal 私 0.8135）。
3. **阈值是隐形大杠杆**：指标是"切片 → clipwise 概率 → 阈值 → 多标签准确率"；逐鸟阈值（0.05/0.35）、分位数阈值（测试分布自适应，0.25）、非目标分布 91 分位（等价固定 FPR）三种策略并存；3rd 直言"没有合适阈值就看不出模型真实性能"。
4. **骨架是 SED + secondary labels**：tattaka 的 BirdCLEF 2021 4th 方案（SED、clipwise/framewise/attention 头、BCE2wayLoss/BCEFocal2WayLoss）被 1st/3rd/起点帖全员复用；标签用软权重（primary 0.9995 / secondary 0.5 / other 0.0025）。
5. **BirdNET 事件**：主办方自己的 BirdNET 模型覆盖 20/21 scored birds，license 澄清后允许使用；public#1/private#2 方案靠它拿到公榜 0.91，但私榜跌到 0.84——**公榜红利的教科书案例**；1st 的最终融合也包含 BirdNET。
6. **治理插曲**：全站最高票帖（177）是"抄袭举报"——三个复制粘贴 kaerururu notebook 的 notebook 获得高赞；社区用举报与署名规范维护分享生态。
一句话：**这是一场"稀有类分工 + 阈值校准"的音频检测赛**——模型骨架是 SED/CNN，胜负在损失与阈值的分组设计。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 计分范围 | 仅 21 个 scored birds（152 类中的）；Group1 14 种 ≥10 样本；Group2 7 种（maupar 仅 1 条拆 5） | 3rd |
| 3rd 单模型 | CNN 无增强 0.7715/0.7278；CNN 增强 0.7761/0.7359（公/私） | 3rd |
| 3rd 纯集成 | CNN 集成 0.8327/0.7898；SED 4 折 0.8339/0.7823 | 3rd |
| 3rd bird split | 组合 0.8532/0.8052；更多模型 0.8750/0.8126（best public）；安全版 0.8556/0.8071；**best private 0.8707/0.8274（未选）** | 3rd |
| 3rd 损失对照 | SED-BCE 私 0.7563 vs SED-focal 私 0.8135；CNN-BCE 私 0.7678 | 3rd |
| 3rd 阈值 | Group1 0.05；skylar 0.35；Group2 非目标 91 分位 | 3rd |
| 1st 单模型 | effnet_b3_ns Val .8789/公 .82/私 .78；eca_nfnet_l0 Val .8864/公 .82/私 .78 | 1st |
| 1st 训练 | 15s chunk；stride (2,2)→(1,1)；2 阶段（2021+2022→scored 过滤）；3 checkpoint 平均；分位数阈值 0.25 | 1st |
| BirdNET | 公榜 0.91→私榜 0.84 大跌；CPU <2h vs 自训 GPU ~8h；20/21 类重合 | public#1 |
| 自训方案 | 私榜 0.79（未选）；Top5 邻域时序后处理（±5s 内检出则补 top5 类） | public#1 |
| 赛事 | 801 队；Weighted Categorization Accuracy；80 帖 | 元数据 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st（models 部分） | 3rd | public#1/private#2 | kaerururu 实验 |
| --- | --- | --- | --- | --- |
| 模型 | SED（tattaka）+ effnet_b3_ns / eca_nfnet_l0；stride 改 (1,1) | CNN（2021 2nd 方案）+ SED（2021 4th） | BirdNET（主办方）+ 自训 SED/CNN | SED + 2nd label 训练 |
| 稀有类处理 | 加权 sampler/loss；2 阶段过滤 scored birds | **bird split + focal/BCE 分工**；小类过采样/手工拆分 | 依赖 BirdNET 覆盖 | 公共基线 |
| 标签 | secondary labels | 软权重 primary 0.9995/secondary 0.5/other 0.0025 | — | 2nd label notebook |
| 阈值 | 分位数阈值 0.25（单模型）；普通阈值 0.2–0.3（集成） | Group1 0.05（skylar 0.35）；Group2 非目标 91 分位 | 后处理 +（未细述） | — |
| 数据/增强 | Gaussian/Pink 噪声、OR-Mixup、背景噪声（2021 nocall/esc50） | mixup/cutmix/spec-augment/背景噪声混入（freefield1010/aicrowd2020/nocall） | BirdNET + 自有增强 | 公共数据集 |
| 验证 | 5 折分层；maupar 拆 5；只算 scored birds 的 LB 代理指标 | "找不到好 CV，主要靠公榜" | — | — |
| 集成 | 3 checkpoint 权重平均 + 多模型融合（含 BirdNET） | 28 模型（8 CNN+8 SED G1+12 SED G2）+ 时间平滑 | 单模型为主 | — |
| 成绩 | 单模型 Val 0.879/0.886、公 0.82、私 0.78 | best public 0.875/私 0.8126；safe 0.8556/0.8071；best private 0.8707/**0.8274**（未选） | BirdNET 公 0.91/私 0.84 | 公 0.71 |
| 失败清单 | —（models 帖未列） | PCEN、加权 BCE、rating 数据、pitch shift、coord-conv；部分增强 | 自训模型私 0.79（未选） | — |

### 共识 / 分歧 / 裁决
**共识一：稀有类必须与常见类分开处理（3rd 的 bird split；1st 的加权/两阶段；全员）**
3rd：按样本量把 21 种鸟分成 Group1（≥10 样本，14 种）/ Group2（7 种）；
1st：按 primary_label 计算采样与损失权重，并在第二阶段只保留含 scored birds 的样本微调；
3rd 的对照：SED-BCE 私 0.7563 vs SED-focal 私 0.8135；bird split 组合 0.8052，后续提升到 0.8274。

**裁决**：极端不平衡下的正解是"按类群分组 + 组内选损失/阈值"，而不是全类统一。置信度：高（有分组前后对照）。

**共识二：阈值校准是模型之外的第二引擎（3rd/1st 明确，多队默认）**
3rd：Group1 0.05、skylar 0.35、Group2 用非目标分布 91 分位；"没有阈值就看不出真实性能"；
1st：分位数阈值（0.25）单模型更好、普通阈值（0.2–0.3）集成更好；
public#1：后处理中也要调阈值。

**裁决**：多标签分类指标下，阈值是每个模型集/每个类别都要重新校准的"最后一公里"；分位数阈值（对测试分布自适应）在单模型场景更稳。置信度：高。

**共识三：SED + secondary labels + 背景噪声增强是骨架（4/4）**
1st/3rd：tattaka 的 SED（2021 4th）为骨干；
标签：primary/secondary 软权重；
增强：背景噪声混合（freefield1010/aicrowd2020/2021 nocall）、mixup/cutmix/spec-augment。

**裁决**：音频弱标签赛的通用配方；背景噪声混入直接模拟测试声景的信噪比结构。置信度：高。

**分歧一：BirdNET 的使用与公榜红利（本场最大争议）**
public#1/private#2：直接用主办方 BirdNET（20/21 类重合，改 species_list），license 澄清后允许；公榜 0.91、私榜 0.84；
1st：把 BirdNET 放进最终融合（但自己的模型才是主贡献）；
3rd：**明确"我们没用 BirdNET"**。

**裁决**：BirdNET 在公榜上系统性高估（可能训练数据覆盖 public 片段），私榜红利不可依赖；允许使用但应把它当"外部强模型"审计（对照 T8/T18）。置信度：高（涨跌数字直接）。

**分歧二：验证与提交选择**
3rd："找不到好 CV，主要看公榜"；提交了两个（best public 0.875/0.8126 与低阈值安全版 0.8556/0.8071），最佳私榜 0.8274 未选；
1st：自建 5 折分层 + scored-bird 专用代理指标优化阈值。

**裁决**：阈值敏感 + 小测试集 → public/private 排序翻转频繁；**提交对冲（激进 + 保守）**优于选 public 峰值。置信度：高。

**分歧三：增强/损失细节的有效性**
3rd：mixup（最有影响）、背景噪声、spec-augment、cutmix 有效；PCEN、加权 BCE、rating 数据、pitch-shift、coord-conv 无效；
1st：Gaussian/Pink 噪声 + OR-Mixup + 背景噪声有效。

**裁决**：**模拟测试声景的增强（噪声/混音）**稳定有效；特征级（PCEN）与标签费率类改动无收益。置信度：中高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| bird split 与损失对照 | 自述 + 3 张分布图 + 公开推理 kernel | 高 |
| BirdNET 公/私涨跌 | public#1 自述（含主办方 license 说明） | 高 |
| 1st 的 SED/两阶段/阈值 | 自述 + GitHub + kernel 链接 | 中高 |
| 抄袭举报 | 三个 notebook 可核 | 高 |
| kaerururu 实验帖 | 公共 notebook/数据集（可复现） | 高 |
| 3rd 的"找不到好 CV" | 自述 | 中 |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **BirdNET 是否被正式认定为"允许的宿主红利"**：主办方在 issue 中同意不执行非商业条款，但对其是否构成不公平优势无结论；1st 的融合里也含 BirdNET。
2. **public→private 大跌的机制**未证实（可能 public 片段进入 BirdNET 训练数据）。
3. 7th 方案（326973）与指标解释帖未收录；"Previous Audio Competitions"（307824）未收录。
4. 3rd 的"找不到好 CV"具体尝试清单未展开。

**失败学（跨队合集）**

- 特征类：PCEN、加权 BCE（按类频次）、rating 数据、pitch-shift、coord-conv（3rd 的负结果）。
- 增强类：SED 上的 mixup、RandomLowpassFilter（3rd）；"augment only scored birds"、"multiply loss ×10"（3rd）。
- 流程类：复制粘贴 notebook（治理）；推理耗时 2h 未优化（起点帖）；只按公榜选提交（3rd 的教训）。

---

## birdclef-2023 — BirdCLEF 2023 轻量深读（Tier B）

> 主题 audio ｜ 类别 Research ｜ 指标 buffered_cmAP ｜ 队伍 1189 ｜ 截止 2023-05-24 ｜ Tier B ｜ 标签 audio,wildlife
> 材料基础：`digests/birdclef-2023.md`（6 篇正文：1st 132 / Pretraining 0.80 88 / 2nd 67 / 4th 55 / 7th 38 / 10th；80 条主题索引）+ 2 张图

### 一句话重述
从声景录音识别鸟种（padded cmAP）。真正考的是**数据侧审计与整理（含 API bug 发现）+ 弱标签/无鸟段处理 + 知识蒸馏/预训练 + 推理加速**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（Correct Data is All You Need） | 294 次实验；发现 **Xeno-Canto API 每物种最多 500 文件**的元数据 bug（多 json 只取第一个）→ 修复后数据大幅扩充；5 折分层；**padded cmAP 要"跨折取均值、不要 OOF"**；CV 0.908/公 0.844/私 **0.764**；3 个 SED 模型（eca_nfnet_l0、convnext_small、convnextv2_tiny）+ ONNX；类采样权重 (count/sum)^0.5 | 1st |
| 1st 的预训练反复 | 只用 2023 数据时预训练增益大；加入额外数据后 LB 不再增益（CV 仍涨）→ 最后一周加严筛选（822 物种、>10 代表）后 **+1 公榜/+2 私榜** | 1st |
| 2nd | 7 模型集成（SED + 2021 2nd CNN）；openvino；伪标+**人工听标 ~1800 条 nocall 无提升**；ebird 数据非公开（问过 host） | 2nd |
| 4th（KD is all you need） | 4×eca_nfnet_l0（mel/PCEN 变体）；**Kaggle Models 预计算 bird-vocalization-classifier 做 KD**（其 cmAP5=0.9479）；公 0.831/私 0.744；额外 no-call/XC/Zenodo/esc50/aicrowd 噪声 | 4th |
| 7th（sumix） | 19 模型集成（effnet_b2+rexnet150）；`sumup/sumix` 双鸟叠加增广；KD（rkl 前缀）；openvino；私 0.7471 | 7th |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 4th | 7th |
| --- | --- | --- | --- | --- |
| 骨干 | 3×SED（nfnet/convnext） | SED+CNN 7 模型 | 4×eca_nfnet_l0 变体 | effnet_b2+rexnet150×19 |
| 数据杠杆 | XC API 修复+严格预训练筛选 | XC 额外数据；伪标+手标 nocall | no-call/XC/Zenodo 噪声 | KD 全量重训 |
| 蒸馏/预训练 | 预训练（条件性有效） | — | **强 KD** | **KD** |
| 增广 | Mixup OR/背景/RandomFiltering/SpecAug | — | 激进 mixup + 多 epoch | **sumup/sumix** |
| 推理 | ONNX；温度均值+attention/max 加权 | openvino | — | openvino（图 1） |
| 私榜 | **0.764** | 2nd | 0.744 | 0.747 |

### 共识 / 分歧 / 裁决
**共识一：数据侧（额外录音+无鸟段+背景）是第一杠杆（4/4）**
1st 的 API bug 修复与严格物种筛选、2nd 的 XC 额外数据、4th 的 no-call/Zenodo/esc50 噪声、7th 的全量 KD 重训。**裁决**：BirdCLEF 类弱标签声景赛，先把"训练数据分布"修对（含 no-call 负样本与背景噪声），再谈模型。置信度：高。

**共识二：知识蒸馏/预训练是第二杠杆，但条件性强（1st/4th/7th）**
4th：用 Kaggle Models 的强分类器 KD（其验证 cmAP5=0.9479）是核心；7th：19 模型 KD；1st：预训练只在"筛选后的 822 物种"下重新有效。**裁决**：蒸馏/预训练有效，但会被数据分布变化抵消；要把它当"最后一轮条件实验"而不是默认组件。置信度：高。

**共识三：推理加速决定能否承载大集成（2nd/7th 图证）**
openvino 最快（~0.024s）、onnx 次之（~0.026s）、torch_jit 最慢（~0.041s）；1st 用 ONNX。**裁决**：声景推理算力昂贵，加速=更大的可承受集成与 TTA。置信度：高（有测量图）。

**分歧一：伪标/人工标注 nocall 是否有效**
2nd 手标 ~1800 条 nocall **无提升**（怀疑伪标 FP 多）；4th/1st 用外部 no-call 数据有效。**裁决**：外部成规模 nocall 有效；在伪标质量不明时手标性价比低。置信度：中。

**分歧二：验证与提交口径**
1st：padded cmAP 要跨折均值（不是 OOF），CV 绝对值（0.908）与 LB（0.764）差很大但排序相关好；4th：只选"CV 和 LB 同涨"的方案。**裁决**：以排序/相关性为准则，不要跨口径比绝对值。置信度：高。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| XC API 500 上限 bug | 自述（数据统计+机制解释） | 中高（可复核） |
| 1st 的 CV/LB 数字与实验量 | 自述 | 中高 |
| KD 的有效性（4th/7th） | 自述 + 公开模型 | 中高 |
| openvino/onnx 速度差 | 图证 | 高（测量层面） |
| 手标 nocall 无效 | 自述（单队） | 中 |

### 悬案与失败学
**事实：失败的模型方向清单很有信息量（1st）**
Transformer（ECAPA TDNN）、更大 chunk、CQT/LEAF、彩色噪声、2021 2nd 的噪声方案、整库 XC 预训练等均无效——**弱标签音频仍以 CNN/SED + 频谱增广为主**。置信度：中高。

**5. 悬案与缺口（登记）**
- 3rd/5th/6th/8th/9th 等方案未收录；1st 承诺的 CV-LB 相关性论文"TBD"。
- XC API bug 的修复现状/官方回应未知（1st 用的是旧 commit）。
- 4th 的 KD 细节（如何用预计算 logits、温度/权重）未展开；2nd 的伪标 FP 假设未验证。

### 图证（KStarter 仓库内路径）
- ../../intel/birdclef-2023/bodies/412922_img/01.jpeg — 推理库耗时对比

---

## birdclef-2025 — BirdCLEF 2025 深读：多轮 Noisy Student 自训练工程

> 主题 audio ｜ 类别 Research ｜ 指标 Birdclef ROC AUC ｜ 队伍 2031 ｜ 截止 2025-06-05 ｜ Tier A ｜ 标签 audio,ranking,wildlife,education
> 材料基础：`digests/birdclef-2025.md`（6 篇：1st 263 票/recipe 119/2024 技法汇总 73/5th 69/系列索引 55/2nd 54；80 条索引）+ 11 张图

### 一句话重述
题面是"声景中 206 类鸟类（含两栖/昆虫）多标签识别，ROC AUC"，实际被考的是**半监督自训练工程**：
1. **范式已经变了**：2nd 原话——"2023 之前是 Additional Data is All You Need，2024 起变成 Journey Down the Rabbit Hole of Pseudo Labels"。头部全部依赖对未标注 soundscapes 的伪标签迭代；1st 的监督基线只到公榜 **0.872**，四轮自训练后 **0.930**。
2. **Noisy Student 的三个旋钮**：① 伪标数据必须以 **MixUp** 方式混入（简单拼接失败；mix 比例 0→1.0 对应 0.872→0.898，1.0 最好）；② 每轮伪标要做 **power transform**（概率取幂，压制"自信噪声"，否则第 3 轮起不收敛）；③ **Stochastic Depth（drop_path=0.15）**只在自训练有效——这三点共同定义了"noisy student"。
3. **预训练是第二引擎**：2nd 用 Xeno-Canto 大规模预训练（7400–7800 类）把 0.83–0.84 抬到 0.86–0.87；但只用往届竞赛数据预训练反而变差——**预训练语料的规模与多样性是关键**。
4. **输入/架构/推理**：20s chunk（1st 的时长对照 5/10/15/20/30s = 0.842/0.864/0.87/0.872/0.872）+ SED head + 小 EfficientNet（B0/B3/v2s/nfnet_l0）；**framewise 重叠平均**（1D 版滑窗 TTA，+0.002–0.003）；平滑/delta-shift TTA/OpenVINO。
5. **稀有类与家族标签陷阱**：Insecta 的科级标签（Cicadidae/Gryllidae/Tettigoniidae）实际与特定区域物种绑定——混入家族级数据有害；改成"按 Xeno-Canto 物种打新标签"训练专用模型才有效（+0.002–0.003）。
6. **验证的失效与例外**：2nd 实测 <1% AUC 差异时 CV 与 LB 几乎无相关；1st 直接"只用 public LB"（host 明示公私同分布，且事后证明诚实）。这与多数场次相反，是本场可登记的例外（对照 T18）。
一句话：**这是一场"自训练工程"比赛**——模型小、数据少，胜负在伪标签的混合方式、降噪变换与迭代停止点上。

### 关键数字（数字账）
| 动作 | 数字 | 来源 |
| --- | --- | --- |
| 1st chunk 时长对照 | 5s 0.842 / 10s 0.864 / 15s 0.87 / 20s 0.872 / 30s 0.872（5 SED b0 集成） | 1st |
| 1st mix 比例对照 | 0 → 0.872；0.25 → 0.883；0.5 → 0.887；0.75 → 0.89；1.0 → **0.898** | 1st |
| 1st 迭代分数 | 监督 0.872（LB）→ 迭代 1 (power 1) 0.909 → 2 (1/0.65) 0.918 → 3 (1/0.55) 0.927 → 4 (1/0.6) **0.930**；第 5 次失效 | 1st |
| 1st drop_path | 0.15；自训练 +0.005（监督训练无增益） | 1st |
| 1st 推理 | framewise 重叠平均 +0.002–0.003；最终 7 模型等权私 **0.935**（公 0.933/私 0.930 的选中版） | 1st |
| 2nd 预训练 | 7400–7800 类 Xeno-Canto；0.83–0.84 → 0.86–0.87 | 2nd |
| 2nd 伪标 | 迭代 1 选 4,430 文件、迭代 2 选 1,483、迭代 3 选 1,437；阈值 0.5 保留 / <0.1 置零 | 2nd |
| 2nd 后处理/TTA | 每文件 top 概率缩放 +0.005–0.01；2.5s 重叠 TTA +0.005–0.008（0.917→0.922 公/0.91→0.918 私） | 2nd |
| 5th 阶段链 | stage1 0.839 → 蒸馏 ×5 0.884 → +soundscapes 0.921（effv2s）；最终 13 模型公 0.928/私 0.924 | 5th |
| Recipe | mel 参数 0.810→0.859；集成 0.854–0.859 → 0.872 | 573066 |
| 2nd 无鸟段实验 | 跳过无发声段 → LB 下降（保留整段更好） | 2nd |
| 1st Amphibia/Insecta 专用模型 | 700 物种/17,844 样本；min 1 样本/物种；+0.002–0.003 | 1st |
| 赛事 | 2031 队；ROC AUC；80 帖 | 元数据 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd | 5th | Recipe |
| --- | --- | --- | --- | --- |
| Chunk/特征 | 20s；mel 224 bins、n_fft 4096、hop 1252；3×重复 mel | 5s；Spec→2D CNN | 10s；log(mel+1e-6) | — |
| 主干 | SED + effnet_b0/b3/b4、regnety、nfnet_l0 | SED/MLP + effnetv2_s、nfnet_l0 | SED + effnetv2_s/b3、effnet_b3_ns/b0_ns | EfficientNet（中层特征池化） |
| 预训练 | 引 2024 预训练经验 | **Xeno-Canto 7400–7800 类预训练**（关键） | 无（自蒸馏替代） | — |
| 自训练 | **Noisy Student**：MixUp(比例 1.0)+power transform+drop_path 0.15；4 迭代 | 伪标（阈值 0.5/0.1）+按类替换采样；2–3 迭代 | **自蒸馏**：teacher→伪标+原标签，权重重初始化；4–5 轮 + soundscapes 2 轮 | — |
| 采样/损失 | CE（理由：不平衡下更稳）；标签不归一化；WeightedRandomSampler | Focal+BCE；Balanced/平方权重/上采样 | Focal γ=2；稀有类复制 | FocalBCE |
| 推理/后处理 | framewise 重叠平均；平滑 [0.1,0.2,0.4,0.2,0.1]；delta shift；OpenVINO | 每文件 top 概率缩放；2.5s 重叠 TTA；5 折全提交 | 2.5s 重叠 + 平滑 [0.1,0.8,0.1]；OpenVINO | 后处理 + 集成 |
| 集成 | 7 模型跨阶段；**等权最好（私 0.935）** | 3 模型（不同预训练/迭代/采样） | 13 模型（4 组 seed） | 4 模型 0.854–0.859→0.872 |
| 验证 | 无好 CV，仅 public（host 保证） | 分层/按作者分组；高分段相关消失 | 5 折 | public |
| 成绩 | 公 0.933/私 0.930 | 公 0.922/私 0.918（TTA） | 公 0.928/私 0.924 | 公 0.872 |
| 失败清单 | 320+ 想法 95% 红（未列）；target XC 数据有害；family 标签混入有害 | 往届数据预训练、XC/iNat 数据、主数据软标签、time flip | CNN/1D 模型、过多增强、低排名类 power 后处理 | raw-wave 增强有害 |

### 共识 / 分歧 / 裁决
**共识一：伪标签自训练是主引擎（1st/2nd/5th + 2024 汇总）**
1st：监督 0.872 → 4 轮自训练 0.930；
2nd：ablation baseline 0.83–0.84 → 预训练 0.86–0.87 → 伪标 1 0.89–0.895 → 伪标 2–3 0.90–0.91 → TTA 0.922 → 后处理 +0.005–0.01；
5th：3 阶段自蒸馏（stage1 0.839 → distill ×5 0.884 → +soundscapes 0.921）。

**裁决**：有未标注目标域音频时，自训练是最大的单项杠杆；本场三家用了不同变体（noisy student / 替换采样 / 迭代自蒸馏），方向一致。置信度：高。

**共识二：预训练语料要"大而多样"（2nd 的对照；1st/5th 受益）**
2nd：Xeno-Canto 7400–7800 类预训练 +0.03；只用往届竞赛数据预训练变差；新下载的 2025 快照不如 2024 预训练权重；
1st：2024 预训练经验 + 2025 专用模型。

**裁决**：预训练的价值来自**语料规模与物种多样性**，不是"再训一遍"；这与 T8（外部数据有效性条件性）一致。置信度：高。

**共识三：SED + framewise + 重叠平均推理（1st/2nd/5th）**
1st：framewise 重叠平均 +0.002–0.003；"1D 版滑窗分割"；
2nd：2.5s 重叠 TTA +0.005–0.008；
5th：2.5s 重叠 + 平滑。

**裁决**：把 chunk 当独立样本会浪费 SED 的帧级输出；重叠平均是最稳的推理端增益。置信度：高。

**共识四：小 EfficientNet + 适度的增强/后处理（全员）**
骨干集中在 B0/B3/v2s/nfnet_l0；增强有效项：MixUp/Sumix、增益/噪声、时频掩码（有争议）；后处理：时序平滑/hop 后缩放/OpenVINO。

**裁决**：CPU 推理限制决定模型规模上限；工程（量化、复用频谱、多进程）与后处理是必备项。置信度：高。

**分歧一：伪标签的降噪方式**
1st：**power transform**（概率取幂 >1），让多轮迭代继续收敛（1/0.65/0.55/0.6）；
2nd：阈值（>0.5 保留、<0.1 置零）+ 软标签；
5th：teacher 预测与原标签直接混合。

**裁决**：共同目标是"只保留高置信、压制低置信"；1st 的幂变换是**多轮迭代不崩**的关键（第 3 轮起尤其），比硬阈值更平滑。置信度：中高。

**分歧二：验证与 LB 反馈**
2nd：<1% AUC 差异时 CV-LB 无关（高分段散点图）；
1st：无好 CV，"只用 public"（host 明示公私同分布，事后证明诚实）；
5th：5 折 + 多 seed。

**裁决**：本场是 T18 的例外——host 明确公私同分布且实际相关良好，**LB 反馈可用**；但前提是 host 的诚实与多 fold/seed 集成把 LB 噪声降下来。不可默认迁移到其他场次。置信度：高（本场）/低（跨场）。

**分歧三：数据清理的边界**
2nd：去掉"无鸟段"**降低** LB（false positives 帮助泛化）；只清 alien speech；
5th：VAD+人工清理人声、并人工标注稀有类发声段。

**裁决**：清理应针对**异质干扰（人声/讲解/alien speech）**；"无目标段"可能提供正则化，删除需验证。置信度：中高。

**分歧四：损失函数**
1st：CE 最佳（在不平衡下惩罚过度代表类）；
2nd：Focal+BCE；5th：Focal γ=2；Recipe：FocalBCE。

**裁决**：损失可因训练方案不同而互换（1st 做过多组对照），**平衡策略与阈值/后处理比损失名更重要**。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 全流程与对照表 | 自述 + 3 张图 + 公开 inference notebook/数据集 | 高 |
| 2nd 预训练/伪标/TTA 阶梯 | 自述 + 图 + GitHub + paper | 高 |
| 5th 三阶段自蒸馏 | 自述 + 4 张图 + 代码/模型 | 中高 |
| Recipe mel 参数增益 | 自述（5 次提交/天调参） | 中 |
| 2024 技法汇总 | 二手汇总之表 | 中 |
| "无鸟段删除反而降分" | 2nd 单队实验 | 中 |

### 悬案与失败学
**8. 悬案与失败学**
**悬案**

1. **1st 的第 5 次迭代为何失效**：只有"power 调整也无法继续"的现象，没有机制解释。
2. 2nd 的第 3 次伪标必须换 OOF 策略、且增益不再——未完全解释。
3. Human voice(568886)、rare-class 数据(570760)、Unstable Experiments(570402) 未收录——人声/稀有类的完整处理缺失。
4. 5th 的 seed 复用错误（Group A/B 同 seed）对集成影响未量化。

**失败学（跨队合集）**

- 1st：320+ 想法 95% 被否（未列）；target Xeno-Canto 数据通常有害；family 标签混入有害；第五轮迭代失效。
- 2nd：仅用往届数据预训练；XC/iNat 数据；主数据软标签；time-flip；去掉无鸟段。
- 5th：CNN/1D 模型；过多增强；低排名类 power 后处理（怕过拟合未用）。
- Recipe：raw-wave 上的任何增强/处理都有害。

---

## birdclef-2026 — BirdCLEF 2026 轻量深读（Tier B）

> 主题 audio ｜ 类别 Research ｜ 指标 Birdclef ROC AUC ｜ 队伍 4094 ｜ 截止 2026-06-03 ｜ Tier B ｜ 标签 audio,ranking,wildlife
> 材料基础：`digests/birdclef-2026.md`（6 篇正文：Claude-Code 被移除 704391 / 1st 704752 / 2nd 704399 / 10th 704271 / 11th 704264 / Claude 占位 681146；80 条主题索引）+ 7 张图

### 一句话重述
鸟/两栖/昆虫声景识别（ROC AUC）。2026 的两大主题：**"Perch 蒸馏 → 微调 → 多轮 Noisy Student 自训练"成为标准配方**，以及 **AI 编码代理（Claude Code）引发的参赛方式与合规争议**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（169 票） | 5 秒输入多样化集成（SED/MLP 头、两栖/昆虫专家、属级专家、Perch v2 线性头）；两阶段训练：**cosine embedding 蒸馏**（Perch v2 / AudioProtoPNet）→ 微调 + **多轮 Noisy Student**；自训练：1 轮公 0.946、2 轮 **0.950**、3 轮 0.949；LSS 注入标签和归一化 0.5 解决过拟合；PL 与 LSS 注入器分离（不同样本）；PL 标签和上限 0.75；Site-22 非 LSS 物种 mask +0.002；属级专家 +0.001~0.002；**两个域定制验证集**（Site-22 未见站点 / 贪心覆盖）；rank blending；最终公 0.967/私 0.961 | 1st |
| 2nd（53 票） | Perch+蒸馏 SED+自研 CNN+昆虫专家；**LB 主要信号**（LSS AUC 与 LB 相关仅 ~0.2）；4 轮伪标；5s 窗口；EffNetV2s/B0/NFNet；**soft AUC + 0.25 BCE**；Perch 蒸馏 +0.02 但增加相关性 → 为保集成多样性**弃用**；XC 预训练骨干把分数推过 0.930 | 2nd |
| 10th / 11th | "simple model as always"；11th "without Perch"（另有一个"差点的第 3 名"） | 10th/11th |
| AI 代理事件 | 101 名"纯 Claude-Code 方案"被取消资格（全自动 autoresearch 循环 + 邮件授权提交）；"Claude-Code 结果"占位帖 142 票；"Is everyone using LLM tools?" 60 票/116 评论 | 704391+主题索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 2nd |
| --- | --- | --- |
| 教师/蒸馏 | Perch v2 + AudioProtoPNet（cosine embedding 蒸馏，每模型重蒸） | Perch 蒸馏 +0.02 但**为多样性弃用** |
| 自训练 | Noisy Student（LSS/PL 注入器分离、标签和上限） | 4 轮伪标（先混 LSS，后改为替换 50–60%） |
| 专家 | 两栖/昆虫、属级 | 昆虫专家（nikitababich XC 数据） |
| 输入 | 5s（128×384/160×512） | 5s；XC 骨干用原 mel 规格 |
| 验证 | 两个 LSS 域拆分 + 调 PP | 验证不可靠 → LB 主信号 |
| 损失 | CE + 蒸馏 cosine | soft AUC + 0.25 BCE |
| 关键判断 | 额外 XC/iNat 多数变差，仅专家用 | 相关性控制优先于单模分数 |

### 共识 / 分歧 / 裁决
**共识一：Perch（外部强模型）是 2026 的入场券，蒸馏是把它的能力搬进小模型的标准桥（1st/2nd）**
1st 两阶段蒸馏 + 自训练达 0.935+（无自训练）；2nd 蒸馏 +0.02；11th 标题即为"Without Perch"（暗示不用 Perch 要吃亏）。**裁决**：有强外部音频模型时，embedding 蒸馏（cosine）比直接用其输出更可塑；但蒸馏会增加模型相关性，要配合架构/头/标签空间多样性。置信度：高。

**共识二：Noisy Student 自训练仍有效，但必须"防注入信号反噬"（1st 的核心技术贡献）**
1st 发现"蒸馏+LSS 已经很强，加噪声 PL 会拖垮模型"，解法：LSS 标签和归一化 0.5、PL 标签和上限 0.75、两个注入器分样本、power transform、按标签和采样。收益：1→2 轮公 0.946→0.950，3 轮回落。**裁决**：自训练的关键是**控制注入强度与来源隔离**，不是轮数越多越好。置信度：高（有消融数字）。

**共识三：5 秒窗口（配合精确裁剪）优于更长的 20 秒（1st/2nd）**
1st 明说 >5s 不行（域适应+标签模式）；2nd 的 20s 框架"持续低估"。**裁决**：本赛制/标注下 5s 是甜点；跨年可变，需要按域做时长搜索。置信度：高。

**共识四：验证极难，两队的应对相反（1st 造域拆分；2nd 用 LB）**
1st：Site-22 未见站点 + 贪心覆盖两个 LSS 拆分，调参比 LB 更可信；2nd：自建验证全不可靠（LSS AUC 与 LB 相关 0.2），回到 LB。**裁决**：**比赛新引入的 LSS/验证数据**应优先用于"域泛化/覆盖"两类拆分；LB 仍可作相对信号但有过拟合风险。置信度：中高。

**分歧：多样性的来源（蒸馏 vs 架构/头/标签空间）**
1st 每模型重新蒸馏（不同 seed/教师）以制造细微分集；2nd 为保多样性完全弃用蒸馏。**裁决**：两条路都能到前 2；核心是"让模型间不相关"，蒸馏可以是多样性工具，也可以成为相关性来源——取决于如何使用。置信度：中高。

**事件：AI 编码代理与合规**
101 名全自动 Claude-Code 方案被取消资格（系统有验证门 + 邮件人工授权提交）；社区同时在争论"是不是所有人都在用 LLM 工具"。**裁决**：2026 起，agent 辅助开发成为默认生产力，但**全自动参赛**触碰规则边界；"人做 Idea、agent 做工程"的混合模式（1st 明述）是安全区。置信度：高（事件存在）。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的自训练/注入参数与消融 | 自述 + 图 + 代码 | 中高 |
| 2nd 的 4 轮伪标与蒸馏弃用 | 自述 + 公开 notebook | 中高 |
| LSS AUC-LB 相关 ~0.2 | 2nd 自述 | 中 |
| Claude-Code 被移除 | 帖标题 + 当事人叙述 | 高（事件）；移除原因未明 |
| 10th/11th 分数 | 未细读 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 101 名被移除的**具体原因**（全自动提交？规则条款？）未在收录正文中说明；official recap 未入库。
- "Is everyone using LLM tools?"（60 票/116 评论）与 Claude 占位帖（142 票）未细读——AI 工具在竞赛中的边界没有定论。
- 1st 的完整消融（各注入器单独贡献）与 3rd 名方案未收录。

### 图证（KStarter 仓库内路径）
- ../../intel/birdclef-2026/bodies/704752_img/01.png — 1st 的完整管线

---
