# 案例书：other（6 场）

> 由 KStarter 深读文档生成：每场含一句话重述、全量数字账、逐方案对照矩阵、共识/分歧与裁决全文、证据分级、悬案与失败学、图证路径、出处与外部题解。
> 用途：为新比赛找结构类比时，先读本册，再回 KStarter 深读原文核对。

## 2023-kaggle-ai-report — 2023 Kaggle AI Report 轻量深读（Tier B）

> 主题 other ｜ 类别 Community ｜ 指标 Mean Absolute Error ｜ 队伍 220 ｜ 截止 2023-07-16 ｜ Tier B ｜ 标签 other,code,review
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/2023-kaggle-ai-report.md
> 材料基础：`digests/2023-kaggle-ai-report.md`（6 篇正文：获奖公布 429989 / 获奖作品索引 430092 / 积分奖牌争议 409784 / 冠军解决方案数据集 421036 / GenAI 类冠军 430488 / 继续发 notebook 是否影响评奖 420122；80 条主题索引）+ 2 张归档图

### 一句话重述
Kaggle 官方征文赛：写"过去两年 ML 社区学到了什么"的综述，按 **7 类**（Text / Image&Video / Tabular&TimeSeries / Kaggle Competitions / Generative AI / AI Ethics / Other）各评 1 名冠军，另有 15 个 Honorable Mention，并集结为 2023 Kaggle AI Report。本场的真实张力是**"排行榜平台引入主观同行评审"**：73 票的积分/奖牌争议帖、21 票的 AI 生成内容政策帖、156 评论的置顶 Q&A，都围绕评审公平与流程展开；而冠军作品里最可复用的是 tabular 冠军的"元分析"写法——把 S3 前 13 场冠军的算法选择做成对照表（图 1）。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 规模与类别 | **220 队**；**7 个类别各 1 名冠军** + 15 个 HM（Text/Image/Tabular/Competitions/GenAI/Ethics 各 2 个 HM，Other 3 个） | 429989 |
| 冠军名单 | Text：@abireltaief（LLM 总览）；Image/Video：@radbear（视觉模型进展）；Tabular：@rhysie（典型表格管线，含 S3 前 13 场冠军算法表）；Kaggle Competitions：@iamleonie（Towards Green AI）；GenAI：@trushk（生成式 AI 综述）；AI Ethics：Team TISL；Other：@pluvias（优化算法 MoMo/Sophia） | 429989 / 430092 |
| 评审机制 | 同行评审（peer feedback）+ **Grand Masters 专家组终审**；置顶 Q&A **156 评论**；"同行评审到底评什么" 12 票 / 15 评论；"论文评审结构"指南 6 票；"早点评审"倡议 12 票 | 400084 / 421717 / 421491 / 422312 |
| 争议 ①：积分奖牌 | 73 票 / 37 评论"该不该给这场发奖牌/积分"；官方更新帖 29 票 / 15 评论（确定计入）；"终于有 analytics 赛奖牌" 10 票 | 409784 / 410802 / 409708 |
| 争议 ②：AI 生成/抄袭 | 政策帖 21 票 / 24 评论；"用 ZeroGPT 查 essay" 7 票 / 21 评论；"像 Kaggler 而不是 bot" 6 票 / 9 评论 | 409388 / 419618 / 421046 |
| 结果透明度 | "Seeking Transparency on Results" 11 票 / 4 评论；"Scores over ranking?" 7 票；Other 类别排名顺序质疑 2 票 / 5 评论；最终报告 446174（22 票）公布 | 429994 / 430034 / 430133 / 446174 |
| 复用产物 | 冠军本人的 Kaggle Winning Solutions Dataset（结构化抽取方法）+ 抽取代码 + 说明文章 + 示例分析 | 421036 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 冠军写法（7 类共性） | 评审期待 | 风险点 |
| --- | --- | --- | --- |
| 选题 | 一个类别的 2 年进展综述 | 分类内可比、覆盖近两年 | 跨类混淆（419771） |
| 证据 | 论文 + 图表（如 S3 冠军算法表、Trustworthy AI 图） | 引用可查、结构清晰 | 无引用/空泛 |
| 写作 | 结构化 essay/notebook | 同行可快速评审 | AI 痕迹/抄袭（409388） |
| 交付 | 挂到比赛数据集、公开 notebook | 可复现、可引用 | 提交规范细节多（421798） |

### 共识 / 分歧 / 裁决
**共识一：同行评审 + GM 终审是"知识型赛道"的可用机制，但需要流程护栏（400084 / 421491 / 421717 / 422312；置信度中高）**
156 评论的 Q&A 与多篇流程帖说明评审细则本身是参赛门槛；官方用 GM 组做终审、用"评审结构"帖引导反馈质量。**裁决**：投此类赛道，按论文结构（问题—证据—结论—引用）写作，并主动为评审者降低阅读成本。置信度：中高。

**分歧一：主观评审 vs 客观排行榜的积分价值（409784 vs 410802；置信度中高）**
老玩家担忧"Kaggling 的客观性被破坏"，官方最终确认计入奖牌/积分并发布更新帖。**裁决**：平台已把 meta/知识型赛道纳入积分体系；参赛者应意识到这类比赛的"评审方差"大于指标赛，选题与写作的确定性投入更划算。置信度：中高。

**共识二：AI 生成内容与抄袭是重点风控（409388 / 419618 / 421046；置信度中高）**
官方出台 AI 内容政策，社区自发用 ZeroGPT 互查，并推动"像 Kaggler 一样评审"。**裁决**：保留写作过程证据（草稿、引用、代码），宁可写得朴素也不要冒险；被质疑的成本远高于收益。置信度：中高。

**事件一：元分析式 essay 最受评审青睐（429989 + 421036；置信度中）**
tabular 冠军把 S3 前 13 场冠军的模型选择编成表；另一位冠军把 Kaggle winning solutions 抽成结构化数据集。**裁决**：在"报告类"比赛里，**可复用的结构化产物**（表、数据集、清单）比长篇叙述更能体现贡献。置信度：中。

**事件二：评审透明度仍不足（429994 / 430034 / 430133；置信度中）**
有选手公开要求结果透明、质疑"分数 vs 名次"和 Other 类排名顺序。**裁决**：接受结果不可复算的现实，把重心放在"作品可被引用/复用"上。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 7 类冠军与 HM 名单 | 官方帖（429989） | 高 |
| 奖项计入积分/奖牌 | 官方更新帖（410802） | 高 |
| 同行评审流程与争议 | 多帖 + 156 评论 Q&A | 中高 |
| AI 内容政策 | 官方帖（409388） | 高 |
| 冠军作品方法论（如 S3 表） | 作品截图（429989_img/01） | 中高 |
| 结果透明度质疑 | 讨论帖（429994 等） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 评审 rubric、具体分数与评审人意见未公开；
- Other 类排名顺序与"分数 vs 名次"争议无官方结论；
- 归档的 6 篇正文不包含完整获奖作品正文（需跳转站外 notebook）；
- 报告 overview 里的 MAE 指标与评审制实际流程的关系未被归档材料解释；
- **图证缺口**：无（2 张图，本深读内嵌 2 张）。

### 图证（KStarter 仓库内路径）
- ../../intel/2023-kaggle-ai-report/bodies/429989_img/01.png — S3 前 13 场冠军算法使用表
- ../../intel/2023-kaggle-ai-report/bodies/429989_img/02.png — Trustworthy AI 六边形

### 出处
- 获奖公布（51 票 / 30 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/429989
- 获奖作品索引（2 票 / 2 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/430092
- 积分与奖牌争议（73 票 / 37 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/409784
- 官方积分更新（29 票 / 15 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/410802
- AI 生成内容政策（21 票 / 24 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/409388
- ZeroGPT 互查（7 票 / 21 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/419618
- 置顶 Q&A（13 票 / 156 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/400084
- 结果透明性质疑（11 票 / 4 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/429994
- 冠军解决方案数据集（5 票 / 2 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/421036
- 最终报告发布（22 票 / 2 评论）：https://www.kaggle.com/competitions/2023-kaggle-ai-report/discussion/446174

---

## 5-day-ai-agents-intensive-vibecoding-course-with-google — 5-Day AI Agents Intensive (Vibe Coding with Google) 轻量深读（Tier B）

> 主题 other ｜ 类别 Featured ｜ 指标  ｜ 队伍 0 ｜ 截止 2026-06-19 ｜ Tier B ｜ 标签 other,agent,rl
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/5-day-ai-agents-intensive-vibecoding-course-with-google.md
> 材料基础：`digests/5-day-ai-agents-intensive-vibecoding-course-with-google.md`（6 篇正文：Codelabs FAQ 1654+ / Welcome+Setup 2592 / Final(Unit5) 1254 / Day2 2147 / Day3 1564 / Day1 4217 票；80 条主题索引）+ 0 张归档图

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 课程结构（5 Unit/工具/概念） | 官方课程帖（Day1–5+FAQ） | 高 |
| 成本/配额/部署说明 | 官方 FAQ | 高 |
| 课程"成效"（学员收获/落地数据） | 无 | —（缺口） |

### 悬案与失败学
**4. 悬案与缺口（登记）**
- **Unit 4（Day 4）与 Capstone 正文未收录**（主题索引有 Day4 709165、Capstone 709721、Wrap-up 609?）；本轻读缺 1/5 课程内容。
- 课程无数值化成效/评测；"0 队"表明它不是可竞技的赛道。
- 无归档图（本场无图证）。

### 出处
- Day 1（4217 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708280
- Welcome + Setup（2592 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708114
- Day 2（2147 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708469
- Codelabs FAQ（1654 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708107
- Day 3（1564 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/708744
- Final Assignment（1254 票）：https://www.kaggle.com/competitions/5-day-ai-agents-intensive-vibecoding-course-with-google/discussion/709464
- 缺口登记：Day 4（709165）、Capstone（709721）、Wrap-up（709712）、Learn Guide（716539）

---

## kaggle-survey-2021 — 2021 Kaggle ML & DS Survey（数据叙事 notebook 赛）轻量深读（Tier B）

> 主题 other ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2021-11-28 ｜ Tier B ｜ 标签 other,code
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/kaggle-survey-2021.md
> 材料基础：`digests/kaggle-survey-2021.md`（6 篇正文：7 条建议 279327 / 获奖名单 295401 / 8 大主题 278727 / 往届获奖 278542 / 早期提交奖 288495 / 21 个获奖示例 281091；72 条主题索引）+ 6 张归档图

### 一句话重述
第五届 Kaggle 年度调查的"最佳分析 notebook"赛：用问卷数据讲一个**具体**的数据故事，由 Kaggle 评审发奖。本场的最大价值是社区沉淀出的**方法论 checklist**（上届得主的 7 条建议，94 票）与**获奖作品画像**：冠军用多源外部数据构造 **AI 采用指数**，亚军们分别做 5 年性别对比（D3 主题化可视化）、Analyst vs Scientist 薪资/职责、早期职业路径与云趋势——**选题独特性与叙事质量**而非代码复杂度决定名次。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 获奖名单（295401） | 第 1 名 $10,000：《Data Science in 2021: Adaptation or Adoption?》（多源外部数据 + **AI adoption index** + 交互可视化）；4 名 runner-up 各 $5,000：性别 5 年对比（D3 + 1920s 主题）、Analyst vs Scientist（薪资差与职责）、早期职业路径（硕士生 vs 职场人）、云计算趋势（生产力/COVID/地理） | 295401 |
| 7 条建议（279327） | ①选一个具体问题（别做逐变量全景 EDA）；②角度与众不同；③研究并引用来源；④**先确认数据类型再选方法**——问卷几乎全是定性变量，不能出现 Pearson/直方图/线性回归；⑤简单图表 > 花哨图表（避开饼图/3D）；⑥所有结果都要有文字解释与完整轴/标题/图例；⑦注意美学与导航 | 279327 |
| 8 大叙事主题（278727） | ①地域 ②性别 ③技术兴起 ④编程语言 ⑤教育水平 ⑥跨年时序对比 ⑦"有价值的数据科学家" ⑧"如何成为数据科学家" | 278727 |
| 社区资产 | 往届获奖名单（2017–2020，54 票）；21 个分析赛获奖 notebook 巡礼（25 票）；外部数据集清单（24 票）；可视化改进建议（25 票）；$1,000 早期提交奖（47 票） | 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 冠军 | Runner-up（性别） | Runner-up（职业对比） | 上一届得主的建议 |
| --- | --- | --- | --- | --- |
| 选题 | AI 采用指数 | 男/女 5 年对比 | Analyst vs Scientist | "选一个具体问题" |
| 数据 | 多外部源拼接 | 2017–2021 跨年 | 同届调查 | 研究+引用来源 |
| 可视化 | 交互式 | D3.js + 1920s 主题 | 简洁图表 | 简单图表 + 完整注释 |
| 技法 | 自建指标体系 | 跨年比较 | 薪资/职责分解 | 方法匹配测量尺度 |

### 共识 / 分歧 / 裁决
**共识一：方法必须匹配数据尺度——问卷数据禁用连续变量方法（279327；置信度高）**
作者明确点名 Pearson 相关、直方图、散点图、线性回归不适用于定性变量；"0-1 编码不等于定量"。**裁决**：分析前先写清测量尺度与方法映射。置信度：高。

**共识二：选题"窄而独特"优于全景 EDA（7 条建议 + 获奖画像；置信度中高）**
获奖作品都是"一个明确命题 + 独特角度"（采用指数、性别对比、职业差异）；作者指出"Database-EDA"式 notebook 从不获奖。**裁决**：先定叙事主线，再选图与统计。置信度：中高。

**共识三：叙事与可视化质量=评分主体，引用与来源标注是硬要求（279327、281675；置信度中高）**
建议里包含"引用来源即使未复制代码"、"每个 cell 都要有解释"与"美观导航"。**裁决**：把 notebook 当论文写（问题→方法→结果→结论）。置信度：中高。

**事件：官方用早期提交奖激励分享（288495；置信度中）**
$1,000 奖励"提前公开的优秀 notebook"，与 2022 届冠军"提前两周公开换反馈"策略一致。**裁决**：评审制赛的早期公开是正收益策略。置信度：中。

**分歧：主题同质化（8 大主题清单；置信度中）**
8 大主题既是选题库也是同质化风险提示（性别/教育/语言被反复写）。**裁决**：用主题清单做起点，用外部数据或新指标做差异化。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 获奖名单与评语 | 官方公告 | 高 |
| 7 条建议 | 上届得主自述（94 票） | 中高 |
| 8 大主题 | 社区观察（63 票） | 中 |
| 21 个获奖示例/往届名单 | 社区汇总 + 官方链接 | 中高 |
| 早期提交奖 | 官方公告 | 高 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 获奖 notebook 的完整技术细节未收录（评语为主）；
- 8 大主题的示例链接在 digest 中未逐条展开；
- 早期提交奖的获奖者名单未收录；
- **图证缺口**：无（6 张图，本深读内嵌 1 张）。

### 图证（KStarter 仓库内路径）
- ../../intel/kaggle-survey-2021/bodies/295401_img/01.png — 冠军的 AI 采用指数

### 出处
- 7 条建议（94 票 / 34 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/279327
- 获奖名单（63 票 / 31 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/295401
- 8 大叙事主题（63 票 / 14 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/278727
- 往届获奖名单（54 票 / 17 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/278542
- 早期提交奖（47 票 / 20 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/288495
- 21 个获奖示例（25 票 / 2 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/281091
- 分析赛与讲故事（31 票 / 14 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/291684
- 可视化建议（25 票 / 9 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/281675
- 外部数据集（24 票 / 2 评论）：https://www.kaggle.com/competitions/kaggle-survey-2021/discussion/280726

---

## kaggle-survey-2022 — 2022 Kaggle ML & DS Survey（数据叙事 notebook 赛）轻量深读（Tier B）

> 主题 other ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2022-11-27 ｜ Tier B ｜ 标签 other,code
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/kaggle-survey-2022.md
> 材料基础：`digests/kaggle-survey-2022.md`（6 篇正文：历届获奖 359064 / 1st 幕后连载 part I 374157、part II 374969、part V 377522 / 上届作品集 359075 / 外部数据源 359047；63 条主题索引）+ 0 张归档图

### 一句话重述
Kaggle 第六届年度调查的"最佳分析 notebook"赛：用当年问卷（几乎全是定性/哑变量字段）写出一篇有叙事、有洞见的分析报告，由评审选出获奖者——**比的是选题、叙事与可视化，不是模型精度**。本届冠军的"把定性变连续"（按国家分组算占比，构造 15 个"因子"）是核心方法论；他自述开发约 **70–80 小时**，且把大量时间花在开工前的选题与草图设计上。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（2022） | "因子化"变换：以国家为分组变量，计算各群体特征占比（如 30 岁以下比例 ∈ [0,1]），共构造 **15 个因子**（覆盖人口/教育/技术/职业），把定性问卷变成可做分布/相关/回归/散点的连续变量；开发约 70–80 小时；开工前先画草图、选题放几天再用"冷脑袋"取舍；提前 2 周多公开 notebook 收集反馈；作者是第 3 次参赛（2019 无奖、2020 notebook 奖） | 374157 / 374969 / 377522 |
| 历届获奖库 | 2017–2021 全部获奖 notebook 清单（如 2021 冠军 "Adaptation or Adoption?"、2020 "One chart, many answers"、2019 "A story told through a heatmap"） | 359064 / 359075 |
| 外部数据源建议 | 往届调查（2017–2021）、Stack Overflow 开发者调查（2011–2022）、World Development Indicators 等国家级数据、Meta Kaggle、Data Science Job Salaries | 359047 |
| 评审与社区反馈 | "Charts don't talk for themselves"——图表必须配清晰解读（20 票 / 35 评论）；奖项公告（33 票 / 40 评论）；官方 Q&A（25 票 / 41 评论）；kernel 统计（16 票） | 索引 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st 的路线 | 常见做法（评审帖暗示） |
| --- | --- | --- |
| 选题 | 先构思、草图验证、放置几天再取舍 | 直接加载数据边做边找 |
| 数据处理 | **因子化**（分组占比→连续变量） | 直接对哑变量画柱状图 |
| 叙事 | 明确主线（国家间对比）+ 15 个跨领域因子 | 图表堆砌、缺少解读 |
| 运营 | 提前 2 周公开换反馈 | 截止前才发布 |
| 外部数据 | 按需拼接往届/SO/国家指标 | 只用赛方数据 |

### 共识 / 分歧 / 裁决
**共识一：评审制分析赛的核心是叙事与洞见，投入产出比与算力无关（1st、社区帖；置信度中高）**
冠军 70–80 小时主要花在选题/设计/叙事；官方反馈强调"图表需要解读"（20 票帖）。**裁决**：这类比赛的优化目标是"读者能复述你的结论"，代码与图表只是载体。置信度：中高。

**共识二："定性 → 连续"的因子化是调查数据的通用放大招（1st；置信度中）**
按分组变量计算占比，把哑变量变成 [0,1] 连续指标，从而解锁回归/相关/分布分析；作者用 15 个因子做国家对比。**裁决**：任何"类别 × 分组"的问卷数据都可套用该变换。置信度：中（单届冠军方法，但逻辑普适）。

**共识三：外部数据源拼接显著增强故事深度（359047、历届获奖库；置信度中）**
往届调查（时间趋势）、Stack Overflow（横向对照）、国家指标（上下文）、Meta Kaggle（站内行为）、薪资数据（行业对照）。**裁决**：在评审制比赛中，"多源交叉验证一个洞见"比"单表多画几张图"更有说服力。置信度：中。

**事件：评审规则的显式约束（359342、372587、358116；置信度中）**
社区明确"图表不会自己说话"、奖项按名次而非单一第 1、官方 Q&A 持续澄清规则。**裁决**：报名前逐条读评审规则（冠军也强调这一点），按 rubric 组织内容。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 冠军的因子化方法与投入时长 | 自述（幕后连载 3 篇） | 中高 |
| 历届获奖清单 | 社区汇总帖 + 官方链接 | 高 |
| 外部数据源建议 | 高票帖 | 中 |
| "图表需解读"的评审导向 | 社区反馈帖 | 中 |
| 提前公开换反馈策略 | 冠军自述 | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 获奖名次完整名单与个别获奖 notebook 的细节未收录；
- 因子化的 15 个因子清单未逐条展开；
- 评审 rubric 的完整加权未知；
- **图证缺口**：本场归档 0 图。

### 出处
- 冠军幕后 part I：开发前构思（19 票 / 7 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/374157
- 冠军幕后 part II：因子化思路（12 票）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/374969
- 冠军幕后 part V：总结与运营（10 票 / 6 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/377522
- 历届获奖 notebook 清单（53 票 / 16 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/359064
- 上届作品集（9 票）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/359075
- 外部数据源建议（35 票 / 6 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/359047
- "图表不会自己说话"（20 票 / 35 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/359342
- 奖项公告（33 票 / 40 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/372587
- 官方 Q&A（25 票 / 41 评论）：https://www.kaggle.com/competitions/kaggle-survey-2022/discussion/358116

### 外部题解（kaggle-solutions）
- rank 1｜description：https://www.kaggle.com/c/kaggle-survey-2022/discussion/375837

---

## nfl-big-data-bowl-2022 — NFL Big Data Bowl 2022 轻量深读（Tier B）

> 主题 other ｜ 类别 Community ｜ 指标  ｜ 队伍 0 ｜ 截止 2022-01-06 ｜ Tier B ｜ 标签 other,sports
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/nfl-big-data-bowl-2022.md
> 材料基础：`digests/nfl-big-data-bowl-2022.md`（6 篇正文：NFL 入门指南 274258 / 历届获奖作品 274056 / 官方欢迎 274066 / 官方欢迎与规则 274053 / 官方 demos 275296 / film study 283822；80 条主题索引）+ 0 张归档图

### 一句话重述
第四届 Big Data Bowl（**特勤组主题**）：用 2018–2020 三个赛季的 NFL Next Gen Stats 追踪数据（位置/速度/加速度/朝向）+ PFF 球探数据，分析 **punts / kickoffs / field goals & extra points** 三类战术，评审制、无目标指标，提交必须在截止时公开；另设高校组别。材料的最大价值是"分析赛方法论样板"：从**领域入门（规则/位置/计分）→ 官方 demo（踢球手偏移量，R/Python 双教程）→ 往届获奖作品**这条链路上手；同时讨论区大量帖子集中在**追踪数据质量**（身高不一致、球飞行轨迹异常、无效值、PFF 与 tracking 不匹配）。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 赛制 | **第四届** Big Data Bowl，特勤组主题；无目标指标、评审制；提交须在截止时公开；设**高校组**；无积分/奖牌（有帖专门质疑） | 274053 / 274066 / 275717 |
| 数据 | 2018–2020 赛季 NGS：全体球员位置/速度/加速度/朝向 + PFF 球探数据；三类特勤组战术策略语境不同 | 274066 |
| 官方上手链 | Beginner's Guide（18 票：规则/位置/计分）；"Special teams basics in 10 minutes"（17 票）；官方 demos：**踢球手相对中线偏移量**，R + Python 双教程（读数/清洗/动画/绘图）；Tom Bliss 位置标准化教程 | 274258 / 274376 / 275296 / 274066 |
| 历届模板 | BDB 2021 高校组/开放组获奖、NFL 1st & Future、Punt Analytics 获奖作品清单（29 票） | 274056 |
| 领域活动 | 首次 **Coaches Corner + film study**：Super Bowl 冠军 Usama Young 等教练/球员复盘弃踢战术 | 274066 / 283822 |
| 数据质量热帖 | 球员身高不一致（6 票 / 5 评论）；tracking 精度（7 票）；飞行球运动学异常；无效 tracking 值；playResult 计算；PFF/tracking 不匹配补丁；PFF hangTime NaN；同球员出现在多队 | 276122 / 295359 / 284774 / 284166 / 292798 / 298160 / 278358 / 287678 |
| 结果 | "2022 Big Data Bowl Winners" 7 票；judging/next steps 10 票 / 6 评论；虚拟 show 计划 | 307969 / 300722 / 309716 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 领域入门线 | 数据工程线 | 评审/叙事线 |
| --- | --- | --- | --- |
| 代表帖 | 规则指南 274258 / 特勤组 10 分钟 274376 | demos 275296 / 数据质量帖 | 274056 往届 / 300722 judging |
| 内容 | 位置、计分、战术语境 | 坐标标准化、朝向、PFF 对齐、异常值 | 问题定义、叙事、notebook 排版 |
| 产出 | 能看懂 play 与位置职责 | 可信的派生指标（偏移量等） | 可读的分析故事 |
| 风险 | 用错领域假设 | 脏数据导致结论错误 | 无指标可依 → 评分主观 |

### 共识 / 分歧 / 裁决
**共识一：评审制分析赛比的是"问题 + 叙事 + 可复现"（274053 / 274056 / 300722；置信度高）**
官方明确问题清单不是答题指南；往届获奖帖强调问题定义、清晰代码、排版、叙事与配色；提交必须公开。**裁决**：选题先行，用往届获奖的结构（问题—方法—结果—建议）套自己的题材；notebook 可读性与代码质量是显式评分面。置信度：高。

**共识二：领域入门先行是系列赛传统（274258 / 274376 / 287366 / 274428；置信度中高）**
最高票帖中有多篇是给"没有橄榄球背景"的 Kaggler 补规则/位置/战术的指南。**裁决**：不熟 NFL 时先花半天读规则与位置，再决定分析切口；否则容易把特勤组战术语境搞错。置信度：中高。

**共识三：追踪数据必须先做质量审计（276122 / 295359 / 284774 / 284166 / 298160；置信度中高）**
身高列不一致、跟踪精度、飞行球运动学、无效值、PFF 与 tracking 不匹配等被反复提出，甚至有人专门给出补丁。**裁决**：任何派生指标（速度、距离、偏移）之前先做一致性校验与可视化抽检；把清洗规则写进 notebook。置信度：中高。

**事件一：官方 demo 是最低成本的起手模板（275296；置信度中高）**
踢球手偏移量的 R/Python 双教程覆盖"读数 → 清洗 → 动画 → 绘图"，也是评审眼里可复现的默认风格。**裁决**：先复现 demo 再谈创新；把 demo 的坐标标准化与动画作为基线。置信度：中高。

**事件二：无排行榜 → 结果主观性与期望管理（275717 / 300722 / 314825；置信度中）**
有帖问"为什么不发积分/奖牌"；judging/next steps 帖说明评审流程与后续展示。**裁决**：接受主观评审，把差异化的"故事 + 可视化"作为主要抓手。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 赛制、数据范围与公开要求 | 官方帖（274053 / 274066） | 高 |
| 官方 demo 与工具链 | 官方帖（275296） | 高 |
| Coaches Corner / film study | 官方帖（283822） | 高 |
| 历届获奖模板 | 社区整理（274056） | 中高 |
| 数据质量问题 | 多帖（276122 / 295359 等） | 中高（现象密集） |
| 获奖作品方法论 | 未归档（仅结果帖 307969） | 低 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2022 获奖作品正文与 judging 细节未归档（307969 只有标题级信息）；
- 高校组与开放组的结果差异未归档；
- 数据质量问题的官方修正如否/范围未定论；
- 外部数据规则（284626）与天气数据（276845）的答复未归档；
- **图证缺口**：本场 0 张归档图（目录为空），已登记。

### 出处
- 官方欢迎与规则（22 票 / 7 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/274053
- 任务说明与数据范围（41 票 / 27 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/274066
- 官方 demos（18 票 / 1 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/275296
- NFL 入门指南（18 票 / 5 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/274258
- 特勤组 10 分钟（17 票 / 4 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/274376
- 历届获奖作品（29 票 / 4 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/274056
- film study（20 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/283822
- judging 与 next steps（10 票 / 6 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/300722
- 2022 Winners（7 票 / 2 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/307969
- PFF/tracking 不匹配补丁（2 票 / 0 评论）：https://www.kaggle.com/competitions/nfl-big-data-bowl-2022/discussion/298160

---

## predict-ai-model-runtime — Predict AI Model Runtime 轻量深读（Tier B）

> 主题 other ｜ 类别 Research ｜ 指标 58266_TpuGraphsEval ｜ 队伍 616 ｜ 截止 2023-11-17 ｜ Tier B ｜ 标签 other,
> 深读原文（KStarter）：https://github.com/changQiangXia/KStarter/blob/main/analysis/deep/predict-ai-model-runtime.md
> 材料基础：`digests/predict-ai-model-runtime.md`（6 篇正文：1st 456343 / 10th 456129 / 6th 456084 / 11th 456092 / 4th 456462 / 科普帖 435631；80 条主题索引）+ 6 张图

### 一句话重述
给 TPU 编译器（XLA）预测配置优劣：**tile** 子任务给融合子图挑 tile 尺寸（按 top-5 slowdown 排序），**layout** 子任务给张量维度排布挑 layout 配置（按 Kendall tau 排序）。真正的考点是**大图（10^4 节点）× 海量候选配置（1000+/图）的排序学习 + 内存/显存压缩 + 极小评测集下的抗震**。

### 关键数字（数字账）
| 关键数字 | 值 | 来源 |
| --- | --- | --- |
| 1st（68 票） | 图剪枝（只留可配置节点及其邻居）→ vRAM ÷4、训练快 5×；base-7 压缩 node_config_feat；-1 padding 统一嵌入；SAGEConv + SelfChannelAttention + **CrossConfigAttention**；PairwiseHingeLoss；**推理 batch 内配对 → 10 次置换 TTA 平均**。单模 0.748 pub / 0.714 priv；5–10 模型平均 0.757/0.736（**未选为最终提交**） | 1st |
| 10th（25 票） | **中级融合**（intermediate fusion）；layout 用线性注意力图 Transformer（12 块、APPNP/ELU+1、4090 可跑）；tile 用 cross-attention 融合；**ListMLE + 每批 ~1000 配置**；tile-only 0.197/0.196；最终选公榜最佳 sub → 0.721 pub / 0.703 priv；"最幸运私榜"另一 sub 0.706/0.715 → 自认抽奖 | 10th |
| 6th（28 票） | layout 用**5 跳邻居子图**（只保留与 cluster 节点相关的"差异节点"）+ 梯度累积；GraphNorm；4 层残差 SAGEConv（tile 上 GAT 更好）；layout 用 pairwise ranking、tile 用 ListMLE；2×48GB 工作站 | 6th |
| 11th（27 票） | **纯 LightGBM**：手工图特征（节点类型计数/拷贝次数/minor 维度分桶/填充和/配置出现率——遗传搜索下出现越频繁越可能快）；pointwise 归一化排名 MAE = 0.715/0.680；**pairwise 二分类 → 1000² 全配对求和的排序** = 0.728 pub / 0.701 priv；tile-only 0.198/0.195 | 11th |
| 事件 | 官方中途数据更新要求重训（33 票）；测试采样泄漏帖（13 票）；CV/LB 讨论（14 票）；公榜/私榜大洗牌（10th 自述"lottery"） | 社区 |

### 逐方案对照矩阵
**2. 逐方案对照矩阵**
| 维度 | 1st | 10th | 6th | 11th | 4th |
| --- | --- | --- | --- | --- | --- |
| 模型族 | GNN（SAGEConv+双注意力） | 图 Transformer（线性注意力/APPNP） | GNN（SAGE/GIN，tile 用 GAT） | LightGBM | 简单 MLP |
| 配置融合 | 早期（拼接输入） | **中级融合**（性价比最优解） | 早期（子图内配对） | 特征聚合（无需图结构） | 均值池化后点积 |
| 图规模处理 | 剪枝 + 去重 + base-7 压缩 | 分块按时加载（JIT）+ 线性注意力 | 5 跳邻域子图 + 梯度累积 | 手工统计特征降维 | node_feat 手动索引子集 |
| 损失 | PairwiseHinge | **ListMLE（1000 配置/批）** | pairwise（layout）/ListMLE（tile） | MAE / 二分类 | 排名目标 |
| 抗 shakeup | 5–10 模型平均（最终却选了单模） | 10–20 组配置混合 | — | — | — |
| 分数（pub/priv） | 0.748/0.714（单模） | 0.721/0.703（选定 sub） | — | 0.728/0.701（layout pairwise） | — |

### 共识 / 分歧 / 裁决
**共识一：内存/显存工程是头号瓶颈（四队共同）**
1st 剪枝+去重+压缩；10th 只驻留图特征、配置按需分块加载；6th 用 5 跳子图+梯度累积；11th 干脆降维成表格特征。**裁决**：本赛的"建模能力"上限被工程管线决定——先让数据装得下、跑得动，再谈结构。置信度：高。

**共识二：任务是"排序"而不是"回归"（3/4 队）**
1st PairwiseHinge；10th/6th ListMLE；11th 的 pairwise 版比 pointwise 高 +0.013 pub / +0.021 priv。**裁决**：tile/layout 的评价只看相对排名（top-5 / Kendall tau），pointwise 拟合绝对值是次优归纳偏置。置信度：高（11th 有同管线对照）。

**共识三：评测集太小 → 排名噪声主导（1st/10th/11th）**
10th 明说"重跑同设置换种子差异不显著"，被迫做 11 折才勉强分辨；11th 因无法做更好 CV 而被 shake down；1st 的最终选择与最佳集成差 0.021 priv。**裁决**：单赛分数不可全信，多配置混合/多重 TTA 是对冲手段。置信度：高（多人独立自述 + 榜面证据）。

**分歧一：图结构 vs 手工特征**
1st/10th/6th 都押 GNN/图 Transformer；11th 用 LightGBM + 手工图统计拿到 0.728 pub（**高于 1st 的单模公榜分**），且明说"假设运行时≈各节点运行时之和，聚合统计足够"。**裁决**：GNN 非必需——当可解释特征能覆盖主要方差时，表格模型在同分带内更省算力；但最终金牌归属仍需图模型。置信度：中高。

**分歧二：注意力该用在图边还是别处**
1st 明确说 GAT 类边注意力无用（"TPU 图的连接都是真连接"），但**通道注意力 + 跨配置注意力**巨大增益；10th/6th 也在配置轴上做注意力/配对。**裁决**："该在哪里做注意力"由噪声来源决定——本赛噪声在配置间比较，不在边权重。这是"先定位不确定性来源，再选归纳偏置"的范例。置信度：中高（1st 自述 + 架构图）。

**分歧三：融合时点**
早期融合（1st/6th）计算重复但表达力强；晚期融合省算力但丢失节点级对应；10th 论证中级融合是 Pareto 解。**裁决**：中级融合在"图大 × 配置多"时是最佳工程折中。置信度：中高。

**事件：官方数据更新与测试采样泄漏**
第 33 票帖要求全量重训；13 票帖指出测试采样泄漏——说明本题数据管线本身有坑。**裁决**：ML for Systems 赛要额外审计数据版本（host 可能中途换数据）。置信度：中。

### 证据分级
| 断言 | 等级 | 说明 |
| --- | --- | --- |
| 1st 的剪枝/压缩/注意力/TTA 链条 | 自述 + 架构图 + 公开代码 | 高 |
| 10th 的 unstable eval 与 11 折方案 | 自述（具体数字） | 中高 |
| 6th 的 5 跳子图与 GraphNorm | 自述 + 代码 + 图 | 中高 |
| 11th 的 LightGBM 分数与特征清单 | 自述（同管线对照 pointwise/pairwise） | 中高 |
| 公榜/私榜大洗牌 | 多队自述 + 榜面 | 高（现象） |
| 官方数据更新的影响范围 | 单帖（33 票） | 中 |

### 悬案与失败学
**5. 悬案与缺口（登记）**
- 2nd（456365）/3rd（456377）/5th/8th/9th/19th 的 write-up 未入库，中位数解法分布不完整；
- "测试采样泄漏"（456090）与 "Something Interesting About Test Data"（456083）未细读，泄漏的实际影响未量化；
- 1st 提到"最佳集成未选"——若选它是否夺冠，无法验证（事后不可反证）；
- 官方评测集到底几张图、每子任务权重如何合并（`58266_TpuGraphsEval` 细则）未在材料中展开。

### 图证（KStarter 仓库内路径）
- ../../intel/predict-ai-model-runtime/bodies/456343_img/01.png — 1st 的网络结构
- ../../intel/predict-ai-model-runtime/bodies/456129_img/01.png — 10th 的 tile/layout 双模型

### 出处
- 1st（68 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456343
- 10th（25 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456129
- 6th（28 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456084
- 11th（27 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456092
- 4th（25 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456462
- 科普（101 票，layout/tile 定义）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/435631
- 数据更新（33 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/443581
- 测试采样泄漏（13 票）：https://www.kaggle.com/competitions/predict-ai-model-runtime/discussion/456090

### 外部题解（kaggle-solutions）
- rank 2｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456365
- rank 3｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456377
- rank 5｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456093
- rank 7｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456673
- rank 8｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456645
- rank 9｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456206
- rank 13｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/458370
- rank 14｜description：https://www.kaggle.com/c/predict-ai-model-runtime/discussion/456105

---
