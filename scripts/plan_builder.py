#!/usr/bin/env python3
"""根据新比赛画像 + 案例库，生成 Improvement Plan 骨架。

用法：
  python scripts/plan_builder.py --task "tabular regression" --metric "MedAE" \
      --tags "tabular,synthetic" --notes "1500 队，小数据，public 20%"

输出：markdown 计划骨架（Competition Card / 匹配案例 / 候选假设空表 / 执行顺序 / 收官清单）。
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "assets" / "case_index.csv"
CARDS = ROOT / "assets" / "case_cards.jsonl"

# 症状关键词 → idea-playbook 章节
SYNDROME_MAP = [
    (r"medae|median|分位|quantile", ["S6"]),
    (r"auc|ndcg|map@|top-?k|排序|ranking|kendall", ["S7"]),
    (r"f1|accuracy|阈值|threshold", ["S8"]),
    (r"容差|tolerance|map@", ["S9"]),
    (r"log ?loss|概率|校准", ["S10"]),
    (r"gini|capture|复合|stability", ["S11"]),
    (r"合成|synthetic|playground|随机", ["S12", "S13"]),
    (r"实体|entity|group|玩家|患者", ["S14", "S4"]),
    (r"缺失|missing|哨兵|noise|噪声", ["S15"]),
    (r"ood|漂移|drift|类别", ["S16"]),
    (r"域差|domain|多来源|域适应", ["S17"]),
    (r"长尾|long.?tail|imbalance|稀有", ["S18"]),
    (r"集成|ensemble|stack", ["S20"]),
    (r"调参|hyper|optuna", ["S21"]),
    (r"算力|时延|latency|限时|t4|gpu", ["S22"]),
    (r"多目标|multi.?target|multilabel", ["S23"]),
    (r"检索|retrieval|matching|embedding", ["S24"]),
    (r"llm|prompt|生成|language model", ["S25"]),
    (r"agent|rl|reinforcement|self.?play|对战", ["S26"]),
    (r"优化|黑箱|search|ctf|安全", ["S27"]),
    (r"评审|review|writeup|hackathon|研究", ["S28"]),
    (r"时序|time.?series|forecast|在线", ["S5"]),
    (r"cv|图像|image|分割|检测", ["S17"]),
]


def tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[\s,;/|]+", text.lower()) if t]


def score(row: dict[str, str], query: list[str], metric: str, tags: list[str]) -> float:
    blob = " ".join([row["slug"], row["title"], row["metric"], row["tags"], row["one_line"]]).lower()
    s = 0.0
    for token in query:
        if token in blob:
            s += 3
    if metric:
        s += 6 if metric.lower() in row["metric"].lower() else 0
    row_tags = set(t for t in row["tags"].split(",") if t)
    s += 3 * len(row_tags & set(tags))
    return s


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--metric", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args()

    rows = list(csv.DictReader(INDEX.open(encoding="utf-8")))
    tag_list = [t.strip() for t in args.tags.split(",") if t.strip()]
    query = tokens(args.task)
    ranked = sorted(((score(r, query, args.metric, tag_list), r) for r in rows), key=lambda x: x[0], reverse=True)
    hits = [(s, r) for s, r in ranked if s > 0][: args.limit]

    cards = {}
    if CARDS.exists():
        for line in CARDS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                c = json.loads(line)
                cards[c["slug"]] = c

    blob = f"{args.task} {args.metric} {' '.join(tag_list)}".lower()
    syndromes = []
    for pattern, ids in SYNDROME_MAP:
        if re.search(pattern, blob):
            syndromes.extend(ids)
    syndromes = list(dict.fromkeys(syndromes)) or ["S1", "S12"]

    print(f"# Improvement Plan（骨架）— {args.task}")
    print("\n## 0. Competition Card")
    print(f"- 任务：{args.task}")
    print(f"- 指标：{args.metric or '待确认（读官方实现）'}")
    print(f"- 标签/主题：{', '.join(tag_list) or '待补'}")
    print(f"- 备注：{args.notes or '待补（数据规模/切分/评测约束/平台规则）'}")
    print("- 待补：CV-LB 关系 / 当前 baseline / 分数由谁决定 / 噪声地板")

    print("\n## 1. 匹配案例（结构类比，读机制不抄参数）")
    if not hits:
        print("- （未命中，放宽 task/metric/tags 或直接浏览 references/case-index.md）")
    for s, r in hits:
        print(f"\n### {r['slug']}（score {s:.0f}｜{r['theme']}/{r['category']}｜{r['metric']}）")
        print(f"- 一句话：{r['one_line'] or r['title']}")
        card = cards.get(r["slug"])
        if card:
            for k in card["key_numbers"][:3]:
                print(f"- 关键数字：{k['claim']}：{k['value'][:180]}（{k['source']}）")
            if card["failures"]:
                print(f"- 失败/悬案：{card['failures'][0]}")
        print(f"- 深读：{r['deep_doc']}")

    print("\n## 2. 相关思路章节（idea-playbook）")
    print(f"- 建议先读：{', '.join(syndromes)}（`references/idea-playbook.md`）")

    print("\n## 3. 候选假设（待填，每条必须有机制/类比证据/证伪实验/kill 标准）")
    print("| # | 假设 | 机制 | 类比证据（slug+数字） | 证伪实验（同折 OOF） | 期望收益 | 成本 | 风险 | Kill 标准 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for i in range(1, 6):
        print(f"| {i} |  |  |  |  |  |  |  |  |")

    print("\n## 4. 执行顺序")
    print("1. 修验证/指标口径/提交格式（最高优先）")
    print("2. 指标结构后处理（若命中 S6–S11）")
    print("3. 数据/结构红利（若命中 S12–S18）")
    print("4. 模型/集成/训练（S19–S23）")
    print("5. 领域专项（S24–S27）")
    print("6. 交付/收官（S28）")

    print("\n## 5. 收官保护")
    print("- 跑 `scripts/submission_guard.py`；按 `assets/endgame_checklist.md` 冻结与对冲。")
    print("- 每条实验写入 `assets/experiment_ledger_template.csv`，连续两轮无 OOF 增益回到诊断。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
