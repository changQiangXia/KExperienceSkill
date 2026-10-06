# 表格赛高级配方（外部来源蒸馏）

> 来源：[kei-kochiya/kaggle-skills](https://github.com/kei-kochiya/kaggle-skills)（MIT License）的
> `kaggle-tabular-playbook/references/` 与 S6E1/S6E2/S6E3/S6E5/S6E9 handbook；
> 本地 clone 在 KStarter `data/cache/kaggle-skills`，派生索引见 `analysis/external/KAGGLE_SKILLS.md`。
> 纪律：以下数字多为**原文自述、未独立复算**（证据等级 = 原文数字/自述）；采纳前先按
> [experiment-protocol.md](experiment-protocol.md) 做同折对照，并按 [validation-to-lb.md](validation-to-lb.md) 判断 CV↔LB。

## 速查表

| 配方 | 何时用 | 第一步 | Kill 标准 |
| --- | --- | --- | --- |
| 生成器取证（snap/radix/mantissa/Benford） | Playground 合成数据、分数扎堆 | 对原数据做 snap 差值与小数位/Benford 筛查 | 找不到确定性不变量 → 不投入 |
| 嵌套 OOF 目标编码 | 高基数类别、需要 TE 做主特征 | 内层 5 折算 TE、经验贝叶斯平滑 | 折内嵌套后增益消失 → 弃 |
| CIR 校准 + Ridge 堆叠 | 概率型指标、基模型尺度不一致 | 每模型 CIR 后再 Ridge/Logit 堆叠 | 校准后 OOF 不升 → 退回原始概率 |
| Logit 堆叠 + 秩平均 | AUC/排序指标、大池融合 | logit 变换 + L2 逻辑回归；跨融合器秩平均 | ρ>0.998 的候选直接拒 |
| AUC-direct FFT 融合 | 二分类大样本、要直接优化 AUC | 直方图分箱 + fftconvolve 算成对损失 | 分箱数敏感/增益 < MDE → 弃 |
| GLM 残差 base_margin | 线性模型已强、想再加 GBDT | 内层折算 GLM logit 当 init_score | 内层嵌套不干净 → 禁止使用 |
| 超球 Fréchet 集成 + lexrank | 排序指标、概率向量被归一化/裁剪 | 单位化后测地重心；lexsort 破平局 | 破平局无增益 → 保留原序 |
| 软伪标签蒸馏 | 有可靠 teacher、测试集大 | 连续概率 + w_test=2.0，严格 OOF teacher | 硬标签或 teacher 泄漏 → 弃 |
| 过拟合法则检查 | 任何想"跟着公榜调"的时刻 | 用嵌套 CV 排名代替公榜排名 | 公榜增益 > 嵌套 CV 增益 → 停手 |

## 1. 生成器取证（Playground 合成数据的确定性不变量）

- **7 支柱**：对抗验证、合成 vs 原始数据取证、分箱经验目标率（阶梯发现）、尾数/舍入/Benford、领域方程残差、
  类别交互信息散度、重复行/泄漏检查。
- **确定性不变量**（它们造成"可分"的硬边界）：snap 匹配（回映原始数据取值）、radix 连续×类别联合编码、
  模 10 位分解、谐振周期特征、CTGAN 边界规则（100% 精确率行）。
- 我们的对应案例：s6e3（Radix/Benford）、s6e9（同分布裸特征失效 → 元特征）、s5e2（孪生行/原数据找回）。
  第一步：先在 KStarter `notes/tabular/playground-series-s6e3.md` 抄作业，再按本配方扩到当前赛。
- Kill：snap 命中率接近随机、Benford 无偏离、原数据匹配不上 → 回到常规建模。

## 2. 嵌套 OOF 目标编码（经验贝叶斯 + 多聚合）

- 平滑公式：`ŷ_c = (n_c·ȳ_c + m·μ_global) / (n_c + m)`，其中 `m = σ²_within / σ²_between`。
- 工程要点：**内层 5 折嵌套**（外层折的训练部分里再切内层）；多聚合（mean/median/std/skew/count…）拼接；
  类别组合用金字塔（单列 → 二元 → 三元）。
- 反例：s6e2 的 69th ChatGPT 全自动方案里，三元组 TE 在 KFold 外计算 → 私榜崩，剔除后反而 top20。
- 第一步：对最强类别列做一个内层嵌套 TE，与全局 TE 对比 OOF；Kill：增益 < MDE 或折间符号不稳。

## 3. CIR 校准 + Ridge 堆叠（低自由度元学习）

- `CenteredIsotonicRegression`：单调映射每个基模型输出到经验分位，保持整体重心（防均值漂移），
  解决"尾部低估/密集区高估 + 模型间尺度不一致"。
- 堆叠：校准后的预测喂 Ridge（回归）或 Logit+逻辑回归（分类）；**不要**上复杂非线性元模型。
- 我们案例：`case-books/tabular.md` 的 s6e1/s6e2 段（CIR+Ridge 拿到 1st）。
- 第一步：对 3 个尺度差异最大的基模型做 CIR→Ridge，与直接 Ridge 比 OOF。
- Kill：校准后 OOF 不升或折间不稳定 → 停用 CIR，仅保留 Ridge。

## 4. Logit 堆叠 + 秩平均 + 提交对冲

- Logit 空间：概率取 logit 后再 L2 逻辑回归，缓解极端概率与尺度差；排序指标下更稳。
- **同步多数据集折协议**：原数据+合成数据按同一折划分拼接，避免"折对齐幻觉"。
- 漂移剪枝：逐特征对抗 AUC → 高漂移特征双流分支/剪枝（我们的 `public-intel-differential.md` 是同类思想）。
- **候选筛选**：与当前融合的 Spearman ρ > 0.998 视为共线冗余，直接拒（任何权重都动不了名次）。
- **提交对冲（Clark 1961）**：两个提交相关性 ρ>0.99 时，第二个几乎零对冲价值；ρ≈0.90 且差距 <2σ 才有意义
  （配合 `submission-portfolio.md` 使用）。

## 5. AUC-direct FFT 融合（把成对排序损失变成卷积）

- 目标：直接优化成对 ROC-AUC 代理损失（正×负对数量可达 260 亿级）；用直方图分箱把成对比较变成
  两个分布的**卷积**，`scipy.signal.fftconvolve` 做到 O(n + N log N)。
- 配套：TabPFN 全上下文（`fit_with_cache`、`ignore_pretraining_limits=True`）在 66.8 万行上给出单模最强 OOF 0.946485
  （外部自述；缩放律 ≈ +18.6e-5 AUC / 上下文翻倍）。
- **关键陷阱**：不要把交叉验证产生的 OOF 预测喂给 TabPFN/KNN 这类"读邻居"的模型——会造成 +0.00162 的泄漏幻觉，
  真实迁移到测试集是 -0.00054。
- 第一步：把融合权重搜索从"网格/爬山"换成 FFT 直接法，先在小样本上对齐爬山结果；Kill：分箱数敏感或提升 < MDE。

## 6. GLM 残差提升（base_margin / init_score）

- 做法：先训线性/逻辑回归 → 取 logit 作为 `base_margin`/`init_score`，再让 GBDT 只学残差。
- 外部自述收益：3rd 0.946326 → 0.946502（+0.00018）；8th 0.946509 → 0.946617（+0.00011）。
- **禁止泄漏**：fold k 的 base_margin 必须在 fold k 的训练部分内用内层 CV 生成；否则等于把标签喂给线性层再喂给树。
- 我们案例：s6e1 的 GLM/残差思路、`technique-transfer.md` 的"残差提升"条目（R1）。
- Kill：内层嵌套后增益消失 → 弃；折间符号不一致 → 弃。

## 7. 超球 Fréchet 集成 + 确定性边界 + 零平局

- **欧氏收缩问题**：概率向量在高维里做加权平均会向原点塌缩（范数变小），排序信息被稀释。
- **测地重心**：把每个模型输出单位化到 S^{N-1}，求加权 Fréchet/Karcher 均值（迭代投影），保排序结构。
- **确定性边界不变量**：生成器产生的"硬规则行"（100% 精确率）要显式强制，不交给模型学。
- **lexrank 破平局**：AUC 下每对平局损失 0.5 个 AUC 点；用 `np.lexsort((secondary_continuous, primary))`
  给所有样本严格唯一排名（RealMLP 之类连续预测器当 secondary），比 clip/四舍五入安全。
- 第一步：测融合前后平局数量与 AUC 差；若平局为 0 且向量未塌缩，可跳过本节。

## 8. 软伪标签蒸馏 + 分组子模型悖论

- **软蒸馏法则**：用连续概率当学生目标（`w_test=2.0`），不要阈值化成 0/1；硬伪标签在外部自述里比不用还差，
  打乱软标签会让性能崩溃（证明传递的是校准后的 epistemic 不确定性）。
- **teacher 隔离**：外层折 k 的测试行 teacher 必须没见过折 k 标签（严格 OOF teacher）。
- **分组子模型悖论**：按类别切片训练的子模型单独 CV 更低（如 0.9449 vs 全局 0.9462），但进元栈后稳定 +0.000016——
  因为误差与全局模型正交；这是"多样性 > 单体强度"的又一实例。

## 9. 过拟合法则：公榜拟合的定量代价

- 外部自述的线性法则（S6E9）：`ΔPrivate ≈ +16.7u − 0.88 × ΔPublic`（r = −0.97）。
  即**每从公榜多榨 1u（1e-5），私榜平均赔 ~0.9u**；公榜 0.94945（#1）→ 私榜 0.94313（rank 1646）。
- 公榜-私榜固定偏移 ≈ 105u（诚实提交），偏移本身不是过拟合信号；**偏离嵌套 CV** 才是。
- 排名可靠性：嵌套 CV 对私榜的 Spearman 0.991，公榜只有 0.793。
- 落地：把"公榜提升"当危险信号处理，回到 `validation-to-lb.md` 的 CV 优先纪律与 `submission-portfolio.md` 对冲。

## 链接索引（来源佐证）

- 外部来源仓库：https://github.com/kei-kochiya/kaggle-skills （MIT）
- 生成器取证：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/eda_data_forensics.md
- 特征工程：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/feature_engineering.md
- OOF 目标编码：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/oof_target_encoding.md
- CIR + Ridge 堆叠：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/stacking_cir_ridge.md
- Logit 堆叠 + 秩平均：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/logit_stacking_rank_blend.md
- AUC-direct FFT：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/auc_direct_fft_blend.md
- GLM base_margin：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/glm_residual_base_margin.md
- Fréchet + lexrank：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/riemannian_hypersphere_frechet_blend.md
- 软伪标签蒸馏：https://github.com/kei-kochiya/kaggle-skills/blob/main/.agent/skills/kaggle-tabular-playbook/references/soft_pseudolabel_distillation.md
