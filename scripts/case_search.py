#!/usr/bin/env python3
"""在案例库中检索类比比赛（支持浅层索引与深层案例卡）。

用法：
  python scripts/case_search.py --query "Median Absolute Error"
  python scripts/case_search.py --theme tabular --tag synthetic --limit 10
  python scripts/case_search.py --query "CoT 伪造 工具通道" --deep
  python scripts/case_search.py --query "domain shift" --deep --json

--deep 会在 case_cards.jsonl 的关键数字/裁决/失败学/证据分级中一起检索。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "assets" / "case_index.csv"
CARDS = ROOT / "assets" / "case_cards.jsonl"


def tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[\s,;/|]+", text.lower()) if t]


def card_blob(card: dict) -> str:
    parts = [card.get("one_line", ""), card.get("title", "")]
    for k in card.get("key_numbers", []):
        parts += [k.get("claim", ""), k.get("value", ""), k.get("source", "")]
    for v in card.get("verdicts", []):
        parts += [v.get("heading", ""), v.get("text", "")]
    parts += card.get("failures", [])
    for e in card.get("evidence", []):
        parts += [e.get("assertion", ""), e.get("note", "")]
    return " ".join(parts).lower()


def score(row: dict, card: dict | None, query: list[str], metric: str, theme: str, tags: list[str], deep: bool) -> float:
    blob = " ".join([row["slug"], row["title"], row["theme"], row["metric"], row["tags"], row["one_line"]]).lower()
    if deep and card:
        blob += " " + card_blob(card)
    s = 0.0
    for token in query:
        if token in blob:
            s += 3
        if token in row["slug"].lower():
            s += 2
    if metric:
        s += 6 if metric.lower() in row["metric"].lower() else 0
    if theme:
        s += 4 if theme.lower() == row["theme"].lower() else 0
    row_tags = set(t for t in row["tags"].split(",") if t)
    for tag in tags:
        s += 4 if tag.lower() in row_tags else 0
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description="Kaggle 经验案例检索")
    parser.add_argument("--query", default="", help="关键词（空格分隔）")
    parser.add_argument("--metric", default="")
    parser.add_argument("--theme", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--deep", action="store_true", help="在完整案例卡中检索")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not INDEX.exists():
        print(f"ERROR: 缺少 {INDEX}", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(INDEX.open(encoding="utf-8")))
    cards = {}
    if args.deep and CARDS.exists():
        for line in CARDS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                c = json.loads(line)
                cards[c["slug"]] = c

    query = tokens(args.query)
    ranked = sorted(
        ((score(r, cards.get(r["slug"]), query, args.metric, args.theme, args.tag, args.deep), r) for r in rows),
        key=lambda x: x[0],
        reverse=True,
    )
    hit = [(s, r) for s, r in ranked if s > 0][: args.limit]
    if not hit:
        print("没有命中；尝试放宽关键词/去掉 theme 或 metric 过滤，或用 --deep。")
        return 0

    if args.json:
        out = []
        for s, r in hit:
            card = cards.get(r["slug"], {})
            out.append({**r, "score": s, "key_numbers": card.get("key_numbers", [])[:4]})
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    for s, r in hit:
        print(f"[{s:.0f}] {r['slug']}  ({r['theme']}/{r['category']} | {r['metric']} | {r['tags']})")
        if r["one_line"]:
            print(f"     {r['one_line'][:200]}")
        card = cards.get(r["slug"])
        if card:
            for k in card.get("key_numbers", [])[:2]:
                print(f"     · {k['claim']}: {k['value'][:160]} [{k['source']}]")
            for s in card.get("sources", [])[:1]:
                print(f"     link: [{s['label'][:60]}]({s['url']})")
        print(f"     deep: {r['deep_doc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
