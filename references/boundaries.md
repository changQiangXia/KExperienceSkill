# 边界与反例手册（Boundaries）：同一招什么时候赢、什么时候输

> 深度补充：每条技法给出"有效侧条件 / 失效侧条件 / 配对案例 / 诊断信号 / 最小证伪实验"。
> 用法：选中一条思路后，先读这里判断你站在哪一侧；诊断信号决定要不要做这个实验。

## B1｜伪标签
- **有效侧**：教师显著强于学生；伪标用于表示预训练（之后用干净标签微调）；目标有真实信号；同折对照证明增益。
- **失效侧**：低信号/随机目标；伪标直接混训；教师与测试分布错配；没有 OOF 对照。
- **配对案例**：sorghum 2nd 伪标 +3.2（私榜 91.9→95.1）；s5e9 26th 伪标收益不可证；hotel-id 2nd FGVC8 伪标失败；planttraits sample_submission 套利导致换测试集。
- **诊断**：随机目标 z 检验；教师-学生 OOF 对照；伪标置信度分布。
- **证伪实验**：同折 A/B（无伪标 / 预训练式 / 直接混训）。

## B2｜大集成
- **有效侧**：存在 ≥3 个跨家族、OOF 相关性 <0.99 的强模型；数据信息量足够；融合权重在 OOF 上调。
- **失效侧**：低信号目标（EC2、S5E9）；成员同质；权重在公榜上搜；成员本身未过 CV。
- **配对案例**：s3e23 6 树 + 非树 0.7922 > 单模 0.79136；s3e18 EC2 集成无法超过 0.592；s3e9 跨家族集成 12.03。
- **诊断**：OOF 相关矩阵；逐成员边际增益曲线；折间方差。
- **证伪实验**：逐成员 forward selection，记录 ΔOOF 与 Δstd。

## B3｜GroupKFold
- **有效侧**：实体整体落在 train 或 test；LEAK 明显（同玩家/患者/图源）。
- **失效侧**：实体无重复；分组后与 LB 相关性反而更差（需要实测）；分组导致训练数据骤减。
- **配对案例**：scrabble 按 nickname 分组后分数显著变差（更诚实）；s3e22 hospital_number 复用；foursquare 67% 重叠。
- **诊断**：实体跨折比例；KFold vs GroupKFold 的 OOF 差；≥3 次提交的 CV-LB 秩相关。
- **证伪实验**：同一模型双轨 CV + 提交对照。

## B4｜Optuna/自动调参
- **有效侧**：验证稳定、搜索空间合理、预算充足；用种子稳定性检验筛选参数。
- **失效侧**：小数据/高噪声；换 KFold 种子后最优参数消失；搜索轮数 >> 数据信息量。
- **配对案例**：s3e9 1st/12th 明确 Optuna 参数不稳改手工；s3e8 3rd 同时盯 RMSE 与折间 std。
- **诊断**：3 个种子 × 最优参数；参数-分数曲面平坦度。
- **证伪实验**：换种子重跑；若排名反转则放弃自动最优。

## B5｜isotonic vs 单参数校准
- **有效侧**：样本多 + 明确单调失配 → isotonic；系统性偏移 → 单参数平移。
- **失效侧**：小数据 isotonic 过拟合阶梯；偏移随子群变化。
- **配对案例**：nov2022 单参数平移 CV 0.6476→0.5281；T2（两者差异常在噪声量级）。
- **诊断**：校准曲线（reliability diagram）；每 bin 样本量。
- **证伪实验**：OOF 上比较 单参数 / isotonic / 不校准，记录折间方差。

## B6｜高分辨率
- **有效侧**：细粒度纹理/小目标/病理切片；算力允许；域差大时高分辨率常是第一杠杆。
- **失效侧**：显存/时延受限（需切块/梯度检查点）；目标不依赖细节；过拟合小数据。
- **配对案例**：sorghum 2nd 512→960 私榜 84.1→91.9、3rd 512→1024 +0.04；herbarium SwinB384 +0.017；planttraits EVA 448 vs 336。
- **诊断**：分辨率阶梯 OOF；显存/时延预算；错误样本是否小目标。
- **证伪实验**：224/384/512 三档同折对照。

## B7｜外部数据
- **有效侧**：类别映射清晰；与目标域兼容；对抗验证通过；许可允许。
- **失效侧**：标签口径不同；只对公榜有效（分布红利）；许可不清；未做去重。
- **配对案例**：sorghum FGVC8 +0.03（1st/3rd）；hotel-id Hotel50K 未用上、FGVC8 伪标失败；s3e18 对抗验证后合并原数据。
- **诊断**：类别重叠率；对抗验证 AUC；加入前后 OOF/折间方差。
- **证伪实验**：同折 A/B（仅本赛 / 加外部），并对齐验证集。

## B8｜长尾重加权/重采样
- **有效侧**：测试分布同样长尾但稀有类权重高（macro-F1）；稀有类有足够样本。
- **失效侧**：测试与训练同分布（微-F1/AUC）→ 均衡化伤分；稀有类样本 < 子中心数。
- **配对案例**：herbarium 1st：class-aware sampling 与清洗无效，度量损失有效；geolifeclef 2nd：长尾"不处理"最好；fathomnet <10 图归 unknown。
- **诊断**：训练/测试类别分布对比；每类样本数。
- **证伪实验**：重加权强度扫描 + OOF macro/micro 双指标。

## B9｜中位数/分位后处理
- **有效侧**：指标中位数型；目标离散/档位化；测试同分布。
- **失效侧**：指标均值型（RMSE/MAE）；目标连续且档位精度不足。
- **配对案例**：s3e25 权重 +0.03、9 档 56%→0.25；s3e14 唯一值吸附 +0.3。
- **诊断**：指标的数学结构；目标唯一值比例。
- **证伪实验**：OOF 吸附/权重对照。

## B10｜公开榜选模
- **有效侧**：public 样本大、与 CV 同分布且相关性已证明；提交次数多。
- **失效侧**：小 public（20/80）、分布红利、分带极窄、shakeup 历史。
- **配对案例**：s3e9 5407 vs 721；s3e22 7 区域；s5e9 未选提交更高。
- **诊断**：public 样本量；分带宽度 vs 折间方差；CV-LB 秩相关。
- **证伪实验**：用 ≥5 次提交比较"按 CV 选"与"按 LB 选"的私榜结果。

## B11｜多目标：拆 vs 合
- **有效侧**：目标最优模型族不同；指标逐列平均；目标间相关性低。
- **失效侧**：目标间强相关；重 FE 的多输出 + 大模型能共享表示；拆分会减少每目标数据。
- **配对案例**：s3e18 EC1 树/EC2 KNN 排序反转；1st MultiOutput 也能赢。
- **诊断**：每目标小调参的最优族；目标相关矩阵。
- **证伪实验**：拆/合同折 A/B（2×2）。

## B12｜检索（embedding+kNN） vs 分类（logits）
- **有效侧**：类别多、遮挡/域差大、有检索结构（1:N 匹配）。
- **失效侧**：类别少且可分；logits 校准好；长尾严重（kNN 受密度影响）。
- **配对案例**：hotel-id 1st 检索夺冠 vs 2nd/3rd logits 不差；learning-equality 召回+重排。
- **诊断**：带掩码/域差的本地验证集；类别数与每类样本。
- **证伪实验**：同特征下 kNN vs logits 的 OOF 对照。

## B13｜规则型 agent vs RL
- **有效侧**：规则明确、可精确计算（兵力/资源/终局）；RL 缺快模拟器或算力。
- **失效侧**：连续控制/大状态空间/规则复杂（Lux 大地图）；RL 有模拟器 + 课程 + 对手多样性。
- **配对案例**：kore 1st 规则七模块；maze 1st 规则评分函数 2006.5 vs 3rd JAX+BC+PPO 1796.4；lux RL 头部。
- **诊断**：能否写出可解释基线；模拟器吞吐；动作空间大小。
- **证伪实验**：规则基线 vs 轻量 RL 在冻结对手池上的胜率。

## B14｜课程学习
- **有效侧**：场景可缩放、技能可迁移、终局规则一致。
- **失效侧**：小场景与大场景策略冲突；小场景本身过难。
- **配对案例**：lux 16→32→64 热启动；16×16 也常打不满（约 600 步/局）。
- **诊断**：小/大场景的最优策略相似度；样本效率曲线。
- **证伪实验**：课程 vs 直接大场景的样本效率对照。

## B15｜自对弈对手多样性
- **有效侧**：历史版本池 + 针对性对抗 + 异质对手；大样本评估。
- **失效侧**：同质池收敛到单一策略；评估样本小。
- **配对案例**：maze 1st 对镜像 53/47；3rd 自述同质池导致战斗弱。
- **诊断**：对镜像/历史/异质策略的胜率矩阵。
- **证伪实验**：镜像与异质对手回归测试。

## B16｜知识蒸馏
- **有效侧**：教师强、推理约束硬、有软标签/无标签数据。
- **失效侧**：教师分布错配；教师错误被复制（无干净校正）；温度/容量不匹配。
- **配对案例**：lmsys 70B→9B；feedback Efficiency Track；sorghum 伪标（预训练式）。
- **诊断**：教师-学生 LogLoss/校准对比；软标签温度扫描。
- **证伪实验**：硬标签 vs 软标签（T=1/2/4）同折对照。

## B17｜域内预训练权重
- **有效侧**：目标域与预训练域接近（植物/病理/卫星）；标注少。
- **失效侧**：预训练域偏差大；权重下载/许可受限。
- **配对案例**：planttraits PlantCLEF 显著提升；sorghum ImageNet22k；google-universal-image-embedding CLIP LAION 0.499 vs ImageNet 0.405。
- **诊断**：候选权重对照表；线性探针分数。
- **证伪实验**：2–3 个权重的冻结特征线性探针。

## B18｜身份辅助任务
- **有效侧**：目标与群体身份强相关；身份可聚类/可得；长尾可焦点损失。
- **失效侧**：身份与目标弱相关；聚类噪声大。
- **配对案例**：planttraits 17,396 物种三头；6th 标签链。
- **诊断**：目标-身份 ANOVA / 组内方差比例。
- **证伪实验**：加/不加辅助头对照。

## B19｜指标结构后处理（通用）
- **有效侧**：指标有约束（零和/阈值/容差/中位数）；后处理在 OOF 验证。
- **失效侧**：约束在隐藏测试被破坏；阈值用公榜搜。
- **配对案例**：optiver 零和投影 ≈0.005；s3e8 分组裁剪 +1.3；s3e25 档位。
- **诊断**：指标约束检查表；OOF vs LB 后处理增益一致性。
- **证伪实验**：OOF 加/不加后处理 + LB sanity。

## B20｜提交组合对冲
- **有效侧**：公榜小/分布不确定/有 shakeup 史；候选多样。
- **失效侧**：CV-LB 相关已证明且测试大；提交次数少（必须集中）。
- **配对案例**：s3e22 7 区域（对冲有效）；home-credit 双提交；s3e9 ≤2 次提交（相关已证明）。
- **诊断**：public 样本量与历史洗牌；候选相关性。
- **证伪实验**：模拟 public 子采样，估计组合的私榜期望排名。

## B21｜LLM 约束工程（schema/预算/工具）
- **有效侧**：先本地校验 + 预算上限 + 工具兼容表。
- **失效侧**：未本地 validate 就消耗提交；工具不兼容；死循环烧预算。
- **配对案例**：autonomous-agent（schema/工具/预算失败清单）；gemini-long-context（Save&Run All、配额）。
- **诊断**：本地 validate 通过率；预算消耗曲线。
- **证伪实验**：端到端最小 agent 跑通后再加复杂度。

## B22｜评审制交付
- **有效侧**：按 rubric 映射 + 可复现 + 消融/失败路径 + 图表。
- **失效侧**：只报结果、私有依赖、格式/字数违规。
- **配对案例**：pokemon-strategy 官方高分标准；bigquery 复现过滤；gpt-oss 深度复核。
- **诊断**：陌生环境冷启动；rubric 逐项自查。
- **证伪实验**：让第三方按说明复现并复述。

## B23｜社区投票/非客观评分
- **有效侧**：早发布 + 持续维护 + 自包含资产；把投票当曝光问题管理。
- **失效侧**：指望客观性；后期拉票；忽略投票权重变化。
- **配对案例**：kaggle-measuring-agi 15% upvote 争议；data-assistants 中期奖改变分享行为。
- **诊断**：rubric 权重；发布时机。
- **证伪实验**：跟踪发布后分数/曝光变化。

## B24｜黑箱搜索
- **有效侧**：有本地代理评分器；噪声低于增益；局部结构平滑。
- **失效侧**：评分不可复现/噪声大；多峰；预算不足。
- **配对案例**：santa-2024（代理评分 + 局部精修）；ai-village-ctf（少量调用学结构）。
- **诊断**：同解重复评分方差；批量-噪声曲线。
- **证伪实验**：重复评分 10 次估 σ，再定接受阈值。

## B25｜特征选择
- **有效侧**：高基数/冗余特征多；每目标单独选择；用 OOF/置换重要性。
- **失效侧**：选择在验证集上做（泄漏）；低信号时选择不稳定。
- **配对案例**：s3e18 EC1 19 个 vs EC2 7 个；s3e8 2nd 用 CV 阈值选列；s3e9 重复行目标分箱。
- **诊断**：选择前后 OOF；选择稳定度（不同种子）。
- **证伪实验**：多折多种子重选，统计被选特征频率。

## B26｜公共 notebook 复用
- **有效侧**：有 CV 证明 + 提供特征/验证/后处理机制；注明来源。
- **失效侧**：无 CV 的高分 notebook；公榜过拟合的权重/阈值；末期钓鱼方案。
- **配对案例**：s3e9 公开高分但 CV 差；s3e23 胜利说明书（有 CV 论证）；s3e25 引用缺失争议。
- **诊断**：该 notebook 是否给 CV；是否只给 LB。
- **证伪实验**：本地复现其 CV；与自研基线同折对比。

## 链接索引（来源佐证）

> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 3 条）+ KStarter 深读原文。

- **fathomnet-out-of-sample-detection**（cv/Research｜FathomNet 2023）
  - [4th 方案（5 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/413092)
  - [标签错误讨论（6 票 / 2 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/407400)
  - [metric 修复与重算（3 票 / 0 评论）](https://www.kaggle.com/competitions/fathomnet-out-of-sample-detection/discussion/404769)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/fathomnet-out-of-sample-detection.md)
- **google-universal-image-embedding**（cv/Research｜PostProcessorKernelDesc）
  - [1st（359316）](https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359316)
  - [2nd（555 行处）](https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359525)
  - [4th](https://www.kaggle.com/competitions/google-universal-image-embedding/discussion/359487)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/google-universal-image-embedding.md)
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
- **data-assistants-with-gemma**（nlp/Community｜）
  - [中期奖公告（30 票 / 6 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/487380)
  - [Gemma 发布与集成（50 票 / 13 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/478606)
  - [Gemma meets LangChain（7 票 / 4 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/479620)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/data-assistants-with-gemma.md)
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
- **lmsys-chatbot-arena**（nlp/Research｜Log Loss）
  - [16th（Chris Deotte）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527596)
  - [1st（sayoulala）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527629)
  - [2nd（tascj）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527685)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/lmsys-chatbot-arena.md)
- **openai-gpt-oss-20b-red-teaming**（nlp/Featured｜）
  - [获奖公布与评审说明（24 票 / 91 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608537)
  - [攻击方法分层分类（4 票 / 5 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608997)
  - [官方欢迎帖（39 票 / 50 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/596882)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/openai-gpt-oss-20b-red-teaming.md)
- **ai-village-ctf**（sim-agent/Research｜Nvidia Defcon）
  - [HOTTERDOG 梗图与讨论（52 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/344336)
  - [48 小时梗图（39 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/344396)
  - [7th：21 solutions（33 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/351800)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/ai-village-ctf.md)
- **autonomous-agent-prediction-beta**（sim-agent/Playground｜Autonomous Agent Prediction Beta Metric）
  - [3rd 方案（6 票 / 2 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/737407)
  - [官方失败原因清单（9 票 / 11 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/723907)
  - [$2 预算讨论（11 票 / 7 评论）](https://www.kaggle.com/competitions/autonomous-agent-prediction-beta/discussion/723806)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/autonomous-agent-prediction-beta.md)
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
- **santa-2024**（sim-agent/Featured｜Santa 2024 Metric）
  - [批量困惑度（92 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548249)
  - [1st（85 票，正文仅 repo 链接）](https://www.kaggle.com/competitions/santa-2024/discussion/560560)
  - [SA 总论 255.9（59 票）](https://www.kaggle.com/competitions/santa-2024/discussion/548476)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/santa-2024.md)
- **foursquare-location-matching**（tabular/Featured｜Jaccard）
  - [Unidecode（128 票）](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/320938)
  - [13th GNN（102 票）](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/336124)
  - [1st（92 票）](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/336055)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/foursquare-location-matching.md)
- **home-credit-credit-risk-model-stability**（tabular/Featured｜Home Credit 2023 - Gini Stability）
  - [数据理解（375 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/473950)
  - [1st（175 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/508337)
  - [公开 8/私有 253（60 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/507946)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/home-credit-credit-risk-model-stability.md)
- **learning-equality-curriculum-recommendations**（tabular/Featured｜F-Score Beta (Micro)）
  - [1st（209 票）](https://www.kaggle.com/competitions/learning-equality-curriculum-recommendations/discussion/394812)
  - [2nd（79 票）](https://www.kaggle.com/competitions/learning-equality-curriculum-recommendations/discussion/395110)
  - [3rd（59 票）](https://www.kaggle.com/competitions/learning-equality-curriculum-recommendations/discussion/394838)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/learning-equality-curriculum-recommendations.md)
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
