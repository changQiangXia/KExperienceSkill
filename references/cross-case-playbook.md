# 跨场对比专题（Cross-Case Playbook）

> 第 2 轮深度：把同一问题在不同比赛里的做法并列比较，给出**条件化裁决**（什么时候用哪招）。
> 每章：问题 → 案例对照表（做法/数字/结果）→ 裁决与条件 → 决策规则 → 优先读的原文。
> 数字来自 KStarter 案例卡；引用前回 `references/case-books/<theme>.md` 或 KStarter 原文核对。

## C1｜指标结构套利：什么指标该做什么后处理

**问题**：不同指标的可利用结构完全不同；先做对结构，比换模型便宜得多。

| 案例 | 指标结构 | 后处理动作 | 数字结果 |
| --- | --- | --- | --- |
| s3e25 | 中位数型（MedAE） | 两端样本权重 0.01 + 9 档整形 | CV +0.03；56% 命中 → 0.25 |
| s3e14 | 目标仅 776 唯一值 | 预测吸附最近唯一值 | MAE +0.3 |
| s3e8 | 目标有业务上下界 | 分组分位裁剪（Q3+1.5IQR / 组内最小值） | 上界 +0.2、下界再 +1.1 |
| optiver | target 跨股票加权和恒为 0 | 零和投影（减加权均值） | ≈0.005 |
| AI4Code | 排序 + 槽位 | 最小化错位概率和 | 替代 argmax 的独立增益 |
| learning-equality | 检索→集合 | 阈值×召回数网格（margin 0.16） | F2 提升 |
| iwildcam | 计数（MAE） | 按密度分桶调阈值/NMS（8 框为界） | public 0.247 |
| fathomnet | 分类 + 未知类 | 1−max(prob) + 5×集成 std；<10 图归 unknown | OSD 基线 |

**裁决**：先读指标数学结构（中位数/排序/阈值/容差/零和/计数），再决定后处理；后处理阈值一律用 OOF 定，公榜只做 sanity check。

**决策规则**：

```text
中位数/分位 → 权重 + 档位
目标离散/唯一值少 → 吸附/分箱
有结构约束（零和/上下界/容差）→ 投影/裁剪
排序/检索 → 阈值后处理 + 秩融合
计数 → 密度分层阈值
```

**优先读**：s3e25、s3e14、s3e8、optiver、iwildcam、learning-equality。

## C2｜CV 与公榜：什么时候信谁

**问题**：CV-LB 关系由赛制与数据切分决定，不是态度问题。

| 案例 | 结构 | 现象 | 裁决 |
| --- | --- | --- | --- |
| s3e9 | CV 5407 vs 公榜 721 | 公榜是随机变量 | 只信 CV，提交 ≤2 |
| s3e22 | 20/80、小数据 | 7 区域洗牌；未选提交更高 | 提交对冲 + 只信 CV |
| s5e9 | 分数带 26.38–26.41 | LB 微差无信息 | 分布整形 + CV |
| scrabble | 实体块切分 | GroupKFold 更低更诚实 | 分组口径 + 实测相关性 |
| geolifeclef | 公榜仅 10% | 公榜很噪 | 以验证分选模 |
| feedback-prize | CV-LB 近完美线性 | CV 可当决策依据 | 大胆用 CV |
| planttraits | 提交列顺序错误 | CV/LB 大幅偏离 | 先查格式再怀疑模型 |

**裁决**：CV 可信的三条件 = 无实体/时间泄漏、指标口径正确、与公榜的秩相关经多次提交验证；缺一不可。

**决策规则**：先算 public/CV 样本量比；<1/3 时按随机变量处理；≥3–5 次提交后再判断相关性。

**优先读**：s3e9、s3e22、scrabble、geolifeclef-2022、feedback-prize。

## C3｜伪标签与蒸馏：有效与失败的分界

| 案例 | 用法 | 结果 | 分界 |
| --- | --- | --- | --- |
| sorghum 2nd | 伪标签迭代（本届数据） | 私榜 91.9→95.1 | 有信号 + 高置信 + 迭代 |
| sorghum 1st | 外部数据 + 伪标签 | 0.962→0.965 | 类别映射清晰 |
| s5e9 26th | 30% 测试伪标签 + 残差 | 自述提升，无同折对照 | 低信号：不可证 |
| hotel-id 2nd | FGVC8 伪标签 | 失败 | 域/标签映射错配 |
| lmsys | 大模型软标签蒸馏 | 70B→9B 可部署 | 教师强 + 干净校正 |
| feedback | 跨届无泄漏伪标 | 提升 | 无泄漏 + 校准 |

**裁决**：伪标签有效需要三件事同时成立——教师显著强于学生、伪标用于表示/预训练或经高置信过滤、同折对照证明；低信号与错配域是失败高发区。

**决策规则**：先做信号检验 → 再做"无伪标 / 预训练式 / 直接混训"三臂对照；直接混训只在教师强且验证干净时使用。

**优先读**：sorghum、hotel-id、s5e9、lmsys、feedback-prize。

## C4｜集成与多样性：什么时候加、什么时候停

| 案例 | 集成形态 | 结果 | 条件 |
| --- | --- | --- | --- |
| s3e23 | 6 树 + 1 非树（框架：ensemble 0.79220） | > 最好单模 0.79136 | 候选强且多样 |
| s3e23 #2 | 6 树爬山（允许负权重） | LB 0.7907→0.79101 | OOF 调权 |
| s3e18 EC2 | 集成尝试 | 无法超过 0.592 | 低信号/低天花板 |
| s3e9 | GB+RF+Ridge | 12.03 vs 单 Ridge 12.16 | 跨家族 |
| s3e8 2nd | 1816 模型两级栈 | L1→L2 稳定增益 | 大池 + CV 阈值筛选 |
| herbarium | 8 骨干按公/私榜融合 | 0.86282→0.87662 | 同族细粒度、权重需防过拟合 |
| planttraits 6th | AutoGluon 栈 | 0.526 | 多模态融合 |

**裁决**：集成的收益来自**协方差下降**；成员同质或目标低信号时收益趋零甚至过拟合。

**决策规则**：先算 OOF 相关矩阵；>0.99 的成员不加；权重只在 OOF 上搜；低信号目标设成员上限。

**优先读**：s3e23、s3e18、s3e9、s3e8、herbarium。

## C5｜域适应与分辨率：视觉比赛的第一杠杆

| 案例 | 域差 | 主要动作与数字 |
| --- | --- | --- |
| sorghum | 两块田、光照 | 512→960 私榜 84.1→91.9；IBN +0.05；直方图 +0.03；ArcFace +0.015；1024 +0.04 |
| hotel-id | 训练无掩码/测试大遮挡 | BlendFlip +0.03–0.04 mAP；md5 去重；子中心 ArcFace 0.717 |
| herbarium | 长尾细粒度 | 多级 CE +0.011；subcenter +0.017；384 +0.017；融合 0.877 |
| IMC 2024 | 透明/旋转子域 | 分场景：常规匹配工程；透明用几何先验（圆周布相机） |
| planttraits | 图像+表格 | PlantCLEF 域内预训练；三头身份任务；分层 LR |

**裁决**：视觉域差先做"分辨率阶梯 + 域归一化（IBN/直方图/颜色）+ 测试分布对齐增强"，再谈损失与集成；域内预训练权重常比换结构更值。

**决策规则**：画 train/test 外观分布 → 分辨率阶梯 → 单项域适应消融 → 度量损失 → 外部/伪标 → 融合。

**优先读**：sorghum、hotel-id、herbarium、planttraits、IMC 2024。

## C6｜长尾与未知类：按指标选策略

| 案例 | 指标 | 策略 | 结果 |
| --- | --- | --- | --- |
| herbarium | Macro F1 | 多级监督 + subcenter；放弃重采样/清洗 | 单模 0.863 |
| fathomnet | 分类 + OSD | <10 图归 unknown + label smoothing 0.1 | OSD 基线 |
| geolifeclef-2022 | top-30 | 长尾"不处理"最好；邻域换标 | 换标 +2% |
| iwildcam | 计数 MAE | 密度分层阈值，不训练 | 0.247 |
| hotel-id | MAP@K | md5 去重、子中心 ArcFace | 0.717 |

**裁决**：Macro/长尾敏感的用度量损失 + 层级监督；Micro/AUC 且测试同分布时"不处理"最好；未知类单独建 OSD 分数。

**决策规则**：先对比训练/测试类别分布；再决定"归并 unknown / 重加权 / 度量损失 / 不处理"。

**优先读**：herbarium、fathomnet、geolifeclef-2022、iwildcam。

## C7｜多目标：拆开还是合并

| 案例 | 结构 | 结果 |
| --- | --- | --- |
| s3e18 | EC1 树 / EC2 Bagged KNN，排序反转 | 11th 拆开进前 11；1st MultiOutput + 重 FE 也赢 |
| planttraits | 6 性状 + 物种身份 | 三头（回归+硬分类+软分类）；6th 标签链 |
| feedback | 整篇 + span 级 | span 池化 + 两级集成 |

**裁决**：先做"每目标小调参"实验——若最优模型族不同则拆；若目标强相关且有重 FE，多输出可共享表示。

**决策规则**：目标相关矩阵 + 每目标最优族 → 拆/合 A/B（2×2）→ 合并时用多头/软分类/标签链。

**优先读**：s3e18、planttraits。

## C8｜规则、RL 与搜索：agent 赛的路线选择

| 案例 | 路线 | 结果 | 条件 |
| --- | --- | --- | --- |
| kore-2022-beta | 规则七模块 vs Q-learning | 规则 1st；RL 打不过示例微调 | 规则可精确计算 |
| maze-crawler | 评分函数 BFS vs JAX+BC+PPO | 2006.5 vs 1796.4 | 终局可构造；RL 需模拟器 |
| lux-ai-s2 | PPO + 课程 + 热启动 | 头部 RL 配方 | 大状态空间、可向量化 |
| santa-2024 | 黑箱评分 + 局部搜索 | P5 28.5 | 有代理评分器 |
| ai-village-ctf | 最弱环攻击 | 0.894 上限 | 竞速/饱和赛 |

**裁决**：能写规则先写规则；RL 需要快模拟器、课程与对手多样性；黑箱搜索先建代理评分器。

**决策规则**：动作空间可规则化？→ 规则基线；有模拟器？→ 课程 RL；评分可本地近似？→ 局部搜索。

**优先读**：kore、maze、lux、santa、ai-village-ctf。

## C9｜LLM 约束工程：评测器决定方案

| 案例 | 约束 | 关键动作 | 数字 |
| --- | --- | --- | --- |
| aimo | T4×2、限时 | TIR 工具 + 大候选投票；3rd 120–160 候选、强制 `\boxed{}` | 1st 两阶段微调；3rd 不微调 |
| nemotron | rank≤32 LoRA、temp=0、不能跑程序 | 弱项类别合成；min-logprob 0.69 | crypt 7.9% vs 其他 100% |
| lmsys | 2×T4 16GB | 70B→9B 蒸馏 + 校准 | 公共 notebook 演进 |
| autonomous-agent | 60min/$2、ADK schema | 本地校验 + 预算工作流 | 3rd OOF 选模 |
| gpt-oss | 红队评审 | CoT 伪造/工具通道/reasoning_effort | 145 份深审 |

**裁决**：先写"评测器约束测试套件"（格式/时延/工具/预算），再谈模型；弱项类别单独合成数据。

**决策规则**：约束 → 测试 → 基线 → 弱项表 → 合成/蒸馏 → 后处理解析。

**优先读**：aimo、nemotron、lmsys、autonomous-agent、gpt-oss。

## C10｜评审制交付：什么决定名次

| 案例 | 交付形态 | 评审偏好 |
| --- | --- | --- |
| pokemon-strategy | write-up（Model/Deck/Report） | 闭环 + 消融 + 失败路径 + 图表；不公开分项 |
| bigquery | 应用 + artifact | 公开可访问、必须用三大类之一、获奖复现 |
| gpt-oss | 安全发现 | 高召回初筛 + 145 深审 + 盲样 QA + 增量危害 |
| med-gemma | 医疗应用 | 部署与提交物流；基座能力边界 |
| geolifeclef-2024 | working note | 6/7→7/8 时间线；可复现；CEUR/LNCS |
| 2023-ai-report | essay | 同行评审 + GM 终审；写作规范 |

**裁决**：评审制=可复现证据 + 清晰叙事 + 合规；分项不公开时按自包含交付。

**决策规则**：rubric → 交付清单 → 陌生环境冷启动 → 消融/失败路径 → 提前 48h 提交。

**优先读**：pokemon-strategy、bigquery、gpt-oss、med-gemma、geolifeclef-2024。

## C11｜提交策略与对冲：怎么用提交预算

| 案例 | 提交纪律 | 结果 |
| --- | --- | --- |
| s3e9 | ≤2 次提交（CV 可信） | 冠军 |
| s3e22 | top 11 中 7 队只交 1–2 次；未选提交更高 | 洗牌下的对冲纪律 |
| home-credit | 中性下注 + 双提交对冲 | 1st 0.605 vs 单边押错 |
| planttraits | 列顺序错误导致 CV/LB 偏离 | 格式事故 |
| bigquery | 提交按钮失效多帖 | 提前 48h |
| autonomous-agent | select_submission 上限 +0.0005 / 最差 −0.0166 | 保守选择 |

**裁决**：提交预算是资源；先锚点、中段对照、尾部对冲、留 1–2 次给最终选择。

**决策规则**：CV-LB 相关已证明 → 集中;未证明 → 组合对冲；格式先行。

**优先读**：s3e9、s3e22、home-credit、planttraits、autonomous-agent。

## C12｜泄漏、重复与合规

| 案例 | 现象 | 处理 | 教训 |
| --- | --- | --- | --- |
| foursquare | 67% 测试与训练重叠 | 规则建模重复关系；另备非泄漏版 | 先量化再决定 |
| s3e22 | hospital_number 复用 | 实体分组/一致化 | 泄漏与信号双面 |
| s3e8 | 重复行 exploit | 公榜 −0.05 / 私榜 +0.1 | 放弃 |
| s3e18 | 原数据合并 | 对抗验证后合并 | 分布一致再并 |
| planttraits | sample_submission 套利 | 官方换测试集 + 重置 LB | 违规成本 |
| s5e9 | 原数据随机 | 随机目标检验 | 判信号后可转向生成结构 |

**裁决**：先量化泄漏规模与合规边界；把"利用"与"放弃"都做成可切换方案。

**决策规则**：检测 → 量化 → 规则确认 → 双方案（保守/利用）→ 提交对冲。

**优先读**：foursquare、s3e22、s3e8、s3e18、planttraits。

## C13｜实验纪律：为什么有的队能持续涨分

| 案例 | 纪律 | 数字 |
| --- | --- | --- |
| s3e9 | 换种子检验 Optuna；只信 CV | 参数不存活 |
| s3e8 3rd | RMSE + 折间 std 双目标 | std 4.5→3.8 |
| s3e23 | OOF 上调权重（爬山允许负权重） | LB 0.7907→0.79101 |
| s5e9 26th | 伪标签无同折对照 | 收益不可证 |
| feedback | CV-LB 近线性 | 敢用 CV 决策 |
| s3e18 | 指标实现口径单测 | 逐列 AUC vs GINI |

**裁决**：持续涨分的队都在"修测量 → 单变量实验 → 台账 → 预注册 kill"上自律。

**决策规则**：走 `references/experiment-protocol.md`；每个实验一张 Experiment Card；连续两轮无 OOF 增益回诊断。

**优先读**：s3e9、s3e8、s3e23、feedback-prize。

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
- **geolifeclef-2024**（cv/Research｜F-Score Beta (Micro)）
  - [working note 邀请（8 票 / 4 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/506431)
  - [新手门槛吐槽（20 票 / 3 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481283)
  - [ClimateClef 数据集（20 票 / 4 评论）](https://www.kaggle.com/competitions/geolifeclef-2024/discussion/481485)
  - [KStarter 深读原文](https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/geolifeclef-2024.md)
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
