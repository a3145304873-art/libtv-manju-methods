# -*- coding: utf-8 -*-
"""Build v5: correct 心易 eyes = white eye discs with brown ring, NO pupil.

The reference has no black pupil/highlight. Fix positive/negative prompts.
K_A reused image is correct (white disc + brown ring); only prompts change.
V1/V2/V3 outputs cleared.

Output: 02_画布/EP02-like-capybara-tail-v5-nopupil.monet
"""
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP02-like-capybara-tail-v4-eyes-scoped.monet"
OUT = HERE / "EP02-like-capybara-tail-v5-nopupil.monet"

NEW_EYES = "白色圆形眼片，中心没有黑色瞳孔；外圈一圈深棕色细描边；眼片中心保持空白，没有高光点"
d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
for n in c["nodes"]:
    lab = n["meta"].get("label", "")
    if n["type"] == "input-image" and "R02F" in lab:
        n["meta"]["label"] = "R02F 心易脸部/眼睛参考（白片＋深棕圈·无瞳孔）"
    if n["type"] not in ("gen-image", "gen-video"):
        continue
    if not (lab.startswith("【已生成】K_A") or lab.startswith("【待生成")):
        continue
    mp = n["params"]["model_params"]
    p = mp["prompt"]
    reps = [
        ("白色圆形眼白、黑色小圆瞳、单个高光", NEW_EYES),
        ("眼白形状、瞳孔大小/位置、开合度", "眼片形状、外圈深棕线、中心空白"),
        ("不转瞳孔", "不出现瞳孔/黑瞳/眼珠"),
        ("心易的瞳孔放大/缩小、心易的瞳孔移动", "心易的黑瞳、心易的眼珠、心易的虹膜、心易的瞳孔、心易的高光点"),
        ("白圆眼白、黑小圆瞳、单高光", "白色圆眼片、中心无瞳孔、外圈深棕线、无高光点"),
        ("白色圆眼白、黑色小圆瞳、单个高光", NEW_EYES),
        ("不要放大瞳孔", "不要黑色瞳孔/眼珠/高光点"),
        ("放大瞳孔、大眼珠", "黑色瞳孔、眼珠、大眼珠、高光点"),
    ]
    for old, new in reps:
        p = p.replace(old, new)
    assert "黑色小圆瞳" not in p, lab
    assert "黑小圆瞳" not in p, lab
    mp["prompt"] = p
    if n["type"] == "gen-video":
        n["outputs"] = []
        n["meta"]["label"] = lab.replace("【待生成·锁眼(仅心易)】", "【待生成·无瞳锁眼】")
    else:
        n["meta"]["label"] = lab.replace("（眼睛锁定·仅心易）", "（白片无瞳·仅心易）")
c["name"] = "蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·无瞳锁眼」v5 · 23s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(OUT.name, len(c["nodes"]), len(c["edges"]), len(c["groups"]))
for n in c["nodes"]:
    if n["type"] in ("gen-image", "gen-video"):
        print(n["meta"]["label"][:30], len(n["params"]["model_params"]["prompt"]))
        if "黑色小圆瞳" in n["params"]["model_params"]["prompt"] or "黑小圆瞳" in n["params"]["model_params"]["prompt"]:
            print("  !!! still has pupil")
