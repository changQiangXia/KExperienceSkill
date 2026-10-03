# 前 50 选手经验张力（P2）

> 同步自 KStarter `99501882bd14`（2026-10-04）；证据链接为 Kaggle 原文。


> 写法：张力 → 当前裁决 → 证据。证据为 `people/claims/gm_claims.csv` 中的断言，可经 `verify_claims.py` 回链原文。

## T1｜公开榜 vs 私有榜选模

**当前裁决**：按公私有划分与样本量决定：随机划分且 public 占比大时可参考 public；小样本/时间漂移/已知泄漏时只信 CV，并接受 public 排名下滑。

**证据**：
- [foursquare-location-matching#338112-03](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/338112)（philippsinger｜A｜最合理 CV：切出 600k 记录且 POI 唯一作验证、在剩余数据上训练（但少训一半数据）；距截止 6 周起改用 public LB 评估）
- [tlvmc-parkinsons-freezing-gait-prediction#416057-04](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction/discussion/416057)（takoihiraokazu｜A｜用 public 分数做模型选择，用 CV 指导序列长度；最终 CV 0.548 / public 0.530 / private 0.45）
- [petfinder-pawpularity-score#301015-01](https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/301015)（cdeotte｜A｜最终两个提交分别选 best LB（CV 17.15 / LB 17.64）与 best CV（CV 16.98 / LB 17.78）；b）
- [novozymes-enzyme-stability-prediction#376116-04](https://www.kaggle.com/competitions/novozymes-enzyme-stability-prediction/discussion/376116)（cdeotte｜A｜被怀疑过拟合的 RF（public 0.829）最终 private 546 第一；赛后把 RF 调 depth=4 得 public 65）
- [amex-default-prediction#348014-05](https://www.kaggle.com/competitions/amex-default-prediction/discussion/348014)（titericz｜B｜赛后发现有 2 个 private 可排 3-4 名的集成，因 CV 较低未被选）
- [icr-identify-age-related-conditions#431067-04](https://www.kaggle.com/competitions/icr-identify-age-related-conditions/discussion/431067)（cdeotte｜A｜两种风险方案：LB probing 伪标签、保守 PP 阈值；结果都伤了 private；作者最终选择它们冲一失败；干净的 time-CV ）

## T2｜伪标签/自训练：有效 vs 有害

**当前裁决**：有效但有条件：需控制伪标签噪声与标签和上限（birdclef 的两个 enabler），并保证 CV 与 LB 同向；用测试集自训练属灰区，风险与收益都大。

**证据**：
- [amex-default-prediction#347641-01](https://www.kaggle.com/competitions/amex-default-prediction/discussion/347641)（cdeotte｜A｜先用 LGBM 的 OOF+test 软标签预训练 Transformer，再用硬标签微调；test 数据也参与蒸馏）
- [birdclef-2026#704752-05](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)（nikitababich｜A｜跟踪单种子 SED 模型：1 stage 0.935、1 iter 0.946、2 iter 0.950、3 iter 0.949，两轮最优）
- [tlvmc-parkinsons-freezing-gait-prediction#416057-03](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction/discussion/416057)（takoihiraokazu｜A｜用 notype 数据与 Event 列构造硬伪标签（三目标最高预测值决定，Event=1 才置 1）；两轮伪标签：CV 从 0.279 到）
- [happy-whale-and-dolphin#320298-03](https://www.kaggle.com/competitions/happy-whale-and-dolphin/discussion/320298)（cdeotte｜A｜最佳单模 8 折 CV 0.866 / LB 0.859；12 模型 × 8 折 = 96 个模型按每折 5 预测投票集成 LB 0.868）
- [feedback-prize-english-language-learning#369609-04](https://www.kaggle.com/competitions/feedback-prize-english-language-learning/discussion/369609)（cdeotte｜B｜用 FP1 伪标签后单模 CV 从 0.4470 提升到 0.4370，但 LB 不升；且 FP1 目标分布高于 FP3）
- [birdclef-2026#704752-04](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)（nikitababich｜C｜两个解法：把 PL 标签和上限压到低于 focal 标签和；LSS 与 PL 注入同一 batch 但不同样本、禁止重叠）
- [llm-detect-ai-generated-text#470148-04](https://www.kaggle.com/competitions/llm-detect-ai-generated-text/discussion/470148)（asalhi｜A｜对集成打分：最高 X 行当 AI、最低 Y 行当人类加入训练（首轮 X=Y=1000，重复 4 到 5 次、每轮加 200 或 250）；再）

## T3｜规模（Scaling）vs 小模型/正则

**当前裁决**：由数据量与信噪比决定：大数据/高信息量支持放大（icecube/lux-3/LLM 赛），小数据或噪声大时更小的模型与更强正则更稳（polymer/DFL/playground）。

**证据**：
- [icecube-neutrinos-in-deep-ice#402888-02](https://www.kaggle.com/competitions/icecube-neutrinos-in-deep-ice/discussion/402888)（dipamc77｜A｜小模型有效的增广、监督对比、多池化、球面单分类器在大模型上被洗掉；真正提升来自 scaling：128 维 9 层 200 batch 约 ）
- [map-charting-student-math-misunderstandings#612268-04](https://www.kaggle.com/competitions/map-charting-student-math-misunderstandings/discussion/612268)（tascj0｜A｜对照 7B/8B/9B/14B/32B：loss 从 0.2716 降到 0.2589，MAP@3 从 0.9444 升到 0.9484；3）
- [playground-series-s5e3#568268-01](https://www.kaggle.com/competitions/playground-series-s5e3/discussion/568268)（cdeotte｜A｜用带偏置的简单模型（线性模型）作主模型；在线性模型上受控加入非线性交互项，并用前向特征选择挑选（LinearSVC starter））
- [neurips-open-polymer-prediction-2025#607947-05](https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025/discussion/607947)（jsday96｜A｜对照：ChemBERTa CV 0.0634、polyBERT 0.592、ModernBERT-base 0.0584、ModernBER）
- [dfl-bundesliga-data-shootout#359932-02](https://www.kaggle.com/competitions/dfl-bundesliga-data-shootout/discussion/359932)（philippsinger｜C｜只选 efficientnetv2_b0 或 b1；更大 backbone 快速过拟合）
- [playground-series-s5e1#560549-02](https://www.kaggle.com/competitions/playground-series-s5e1/discussion/560549)（cdeotte｜A｜全 5 产品共训 15 epochs cosine；加 30 个假日 bool；用 2017/2018 的首轮预测做伪标签训第二轮、再训第三）

## T4｜长序列/长上下文 vs 短训长推

**当前裁决**：训练长度与推理长度可解耦：文本/文档任务倾向更长上下文（max_len 1024-5120），时序事件任务用短序列训练 + 长序列推理并只取中段更优。

**证据**：
- [learning-agency-lab-automated-essay-scoring-2#497832-02](https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2/discussion/497832)（cdeotte｜B｜DeBERTa 用 max_length 1024/1536；RoBERTa 类改用 LongFormer；tokenizer 加 trim）
- [feedback-prize-2021#313389-04](https://www.kaggle.com/competitions/feedback-prize-2021/discussion/313389)（cdeotte｜A｜多 backbone 支持长序列：DeBERTa 任意长度、Funnel 改 config 到 1536、BigBird 用 origina）
- [AI4Code#360501-04](https://www.kaggle.com/competitions/AI4Code/discussion/360501)（hydantess｜A｜MLM 15 epochs max_len 1024 需 3 天；训练 10 epochs max_len 2048 需 7 天；作者判断 ）
- [tlvmc-parkinsons-freezing-gait-prediction#416057-01](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction/discussion/416057)（takoihiraokazu｜A｜训练用短序列（tDCS FOG 1000、DeFog 5000）、推理用长序列（3000 到 5000、15000 到 30000），只用预）
- [birdclef-2026#704752-01](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)（nikitababich｜A｜第一阶段用 cosine loss 蒸馏 backbone（11 epochs、LR 5e-4、one-cycle、batch 64）；第二）

## T5｜大集成 vs 单模/蒸馏单模

**当前裁决**：预算与推理约束决定：候选异构且时间充足时大集成/多层 stack 仍是最稳上限；推理受限或候选同质时，单模 + 蒸馏/伪标签可接近甚至超过集成。

**证据**：
- [playground-series-s5e6#587393-04](https://www.kaggle.com/competitions/playground-series-s5e6/discussion/587393)（cdeotte｜A｜9 个模型（含公开 notebook 模型）各训练多种子，合计约 300 组预测，权重用 GPU hill climbing 搜索）
- [playground-series-s5e10#614079-01](https://www.kaggle.com/competitions/playground-series-s5e10/discussion/614079)（cdeotte｜A｜2×XGB 加 3×TabM 加 2×XGB（stacked over 3×TabM）共 7 模型 hill climbing；TabM 变）
- [amex-default-prediction#348014-03](https://www.kaggle.com/competitions/amex-default-prediction/discussion/348014)（titericz｜A｜两种集成：LGBM stacking 与 CMA 进化策略；最终提交是 3 个集成的平均（LGBM stack 61 模型加两个 CMA 5）
- [feedback-prize-effectiveness#347537-01](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347537)（philippsinger｜A｜用大集成（含 2 级模型）给上一届 Feedback 生成伪标签（4 轮）+ 给本赛 train 生成 OOF 伪标签，两份软标签合并训练单）
- [playground-series-s6e8#738592-02](https://www.kaggle.com/competitions/playground-series-s6e8/discussion/738592)（cdeotte｜A｜让 Codex GPT 5.6 Sol 与 Claude Code Fable 5 各自攻单模（RealMLP 与 XGB），落后方获得领先）
- [stanford-rna-3d-folding#609774-03](https://www.kaggle.com/competitions/stanford-rna-3d-folding/discussion/609774)（jaejohn｜C｜不改模型本体，集中增强优化与选择：float64 打分、torch.cdist 向量化、预计算三次样条能量函数、PyTorch LBFGS、）

## T6｜线性融合 vs 非线性 stack

**当前裁决**：线性融合（hill climbing/加权平均）是默认安全解；当存在场景切换、特征缺失导致的条件分支时，非线性 stack 明显更优（playground-s5e4）。

**证据**：
- [petfinder-pawpularity-score#301015-04](https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/301015)（cdeotte｜A｜每天训一个新模型、保存 OOF，与当前 best CV 集成和 best LB 集成分别等权比较；提升哪个就加入哪个；关键是多样性（尺寸、b）
- [playground-series-s5e5#582611-01](https://www.kaggle.com/competitions/playground-series-s5e5/discussion/582611)（cdeotte｜A｜用 GPU hill climbing 从数百个 GBDT/NN/cuML 模型中选出 7 个（3 个 TE-XGB、1 个 product）
- [playground-series-s5e4#575784-02](https://www.kaggle.com/competitions/playground-series-s5e4/discussion/575784)（cdeotte｜A｜用非线性 stack 而非 hill climbing/ridge 做 level-2，让融合器按场景选择不同基模型）
- [playground-series-s5e6#587393-04](https://www.kaggle.com/competitions/playground-series-s5e6/discussion/587393)（cdeotte｜A｜9 个模型（含公开 notebook 模型）各训练多种子，合计约 300 组预测，权重用 GPU hill climbing 搜索）

## T7｜泄漏利用：红利 vs 反噬

**当前裁决**：可利用但必须把 private 风险计入：重复行/切分探测能大幅提分（foursquare/novozymes），但用公开榜探针制造训练目标会伤 private（ICR），且公开榜小比例时排名不可信（jigsaw）。

**证据**：
- [foursquare-location-matching#336055-02](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/336055)（takoihiraokazu｜A｜把 train 与 test 按 name、lat、lon 绑定：加 train-train 真对（1）；移除与 train 绑定的假对（2）
- [novozymes-enzyme-stability-prediction#376116-02](https://www.kaggle.com/competitions/novozymes-enzyme-stability-prediction/discussion/376116)（cdeotte｜A｜利用规则：全 0 提交报错且不扣次数；2 次提交定位切分：public 为 df.iloc[:541] 加 df.iloc[1757:] 加）
- [jigsaw-toxic-severity-rating#306074-01](https://www.kaggle.com/competitions/jigsaw-toxic-severity-rating/discussion/306074)（cdeotte｜A｜最终两个提交在 public 排 1500 与 1800，private 都到 52；两者都是 leak-free CV 0.707、pub）
- [icr-identify-age-related-conditions#431067-04](https://www.kaggle.com/competitions/icr-identify-age-related-conditions/discussion/431067)（cdeotte｜A｜两种风险方案：LB probing 伪标签、保守 PP 阈值；结果都伤了 private；作者最终选择它们冲一失败；干净的 time-CV ）
- [feedback-prize-english-language-learning#369609-04](https://www.kaggle.com/competitions/feedback-prize-english-language-learning/discussion/369609)（cdeotte｜B｜用 FP1 伪标签后单模 CV 从 0.4470 提升到 0.4370，但 LB 不升；且 FP1 目标分布高于 FP3）

## T8｜数据增广：高影响 vs 无用

**当前裁决**：按模态与数据量：视觉/序列任务增广常是首要杠杆（ASL/Rogii/Petfinder），回归与文本小数据增广往往无效甚至有害（反馈英语/amex 清单）。

**证据**：
- [asl-fingerspelling#434485-03](https://www.kaggle.com/competitions/asl-fingerspelling/discussion/434485)（christofhenkel｜A｜组合增广：时间缩放/平移、左右翻转、同签名者内 CutMix、手指/面部/姿态 dropout、时间与空间 masking；多数增广作用 5）
- [rogii-wellbore-geology-prediction#733220-05](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/733220)（w5833946｜B｜两个核心增广：Z-shift（块 bootstrap 生成 TVT 路径并保持 TVT+Z 不变，用 typewell 重建 GR，另模拟罕）
- [petfinder-pawpularity-score#301015-02](https://www.kaggle.com/competitions/petfinder-pawpularity-score/discussion/301015)（cdeotte｜B｜用随机方形裁剪（保留纵横比）代替压扁；随机裁剪同时充当增广）
- [feedback-prize-english-language-learning#369578-05](https://www.kaggle.com/competitions/feedback-prize-english-language-learning/discussion/369578)（philippsinger｜B｜无效：增广（回归尤其）、不同损失、TFIDF、其他 backbone（T5、GPT 等，Deberta 太强）、2 级模型或 stacker）
- [amex-default-prediction#348014-04](https://www.kaggle.com/competitions/amex-default-prediction/discussion/348014)（titericz｜A｜有效：知识蒸馏、更长 early stop（3000 到 10000）、大 kfold、全量训练、伪标签；无效：dow 平均后处理、LGBM）

## T9｜蒸馏/teacher-student：提速与掉分

**当前裁决**：蒸馏在推理受限时性价比最高，但教师噪声会传导：需限制伪标签权重、保持真实标签监督；学生有可能超过教师（jsday96），教师选择错误会拖后腿（Mamba）。

**证据**：
- [amex-default-prediction#347641-01](https://www.kaggle.com/competitions/amex-default-prediction/discussion/347641)（cdeotte｜A｜先用 LGBM 的 OOF+test 软标签预训练 Transformer，再用硬标签微调；test 数据也参与蒸馏）
- [llm-detect-ai-generated-text#470093-02](https://www.kaggle.com/competitions/llm-detect-ai-generated-text/discussion/470093)（jsday96｜A｜teacher：1 个 DeBERTa 加 2 个 Mamba（1024 上下文）给测试打软标签（DeBERTa 90% 权重）；训两个短上）
- [feedback-prize-effectiveness#347537-01](https://www.kaggle.com/competitions/feedback-prize-effectiveness/discussion/347537)（philippsinger｜A｜用大集成（含 2 级模型）给上一届 Feedback 生成伪标签（4 轮）+ 给本赛 train 生成 OOF 伪标签，两份软标签合并训练单）
- [birdclef-2026#704752-01](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)（nikitababich｜A｜第一阶段用 cosine loss 蒸馏 backbone（11 epochs、LR 5e-4、one-cycle、batch 64）；第二）
- [birdclef-2026#704752-04](https://www.kaggle.com/competitions/birdclef-2026/discussion/704752)（nikitababich｜C｜两个解法：把 PL 标签和上限压到低于 focal 标签和；LSS 与 PL 注入同一 batch 但不同样本、禁止重叠）
- [llm-detect-ai-generated-text#470093-05](https://www.kaggle.com/competitions/llm-detect-ai-generated-text/discussion/470093)（jsday96｜A｜mamba-790m 速度与 DeBERTa-large 相当、显存更低；但取 last-token logits 受 padding 影响）

## T10｜时间/分组 CV 的必要性

**当前裁决**：存在时间漂移、会话/用户泄漏或域偏移时必须用时间切分或分组折（ICR/Otto/Eedi/写作）；否则随机折会系统性高估。

**证据**：
- [icr-identify-age-related-conditions#431067-01](https://www.kaggle.com/competitions/icr-identify-age-related-conditions/discussion/431067)（cdeotte｜A｜按日期排序、给无日期样本随机分配日期，再滑动 START/END 窗口，每折验证为窗口内全部行；理由：XGB 把时间当特征时会成为最重要特征）
- [otto-recommender-system#370210-02](https://www.kaggle.com/competitions/otto-recommender-system/discussion/370210)（cdeotte｜B｜前 3 周训练、最后 1 周验证；再把验证周拆成 A/B，A 当测试输入、B 当标签）
- [eedi-mining-misconceptions-in-mathematics#551391-01](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics/discussion/551391)（ebinan92｜A｜从 GroupKFold by QuestionId 改为 by SubjectId，让验证集包含更多仅出现在验证的 Misconcepti）
- [linking-writing-processes-to-writing-quality#466906-02](https://www.kaggle.com/competitions/linking-writing-processes-to-writing-quality/discussion/466906)（darraghdog｜B｜观察 GBM 的 LB/CV 比远好于 Deberta（Deberta CV 强但 LB 差）→ 推测 LB 按主题或学生年份划分存在域偏移）
- [MABe-mouse-behavior-detection#663029-01](https://www.kaggle.com/competitions/MABe-mouse-behavior-detection/discussion/663029)（cdeotte｜A｜只用 host 说明会出现在测试中的 15 个 lab_id 计算 CV；XGB 的 CV 0.475 与 public LB 0.477 ）

## T11｜使用测试数据：特征适配 vs 标签窥探

**当前裁决**：用测试特征做域适应/伪标签通常可接受且有收益；用测试标签或探针反推标签风险高，且可能违反赛制精神；需在规则边界内选择。

**证据**：
- [llm-detect-ai-generated-text#470148-04](https://www.kaggle.com/competitions/llm-detect-ai-generated-text/discussion/470148)（asalhi｜A｜对集成打分：最高 X 行当 AI、最低 Y 行当人类加入训练（首轮 X=Y=1000，重复 4 到 5 次、每轮加 200 或 250）；再）
- [novozymes-enzyme-stability-prediction#376116-01](https://www.kaggle.com/competitions/novozymes-enzyme-stability-prediction/discussion/376116)（cdeotte｜B｜用 public test 当验证：先生成大量单模型与特征，再 probe LB 取回 public 标签，用它们训 level-2 模型）
- [icr-identify-age-related-conditions#431067-04](https://www.kaggle.com/competitions/icr-identify-age-related-conditions/discussion/431067)（cdeotte｜A｜两种风险方案：LB probing 伪标签、保守 PP 阈值；结果都伤了 private；作者最终选择它们冲一失败；干净的 time-CV ）
- [foursquare-location-matching#338112-04](https://www.kaggle.com/competitions/foursquare-location-matching/discussion/338112)（philippsinger｜A｜作者赛后才知道泄漏（论坛早有讨论）；期间选择被泄漏偏置（更长训练、更强过拟合在该数据上有效），但确保长训不伤 CV；赛后分析显示方案在无重叠）

## T12｜Agent 自动化：生产力 vs 新意边界

**当前裁决**：工程实现、实验循环、看板与打包可高度自动化（s6e8/rogii/neurogolf），但问题重构、新意与关键假设仍需人类判断（pressman1 明言不能替代思考）。

**证据**：
- [playground-series-s6e8#738592-01](https://www.kaggle.com/competitions/playground-series-s6e8/discussion/738592)（cdeotte｜A｜让单个 Codex GPT 5.6 Sol autorun agent 全自动：读赛题、下数据、建大集成；每加 10 到 50 个模型就自动）
- [playground-series-s6e8#738592-02](https://www.kaggle.com/competitions/playground-series-s6e8/discussion/738592)（cdeotte｜A｜让 Codex GPT 5.6 Sol 与 Claude Code Fable 5 各自攻单模（RealMLP 与 XGB），落后方获得领先）
- [rogii-wellbore-geology-prediction#733181-01](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction/discussion/733181)（cdeotte｜A｜codex --yolo 连续两周 + 2×L4 跑实验；GPT5.6 Sol 读讨论/notebook/搜网页理解科学；每晚与 Codex）
- [neurogolf-2026#726653-01](https://www.kaggle.com/competitions/neurogolf-2026/discussion/726653)（yiheng｜A｜先构建优化系统而非逐任务优化：受 2025 Code Golf 第四名方案启发（并行采样、规则化 prompt 生成、候选验证、选最优、结构）
- [orbit-wars#714324-02](https://www.kaggle.com/competitions/orbit-wars/discussion/714324)（pressman1｜C｜用 Codex 完成开发，人工只审文档；agent 能正确实现规格但建议与创造力不足）

