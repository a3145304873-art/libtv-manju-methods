# -*- coding: utf-8 -*-
"""Build capybara 心易 + in-video floating-bubble demo from the user's generated v3.

Preserves A01–A04 and KC generated outputs; replaces 心易 with the brown capybara;
adds A05 (white 3D bubble reference); rebuilds K_A/K_B/K_C and V1/V2/V3 as a
15s fast Q&A (6+4+5), with floating bubbles inside the video (no post overlays).

Output: 02_画布/EP02-like-capybara-bubble-v1.monet
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
SRC = Path(r"C:\Users\N31738\Downloads\蛋仔记单词 · -like 三词样片「蛋仔的小院」v3 · 基于已生成素材（8＋8＋10s）.monet")
OUT = HERE / "EP02-like-capybara-bubble-v1.monet"

CAPY_URL = "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-d240c8bf55/image/20261102-032549-6dfb56a52913e945-e5-bf-83-e6-98-93-e6-b0-b4-e8-b1-9a-e6-a.png"
CAPY_MD5 = "100cfe8f4f09ec467008f61a0ab30d7d"

d = json.loads(SRC.read_text(encoding="utf-8-sig"))
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
for key, val in ids.items():
    assert val in by, f"missing node {key} {val}"
print("ids", ids)


def link(text: str) -> str:
    def repl(m):
        k = m.group(1)
        assert k in ids, f"unknown token {k}"
        return "{{" + ids[k] + "}}"
    text = re.sub(r"\[\[([A-Z0-9_]+)\]\]", repl, text)
    assert "[[" not in text, f"leftover token: {text[:80]}"
    return text


# 1) R02: capybara, permanent URL
r02 = by[ids["R02"]]
r02["meta"]["label"] = "R02 心易·水豚（Monet 永久 URL）"
o = r02["outputs"][0]
o["value"] = CAPY_URL
o["name"] = "心易-水豚-标准.png"
o["resolution"] = {"width": 400, "height": 600}
o["metadata"] = {"size": 258953, "md5": CAPY_MD5}
o["updatedAt"] = NOW
o["updatedBy"] = AUTHOR
r02["meta"]["width"] = 280.0
r02["meta"]["height"] = 420.0

# 2) A05: floating bubble reference (new, no R02)
a05_id = "node-" + hashlib.md5(("capybara-bubble:v1:A05").encode("utf-8")).hexdigest()[:8]
a05 = {
    "id": a05_id, "type": "gen-image", "mainOutputId": None,
    "meta": {"x": 360.0, "y": 800.0, "width": 300.0, "height": 170.0,
             "label": "【待生成】A05 浮动气泡参考 · 白色3D气泡（?）", "resourceType": None},
    "outputs": [],
    "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
        "prompt": "16:9 纯白底道具设定图，只生成一个白色 3D 对话气泡：圆角、软阴影、尾巴朝左下；气泡里只有一个黑色大问号“?”，无其他文字/图案；3D卡通渲染+搪胶材质，轻微高光；无角色、无手、无 logo。负向：文字、多个气泡、角色、手、彩色、logo、水印。",
        "reference_images": [], "aspect_ratio": "16:9", "image_size": "1K",
        "width": 1024, "height": 1024, "quality": "medium",
        "output_format": "png", "moderation": "low", "auto_compress": True,
    }},
    "specialParams": None, "config": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
}
ids["A05"] = a05_id
nodes.append(a05)
by[a05_id] = a05

# 3) K frames: capybara + floating bubble
ka_prompt = """16:9 电影感首帧，第0秒，只生成一张。小院石桌角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在石桌旁，头顶橘子；她头右上浮一个白色3D对话气泡（参考 [[A05]]），气泡里只有一个大问号“?”，尾巴指向她；心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，看向心易/气泡。低机位，午后暖光，3D卡通+真实光影（皮克斯/搪胶）。
无其他文字/字幕/logo；气泡里只有“?”。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字、字幕、logo、人类、比例失真、过曝。"""
kb_prompt = """16:9 电影感首帧，第0秒，只生成一张。小院花坛角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在花坛旁；她头右上浮一个白色3D对话气泡（参考 [[A05]]），气泡里只有一个大问号“?”，尾巴指向她；心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，看向花坛/气泡；花丛里有小蛇（参考 [[A03]]，圆头大眼、无尖牙、可爱）。低机位，午后暖光，3D卡通+真实光影。
无其他文字/字幕/logo；气泡里只有“?”。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字、字幕、logo、人类、恐怖蛇、尖牙、比例失真、过曝。"""
kc_prompt = """16:9 电影感首帧，第0秒，只生成一张。小院狗窝/门口角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在狗窝旁；她头右上浮一个白色3D对话气泡（参考 [[A05]]），气泡里只有一个大问号“?”，尾巴指向她；心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，拿着红色狗绳（参考 [[A01]]），看向心易/气泡；狗窝旁坐着一只金毛（参考 [[A04]]，摇尾/吐舌）。低机位，午后暖光，3D卡通+真实光影。
无其他文字/字幕/logo；气泡里只有“?”。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字、字幕、logo、人类、比例失真、过曝。"""

for key, prompt, refs in (
    ("K_A", ka_prompt, ["R00", "R01", "R02", "A02", "A05"]),
    ("K_B", kb_prompt, ["R00", "R01", "R02", "A02", "A03", "A05"]),
    ("K_C", kc_prompt, ["R00", "R01", "R02", "A01", "A02", "A04", "A05"]),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    n["outputs"] = []
    n["meta"]["label"] = {
        "K_A": "【待生成】K_A 首帧 · 石桌 · 水豚心易+浮动气泡（?）",
        "K_B": "【待生成】K_B 首帧 · 花坛 · 水豚心易+浮动气泡（?）",
        "K_C": "【待生成】K_C 首帧 · 狗窝 · 水豚心易+浮动气泡（?）",
    }[key]

# 4) V1/V2/V3: fast Q&A 6+4+5s
v1_prompt = """【风格】15s 快问快答，横屏；小院石桌角；心易只发“咔啵”，不说话、无其他词；黄蛋说话；白色3D气泡在画面里，不后期。镜头快推/短甩/急停，词间硬切。
【角色】心易（参考 [[K_A]] 中的水豚）：棕色水豚/卡皮巴拉毛绒玩偶，奶油色大脸板、橘色腮红、小棕耳、一字嘴、白肚、棕色短手短脚、奶油色脚踝、头顶橘子＋绿叶；只发“咔啵”（升调疑问/降调收到），嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔，黄色蛋壳、奶油色脸板、棕眼、短圆手无手指、白袜白靴；说话的人。
【气泡】白色3D对话气泡，里面只有一个“?”；保持在心易头右上，不遮脸；不要换成文字/表情/多个气泡。
【图片引用】[[K_A]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A02]]=小院。
0–2 秒：黄蛋：“like 是‘像’。一个词加 like，就是‘像它一样’。”
2–2.8 秒：心易：“咔啵？”（升调、歪头；气泡“?”）黄蛋看气泡。
2.8–5.2 秒：黄蛋：“rocklike？rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌；心易点头。
5.2–6 秒：黄蛋：“真不错！snakelike——”心易转头；镜尾硬切。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""
v2_prompt = """【风格】4s 快问快答，横屏；小院花坛角；心易只发“咔啵”，不说话；黄蛋说话；白色3D气泡在画面里，不后期；词间硬切。
【角色】心易（参考 [[K_B]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；只发“咔啵”，嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔；说话的人。
【气泡】白色3D气泡里只有一个“?”；在心易头右上，不遮脸。
【图片引用】[[K_B]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A02]]=小院；[[A03]]=小蛇。
0–0.8 秒：心易：“咔啵？”（升调、歪头；气泡“?”）
0.8–3.2 秒：黄蛋：“snakelike？snake 是蛇——snakelike 就是像蛇一样，蜿蜒的！”心易整臂蛇形；小蛇从花丛滑出。
3.2–4 秒：黄蛋：“真棒！doglike——”心易转头；镜尾硬切。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字、logo、恐怖蛇、尖牙、慢速横移、渐变、白场、过曝、漂浮。"""
v3_prompt = """【风格】5s 快问快答，横屏；小院狗窝/门口角；心易只发“咔啵”，不说话；黄蛋说话；白色3D气泡在画面里，不后期；结尾三卡复习。
【角色】心易（参考 [[K_C]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；只发“咔啵”，嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔；说话的人。
【气泡】白色3D气泡里只有一个“?”；在心易头右上，不遮脸；结尾不换成文字。
【图片引用】[[K_C]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A01]]=狗绳/词卡；[[A02]]=小院；[[A04]]=金毛；[[KC]]=三张词卡版式。
0–0.8 秒：心易：“咔啵？”（升调、歪头；气泡“?”）
0.8–3.2 秒：黄蛋：“doglike？dog 是狗——doglike 就是像狗一样，忠诚的！”心易拿狗绳；金毛摇尾。
3.2–4.2 秒：黄蛋：“你记住了多少？”心易指桌上的三张卡（[[KC]] 版式）。
4.2–5 秒：三卡定格；心易点头；镜尾定格。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""

for key, prompt, dur, refs in (
    ("V1", v1_prompt, 6, ["R00", "R01", "A02", "K_A"]),
    ("V2", v2_prompt, 4, ["R00", "R01", "A02", "A03", "K_B"]),
    ("V3", v3_prompt, 5, ["R00", "R01", "A01", "A02", "A04", "KC", "K_C"]),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    mp["first_frame_image"] = {"node_id": ids["K_A" if key == "V1" else "K_B" if key == "V2" else "K_C"]}
    mp["duration"] = dur
    mp["generate_audio"] = True
    n["outputs"] = []
    n["meta"]["label"] = {
        "V1": "【待生成】V1 · 6s · 快问快答 · rocklike（水豚+浮动气泡）",
        "V2": "【待生成】V2 · 4s · 快问快答 · snakelike",
        "V3": "【待生成】V3 · 5s · 快问快答 · doglike＋三卡收尾",
    }[key]
    assert len(mp["prompt"]) <= 1900, (key, len(mp["prompt"]))

# 5) A01–A04/KC labels: generated
for key in ("A01", "A02", "A03", "A04", "KC"):
    n = by[ids[key]]
    if n.get("outputs"):
        n["meta"]["label"] = n["meta"]["label"].replace("【待生成】", "【已生成】", 1)

# 6) S0
s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词样片「水豚心易·气泡版」：rocklike／snakelike／doglike，6＋4＋5＝15s。
心易＝棕色水豚，只发“咔啵”；黄蛋说话；白色3D浮动气泡在视频里，不后期。
A01–A04、KC 已生成保留；K/V 用新水豚重生成。

【跑序】
1. 先跑 A05 浮动气泡参考（白底、一个“?”）。
2. 跑 K_A / K_B / K_C；首帧应带水豚心易＋气泡“?”。
3. 跑 V1（6s）/ V2（4s）/ V3（5s）；气泡在画面里，不做后期。
4. 后期只加 BGM/环境声；不要贴气泡、不要贴词卡。

【口径】
- 心易是水豚，不是蛋仔/猫耳；头顶橘子保留；只发“咔啵”，无其他词。
- 黄蛋说话；不说“心易问”，直接答气泡。
- 气泡只放“?”；不写英文长句；英文单词由黄蛋说。
- V3 最后三卡复习用 KC 版式；卡面文字在视频里。
- 若模型给心易加词/气泡变字：重跑；不改后期。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# 7) Remove G01
g01_id = next((n["id"] for n in nodes if "G01" in n["meta"].get("label", "")), None)
if g01_id:
    nodes[:] = [n for n in nodes if n["id"] != g01_id]
    by.pop(g01_id, None)

# 8) Groups
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {
        "id": "group-" + hashlib.md5(("capybara-bubble:v1:group:" + key).encode("utf-8")).hexdigest()[:8],
        "nodeIds": [ids[k] for k in keys],
        "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚心易/比例", ["R00", "R01", "R02"], "#E68BB3"),
    group("g01", "01 道具/小院/小蛇/金毛/气泡 · 先跑", ["A01", "A02", "A03", "A04", "A05"], "#8E8DE0"),
    group("g02", "02 首帧/词卡 · K_A、K_B、K_C、KC", ["K_A", "K_B", "K_C", "KC"], "#E8B85D"),
    group("g03", "03 视频 V1 · 6s · rocklike", ["V1"], "#DC775D"),
    group("g04", "04 视频 V2 · 4s · snakelike", ["V2"], "#DC775D"),
    group("g05", "05 视频 V3 · 5s · doglike＋收尾", ["V3"], "#DC775D"),
    group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
]
c["groups"] = groups

# 9) Edges exact from refs/ff
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
edges = []
for a, b in sorted(required):
    edges.append({
        "id": "edge-" + hashlib.md5((a + ">" + b).encode("utf-8")).hexdigest()[:8],
        "sourceNodeId": a, "sourceHandle": "output",
        "targetNodeId": b, "targetHandle": "input",
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    })
c["edges"] = edges
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易·气泡版」v1 · 15s"

# 10) Validate
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
print("prompts", {k: len(by[ids[k]]["params"]["model_params"]["prompt"]) for k in ("K_A", "K_B", "K_C", "V1", "V2", "V3")})
print("->", OUT)
print("->", downloads)

