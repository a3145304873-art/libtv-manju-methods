# -*- coding: utf-8 -*-
"""燕云大招 V4 冰龙贯野 · 横扫版 8s 直出画布

设计稿见 00_方案/35-大招V4-冰龙贯野-横扫版-动作链与相机路线-v2.md。
本画布只放一条候选（不四连跑）：A1 脸 + A2 全身 + A5 武器 作 reference，
V4 用 seedance-2.0-mini / 8s / 720p / 16:9 / 开启音频，与 30 号四候选同参数。

关键写法：龙的「身体」贴扫击弧线、「龙首」沿末段切线冲出撞门。
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
OUT = HERE / "燕云大招-横扫版-8s-v1.monet"
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-04T20:00:00.000+08:00"
PREFIX = "yds1"
BY = "linguanxi"

KEYS = ("A1", "A2", "A5", "V4", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}


def tok(k):
    return "{{" + ID[k] + "}}"


FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    for k in ("A1", "A2", "A5"):
        if core.startswith(k):
            FOUND[k] = v
for k in ("A1", "A2", "A5"):
    if k not in FOUND:
        raise SystemExit("已生成资产清单-v3.json 缺：" + k)


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


P_V4 = f"""16:9，8 秒，东方仙侠大招《冰龙贯野》，一条直出。
【引用图片说明】{tok('A1')}＝角色脸（保持同一人）；{tok('A2')}＝全身与服装比例；{tok('A5')}＝武器外形。全片只有这一把剑，不换人、不换手。
【通用基底】国漫写实 CG，电影级画质；冷冽青蓝主调，曜金只一点；写实冰雪、金属与布料；体积光；24fps；无穿模；动作凌厉，运镜沉稳不炫技。
【速度与打击】前两拍压住节奏（慢动作），横扫段骤然爆发、快到只剩残影；命中插入冲击帧与 0.1 秒抽帧顿挫，镜头猛沉 0.3 米后急速回弹；音效随动作瞬时触发，命中配破空音爆与金石碎裂。
【场景】雪原古战场，画面右侧纵深约三十米处立一座十二米高的残破石门；地面旧雪与冰纹；风雪低吹。
【角色与武器】一米八五青年剑客，白发束起、白袍黑腰封、双臂覆薄冰；右手单手握剑、虎口贴剑格；藏音·龙跃霄汉：冰泉色剑身、擎冰刃口、炼虹剑颚、曜日一点明光；剑身不整体发光，只留一道冷白高光。
【动作链】蓄势＝重心后坐、身体左转三十度、剑带到左后上方、剑尖朝左后下；展开＝右脚蹬地、左脚碾转、剑穿过体前中线、冰纹自剑格亮起；释放＝一次横扫约一百四十度、剑从正前扫到右侧、剑尖停在右前三十度指向石门；碰撞＝龙首撞门、石门被横向切开、碎石沿切线飞出、躯干被带回五度；收势＝剑尖点地、后脚落实、上身回正。
【冰龙】龙尾始终连着剑身中段：剑扫到哪里，龙身就长到哪里，形成一条贴着扫击弧线的冰龙；剑停在右前时，龙首沿最后一段切线直线冲出撞门；龙不盘旋、不绕圈、不回头。
【逐拍】
0-1.4 秒｜低机位微距：手、剑格、半张脸；冰霜沿剑脊爬、剑身轻颤；他抬眼。只有剑鸣与被抽空的风。
1.4-2.8 秒｜侧后四分之三全身：右脚蹬地、左脚碾转、胯从左转到正前、肩线反向拧；剑从左上落到体前；冰纹自剑格向剑身逐段亮起。
2.8-4.6 秒｜正前方中景，镜头随剑平摇：一次横扫约一百四十度，剑从正前扫到右侧、剑尖停在右前；龙身被剑从空气里拉出、贴着弧线铺开；角色右脚蹬直、重心压在前脚、白发与衣摆拖在剑后。
4.6-6.2 秒｜左前方中远景：龙首沿切线撞上石门，插入冲击帧与 0.1 秒抽帧顿挫；石门被横向切开一道斜口，碎石与冰晶沿切线飞出，雪浪自门底向两侧排开；镜头猛沉后回弹。
6.2-8.0 秒｜拉远至大远景：门半塌、冰尘未落；地面上被犁出一道横沟；残留的冰晶弧线像划痕悬在半空后落下；他站定、剑尖点地、白袍落回；画面定格。
【核心特效】冰龙（唯一主奇观，弧段＋切线）、冰纹生长、冲击波排雪、冰尘与弧线残痕。
【收势】留下：十二米石门被横切开的斜口、地面上二十米长的横沟、还在落的冰尘；站着：他，剑尖点地。
【负向】不出现第二把剑、不换左手、不多手、不整体发光、不红眼、不出现红色、不出现西方翼龙、不出现对手尸体或血液、不生成字幕/UI/水印、不穿模、不全程慢动作、不出现水墨、不出现第二奇观（剑阵、剑雨、天门、法相都不出现）、龙不盘旋不回旋、剑不脱手。"""

P_S0 = """【本版要点（横扫 v2）】
1 招式：横扫约 140°，左后上 → 体前 → 右侧平；力量来自右脚蹬地＋左脚碾转，不是手臂抡。
2 冰龙：身体贴扫过的弧线（龙尾连剑身中段），龙首沿末段切线直冲石门。身体负责"扫"，龙首负责"贯"。
3 五拍不等长：蓄势 1.4 / 展开 1.4 / 释放 1.8 / 碰撞 1.6 / 收势 1.8，释放与碰撞分开才有顿挫。
4 相机一镜一动作：微距缓推 → 侧后横移 → 正前平摇 70°（横扫必须跟） → 左前猛沉回弹 → 后退上升。
5 收势必须回答留下什么：门被横切、地上 20m 横沟、冰尘在落、他剑尖点地。
6 握法：只有 ① 微距可验（手约 35%）；②③ 全身手 <10%，不要求握法可读。
设计稿：00_方案/35-大招V4-冰龙贯野-横扫版-动作链与相机路线-v2.md"""


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


def input_text(nid, x, y, label, text):
    return {
        "id": nid, "type": "input-text", "mainOutputId": "output-" + nid.split("-")[1],
        "meta": {"x": x, "y": y, "width": 320, "height": 460, "label": label, "resourceType": None},
        "outputs": [{
            "id": "output-" + nid.split("-")[1], "status": "done", "error": None,
            "value": text, "cover": None, "name": label, "resolution": None,
            "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def gen_video(nid, x, y, label, prompt):
    mp = {
        "prompt": prompt,
        "reference_images": [{"node_id": ID["A1"]}, {"node_id": ID["A2"]}, {"node_id": ID["A5"]}],
        "_reference_way": "reference",
        "reference_videos": [], "reference_audios": [],
        "first_frame_image": None, "last_frame_image": None,
        "aspect_ratio": "16:9", "resolution": "720p", "duration": 8,
        "generate_audio": True, "seed": -1,
    }
    return {
        "id": nid, "type": "gen-video", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": 400, "height": 300, "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": mp},
        "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def main():
    nodes = [
        input_image(ID["A1"], 20, 20, "【已生成·复用】A1 脸部", up("A1")),
        input_image(ID["A2"], 20, 240, "【已生成·复用】A2 全身", up("A2")),
        input_image(ID["A5"], 20, 460, "【已生成·复用】A5 武器", up("A5")),
        input_text(ID["S0"], 20, 680, "S0 横扫版设计要点", P_S0),
        gen_video(ID["V4"], 420, 20, "【候选】V4 冰龙贯野·横扫 8s", P_V4),
    ]
    pairs = [(ID["A1"], ID["V4"]), (ID["A2"], ID["V4"]), (ID["A5"], ID["V4"])]
    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        {"id": "g-yds1-0", "nodeIds": [ID["A1"], ID["A2"], ID["A5"]],
         "bounds": bf([ID["A1"], ID["A2"], ID["A5"]]), "label": "00 已生成资产（复用）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "g-yds1-1", "nodeIds": [ID["S0"]], "bounds": bf([ID["S0"]]),
         "label": "01 设计要点（横扫 v2）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8DE05B"}},
        {"id": "g-yds1-2", "nodeIds": [ID["V4"]], "bounds": bf([ID["V4"]]),
         "label": "02 候选（只跑这一条）",
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
            "name": "燕云大招 · 冰龙贯野·横扫版 8s v1",
            "description": ("单条候选：横扫 140°，冰龙身体贴弧线、龙首沿切线撞门。"
                            "挂 A1/A2/A5；seedance-2.0-mini 8s 720p 开音频；不四连跑。"),
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
    print(f"  V4: prompt {len(P_V4)} 字, model seedance-2.0-mini 8s 720p, node={ID['V4']}")


if __name__ == "__main__":
    main()
