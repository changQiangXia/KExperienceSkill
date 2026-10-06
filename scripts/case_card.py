#!/usr/bin/env python3
"""打印某场比赛的完整案例卡（关键数字/裁决/失败学/证据分级）。

用法：python scripts/case_card.py --slug playground-series-s3e25 [--json]
不带 --slug 时列出所有 slug。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ASSET = pathlib.Path(__file__).resolve().parent.parent / "assets" / "case_cards.jsonl"


def load_cards() -> dict[str, dict]:
    if not ASSET.exists():
        print(f"ERROR: 缺少 {ASSET}（先运行 tools/build_case_cards.py）", file=sys.stderr)
        sys.exit(1)
    cards = {}
    for line in ASSET.read_text(encoding="utf-8").splitlines():
        if line.strip():
            card = json.loads(line)
            cards[card["slug"]] = card
    return cards


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    cards = load_cards()

    if not args.slug:
        for slug in sorted(cards):
            print(slug)
        return 0
    card = cards.get(args.slug)
    if not card:
        print(f"没有 {args.slug}；尝试 python scripts/case_card.py 查看全部 slug", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(card, ensure_ascii=False, indent=2))
        return 0

    print(f"# {card['slug']} — {card['title']}")
    print(f"- {card['theme']} / {card['category']} / 指标 {card['metric']} / 队伍 {card['teams']}")
    print(f"- 深读：{card['deep_doc']}")
    print(f"\n## 一句话\n{card['one_line']}\n")
    print("## 关键数字")
    for k in card["key_numbers"]:
        print(f"- {k['claim']}：{k['value']}（{k['source']}）")
    print("\n## 共识 / 分歧 / 裁决")
    for v in card["verdicts"]:
        print(f"- {v['heading']}：{v['text']}")
    print("\n## 失败与悬案")
    for f in card["failures"]:
        print(f"- {f}")
    print("\n## 证据分级")
    for e in card["evidence"]:
        print(f"- {e['assertion']}｜{e['level']}｜{e['note']}")
    print("\n## 题解链接（来源佐证）")
    for s in card.get("sources", []):
        print(f"- [{s['label']}]({s['url']})")
    if card.get("external_links"):
        print("\n## 外部题解（kaggle-solutions，未收录过的）")
        for link in card["external_links"]:
            print(f"- [rank {link['rank']}｜{link['kind']}]({link['url']})")
    if card.get("deep_doc_url"):
        print(f"- [KStarter 深读原文]({card['deep_doc_url']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
