# 欠覆盖方向补强：推荐/排序、优化/黑箱、时间序列

> 背景：264 场案例书按 tabular/cv/nlp/science/sim-agent/audio/other 分册，但这三个方向散落在多册里、没有独立入口。
> 本文给"读哪些案例 + 抄哪些跨人决策项 + 起步顺序 + kill 标准"，不改动案例书结构。
> 证据：`assets/gm_claims_snapshot.csv`（claim id 可回链）与 `techniques`（`technique_lookup.py` 可查）。

## 1. 推荐 / 排序（ranking、recsys、检索增强）

**先读案例**

- `otto-recommender-system`、`h-and-m-personalized-fashion-recommendations`：大规模候选生成 + 召回/排序两段式。
- `learning-equality-curriculum-recommendations`、`wikipedia-image-caption`：检索/匹配类指标（F-beta、NDCG@K）。
- `map-charting-student-math-misunderstandings`、`jigsaw-toxic-severity-rating`：MAP@K / 成对排序，后处理与阈值占分。

**跨人决策项（严格复现优先）**

- `czii-cryo-et-object-identification#561510-04`（@christofhenkel｜严 11）：**rank matching**——把 B 的预测替换成 A 的同秩值再做融合，消除分布错位。
- `kaggle-llm-science-exam#446240-01`（@philippsinger｜严 7）：chunk + 公开 embedding + 余弦相似度在 GPU 上自写（不用 FAISS），小数据下更可控。
- `eedi-mining-misconceptions-in-mathematics#551391-04`（@ebinan92｜严 7）：biencoder 取 top-52 候选 → LLM 生成单 token 取 logits 排序。
- `kaggle-llm-science-exam#446318-01`（@cdeotte｜严 7）：RAG 与模型容量的增量对比（新增 RAG 比换更大模型更提分）。

**起步顺序**：① 先拆"候选层 / 排序层"，测每层的 recall@K 与最终指标的关系；② 负采样与去重（已读过滤）；③ 排序层先上低自由度融合（秩平均/逻辑回归）；④ 最后做 top-K 截断与校准后处理。

**Kill**：top-K 截断不变时排序层提升不体现在指标 → 回到候选层；候选 recall 已饱和 → 停止扩召回，转排序与后处理。

## 2. 优化 / 黑箱 / 结构搜索

**先读案例**

- `santa-2024`（黑箱代理评分：批量困惑度暴力搜索）、`santa-2025`（连续/组合优化）。
- `google-code-golf-2025`：搜索空间 + 代码体积套利（4th 98% LLM 生成，AST 规则化提示）。
- `maze-crawler`：**启发式 1st 击败 PPO 3rd**——"更重的 RL 不是默认答案"。
- `ai-village-ctf`、`kore-2022`：代理基线 / 规则基线先行的博弈优化。
- `optiver-trading-at-the-close`：结构约束投影类后处理（验证集 5.8287→5.8240）。

**跨人决策项 / 技法**

- `technique_lookup.py --technique 黑箱代理评分`（santa-2024：批量困惑度可在 2×T4 上暴力搜排列）。
- `technique_lookup.py --technique 结构约束投影`（optiver 后处理，≈0.005 增益）。
- `technique_lookup.py --technique 规则基线` / `爬山权重搜索`。

**起步顺序**：① 先写规则/启发式基线并测延迟；② 若评分昂贵，先做**代理评分器**并验证与真评分秩相关；③ 结构约束（合法性/对称性）做成投影而不是罚项；④ 小步局部搜索 + 多次重启；⑤ 只有代理不可靠时才上学习型优化。

**Kill**：代理与真评分秩相关 <0.8 → 换代理；搜索预算已到但曲线仍单调 → 先改搜索空间而不是加算力。

## 3. 时间序列 / 在线 / 金融

**先读案例**

- `jane-street-real-time-market-data-forecasting`（2 折时序 CV + 200 天 gap 模拟私榜）。
- `g-research-crypto-forecasting`、`godaddy-microbusiness-density-forecasting`、`playground-series-s5e12`（概念漂移/ID 位移）。
- `predict-energy-behavior-of-prosumers`、`child-mind-institute-detect-sleep-states`（多源时序 + 缺失/漂移）。
- `ubiquant-market-prediction`、`amex-default-prediction`（无效清单密集，先看负结果）。

**跨人决策项（严格复现优先）**

- `tlvmc-parkinsons-freezing-gait-prediction#416057-02`（@takoihiraokazu｜严 14）：StratifiedGroupKFold by Subject + GRU + warmup（比 cosine 稳）。
- `amex-default-prediction#348014-04`（@titericz｜严 7）：有效=蒸馏/更长 early stop/大 kfold/全量训练/伪标签；无效=dow 平均后处理/LGBM 样本权重/focal loss。
- `ubiquant-market-prediction#338561-04`（@hydantess｜严 7）：无效=feature clipping/avg features/按 time_id groupby/按 corr 选特征/样本权重/target 归一化。
- `child-mind-institute-detect-sleep-states#459598-01`（@aerdem4｜严 5）：WaveNet 变体 + 差分/波动率特征。

**技法**：`时间切分/purge`、`实体分组 CV`、`在线学习`、`频率/OOD 编码`。

**起步顺序**：① 先修"时间可复现的折"（gap/purge/rolling，对齐公榜-私榜的时间切法）；② 做分布漂移检查（对抗验证）；③ 树/线性基线 → 序列模型；④ 在线更新/滚动重训；⑤ 提交时用近期窗口对冲。

**Kill**：CV 与 LB 的 Spearman <0.3 → 停建模先修验证；滚动窗收益在多个时间折上不一致 → 视为噪声。

## 与流程层的关系

以上三节都服从 `gm-generalized-process.md` 的 P0–P6：先数据理解与验证（P0/P1），再特征/建模（P2/P3），最后融合与提交工程（P4/P5），复盘写负结果（P6）。
路由入口：`python scripts/recommend.py --task "<你的任务>" --metric "<指标>" --tags "<标签>"`。
