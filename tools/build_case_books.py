#!/usr/bin/env python3
"""从 KStarter 深读文档生成按主题分册的"案例书"（每场一份结构化深讲解）。

输出：references/case-books/<theme>.md
每场包含：元信息 / 一句话 / 材料基础 / 关键数字（全表）/ 逐方案对照矩阵 /
共识分歧与裁决（全文）/ 证据分级（全表）/ 悬案与失败（全文）/ 图证（文本指针）/ 出处。

用法：
  python tools/build_case_books.py --kstarter-root /root/autodl-tmp/kaggle
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parent.parent
HEADING = re.compile(r"^(#{1,4})\s+(.*)$")

ORDER = ["tabular", "cv", "nlp", "science", "sim-agent", "audio", "other"]


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current, buffer = "", []
    for line in lines:
        m = HEADING.match(line.strip())
        if m:
            if buffer or current:
                sections.append((current, buffer))
            current, buffer = m.group(2), []
        else:
            buffer.append(line)
    if buffer or current:
        sections.append((current, buffer))
    return sections


def clean_block(body: list[str]) -> str:
    text = "\n".join(body).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def parse_case(root: pathlib.Path, slug: str, meta: dict) -> str:
    path = root / "analysis" / "deep" / f"{slug}.md"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    sections = split_sections(lines)

    title = slug
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    material = next((l.strip("> ").strip() for l in lines if "材料基础" in l), "")

    one_line = ""
    key_numbers: list[str] = []
    matrices: list[tuple[str, str]] = []
    verdicts: list[tuple[str, str]] = []
    evidence: list[tuple[str, str]] = []
    failures: list[tuple[str, str]] = []
    figures: list[str] = []
    sources: list[str] = []

    for heading, body in sections:
        block = clean_block(body)
        if "一句话重述" in heading:
            one_line = "\n".join(
                l.strip() for l in body if l.strip() and not l.strip().startswith(("#", "|"))
            ).strip()
        if "数字" in heading and "|" in block:
            table_lines = [l for l in body if l.strip().startswith("|")]
            if table_lines:
                key_numbers.append("\n".join(table_lines))
        if "对照矩阵" in heading and block:
            matrices.append((heading, block))
        if re.search(r"共识|分歧|事件|裁决", heading) and block:
            verdicts.append((heading, block))
        if "证据分级" in heading and block:
            evidence.append(block)
        if re.search(r"悬案|缺口|失败", heading) and block:
            failures.append((heading, block))
        if re.search(r"图表证据|图证", heading):
            for para in block.split("\n\n"):
                if "![ " in para or para.strip().startswith("!["):
                    alt = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", para)
                    if alt:
                        figures.append(f"- {alt.group(2)} — {alt.group(1)}")
        if heading in ("出处", "出处（主题 id）") or heading.startswith("出处"):
            for l in body:
                if l.strip().startswith("-") or "https://" in l:
                    sources.append(l.strip())

    out: list[str] = []
    out.append(f"## {slug} — {title}")
    out.append("")
    out.append(
        f"> 主题 {meta.get('theme','')} ｜ 类别 {meta.get('category','')} ｜ 指标 {meta.get('metric','')} "
        f"｜ 队伍 {meta.get('teams','')} ｜ 截止 {meta.get('deadline','')} ｜ Tier {meta.get('tier','')} ｜ 标签 {meta.get('tags','')}"
    )
    if material:
        out.append(f"> {material}")
    out.append("")
    if one_line:
        out.append("### 一句话重述")
        out.append(one_line)
        out.append("")
    if key_numbers:
        out.append("### 关键数字（数字账）")
        for block in key_numbers:
            out.append(block)
            out.append("")
    if matrices:
        out.append("### 逐方案对照矩阵")
        for heading, block in matrices:
            out.append(f"**{heading}**")
            out.append(block)
            out.append("")
    if verdicts:
        out.append("### 共识 / 分歧 / 裁决")
        for heading, block in verdicts:
            out.append(f"**{heading}**")
            out.append(block)
            out.append("")
    if evidence:
        out.append("### 证据分级")
        for block in evidence:
            out.append(block)
            out.append("")
    if failures:
        out.append("### 悬案与失败学")
        for heading, block in failures:
            out.append(f"**{heading}**")
            out.append(block)
            out.append("")
    if figures:
        out.append("### 图证（KStarter 仓库内路径）")
        out.extend(figures)
        out.append("")
    if sources:
        out.append("### 出处")
        out.extend(dict.fromkeys(sources))
        out.append("")
    out.append("---")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kstarter-root", default="/root/autodl-tmp/kaggle")
    args = parser.parse_args()
    root = pathlib.Path(args.kstarter_root)
    index_path = SKILL / "assets" / "case_index.csv"
    index = list(csv.DictReader(index_path.open(encoding="utf-8")))

    by_theme: dict[str, list[dict]] = {}
    for row in index:
        theme = row["theme"] or "other"
        by_theme.setdefault(theme, []).append(row)

    outdir = SKILL / "references" / "case-books"
    outdir.mkdir(parents=True, exist_ok=True)
    total = 0
    for theme in ORDER + sorted(set(by_theme) - set(ORDER)):
        items = by_theme.get(theme)
        if not items:
            continue
        parts = [
            f"# 案例书：{theme}（{len(items)} 场）",
            "",
            "> 由 KStarter 深读文档生成：每场含一句话重述、全量数字账、逐方案对照矩阵、共识/分歧与裁决全文、证据分级、悬案与失败学、图证路径与出处。",
            "> 用途：为新比赛找结构类比时，先读本册，再回 KStarter 深读原文核对。",
            "",
        ]
        for row in sorted(items, key=lambda r: r["slug"]):
            parts.append(parse_case(root, row["slug"], row))
        (outdir / f"{theme}.md").write_text("\n".join(parts), encoding="utf-8")
        total += len(items)
        print(f"{theme}: {len(items)} cases")
    print(f"total {total} cases -> {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
