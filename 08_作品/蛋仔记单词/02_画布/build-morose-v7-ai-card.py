# -*- coding: utf-8 -*-
"""Add an AI-generated single-card tail (KC_AI) alongside the PIL fallback."""
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v6-final-story.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v7-ai-card.monet"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "morose-restaurant-v7"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}

KC = next(n for n in nodes if n["meta"].get("label", "").startswith("KC"))
KC["meta"]["y"] = 820.0
S0 = next(n for n in nodes if n["meta"].get("label", "").startswith("S0"))

PROMPT = """16:9 一张词卡摆在木桌上，只生成一张，不要多张。米白卡片、浅灰边；卡面写两行：第一行红字“morose”；第二行黑字“没肉丝 → 郁闷的”。黑色手写感字，红色关键词；小院背景虚化，午后暖光。除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、文字重叠、两张卡/三张卡/多余卡、错误单词、中文错字。"""

nid = "node-" + hashlib.md5((PREFIX + ":KC_AI").encode()).hexdigest()[:8]
oid = "output-" + hashlib.md5((PREFIX + ":KC_AI:out").encode()).hexdigest()[:10]
kc_ai = {
    "id": nid, "type": "gen-image", "mainOutputId": None,
    "meta": {"x": 1200.0, "y": 600.0, "width": 300.0, "height": 169.0,
             "label": "【待生成】KC_AI 单卡尾 · AI生成（morose / 没肉丝 → 郁闷的）", "resourceType": None},
    "outputs": [],
    "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
        "prompt": PROMPT, "reference_images": [],
        "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 1024,
        "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True,
    }},
    "specialParams": None, "config": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
}
nodes.append(kc_ai)
by[nid] = kc_ai

# group g06 add KC_AI; recompute
for g in c["groups"]:
    if any(i == KC["id"] for i in g["nodeIds"]):
        g["nodeIds"].append(nid)
        ns = [by[i] for i in g["nodeIds"]]
        g["bounds"] = {
            "x": float(min(n["meta"]["x"] for n in ns) - 20),
            "y": float(min(n["meta"]["y"] for n in ns) - 20),
            "width": float(max(n["meta"]["x"] + n["meta"]["width"] for n in ns) - min(n["meta"]["x"] for n in ns) + 40),
            "height": float(max(n["meta"]["y"] + n["meta"]["height"] for n in ns) - min(n["meta"]["y"] for n in ns) + 40),
        }

s0 = S0["outputs"][0]
s0["value"] += """

【单卡尾：AI 版 vs PIL 版】
- 先跑 KC_AI：一张米白卡、木桌/小院、红字 morose、黑字 没肉丝 → 郁闷的。
- 文字必须完全一致；出现错字/串卡/多张卡就重跑，别硬用。
- 如果 AI 卡文字不稳，回退 KC（PIL 版，字绝对准）。
- 正片只用其中一张，不要两张都放。
"""
S0["meta"]["label"] = "S0 制作说明 · 先读"

# validate groups coverage/bounds
ids_set = {n["id"] for n in nodes}
grouped = [i for gg in c["groups"] for i in gg["nodeIds"]]
assert sorted(grouped) == sorted(ids_set), (len(grouped), len(ids_set))
for i, a in enumerate(c["groups"]):
    for b in c["groups"][i + 1:]:
        ax, ay, aw, ah = a["bounds"].values()
        bx, by_, bw, bh = b["bounds"].values()
        if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
            raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")

c["name"] = "蛋仔记单词 · morose 小饭馆版 v7 · AI单卡尾 · 20s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{len(nodes)} nodes / {len(c['edges'])} edges / {len(c['groups'])} groups")
print("->", OUT)
