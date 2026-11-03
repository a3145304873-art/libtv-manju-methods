# -*- coding: utf-8 -*-
"""Build v4: eye lock scoped to 心易 only; 黄蛋 keeps expressive eyes.

The previous global negative could suppress 黄蛋's blinks/expressions.
This version puts the lock at 心易's character/reference point and explicitly
exempts 黄蛋.

Output: 02_画布/EP02-like-capybara-tail-v4-eyes-scoped.monet
"""
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP02-like-capybara-tail-v3-eyelock.monet"
OUT = HERE / "EP02-like-capybara-tail-v4-eyes-scoped.monet"

NEW_BLOCK = """【心易眼睛·仅限心易】心易是毛绒玩具，眼睛是固定塑料/刺绣件，不是生物眼：白色圆形眼白、黑色小圆瞳、单个高光；眼白形状、瞳孔大小/位置、开合度全程完全不变；不眨眼、不眯眼、不抬眼皮、不皱眉、不转瞳孔、不放大缩小、不出现泪光；情绪只靠歪头/身体/手势/咔啵。**黄蛋不受此限制：黄蛋的眼睛可以正常眨眼、看、做表情，不要套用。** 镜头以中景/中近景为主，不要心易眼睛大特写。"""
NEW_NEG = "心易的眼皮、心易的眼睑、心易的眉毛、心易的眨眼、心易的眯眼、心易的半闭眼、心易的瞳孔放大/缩小、心易的瞳孔移动、心易的眼神变化、心易的眼球转动、心易的泪光、睫毛、眼影、虹膜变色、眼睛变形、卡通大眼、拟人化眼神、心易的眼睛大特写；不要限制黄蛋的眼睛，不要给黄蛋加眼罩/无眼/死鱼眼"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
for n in c["nodes"]:
    lab = n["meta"].get("label", "")
    if not (lab.startswith("【已生成】K_A") or lab.startswith("【待生成") and lab.startswith("【待生成") and ("V1" in lab or "V2" in lab or "V3" in lab)):
        continue
    mp = n["params"]["model_params"]
    p = mp["prompt"]
    p2 = re.sub(r"【眼睛硬约束】.*?不要眼睛大特写。", NEW_BLOCK, p, count=1, flags=re.S)
    # negative: replace the generic block after 负向： up to 、logo
    p2 = re.sub(r"负向：眼皮、眼睑、眉毛、眨眼、眯眼、半闭眼、瞳孔放大/缩小、瞳孔移动、眼神变化、眼球转动、泪光、睫毛、眼影、虹膜变色、眼睛变形、卡通大眼、拟人化眼神、眼睛大特写、", "负向：" + NEW_NEG + "、", p2, count=1)
    assert p2 != p, f"no change in {lab}"
    mp["prompt"] = p2
    if n["type"] == "gen-video":
        n["outputs"] = []
        n["meta"]["label"] = lab.replace("【待生成·锁眼】", "【待生成·锁眼(仅心易)】")
    else:
        n["meta"]["label"] = lab.replace("（眼睛锁定）", "（眼睛锁定·仅心易）")
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·尾帧链·锁眼(仅心易)」v4 · 23s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(OUT.name, len(c["nodes"]), len(c["edges"]), len(c["groups"]))
for n in c["nodes"]:
    if n["type"] in ("gen-image", "gen-video"):
        print(n["meta"]["label"][:28], len(n["params"]["model_params"]["prompt"]))
