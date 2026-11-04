# -*- coding: utf-8 -*-
"""关键帧验证 v2：K3′ 制动定格（全身）＋ K4′ 实色版

相对 v1 只改两类变量，且两类都已在别的图里单独验过：
  · 景别（K3 裁到腰 → 全身入画、双脚可见），这是 K3 失败的直接原因；
  · 握法（换成 2026-11-04 v4 特写验证通过的定稿条款：护腕轴线正对剑尖 / 指序 / 剑首短圆）。
  · K4′ 另换一版"审核更友好"的措辞：持剑法、剑的前端、刃边；避免"剑从掌心穿出"一类描述。
明暗条款按 v1 实测校正：纸白 10–15%、近黑 ≥40%（v1 的 K3 近黑只有 13.1%，发灰）。

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
OUT = HERE / "燕云冲击帧-关键帧验证-16x9-v2.monet"
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-04T17:00:00.000+08:00"
PREFIX = "yjk2"
BY = "linguanxi"

KEYS = ("A1", "A2", "A5", "K3", "K4")
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


P_K3 = f"""黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张，古风白发剑客的冲击定格。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝发型、服装与体型；{tok('A5')}＝武器外形。人物与剑必须是这三张里的，不许换人换剑。
【这一帧在说什么】他刚完成一次向右上方的横斩，正在制动：力量已经出去，身体被自己的力带着停住。不是站着摆姿势，也不是蓄势待发。
【景别·本轮最关键】全身入画：双脚都看得见、完整落在画面下缘以上；后腿屈膝下沉、前腿向前踏出并踩实、脚尖朝外约30度；不要裁到腰，不要裁到小腿。
【身体与发力】3/4 侧身；胯转向画面右前、肩线反向拧向左后；腰先带着躯干走，右臂最后展开；左手并起食指中指成剑指、收在左腰前；下颌略收，眼睛看向剑锋。
【剑与剑路】剑身宽侧面正对画面，自画面右下角斜贯左上角约40度，两端出画；两侧刃口的霜齿看得清，剑身中段有冰纹与一道龙形暗纹；剑不发光、没有拖尾光带。
【握法·定稿条款】护腕的轴线正对剑尖，护腕的延长线穿过剑尖；小臂、手腕、拳头、剑柄、剑身沿同一条斜线排开；小臂不许与剑身成T形或接近垂直。虎口紧贴剑格，手与剑格之间不留裸露的剑柄；自剑格往剑首方向依次是：剑格—食指—中指—无名指—小指—剑首；四指扣紧、指节弯曲、指尖收进掌心一侧；拇指压在食指上。剑首短而圆、紧贴拳后、长度不超过手宽的一半，不尖不弯、不是刀刃。手占画面高约8%，指节可辨。
【余势】银白长发、白色衣摆与宽袖一齐朝画面左上方甩，方向与剑路一致，用浓墨块＋飞白表现；剑柄位置有一圈很薄的墨爆向外炸开，只占画面左上一角，不遮脸、不遮持剑手、不遮剑身。
【明暗】背景是大块浓墨与泼墨；近黑（亮度16%以下）占画面四成以上；纸白（脸、剑身、左上留白）占一成到一成五；其余为灰调中间层；不要灰雾、不要整体发灰。
负向：裁到腰、裁到小腿、脚不在画面内、站姿摆拍、双腿并直、小臂与剑身垂直、握锤式、肘部遮住剑柄、两只右手、双手同时持剑、第三只手、多余手臂、四指平摊、折腕、剑首画成第二个刃、剑发光、能量雾、墨遮住脸、彩色、居中对称、字幕、水印、logo、游戏UI、卡通。"""

P_K4 = f"""国漫写实、游戏角色高光质感，冷调冰雪，实色，16:9 横版，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝发型、服装与体型；{tok('A5')}＝武器外形。人物与剑必须是这三张里的，不许换人换剑。
【这一帧在说什么】他刚完成一次向画面左上的挥剑，正在收势：重心落在后腿，肩胯反拧，剑停在斜上方。
【景别·本轮最关键】全身入画：双脚都看得见、完整落在画面下缘以上；后腿屈膝下沉、前腿向前踏出并踩实、脚尖朝外约30度；不要裁到腰。
【身体】3/4 侧身；胯转向画面右前、肩线反向拧向左后；腰先带着躯干走，右臂最后展开；左手并起食指中指成剑指、收在左腰前；下颌略收，眼睛看向剑锋。
【服装】按 {tok('A2')} 实色：白色宽袖长袍、黑色高领内衬、黑色宽腰封与金属扣、黑色护腕、黑色长靴，袍下摆有冰纹。
【剑】半透明冰晶长刃，靠近剑格处最宽、向剑的前端收细；碧色玉质龙纹剑格与冰晶剑首保留本色；剑不发光，只有刃边反光与内部折射。
【剑与剑路】剑身宽侧面正对画面，自画面右下角斜贯左上角约40度，两端出画。
【持剑法】护腕的轴线正对剑的前端，延长线穿过剑的前端；小臂、手腕、拳头、剑柄、剑身沿同一条斜线；小臂不许与剑身成T形或接近垂直。手包住剑柄、四指扣紧、指节可辨；手与剑格之间不留裸露的剑柄；剑首短而圆、紧贴拳后、长度不超过手宽的一半。画面里只有两只手：这一只持剑，另一只成剑指。
【余势与环境】白发与衣摆朝左上方甩动；剑脊后方拖出细碎的冰晶颗粒与霜雾，宽不超过画面宽的十分之一，不遮脸、不遮持剑手、不遮剑身；背景是冷灰雪原与低垂雪雾，简洁，不出现建筑与其他人；地面有被剑气掀起的雪粒。
【光】低角度侧逆光，脸右侧有一道冷白边光；脸可读，五官写实但不堆细节。
【构图】人物压在右侧三分线，剑把画面切成左下大三角与右上小三角。
负向：黑白、水墨、纸白、发光、光晕、能量光柱、过饱和蓝色、紫色魔法、卡通、低模、塑料质感、裁到腰、站姿摆拍、双腿并直、小臂与剑身垂直、握锤式、两只右手、双手同时持剑、第三只手、多余手臂、折腕、剑首画成第二个刃、字幕、水印、logo、游戏UI、居中对称。"""

PLAN = [
    ("K3", "03 制动定格′·全身（水墨·定稿握法）", P_K3),
    ("K4", "04 制动定格′·全身实色（审核友好措辞）", P_K4),
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
        "reference_images": [{"node_id": ID["A1"]}, {"node_id": ID["A2"]}, {"node_id": ID["A5"]}],
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
    for i, (key, label, prompt) in enumerate(PLAN):
        nodes.append(gen_image(ID[key], 420 + i * 360, 20, "【待生成】" + label, prompt))
        for r in ("A1", "A2", "A5"):
            pairs.append((ID[r], ID[key]))
    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [{"id": "g-yjk2-0", "nodeIds": [ID["A1"], ID["A2"], ID["A5"]],
               "bounds": bf([ID["A1"], ID["A2"], ID["A5"]]), "label": "00 已生成资产（复用）",
               "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}}]
    for i, (key, label, _p) in enumerate(PLAN, start=1):
        groups.append({"id": f"g-yjk2-{i}", "nodeIds": [ID[key]], "bounds": bf([ID[key]]),
                       "label": label, "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}})
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 关键帧验证 v2（K3′ 全身＋实色对照）",
            "description": ("K3′：全身入画＋定稿握法＋明暗校正（水墨）；K4′：同姿势同景别，实色，"
                            "换审核友好措辞。挂 A1/A2/A5。只出图，不上视频。"),
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
        print(f"  {key}: prompt {len(prompt)} 字, node={ID[key]}")


if __name__ == "__main__":
    main()
