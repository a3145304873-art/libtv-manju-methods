# -*- coding: utf-8 -*-
"""Restaurant v3: first frame has NO lunch box; 心易 brings it out only after the order."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v2-eye-lock.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v3-order-first.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
by = {n["id"]: n for n in c["nodes"]}


def find(prefix):
    return next(n for n in c["nodes"] if n["meta"].get("label", "").startswith(prefix))


ka = find("【待生成】K_A")
v1 = find("【待生成】V1")
a05 = next(r["node_id"] for r in ka["params"]["model_params"]["reference_images"]
           if "打包盒" in by[r["node_id"]]["meta"].get("label", ""))

# K_A: no box at all
mp = ka["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace(
    "；柜台上放着打开的打包盒（参考 {{" + a05 + "}}）。",
    "；柜台上只有收银机/菜单，没有打包盒，心易双手空着。",
)
mp["reference_images"] = [r for r in mp["reference_images"] if r["node_id"] != a05]
mp["prompt"] = mp["prompt"].replace(
    "负向：旧黄蛋光滑塑料、",
    "负向：旧黄蛋光滑塑料、餐台上提前出现打包盒/餐盒、心易一开始手里有餐盒、",
)
assert a05 not in mp["prompt"]
assert all(r["node_id"] != a05 for r in mp["reference_images"])
c["edges"] = [e for e in c["edges"] if not (e["targetNodeId"] == ka["id"] and e["sourceNodeId"] == a05)]

# V1: box appears only at 4-6s
mp = v1["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace(
    "0–2 秒：{{" + ka["id"] + "}} 黄蛋站在柜台前，指墙上菜单图片：“青椒肉丝饭，肉丝多一点！”\n2–4 秒：心易点头，冲后厨喊：“咔啵！”（收到）\n4–6 秒：心易从出菜口拿打包盒，装袋/递出；黄蛋接。\n6–8 秒：黄蛋端着餐盒走向木桌；**尾帧停在半路/桌边，稳定 1 秒**，给 V2 接尾帧。",
    "0–2 秒：{{" + ka["id"] + "}} 黄蛋站在柜台前，指墙上菜单图片：“青椒肉丝饭，肉丝多一点！”**柜台上只有收银机/菜单，没有打包盒。**\n"
    "2–4 秒：心易点头，转身走向后厨/出菜口：“咔啵！”（收到）**手里仍然没有餐盒。**\n"
    "4–6 秒：心易从出菜口拿出打包盒，装袋/递出；黄蛋接。**打包盒到 4 秒后才出现。**\n"
    "6–8 秒：黄蛋端着餐盒走向木桌；**尾帧停在半路/桌边，稳定 1 秒**，给 V2 接尾帧。",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、0–4 秒提前出现打包盒/餐盒、心易一开始手里有餐盒、",
)
assert "0–4 秒提前出现打包盒" in mp["prompt"]
assert "4 秒后才出现" in mp["prompt"]

# S0 note
s0 = next(n for n in c["nodes"] if n["meta"].get("label", "").startswith("S0"))
v = s0["outputs"][0]["value"]
if "点单后才拿盒" not in v:
    v += """

【点单后才拿盒】
K_A 首帧：柜台只有收银机/菜单，没有打包盒，心易双手空着。
V1 0–2 黄蛋点单；2–4 心易转身去后厨/出菜口；4–6 才拿出打包盒；6–8 端走。
负向：0–4 秒提前出现打包盒/餐盒、心易一开始手里有餐盒。
"""
    s0["outputs"][0]["value"] = v

c["name"] = "蛋仔记单词 · morose 小饭馆版 v3 · 点单后才拿盒 · 20s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print("->", OUT)


