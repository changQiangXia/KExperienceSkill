#!/usr/bin/env python3
"""从 KStarter 同步"前 50 选手"经验层到本 skill。

生成：
  assets/gm_claims_snapshot.csv   精简断言快照（A/B 且带 >=1 个具体技法标签；
                                  replication=广义复现，strict_replication=技法组合级复现）
  assets/people_manifest.json     来源与门禁 provenance
  references/people-routing.md    按比赛类型找人 + 该类型的复现决策项
  references/people-evidence.md   证据分级 / 复现度 / 口径规则
  references/people-tensions.md   12 组张力裁决（来自 KStarter）

用法：python tools/sync_people_layer.py [--kstarter /path/to/kaggle]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re
import subprocess
import time

SPECIFIC_TAGS = [
    "伪标签/自训练", "知识蒸馏", "时间/分组切分", "目标编码/类别特征", "分组聚合特征", "残差提升",
    "检索/RAG", "信号/频谱处理", "贝叶斯/概率模型", "度量学习/ArcFace", "数据增广", "合成/生成数据",
    "外部数据", "dtype/内存优化", "TTA", "后处理/校准", "集成权重选择", "混合精度/量化",
    "长序列/上下文", "规模/Scaling", "类别不平衡", "损失设计",
]
DOMAINS = ["视觉 CV", "文本 NLP", "表格/结构化", "时间序列", "语音/音频", "生物/医疗", "强化学习/博弈", "科学研究"]

TAG_KEYWORDS = {
    "伪标签/自训练": r"pseudo|伪标签|self.?train|noisy student|自训练",
    "知识蒸馏": r"distill|蒸馏|teacher|kd\b",
    "时间/分组切分": r"时间|time.?cv|group|滑窗|subject|prompt_id|按周|切分|holdout|按文件|按视频",
    "目标编码/类别特征": r"target encod|类别|categorical|分箱|bins|one.?hot|encoding|编码",
    "分组聚合特征": r"groupby|聚合|agg\b|统计特征|count encod",
    "残差提升": r"residual|残差|base_margin",
    "检索/RAG": r"\brag\b|retriev|faiss|cosine|embedding 检索|rerank|bi.?encoder|检索|相似度",
    "信号/频谱处理": r"spectrogram|mel|fft|filter|signal|eeg|audio|波形|频谱|频域",
    "贝叶斯/概率模型": r"bayes|posterior|prior|gaussian process|\bgp\b|hmm|particle|贝叶斯",
    "度量学习/ArcFace": r"arcface|metric learning|triplet",
    "数据增广": r"augment|增广|mixup|cutmix|flip|rotate|cutout|dropout|masking",
    "合成/生成数据": r"synthetic|合成|generat|t5|flux|扩散|生成数据|llm-generated",
    "外部数据": r"external|外部|原始数据|persuade|旧赛|去年|补充数据|额外数据",
    "dtype/内存优化": r"dtype|int8|int16|float16|float32|内存|memory|vram|压缩|quantile.?matrix|字节",
    "TTA": r"tta|test.?time|permute|翻转|多视图|hflip|rot90|reflection",
    "后处理/校准": r"post.?process|后处理|threshold|阈值|校准|calibrat|clip|nms|平滑|剪枝",
    "集成权重选择": r"weight|权重|voting|投票|median|中位数|hill|加权|平均",
    "混合精度/量化": r"fp16|bf16|int8|int4|量化|quant|awq|gptq|fp8|mixed precision",
    "长序列/上下文": r"max_len|max_length|context|2048|4096|5120|长文本|长序列|上下文|sequence length",
    "规模/Scaling": r"scal|更大|bigger|大模型|模型规模|参数量|bitter",
    "类别不平衡": r"imbalan|不平衡|class weight|resampl|downsampl|focal",
    "损失设计": r"loss|损失|dice|bce|cross.?entropy|focal|mae",
}

SNAPSHOT_FIELDS = [
    "claim_id", "person", "role", "domain", "stage", "action_class", "condition", "action", "mechanism",
    "result", "evidence_level", "replication", "strict_replication", "skill_tags", "flags", "source_url",
    "votes", "date",
]

# 严格复现度阈值：strict >= STRICT_MIN 视为"技法组合级复现"（同领域另一单位同时复现 >=2 个具体技法）
STRICT_MIN = 2


def kstarter_commit(path: pathlib.Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kstarter", default="/root/autodl-tmp/kaggle")
    parser.add_argument("--skill", default=str(pathlib.Path(__file__).resolve().parents[1]))
    parser.add_argument("--min-specific-tags", type=int, default=1,
                        help="进入快照所需的具体技法标签数（默认 1，即 A/B 中所有可检索断言）")
    parser.add_argument("--snapshot-date", default=time.strftime("%Y-%m-%d"))
    args = parser.parse_args()

    ks = pathlib.Path(args.kstarter)
    skill = pathlib.Path(args.skill)
    claims = {c["claim_id"]: c for c in csv.DictReader((ks / "people/claims/gm_claims.csv").open(encoding="utf-8"))}
    units = {
        t["claim_id"]: t["unit"] for t in csv.DictReader((ks / "people/claims/gm_claim_tags.csv").open(encoding="utf-8"))
    }

    # skill 侧标签：只用 condition/action/mechanism 匹配，避免全文字段交叉污染
    tags: dict[str, list[str]] = {}
    for cid, c in claims.items():
        blob = c["condition"] + " " + c["action"] + " " + c["mechanism"]
        tags[cid] = [t for t in SPECIFIC_TAGS if re.search(TAG_KEYWORDS[t], blob, re.I)]

    # 复现度：具体技法标签 × 同领域 × 证据单位（同队已合并）
    tag_domain_units: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for cid, c in claims.items():
        doms = set(c["domain"].split(";"))
        for t in tags.get(cid, []):
            if t in SPECIFIC_TAGS:
                for d in doms:
                    tag_domain_units[(t, d)].add(units[cid])

    def replication(c: dict) -> int:
        best = 0
        for t in tags.get(c["claim_id"], []):
            if t in SPECIFIC_TAGS:
                for d in c["domain"].split(";"):
                    best = max(best, len(tag_domain_units[(t, d)]))
        return best

    # 严格复现度：同一领域内，独立证据单位同时复现该断言的 >=2 个具体技法标签（含自身单位）
    def strict_in(c: dict, domain: str) -> int:
        ts = [t for t in tags.get(c["claim_id"], []) if t in SPECIFIC_TAGS]
        best = 0
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                shared = tag_domain_units[(ts[i], domain)] & tag_domain_units[(ts[j], domain)]
                best = max(best, len(shared))
        return best

    def strict_replication(c: dict) -> int:
        return max((strict_in(c, d) for d in c["domain"].split(";")), default=0)

    def strict_tag_in(c: dict, tag: str, domain: str) -> int:
        """路由用：只统计包含该标签的组合复现（保证 <= 该标签的单位数）。"""
        base = tag_domain_units[(tag, domain)]
        best = 0
        for t2 in tags.get(c["claim_id"], []):
            if t2 == tag:
                continue
            best = max(best, len(base & tag_domain_units[(t2, domain)]))
        return best

    def relevance(c: dict, tag: str) -> int:
        pattern = TAG_KEYWORDS[tag]
        score = 0
        if re.search(pattern, c["action_class"] + " " + c["stage"], re.I):
            score += 6
        score += 2 * len(re.findall(pattern, c["action"], re.I))
        score += len(re.findall(pattern, c["condition"], re.I))
        return score

    snapshot = [
        c for c in claims.values()
        if c["evidence_level"] in ("A", "B") and len(tags.get(c["claim_id"], [])) >= args.min_specific_tags
    ]
    snapshot.sort(
        key=lambda c: (-strict_replication(c), -replication(c), "A" != c["evidence_level"], -int(c["votes"]))
    )

    out_dir = skill / "assets"
    ref_dir = skill / "references"
    out_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "gm_claims_snapshot.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SNAPSHOT_FIELDS)
        writer.writeheader()
        for c in snapshot:
            row = {k: c.get(k, "") for k in SNAPSHOT_FIELDS}
            row["replication"] = replication(c)
            row["strict_replication"] = strict_replication(c)
            row["skill_tags"] = ";".join(tags.get(c["claim_id"], []))
            row["date"] = (c.get("date") or "")[:10]
            writer.writerow(row)

    # 路由文档
    lines = [
        "# 按比赛类型找人（前 50 选手经验层）",
        "",
        f"> 快照 {args.snapshot_date}，来源 KStarter `{kstarter_commit(ks)[:12]}`；"
        "复现度 = 具体技法标签 × 同领域 × 独立证据单位（同队合并）；"
        "标注 `严 N` 的是技法组合级复现（同领域另一单位同时复现 ≥2 个具体技法），优先采纳。",
        "> 完整断言与逐字引用见 KStarter `people/claims/gm_claims.csv`；领域 playbook 见 `analysis/people/playbooks/`。",
        "> 查询：`python scripts/gm_claim_search.py --domain cv --strict-units 2`。",
        "",
    ]
    manifest_domains = {}
    for domain in DOMAINS:
        pool = [c for c in snapshot if domain in c["domain"]]
        if not pool:
            continue
        anchors = collections.Counter(c["person"] for c in pool)
        tag_stats = []
        for t in SPECIFIC_TAGS:
            items = [c for c in pool if t in tags.get(c["claim_id"], [])]
            if not items:
                continue
            strict_best = max(strict_tag_in(c, t, domain) for c in items)
            tag_stats.append((t, len(tag_domain_units[(t, domain)]), strict_best, items))
        tag_stats.sort(key=lambda x: (-x[2], -x[1], -len(x[3])))

        lines += [f"## {domain}", ""]
        lines.append(
            "**先找人**：" + "、".join(f"[@{h}](https://www.kaggle.com/{h})（{n} 条）" for h, n in anchors.most_common(6))
        )
        lines.append("")
        lines.append("**复现决策项（按证据单位数）**：")
        for t, unit_count, strict_best, items in tag_stats[:8]:
            best = sorted(
                items,
                key=lambda c: (
                    0 if strict_tag_in(c, t, domain) >= STRICT_MIN else 1,
                    -relevance(c, t),
                    "A" != c["evidence_level"],
                    -int(c["votes"]),
                ),
            )[0]
            if relevance(best, t) < 8:
                continue
            lines.append(
                f"- **{t}**（{unit_count} 单位 / 严 {strict_tag_in(best, t, domain)}）：{best['action'][:88]} "
                f"—— @{best['person']}｜{best['evidence_level']}｜[原文]({best['source_url']})"
            )
        lines.append("")
        manifest_domains[domain] = {
            "snapshot_claims": len(pool),
            "strict_claims": sum(1 for c in pool if strict_in(c, domain) >= STRICT_MIN),
            "anchors": anchors.most_common(6),
            "top_tags": [(t, u, s) for t, u, s, _ in tag_stats[:8]],
        }

    (ref_dir / "people-routing.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    flags = collections.Counter(f for c in snapshot for f in c["flags"].split(";") if f)
    levels = collections.Counter(c["evidence_level"] for c in snapshot)
    strict_claims = sum(1 for c in snapshot if strict_replication(c) >= STRICT_MIN)
    broad_claims = sum(1 for c in snapshot if replication(c) >= 2)
    evidence_doc = f"""# 前 50 选手经验层：证据与口径

> 快照 {args.snapshot_date} ｜ 来源 KStarter `{kstarter_commit(ks)}` ｜ 快照断言 {len(snapshot)} 条。

## 数据形态

- `assets/gm_claims_snapshot.csv`：{len(snapshot)} 条断言（A {levels['A']} / B {levels['B']}），来自 152 条 ≥50 票 GM 主题帖全量抽取（551 条）中"带 ≥{args.min_specific_tags} 个具体技法标签"的 A/B 断言；其中广义复现 ≥2 单位 {broad_claims} 条，技法组合级复现（strict ≥{STRICT_MIN}）{strict_claims} 条。
- 每条断言 = 条件 → 动作 → 机制 → 结果 + 证据等级 + 原文链接；不含逐字引用（引用与 topic id 校验见 KStarter `scripts/people/verify_claims.py`）。
- 标签与证据单位来自 KStarter `people/claims/gm_claim_tags.csv`；复现度只统计**具体技法标签**（见 `tools/sync_people_layer.py` 的 SPECIFIC_TAGS），并限制在同领域。

## 证据规则

- 等级：A = 原文可复算数字 + 名次/团队背书；B = 有数字无独立背书；C 不进快照。
- 复现度两口径（都用**独立证据单位**；`team_evidence` 按（比赛 + 队名）合并，同队多人只算 1 个单位）：
  - `replication`（广义）：同领域内使用该断言**任一**具体技法标签的单位数上限；≥3 可当"跨人复现"，=2 视为"弱复现"。
  - `strict_replication`（严格）：同领域内**同时**复现该断言 ≥2 个具体技法标签的单位数（含自身单位；统计跨全部证据等级、含 C 级——它证明"技法被复现"，增益可信度仍看断言自身等级）；≥{STRICT_MIN} 说明技法组合被独立复现，采纳优先级最高。
- 口径旗标（flags）：
  - `lb_unusable`：Kaggle 冻结榜（分数全 0），名次不可用；
  - `lb_public_misleading`：公开榜名次与最终/私有结果背离（含泄漏争议场次）；
  - `team_evidence`：团队成绩，不归因个人；
  - `leak_usage` / `test_self_training` / `evaluator_exploit`：需要先确认比赛规则；
  - `negative_result`：负结果（反例证据）。
- 引用断言时标注 `claim_id + replication/strict + level`；先采纳 strict ≥{STRICT_MIN}，再考虑广义复现高的；并查 `people-tensions.md` 是否有相反裁决。

## 已知边界

- 抽取/审计为同一模型完成；30 条分层审计见 KStarter `people/claims/AUDIT.md`（机器校验 100%，语义抽检 30/30 pass）。
- 快照只覆盖 KStarter 归档的 94 场（有 ≥50 票 GM 主题帖的比赛），不是选手完整生涯。
- 旗标统计（快照内）：{", ".join(f"{k} {v}" for k, v in flags.most_common())}
"""
    (ref_dir / "people-evidence.md").write_text(evidence_doc, encoding="utf-8")

    tensions_src = ks / "analysis/people/TENSIONS.md"
    if tensions_src.exists():
        body = tensions_src.read_text(encoding="utf-8")
        header = f"> 同步自 KStarter `{kstarter_commit(ks)[:12]}`（{args.snapshot_date}）；证据链接为 Kaggle 原文。\n\n"
        (ref_dir / "people-tensions.md").write_text(body.split("\n", 1)[0] + "\n\n" + header + body.split("\n", 1)[1], encoding="utf-8")

    manifest = {
        "source": "KStarter",
        "kstarter_commit": kstarter_commit(ks),
        "snapshot_date": args.snapshot_date,
        "snapshot_claims": len(snapshot),
        "levels": dict(levels),
        "min_specific_tags": args.min_specific_tags,
        "broad_replication_ge2": broad_claims,
        "strict_replication": {"min": STRICT_MIN, "claims": strict_claims},
        "domains": manifest_domains,
        "flags": dict(flags),
    }
    (out_dir / "people_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"snapshot: {len(snapshot)} claims (A {levels['A']} / B {levels['B']}) -> assets/gm_claims_snapshot.csv")
    print(f"  broad replication >=2: {broad_claims}; strict >= {STRICT_MIN}: {strict_claims}")
    print(f"routing: {len(manifest_domains)} domains -> references/people-routing.md")
    print(f"kstarter commit: {kstarter_commit(ks)[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
