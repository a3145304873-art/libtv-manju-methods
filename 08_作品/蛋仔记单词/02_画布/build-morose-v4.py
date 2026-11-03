# -*- coding: utf-8 -*-
"""Build morose v4: narration-only + three-card tail.

- 黄蛋 does not speak; 心易 does not speak (only "咔啵?" over the tail still).
- V1 8s + V2 9s (T_A chain) + 3s three-card tail = 20s.
- Adds KC tail input still (morose / 没肉丝 / 郁闷的).

Output: 02_画布/EP01-morose-meme-v4.monet
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
SRC = HERE / "EP01-morose-meme-v3.monet"
OUT = HERE / "EP01-morose-meme-v4.monet"
TAIL = json.loads((ROOT / "01_资产" / "道具" / "morose-tail-upload.json").read_text(encoding="utf-8"))

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


ids = {}
for k, p in (("R00", "R00"), ("R01", "R01"), ("R02", "R02"), ("R02E", "R02E"), ("R01P", "R01P"),
             ("A02", "A02"), ("A05", "A05"), ("K_A", "K_A"), ("T_A", "T_A 占位"),
             ("V1", "V1"), ("V2", "V2"), ("S0", "S0")):
    ids[k] = find(p)["id"]


def link(s):
    for k in list(ids):
        s = s.replace("[[" + k + "]]", "{{" + ids[k] + "}}")
    assert "[[" not in s
    return s


def input_image(key, label, info, x, y, width=300.0):
    nid = "node-" + hashlib.md5(("egg-morose-meme:v4:" + key).encode()).hexdigest()[:8]
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


kc = input_image("KC", "KC 三卡尾 · morose / 没肉丝 / 郁闷的（后期用）", TAIL, 1160, 640)
nodes.append(kc)
by[kc["id"]] = kc

EYE = "心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油色眼白、外圈粗深棕描边、内部没有黑瞳孔、没有棕色虹膜，像布偶刺绣/纽扣眼；不要黑豆眼/写实瞳孔/动漫高光）。"
V1 = f"""【风格】20s 玩梗记单词，横屏；小院石桌；**黄蛋不说话、心易不说话**；无文字/无气泡；旁白后期加。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；不说话，只做动作。{EYE} 不说话，只看/点头。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–2 秒：[[K_A]] 黄蛋双手打开餐盒，眼睛发亮；心易看餐盒。两人不说话。
2–4 秒：黄蛋看到只有青椒，愣住；拿勺子拨找。不说话。
4–6 秒：黄蛋继续拨找，肩膀慢慢垮下。不说话。
6–8 秒：黄蛋趴到桌边，**保持趴桌姿势 1 秒，镜尾稳定**，给 V2 接尾帧。
【声音】无角色人声；只有餐盒/勺子环境声；旁白后期。
负向：角色说话/对白/口型、视频内文字/气泡/字幕、黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""
V2 = f"""【风格】20s 玩梗记单词，横屏；小院石桌；**黄蛋不说话、心易不说话**；无文字/无气泡；旁白后期加。**首帧＝T_A**：必须从 V1 最后一帧继续，不能换机位/不能重摆/不能换光。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；不说话，只做动作。{EYE} 不说话，只看/点头。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；与 T_A 同一位置/光线/构图。
0–3 秒：[[T_A]] 黄蛋从趴桌姿势慢慢抬头，闷闷不乐；心易看他。不说话。
3–5 秒：黄蛋坐直一点，看向餐盒；心易点头。不说话。
5–7 秒：黄蛋指了指餐盒里的青椒丝；心易看餐盒。不说话。
7–9 秒：黄蛋看镜头；镜尾定格 1s。不说话。
【声音】无角色人声；只有环境声；旁白后期。
负向：角色说话/对白/口型、视频内文字/气泡/字幕、黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、换机位/重摆/换光、慢速横移、渐变、白场、过曝。"""
for key, prompt, dur in (("V1", V1, 8), ("V2", V2, 9)):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["duration"] = dur
    n["outputs"] = []
    n["meta"]["label"] = {
        "V1": "【待生成】V1 · 8s · 打开餐盒/没肉丝（两人不说话）",
        "V2": "【待生成】V2 · 9s · 郁闷的（首帧＝T_A，两人不说话）",
    }[key]
    assert len(mp["prompt"]) <= 1900

by[ids["S0"]]["meta"]["x"] = 1160.0
by[ids["S0"]]["meta"]["y"] = 840.0


def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {"id": "group-" + hashlib.md5(("egg-morose-meme:v4:group:" + key).encode()).hexdigest()[:8],
            "nodeIds": [ids[k] for k in keys],
            "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", ["R00", "R01", "R02", "R02E"], "#E68BB3"),
    group("g01", "01 黄蛋毛绒版 · 先跑", ["R01P"], "#D8A657"),
    group("g02", "02 小院/餐盒 · 先跑", ["A02", "A05"], "#8E8DE0"),
    group("g03", "03 首帧/尾帧 · K_A、T_A", ["K_A", "T_A"], "#E8B85D"),
    group("g04", "04 视频 V1 · 8s · 没肉丝", ["V1"], "#DC775D"),
    group("g05", "05 视频 V2 · 9s · 郁闷的", ["V2"], "#DC775D"),
    group("g06", "06 三卡尾/说明 · 后期", ["KC", "S0"], "#7FB07F"),
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
c["name"] = "蛋仔记单词 · 玩梗样片「morose＝没肉丝」v4 · 20s（旁白＋三卡尾）"

s0 = by[ids["S0"]]
s0["meta"]["x"] = 1160.0
s0["meta"]["y"] = 840.0
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》玩梗样片 v4：morose = 没肉丝 → 郁闷的。20s。
V1 8s + V2 9s（T_A 接尾帧）+ 三卡尾静帧 3s。
黄蛋不说话；心易不说话；讲解＝旁白后期；结尾心易“咔啵？”。

【跑序】
1. 修 R02（水豚）/R02E（眼睛）为你当前账号可读。
2. 跑 R01P（黄蛋毛绒版）。
3. 跑 A05（餐盒，无肉丝）。
4. 跑 K_A；看眼睛、两人闭嘴。
5. 跑 V1（8s）；结尾黄蛋趴桌稳定 1 秒。
6. 截 V1 最后一帧，替换 T_A。
7. 跑 V2（9s，首帧＝T_A）。
8. 后期：V1+V2 → 三卡尾 KC（3s）；加旁白；结尾心易“咔啵？”。

【旁白稿】
V1：morose。黄蛋点了青椒肉丝饭。打开一看——只有青椒，没有肉丝。
V2：没肉丝，所以 morose——郁闷的。morose，闷闷不乐的。
尾：你记住了吗？（心易：咔啵？）

【口径】
- 黄蛋不说话、不对口型；心易不说话（结尾咔啵除外）。
- 视频内无文字/气泡；三卡尾是后期静帧。
- 心易眼睛按 R02E：白/奶油眼白＋粗深棕圈，无黑瞳孔/无棕色虹膜。
- R02/R02E 跨账号可能空；空就手动替换。
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
    if "V2" in n["meta"].get("label", ""):
        for line in mp["prompt"].splitlines():
            if "{{" in line:
                print("V2LINE", line)
    for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
        assert tok in by_id, f"missing {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n[chr(109)+chr(101)+chr(116)+chr(97)].get(chr(108)+chr(97)+chr(98)+chr(101)+chr(108))}"
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




