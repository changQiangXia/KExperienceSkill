#!/usr/bin/env python3
"""OOF 指标报告：主指标 + bootstrap CI + 配对比较 + 多假设 FDR + 多次偷看校正（无第三方依赖）。

用法：
  python scripts/oof_report.py --oof oof.csv --target y --pred pred --metric rmse
  python scripts/oof_report.py --oof oof.csv --target y --pred base --pred2 new --metric auc
  python scripts/oof_report.py --oof oof.csv --target y --pred base --manifest variants.csv --metric auc --fdr 0.05
  python scripts/oof_report.py --oof oof.csv --target y --pred base --pred2 new --metric auc --looks 12

说明：
  - --manifest：CSV 两列（name,pred），对每个变体做与 --pred 的配对 bootstrap，输出 p 值与 BH-FDR q 值；
  - --looks N：同一对提交被反复查看 N 次时，把置信区间按 Bonferroni（α/N）收紧，避免"多看几次就显著"。
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib
import random
import sys

LOWER_BETTER = {"rmse", "mae", "medae", "logloss"}


def metric_value(metric: str, y: list[float], p: list[float], threshold: float) -> float:
    n = len(y)
    if metric == "rmse":
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(y, p)) / n)
    if metric == "mae":
        return sum(abs(a - b) for a, b in zip(y, p)) / n
    if metric == "medae":
        errs = sorted(abs(a - b) for a, b in zip(y, p))
        m = n // 2
        return errs[m] if n % 2 else (errs[m - 1] + errs[m]) / 2
    if metric == "logloss":
        eps = 1e-15
        return -sum(a * math.log(min(max(b, eps), 1 - eps)) + (1 - a) * math.log(1 - min(max(b, eps), 1 - eps)) for a, b in zip(y, p)) / n
    if metric == "auc":
        pairs = sorted(zip(p, y), key=lambda t: t[0])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and pairs[j + 1][0] == pairs[i][0]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[k] = avg
            i = j + 1
        pos = sum(1 for _, label in pairs if label >= 0.5)
        neg = n - pos
        if pos == 0 or neg == 0:
            return float("nan")
        rank_sum = sum(r for r, (_, label) in zip(ranks, pairs) if label >= 0.5)
        return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)
    if metric in ("accuracy", "f1"):
        tp = fp = fn = tn = 0
        for a, b in zip(y, p):
            pred = b >= threshold
            if a >= 0.5 and pred:
                tp += 1
            elif a < 0.5 and pred:
                fp += 1
            elif a >= 0.5 and not pred:
                fn += 1
            else:
                tn += 1
        if metric == "accuracy":
            return (tp + tn) / n
        return (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
    raise ValueError(metric)


def bootstrap_multi(y: list[float], preds: list[list[float]], metric: str, threshold: float, n_boot: int, seed: int):
    """一次重采样内同时评估所有 pred（共用同一组 idx，配对比较更严谨也更快）。"""
    rng = random.Random(seed)
    n = len(y)
    values = [[] for _ in preds]
    deltas = [[] for _ in preds[1:]]
    lower = metric in LOWER_BETTER
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ys = [y[i] for i in idx]
        ms = [metric_value(metric, ys, [p[i] for i in idx], threshold) for p in preds]
        for k, m in enumerate(ms):
            values[k].append(m)
        if len(ms) > 1 and not any(math.isnan(m) for m in ms):
            for k in range(1, len(ms)):
                deltas[k - 1].append((ms[k] - ms[0]) if not lower else (ms[0] - ms[k]))
    return values, deltas


def bootstrap(y, preds, metric, threshold, n_boot, seed):
    values, deltas = bootstrap_multi(y, preds, metric, threshold, n_boot, seed)
    return values, (deltas[0] if deltas else [])


def ci(vals: list[float], alpha: float = 0.05) -> tuple[float, float]:
    s = sorted(vals)
    lo = s[min(int((alpha / 2) * len(s)), len(s) - 1)]
    hi = s[min(int((1 - alpha / 2) * len(s)), len(s) - 1)]
    return lo, hi


def p_one_sided(deltas: list[float]) -> float:
    """deltas>0 = 变体更好；p = P(Δ≤0)。"""
    if not deltas:
        return 1.0
    return max(sum(1 for d in deltas if d <= 0) / len(deltas), 1.0 / len(deltas))


def bh_qvalues(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    q = [1.0] * m
    prev = 1.0
    for rank, idx in enumerate(reversed(order), 1):
        j = m - rank + 1
        val = min(prev, pvals[idx] * m / j)
        q[idx] = val
        prev = val
    return q


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oof", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--pred", required=True)
    parser.add_argument("--pred2", default="")
    parser.add_argument("--metric", default="rmse",
                        choices=["rmse", "mae", "medae", "auc", "logloss", "accuracy", "f1"])
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--manifest", default="", help="CSV（name,pred）：多假设 FDR 模式")
    parser.add_argument("--fdr", type=float, default=0.05, help="BH-FDR 显著性阈值（默认 0.05）")
    parser.add_argument("--looks", type=int, default=1, help="同一比较被查看的次数（>1 时按 Bonferroni 收紧 CI）")
    args = parser.parse_args()

    rows = list(csv.DictReader(pathlib.Path(args.oof).open(encoding="utf-8-sig")))
    if not rows:
        print("ERROR: 空文件", file=sys.stderr)
        return 1
    if args.pred not in rows[0] or args.target not in rows[0]:
        print(f"ERROR: 列不存在；可用列：{list(rows[0])}", file=sys.stderr)
        return 1
    y = [float(r[args.target]) for r in rows]
    preds = [[float(r[args.pred]) for r in rows]]
    if args.pred2:
        preds.append([float(r[args.pred2]) for r in rows])
    names = [args.pred]
    if args.pred2:
        names.append(args.pred2)
    if args.manifest:
        for row in csv.DictReader(pathlib.Path(args.manifest).open(encoding="utf-8-sig")):
            names.append(row.get("name", row.get("pred", "")))
            preds.append([float(r[row["pred"]]) for r in rows])

    base = metric_value(args.metric, y, preds[0], args.threshold)
    values, deltas_multi = bootstrap_multi(y, preds, args.metric, args.threshold, args.n_boot, args.seed)
    deltas = deltas_multi[0] if deltas_multi else []
    lo, hi = ci(values[0])
    direction = "lower-better" if args.metric in LOWER_BETTER else "higher-better"
    print(f"metric={args.metric} ({direction})  n={len(y)}  value={base:.6f}  95%CI=[{lo:.6f}, {hi:.6f}]")

    if len(preds) >= 2 and args.pred2:
        base2 = metric_value(args.metric, y, preds[1], args.threshold)
        lo2, hi2 = ci(values[1])
        print(f"pred2={args.pred2}: value={base2:.6f}  95%CI=[{lo2:.6f}, {hi2:.6f}]")
        if deltas:
            dlo, dhi = ci(deltas)
            p_improve = sum(1 for d in deltas if d > 0) / len(deltas)
            print(f"improvement (positive = pred2 better): mean={sum(deltas)/len(deltas):+.6f}  95%CI=[{dlo:+.6f}, {dhi:+.6f}]  P(better)={p_improve:.3f}")
            if args.looks > 1:
                alo, ahi = ci(deltas, alpha=0.05 / args.looks)
                print(f"looks={args.looks} 校正（Bonferroni α/{args.looks}）：95%CI→[{alo:+.6f}, {ahi:+.6f}]；"
                      "正确做法是预注册查看次数/用序贯检验，本项只是保守下限")
            if dlo > 0:
                print("结论：pred2 在 bootstrap 下显著更好（CI 下界 > 0）")
            elif dhi < 0:
                print("结论：pred2 显著更差")
            else:
                print("结论：差异不显著（CI 跨 0）——不要据此改方案")

    if args.manifest and deltas_multi:
        pvals = [p_one_sided(d) for d in deltas_multi]
        qvals = bh_qvalues(pvals)
        print(f"\n## 多假设比较（BH-FDR α={args.fdr}，基线={args.pred}）")
        print("| 变体 | 指标值 | meanΔ | 95%CI | p(单侧) | q(BH) | 判定 |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for i, name in enumerate(names[1:]):
            val = metric_value(args.metric, y, preds[i + 1], args.threshold)
            d = deltas_multi[i]
            mean = sum(d) / len(d)
            dlo, dhi = ci(d)
            verdict = "显著" if qvals[i] < args.fdr else "不显著"
            print(f"| {name} | {val:.6f} | {mean:+.6f} | [{dlo:+.6f}, {dhi:+.6f}] | {pvals[i]:.4f} | {qvals[i]:.4f} | {verdict} |")
        print("注：q 值控制的是整组假设的错误发现率；'显著'仍需过同折对照与机制解释。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
