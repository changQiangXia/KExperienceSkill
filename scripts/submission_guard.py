#!/usr/bin/env python3
"""提交前 CSV 体检：列顺序/行数/ID 集合/空值/数值可解析。

只依赖标准库，适合在 Kaggle notebook 或本地最后一步运行。

用法：
  python submission_guard.py --submission submission.csv --sample sample_submission.csv
  python submission_guard.py --submission sub.csv --sample sample.csv --strict --quiet

退出码：0 = 通过（或仅 warning）；1 = 有 error（--strict 时 warning 也算失败）。
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib
import sys


def read_csv(path: pathlib.Path) -> tuple[list[str], list[list[str]]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError(f"{path} 是空文件")
    return rows[0], rows[1:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Kaggle submission CSV 体检")
    parser.add_argument("--submission", required=True)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--id-col", default=None, help="默认取 sample 的第一列")
    parser.add_argument("--allow-extra-cols", action="store_true")
    parser.add_argument("--skip-numeric", action="store_true", help="跳过非 ID 列的数值检查")
    parser.add_argument("--strict", action="store_true", help="warning 也视为失败")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    sub_path = pathlib.Path(args.submission)
    sample_path = pathlib.Path(args.sample)
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    for path in (sub_path, sample_path):
        if not path.exists():
            print(f"ERROR: 文件不存在: {path}")
            return 1
        if path.stat().st_size == 0:
            print(f"ERROR: 文件为空: {path}")
            return 1

    try:
        sub_header, sub_rows = read_csv(sub_path)
        sample_header, sample_rows = read_csv(sample_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: 解析失败: {exc}")
        return 1

    # 1) 列与列顺序
    if sub_header != sample_header:
        if set(sub_header) == set(sample_header):
            errors.append(
                "列名相同但顺序不同：Kaggle 按位置读取，顺序错误会直接扣分/判错。"
            )
        else:
            missing = [c for c in sample_header if c not in sub_header]
            extra = [c for c in sub_header if c not in sample_header]
            if missing:
                errors.append(f"缺少列: {missing[:8]}")
            if extra:
                if args.allow_extra_cols:
                    warnings.append(f"存在额外列（已允许）: {extra[:8]}")
                else:
                    errors.append(f"存在额外列: {extra[:8]}")

    # 2) 行数
    if len(sub_rows) != len(sample_rows):
        errors.append(f"行数不一致: submission={len(sub_rows)} sample={len(sample_rows)}")

    # 3) ID 集合
    id_col = args.id_col or (sample_header[0] if sample_header else None)
    id_idx = sample_header.index(id_col) if id_col in sample_header else None
    if id_idx is None:
        warnings.append(f"找不到 ID 列 {id_col!r}，跳过 ID 校验")
    else:
        def ids_of(rows: list[list[str]]) -> list[str]:
            return [r[id_idx] for r in rows if len(r) > id_idx]

        sub_ids = ids_of(sub_rows)
        sample_ids = ids_of(sample_rows)
        dup = {i for i in sub_ids if sub_ids.count(i) > 1}
        if dup:
            errors.append(f"ID 列存在重复值: {list(dup)[:5]}")
        missing_ids = set(sample_ids) - set(sub_ids)
        extra_ids = set(sub_ids) - set(sample_ids)
        if missing_ids:
            errors.append(f"缺少 {len(missing_ids)} 个 ID，例如 {list(missing_ids)[:5]}")
        if extra_ids:
            errors.append(f"多出 {len(extra_ids)} 个 ID，例如 {list(extra_ids)[:5]}")

    # 4) 空值 / 非有限值 / 数值可解析
    pred_cols = [i for i, c in enumerate(sub_header) if i != id_idx]
    bad_empty = 0
    bad_numeric = 0
    examples: list[str] = []
    for r_i, row in enumerate(sub_rows):
        for c_i in pred_cols:
            if c_i >= len(row):
                bad_empty += 1
                continue
            cell = row[c_i].strip()
            if cell == "" or cell.lower() in {"nan", "na", "none", "null"}:
                bad_empty += 1
                if len(examples) < 5:
                    examples.append(f"row {r_i + 2} col {sub_header[c_i]}")
                continue
            if not args.skip_numeric:
                try:
                    value = float(cell)
                    if math.isnan(value) or math.isinf(value):
                        bad_numeric += 1
                except ValueError:
                    bad_numeric += 1
    if bad_empty:
        errors.append(f"预测列存在空/NaN 文本 {bad_empty} 处，例如 {examples[:3]}")
    if bad_numeric:
        warnings.append(f"有 {bad_numeric} 个预测值无法解析为有限数值（确认指标是否允许）")

    if not args.quiet:
        notes.append(f"submission: {len(sub_rows)} 行 × {len(sub_header)} 列 -> {sub_path}")
        notes.append(f"sample:     {len(sample_rows)} 行 × {len(sample_header)} 列 -> {sample_path}")
        for n in notes:
            print(n)
        for w in warnings:
            print(f"WARN:  {w}")
        for e in errors:
            print(f"ERROR: {e}")
        if not errors:
            print("PASS ✅ 提交格式通过")

    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
