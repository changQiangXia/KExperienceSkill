# 比赛经验书（Experience Book）

> 264 场经验的领域化总结。每章：这类比赛**真正考什么** → **已验证打法（带案例与数字）** → **常见失败** → **迁移到新比赛的动作与证伪实验**。
> 用法：先用 `scripts/case_search.py` / `references/case-index.md` 找到 3–5 个类比场次，读它们的深读文档（KStarter 仓库 https://github.com/changQiangXia/KStarter 的 `analysis/deep/<slug>.md`），再用 `improvement-plan-protocol.md` 输出改进方案。数字均来自归档材料，引用前回原场核对。

## 1. 表格与合成数据（Playground 家族）

**真正考什么**：合成数据生成器留下的结构（孪生行、顺序/索引、翻转）、指标数学结构、CV 纪律、集成工程；领域知识帮助有限。

**已验证打法**

- **随机目标检验**：原目标 vs 100 次打乱目标的 XGB 对照，z∈±2 判无信号；S5E9 z=-0.83，近 6 场回归 **3/6 随机**（S4E12/S5E2/S5E9）。无信号时，收益来自生成痕迹与稳健集成，而不是领域建模。
- **孪生行/重复结构**：S5E2 原数据 10% 重复、合成把 5e4 行扩成 4e6 行（≈每行 80 份副本）；KNN k=1 可找孪生行，`groupby` 聚合是核心 FE。
- **指标结构套利**：MedAE 只取决于误差中位数那一个样本——对 AE≤0.06 或 ≥0.7 的样本给 0.01 权重使 LGBM CV +0.03；9 个档位 ±0.25 覆盖 89.5%，猜对约 56% 即 0.25（S3E25）。
- **窄分带纪律**：S5E9 榜首 26.38–26.41、S3E25 大量 0.25 聚集——LB 微差没有信息量，用 CV/分布整形决策。
- **多目标拆合**：S3E18 的 EC1（树模型）与 EC2（Bagged KNN）最优模型排序完全反转；11th 拆开建模进前 11，1st 用 MultiOutput + 重 FE 也能赢。
- **清洗三件套 + OOD**：哨兵值（-666）、重复行、近常数冗余列（fr_COO2）；test 端未见类别用频率编码。
- **大池 + 阈值递进 + 二级栈**：S3E8 2nd 用 1816 个模型（L1 1709 + L2 105）、CV 阈值 572.6；8th 的分组合法性裁剪（Q3+1.5·IQR 上界 + 下界裁剪）再 +1.3。

**常见失败**：抄无 CV 证明的公开 notebook；用 LB 微差选模；不做实体/时间切分审计；在无信号场堆大集成；伪标签没有同折对照。

**迁移动作**：① 指标结构分类 → 3–5 个后处理候选；② 随机目标/对抗验证；③ 清洗三件套；④ 多目标拆合实验；⑤ 异质集成（含非树成员）；⑥ 提交格式演练。

## 2. 金融 / 市场 / 在线时序

**真正考什么**：指标的经济含义（Sharpe/capture/zero-mean R²）>> 模型结构；非平稳、在线约束与风险管理。

**已验证打法**

- **Amex**：自定义 Gini + top-x% capture 本质是头部排序；数据被注入噪声（含 (0,0.01] 均匀噪声）、短序列客户行为迥异；测试期数据可用。冠军融合权重和=0.9 也夺冠——说明头部指标对权重不敏感，别把 LB 微差当信号。
- **Jane Street**：评测期 notebook 每周/每日接收新数据并**现场训练推理**（约 1 分钟/日）——考点是在线自适应 + 时延工程 + 验证窗口对齐。
- **Hull Tactical**：指标是 Sharpe，预测精度让位于组合构建；第 4 名完全不用 ML（短期反转 alpha + 逆波动率加权 + 波动率目标）。
- **通用时序**：时间切分 + purge/embargo；“截至当前”滚动特征；指标口径（预测期/单位）先核对。

**常见失败**：随机 KFold 造成时间穿越；用未来信息构造特征；用 RMSE 思维优化 Sharpe。

**迁移动作**：① 把指标翻译成经济行为（排序/风险/换手）；② 建最小无泄漏时间切分；③ 先做风险管理/组合层；④ 再谈模型。

## 3. 信用风险与稳定性

**真正考什么**：复合指标可能被提交策略操纵；稳定性与头部排序；短序列/弱样本子群。

**已验证打法**

- **Home Credit 2023（Gini Stability）**：1st 直接把比赛切成两段做风险下注；社区用"中性下注 + 双提交对冲"应对可操纵指标；押单边最差。
- **Amex 短序列**：≤2 月账单客户违约率反而高（seq=13 → 23.2%、12 → 38.9%、11 → 44.7%），2nd 用专用小模型 + 秩组内回填。
- **二次去噪**：利用主办方噪声注入的行级相关结构修复列（LGBM +0.0007 / XGB +0.0008 / CatBoost +0.0004）。

**常见失败**：只优化纯预测指标、忽略指标可操纵性；把短序列混进全量模型；不做提交对冲。

**迁移动作**：① 先做"指标博弈分析"（提交行为能否影响分数）；② 分组建模弱子群；③ 设计双提交对冲。

## 4. CV 分类与细粒度

**真正考什么**：域适应、分辨率、度量学习、身份/层级结构、长尾；以及"训练/测试采集差异"。

**已验证打法**

- **Herbarium 2022**：多级 CE（family/genus/species）→ 5crop → subcenter-ArcFace 动态 margin → 384 分辨率 → 冻结层渐进解冻 → SwinV2；单模 private 0.784→0.863，8 骨干融合 0.877；**class-aware sampling 与 data cleaning 无效**。
- **Sorghum 2022**：train/test 来自两块田 → IBN +0.05、直方图均衡 +0.03、ArcFace +0.015、512→1024 +0.04、FGVC8 +0.03、TTA +0.02（3rd≈0.957）；2nd 512→960 私榜 84.1→91.9，伪标签再 +3.2。
- **Hotel-ID 2022**：训练无掩码、测试大遮挡 → BlendFlip 增强 +0.03–0.04 mAP；ArcFace 1536D → PCA 3072D → kNN；2nd/3rd 报告 logits 至少不差。
- **PlantTraits 2024**：目标与物种身份强相关 → 回归 + 硬分类 + 软分类三头（17,396 物种）+ PlantCLEF 域内预训练 + 结构化自注意力；9th DINOv2+CatBoost private 0.51238；6th EVA 单模 0.483–0.486、栈后 0.526。

**常见失败**：忽略域差直接调骨干；长尾盲目重采样；掩码/遮挡不做分布对齐；不做 identity 辅助任务。

**迁移动作**：① 分辨率上限实验；② 域适应（IBN/直方图/颜色）；③ 度量损失 + 分类头；④ 身份/层级辅助任务；⑤ 分层学习率；⑥ TTA/多骨干融合。

## 5. CV 检测 / 分割 / 计数

**真正考什么**：模型之外的系统工程——阈值、后处理、拓扑/容差指标、标注与域差；无 GT 时更是"过滤工程"。

**已验证打法**

- **RSNA 2024 腰椎**：级联流水线（定位→分级）与逐椎间盘处理。
- **HuBMAP WSI**：三件与模型无关的事决定分数（阈值/后处理/域）。
- **Vesuvius 2025**：SDF 表示 + 全卷推理 + 拓扑后处理；公私榜脱钩。
- **IMC 2024**：分场景处理——透明/反光物体用"图像排序 + 相机摆圆周"的几何先验直接拿分。
- **iWildCam 2022**：无 GT 计数——1st 不训练不跟踪，按"每图 >8 框"分密度调阈值/NMS（高密度：置信度 0 + NMS IoU 0.2 + 抑制小框；低密度：0.98/0.8 + 二轮过滤），public MAE 0.247，优于 9th 的 YOLO+WBF+跟踪（0.265/0.275）。
- **FathomNet 2023**：OSD = 1−max(类概率) + 5×集成标准差；<10 图类别并入 unknown + label smoothing 0.1；290 类中 157 类无图。

**常见失败**：只换骨干不查指标/后处理；无 GT 还强行训练检测器（误差传播）；忽略拓扑/容差指标的特殊性。

**迁移动作**：① 先写"模型外三件事"清单（阈值/后处理/域）；② 密度或难易分层后处理；③ 未知类/长尾归并；④ 提交与评测实现核对。

## 6. 多模态与检索

**真正考什么**：模态融合方式、标签病态（presence-only/单标签多义）、检索指标与阈值后处理、I/O 工程。

**已验证打法**

- **GeoLifeCLEF 2022**：presence-only 单标签是病态 → 同 0.01° 网格内 10% 邻域换标 +2%；10 模型伪置信度集成再 +2%；环境协变量用 RF、影像用 CNN；公榜仅 10% 测试数据，必须信验证分。
- **Learning Equality**：主题树上下文注入提升召回 + 阈值/后处理把排序变集合 + 训练期负样本设计。
- **Wikipedia Image/Caption**：URL 图像 I/O（feather/parquet/datatable、并发下载）+ 双塔检索 + 直接复用 Shopee 图文匹配方案骨架。
- **PlantTraits / 遥感多模态**：各模态独立骨干 + 概率层融合；标签链/身份任务补足弱模态。

**常见失败**：把协变量硬塞进 CNN；忽略"无匹配也是合法标签"；不做阈值后处理；I/O 阶段就耗尽时间。

**迁移动作**：① 模态清单与缺失建模；② 标签病态处理（邻域软化/温度/多标签）；③ 检索→集合的阈值后处理；④ 双塔/融合选择。

## 7. NLP / LLM

**真正考什么**：把大模型能力压进评测约束（算力/时延/输出格式）；任务重构（排序/检索/工具推理）；校准与投票。

**已验证打法**

- **LMSYS Chatbot Arena**：2×T4 16GB 约束下把 70B 判断力压进 9B（蒸馏 + 校准）。
- **AIMO Prize**：工具集成推理（Python 当计算器）+ 大候选/投票；1st 两阶段全参微调，3rd 不微调只靠 vLLM 大候选 + 自研打分。
- **Nemotron**：只能交 rank≤32 LoRA、评测 vLLM temp=0、答案在 `\boxed{}`、不能跑程序——把确定性程序翻译成可模仿的 CoT。
- **Feedback Prize**：整篇输入 + 逐 span 池化、前届数据的无泄漏伪标、两级集成 + 均值校准；另有独立 Efficiency Track 考蒸馏与推理优化。
- **AI4Code**：Learning-to-Rank（listwise） + 长上下文（训练 2048/推理 5120）+ 槽位后处理（最小化错位概率和）。

**常见失败**：忽视评测器约束；把生成当排序；不做投票/校准；伪标跨届泄漏。

**迁移动作**：① 先判题型（理解/生成/检索/工具/排序）；② 评测约束清单（算力/时延/格式）；③ 蒸馏/伪标/投票；④ 输出后处理（阈值/槽位/集合）。

## 8. 模拟对战 / RL Agent

**真正考什么**：规则理解与终局构造、模拟器吞吐、自对弈对手多样性、训练收益拐点。

**已验证打法**

- **Lux AI S2 NeurIPS**：fork Jux 非 lockstep 向量化 → 16→32→64 地图课程（各 80M 步、最佳 checkpoint 热启动）→ 行动掩码与冲突取消 → 统计量 EMA 归一化 + WinLoss；32×32 KL>0.02、金属产量跌破 100 后收益枯竭。
- **Maze Crawler**：1st 用单一评分函数 BFS（节点采矿 + 主动逼迫 tiebreak + 碰撞前投放 300 能量矿工），2006.5 分；3rd 用 JAX 移植 + 行为克隆 bootstrap + PPO 自对弈（1796.4），自述对手池同质导致战斗弱；1st 对近镜像 bunterrrr 仅约 53/47。
- **Kore 2022 beta**：1st 是七模块规则 agent；社区 Q-learning 打不过官方示例微调。
- **Pokemon TCG**：Simulation（6807 队）与 Strategy（942 write-up）双赛道；评审闭环写作与自对弈多样性。

**常见失败**：端到端 RL 无课程直接上大场景；自对弈池同质；忽视终局/tiebreak 规则；不看训练拐点跑满预算。

**迁移动作**：① 写清终局规则；② 规则基线先行；③ 快模拟器/课程/热启动；④ 对手与镜像鲁棒性；⑤ 拐点早停；⑥ 提交 slot 策略。

## 9. 优化 / 黑箱搜索 / 安全

**真正考什么**：评分函数经济学（昂贵、非局部、黑箱）、搜索结构、最弱环与合规。

**已验证打法**

- **Santa 2024**：黑箱昂贵评分 → 局部精修速度=搜索宽度；结构化种子降解自由度；本地可复现评分器是杠杆。
- **AI Village CTF**：先花少量调用学结构（边界/查表/接口约束），再暴力剩余空间；攻击成本≈min(模型鲁棒性, 管线假设强度)。
- **gpt-oss 红队**：CoT 可伪造、工具/通道拒绝不一致、大量问题只在 `reasoning_effort=low` 复现；危害按增量评估。

**常见失败**：把黑箱当白箱浪费预算；无结构随机搜索；越界利用漏洞（规则/伦理）。

**迁移动作**：① 量化评分调用成本与噪声；② 找可复现代理评分器；③ 结构探测；④ 机制分解；⑤ 合规审查。

## 10. 评审制 / 研究 / Hackathon / Agent-Config

**真正考什么**：交付质量与可复现性、评审流程偏好、平台/预算约束、非排行榜赛道。

**已验证打法**

- **Pokemon Strategy**：高分 write-up = 观察→改动→验证闭环 + 消融 + 失败路径 + 意图 + 少而精图表；官方不公开分项评分。
- **BigQuery / gpt-oss**：高召回初筛 + 深度复现 + 盲样 QA + 评委换人；缺 artifact/不可访问直接过滤；获奖作品逐一复现。
- **GeoLifeCLEF**：working note 是第二交付物（CEUR-WS/LNCS）；数据获取（Seafile/打包数据）常比建模更耗时。
- **MedGemma / HAI-DEF**：专用基座（分类优先，不支持分割/生成）+ 部署（27B/VertexAI/4B 塌缩）+ 提交事故是主要门槛。
- **Autonomous Agent Prediction**：提交 Agent Config（Google ADK），60min/$2 预算；3rd 用 LGBM/XGB/CatBoost+LR 的 OOF 选择 + “定向→CV→快基线锚点→迭代”工作流；schema/工具兼容/死循环是第一约束。

**常见失败**：只报最终结果；私有依赖导致不可复现；页面/字数/视频格式不合规；预算烧在探索。

**迁移动作**：① 按评审标准写交付；② 复现演练；③ 基座能力边界与部署方案；④ 预算/schema 本地校验；⑤ 提前 48h 提交。

> 相关：本章讲"比赛类型是 agent"（提交 Agent Config）；"用编码 agent 打比赛"（vibe coding → agentic engineering）是另一条线，
> 见 `agent-kaggle-playbook.md`（T1–T4 拓扑、合规红线 birdclef-2026 101st 取消资格、事务门与泄漏审计）。

## 11. 跨领域迁移检查表（把经验变成改进方案）

面对新比赛，对每个候选经验问六件事：

1. **结构同构吗？** 任务、指标、数据切分、评测约束是否对应；
2. **机制是什么？** 这个方法为什么有效（第一性），不是"别人用了"；
3. **反例在哪？** 找同方法失败/无效的场次（`failures.md`）；
4. **可证伪实验？** 在本场 CV 上，一次改动 + 明确 kill 标准；
5. **成本与风险？** 时间/算力/合规/私榜风险；
6. **证据等级？** 官方 > 图证 > 原文数字 > 自述；矛盾项标注。

输出格式与执行协议见 `improvement-plan-protocol.md`。

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
- **wikipedia-image-caption**（cv/Playground｜NDCG@{K}）
  - [官方欢迎（16 票 / 16 评论）](https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272023)
  - [Shopee 方案总汇（5 票 / 0 评论）](https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/283917)
  - [相似赛索引（13 票 / 4 评论）](https://www.kaggle.com/competitions/wikipedia-image-caption/discussion/272091)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/wikipedia-image-caption.md)
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
- **data-assistants-with-gemma**（nlp/Community｜）
  - [中期奖公告（30 票 / 6 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/487380)
  - [Gemma 发布与集成（50 票 / 13 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/478606)
  - [Gemma meets LangChain（7 票 / 4 评论）](https://www.kaggle.com/competitions/data-assistants-with-gemma/discussion/479620)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/data-assistants-with-gemma.md)
- **deep-past-initiative-machine-translation**（nlp/Featured｜DPI BLEU / chrF++）
  - [1st（94 票）](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/discussion/684353)
  - [编译讨论（93 票）](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/discussion/668402)
  - [6th（54 票）](https://www.kaggle.com/competitions/deep-past-initiative-machine-translation/discussion/684231)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/deep-past-initiative-machine-translation.md)
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
- **openai-gpt-oss-20b-red-teaming**（nlp/Featured｜）
  - [获奖公布与评审说明（24 票 / 91 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608537)
  - [攻击方法分层分类（4 票 / 5 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/608997)
  - [官方欢迎帖（39 票 / 50 评论）](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming/discussion/596882)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/openai-gpt-oss-20b-red-teaming.md)
- **2023-kaggle-ai-report**（other/Community｜Mean Absolute Error）
  - [获奖公布（51 票 / 30 评论）](https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/429989)
  - [获奖作品索引（2 票 / 2 评论）](https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/430092)
  - [积分与奖牌争议（73 票 / 37 评论）](https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/409784)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/2023-kaggle-ai-report.md)
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
- **playground-series-s3e18**（tabular/Playground｜Roc Auc Score）
  - ["不是多标签，而是两场比赛"（39 票 / 14 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/420127)
  - [EC2 最佳单模型 Bagged KNN（30 票 / 24 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/420822)
  - [中期总结（41 票 / 2 评论）](https://www.kaggle.com/competitions/playground-series-s3e18/discussion/421462)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/playground-series-s3e18.md)
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
