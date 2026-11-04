# -*- coding: utf-8 -*-
"""握法专项测试 v4 —— 修正姿势描述后重测

v1–v3 全部卡在"腕与剑柄不同向"。自查原资产 A6 后确认：**是提示词的姿势描述错了**。
  · 我写「照 A6 几何：前臂—手—剑柄一条直线」，但 A6 自己手是斜跨在柄上约 30–35°，不是直线；
  · 文字与参考图打架时模型听图的，所以两轮腕角几乎没变；
  · K3 里臂与剑更是接近垂直（握锤式），这才是"握得不顺"的主因。

v4 的改动：
  1. 不引用 A6 的几何，改成可执行条件「护腕的轴线正对剑尖」；
  2. 构图改成与全身图同角度：剑自右下向左上约 40°，小臂沿同一条线从左下伸入；
  3. 去掉「手背朝镜头」——40° 斜握时会逼模型拧手，正是折腕来源；
  4. 负向加「小臂与剑身垂直、握锤式、手臂从右上斜插、肘部入画」。
握点、四指、剑首、审核用词沿用 v2/v3 已生效的写法，一字不改。

导入不花积分；运行需用户明确授权。
"""
import hashlib
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-握法专项-v4.monet"
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-04T16:00:00.000+08:00"
PREFIX = "ywg4"
BY = "linguanxi"

KEYS = ("A5", "A6", "G1", "G2")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}


def tok(k):
    return "{{" + ID[k] + "}}"


FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    for k in ("A5", "A6"):
        if core.startswith(k):
            FOUND[k] = v
for k in ("A5", "A6"):
    if k not in FOUND:
        raise SystemExit("已生成资产清单-v3.json 缺：" + k)


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


BODY = f"""【引用图片说明】{tok('A6')}＝手的形态与握法；{tok('A5')}＝武器外形，剑格、剑首、刃口照它。
【构图·最关键】整条手臂和整个剑身在同一条斜线上：剑自画面右下角伸向左上角，约40度；小臂、手腕、拳头、剑柄、剑身沿这条线依次排开；**护腕的轴线正对剑尖**——把护腕朝剑的方向延长，延长线要穿过剑尖。
【不许出现的姿势】小臂不能从画面上方或右上斜插下来；小臂不能与剑身成T形或接近垂直（那是握锤子的握法）；肘部在画面外；手占画面高35%到45%。
【手】从右前方看这只右手，能看到食指到小指四个指节；手掌内侧贴住剑柄；画面里只有这一只手、这一条手臂。
【握点】虎口（拇指与食指之间的肉）紧贴剑格，手与剑格之间不留裸露的剑柄；从剑格往剑首方向依次是：剑格—食指—中指—无名指—小指—剑首；四指扣紧、指节弯曲、指尖收进掌心一侧；拇指压在食指上，拇指尖被手挡住是正常的。
【剑】剑格是碧色玉质龙纹那一件，只在一端；另一端是短而圆的龙首剑首，紧贴拳后、长度不超过手宽的一半，不尖不弯、不是刀刃；剑身冰晶半透、刃口一条冷白、不发光；剑柄整段被手指包住，指缝之间能看见柄上的纹路。
"""

NEG = ("负向：小臂与剑身垂直、握锤式、手臂从画面右上斜插、肘关节入画、"
       "两只手、第二只手臂、第三只手、四指平摊、手指伸直、扶着剑柄、"
       "虎口与剑格之间有缝、折腕、剑柄与护腕不同向、无剑柄、"
       "剑首画成第二个刃、剑首有尖刺、剑首像刀刃、两端都是剑格、"
       "发光、光晕、字幕、水印、logo、游戏UI、卡通。")

P_G1 = "手部特写，写实，16:9 横版，只生成一张；画面里只有一只右手、一截剑柄、一小段剑身、黑色护腕与一点白袖。\n" + BODY + NEG

P_G2 = ("黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张；"
        "画面里只有一只右手、一截剑柄、一小段剑身、黑色护腕与一点白袖；"
        "皮肤与剑身保持纸白，护腕与袖口压到近黑，碧色剑格只留一点冷碧。\n" + BODY + NEG)

PLAN = [
    ("G1", "01 握法·实色 v4（40°共线·护腕对剑尖）", P_G1),
    ("G2", "02 握法·水墨 v4（同措辞）", P_G2),
]


def input_image(nid, x, y, label, info):
    return {
        "id": nid, "type": "input-image", "mainOutputId": "output-" + nid.split("-")[1],
        "meta": {"x": x, "y": y, "width": 320, "height": 200, "label": label, "resourceType": None},
        "outputs": [{
            "id": "output-" + nid.split("-")[1], "status": "done", "error": None,
            "value": info["url"], "cover": None, "name": info["name"],
            "resolution": {"width": info["width"], "height": info["height"]},
            "size": info["size"], "md5": info["md5"],
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def gen_image(nid, x, y, label, prompt):
    mp = {
        "prompt": prompt,
        "reference_images": [{"node_id": ID["A5"]}, {"node_id": ID["A6"]}],
        "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 1024,
        "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True,
    }
    return {
        "id": nid, "type": "gen-image", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": mp},
        "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def main():
    nodes = [
        input_image(ID["A5"], 20, 20, "【已生成·复用】A5 武器", up("A5")),
        input_image(ID["A6"], 20, 340, "【已生成·复用】A6 握剑手", up("A6")),
    ]
    pairs = []
    for i, (key, label, prompt) in enumerate(PLAN):
        nodes.append(gen_image(ID[key], 420 + i * 360, 20, "【待生成】" + label, prompt))
        pairs += [(ID["A5"], ID[key]), (ID["A6"], ID[key])]
    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [{"id": "g-ywg4-0", "nodeIds": [ID["A5"], ID["A6"]],
               "bounds": bf([ID["A5"], ID["A6"]]), "label": "00 参考（武器＋握法）",
               "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}}]
    for i, (key, label, _p) in enumerate(PLAN, start=1):
        groups.append({"id": f"g-ywg4-{i}", "nodeIds": [ID[key]], "bounds": bf([ID[key]]),
                       "label": label, "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}})
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 握法专项 v4（40°共线·护腕对剑尖）",
            "description": ("修正姿势描述后重测握法：剑与臂同在一条约 40° 斜线上，护腕轴线正对剑尖；"
                            "去掉「手背朝镜头」。G1 实色 / G2 水墨同措辞。只拍手＋剑柄，不掺景别变量。"),
            "nodes": nodes,
            "edges": [{"id": "edge-" + hashlib.md5((str(k) + s + t).encode()).hexdigest()[:8],
                       "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
                       "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY}
                      for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出:", OUT)
    print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(groups)}")
    for key, label, prompt in PLAN:
        print(f"  {key}: prompt {len(prompt)} 字, 参考 [A5, A6], node={ID[key]}")


if __name__ == "__main__":
    main()
