# -*- coding: utf-8 -*-
"""Build v3: hard eye-lock prompts on the 23s canvas.

Eyes are fixed plastic/embroidered toy parts: no blink, no eyelids, no brows,
no pupil movement/size change, no eye close-ups. Emotion only body/head/ka-bo.

Output: 02_画布/EP02-like-capybara-tail-v3-eyelock.monet
"""
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP02-like-capybara-tail-v2-23s.monet"
OUT = HERE / "EP02-like-capybara-tail-v3-eyelock.monet"

EYE = """【眼睛硬约束】心易是毛绒玩具，眼睛是固定塑料/刺绣件，不是生物眼：白色圆形眼白、黑色小圆瞳、单个高光；眼白形状、瞳孔大小/位置、开合度全程完全不变；不眨眼、不眯眼、不抬眼皮、不皱眉、不转瞳孔、不放大缩小、不出现泪光；情绪只靠歪头/身体/手势/咔啵。镜头以中景/中近景为主，不要眼睛大特写。"""
NEG = "眼皮、眼睑、眉毛、眨眼、眯眼、半闭眼、瞳孔放大/缩小、瞳孔移动、眼神变化、眼球转动、泪光、睫毛、眼影、虹膜变色、眼睛变形、卡通大眼、拟人化眼神、眼睛大特写"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
for n in c["nodes"]:
    lab = n["meta"].get("label", "")
    if lab.startswith("【已生成】K_A") or lab.startswith("【待生成】K_A"):
        mp = n["params"]["model_params"]
        mp["prompt"] = mp["prompt"].replace("**眼睛必须严格参考", EYE + "\n**眼睛必须严格参考")
        mp["prompt"] = mp["prompt"].replace("负向：", "负向：" + NEG + "、")
        n["meta"]["label"] = "【已生成】K_A 首帧 · 石桌 · 复用旧图（眼睛锁定）"
    elif lab.startswith("【待生成】V"):
        mp = n["params"]["model_params"]
        mp["prompt"] = mp["prompt"].replace("【图片引用】", EYE + "\n【图片引用】")
        mp["prompt"] = mp["prompt"].replace("负向：", "负向：" + NEG + "、")
        n["outputs"] = []
        n["meta"]["label"] = lab.replace("【待生成】", "【待生成·锁眼】")
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·尾帧链·锁眼」v3 · 23s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(OUT.name, len(c["nodes"]), len(c["edges"]), len(c["groups"]))
print({n["meta"]["label"][:24]: len(n["params"]["model_params"]["prompt"]) for n in c["nodes"] if n["type"] in ("gen-image", "gen-video")})
