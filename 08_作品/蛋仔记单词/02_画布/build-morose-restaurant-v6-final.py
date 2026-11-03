# -*- coding: utf-8 -*-
"""Restaurant v6: no rescue; 黄蛋 silent/morose; narration ends; cut to card v2."""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v5-clean.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v6-final-story.monet"
CARD = json.loads((ROOT / "01_资产" / "道具" / "morose-card-v2-upload.json").read_text(encoding="utf-8"))
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "morose-restaurant-v6"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


A07 = find("【待生成】A07")
V2 = find("【待生成】V2")
KC = find("KC")
S0 = find("S0")

# remove A07
nodes.remove(A07)

# V2 refs remove A07; replace block
mp = V2["params"]["model_params"]
mp["reference_images"] = [r for r in mp["reference_images"] if r["node_id"] != A07["id"]]
block = """【道具】{{%s}} 关着的打包盒；{{%s}} 打开后的盒内（白饭＋青椒，无肉丝）；{{%s}} 小白碟＋一根肉丝。
0–2 秒：{{%s}} 黄蛋站在木桌旁，餐盒**关着**，已经在**木桌桌面**上；他把手放在盒盖上。
2–4 秒：黄蛋打开盒盖——里面只有青椒，没有肉丝：“……怎么没有肉丝？”
4–6 秒：心易在柜台后僵住/探头：“咔啵？”
6–7 秒：心易缩回后厨窗口：“咔——啵”
7–8 秒：心易端小白碟（一根肉丝）放桌上：“咔啵！”
8–9 秒：黄蛋看那一根，更郁闷：“所以我很 morose？”心易低头/拍肩：“咔……啵……”镜尾定格 1s。""" % (
    find("A05C")["id"], find("A05")["id"], A07["id"], find("T_A")["id"])
new = """【道具】{{%s}} 关着的打包盒；{{%s}} 打开后的盒内（白饭＋青椒，无肉丝）。
0–2 秒：{{%s}} 黄蛋站在木桌旁，餐盒**关着**，已经在**木桌桌面**上；他把手放在盒盖上。
2–4 秒：黄蛋打开盒盖——里面只有青椒，没有肉丝：“……怎么没有肉丝？”
4–6 秒：心易在柜台后僵住，探头：“咔啵？”
6–7 秒：黄蛋看向心易：“肉丝呢？”
7–8 秒：心易慢慢缩回后厨窗口：“咔——啵”；**不拿任何食物出来，不补救**。
8–9 秒：黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；**不说话**；镜尾定格 1s。""" % (
    find("A05C")["id"], find("A05")["id"], find("T_A")["id"])
assert block in mp["prompt"], "V2 block not found"
mp["prompt"] = mp["prompt"].replace(block, new)
assert "A07" not in mp["prompt"]
assert A07["id"] not in mp["prompt"]
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、心易拿食物补救、",
)

# KC card v2
kc = KC["outputs"][0]
kc["value"] = CARD["url"]
kc["name"] = CARD["name"]
kc["resolution"] = {"width": CARD["width"], "height": CARD["height"]}
kc["metadata"] = {"size": CARD["size"], "md5": CARD["md5"]}
KC["meta"]["label"] = "KC 单卡尾 v2 · morose / 没肉丝 → 郁闷的（木桌/小院）"

# S0
s0 = S0["outputs"][0]
s0["value"] += """

【结尾·无补救】
- 黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；不说话。
- 旁白：“没有肉丝，morose，闷闷不乐的。你记住了吗？”
- 旁白结束，硬切单卡 v2：morose / 没肉丝 → 郁闷的。
- 心易不拿任何食物出来、不补救；结尾也不再补心易“咔啵？”。
"""
S0["meta"]["label"] = "S0 制作说明 · 先读"

# groups: remove A07; keep g02 A05C/A06
for g in c["groups"]:
    if A07["id"] in g["nodeIds"]:
        g["nodeIds"] = [i for i in g["nodeIds"] if i != A07["id"]]
        # recompute bounds from remaining nodes
        ns = [n for n in nodes if n["id"] in g["nodeIds"]]
        g["bounds"] = {
            "x": float(min(n["meta"]["x"] for n in ns) - 20),
            "y": float(min(n["meta"]["y"] for n in ns) - 20),
            "width": float(max(n["meta"]["x"] + n["meta"]["width"] for n in ns) - min(n["meta"]["x"] for n in ns) + 40),
            "height": float(max(n["meta"]["y"] + n["meta"]["height"] for n in ns) - min(n["meta"]["y"] for n in ns) + 40),
        }

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
c["name"] = "蛋仔记单词 · morose 小饭馆版 v6 · 无补救/旁白收/单卡 v2 · 20s"

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
    for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
        assert tok in by_id, f"missing {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
    for r in refs + ([ff] if ff else []):
        assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
    assert not mp.get("reference_audios")
for i, a in enumerate(c["groups"]):
    for b in c["groups"][i + 1:]:
        ax, ay, aw, ah = a["bounds"].values()
        bx, by_, bw, bh = b["bounds"].values()
        if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
            raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
grouped = [i for gg in c["groups"] for i in gg["nodeIds"]]
assert sorted(grouped) == sorted(ids_set)

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(c['edges'])} edges / {len(c['groups'])} groups")
print("->", OUT)
