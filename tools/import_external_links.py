#!/usr/bin/env python3
"""把 KStarter 的外部题解索引（kaggle-solutions）导入本 skill。

输入：<kstarter-root>/analysis/external/kaggle_solutions_index.csv（由 KStarter
      `scripts/build_external_index.py` 生成）
输出：
  assets/external_solution_links.csv  外链资产（全量 4768 条：排名/类型/是否已在本 skill 出现/旗标）
  references/champion-solutions.md    冠军方案索引（覆盖场按主题 + 历史精选 + 代码/Notebook 参考）

用法：
  python tools/import_external_links.py --kstarter-root /root/autodl-tmp/kaggle
"""

from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import time
from urllib.parse import urlparse

SKILL = pathlib.Path(__file__).resolve().parent.parent
# 扫描"已收录"时排除的派生文件/片段：external 资产、冠军索引、案例卡；案例书里的
# "### 外部题解（kaggle-solutions）"小节也整段跳过。否则导入结果会自我强化，把新链接误判成已收录。
DERIVED_FILES = {
    "assets/external_solution_links.csv",
    "references/champion-solutions.md",
    "assets/case_cards.jsonl",
}
EXTERNAL_SECTION = "### 外部题解（kaggle-solutions）"
SCAN_TOP = ["README.md", "SKILL.md"]
SCAN_DIRS = ["references", "scripts", "tools", "agents", "assets"]
URL_RE = re.compile(r"https://www\.kaggle\.com/[A-Za-z0-9/_.?=&%#-]*")
HEADING_RE = re.compile(r"^#{2,4} ")
FIELDS = [
    "slug", "in_case_index", "theme", "year", "category", "rank", "link_kind",
    "url", "domain", "flag", "already_in_skill",
]


def canonical(url: str) -> str:
    url = (url or "").strip()
    parsed = urlparse(url)
    path = re.sub(r"^/c/", "/competitions/", parsed.path.rstrip("/"))
    return f"{parsed.netloc.lower()}{path}".lower()


def rank_num(rank: str) -> int:
    match = re.search(r"\d+", rank or "")
    return int(match.group(0)) if match else 10**6


def scan_skill_urls() -> set[str]:
    """扫描本仓库策展文档里已出现的 Kaggle URL（排除派生文件与外链小节，防反馈环）。"""
    files = [SKILL / name for name in SCAN_TOP]
    for folder in SCAN_DIRS:
        files += [p for p in (SKILL / folder).rglob("*") if p.is_file()]
    urls: set[str] = set()
    for path in files:
        rel = path.relative_to(SKILL).as_posix()
        if rel in DERIVED_FILES or path.suffix not in {".md", ".csv", ".json", ".py", ".yaml", ".yml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".md" and EXTERNAL_SECTION in text:
            kept, skip = [], False
            for line in text.splitlines():
                if line.strip() == EXTERNAL_SECTION:
                    skip = True
                    continue
                if skip and HEADING_RE.match(line):
                    skip = False
                if not skip:
                    kept.append(line)
            text = "\n".join(kept)
        urls |= {canonical(u) for u in URL_RE.findall(text)}
    return urls


def usable(row: dict) -> bool:
    return row["flag"] != "legacy_blog" and "kaggle.com" in row["domain"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kstarter-root", default="/root/autodl-tmp/kaggle")
    parser.add_argument("--historical-limit", type=int, default=80, help="历史精选最多列多少场")
    args = parser.parse_args()

    root = pathlib.Path(args.kstarter_root)
    src = root / "analysis/external/kaggle_solutions_index.csv"
    if not src.exists():
        print(f"ERROR: 缺少 {src}；先在 KStarter 运行 scripts/build_external_index.py")
        return 1
    index = list(csv.DictReader(src.open(encoding="utf-8")))
    cases = {
        r["slug"]: r
        for r in csv.DictReader((SKILL / "assets/case_index.csv").open(encoding="utf-8"))
    }
    existing = scan_skill_urls()

    rows = []
    dedup: dict[tuple[str, str], dict] = {}
    for r in index:
        slug = r["comp_slug"]
        row = {
            "slug": slug,
            "in_case_index": "1" if slug in cases else "0",
            "theme": cases.get(slug, {}).get("theme", ""),
            "year": r["year"],
            "category": r["category"],
            "rank": r["rank"],
            "link_kind": r["link_kind"],
            "url": r["url"],
            "domain": r["link_domain"],
            "flag": r["flag"],
            "already_in_skill": "1" if canonical(r["url"]) in existing else "0",
        }
        key = (slug, canonical(r["url"]))
        old = dedup.get(key)
        if old is None or (rank_num(row["rank"]), row["link_kind"] != "description") < (
            rank_num(old["rank"]), old["link_kind"] != "description"
        ):
            dedup[key] = row
    dropped = len(index) - len(dedup)
    rows = list(dedup.values())
    rows.sort(key=lambda r: (-int(r["in_case_index"]), r["theme"], r["slug"], rank_num(r["rank"])))

    asset = SKILL / "assets/external_solution_links.csv"
    with asset.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    by_slug: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_slug[r["slug"]].append(r)
    covered = [s for s in by_slug if s in cases]
    new_covered = [r for r in rows if r["in_case_index"] == "1" and r["already_in_skill"] == "0" and usable(r)]
    champion = {s: [r for r in by_slug[s] if rank_num(r["rank"]) == 1 and usable(r)] for s in by_slug}

    themes = collections.defaultdict(list)
    for slug in covered:
        if champion.get(slug):
            themes[cases[slug]["theme"]].append(slug)
    for theme in themes:
        themes[theme].sort()

    hist = [
        s for s in by_slug
        if s not in cases and champion.get(s) and len(by_slug[s]) >= 5
    ]
    hist.sort(key=lambda s: (-len(by_slug[s]), s))
    hist = hist[: args.historical_limit]

    code_links = collections.defaultdict(list)
    for slug in covered:
        for r in by_slug[slug]:
            if r["link_kind"] == "code" and usable(r):
                code_links[cases[slug]["theme"]].append((slug, r))

    lines = [
        "# 冠军方案索引（外部题解层）",
        "",
        f"> 来源：[faridrashidi/kaggle-solutions](https://github.com/faridrashidi/kaggle-solutions)"
        "（MIT License, Farid Rashidi）；数据经 KStarter `analysis/external/` 索引导出，"
        f"{time.strftime('%Y-%m-%d')} 快照。",
        f"> 覆盖场冠军链接共 {sum(1 for s in covered if champion.get(s))} 场；"
        f"全部链接（含 rank 2–10、代码/Notebook）见 `assets/external_solution_links.csv`。",
        "> 用法：先读冠军方案定方向，再回 `case-books/<主题>.md` 对照机制与数字；"
        "`已收录` 指该链接此前已出现在本 skill 文档中。",
        "",
    ]
    for theme in sorted(themes):
        slugs = themes[theme]
        lines += [f"## {theme}（{len(slugs)} 场覆盖场内冠军方案）", ""]
        for slug in slugs:
            card = cases[slug]
            for r in champion[slug]:
                mark = "" if r["already_in_skill"] == "0" else "｜已收录"
                lines.append(f"- [{card['title']}]({r['url']})｜rank 1{mark}")
        lines.append("")

    lines += [f"## 历史精选（不在 264 覆盖内，按外部链接数取前 {len(hist)} 场）", ""]
    title_of = {r["comp_slug"]: r["comp_title"] for r in index}
    for slug in hist:
        r = champion[slug][0]
        lines.append(f"- {title_of.get(slug, slug)}（{r['year']}｜{len(by_slug[slug])} 条）｜[rank 1 方案]({r['url']})")
    lines += [
        "",
        "## 代码 / Notebook 参考（覆盖场内，每主题最多 8 条）",
        "",
        "> 公开 notebook 是执行层素材；用前先核对规则与泄漏风险（见 `public-intel-differential.md`）。",
        "",
    ]
    for theme in sorted(code_links):
        lines.append(f"### {theme}")
        lines.append("")
        for slug, r in code_links[theme][:8]:
            lines.append(f"- [{slug}]({r['url']})｜rank {r['rank']}")
        lines.append("")

    (SKILL / "references/champion-solutions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"asset: {len(rows)} links -> assets/external_solution_links.csv")
    print(f"  dedup: dropped {dropped} duplicate (slug,url) rows")
    print(f"  covered comps {len(covered)} | new-to-skill usable {len(new_covered)}")
    print(f"champion: {sum(1 for s in covered if champion.get(s))} covered comps + {len(hist)} historical -> references/champion-solutions.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
