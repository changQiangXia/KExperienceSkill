#!/usr/bin/env python3
"""生成 assets/technique_case_map.csv：技法 × 案例（支持/反例/示例）+ 关键数字摘录。

用法：python tools/build_technique_map.py
"""

from __future__ import annotations

import csv
import json
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parent.parent
CARDS = SKILL / "assets" / "case_cards.jsonl"

# technique: support/refute/example + evidence probe
TECHNIQUES: dict[str, dict] = {
    "随机目标检验": {"support": ["playground-series-s5e9"], "example": ["playground-series-s5e2"], "probe": "随机|z|打乱"},
    "中位数样本权重": {"support": ["playground-series-s3e25"], "probe": "权重|MedAE|0.06"},
    "目标档位吸附": {"support": ["playground-series-s3e14", "playground-series-s3e25"], "probe": "唯一|档位|吸附|0.25"},
    "分组合法性裁剪": {"support": ["playground-series-s3e8"], "probe": "裁剪|Q3|IQR|下界"},
    "结构约束投影": {"support": ["optiver-trading-at-the-close"], "probe": "零和|加权|后处理"},
    "单参数校准": {"support": ["tabular-playground-series-nov-2022"], "probe": "1.17|平移|校准"},
    "isotonic 校准": {"support": ["tabular-playground-series-nov-2022"], "refute": ["tabular-playground-series-nov-2022"], "probe": "isotonic|校准"},
    "秩融合": {"support": ["playground-series-s3e18", "playground-series-s3e23"], "probe": "AUC|秩|平均"},
    "阈值后处理": {"support": ["learning-equality-curriculum-recommendations", "playground-series-s3e22"], "probe": "阈值|margin|micro"},
    "实体分组 CV": {"support": ["scrabble-player-rating", "playground-series-s3e22"], "probe": "GroupKFold|分组|nickname"},
    "对抗验证": {"support": ["playground-series-s3e18"], "probe": "对抗|adversarial"},
    "时间切分/purge": {"support": ["jane-street-real-time-market-data-forecasting", "amex-default-prediction"], "probe": "时序|gap|窗口|200 天"},
    "在线学习": {"support": ["jane-street-real-time-market-data-forecasting", "optiver-trading-at-the-close"], "probe": "在线|重训|更新"},
    "伪标签": {"support": ["sorghum-id-fgvc-9"], "refute": ["hotel-id-to-combat-human-trafficking-2022-fgvc9", "playground-series-s5e9"], "probe": "伪标"},
    "知识蒸馏": {"support": ["lmsys-chatbot-arena", "feedback-prize-effectiveness"], "probe": "蒸馏|教师|9B|70B"},
    "ArcFace/subcenter": {"support": ["herbarium-2022-fgvc9", "sorghum-id-fgvc-9", "hotel-id-to-combat-human-trafficking-2022-fgvc9"], "probe": "ArcFace|subcenter|margin"},
    "IBN/直方图域适应": {"support": ["sorghum-id-fgvc-9", "hotel-id-to-combat-human-trafficking-2022-fgvc9"], "probe": "IBN|直方图|BlendFlip"},
    "高分辨率": {"support": ["sorghum-id-fgvc-9", "herbarium-2022-fgvc9"], "probe": "512|960|1024|384"},
    "身份辅助任务": {"support": ["planttraits2024"], "probe": "物种|三头|17,396|软分类"},
    "分层学习率": {"support": ["planttraits2024", "herbarium-2022-fgvc9"], "probe": "学习率|warmup|冻结|scheduler"},
    "课程学习+热启动": {"support": ["lux-ai-season-2-neurips-stage-2"], "refute": ["lux-ai-season-2-neurips-stage-2"], "probe": "16×16|32×32|64×64|checkpoint"},
    "行动掩码/冲突取消": {"support": ["lux-ai-season-2-neurips-stage-2"], "probe": "掩码|冲突|invalid"},
    "自对弈对手多样性": {"support": ["maze-crawler", "pokemon-tcg-ai-battle-challenge-strategy"], "probe": "自对弈|镜像|对手|53/47"},
    "规则基线": {"support": ["kore-2022-beta", "maze-crawler"], "probe": "规则|七模块|评分函数"},
    "黑箱代理评分": {"support": ["santa-2024"], "example": ["ai-village-ctf"], "probe": "评分|代理|困惑度|local"},
    "密度分层阈值": {"support": ["iwildcam2022-fgvc9"], "probe": "密度|8 个|阈值|NMS"},
    "未知类/OSD": {"support": ["fathomnet-out-of-sample-detection", "geolifeclef-2022-lifeclef-2022-fgvc9"], "probe": "unknown|OSD|邻域换标|无匹配"},
    "工具集成推理(TIR)": {"support": ["ai-mathematical-olympiad-prize"], "probe": "TIR|Python|代码"},
    "大候选+投票": {"support": ["ai-mathematical-olympiad-prize"], "probe": "候选|投票|120|160"},
    "多目标拆合": {"support": ["playground-series-s3e18", "planttraits2024"], "probe": "EC1|EC2|标签链|多头"},
    "异质集成": {"support": ["playground-series-s3e23", "playground-series-s3e9"], "refute": ["playground-series-s3e18"], "probe": "集成|非树|Ridge|Bagged"},
    "爬山权重搜索": {"support": ["playground-series-s3e23", "playground-series-s3e14", "playground-series-s3e8"], "probe": "爬山|hill|权重"},
    "域内预训练权重": {"support": ["planttraits2024", "google-universal-image-embedding", "sorghum-id-fgvc-9"], "probe": "预训练|CLIP|PlantCLEF|ImageNet"},
    "频率/OOD 编码": {"support": ["playground-series-s3e18"], "probe": "频率|OOD|未见"},
    "提交对冲": {"support": ["playground-series-s3e22", "home-credit-credit-risk-model-stability"], "probe": "对冲|双提交|候选"},
    "评审闭环写作": {"support": ["pokemon-tcg-ai-battle-challenge-strategy", "bigquery-ai-hackathon"], "probe": "闭环|消融|失败路径|复现"},
    "Agent schema/预算": {"support": ["autonomous-agent-prediction-beta", "gemini-long-context"], "probe": "schema|预算|Save|validate"},
    "LLM 引用核验": {"support": ["openai-to-z-challenge"], "probe": "幻觉|核验|引用"},
    "行动成本模型": {"support": ["ai-agent-security-multi-step-tool-attacks"], "probe": "成本|decode|hops|token"},
    "期望错位后处理": {"support": ["AI4Code"], "probe": "错位|槽位|交换"},
}


def main() -> int:
    cards = {}
    for line in CARDS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            cards[c["slug"]] = c

    rows = []
    for tech, spec in TECHNIQUES.items():
        for role in ("support", "refute", "example"):
            for slug in spec.get(role, []):
                card = cards.get(slug)
                if not card:
                    continue
                probe = re.compile(spec.get("probe", ""), re.I) if spec.get("probe") else None
                snippet = ""
                for k in card["key_numbers"]:
                    blob = f"{k['claim']} {k['value']}"
                    if probe and probe.search(blob):
                        snippet = f"{k['claim']}：{k['value']}"
                        break
                if not snippet and card["key_numbers"]:
                    snippet = f"{card['key_numbers'][0]['claim']}：{card['key_numbers'][0]['value']}"
                rows.append(
                    {
                        "technique": tech,
                        "role": role,
                        "slug": slug,
                        "snippet": re.sub(r"\s+", " ", snippet)[:280],
                        "topic_ids": " ".join(k["source"] for k in card["key_numbers"][:3] if k["source"]),
                    }
                )

    out = SKILL / "assets" / "technique_case_map.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"technique_case_map.csv: {len(rows)} rows, {len(TECHNIQUES)} techniques -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
