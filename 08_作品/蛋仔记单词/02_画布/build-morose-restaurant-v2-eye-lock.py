# -*- coding: utf-8 -*-
"""Create restaurant v2 with 心易's no-pupil eye lock. Preserves all done assets."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v1.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v2-eye-lock.monet"

EYE = ("白色圆形眼片，中心没有黑色瞳孔/眼珠/虹膜；外圈一圈深棕色细描边；"
       "眼片中心保持空白，没有高光点；眼片形状、外圈深棕线、中心空白全程不变；"
       "不眨眼、不眯眼、不抬眼皮、不皱眉；情绪只靠歪头/身体/手势/咔啵")
NEG = ("心易的黑瞳、心易的眼珠、心易的虹膜、心易的瞳孔、心易的高光点、"
       "心易的眼皮/眼睑/眉毛/眨眼/眯眼/半闭眼/眼神变化/眼睛大特写")

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
for n in c["nodes"]:
    lab = n["meta"].get("label", "")
    if lab.startswith("R02E"):
        n["meta"]["label"] = "R02E 心易眼睛参考 · 白圆眼片＋细深棕圈·中心空白"
    if n.get("type") in ("gen-image", "gen-video"):
        mp = n["params"]["model_params"]
        t = mp["prompt"]
        t2 = re.sub(r"心易（参考 (\{\{node-[0-9a-f]+\}\})，棕色水豚；眼睛严格按 (\{\{node-[0-9a-f]+\}\})：[^）]*）",
                    lambda m: f"心易（参考 {m.group(1)}，棕色水豚；眼睛严格按 {m.group(2)}：{EYE}）", t)
        t2 = t2.replace("心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光", NEG)
        if t2 != t:
            mp["prompt"] = t2
            print(lab, "updated", len(t), "->", len(t2))
    if lab.startswith("S0"):
        v = n["outputs"][0]["value"]
        if "心易眼睛" not in v:
            v += """

【心易眼睛·锁死】
白圆眼片、中心空白无瞳孔；外圈一圈深棕色细描边；无高光点；眼片形状/外圈/中心空白全程不变；不眨眼/不眯眼/不抬眼皮/不皱眉；情绪只靠歪头/身体/手势/咔啵。
负向只写“心易的……”：心易的黑瞳/眼珠/虹膜/瞳孔/高光点/眼皮/眼睑/眉毛/眨眼/眯眼/半闭眼/眼神变化/眼睛大特写。不要限制黄蛋的眼睛。

【资产保留】
R01P/A05/R00/R01/R02/R02E/KC 均已生成，保留不重跑；只新生成 A06/A07/K_A/V1/V2。
"""
            n["outputs"][0]["value"] = v
c["name"] = "蛋仔记单词 · morose 小饭馆版 v2 · 心易无瞳孔锁死 · 20s"

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print("->", OUT)
