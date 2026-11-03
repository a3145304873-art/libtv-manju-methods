# -*- coding: utf-8 -*-
"""Build narration + three-card tail version of the -like demo.

- 黄蛋 no longer speaks; 心易 only makes a sound at the tail.
- Narration is post-production voiceover.
- V1/V2/V3 4s each + 3s three-card tail (still) = 15s.
- Adds R02E eye reference; uses the user's three-card tail image as KC.

Output: 02_画布/EP02-like-narration-tail-v1.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP02-like-capybara-caption-plush-v1.monet"
OUT = HERE / "EP02-like-narration-tail-v1.monet"
EYE = json.loads((ROOT / "01_资产" / "角色" / "morose-refs-upload.json").read_text(encoding="utf-8"))["心易-水豚-眼睛参考"]
TAIL = json.loads((ROOT / "01_资产" / "道具" / "tail-upload.json").read_text(encoding="utf-8"))

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


ids = {}
for k, p in (("R00", "R00"), ("R01", "R01"), ("R02", "R02"), ("R01P", "R01P"),
             ("A01", "A01"), ("A02", "A02"), ("A03", "A03"), ("A04", "A04"),
             ("K_A", "K_A"), ("K_B", "K_B"), ("K_C", "K_C"), ("KC", "KC"),
             ("V1", "V1"), ("V2", "V2"), ("V3", "V3"), ("S0", "S0")):
    ids[k] = find(p)["id"]
by[ids["R01P"]]["meta"]["y"] = 900.0


def link(s):
    for k in list(ids):
        s = s.replace("[[" + k + "]]", "{{" + ids[k] + "}}")
    assert "[[" not in s
    return s


def input_image(key, label, info, x, y, width=300.0):
    nid = "node-" + hashlib.md5(("like-narration:v1:" + key).encode()).hexdigest()[:8]
    ids[key] = nid
    h = round(width * info["height"] / info["width"], 1)
    return {
        "id": nid, "type": "input-image", "mainOutputId": "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10],
        "meta": {"x": float(x), "y": float(y), "width": width, "height": h,
                 "label": label, "resourceType": None},
        "outputs": [{"id": "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10],
                     "status": "done", "error": None, "value": info["url"], "cover": None,
                     "name": info["name"], "resolution": {"width": info["width"], "height": info["height"]},
                     "source": None, "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": {"size": info["size"], "md5": info["md5"]}}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


# add R02E eye reference
r02e = input_image("R02E", "R02E 心易眼睛参考 · 白眼球＋深棕圈（锁眼）", EYE, 0, 1000)
nodes.append(r02e)
by[r02e["id"]] = r02e

# replace KC gen-image with the user's three-card tail still (same id, keep position)
kc = by[ids["KC"]]
kc["type"] = "input-image"
kc["mainOutputId"] = "output-" + hashlib.md5(b"KC-tail").hexdigest()[:10]
kc["meta"]["label"] = "KC 三卡尾 · rocklike/snakelike/doglike（用户图，后期用）"
kc["meta"]["width"] = 300.0
kc["meta"]["height"] = 169.0
kc["outputs"] = [{
    "id": kc["mainOutputId"], "status": "done", "error": None, "value": TAIL["url"],
    "cover": None, "name": TAIL["name"], "resolution": {"width": TAIL["width"], "height": TAIL["height"]},
    "source": None, "batchId": None, "execution": None, "graphRunId": None,
    "iterationPath": None, "taskSource": None, "taskId": None,
    "executorRunId": None, "stage": None, "deletedAt": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    "metadata": {"size": TAIL["size"], "md5": TAIL["md5"]},
}]
kc["params"] = None

EYE_TXT = "心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油色眼白、外圈粗深棕描边、内部没有黑瞳孔、没有棕色虹膜，像布偶刺绣/纽扣眼；不要黑豆眼/写实瞳孔/动漫高光）。"
KA = f"""16:9 电影感首帧，第0秒，只生成一张。小院石桌（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，手掌按在石桌上，摆“坚固”姿势；{EYE_TXT} 在画面右1/3，看向黄蛋。两人都不说话、嘴巴闭合；无文字、无气泡、无字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、角色说话、文字、气泡、字幕、logo、人类、比例失真、过曝。"""
KB = f"""16:9 电影感首帧，第0秒，只生成一张。小院花坛角（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，整条手臂做蛇形波浪；{EYE_TXT} 在画面右1/3，看向黄蛋；花丛里小蛇（参考 [[A03]]，圆头大眼、无尖牙）。两人都不说话、嘴巴闭合；无文字/气泡/字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、角色说话、文字、气泡、字幕、logo、恐怖蛇、尖牙、比例失真、过曝。"""
KC_P = f"""16:9 电影感首帧，第0秒，只生成一张。小院狗窝/门口角（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，拿着红色狗绳（参考 [[A01]]），另一只手轻指狗窝；{EYE_TXT} 在画面右1/3，看向黄蛋/金毛；狗窝旁坐着一只金毛（参考 [[A04]]，摇尾/吐舌）。两人都不说话、嘴巴闭合；无文字/气泡/字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、角色说话、文字、气泡、字幕、logo、人类、比例失真、过曝。"""
for key, prompt, refs in (
    ("K_A", KA, ["R00", "R01P", "R02", "R02E", "A02"]),
    ("K_B", KB, ["R00", "R01P", "R02", "R02E", "A02", "A03"]),
    ("K_C", KC_P, ["R00", "R01P", "R02", "R02E", "A01", "A02", "A04"]),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    n["outputs"] = []
    n["meta"]["label"] = {
        "K_A": "【待生成】K_A 首帧 · 石桌 · 两人不说话（锁眼）",
        "K_B": "【待生成】K_B 首帧 · 花坛 · 两人不说话（锁眼）",
        "K_C": "【待生成】K_C 首帧 · 狗窝 · 两人不说话（锁眼）",
    }[key]

V1 = f"""【风格】15s 旁白教学，横屏；小院石桌；**黄蛋不说话、心易不说话**；无文字/气泡；旁白后期加；镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；不说话，只做动作。{EYE_TXT} 不说话，只看/点头。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–4 秒：[[K_A]] 黄蛋手掌按石桌，摆“坚固”姿势，看向镜头/心易；心易看着石桌，点头。全程不说话、嘴巴闭合。
【声音】无角色人声；只有环境声；旁白后期。
负向：角色说话/对白/口型、文字、气泡、字幕、旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、logo、慢速横移、渐变、白场、过曝。"""
V2 = f"""【风格】15s 旁白教学，横屏；小院花坛；**黄蛋不说话、心易不说话**；无文字/气泡；旁白后期加；词间硬切。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：毛绒/毛毡；不说话，只做动作。{EYE_TXT} 不说话，只看/点头。
【场景】[[A02]] 小院花坛角，午后暖光；花丛里有小蛇（[[A03]]）。
0–4 秒：[[K_B]] 黄蛋整条手臂做蛇形波浪，指向花坛；小蛇从花丛滑出；心易看着花坛，点头。全程不说话、嘴巴闭合。
【声音】无角色人声；只有环境声；旁白后期。
负向：角色说话/对白/口型、文字、气泡、字幕、旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、logo、恐怖蛇、尖牙、慢速横移、渐变、白场、过曝。"""
V3 = f"""【风格】15s 旁白教学，横屏；小院狗窝；**黄蛋不说话、心易不说话**；无文字/气泡；旁白后期加；词间硬切。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：毛绒/毛毡；不说话，只做动作。{EYE_TXT} 不说话，只看/点头。
【场景】[[A02]] 小院狗窝/门口角，午后暖光。
0–4 秒：[[K_C]] 黄蛋拿着狗绳（[[A01]]），轻指狗窝；金毛（[[A04]]）摇尾/吐舌；心易看着金毛，点头。全程不说话、嘴巴闭合。
【声音】无角色人声；只有环境声；旁白后期。
负向：角色说话/对白/口型、文字、气泡、字幕、旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、logo、慢速横移、渐变、白场、过曝。"""
for key, prompt, refs, ff in (
    ("V1", V1, ["R00", "R01P", "R02", "R02E", "A02"], "K_A"),
    ("V2", V2, ["R00", "R01P", "R02", "R02E", "A02", "A03"], "K_B"),
    ("V3", V3, ["R00", "R01P", "R02", "R02E", "A01", "A02", "A04"], "K_C"),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    mp["first_frame_image"] = {"node_id": ids[ff]}
    mp["duration"] = 4
    mp["generate_audio"] = True
    n["outputs"] = []
    n["meta"]["label"] = {
        "V1": "【待生成】V1 · 4s · rocklike（两人不说话）",
        "V2": "【待生成】V2 · 4s · snakelike（两人不说话）",
        "V3": "【待生成】V3 · 4s · doglike（两人不说话）",
    }[key]
    assert len(mp["prompt"]) <= 1900

# groups
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {"id": "group-" + hashlib.md5(("like-narration:v1:group:" + key).encode()).hexdigest()[:8],
            "nodeIds": [ids[k] for k in keys],
            "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", ["R00", "R01", "R02", "R02E"], "#E68BB3"),
    group("g01", "01 黄蛋毛绒版 · 先跑", ["R01P"], "#D8A657"),
    group("g02", "02 道具/小院/小蛇/金毛", ["A01", "A02", "A03", "A04"], "#8E8DE0"),
    group("g03", "03 首帧 · K_A、K_B、K_C", ["K_A", "K_B", "K_C"], "#E8B85D"),
    group("g04", "04 视频 V1 · 4s · rocklike", ["V1"], "#DC775D"),
    group("g05", "05 视频 V2 · 4s · snakelike", ["V2"], "#DC775D"),
    group("g06", "06 视频 V3 · 4s · doglike", ["V3"], "#DC775D"),
    group("g07", "07 三卡尾/说明 · 后期", ["KC", "S0"], "#7FB07F"),
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
edges = [{"id": "edge-" + hashlib.md5((a + ">" + b).encode()).hexdigest()[:8],
          "sourceNodeId": a, "sourceHandle": "output",
          "targetNodeId": b, "targetHandle": "input",
          "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}
         for a, b in sorted(required)]
c["edges"] = edges
c["name"] = "蛋仔记单词 · -like 三词「旁白讲解＋三卡尾」v1 · 15s"

s0 = by[ids["S0"]]
s0["meta"]["x"] = 1160.0
s0["meta"]["y"] = 840.0
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词「旁白讲解＋三卡尾」：rocklike／snakelike／doglike，4＋4＋4＋3＝15s。
讲解＝旁白（后期）；黄蛋不说话；心易不说话，只在结尾“咔啵？”；三卡尾用 KC 用户图。

【跑序】
1. 修 R02（水豚）和 R02E（眼睛）为你当前账号可读；跨账号可能空。
2. 跑 R01P（黄蛋毛绒版）。
3. 跑 K_A / K_B / K_C。
4. 跑 V1 / V2 / V3（各 4s；两人不说话）。
5. 后期：V1+V2+V3 接三卡尾 KC（3s）；加旁白；结尾心易“咔啵？”。

【旁白稿】
V1：like 是“像”。一个词加 like，就是“像它一样”。rocklike：rock 是石头——像石头一样，坚固的。
V2：snakelike：snake 是蛇——像蛇一样，蜿蜒的。
V3：doglike：dog 是狗——像狗一样，忠诚的。
尾：你记住了吗？
（心易：咔啵？）

【口径】
- 黄蛋不说话、不对口型；心易不说话（结尾咔啵除外）。
- 视频内无文字/气泡；三卡尾是后期静帧。
- 心易眼睛按 R02E：白色/奶油眼白＋粗深棕圈，无黑瞳孔/无棕色虹膜。
- R02/R02E 跨账号可能空；空就手动替换。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# validate
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
        assert tok in by_id, f"missing {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff"
    for r in refs + ([ff] if ff else []):
        assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
    assert not mp.get("reference_audios")
    if n["type"] == "gen-video":
        assert ff in mp["prompt"]
for i, a in enumerate(groups):
    for b in groups[i + 1:]:
        ax, ay, aw, ah = a["bounds"].values()
        bx, by_, bw, bh = b["bounds"].values()
        if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
            raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
grouped = [i for g in groups for i in g["nodeIds"]]
assert sorted(grouped) == sorted(ids_set)

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
print("->", OUT)



