# 思路库（Idea Playbook）：症状 → 可执行思路

> 用法：先定位你现在的症状（S1–S28），从对应思路里挑 2–4 条；每条都给了机制、类比证据、第一步实验。选定后写进改进方案的假设表，并给 kill 标准。
> 证据后括号是 KStarter 场次 slug；机制比参数更重要，迁移时必须做同折对照。

## A. 验证与榜单

### S1｜CV 与 LB 方向不一致
- **I1.1 实体切分审计**：同一玩家/患者/图源跨 train/test 会让历史统计泄漏｜scrabble、s3e22、herbarium｜第一步：统计实体跨折比例，跑 GroupKFold vs KFold 对照。
- **I1.2 指标实现核对**：官方 metric 可能有 bug 或口径与文档不一致｜fathomnet（AUC bug）、s3e18（逐列 AUC vs GINI）｜第一步：下载官方实现，用构造样本单测。
- **I1.3 时间穿越排查**：滚动特征是否"截至当前"、标签窗口是否重叠｜amex、jane-street｜第一步：把每个特征的最大时间与标签时间对齐画图。
- **I1.4 提交格式核对**：列顺序/行数/ID 集合错误会伪装成模型问题｜planttraits（列顺序）｜第一步：跑 submission_guard + 最小提交。
- **I1.5 分布偏移对抗验证**：train/test 二分类 AUC>0.6 说明有偏移｜s3e18、geolifeclef｜第一步：训练对抗分类器看 AUC 与重要特征。
- **I1.6 分组 vs 随机双轨**：把两版 CV 与 ≥3 次提交的 LB 做秩相关，选相关更高者｜scrabble、s3e9｜第一步：记录提交台账（CV, LB）。

### S2｜公开榜分数扎堆、微差无信息
- **I2.1 停止 LB 调参**：分带宽度≈噪声时，LB 只验证绝对水平｜s5e9（26.38–26.41）、s3e25（0.25 聚集）｜第一步：计算分带宽度与 CV 折间方差。
- **I2.2 指标结构后处理**：扎堆常因指标有可利用结构（中位数/阈值/容差）｜s3e25、s3e14（唯一值吸附 +0.3）｜第一步：OOF 上枚举 3 个后处理。
- **I2.3 分布整形**：把预测贴到目标的离散/分位结构上｜s3e14、s3e25｜第一步：统计目标唯一值/分位，比较吸附前后 OOF。
- **I2.4 提交组合对冲**：用不同模型族/后处理做 2–3 个候选，避免全押 LB 最优｜s3e22（7 区域）｜第一步：写候选表（CV/风险/相关性）。
- **I2.5 换评测视角**：用 OOF 的头部/尾部子群分数代替总分数做选择｜amex（头部 capture）｜第一步：按子群重算 OOF 指标。

### S3｜公榜高、私榜崩（shakeup）
- **I3.1 小样本量化**：public 样本越少，排名越是随机变量｜s3e9（5407 vs 721）｜第一步：算 public/private 样本量与分差。
- **I3.2 提交组合对冲**：CV 最强 + 保守候选各一，按风险分配槽位｜s3e22、home-credit（双提交）｜第一步：定义"保守"（少后处理/弱校准依赖）。
- **I3.3 降低 public 依赖**：把后处理/权重搜索全部移回 OOF｜s3e9、s3e8｜第一步：审计所有"以 LB 定参数"的地方。
- **I3.4 稳健模型优先**：shakeup 场次里，CV 与私榜相关性高于公榜｜s3e22（region 3/4/5）｜第一步：用历史提交验证 CV-私榜相关。
- **I3.5 提交时机**：不要把全部提交留到最后一天；早期提交建立 CV-LB 关系｜s3e22（top11 多为 1–2 次提交）｜第一步：开赛先交 baseline 锚点。

### S4｜分组 CV 与 LB 冲突
- **I4.1 切分逻辑优先**：实体整体落在一侧时，GroupKFold 才是诚实口径｜scrabble、s3e22｜第一步：读数据生成说明 + 实体分布。
- **I4.2 分组内特征"截至当前"**：历史聚合必须只用当前样本之前的信息｜scrabble（玩家历史）｜第一步：重写聚合特征并对照。
- **I4.3 双轨记录**：KFold 当乐观上界、GroupKFold 当泛化估计｜scrabble｜第一步：每个模型记录两个分数。
- **I4.4 相关性裁决**：用 ≥3 次提交看哪版 CV 与 LB 同向｜s3e9｜第一步：建提交台账。

### S5｜时间序列/在线评测
- **I5.1 时间切分 + gap**：用与评测同规模的窗口做 CV｜jane-street（2 折 ×200 天 + 200 天 gap）｜第一步：复刻评测窗口。
- **I5.2 在线学习**：小 lr + 混旧数据防遗忘｜jane-street（每天 7 epoch）、optiver（5 次更新 5.4438→5.4030）｜第一步：对比"不更新/1 次/多次"。
- **I5.3 时延预算工程**：先满足时间约束再谈模型｜jane-street（~1 分钟/日）｜第一步：写推理时延基准。
- **I5.4 简单模型 + 训练细节**：复杂结构在非平稳上未必赢｜jane-street（简单 MLP 0.0064）｜第一步：MLP/GBDT 基线。
- **I5.5 组合层/风险层**：Sharpe 类指标先做波动率控制｜hull（4th 无 ML）｜第一步：逆波动率 + 目标波动率基线。

## B. 指标结构

### S6｜中位数/分位型指标（MedAE 等）
- **I6.1 样本权重**：两端样本降权，只让"可能成为中位数"的样本主导｜s3e25（0.01 权重 → +0.03）｜第一步：OOF 扫描权重阈值。
- **I6.2 档位/分位整形**：预测向训练分布档位吸附｜s3e14（776 唯一值 → +0.3）、s3e25（9 档）｜第一步：OOF 对比吸附/不吸附。
- **I6.3 目标离散度统计**：唯一值/分位覆盖决定后处理空间｜s3e14、s3e25｜第一步：统计目标唯一值比例。
- **I6.4 分布假设检验**：确认测试与训练同构再整形｜s3e25｜第一步：对抗验证/分位对比。

### S7｜排序型指标（AUC/NDCG/top-K）
- **I7.1 秩平均/校准不变融合**：概率平均会带校准误差｜THEORY L14｜第一步：比较秩平均 vs 概率平均。
- **I7.2 追加预测**：top-K 下低分追加可能不伤分｜L38｜第一步：读评测实现，做小规模对照。
- **I7.3 头部子群优化**：capture/头部指标只看高分区｜amex（短序列 + 噪声修复）｜第一步：按分数段重算 OOF。
- **I7.4 槽位/集合后处理**：排序变集合需要阈值/期望错位最小化｜AI4Code（槽位）、learning-equality（阈值）｜第一步：实现期望错位/阈值搜索。

### S8｜阈值型指标（F1/Accuracy）
- **I8.1 OOF 阈值搜索**：与先验校正联合｜THEORY L22/L25｜第一步：画 OOF 阈值-指标曲线。
- **I8.2 先验校正**：类别分布偏移时调整先验｜s3e22（micro-F1=accuracy）｜第一步：统计 train/test 正率。
- **I8.3 分类型两阶段**：阈值附近样本单独建模｜THEORY L37｜第一步：分桶再比较。

### S9｜容差型指标（MAP@{K}/容差）
- **I9.1 target 整形**：把预测贴到容差网格｜s3e25、计数赛｜第一步：OOF 网格搜索。
- **I9.2 两极化流水线**：容差内精确、容差外不敏感｜L37｜第一步：构造"命中率"代理指标。

### S10｜概率/校准型（LogLoss）
- **I10.1 单参数校准**：logit 平移/温度，抗过拟合｜nov2022（−1.17）｜第一步：OOF 扫单参数 vs isotonic。
- **I10.2 isotonic 谨慎用**：小数据会过拟合阶梯｜T2｜第一步：比较折间方差。
- **I10.3 蒸馏 + 校准**：把大模型判断力压进小模型｜lmsys｜第一步：教师软标签 + 温度搜索。

### S11｜复合/可操纵指标
- **I11.1 指标博弈分析**：先判断提交策略能否影响分数｜home-credit（Gini Stability）｜第一步：读指标实现，列出可操纵项。
- **I11.2 参数敏感性**：模型差距 0.00X vs 参数差距 0.0X｜home-credit｜第一步：参数网格 + 双提交对冲。
- **I11.3 双提交对冲**：中性下注优于单边｜home-credit（1st 0.605 vs 押错 253）｜第一步：设计两个不同假设的提交。

## C. 数据与结构

### S12｜低信号/目标随机
- **I12.1 随机目标 z 检验**：100 次打乱目标对照｜s5e9（z=-0.83）｜第一步：跑检验并记录。
- **I12.2 转生成痕迹**：找孪生行/重复倍数/顺序指纹｜s5e2（≈80× 副本）｜第一步：重复率与同源组统计。
- **I12.3 压缩模型预算**：低信号场不堆大集成｜s5e9、s3e18（EC2）｜第一步：设"够了就停"预算。
- **I12.4 稳健集成 + 分布整形**：收益来自稳定性而非拟合能力｜s5e9、s3e25｜第一步：比较单模/集成/整形。

### S13｜重复行/孪生行
- **I13.1 groupby 聚合**：同源行统计是最强 FE｜s5e2（groupby 全组合 + 直方图分桶）｜第一步：按重复键聚合 mean/std/count。
- **I13.2 KNN 找孪生**：k=1 找同源行做特征/覆盖｜s5e2｜第一步：OOF 上测试孪生特征。
- **I13.3 分组目标分箱**：重复行目标均值作分箱标签｜s3e9（线性 14→12）｜第一步：按重复组构造目标均值特征。

### S14｜实体复用
- **I14.1 实体键审计**：同一 ID 多次出现（患者/马/玩家）｜s3e22（死 5 次）、scrabble｜第一步：pivot 实体×目标。
- **I14.2 分组 CV + 组内特征**：防泄漏，历史特征"截至当前"｜scrabble｜第一步：GroupKFold 对照。
- **I14.3 实体级后处理**：按实体聚合预测/一致化｜s3e22｜第一步：实体级 max/mean 对照。

### S15｜缺失、哨兵值与坏值
- **I15.1 哨兵值扫描**：-1/-666/999/空串/none vs None｜s3e18（-666）｜第一步：逐列值频 + 规则化。
- **I15.2 缺失指示特征**：缺失可能携带信息｜s4e12（NaN 与目标强相关）｜第一步：加缺失指示并对照。
- **I15.3 行级噪声结构**：指示列修复被加噪列｜amex（B_1 小值标记）｜第一步：找与噪声相关的指示列。

### S16｜test 端 OOD / 类别漂移
- **I16.1 频率编码**：未见类别只表达"稀有"｜s3e18｜第一步：把类别替换为频率/分位。
- **I16.2 clip/映射**：把 OOD 值映射到训练范围｜s3e18、s3e25｜第一步：OOF 对照。
- **I16.3 保守回退**：OOD 样本给全局均值/最保守预测｜T15｜第一步：分桶评估。

### S17｜域差/多来源
- **I17.1 域适应组合**：IBN/直方图均衡/颜色归一化｜sorghum（IBN +0.05、直方图 +0.03）｜第一步：分布可视化 + 单项消融。
- **I17.2 分辨率优先**：512→960/1024 常是最大单项｜sorghum（2nd +7.8）、herbarium（+0.017）｜第一步：分辨率阶梯实验。
- **I17.3 按子场景拆分**：透明/旋转等特殊子域单独处理｜IMC 2024（几何先验）｜第一步：按域聚类再建子模型。
- **I17.4 域内预训练**：领域权重 > 通用权重｜planttraits（PlantCLEF）、sorghum（FGVC8）｜第一步：比较 2–3 个预训练权重。

### S18｜长尾/稀有类
- **I18.1 度量损失 + 层级监督**：subcenter-ArcFace + 多级 CE｜herbarium（+0.017 / +0.011）｜第一步：损失替换对照。
- **I18.2 归并 unknown**：<N 图类别并入未知类｜fathomnet（<10 图）｜第一步：扫描归并阈值。
- **I18.3 分布匹配优先**：测试同样长尾时"不处理"最好｜geolifeclef-2022｜第一步：统计测试/训练分布。
- **I18.4 label smoothing**：噪声/长尾下 0.1 平滑｜fathomnet｜第一步：平滑系数扫描。

## D. 模型、集成与训练

### S19｜单模 plateau
- **I19.1 跨家族多样性**：6 树 + 1 非树｜s3e23（0.7922 vs 单模 0.79136）｜第一步：加核近似 LR/NN。
- **I19.2 强预训练/域内权重**：换起点比调结构更值｜planttraits、HERBARIUM（SwinV2）｜第一步：权重对照表。
- **I19.3 表示学习**：embedding + GBDT｜planttraits 9th（DINOv2+CatBoost 0.512）｜第一步：冻结骨干提特征。
- **I19.4 身份/辅助任务**：物种/群体身份三头｜planttraits 1st（17,396 物种）｜第一步：加辅助分类头。
- **I19.5 分层学习率**：头高 LR 早 warmup、骨干递减｜planttraits（调度图）｜第一步：层组 LR 扫描。

### S20｜集成无增益
- **I20.1 先查相关性**：OOF 相关性 >0.99 的模型无增量｜THEORY L7｜第一步：画 OOF 相关矩阵。
- **I20.2 换融合层**：秩平均/校准不变融合/带约束权重｜L14、s3e23（hill climbing 允许负权重）｜第一步：比较 3 种融合。
- **I20.3 只在 OOF 上调权重**：公榜权重是私榜风险｜s3e9、s3e8｜第一步：OOF vs LB 权重对照。
- **I20.4 低信号目标停止集成**：EC2 类目标集成过拟合｜s3e18 11th｜第一步：比较单模 vs 集成 OOF。

### S21｜调参不稳定
- **I21.1 种子稳定性检验**：换 KFold 种子重跑｜s3e9（Optuna 参数不存活）｜第一步：3 个种子 × 最优参数。
- **I21.2 手动/粗网格优先**：稳定优于最优｜s3e9 1st｜第一步：粗网格 + 早停。
- **I21.3 双目标选择**：RMSE + 折间 std 同时看｜s3e8 3rd（std 4.5→3.8）｜第一步：记录每折分数。

### S22｜计算/时延受限
- **I22.1 离线特征 + 轻模型**：embedding+GBDT｜planttraits、GAN 提特征｜第一步：冻结特征 + 快速模型。
- **I22.2 蒸馏**：大模型 → 可部署小模型｜lmsys、feedback（Efficiency Track）｜第一步：软标签训练。
- **I22.3 量化/编译/缓存**：KV cache、混合精度、批量推理｜aimo（vLLM KV FP16）、pipeline 工程｜第一步：推理基准。
- **I22.4 预算分配**：并行实验轨道 + kill 标准｜SOP｜第一步：写实验台账与预算表。

### S23｜多目标/多任务
- **I23.1 拆合实验**：每目标单独调参比较最优族｜s3e18（EC1 树/EC2 KNN）｜第一步：小规模拆/合对照。
- **I23.2 标签链**：按可预测性排序逐个预测｜planttraits 6th｜第一步：链式 vs 并行。
- **I23.3 多头/软分类**：回归+硬分类+软分类｜planttraits 1st｜第一步：加软分类头。
- **I23.4 目标级特征选择**：EC1 19 个 vs EC2 7 个｜s3e18｜第一步：分目标做重要性。

## E. 领域专项

### S24｜检索/匹配
- **I24.1 先召回后重排**：TF-IDF/SimCSE 召回 + 重排｜learning-equality（1st/3rd）｜第一步：召回@K 基线。
- **I24.2 难负样本 + 语言/域分桶**：对称 InfoNCE、batch 采样｜learning-equality 2nd（+0.01–0.02）｜第一步：负样本策略对照。
- **I24.3 阈值后处理**：排序→集合的阈值/数量网格｜learning-equality（margin 0.16）｜第一步：OOF 网格。
- **I24.4 嵌入对齐集成**：拼接→PCA→统一维度｜google-universal-image-embedding 4th｜第一步：对齐式融合 vs 概率平均。

### S25｜LLM/生成
- **I25.1 约束清单**：先写评测器约束（token/时延/格式）｜nemotron、lmsys｜第一步：把约束写成测试。
- **I25.2 工具集成推理**：代码执行 + 投票｜aimo（TIR）、3rd 120–160 候选｜第一步：加代码工具与投票。
- **I25.3 数据合成/课程**：按弱项类别合成可验证数据｜nemotron（crypt 7.9%）｜第一步：类别解出率表。
- **I25.4 输出后处理**：强制 `\boxed{}`、格式解析、拒绝抽样｜aimo｜第一步：解析失败率统计。
- **I25.5 引用/幻觉核验**：LLM 来源逐条核验｜openai-to-z｜第一步：抽 20 条来源验证。

### S26｜Agent/RL 对战
- **I26.1 规则基线**：可解释评分函数/兵力计算｜kore（七模块）、maze（评分函数 BFS）｜第一步：先写规则 bot。
- **I26.2 终局构造**：把 tiebreak 当主动目标｜maze（碰撞前投矿工）｜第一步：写终局规则表。
- **I26.3 课程 + 热启动**：小场景→大场景｜lux（16→32→64）｜第一步：小图基线 + checkpoint 迁移。
- **I26.4 拐点早停**：KL/资源/胜率多指标｜lux（KL>0.02、金属<100）｜第一步：画训练曲线。
- **I26.5 对手多样性/镜像**：防偏科｜maze（53/47）、3rd 反思｜第一步：历史版本池 + 镜像对局。

### S27｜黑箱/优化/安全
- **I27.1 代理评分器**：本地可复现近似评分｜santa-2024｜第一步：建同分布代理并验证相关性。
- **I27.2 结构探测**：边界二分/查表/接口约束｜ai-village-ctf｜第一步：少量调用学结构。
- **I27.3 局部精修 + 结构化种子**：搜索宽度换质量｜santa-2024（P5 28.5）｜第一步：邻域参数扫描。
- **I27.4 最弱环定位**：攻击成本≈min(模型鲁棒性, 管线假设)｜ai-village-ctf｜第一步：列管线假设清单。

## F. 交付、平台与评审

### S28｜提交/平台/评审交付
- **I28.1 提交契约演练**：列顺序/zip/schema/凭证｜planttraits、gan、autonomous-agent｜第一步：最小提交 + submission_guard。
- **I28.2 提前 48h**：平台故障不可控｜bigquery（提交按钮失效）、med-gemma（提交事故）｜第一步：写收官清单并执行。
- **I28.3 评审交付闭环**：观察→改动→验证 + 消融 + 失败路径｜pokemon-strategy（官方标准）｜第一步：按模板重写 write-up。
- **I28.4 复现门槛**：评委按说明复现｜bigquery（获奖逐一复现）、gpt-oss（145 份深审）｜第一步：陌生环境冷启动。
- **I28.5 预算/配额**：成本模型 + 自部署 fallback｜bigquery（$300+$50+$5）、autonomous-agent（$2/60min）｜第一步：算调用量与额度。
- **I28.6 评审赛道适配**：Model/Deck/Report 或 working note 规范｜pokemon、geolifeclef｜第一步：读 rubric 并映射交付物。

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
- **amex-default-prediction**（tabular/Featured｜Amex Custom Gini And X% Percentage Capture）
  - [1st](https://www.kaggle.com/competitions/amex-default-prediction/discussion/348111)
  - [2nd](https://www.kaggle.com/competitions/amex-default-prediction/discussion/347637)
  - [3rd](https://www.kaggle.com/competitions/amex-default-prediction/discussion/349741)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/amex-default-prediction.md)
- **home-credit-credit-risk-model-stability**（tabular/Featured｜Home Credit 2023 - Gini Stability）
  - [数据理解（375 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/473950)
  - [1st（175 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/508337)
  - [公开 8/私有 253（60 票）](https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability/discussion/507946)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/home-credit-credit-risk-model-stability.md)
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
- **playground-series-s4e12**（tabular/Playground｜Root Mean Squared Logarithmic Error）
  - [1st（230 行处）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/554328)
  - [NAN 与目标（126 票）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/552165)
  - [Rank2 暴力集成（27 票）](https://www.kaggle.com/competitions/playground-series-s4e12/discussion/554505)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s4e12.md)
- **playground-series-s5e2**（tabular/Playground｜Mean Squared Error）
  - [1st 单模型 + FE（189 票 / 102 评论）](https://www.kaggle.com/competitions/playground-series-s5e2/discussion/565539)
  - [3rd（33 票 / 16 评论）](https://www.kaggle.com/competitions/playground-series-s5e2/discussion/565653)
  - [5th 噪声堆找信号针（14 票）](https://www.kaggle.com/competitions/playground-series-s5e2/discussion/565583)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s5e2.md)
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
