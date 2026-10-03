#!/usr/bin/env python3
"""给参考文档追加"链接索引（来源佐证）"：列出文中提到的比赛及其题解链接 + KStarter 深读原文。

幂等：重复运行会替换已有附录。

用法：
  python tools/add_links_appendix.py --all
  python tools/add_links_appendix.py --file references/case-deep-dives.md --max-sources 3
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parent.parent
CARDS = SKILL / "assets" / "case_cards.jsonl"
MARKER = "## 链接索引（来源佐证）"

MANUAL_ALIASES = {
    "aimo": "ai-mathematical-olympiad-prize",
    "nemotron": "nvidia-nemotron-model-reasoning-challenge",
    "lmsys": "lmsys-chatbot-arena",
    "imc": "image-matching-challenge-2024",
    "santa": "santa-2024",
    "kore": "kore-2022-beta",
    "maze": "maze-crawler",
    "lux": "lux-ai-season-2-neurips-stage-2",
    "pokemon": "pokemon-tcg-ai-battle-challenge-strategy",
    "bigquery": "bigquery-ai-hackathon",
    "med-gemma": "med-gemma-impact-challenge",
    "gemini": "gemini-long-context",
    "autonomous-agent": "autonomous-agent-prediction-beta",
    "gpt-oss": "openai-gpt-oss-20b-red-teaming",
    "scrabble": "scrabble-player-rating",
    "gan": "gan-getting-started",
    "wikipedia": "wikipedia-image-caption",
    "nov2022": "tabular-playground-series-nov-2022",
    "hotel-id": "hotel-id-to-combat-human-trafficking-2022-fgvc9",
    "home-credit": "home-credit-credit-risk-model-stability",
    "jane-street": "jane-street-real-time-market-data-forecasting",
    "hull": "hull-tactical-market-prediction",
    "optiver": "optiver-trading-at-the-close",
    "amex": "amex-default-prediction",
}


def load_cards() -> dict[str, dict]:
    cards = {}
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            cards[c["slug"]] = c
    return cards


def build_aliases(cards: dict[str, dict]) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}

    def add(alias: str, slug: str) -> None:
        alias = alias.strip()
        if len(alias) < 4:
            return
        aliases.setdefault(alias.lower(), [])
        if slug not in aliases[alias.lower()]:
            aliases[alias.lower()].append(slug)

    for slug in cards:
        add(slug, slug)
        m = re.match(r"playground-series-(s\d+e\d+)$", slug)
        if m:
            add(m.group(1), slug)
        parts = slug.split("-")
        add(parts[0], slug)
        if len(parts) >= 2:
            add("-".join(parts[:2]), slug)
    for alias, slug in MANUAL_ALIASES.items():
        if slug in cards:
            add(alias, slug)
    # 只保留唯一映射的别名，避免歧义；人工别名允许重复（保留全部）
    unique: dict[str, list[str]] = {}
    for alias, slugs in aliases.items():
        if alias in MANUAL_ALIASES or len(slugs) == 1:
            unique[alias] = slugs
    return unique


def appendix(cards: dict[str, dict], slugs: list[str], max_sources: int) -> str:
    lines = [MARKER, "", "> 自动生成：本文档提到的比赛及其题解链接（Kaggle discussion，最多 %d 条）+ KStarter 深读原文。" % max_sources, ""]
    for slug in slugs:
        card = cards[slug]
        lines.append(f"- **{slug}**（{card.get('theme','')}/{card.get('category','')}｜{card.get('metric','')}）")
        for src in card.get("sources", [])[:max_sources]:
            lines.append(f"  - [{src['label']}]({src['url']})")
        if card.get("deep_doc_url"):
            lines.append(f"  - [KStarter 深读原文]({card['deep_doc_url']})")
    lines.append("")
    return "\n".join(lines)


def process(path: pathlib.Path, cards: dict[str, dict], aliases: dict[str, list[str]], max_sources: int) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        text = text[: text.index(MARKER)].rstrip() + "\n\n"
    found: set[str] = set()
    haystack = text.lower()
    for alias, slugs in aliases.items():
        if re.search(r"(?<![a-z0-9_-])" + re.escape(alias) + r"(?![a-z0-9_-])", haystack):
            for slug in slugs:
                found.add(slug)
    if not found:
        return 0
    slugs = sorted(found, key=lambda s: (cards[s].get("theme", ""), s))
    path.write_text(text + "\n" + appendix(cards, slugs, max_sources), encoding="utf-8")
    return len(slugs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--max-sources", type=int, default=3)
    args = parser.parse_args()
    cards = load_cards()
    aliases = build_aliases(cards)

    targets = [pathlib.Path(f) for f in args.file]
    if args.all:
        targets = sorted((SKILL / "references").glob("*.md"))
        targets = [p for p in targets if p.name not in ("case-index.md",)]
    for path in targets:
        n = process(path, cards, aliases, args.max_sources)
        print(f"{path.name}: {n} slugs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
