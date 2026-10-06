#!/usr/bin/env python3
"""回顾式技能自评：用"开赛时可见的元数据"问路由器，看它能否找回该场的获胜技法。

方法（留一法，防泄漏）：
  1. 评测集：从 264 场里按主题分层取 N 场，且案例卡中至少含 2 个可识别技法；
  2. 查询串：slug（去连字符）+ metric + theme + category（不含标题里的解法描述与 tags）；
  3. 路由：调用 `scripts/recommend.py --json --exclude-slug <slug>`（排除该场自己的案例/技法/断言/文档小节）；
  4. 真值：该场案例卡文本中出现的技法名（来自 technique_case_map 的 71 个技法词典）；
  5. 指标：recall@5 / recall@10 / 命中主题率；对照随机基线 k/71 与"全局高频技法 top-k"基线。

用法：
  python scripts/skill_eval.py [--per-theme 4] [--min-recall 0.4] [--json]
输出：assets/skill_eval_latest.json（含每场明细与均值）。
退出码：给了 --min-recall 且均值低于阈值时返回 1（可当回归门禁）。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import sys
import time
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "assets" / "case_index.csv"
CARDS = ROOT / "assets" / "case_cards.jsonl"
TECH = ROOT / "assets" / "technique_case_map.csv"
OUT = ROOT / "assets" / "skill_eval_latest.json"
PY = sys.executable

# 真值补充：技法名在卡片文本里的常见别名（只用于"真值识别"，不影响路由）
ALIASES = {
    "伪标签": ["伪标", "pseudo", "self-train", "自训练"],
    "isotonic 校准": ["isotonic", "等距回归", "等渗", "CIR"],
    "知识蒸馏": ["蒸馏", "distill"],
    "阈值后处理": ["阈值", "threshold"],
    "实体分组 CV": ["GroupKFold", "分组切分", "group cv", "分组 CV"],
    "对抗验证": ["adversarial", "对抗"],
    "随机目标检验": ["随机目标", "打乱目标", "shuffle"],
    "时间切分/purge": ["时间切分", "purge", "时序验证"],
    "黑箱代理评分": ["代理评分", "surrogate", "代理模型"],
    "规则基线": ["启发式", "heuristic", "规则"],
    "课程学习+热启动": ["课程学习", "curriculum", "热启动"],
    "自对弈对手多样性": ["自对弈", "self-play"],
    "行动掩码/冲突取消": ["行动掩码", "action mask"],
    "爬山权重搜索": ["爬山", "hill climb", "hill-climb"],
    "秩融合": ["秩平均", "rank average", "rank blend"],
    "异质集成": ["异质集成", "diverse ensemble"],
    "提交对冲": ["对冲", "hedge", "提交组合"],
    "目标档位吸附": ["档位吸附", "档位"],
    "多目标拆合": ["多目标", "拆合"],
    "大候选+投票": ["大候选", "候选投票", "voting"],
    "工具集成推理(TIR)": ["工具集成", "TIR", "工具调用", "tool-integrated"],
    "LLM 引用核验": ["引用核验", "citation"],
    "评审闭环写作": ["评审闭环", "write-up 写作", "报告写作"],
    "频率/OOD 编码": ["频率编码", "OOD 编码"],
    "身份辅助任务": ["身份辅助", "辅助任务", "auxiliary task"],
    "高分辨率": ["高分辨率", "high resolution", "hires"],
    "IBN/直方图域适应": ["IBN", "直方图均衡"],
    "ArcFace/subcenter": ["ArcFace", "subcenter"],
    "域内预训练权重": ["域内预训练", "领域预训练"],
    "在线学习": ["在线学习", "online learning"],
    "分层学习率": ["分层学习率", "layer-wise", "LLRD"],
    "结构约束投影": ["结构约束", "投影后处理"],
    "未知类/OSD": ["OSD", "未知类", "open-set"],
    "密度分层阈值": ["密度分层", "分层阈值"],
    "Agent schema/预算": ["schema", "预算约束"],
}


def load_cards() -> dict[str, dict]:
    cards = {}
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            card = json.loads(line)
            cards[card["slug"]] = card
    return cards


def card_text(card: dict) -> str:
    parts = [card.get("one_line", ""), card.get("title", "")]
    for k in card.get("key_numbers", []):
        parts += [k.get("claim", ""), k.get("value", "")]
    for v in card.get("verdicts", []):
        parts += [v.get("heading", ""), v.get("text", "")]
    parts += card.get("failures", [])
    for e in card.get("evidence", []):
        parts += [e.get("assertion", ""), e.get("note", "")]
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="回顾式技能自评（留一法）")
    parser.add_argument("--per-theme", type=int, default=4)
    parser.add_argument("--min-recall", type=float, default=0.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cards = load_cards()
    techniques = sorted({r["technique"] for r in csv.DictReader(TECH.open(encoding="utf-8"))})
    rows = list(csv.DictReader(INDEX.open(encoding="utf-8")))

    # 真值来源一：技法×案例映射表（support/example）
    map_gt: dict[str, set[str]] = {}
    for r in csv.DictReader(TECH.open(encoding="utf-8")):
        if r["role"] in ("support", "example"):
            map_gt.setdefault(r["slug"], set()).add(r["technique"])

    # 真值来源二：案例卡文本（全名或别名命中）——宽松层，仅作辅助指标
    gt_loose: dict[str, list[str]] = {}
    for slug, card in cards.items():
        text = card_text(card)
        hits = {t for t in techniques if t in text}
        for t, aliases in ALIASES.items():
            if t in techniques and any(a.lower() in text.lower() for a in aliases):
                hits.add(t)
        hits |= map_gt.get(slug, set())
        if hits:
            gt_loose[slug] = sorted(hits)
    gt_strict: dict[str, list[str]] = {s: sorted(v) for s, v in map_gt.items()}
    gt = gt_loose

    # 分层选样：严格层（≥2 技法映射）全取；宽松层再补每主题上限内的场次
    by_theme: dict[str, list[str]] = {}
    for row in rows:
        slug = row["slug"]
        if slug in gt_loose and len(gt_loose[slug]) >= 2:
            by_theme.setdefault(row["theme"], []).append(slug)
    selected = [s for s in map_gt if len(map_gt[s]) >= 2]
    seen = set(selected)
    for theme in sorted(by_theme):
        picks = [s for s in sorted(by_theme[theme]) if s not in seen][: args.per_theme]
        selected += picks
        seen |= set(picks)

    meta = {r["slug"]: r for r in rows}

    details, theme_hits = [], 0
    for slug in selected:
        row = meta[slug]
        query = " ".join([slug.replace("-", " "), row["metric"], row["theme"], row["category"]])
        cmd = [PY, str(ROOT / "scripts" / "recommend.py"), "--task", query, "--json",
               "--exclude-slug", slug, "--top-techniques", "10", "--top-cases", "5"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if proc.returncode != 0:
            print(f"[WARN] {slug} 路由失败：{proc.stderr.strip()[:120]}", file=sys.stderr)
            continue
        routed = json.loads(proc.stdout)
        got = [t["technique"] for t in routed["techniques"]]
        def rec(truth, k):
            return len(set(got[:k]) & set(truth)) / len(truth) if truth else None
        strict5, strict10 = rec(gt_strict.get(slug, []), 5), rec(gt_strict.get(slug, []), 10)
        loose5, loose10 = rec(gt_loose.get(slug, []), 5), rec(gt_loose.get(slug, []), 10)
        top_theme = routed["cases"][0]["theme"] if routed["cases"] else ""
        if top_theme == row["theme"]:
            theme_hits += 1
        details.append({"slug": slug, "theme": row["theme"], "truth_strict": gt_strict.get(slug, []),
                        "truth_loose": gt_loose.get(slug, []), "routed_top10": got,
                        "strict_recall@5": strict5, "strict_recall@10": strict10,
                        "loose_recall@5": loose5, "loose_recall@10": loose10, "top_theme": top_theme})

    n = len(details)
    strict_rows = [d for d in details if d["strict_recall@10"] is not None]
    loose_rows = [d for d in details if d["loose_recall@10"] is not None]

    def mean(rows, key):
        vals = [d[key] for d in rows if d.get(key) is not None]
        return sum(vals) / max(len(vals), 1)

    def global_baseline(gtmap, rows, k=5):
        freq = Counter(t for d in rows for t in gtmap.get(d["slug"], []))
        top = [t for t, _ in freq.most_common(k)]
        vals = [len(set(top) & set(gtmap[d["slug"]])) / len(gtmap[d["slug"]]) for d in rows if gtmap.get(d["slug"])]
        return sum(vals) / max(len(vals), 1)

    mean5_strict = mean(strict_rows, "strict_recall@5")
    mean10_strict = mean(strict_rows, "strict_recall@10")
    mean5_loose = mean(loose_rows, "loose_recall@5")
    mean10_loose = mean(loose_rows, "loose_recall@10")
    random5 = 5 / max(len(techniques), 1)
    global5_strict = global_baseline(gt_strict, strict_rows)
    global5_loose = global_baseline(gt_loose, loose_rows)
    result = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "n_cases": n,
        "n_strict": len(strict_rows),
        "n_loose": len(loose_rows),
        "per_theme": args.per_theme,
        "strict_recall@5": round(mean5_strict, 4),
        "strict_recall@10": round(mean10_strict, 4),
        "loose_recall@5": round(mean5_loose, 4),
        "loose_recall@10": round(mean10_loose, 4),
        "theme_hit_rate": round(theme_hits / max(n, 1), 4),
        "baselines": {"random_recall@5": round(random5, 4),
                      "global_top5_strict": round(global5_strict, 4),
                      "global_top5_loose": round(global5_loose, 4)},
        "details": details,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# 技能自评（留一法，n={n}）")
        print(f"- 严格层（技法×案例映射，n={len(strict_rows)}）：recall@5 = {mean5_strict:.3f}，"
              f"recall@10 = {mean10_strict:.3f}（全局高频基线 {global5_strict:.3f}，随机 {random5:.3f}）")
        print(f"- 宽松层（含文本别名，n={len(loose_rows)}）：recall@5 = {mean5_loose:.3f}，"
              f"recall@10 = {mean10_loose:.3f}（全局高频基线 {global5_loose:.3f}）")
        print(f"- 主题命中率 = {theme_hits / max(n, 1):.3f}")
        worst = sorted(strict_rows, key=lambda d: d["strict_recall@10"])[:5]
        label = lambda d: f"{d['slug']}({d['strict_recall@10']:.2f})"
        if len(worst) < 5:
            worst += sorted(loose_rows, key=lambda d: d["loose_recall@10"])[: 5 - len(worst)]
            label = lambda d: (f"{d['slug']}({d['strict_recall@10']:.2f})" if d["strict_recall@10"] is not None
                               else f"{d['slug']}*({d['loose_recall@10']:.2f})")
        print("- 最差 5 场（* 为仅宽松层）：" + "、".join(label(d) for d in worst))
        print(f"- 明细 -> {OUT.relative_to(ROOT)}")

    if args.min_recall and mean10_strict < args.min_recall:
        print(f"FAIL: 严格层 recall@10 {mean10_strict:.3f} < 阈值 {args.min_recall}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
