# -*- coding: utf-8 -*-
"""关键帧验证 v3b：前景握把（新画布复测）（手占画面高 15%）

起因：K4′ 全身帧手只占 6.3%，八条握法判据里只过一条，读作"手掌扶着剑格"。
按 34 号《手部持剑姿势规范》的尺度预算，要到 12–20% 才读得出"握住"，且必须配前景＋柄两头露。

本图锁死三个尺寸（先算后画）：
    画幅 1280×720；手高 15% ≈ 108px；身体高 ≈60% ≈ 432px（手/身 ≈0.25，约 2 倍自然比例 → 前景透视）
姿态与握法条款直接搬 34 号 §3.1 的八条可执行句式。

只出实色一张：实色画手比水墨稳，水墨在 8% 尺度上会糊成团。
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
OUT = HERE / "燕云冲击帧-关键帧验证-16x9-v3b.monet"
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
CREATED = "2026-11-04T19:00:00.000+08:00"
PREFIX = "yjk3b"
BY = "linguanxi"

KEYS = ("A1", "A2", "A5", "K5", "K5b")
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


P_K5 = f"""国漫写实、游戏角色高光质感，冷调冰雪，实色，16:9 横版，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝服装与体型；{tok('A5')}＝武器外形。人物与剑必须是这三张里的，不许换人换剑。
【景别与尺寸·先定这个】持剑手在画面右下角的前景，**手占画面高约七分之一（15%）**，四根手指要看得清；人物整体在手的左后方，**全身仍入画、双脚看得见**，身体从头顶到脚约占画面高六成；近大远小：手比身体离镜头近得多，右侧前臂被透视缩短。
【这一帧在说什么】他刚完成一次向画面左上的横斩，正在制动：重心落在后腿，肩胯反拧，剑停在斜上方。
【身体与发力】3/4 侧身；后腿屈膝下沉、前腿向前踏出并踩实；胯转向画面右前、肩线反向拧向左后；腰先带着躯干走；下颌略收，眼睛看向剑锋。
【剑与剑路】剑身宽侧面正对画面，自画面右下的手握处斜贯左上角，剑尖在左上出画；两侧刃口的霜齿看得清，剑身中段有冰纹与一道龙形暗纹；剑不发光、没有拖尾光带。
【握持·遮挡】剑柄从拳心穿过，四指压在剑柄的近侧、指尖绕过剑柄到远侧；剑柄被手指压住，**在指缝处断开**，看不见一条连续不断的柄。
【握持·两侧】拳的两边都看得到剑柄：剑格一侧露出约半个手宽，剑首一侧露出约一个手宽。
【握持·虎口】虎口贴住剑格下沿，手掌与剑柄之间有接触阴影、不留缝；手掌不要贴在剑格上。
【握持·拇指】拇指横压在中指第二指节上；从手背侧只看得见虎口鼓起。
【握持·指节】四个指节排成一道弧，因为他们绕的是圆柱；不要四条平行香肠。
【握持·腕】护腕的轴线正对剑尖，夹角小于15度。
【握持·数量】画面里只有两只手：这一只持剑，另一只并起食指中指成剑指、收在胸前。
【余势】银白长发与白色衣摆朝画面左上方甩，方向与剑路一致；剑脊后方拖出细碎冰晶颗粒与霜雾，宽不超过画面宽的十分之一，不遮脸、不遮持剑手、不遮剑身。
【环境与光】冷灰雪原与低垂雪雾，简洁，不出现建筑与其他人；地面有被剑气掀起的雪粒；低角度侧逆光，脸右侧一道冷白边光。
负向：手占画面太小、手指平摊、手掌贴在剑格上、握着护手而不是剑柄、剑柄从掌心穿过、剑柄在指缝处连续不断、看不见剑柄、剑柄被袖口吞掉、四指并排成平行香肠、拇指竖起、折腕、三只手、两只右手、双手同握一柄、六指、指头粘连、手悬空不接触剑柄、全身缩成一个点、裁到脚、发光、光晕、能量光柱、过饱和蓝色、紫色魔法、卡通、低模、塑料质感、字幕、水印、logo、游戏UI。"""

P_K5B = ("黑白水墨武侠风，炭笔线条＋水墨块面混合，高对比，16:9 横版，只生成一张；" + P_K5.split(chr(10),1)[1]).replace("国漫写实、游戏角色高光质感，冷调冰雪，实色", "")

PLAN = [
    ("K5", "05 前景握把·实色（手占15%·八条判据）", P_K5),
    ("K5b", "06 前景握把·水墨（同构图对照）", P_K5B),
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

    groups = [{"id": "g-yjk3-0", "nodeIds": [ID["A1"], ID["A2"], ID["A5"]],
               "bounds": bf([ID["A1"], ID["A2"], ID["A5"]]), "label": "00 已生成资产（复用）",
               "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}}]
    for i, (key, label, _p) in enumerate(PLAN, start=1):
        groups.append({"id": f"g-yjk3-{i}", "nodeIds": [ID[key]], "bounds": bf([ID[key]]),
                       "label": label, "style": {"accent": None, "opacity": None, "borderColor": "#E05B8D"}})
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 关键帧验证 v3b（前景握把·复测）",
            "description": ("按 34 号尺度预算重做 A 页关键帧：手在右下前景、占画面高约15%，"
                            "身体在左后方仍全身入画，剑与臂共线。八条握法判据的可执行句式直接内嵌。"),
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
    print("尺寸预算：画幅1280x720 | 手15%=108px | 身体60%=432px | 手/身=0.25")
    for key, label, prompt in PLAN:
        print(f"  {key}: prompt {len(prompt)} 字, node={ID[key]}")


if __name__ == "__main__":
    main()
