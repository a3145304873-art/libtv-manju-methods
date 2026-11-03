# -*- coding: utf-8 -*-
"""等菜卡 → Monet 画布（心易做菜 · 菇子柒式四段版）

用法：
    py -3 build_from_slope.py recipes/EP01-等土豆熟.json [-o EP01-等土豆熟-v1.monet]

结构（对齐菇子柒/秃秃）：
    60 s = 取 / 理 / 火 / 吃，4 段 × 15 s，每段 2 动作 + 1 空镜，约 5 秒一拍。
    一面坡四级台地；段与段是硬切（换台地），段内 3 个镜头。
    视频全部走全能参考（_reference_way=reference），不挂首/尾帧槽。

组＝跑序：
    00 参考 → 01 场景 → 02 道具 → 03 四格 → 04 参考帧 K1–K4
    → 05 V1 → 06 V2 → 07 V3 → 08 V4 → 09 说明
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TS = "2026-11-02T17:10:00.000+08:00"
BY = "libtv-workspace"
PREFIX = "xyslope-01"

nodes, edges, groups = [], [], []


# ---------------- 角色与风格常量 ----------------
CHAR_BODY = (
    "圆身、无脖子、头身一体；暖棕短绒、"
    "绒毛方向可见、边缘有绒光；奶油色大脸板、白色圆形眼片＋外圈一条深棕细线、中心空白（无瞳孔、无高光点）、"
    "橘色腮红、一字嘴（不上扬）；白肚；棕色短手、无手指，圆脚、脚踝一圈奶油色；"
    "只有两只短手和两只圆脚，任何角度都不出现第三只手、多余手臂或手；"
    "头顶一颗橘子带两片绿叶（本体：不可摘、不可吃、不可换成别的水果）。"
    "表情淡定，情绪只靠歪头、后仰、蹲、耳朵与身体；不看镜头、不卖萌、不拟人化眼神。"
)

EYE = (
    "【心易眼睛·仅限心易】心易是毛绒玩具，眼睛是固定塑料/刺绣件，不是生物眼："
    "白色圆形眼片，中心没有黑色瞳孔；外圈一圈深棕色细描边；眼片中心保持空白，没有高光点；"
    "眼片形状、外圈深棕线、中心空白全程不变；不出现瞳孔/黑瞳/眼珠/虹膜/高光点；"
    "眼睛全程睁开，用力、咬、满足时也不闭眼、不眯眼、不笑成弯眼；"
    "不眨眼、不抬眼皮、不皱眉；情绪只靠歪头/身体/手势/咔啵。"
)

SCALE = (
    "尺度：这是一个为她配好的小世界——石灶比她高，灶口到她胸口；陶锅坐在灶顶，"
    "锅沿高过她头顶；灶边的柴堆可以踩着爬上灶台；石池她坐得上去、两只脚泡得进去；"
    "木棍、陶碟、小勺按她身量配。锅盆可以比她大，但不要画成人类尺寸的巨物，"
    "也不要把世界缩成玩具模型。"
)

LIGHT = (
    "光：清晨六点半到八点，雾没散；暖白晨光从坡顶低角度斜下来，做逆光与轮廓光；"
    "火只是灶口一小团暖点，不照全场；不用冷蓝、不用夜景、不打第二支灯。"
)

MATERIAL = (
    "材质：毛绒（短绒、绒光、压痕、沾泥变暗）／粗陶（哑光、开片）／湿石（水痕、苔）／"
    "食物（焦皮、淀粉白、热气）四层要能分辨。"
)

NEG_IMG = (
    "负向：人类、人手、手指、指甲、蛋壳、猫耳、天线、第二角色、文字、字幕、logo、水印、边框、"
    "心易的黑瞳、心易的瞳孔、心易的高光点、心易的眨眼、心易的眯眼、心易的闭眼、心易的笑眼、"
    "心易的弯眼、心易的眼褶、心易的眼皮、心易的眉毛、削皮器、刀、金属削皮器、"
    "橘子掉落、塑料高光、卡通描边、过饱和、广告打光、多个光源、夜景、冷蓝、比例失真。"
)

NEG_VID = (
    "负向：人类、人手、手指、指甲、牙齿、蛋壳、猫耳、天线、鎏金、粉蛋、第二角色、多余角色、"
    "文字、字幕、气泡、logo、水印、边框、心易的瞳孔、心易的黑瞳、心易的高光点、心易的眨眼、"
    "心易的眯眼、心易的闭眼、心易的笑眼、心易的弯眼、心易的眼褶、心易的眼皮、心易的眉毛、"
    "心易的眼睛大特写、削皮器、刀、金属削皮器、勺子、木勺、锅铲、勺头、土豆滚落、土豆掉地上、"
    "闭眼微笑、满足地闭眼、笑眯眼、"
    "多余手臂、第三只手、第四只手、多双手、多余的手、额外的手、手臂数量错误、四条手臂、四只手、腰侧的手、侧面的手、六条腿、"
    "锅盖盖着、锅盖合上、锅盖突然盖上、土豆凭空出现、土豆从空中出现、盐碟凭空出现、盐凭空出现、碟子突然出现、"
    "多颗土豆、三颗土豆、一堆土豆、土豆数量变化、"
    "火塘、石圈、平地上的火堆、锅放在地上、灶台消失、灶台变形、橘子掉落、橘子被吃、换水果、"
    "毛绒烧焦或熔化、塑料高光、卡通描边、过饱和、广告打光、多个光源、夜景、冷蓝、镜头切换、"
    "瞬移、变形、道具穿模、食材凭空出现、火未点即有火、成品摆盘、看向观众。"
)


def char_text(card):
    return "心易：" + card["character"]["height_line"] + "，" + CHAR_BODY


# ---------------- ID 与节点 ----------------
def hid(key, n=8, salt=""):
    return hashlib.md5((PREFIX + "|" + key + "|" + salt).encode("utf-8")).hexdigest()[:n]


def nid(key):
    return "node-" + hid(key)


def oid(key):
    return "output-" + hid(key, 10, "out")


def eid(a, b):
    return "edge-" + hid(a + ">" + b, 8, "edge")


def gid(label):
    return "group-" + hid(label, 8, "group")


def add_node(n):
    nodes.append(n)
    return n


def input_image(key, label, url, name, w, h, x, y, nw):
    nh = round(nw * h / w, 2)
    o = oid(key)
    add_node({
        "id": nid(key), "type": "input-image", "mainOutputId": o,
        "meta": {"x": float(x), "y": float(y), "width": float(nw), "height": float(nh),
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": o, "status": "done", "error": None, "value": url, "cover": None, "name": name,
            "resolution": {"width": w, "height": h}, "source": None, "batchId": None, "execution": None,
            "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_image(key, label, prompt, refs, x, y, nw, nh):
    add_node({
        "id": nid(key), "type": "gen-image", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": float(nw), "height": float(nh),
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
            "prompt": prompt,
            "reference_images": [{"node_id": nid(r)} for r in refs],
            "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 576,
            "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True}},
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_video(key, label, prompt, refs, duration, x, y):
    """全能参考：不挂首/尾帧槽，图只进 reference_images。"""
    add_node({
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 460.0, "height": 259.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": nid(r)} for r in refs],
            "reference_videos": [], "reference_audios": [],
            "first_frame_image": None, "last_frame_image": None,
            "resolution": "720p", "aspect_ratio": "16:9", "duration": duration,
            "seed": -1, "generate_audio": True, "watermark": False}},
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def input_text(key, label, text, x, y, nw, nh):
    o = oid(key)
    add_node({
        "id": nid(key), "type": "input-text", "mainOutputId": o,
        "meta": {"x": float(x), "y": float(y), "width": float(nw), "height": float(nh),
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": o, "status": "done", "error": None, "value": text, "cover": None, "name": label,
            "resolution": None, "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None, "executorRunId": None,
            "stage": None, "deletedAt": None, "createdAt": TS, "createdBy": BY,
            "updatedAt": TS, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def edge(src_key, dst_key):
    edges.append({
        "id": eid(nid(src_key), nid(dst_key)),
        "sourceNodeId": nid(src_key), "sourceHandle": "output",
        "targetNodeId": nid(dst_key), "targetHandle": "input",
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def wire(dst_key, refs):
    for r in refs:
        edge(r, dst_key)


def group(label, keys, color):
    groups.append({"label": label, "keys": keys, "color": color})


def tk(key):
    return "{{" + nid(key) + "}}"


# ---------------- 校验 ----------------
def validate_card(card):
    errs = []
    for k in ("ep", "dish", "series_title", "canvas_name", "character", "areas", "props", "segments", "post"):
        if not card.get(k):
            errs.append(f"缺少字段 {k}")
    if errs:
        raise SystemExit("等菜卡校验失败：\n - " + "\n - ".join(errs))
    areas = {a.get("key"): a for a in card["areas"]}
    if len(areas) != 4:
        errs.append(f"必须 4 个台地，当前 {len(areas)}")
    for k, a in areas.items():
        for f in ("name", "desc", "layout", "props_here"):
            if not a.get(f):
                errs.append(f"台地 {k} 缺 {f}")
    if len(card["segments"]) != 4:
        errs.append(f"必须 4 段，当前 {len(card['segments'])}")
    for s in card["segments"]:
        if s.get("duration") != 15:
            errs.append(f"{s.get('key')} 时长必须是 15s")
        if s.get("area") not in areas:
            errs.append(f"{s.get('key')} 的台地 {s.get('area')} 不在 areas 里")
        if not s.get("sound"):
            errs.append(f"{s.get('key')} 缺 sound")
        beats = s.get("beats", [])
        if len(beats) != 3:
            errs.append(f"{s.get('key')} 必须 3 拍，当前 {len(beats)}")
        elif [b.get("kind") for b in beats][:2] != ["action", "action"] or beats[2].get("kind") not in ("action", "hold"):
            errs.append(f"{s.get('key')} 的拍子必须是 action/action/(action 或 hold)")
        for b in beats:
            if not b.get("t") or not b.get("text"):
                errs.append(f"{s.get('key')} 有 beat 缺 t/text")
    subs = [x for s in card["segments"] for x in s.get("subs", [])]
    if len(subs) > 8:
        errs.append(f"字幕 {len(subs)} 条，超过 8 条")
    kabo = card["post"].get("kabo", [])
    if not (2 <= len(kabo) <= 4):
        errs.append(f"咔啵 {len(kabo)} 声，应为 2–4 声")
    if card.get("tail_refs") and not card.get("placeholder"):
        errs.append("tail_refs=true 时必须给 placeholder（尾帧占位图）")
    if errs:
        raise SystemExit("等菜卡校验失败：\n - " + "\n - ".join(errs))


# ---------------- 提示词 ----------------
def scene_prompt(area):
    return (
        "16:9 场景设定空景，不出现任何角色、不出现手。"
        + area["desc"] + "\n" + area["layout"] + "\n"
        + SCALE + "\n" + LIGHT + "\n"
        "画面要唯美：浅景深、一层薄雾、光里有浮尘、石头与器物表面有湿润感；"
        "只有必须的东西，没有现代电器、不锈钢、塑料收纳盒、杂物堆。\n"
        "参考图：" + tk("a0") + " 只用于确认她的身量比例，画面里不出现角色。\n"
        "无文字、无 logo、无水印。\n" + NEG_IMG
    )


def prop_prompt(p):
    return (
        "纯白底道具图，只出现一件物品，不出现角色、不出现手。" + p["body"] + "\n"
        "正面微侧、居中构图、完整入画，柔和顶光，物品下方有自然的接触阴影；真实自然材质，不塑料、不卡通。\n"
        "无文字、无 logo、无水印、无边框。\n" + NEG_IMG
    )


def grid_prompt(card):
    cells = []
    for s in card["segments"]:
        area = next(a for a in card["areas"] if a["key"] == s["area"])
        name = area["name"]
        text = s["beats"][1]["text"]
        area2 = s.get("area2")
        if area2:
            a2 = next(a for a in card["areas"] if a["key"] == area2)
            prefix = "切到" + a2["name"] + "："
            if text.startswith(prefix):
                text = text[len(prefix):]
            name = a2["name"]
        cells.append(f"{name}：{text}")
    return (
        "两列两行四宫格分镜预演图，细白分隔线，16:9 整体画幅；四格按左上→右上→左下→右下阅读：\n"
        + "\n".join(f"第 {i+1} 格：{c}。" for i, c in enumerate(cells)) + "\n"
        "四格同一角色、同一晨雾与暖白逆光；同一毛色、同一颗橘子；不出现人类，格内不写任何文字或编号。\n"
        "参考图：" + tk("a0") + "=角色外观；" + tk("a0f") + "=眼睛；"
        + "；".join(tk(f"s{i+1}") + "=" + a["name"] for i, a in enumerate(card["areas"])) + "。\n"
        + char_text(card) + "\n" + EYE + "\n" + SCALE + "\n" + LIGHT + "\n" + NEG_IMG
    )


def k_prompt(card, i, prop_keys):
    s = card["segments"][i]
    area = next(a for a in card["areas"] if a["key"] == s["area"])
    first = s["beats"][0]["text"]
    prop_txt = "；".join(
        tk(k) + "=" + next(p["label"] for p in card["props"] if p["key"] == k).replace(" · 白底", "")
        for k in prop_keys
    )
    area2 = s.get("area2")
    area2_line = ""
    if area2:
        a2 = next(a for a in card["areas"] if a["key"] == area2)
        area2_line = "本段开场在" + area["name"] + "；第二镜切到" + a2["name"] + "。\n"
    area_idx = [a["key"] for a in card["areas"]].index(area["key"]) + 1
    return (
        "16:9 横屏电影感开场画面，只生成一张。第 0 秒：" + first + "。\n"
        "场景：" + area["desc"] + "\n" + area["layout"] + area2_line
        + char_text(card) + "\n" + EYE + "\n" + SCALE + "\n" + LIGHT + MATERIAL + "\n"
        "构图：低机位、浅景深、晨雾逆光；她约占画面高四分之一（中景可到三分之一）；画面里只有她。\n"
        "参考图：" + tk("a0") + "=角色外观；" + tk("a0f") + "=眼睛；" + tk(f"s{area_idx}") + "=场景与光；"
        + tk("g1") + f"=四格预演第 {i+1} 格（只取构图，不出现分格线）；" + prop_txt + "。\n"
        "无文字、无 logo、无水印。\n" + NEG_IMG
    )


def beats_text(seg):
    return "\n".join(f"{b['t']}：{b['text']}。" for b in seg["beats"])


def v_prompt(card, i):
    s = card["segments"][i]
    area = next(a for a in card["areas"] if a["key"] == s["area"])
    area2 = s.get("area2")
    scene_block = area["desc"] + "\n" + area["layout"]
    extra_ref = ""
    if area2:
        a2 = next(a for a in card["areas"] if a["key"] == area2)
        idx = [a["key"] for a in card["areas"]].index(area2) + 1
        scene_block += "\n第二镜切到" + a2["name"] + "：" + a2["desc"] + "\n" + a2["layout"]
        extra_ref = "；" + tk(f"s{idx}") + "＝第二镜的" + a2["name"]
    tail_ref = ""
    tail_task = ""
    if card.get("tail_refs") and i > 0:
        tail_ref = "；" + tk(f"t{i}") + "＝上一段最后一帧（只取她的毛色、光向、道具状态，不取构图）"
        tail_task = "上一段尾帧只用于对齐角色与光，构图仍以 " + tk(f"k{i+1}") + " 为准。"
    return (
        "【全能参考】参考图依次是：" + tk(f"k{i+1}") + "＝本段开场构图（" + area["name"]
        + "，低机位、晨雾逆光、她的位置与道具状态）；"
        + tk("a0") + "＝心易外观；" + tk("a0f") + "＝眼睛" + extra_ref + tail_ref + "。\n"
        "【任务】以 " + tk(f"k{i+1}") + " 的机位、构图、光线与开场状态为准；第 0 秒尽量与参考一致，"
        "不要重新构图、不要换机位。" + tail_task + "\n"
        "【角色】" + char_text(card) + "\n" + EYE + "\n"
        "【场景与尺度】" + scene_block + "\n" + SCALE + "\n"
        "【光与材质】" + LIGHT + MATERIAL + "\n"
        "【时间拍】\n" + beats_text(s) + "\n"
        "【镜头】本段 15 秒 3 个镜头，秒数按【时间拍】，不平均分；切点落在动作完成后，不切在动作中间；低机位、浅景深、逆光。\n"
        "【声音】" + s["sound"] + "。\n"
        "【字幕】本段不生成任何字幕；画面里不出现文字、竖排白字、气泡、水印。\n"
        + NEG_VID
    )


# ---------------- 组装 ----------------
def s0_text(card):
    return (
        "【本画布】《等一下》" + card["ep"] + "《" + (card.get("title") or card["dish"]) + "》60 秒＝4 段×15 秒："
        "取 → 理 → 火 → 吃；一坡四台（菜园／溪／灶／汤池），晨雾逆光。\n"
        "参考：菇子柒／秃秃做饭系列——取→理→火→分、约 5 秒一拍、角色不说话、环境声打底、白字压主体。\n\n"
        "【跑序】01 场景（4 张，可同跑）→ 02 道具（4 件，并行）→ 03 四格（定稿）→ 04 K1–K4 → 05 V1 → 06 V2 → 07 V3 → 08 V4。\n\n"
        "【纪律】\n"
        "1. 先只跑 V1（取），看晨雾、逆光、拔秧和土豆滚下坡成不成立；不要一键全跑。\n"
        "2. 段与段是硬切（换台地），不用尾帧链；每段以自己那张 K 为开场参考。\n"
        "3. 四条视频都是全能参考（_reference_way=reference），不挂首/尾帧槽。\n"
        "4. 视频里无字、无气泡；白字竖排（菇子柒式）与咔啵全部后期。\n"
        "5. T1–T3 是上一段尾帧的**第二参考**：跑完 V1 截最后一帧替换 T1 再跑 V2；没换之前不要跑 V2/V3/V4。构图仍以各自的 K 为准，T 只取角色/光/道具。\n\n"
        "【角色】水豚心易：只发咔啵、不说话；头顶橘子是本体；短手无指，用木棍。"
        "眼睛是白片＋深棕圈、中心空白，不眨眼、不眯眼；情绪靠身体。\n"
        "【声音】咔啵后期配（约 8s「咔啵！」、约 42s「咔——啵」、约 57s「咔啵~」）；视频里不要台词、不要音乐。\n"
        "【字幕】后期白字竖排 7 条：一窝／洗洗／埋进去／等一下／好了／面／烫；尾卡「非教程 仅供娱乐」。\n\n"
        "【改法】改等菜卡 JSON 后重跑 build_from_slope.py，不手改 .monet。"
    )


def build(card, out):
    validate_card(card)
    ch = card["character"]

    input_image("a0", ch["label"], ch["ref_url"], ch["ref_name"], ch["ref_w"], ch["ref_h"], 0, 0, 300)
    input_image("a0f", ch["face_label"], ch["face_url"], ch["face_name"],
                ch["face_w"], ch["face_h"], 0, 480, 300)
    input_text("s0", "S0 制作说明 · 先读", s0_text(card), 0, 1040, 320, 760)

    # 01 场景
    for i, a in enumerate(card["areas"]):
        gen_image(f"s{i+1}", f"【待生成】S{i+1} 场景 · {a['name']} · 晨雾 · 16:9 空景",
                  scene_prompt(a), ["a0"], 360, i * 300, 460, 259)
        edge("a0", f"s{i+1}")

    # 02 道具
    for i, p in enumerate(card["props"]):
        gen_image(p["key"], "【待生成】" + p["label"], prop_prompt(p), [], 900, i * 240, 380, 214)

    # 02b 尾帧参考（第二参考，不是首帧）
    if card.get("tail_refs"):
        ph = card["placeholder"]
        for j in range(1, 4):
            input_image(
                f"t{j}",
                f"T{j}【待替换⚠】V{j} 尾帧 → V{j+1} 第二参考（截 V{j} 最后一帧替换；只取角色/光，不取构图）",
                ph["url"], ph["name"], ph["w"], ph["h"], 900, 1000 + (j - 1) * 280, 440)

    # 03 四格
    gen_image("g1", "【待生成】G1 四格预演 · 取/理/火/吃", grid_prompt(card),
              ["a0", "a0f", "s1", "s2", "s3", "s4"], 1400, 0, 520, 293)
    wire("g1", ["a0", "a0f", "s1", "s2", "s3", "s4"])

    # 04 参考帧 K1–K4
    k_refs = [
        ["a0", "a0f", "s1", "g1", "p1"],
        ["a0", "a0f", "s2", "g1", "p1"],
        ["a0", "a0f", "s3", "g1", "p1", "p3"],
        ["a0", "a0f", "s4", "g1", "p2", "p4"],
    ]
    k_props = [["p1"], ["p1"], ["p1", "p3"], ["p2", "p4"]]
    for i in range(4):
        gen_image(f"k{i+1}", f"【参考帧】K{i+1} V{i+1} 开场 · {card['segments'][i]['title']}",
                  k_prompt(card, i, k_props[i]), k_refs[i], 1400, 340 + i * 300, 440, 248)
        wire(f"k{i+1}", k_refs[i])

    # 05–08 视频
    for i in range(4):
        key = f"v{i+1}"
        refs = [f"k{i+1}", "a0", "a0f"]
        area2 = card["segments"][i].get("area2")
        if area2:
            idx = [a["key"] for a in card["areas"]].index(area2) + 1
            refs.append(f"s{idx}")
        if card.get("tail_refs") and i > 0:
            refs.append(f"t{i}")
        gen_video(key, f"【待生成】V{i+1} {card['segments'][i]['title']} · 15s · 全能参考",
                  v_prompt(card, i), refs, 15, 1960, i * 320)
        wire(key, refs)

    # 组
    refs = {"a0", "a0f"}
    group("00 参考 · 角色与眼睛", ["a0", "a0f"], "#E68BB3")
    group("01 场景 · 四台地 · 可同跑", [f"s{i+1}" for i in range(4)], "#8E8DE0")
    group("02 道具白底 · 并行", [p["key"] for p in card["props"]], "#7FB07F")
    group("03 四格预演 · 定稿后再往下", ["g1"], "#E8B85D")
    group("04 参考帧 K1–K4", [f"k{i+1}" for i in range(4)], "#6FA8DC")
    for i in range(4):
        group(card.get("group_labels", {}).get(f"v{i+1}", f"0{5+i} V{i+1} · {card['segments'][i]['title']}"),
              [f"v{i+1}"], "#DC775D")
    group("09 说明 · 先读", ["s0"], "#9A9A9A")
    if card.get("tail_refs"):
        group("10 尾帧参考 · 跑完上一段再换", ["t1", "t2", "t3"], "#B08BBB")

    # 节点状态标注（如【必重跑】【已生成·保留】）
    for k, pref in (card.get("label_prefix") or {}).items():
        n = next((x for x in nodes if x["id"] == nid(k)), None)
        if n:
            n["meta"]["label"] = pref + re.sub(r"^【[^】]*】", "", n["meta"]["label"])
    for k, lab in (card.get("label_overrides") or {}).items():
        n = next((x for x in nodes if x["id"] == nid(k)), None)
        if n:
            n["meta"]["label"] = lab

    out_groups = finalize_groups()
    canvas = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": TS,
        "canvas": {
            "name": card["canvas_name"],
            "description": card["description"],
            "nodes": nodes, "edges": edges, "groups": out_groups,
        },
    }

    problems = self_check(canvas)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {out}: {len(nodes)} 节点 / {len(edges)} 边 / {len(out_groups)} 组")
    for n in nodes:
        if n["type"] == "gen-video":
            print(f"  {n['meta']['label']}: {len(n['params']['model_params']['prompt'])} 字符 / "
                  f"{n['params']['model_params']['duration']}s")
    if problems:
        print("自检失败：")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("自检通过")


def finalize_groups():
    by_id = {n["id"]: n for n in nodes}
    out = []
    for g in groups:
        ns = [by_id[nid(k)] for k in g["keys"]]
        pad = 20
        x0 = min(n["meta"]["x"] for n in ns) - pad
        y0 = min(n["meta"]["y"] for n in ns) - pad
        x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
        y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
        out.append({
            "id": gid(g["label"]), "nodeIds": [n["id"] for n in ns],
            "bounds": {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0},
            "label": g["label"],
            "style": {"accent": None, "opacity": None, "borderColor": g["color"]},
            "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
        })
    return out


def self_check(canvas):
    problems = []
    ns, es, gs = canvas["canvas"]["nodes"], canvas["canvas"]["edges"], canvas["canvas"]["groups"]
    by_id = {n["id"]: n for n in ns}
    seen = set()
    for e in es:
        key = (e["sourceNodeId"], e["targetNodeId"])
        if key in seen:
            problems.append(f"重复边 {key}")
        seen.add(key)
        s, t = by_id.get(e["sourceNodeId"]), by_id.get(e["targetNodeId"])
        if not s or not t:
            problems.append(f"边端点不存在 {key}")
            continue
        if s["type"] == "gen-video" and t["type"] == "gen-video":
            problems.append(f"video→video 边 {key}")
    for n in ns:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        prompt = mp.get("prompt", "")
        refs = [r["node_id"] for r in mp.get("reference_images", [])]
        tokens = set(re.findall(r"\{\{(node-[^\}]+)\}\}", prompt))
        for t in tokens:
            if t not in by_id:
                problems.append(f"{n['id']}: token 无节点 {t}")
            if t not in refs:
                problems.append(f"{n['id']}: token {t} 没挂引用")
        for r in refs:
            if r not in by_id:
                problems.append(f"{n['id']}: 引用不存在 {r}")
            if (r, n["id"]) not in seen:
                problems.append(f"{n['id']}: 引用 {r} 没有连线")
            if by_id[r]["type"] == "input-image" and not by_id[r].get("outputs"):
                problems.append(f"{n['id']}: 引用了没有输出的 input-image {r}")
        if n["type"] == "gen-video":
            if mp.get("first_frame_image") or mp.get("last_frame_image"):
                problems.append(f"{n['id']}: 全能参考模式不应挂首/尾帧槽")
            if mp.get("_reference_way") != "reference":
                problems.append(f"{n['id']}: _reference_way 必须是 reference")
        if len(prompt) > 2000:
            problems.append(f"{n['id']}: prompt {len(prompt)} 字符超过 2000")
    for i, g in enumerate(gs):
        b = g["bounds"]
        for h in gs[i + 1:]:
            c = h["bounds"]
            if (b["x"] < c["x"] + c["width"] and c["x"] < b["x"] + b["width"]
                    and b["y"] < c["y"] + c["height"] and c["y"] < b["y"] + b["height"]):
                problems.append(f"组重叠：{g['label']} / {h['label']}")
        for nid_ in g["nodeIds"]:
            m = by_id[nid_]["meta"]
            if not (b["x"] <= m["x"] and m["x"] + m["width"] <= b["x"] + b["width"]
                    and b["y"] <= m["y"] and m["y"] + m["height"] <= b["y"] + b["height"]):
                problems.append(f"节点 {nid_} 超出组 {g['label']}")
    grouped = {n for g in gs for n in g["nodeIds"]}
    for n in ns:
        if n["id"] not in grouped:
            problems.append(f"节点不在任何分组 {n['id']}")
    return problems


def main():
    ap = argparse.ArgumentParser(description="等菜卡 → Monet 画布（四段版）")
    ap.add_argument("card", help="等菜卡 JSON")
    ap.add_argument("-o", "--out", default=None, help="输出 .monet")
    args = ap.parse_args()
    card_path = Path(args.card)
    card = json.loads(card_path.read_text(encoding="utf-8-sig"))
    out = Path(args.out) if args.out else card_path.parent / f"{card['ep']}-{card['dish']}-v1.monet"
    build(card, out)


if __name__ == "__main__":
    main()
