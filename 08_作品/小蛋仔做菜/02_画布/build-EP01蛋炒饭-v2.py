# -*- coding: utf-8 -*-
"""《小蛋仔做菜》EP01《蛋炒饭》Monet 画布 v2 —— 16:9 / 30s / 2 段 × 15s / 蛋小粉。

v2 修正（2026-10-29 用户反馈）：
- 关键帧太多（v1 是 12 张）→ 现在 2 张，每段一张段首帧。
- 视频切得太碎（v1 是 12 段 × 2.5s）→ 现在 2 段 × 15s，每段 5 个镜头、每个 3 秒。
- 参考 W10 的做法：**一张网格分镜直接作为视频生成的参考输入**，模型在段内完成切镜。

结构：A0 角色 + S1 厨景 + P1–P5 道具 + G1/G2 六宫格 + K1/K2 段首帧 + V1/V2 十五秒段 + S0 说明。
自检：引用有边、无 video→video 边、组不重叠、节点不出组、Vidu prompt ≤ 2000 字符。
改提示词改本脚本重跑，不手改 .monet。
"""
import json
import random
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "EP01-蛋炒饭-v2.monet"
TS = "2026-10-29T16:00:00.000+08:00"
BY = "libtv-workspace"

STO = "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image"
REF_FEN = f"{STO}/20261022-035437-0d34f1caae5e8c3e-e8-a7-92-e8-89-b2-e7-b2-89-e8-9b-8b-e6-a.jpg"

CHAR = ("蛋小粉：一只约 12 厘米高的粉色搪胶蛋仔，圆形蛋身、正面一片奶油色椭圆脸盘、绿色星星眼、细弯眉、小嘴、粉色圆腮、"
        "头顶一根带小圆球的粉色触角、短圆手臂、白色小袜靴；外观严格照参考图，不增不减不变色，无人类五官、无手指、无衣物")
SCALE = "所有厨具都是正常人类尺度，比它大很多：锅径约等于它身高的二十倍；画面里必须有一件东西能对照出它的身高"
SCENE = ("场景：人类出租屋的小厨房，木质台面、旧瓷砖墙，右侧窗户透进清晨的光；台面上有白瓷碗、黑铁锅、木砧板；"
         "背景干净、浅景深、有生活痕迹但不是样板间")
TONE = "基调：熟练、安静、专业；它是有手艺的小厨师，动作利落不狼狈；可爱来自体型与手艺的反差，不来自失误"
NEG_IMG = ("负向：人类、手指、毛发、卡通扁平渲染、塑料玩具感、比例失真、角色复制、第二只蛋仔、道具重复、文字、水印、logo、"
           "边框、过曝、广告打光、两个光源。")
NEG_VID = ("负向：人类、手指、多余角色、第二只蛋仔、卡通扁平、塑料玩具感、比例失真、瞬移、变形、角色复制、道具复制、字幕、"
           "文字、水印、BGM旋律、说话、镜头旋转、镜头漂移、翻车动作、鬼畜重复。")

nodes, edges, groups = [], [], []


def rid(prefix):
    return f"{prefix}-{random.getrandbits(32):08x}"


def add_node(node):
    nodes.append(node)
    return node


def input_image(nid, label, url, name, w, h, x, y, nw, nh):
    oid = f"output-{random.getrandbits(32):08x}"
    add_node({
        "id": nid, "type": "input-image", "mainOutputId": oid,
        "meta": {"x": x, "y": y, "width": nw, "height": float(nh), "label": label, "resourceType": None},
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": url, "cover": None, "name": name,
            "resolution": {"width": w, "height": h}, "source": None, "batchId": None, "execution": None,
            "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
            "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_image(nid, label, prompt, refs, x, y, nw=320, nh=207):
    add_node({
        "id": nid, "type": "gen-image", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": float(nw), "height": float(nh), "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1, "model_id": "gpt-image-2",
            "model_params": {
                "prompt": prompt,
                "reference_images": [{"node_id": r} for r in refs],
                "aspect_ratio": "16:9",
                "image_size": "1K",
                "width": 1024, "height": 576,
                "quality": "medium", "output_format": "png",
                "moderation": "low", "auto_compress": True,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_video(nid, label, prompt, first_frame, refs, duration, x, y):
    add_node({
        "id": nid, "type": "gen-video", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": 360.0, "height": 240.0, "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1, "model_id": "vidu-q4-preview",
            "model_params": {
                "prompt": prompt,
                "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in refs],
                "reference_audios": [],
                "first_frame_image": {"node_id": first_frame},
                "resolution": "720p", "aspect_ratio": "16:9",
                "duration": duration, "generate_audio": True, "watermark": False,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def input_text(nid, label, text, x, y, nw, nh):
    oid = f"output-{random.getrandbits(32):08x}"
    add_node({
        "id": nid, "type": "input-text", "mainOutputId": oid,
        "meta": {"x": x, "y": y, "width": float(nw), "height": float(nh), "label": label, "resourceType": None},
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": text, "cover": None, "name": label,
            "resolution": None, "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None, "executorRunId": None, "stage": None,
            "deletedAt": None, "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
            "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def edge(src, dst):
    edges.append({
        "id": rid("edge"), "sourceNodeId": src, "sourceHandle": "output",
        "targetNodeId": dst, "targetHandle": "input",
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


# ---------- 参考 ----------
N_A0 = "node-a0fendan"
input_image(N_A0, "A0 蛋小粉标准（已上传·复用四小只）", REF_FEN, "角色-粉蛋-标准.jpg", 1305, 1495, 0, 0, 300, 345)

# ---------- 说明 ----------
N_S0 = "node-s0readme"
S0_TEXT = (
    "【本画布做什么】\n"
    "《小蛋仔做菜》EP01《蛋炒饭》v2：16:9、30 秒＝2 段 × 15 秒，每段 5 个镜头、每个 3 秒。\n"
    "厨师＝蛋小粉；基调＝熟练不滑稽。\n\n"
    "【v2 相对 v1 改了什么】\n"
    "v1 是 12 张关键帧 + 12 段 2.5 秒，切得太碎、图太多。v2 回到 W10 的做法：\n"
    "一、每段只有一张段首帧（关键帧 12→2）；\n"
    "二、每段一张六宫格分镜，**直接作为视频生成的参考输入**，段内切镜交给模型；\n"
    "三、一段 15 秒，段内 5 个镜头（3 秒一个），不再 2.5 秒一切。\n\n"
    "【跑序】\n"
    "01 厨景 → 02 道具（可并行）→ 03 两张六宫格（审核定稿）→ 04 K1/K2 段首帧 → 05 V1/V2 十五秒段。\n"
    "网格没定稿不要跑段首帧；段首帧没定稿不要跑视频。\n\n"
    "【风险，先跑 V1 验证】\n"
    "本库 I06 记录过「多宫格图片直接接视频会干扰构图」。那是因为早期把它当首帧用；\n"
    "这里是当 reference_images（参考），首帧仍是单张 K。仍属未验证组合——**先只跑 V1 一条**，看段内切点是否干净，再决定 V2 和后续集数。\n"
    "若段内切点失控，退路是：仍按 15 秒交付，但拆成 3 段 5 秒生成，切点 6 个（退化成本约 +4 次派发）。\n\n"
    "【改法】\n"
    "改提示词请改 build-EP01蛋炒饭-v2.py 后重跑，不手改 .monet。"
)
input_text(N_S0, "S0 制作说明 · 先读", S0_TEXT, 0, 400, 320, 780)

# ---------- 场景与道具 ----------
N_S1 = "node-s1kitchen"
gen_image(
    N_S1, "【待生成】S1 厨房台面 · 清晨空景 · 16:9",
    "16:9 场景设定空景，不出现任何角色。人类出租屋的小厨房：木质台面占据画面下方，台面上靠墙放着一只白瓷碗、一口黑铁锅"
    "（锅径约是蛋仔身高的二十倍）、一块木砧板；右侧旧瓷砖墙上有一扇窗，清晨的光斜进来照在台面上；"
    "背景有用了很久的痕迹：瓷砖缝、木台面的刀痕、墙上的挂钩，但不是样板间，也不脏乱。\n"
    f"{SCALE}。画面干净、浅景深、真实光影、有生活痕迹，不摆拍、不广告打光。\n"
    f"参考图：{{{{{N_A0}}}}} 只用于确认它的身高比例，画面里不出现角色。\n"
    "无文字、无 logo、无水印。\n" + NEG_IMG,
    [N_A0], 340, 0, 420, 236
)
edge(N_A0, N_S1)

PROPS = [
    ("P1", "node-p1rice", "隔夜饭（白瓷碗装）", "白瓷碗里装着隔夜米饭，米粒干爽、颗颗分离、表面一层薄油光；碗口完整，碗身有细腻釉面高光"),
    ("P2", "node-p2egg", "鸡蛋（两只）", "两只新鲜的浅褐色鸡蛋并排，蛋壳有细小气孔与自然光泽，其中一只蛋壳上有一道细裂缝"),
    ("P3", "node-p3wok", "黑铁锅＋木柄锅铲", "一口用旧的黑铁锅，锅内有哑光油膜与磨损痕迹，木柄锅铲斜搭在锅沿上，木柄有使用包浆"),
    ("P4", "node-p4garnish", "配料小碟（葱花＋火腿丁）", "两只小碟并排放：一只装切好的翠绿葱花，一只是切好的粉红色火腿小丁，颗粒大小均匀"),
    ("P5", "node-p5stool", "小板凳", "一只矮木凳，四条腿、凳面有木纹与磨损圆角，用于站在上面够到台面"),
]
prop_ids = []
for i, (name, nid, label, body) in enumerate(PROPS):
    prop_ids.append(nid)
    gen_image(
        nid, f"【待生成】{name} {label} · 白底道具",
        f"纯白底道具图，只出现一件物品，不出现角色、不出现手。{body}。\n"
        "正面微侧、居中构图、完整入画，柔和顶光，物品下方有自然的接触阴影；真实材质，不塑料、不卡通。\n"
        "无文字、无 logo、无水印、无边框。\n" + NEG_IMG,
        [], 340, 280 + i * 210, 320, 200
    )

# ---------- 两张六宫格 ----------
SHEETS = [
    {
        "id": "node-g1sheet",
        "label": "G1 第一段六宫格 · 备料→切丁→点火",
        "cells": [
            "它站在木台面的食材阵列中间，身前是一碗隔夜饭、两只鸡蛋、一小碟葱花、一小碟火腿丁；它侧身抬头看饭堆，一只手伸向鸡蛋",
            "它双手抱着一只鸡蛋，磕在白瓷碗的碗沿上，蛋壳裂开，蛋液正落进碗里",
            "它双手抱着木筷子的末端，筷子斜插进碗里的蛋液，蛋液旋成涡",
            "俯拍：木砧板上摊着一片火腿，一把比它高的菜刀刀刃压在火腿上，它双手按在刀背顶端",
            "低角仰拍：它站在灶前的小板凳上，手搭在旋钮上，蓝色火苗刚从灶眼窜起",
            "空镜：白瓷碗里的隔夜饭微距，米粒干爽、颗颗分离、表面一层薄油光",
        ],
    },
    {
        "id": "node-g2sheet",
        "label": "G2 第二段六宫格 · 倒油→翻炒→出锅",
        "cells": [
            "它站在板凳上抱着一只比它高的油瓶往黑铁锅里倒油，油线刚触到锅底",
            "蛋液落进热油，边缘起泡、变成金黄，几颗油花溅起；它微微眯眼看着，不躲",
            "俯拍：木柄锅铲推进饭里，米粒跳起、开始裹上蛋液，画面边缘露出它两只手握着铲柄",
            "它站在锅耳上，双手握着锅铲柄，铲头插进饭的底部，身体开始往下压",
            "俯拍：白瓷盘里堆着金黄的蛋炒饭，它站在盘边捧着一只小勺往嘴里送，眼睛眯起",
            "空镜：盘中蛋炒饭的热气特写，金色米粒上的油光与上升的白色蒸汽",
        ],
    },
]
for s in SHEETS:
    cells = s["cells"]
    gen_image(
        s["id"], f"【待生成】{s['label']} · 3 列 2 行 · 16:9",
        "请生成一张三列两行的分镜设计图，一张大图中包含六个按顺序排列的画面，从左到右、从上到下按时间顺序阅读，"
        "整体保持统一的光线方向、色调与材质。\n"
        f"{SCENE}\n{TONE}\n{SCALE}。\n"
        "每一格都要能看出这只蛋仔站在哪里、正在做什么，每一格至少有一件东西能对照出它的身高。\n"
        + "\n".join(f"第 {i+1} 格：{c}。" for i, c in enumerate(cells)) +
        "\n格子里只出现这一只蛋仔，不出现人类、不出现第二只蛋仔、不出现文字与标识；每格只表现一个动作瞬间，"
        "格与格之间不要加标注、边框文字或分隔线。\n"
        "无文字、无 logo、无水印。\n"
        f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线。\n"
        f"角色：{CHAR}。\n" + NEG_IMG,
        [N_A0, N_S1], 800, 0 if s["id"].endswith("1sheet") else 320, 400, 300
    )
    for r in [N_A0, N_S1]:
        edge(r, s["id"])

# ---------- 两段 ----------
SEGS = [
    {
        "name": "V1", "k": "node-k1first", "g": "node-g1sheet", "dur": 15,
        "klabel": "【关键帧】K1 第一段首帧 · 备料 · 16:9",
        "kbody": ("它站在木台面的食材阵列中间，身前是一碗隔夜饭、两只鸡蛋、一小碟葱花、一小碟火腿丁；"
                  "它侧身抬头看饭堆，一只手正伸向鸡蛋。"),
        "vlabel": "【待生成】V1 第一段 0–15s · 备料→切丁→点火 · 15s",
        "shots": [
            ("0–3 秒", "它低头扫了一眼食材，伸手把两只鸡蛋拨到自己身前，抬头看向画面右侧的锅。"),
            ("3–6 秒", "它双手抱起一只鸡蛋，在碗沿上利落一磕，蛋壳裂开，蛋液落进碗里，壳分成两半。"),
            ("6–9 秒", "它抱着木筷子的末端，快速而稳定地搅动蛋液，蛋液被打散、泛起细小的泡，然后停手看向锅。"),
            ("9–12 秒", "它按着刀背往下压，一刀切断火腿，挪一下再切，切出一排大小均匀的小丁，然后直起身。"),
            ("12–15 秒", "它把板凳推到灶前、爬上去、踮脚拧开旋钮，蓝色火苗窜起，火光映在蛋壳上。"),
        ],
        "sound": "台面轻响、蛋壳碎裂、搅打声、刀落砧板两声、旋钮咔哒与燃气轰起；无人声台词",
    },
    {
        "name": "V2", "k": "node-k2first", "g": "node-g2sheet", "dur": 15,
        "klabel": "【关键帧】K2 第二段首帧 · 倒油 · 16:9",
        "kbody": ("它站在灶前的小板凳上，抱着一只比自己高的油瓶，瓶身刚倾斜，油线正要落进黑铁锅；"
                  "灶眼上的蓝色火苗正烧着。"),
        "vlabel": "【待生成】V2 第二段 15–30s · 倒油→翻炒→出锅 · 15s",
        "shots": [
            ("0–3 秒", "它稳稳地倒油，油线拉成一条细线，见油面起细纹就收住瓶口。"),
            ("3–6 秒", "它端着小碗把蛋液倒进热油，边缘立刻起泡、变成金黄，油花溅起；它微微眯眼看着，不躲。"),
            ("6–9 秒", "它双手握铲把饭推进锅里摊开，再翻炒，米粒一颗颗跳起、裹上蛋液。"),
            ("9–12 秒", "它站上锅耳，铲头插进饭底，把整个身体的重量压下去，锅铲像杠杆一样把整片饭撬起翻面，饭在空中展开又落回锅里。"),
            ("12–15 秒", "饭滑进白瓷盘，热气升起；它捧着小勺舀一口送进嘴里，眯起眼睛，把盘子往镜头方向推近一点。"),
        ],
        "sound": "倒油声、油爆密集、饭粒落锅、铲子受力、饭翻落的闷响、勺子碰盘；无人声台词",
    },
]

for i, seg in enumerate(SEGS):
    # 段首帧
    gen_image(
        seg["k"], seg["klabel"],
        f"16:9 横屏电影感画面。{seg['kbody']}\n"
        f"角色：{CHAR}。\n{TONE}\n{SCENE}\n{SCALE}。\n"
        "真实光影、浅景深、微距质感；画面里不出现人类、不出现第二只蛋仔、不出现文字与标识。\n"
        f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线；{{{{{seg['g']}}}}} 分镜第一格构图。\n"
        + NEG_IMG,
        [N_A0, N_S1, seg["g"]], 1240, i * 240, 360, 207
    )
    for r in [N_A0, N_S1, seg["g"]]:
        edge(r, seg["k"])

    # 十五秒段
    shot_txt = "\n".join(f"{t}：{d}" for t, d in seg["shots"])
    prompt = (
        f"【首帧锁定】首帧使用 {{{{{seg['k']}}}}}：第 0 秒就是这一帧，锁角色位置/朝向/光线与道具状态。\n"
        f"【分镜表】{{{{{seg['g']}}}}} 是本段的分镜设计图，一格一个镜头，按顺序推进；只参考它的构图与动作顺序，不要出现分格边框。\n"
        f"【角色】{CHAR}；它不说话，只靠动作和表情。\n"
        f"{TONE}\n{SCENE}\n{SCALE}。\n"
        f"【镜头】本段 15 秒，5 个镜头，每个约 3 秒，硬切衔接、不叠化、不推拉过渡：\n{shot_txt}\n"
        f"【声音】{seg['sound']}。\n"
        f"【字幕预留】字幕只在后期贴（{'／'.join(['备料', '磕蛋', '搅蛋', '切丁', '点火', '倒油', '下锅', '翻炒', '一铲', '出锅'][i*5:(i+1)*5])}），画面里不出现任何文字。\n"
        f"【图片引用】{{{{{seg['k']}}}}}=首帧；{{{{{seg['g']}}}}}=分镜表；{{{{{N_A0}}}}}=角色外观。\n"
        + NEG_VID
    )
    gen_video(seg["name"] and f"node-v{i+1}seg", seg["vlabel"], prompt, seg["k"],
              [seg["k"], seg["g"], N_A0], seg["dur"], 1700, i * 280)
    for r in [seg["k"], seg["g"], N_A0]:
        edge(r, f"node-v{i+1}seg")


# ---------- 组 ----------
def group(label, ids, x, y, w, h, color):
    groups.append({
        "id": rid("group"), "nodeIds": ids,
        "bounds": {"x": x, "y": y, "width": w, "height": h},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


group("00 参考 · 蛋小粉（已上传免重传）", [N_A0], -20, -20, 340, 380, "#E68BB3")
group("01 厨景 · 先跑", [N_S1], 320, -20, 460, 270, "#8E8DE0")
group("02 道具白底 · 与 01 并行", prop_ids, 320, 272, 460, 1190, "#7FB07F")
group("03 六宫格 · 两段分镜 · 定稿后再往下", ["node-g1sheet", "node-g2sheet"], 780, -20, 440, 660, "#E8B85D")
group("04 段首帧 K1/K2", ["node-k1first", "node-k2first"], 1220, -20, 400, 500, "#6FA8DC")
group("05 十五秒段 V1/V2 · 先只跑 V1", ["node-v1seg", "node-v2seg"], 1680, -20, 400, 560, "#DC775D")
group("06 制作说明 · 先读", [N_S0], -20, 392, 340, 800, "#B0B0B0")

canvas = {
    "schemaVersion": 2,
    "type": "monet.canvas",
    "exportedAt": TS,
    "canvas": {
        "name": "小蛋仔做菜 · EP01 蛋炒饭 v2 · 16:9 · 2段×15s · 蛋小粉",
        "description": (
            "30s＝2 段×15s，每段 5 个镜头（3s/镜）。厨师＝蛋小粉，基调熟练不滑稽。"
            "每段一张六宫格分镜直接作参考输入（W10 做法），段内切镜交给模型；每段只有一张段首帧（2 张，不是 12 张）。"
        ),
        "nodes": nodes,
        "edges": edges,
        "groups": groups,
    },
}

# ---------- 自检 ----------
problems = []
by_id = {n["id"]: n for n in nodes}
for n in nodes:
    if n["type"] in ("gen-image", "gen-video"):
        mp = n["params"]["model_params"]
        refs = [r["node_id"] for r in mp.get("reference_images", [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        tokens = set(re.findall(r"\{\{(node-[^\}]+)\}\}", mp.get("prompt", "")))
        for r in refs + ([ff] if ff else []):
            if r not in by_id:
                problems.append(f"{n['id']}: 引用不存在 {r}")
            if r not in tokens and r != ff:
                problems.append(f"{n['id']}: 参考图 {r} 未在 prompt 中以 {{{{…}}}} 提及")
        for t in tokens:
            if t not in by_id:
                problems.append(f"{n['id']}: prompt token {t} 无对应节点")
            srcs = {e["sourceNodeId"] for e in edges if e["targetNodeId"] == n["id"]}
            if t not in srcs:
                problems.append(f"{n['id']}: prompt 引用 {t} 没有连线")
        if n["type"] == "gen-video":
            L = len(mp["prompt"])
            if L > 2000:
                problems.append(f"{n['id']}: Vidu prompt {L} 字符超 2000")
            srcs = {e["sourceNodeId"] for e in edges if e["targetNodeId"] == n["id"]}
            if ff not in srcs:
                problems.append(f"{n['id']}: 首帧 {ff} 没有连线")
            for e in edges:
                if e["sourceNodeId"] == n["id"] and by_id.get(e["targetNodeId"], {}).get("type") == "gen-video":
                    problems.append(f"{n['id']}: video→video 边")
for i in range(len(groups)):
    for j in range(i + 1, len(groups)):
        a, b = groups[i]["bounds"], groups[j]["bounds"]
        if a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and \
           a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]:
            problems.append(f"组重叠: {groups[i]['label']} ↔ {groups[j]['label']}")
for g in groups:
    for nid in g["nodeIds"]:
        m = by_id[nid]["meta"]
        b = g["bounds"]
        if not (b["x"] <= m["x"] and m["x"] + m["width"] <= b["x"] + b["width"] and
                b["y"] <= m["y"] and m["y"] + m["height"] <= b["y"] + b["height"]):
            problems.append(f"节点 {nid} 超出组 {g['label']} 边界")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已生成 {OUT.name}: {len(nodes)} 节点 / {len(edges)} 边 / {len(groups)} 组 / 2×15s")
for n in nodes:
    if n["type"] == "gen-video":
        print(f"  {n['meta']['label']}: prompt {len(n['params']['model_params']['prompt'])} 字符")
if problems:
    print("\n自检失败:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("自检通过")
