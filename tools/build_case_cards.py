#!/usr/bin/env python3
"""从 KStarter 深读文档抽取"案例卡"：
assets/case_cards.jsonl —— 每场一条，含关键数字、共识/分歧裁决、失败学、证据分级。

用法：
  python tools/build_case_cards.py --kstarter-root /root/autodl-tmp/kaggle
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parent.parent
HEADING = re.compile(r"^(#{1,4})\s+(.*)$")


def parse_tables(lines: list[str]):
    block: list[list[str]] = []
    for line in lines + [""]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            block.append([c.strip() for c in stripped.strip("|").split("|")])
            continue
        if block:
            if len(block) >= 3:
                yield block[0], block[2:]
            block = []


def value_index(header: list[str]) -> int | None:
    for i, cell in enumerate(header):
        if cell in ("值", "数字", "变化", "数值", "数字/值", "增量", "指标值"):
            return i
    for i, cell in enumerate(header):
        if "关键数字" in cell:
            continue
        if "值" in cell or "数字" in cell:
            return i
    return None


def clean(text: str, limit: int = 300) -> str:
    text = re.sub(r"\*\*|`", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def parse_doc(path: pathlib.Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    sections: list[tuple[str, list[str]]] = []
    current, buffer = "", []
    for line in lines:
        m = HEADING.match(line.strip())
        if m:
            if buffer:
                sections.append((current, buffer))
            current, buffer = m.group(2), []
        else:
            buffer.append(line)
    if buffer:
        sections.append((current, buffer))

    key_numbers: list[dict[str, str]] = []
    verdicts: list[dict[str, str]] = []
    failures: list[str] = []
    evidence: list[dict[str, str]] = []

    for heading, body in sections:
        if "数字" in heading:
            for header, rows in parse_tables(body):
                v_idx = value_index(header)
                s_idx = next((i for i, c in enumerate(header) if "来源" in c or "备注" in c or "说明" in c), None)
                for row in rows:
                    if len(row) < 2:
                        continue
                    cells = (row + [""] * len(header))[: len(header)]
                    v = cells[v_idx] if v_idx is not None else cells[1]
                    c_idx = next((i for i in range(len(header)) if i not in {v_idx, s_idx}), 0)
                    claim = cells[c_idx]
                    source = cells[s_idx] if s_idx is not None else ""
                    if claim and re.search(r"\d", " ".join(cells)):
                        key_numbers.append({"claim": clean(claim, 160), "value": clean(v, 220), "source": clean(source, 80)})
        if re.search(r"共识|分歧|事件|裁决", heading):
            text = " ".join(t.strip() for t in body if t.strip() and not t.strip().startswith("|"))
            if text:
                verdicts.append({"heading": clean(heading, 80), "text": clean(text, 260)})
        if re.search(r"悬案|缺口|失败|无效|反例", heading):
            for line in body:
                s = line.strip()
                if s.startswith(("-", "*", "+")) and len(s) > 12:
                    failures.append(clean(s.lstrip("-*+ "), 220))
        if "证据分级" in heading:
            for header, rows in parse_tables(body):
                for row in rows:
                    if len(row) >= 2:
                        evidence.append(
                            {
                                "assertion": clean(row[0], 140),
                                "level": clean(row[1], 60),
                                "note": clean(row[2] if len(row) > 2 else "", 120),
                            }
                        )
    return {
        "key_numbers": key_numbers[:14],
        "verdicts": verdicts[:12],
        "failures": failures[:10],
        "evidence": evidence[:12],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kstarter-root", default="/root/autodl-tmp/kaggle")
    args = parser.parse_args()
    root = pathlib.Path(args.kstarter_root)
    index_path = SKILL / "assets" / "case_index.csv"
    if not index_path.exists():
        print("ERROR: 先运行 tools/build_case_index.py")
        return 1
    index = list(csv.DictReader(index_path.open(encoding="utf-8")))

    cards = []
    for row in index:
        deep = root / row["deep_doc"]
        parsed = parse_doc(deep) if deep.exists() else {"key_numbers": [], "verdicts": [], "failures": [], "evidence": []}
        cards.append({**row, **parsed})

    out = SKILL / "assets" / "case_cards.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for card in cards:
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")

    print(f"case_cards.jsonl: {len(cards)} cards -> {out}")
    print(
        "coverage: key_numbers=%d verdicts=%d failures=%d evidence=%d"
        % (
            sum(1 for c in cards if c["key_numbers"]),
            sum(1 for c in cards if c["verdicts"]),
            sum(1 for c in cards if c["failures"]),
            sum(1 for c in cards if c["evidence"]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
