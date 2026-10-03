#!/usr/bin/env python3
"""从 KStarter 仓库生成 skill 的案例索引：
- assets/case_index.csv
- references/case-index.md

用法：
  python tools/build_case_index.py --kstarter-root /root/autodl-tmp/kaggle
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parent.parent

TAG_RULES = [
    ("tabular", r"tabular|playground|tps|tabular-playground"),
    ("regression", r"regression|regress"),
    ("classification", r"classification|classif|binary|multiclass|multilabel"),
    ("time-series", r"time.?series|forecast|temporal|jp[x]?|market|stock|energy"),
    ("cv", r"image|vision|segment|detect|photo|video|gan|contrail|histopath|cell|leaf|plant"),
    ("segmentation", r"segment"),
    ("detection", r"detect|yolo|osd"),
    ("nlp", r"nlp|text|prompt|llm|language|translation|caption|essay|chat"),
    ("llm", r"llm|gpt|gemma|gemini|prompt|language model"),
    ("agent", r"agent|simulation|battle|game|bot|rl|reinforcement"),
    ("rl", r"rl\b|reinforcement|ppo|self.?play|agent"),
    ("audio", r"audio|speech|bird|sound|whale|cough"),
    ("science", r"science|physics|biology|medical|health|climate|chem|protein|brain"),
    ("medical", r"medical|health|brain|tumor|cancer|xray|cxr|pathology|derm|medgemma"),
    ("finance", r"stock|market|crypto|insurance|amex|jpx|credit|loan|trading"),
    ("code", r"code|software|notebook|ai4code|kaggle-ai-report"),
    ("retrieval", r"retriev|matching|search|similarity|embedding|knn|image-caption"),
    ("ranking", r"ranking|ndcg|auc|map@|kendall|spearman"),
    ("optimization", r"optimization|optimisation|santa|knapsack|routing"),
    ("generative", r"gan|generat|diffusion|synthetic"),
    ("review", r"review|essay|report|writeup|analytics|hackathon|research"),
    ("synthetic", r"playground|synthetic|generated"),
    ("geospatial", r"geolife|remote|satellite|rsna|amazon|lidar"),
    ("sports", r"nfl|nba|march|football|soccer|sport|baseball|tennis"),
    ("wildlife", r"whale|bird|iwildcam|animal|fathomnet|marine|species|fish"),
    ("agriculture", r"sorghum|plant|leaf|herbarium|crop|agricultur|weed|seed"),
    ("drug-discovery", r"drug|protein|molecule|chem|enzyme|redrug|oncology"),
    ("ecommerce", r"shopee|h&m|retail|product|price|fashion|store|sale"),
    ("education", r"student|education|curriculum|tutor|essay|quiz|learning"),
    ("security", r"security|attack|jailbreak|red.?team|ctf|malware|phishing"),
]


def parse_digest(root: pathlib.Path, slug: str) -> dict[str, str]:
    path = root / "digests" / f"{slug}.md"
    meta = {"theme": "", "category": "", "subclass": "", "metric": "", "teams": "", "deadline": ""}
    if not path.exists():
        return meta
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()[:10]:
        if "类别：" in line:
            pairs = dict(
                (p.split("：", 1)[0].strip(), p.split("：", 1)[1].strip())
                for p in line.lstrip("- ").split("｜")
                if "：" in p
            )
            meta["category"] = pairs.get("类别", "")
            meta["theme"] = pairs.get("主题", "")
            meta["subclass"] = pairs.get("子类", "")
        if "队伍数：" in line:
            m = re.search(r"队伍数：\s*([\d,]+)", line)
            meta["teams"] = m.group(1) if m else ""
        if "截止：" in line:
            m = re.search(r"截止：\s*([\d-]+)", line)
            meta["deadline"] = m.group(1) if m else ""
        if "评估指标：" in line:
            meta["metric"] = line.split("评估指标：", 1)[1].strip()
    return meta


def parse_deep(root: pathlib.Path, slug: str) -> dict[str, str]:
    path = root / "analysis" / "deep" / f"{slug}.md"
    if not path.exists():
        return {"title": slug, "one_line": "", "tier": "B"}
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    title = slug
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    tier = "B" if "Tier B" in "\n".join(lines[:5]) else "A"
    one_line = ""
    for i, line in enumerate(lines):
        if "一句话重述" in line and line.lstrip().startswith("#"):
            for nxt in lines[i + 1 :]:
                stripped = nxt.strip()
                if not stripped or stripped.startswith(("#", "|", ">", "-")):
                    if one_line:
                        break
                    continue
                one_line += stripped + " "
                if len(one_line) > 150:
                    break
            break
    one_line = re.sub(r"\*\*|`", "", one_line)
    one_line = re.sub(r"\s+", " ", one_line).strip()
    return {"title": title, "one_line": one_line[:180], "tier": tier}


def tags_for(blob: str) -> str:
    low = blob.lower()
    return ",".join(dict.fromkeys(tag for tag, pattern in TAG_RULES if re.search(pattern, low)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kstarter-root", default="/root/autodl-tmp/kaggle")
    args = parser.parse_args()
    root = pathlib.Path(args.kstarter_root)
    if not (root / "analysis" / "deep").exists():
        print(f"ERROR: {root} 不是有效的 KStarter 根目录")
        return 1

    slugs = sorted(p.stem for p in (root / "analysis" / "deep").glob("*.md"))
    rows = []
    github_base = "https://github.com/changQiangXia/KStarter/blob/main/"
    for slug in slugs:
        meta = parse_digest(root, slug)
        deep = parse_deep(root, slug)
        notes = list((root / "notes").rglob(f"{slug}.md"))
        blob = f"{slug} {deep['title']} {meta['theme']} {meta['metric']}"
        theme_tag = "agent" if meta["theme"] == "sim-agent" else (meta["theme"] or "other")
        tag_str = ",".join(dict.fromkeys([theme_tag] + tags_for(blob).split(",")))
        rows.append(
            {
                "slug": slug,
                "title": deep["title"],
                "theme": meta["theme"],
                "category": meta["category"],
                "metric": meta["metric"],
                "teams": meta["teams"],
                "deadline": meta["deadline"],
                "tier": deep["tier"],
                "tags": tag_str,
                "one_line": deep["one_line"],
                "deep_doc": f"analysis/deep/{slug}.md",
                "notes_doc": notes[0].relative_to(root).as_posix() if notes else "",
                "deep_doc_url": f"{github_base}analysis/deep/{slug}.md",
                "notes_doc_url": f"{github_base}{notes[0].relative_to(root).as_posix()}" if notes else "",
            }
        )

    out_csv = SKILL / "assets" / "case_index.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    by_theme: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by_theme.setdefault(r["theme"] or "other", []).append(r)
    lines = [
        "# 264 场经验索引（Case Index）",
        "",
        f"> 共 {len(rows)} 场；`assets/case_index.csv` 是机器可读版，用 `scripts/case_search.py` 检索；深读原文见 KStarter 仓库 `analysis/deep/<slug>.md`。",
        "> 用法：面对新比赛先按 主题/指标/标签 找 3–5 个类比场次，提取机制而不是照抄参数。",
        "",
    ]
    for theme, items in sorted(by_theme.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"## {theme}（{len(items)} 场）")
        lines.append("")
        for r in items:
            lesson = r["one_line"] or r["title"]
            lines.append(
                f"- `{r['slug']}`（{r['category']}｜{r['metric'] or '—'}｜{r['tags']}）：{lesson} "
                f"[深读原文]({r['deep_doc_url']})"
            )
        lines.append("")
    (SKILL / "references" / "case-index.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"case_index.csv: {len(rows)} rows -> {out_csv}")
    print(f"case-index.md -> {SKILL / 'references' / 'case-index.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
