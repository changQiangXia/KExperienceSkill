#!/usr/bin/env python3
"""查询前 50 选手断言快照（P2/P3 经验层）。

用法：
  python scripts/gm_claim_search.py --domain cv --stage 融合 --min-units 3
  python scripts/gm_claim_search.py --domain cv --strict-units 2      # 只要技法组合级复现
  python scripts/gm_claim_search.py --tag 伪标签 --level A --limit 10
  python scripts/gm_claim_search.py --query "时间切分" --json

复现度：replication = 同领域使用任一具体技法的单位数；strict_replication = 同领域同时复现
≥2 个具体技法的单位数（含自身，≥2 视为技法组合级复现）。

输出字段：claim_id / person / level / replication / strict / stage / action / source_url
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "assets" / "gm_claims_snapshot.csv"

DOMAIN_ALIASES = {
    "cv": "视觉 CV", "vision": "视觉 CV",
    "nlp": "文本 NLP", "text": "文本 NLP", "llm": "文本 NLP",
    "tabular": "表格/结构化", "table": "表格/结构化",
    "ts": "时间序列", "timeseries": "时间序列",
    "audio": "语音/音频", "speech": "语音/音频",
    "bio": "生物/医疗", "medical": "生物/医疗",
    "rl": "强化学习/博弈", "sim": "强化学习/博弈",
    "science": "科学研究",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="", help="cv/nlp/tabular/ts/audio/bio/rl/science 或中文领域")
    parser.add_argument("--stage", default="")
    parser.add_argument("--tag", default="", help="skill 侧标签（子串匹配）")
    parser.add_argument("--person", default="")
    parser.add_argument("--level", default="", help="A/B")
    parser.add_argument("--min-units", type=int, default=2)
    parser.add_argument("--strict-units", type=int, default=0,
                        help="严格复现单位数下限（0=不启用；2=只要技法组合级复现）")
    parser.add_argument("--query", default="", help="对 condition/action/mechanism 的正则检索")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    domain = DOMAIN_ALIASES.get(args.domain.lower(), args.domain)
    rows = list(csv.DictReader(SNAPSHOT.open(encoding="utf-8")))
    out = []
    for r in rows:
        if domain and domain not in r["domain"]:
            continue
        if args.stage and args.stage not in r["stage"]:
            continue
        if args.tag and args.tag not in r["skill_tags"]:
            continue
        if args.person and args.person.lower() not in r["person"].lower():
            continue
        if args.level and r["evidence_level"] != args.level:
            continue
        if int(r["replication"]) < args.min_units:
            continue
        if args.strict_units and int(r["strict_replication"]) < args.strict_units:
            continue
        if args.query and not re.search(args.query, r["condition"] + " " + r["action"] + " " + r["mechanism"], re.I):
            continue
        out.append(r)
    out.sort(key=lambda r: (-int(r["strict_replication"]), -int(r["replication"]),
                            "A" != r["evidence_level"], -int(r["votes"])))
    out = out[: args.limit]

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0

    if not out:
        print("no claims matched", file=sys.stderr)
        return 1
    for r in out:
        action = re.sub(r"\s+", " ", r["action"])[:88]
        print(f"[{r['evidence_level']}｜units {r['replication']}/严 {r['strict_replication']}] "
              f"@{r['person']}｜{r['stage']}｜{action}")
        print(f"    {r['claim_id']}  {r['source_url']}")
    print(f"-- {len(out)} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
