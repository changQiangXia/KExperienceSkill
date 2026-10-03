# 机制推演手册（Mechanisms）：为什么有效、何时会失效

> 深度补充：把经验从"某场这样做涨了 X"推进到"第一性机制 + 公式 + 适用条件 + 证伪实验"。
> 每条：命题 → 机制/推导 → 适用条件 → 失效条件 → 验证实验 → 案例。
> 公式是工作近似，用于决策与量级估计，不作为精确定理。

## 1. 指标机制

### M1｜MedAE 只由"中位样本"决定

- **命题**：MedAE = median(|e_i|)，任何不改变中位数位置的样本扰动都不影响分数。
- **推导**：设 n 个绝对误差排序 e_(1)≤…≤e_(n)，分数 = e_(⌈n/2⌉)。把 e_(k)（k≪n/2）从 0.01 改到 0.3 不影响分数；把 e_(k)（k≫n/2）从 10 改到 1000 也不影响。只有"跨过中位线"的样本改变分数。
- **样本权重**：给远离中位线的样本小权重（如 0.01），等价于把容量集中到 |e| 在中位数附近的样本；s3e25 实测 +0.03。
- **档位整形的上界**：若训练目标有 m 个档位、容差 τ，且 (1-α) 的样本落在某档位 ±τ 内，则只需让 ≥50% 的样本命中档位附近即可；所需命中率 ≈ 0.5/(1-α)。s3e25：1-α=0.895 → 56%。
- **适用**：中位数/分位损失（MedAE、quantile loss、部分排序指标）。
- **失效**：测试分布与训练档位不同构；档位精度不足 τ。
- **验证**：OOF 上比较"原始预测 / 权重版 / 档位版"的中位误差与命中率。
- **案例**：s3e25（+0.03、56%、89.5%）；s3e14（776 唯一值吸附 +0.3）。

### M2｜RMSE/MAE 的尾部敏感性与 winsorize

- **命题**：RMSE 对尾部误差二次敏感，MAE 线性；裁剪/稳健损失改变的是"偏差-方差"权衡。
- **推导**：∂RMSE²/∂e_i = 2e_i/n，大误差梯度大；MAE 梯度 ±1/n，尾部不放大。
- **winsorize 的代价**：把 |e|>c 截断到 c，偏差上界 ≈ (1-p_c)·(E[|e| | |e|>c]-c)，方差下降；当尾部是噪声（非信号）时净收益为正。
- **适用**：目标含离群/噪声注入（amex 的 (0,0.01] 噪声）。
- **失效**：尾部是真实极端事件（保险/灾害），截断会丢信号。
- **验证**：分位数裁剪阈值扫描 + OOF；看 LB 是否同向。
- **案例**：amex 二次去噪、s3e8 分组合法性裁剪。

### M3｜排序指标的单调不变性

- **命题**：AUC/NDCG/Kendall 等排序指标对任何严格单调变换不变；因此概率校准不影响排序分数。
- **推论**：① 融合排序分数应用"秩平均"而非概率平均；② 校准只为 LogLoss/阈值型指标服务；③ 追加一批分数更低的候选，不改变已有 top-K 集合（除非指标对候选总数或平均精度敏感）。
- **失效**：NDCG 带相关性增益或截断按分数阈值时，绝对分数会影响；MAP 对候选总数敏感。
- **验证**：对同一批 OOF 做单调变换（x→logit、x→rank），确认 AUC 不变、LogLoss 变化。
- **案例**：s3e18 逐列 AUC；kaggle-measuring-agi 判别力；THEORY L14/L38。

### M4｜F1/阈值型指标：最优阈值是先验与成本的函数

- **命题**：F1 最优阈值 θ* 随正类先验 π 与误分类成本变化；先验偏移时旧阈值不再最优。
- **推导**：F1 = 2TP/(2TP+FP+FN)；在概率校准良好时，θ* 一阶条件可写成 π 与代价比的函数；π 变小 → 阈值上移（更保守）。
- **micro-F1 = accuracy**：单标签多分类下 micro-F1 等于 accuracy，无需阈值搜索（s3e22）。
- **适用**：F1/Accuracy/带阈值的召回-精度指标。
- **失效**：校准差时阈值搜索会把校准误差当信号。
- **验证**：OOF 阈值曲线 + 先验偏移模拟（重采样正类比例）。
- **案例**：s3e22（micro-F1=accuracy）；home-credit（先验/稳定性）。

### M5｜LogLoss 的 Brier 分解与单参数校准

- **命题**：概率分数 = 校准（reliability）+ 区分度（resolution）+ 不可约不确定性。系统性偏移只需要单参数修正。
- **推导**：若 logit 预测有常数偏移 b（p' = σ(z+b)），则平移 -b 恢复校准；isotonic 需要估计每个分箱的映射，方差 ≈ k/n_bin，小样本下容易过拟合阶梯。
- **适用**：已知偏差方向、数据量中等。
- **失效**：偏移随特征/子群变化（需要条件校准或分群校准）。
- **验证**：OOF 上比较"单参数 vs isotonic vs 不校准"，看折间方差。
- **案例**：nov2022（−1.17，CV 0.6476→0.5281）；T2。

### M6｜R² 的"只计正值"与裁剪

- **命题**：官方只计 R²>0 时，负 R² 的模型被截断为无效；对预测/目标的极端值处理会改变均值与方差分解。
- **机制**：R² = 1 - SSE/SST；异常值同时抬高 SSE 与 SST，对多目标平均时影响非线性。
- **适用**：多目标回归、R² 家族指标。
- **失效**：极端值本身是信号。
- **验证**：极端值裁剪前后 OOF/榜单对比；逐目标看。
- **案例**：planttraits2024（R²>0、极端标签、多目标）。

### M7｜复合可操纵指标（Gini Stability）

- **命题**：当指标包含"可被提交策略影响的项"（稳定性、阈值、时间分段）时，最优行为是风险下注而非纯预测。
- **推导**：设总分 = f(模型质量, 提交策略参数)；若 ∂f/∂策略 ≫ ∂f/∂模型，则预算应转向策略与对冲。
- **反制**：官方可能修补指标；单边重仓风险大。
- **验证**：参数敏感性曲线 + 双提交对冲（中性下注）。
- **案例**：home-credit（模型差距 0.00X vs 参数差距 0.0X；双提交对冲）。

## 2. 验证机制

### M8｜公榜是小样本随机变量

- **命题**：public 分数是测试子样本估计，排名噪声 ≈ σ/√m；分差小于该量级时排名无信息。
- **推导**：设单样本指标方差 σ²，public 子样本 m，则均值标准误 σ/√m；两个模型真实差距 Δ 需要 |Δ| ≳ 2σ/√m 才能在公榜上稳定区分。s3e9：CV 5407 vs public 721 → 噪声放大 √(5407/721)≈2.7×。
- **推论**：① 分带极窄（26.38–26.41、0.25 聚集）时停用 LB 选模；② 提交次数是预算，不是探索工具；③ 用 CV 做选择，LB 只验证绝对水平。
- **失效**：CV 与测试不同分布（此时 CV 也噪声/偏差）。
- **验证**：记录 ≥3–5 次（CV, LB），算秩相关；算分带宽度/折间标准差。
- **案例**：s3e9、s5e9、s3e22、s3e25。

### M9｜实体泄漏的偏差量级

- **命题**：同一实体跨折出现时，模型可记忆实体级偏移，OOF 乐观程度 ≈ 实体级方差中可被特征解释的部分。
- **推导**：设目标 y = μ_entity + ε；若实体同时出现在训练与验证，验证样本可用"实体 ID/历史统计"预测 μ_entity，OOF 误差低于真实泛化误差；偏差随实体出现次数与实体方差增大。
- **诊断**：比较 KFold 与 GroupKFold 的 OOF 差；差越大，泄漏越强。
- **适用**：玩家/患者/图源/设备等重复实体。
- **失效**：实体只有一次出现（无泄漏）。
- **验证**：GroupKFold vs KFold 对照 + 与 LB 的秩相关。
- **案例**：scrabble（GroupKFold 分数显著变差）；s3e22（hospital_number 复用）；foursquare（67% 重叠）。

### M10｜时间泄漏与 purge/embargo

- **命题**：当标签窗口与特征窗口重叠时，随机 CV 会用未来信息；purge 去掉重叠样本，embargo 再加缓冲期。
- **机制**：滚动特征通常在样本时刻 t 汇总 [t-w, t]；若标签是 [t, t+h] 的结果，训练样本 t' > t-h 就与验证标签窗口重叠。
- **诊断**：画特征最大时间 vs 标签时间；检查 CV 与 LB 的差距随时间折变化。
- **适用**：金融/时序/在线评测。
- **失效**：标签瞬时（无窗口）时不必要。
- **验证**：时间切分 + gap vs 随机 CV 对照。
- **案例**：jane-street（200 天 gap）；amex（测试期未来数据可用）。

### M11｜随机目标检验的统计功效

- **命题**：用打乱目标构造零分布，原目标 CV 的 z 分数判断"原数据是否有信号"。
- **推导**：z = (CV_orig - mean(CV_shuffle)) / std(CV_shuffle)；|z|<2 不能拒绝"无信号"。功效取决于打乱次数（100 次 → z 的分辨率约 0.1）、模型容量与 CV 折数。
- **注意**：检验的是**原数据**；合成数据可能仍含生成结构（S5E2/S5E11）。
- **失效**：模型容量太低（学不到信号 → 假阴性）；打乱破坏了特征-特征结构（只测目标关联）。
- **验证**：换模型容量/折数复跑；对原数据与合成数据分别检验。
- **案例**：s5e9（z=-0.83，3/6 随机）。

### M12｜对抗验证的边界

- **命题**：train/test 二分类 AUC≈0.5 说明"线性/当前模型可分的偏移"不存在；它不保证无偏移。
- **机制**：AUC 度量的是给定特征空间的可分性；非线性或高维交互偏移可能被低容量对抗模型漏掉。
- **诊断**：AUC 0.5–0.6 仍要看重要特征与分布图；AUC>0.7 基本可判定偏移。
- **失效**：样本量小、特征少时功效低。
- **验证**：对抗模型容量阶梯（LR → GBDT → NN）+ 重要特征检查。
- **案例**：s3e18（原数据可并入）；geolifeclef（10% 公榜）。

## 3. 训练机制

### M13｜伪标签：表示转移 vs 误差传播

- **命题**：伪标签有两种用法：① 预训练式（在伪标数据上学习表示，再用干净标签微调）— 偏差可被后续微调校正；② 直接混训（伪标与真标一起训练）— 教师误差直接进入学生标签。
- **推导**：设教师准确率 a、学生基线准确率 s；直接混训的标签噪声 ≈ (1-a)，若 a<s 则净害。预训练式通过"先学表示、后学决策"把噪声限制在表示层。
- **适用**：教师强于学生、伪标置信度高、有干净验证。
- **失效**：低信号目标（s5e9）、分布错配（hotel-id FGVC8 伪标失败）。
- **验证**：同折 A/B：无伪标 / 预训练式 / 直接混训；看 OOF 与折间方差。
- **案例**：sorghum（2nd 伪标 +3.2）；s5e9（收益不可证）；hotel-id（伪标失败）；T6/T30。

### M14｜蒸馏与温度：为什么小模型能学大模型判断力

- **命题**：软标签（概率分布）比硬标签携带更多"类间相似性"信息；温度 T 平滑分布，梯度尺度 ∝ 1/T²。
- **机制**：学生拟合教师的软分布，等价于学习教师的决策边界几何，而不是只学 argmax。
- **适用**：推理受限（lmsys 2×T4）、教师显著更强、有大量无标签/弱标签数据。
- **失效**：教师与目标分布错配；教师错误被系统性复制（无干净数据校正）。
- **验证**：T ∈ {1,2,4} × 学生容量；与硬标签基线对照；看校准（LogLoss）。
- **案例**：lmsys（70B→9B）；feedback（Efficiency Track 蒸馏）；T6。

### M15｜ArcFace/subcenter：类间几何与长尾

- **命题**：ArcFace 在角度空间加 margin（logit = s·cos(θ_y + m)），直接优化类内紧凑/类间分离；subcenter 用 k 个子中心表达多模态类。
- **适用**：细粒度、类间相似、长尾。
- **失效**：小类样本 < 子中心数；训练不稳定（s/m 需调）。
- **验证**：CE vs CE+ArcFace vs subcenter；看混淆矩阵与稀有类召回。
- **案例**：herbarium（subcenter +0.017）；sorghum（ArcFace +0.015）；hotel-id 2nd。

### M16｜IBN/直方图：域风格归一化

- **命题**：IN 去除每图风格统计（亮度/对比度/色调），BN 保留判别信息；浅层 IN + 深层 BN 兼顾域不变与判别。
- **适用**：train/test 来自不同采集域（sorghum 两块田、hotel 掩码）。
- **失效**：域差在语义/结构而非风格；数据量小导致 IN 统计不稳。
- **验证**：IBN/直方图/颜色归一化单项消融 + 域分布可视化。
- **案例**：sorghum（IBN +0.05、HE +0.03）；T14。

### M17｜分层学习率：预训练特征与任务头的最优步长差异

- **命题**：随机初始化的任务头需要大步长/早 warmup；预训练骨干需要小步长防灾难性遗忘。
- **机制**：头的梯度尺度大且方向噪声大；骨干特征已接近最优，大 lr 会破坏表示。
- **适用**：预训练视觉/语言骨干的微调。
- **失效**：数据量极大时全参微调可承受更大 lr。
- **验证**：层组 lr 扫描（头:骨干 = 10:1、5:1、1:1）+ 冻结/解冻顺序。
- **案例**：planttraits（head 1e-4、blocks 8e-5→2e-5）；herbarium（冻结层 100→0）。

### M18｜RL 课程与热启动

- **命题**：课程学习降低初期探索难度，热启动复用已学技能；在复杂环境比从头训大场景样本效率高。
- **机制**：小场景缩短 horizon、降低状态/动作组合；最佳 checkpoint 保留了基础技能（采集/建造），大场景只需学习新结构。
- **适用**：可缩放地图/难度、终局规则一致的 agent 环境。
- **失效**：小场景与大场景策略冲突（小图最优策略在大图无效）；小图本身难度高（lux 16×16 也常打不满）。
- **验证**：小→大 vs 直接大图的样本效率与最终胜率。
- **案例**：lux（16→32→64、80M 步热启动）。

### M19｜RL 收益拐点：KL、资源与熵

- **命题**：策略更新过大（KL 高）会破坏已学行为；资源指标跌破关键阈值说明策略漂移；熵塌缩导致探索停止。
- **诊断**：KL>0.02（lux 32×32）、金属产量<100（重机器人成本）、loss 周期性尖刺（环境同步重置）。
- **动作**：早停 / 调 lr / 滚动重置环境 / 加大熵系数。
- **失效**：指标间冲突（胜率仍升但资源崩）需多指标交叉。
- **验证**：画 KL/熵/资源/对旧 checkpoint 胜率四联图。
- **案例**：lux（20–30M 步后收益枯竭）。

### M20｜自对弈分布塌缩与对手多样性

- **命题**：同质对手池下，最优响应会收敛到单一策略；对未见策略脆弱。
- **机制**：自对弈是"对当前分布"的梯度，缺乏对抗性覆盖；AlphaStar 式对抗对手/历史池扩大分布。
- **诊断**：对历史版本胜率上升，但对镜像/异质策略胜率低（maze 1st 对镜像 53/47）。
- **验证**：镜像对局、跨版本联赛、固定异质对手集。
- **案例**：maze（53/47；3rd 反思）；pokemon 自对弈多样性。

### M21｜集成的偏差-方差-协方差分解

- **命题**：M 个模型平均的期望误差 = 平均偏差² + (1/M)平均方差 + (1-1/M)平均协方差。
- **推论**：增加同质模型只降方差项，收益随 M 减小；降低协方差（跨家族、不同数据/目标/预处理）才是主增益。OOF 相关性是协方差的代理。
- **适用**：AUC/回归/概率融合。
- **失效**：低信号时协方差≈方差，集成无用甚至过拟合。
- **验证**：OOF 相关矩阵 + 逐模型加入的边际增益曲线。
- **案例**：s3e23（6 树 + 1 非树）；s3e18 EC2 集成无效；s3e9 GB+RF+Ridge。

### M22｜目标编码/频率编码的泄漏机制

- **命题**：类别→目标均值编码必须 OOF 且带平滑，否则验证行目标泄漏。
- **推导**：无 OOF 时编码包含当前行目标；泄漏量 ∝ 该类样本数少（平滑不足）。
- **适用**：高基数类别、小类。
- **失效**：类别在 test 中大量未见 → 退化，用频率编码/回退。
- **验证**：OOF vs 全局编码的 CV 差；未见类别比例。
- **案例**：s3e18 频率编码；通用 T7。

## 4. 检索与匹配机制

### M23｜双塔 vs cross-encoder

- **命题**：双塔独立编码（可预计算、延迟低）、cross-encoder 交互编码（精度高、延迟大）；两阶段"召回→重排"是预算下的最优组合。
- **机制**：双塔损失上界受嵌入维数与交互缺失限制；重排用 cross 特征扩大上界。
- **验证**：召回@K 与最终指标分解；难负样本比例。
- **案例**：learning-equality（召回→重排）；AI4Code（LTR 两阶段）。

### M24｜难负样本与假负例

- **命题**：对比学习梯度随负样本相似度增大；过难负样本可能是假负例（同义/同实体），引入标签噪声。
- **动作**：semi-hard 采样、去偏、难负样本过采样比例控制。
- **验证**：负样本难度分布 + 假负例抽样审查。
- **案例**：learning-equality（难负样本 128/样本、batch>768）。

### M25｜阈值后处理的最优 F-beta

- **命题**：F-beta 最优阈值随先验与 beta 变化；在概率校准时可按 OOF 网格搜索。
- **推导**：F_b = (1+b²)TP / ((1+b²)TP + FP + b²FN)；阈值上移减少 FP、增加 FN，最优处 ∂F/∂θ=0。
- **适用**：检索/分类的集合化输出。
- **失效**：概率未校准；测试先验变化。
- **验证**：阈值×召回数网格 + 先验扰动模拟。
- **案例**：learning-equality（margin 0.16 动态阈值）。

## 5. 黑箱与搜索机制

### M26｜评分噪声与搜索信噪比

- **命题**：黑箱评分有噪声 σ_s 时，搜索提升必须超过噪声才能确认；批量评估平均可降噪 √B。
- **机制**：局部搜索的每一步增益 Δ 被噪声淹没时，选择会被随机化（等价于随机游走）。
- **动作**：先估计 σ_s（重复同一输入），再决定批量 B 与接受阈值。
- **验证**：同一解重复评分 10 次估计 σ；不同批量下搜索曲线。
- **案例**：santa-2024（本地代理评分器、批量困惑度）；ai-village-ctf（少量调用学结构）。

### M27｜局部精修 vs 全局搜索

- **命题**：当解空间有结构、评分平滑时，局部邻域精修的样本效率远高于全局随机搜索；结构化种子把搜索限制在可行区域。
- **机制**：邻域移动的方差小、可复用增量评估；全局搜索命中率随维度指数下降。
- **适用**：排列组合/参数优化（santa）。
- **失效**：多峰/非局部约束（需要重启/退火）。
- **验证**：邻域大小/移动上限网格 + 重启策略对照。
- **案例**：santa-2024（k=3/max_moving=5、k=4/1；P5 28.5）。

## 链接索引（来源佐证）

> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 3 条）+ KStarter 深读原文。

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
- **AI4Code**（nlp/Featured｜AI4CodeKendallTau）
  - [领域理解（328905）](https://www.kaggle.com/competitions/AI4Code/discussion/328905)
  - [2nd（343659）](https://www.kaggle.com/competitions/AI4Code/discussion/343659)
  - [11th Nested Transformers（343680）](https://www.kaggle.com/competitions/AI4Code/discussion/343680)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/AI4Code.md)
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
- **ai-village-ctf**（sim-agent/Research｜Nvidia Defcon）
  - [HOTTERDOG 梗图与讨论（52 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/344336)
  - [48 小时梗图（39 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/344396)
  - [7th：21 solutions（33 票）](https://www.kaggle.com/competitions/ai-village-ctf/discussion/351800)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/ai-village-ctf.md)
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
- **playground-series-s5e11**（tabular/Playground｜Roc Auc Score）
  - [1st（95 票 / 54 评论）](https://www.kaggle.com/competitions/playground-series-s5e11/discussion/647362)
  - [2nd（31 票 / 16 评论）](https://www.kaggle.com/competitions/playground-series-s5e11/discussion/647288)
  - [4th（17 票）](https://www.kaggle.com/competitions/playground-series-s5e11/discussion/647417)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s5e11.md)
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
