#!/usr/bin/env python3
"""OOF 指标报告：主指标 + bootstrap CI + 可选配对比较（无第三方依赖）。

用法：
  python scripts/oof_report.py --oof oof.csv --target y --pred pred --metric rmse
  python scripts/oof_report.py --oof oof.csv --target y --pred base --pred2 new --metric auc
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


def bootstrap(y: list[float], preds: list[list[float]], metric: str, threshold: float, n_boot: int, seed: int):
    rng = random.Random(seed)
    n = len(y)
    values = [[] for _ in preds]
    deltas = []
    lower = metric in LOWER_BETTER
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ys = [y[i] for i in idx]
        ms = [metric_value(metric, ys, [p[i] for i in idx], threshold) for p in preds]
        for k, m in enumerate(ms):
            values[k].append(m)
        if len(ms) == 2 and not (math.isnan(ms[0]) or math.isnan(ms[1])):
            deltas.append((ms[1] - ms[0]) if not lower else (ms[0] - ms[1]))
    return values, deltas


def ci(vals: list[float]) -> tuple[float, float]:
    s = sorted(vals)
    return s[int(0.025 * len(s))], s[int(0.975 * len(s))]


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

    base = metric_value(args.metric, y, preds[0], args.threshold)
    values, deltas = bootstrap(y, preds, args.metric, args.threshold, args.n_boot, args.seed)
    lo, hi = ci(values[0])
    direction = "lower-better" if args.metric in LOWER_BETTER else "higher-better"
    print(f"metric={args.metric} ({direction})  n={len(y)}  value={base:.6f}  95%CI=[{lo:.6f}, {hi:.6f}]")

    if len(preds) == 2:
        base2 = metric_value(args.metric, y, preds[1], args.threshold)
        lo2, hi2 = ci(values[1])
        print(f"pred2={args.pred2}: value={base2:.6f}  95%CI=[{lo2:.6f}, {hi2:.6f}]")
        if deltas:
            dlo, dhi = ci(deltas)
            p_improve = sum(1 for d in deltas if d > 0) / len(deltas)
            print(f"improvement (positive = pred2 better): mean={sum(deltas)/len(deltas):+.6f}  95%CI=[{dlo:+.6f}, {dhi:+.6f}]  P(better)={p_improve:.3f}")
            if dlo > 0:
                print("结论：pred2 在 bootstrap 下显著更好（CI 下界 > 0）")
            elif dhi < 0:
                print("结论：pred2 显著更差")
            else:
                print("结论：差异不显著（CI 跨 0）——不要据此改方案")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
