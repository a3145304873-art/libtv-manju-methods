# -*- coding: utf-8 -*-
"""燕云冲击帧 v11：首帧 + 尾帧（seedance-2.5 的 last_frame_image）

依据（2026-10-30 查证）：Monet 的 gen-video 参数里确实有 last_frame_image，但**按模型**：
  kling-video-o3 ✅｜seedance-2.5 ✅｜wan30-video ✅｜vidu-q4-preview ❌
我之前说"平台没有尾帧输入"是错的——那句话只对 vidu / seedance-2.0-mini 成立（我们之前只用过这两个）。

v11 的改动：
  1. 视频模型换成 seedance-2.5（支持尾帧），duration 5s，编辑时裁；
  2. 新增 E1/E2/E3「结束姿势」图（实色），作为 last_frame_image；
  3. 动作被首尾两张图夹住，模型必须走到位——不需要靠文字说服它；
  4. **删掉 T 截帧占位**：I 直接从 E 改画，手工步骤从 2 个降到 1 个（只剩剪辑补白闪）。
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
OUT = HERE / "燕云冲击帧-首尾帧-16x9-v11.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T12:40:00.000+08:00"
PREFIX = "ywsd"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V10 = load_mod("yanwu_v10", "build-燕云冲击帧-全链-v10.py")

KEYS = ("P1", "P2", "S1",
        "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "E1", "E2", "E3",
        "V1", "V2", "V3", "I1", "I2", "I3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}

MAP = {V10.ID[k]: ID[k] for k in V10.KEYS if k in ID}
MAP[V10.ID["T1"]] = ID["E1"]
MAP[V10.ID["T2"]] = ID["E2"]
MAP[V10.ID["T3"]] = ID["E3"]


def remap(text):
    for old, new in MAP.items():
        text = re.sub(r"(?<![0-9A-Za-z])" + re.escape(old) + r"(?![0-9A-Za-z])", new, text)
    return text


def tok(k):
    return "{{" + ID[k] + "}}"


# ------------------------------------------------ 复用 v10 的资产 / 起势 / 冲击帧 prompt
P_A0, P_A1, P_A2, P_A3 = remap(V10.P_A0), remap(V10.P_A1), remap(V10.P_A2), remap(V10.P_A3)
P_A4, P_A5, P_A6 = remap(V10.P_A4), remap(V10.P_A5), remap(V10.P_A6)
P_K1, P_K2, P_K3 = remap(V10.P_K1), remap(V10.P_K2), remap(V10.P_K3)
P_I1, P_I2, P_I3 = remap(V10.P_I1), remap(V10.P_I2), remap(V10.P_I3)

# ------------------------------------------------ 新增：结束姿势（尾帧）
P_E1 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K1')}＝起势（同一人同一招，只借人物特征与机位，姿势要换成刺到底）；{tok('A1')}＝脸（锁五官）；{tok('A2')}＝全身（锁服装/比例）；{tok('A5')}＝武器。
【画面】近景（胸以上＋持剑手），**刺到最远的那一帧**：右臂完全伸直、剑沿纵深刺出（剑尖朝镜头略偏左、近大远小明显）、
肩线斜切画面、身体拧到位；脸在暗部，只有眼窝受光，眼神锁定；衣摆与发丝被出剑带得向后拉。
【构图/机位】16:9 横版，近景，人物占画面高约 90%，脸在右三分；剑身从右下贯向左上。
【光影/材质】侧逆光、冷调、实色电影感；剑身一道冷白反光；**全图不许出现红色**。
负向：横持剑、剑身与画面平行、手臂弯曲、收剑、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、UI、卡通。
"""

P_E2 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K2')}＝起势（同一人同一招，只借人物特征与机位，姿势要换成斩完的收势）；{tok('A2')}＝全身（锁服装/比例）；{tok('A5')}＝武器。
【画面】中景全身，**斩完的收势**：剑横在身体左前方、与肩同高、刃口朝外；上身向左拧约 15°、重心前移一档；
右臂伸展、肩线斜切；衣摆与白发向左甩出，脚下雪面被扫起一层雪雾。
【构图/机位】16:9 横版，平视略低，中景全身；人物占画面高约 75%，站右三分。
【光影/材质】侧逆光、冷调、实色电影感；剑身一道冷白反光；**全图不许出现红色**。
负向：剑在右侧、剑未斩出、正对镜头站立、手臂弯曲、残影、多手多剑、人物过小、红、彩色光效、文字、水印、logo、UI、卡通。
"""

P_E3 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K3')}＝起势（同一人同一招，只借人物特征与机位，姿势要换成撩到顶）；{tok('A2')}＝全身（锁服装/比例）；{tok('A5')}＝武器。
【画面】半身，**撩到顶**：剑举在右肩斜上方、刃口朝上、剑尖指右上方；右臂举过肩、肩线打开；
身体随势上拔、下颌微抬；衣摆与白发向上翻卷。
【构图/机位】16:9 横版，半身（腰以上），人物占画面高约 85%，站右三分；剑尖在画面右上方。
【光影/材质】侧逆光、冷调、实色电影感；刃口一道冷白反光；**全图不许出现红色**。
负向：剑在下方、剑尖朝地、剑未撩起、正对镜头站立、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、UI、卡通。
"""


# ------------------------------------------------ 视频 prompt：加尾帧锁定，节拍改成 5s
def with_tail(prompt, e_key):
    line = (f"【尾帧锁定】最后一帧必须停在 {tok(e_key)} 的姿势上：剑的位置、手臂角度、身体朝向、镜头景别全部对齐，"
            "不要自己改收势，也不要提前停下。\n")
    lines = prompt.split("\n")
    out = []
    for ln in lines:
        out.append(ln)
        if ln.startswith("【首帧锁定】"):
            out.append(line.rstrip("\n"))
    txt = "\n".join(out)
    txt = txt.replace("16:9 · 4 秒", "16:9 · 5 秒")
    txt = txt.replace("0.0–0.5 秒", "0.0–0.6 秒")
    txt = txt.replace("0.5–1.5 秒", "0.6–2.0 秒")
    txt = txt.replace("0.6–1.5 秒", "0.6–2.0 秒")
    txt = txt.replace("1.5–4.0 秒", "2.0–5.0 秒")
    txt = txt.replace("保持这个结束姿势不动", "保持这个结束姿势直到第 5 秒")
    txt = txt.replace("保持横扫收势不动", "保持横扫收势直到第 5 秒")
    txt = txt.replace("保持劈完的姿势不动", "保持结束姿势直到第 5 秒")
    txt = txt.replace("保持刺到最远的姿势不动", "保持刺到最远的姿势直到第 5 秒")
    txt = txt.replace("保持撩到位的姿势不动", "保持撩到位的姿势直到第 5 秒")
    return txt


P_V1 = with_tail(remap(V10.P_V1), "E1")
P_V2 = with_tail(remap(V10.P_V2), "E2")
P_V3 = with_tail(remap(V10.P_V3), "E3")

S1_TEXT = """【角色与武器设定 · 只读】
人物：年轻男性剑客，白发（长过胸、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，
手腕黑色护腕，深色靴；双臂缠绕淡薄的冰霜气劲；面部清瘦、眉压低、眼神冷静；本组不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑；剑身半透、内部龙形霜纹；护手一道极细虹彩（青→品红）；
护手根部玉绿色晶簇；剑柄缠绳；剑尖明光偏暖（曜日）。

【本画布用首尾帧】K＝起势（实色首帧），E＝结束姿势（实色尾帧），V 被两张图夹住——
模型没有"偷懒摆姿势"的空间，必须把招式走完。I 直接从 E 改画，不再需要手工截帧。
"""

S0_TEXT = """【首尾帧版 · 先读】

为什么这版能解决"动作不发生"：
之前只给首帧，模型走最省力路径（原地亮剑）。现在给**首帧 K + 尾帧 E**，
它必须从 K 的姿势过渡到 E 的姿势，动作被两张图夹出来——这比在文字里写"请刺出去"有效得多。

跑序（组＝跑序）：
00 素材（P1/P2 已预填）
→ 01 母版 + 锚点：A0 设定母版（人看不接下游）、A1 脸、A2 正身、A5 武器
→ 02 资产派生：A3 侧面、A4 背面、A6 握剑手
→ 03 起势 K1/K2/K3（实色）
→ 04 尾帧 E1/E2/E3（实色结束姿势）★ 这组是新的，先跑它再跑视频
→ 05 招式 V1/V2/V3：seedance-2.5 · 5s · 16:9 · 720p，first=K，last=E
→ 06 冲击帧 I1/I2/I3：把 E 改画成水墨红黑冲击帧

和上一版的区别：
· 视频模型 vidu/2.0-mini → **seedance-2.5**（只有它这一档支持 last_frame_image）
· 时长 4s → **5s**（2.5 的档位），编辑时裁到 3–3.2s
· 删掉 T 截帧占位：I 从 E 改画，不用再截末帧替换
· 剩下的手工只有：挑资产 + 剪辑补白闪

尾帧同时挂在 last_frame_image 和 reference_images 两处：字段是数据通道（平台只认字段），参考位是给检查器与肉眼看的（检查器还不认 last_frame 字段）。
模型：生图 gpt-image-2（全部 1K / medium）；视频 seedance-2.5（5s · 16:9 · 720p · 带音）。
"""


def gen_video_25(n, x, y, label, prompt, refs, first, last):
    node = V10._base(n, "gen-video", x, y, 320, 280, label)
    node["params"] = {
        "num": 1, "model_id": "seedance-2.5",
        "model_params": {
            "_task_mode": "standard",
            "prompt": prompt,
            "_reference_way": "reference",
            "reference_images": [{"node_id": r} for r in refs],
            "reference_videos": [],
            "reference_audios": [],
            "first_frame_image": {"node_id": first},
            "last_frame_image": {"node_id": last},
            "aspect_ratio": "16:9", "resolution": "720p", "duration": 5,
            "generate_audio": True, "seed": -1,
        },
    }
    return node


def build():
    i = ID
    gi = V10.gen_image
    ii = V10.input_image
    it = V10.input_text

    nodes = [
        ii(i["P1"], 20, 20, "【素材】P1 原始人物截图", V10.V9.P1_UP),
        ii(i["P2"], 20, 240, "【素材】P2 原始武器截图", V10.V9.P2_UP),
        it(i["S1"], 20, 470, 320, 420, "S1 角色与武器设定", S1_TEXT),

        gi(i["A0"], 420, 20, "【待生成】A0 设定母版（一张看完所有设定）", P_A0, [i["P1"], i["P2"]]),
        gi(i["A1"], 820, 20, "【待生成】A1 脸部特写", P_A1, [i["P1"]]),
        gi(i["A2"], 820, 340, "【待生成】A2 正面全身（锚）", P_A2, [i["P1"]]),
        gi(i["A5"], 820, 660, "【待生成】A5 武器白底正交", P_A5, [i["P2"]]),

        gi(i["A3"], 1220, 20, "【待生成】A3 侧面 90°（派生自 A2）", P_A3, [i["A2"]]),
        gi(i["A4"], 1220, 340, "【待生成】A4 背面（派生自 A2）", P_A4, [i["A2"]]),
        gi(i["A6"], 1220, 660, "【待生成】A6 握剑的手", P_A6, [i["P1"], i["P2"]]),

        gi(i["K1"], 1620, 20, "【待生成】K1 ① 起势 · 刺", P_K1,
           [i["A1"], i["A2"], i["A5"]], size="1K", quality="medium"),
        gi(i["K2"], 1620, 340, "【待生成】K2 ② 起势 · 斩", P_K2, [i["A2"], i["A5"]],
           size="1K", quality="medium"),
        gi(i["K3"], 1620, 660, "【待生成】K3 ③ 起势 · 撩", P_K3, [i["A2"], i["A5"]],
           size="1K", quality="medium"),

        gi(i["E1"], 2020, 20, "【待生成】E1 ① 尾帧 · 刺到底", P_E1,
           [i["K1"], i["A1"], i["A2"], i["A5"]], size="1K", quality="medium"),
        gi(i["E2"], 2020, 340, "【待生成】E2 ② 尾帧 · 斩收势", P_E2,
           [i["K2"], i["A2"], i["A5"]], size="1K", quality="medium"),
        gi(i["E3"], 2020, 660, "【待生成】E3 ③ 尾帧 · 撩到顶", P_E3,
           [i["K3"], i["A2"], i["A5"]], size="1K", quality="medium"),

        gen_video_25(i["V1"], 2420, 20, "【待生成】V1 ① 5s · 刺（首尾帧）", P_V1,
                     [i["A2"], i["A5"], i["E1"]], i["K1"], i["E1"]),
        gen_video_25(i["V2"], 2420, 340, "【待生成】V2 ② 5s · 斩（首尾帧）", P_V2,
                     [i["A2"], i["A5"], i["E2"]], i["K2"], i["E2"]),
        gen_video_25(i["V3"], 2420, 660, "【待生成】V3 ③ 5s · 撩（首尾帧）", P_V3,
                     [i["A2"], i["A5"], i["E3"]], i["K3"], i["E3"]),

        gi(i["I1"], 2820, 20, "【待生成】I1 ① 冲击帧 · 向心放射", P_I1,
           [i["E1"], i["A2"], i["A5"]]),
        gi(i["I2"], 2820, 340, "【待生成】I2 ② 冲击帧 · 横向墨痕", P_I2,
           [i["E2"], i["A2"], i["A5"]]),
        gi(i["I3"], 2820, 660, "【待生成】I3 ③ 冲击帧 · 斜向墨痕", P_I3,
           [i["E3"], i["A2"], i["A5"]]),

        it(i["S0"], 420, 1010, 1520, 460, "S0 首尾帧说明 · 先读", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["A0"]), (i["P2"], i["A0"]),
        (i["P1"], i["A1"]), (i["P1"], i["A2"]), (i["P2"], i["A5"]),
        (i["A2"], i["A3"]), (i["A2"], i["A4"]), (i["P1"], i["A6"]), (i["P2"], i["A6"]),
        (i["A1"], i["K1"]), (i["A2"], i["K1"]), (i["A5"], i["K1"]),
        (i["A2"], i["K2"]), (i["A5"], i["K2"]),
        (i["A2"], i["K3"]), (i["A5"], i["K3"]),
        (i["K1"], i["E1"]), (i["A1"], i["E1"]), (i["A2"], i["E1"]), (i["A5"], i["E1"]),
        (i["K2"], i["E2"]), (i["A2"], i["E2"]), (i["A5"], i["E2"]),
        (i["K3"], i["E3"]), (i["A2"], i["E3"]), (i["A5"], i["E3"]),
        (i["A2"], i["V1"]), (i["A5"], i["V1"]), (i["K1"], i["V1"]), (i["E1"], i["V1"]),
        (i["A2"], i["V2"]), (i["A5"], i["V2"]), (i["K2"], i["V2"]), (i["E2"], i["V2"]),
        (i["A2"], i["V3"]), (i["A5"], i["V3"]), (i["K3"], i["V3"]), (i["E3"], i["V3"]),
        (i["E1"], i["I1"]), (i["A2"], i["I1"]), (i["A5"], i["I1"]),
        (i["E2"], i["I2"]), (i["A2"], i["I2"]), (i["A5"], i["I2"]),
        (i["E3"], i["I3"]), (i["A2"], i["I3"]), (i["A5"], i["I3"]),
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
        {"id": "g-ywsd-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 素材", "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "g-ywsd-1", "nodeIds": [i["A0"], i["A1"], i["A2"], i["A5"]],
         "bounds": bounds_for([i["A0"], i["A1"], i["A2"], i["A5"]]),
         "label": "01 母版 + 锚点（先跑）", "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "g-ywsd-2", "nodeIds": [i["A3"], i["A4"], i["A6"]],
         "bounds": bounds_for([i["A3"], i["A4"], i["A6"]]),
         "label": "02 资产派生", "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "g-ywsd-3", "nodeIds": [i["K1"], i["K2"], i["K3"]],
         "bounds": bounds_for([i["K1"], i["K2"], i["K3"]]),
         "label": "03 起势 K（首帧）", "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "g-ywsd-4", "nodeIds": [i["E1"], i["E2"], i["E3"]],
         "bounds": bounds_for([i["E1"], i["E2"], i["E3"]]),
         "label": "04 尾帧 E（结束姿势）★ 先跑这组", "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}},
        {"id": "g-ywsd-5", "nodeIds": [i["V1"], i["V2"], i["V3"]],
         "bounds": bounds_for([i["V1"], i["V2"], i["V3"]]),
         "label": "05 招式 5s · 首尾帧夹住", "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "g-ywsd-6", "nodeIds": [i["I1"], i["I2"], i["I3"]],
         "bounds": bounds_for([i["I1"], i["I2"], i["I3"]]),
         "label": "06 冲击帧 · 水墨红黑（改画自 E）", "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "g-ywsd-7", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "07 说明", "style": {"accent": None, "opacity": None, "borderColor": "#888888"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    return {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 首尾帧（seedance-2.5）v11",
            "description": ("K 起势 + E 结束姿势 → V 被两张图夹住（first_frame / last_frame_image，seedance-2.5 支持）→ "
                            "I 从 E 改画成水墨红黑冲击帧。删掉截帧占位，手工只剩挑图与剪辑补白闪。"),
            "nodes": nodes,
            "edges": [{
                "id": f"e-ywsd-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
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
        lf = (mp.get("last_frame_image") or {}).get("node_id")
        label = n["meta"]["label"]
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for tk in toks:
            if tk not in by_id:
                problems.append(f"引用节点不存在: {label} -> {tk}")
            if tk not in refs and tk not in (ff, lf):
                problems.append(f"引用未挂字段: {label} -> {tk}")
        for r in refs + [x for x in (ff, lf) if x]:
            if (r, n["id"]) not in edge_set and r != lf:
                problems.append(f"字段挂了没连线(非尾帧): {label} <- {r}")
            rn = by_id.get(r)
            if rn and rn["type"] == "input-image" and not rn.get("outputs"):
                problems.append(f"被引用的上传节点是空的: {label} <- {r}")
        if n["type"] == "gen-video":
            if ff and ff not in toks:
                problems.append(f"首帧未在正文点名: {label}")
            if lf and lf not in toks:
                problems.append(f"尾帧未在正文点名: {label}")
            if len(prompt) > 2000:
                problems.append(f"prompt 超 2000 字: {label} ({len(prompt)})")
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
        if n["type"] == "gen-video":
            mp = n["params"]["model_params"]
            print(f"  {n['meta']['label']}: {n['params']['model_id']} {mp['duration']}s "
                  f"first={bool(mp['first_frame_image'])} last={bool(mp['last_frame_image'])} "
                  f"prompt {len(mp['prompt'])} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()

