# -*- coding: utf-8 -*-
"""燕云冲击帧 v17：只锁「资产」，姿势帧与视频重出

用户意见（2026-10-30）：V1 适配不好、几张首尾帧不合适 → 这些不用，优先复用能用的。
所以：
  · **复用**：A0 设定母版 / A1 脸 / A2 正面全身 / A3 侧面 / A4 背面 / A5 武器 / A6 握剑手（7 张，已生成，直接挂 URL）
  · **重出**：K1–K3 起势、E1–E3 到位（1K，便宜）、I1–I3 冲击帧（1K）、V1–V3 招式（5s，贵但要重跑）
  · **可选**：W1–W3 墨动（标【可选·先不跑】——墨动可以用 墨凝.py + 静帧推近在后期做）
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-分镜-16x9-v18.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单.json").read_text(encoding="utf-8"))
CREATED = "2026-10-30T17:10:00.000+08:00"
PREFIX = "ywsk"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V15 = load_mod("yanwu_v15b", "build-燕云冲击帧-发力-v15.py")
KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "B1",
        "K1", "K2", "K3", "E1", "E2", "E3", "V1", "V2", "V3",
        "I1", "I2", "I3", "W1", "W2", "W3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}
RMAP = {V15.ID[k]: ID[k] for k in V15.ID}


def tok(k):
    return "{{" + ID[k] + "}}"


def rm(s):
    for old, new in RMAP.items():
        s = s.replace(old, new)
    return s


P_B1 = f"""16:9 横版，**一镜三格分镜条**（同一机位、同一人、同一光），只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝全身（锁服装/比例）；{tok('A5')}＝武器。
【版式】画面横向平分三格，两条极细黑线分隔，**格内不要任何文字编号**：左格「起势」、中格「发力」、右格「到位」。
【左格·起势】身体侧对镜头（约 3/4 背），剑收在右侧腰际、剑尖出画右缘；重心压后腿、上身前倾蓄着；脸只露半张侧面、眼盯画左。
【中格·发力】身体开始转正、腰胯先动；剑已抽到身前、剑身带一道极短残影；衣摆开始被带起来。
【右格·到位】身体完全转正、脸朝镜头；右臂全伸、剑身贯出画左缘；重心压到前腿；衣摆与白发甩向画右后方；脚下雪面被蹬开、雪尘还在半空。
【硬性要求】三格差别必须**一眼看得出**：朝向（侧→正）、剑的位置（右腰→贯出画左）、衣摆方向（垂→甩）。三格画得像同一张就是废图，重抽。
【风格】实色电影感、冷调、暗部近黑、刃口冷白反光；全图无红。
负向：三格雷同、格内文字、编号、分格线过粗、三格不同的人、三格不同服装、全身远景、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借左格「起势」的姿势与朝向，不借三格排版、不画分格线）；{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】近景（胸以上＋持剑手）。**起势**：身体**侧对镜头（约 3/4 背）**，剑收在右侧腰际、剑尖出画右缘；
重心压后腿、上身前倾蓄着；**脸只露半张侧面**，眼盯画左；肩背绷紧。
【构图】主体被裁：头顶贴上缘、右肩被右缘切掉；只留一块白在左上约五分之一。
【光影/材质】侧逆光、冷调、实色；暗部近黑；刃口冷白反光；无红。
负向：正脸对镜头、身体转正、剑在身前、全身入画、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_K2 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借左格的身体拧转方向）；{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】半身。**起势**：上身**向右拧到接近背对镜头**，剑举在右肩后上方、剑尖出画右缘；
左肩朝镜头、头随身体转过去只露侧脸；重心在右腿。
【构图】主体被裁：头顶贴上缘、下缘裁到腰；白在左上四分之一。
【光影/材质】侧逆光、冷调、实色；暗部近黑；无红。
负向：正对镜头、身体没转、剑在身前、全身入画、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_K3 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借左格的身体下沉与垂剑）；{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】近景。**起势**：**低头**、剑尖垂在画面右下并出画右下角；手腕内扣、右肩下沉；
重心**明显下沉**一档（膝弯、胯坐）；上半张脸陷在暗部，只露眼睛。
【构图】主体被裁：头顶贴上缘、下缘裁到胸；白在左上五分之一。
【光影/材质】侧逆光、冷调、实色；暗部近黑；无红。
负向：抬头、剑在身前、全身入画、身体直立、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_E1 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借右格「到位」的姿势与朝向，不借排版）；{tok('K1')}＝起势（同一人同一镜）；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】同一近景。**到位**：身体**完全转正、脸朝镜头**；右臂全伸、剑身贯出画左缘（看不到端点）、近大远小；
**重心已压到前腿**、后腿蹬直；衣摆与白发被甩向画右后方；脚下雪面被蹬开、雪尘还在半空。
【构图】头顶贴上缘、下缘裁到胸；白仍在左上五分之一。
【光影/材质】同上，实色、无红。
负向：侧身、背对、脸朝画外、剑在腰侧、重心没动、全身入画、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_E2 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借右格「到位」的朝向与展开）；{tok('K2')}＝起势；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】同一半身。**到位**：上身**已转到正对镜头、并向左多转约 20°**，剑横贯到身体左前、**剑尖出画左缘**；
重心从右腿移到两腿之间、胯打开；衣摆与白发向左甩开；脚下雪面被扫开一条弧。
【构图】头顶贴上缘、下缘裁到腰；白仍在左上四分之一。
【光影/材质】同上，实色、无红。
负向：上身仍背对、剑在右侧、身体没转、全身入画、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""

P_E3 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('B1')}＝分镜条（只借右格「到位」的上拔与上举）；{tok('K3')}＝起势；{tok('A2')}＝全身；{tok('A5')}＝武器。
【画面】同一近景。**到位**：**抬头**、剑尖从右下挑到画面中上并**出画右上角**、刃口朝上；
身体被带得**上拔**（膝伸直、胯提起、肩线打开）；衣摆与白发向上翻卷；脚下雪面被蹬开、雪尘上扬。
【构图】头顶贴上沿（切掉一点发顶）、下缘裁到胸；白仍在左上五分之一。
【光影/材质】同上，实色、无红。
负向：低头、剑在下方、身体下沉、全身入画、三格排版、分格线、文字、红、彩色光效、水印、logo、游戏UI、卡通。
"""



P_V1, P_V2, P_V3 = rm(V15.P_V1), rm(V15.P_V2), rm(V15.P_V3)
P_I1, P_I2, P_I3 = rm(V15.P_I1), rm(V15.P_I2), rm(V15.P_I3)
W_TPL, S1, S0 = V15.W_TPL, V15.S1, V15.S0

# 只复用资产与原始素材（姿势帧/视频 按用户意见重出）
REUSE = {"P1": "P1 原始", "P2": "P2 原始", "A0": "A0", "A1": "A1", "A2": "A2",
         "A3": "A3", "A4": "A4", "A5": "A5", "A6": "A6"}
FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    for key, pref in REUSE.items():
        if core.startswith(pref):
            FOUND[key] = v
            break


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


def main():
    F = V15.V14.V10
    gi, ii, it = F.gen_image, F.input_image, F.input_text
    nodes = [
        ii(ID["P1"], 20, 20, "【已生成·复用】P1 原始人物", up("P1")),
        ii(ID["P2"], 20, 240, "【已生成·复用】P2 原始武器", up("P2")),
        it(ID["S1"], 20, 470, 320, 470, "S1 角色与武器设定", S1),

        ii(ID["A0"], 420, 20, "【已生成·复用】A0 设定母版", up("A0")),
        ii(ID["A1"], 820, 20, "【已生成·复用】A1 脸部特写", up("A1")),
        ii(ID["A2"], 820, 340, "【已生成·复用】A2 正面全身（锚）", up("A2")),
        ii(ID["A5"], 820, 660, "【已生成·复用】A5 武器白底", up("A5")),
        ii(ID["A3"], 1220, 20, "【已生成·复用】A3 侧面", up("A3")),
        ii(ID["A4"], 1220, 340, "【已生成·复用】A4 背面", up("A4")),
        ii(ID["A6"], 1220, 660, "【已生成·复用】A6 握剑手", up("A6")),

        gi(ID["B1"], 1620, -380, "【待生成·先跑】B1 一镜三格分镜条（起势/发力/到位）", P_B1,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["K1"], 1620, 20, "【待生成·重出】K1 ① 起势 · 剑收右腰", P_K1,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["K2"], 1620, 340, "【待生成·重出】K2 ② 起势 · 剑举右肩后", P_K2,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["K3"], 1620, 660, "【待生成·重出】K3 ③ 起势 · 剑尖垂右下", P_K3,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),

        gi(ID["E1"], 2020, 20, "【待生成·重出】E1 ① 到位 · 刺出", P_E1,
           [ID["K1"], ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["E2"], 2020, 340, "【待生成·重出】E2 ② 到位 · 腰甩横贯", P_E2,
           [ID["K2"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["E3"], 2020, 660, "【待生成·重出】E3 ③ 到位 · 上挑", P_E3,
           [ID["K3"], ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
    ]

    def vid(n, x, y, label, prompt, refs, first, last):
        return {
            "id": n, "type": "gen-video", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "seedance-2.5", "model_params": {
                "_task_mode": "standard", "prompt": prompt, "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in refs],
                "reference_videos": [], "reference_audios": [],
                "first_frame_image": {"node_id": first},
                "last_frame_image": {"node_id": last} if last else None,
                "aspect_ratio": "16:9", "resolution": "720p", "duration": 5,
                "generate_audio": True, "seed": -1}},
            "specialParams": None, "config": None,
            "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        }

    nodes += [
        vid(ID["V1"], 2420, 20, "【待生成·重出】V1 ① 5s · 刺", P_V1,
            [ID["A2"], ID["A5"], ID["E1"]], ID["K1"], ID["E1"]),
        vid(ID["V2"], 2420, 340, "【待生成·重出】V2 ② 5s · 斩", P_V2,
            [ID["A2"], ID["A5"], ID["E2"]], ID["K2"], ID["E2"]),
        vid(ID["V3"], 2420, 660, "【待生成·重出】V3 ③ 5s · 撩", P_V3,
            [ID["A2"], ID["A5"], ID["E3"]], ID["K3"], ID["E3"]),
        gi(ID["I1"], 2820, 20, "【待生成·重出】I1 ① 冲击帧 · 向心放射", P_I1,
           [ID["E1"], ID["A2"], ID["A5"]]),
        gi(ID["I2"], 2820, 340, "【待生成·重出】I2 ② 冲击帧 · 横向墨痕", P_I2,
           [ID["E2"], ID["A2"], ID["A5"]]),
        gi(ID["I3"], 2820, 660, "【待生成·重出】I3 ③ 冲击帧 · 斜向墨痕", P_I3,
           [ID["E3"], ID["A2"], ID["A5"]]),
        vid(ID["W1"], 3220, 20, "【可选·先不跑】W1 ① 墨动", W_TPL.format(img=tok("I1")), [ID["I1"]], ID["I1"], None),
        vid(ID["W2"], 3220, 340, "【可选·先不跑】W2 ② 墨动", W_TPL.format(img=tok("I2")), [ID["I2"]], ID["I2"], None),
        vid(ID["W3"], 3220, 660, "【可选·先不跑】W3 ③ 墨动", W_TPL.format(img=tok("I3")), [ID["I3"]], ID["I3"], None),
        it(ID["S0"], 420, 1050, 1520, 470, "S0 复用资产版 · 先读", S0),
    ]

    for _n in nodes:
        if _n["type"] == "gen-image" and _n["meta"]["label"].startswith(("【待生成·重出】K", "【待生成·重出】E")):
            _n["params"]["model_params"]["reference_images"].insert(0, {"node_id": ID["B1"]})

    pairs = [
        (ID["A1"], ID["B1"]), (ID["A2"], ID["B1"]), (ID["A5"], ID["B1"]),
        (ID["B1"], ID["K1"]), (ID["B1"], ID["K2"]), (ID["B1"], ID["K3"]),
        (ID["B1"], ID["E1"]), (ID["B1"], ID["E2"]), (ID["B1"], ID["E3"]),
        (ID["A1"], ID["K1"]), (ID["A2"], ID["K1"]), (ID["A5"], ID["K1"]),
        (ID["A1"], ID["K2"]), (ID["A2"], ID["K2"]), (ID["A5"], ID["K2"]),
        (ID["A1"], ID["K3"]), (ID["A2"], ID["K3"]), (ID["A5"], ID["K3"]),
        (ID["K1"], ID["E1"]), (ID["A1"], ID["E1"]), (ID["A2"], ID["E1"]), (ID["A5"], ID["E1"]),
        (ID["K2"], ID["E2"]), (ID["A2"], ID["E2"]), (ID["A5"], ID["E2"]),
        (ID["K3"], ID["E3"]), (ID["A1"], ID["E3"]), (ID["A2"], ID["E3"]), (ID["A5"], ID["E3"]),
        (ID["A2"], ID["V1"]), (ID["A5"], ID["V1"]), (ID["K1"], ID["V1"]), (ID["E1"], ID["V1"]),
        (ID["A2"], ID["V2"]), (ID["A5"], ID["V2"]), (ID["K2"], ID["V2"]), (ID["E2"], ID["V2"]),
        (ID["A2"], ID["V3"]), (ID["A5"], ID["V3"]), (ID["K3"], ID["V3"]), (ID["E3"], ID["V3"]),
        (ID["E1"], ID["I1"]), (ID["A2"], ID["I1"]), (ID["A5"], ID["I1"]),
        (ID["E2"], ID["I2"]), (ID["A2"], ID["I2"]), (ID["A5"], ID["I2"]),
        (ID["E3"], ID["I3"]), (ID["A2"], ID["I3"]), (ID["A5"], ID["I3"]),
        (ID["I1"], ID["W1"]), (ID["I2"], ID["W2"]), (ID["I3"], ID["W3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        ("00 素材（复用）", ["P1", "P2", "S1"], "#8E8DE0"),
        ("01 资产（已生成·复用）", ["A0", "A1", "A2", "A5"], "#5B8DE0"),
        ("02 资产派生（已生成·复用）", ["A3", "A4", "A6"], "#5BE0C8"),
        ("03 分镜条（先跑这张）", ["B1"], "#E0C05B"),
        ("04 起势 K（按分镜左格）", ["K1", "K2", "K3"], "#E05B8D"),
        ("05 到位 E（按分镜右格）", ["E1", "E2", "E3"], "#E05B8D"),
        ("06 招式 V（重出）", ["V1", "V2", "V3"], "#E0A15B"),
        ("07 冲击帧 I（重出）", ["I1", "I2", "I3"], "#5BE0C8"),
        ("08 墨动 W（可选）", ["W1", "W2", "W3"], "#C8A15B"),
        ("09 说明", ["S0"], "#888888"),
    ]
    gl = []
    for k, (label, keys, color) in enumerate(groups):
        ids = [ID[x] for x in keys]
        gl.append({"id": f"g-ywsj-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
                   "style": {"accent": None, "opacity": None, "borderColor": color},
                   "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY})

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 分镜驱动（16:9）v18",
            "description": ("先出一张一镜三格分镜条（起势/发力/到位）把差异定下来，K/E 分别取左格与右格重出；"
                            "W 墨动标为可选（可后期用 墨凝.py 做）。"),
            "nodes": nodes,
            "edges": [{"id": "edge-" + hashlib.md5((str(k) + s + t).encode()).hexdigest()[:8],
                       "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
                       "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY}
                      for k, (s, t) in enumerate(pairs)],
            "groups": gl,
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(gl)}")
    print("复用:", sorted(FOUND))
    print("要跑:", [n["meta"]["label"] for n in nodes if n["type"].startswith("gen")])


if __name__ == "__main__":
    main()
