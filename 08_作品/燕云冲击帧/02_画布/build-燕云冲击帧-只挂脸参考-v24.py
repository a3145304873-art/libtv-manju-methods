# -*- coding: utf-8 -*-
"""燕云冲击帧 v24：K/E 只挂脸参考（去掉 A2/A5 的姿势牵引），I 保留夸张构图

诊断（2026-10-30 用户：「这个动作还是很奇怪」）：
  K/E 挂了 A2（正面全身、手臂下垂）与 A5（武器白底、剑水平），这两张在把姿势往
  「正面站姿 + 横剑在腹前」拉——于是六张图都像「捧着剑站着」，朝向几乎没变。
  irst 修法：K/E 只挂 A1（脸），姿势全靠文字；I 挂 E + A1。
  另外把 K/E 的提示词降级成「只管身体和手」——前景大剑/低机位/三层景深是插画构图，
  实拍帧做不到，写了只会两头为难。分工：实拍管人和动作，水墨管夸张透视。
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
OUT = HERE / "燕云冲击帧-只挂脸参考-16x9-v24.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单.json").read_text(encoding="utf-8"))
CREATED = "2026-10-30T18:40:00.000+08:00"
PREFIX = "ywsq"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V23 = load_mod("yanwu_v23", "build-燕云冲击帧-2.0mini-frames-v23.py")
KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "E1", "E2", "E3", "V1", "V2", "V3",
        "I1", "I2", "I3", "W1", "W2", "W3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}
RMAP = {V23.ID[k]: ID[k] for k in V23.ID}


def tok(k):
    return "{{" + ID[k] + "}}"


def rm(s):
    for old, new in RMAP.items():
        s = s.replace(old, new)
    return s


P_V1, P_V2, P_V3 = rm(V23.P_V1), rm(V23.P_V2), rm(V23.P_V3)
W_TPL, S0, S1 = V23.W_TPL, V23.S0, V23.S1

GRIP = ("【握法】右手正握剑柄：虎口朝剑格、食指扣在剑格下沿、其余三指环握、掌心贴柄；"
        "剑格在拳前约两指、剑身自拳背上方伸出；手腕与前臂成一条直线、不许折腕。"
        "左手并起食指中指成剑指。")
NOGLOW = "剑身**不发光、不要冰晶特效**，只留一道冷白高光，保证剑的朝向看得清。"

P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸（只锁五官与白发，**不参考它的姿势**）。
【机位】**平视**，半身（腰以上），镜头与人物胸口同高。
【姿势】**侧身 3/4、面朝画左**；右手持剑收在**右腰侧、剑身在身后**、剑尖朝后下方（画面里看不见剑尖）；
左臂自然垂在身侧；重心**压后腿**、膝微屈；肩背绷着、下颌收。
{GRIP}
【光影】侧逆光、冷调、实色；暗部近黑；{NOGLOW}
负向：正脸对镜头、剑在身前、剑横在腹前、剑挡胸、发光、冰晶光效、全身、平视正面、彩色、文字、水印、logo、游戏UI、卡通。
"""

P_K2 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸（只锁五官，不参考姿势）。
【机位】**平视**，半身。
【姿势】上身**向右拧到接近背对镜头**，头随身体转过去、**只露侧脸与后脑**；
右手举剑过右肩、**右肘高于肩**、剑身在身后斜向画外、剑尖看不见；左肩朝镜头、左臂横在胸前。
{GRIP}
【光影】侧逆光、冷调、实色；{NOGLOW}
负向：正对镜头、脸朝镜头、剑在身前、剑横在腹前、发光、冰晶光效、全身、彩色、文字、水印、logo、游戏UI、卡通。
"""

P_K3 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸（只锁五官，不参考姿势）。
【机位】**平视**，近景（胸以上＋持剑手）。
【姿势】**低头**，右手持剑自然下垂、**手臂贴在右腿外侧**、剑尖垂向地面（画面右下）；
左臂收在身后；重心**下沉**一档（膝弯、胯坐）；上半张脸陷在暗部。
{GRIP}
【光影】侧逆光、冷调、实色；{NOGLOW}
负向：抬头、剑在身前、剑横在腹前、手臂抬到胸前、发光、冰晶光效、全身、彩色、文字、水印、logo、游戏UI、卡通。
"""

P_E1 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K1')}＝起势（同一人同一机位）；{tok('A1')}＝脸（只锁五官）。
【机位】同起势：平视、半身。
【姿势】**身体转正、面朝镜头**；右臂**完全伸直、向前送到底**，剑身沿手臂方向指出去、
**剑尖朝镜头略偏左、近大远小**；剑柄在拳中、剑格在拳前；重心**压前腿**、后腿蹬直；左臂向后甩开。
{GRIP}
【光影】同起势；{NOGLOW}
负向：手臂弯曲、剑横在腹前、剑在身侧、剑没指出去、身体侧着、发光、冰晶光效、全身、彩色、文字、水印、logo、游戏UI、卡通。
"""

P_E2 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K2')}＝起势（同一人同一机位）；{tok('A1')}＝脸。
【机位】同起势：平视、半身。
【姿势】上身**已转到正对镜头、并向左多转约 20°**；右臂**横着伸开**、剑身横贯身前、
**剑尖朝画左**（可略出画）；重心从右腿移到两腿之间、胯打开；左臂向左后方甩。
{GRIP}
【光影】同起势；{NOGLOW}
负向：上身背对、脸朝画外、剑竖着、剑在身后、手臂贴身、发光、冰晶光效、全身、彩色、文字、水印、logo、游戏UI、卡通。
"""

P_E3 = f"""16:9 横版电影级**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K3')}＝起势（同一人同一机位）；{tok('A1')}＝脸。
【机位】同起势：平视、近景（胸以上＋持剑手）。
【姿势】**抬头**；右手持剑**从右下向上挑起**、右臂抬到肩高、**剑尖指向右上、可略出画**；
身体被带得**上拔**（膝伸直、胯提起、肩线打开）；左臂向下落。
{GRIP}
【光影】同起势；{NOGLOW}
负向：低头、剑在下方、剑横着、手臂没抬起来、发光、冰晶光效、全身、彩色、文字、水印、logo、游戏UI、卡通。
"""

INK_HEAD = "水墨武侠风，黑白单色高对比插画，古风男性剑客，只生成一张。"
INK_TAIL = ("【构图·三层景深】前景（左侧至中下）：巨大的剑身、夸张透视缩短，剑身留白作金属高光、刃口一条完整亮线；"
            "中景（右侧黄金分割）：角色上半身，面部与右手为焦点；背景：大面积泼墨、狂草笔触、墨滴飞溅，无具体实体。"
            "【光影】强黑白对比，留白即高光；光从右上方打向面部与剑身，边缘光锐利。【限制】低机位仰视；黑白无彩。")
INK_NEG = "负向：彩色、红色、写实照片、3D 渲染、背景实体、居中对称、剑横在腹前、发光、文字、水印、logo、游戏UI。"

P_I1 = f"""{INK_HEAD}
【引用图片说明】{tok('E1')}＝姿势与构图的唯一依据（不许改）；{tok('A1')}＝脸。
【动作】侧身突刺——剑身平举向前递出，**剑尖直指观者**，力量感与冲锋感极强。
{INK_TAIL}
{INK_NEG}
"""

P_I2 = f"""{INK_HEAD}
【引用图片说明】{tok('E2')}＝姿势与构图的唯一依据（不许改）；{tok('A1')}＝脸。
【动作】横斩收势——剑身横贯身前、剑尖朝画左。
{INK_TAIL}
{INK_NEG}
"""

P_I3 = f"""{INK_HEAD}
【引用图片说明】{tok('E3')}＝姿势与构图的唯一依据（不许改）；{tok('A1')}＝脸。
【动作】上挑到位——剑从下向上挑起、身体上拔。
{INK_TAIL}
{INK_NEG}
"""

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
    F = V23.V15.V14.V10
    gi, ii, it = F.gen_image, F.input_image, F.input_text
    nodes = [
        ii(ID["P1"], 20, 20, "【已生成·复用】P1 原始人物", up("P1")),
        ii(ID["P2"], 20, 240, "【已生成·复用】P2 原始武器", up("P2")),
        it(ID["S1"], 20, 470, 320, 470, "S1 角色与武器设定", S1),
        ii(ID["A0"], 420, 20, "【已生成·复用】A0 设定母版", up("A0")),
        ii(ID["A1"], 820, 20, "【已生成·复用】A1 脸部特写", up("A1")),
        ii(ID["A2"], 820, 340, "【已生成·复用】A2 正面全身（**只给 I/V 用，不挂 K/E**）", up("A2")),
        ii(ID["A5"], 820, 660, "【已生成·复用】A5 武器白底（**不挂 K/E**）", up("A5")),
        ii(ID["A3"], 1220, 20, "【已生成·复用】A3 侧面", up("A3")),
        ii(ID["A4"], 1220, 340, "【已生成·复用】A4 背面", up("A4")),
        ii(ID["A6"], 1220, 660, "【已生成·复用】A6 握剑手（**可单独参考握法**）", up("A6")),

        gi(ID["K1"], 1620, 20, "【待生成】K1 ① 起势 · 剑收右腰（侧身）", P_K1,
           [ID["A1"]], size="1K", quality="medium"),
        gi(ID["K2"], 1620, 340, "【待生成】K2 ② 起势 · 背对举剑", P_K2,
           [ID["A1"]], size="1K", quality="medium"),
        gi(ID["K3"], 1620, 660, "【待生成】K3 ③ 起势 · 低头垂剑", P_K3,
           [ID["A1"]], size="1K", quality="medium"),
        gi(ID["E1"], 2020, 20, "【待生成】E1 ① 到位 · 直臂前送", P_E1,
           [ID["K1"], ID["A1"]], size="1K", quality="medium"),
        gi(ID["E2"], 2020, 340, "【待生成】E2 ② 到位 · 横臂横贯", P_E2,
           [ID["K2"], ID["A1"]], size="1K", quality="medium"),
        gi(ID["E3"], 2020, 660, "【待生成】E3 ③ 到位 · 上挑过肩", P_E3,
           [ID["K3"], ID["A1"]], size="1K", quality="medium"),
    ]

    def vid(n, x, y, label, prompt, first, last):
        return {
            "id": n, "type": "gen-video", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
                "prompt": prompt, "_reference_way": "frames",
                "reference_images": [], "reference_videos": [], "reference_audios": [],
                "first_frame_image": {"node_id": first},
                "last_frame_image": {"node_id": last} if last else None,
                "aspect_ratio": "16:9", "resolution": "720p", "duration": 4,
                "generate_audio": True, "seed": -1}},
            "specialParams": None, "config": None,
            "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        }

    nodes += [
        vid(ID["V1"], 2420, 20, "【待生成】V1 ① 4s · 刺", P_V1, ID["K1"], ID["E1"]),
        vid(ID["V2"], 2420, 340, "【待生成】V2 ② 4s · 斩", P_V2, ID["K2"], ID["E2"]),
        vid(ID["V3"], 2420, 660, "【待生成】V3 ③ 4s · 撩", P_V3, ID["K3"], ID["E3"]),
        gi(ID["I1"], 2820, 20, "【待生成】I1 ① 冲击帧 · 黑白·剑指观者", P_I1, [ID["E1"], ID["A1"]]),
        gi(ID["I2"], 2820, 340, "【待生成】I2 ② 冲击帧 · 黑白·横贯", P_I2, [ID["E2"], ID["A1"]]),
        gi(ID["I3"], 2820, 660, "【待生成】I3 ③ 冲击帧 · 黑白·上挑", P_I3, [ID["E3"], ID["A1"]]),
        vid(ID["W1"], 3220, 20, "【可选·先不跑】W1 ① 墨动", W_TPL.format(img=tok("I1")), ID["I1"], None),
        vid(ID["W2"], 3220, 340, "【可选·先不跑】W2 ② 墨动", W_TPL.format(img=tok("I2")), ID["I2"], None),
        vid(ID["W3"], 3220, 660, "【可选·先不跑】W3 ③ 墨动", W_TPL.format(img=tok("I3")), ID["I3"], None),
        it(ID["S0"], 420, 1050, 1520, 470, "S0 说明 · 先读", S0),
    ]

    pairs = [
        (ID["A1"], ID["K1"]), (ID["A1"], ID["K2"]), (ID["A1"], ID["K3"]),
        (ID["K1"], ID["E1"]), (ID["A1"], ID["E1"]),
        (ID["K2"], ID["E2"]), (ID["A1"], ID["E2"]),
        (ID["K3"], ID["E3"]), (ID["A1"], ID["E3"]),
        (ID["K1"], ID["V1"]), (ID["K2"], ID["V2"]), (ID["K3"], ID["V3"]),
        (ID["E1"], ID["I1"]), (ID["A1"], ID["I1"]),
        (ID["E2"], ID["I2"]), (ID["A1"], ID["I2"]),
        (ID["E3"], ID["I3"]), (ID["A1"], ID["I3"]),
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
        ("01 资产（复用）· A2/A5 不挂 K/E", ["A0", "A1", "A2", "A5"], "#5B8DE0"),
        ("02 资产派生（复用）", ["A3", "A4", "A6"], "#5BE0C8"),
        ("03 起势 K（只挂脸）", ["K1", "K2", "K3"], "#E05B8D"),
        ("04 到位 E（只挂脸+起势）", ["E1", "E2", "E3"], "#E05B8D"),
        ("05 招式 V（frames 首尾帧）", ["V1", "V2", "V3"], "#E0A15B"),
        ("06 冲击帧 I（黑白）", ["I1", "I2", "I3"], "#5BE0C8"),
        ("07 墨动 W（可选）", ["W1", "W2", "W3"], "#C8A15B"),
        ("08 说明", ["S0"], "#888888"),
    ]
    gl = []
    for k, (label, keys, color) in enumerate(groups):
        ids = [ID[x] for x in keys]
        gl.append({"id": f"g-ywsq-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
                   "style": {"accent": None, "opacity": None, "borderColor": color},
                   "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY})

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 只挂脸参考（16:9）v24",
            "description": ("K/E 只挂 A1（脸），去掉 A2 站姿与 A5 横剑的姿势牵引；K/E 提示词只管身体与手；"
                            "I 保留黑白夸张构图。V 用 2.0-mini 的 frames 模式夹首尾帧。"),
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


if __name__ == "__main__":
    main()
