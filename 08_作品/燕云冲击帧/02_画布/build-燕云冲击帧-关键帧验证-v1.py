# -*- coding: utf-8 -*-
"""关键帧四设计 · 静帧验证 v1

四个 gpt-image-2 节点，各跑 1 张 16:9 / 1K 静帧：
    K1 黑底双剑（B 器物型 · 无人 · 水墨）
    K2 脸＋斜剑（A 凝视型 · 半身 · 水墨）
    K3 制动定格（A 页主候选 · 水墨）
    K4 制动定格·实色版（与 K3 同姿势，单变量对照）

挂 A1 脸 / A2 全身 / A5 武器 做身份一致性参考；K1 只挂 A5。
提示词全文与设计依据见 00_方案/33-关键帧四设计-静帧验证-v1.md。
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
OUT = HERE / "燕云冲击帧-关键帧验证-16x9-v1.monet"
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-04T12:00:00.000+08:00"
PREFIX = "yjk1"
BY = "linguanxi"

KEYS = ("A1", "A2", "A5", "K1", "K2", "K3", "K4")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}


def tok(k):
    return "{{" + ID[k] + "}}"


# 已生成资产清单里找出 A1/A2/A5 的 url 与分辨率
FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    for k in ("A1", "A2", "A5"):
        if core.startswith(k):
            FOUND[k] = v

missing = [k for k in ("A1", "A2", "A5") if k not in FOUND]
if missing:
    raise SystemExit("已生成资产清单-v3.json 缺：" + ", ".join(missing))


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


P_K1 = f"""黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张，画面里没有人。
【引用图片说明】{tok('A5')}＝武器外形，剑形、剑格、刃口必须与它一致，不许改形。
【主体】画面正中偏上悬着两柄竖立的同款长剑：剑尖朝上、剑身竖直，左右各一柄；两柄之间留出一条纯黑的竖直空隙，宽约画面五分之一；左柄略近略大，右柄略远略小。
【剑身】半透明冰晶长刃，靠近剑格处最宽、向剑尖收细；刃口有一条极细的霜齿边；剑身内部有淡冰纹与一道龙形暗纹（用飞白细线表现，不描实）；碧色玉质龙纹剑格只保留一点冷碧色，其余一律黑白。
【光】剑不发光、没有光晕、没有能量雾：全图唯一亮的是两侧刃口各一条冷白反光线，宽不超过画面宽的百分之一。
【爆点】两柄剑之间的中上方有一粒极小的纯白星芒，直径约为画面高的十八分之一；星芒四周只有四到六道很短的细光刺，不许扩散成光团、不许照亮背景。
【构图】纯黑底，黑要黑到发实；没有任何背景纹理；两柄剑的上端与下端都出画，看不到剑尖与剑首，也看不到握剑的人。
【明暗】近黑（亮度16%以下）占八成以上；纸白只出现在刃口反光、剑身中部与星芒，合计不超过画面一成；中间灰只允许出现在剑身厚度的边缘。
负向：人物、手、人脸、身体、发光、光晕、能量雾、彩色、大面积碧色、晶体高光、发光晶体、背景纹理、云、山、地面、地面反射、剑尖朝下、两柄剑交叉、字幕、水印、logo、游戏UI、卡通、贴图感。"""

P_K2 = f"""黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张，古风白发剑客半身像。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝发型、服装与体型比例；{tok('A5')}＝武器外形。人物必须是这三张里的人，不许换成别人。
【角色】青年男性剑客，银白色长发过肩、额前中分，发丝向画面左方横甩、方向一致，用浓墨块＋飞白碎笔表现，不用细线素描；剑眉、细长黑眼、神情冷峻。
【服装】白色宽袖长袍，衣纹用排线（hatching）＋飞白，袍面大面积留白；黑色高领内衬与黑色宽腰封压到近黑，腰封上一枚金属扣件是全图最重的小暗部；黑色护腕。
【武器与位置】右手持一柄半透明冰晶长剑；剑自画面左下角入画、向右上斜穿，与画面成约38度，跨度超过一条对角线，两端都出画；剑身宽侧面正对画面，宽度约为画面高的十分之一，能看清刃口霜齿与内部冰纹；碧色龙纹剑格在剑身中段露一点冷碧色。
【前后关系】剑压在人物身前（人物在剑后），剑身从右肩下方穿过，但不遮住脸、不遮住任何一只眼；握剑的手在画面左下角之外，画面里不出现手。
【构图】半身裁到腰；脸占画面高约四成、压在右侧三分线；画面左上是纸白留白。
【光影】脸是一小块干净的纸白；五官只用极少线条：眉、眼线、鼻梁、唇线各一笔；左眼落在暗部只留轮廓，右眼清楚、眼白只露一点；头发、腰封、背景墨块压到近黑。
【明暗配比】纸白（亮度86%以上）占一成到一成五；近黑（亮度16%以下）占四成以上；其余是灰调中间层；背景是泼墨块＋墨点喷溅＋干笔擦痕，不许碎成灰雾。
负向：彩色、发光、能量光效、冰晶反光、晶体质感、精细写实、五官细节堆砌、整把剑收在画面内、剑尖可见、剑尖朝镜头、剑横在胸前、剑遮住脸、两只眼都被遮、画面里出现手、居中对称、多余的手、第三只手、字幕、水印、logo、游戏UI、卡通。"""

P_K3 = f"""黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张，古风白发剑客的冲击定格。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝发型、服装与体型；{tok('A5')}＝武器外形。人物与剑必须是这三张里的，不许换人换剑。
【这一帧在说什么】他刚刚完成一次向右上方的横斩，此刻正在制动：重心落在后腿，肩胯反拧，剑停在斜上方。不是站着摆姿势，也不是蓄势待发。
【身体与发力】3/4 侧身；后腿屈、前腿向前踏出并踩实（脚尖朝外约30度）；胯转向画面右前，肩线反向拧向左后，肩胯成反向扭转；腰先带着躯干走，右臂最后才展开，伸到画面右上，肘不僵直；左手并起食指中指成剑指，收在左腰前；下颌略收，眼睛看向剑锋方向。
【剑与剑路】剑身宽侧面正对画面，从画面右下角一路斜贯到左上角，与画面成约40度，两端都出画；两侧刃口的霜齿看得清，剑身中段有冰纹与一道龙形暗纹；剑不发光，没有拖尾光带。
【握法·前景握把】持剑手在画面右下角的前景，手占画面高12%到15%，四指可见地环握剑柄、拇指压在食指上；剑柄横穿手心、两头都露在手外，下端露冰晶剑首、上端露碧色剑格；虎口紧贴剑格下沿，剑与小臂成一条直线、手腕不折，剑身自拳头上方延伸出去；剑柄不许被护手、剑身或衣袖盖住；护手（碧色龙纹剑格）宽度约为剑柄的两倍；剑柄加剑首约占全剑长度的八分之一。
【余势】银白长发、白色衣摆与宽袖一齐朝画面左上方甩，方向与剑路一致，用浓墨块＋飞白表现；剑柄位置有一圈很薄的墨爆向外炸开，只占画面左上一角，不遮脸、不遮持剑手、不遮剑身。
【构图与明暗】人物压在右侧三分线，剑把画面切成左下大三角与右上小三角；纸白（脸、剑身、留白）占一成到一成五；近黑（头发、腰封、背景墨块）占四成以上；其余灰调；背景为大块泼墨＋墨点喷溅＋干笔擦痕。
负向：站姿摆拍、双腿并直、下蹲、弓步、马步、剑横在胸前、剑尖朝镜头、剑身正对镜头变成一条线、整把剑收在画面内、剑发光、剑气光带、能量雾、墨遮住脸、多只手、第三只手、多余手臂、握在剑身上、剑从掌心穿出、折腕、无剑柄、剑柄被袖口吞掉、彩色、精细写实、居中对称、全身背影、字幕、水印、logo、游戏UI、卡通。"""

P_K4 = f"""国漫写实、游戏角色高光质感，冷调冰雪，实色，16:9 横版，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝发型、服装与体型；{tok('A5')}＝武器外形。人物与剑必须是这三张里的，不许换人换剑。
【这一帧在说什么】他刚刚完成一次向右上方的横斩，此刻正在制动：重心落在后腿，肩胯反拧，剑停在斜上方。不是站着摆姿势，也不是蓄势待发。
【身体与发力】3/4 侧身；后腿屈、前腿向前踏出并踩实（脚尖朝外约30度）；胯转向画面右前，肩线反向拧向左后；腰先带着躯干走，右臂最后才展开，伸到画面右上，肘不僵直；左手并起食指中指成剑指，收在左腰前；下颌略收，眼睛看向剑锋方向。
【服装】按 {tok('A2')} 实色：白色宽袖长袍、黑色高领内衬、黑色宽腰封与金属扣、黑色护腕、黑色长靴，袍下摆有冰纹。
【武器】半透明冰晶长刃，靠近剑格处最宽、向剑尖收细，刃口霜齿发冷白，碧色玉质龙纹剑格与冰晶剑首保留本色；剑不发光，只有刃口反光和内部折射。
【剑与剑路】剑身宽侧面正对画面，从画面右下角斜贯到左上角，与画面成约40度，两端都出画。
【握法·前景握把】持剑手在画面右下角的前景，手占画面高12%到15%，四指可见地环握剑柄、拇指压在食指上；剑柄横穿手心、两头都露在手外；虎口紧贴剑格下沿，剑与小臂成一条直线、手腕不折；剑柄不许被袖口或剑身盖住。
【余势与环境】白发与衣摆朝左上方甩动；剑脊后方拖出细碎的冰晶颗粒与霜雾，宽不超过画面宽的十分之一，不遮脸、不遮持剑手、不遮剑身；背景是冷灰雪原与低垂雪雾，简洁，不出现建筑与其他人；地面有被剑气掀起的雪粒。
【光】低角度侧逆光，脸右侧有一道冷白边光；脸可读，五官写实但不堆细节。
【构图】人物压在右侧三分线，剑把画面切成左下大三角与右上小三角。
负向：黑白、水墨、纸白、发光、光晕、能量光柱、过饱和蓝色、紫色魔法、卡通、低模、塑料质感、站姿摆拍、双腿并直、剑横在胸前、剑尖朝镜头、整把剑收在画面内、多只手、握在剑身上、剑从掌心穿出、折腕、无剑柄、字幕、水印、logo、游戏UI、居中对称。"""

PLAN = [
    ("K1", "01 器物型·黑底双剑（无人·水墨）", P_K1, ["A5"]),
    ("K2", "02 凝视型·脸＋斜剑（水墨）", P_K2, ["A1", "A2", "A5"]),
    ("K3", "03 制动定格（水墨·主候选）", P_K3, ["A1", "A2", "A5"]),
    ("K4", "04 制动定格·实色版（对照）", P_K4, ["A1", "A2", "A5"]),
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


def gen_image(nid, x, y, label, prompt, refs):
    mp = {
        "prompt": prompt,
        "reference_images": [{"node_id": ID[r]} for r in refs],
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
        input_image(ID["A1"], 20, 20, "【已生成·复用】A1 脸部", up("A1")),
        input_image(ID["A2"], 20, 340, "【已生成·复用】A2 全身", up("A2")),
        input_image(ID["A5"], 20, 660, "【已生成·复用】A5 武器", up("A5")),
    ]
    pairs = []
    for i, (key, label, prompt, refs) in enumerate(PLAN):
        nodes.append(gen_image(ID[key], 420 + i * 360, 20, "【待生成】" + label, prompt, refs))
        for r in refs:
            pairs.append((ID[r], ID[key]))
    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [{"id": "g-yjk1-0", "nodeIds": [ID["A1"], ID["A2"], ID["A5"]],
               "bounds": bf([ID["A1"], ID["A2"], ID["A5"]]), "label": "00 已生成资产（复用）",
               "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}}]
    for i, (key, label, _p, _r) in enumerate(PLAN, start=1):
        groups.append({"id": f"g-yjk1-{i}", "nodeIds": [ID[key]], "bounds": bf([ID[key]]),
                       "label": label, "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}})
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 关键帧验证 v1（四设计静帧）",
            "description": ("四个关键帧设计各跑 1 张 16:9 静帧：K1 黑底双剑（器物型·无人）、"
                            "K2 脸＋斜剑（凝视型）、K3 制动定格（主候选·水墨）、K4 制动定格实色版（对照）。"
                            "挂 A1/A2/A5 原资产；K1 只挂 A5。只出图，不上视频。"),
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
    for key, label, prompt, refs in PLAN:
        print(f"  {key}: prompt {len(prompt)} 字, 参考 {refs}, node={ID[key]}")


if __name__ == "__main__":
    main()
