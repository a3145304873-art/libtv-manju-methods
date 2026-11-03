# -*- coding: utf-8 -*-
"""Build v5: add a plush/felt 黄蛋 reference (R01P) matching the capybara texture.

R01P is a gen-image referencing the original R01; K/V use R01P instead of R01.
The user generates R01P first, then K/V. Keeps A01–A04/KC outputs.

Output: 02_画布/EP02-like-capybara-caption-plush-v1.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP02-like-capybara-caption-v1.monet"
OUT = HERE / "EP02-like-capybara-caption-plush-v1.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}
ids = {
    "R00": "node-3b85595e", "R01": "node-1dec7c6e", "R02": "node-34b2e592",
    "A01": "node-55532172", "A02": "node-d67c8efd", "A03": "node-f20de25c", "A04": "node-a7f97bc6",
    "KC": "node-7bc3ca9e",
    "K_A": "node-8bb56275", "K_B": "node-86fcfdf3", "K_C": "node-d00720ed",
    "V1": "node-0c21fa45", "V2": "node-1b546606", "V3": "node-4aabdc25",
    "S0": "node-ce285427",
}
for k, v in ids.items():
    assert v in by, f"missing {k} {v}"

R01P_PROMPT = """16:9 纯白底角色设定图，只生成一只黄蛋（毛绒版），全身正面。
保留黄蛋身份：黄色蛋形身体、奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿。
材质改成和参考水豚玩偶一致的**短毛绒/毛毡玩偶质感**：表面细短绒毛、可见纤维、柔和缝线、哑光；脸板是奶油色毛毡/布；眼睛是亮面塑料/刺绣；天线球是布球；袜子/鞋是白布；边缘有轻微绒毛轮廓；柔光棚拍，轻微投影。
不要：光滑塑料/搪胶、真实鸡蛋、蛋壳裂开、蛋黄/蛋液、牙齿、人类手指、猫耳/水豚耳朵、橘子、文字/logo/水印。
负向：光滑塑料、真实照片、人类、手指、牙齿、裂壳、蛋液、蛋黄、文字、logo、水印、比例失真。"""

nid = "node-" + hashlib.md5(("capybara-caption-plush:v1:R01P").encode("utf-8")).hexdigest()[:8]
r01p = {
    "id": nid, "type": "gen-image", "mainOutputId": None,
    "meta": {"x": 360.0, "y": 800.0, "width": 300.0, "height": 170.0,
             "label": "【待生成】R01P 黄蛋毛绒版 · 同水豚短毛绒质感", "resourceType": None},
    "outputs": [],
    "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
        "prompt": R01P_PROMPT,
        "reference_images": [{"node_id": ids["R01"]}],
        "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 1024,
        "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True,
    }},
    "specialParams": None, "config": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
}
ids["R01P"] = nid
nodes.append(r01p)
by[nid] = r01p

# K/V: use R01P instead of R01
for n in nodes:
    if n.get("type") not in ("gen-image", "gen-video") or n["id"] == nid:
        continue
    lab = n["meta"].get("label", "")
    if not any(lab.startswith(k) for k in ("【待生成】K_", "【待生成】V")):
        continue
    mp = n["params"]["model_params"]
    mp["prompt"] = mp["prompt"].replace("{{" + ids["R01"] + "}}", "{{" + ids["R01P"] + "}}")
    refs = []
    for r in mp.get("reference_images", []):
        refs.append({"node_id": ids["R01P"]} if r["node_id"] == ids["R01"] else r)
    mp["reference_images"] = refs
    n["outputs"] = []
    n["meta"]["label"] = lab.replace("水豚＋黄蛋", "水豚＋毛绒黄蛋").replace("rocklike", "rocklike（毛绒黄蛋）")

# groups: R01P into g00
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {
        "id": "group-" + hashlib.md5(("capybara-caption-plush:v1:group:" + key).encode("utf-8")).hexdigest()[:8],
        "nodeIds": [ids[k] for k in keys],
        "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/比例", ["R00", "R01", "R02"], "#E68BB3"),
    group("g01", "01 黄蛋毛绒/道具/小院/小蛇/金毛 · 先跑", ["R01P", "A01", "A02", "A03", "A04"], "#8E8DE0"),
    group("g02", "02 首帧/词卡 · K_A、K_B、K_C、KC", ["K_A", "K_B", "K_C", "KC"], "#E8B85D"),
    group("g03", "03 视频 V1 · 6s · rocklike", ["V1"], "#DC775D"),
    group("g04", "04 视频 V2 · 4s · snakelike", ["V2"], "#DC775D"),
    group("g05", "05 视频 V3 · 5s · doglike＋收尾", ["V3"], "#DC775D"),
    group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
]
c["groups"] = groups

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
edges = [{
    "id": "edge-" + hashlib.md5((a + ">" + b).encode("utf-8")).hexdigest()[:8],
    "sourceNodeId": a, "sourceHandle": "output",
    "targetNodeId": b, "targetHandle": "input",
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
} for a, b in sorted(required)]
c["edges"] = edges
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·后期白字」v1 · 15s"

s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词样片「水豚心易＋毛绒黄蛋·后期白字」：rocklike／snakelike／doglike，6＋4＋5＝15s。
心易＝棕色水豚，只发“咔啵”；黄蛋＝短毛绒版，说话；视频内无文字/气泡；白字横排后期加。
A01–A04、KC 已生成保留；R01P 是黄蛋毛绒版，先跑；K/V 用 R01P。

【跑序】
1. 先跑 R01P（黄蛋毛绒版）；看质感/身份是否对。
2. R01P 满意后跑 K_A / K_B / K_C。
3. 跑 V1（6s）/ V2（4s）/ V3（5s）。
4. 后期加横排白字（弹入/弹出）；只加 BGM/环境声。

【口径】
- 心易是水豚，不是蛋仔/猫耳；头顶橘子保留；只发“咔啵”，无其他词。
- 黄蛋保留黄身/奶油脸/棕眼/天线球/白袜白鞋；只换成短毛绒/毛毡质感，不改比例/五官。
- 黄蛋说话；不说“心易问”。
- 视频内无文字/气泡；字幕后期。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

ids_set = {n["id"] for n in nodes}
assert len(ids_set) == len(nodes)
by_id = {n["id"]: n for n in nodes}
edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
for n in nodes:
    if n["type"] not in ("gen-image", "gen-video"):
        continue
    mp = n["params"]["model_params"]
    refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
    ff = (mp.get("first_frame_image") or {}).get("node_id")
    for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
        assert tok in by_id, f"missing token {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff"
    for r in refs + ([ff] if ff else []):
        assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
    assert not mp.get("reference_audios"), "reference_audios must be empty"
    if n["type"] == "gen-video":
        assert 3 <= mp["duration"] <= 16
        assert ff in mp["prompt"]
for i, a in enumerate(groups):
    for b in groups[i + 1:]:
        ax, ay, aw, ah = a["bounds"].values()
        bx, by_, bw, bh = b["bounds"].values()
        if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
            raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
grouped = [i for g in groups for i in g["nodeIds"]]
assert sorted(grouped) == sorted(ids_set), "group coverage mismatch"

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
downloads = Path.home() / "Downloads" / OUT.name
shutil.copyfile(OUT, downloads)
print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
print("R01P", nid)
print("->", OUT)
print("->", downloads)

