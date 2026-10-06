#!/usr/bin/env python3
"""Agent 产物审计：把"双 agent 审计"里可机器化的检查做成脚本。

覆盖 8 条提交门中可自动化的部分：长度一致 / NaN / 行序 / 折覆盖 / 折哈希 /
平局率（AUC lexrank 提示）/ 单特征泄漏烟雾测试 / 常量预测。
不可自动化的（公榜反馈泄漏、伪标签来源、流程合规）仍需人工或独立审计 agent。

用法：
  python scripts/agent_audit.py --oof oof.npy --test pred.npy \
      --test-ids test_ids.csv --sample sample_submission.csv \
      --folds folds.npy --expect-fold-hash <sha256> \
      --train train.csv --target target

退出码：出现 FAIL 返回 1（可直接进 CI / 提交前门禁）。
参考：references/agent-kaggle-playbook.md §3.7、assets/agent_workflow_checklist.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import pathlib
import sys

import numpy as np

RESULTS: list[tuple[str, str]] = []


def check(level: str, message: str) -> None:
    RESULTS.append((level, message))
    print(f"[{level}] {message}")


def load_vec(path: pathlib.Path) -> np.ndarray:
    return np.load(path, allow_pickle=False).reshape(-1)


def csv_column(path: pathlib.Path, column: str = "") -> list[str]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        idx = header.index(column) if column and column in header else 0
        return [row[idx] for row in reader if row]


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc(y: np.ndarray, score: np.ndarray) -> float:
    """秩和法 AUC（含平均秩处理平局），不依赖 sklearn。"""
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score), dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    sorted_score = score[order]
    start = 0
    for i in range(1, len(score) + 1):
        if i == len(score) or sorted_score[i] != sorted_score[start]:
            if i - start > 1:
                ranks[order[start:i]] = (start + 1 + i) / 2.0
            start = i
    n_pos = float((y == 1).sum())
    n_neg = float((y == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return (ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def main() -> int:
    parser = argparse.ArgumentParser(description="agent 产物审计（8 门中可机器化部分）")
    parser.add_argument("--oof", required=True, help="OOF 预测 .npy")
    parser.add_argument("--test", required=True, help="测试集预测 .npy")
    parser.add_argument("--expected-oof", type=int, default=0)
    parser.add_argument("--expected-test", type=int, default=0)
    parser.add_argument("--test-ids", default="", help="测试 id 的 CSV（一列）")
    parser.add_argument("--sample", default="", help="sample_submission（第一列=id 顺序）")
    parser.add_argument("--folds", default="", help="折分配 .npy（长度=OOF）")
    parser.add_argument("--expect-fold-hash", default="", help="折文件的 sha256（台账比对）")
    parser.add_argument("--train", default="", help="训练集 CSV（单特征泄漏烟雾测试）")
    parser.add_argument("--target", default="", help="目标列名（配合 --train）")
    parser.add_argument("--leak-threshold", type=float, default=0.99,
                        help="单特征 AUC 超过该值判 FAIL（默认 0.99）")
    parser.add_argument("--tie-warn", type=float, default=0.01,
                        help="重复预测占比超过该值给 WARN（默认 0.01，即 1%%）")
    args = parser.parse_args()

    oof_path = pathlib.Path(args.oof)
    test_path = pathlib.Path(args.test)
    if not oof_path.exists() or not test_path.exists():
        print("ERROR: --oof / --test 文件不存在", file=sys.stderr)
        return 1
    oof = load_vec(oof_path)
    test = load_vec(test_path)

    # 1) 长度一致
    if args.expected_oof and len(oof) != args.expected_oof:
        check("FAIL", f"OOF 长度 {len(oof)} != 期望 {args.expected_oof}")
    else:
        check("PASS", f"OOF 长度 {len(oof)}")
    if args.expected_test and len(test) != args.expected_test:
        check("FAIL", f"测试预测长度 {len(test)} != 期望 {args.expected_test}")
    else:
        check("PASS", f"测试预测长度 {len(test)}")

    # 2) NaN / Inf
    for name, vec in (("OOF", oof), ("test", test)):
        bad = int((~np.isfinite(vec)).sum())
        check("FAIL" if bad else "PASS", f"{name} 非有限值：{bad}")

    # 3) 行序（test-ids vs sample_submission 第一列）
    if args.test_ids and args.sample:
        ids = csv_column(pathlib.Path(args.test_ids))
        sample = csv_column(pathlib.Path(args.sample))
        if len(ids) != len(sample):
            check("FAIL", f"test_ids 行数 {len(ids)} != sample {len(sample)}")
        else:
            mismatch = sum(1 for a, b in zip(ids, sample) if a != b)
            check("FAIL" if mismatch else "PASS", f"行序不一致行数：{mismatch}/{len(ids)}")
        if len(ids) != len(test):
            check("FAIL", f"test_ids 行数 {len(ids)} != 测试预测长度 {len(test)}")
    else:
        check("WARN", "未提供 --test-ids/--sample，行序检查跳过")

    # 4) 平局率（AUC 排序任务）
    for name, vec in (("OOF", oof), ("test", test)):
        unique, counts = np.unique(vec, return_counts=True)
        tie_ratio = 1.0 - len(unique) / max(len(vec), 1)
        level = "WARN" if tie_ratio > args.tie_warn else "PASS"
        check(level, f"{name} 重复值占比 {tie_ratio:.4%}（唯一值 {len(unique)}）")

    # 5) 折覆盖 / 折间稳定性
    if args.folds:
        folds = load_vec(pathlib.Path(args.folds))
        if len(folds) != len(oof):
            check("FAIL", f"folds 长度 {len(folds)} != OOF 长度 {len(oof)}")
        else:
            stats = []
            for f in np.unique(folds):
                seg = oof[folds == f]
                stats.append((int(f), len(seg), float(seg.mean()), float(seg.std())))
            means = [s[2] for s in stats]
            spread = (max(means) - min(means)) if means else 0.0
            check("PASS", f"折覆盖 {len(stats)} 折：" +
                  "、".join(f"f{f}: n={n} mean={m:.4f}" for f, n, m, _ in stats))
            if len(stats) > 1 and spread > 0.05:
                check("WARN", f"折间均值差距 {spread:.4f} 偏大，检查折一致性")
        if args.expect_fold_hash:
            got = file_hash(pathlib.Path(args.folds))
            check("PASS" if got == args.expect_fold_hash else "FAIL",
                  f"折文件 sha256 {'一致' if got == args.expect_fold_hash else '不一致'}")

    # 6) 单特征泄漏烟雾测试
    if args.train and args.target:
        path = pathlib.Path(args.train)
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        if args.target not in (reader.fieldnames or []):
            check("WARN", f"train 中找不到目标列 {args.target}，泄漏烟雾测试跳过")
        else:
            y = np.array([1 if str(r[args.target]).strip().lower() in {"1", "true", "yes"} else 0
                          for r in rows])
            if y.min() == y.max():
                # 回归目标：改用 |Spearman 近似| 检查
                yv = np.array([float(r[args.target]) for r in rows])
                for col in reader.fieldnames:
                    if col == args.target:
                        continue
                    try:
                        x = np.array([float(r[col]) for r in rows])
                    except (TypeError, ValueError):
                        continue
                    if not np.isfinite(x).all() or x.std() == 0:
                        continue
                    corr = abs(float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(yv)))[0, 1]))
                    if corr > 0.9:
                        check("WARN", f"单特征 {col} 与目标秩相关 {corr:.3f} 偏高（回归目标）")
                check("PASS", "回归目标：单特征等级相关检查完成（仅提示）")
            else:
                flagged = []
                for col in reader.fieldnames:
                    if col == args.target:
                        continue
                    try:
                        x = np.array([float(r[col]) for r in rows])
                    except (TypeError, ValueError):
                        continue
                    if not np.isfinite(x).all() or x.std() == 0:
                        continue
                    a = auc(y, x)
                    a = max(a, 1 - a) if math.isfinite(a) else float("nan")
                    if math.isfinite(a) and a > args.leak_threshold:
                        flagged.append((col, a))
                if flagged:
                    check("FAIL", "单特征 AUC 过高（疑似泄漏/目标代理）：" +
                          "、".join(f"{c}={v:.4f}" for c, v in flagged[:5]))
                else:
                    check("PASS", f"单特征泄漏烟雾测试通过（{len(reader.fieldnames or [])} 列，阈值 {args.leak_threshold}）")

    # 7) 常量预测
    for name, vec in (("OOF", oof), ("test", test)):
        std = float(vec.std())
        bad = (not math.isfinite(std)) or std == 0
        check("FAIL" if bad else "PASS", f"{name} 标准差 {std:.6g}")

    fails = sum(1 for lv, _ in RESULTS if lv == "FAIL")
    warns = sum(1 for lv, _ in RESULTS if lv == "WARN")
    print(f"\nsummary: {len(RESULTS) - fails - warns} PASS / {warns} WARN / {fails} FAIL")
    if fails:
        print("结论：存在 FAIL，禁止生成提交（修好后重跑；配合 references/agent-kaggle-playbook.md §3.7 的 8 门人工审计）")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
