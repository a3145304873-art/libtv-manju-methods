# -*- coding: utf-8 -*-
"""Build v6: clean R02 (single capybara + face ref), 心易 praise, tail-frame chain.

Based on the user's generated v5 file. Preserves A01–A04, R01P, KC.
- R02: keep only the single capybara output; add R02F face/eye reference.
- K_A: exact eyes; V1 first frame.
- T_A/T_B: placeholders for V1/V2 last frames; V2/V3 first frames.
- V1/V2 end with a walk to the next corner; 心易 praises with a happy "咔啵";
  黄蛋 no longer says 真不错/真棒.
- Video has no text; praise bubbles/subtitles post.

Output: 02_画布/EP02-like-capybara-tail-v1.monet
"""
import hashlib
import json
import os
import re
import shutil
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = Path(r"C:\Users\N31738\Downloads\蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·后期白字」v1 · 15s.monet")
OUT = HERE / "EP02-like-capybara-tail-v1.monet"
TA_SRC = HERE / "EP01-morose-v1.monet"

d = json.loads(SRC.read_text(encoding="utf-8-sig"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}

# find IDs by label
def find(sub, start=True):
    for n in nodes:
        lab = n["meta"].get("label", "")
        if (lab.startswith(sub) if start else sub in lab):
            return n
    raise SystemExit(f"missing {sub}")

R00 = find("R00")
R01 = find("R01")
R02 = find("R02")
R01P = find("【待生成】R01P")
A01 = find("【已生成】A01")
A02 = find("【已生成】A02")
A03 = find("【已生成】A03")
A04 = find("【已生成】A04")
KA = find("【待生成】K_A")
KC = find("【已生成】KC")
V1 = find("【待生成】V1")
V2 = find("【待生成】V2")
V3 = find("【待生成】V3")
S0 = find("S0")
KB = find("【待生成】K_B")
KC_FRAME = find("【待生成】K_C")
IMG = find("image.png")

ids = {k: v["id"] for k, v in {
    "R00": R00, "R01": R01, "R02": R02, "R01P": R01P,
    "A01": A01, "A02": A02, "A03": A03, "A04": A04,
    "K_A": KA, "KC": KC, "V1": V1, "V2": V2, "V3": V3, "S0": S0,
}.items()}

# R02: keep only the single capybara output
r02 = R02
assert r02["outputs"], "R02 no outputs"
r02["outputs"] = [r02["outputs"][0]]
r02["meta"]["label"] = "R02 心易·水豚（单图锁定）"

# R02F face/eye reference
FACE_URL = "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-04cc34bdc4/image/20261102-065612-d1b27798ec4a1cfa-e5-bf-83-e6-98-93-e6-b0-b4-e8-b1-9a-e8-8.png"
def input_node(key, label, url, name, w, h, size, md5, x, y, disp_w):
    nid = "node-" + hashlib.md5(("capybara-tail:v1:" + key).encode()).hexdigest()[:8]
    oid = "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10]
    return {
        "id": nid, "type": "input-image", "mainOutputId": oid,
        "meta": {"x": float(x), "y": float(y), "width": float(disp_w), "height": round(disp_w * h / w, 1),
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": url, "cover": None,
            "name": name, "resolution": {"width": w, "height": h}, "source": None,
            "batchId": None, "execution": None, "graphRunId": None, "iterationPath": None,
            "taskSource": None, "taskId": None, "executorRunId": None, "stage": None,
            "deletedAt": None, "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW,
            "updatedBy": AUTHOR, "metadata": {"size": size, "md5": md5},
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

r02f = input_node("R02F", "R02F 心易脸部/眼睛参考（白底黑瞳）", FACE_URL, "心易-水豚-脸部.png",
                  430, 720, 381918, "bd9fb2dfcf53e20eff8e0453ec5e7763", 0, 1010, 220)
ids["R02F"] = r02f["id"]
nodes.append(r02f)
by[r02f["id"]] = r02f

# T_A / T_B placeholders: copy the existing T_A placeholder from EP01
ta_canvas = json.loads(TA_SRC.read_text(encoding="utf-8-sig"))["canvas"]
ta_node = next(n for n in ta_canvas["nodes"] if "T_A" in n["meta"].get("label", ""))
ta_out = json.loads(json.dumps(ta_node["outputs"][0]))
ta_url = ta_out["value"]
ta_res = ta_out["resolution"]
ta_meta = ta_out.get("metadata") or {}
ta_name = ta_out.get("name", "T_A-占位-1280x720.jpg")

def ta_node(key, label, y):
    nid = "node-" + hashlib.md5(("capybara-tail:v1:" + key).encode()).hexdigest()[:8]
    oid = "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10]
    out = json.loads(json.dumps(ta_out)); out["id"] = oid
    out["createdAt"] = NOW; out["updatedAt"] = NOW; out["createdBy"] = AUTHOR; out["updatedBy"] = AUTHOR
    return {
        "id": nid, "type": "input-image", "mainOutputId": oid,
        "meta": {"x": 1140.0, "y": float(y), "width": 300.0, "height": 168.75,
                 "label": label, "resourceType": None},
        "outputs": [out], "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

t_a = ta_node("T_A", "【待替换⚠】T_A V1 尾帧 → V2 首帧（截 V1 最后一帧替换）", 800)
t_b = ta_node("T_B", "【待替换⚠】T_B V2 尾帧 → V3 首帧（截 V2 最后一帧替换）", 1000)
ids["T_A"] = t_a["id"]; ids["T_B"] = t_b["id"]
nodes.extend([t_a, t_b]); by[t_a["id"]] = t_a; by[t_b["id"]] = t_b

# Remove K_B / K_C / image.png
remove = {KB["id"], KC_FRAME["id"], IMG["id"]}
nodes[:] = [n for n in nodes if n["id"] not in remove]
for i in remove:
    by.pop(i, None)

# K_A prompt: exact eyes
ka_prompt = """16:9 电影感首帧，第0秒，只生成一张。小院石桌角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，从石桌后探出半个身子，头顶橘子；**眼睛必须严格参考 [[R02F]]：白色圆形眼白、黑色小圆瞳、单个高光；不要眼皮、不要眉毛、不要放大瞳孔、不要拟人化眼神**；黄蛋（参考 [[R01P]]，毛绒黄蛋）在画面右1/3，看向心易。无气泡、无文字、无字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧心易/粉蛋/猫耳/天线、眼皮、眉毛、放大瞳孔、大眼珠、拟人化眼神、气泡、文字、字幕、logo、人类、比例失真、过曝。"""
mp = KA["params"]["model_params"]
mp["prompt"] = ka_prompt.replace("[[A02]]", "{{" + ids["A02"] + "}}").replace("[[R02]]", "{{" + ids["R02"] + "}}").replace("[[R02F]]", "{{" + ids["R02F"] + "}}").replace("[[R01P]]", "{{" + ids["R01P"] + "}}")
mp["reference_images"] = [{"node_id": ids[k]} for k in ("R00", "R01P", "R02", "R02F", "A02")]
KA["outputs"] = []
KA["meta"]["label"] = "【待生成】K_A 首帧 · 石桌 · 水豚（锁眼）＋毛绒黄蛋"

# V1: praise by 心易; walk to flower bed; first frame K_A
v1 = """【风格】15s 快问快答，横屏；小院石桌角；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡，白字/气泡后期加；结尾走向花坛。
【角色】心易（参考 [[K_A]] 中的水豚）：棕色水豚/卡皮巴拉毛绒玩偶，奶油色大脸板、橘色腮红、小棕耳、一字嘴、白肚、棕色短手短脚、奶油色脚踝、头顶橘子；**眼睛严格按 [[R02F]]：白色圆眼白、黑色小圆瞳、单个高光；不要眼皮/眉毛/放大瞳孔/拟人化**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[K_A]]=首帧；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A02]]=小院；[[R02F]]=眼睛参考。
0–1.5 秒：心易看镜头/黄蛋，发“咔啵。”（平调）；黄蛋看心易。
1.5–3.8 秒：黄蛋：“rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌。
3.8–4.6 秒：心易发“咔啵！”（开心、短促，像“真不错！”）；黄蛋点头，**黄蛋不说“真不错”**。
4.6–6 秒：黄蛋：“snakelike——”两人转身朝花坛走；镜尾停在**花坛入口**，黄蛋/心易在画面里，背景能看到花坛。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""
v2 = """【风格】4s 快问快答，横屏；花坛入口；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡；结尾走向狗窝。
【角色】心易（参考 [[T_A]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；**眼睛严格按 [[R02F]]：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[T_A]]=首帧（必须从该帧完全接续，不要重新构图）；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A02]]=小院；[[A03]]=小蛇；[[R02F]]=眼睛参考。
0–0.5 秒：从 T_A 花坛入口开始；心易发“咔啵？”（升调）。
0.5–2.6 秒：黄蛋：“snake 是蛇——snakelike 就是像蛇一样，蜿蜒的！”心易整臂蛇形；小蛇从花丛滑出。
2.6–3.2 秒：心易发“咔啵！”（开心、短促，像“真棒！”）；黄蛋点头，**黄蛋不说“真棒”**。
3.2–4 秒：黄蛋：“doglike——”两人转身朝狗窝走；镜尾停在**狗窝入口**。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、恐怖蛇、尖牙、慢速横移、渐变、白场、过曝、漂浮。"""
v3 = """【风格】5s 快问快答，横屏；狗窝入口；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡；结尾三卡/“你记住了多少？”
【角色】心易（参考 [[T_B]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；**眼睛严格按 [[R02F]]：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[T_B]]=首帧（必须从该帧完全接续）；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A01]]=狗绳/词卡；[[A02]]=小院；[[A04]]=金毛；[[KC]]=三张词卡版式；[[R02F]]=眼睛参考。
0–0.5 秒：从 T_B 狗窝入口开始；心易发“咔啵？”（升调）。
0.5–2.6 秒：黄蛋：“dog 是狗——doglike 就是像狗一样，忠诚的！”心易拿狗绳；金毛摇尾。
2.6–3.2 秒：心易发“咔啵！”（开心、短促，像“真棒！”）；黄蛋点头，**黄蛋不说“真棒”**。
3.2–4.2 秒：黄蛋：“你记住了多少？”心易指桌上的三张卡（[[KC]] 版式）。
4.2–5 秒：三卡定格；心易点头；镜尾定格。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""

for key, prompt, dur, refs, ff in (
    ("V1", v1, 6, ["R00", "R01P", "A02", "K_A", "R02F"], "K_A"),
    ("V2", v2, 4, ["R00", "R01P", "A02", "A03", "T_A", "R02F"], "T_A"),
    ("V3", v3, 5, ["R00", "R01P", "A01", "A02", "A04", "KC", "T_B", "R02F"], "T_B"),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    toks = {k: "{{" + ids[k] + "}}" for k in refs + [ff]}
    p = prompt
    for k, v in toks.items():
        p = p.replace("[[" + k + "]]", v)
    assert "[[" not in p, f"leftover token in {key}: {p[:80]}"
    mp["prompt"] = p
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    mp["first_frame_image"] = {"node_id": ids[ff]}
    mp["duration"] = dur
    mp["generate_audio"] = True
    n["outputs"] = []
    n["meta"]["label"] = {
        "V1": "【待生成】V1 · 6s · rocklike＋心易夸＋走向花坛",
        "V2": "【待生成】V2 · 4s · snakelike＋心易夸＋走向狗窝（首帧 T_A）",
        "V3": "【待生成】V3 · 5s · doglike＋心易夸＋三卡（首帧 T_B）",
    }[key]
    assert len(p) <= 1900, (key, len(p))

# Groups
by[ids["S0"]]["meta"]["y"] = 1300.0
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {
        "id": "group-" + hashlib.md5(("capybara-tail:v1:group:" + key).encode()).hexdigest()[:8],
        "nodeIds": [ids[k] for k in keys],
        "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

groups = [
    group("g00", "00 参考素材 · 黄蛋/黄蛋毛绒/水豚/脸部", ["R00", "R01", "R02", "R02F"], "#E68BB3"),
    group("g01", "01 道具/小院/小蛇/金毛/毛绒黄蛋", ["A01", "A02", "A03", "A04", "R01P"], "#8E8DE0"),
    group("g02", "02 首帧/尾帧/词卡 · K_A、T_A、T_B、KC", ["K_A", "T_A", "T_B", "KC"], "#E8B85D"),
    group("g03", "03 视频 V1 · 6s · rocklike＋走向花坛", ["V1"], "#DC775D"),
    group("g04", "04 视频 V2 · 4s · snakelike＋走向狗窝", ["V2"], "#DC775D"),
    group("g05", "05 视频 V3 · 5s · doglike＋三卡", ["V3"], "#DC775D"),
    group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
]
c["groups"] = groups

# S0
s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词样片「水豚心易＋毛绒黄蛋·尾帧链」：rocklike／snakelike／doglike，6＋4＋5＝15s。
心易＝棕色水豚，只发“咔啵”；黄蛋＝毛绒黄蛋，说话；视频内无文字/气泡；白字/夸赞气泡后期加。
A01–A04、R01P、KC 已生成保留；R02 只保留单图，R02F 锁眼睛；K_B/K_C 删除，改 T_A/T_B 尾帧链。

【跑序】
1. 跑 K_A（锁眼首帧）。
2. 跑 V1（6s）；截 V1 最后一帧，替换 T_A。
3. 跑 V2（4s，首帧 T_A）；截 V2 最后一帧，替换 T_B。
4. 跑 V3（5s，首帧 T_B）。
5. 后期：加心易夸赞气泡（真不错/真棒）＋横排白字字幕；只加 BGM/环境声。

【口径】
- 心易是水豚，不是蛋仔/猫耳；头顶橘子保留；只发“咔啵”，无其他词。
- 眼睛严格按 R02F：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔/拟人化。
- 夸赞由心易发“咔啵！”（开心、短促）；黄蛋不再说“真不错/真棒”。
- V1 结尾走到花坛入口；V2 结尾走到狗窝入口；T_A/T_B 必须用真实尾帧替换。
- 视频内无文字/气泡；字幕/夸赞气泡后期。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# Edges
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
    "id": "edge-" + hashlib.md5((a + ">" + b).encode()).hexdigest()[:8],
    "sourceNodeId": a, "sourceHandle": "output",
    "targetNodeId": b, "targetHandle": "input",
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
} for a, b in sorted(required)]
c["edges"] = edges
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·尾帧链」v1 · 15s"

# Validate
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
print("prompts", {k: len(by[ids[k]]["params"]["model_params"]["prompt"]) for k in ("K_A", "V1", "V2", "V3")})
print("->", OUT)
print("->", downloads)





