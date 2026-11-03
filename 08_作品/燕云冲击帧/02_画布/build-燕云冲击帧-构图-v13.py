# -*- coding: utf-8 -*-
"""燕云冲击帧 v13：v12 + K/E 的构图改造（裁切 / 出画 / 单块留白 / 指向画外）

依据（2026-10-30 量参考帧）：三条参考的墨重心都在正中（0.49–0.52），
所以差别不在"三分法"，而在：主体被画框裁掉、兵器尖端出画、只有一块白、横平竖直压斜线。

做法：复用 v12 的整张画布（资产/首尾帧/招式/冲击帧/墨动全在），
只给 K1–K3、E1–E3 六个节点插入【构图】块并补负向；节点 ID 换前缀 ywsf。
"""
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-构图-16x9-v13.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T14:20:00.000+08:00"
PREFIX = "ywsf"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V12 = load_mod("yanwu_v12", "build-燕云冲击帧-墨动-v12.py")
DOC = V12.DOC


# ---------------------------------------------------------------- 泛用 ID 重映射
def new_id(old):
    return "node-" + hashlib.md5((PREFIX + old).encode()).hexdigest()[:8]


MAP = {n["id"]: new_id(n["id"]) for n in DOC["canvas"]["nodes"]}


def rm(s):
    for old, new in MAP.items():
        s = s.replace(old, new)
    return s


canvas = DOC["canvas"]
for n in canvas["nodes"]:
    n["id"] = MAP[n["id"]]
    if n.get("mainOutputId"):
        n["mainOutputId"] = "output-" + n["id"][5:13]
    for o in n.get("outputs") or []:
        o["id"] = "output-" + n["id"][5:13]
    mp = (n.get("params") or {}).get("model_params") or {}
    if mp:
        mp["prompt"] = rm(mp.get("prompt") or "")
        if mp.get("reference_images"):
            mp["reference_images"] = [{"node_id": MAP.get(r["node_id"], r["node_id"])} for r in mp["reference_images"]]
        for key in ("first_frame_image", "last_frame_image"):
            v = mp.get(key)
            if isinstance(v, dict) and v.get("node_id"):
                v["node_id"] = MAP.get(v["node_id"], v["node_id"])
for e in canvas["edges"]:
    e["sourceNodeId"] = MAP[e["sourceNodeId"]]
    e["targetNodeId"] = MAP[e["targetNodeId"]]
    e["id"] = "edge-" + hashlib.md5(("f" + e["sourceNodeId"] + e["targetNodeId"]).encode()).hexdigest()[:8]
for g in canvas["groups"]:
    g["nodeIds"] = [MAP[x] for x in g["nodeIds"]]
    g["id"] = "g-" + hashlib.md5(("f" + g["id"]).encode()).hexdigest()[:8]

# ---------------------------------------------------------------- 构图块
COMP = {
    "K1": "【构图·起势·近景】头顶贴上缘、右肩被右缘切掉（**不许全身入画**）；剑尖**出画右缘**，画面里看不到端点；"
          "只留一块白：右上四分之一，其余全实；视线朝画左、出画；斜线只给剑一条，其余横平竖直。",
    "K2": "【构图·起势·中景】脚出下缘一成（切掉脚踝以下，**不许站完整**）；剑垂右侧、尖**出画右缘**；"
          "留白只在左上四分之一；身体压右三分，肩线水平；斜线只给剑一条。",
    "K3": "【构图·起势·半身】剑尖垂在右下、**出画右下角**；头顶贴上缘（切掉帽顶/发顶）；"
          "留白只在左上五分之一；人物只到腰，**不许画腿**；视线朝画左下出画。",
    "E1": "【构图·结束·近景】剑尖**出画左缘**（看不到端点，只有剑身贯出去）；脸在右三分、上三分线上；"
          "下缘裁到胸，**不许见腰以下**；留白只在左下五分之一；肩线斜切但不过度。",
    "E2": "【构图·结束·中景】剑横贯画面、尖**出画左缘**；下缘裁到膝；身体压右三分；留白只在右上五分之一；"
          "雪雾只在下缘一条带上，不要满幅。",
    "E3": "【构图·结束·半身】剑尖**出画右上角**；脸在右三分、上三分线上；下缘裁到腰，**不许见腿**；"
          "留白只在左下四分之一；衣摆向上翻卷但不要铺满上半幅。",
}
COMP_NEG = "全身入画、站完整、兵器尖端完整留在画面内、多处零散留白、空白均匀分布、主体居中对称、平视正对"


def patch_prompt(prompt, key):
    block = COMP[key]
    if block in prompt:
        return prompt
    # 插在【画面】之前，保证权重靠前
    if "【画面】" in prompt:
        out = prompt.replace("【画面】", block + "\n【画面】", 1)
    else:
        out = prompt + "\n" + block
    # 负向补构图禁手
    if "全身入画" not in out:
        out = out.replace("负向：", "负向：" + COMP_NEG + "、", 1)
    return out


label2key = {}
for n in canvas["nodes"]:
    lab = n["meta"]["label"]
    for k in COMP:
        if lab.startswith(f"【待生成】{k} "):
            label2key[n["id"]] = k

for n in canvas["nodes"]:
    if n["id"] in label2key:
        mp = n["params"]["model_params"]
        mp["prompt"] = patch_prompt(mp["prompt"], label2key[n["id"]])

canvas["name"] = "燕云冲击帧 · 构图版（裁切/出画/单块留白）v13"
canvas["description"] = ("在 v12 基础上按参考帧的构图思想改 K/E：主体被画框裁掉、兵器尖端出画、"
                         "只留一块白（≥1/4）、视线与刃线同向出画、横平竖直压斜线。")
DOC["exportedAt"] = CREATED

if __name__ == "__main__":
    OUT.write_text(json.dumps(DOC, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    c = DOC["canvas"]
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(c['nodes'])} / 边 {len(c['edges'])} / 组 {len(c['groups'])}")
    for n in c["nodes"]:
        if n["id"] in label2key:
            p = n["params"]["model_params"]["prompt"]
            print(f"  {n['meta']['label'][:22]:<22} {len(p)} 字  构图块={'是' if '【构图·' in p else '否'}")
