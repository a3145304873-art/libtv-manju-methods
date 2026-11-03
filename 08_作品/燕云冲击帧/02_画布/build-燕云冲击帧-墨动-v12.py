# -*- coding: utf-8 -*-
"""燕云冲击帧 v12：v11 + 「墨动」段（I→W 图生视频）+ I 提示词换手感写法

改动依据（2026-10-30）：
  1. 重测《拔剑》水墨段（原始尺寸）：前 1–1.5 秒帧差 9–24，之后 <0.5 —— 参考的"定格"是
     「墨先动 1–1.5 秒，然后才停」；我上一轮用 96×54 缩图测帧差，把墨动平均掉了，结论是错的。
  2. I 提示词从"工程说明"改成"绘画手感"写法（纸/墨/笔/光/留白/人 六层 + 宿墨飞白这类词）。

结构：v11 的 23 个节点全部保留（ID 重映射到 ywse 前缀），新增 W1/W2/W3：
      I（水墨帧）→ W（3–4s 微动，只让墨动）→ 剪辑里接在"过曝回落"之后。
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
OUT = HERE / "燕云冲击帧-墨动-16x9-v12.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T13:10:00.000+08:00"
PREFIX = "ywse"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V11 = load_mod("yanwu_v11", "build-燕云冲击帧-首尾帧-v11.py")
DOC = V11.build()
ID11 = V11.ID
ID12 = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in ID11}
MAP = {ID11[k]: ID12[k] for k in ID11}


def rm(s):
    if not isinstance(s, str):
        return s
    for old, new in MAP.items():
        s = s.replace(old, new)
    return s


# ---------------------------------------------------------------- ID 重映射
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
    e["id"] = "edge-" + hashlib.md5(("e" + e["sourceNodeId"] + e["targetNodeId"]).encode()).hexdigest()[:8]
for g in canvas["groups"]:
    g["nodeIds"] = [MAP[x] for x in g["nodeIds"]]
    g["id"] = "g-" + hashlib.md5(("g" + g["id"]).encode()).hexdigest()[:8]

# ---------------------------------------------------------------- I 提示词：换手感写法
HAND = (
    "【气韵】这是一张**宣纸上的水墨定格**，不是插画、不是 3D、不是照片。纸筋与帘纹可见，墨分五阶（焦、浓、重、淡、清），"
    "最深处近纯黑；破墨与涨墨：爆点一侧的墨还在洇，边缘是毛的；一道飞白擦出去，笔断意连。\n"
    "【笔与动】墨点悬在半空、衣带未落、发丝有余势——是「动作刚停住的那一瞬」，不是摆好的海报；"
    "笔与笔之间要留「没画完」的地方。\n"
    "【光影】一道硬侧光：暗部压到近黑，亮部过曝成纸白，没有柔光过渡，没有体积光。\n"
    "【人】只给轮廓：脸在暗部，只露一只眼，不刻画五官细节。\n"
)
EXTRA_NEG = ("、塑料感、平滑渐变、矢量感、精致插画、居中对称、构图过满、体积光、柔光过渡、"
             "整张只有一种墨色、死静的摆拍感")


def upgrade(prompt):
    p = prompt
    if "【气韵】" not in p:
        p = p.replace("【限制】", HAND + "【限制】", 1)
    p = p.replace("负向：", "禁止：矢量感、居中对称、死静的摆拍感；负向：", 1)
    if "死静的摆拍感" not in p:
        p = p.rstrip() + EXTRA_NEG + "。"
    return p


for n in canvas["nodes"]:
    if n["type"] == "gen-image" and n["meta"]["label"].startswith("【待生成】I"):
        mp = n["params"]["model_params"]
        mp["prompt"] = upgrade(mp["prompt"])

# ---------------------------------------------------------------- 新增 W：墨动
W_PROMPT = """【首帧锁定】首帧使用 {img}：画面已经是水墨冲击帧的完成稿，构图、人物位置、剑的角度、颜色、明暗分布一帧都不许变。
【任务】只让"墨"动：墨缓慢晕开、墨点悬浮后缓缓飘落、衣摆与发丝带着极小的余势轻摆、纸纹有一层很薄的呼吸感；
幅度要小到像"画面在呼吸"，不是"画面在动"。
【禁止】人物与剑移动位置、改构图、改颜色、加新的笔触、镜头推拉摇移、切镜、加字、变回实色。
【时长】4 秒；首尾几乎一致，便于循环或直接定格。
"""

nodes = canvas["nodes"]
pairs = [(e["sourceNodeId"], e["targetNodeId"]) for e in canvas["edges"]]
ix, iy = 3220, 20
w_ids = []
for k, (ik, nk) in enumerate((("I1", "W1"), ("I2", "W2"), ("I3", "W3"))):
    wid = "node-" + hashlib.md5((PREFIX + nk).encode()).hexdigest()[:8]
    w_ids.append(wid)
    prompt = W_PROMPT.format(img="{{" + ID12[ik] + "}}")
    node = {
        "id": wid, "type": "gen-video", "mainOutputId": None,
        "meta": {"x": ix, "y": iy + k * 320, "width": 320, "height": 280,
                 "label": f"【待生成】{nk} {['①','②','③'][k]} 墨动 4s（只让墨动）", "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1, "model_id": "seedance-2.5",
            "model_params": {
                "_task_mode": "standard", "prompt": prompt, "_reference_way": "reference",
                "reference_images": [{"node_id": ID12[ik]}],
                "reference_videos": [], "reference_audios": [],
                "first_frame_image": {"node_id": ID12[ik]},
                "last_frame_image": None,
                "aspect_ratio": "16:9", "resolution": "720p", "duration": 4,
                "generate_audio": True, "seed": -1,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }
    nodes.append(node)
    pairs.append((ID12[ik], wid))

canvas["edges"] = [{
    "id": "edge-" + hashlib.md5(("e" + s + t).encode()).hexdigest()[:8],
    "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
    "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
} for s, t in pairs]

canvas["groups"].append({
    "id": "g-w-1", "nodeIds": w_ids,
    "bounds": {"x": ix - 18, "y": iy - 46, "width": 356, "height": 3 * 320 + 68},
    "label": "07 墨动 W · 只让墨动（参考片开头那 1–1.5 秒）",
    "style": {"accent": None, "opacity": None, "borderColor": "#C8A15B"},
    "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
})

canvas["name"] = "燕云冲击帧 · 首尾帧 + 墨动（16:9）v12"
canvas["description"] = ("K 起势 + E 尾帧夹住招式（seedance-2.5）→ I 水墨帧改画（手感写法）→ "
                         "W 只让墨动的 4s 微动。剪辑链：V 实色 → 过曝回落 → W 墨动 → 定格/渐暗。")
DOC["exportedAt"] = CREATED


# ---------------------------------------------------------------- 自检
def self_check(doc):
    c = doc["canvas"]
    problems = []
    by_id = {n["id"]: n for n in c["nodes"]}
    if len(by_id) != len(c["nodes"]):
        problems.append("节点 ID 重复")
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in c["edges"]}
    grp = {}
    for g in c["groups"]:
        for x in g["nodeIds"]:
            if x in grp:
                problems.append(f"节点重复分组: {x}")
            grp[x] = g["label"]
    for n in c["nodes"]:
        if n["id"] not in grp:
            problems.append(f"节点不在分组: {n['id']}")
    for s, t in edge_set:
        for lab, ids in {g["label"]: g["nodeIds"] for g in c["groups"]}.items():
            if s in ids and t in ids:
                problems.append(f"同组内依赖边: [{lab}]")
    for n in c["nodes"]:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        prompt = mp.get("prompt") or ""
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        lf = (mp.get("last_frame_image") or {}).get("node_id")
        lab = n["meta"]["label"]
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for t in toks:
            if t not in by_id:
                problems.append(f"引用不存在: {lab} -> {t}")
            if t not in refs and t not in (ff, lf):
                problems.append(f"引用未挂字段: {lab} -> {t}")
        for r in refs + [x for x in (ff, lf) if x]:
            if (r, n["id"]) not in edge_set:
                problems.append(f"字段挂了没连线: {lab} <- {r}")
        if len(prompt) > 2000:
            problems.append(f"prompt 超 2000 字: {lab} ({len(prompt)})")
    for a_i, a in enumerate(c["groups"]):
        ba = a["bounds"]
        for b in c["groups"][a_i + 1:]:
            bb = b["bounds"]
            if (ba["x"] < bb["x"] + bb["width"] and ba["x"] + ba["width"] > bb["x"]
                    and ba["y"] < bb["y"] + bb["height"] and ba["y"] + ba["height"] > bb["y"]):
                problems.append(f"分组重叠: {a['label']} / {b['label']}")
    return problems


if __name__ == "__main__":
    probs = self_check(DOC)
    OUT.write_text(json.dumps(DOC, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    c = DOC["canvas"]
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(c['nodes'])} / 边 {len(c['edges'])} / 组 {len(c['groups'])}")
    for n in c["nodes"]:
        if n["meta"]["label"].startswith(("【待生成】I", "【待生成】W", "【待生成】V")):
            print(f"  {n['meta']['label'][:30]:<30} {len(n['params']['model_params']['prompt'])} 字")
    if probs:
        print("自检问题:")
        for p in probs:
            print("  [X]", p)
    else:
        print("自检通过 OK")

