# -*- coding: utf-8 -*-
"""Build text-bubble version from the capybara floating-bubble canvas.

Bubble = 心易's words: first line the English word, second line 是什么意思？
Adds A05_R / A05_S / A05_D as exact bubble references; K/V use text bubbles
inside the video (no post overlays). Preserves A01–A04 and KC outputs.

Output: 02_画布/EP02-like-capybara-bubble-text-v1.monet
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
SRC = HERE / "EP02-like-capybara-bubble-v1.monet"
OUT = HERE / "EP02-like-capybara-bubble-text-v1.monet"

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
old_a05 = next(n["id"] for n in nodes if "A05" in n["meta"].get("label", ""))
print("old A05", old_a05)


def link(text: str) -> str:
    def repl(m):
        k = m.group(1)
        assert k in ids, f"unknown token {k}"
        return "{{" + ids[k] + "}}"
    text = re.sub(r"\[\[([A-Z0-9_]+)\]\]", repl, text)
    assert "[[" not in text
    return text


def new_image(key, label, prompt, x, y):
    nid = "node-" + hashlib.md5(("capybara-bubble-text:v1:" + key).encode("utf-8")).hexdigest()[:8]
    ids[key] = nid
    return {
        "id": nid, "type": "gen-image", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 300.0, "height": 170.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
            "prompt": prompt, "reference_images": [], "aspect_ratio": "16:9",
            "image_size": "1K", "width": 1024, "height": 1024,
            "quality": "medium", "output_format": "png", "moderation": "low",
            "auto_compress": True,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


# 1) remove old A05, add three exact bubble refs
nodes[:] = [n for n in nodes if n["id"] != old_a05]
by.pop(old_a05, None)
for key, word, y in (("A05_R", "rocklike", 800), ("A05_S", "snakelike", 1000), ("A05_D", "doglike", 1200)):
    prompt = f"""16:9 纯白底道具设定图，只生成一个白色 3D 对话气泡：圆角、软阴影、尾巴朝左下；气泡里两行黑字：第一行“{word}”，第二行“是什么意思？”；无其他文字/图案；3D卡通渲染+搪胶材质，轻微高光；无角色、无手、无 logo。
负向：文字错误、乱码、多余文字、多个气泡、角色、手、彩色、logo、水印。"""
    n = new_image(key, f"【待生成】{key} 气泡参考 · {word} / 是什么意思？", prompt, 360, y)
    nodes.append(n)
    by[n["id"]] = n

# 2) K frames: exact text bubbles
ka = """16:9 电影感首帧，第0秒，只生成一张。小院石桌角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在石桌旁，头顶橘子；她头右上浮一个白色3D对话气泡（参考 [[A05_R]]），气泡里两行黑字：第一行“rocklike”，第二行“是什么意思？”；文字必须和 [[A05_R]] 完全一致，不要改字/加字/变成问号。心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，看向心易/气泡。低机位，午后暖光，3D卡通+真实光影（皮克斯/搪胶）。
无其他文字/字幕/logo。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字错误、乱码、字幕、logo、人类、比例失真、过曝。"""
kb = """16:9 电影感首帧，第0秒，只生成一张。小院花坛角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在花坛旁；她头右上浮一个白色3D对话气泡（参考 [[A05_S]]），气泡里两行黑字：第一行“snakelike”，第二行“是什么意思？”；文字必须和 [[A05_S]] 完全一致。心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，看向花坛/气泡；花丛里有小蛇（参考 [[A03]]，圆头大眼、无尖牙、可爱）。低机位，午后暖光，3D卡通+真实光影。
无其他文字/字幕/logo。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字错误、乱码、字幕、logo、人类、恐怖蛇、尖牙、比例失真、过曝。"""
kc = """16:9 电影感首帧，第0秒，只生成一张。小院狗窝/门口角（参考 [[A02]]）：双人中景，心易（参考 [[R02]]，棕色水豚/卡皮巴拉毛绒玩偶）在画面左1/3，站在狗窝旁；她头右上浮一个白色3D对话气泡（参考 [[A05_D]]），气泡里两行黑字：第一行“doglike”，第二行“是什么意思？”；文字必须和 [[A05_D]] 完全一致。心易嘴巴闭合、不说话、表情淡定。黄蛋（参考 [[R01]]，外形/比例参考 [[R00]]）在画面右1/3，拿着红色狗绳（参考 [[A01]]），看向心易/气泡；狗窝旁坐着一只金毛（参考 [[A04]]，摇尾/吐舌）。低机位，午后暖光，3D卡通+真实光影。
无其他文字/字幕/logo。
负向：旧心易/粉蛋/猫耳/天线、角色说话、多个气泡、文字错误、乱码、字幕、logo、人类、比例失真、过曝。"""
for key, prompt, refs in (
    ("K_A", ka, ["R00", "R01", "R02", "A02", "A05_R"]),
    ("K_B", kb, ["R00", "R01", "R02", "A02", "A03", "A05_S"]),
    ("K_C", kc, ["R00", "R01", "R02", "A01", "A02", "A04", "A05_D"]),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    n["outputs"] = []
    n["meta"]["label"] = {
        "K_A": "【待生成】K_A 首帧 · 石桌 · rocklike / 是什么意思？",
        "K_B": "【待生成】K_B 首帧 · 花坛 · snakelike / 是什么意思？",
        "K_C": "【待生成】K_C 首帧 · 狗窝 · doglike / 是什么意思？",
    }[key]

# 3) V prompts: text bubble stays exact
v1 = """【风格】15s 快问快答，横屏；小院石桌角；心易只发“咔啵”，不说话、无其他词；黄蛋说话；白色3D气泡在画面里，不后期。镜头快推/短甩/急停，词间硬切。
【角色】心易（参考 [[K_A]] 中的水豚）：棕色水豚/卡皮巴拉毛绒玩偶，奶油色大脸板、橘色腮红、小棕耳、一字嘴、白肚、棕色短手短脚、奶油色脚踝、头顶橘子＋绿叶；只发“咔啵”（升调疑问/降调收到），嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔；说话的人。
【气泡】白色3D对话气泡，两行黑字：`rocklike` / `是什么意思？`；文字保持不换；在心易头右上，不遮脸；不要变字/消失/多个气泡。
【图片引用】[[K_A]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A02]]=小院。
0–2 秒：黄蛋：“like 是‘像’。一个词加 like，就是‘像它一样’。”
2–2.8 秒：心易：“咔啵？”（升调、歪头；气泡文字保持 `rocklike` / `是什么意思？`）黄蛋看气泡。
2.8–5.2 秒：黄蛋：“rocklike？rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌；心易点头。
5.2–6 秒：黄蛋：“真不错！snakelike——”心易转头；镜尾硬切。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字错误、文字变化、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""
v2 = """【风格】4s 快问快答，横屏；小院花坛角；心易只发“咔啵”，不说话；黄蛋说话；白色3D气泡在画面里，不后期；词间硬切。
【角色】心易（参考 [[K_B]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；只发“咔啵”，嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔；说话的人。
【气泡】白色3D气泡，两行黑字：`snakelike` / `是什么意思？`；文字保持不换；在心易头右上，不遮脸。
【图片引用】[[K_B]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A02]]=小院；[[A03]]=小蛇。
0–0.8 秒：心易：“咔啵？”（升调、歪头；气泡保持 `snakelike` / `是什么意思？`）
0.8–3.2 秒：黄蛋：“snakelike？snake 是蛇——snakelike 就是像蛇一样，蜿蜒的！”心易整臂蛇形；小蛇从花丛滑出。
3.2–4 秒：黄蛋：“真棒！doglike——”心易转头；镜尾硬切。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字错误、文字变化、logo、恐怖蛇、尖牙、慢速横移、渐变、白场、过曝、漂浮。"""
v3 = """【风格】5s 快问快答，横屏；小院狗窝/门口角；心易只发“咔啵”，不说话；黄蛋说话；白色3D气泡在画面里，不后期；结尾三卡复习。
【角色】心易（参考 [[K_C]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；只发“咔啵”，嘴巴闭合/小张口，无台词。黄蛋：黄色蛋仔；说话的人。
【气泡】白色3D气泡，两行黑字：`doglike` / `是什么意思？`；文字保持不换；在心易头右上，不遮脸；结尾不换成文字。
【图片引用】[[K_C]]=首帧；[[R00]]=身高比例；[[R01]]=黄蛋；[[A01]]=狗绳/词卡；[[A02]]=小院；[[A04]]=金毛；[[KC]]=三张词卡版式。
0–0.8 秒：心易：“咔啵？”（升调、歪头；气泡保持 `doglike` / `是什么意思？`）
0.8–3.2 秒：黄蛋：“doglike？dog 是狗——doglike 就是像狗一样，忠诚的！”心易拿狗绳；金毛摇尾。
3.2–4.2 秒：黄蛋：“你记住了多少？”心易指桌上的三张卡（[[KC]] 版式）。
4.2–5 秒：三卡定格；心易点头；镜尾定格。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：心易说人话/加词、字幕、后期气泡、旧心易/粉蛋/猫耳/天线、多个气泡、文字错误、文字变化、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""
for key, prompt, dur, refs in (
    ("V1", v1, 6, ["R00", "R01", "A02", "K_A"]),
    ("V2", v2, 4, ["R00", "R01", "A02", "A03", "K_B"]),
    ("V3", v3, 5, ["R00", "R01", "A01", "A02", "A04", "KC", "K_C"]),
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
        "V1": "【待生成】V1 · 6s · 快问快答 · rocklike（文字气泡）",
        "V2": "【待生成】V2 · 4s · 快问快答 · snakelike（文字气泡）",
        "V3": "【待生成】V3 · 5s · 快问快答 · doglike＋三卡收尾",
    }[key]
    assert len(mp["prompt"]) <= 1900, (key, len(mp["prompt"]))

# 4) labels for generated assets
for key in ("A01", "A02", "A03", "A04", "KC"):
    n = by[ids[key]]
    if n.get("outputs"):
        n["meta"]["label"] = n["meta"]["label"].replace("【待生成】", "【已生成】", 1)

# 5) S0
s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词样片「水豚心易·气泡文字版」：rocklike／snakelike／doglike，6＋4＋5＝15s。
心易＝棕色水豚，只发“咔啵”；气泡里是她的心里话：`rocklike` / `是什么意思？`；黄蛋说话，直接答。
A01–A04、KC 已生成保留；K/V 用新水豚+文字气泡重生成。

【跑序】
1. 先跑 A05_R / A05_S / A05_D 三张气泡参考（白底，两行字：单词 / 是什么意思？）。
2. 跑 K_A / K_B / K_C；首帧气泡文字必须和对应 A05 参考一致。
3. 跑 V1（6s）/ V2（4s）/ V3（5s）；气泡文字保持，不后期。
4. 后期只加 BGM/环境声；不要贴气泡、不要贴词卡。

【口径】
- 心易是水豚，不是蛋仔/猫耳；头顶橘子保留；只发“咔啵”，无其他词。
- 黄蛋说话；不说“心易问”，直接答气泡。
- 气泡两行：`rocklike` / `是什么意思？`；不要长句、不要变字。
- V3 最后三卡复习用 KC 版式；卡面文字在视频里。
- 若模型写错气泡字：重跑；不要后期补。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# 6) groups
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {
        "id": "group-" + hashlib.md5(("capybara-bubble-text:v1:group:" + key).encode("utf-8")).hexdigest()[:8],
        "nodeIds": [ids[k] for k in keys],
        "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚心易/比例", ["R00", "R01", "R02"], "#E68BB3"),
    group("g01", "01 道具/小院/小蛇/金毛/三张气泡 · 先跑", ["A01", "A02", "A03", "A04", "A05_R", "A05_S", "A05_D"], "#8E8DE0"),
    group("g02", "02 首帧/词卡 · K_A、K_B、K_C、KC", ["K_A", "K_B", "K_C", "KC"], "#E8B85D"),
    group("g03", "03 视频 V1 · 6s · rocklike", ["V1"], "#DC775D"),
    group("g04", "04 视频 V2 · 4s · snakelike", ["V2"], "#DC775D"),
    group("g05", "05 视频 V3 · 5s · doglike＋收尾", ["V3"], "#DC775D"),
    group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
]
c["groups"] = groups

# 7) edges
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
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易·气泡文字版」v1 · 15s"

# 8) validate
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

