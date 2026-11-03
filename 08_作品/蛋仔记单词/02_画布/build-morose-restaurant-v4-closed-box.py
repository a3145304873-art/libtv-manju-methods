# -*- coding: utf-8 -*-
"""Restaurant v4: handoff box is CLOSED; open only at the table."""
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v3-order-first.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v4-closed-box.monet"
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "morose-restaurant-v4"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


A05 = find("【已生成】A05")
A06 = find("【待生成】A06")
A07 = find("【待生成】A07")
K_A = find("【待生成】K_A")
T_A = find("T_A")
V1 = find("【待生成】V1")
V2 = find("【待生成】V2")
S0 = find("S0")

# A05C closed box
a05c_id = "node-" + hashlib.md5((PREFIX + ":A05C").encode()).hexdigest()[:8]
a05c = {
    "id": a05c_id, "type": "gen-image", "mainOutputId": None,
    "meta": {"x": 360.0, "y": 540.0, "width": 300.0, "height": 197.0,
             "label": "【待生成】A05C 关着的打包盒（盖紧，无食物露出）", "resourceType": None},
    "outputs": [],
    "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
        "prompt": "16:9 纯白底道具设定图：一个关着盖子的白色外卖餐盒/便当盒，长方形，盖子扣紧，无文字/logo；3D卡通+真实光影，轻微投影；无角色/手/食物露出。负向：打开、食物露出、肉丝、角色、手、文字、logo、水印、真实照片。",
        "reference_images": [], "aspect_ratio": "16:9", "image_size": "1K",
        "width": 1024, "height": 1024, "quality": "medium", "output_format": "png",
        "moderation": "low", "auto_compress": True,
    }},
    "specialParams": None, "config": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
}
nodes.append(a05c)
by[a05c_id] = a05c

# move A06/A07 down to make room for A05C
A06["meta"]["y"] = 760.0
A07["meta"]["y"] = 980.0

A05_URL_T = "{{" + A05["id"] + "}}"
A05C_T = "{{" + a05c_id + "}}"

# V1: closed box only
mp = V1["params"]["model_params"]
mp["reference_images"] = [r for r in mp["reference_images"] if r["node_id"] != A05["id"]]
mp["reference_images"].append({"node_id": a05c_id})
mp["prompt"] = mp["prompt"].replace(
    "【道具】{{" + A05["id"] + "}} 打包盒（白饭＋青椒，无肉丝）。",
    "【道具】{{" + a05c_id + "}} 盖着盖子的打包盒（里面是白饭＋青椒，无肉丝；但**不能提前打开、不能露出食物**）。",
)
mp["prompt"] = mp["prompt"].replace(
    "4–6 秒：心易从出菜口拿出打包盒，装袋/递出；黄蛋接。**打包盒到 4 秒后才出现。**",
    "4–6 秒：心易从出菜口拿出**盖着盖子的**打包盒，装袋/递出；黄蛋接。**盒子始终关着，不打开。**",
)
mp["prompt"] = mp["prompt"].replace(
    "6–8 秒：黄蛋端着餐盒走向木桌；",
    "6–8 秒：黄蛋端着**关着的**餐盒走向木桌；",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、餐盒提前打开/露出食物、",
)
assert A05["id"] not in mp["prompt"]
assert a05c_id in mp["prompt"]

# V2: closed at T_A, opens at 2-4s
mp = V2["params"]["model_params"]
if not any(r["node_id"] == a05c_id for r in mp["reference_images"]):
    mp["reference_images"].append({"node_id": a05c_id})
mp["prompt"] = mp["prompt"].replace(
    "【道具】{{" + A05["id"] + "}} 打包盒（白饭＋青椒，无肉丝）；{{" + A07["id"] + "}} 小白碟＋一根肉丝。",
    "【道具】{{" + a05c_id + "}} 关着的打包盒；{{" + A05["id"] + "}} 打开后的盒内（白饭＋青椒，无肉丝）；{{" + A07["id"] + "}} 小白碟＋一根肉丝。",
)
old = "0–2 秒：{{" + T_A["id"] + "}} 黄蛋在桌边打开打包盒，只有青椒：“……怎么没有肉丝？”\n2–4 秒：心易在柜台后僵住/探头：“咔啵？”（心虚）\n4–6 秒：心易缩回后厨窗口：“咔——啵”（等一下）\n6–8 秒：心易端小白碟（一根肉丝）放桌上：“咔啵！”（补救）\n8–9 秒：黄蛋看那一根，更郁闷；心易低头/拍肩：“咔……啵……”镜尾定格 1s。"
new = "0–2 秒：{{" + T_A["id"] + "}} 黄蛋在桌边，餐盒**关着**；他把餐盒放稳，手放在盒盖上。\n2–4 秒：黄蛋打开盒盖——里面只有青椒，没有肉丝：“……怎么没有肉丝？”\n4–6 秒：心易在柜台后僵住/探头：“咔啵？”（心虚）\n6–7 秒：心易缩回后厨窗口：“咔——啵”（等一下）\n7–8 秒：心易端小白碟（一根肉丝）放桌上：“咔啵！”（补救）\n8–9 秒：黄蛋看那一根，更郁闷；心易低头/拍肩：“咔……啵……”镜尾定格 1s。"
assert old in mp["prompt"], "V2 timing block not found"
mp["prompt"] = mp["prompt"].replace(old, new)
mp["prompt"] = mp["prompt"].replace(
    "**首帧＝T_A**：从 V1 最后一帧（黄蛋端盒走到桌边）继续，不换机位/不重摆/不换光。",
    "**首帧＝T_A**：从 V1 最后一帧（黄蛋端着关着的餐盒走到桌边）继续，不换机位/不重摆/不换光；**餐盒在 T_A 是关着的，2–4 秒才打开**。",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、T_A 首帧餐盒已打开、0–2 秒露出食物、",
)
assert a05c_id in mp["prompt"]
assert "餐盒在 T_A 是关着的" in mp["prompt"]

# groups: A05C joins g02; A05 stays g01
def group(key, label, keys, color, pad=20):
    ns = [by[k] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {"id": "group-" + hashlib.md5((PREFIX + ":group:" + key).encode()).hexdigest()[:8],
            "nodeIds": [n["id"] for n in ns],
            "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

g = {x["id"]: x for x in nodes}
groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", [find("R00")["id"], find("R01")["id"], find("R02")["id"], find("R02E")["id"]], "#E68BB3"),
    group("g01", "01 已生成 · 黄蛋毛绒/打开的餐盒", [find("R01P")["id"], A05["id"]], "#D8A657"),
    group("g02", "02 小饭馆/关盒/肉丝 · 先跑", [a05c_id, A06["id"], A07["id"]], "#8E8DE0"),
    group("g03", "03 首帧/尾帧 · K_A、T_A", [K_A["id"], T_A["id"]], "#E8B85D"),
    group("g04", "04 视频 V1 · 8s · 点单/端走", [V1["id"]], "#DC775D"),
    group("g05", "05 视频 V2 · 9s · 打开/补救", [V2["id"]], "#DC775D"),
    group("g06", "06 单卡尾/说明 · 后期", [find("KC")["id"], S0["id"]], "#7FB07F"),
]
c["groups"] = groups

# rebuild edges
required = set()
for n in nodes:
    if n.get("type") == "gen-video":
        mp = n["params"]["model_params"]
        for r in mp.get("reference_images", []):
            required.add((r["node_id"], n["id"]))
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        if ff:
            required.add((ff, n["id"]))
    elif n.get("type") == "gen-image":
        for r in n["params"]["model_params"].get("reference_images", []):
            required.add((r["node_id"], n["id"]))
c["edges"] = [{"id": "edge-" + hashlib.md5((a + ">" + b).encode()).hexdigest()[:8],
               "sourceNodeId": a, "sourceHandle": "output",
               "targetNodeId": b, "targetHandle": "input",
               "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}
              for a, b in sorted(required)]
c["name"] = "蛋仔记单词 · morose 小饭馆版 v4 · 关盒递出/到桌打开 · 20s"

s0 = S0["outputs"][0]
if "关盒递出" not in s0["value"]:
    s0["value"] += """

【关盒递出】
- 心易从出菜口拿的是 A05C 关着的打包盒；V1 全程不打开、不露食物。
- V2 首帧 T_A 盒子仍然关着；2–4 秒黄蛋才打开，发现只有青椒。
- 负向：餐盒提前打开/露出食物、T_A 首帧已打开。
- A05 打开的餐盒只用于 V2 打开后的盒内；A05C 用于 V1/交接。
"""
S0["meta"]["label"] = "S0 制作说明 · 先读"

# validate
ids_set = {n["id"] for n in nodes}
by_id = {n["id"]: n for n in nodes}
edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in c["edges"]}
for n in nodes:
    if n["type"] not in ("gen-image", "gen-video"):
        continue
    mp = n["params"]["model_params"]
    refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
    ff = (mp.get("first_frame_image") or {}).get("node_id")
    for tok in __import__("re").findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
        assert tok in by_id, f"missing {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
    for r in refs + ([ff] if ff else []):
        assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
    assert not mp.get("reference_audios")
for i, a in enumerate(groups):
    for b in groups[i + 1:]:
        ax, ay, aw, ah = a["bounds"].values()
        bx, by_, bw, bh = b["bounds"].values()
        if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
            raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
grouped = [i for gg in groups for i in gg["nodeIds"]]
assert sorted(grouped) == sorted(ids_set)

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(c['edges'])} edges / {len(groups)} groups")
print("->", OUT)


