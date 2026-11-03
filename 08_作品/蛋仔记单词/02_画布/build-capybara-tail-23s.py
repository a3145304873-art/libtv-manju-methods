# -*- coding: utf-8 -*-
"""Build 23s version: natural speaking time, slower opening, same tail chain.

V1 10s / V2 6s / V3 7s = 23s.
Opening 0-5s: 3 ka-bo + 3 post bubbles (like / rule / rocklike question).
Praise by 心易; 黄蛋 no praise. R02F eyes locked; K_A reused; T_A/T_B chain.

Output: 02_画布/EP02-like-capybara-tail-v2-23s.monet
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
SRC = HERE / "EP02-like-capybara-tail-v1.monet"
OUT = HERE / "EP02-like-capybara-tail-v2-23s.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}
ids = {
    "R00": "node-3b85595e", "R01": "node-1dec7c6e", "R02": "node-34b2e592",
    "R02F": None, "R01P": None,
    "A01": "node-55532172", "A02": "node-d67c8efd", "A03": "node-f20de25c", "A04": "node-a7f97bc6",
    "K_A": "node-8bb56275", "T_A": None, "T_B": None, "KC": "node-7bc3ca9e",
    "V1": "node-0c21fa45", "V2": "node-1b546606", "V3": "node-4aabdc25",
    "S0": "node-ce285427",
}
for n in nodes:
    lab = n["meta"].get("label", "")
    if lab.startswith("R02F"):
        ids["R02F"] = n["id"]
    elif lab.startswith("【已生成】R01P") or lab.startswith("【待生成】R01P"):
        ids["R01P"] = n["id"]
    elif lab.startswith("【待替换⚠】T_A"):
        ids["T_A"] = n["id"]
    elif lab.startswith("【待替换⚠】T_B"):
        ids["T_B"] = n["id"]
for k in ("R02F", "R01P", "T_A", "T_B"):
    assert ids[k], f"missing {k}"


def link(text):
    for k, v in ids.items():
        if v:
            text = text.replace("[[" + k + "]]", "{{" + v + "}}")
    assert "[[" not in text
    return text


v1 = """【风格】23s 快问快答，横屏；小院石桌角；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡；结尾走向花坛。开头放慢，按 3 口气泡的说话时间。
【角色】心易（参考 [[K_A]] 中的水豚）：棕色水豚/卡皮巴拉毛绒玩偶，奶油色大脸板、橘色腮红、小棕耳、一字嘴、白肚、棕色短手短脚、奶油色脚踝、头顶橘子；**眼睛严格按 [[R02F]]：白色圆眼白、黑色小圆瞳、单个高光；不要眼皮/眉毛/放大瞳孔/拟人化**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[K_A]]=首帧；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A02]]=小院；[[R02F]]=眼睛参考。
0–1.2 秒：心易看镜头/黄蛋，发“咔啵。”（平调，像“听着”）；黄蛋听。
1.2–3.4 秒：心易发“咔啵！”（强调/上扬，像“对！”）；黄蛋听。
3.4–5.0 秒：心易发“咔啵？”（升调疑问，像“嗯？”）；黄蛋准备答。
5.0–8.4 秒：黄蛋：“rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌；语速正常，不赶。
8.4–9.2 秒：心易发“咔啵！”（开心、短促，像“真不错！”）；黄蛋点头，**黄蛋不说“真不错”**。
9.2–10 秒：黄蛋：“snakelike——”两人转身朝花坛走；镜尾停在花坛入口。
【声音】黄蛋人声；心易只有三声“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""
v2 = """【风格】23s 快问快答，横屏；花坛入口；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡；结尾走向狗窝。
【角色】心易（参考 [[T_A]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；**眼睛严格按 [[R02F]]：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[T_A]]=首帧（必须从该帧完全接续，不要重新构图）；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A02]]=小院；[[A03]]=小蛇；[[R02F]]=眼睛参考。
0–0.5 秒：从 T_A 花坛入口开始；心易发“咔啵？”（升调）。
0.5–3.6 秒：黄蛋：“snake 是蛇——snakelike 就是像蛇一样，蜿蜒的！”心易整臂蛇形；小蛇从花丛滑出；语速正常。
3.6–4.4 秒：心易发“咔啵！”（开心、短促，像“真棒！”）；黄蛋点头，**黄蛋不说“真棒”**。
4.4–5.4 秒：黄蛋：“doglike——”两人转身朝狗窝走；镜尾停在狗窝入口。
5.4–6 秒：镜尾停在狗窝入口。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、恐怖蛇、尖牙、慢速横移、渐变、白场、过曝、漂浮。"""
v3 = """【风格】23s 快问快答，横屏；狗窝入口；心易只发“咔啵”，不说话；黄蛋说话；视频内无文字/气泡；结尾三卡/“你记住了多少？”
【角色】心易（参考 [[T_B]] 中的水豚）：棕色水豚玩偶，奶油脸、橘腮红、小棕耳、一字嘴、白肚、棕短手短脚、头顶橘子；**眼睛严格按 [[R02F]]：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔**；只发“咔啵”，无台词。黄蛋：毛绒黄蛋（参考 [[R01P]]）；说话的人。
【图片引用】[[T_B]]=首帧（必须从该帧完全接续）；[[R00]]=身高比例；[[R01P]]=毛绒黄蛋；[[A01]]=狗绳/词卡；[[A02]]=小院；[[A04]]=金毛；[[KC]]=三张词卡版式；[[R02F]]=眼睛参考。
0–0.5 秒：从 T_B 狗窝入口开始；心易发“咔啵？”（升调）。
0.5–3.6 秒：黄蛋：“dog 是狗——doglike 就是像狗一样，忠诚的！”心易拿狗绳；金毛摇尾；语速正常。
3.6–4.4 秒：心易发“咔啵！”（开心、短促，像“真棒！”）；黄蛋点头，**黄蛋不说“真棒”**。
4.4–5.6 秒：黄蛋：“你记住了多少？”心易指桌上的三张卡（[[KC]] 版式）。
5.6–7 秒：三卡定格；心易点头；镜尾定格。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、心易说人话/加词、眼皮/眉毛/放大瞳孔/大眼珠、旧心易/粉蛋/猫耳/天线、logo、口型穿帮、慢速横移、渐变、白场、过曝、漂浮。"""

for key, prompt, dur, label in (
    ("V1", v1, 10, "【待生成】V1 · 10s · 开头3气泡＋rocklike＋心易夸＋走向花坛"),
    ("V2", v2, 6, "【待生成】V2 · 6s · snakelike＋心易夸＋走向狗窝（首帧 T_A）"),
    ("V3", v3, 7, "【待生成】V3 · 7s · doglike＋心易夸＋三卡（首帧 T_B）"),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["duration"] = dur
    n["outputs"] = []
    n["meta"]["label"] = label
    assert len(mp["prompt"]) <= 1900, (key, len(mp["prompt"]))

s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》-like 三词样片「水豚心易＋毛绒黄蛋·尾帧链」v2：rocklike／snakelike／doglike，10＋6＋7＝23s。
开头放慢：0–5s 三口气泡（like 是像 / 加 like 就是像它一样 / rocklike 是什么），心易三声咔啵；黄蛋 5s 后才答。
心易＝棕色水豚只发“咔啵”；黄蛋＝毛绒黄蛋说话；视频内无文字/气泡；白字/夸赞气泡后期加。
A01–A04、R01P、KC、K_A 复用；只重生成 V1/V2/V3；T_A/T_B 截尾帧替换。

【跑序】
1. K_A 已复用，不用跑。
2. 跑 V1（10s）；截最后一帧替换 T_A。
3. 跑 V2（6s，首帧 T_A）；截最后一帧替换 T_B。
4. 跑 V3（7s，首帧 T_B）。
5. 后期：开头三气泡、心易夸赞气泡、横排字幕；只加 BGM/环境声。

【口径】
- 心易是水豚，不是蛋仔/猫耳；头顶橘子保留；只发“咔啵”，无其他词。
- 眼睛严格按 R02F：白圆眼白、黑小圆瞳、单高光；不要眼皮/眉毛/放大瞳孔/拟人化。
- 夸赞由心易发“咔啵！”；黄蛋不再说“真不错/真棒”。
- V1 结尾走到花坛入口；V2 结尾走到狗窝入口；T_A/T_B 必须用真实尾帧替换。
- 视频内无文字/气泡；字幕/气泡后期。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·尾帧链」v2 · 23s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(OUT.name, len(nodes), len(c["edges"]), len(c["groups"]))
print({k: by[ids[k]]["params"]["model_params"]["duration"] for k in ("V1", "V2", "V3")})
print("prompts", {k: len(by[ids[k]]["params"]["model_params"]["prompt"]) for k in ("V1", "V2", "V3")})
