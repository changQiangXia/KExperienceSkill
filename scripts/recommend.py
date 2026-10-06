#!/usr/bin/env python3
"""统一入口路由：给一张比赛卡，返回该读的文档 / 类比案例 / 技法 / GM 决策项 / 脚本。

底层是纯 Python BM25（无第三方依赖），索引四类资产：
  assets/case_cards.jsonl            → 案例（264）
  assets/technique_case_map.csv      → 技法（71）
  assets/gm_claims_snapshot.csv      → GM 断言（364）
  references/**/*.md（按小节切分）   → 文档段落
另有静态脚本目录，按任务关键词匹配。

用法：
  python scripts/recommend.py --task "tabular regression" --metric MedAE --tags "tabular,synthetic" \
      --notes "1500 teams, 小数据, 公榜 20%" [--theme tabular] [--json]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = ROOT / "assets" / "case_cards.jsonl"
TECH = ROOT / "assets" / "technique_case_map.csv"
CLAIMS = ROOT / "assets" / "gm_claims_snapshot.csv"
REFS = [ROOT / "README.md", ROOT / "SKILL.md"] + sorted((ROOT / "references").rglob("*.md"))

SCRIPT_CATALOG = [
    ("python scripts/case_card.py --slug <slug>", "读单场完整案例卡（数字/裁决/失败学/外链）", "case 案例 card 单场"),
    ("python scripts/case_search.py --query <词> --deep", "按关键词/主题检索案例", "search 检索 案例"),
    ("python scripts/technique_lookup.py --technique <名>", "查技法的支持案例/反例/第一步/kill", "technique 技法"),
    ("python scripts/gm_claim_search.py --domain <d> --strict-units 2", "查 GM 复现断言", "gm 选手 断言 agent"),
    ("python scripts/recommend.py ...", "本脚本：比赛卡 → 路由", "router 路由"),
    ("python scripts/plan_builder.py --task <...> --metric <...>", "生成 Improvement Plan 骨架", "plan 计划 方案"),
    ("python scripts/plan_tracker.py init/judge", "预注册台账：假设/MDE/kill 判定", "tracker 实验 台账 预注册"),
    ("python scripts/experiment_harness.py --data <csv> --target <col>", "生成折文件/实验台账", "fold cv 切分 实验"),
    ("python scripts/oof_report.py --oof <csv> --target y --pred a --pred2 b", "OOF 指标 + bootstrap CI + 配对比较 + FDR", "oof 指标 置信 显著"),
    ("python scripts/lb_noise.py --metric auc --auc 0.95 --n-test 100000", "LB 噪声/名次反转/最小可检测提升", "lb 公榜 噪声 名次"),
    ("python scripts/agent_audit.py --oof <npy> --test <npy>", "agent 产物审计（8 门可机器化部分）", "agent 审计 泄漏 提交"),
    ("python scripts/submission_guard.py --submission <csv> --sample <csv>", "提交格式体检", "提交 格式 submission"),
    ("python scripts/doctor.py", "仓库门禁：引用/schema/脚本/生成器", "doctor 门禁 校验"),
    ("python tools/import_external_links.py", "导入外部题解索引（KStarter → skill）", "同步 外链 导入"),
]
THEME_DOMAIN = {"tabular": "表格/结构化", "cv": "视觉 CV", "nlp": "文本 NLP", "science": "科学研究",
                "sim-agent": "强化学习/博弈", "audio": "语音/音频"}
DEFAULT_SCRIPTS = ["case_card.py", "case_search.py", "technique_lookup.py", "gm_claim_search.py",
                   "plan_builder.py", "plan_tracker.py", "lb_noise.py"]
ALIASES = {
    "classification": ["分类", "classif", "binary", "multiclass"],
    "sentiment": ["情感", "文本分类"],
    "regression": ["回归", "regress", "rmse"],
    "segmentation": ["分割", "segment", "dice"],
    "detection": ["检测", "detect", "yolo", "bbox"],
    "forecast": ["预测", "时序", "time series", "forecast"],
    "recommendation": ["推荐", "排序", "ranking", "ndcg", "map@"],
    "transformer": ["注意力", "attention", "预训练", "微调", "llm"],
    "agent": ["智能体", "rl", "self-play", "自对弈"],
    "tabular": ["表格", "gbdt", "xgboost", "catboost"],
    "synthetic": ["合成", "生成器", "generator"],
    "leak": ["泄漏", "leakage", "对抗验证"],
}


def tokens(text: str) -> list[str]:
    text = (text or "").lower()
    out = re.findall(r"[a-z0-9_]+", text)
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(run) == 1:
            out.append(run)
        else:
            out += [run[i:i + 2] for i in range(len(run) - 1)]
    return out


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = docs
        self.lens = [len(d) for d in docs]
        self.avg = sum(self.lens) / max(len(docs), 1)
        self.tf = [Counter(d) for d in docs]
        df = Counter()
        for d in docs:
            df.update(set(d))
        n = max(len(docs), 1)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        out = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for t in query:
                if t not in tf:
                    continue
                f = tf[t]
                s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg))
            out.append(s)
        return out


def load_cases():
    rows = []
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        card = json.loads(line)
        text = " ".join([
            card.get("title", ""), card.get("one_line", ""), card.get("tags", ""),
            card.get("theme", ""), card.get("metric", ""),
            " ".join(k.get("claim", "") + " " + k.get("value", "") for k in card.get("key_numbers", [])[:6]),
            " ".join(v.get("heading", "") for v in card.get("verdicts", [])[:6]),
        ])
        rows.append({"slug": card["slug"], "title": card.get("title", ""), "theme": card.get("theme", ""),
                     "metric": card.get("metric", ""), "tags": card.get("tags", ""), "doc": text})
    return rows


def load_techniques():
    grouped: dict[str, dict] = {}
    for r in csv.DictReader(TECH.open(encoding="utf-8")):
        item = grouped.setdefault(r["technique"], {"technique": r["technique"], "support": [], "refute": [],
                                                    "example": [], "snippets": []})
        role = (r.get("role") or "support").strip()
        item[role if role in ("support", "refute", "example") else "support"].append(r.get("slug", ""))
        item["snippets"].append(r.get("snippet", ""))
    out = []
    for item in grouped.values():
        doc = " ".join([item["technique"], " ".join(item["snippets"]),
                        " ".join(item["support"] + item["refute"] + item["example"])])
        out.append({**item, "support": ",".join(item["support"]), "refute": ",".join(item["refute"]),
                    "example": ",".join(item["example"]), "doc": doc,
                    "prior": len(item["support"]) + len(item["example"])})
    return out


def load_claims():
    rows = []
    for r in csv.DictReader(CLAIMS.open(encoding="utf-8")):
        rows.append({
            "claim_id": r["claim_id"], "person": r["person"], "level": r["evidence_level"],
            "replication": r["replication"], "strict": r["strict_replication"], "domain": r["domain"],
            "tags": r["skill_tags"], "url": r["source_url"], "action": r["action"],
            "doc": " ".join([r["condition"], r["action"], r["mechanism"], r["result"], r["skill_tags"]]),
        })
    return rows


def load_doc_sections():
    rows = []
    for path in REFS:
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        current, buffer = "", []
        for line in lines:
            if line.startswith("## "):
                if current:
                    rows.append((path, current, " ".join(buffer)))
                current, buffer = line[3:].strip(), []
            elif line.startswith("#"):
                continue
            else:
                buffer.append(line)
        if current:
            rows.append((path, current, " ".join(buffer)))
    out = []
    for path, heading, body in rows:
        if any(k in heading for k in ("链接索引", "来源佐证", "出处")):
            continue
        out.append({"path": path.relative_to(ROOT).as_posix(), "heading": heading,
                    "doc": heading + " " + body[:1500]})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="比赛卡 → 经验路由")
    parser.add_argument("--task", default="", help="任务描述，如 'tabular regression'")
    parser.add_argument("--metric", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--theme", default="", choices=["", "tabular", "cv", "nlp", "science", "sim-agent", "audio", "other"])
    parser.add_argument("--exclude-slug", default="", help="留一法：排除该比赛的案例/技法/断言/文档小节（供 eval 用）")
    parser.add_argument("--top-cases", type=int, default=5)
    parser.add_argument("--top-docs", type=int, default=5)
    parser.add_argument("--top-techniques", type=int, default=5)
    parser.add_argument("--top-claims", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    query_text = " ".join([args.task, args.metric, args.tags, args.notes, args.theme])
    query = tokens(query_text)
    for key, words in ALIASES.items():
        if key in query_text.lower():
            for w in words:
                query += tokens(w)
    if not query:
        print("ERROR: 至少给 --task/--metric/--tags 之一", file=__import__("sys").stderr)
        return 1

    cases, techs, claims, docs = load_cases(), load_techniques(), load_claims(), load_doc_sections()
    if args.exclude_slug:
        ex = args.exclude_slug
        cases = [c for c in cases if c["slug"] != ex]
        kept = []
        for t in techs:
            members = {s.strip() for s in (t["support"] + "," + t["refute"] + "," + t["example"]).split(",") if s.strip()}
            if members == {ex}:
                continue
            kept.append(t)
        techs = kept
        claims = [c for c in claims if not c["claim_id"].startswith(ex + "#")]
        docs = [d for d in docs if ex not in d["heading"]]
    cs = BM25([tokens(c["doc"]) for c in cases]).scores(query)
    ts = BM25([tokens(t["doc"]) for t in techs]).scores(query)
    gs = BM25([tokens(c["doc"]) for c in claims]).scores(query)
    ds = BM25([tokens(d["doc"]) for d in docs]).scores(query)
    tagset = {t.strip().lower() for t in args.tags.split(",") if t.strip()}

    def case_boost(c):
        b = 0.0
        if args.theme and c["theme"] == args.theme:
            b += 2.0
        if args.metric and args.metric.lower() in c["metric"].lower():
            b += 1.5
        b += 1.0 * len(tagset & {t.strip().lower() for t in c["tags"].split(",")})
        return b

    ranked_cases = sorted(((cs[i] + case_boost(c), c) for i, c in enumerate(cases)), key=lambda x: -x[0])
    ranked_cases = [x for x in ranked_cases if x[0] > 0][: args.top_cases]

    top_case_slugs = {c["slug"] for _, c in ranked_cases}

    def tech_boost(t):
        return 1.0 if top_case_slugs & {s.strip() for s in t["support"].split(",") if s.strip()} else 0.0

    ranked_tech = sorted(
        ((ts[i] + 0.6 * math.log1p(t.get("prior", 0)) + tech_boost(t), t) for i, t in enumerate(techs)),
        key=lambda x: -x[0],
    )
    ranked_tech = [x for x in ranked_tech if x[0] > 0][: args.top_techniques]

    def claim_boost(c):
        b = 0.0
        if args.theme and THEME_DOMAIN.get(args.theme, "") in c["domain"]:
            b += 1.0
        b += 0.5 * len(tagset & {t.strip().lower() for t in c["tags"].split(";")})
        if c["level"] == "A":
            b += 0.5
        if int(c["strict"] or 0) >= 2:
            b += 0.5
        return b

    ranked_claims = sorted(((gs[i] + claim_boost(c), c) for i, c in enumerate(claims)), key=lambda x: -x[0])
    ranked_claims = [x for x in ranked_claims if x[0] > 0][: args.top_claims]

    best_by_path: dict[str, list] = {}
    for i, d in enumerate(docs):
        if ds[i] <= 0:
            continue
        best_by_path.setdefault(d["path"], []).append((ds[i], d))
    doc_pool = []
    for path, items in best_by_path.items():
        items.sort(key=lambda x: -x[0])
        doc_pool.append(items[0])
    doc_pool.sort(key=lambda x: -x[0])
    ranked_docs = doc_pool[: args.top_docs]

    script_q = tokens(query_text)
    ranked_scripts = []
    for cmd, purpose, keywords in SCRIPT_CATALOG:
        hay = (keywords + " " + purpose).lower()
        s = sum(1 for t in script_q if len(t) > 1 and t in hay)
        if s:
            ranked_scripts.append((s, cmd, purpose))
    ranked_scripts.sort(key=lambda x: -x[0])
    ranked_scripts = ranked_scripts[:5]
    if not ranked_scripts:
        ranked_scripts = [(0, cmd, purpose) for cmd, purpose, _ in SCRIPT_CATALOG
                          if any(name in cmd for name in DEFAULT_SCRIPTS)][:5]

    if args.json:
        print(json.dumps({
            "query": {"task": args.task, "metric": args.metric, "tags": args.tags, "theme": args.theme},
            "docs": [{"path": d["path"], "heading": d["heading"], "score": round(s, 3)} for s, d in ranked_docs],
            "cases": [{"slug": c["slug"], "title": c["title"], "theme": c["theme"], "score": round(s, 3)} for s, c in ranked_cases],
            "techniques": [{"technique": t["technique"], "score": round(s, 3)} for s, t in ranked_tech],
            "gm_claims": [{"claim_id": c["claim_id"], "person": c["person"], "level": c["level"],
                            "strict": c["strict"], "action": c["action"][:120], "url": c["url"]} for s, c in ranked_claims],
            "scripts": [{"cmd": cmd, "purpose": p} for _, cmd, p in ranked_scripts],
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"# 路由：{args.task or '(未填 task)'}｜{args.metric or '—'}｜tags={args.tags or '—'}｜theme={args.theme or '—'}\n")
    print("## 先读（文档小节）")
    for i, (s, d) in enumerate(ranked_docs, 1):
        print(f"{i}. `{d['path']}` › {d['heading']}  [{s:.1f}]")
    print("\n## 类比案例")
    for i, (s, c) in enumerate(ranked_cases, 1):
        print(f"{i}. `{c['slug']}` — {c['title']}（{c['theme']}/{c['metric']}）")
        print(f"   → python scripts/case_card.py --slug {c['slug']}")
    print("\n## 技法候选")
    for i, (s, t) in enumerate(ranked_tech, 1):
        print(f"{i}. {t['technique']}（支持 {t['support'][:60]}）→ python scripts/technique_lookup.py --technique {t['technique']}")
    print("\n## GM 决策项（严格复现优先）")
    for i, (s, c) in enumerate(ranked_claims, 1):
        print(f"{i}. [{c['level']}｜严{c['strict']}] @{c['person']}｜{c['action'][:70]}…")
        print(f"   {c['url']}")
    print("\n## 脚本")
    for i, (s, cmd, purpose) in enumerate(ranked_scripts, 1):
        print(f"{i}. `{cmd}` — {purpose}")
    print("\n## 起步三步")
    print("1. 读 top1 案例卡的数字与裁决（case_card），确认结构可比性；")
    print("2. 对 top1 技法做第一步实验（technique_lookup），先过同折对照；")
    print("3. 用 plan_builder/plan_tracker 建预注册假设（含 MDE 与 kill），再开工。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
