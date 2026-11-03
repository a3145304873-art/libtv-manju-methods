# -*- coding: utf-8 -*-
"""《小蛋仔做菜》EP01《蛋炒饭》Monet 画布 v2 —— 16:9 / 30s / 2 段 × 15s / 蛋小粉。

v2 修正（2026-10-29 用户反馈）：
- 关键帧太多（v1 是 12 张）→ 现在 2 张，每段一张段首帧。
- 视频切得太碎（v1 是 12 段 × 2.5s）→ 现在 2 段 × 15s，每段 5 个镜头、每个 3 秒。
- 参考 W10 的做法：**一张网格分镜直接作为视频生成的参考输入**，模型在段内完成切镜。

结构：A0 角色 + S1 厨景 + P1–P5 道具 + G1/G2 六宫格 + K1/K2 段首帧 + V1/V2 十五秒段 + S0 说明。
自检：引用有边、无 video→video 边、组不重叠、节点不出组、视频 prompt ≤ 2000 字符。
改提示词改本脚本重跑，不手改 .monet。
"""
import json
import random
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "EP01-蛋炒饭-v8.monet"
TS = "2026-10-29T20:00:00.000+08:00"
BY = "libtv-workspace"

STO = "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image"
REF_FEN = f"{STO}/20261022-035437-0d34f1caae5e8c3e-e8-a7-92-e8-89-b2-e7-b2-89-e8-9b-8b-e6-a.jpg"

CHAR = ("蛋小粉：一只约 30 厘米高的粉色搪胶蛋仔（大约一只猫的高度，明显大过一只碗），圆形蛋身、正面一片奶油色椭圆脸盘、"
        "绿色星星眼、细弯眉、小嘴、粉色圆腮、头顶一根带小圆球的粉色触角、短圆手臂、白色小袜靴；"
        "外观严格照参考图，不增不减不变色，无人类五官、无手指、无衣物")
SCALE = ("尺度：它约 30 厘米高，锅径约为它身高的 2.5 倍，一只碗的口径约等于它的身高，菜刀长度约等于它的身高；"
         "它能双手抱住刀柄、端起小碗、扶住锅沿，动作是够得着的，不是够不着")
SPACE = ("空间分区：台面左侧是备料区（原木砧板、粗陶碗、几只陶碟、陶油壶、棉麻抹布），右侧是灶台区（黑铁锅坐在土灶灶眼上，"
         "蓝色火苗在锅底）；小板凳放在灶台前的地面上、与锅之间隔着灶台边缘，板凳不进锅、不放进灶眼、不上灶台；"
         "砧板上的东西不挪到锅里，锅里的东西不放到砧板上")
SCENE = ("场景：森林边的一间小木屋厨房，半开放的木结构，左侧原木台面是备料区，右侧一座土灶上坐着黑铁锅；"
         "木墙上挂着竹筛、木勺和干花，窗台上放着一陶盆绿植；窗外是晨雾里的树林和苔藓，光从窗口斜进来，"
         "台面上有一小块阳光；室内干净、安静、只有必须的东西，没有现代电器、没有不锈钢、没有塑料收纳盒")
LIGHT = ("光线：单一光源——清晨的窗光从右上方斜入，柔和不硬，带一点点雾气的散射；灶火只作暖色补光；"
         "色调是原木色 + 苔绿 + 奶油白 + 陶土橙，画面通透不脏、不黄")
TONE = ("基调：治愈、安静、慢；它是有手艺的小厨师，动作利落但节奏舒缓，不狼狈、不嬉闹；"
        "可爱来自体型与手艺的反差，治愈来自干净的环境、柔和的光和放大的环境声")
NEG_IMG = ("负向：人类、手指、毛发、卡通扁平渲染、塑料玩具感、比例失真、角色复制、第二只蛋仔、道具重复、文字、水印、logo、"
           "边框、过曝、广告打光、多个光源、道具穿模、板凳出现在锅里或灶眼里、厨具悬空、刀压在刀背上、"
           "人手、人类手掌、五指手指、指甲、人的小臂、穿袖子的手、握着刀柄的真人手、现代电器、不锈钢台面、塑料收纳盒、瓷砖大白墙、杂物堆积、脏污油腻、蛋液来自未磕开的蛋、完好蛋壳旁出现蛋液、火腿丁凭空出现、未切即出现丁、葱未切即碎、笼屉未开盖即放入食物、食物凭空出现在锅里、油量过多淹没食材、油面高过食材、食材数量增加或凭空消失、刀刃未接触食材却已切开、火未点即有火焰、锅未热即冒烟。")
NEG_VID = ("负向：人类、手指、多余角色、第二只蛋仔、卡通扁平、塑料玩具感、比例失真、瞬移、变形、角色复制、道具复制、字幕、"
           "文字、水印、BGM旋律、说话、镜头旋转、镜头漂移、翻车动作、鬼畜重复、板凳进锅、道具穿模、刀悬空、"
           "人手、人类手掌、五指、指甲、人的小臂、真人手握刀、现代电器、不锈钢、塑料收纳盒、杂物堆积、无因之果、食材凭空出现或消失、油量过多、火未点即有火、上一镜的道具在下一镜消失、食物自己变化、切好的食材瞬间变成另一种形状。")

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
            "num": 1, "model_id": "seedance-2.0-mini",
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
    "《小蛋仔做菜》EP01《蛋炒饭》v8：16:9、60 秒＝4 段 × 15 秒；每段 3 个动作拍 + 1 个呼吸拍。\n"
    "厨师＝蛋小粉；基调＝治愈、安静、慢。\n\n"
    "【v4 相对 v3 改了什么（按用户看片反馈）】\n"
    "1. 场景从「人类出租屋小厨房」换成「森林边的小木屋厨房」：原木台面、土灶、竹筛木勺、窗台绿植，窗外是晨雾里的树林与苔藓。\n"
    "2. 加了光线约束：只有一个光源（清晨窗光），灶火只作暖色补光；原木色 + 苔绿 + 奶油白 + 陶土橙。\n"
    "3. 材质整体换成自然系：粗陶碗碟、陶酱油壶、原木砧板、棉麻抹布；负向禁现代电器、不锈钢、塑料收纳盒、瓷砖大白墙、杂物堆积。\n"
    "4. 声音加环境底：鸟鸣、风过树叶、柴火轻爆；动作声之上有一层自然的底噪。\n"
    "5. 基调从「熟练不滑稽」扩成「治愈、安静、慢」：动作利落但节奏舒缓，治愈来自干净的环境、柔和的光和放大的环境声。\n\n"
    "【v3 已修的（保留）】\n"
    "角色 30 厘米 / 锅径 2.5 倍身高；空间分区、板凳不进锅；切菜改成握刀柄垂直落下；备菜补到 15 环节。\n\n"
    "【跑序】\n"
    "01 厨景 → 02 道具 P1–P7（可并行）→ 03 三张六宫格（审核定稿）→ 04 K1–K3 段首帧 → 05 V1–V3 十五秒段。\n"
    "网格没定稿不要跑段首帧；段首帧没定稿不要跑视频。\n\n"
    "【风险，先跑 V1 验证】\n"
    "本库 I06 记录过「多宫格图片直接接视频会干扰构图」，那条是把它当首帧用的坑；\n"
    "这里只当 reference_images，首帧仍是单张 K。仍属未验证组合——**先只跑 V1**，看段内 5 个切点是否干净。\n"
    "若切点失控，退路是仍按 15 秒交付、拆成 3 段 5 秒生成（切点还是 6 个，成本 +4 次派发）。\n\n"
    "【改法】\n"
    "改提示词请改 build-EP01蛋炒饭-v3.py 后重跑，不手改 .monet。"
)
input_text(N_S0, "S0 制作说明 · 先读", S0_TEXT, 0, 400, 320, 780)

# ---------- 场景与道具 ----------
N_S1 = "node-s1kitchen"
gen_image(
    N_S1, "【待生成】S1 小木屋厨房 · 清晨空景 · 16:9",
    "16:9 场景设定空景，不出现任何角色。森林边的一间小木屋厨房，半开放的木结构：\n"
    "左侧原木台面是备料区，台面上放着一块原木砧板、几只粗陶碟、一把陶油壶、一块叠好的棉麻抹布；\n"
    "右侧一座土灶，土灶上坐着一口黑铁锅，锅径约是蛋仔身高的 2.5 倍；灶口是熄的，只有一点余火的红。\n"
    "木墙上挂着竹筛、木勺和一束干花；窗台上放着一陶盆绿植；窗外是晨雾里的树林与苔藓，光从窗口斜进来，在台面上留下一小块阳光。\n"
    "室内干净、安静、只有必须的东西：没有现代电器、没有不锈钢、没有塑料收纳盒、没有杂物堆。\n"
    f"{SCALE}。{SPACE}。{LIGHT}。\n"
    f"参考图：{{{{{N_A0}}}}} 只用于确认它的身高比例，画面里不出现角色。\n"
    "浅景深、真实光影、微距质感，不摆拍、不广告打光。无文字、无 logo、无水印。\n" + NEG_IMG,
    [N_A0], 340, 0, 420, 236
)
edge(N_A0, N_S1)

PROPS = [
    ("P1", "node-p1rice", "隔夜饭（粗陶碗装）", "粗陶碗里装着隔夜米饭，米粒干爽、颗颗分离但结成一团一团；碗口完整，碗身有细腻釉面高光"),
    ("P2", "node-p2egg", "鸡蛋（两只）", "两只新鲜的浅褐色鸡蛋并排，蛋壳有细小气孔与自然光泽，其中一只蛋壳上有一道细裂缝"),
    ("P3", "node-p3wok", "黑铁锅＋木柄锅铲", "一口用旧的黑铁锅，锅内有哑光油膜与磨损痕迹，木柄锅铲斜搭在锅沿上，木柄有使用包浆"),
    ("P4", "node-p4garnish", "两只小碟（葱花＋火腿丁）", "两只陶碟并排：一只装切好的翠绿葱花，一只装切好的粉红色火腿小丁，颗粒大小均匀"),
    ("P5", "node-p5ham", "火腿片（砧板上）", "木砧板上摊着两片粉红色火腿片，边缘整齐，表面有细微的肉纹与水光"),
    ("P6", "node-p6season", "调味三件（盐碟·酱油瓶·小油瓶）", "一只小碟里是白色细盐，一只粗陶酱油壶，一只矮油瓶，瓶口干净、贴纸无字"),
    ("P7", "node-p7stool", "小板凳", "一只矮木凳，四条腿、凳面有木纹与磨损圆角，用于站在上面够到台面"),
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


CAUSAL = ("因果律：每一个画面里出现的东西、每一种状态，都必须由本镜里看得见的动作产生——"
          "蛋液只能从磕开的蛋壳里流出来，火腿丁只能由落下的刀切出来，火只能在拧开旋钮之后出现，"
          "油只能在壶倾斜之后出现在锅里；不许有「结果先于过程」，也不许有凭空出现或凭空消失的道具")
HANDS = ("手：它只有两只短圆的、没有手指的手（像圆头的小短臂），全程用它夹、抱、按、推；"
         "画面里绝不出现人类的手——没有手掌、没有五指、没有指甲、没有人的小臂，也没有穿袖子的手；"
         "拿刀、端碗、拧旋钮都只能是它那两只圆手，工具是被圆手抱住的，不是被手指捏住的")
QUANTITY = ("数量与用量：鸡蛋两只、火腿一片、小葱一小把、米饭一碗；油只倒薄薄一层，铺满锅底即可，油面不超过锅深的十分之一，"
            "绝不淹没食材；酱油只抖两滴、盐只撒一小撮；碗、碟、刀、锅的数量和位置在一段之内不增不减")
# ---------- 四张四宫格 ----------
# 每段 15 秒 = 3 个动作拍（3.3/3.3/3.4 s）+ 1 个呼吸拍（5.0 s）。呼吸拍不推进剧情，只拍火、蒸汽、光。
SHEETS = [
    {
        "id": "node-g1sheet",
        "label": "G1 第一段 · 备料一（抓饭／切配料／打蛋／呼吸）",
        "cells": [
            "起：粗陶碗里的隔夜饭结成一团一团｜动作：它双手伸进碗里捻、抓｜止：饭散成松散的米粒堆",
            "起：砧板上摊着一整片火腿、旁边一小把葱｜动作：它抱住刀柄抬刀落下，切出火腿条，再切葱｜止：砧板上有一小堆火腿丁和葱花",
            "起：两只完整的鸡蛋在碗边｜动作：它抱起一只，磕在碗沿上｜止：壳裂开、蛋液落进碗、壳分成两半",
            "呼吸拍：砧板静物特写，火腿丁、葱花、打散的蛋液并排，晨光斜落在上面，光里的浮尘缓慢移动——这一格没有动作，只有光和静物",
        ],
    },
    {
        "id": "node-g2sheet",
        "label": "G2 第二段 · 备料二（搅蛋／点火／倒油／呼吸）",
        "cells": [
            "起：碗里蛋黄完整、蛋液安静｜动作：它抱着木筷子末端搅动｜止：蛋液均匀、表面泛起细小的泡",
            "起：灶眼是熄的｜动作：它踮脚拧旋钮｜止：蓝色火苗从灶眼窜起；板凳在灶台前的地面上，不在锅里",
            "起：锅里是干的、没有油｜动作：它抱着陶油壶倾斜，油线落进锅底｜止：锅底铺着薄薄一层油",
            "呼吸拍：低角特写，锅底蓝火轻轻跳动，薄油表面有细纹和一点热气——这一格没有动作，只有火和油",
        ],
    },
    {
        "id": "node-g3sheet",
        "label": "G3 第三段 · 下锅（蛋液／下饭／翻炒／呼吸）",
        "cells": [
            "起：碗里是打散的蛋液，锅里有薄油｜动作：它端碗倾倒，再用铲推散｜止：蛋液在锅里起泡、被分成小块的金黄蛋块",
            "起：粗陶碗里是隔夜饭，锅里有蛋块｜动作：它端起碗把饭倒进锅｜止：饭粒落进锅里，和蛋块混在一起",
            "起：饭和蛋分层、米是白的｜动作：它双手握铲推、翻｜止：米粒裹上蛋液，颜色均匀金黄",
            "呼吸拍：俯拍锅里，饭在余温里轻轻冒热气，几缕蒸汽升起来又散开——这一格没有动作，只有蒸汽",
        ],
    },
    {
        "id": "node-g4sheet",
        "label": "G4 第四段 · 收（调味／一铲／装盘尝／呼吸）",
        "cells": [
            "起：锅里是炒好的饭｜动作：它抱着陶酱油壶抖两滴、再撒一把葱花｜止：饭上有两处酱点、一层绿色葱花",
            "起：饭在锅里摊平｜动作：它站上锅耳，铲头插进饭底，整个人压下去｜止：整片饭被撬起来翻面，落回锅里",
            "起：锅里有饭、陶盘是空的｜动作：它倾斜锅把饭滑进盘、舀一勺尝｜止：饭在盘里堆起，它在吃",
            "呼吸拍：陶盘里蛋炒饭的热气特写，镜头不动、停住 5 秒，热气一直上升——这一格没有动作，只有热气",
        ],
    },
]
for i, s in enumerate(SHEETS):
    cells = s["cells"]
    gen_image(
        s["id"], f"【待生成】{s['label']} · 2 列 2 行 · 16:9",
        "请生成一张两列两行的分镜设计图，一张大图中包含四个按顺序排列的画面，从左到右、从上到下按时间顺序阅读，"
        "整体保持统一的光线方向、色调与材质。前三格是一件事的三个瞬间，第四格是没有动作的空镜（只有火、蒸汽、光或静物）。\n"
        f"{SCENE}\n{LIGHT}\n{TONE}\n{SCALE}。\n{SPACE}。\n{CAUSAL}。{QUANTITY}。{HANDS}。\n"
        "每一格都按「起—动作—止」画，只能画出这一格动作完成后的样子；刀必须握在刀柄上、垂直落下切到食物；"
        "火只在灶眼上；每一格都要能看出它站在哪里。画面要唯美：浅景深、一层薄雾、光里有浮尘、器物表面有湿润感。\n"
        + "\n".join(f"第 {j+1} 格：{c}。" for j, c in enumerate(cells)) +
        "\n格子里只出现这一只蛋仔，不出现人类、不出现第二只蛋仔、不出现文字与标识；"
        "格与格之间不要加标注、边框文字或分隔线。\n"
        "无文字、无 logo、无水印。\n"
        f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线。\n"
        f"角色：{CHAR}。\n" + NEG_IMG,
        [N_A0, N_S1], 800, i * 320, 400, 300
    )
    for r in [N_A0, N_S1]:
        edge(r, s["id"])

# ---------- 四段 ----------
SEGS = [
    {
        "name": "V1", "k": "node-k1first", "g": "node-g1sheet", "dur": 15,
        "klabel": "【关键帧】K1 第一段首帧 · 抓饭 · 16:9",
        "kbody": ("它站在台面备料区边，身前是粗陶碗装着的、结成一团一团的隔夜饭，旁边是木砧板、一整片火腿、一小把葱、"
                  "两只完整的鸡蛋；它双手刚伸进饭碗里，饭还是结块的。"),
        "vlabel": "【待生成】V1 备料一 0–15s · 抓饭／切配料／打蛋／呼吸 · 15s",
        "subs": ["隔夜饭", "切点葱"],
        "shots": [
            ("0–3.3 秒", "起幅：饭在碗里结成团。它双手伸进碗里捻、抓，把饭抓散；散开后手停一下，让米粒落定。"),
            ("3.3–6.6 秒", "起幅：砧板上是一整片火腿和一小把葱。它抱住刀柄抬起、垂直落下切出火腿条，再切葱；刀落在砧板上。"),
            ("6.6–10 秒", "起幅：两只完整的鸡蛋在碗边。它抱起一只在碗沿上磕开，蛋壳先裂、蛋液再落进碗里，壳分成两半。"),
            ("10–15 秒", "空镜：砧板静物，火腿丁、葱花、打散的蛋液并排摆着；晨光斜落在上面，光里的浮尘缓慢移动，画面里没有动作。"),
        ],
        "sound": "鸟鸣、风过树叶、柴火的底噪；米粒摩擦、刀落砧板、蛋壳碎裂；这一整段没有音乐、没有台词",
    },
    {
        "name": "V2", "k": "node-k2first", "g": "node-g2sheet", "dur": 15,
        "klabel": "【关键帧】K2 第二段首帧 · 搅蛋 · 16:9",
        "kbody": ("它站在台面边，手里抱着木筷子的末端，筷子插在碗里的蛋液里；灶台在画面右侧，灶眼是熄的。"),
        "vlabel": "【待生成】V2 备料二 15–30s · 搅蛋／点火／倒油／呼吸 · 15s",
        "subs": ["打散", "火"],
        "shots": [
            ("0–3.3 秒", "起幅：碗里蛋黄完整。它抱着筷子末端不快不慢地搅，蛋液被打散、泛起细小的泡，然后停手。"),
            ("3.3–6.6 秒", "起幅：灶眼是熄的。它站在土灶前的小板凳上踮脚拧开旋钮，蓝色火苗才窜起来，火光映在蛋壳上。"),
            ("6.6–10 秒", "起幅：锅里是干的。它抱着陶油壶倾斜，油线落进锅底，见油面起细纹就收住——只铺薄薄一层。"),
            ("10–15 秒", "空镜：低角特写，锅底蓝火轻轻跳动，薄油表面浮着细纹和一点热气；画面里没有动作，只有火和油。"),
        ],
        "sound": "窗外鸟鸣与风；搅打声、旋钮咔哒、燃气轻响、倒油；这一整段没有音乐、没有台词",
    },
    {
        "name": "V3", "k": "node-k3first", "g": "node-g3sheet", "dur": 15,
        "klabel": "【关键帧】K3 第三段首帧 · 下蛋液 · 16:9",
        "kbody": ("它站在灶前，手里端着装蛋液的小碗，碗口对着锅；锅里有薄油，火是蓝的。"),
        "vlabel": "【待生成】V3 下锅 30–45s · 蛋液／下饭／翻炒／呼吸 · 15s",
        "subs": ["下锅", ""],
        "shots": [
            ("0–3.3 秒", "起幅：碗里是打散的蛋液，锅里有薄油。它端碗倾倒，蛋液落进热油、边缘起泡变金黄，再握铲推散成小块。"),
            ("3.3–6.6 秒", "起幅：粗陶碗里是隔夜饭，锅里有蛋块。它端起碗把饭倒进锅，饭粒落进锅中。"),
            ("6.6–10 秒", "起幅：饭和蛋分层、米是白的。它双手握铲推、翻炒，米粒一颗颗跳起、裹上蛋液变成均匀的金黄。"),
            ("10–15 秒", "空镜：俯拍锅里，炒饭在余温里轻轻冒热气，几缕蒸汽升起来又散开；画面里没有动作，只有蒸汽。"),
        ],
        "sound": "鸟鸣与远处的风；油爆、铲子刮锅、饭粒落锅与跳动、蒸汽轻响；这一整段没有音乐、没有台词",
    },
    {
        "name": "V4", "k": "node-k4first", "g": "node-g4sheet", "dur": 15,
        "klabel": "【关键帧】K4 第四段首帧 · 调味 · 16:9",
        "kbody": ("俯拍：锅里是炒好的金黄蛋炒饭，它抱着一只陶酱油壶、另一手拿着一小碟葱花，正要往下抖。"),
        "vlabel": "【待生成】V4 收 45–60s · 调味／一铲／装盘尝／呼吸 · 15s",
        "subs": ["一点点", "一铲", "自己炒自己"],
        "shots": [
            ("0–3.3 秒", "起幅：锅里是炒好的饭。它抱着陶酱油壶抖了两滴，再撒一把葱花。"),
            ("3.3–6.6 秒", "起幅：饭在锅里摊平。它站上锅耳，铲头插进饭底，把整个身体的重量压下去，把整片饭撬起来翻面。"),
            ("6.6–10 秒", "起幅：锅里有饭、陶盘是空的。它倾斜锅把饭滑进盘，舀一勺送进嘴里，眯起眼睛。"),
            ("10–15 秒", "空镜：陶盘里蛋炒饭的热气特写，镜头一动不动地停着，热气一直往上升，散开在光里；画面里没有动作。"),
        ],
        "sound": "窗外鸟鸣与风；两滴酱油、葱花落锅、铲子受力、饭翻落的闷响、勺碰盘；结尾一声轻轻的「嘟」，没有台词、没有音乐",
    },
]

for i, seg in enumerate(SEGS):
    gen_image(
        seg["k"], seg["klabel"],
        f"16:9 横屏电影感画面。{seg['kbody']}\n"
        f"角色：{CHAR}。\n{TONE}\n{SCENE}\n{LIGHT}\n{SCALE}。\n{SPACE}。\n{CAUSAL}。{QUANTITY}。{HANDS}。\n"
        "真实光影、浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；画面里不出现人类、不出现第二只蛋仔、不出现文字与标识。\n"
        f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线；{{{{{seg['g']}}}}} 分镜第一格构图。\n"
        + NEG_IMG,
        [N_A0, N_S1, seg["g"]], 1240, i * 240, 360, 207
    )
    for r in [N_A0, N_S1, seg["g"]]:
        edge(r, seg["k"])

    shot_txt = "\n".join(f"{t}：{d}" for t, d in seg["shots"])
    subs = "／".join([s for s in seg["subs"] if s])
    prompt = (
        f"【首帧锁定】首帧使用 {{{{{seg['k']}}}}}：第 0 秒就是这一帧，锁角色位置/朝向/光线与道具状态。\n"
        f"【分镜表】{{{{{seg['g']}}}}} 是本段的分镜设计图，一格一个镜头，按顺序推进；只参考它的构图与动作顺序，不要出现分格边框。\n"
        f"【角色】{CHAR}；它不说话，只靠动作和表情。\n"
        f"{TONE}\n{SCENE}\n{LIGHT}\n{SCALE}。\n{SPACE}。\n"
        f"【因果】{CAUSAL}。\n【用量】{QUANTITY}。\n【手】{HANDS}。\n"
        f"【节奏】本段 15 秒 4 个镜头：前三个各约 3.3 秒做一个动作，做完要停一下再切；第四个是 5 秒的空镜，"
        "不推进剧情，只让火、蒸汽、光或静物自己动。不要加速，不要炫技运镜，镜头基本不动。\n"
        f"【镜头】\n{shot_txt}\n"
        f"【声音】{seg['sound']}。\n"
        f"【字幕预留】字幕只在后期贴（{subs}），画面里不出现任何文字。\n"
        f"【图片引用】{{{{{seg['k']}}}}}=首帧；{{{{{seg['g']}}}}}=分镜表；{{{{{N_A0}}}}}=角色外观。\n"
        + NEG_VID
    )
    gen_video(f"node-v{i+1}seg", seg["vlabel"], prompt, seg["k"],
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
group("02 道具白底 P1–P7 · 与 01 并行", prop_ids, 320, 272, 460, 1490, "#7FB07F")
group("03 四宫格 G1–G4 · 定稿后再往下", [s["id"] for s in SHEETS], 780, -20, 440, 1300, "#E8B85D")
group("04 段首帧 K1–K4", [s["k"] for s in SEGS], 1220, -20, 400, 980, "#6FA8DC")
group("05 十五秒段 V1–V4 · 先只跑 V1", [f"node-v{i+1}seg" for i in range(4)], 1680, -20, 400, 1100, "#DC775D")
group("06 制作说明 · 先读", [N_S0], -20, 392, 340, 800, "#B0B0B0")

canvas = {
    "schemaVersion": 2,
    "type": "monet.canvas",
    "exportedAt": TS,
    "canvas": {
        "name": "小蛋仔做菜 · EP01 蛋炒饭 v8 · 16:9 · 4段×15s · 治愈节奏版",
        "description": (
            "60s＝4 段×15s，每段 3 个动作拍（3.3s）+ 1 个呼吸拍（5s），共 12 个动作、4 个空镜。"
            "按「菇子柒」的实测节奏改：单拍从 3s 拉到 3.3–5s，字幕从 15 条砍到 8 条，取消音乐只留环境音，"
            "画面加薄雾与浮尘求唯美。模型 seedance-2.0-mini。"
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
                problems.append(f"{n['id']}: 视频 prompt {L} 字符超 2000")
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
print(f"已生成 {OUT.name}: {len(nodes)} 节点 / {len(edges)} 边 / {len(groups)} 组 / 4x15s")
for n in nodes:
    if n["type"] == "gen-video":
        print(f"  {n['meta']['label']}: prompt {len(n['params']['model_params']['prompt'])} 字符")
if problems:
    print("\n自检失败:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("自检通过")
