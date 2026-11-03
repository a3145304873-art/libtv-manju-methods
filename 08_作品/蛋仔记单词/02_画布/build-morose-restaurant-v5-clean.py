# -*- coding: utf-8 -*-
"""Restaurant v5: no gloss after 咔啵; word spoken; box on table, not stool."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v4-closed-box.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v5-clean.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


A06 = find("【待生成】A06")
KA = find("【待生成】K_A")
V1 = find("【待生成】V1")
V2 = find("【待生成】V2")
S0 = find("S0")

EYE = ("白色圆形眼片，中心没有黑色瞳孔/眼珠/虹膜；外圈一圈深棕色细描边；"
       "眼片中心保持空白，没有高光点；眼片形状、外圈深棕线、中心空白全程不变；"
       "眼睛全程睁开，白色圆形眼片完整可见；不眨眼、不眯眼、不抬眼皮、不皱眉、不闭眼、不笑眼；"
       "情绪只靠歪头/身体/手势/咔啵")
NEG = ("心易的黑瞳、心易的眼珠、心易的虹膜、心易的瞳孔、心易的高光点、"
       "心易的眼皮/眼睑/眉毛/眨眼/眯眼/半闭眼/闭眼/笑眼/眼神变化/眼睛大特写")

# A06: clear table, no red stool near it
A06["params"]["model_params"]["prompt"] = (
    "16:9 电影感内景空景，只生成一张。街边小饭馆/快餐店内部：木质柜台＋收银机＋出菜口＋后厨窗口（背景有炒锅/灶台）；"
    "画面中央有一张**明确的木餐桌**（桌面宽、桌腿清晰）；椅子/凳子收在桌下或离桌远，**不要红色塑料凳靠近桌面**；"
    "墙上菜单只有食物图片、无文字/无价格；暖黄灯，窗外傍晚街景虚化；3D卡通+真实光影（皮克斯/搪胶）。"
    "无人物、无手、无文字、无logo/水印。"
    "负向：人物、手、文字、价格、logo、水印、真实照片、过曝、杂乱、红色塑料凳、凳子靠近桌子、餐盒放凳子上。"
)

# eye replacement in K_A/V1/V2
for n in (KA, V1, V2):
    mp = n["params"]["model_params"]
    t = re.sub(r"心易（参考 (\{\{node-[0-9a-f]+\}\})，棕色水豚；眼睛严格按 (\{\{node-[0-9a-f]+\}\})：[^）]*）",
               lambda m: f"心易（参考 {m.group(1)}，棕色水豚；眼睛严格按 {m.group(2)}：{EYE}）", mp["prompt"])
    t = re.sub(r"心易的黑瞳、心易的眼珠、心易的虹膜、心易的瞳孔、心易的高光点、心易的眼皮/眼睑/眉毛/眨眼/眯眼/半闭眼/眼神变化/眼睛大特写", NEG, t)
    mp["prompt"] = t

# remove glosses after 咔啵
for n in (V1, V2):
    mp = n["params"]["model_params"]
    t = mp["prompt"]
    for a, b in (("“咔啵！”（收到）", "“咔啵！”"), ("“咔啵？”（心虚）", "“咔啵？”"),
                 ("“咔——啵”（等一下）", "“咔——啵”"), ("“咔啵！”（补救）", "“咔啵！”")):
        t = t.replace(a, b)
    mp["prompt"] = t

# V1: place box on tabletop, not stool
mp = V1["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace(
    "6–8 秒：黄蛋端着**关着的**餐盒走向木桌；**尾帧停在半路/桌边，稳定 1 秒**，给 V2 接尾帧。",
    "6–8 秒：黄蛋端着**关着的**餐盒走到木桌前，把餐盒放在**木桌桌面正中央**（不是凳子/椅子），手离开；**尾帧停在餐盒在桌面上的稳定画面 1 秒**，给 V2 接尾帧。",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、餐盒放在凳子/椅子上、红色塑料凳当桌子、",
)

# V2: box on table, add word line
mp = V2["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace(
    "0–2 秒：{{" + find("T_A")["id"] + "}} 黄蛋在桌边，餐盒**关着**；他把餐盒放稳，手放在盒盖上。",
    "0–2 秒：{{" + find("T_A")["id"] + "}} 黄蛋站在木桌旁，餐盒**关着**，已经在**木桌桌面**上；他把手放在盒盖上。",
)
mp["prompt"] = mp["prompt"].replace(
    "8–9 秒：黄蛋看那一根，更郁闷；心易低头/拍肩：“咔……啵……”镜尾定格 1s。",
    "8–9 秒：黄蛋看那一根，更郁闷：“所以我很 morose？”心易低头/拍肩：“咔……啵……”镜尾定格 1s。",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、餐盒放在凳子/椅子上、红色塑料凳当桌子、",
)
assert "所以我很 morose" in mp["prompt"]

# S0: rules
v = S0["outputs"][0]["value"]
v += """

【咔啵不加释义】
只写“咔啵/咔——啵/咔啵？”，不要写（收到）（心虚）（等一下）（补救）（抱歉）等中文释义；动作写在括号外。模型会把括号里的字念出来。

【单词必须出现】
- 黄蛋 V2 说：“所以我很 morose？”
- 旁白完整稿：morose。黄蛋点了青椒肉丝饭。打开一看——只有青椒，没有肉丝。没肉丝，所以 morose——郁闷的。你记住了吗？
- 尾卡：morose / 没肉丝 → 郁闷的。
- 只出 V1+V2 的 17s 不算成片，必须带旁白/尾卡。

【桌面】
A06 明确木餐桌；V1 把餐盒放桌面正中央；V2 餐盒已经在桌面；负向：餐盒放凳子/椅子、红色塑料凳当桌子。

【心易眼睛】
白色圆眼片，中心空白无瞳孔；细深棕外圈；无高光；全程睁开；不眨眼/眯眼/闭眼/笑眼；情绪靠歪头/身体/手势/咔啵。
负向只写“心易的……”，不限制黄蛋。
"""
S0["outputs"][0]["value"] = v

d["canvas"]["name"] = "蛋仔记单词 · morose 小饭馆版 v5 · 无括号释义＋单词＋桌面 · 20s"

# validate prompt lengths
for n in (A06, KA, V1, V2):
    mp = n["params"]["model_params"]
    assert len(mp["prompt"]) <= 2000, (n["meta"]["label"], len(mp["prompt"]))
    print(n["meta"]["label"], len(mp["prompt"]))

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print("->", OUT)
