#!/usr/bin/env python3
"""预注册实验台账：把 Improvement Plan 的假设/MDE/kill 冻结，再按结果自动判定。

核心规则（防事后改标准）：
  - 假设一旦登记就冻结；有实验结果后再改必须用 --amend，并在报告里标红；
  - 判定只用预注册的 MDE 与折胜数阈值，不允许临场调整；
  - PASS=达到 MDE 且折胜数达标；KILL=均值≤0 或折胜数明显不足；其余=INCONCLUSIVE。

用法：
  python scripts/plan_tracker.py init --out runs/plan.json --competition <slug> --metric auc --baseline-cv 0.9500
  python scripts/plan_tracker.py preregister --plan runs/plan.json --id H1 --claim "嵌套 TE +0.001" \
      --mde 0.0005 --min-fold-wins 4 --cost-hours 3
  python scripts/plan_tracker.py record --plan runs/plan.json --id H1 --cv 0.9512 \
      --fold-deltas "0.001,0.0008,0.0015,0.0009,0.0011" --cost-hours 2.5
  python scripts/plan_tracker.py judge --plan runs/plan.json
  python scripts/plan_tracker.py report --plan runs/plan.json
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import time


def load(path: pathlib.Path) -> dict:
    if not path.exists():
        print(f"ERROR: 找不到 {path}（先运行 init）", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: pathlib.Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def find(state: dict, hid: str) -> dict:
    for h in state["hypotheses"]:
        if h["id"] == hid:
            return h
    print(f"ERROR: 没有假设 {hid}", file=sys.stderr)
    sys.exit(1)


def sign_p(wins: int, n: int) -> float:
    """单侧符号检验：P(X>=wins | Bin(n,0.5))。"""
    if n <= 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)


def judge_one(state: dict, h: dict) -> dict:
    exps = h.get("experiments", [])
    if not exps:
        return {"status": "PENDING", "reason": "尚未记录实验"}
    deltas: list[float] = []
    for e in exps:
        if e.get("fold_deltas"):
            deltas += [float(x) for x in e["fold_deltas"]]
        elif e.get("cv") is not None and state["competition"].get("baseline_cv") is not None:
            deltas.append(float(e["cv"]) - float(state["competition"]["baseline_cv"]))
    if not deltas:
        return {"status": "PENDING", "reason": "缺少 fold_deltas 或 baseline_cv"}
    mean = sum(deltas) / len(deltas)
    wins = sum(1 for d in deltas if d > 0)
    n = len(deltas)
    p = sign_p(wins, n)
    mde, min_wins = float(h["mde"]), int(h["min_fold_wins"])
    if mean >= mde and wins >= min_wins:
        status = "PROMOTE"
    elif mean <= 0 or wins < max(1, math.ceil(min_wins / 2)):
        status = "KILL"
    else:
        status = "INCONCLUSIVE"
    return {"status": status, "mean_delta": mean, "wins": wins, "n": n, "sign_p": p,
            "mde": mde, "min_fold_wins": min_wins,
            "amended_after_experiments": h.get("amended_after_experiments", False)}


def cmd_init(args) -> int:
    state = {
        "competition": {"slug": args.competition, "metric": args.metric, "baseline_cv": args.baseline_cv,
                         "created_at": time.strftime("%Y-%m-%d %H:%M:%S")},
        "hypotheses": [],
    }
    save(pathlib.Path(args.out), state)
    print(f"初始化 -> {args.out}（metric={args.metric}, baseline_cv={args.baseline_cv}）")
    return 0


def cmd_preregister(args) -> int:
    path = pathlib.Path(args.plan)
    state = load(path)
    if any(h["id"] == args.id for h in state["hypotheses"]):
        print(f"ERROR: {args.id} 已存在（假设登记后不可改，除非 --amend）", file=sys.stderr)
        return 1
    state["hypotheses"].append({
        "id": args.id, "claim": args.claim, "mde": args.mde, "min_fold_wins": args.min_fold_wins,
        "cost_budget_hours": args.cost_hours, "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "frozen": True, "experiments": [],
    })
    save(path, state)
    print(f"预注册 {args.id}: {args.claim}（MDE={args.mde}, 折胜≥{args.min_fold_wins}, 预算 {args.cost_hours}h）")
    return 0


def cmd_amend(args) -> int:
    path = pathlib.Path(args.plan)
    state = load(path)
    h = find(state, args.id)
    if h["experiments"]:
        h["amended_after_experiments"] = True
    if args.mde is not None:
        h["mde"] = args.mde
    if args.min_fold_wins is not None:
        h["min_fold_wins"] = args.min_fold_wins
    if args.claim:
        h["claim"] = args.claim
    h["amended_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save(path, state)
    print(f"已修订 {args.id}（有实验结果={bool(h['experiments'])}，将标记在报告里）")
    return 0


def cmd_record(args) -> int:
    path = pathlib.Path(args.plan)
    state = load(path)
    h = find(state, args.id)
    deltas = [float(x) for x in args.fold_deltas.split(",") if x.strip()] if args.fold_deltas else []
    h["experiments"].append({
        "cv": args.cv, "fold_deltas": deltas, "cost_hours": args.cost_hours,
        "notes": args.notes, "recorded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    save(path, state)
    print(f"记录 {args.id}: cv={args.cv} folds={len(deltas)} cost={args.cost_hours}h")
    return 0


def cmd_judge(args) -> int:
    state = load(pathlib.Path(args.plan))
    targets = [find(state, args.id)] if args.id else state["hypotheses"]
    for h in targets:
        v = judge_one(state, h)
        line = f"{h['id']}: {v['status']}"
        if "mean_delta" in v:
            line += f" | meanΔ={v['mean_delta']:+.5f} wins={v['wins']}/{v['n']} sign_p={v['sign_p']:.4f}"
            if v["amended_after_experiments"]:
                line += " | ⚠ 事后修订"
        else:
            line += f" | {v['reason']}"
        print(line)
    return 0


def cmd_report(args) -> int:
    state = load(pathlib.Path(args.plan))
    c = state["competition"]
    print(f"# 实验台账：{c['slug']}（{c['metric']}，baseline {c['baseline_cv']}）\n")
    print("| 假设 | MDE | 折胜门槛 | 状态 | meanΔ | 实验数 | 成本(h) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    total_cost = 0.0
    for h in state["hypotheses"]:
        v = judge_one(state, h)
        cost = sum(float(e.get("cost_hours") or 0) for e in h.get("experiments", []))
        total_cost += cost
        mean = f"{v['mean_delta']:+.5f}" if "mean_delta" in v else "—"
        flag = "⚠" if v.get("amended_after_experiments") else ""
        print(f"| {h['id']} {flag} | {h['mde']} | ≥{h['min_fold_wins']} | {v['status']} | {mean} | "
              f"{len(h.get('experiments', []))} | {cost:.1f} |")
    print(f"\n总成本：{total_cost:.1f}h｜假设数：{len(state['hypotheses'])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="预注册实验台账")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--out", required=True)
    p.add_argument("--competition", required=True)
    p.add_argument("--metric", default="")
    p.add_argument("--baseline-cv", type=float, default=None)
    p.set_defaults(func=cmd_init)
    p = sub.add_parser("preregister")
    p.add_argument("--plan", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--claim", required=True)
    p.add_argument("--mde", type=float, required=True)
    p.add_argument("--min-fold-wins", type=int, default=4)
    p.add_argument("--cost-hours", type=float, default=0.0)
    p.set_defaults(func=cmd_preregister)
    p = sub.add_parser("amend")
    p.add_argument("--plan", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--claim", default="")
    p.add_argument("--mde", type=float, default=None)
    p.add_argument("--min-fold-wins", type=int, default=None)
    p.set_defaults(func=cmd_amend)
    p = sub.add_parser("record")
    p.add_argument("--plan", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--cv", type=float, default=None)
    p.add_argument("--fold-deltas", default="")
    p.add_argument("--cost-hours", type=float, default=0.0)
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_record)
    p = sub.add_parser("judge")
    p.add_argument("--plan", required=True)
    p.add_argument("--id", default="")
    p.set_defaults(func=cmd_judge)
    p = sub.add_parser("report")
    p.add_argument("--plan", required=True)
    p.set_defaults(func=cmd_report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
