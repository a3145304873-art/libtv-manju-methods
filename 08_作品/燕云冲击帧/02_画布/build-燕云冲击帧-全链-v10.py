# -*- coding: utf-8 -*-
"""燕云冲击帧 · 全链单画布 v10

一条画布跑完：素材 → 设定母版 + 资产 → 起势 → 招式 → 截帧 → 冲击帧。
做法：复用 v9 的资产 prompt 与 v7 的镜头 prompt（避免手抄出错），只把节点 ID 重映射到本画布。

结构（8 组，按跑序）：
  00 素材        P1 原始人物 / P2 原始武器 / S1 设定
  01 母版+锚点   A0 设定母版（人看，不接下游）/ A1 脸 / A2 正面全身 / A5 武器
  02 资产派生    A3 侧面 / A4 背面 / A6 握剑手
  03 起势        K1 刺 / K2 斩 / K3 撩
  04 招式        V1 / V2 / V3（4s，止于实色定格）
  05 定格帧      T1 / T2 / T3（占位，截末帧替换）
  06 冲击帧      I1 / I2 / I3（水墨红黑，改画自 T）
  07 说明        S0
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
OUT = HERE / "燕云冲击帧-全链-16x9-v10.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T12:10:00.000+08:00"
PREFIX = "ywsc"
BY = "linguanxi"


def load_mod(name, filename):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V7 = load_mod("yanwu_v7", "build-燕云冲击帧-刺斩撩-v7.py")
V9 = load_mod("yanwu_v9", "build-燕云冲击帧-资产板-v9.py")

KEYS = ("P1", "P2", "S1",
        "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "V1", "V2", "V3", "T1", "T2", "T3",
        "I1", "I2", "I3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode("utf-8")).hexdigest()[:8] for k in KEYS}


def remap(text, mapping):
    for old, new in mapping.items():
        text = re.sub(r"(?<![0-9A-Za-z])" + re.escape(old) + r"(?![0-9A-Za-z])", new, text)
    return text


# 资产 prompt：v9 的 ID → 本画布
ASSET_MAP = {}
for k in ("P1", "P2", "A1", "A2", "A3", "A4", "A5", "A6", "A0"):
    ASSET_MAP[V9.ID[k]] = ID[k]

# 镜头 prompt：v7 的 P1/P2 换成清晰资产；K/T 映射到本画布
SHOT_MAP = {"K1": "K1", "K2": "K2", "K3": "K3", "T1": "T1", "T2": "T2", "T3": "T3",
            "P1": "A2", "P2": "A5"}
SHOT_ID_MAP = {V7.ID[k]: ID[v] for k, v in SHOT_MAP.items()}

P_A0 = remap(V9.P_A0, ASSET_MAP)
P_A1 = remap(V9.P_A1, ASSET_MAP)
P_A2 = remap(V9.P_A2, ASSET_MAP)
P_A3 = remap(V9.P_A3, ASSET_MAP)
P_A4 = remap(V9.P_A4, ASSET_MAP)
P_A5 = remap(V9.P_A5, ASSET_MAP)
P_A6 = remap(V9.P_A6, ASSET_MAP)

P_K1 = remap(V7.P_K1, SHOT_ID_MAP)
P_K2 = remap(V7.P_K2, SHOT_ID_MAP)
P_K3 = remap(V7.P_K3, SHOT_ID_MAP)
P_V1 = remap(V7.P_V1, SHOT_ID_MAP)
P_V2 = remap(V7.P_V2, SHOT_ID_MAP)
P_V3 = remap(V7.P_V3, SHOT_ID_MAP)
P_I1 = remap(V7.P_I1, SHOT_ID_MAP)
P_I2 = remap(V7.P_I2, SHOT_ID_MAP)
P_I3 = remap(V7.P_I3, SHOT_ID_MAP)

# 近景那一镜（刺）额外挂脸部资产：在引用行后面补一句
P_K1 = P_K1.replace("【引用图片说明】",
                    "【引用图片说明】" + "{{" + ID["A1"] + "}}＝脸部特写（锁五官与白发长度）；", 1)

S1_TEXT = """【角色与武器设定 · 只读】
人物：年轻男性剑客，白发（长过胸、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，
手腕黑色护腕，深色靴；双臂缠绕淡薄的冰霜气劲；面部清瘦、眉压低、眼神冷静；本组不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑；剑身半透、内部龙形霜纹；护手一道极细虹彩（青→品红）；
护手根部玉绿色晶簇；剑柄缠绳；剑尖明光偏暖（曜日）。

【这一条画布里全都有】原始截图 → 设定母版 + 干净资产 → 三条片（刺/斩/撩）→ 冲击帧。
跑序按组号：00 → 01 → 02 → 03 → 04 → 05 → 06。
"""

S0_TEXT = """【全链一条画布 · 先读】

跑序（组号＝顺序，组内并行、组间串行）：
00 素材（P1/P2 已预填，可直接跑）
→ 01 母版 + 锚点：A0 设定母版（一张看完所有设定，**不接下游**）、A1 脸、A2 正面全身、A5 武器
   · 先跑这一组；A2 是这组里最关键的一张——它对了，后面全对；它错了，全部跟着错
→ 02 资产派生：A3 侧面、A4 背面、A6 握剑手（只参考 A2 / A5，保证同一个人、同一件器）
→ 03 起势：K1 刺 / K2 斩 / K3 撩（各用 A1+A2+A5 当参考）
→ 04 招式：V1/V2/V3（4s，seedance，**写实**，结尾停在实色定格，视频里不转水墨）
→ 05 定格帧：T1/T2/T3（占位图；跑完 V 后取最后一帧替换，节点 ID 不变）
→ 06 冲击帧：I1/I2/I3（把 T 改画成**水墨红黑**冲击帧，2K）

三个"纪律"：
1. **K/V 里不许出现红**，红只活在 I（冲击帧）里；
2. **V 里不许转水墨**——一转，末帧就不是实色定格，T 截出来没法用；
3. **T 没替换之前别跑 06**，否则出来的是占位卡的画。

剪辑（每镜）：
V 演完 → 停在定格帧 → 1 帧白（或 1 白 1 负片）→ 切冲击帧 I → I 保持 1.8–2.3s → 渐暗 3 帧。
白闪帧数用 02_画布/量白闪.py 量，别猜。

模型：生图 gpt-image-2（**全部 1K / medium**）；视频 seedance-2.0-mini（4s · 16:9 · 720p · 带音）。
三镜：刺 →（近景）/ 斩 ↔（中景）/ 撩 ↗（半身），方向与景别都不同，别拍成同一条的三个角度。
"""


# ---------------------------------------------------------------- 节点工厂
def _base(n, t, x, y, w, h, label):
    return {
        "id": n, "type": t, "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": w, "height": h, "label": label, "resourceType": None},
        "outputs": [], "params": None, "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def input_image(n, x, y, label, up, w=320, h=200):
    out = {
        "id": f"output-{n[5:13]}", "status": "done", "error": None,
        "value": up["url"], "cover": None, "name": up["name"],
        "resolution": {"width": up["width"], "height": up["height"]},
        "source": None, "batchId": None, "execution": None, "graphRunId": None,
        "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        "metadata": {"size": up["size"], "md5": up["md5"]},
    }
    node = _base(n, "input-image", x, y, w, h, label)
    node["mainOutputId"] = out["id"]
    node["outputs"] = [out]
    return node


def input_text(n, x, y, w, h, label, text):
    out = {
        "id": f"output-{n[5:13]}", "status": "done", "error": None,
        "value": text, "cover": None, "name": label,
        "resolution": None, "source": None, "batchId": None, "execution": None,
        "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        "metadata": None,
    }
    node = _base(n, "input-text", x, y, w, h, label)
    node["mainOutputId"] = out["id"]
    node["outputs"] = [out]
    return node


def gen_image(n, x, y, label, prompt, refs, size="1K", quality="medium"):
    node = _base(n, "gen-image", x, y, 320, 280, label)
    node["params"] = {
        "num": 1, "model_id": "gpt-image-2",
        "model_params": {
            "prompt": prompt,
            "reference_images": [{"node_id": r} for r in refs],
            "aspect_ratio": "16:9", "image_size": size,
            "width": 1024, "height": 1024, "quality": quality,
            "output_format": "png", "moderation": "low", "auto_compress": True,
        },
    }
    return node


def gen_video(n, x, y, label, prompt, refs, first):
    node = _base(n, "gen-video", x, y, 320, 280, label)
    node["params"] = {
        "num": 1, "model_id": "seedance-2.0-mini",
        "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": r} for r in refs],
            "reference_audios": [],
            "first_frame_image": {"node_id": first},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": 4,
            "generate_audio": True, "watermark": False,
        },
    }
    return node


def build():
    i = ID
    ups, src_name = V7.load_placeholders()
    up0 = V9.P1_UP
    up1 = V9.P2_UP

    nodes = [
        input_image(i["P1"], 20, 20, "【素材】P1 原始人物截图", up0),
        input_image(i["P2"], 20, 240, "【素材】P2 原始武器截图", up1),
        input_text(i["S1"], 20, 470, 320, 420, "S1 角色与武器设定", S1_TEXT),

        gen_image(i["A0"], 420, 20, "【待生成】A0 设定母版（一张看完所有设定）", P_A0, [i["P1"], i["P2"]]),
        gen_image(i["A1"], 820, 20, "【待生成】A1 脸部特写", P_A1, [i["P1"]]),
        gen_image(i["A2"], 820, 340, "【待生成】A2 正面全身（锚）", P_A2, [i["P1"]]),
        gen_image(i["A5"], 820, 660, "【待生成】A5 武器白底正交", P_A5, [i["P2"]]),

        gen_image(i["A3"], 1220, 20, "【待生成】A3 侧面 90°（派生自 A2）", P_A3, [i["A2"]]),
        gen_image(i["A4"], 1220, 340, "【待生成】A4 背面（派生自 A2）", P_A4, [i["A2"]]),
        gen_image(i["A6"], 1220, 660, "【待生成】A6 握剑的手", P_A6, [i["P1"], i["P2"]]),

        gen_image(i["K1"], 1620, 20, "【待生成】K1 ① 起势 · 刺 1K", P_K1,
                  [i["A1"], i["A2"], i["A5"]], size="1K", quality="medium"),
        gen_image(i["K2"], 1620, 340, "【待生成】K2 ② 起势 · 斩 1K", P_K2,
                  [i["A2"], i["A5"]], size="1K", quality="medium"),
        gen_image(i["K3"], 1620, 660, "【待生成】K3 ③ 起势 · 撩 1K", P_K3,
                  [i["A2"], i["A5"]], size="1K", quality="medium"),

        gen_video(i["V1"], 2020, 20, "【待生成】V1 ① 4s · 刺 →", P_V1,
                  [i["A2"], i["A5"]], i["K1"]),
        gen_video(i["V2"], 2020, 340, "【待生成】V2 ② 4s · 斩 ↔", P_V2,
                  [i["A2"], i["A5"]], i["K2"]),
        gen_video(i["V3"], 2020, 660, "【待生成】V3 ③ 4s · 撩 ↗", P_V3,
                  [i["A2"], i["A5"]], i["K3"]),

        input_image(i["T1"], 2420, 20, "【占位】T1 ① 定格帧 · 跑完 V1 取末帧替换", ups[0]),
        input_image(i["T2"], 2420, 340, "【占位】T2 ② 定格帧 · 跑完 V2 取末帧替换", ups[1]),
        input_image(i["T3"], 2420, 660, "【占位】T3 ③ 定格帧 · 跑完 V3 取末帧替换", ups[2]),

        gen_image(i["I1"], 2820, 20, "【待生成】I1 ① 冲击帧 · 向心放射", P_I1,
                  [i["T1"], i["A2"], i["A5"]]),
        gen_image(i["I2"], 2820, 340, "【待生成】I2 ② 冲击帧 · 横向墨痕", P_I2,
                  [i["T2"], i["A2"], i["A5"]]),
        gen_image(i["I3"], 2820, 660, "【待生成】I3 ③ 冲击帧 · 斜向墨痕", P_I3,
                  [i["T3"], i["A2"], i["A5"]]),

        input_text(i["S0"], 420, 1010, 1520, 420, "S0 全链说明 · 先读", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["A0"]), (i["P2"], i["A0"]),
        (i["P1"], i["A1"]), (i["P1"], i["A2"]), (i["P2"], i["A5"]),
        (i["A2"], i["A3"]), (i["A2"], i["A4"]), (i["P1"], i["A6"]), (i["P2"], i["A6"]),
        (i["A1"], i["K1"]), (i["A2"], i["K1"]), (i["A5"], i["K1"]),
        (i["A2"], i["K2"]), (i["A5"], i["K2"]),
        (i["A2"], i["K3"]), (i["A5"], i["K3"]),
        (i["A2"], i["V1"]), (i["A5"], i["V1"]), (i["K1"], i["V1"]),
        (i["A2"], i["V2"]), (i["A5"], i["V2"]), (i["K2"], i["V2"]),
        (i["A2"], i["V3"]), (i["A5"], i["V3"]), (i["K3"], i["V3"]),
        (i["T1"], i["I1"]), (i["A2"], i["I1"]), (i["A5"], i["I1"]),
        (i["T2"], i["I2"]), (i["A2"], i["I2"]), (i["A5"], i["I2"]),
        (i["T3"], i["I3"]), (i["A2"], i["I3"]), (i["A5"], i["I3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bounds_for(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        {"id": "group-ywsc-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 素材", "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywsc-1", "nodeIds": [i["A0"], i["A1"], i["A2"], i["A5"]],
         "bounds": bounds_for([i["A0"], i["A1"], i["A2"], i["A5"]]),
         "label": "01 母版 + 锚点（先跑）", "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywsc-2", "nodeIds": [i["A3"], i["A4"], i["A6"]],
         "bounds": bounds_for([i["A3"], i["A4"], i["A6"]]),
         "label": "02 资产派生", "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywsc-3", "nodeIds": [i["K1"], i["K2"], i["K3"]],
         "bounds": bounds_for([i["K1"], i["K2"], i["K3"]]),
         "label": "03 起势 K1/K2/K3（刺/斩/撩）", "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywsc-4", "nodeIds": [i["V1"], i["V2"], i["V3"]],
         "bounds": bounds_for([i["V1"], i["V2"], i["V3"]]),
         "label": "04 招式 4s · 止于实色定格", "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "group-ywsc-5", "nodeIds": [i["T1"], i["T2"], i["T3"]],
         "bounds": bounds_for([i["T1"], i["T2"], i["T3"]]),
         "label": "05 定格帧（占位，截末帧替换）", "style": {"accent": None, "opacity": None, "borderColor": "#C8C2B4"}},
        {"id": "group-ywsc-6", "nodeIds": [i["I1"], i["I2"], i["I3"]],
         "bounds": bounds_for([i["I1"], i["I2"], i["I3"]]),
         "label": "06 冲击帧 · 水墨红黑（改画自 T）", "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}},
        {"id": "group-ywsc-7", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "07 全链说明", "style": {"accent": None, "opacity": None, "borderColor": "#888888"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    return {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 全链单画布（资产→三招→冲击帧）v10",
            "description": ("一条画布跑完全部：素材 → A0 设定母版 + A1/A2/A5 锚点 + A3/A4/A6 派生 → "
                            "K 起势（刺/斩/撩）→ V 招式（4s，止于实色定格）→ T 截帧 → I 水墨红黑冲击帧。"
                            f"占位图取自 {src_name}。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywsc-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
                "targetNodeId": t, "targetHandle": "input",
                "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
            } for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }


def self_check(doc):
    c = doc["canvas"]
    nodes, edges, groups = c["nodes"], c["edges"], c["groups"]
    by_id = {n["id"]: n for n in nodes}
    problems = []
    if len(by_id) != len(nodes):
        problems.append("节点 ID 重复")
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    node_group = {}
    for g in groups:
        for n in g["nodeIds"]:
            if n in node_group:
                problems.append(f"节点重复分组: {n}")
            node_group[n] = g["label"]
    for n in nodes:
        if n["id"] not in node_group:
            problems.append(f"节点不在分组: {n['id']}")
    gmap = {g["label"]: g["nodeIds"] for g in groups}
    for s, t in edge_set:
        for lab, ids in gmap.items():
            if s in ids and t in ids:
                problems.append(f"同组内依赖边: [{lab}] {s}->{t}")
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = (n.get("params") or {}).get("model_params") or {}
        prompt = mp.get("prompt") or ""
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        label = n["meta"]["label"]
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for tk in toks:
            if tk not in by_id:
                problems.append(f"引用节点不存在: {label} -> {tk}")
            if tk not in refs and tk != ff:
                problems.append(f"引用未挂字段: {label} -> {tk}")
        for r in refs + ([ff] if ff else []):
            if (r, n["id"]) not in edge_set:
                problems.append(f"字段挂了没连线: {label} <- {r}")
            rn = by_id.get(r)
            if rn and rn["type"] == "input-image" and not rn.get("outputs"):
                problems.append(f"被引用的上传节点是空的: {label} <- {r}")
        if n["type"] == "gen-video":
            if ff and ff not in toks:
                problems.append(f"首帧未在正文点名: {label}")
            if len(prompt) > 2000:
                problems.append(f"prompt 超 2000 字: {label} ({len(prompt)})")
            if mp.get("duration") != 4:
                problems.append(f"时长不是 4s: {label}")
    for a_i, a in enumerate(groups):
        ba = a["bounds"]
        for b in groups[a_i + 1:]:
            bb = b["bounds"]
            if (ba["x"] < bb["x"] + bb["width"] and ba["x"] + ba["width"] > bb["x"]
                    and ba["y"] < bb["y"] + bb["height"] and ba["y"] + ba["height"] > bb["y"]):
                problems.append(f"分组 bounds 重叠: {a['label']} / {b['label']}")
    return problems, edges


def main():
    doc = build()
    problems, edges = self_check(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    c = doc["canvas"]
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(c['nodes'])} / 边 {len(edges)} / 组 {len(c['groups'])}")
    for n in c["nodes"]:
        if n["type"] in ("gen-image", "gen-video"):
            print(f"  {n['meta']['label'][:34]:<34} {len(n['params']['model_params']['prompt']):>4} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()


