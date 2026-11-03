# -*- coding: utf-8 -*-
"""燕云冲击帧 · 资产板 v8（先跑这条，再跑三条片）

原因（2026-10-30 用户指出）：现在用的是 526×533 / 632×711 的游戏截图裁切，带 UI 与水印，
人物只到膝下、没有侧面与背面、武器是斜角透视。拿它当参考生成 16:9 全身镜头，模型只能猜——
下半身、背面、剑的正交形状全靠编，三条片的人物一定漂。所以先把资产做干净。

结构（4 组，按跑序）：
  00 素材     P1 原始人物截图 / P2 原始武器截图 / S1 设定
  01 锚点     A1 脸部特写（1:1 只做脸）/ A2 正面全身（三视图的锚）/ A5 武器白底正交
  02 派生     A3 侧面 90° / A4 背面（都只参考 A2，保证同一人）/ A6 握剑的手
  03 说明     S0

用法：python build-燕云冲击帧-资产板-v8.py
"""
import glob
import hashlib
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-资产板-v9.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T11:30:00.000+08:00"
PREFIX = "ywsb"
BY = "linguanxi"

P1_UP = {
    "name": "P1-人物-白发剑客.png",
    "url": ("https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/"
            "canvas-e4318cc875/image/20261027-122555-bb6fa0be7e68df3f-p1-e4-ba-ba-e7-89-a9-"
            "e7-99-bd-e5-8f-91-e.png"),
    "width": 526, "height": 533, "size": 572149,
    "md5": "7e5dbc051eff3e58b92f5a973c017d1a",
}
P2_UP = {
    "name": "P2-武器-龙跃霄汉.png",
    "url": ("https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/"
            "canvas-e4318cc875/image/20261027-122556-5df2712152eae9b4-p2-e6-ad-a6-e5-99-a8-"
            "e9-be-99-e8-b7-83-e.png"),
    "width": 632, "height": 711, "size": 528519,
    "md5": "df2829d66050b0a95f9c6819ac355f86",
}


def nid(key):
    return "node-" + hashlib.md5((PREFIX + key).encode("utf-8")).hexdigest()[:8]


KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "S0")
ID = {k: nid(k) for k in KEYS}


def tok(key):
    return "{{" + ID[key] + "}}"


BASE = ("中性浅灰底（#B8B8B8 左右，纯色、无渐变、无纹理、无文字、无水印、无 UI 边框）；"
        "电影级写实，柔和顶侧光，人物/器物自己投一点软阴影；画面里只有一个主体。")

S1_TEXT = """【角色与武器设定 · 只读】
人物：年轻男性剑客，白发（长过胸、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，
手腕黑色护腕，双脚深色靴；双臂缠绕淡薄的冰霜气劲（薄，不要抢主体）；面部清瘦、眉压低、眼神冷静；
本组不戴斗笠。

武器：藏音·龙跃霄汉——冰晶长剑；剑身半透、内部有龙形霜纹；护手一道极细虹彩（青→品红）；
护手根部结着玉绿色冰晶簇；剑柄缠绳；剑尖明光偏暖（曜日）。

【这张画布只做资产】把两个原始截图里的信息"洗"成干净资产：脸 / 正面全身 / 侧面 / 背面 / 武器 / 手。
资产的用途是给下游生成当参考图，不是最终画面——所以要求：正视、全身、纯色底、无遮挡、无 UI、无水印。
"""

S0_TEXT = """【资产板 · 先跑这条，再跑三条片】

为什么先跑这条：
现在用的是 526×533 / 632×711 的游戏截图裁切——人物只到膝下、没有侧面与背面、武器是斜角透视，
还带 UI 与水印。拿它当参考生成 16:9 全身镜头，模型只能猜：下半身怎么画、背面什么发型、剑的正交形状是啥。
猜出来的东西三条片各猜一遍，人物就漂了。所以先把资产做干净，后面三条片才有统一依据。

跑序：
00 素材（P1/P2 已预填）
→ 01 母版 + 锚点：A0 设定母版（一张看完所有设定）、A1 脸、A2 正面全身、A5 武器（**先跑这一组，它们是锚**）
   · A0 是"人看"的母版：审图、存档、给别人看都看这一张，**不接下游**
   · A1/A2/A5 是"机器用"的资产：下游直接引用
→ 02 派生：A3 侧面、A4 背面、A6 握剑手（只参考 A2 / A5，保证同一个人、同一件器）
→ 手工挑图：每个节点最多留 1 张，用起来的那张才往下游接。

资产纪律（I05）：
· 纯色底（#B8B8B8），无渐变无纹理无文字无水印——有底色才能贴到任何场景里
· 正面全身必须"手臂自然下垂、不含武器"，武器单独一张（合在一起会让模型把剑焊在手上）
· 侧面/背面必须只参考 A2，否则会画出"另一个人"
· 三视图不要拼成一张长图喂下游——一张图三个人物会污染构图；这里是分开的六个节点

跑完之后：
把 A2 / A5 换成三条片的参考（我出 v9 接线，你不用手拖），K/V/I 全部改用清晰资产 + 原始截图双参考。

如果手上还有更干净的素材：关掉 UI 的游戏内正面全身截图、或官方立绘/海报，换掉 P1 会让 A2 好很多。
"""

# ---------------------------------------------------------------- 资产 prompt
P_A0 = f"""16:9 横版，**角色设定母版（一张看完所有设定）**，只生成一张。
【引用图片说明】{tok('P1')}＝人物来源（锁脸/发型/服装/比例）；{tok('P2')}＝武器来源（锁剑身/护手/剑柄）。
【版式】三分栏，从左到右：
  左栏：脸部正面特写（胸以上，占左栏高 80%）；
  中栏：正面全身直立，手臂自然下垂、**手中不含武器**；
  右栏：同一角色的 90° 侧面与背面并排（等高，各占右栏一半）；
  上方留一条空白，**不要写任何文字或标注**。
【一致性】四个视图必须是同一个人：同一张脸、同一发型长度、同一套服装、同一比例；不得换装、换脸、改比例。
【风格/底】中性浅灰底（#B8B8B8 纯色，无渐变无纹理）；电影级写实；柔和顶侧光。
负向：不同的脸、换装、换发型、动态姿势、持剑出招、武器、背景环境、UI、水印、文字、标注线、格子边框、卡通、夸张比例。
"""

P_A1 = f"""16:9 横版，**角色脸部特写（胸以上，正面）**，只生成一张。
【引用图片说明】{tok('P1')}＝人物来源（锁脸型/眉/眼/鼻/唇/发际线/白发长度）。
【画面】正面胸以上特写，脸占画面高度的 70%，视线看向镜头；白发从额前垂到胸前、发尾散乱；
白袍立领＋黑色内衬的领口可见；表情冷静、无笑、眉压低。
【风格/底】{BASE}
负向：全身、半身以下、手、武器、斗笠、背景环境、UI、水印、文字、多人、侧脸、夸张表情、卡通、3D 渲染感。
"""

P_A2 = f"""16:9 横版，**角色正面全身三视图之「正面」**，只生成一张。
【引用图片说明】{tok('P1')}＝人物来源（锁脸/发型/服装/比例）。若截图只到膝下，请按上身比例自然补全下半身与靴。
【画面】正面直立，双脚并拢略分、手臂自然下垂、**手中不含武器**；人物占画面高度 85%，居中；
白袍宽袖、黑色腰封与革带、黑色护腕、深色靴；白发披在肩前；双臂有极薄的冰霜气劲（薄、别抢主体）。
【风格/底】{BASE}
负向：手持武器、出招、挥剑、动态姿势、斗笠、背景环境、UI、水印、文字、多人、半身、坐姿、卡通、夸张比例。
"""

P_A3 = f"""16:9 横版，**同一个角色的「90° 侧面」视图**，只生成一张。
【引用图片说明】{tok('A2')}＝**唯一依据**：同一个人、同一发型、同一服装、同一比例，只把机位转到正侧面（朝画左）。
【画面】侧身直立，面朝画左；手臂自然下垂、不含武器；人物占画面高度 85%，居中；白发垂在肩后与胸前；
白袍宽袖的侧面轮廓、腰封厚度、靴型清晰。
【风格/底】{BASE}
负向：正脸、背面、手持武器、出招、动态姿势、背景环境、UI、水印、文字、多人、半身、卡通、换服装、换发型。
"""

P_A4 = f"""16:9 横版，**同一个角色的「背面」视图**，只生成一张。
【引用图片说明】{tok('A2')}＝**唯一依据**：同一个人、同一发型、同一服装、同一比例，只把机位转到背面。
【画面】背身直立，手臂自然下垂、不含武器；人物占画面高度 85%，居中；白发整片披在背上、发尾散乱；
白袍后背的褶皱、腰封的绑带、靴跟清晰。
【风格/底】{BASE}
负向：正脸、侧脸、手持武器、出招、动态姿势、背景环境、UI、水印、文字、多人、半身、卡通、换服装、换发型。
"""

P_A5 = f"""16:9 横版，**武器白底正交图**，只生成一张。
【引用图片说明】{tok('P2')}＝武器来源（锁剑身形态/霜纹/护手虹彩/玉绿晶簇/剑柄缠绳）。
【画面】一把冰晶长剑**水平放置**、剑尖朝右、全长完整入画，占画面宽 90%、居中；
剑身半透、内部龙形霜纹清晰；护手一道极细虹彩（青→品红）；护手根部玉绿色冰晶簇；剑柄缠绳可见；
**不出现人物、不出现手、不出现剑鞘**；剑身下方一点软阴影。
【风格/底】{BASE}
负向：人物、手、剑鞘、挥动、残影、彩色背景、光效爆炸、UI、水印、文字、多把剑、卡通、3D 渲染感。
"""

P_A6 = f"""16:9 横版，**右手握剑柄的特写**，只生成一张。
【引用图片说明】{tok('P1')}＝人物来源（锁护腕与袖口）；{tok('P2')}＝武器来源（锁剑柄缠绳与护手）。
【画面】右手握住剑柄的近景特写（只到手腕与小臂），剑身向画右延伸出画；白袍宽袖的袖口、黑色护腕清晰；
手指的关节与用力感可见；剑柄缠绳的纹理与护手边缘的虹彩可见。
【风格/底】{BASE}
负向：全身、脸、双手、多手、剑鞘、挥动、背景环境、UI、水印、文字、卡通、夸张手指、六指。
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


def gen_image(n, x, y, label, prompt, refs, size="2K", quality="high"):
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


def build():
    i = ID
    nodes = [
        input_image(i["P1"], 20, 20, "【素材】P1 原始人物截图", P1_UP),
        input_image(i["P2"], 20, 240, "【素材】P2 原始武器截图", P2_UP),
        input_text(i["S1"], 20, 470, 320, 420, "S1 角色与武器设定", S1_TEXT),

        gen_image(i["A0"], 420, 20, "【待生成】A0 设定母版（一张看完所有设定）", P_A0, [i["P1"], i["P2"]]),
        gen_image(i["A1"], 820, 20, "【待生成】A1 脸部特写（只做脸）", P_A1, [i["P1"]]),
        gen_image(i["A2"], 820, 330, "【待生成】A2 正面全身（锚）", P_A2, [i["P1"]]),
        gen_image(i["A5"], 820, 640, "【待生成】A5 武器白底正交", P_A5, [i["P2"]]),

        gen_image(i["A3"], 1220, 20, "【待生成】A3 侧面 90°（派生自 A2）", P_A3, [i["A2"]]),
        gen_image(i["A4"], 1220, 330, "【待生成】A4 背面（派生自 A2）", P_A4, [i["A2"]]),
        gen_image(i["A6"], 1220, 640, "【待生成】A6 握剑的手", P_A6, [i["P1"], i["P2"]]),

        input_text(i["S0"], 420, 1010, 720, 520, "S0 为什么先做资产", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["A0"]), (i["P2"], i["A0"]),
        (i["P1"], i["A1"]),
        (i["P1"], i["A2"]),
        (i["P2"], i["A5"]),
        (i["A2"], i["A3"]),
        (i["A2"], i["A4"]),
        (i["P1"], i["A6"]), (i["P2"], i["A6"]),
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
        {"id": "group-ywsa-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 素材（已预填）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywsa-1", "nodeIds": [i["A0"], i["A1"], i["A2"], i["A5"]],
         "bounds": bounds_for([i["A0"], i["A1"], i["A2"], i["A5"]]),
         "label": "01 母版 A0 + 锚点 A1/A2/A5（先跑这一组）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywsa-2", "nodeIds": [i["A3"], i["A4"], i["A6"]],
         "bounds": bounds_for([i["A3"], i["A4"], i["A6"]]),
         "label": "02 派生 · 侧面 / 背面 / 手（只参考 A2 / A5）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywsa-3", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "03 说明",
         "style": {"accent": None, "opacity": None, "borderColor": "#888888"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    return {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 资产板（设定母版 + 六张可用资产）v9",
            "description": ("A0 一张看完所有设定的设定母版（人看/存档）；A1 脸、A2 正面全身、A3 侧面、A4 背面、"
                            "A5 武器、A6 握剑手（机器用，下游直接引用）。纯灰底、无 UI、无水印。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywsa-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
                "targetNodeId": t, "targetHandle": "input",
                "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
            } for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }


def self_check(doc):
    import re
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
        label = n["meta"]["label"]
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for tk in toks:
            if tk not in by_id:
                problems.append(f"引用节点不存在: {label} -> {tk}")
            if tk not in refs:
                problems.append(f"引用未挂字段: {label} -> {tk}")
        for r in refs:
            if (r, n["id"]) not in edge_set:
                problems.append(f"字段挂了没连线: {label} <- {r}")
            rn = by_id.get(r)
            if rn and rn["type"] == "input-image" and not rn.get("outputs"):
                problems.append(f"被引用的上传节点是空的: {label} <- {r}")
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
        if n["type"] == "gen-image":
            print(f"  {n['meta']['label']}  {len(n['params']['model_params']['prompt'])} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()

