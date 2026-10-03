# 改进方案模板（按赛型）

> 用法：选一个赛型模板，套 `improvement-plan-protocol.md` 的假设表；默认实验是**起点**，不是全部。

## 1. 表格回归（RMSE/MAE/MedAE/分位）

```text
Competition Card：指标结构（均值/中位数/分位）｜目标离散度｜实体/时间切分｜提交限制
默认实验 1：metric 单测 + 目标唯一值/分位统计（30min）
默认实验 2：两端样本权重 / 档位吸附（OOF 对照）
默认实验 3：清洗三件套（哨兵值/重复/近常数）+ OOD 频率编码
默认实验 4：GBDT 基线 + 跨家族多样性（线性/核）
关键检查：随机目标检验（合成赛）｜CV-LB 样本量｜分组 CV
常用案例：s3e25 / s3e14 / s5e9 / s3e9 / s3e8
```

## 2. 表格分类（AUC/F1/LogLoss）

```text
Competition Card：类别分布/阈值型还是排序型｜多标签还是多分类｜实体键
默认实验 1：指标实现 + 阈值/先验口径
默认实验 2：分层/多标签 CV + 实体分组审计
默认实验 3：类别不平衡策略对照（损失/采样/阈值）
默认实验 4：跨家族集成 + 校准（若 LogLoss）
关键检查：头部子群分数｜阈值附近样本｜重复实体
常用案例：s3e18 / s3e22 / amex / feedback-prize
```

## 3. 时序 / 金融 / 在线

```text
Competition Card：预测窗口/评测频率/在线训练限制｜非平稳性｜指标（Sharpe/capture/zero-mean R²）
默认实验 1：复刻评测窗口的时间 CV（含 gap）
默认实验 2：简单基线（Lag/GBDT/MLP）+ "截至当前"滚动特征
默认实验 3：在线更新 vs 不更新的对照
默认实验 4：组合/风险层（若指标是 Sharpe）
关键检查：时间穿越｜时延预算｜分布漂移
常用案例：jane-street / optiver / hull / amex
```

## 4. CV 分类 / 细粒度

```text
Competition Card：域差（采集/设备/光照/掩码）｜分辨率｜类间相似度｜长尾
默认实验 1：分辨率阶梯（224→384→512）
默认实验 2：域适应单项（IBN/直方图/颜色归一化）
默认实验 3：度量损失（ArcFace/subcenter）+ 分类头
默认实验 4：域内预训练权重对照
默认实验 5：TTA / 多折 / 多骨干融合
关键检查：掩码/遮挡分布｜长尾归并｜外部数据许可
常用案例：sorghum / hotel-id / herbarium / planttraits
```

## 5. CV 检测 / 分割 / 计数 / 检索

```text
Competition Card：指标（AP/F1/MAE/拓扑/容差）｜GT 可得性｜阈值/后处理空间
默认实验 1：指标结构分类（体素/拓扑/容差/计数）
默认实验 2：后处理链（去小连通/补洞/裁剪/阈值分层）
默认实验 3：检测/分割/计数多阶段系统
默认实验 4：检索路线对照（logits/embedding+kNN）
关键检查：密度分层｜OOD/未知类｜图像 I/O 与数据版本
常用案例：vesuvius / hubmap / iwildcam / fathomnet / hotel-id
```

## 6. NLP / LLM

```text
Competition Card：任务形态（理解/生成/检索/推理/工具）｜评测约束（token/时延/格式）｜可否微调/工具
默认实验 1：约束测试套件 + 输出解析
默认实验 2：强基线（微调或大候选 + 投票）
默认实验 3：弱项类别表 + 合成数据（若可验证）
默认实验 4：蒸馏/校准（若推理受限）
默认实验 5：后处理（强制格式/拒绝采样/阈值）
关键检查：引用核验｜泄漏/私有数据｜推理预算
常用案例：aimo / nemotron / lmsys / AI4Code / feedback-prize
```

## 7. 模拟对战 / RL Agent

```text
Competition Card：终局规则/结算｜动作空间｜可否本地模拟｜提交 slot 限制
默认实验 1：终局规则表 + 规则基线（评分函数/兵力计算）
默认实验 2：快模拟器或轻量自对弈
默认实验 3：课程 + 热启动
默认实验 4：对手多样性 + 镜像对局
默认实验 5：KL/资源/胜率曲线早停
关键检查：环境一致性｜随机种子｜提交 slot 策略
常用案例：lux / maze / kore / santa
```

## 8. 评审制 / 研究 / Hackathon / Agent-Config

```text
Competition Card：rubric/评审流程｜交付格式（字数/页数/视频/模型）｜可复现要求｜预算/配额
默认实验 1：rubric → 交付清单映射
默认实验 2：陌生环境冷启动复现
默认实验 3：消融 + 失败路径 + 图表
默认实验 4：叙事/视频/文档整合
默认实验 5：预算/配额/提交保护（提前 48h）
关键检查：公开可访问｜私有依赖｜作者归属/资格
常用案例：pokemon-strategy / bigquery / gpt-oss / med-gemma / geolifeclef
```
