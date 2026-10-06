#!/usr/bin/env python3
"""仓库健康检查（一键门禁）。

检查项：
  1. 结构：SKILL/README/关键资产是否齐全
  2. 引用：README/SKILL/references/assets 里的路径与相对链接是否可解析（KStarter 外部路径 → WARN）
  3. Schema：case_index / case_cards / technique_map / gm_claims / external_links / people_manifest
  4. 脚本冒烟：所有 scripts/*.py --help + 只读功能调用
  5. 链接库存：统计 Kaggle 链接与 legacy 旗标（--online-sample N 可做在线抽样）
  6. provenance：assets/provenance.json 与 KStarter 实际 commit 对比（可选）
  7. 生成器幂等：重跑生成器，字节不一致即 FAIL 并自动还原（--generators）

用法：
  python scripts/doctor.py
  python scripts/doctor.py --kstarter-root /root/autodl-tmp/kaggle --generators
退出码：存在 FAIL 返回 1。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
RESULTS: list[tuple[str, str, str]] = []

INDEX_COLS = {"slug", "title", "theme", "category", "metric", "teams", "deadline", "tier", "tags",
              "one_line", "deep_doc", "notes_doc", "deep_doc_url", "notes_doc_url"}
CLAIM_COLS = {"claim_id", "person", "role", "domain", "stage", "action_class", "condition", "action",
              "mechanism", "result", "evidence_level", "replication", "strict_replication", "skill_tags",
              "flags", "source_url", "votes", "date"}
LINK_COLS = {"slug", "in_case_index", "theme", "year", "category", "rank", "link_kind", "url", "domain",
             "flag", "already_in_skill"}
THEMES = {"tabular", "cv", "nlp", "science", "sim-agent", "audio", "other"}


def check(level: str, area: str, message: str) -> None:
    RESULTS.append((level, area, message))
    print(f"[{level}] {area}: {message}")


def scan_doc_refs(path: pathlib.Path) -> list[tuple[int, str, str]]:
    """返回 (行号, 目标, 原始行) 列表。"""
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in re.finditer(r"`((?:references|assets|scripts|tools|agents)/[^`\s]+?\.(?:md|csv|json|jsonl|py|yaml|yml|txt))`", line):
            out.append((lineno, m.group(1), line))
        for m in re.finditer(r"\]\(([^)\s#]+\.(?:md|csv|json|py|yaml|yml))(#[\w\-]*)?\)", line):
            target = m.group(1)
            if target.startswith(("http://", "https://")):
                continue
            out.append((lineno, target, line))
    return out


def check_structure() -> None:
    required = [
        "SKILL.md", "README.md", "agents/openai.yaml",
        ".github/workflows/check.yml", "CHANGELOG.md", "THIRD_PARTY.md", "LICENSE", "assets/provenance.json",
        "assets/case_index.csv", "assets/case_cards.jsonl", "assets/technique_case_map.csv",
        "assets/gm_claims_snapshot.csv", "assets/external_solution_links.csv",
        "assets/agent_spec_template.md", "assets/agent_workflow_checklist.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    check("FAIL" if missing else "PASS", "structure", f"缺失 {missing}" if missing else f"{len(required)} 项齐全")
    if not (ROOT / "references/case-books").is_dir():
        check("FAIL", "structure", "缺少 references/case-books/")


def check_refs() -> None:
    files = [ROOT / "README.md", ROOT / "SKILL.md"]
    files += sorted((ROOT / "references").rglob("*.md"))
    files += sorted((ROOT / "assets").glob("*.md"))
    bad, external = [], []
    for path in files:
        if not path.exists():
            continue
        for lineno, target, line in scan_doc_refs(path):
            if "<" in target or "*" in target:
                continue
            base = ROOT if target.startswith(("references/", "assets/", "scripts/", "tools/", "agents/")) else path.parent
            if (base / target).exists():
                continue
            (external if "KStarter" in line else bad).append(f"{path.relative_to(ROOT)}:{lineno} -> {target}")
    check("FAIL" if bad else "PASS", "refs", f"{len(bad)} 条失效：" + "; ".join(bad[:3]) if bad else f"{len(files)} 个文档全部可解析")
    if external:
        check("WARN", "refs", f"{len(external)} 条指向 KStarter（外部，允许）：" + "; ".join(external[:2]))


def read_csv(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_schemas() -> None:
    # case_index
    rows = read_csv(ROOT / "assets/case_index.csv")
    cols = set(rows[0]) if rows else set()
    missing = INDEX_COLS - cols
    themes = {r["theme"] for r in rows}
    bad_theme = themes - THEMES
    slugs = [r["slug"] for r in rows]
    if missing or len(rows) < 260 or bad_theme or len(set(slugs)) != len(slugs):
        check("FAIL", "schema", f"case_index: rows={len(rows)} missing_cols={sorted(missing)} bad_theme={bad_theme}")
    else:
        check("PASS", "schema", f"case_index {len(rows)} 行 / {len(themes)} 主题")

    # case_cards
    cards, parse_errors = [], 0
    for line in (ROOT / "assets/case_cards.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            cards.append(json.loads(line))
        except json.JSONDecodeError:
            parse_errors += 1
    card_slugs = {c.get("slug") for c in cards}
    missing_slug = set(slugs) - card_slugs
    no_sources = sum(1 for c in cards if not c.get("sources"))
    if parse_errors or missing_slug:
        check("FAIL", "schema", f"case_cards: parse_errors={parse_errors} missing={len(missing_slug)}")
    else:
        check("PASS", "schema", f"case_cards {len(cards)} 张（无 sources {no_sources} 张）")

    # technique map
    tech = read_csv(ROOT / "assets/technique_case_map.csv")
    if len(tech) < 40 or "technique" not in (tech[0] if tech else {}):
        check("FAIL", "schema", f"technique_case_map rows={len(tech)}")
    else:
        check("PASS", "schema", f"technique_case_map {len(tech)} 技法")

    # gm claims
    claims = read_csv(ROOT / "assets/gm_claims_snapshot.csv")
    claim_cols = set(claims[0]) if claims else set()
    if not claims or (CLAIM_COLS - claim_cols):
        check("FAIL", "schema", f"gm_claims 缺列 {sorted(CLAIM_COLS - claim_cols)}")
    else:
        bad = [c["claim_id"] for c in claims if int(c["strict_replication"]) > int(c["replication"])]
        levels = {c["evidence_level"] for c in claims}
        check("FAIL" if bad or levels - {"A", "B"} else "PASS", "schema",
              f"gm_claims {len(claims)} 条 / levels={sorted(levels)}" + (f" / strict>broad {bad[:2]}" if bad else ""))
    manifest = json.loads((ROOT / "assets/people_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("snapshot_claims") != len(claims):
        check("FAIL", "schema", f"people_manifest snapshot_claims={manifest.get('snapshot_claims')} != csv {len(claims)}")
    else:
        check("PASS", "schema", f"people_manifest 与快照一致（{len(claims)}）")

    # external links
    links = read_csv(ROOT / "assets/external_solution_links.csv")
    link_cols = set(links[0]) if links else set()
    empty = sum(1 for r in links if not r.get("url", "").strip())
    if not links or (LINK_COLS - link_cols) or empty:
        check("FAIL", "schema", f"external_links rows={len(links)} missing={sorted(LINK_COLS - link_cols)} empty={empty}")
    else:
        check("PASS", "schema", f"external_links {len(links)} 条")

    # eval 结果（生成物，缺失给 WARN）
    eval_path = ROOT / "assets/skill_eval_latest.json"
    if not eval_path.exists():
        check("WARN", "schema", "缺少 assets/skill_eval_latest.json（运行 scripts/skill_eval.py 生成）")
    else:
        ev = json.loads(eval_path.read_text(encoding="utf-8"))
        need = {"n_cases", "strict_recall@5", "strict_recall@10", "theme_hit_rate", "details"}
        check("FAIL" if need - set(ev) else "PASS", "schema",
              f"skill_eval n={ev.get('n_cases')} strict@5={ev.get('strict_recall@5')} "
              f"strict@10={ev.get('strict_recall@10')}")


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return proc.returncode, (proc.stdout + proc.stderr)[-400:]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def check_scripts() -> None:
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    failed = []
    for script in scripts:
        code, out = run([PY, str(script), "--help"], timeout=30)
        if code != 0:
            failed.append(f"{script.name}: {out.strip().splitlines()[-1] if out.strip() else code}")
    check("FAIL" if failed else "PASS", "scripts", f"{len(scripts)} 个脚本 --help 通过" if not failed else "; ".join(failed[:3]))
    # 只读功能冒烟
    index = read_csv(ROOT / "assets/case_index.csv")
    slug = index[0]["slug"] if index else ""
    smoke = [
        ([PY, "scripts/case_card.py", "--slug", slug], f"case_card {slug}"),
        ([PY, "scripts/gm_claim_search.py", "--limit", "1"], "gm_claim_search"),
        ([PY, "scripts/technique_lookup.py", "--list"], "technique_lookup --list"),
        ([PY, "scripts/recommend.py", "--task", "tabular regression", "--json"], "recommend --json"),
    ]
    for cmd, name in smoke:
        code, out = run(cmd, timeout=60)
        if code != 0:
            check("FAIL", "scripts", f"{name} 失败：{out.strip()[-160:]}")
        else:
            check("PASS", "scripts", name)


def check_link_inventory(online_sample: int) -> None:
    ref_links, seen = 0, set()
    for path in sorted((ROOT / "references").rglob("*.md")):
        for url in re.findall(r"https://www\.kaggle\.com/[A-Za-z0-9/_.?=&%#-]+", path.read_text(encoding="utf-8")):
            if url not in seen:
                seen.add(url)
                ref_links += 1
    links = read_csv(ROOT / "assets/external_solution_links.csv")
    legacy = sum(1 for r in links if r.get("flag") == "legacy_blog")
    check("PASS", "links", f"references 去重 Kaggle 链接 {ref_links} 条；外链资产 {len(links)} 条（legacy_blog {legacy}）")
    if online_sample > 0:
        pool = [r["url"] for r in links if not r.get("flag") and "kaggle.com" in r.get("domain", "")]
        sample = pool[:online_sample]
        bad = []
        for url in sample:
            try:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "doctor/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status >= 400:
                        bad.append((url, resp.status))
            except Exception as exc:  # noqa: BLE001
                bad.append((url, str(exc)[:60]))
        check("FAIL" if bad else "PASS", "links", f"在线抽样 {len(sample)} 条，失败 {len(bad)}" + (f"：{bad[:2]}" if bad else ""))


def check_provenance(kstarter: pathlib.Path | None) -> None:
    path = ROOT / "assets/provenance.json"
    if not path.exists():
        check("WARN", "provenance", "缺少 assets/provenance.json（P2 待补）")
        return
    prov = json.loads(path.read_text(encoding="utf-8"))
    k_commit = prov.get("sources", {}).get("kstarter", {}).get("commit", "")
    if kstarter and (kstarter / ".git").exists():
        code, out = run(["git", "-C", str(kstarter), "rev-parse", "HEAD"])
        head = out.strip() if code == 0 else ""
        if head and k_commit and not head.startswith(k_commit[:12]):
            check("FAIL", "provenance", f"provenance kstarter={k_commit[:12]} != 实际 {head[:12]}")
        else:
            check("PASS", "provenance", f"kstarter commit 一致（{k_commit[:12]}）")
    else:
        check("PASS", "provenance", f"provenance 可解析（kstarter={k_commit[:12] or 'n/a'}）")


GEN_JOBS = [
    ("tools/build_case_index.py", ["--kstarter-root"], ["assets/case_index.csv", "references/case-index.md"]),
    ("tools/build_case_cards.py", ["--kstarter-root"], ["assets/case_cards.jsonl"]),
    ("tools/build_case_books.py", ["--kstarter-root"], ["references/case-books"]),
    ("tools/build_technique_map.py", [], ["assets/technique_case_map.csv"]),
    ("tools/sync_people_layer.py", ["--kstarter"], ["assets/gm_claims_snapshot.csv", "assets/people_manifest.json",
                                                     "references/people-routing.md", "references/people-evidence.md",
                                                     "references/people-tensions.md"]),
    ("tools/import_external_links.py", ["--kstarter-root"], ["assets/external_solution_links.csv",
                                                             "references/champion-solutions.md"]),
]


def snapshot(paths: list[pathlib.Path]) -> dict[str, bytes]:
    data = {}
    for path in paths:
        if path.is_dir():
            for item in sorted(path.rglob("*")):
                if item.is_file():
                    data[str(item.relative_to(ROOT))] = item.read_bytes()
        elif path.is_file():
            data[str(path.relative_to(ROOT))] = path.read_bytes()
    return data


def check_generators(kstarter: pathlib.Path | None) -> None:
    if not kstarter or not (kstarter / "analysis/deep").is_dir():
        check("WARN", "generators", "KStarter 不可用，跳过幂等检查")
        return
    for script, arg_flags, artifacts in GEN_JOBS:
        paths = [ROOT / a for a in artifacts]
        committed = snapshot(paths)
        args = [PY, script]
        for flag in arg_flags:
            args += [flag, str(kstarter)]
        code, out = run(args, timeout=600)
        if code != 0:
            for key, data in committed.items():
                (ROOT / key).write_bytes(data)
            check("FAIL", "generators", f"{script} 退出码 {code}：{out.strip()[-160:]}")
            continue
        first = snapshot(paths)
        code, out = run(args, timeout=600)  # 第二次运行验确定性
        second = snapshot(paths)
        nondet = sorted(k for k in set(first) | set(second) if first.get(k) != second.get(k))
        stale = sorted(k for k in set(committed) | set(first) if committed.get(k) != first.get(k))
        if code != 0 or nondet:
            for key, data in committed.items():
                (ROOT / key).write_bytes(data)
            check("FAIL", "generators", f"{script} 非确定性（已还原）：{nondet[:3] or out.strip()[-120:]}")
        elif stale:
            check("FAIL", "generators", f"{script} 产物过期（上游已更新，已保留新产物待提交）：{stale[:3]}")
        else:
            check("PASS", "generators", f"{script} 确定性 + 与上游同步（{len(committed)} 个产物）")


def main() -> int:
    parser = argparse.ArgumentParser(description="KExperienceSkill 仓库健康检查")
    parser.add_argument("--kstarter-root", default="/root/autodl-tmp/kaggle")
    parser.add_argument("--generators", action="store_true", help="重跑生成器做幂等检查（会临时改写产物，异常时自动还原）")
    parser.add_argument("--online-sample", type=int, default=0, help="在线抽检外链数量（默认 0=离线）")
    args = parser.parse_args()
    kstarter = pathlib.Path(args.kstarter_root) if args.kstarter_root else None

    check_structure()
    check_refs()
    check_schemas()
    check_scripts()
    check_link_inventory(args.online_sample)
    check_provenance(kstarter)
    if args.generators:
        check_generators(kstarter)

    fails = sum(1 for lv, _, _ in RESULTS if lv == "FAIL")
    warns = sum(1 for lv, _, _ in RESULTS if lv == "WARN")
    print(f"\nsummary: {len(RESULTS) - fails - warns} PASS / {warns} WARN / {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
