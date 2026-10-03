# 技法迁移地图（Technique Transfer Map）

> 第 3 轮深度：为 40 个可迁移技法给出"何时用 / 支持案例 / 反例 / 第一步实验 / kill 标准"。
> 机器可读版：`assets/technique_case_map.csv`；查询：`scripts/technique_lookup.py`。
> 机制与边界分别见 `mechanisms.md`（M#）与 `boundaries.md`（B#）。

## 1. 数据与验证

### 随机目标检验（B1/M11）
- 何时用：合成/生成数据回归或分类，开赛 10 分钟内。
- 支持：s5e9（z=-0.83，近 6 场 3/6 随机）。
- 反例/边界：只判原数据信号；合成结构仍可利用（s5e2 孪生行）。
- 第一步：100 次打乱目标对照 XGB；记录 z 与随机 CV 分布。
- Kill：z 在 ±2 内 → 转向生成痕迹与稳健集成，不投领域建模。

### 实体分组 CV（B3/M9）
- 何时用：玩家/患者/设备/图源等实体重复出现。
- 支持：scrabble（GroupKFold 更低更诚实）；s3e22（hospital_number 复用）。
- 反例/边界：分组后与 LB 相关性需实测；scrabble 作者仍不确定最终口径。
- 第一步：统计实体跨折比例；KFold vs GroupKFold 双轨。
- Kill：双轨差距 < 折间方差 → 不值得为分组牺牲数据。

### 对抗验证（B7/M12）
- 何时用：准备合并原数据/外部数据前。
- 支持：s3e18（对抗验证后合并原数据）。
- 反例/边界：AUC≈0.5 不保证无偏移；样本小时功效低。
- 第一步：train vs test 二分类（LR→GBDT 两档容量）。
- Kill：AUC>0.7 或关键特征差异明显 → 不合并，或只做无监督适配。

### 时间切分 + purge/embargo（M10）
- 何时用：预测未来、标签窗口与特征窗口重叠。
- 支持：jane-street（2 折 ×200 天 + 200 天 gap）；amex（测试期数据可用）。
- 反例/边界：随机 KFold 会时间穿越；gap 太小仍泄漏。
- 第一步：画特征最大时间 vs 标签时间；复刻评测窗口。
- Kill：随机 CV 比时间 CV 高很多且 LB 不支持 → 以时间 CV 为准。

## 2. 指标与后处理

### 中位数样本权重（B9/M1）
- 何时用：MedAE/分位损失。
- 支持：s3e25（0.01 权重 → CV +0.03）。
- 反例/边界：测试分布不同构；权重阈值经验化。
- 第一步：OOF 扫"两端阈值 × 权重"。
- Kill：ΔOOF < 1e-4 或折间方差变大。

### 档位/唯一值吸附（B9/M1）
- 何时用：目标离散（唯一值少）或容差档位。
- 支持：s3e14（776 唯一值 → +0.3）；s3e25（9 档 → 56%）。
- 反例/边界：目标连续时吸附引入系统偏差。
- 第一步：统计唯一值比例；OOF 对比吸附/不吸附。
- Kill：唯一值比例 >20% 或 OOF 无提升。

### 结构约束投影（C1/M1）
- 何时用：指标或数据有硬约束（零和、概率和、上下界）。
- 支持：optiver（零和投影 ≈0.005）；s3e8（分组裁剪 +1.3）。
- 反例/边界：约束在隐藏测试被破坏；阈值用公榜搜。
- 第一步：写约束清单；OOF 投影前后对照。
- Kill：OOF 无提升或依赖 single-fold。

### 单参数校准 vs isotonic（B5/M5）
- 何时用：概率型指标（LogLoss/Brier）或阈值型指标。
- 支持：nov2022（−1.17 平移 CV 0.6476→0.5281）；isotonic 拿第 3。
- 反例/边界：小数据 isotonic 过拟合阶梯；偏移随子群变化。
- 第一步：OOF 比较 不校准 / 单参数 / isotonic + 折间方差。
- Kill：提升 < 折间方差 / CI 跨 0。

### 阈值后处理（B12/M25）
- 何时用：F1/检索→集合/无匹配合法。
- 支持：learning-equality（margin 0.16 动态阈值）；s3e22（micro-F1=accuracy）。
- 反例/边界：概率未校准；测试先验变化。
- 第一步：阈值 × 召回数网格 + 先验扰动模拟。
- Kill：OOF 网格峰值平坦（<1e-4）。

## 3. 训练策略

### 伪标签（B1/M13）
- 何时用：教师强、无标签数据多、有干净验证。
- 支持：sorghum 2nd 私榜 91.9→95.1；feedback 跨届无泄漏伪标。
- 反例：hotel-id FGVC8 伪标失败；s5e9 低信号不可证。
- 第一步：同折三臂（无 / 预训练式 / 直接混训）。
- Kill：任一臂 CV 无提升或折间方差翻倍。

### 知识蒸馏（B16/M14）
- 何时用：推理受限、教师显著更强、软标签可得。
- 支持：lmsys（70B→9B）；feedback Efficiency Track。
- 反例/边界：教师分布错配；教师错误被复制。
- 第一步：温度 {1,2,4} × 学生容量；与硬标签基线对照。
- Kill：LogLoss/校准无改善。

### ArcFace/subcenter（M15）
- 何时用：细粒度、类间相似、长尾。
- 支持：herbarium（+0.017）；sorghum（+0.015）；hotel-id 2nd。
- 反例/边界：小类样本少；s/m 需调；类别极少时收益小。
- 第一步：CE vs CE+ArcFace vs subcenter，看稀有类召回。
- Kill：总体指标下降或训练不稳定。

### 高分辨率（B6）
- 何时用：细粒度纹理、小目标、域差大。
- 支持：sorghum 512→960 私榜 +7.8；herbarium 384 +0.017。
- 反例/边界：显存/时延受限；过拟合小数据。
- 第一步：224/384/512 三档同折对照。
- Kill：ΔOOF < 0.005 或显存不可承受。

### 域适应组合（B6/M16）
- 何时用：train/test 采集域不同（光照/设备/掩码）。
- 支持：sorghum IBN +0.05、HE +0.03；hotel-id BlendFlip +0.03–0.04。
- 反例/边界：域差在语义而非风格；掩码分布未知。
- 第一步：分布可视化 + IBN/HE/颜色归一化单项消融。
- Kill：单项 ΔOOF < 0.005。

### 身份辅助任务（B18）
- 何时用：目标与群体身份强相关（物种/商品/用户）。
- 支持：planttraits 三头（17,396 物种）。
- 反例/边界：身份与目标弱相关；聚类噪声。
- 第一步：目标~身份 ANOVA；加辅助头对照。
- Kill：辅助头无提升或拖慢收敛。

### 分层学习率（B17/M17）
- 何时用：预训练骨干 + 随机初始化头。
- 支持：planttraits（头 1e-4、blocks 8e-5→2e-5）。
- 反例/边界：大数据全参微调可承受大 lr。
- 第一步：层组 lr 扫描（10:1 / 5:1 / 1:1）。
- Kill：最优组与单一 lr 差异 < 噪声。

### 多目标拆合（B11/M23）
- 何时用：多标签/多任务指标逐目标平均。
- 支持：s3e18（EC1 树 / EC2 KNN 排序反转）；planttraits（三头）。
- 反例/边界：目标强相关 + 重 FE 时多输出也赢。
- 第一步：每目标小调参 → 最优族对比。
- Kill：拆/合 A/B 差异 < 折间方差。

## 4. Agent / RL / 搜索

### 规则基线（B13/M18）
- 何时用：规则可精确计算、动作可解释。
- 支持：kore（七模块 1st）；maze（评分函数 2006.5 vs RL 1796.4）。
- 反例/边界：连续控制/大状态空间；RL 有快模拟器时反超（lux）。
- 第一步：写可解释规则 bot + 对随机/示例基线胜率。
- Kill：规则基线胜率 <60% 且改进空间小 → 转 RL/搜索。

### 课程 + 热启动（B14/M18）
- 何时用：场景可缩放、技能可迁移。
- 支持：lux（16→32→64、80M 步、checkpoint 热启动）。
- 反例/边界：小场景本身过难（16×16 约 600 步/局）；策略冲突。
- 第一步：小图基线 + 迁移大图 vs 直接大图。
- Kill：迁移无样本效率优势。

### 自对弈对手多样性（B15/M20）
- 何时用：自对弈训练；策略可能被复制。
- 支持：maze（1st 对镜像 53/47；3rd 反思同质池）。
- 反例/边界：评估样本小导致噪声；对手池维护成本。
- 第一步：镜像/历史/异质三类对手胜率矩阵。
- Kill：镜像胜率无提升或少样本不可信。

### 黑箱代理评分（B24/M26）
- 何时用：评分昂贵、非局部、可本地近似。
- 支持：santa-2024（批量困惑度、P5 28.5）；ai-village-ctf（少量调用学结构）。
- 反例/边界：代理与官方评分相关性低；重复评分噪声大。
- 第一步：重复同一解 10 次估 σ_s；建代理并测相关性。
- Kill：代理相关性 <0.8 或 σ_s 大于预期增益。

### 工具集成推理（TIR）/大候选投票（C9/M14）
- 何时用：数学/代码类可验证任务；评测允许工具。
- 支持：aimo（1st TIR 两阶段微调；3rd 120–160 候选不微调）。
- 反例/边界：评测禁止程序执行（nemotron）；时延超限。
- 第一步：约束测试（能否执行/时限）；候选数 {16,64,160} 对照。
- Kill：规则禁止或时延超预算。

## 5. 交付与平台

### 提交对冲（B20/C11）
- 何时用：public 小、分布不确定、有 shakeup 史。
- 支持：s3e22（7 区域；top11 多为 1–2 次提交）；home-credit（双提交）。
- 反例/边界：CV-LB 相关已证明且提交少时集中更优（s3e9 ≤2 次）。
- 第一步：算 public 样本量与候选相关性；定义保守候选。
- Kill：候选相关性 >0.98 → 对冲无意义。

### 评审闭环写作（B22/C10）
- 何时用：评审制/hackathon/研究赛。
- 支持：pokemon（官方五条高分特征）；bigquery（复现过滤）。
- 反例/边界：排行榜型赛道不适用；字数/图表规则各不同。
- 第一步：rubric → 交付清单；补 1 消融 + 1 失败路径。
- Kill：无法在限制内可复现。

### Agent schema/预算（B21/C9）
- 何时用：Agent-Config/LLM 应用赛。
- 支持：autonomous-agent（本地 validate、60min/$2）；gemini-long-context（Save&Run All）。
- 反例/边界：工具兼容性、ADK 花括号注入、温度参数限制。
- 第一步：官方校验器 + 端到端最小 agent + 预算上限。
- Kill：schema 未通过或预算无法覆盖任务。

### LLM 引用核验（B25?/C9）
- 何时用：LLM 参与文献/事实/来源生成。
- 支持：openai-to-z（源文件幻觉）。
- 反例/边界：核验成本可能吞掉效率。
- 第一步：抽 20 条引用逐条验证。
- Kill：错误率 >10% 且无法自动校验 → 降级为纯假设生成。

### 行动成本模型（C9/M26）
- 何时用：Agent 多步攻击/工具调用预算有限。
- 支持：ai-agent-security（seconds=0.52×hops+0.192×decode_tok；decode 占 79–89%）。
- 反例/边界：模型/环境不同，系数需重估。
- 第一步：记录 hops/decode 与墙钟，拟合成本模型。
- Kill：模型 R² 低或无法指导预算分配。

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
- **gemini-long-context**（nlp/Community｜）
  - [获奖公布（19 票 / 33 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/552419)
  - [起步指引（13 票 / 27 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/541152)
  - [Save&Run All 挂载提醒（22 票 / 1 评论）](https://www.kaggle.com/competitions/gemini-long-context/discussion/541420)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/gemini-long-context.md)
- **lmsys-chatbot-arena**（nlp/Research｜Log Loss）
  - [16th（Chris Deotte）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527596)
  - [1st（sayoulala）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527629)
  - [2nd（tascj）](https://www.kaggle.com/competitions/lmsys-chatbot-arena/discussion/527685)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/lmsys-chatbot-arena.md)
- **nvidia-nemotron-model-reasoning-challenge**（nlp/Featured｜NVIDIA Nemotron Metric）
  - [进度奖（huikang，241 票）](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689915)
  - [1st（140 票）](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/709231)
  - [2nd](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/711703)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nvidia-nemotron-model-reasoning-challenge.md)
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
