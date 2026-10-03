#!/usr/bin/env python3
"""在 case_index.csv 中检索类比比赛（供经验迁移与改进方案生成）。

用法：
  python case_search.py --query "Median Absolute Error"
  python case_search.py --theme tabular --tag synthetic --limit 10
  python case_search.py --query "retrieval embedding" --json

输出：slug、主题/类别、指标、标签、一句话经验、深读文档路径。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

ASSET = pathlib.Path(__file__).resolve().parent.parent / "assets" / "case_index.csv"


def tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[\s,;/|]+", text.lower()) if t]


def score(row: dict[str, str], query: list[str], metric: str, theme: str, tags: list[str]) -> float:
    blob = " ".join(
        [row["slug"], row["title"], row["theme"], row["metric"], row["tags"], row["one_line"]]
    ).lower()
    s = 0.0
    for token in query:
        if token in blob:
            s += 3
        if token in row["slug"].lower():
            s += 2
    if metric:
        s += 5 if metric.lower() in row["metric"].lower() else 0
    if theme:
        s += 4 if theme.lower() == row["theme"].lower() else 0
    row_tags = set(t for t in row["tags"].split(",") if t)
    for tag in tags:
        if tag.lower() in row_tags:
            s += 4
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description="Kaggle 经验案例检索")
    parser.add_argument("--query", default="", help="关键词（空格分隔，OR 计分）")
    parser.add_argument("--metric", default="")
    parser.add_argument("--theme", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--asset", default=str(ASSET))
    args = parser.parse_args()

    path = pathlib.Path(args.asset)
    if not path.exists():
        print(f"ERROR: 找不到 {path}", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(path.open(encoding="utf-8")))

    query = tokens(args.query)
    ranked = sorted(
        ((score(r, query, args.metric, args.theme, args.tag), r) for r in rows),
        key=lambda x: x[0],
        reverse=True,
    )
    hit = [(s, r) for s, r in ranked if s > 0][: args.limit]
    if not hit:
        print("没有命中；尝试放宽关键词/去掉 theme 或 metric 过滤。")
        return 0

    if args.json:
        print(json.dumps([{**r, "score": s} for s, r in hit], ensure_ascii=False, indent=2))
        return 0

    for s, r in hit:
        print(f"[{s:.0f}] {r['slug']}  ({r['theme']}/{r['category']} | {r['metric']} | {r['tags']})")
        if r["one_line"]:
            print(f"     {r['one_line'][:180]}")
        print(f"     deep: {r['deep_doc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
