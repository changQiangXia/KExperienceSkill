#!/usr/bin/env python3
"""排行榜噪声计算器：LB 标准误、名次反转概率、最小可检测提升（MDL）。

用途：判断"公榜上的领先是不是噪声"、需要多大真实提升才值得占用提交、
给定测评集大小时能检测多小的差异。

用法：
  python scripts/lb_noise.py --metric auc --score 0.95 --n-test 100000 --prevalence 0.3 --public-frac 0.3
  python scripts/lb_noise.py --metric accuracy --score 0.80 --n-test 50000 --delta 0.002
  python scripts/lb_noise.py --metric rmse --sd 1.2 --n-test 50000 --corr 0.9

假设与边界（务必一起读）：
  - 正态近似；AUC 用 Hanley-McNeil 标准误；RMSE/MAE 用 sd/√n；F1 用保守的二项近似；
  - 两个提交的分数差按 σ_diff = SE·√(2(1-ρ)) 近似，ρ 需要你估计（同家族≈0.99，跨家族≈0.95，多样性融合≈0.90）；
  - 真实竞赛还有分布漂移、公榜/私榜抽样差异，本工具只量化"抽样噪声"这一项。
"""

from __future__ import annotations

import argparse
import math
import sys

METRICS = ["auc", "accuracy", "f1", "rmse", "mae", "logloss", "correlation"]


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def se_auc(score: float, n: float, prevalence: float) -> float:
    a = min(max(score, 1e-6), 1 - 1e-6)
    n_pos = max(n * prevalence, 2)
    n_neg = max(n * (1 - prevalence), 2)
    q1 = a / (2 - a)
    q2 = 2 * a * a / (1 + a)
    var = (a * (1 - a) + (n_pos - 1) * (q1 - a * a) + (n_neg - 1) * (q2 - a * a)) / (n_pos * n_neg)
    return math.sqrt(max(var, 0.0))


def se_metric(metric: str, score: float, n: float, prevalence: float, sd: float, sd_loss: float) -> float:
    if metric == "auc":
        return se_auc(score, n, prevalence)
    if metric in ("accuracy", "f1"):
        return math.sqrt(max(score * (1 - score), 1e-12) / n)
    if metric in ("rmse", "mae"):
        if sd <= 0:
            raise ValueError("RMSE/MAE 需要 --sd（残差标准差）")
        return sd / math.sqrt(n)
    if metric == "logloss":
        if sd_loss <= 0:
            raise ValueError("logloss 需要 --sd-loss（每样本 loss 的标准差）")
        return sd_loss / math.sqrt(n)
    if metric == "correlation":
        r = min(max(score, -0.999), 0.999)
        return (1 - r * r) / math.sqrt(max(n - 1, 1))
    raise ValueError(metric)


def main() -> int:
    parser = argparse.ArgumentParser(description="LB 噪声 / 名次反转 / MDL 计算器")
    parser.add_argument("--metric", required=True, choices=METRICS)
    parser.add_argument("--score", type=float, required=True)
    parser.add_argument("--n-test", type=float, required=True, help="私榜（或整个测试集）样本数")
    parser.add_argument("--prevalence", type=float, default=0.5, help="正类比例（AUC 用）")
    parser.add_argument("--public-frac", type=float, default=0.3, help="公榜占测试集比例")
    parser.add_argument("--sd", type=float, default=0.0, help="RMSE/MAE 的残差标准差")
    parser.add_argument("--sd-loss", type=float, default=0.0, help="logloss 的每样本 loss 标准差")
    parser.add_argument("--corr", type=float, default=0.95, help="两个提交的分数相关系数估计")
    parser.add_argument("--delta", type=float, default=0.0, help="要评估的观察差距（可选）")
    args = parser.parse_args()

    n_priv = args.n_test * (1 - args.public_frac)
    n_pub = args.n_test * args.public_frac
    try:
        se_pub = se_metric(args.metric, args.score, n_pub, args.prevalence, args.sd, args.sd_loss)
        se_priv = se_metric(args.metric, args.score, n_priv, args.prevalence, args.sd, args.sd_loss)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"# LB 噪声评估\n")
    print(f"- metric={args.metric} score={args.score} n_test={args.n_test:.0f} "
          f"public_frac={args.public_frac:.0%}（public n={n_pub:.0f} / private n={n_priv:.0f}）")
    print(f"- 公榜 SE ≈ {se_pub:.5f}（95% 区间 ±{1.96 * se_pub:.5f}）")
    print(f"- 私榜 SE ≈ {se_priv:.5f}（95% 区间 ±{1.96 * se_priv:.5f}）")

    print(f"\n## 名次反转概率（ρ={args.corr}）")
    print("| 观察差距 Δ | σ_diff | z=Δ/σ_diff | P(私榜反转) |")
    print("| --- | --- | --- | --- |")
    deltas = [d for d in (args.delta, 0.0005, 0.001, 0.002, 0.005) if d > 0] if args.delta else [0.0005, 0.001, 0.002, 0.005]
    seen = set()
    for d in deltas:
        if d in seen:
            continue
        seen.add(d)
        sigma = se_priv * math.sqrt(2 * (1 - args.corr))
        z = d / sigma if sigma > 0 else float("inf")
        p = phi(-z)
        print(f"| {d:.5f} | {sigma:.5f} | {z:.2f} | {p:.1%} |")

    print("\n## 最小可检测提升（95%，双侧）")
    print("| 相关性 ρ | σ_diff | MDL | 说明 |")
    print("| --- | --- | --- | --- |")
    for rho, note in [(0.99, "同家族/同管线"), (0.95, "跨家族或不同特征"), (0.90, "多样性融合")]:
        sigma = se_priv * math.sqrt(2 * (1 - rho))
        mdl = 1.96 * sigma
        print(f"| {rho} | {sigma:.5f} | {mdl:.5f} | {note} |")

    sigma_default = se_priv * math.sqrt(2 * (1 - args.corr))
    mdl_default = 1.96 * sigma_default
    target = max(args.delta, 0.001)
    need_mult = (2.8 * sigma_default / target) ** 2 if sigma_default > 0 else float("inf")
    print(f"\n结论：在 ρ={args.corr} 下，小于 {mdl_default:.5f} 的观察差距无法与抽样噪声区分；"
          f"要让 {target:.4f} 的真实提升达到 80% 检出力，约需 {need_mult:.1f}× 当前私榜样本量。")
    print("\n> 注意：以上只量化抽样噪声；公榜/私榜的分布漂移、探榜与过拟合另计（见 validation-to-lb.md）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
