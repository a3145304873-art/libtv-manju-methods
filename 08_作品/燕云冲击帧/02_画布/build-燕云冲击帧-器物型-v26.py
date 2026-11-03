# -*- coding: utf-8 -*-
"""燕云冲击帧 v26：B 器物型（剑光先到 → 星芒 → 人后到）

设计来源：L_03《剑之极》逐帧拆解（00_方案/20、21）
  0–1.5s 黑场（一道冷光提前）→ 1.5–2.3s 左右竖剑做框（无人）→ 2.43s 极小星芒
  → 2.47s 硬切眼睛特写 → 3.9–5.2s 真静止 → 淡出黑

本画布只做"能生成的部分"：3 张黑底兵器帧（K）+ 3 张眼睛特写（E）。
星芒、硬切、淡出、黑场全部在剪辑里做——**这个模板不需要视频生成**。
角色与武器沿用已生成的 A0–A6，不再重复出。
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
OUT = HERE / "燕云冲击帧-器物型-16x9-v26.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单.json").read_text(encoding="utf-8"))
CREATED = "2026-10-30T19:30:00.000+08:00"
PREFIX = "ywss"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V25 = load_mod("yanwu_v25", "build-燕云冲击帧-三宗师-v25.py")
V15M = V25.V23.V15
KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "E1", "E2", "E3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}
RMAP = {V25.ID[k]: ID[k] for k in V25.ID if k in ID}


def tok(k):
    return "{{" + ID[k] + "}}"


def rm(s):
    for old, new in RMAP.items():
        s = s.replace(old, new)
    return s


S0 = """【器物型 · 剪辑配方】

这一版按《剑之极》的设计逻辑：**剑光先到，人后到**。
画布只出 6 张图（3 张黑底兵器 + 3 张眼睛特写），其余全在剪辑里做——
这个模板**不需要视频生成**，因为参考片最关键的三个动作是「黑、切、定」。

剪辑时间线（每条 4.3 秒）：
  0.00–2.00  黑底兵器帧（K），极缓推近 1.00→1.02
  2.00       星芒 1 帧：纯白 + 径向遮罩，直径约画面 1/8（不要铺满）
  2.03–4.03  硬切眼睛特写（E），完全静止
  4.03–4.30  淡出到黑

三条的差异只在"兵器怎么进画"：
  ① 竖剑：剑身竖在画面中偏左，只露刃口反光
  ② 横剑：剑身横压画面上缘三分之一，刃口朝下
  ③ 斜剑：剑尖自右下刺入、斜向左上，只露剑尖

为什么这么省：
  · 参考的黑场 1.5 秒、星芒 1 帧、硬切，都是剪辑能做的；
  · 生成模型只需要画两张"能画准"的图：黑底兵器（好出）、眼睛特写（挂脸参考）；
  · 首尾帧在这里**不能用**——从"黑底剑"过渡到"眼睛"会崩，必须硬切。

跑序：00 素材 → 01/02 复用资产 → 03 黑底兵器 K → 04 眼睛特写 E → 剪辑
"""

K_NEG = "负向：出现人物、手、全身、场景、背景实体、彩色、发光特效、粒子、文字、水印、logo、游戏UI、卡通。"
K_BASE = "16:9 横版，**纯黑背景**的兵器特写，只生成一张。\n【引用图片说明】{a5}＝武器外形（只借外形，不借背景）。\n"
K_TAIL = "\n【光影】唯一的亮部是刃口一道冷白反光与护手的一点微光；其余全部压在纯黑里，**暗部不要灰雾**。\n" + K_NEG

P_K1 = K_BASE.format(a5=tok("A5")) + \
    "【画面】**一把竖立的剑身，位于画面中线偏左**；剑尖朝上、被画面上缘切掉；剑格与护手在画面下三分之一处；" \
    "剑身的冰晶纹理只在反光里隐约可见。\n【构图】垂直三分：左边黑 / 中间剑 / 右边黑；剑身占画面宽约八分之一。" + K_TAIL

P_K2 = K_BASE.format(a5=tok("A5")) + \
    "【画面】**剑身横压画面上缘三分之一**，刃口朝下、几乎水平；剑尖在画面右缘被切掉；护手在左上角暗部。" \
    "\n【构图】横向切分：上三分之一是剑、下面三分之二是纯黑。" + K_TAIL

P_K3 = K_BASE.format(a5=tok("A5")) + \
    "【画面】**剑尖自画面右下角斜向左上刺入**，只露剑尖与前段剑身；剑身向画面外延伸，看不到剑格。" \
    "\n【构图】一条从左下到右上的斜线，其余全黑；剑尖是画面里最亮的一点。" + K_TAIL

E_NEG = "负向：正脸、双眼、完整面部、彩色、发光眼、红眼、场景、背景实体、文字、水印、logo、游戏UI、卡通。"
E_HEAD = "16:9 横版，**黑白水墨风格的极近特写**，只生成一张。\n【引用图片说明】{a1}＝脸（只借五官与白发，不借构图）。\n"
E_TAIL = "\n【光影】强黑白对比：皮肤亮部留白、暗部压到纯黑；只有一只眼是焦点。\n" + E_NEG

P_E1 = E_HEAD.format(a1=tok("A1")) + \
    "【画面】一只眼睛的极近特写，**眼睛占画面右侧三分之二**；瞳孔清晰、眼白留白、睫毛用枯笔；" \
    "**画面左缘是一条竖立的剑身**（只露刃口一道冷白反光）；其余部分是头发与纯黑。\n【构图】垂直切分：左缘剑身 / 中间眼 / 右侧纯黑。" + E_TAIL

P_E2 = E_HEAD.format(a1=tok("A1")) + \
    "【画面】一只眼睛的极近特写，眼睛在画面中间偏下；**画面上缘横着一段剑身**（刃口朝下、只露反光）；" \
    "头发散在暗部。\n【构图】横向切分：上缘剑身 / 中间眼 / 下方纯黑。" + E_TAIL

P_E3 = E_HEAD.format(a1=tok("A1")) + \
    "【画面】瞳孔的极近特写，占画面中心；**剑尖停在眼前**——画面右下角一点冷白刃光指向瞳孔；" \
    "其余全是纯黑。\n【构图】以瞳孔为中心，右下角一点刃光。" + E_TAIL

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
    F = V15M.V14.V10
    gi, ii, it = F.gen_image, F.input_image, F.input_text
    nodes = [
        ii(ID["P1"], 20, 20, "【已生成·复用】P1 原始人物", up("P1")),
        ii(ID["P2"], 20, 240, "【已生成·复用】P2 原始武器", up("P2")),
        it(ID["S1"], 20, 470, 320, 470, "S1 角色与武器设定", V15M.S1),
        ii(ID["A0"], 420, 20, "【已生成·复用】A0 设定母版", up("A0")),
        ii(ID["A1"], 820, 20, "【已生成·复用】A1 脸部特写", up("A1")),
        ii(ID["A2"], 820, 340, "【已生成·复用】A2 正面全身", up("A2")),
        ii(ID["A5"], 820, 660, "【已生成·复用】A5 武器白底", up("A5")),
        ii(ID["A3"], 1220, 20, "【已生成·复用】A3 侧面", up("A3")),
        ii(ID["A4"], 1220, 340, "【已生成·复用】A4 背面", up("A4")),
        ii(ID["A6"], 1220, 660, "【已生成·复用】A6 握剑手", up("A6")),
        gi(ID["K1"], 1620, 20, "【待生成】K1 ① 竖剑（黑底·无人）", P_K1, [ID["A5"]], size="1K", quality="medium"),
        gi(ID["K2"], 1620, 340, "【待生成】K2 ② 横剑压上缘（黑底·无人）", P_K2, [ID["A5"]], size="1K", quality="medium"),
        gi(ID["K3"], 1620, 660, "【待生成】K3 ③ 斜剑入画（黑底·无人）", P_K3, [ID["A5"]], size="1K", quality="medium"),
        gi(ID["E1"], 2020, 20, "【待生成】E1 ① 眼睛特写·剑在左缘", P_E1, [ID["A1"]], size="1K", quality="medium"),
        gi(ID["E2"], 2020, 340, "【待生成】E2 ② 眼睛特写·剑横上缘", P_E2, [ID["A1"]], size="1K", quality="medium"),
        gi(ID["E3"], 2020, 660, "【待生成】E3 ③ 瞳孔特写·剑尖在眼前", P_E3, [ID["A1"]], size="1K", quality="medium"),
        it(ID["S0"], 2420, 20, 620, 900, "S0 剪辑配方 · 先读", S0),
    ]
    pairs = [
        (ID["A5"], ID["K1"]), (ID["A5"], ID["K2"]), (ID["A5"], ID["K3"]),
        (ID["A1"], ID["E1"]), (ID["A1"], ID["E2"]), (ID["A1"], ID["E3"]),
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
        ("01 资产（复用·不重出）", ["A0", "A1", "A2", "A5"], "#5B8DE0"),
        ("02 资产派生（复用）", ["A3", "A4", "A6"], "#5BE0C8"),
        ("03 黑底兵器 K（无人）", ["K1", "K2", "K3"], "#E0C05B"),
        ("04 眼睛特写 E（人后到）", ["E1", "E2", "E3"], "#E05B8D"),
        ("05 剪辑配方", ["S0"], "#888888"),
    ]
    gl = []
    for k, (label, keys, color) in enumerate(groups):
        ids = [ID[x] for x in keys]
        gl.append({"id": f"g-ywss-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
                   "style": {"accent": None, "opacity": None, "borderColor": color},
                   "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY})

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 器物型 B（剑光先到）v26",
            "description": ("按《剑之极》的游戏设计逻辑：黑底兵器（无人）→ 星芒 1 帧 → 硬切眼睛特写。"
                            "只出 6 张图，不需要视频生成；星芒/硬切/淡出在剪辑里做。资产全部复用。"),
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


