# -*- coding: utf-8 -*-
"""等菜卡 → Monet 画布生成器（心易做菜《等一下》）

用法：
    py -3 build_from_wait.py recipes/EP01-等红薯熟.json [-o EP01-等红薯熟-v1.monet]

固定结构（不跟菜改）：
    30 s = V1 15 s「等」 + V2 12 s「成」 + V3 3 s「泡」
    一个景、两个机位、三次生成；视频内无字，白字与咔啵后期。

组＝跑序：
    00 参考 → 01 场景 → 02 道具（并行）→ 03 四格预演 → 04 首帧 K1/K3
    → 05 V1 → 06 T1（截 V1 尾帧替换）→ 07 V2 → 08 V3 → 09 说明

自检不过直接退出，不产出坏文件。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TS = "2026-11-02T16:00:00.000+08:00"
BY = "libtv-workspace"
PREFIX = "xycook-01"

nodes, edges, groups = [], [], []


# ---------------- 角色与风格常量 ----------------
# 身高写在等菜卡 card["character"]["height_line"] 里，换尺度只改卡、不改脚本。
CHAR_BODY = (
    "圆身、无脖子、头身一体；暖棕短绒、"
    "绒毛方向可见、边缘有绒光；奶油色大脸板、白色圆形眼片＋外圈一条深棕细线、中心空白（无瞳孔、无高光点）、"
    "橘色腮红、一字嘴（不上扬）；白肚；棕色短手、无手指，圆脚、脚踝一圈奶油色；"
    "头顶一颗橘子带两片绿叶（本体：不可摘、不可吃、不可换成别的水果）。"
    "表情淡定，情绪只靠歪头、后仰、蹲、耳朵与身体；不看镜头、不卖萌、不拟人化眼神。"
)

# 跨项目规范（08_作品/_共享角色/心易/README.md）：白片＋棕圈、中心空白；不眨眼、不眯眼。
EYE = (
    "【心易眼睛·仅限心易】心易是毛绒玩具，眼睛是固定塑料/刺绣件，不是生物眼："
    "白色圆形眼片，中心没有黑色瞳孔；外圈一圈深棕色细描边；眼片中心保持空白，没有高光点；"
    "眼片形状、外圈深棕线、中心空白全程不变；不出现瞳孔/黑瞳/眼珠/虹膜/高光点；"
    "不眨眼、不眯眼、不抬眼皮、不皱眉、不闭眼；情绪只靠歪头/身体/手势/咔啵。"
)


def char_text(card):
    return "心易：" + card["character"]["height_line"] + "，" + CHAR_BODY


# 小世界的比例（抄秃秃那条的结论：锅盆比它大，工具按它身量配）
SCALE = (
    "尺度：这是一个为她配好的小世界——石灶高到她的胸口、灶口朝她开着；陶锅坐在灶上，"
    "锅沿高过她头顶一头；石池她坐得上去、两只脚泡得进去；木棍、陶碟、小勺按她身量配，"
    "她抱得动、够得着。锅盆可以比她大，但不要画成人类尺寸的巨物，也不要把世界缩成玩具模型。"
)

LIGHT = (
    "光：暮色冷蓝是环境光、灶口暖橙是唯一主光，两条光同一轴线；"
    "不打第三支灯、不加轮廓光、不加反光板。"
)

MATERIAL = (
    "材质：毛绒（短绒、绒光、压痕、沾灰变白）／粗陶（哑光、开片）／石头（湿、苔、水痕）／"
    "食物（焦皮、淀粉白、热气）四层要能分辨。"
)

NEG_IMG = (
    "负向：人类、人手、手指、指甲、蛋壳、猫耳、天线、第二角色、文字、字幕、logo、水印、边框、"
    "心易的黑瞳、心易的瞳孔、心易的高光点、心易的眨眼、心易的眯眼、心易的眼皮、心易的眉毛、"
    "橘子掉落、塑料高光、卡通描边、过饱和、广告打光、多个光源、比例失真。"
)

NEG_VID = (
    "负向：人类、人手、手指、指甲、牙齿、蛋壳、猫耳、天线、鎏金、粉蛋、第二角色、多余角色、"
    "文字、字幕、气泡、logo、水印、边框、心易的瞳孔、心易的黑瞳、心易的高光点、心易的眨眼、"
    "心易的眯眼、心易的眼皮、心易的眉毛、心易的眼睛大特写、橘子掉落、橘子被吃、换水果、"
    "毛绒烧焦或熔化、塑料高光、卡通描边、过饱和、广告打光、多个光源、镜头切换、瞬移、变形、"
    "道具穿模、食材凭空出现、火未点即有火、成品摆盘、看向观众。"
)


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
    """全能参考（_reference_way=reference）：不挂首帧/尾帧槽，图全部走 reference_images。

    2.0-mini 在 reference 模式下 first_frame/last_frame 本来就不生效（燕云 18 号文第 6 节）；
    把上一段最后一帧当参考图，是这条管线的正确写法。
    """
    add_node({
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 460.0, "height": 259.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": nid(r)} for r in refs],
            "reference_videos": [], "reference_audios": [],
            "first_frame_image": None,
            "last_frame_image": None,
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
    for k in ("ep", "dish", "wait", "type", "series_title", "canvas_name", "character",
              "placeholder", "scene", "props", "segments", "post"):
        if not card.get(k):
            errs.append(f"缺少字段 {k}")
    if errs:
        raise SystemExit("等菜卡校验失败：\n - " + "\n - ".join(errs))
    segs = card["segments"]
    if [s.get("duration") for s in segs] != [15, 12, 3]:
        errs.append(f"三段时长必须是 15/12/3，当前 {[s.get('duration') for s in segs]}")
    for s in segs:
        if not s.get("sound"):
            errs.append(f"{s.get('key')} 缺 sound")
        if not s.get("beats"):
            errs.append(f"{s.get('key')} 缺 beats")
        for b in s.get("beats", []):
            if not b.get("t") or not b.get("text"):
                errs.append(f"{s.get('key')} 有 beat 缺 t/text")
    subs = [x for s in segs for x in s.get("subs", [])]
    if len(subs) > 4:
        errs.append(f"字幕 {len(subs)} 条，超过 4 条")
    kabo = card["post"].get("kabo", [])
    if not (2 <= len(kabo) <= 3):
        errs.append(f"咔啵 {len(kabo)} 声，应为 2–3 声")
    if len(card["props"]) != 3:
        errs.append("道具必须是 3 件（P1/P2/P3）")
    if errs:
        raise SystemExit("等菜卡校验失败：\n - " + "\n - ".join(errs))


# ---------------- 提示词 ----------------
def scene_prompt(card):
    sc = card["scene"]
    return (
        "16:9 场景设定空景，不出现任何角色、不出现手。"
        + sc["desc"] + "\n"
        "构图：灶在画面左半、池在右后，灶前留出一块能站下她的空地；画面里没有角色。\n"
        + SCALE + "\n" + LIGHT + "\n"
        "材质：粗陶（哑光、开片）／石头（湿、苔、水痕）／老木（纹理、包浆）／水汽与灰，四种要能分辨。\n"
        "画面要唯美：浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；"
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
    return (
        "两列两行四宫格分镜预演图，细白分隔线，16:9 整体画幅；四格按左上→右上→左下→右下阅读：\n"
        "左上（第一格）：她蹲在灶口，用木棍把红薯推进红灰，火星溅起。\n"
        "右上（第二格）：她蹲着看灰，火光在侧脸跳，烟升起。\n"
        "左下（第三格）：她两只手抱住掰开的红薯，黄瓤、白气。\n"
        "右下（第四格）：池边她坐着，两只脚泡在水里，捧着半个红薯。\n"
        "四格同一角色、同一场景、同一黄昏光；同一毛色、同一颗橘子；不出现人类，格内不写任何文字或编号。\n"
        "参考图：" + tk("a0") + "=角色外观；" + tk("a0f") + "=眼睛；" + tk("s1") + "=场景与光；"
        + tk("p1") + "=生红薯；" + tk("p2") + "=熟红薯；" + tk("p3") + "=木棍。\n"
        + char_text(card) + "\n" + EYE + "\n" + SCALE + "\n" + LIGHT + "\n" + NEG_IMG
    )


def k1_prompt(card):
    return (
        "16:9 横屏电影感开场画面，只生成一张。低机位：前景是石缝里的木棍（大、清晰、带灰），"
        "后景是灶口与她（全身、略虚、被火光勾边），灶台边一颗带泥红薯；黄昏的温泉小院一角，"
        "左侧石灶、右后石池冒白气、水面浮一片橘子。她站直约占画面高四分之一。\n"
        + char_text(card) + "\n" + EYE + "\n" + SCALE + "\n" + LIGHT + MATERIAL + "\n"
        "参考图：" + tk("a0") + "=角色外观；" + tk("a0f") + "=眼睛；" + tk("s1") + "=场景与光；"
        + tk("p1") + "=生红薯；" + tk("p3") + "=木棍；" + tk("g1") + "=四格预演第一格（只取构图，不出现分格线）。\n"
        "无文字、无 logo、无水印；画面干净。\n" + NEG_IMG
    )


def k3_prompt(card):
    return (
        "16:9 横屏电影感收尾画面，只生成一张。机位在池边、回看灶口："
        "画面左前是灶沿与插回石缝的木棍，右侧池沿上她坐着，两只脚泡在水里，"
        "两只短手把半个红薯捧在胸前、切面朝镜头；水面浮一片橘子，蒸汽向上略偏右。中景，她约占画面高三分之一；"
        "暮色为主、水面反一点暖光，灶口只剩余火。\n"
        + char_text(card) + "\n" + EYE + "\n" + SCALE + "\n" + MATERIAL + "\n"
        "参考图：" + tk("a0") + "=角色外观；" + tk("a0f") + "=眼睛；" + tk("s1") + "=同一景；"
        + tk("p2") + "=熟红薯；" + tk("p3") + "=木棍；" + tk("g1") + "=四格预演第四格（只取构图）。\n"
        "无文字、无 logo、无水印。\n" + NEG_IMG
    )


def beats_text(seg):
    return "\n".join(f"{b['t']}：{b['text']}。" for b in seg["beats"])


def v1_prompt(card):
    seg = card["segments"][0]
    return (
        "【全能参考】参考图依次是：" + tk("k1") + "＝开场构图（低机位、前景石缝里的木棍、后景灶口与她、灶台边一颗带泥红薯）；"
        + tk("a0") + "＝心易外观；" + tk("a0f") + "＝眼睛。\n"
        "【任务】以 " + tk("k1") + " 的机位、构图、光线与道具状态为准开场；第 0 秒尽量与参考一致，"
        "不要重新构图、不要换机位。\n"
        "【角色】" + char_text(card) + "\n" + EYE + "\n"
        "【场景与尺度】黄昏温泉小院一角：石灶在左、石池在右后，暮色冷蓝与灶火暖橙。" + SCALE + "\n"
        "【光与材质】" + LIGHT + MATERIAL + "\n"
        "【时间拍】\n" + beats_text(seg) + "\n"
        "【镜头】全程一个镜头，极缓慢推近约 5%，不切、不摇、不环绕；动作慢半拍、落点准。"
        "最后两秒完全静止，只有烟与水汽在动；镜头停住、画面稳定不抖。\n"
        "【声音】" + seg["sound"] + "；不要人声、不要配乐。\n"
        "【字幕预留】后期白字「" + "」「".join(seg["subs"]) + "」；画面里不出现任何文字、气泡、水印。\n"
        + NEG_VID
    )


def v2_prompt(card):
    seg = card["segments"][1]
    return (
        "【全能参考】参考图依次是：" + tk("t1") + "＝上一段最后一帧（同一机位、同一蹲姿、同一灰堆、同一火光）；"
        + tk("a0") + "＝外观；" + tk("a0f") + "＝眼睛。\n"
        "【任务】接着 " + tk("t1") + " 的状态往下走：第 0 秒的机位、她的姿态、灰堆与火光尽量与参考一致，"
        "只让烟与水汽动；不要重新构图、不要换机位。\n"
        "【角色】" + char_text(card) + "\n" + EYE + "\n"
        "【场景与尺度】同一景：黄昏温泉小院一角。" + SCALE + "\n"
        "【光与材质】" + LIGHT + MATERIAL + "\n"
        "【时间拍】\n" + beats_text(seg) + "\n"
        "【镜头】与 V1 同机位；不切、不摇；动作慢半拍。"
        "最后 1 秒把红薯举到胸前、切面朝镜头、眼睛半闭，保持住，不吃完、不放下。\n"
        "【声音】" + seg["sound"] + "；不要人声、不要配乐。\n"
        "【字幕预留】后期白字「" + "」「".join(seg["subs"]) + "」；画面里不出现任何文字、气泡、水印。\n"
        + NEG_VID
    )


def v3_prompt(card):
    seg = card["segments"][2]
    return (
        "【全能参考】参考图依次是：" + tk("k3") + "＝收尾构图（池边回看灶口：左前灶沿与木棍、"
        "右侧她坐在池沿、两只脚泡在水里、两只短手把半个红薯捧在胸前切面朝镜头、水面浮橘子、蒸汽向上略偏右）；"
        + tk("s1") + "＝同一景；" + tk("p2") + "＝熟红薯；" + tk("a0") + "＝外观；" + tk("a0f") + "＝眼睛。\n"
        "【任务】以 " + tk("k3") + " 的机位、构图与光线为准开场；第 0 秒尽量与参考一致，"
        "不要重新构图、不要换机位。\n"
        "【角色】" + char_text(card) + "全身放松、肩膀下沉。\n" + EYE + "\n"
        "【场景与尺度】同一石池边；中景，她约占画面高三分之一；暮色为主，水面反一点暖光，灶口只剩余火。\n"
        "【时间拍】\n" + beats_text(seg) + "\n"
        "【镜头】固定机位，只有蒸汽与水面在动；不切。\n"
        "【声音】" + seg["sound"] + "。\n"
        "【字幕预留】无字幕，只有后期尾卡「非教程 仅供娱乐」；画面里不出现任何文字、水印。\n"
        + NEG_VID
    )


# ---------------- 组装 ----------------
def s0_text(card):
    ph = card["placeholder"]
    return (
        "【本画布】《等一下》" + card["ep"] + "《" + card["dish"] + "》30 秒＝15 秒等 ＋ 12 秒成 ＋ 3 秒泡；"
        "16:9；一个景、两个机位、三次生成。\n"
        "这一集：" + card["wait"] + "（" + card["type"] + "）。\n\n"
        "【跑序】01 场景 → 02 道具（并行）→ 03 四格预演（定稿）→ 04 参考帧 K1/K3 → 05 V1（15s）"
        "→ 06 截 V1 最后一帧替换 T1 → 07 V2（12s）→ 08 V3（3s）。\n\n"
        "【模式】三条视频都是全能参考（_reference_way=reference）：不挂首帧/尾帧槽，图全部走参考图。"
        "2.0-mini 在 reference 模式下首尾帧本来就不生效；上一段最后一帧是被当参考图喂给 V2 的，不是首帧槽。\n\n"
        "【纪律】\n"
        "1. 先只跑 V1，看「一镜到底」成不成立；不要一键全跑。\n"
        "2. T1 没换之前不要跑 V2；T1 必须是 V1 的真实尾帧，不是重画的相似图。\n"
        "3. V3 不接 V2 尾帧（时间省略：她已挪到池边）；V2→V3 用匹配剪辑，见第 6 条。\n"
        "4. 视频里无字、无气泡；白字与咔啵全部后期。\n"
        "5. T1 截完先对检查表：蹲姿、灰堆没揭、木棍在、无火苗、无字；最后一帧糊了就往前退 0.2–0.5 秒（最后两秒是静止的，退一点不影响接）。\n"
        "6. V2 最后 1 秒要把红薯举到胸前、切面朝镜头；V3 开场是同一姿势、同一蒸汽方向（匹配剪辑）。对不上就后期加 0.2 秒叠化/白闪＋whoosh，不要硬切。\n\n"
        "【角色】水豚心易：只发咔啵、不说话；头顶橘子是本体，不摘不吃；短手无指，用木棍。"
        "眼睛是白片＋深棕圈、中心空白，不眨眼、不眯眼；情绪靠身体。\n"
        "【声音】咔啵后期配（约 12s「咔——啵」、约 26s「咔啵~」）；视频里不要台词、不要音乐。\n"
        "【字幕】后期白字 4 条：埋进去／等一下／好了／甜；尾卡「非教程 仅供娱乐」。\n\n"
        "【关于 T1 占位图】" + ph["note"] + "\n\n"
        "【改法】改等菜卡 JSON 后重跑 build_from_wait.py，不手改 .monet。"
    )


def build(card, out):
    validate_card(card)
    ch = card["character"]

    input_image("a0", ch["label"], ch["ref_url"], ch["ref_name"], ch["ref_w"], ch["ref_h"], 0, 0, 300)
    input_image("a0f", ch["face_label"], ch["face_url"], ch["face_name"],
                ch["face_w"], ch["face_h"], 0, 480, 300)
    input_image("t1",
                "T1【待替换⚠】V1 尾帧 → V2 参考（截 V1 最后一帧替换；占位图沿用记单词 T_A 版）",
                card["placeholder"]["url"], card["placeholder"]["name"],
                card["placeholder"]["w"], card["placeholder"]["h"], 900, 940, 440)
    input_text("s0", "S0 制作说明 · 先读", s0_text(card), 0, 1040, 320, 760)

    # 01 场景
    gen_image("s1", "【待生成】S1 场景 · 灶与池同框 · 黄昏 · 16:9 空景",
              scene_prompt(card), ["a0"], 360, 0, 460, 259)
    edge("a0", "s1")

    # 02 道具
    for i, p in enumerate(card["props"]):
        gen_image(p["key"], "【待生成】" + p["label"], prop_prompt(p), [], 380, 340 + i * 240, 380, 214)

    # 03 四格预演
    gen_image("g1", "【待生成】G1 四格预演 · 埋/等/成/泡", grid_prompt(card),
              ["a0", "a0f", "s1", "p1", "p2", "p3"], 860, 0, 520, 293)
    wire("g1", ["a0", "a0f", "s1", "p1", "p2", "p3"])

    # 04 首帧
    gen_image("k1", "【参考帧】K1 V1 开场 · 前景木棍 · 后景她", k1_prompt(card),
              ["a0", "a0f", "s1", "p1", "p3", "g1"], 900, 340, 440, 248)
    wire("k1", ["a0", "a0f", "s1", "p1", "p3", "g1"])

    gen_image("k3", "【参考帧】K3 V3 收尾 · 池边回看灶口", k3_prompt(card),
              ["a0", "a0f", "s1", "p2", "p3", "g1"], 900, 640, 440, 248)
    wire("k3", ["a0", "a0f", "s1", "p2", "p3", "g1"])

    # 05-08 视频（全部全能参考：图只走 reference_images，不挂首/尾帧槽）
    gen_video("v1", "【待生成】V1 等 · 15s · 一镜到底", v1_prompt(card),
              ["k1", "a0", "a0f"], 15, 1440, 0)
    wire("v1", ["k1", "a0", "a0f"])

    gen_video("v2", "【待生成】V2 成 · 12s · 参考 T1", v2_prompt(card),
              ["t1", "a0", "a0f"], 12, 1440, 300)
    wire("v2", ["t1", "a0", "a0f"])

    gen_video("v3", "【待生成】V3 泡 · 3s · 参考 K3", v3_prompt(card),
              ["k3", "s1", "a0", "a0f", "p2"], 3, 1440, 600)
    wire("v3", ["k3", "s1", "a0", "a0f", "p2"])

    # 组（bounds 之后统一算）
    group("00 参考 · 角色与眼睛", ["a0", "a0f"], "#E68BB3")
    group("01 场景 · 先跑", ["s1"], "#8E8DE0")
    group("02 道具白底 · 并行", ["p1", "p2", "p3"], "#7FB07F")
    group("03 四格预演 · 定稿后再往下", ["g1"], "#E8B85D")
    group("04 参考帧 K1/K3", ["k1", "k3"], "#6FA8DC")
    group("05 V1 · 先只跑这一条", ["v1"], "#DC775D")
    group("06 T1 尾帧占位 · 替换前不要跑 V2", ["t1"], "#B0B0B0")
    group("07 V2 · 首帧 T1", ["v2"], "#C97BA6")
    group("08 V3 · 硬切收尾", ["v3"], "#7FA8A0")
    group("09 说明 · 先读", ["s0"], "#9A9A9A")

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
    ap = argparse.ArgumentParser(description="等菜卡 → Monet 画布")
    ap.add_argument("card", help="等菜卡 JSON")
    ap.add_argument("-o", "--out", default=None, help="输出 .monet")
    args = ap.parse_args()
    card_path = Path(args.card)
    card = json.loads(card_path.read_text(encoding="utf-8-sig"))
    out = Path(args.out) if args.out else card_path.parent / f"{card['ep']}-{card['dish']}-v1.monet"
    build(card, out)


if __name__ == "__main__":
    main()
