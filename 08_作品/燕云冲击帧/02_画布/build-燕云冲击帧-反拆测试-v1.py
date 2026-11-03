# -*- coding: utf-8 -*-
"""反拆测试：用「拔剑·水墨定格」反推出来的六段式提示词，换成本角色，出单张测试图。

只改三段（角色 / 服装 / 武器与握法），其余（风格句 / 构图 / 光影 / 负向）照搬反拆稿。
挂 A1 脸 / A2 全身 / A5 武器 三张已生成资产做一致性参考。
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
OUT = HERE / "燕云冲击帧-反拆测试-单图-v3.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-03T12:00:00.000+08:00"
PREFIX = "ywu1"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V15 = load_mod("yanwu_v15x", "build-燕云冲击帧-发力-v15.py")
F = V15.V14.V10

KEYS = ("A1", "A2", "A5", "T1")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}


def tok(k):
    return "{{" + ID[k] + "}}"


P_T1 = f"""黑白水墨武侠风，炭笔线条＋浓墨块面，古风白发剑客半身像。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝服装；{tok('A5')}＝武器外形。人物必须是这三张里的人，不许换成别人。

【第一原则·这是一张以黑为主的画】
整幅画面**六成以上是浓黑**：背景、头发、衣服暗部、腰带全部压成**大片死黑**，墨要成块、不要成雾；
**画面里唯一亮的东西是剑身**（一条白），第二亮的是**脸那一小块纸白**；
除此之外**几乎不留中间灰**——暗部直接黑，亮部直接白，过渡只允许发生在一条窄边上。
如果你画出来是"整体浅灰、白多黑少"，那是错的，必须重画成"黑压白"。

【第二原则·剑是透视冲进来的，不是横在身前】
剑从**画面左下角外**朝镜头**斜着伸进来**：**近大远小**——靠近画面这一端的剑身**宽到约画面高度的四分之一**，
往画面外收缩变窄；**只看到剑身的中后段，剑尖在画面外**。
**绝对不要画成"横在胸前的短剑"**，也**不要画成"又长又细的白棍子"**——要粗、要近、要有厚度。

【第三原则·人物被剑压住】
人物压在画面**右侧三分之一**、下缘裁到腰；**剑横过人物身前**，把人切掉一部分；
白发向画面左方横甩，用**浓墨块＋飞白碎笔**（不是细线）。

角色：面容清瘦冷峻，五官只用极少线条：眉、眼线、鼻梁、唇线各一笔；脸是一小块纸白；
脸略低、一只眼落在暗部；眼睛细长半垂。

服装：白色宽袖长袍，衣纹用排线＋飞白；**黑色交领与黑色宽腰封压到死黑**，腰封上一枚金属扣件；
黑色护腕；袖口墨色渐染。

武器与握法：右手握剑柄，手在画面中部偏右、**手指绕握、手背对镜头**；
手占画面宽约 8%–10%，轮廓完整，**以明亮剑身为背景形成剪影**；手腕与前臂成直线；剑穗垂下。

构图：16:9；**剑是画面里唯一的大亮块**，从左下贯到人物身前；
留白只集中在**左上角一小块**；背景为**大块泼墨＋墨点喷溅**，不许碎成灰雾。

负向：整体发灰、白多黑少、明亮均匀、淡彩水墨、剑横在身前、剑又细又短、剑尖在画面内、
剑柄在画面外看不到手、彩色、发光、能量光效、冰晶反光、精细写实、五官细节堆砌、细线素描头发、
手搭在剑上、剑从掌心穿出、折腕、多余手指、多只手、居中对称、字幕、水印、logo、游戏UI、卡通。
"""

REUSE = {"A1": "A1", "A2": "A2", "A5": "A5"}
FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    if core.startswith("A1"):
        FOUND["A1"] = v
    elif core.startswith("A2"):
        FOUND["A2"] = v
    elif core.startswith("A5"):
        FOUND["A5"] = v


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


def main():
    gi, ii = F.gen_image, F.input_image
    nodes = [
        ii(ID["A1"], 20, 20, "【已生成·复用】A1 脸部", up("A1")),
        ii(ID["A2"], 20, 340, "【已生成·复用】A2 全身", up("A2")),
        ii(ID["A5"], 20, 660, "【已生成·复用】A5 武器", up("A5")),
        gi(ID["T1"], 420, 20, "【待生成】反拆测试图（六段式·换本角色）", P_T1,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
    ]
    pairs = [(ID["A1"], ID["T1"]), (ID["A2"], ID["T1"]), (ID["A5"], ID["T1"])]
    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        ids = [x for x in ids if x in by_id]
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        {"id": "g-ywtz-0", "nodeIds": [ID["A1"], ID["A2"], ID["A5"]],
         "bounds": bf([ID["A1"], ID["A2"], ID["A5"]]), "label": "00 已生成资产（复用）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "g-ywtz-1", "nodeIds": [ID["T1"]],
         "bounds": bf([ID["T1"]]), "label": "01 反拆测试图（只跑这一张）",
         "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 反拆测试（单图）v3",
            "description": ("用「拔剑·水墨定格」反推出的六段式提示词，只换角色/服装/武器三段，"
                            "其余照搬；挂 A1/A2/A5 做一致性参考。只跑一张 T1。"),
            "nodes": nodes,
            "edges": [{"id": "edge-" + hashlib.md5((str(k) + s + t).encode()).hexdigest()[:8],
                       "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
                       "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY}
                      for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(groups)}")
    print("prompt 字数:", len(P_T1))


if __name__ == "__main__":
    main()
