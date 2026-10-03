#!/usr/bin/env python3
"""查询技法 × 案例地图。

用法：
  python scripts/technique_lookup.py --list
  python scripts/technique_lookup.py --technique 伪标签
  python scripts/technique_lookup.py --query 校准
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys

MAP = pathlib.Path(__file__).resolve().parent.parent / "assets" / "technique_case_map.csv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--technique", default="")
    parser.add_argument("--query", default="")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if not MAP.exists():
        print(f"ERROR: 缺少 {MAP}（先运行 tools/build_technique_map.py）", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(MAP.open(encoding="utf-8")))

    if args.list:
        seen = []
        for r in rows:
            if r["technique"] not in seen:
                seen.append(r["technique"])
        for t in seen:
            print(t)
        return 0

    key = args.technique or args.query
    if not key:
        print("用法：--list / --technique X / --query Y", file=sys.stderr)
        return 1
    hits = [r for r in rows if key.lower() in r["technique"].lower()]
    if not hits:
        hits = [r for r in rows if key.lower() in r["snippet"].lower()]
    if not hits:
        print("没有命中；用 --list 查看全部技法。")
        return 0
    current = None
    for r in hits:
        if r["technique"] != current:
            current = r["technique"]
            print(f"\n## {current}")
        print(f"- [{r['role']}] {r['slug']}")
        if r["snippet"]:
            print(f"    {r['snippet'][:240]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
