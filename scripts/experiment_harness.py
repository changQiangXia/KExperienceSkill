#!/usr/bin/env python3
"""生成可复用的折文件与实验台账骨架（无第三方依赖）。

用法：
  python scripts/experiment_harness.py --data train.csv --target target \
      --strategy stratified --n-splits 5 --n-repeats 3 --seed 42 \
      --out train_folds.csv --ledger experiments_ledger.csv \
      --exp-id exp001 --hypothesis "加频次特征提升 AUC" --change "add freq encoding"

策略：kfold | stratified | group | time
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import random
from collections import defaultdict
from datetime import datetime, timezone


def read_rows(path: pathlib.Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        return reader.fieldnames or [], list(reader)


def assign_kfold(n: int, n_splits: int, rng: random.Random) -> list[int]:
    idx = list(range(n))
    rng.shuffle(idx)
    fold_of = [0] * n
    for pos, i in enumerate(idx):
        fold_of[i] = pos % n_splits
    return fold_of


def assign_stratified(rows: list[dict], target: str, n_splits: int, rng: random.Random) -> list[int]:
    by_class: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        by_class[str(row.get(target, ""))].append(i)
    fold_of = [0] * len(rows)
    offset = 0
    for key in sorted(by_class):
        members = by_class[key]
        rng.shuffle(members)
        for j, i in enumerate(members):
            fold_of[i] = (j + offset) % n_splits
        offset = (offset + len(members)) % n_splits
    return fold_of


def assign_group(rows: list[dict], group_col: str, n_splits: int, rng: random.Random) -> list[int]:
    groups: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        groups[str(row.get(group_col, ""))].append(i)
    keys = sorted(groups)
    rng.shuffle(keys)
    fold_of = [0] * len(rows)
    for pos, key in enumerate(keys):
        fold = pos % n_splits
        for i in groups[key]:
            fold_of[i] = fold
    return fold_of


def time_key(value: str):
    try:
        return (0, float(value))
    except (TypeError, ValueError):
        return (1, str(value))


def assign_time(rows: list[dict], time_col: str, n_splits: int) -> list[int]:
    order = sorted(range(len(rows)), key=lambda i: time_key(rows[i].get(time_col, "")))
    fold_of = [0] * len(rows)
    for pos, i in enumerate(order):
        fold_of[i] = min(pos * n_splits // len(rows), n_splits - 1)
    return fold_of


def fold_stats(rows: list[dict], fold_of: list[int], target: str, n_splits: int) -> list[str]:
    out = []
    for f in range(n_splits):
        vals = [rows[i].get(target, "") for i in range(len(rows)) if fold_of[i] == f]
        nums = []
        for v in vals:
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                pass
        if nums:
            mean = sum(nums) / len(nums)
            if set(nums) <= {0.0, 1.0}:
                out.append(f"f{f}:n={len(vals)},pos={mean:.3f}")
            else:
                out.append(f"f{f}:n={len(vals)},mean={mean:.4f}")
        else:
            out.append(f"f{f}:n={len(vals)}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--strategy", choices=["kfold", "stratified", "group", "time"], default="kfold")
    parser.add_argument("--group-col", default="")
    parser.add_argument("--time-col", default="")
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="train_folds.csv")
    parser.add_argument("--ledger", default="")
    parser.add_argument("--exp-id", default="")
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--change", default="")
    args = parser.parse_args()

    rows_path = pathlib.Path(args.data)
    header, rows = read_rows(rows_path)
    if not rows:
        print("ERROR: 数据为空")
        return 1
    if args.strategy == "group" and not args.group_col:
        print("ERROR: group 策略需要 --group-col")
        return 1
    if args.strategy == "time" and not args.time_col:
        print("ERROR: time 策略需要 --time-col")
        return 1

    out_header = header + [f"fold_r{r}" for r in range(args.n_repeats)]
    all_folds = []
    for r in range(args.n_repeats):
        rng = random.Random(args.seed + r)
        if args.strategy == "kfold":
            folds = assign_kfold(len(rows), args.n_splits, rng)
        elif args.strategy == "stratified":
            folds = assign_stratified(rows, args.target, args.n_splits, rng)
        elif args.strategy == "group":
            folds = assign_group(rows, args.group_col, args.n_splits, rng)
        else:
            folds = assign_time(rows, args.time_col, args.n_splits)
        all_folds.append(folds)
        print(f"repeat {r}: " + " ".join(fold_stats(rows, folds, args.target, args.n_splits)))

    out_path = pathlib.Path(args.out)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_header)
        writer.writeheader()
        for i, row in enumerate(rows):
            out = {k: row.get(k, "") for k in header}
            for r, folds in enumerate(all_folds):
                out[f"fold_r{r}"] = folds[i]
            writer.writerow(out)
    print(f"fold 文件：{out_path}（{len(rows)} 行，{args.n_repeats} 个 repeat）")

    if args.ledger:
        ledger = pathlib.Path(args.ledger)
        fields = [
            "experiment_id", "date", "hypothesis", "change", "strategy",
            "n_splits", "n_repeats", "seed", "cv_metric", "cv_value",
            "delta", "decision", "notes",
        ]
        new = not ledger.exists()
        with ledger.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            if new:
                writer.writeheader()
            writer.writerow(
                {
                    "experiment_id": args.exp_id or f"exp-{datetime.now(timezone.utc):%Y%m%d%H%M%S}",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "hypothesis": args.hypothesis,
                    "change": args.change,
                    "strategy": args.strategy,
                    "n_splits": args.n_splits,
                    "n_repeats": args.n_repeats,
                    "seed": args.seed,
                    "cv_metric": "",
                    "cv_value": "",
                    "delta": "",
                    "decision": "",
                    "notes": f"folds={args.out}",
                }
            )
        print(f"台账骨架：{ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
