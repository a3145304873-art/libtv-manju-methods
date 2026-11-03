# -*- coding: utf-8 -*-
"""《小蛋仔做菜》EP01《蛋炒饭》Monet 画布 v1 —— 16:9 / 30s / 12 拍 / 单角色蛋小粉。

设计要点（2026-10-29 用户拍板）：
- 画幅 16:9，30 秒＝12 拍 × 2.5 秒；每拍生成 3 秒，剪辑剪到 2.5 秒。
- 厨师＝蛋小粉（本地已有角色资产，复用 Monet 存储 URL）。
- 基调＝熟练，不滑稽：它是一只技术很好的小厨师，反差来自体型与手艺，不来自翻车。
- 工法参考 W10《锅气交响》，但 W10 没有厨师，本片每一拍都要交代"它站在哪、在做什么"。
- 管线 B：厨景 → 道具 → 分镜网格 → 关键帧（每拍一张）→ 逐拍视频。

自检：引用有边、无 video→video 边、组不重叠、节点不出组、Vidu prompt ≤ 2000 字符。
改提示词改本脚本重跑，不手改 .monet。
"""
import json
import random
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "EP01-蛋炒饭-v1.monet"
TS = "2026-10-29T15:00:00.000+08:00"
BY = "libtv-workspace"

STO = "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image"
# 蛋小粉标准图：四小只画布 2026-10-22 已上传，storage 同账号可跨画布复用（匿名读 401，画布内正常）
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
           "文字、水印、BGM旋律、说话、无故慢动作、镜头旋转、镜头漂移、露馅的翻车动作。")
LOCK = "第 0 秒就是这一帧，锁角色的位置/朝向/表情/光线与道具状态；摄影机全程固定不动，台面与锅的位置不变，不重构图不换机位，从这里直接继续。"

nodes = []
edges = []
groups = []


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
                "width": 1024,
                "height": 576,
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


# ---------- 参考与说明 ----------
N_A0 = "node-a0fendan"
input_image(N_A0, "A0 蛋小粉标准（已上传·复用四小只）", REF_FEN, "角色-粉蛋-标准.jpg", 1305, 1495, 0, 0, 300, 345)

N_S0 = "node-s0readme"
S0_TEXT = (
    "【本画布做什么】\n"
    "《小蛋仔做菜》EP01《蛋炒饭》：16:9、30 秒、12 拍、单角色蛋小粉。每拍生成 3 秒，剪辑剪到 2.5 秒。\n\n"
    "【跑序（组＝跑序，组内并行）】\n"
    "01 厨景 → 02 道具（可与 01 并行）→ 03 分镜网格（审核定稿）→ 04 关键帧 K01–K12 → 05 视频 V01–V12。\n"
    "网格没定稿不要跑关键帧；关键帧没定稿不要跑视频。\n\n"
    "【这一版的基调】\n"
    "熟练，不滑稽。它是一只技术很好的小厨师：磕蛋一次成功、切丁稳、倒油收得干净、一铲翻饭。\n"
    "笑点不在翻车，在「这么小一只，动作却是老师傅」。所有失败/狼狈的写法都从提示词里删掉了。\n\n"
    "【厨师在场纪律（验收用）】\n"
    "1. 每拍至少一端有它在画面里；纯食物空镜只有 P2、P9 两拍。\n"
    "2. 每拍能答出它站在哪儿：台面 / 板凳 / 锅耳 / 盘边。位置变了就是硬切。\n"
    "3. 食物发生的变化必须由它的动作引起。\n"
    "4. 每拍至少一件东西能对照出它 12 厘米的身高。\n\n"
    "【改法】\n"
    "改提示词请改 build-EP01蛋炒饭.py 后重跑，不手改 .monet。视频每段最多 2 抽，P8 下锅、P10 一铲各留 3 抽。\n\n"
    "【前期已改掉的两处】\n"
    "P10 原稿写「颠锅」——12 厘米举不起那口锅，已改成「站在锅耳上、用铲子当杠杆把整片饭撬起来翻面」。\n"
    "角色原为心易，2026-10-29 按用户要求换成蛋小粉。"
)
input_text(N_S0, "S0 制作说明 · 先读", S0_TEXT, 0, 400, 320, 780)

# ---------- 场景 ----------
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

# ---------- 道具白底 ----------
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

# ---------- 十二宫格分镜 ----------
N_G01 = "node-g01sheet"
G01_CELLS = [
    "它站在木台面的食材阵列中间，身前是一碗隔夜饭、两只鸡蛋、一小碟葱花、一小碟火腿丁，它侧身抬头看饭堆，一只手正伸向鸡蛋",
    "俯拍微距：白瓷碗里的隔夜饭铺满画面，米粒干爽颗颗分离、表面薄油光，它的一只手从画面右下入画捻起几粒米",
    "它双手抱着一只鸡蛋，把蛋举到白瓷碗的碗沿上，蛋壳刚碰到碗沿",
    "它双手抱着木筷子的末端，筷子斜插进碗里的蛋液，蛋液表面刚开始打旋",
    "俯拍：木砧板上摊着一片火腿，一把比它高的菜刀刀刃压在火腿上，它双手按在刀背顶端、身体前倾",
    "低角仰拍：它站在灶前的小板凳上，一只手已经搭在灶台旋钮上",
    "它站在板凳上抱着一只比它高的油瓶，瓶身倾斜，油线刚触到锅底",
    "它端着一只小碗，碗口对着锅，蛋液刚开始往下流",
    "俯拍：白米饭刚倒进锅里，木柄锅铲插进饭里，它双手握着铲柄末端",
    "它站在锅耳上，双手握着锅铲柄，铲头已经插进饭的底部",
    "它抱着一只比它还高的酱油瓶，瓶口对着锅里的饭，瓶身刚倾斜",
    "俯拍：白瓷盘里堆着金黄的蛋炒饭、热气上升，它站在盘边捧着一只小勺",
]
gen_image(
    N_G01, "【待生成】G01 十二宫格分镜 · 4 行 3 列 · 16:9",
    "请生成一张四行三列的分镜设计图，一张大图中包含十二个按顺序排列的画面，从左到右、从上到下按时间顺序阅读，"
    "整体保持统一的光线方向、色调与材质。\n"
    f"{SCENE}\n{TONE}\n{SCALE}。\n"
    "每一格都要能看出这只蛋仔站在哪里、正在做什么，每一格至少有一件东西能对照出它的身高。\n"
    + "\n".join(f"第 {i+1} 格：{c}。" for i, c in enumerate(G01_CELLS)) +
    "\n十二个格子里只出现这一只蛋仔，不出现人类、不出现第二只蛋仔、不出现文字与标识；每格只表现一个动作瞬间，"
    "格与格之间不要加标注、边框文字或分隔线。\n"
    "无文字、无 logo、无水印。\n"
    f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线。\n"
    f"角色：{CHAR}。\n" + NEG_IMG,
    [N_A0, N_S1], 800, 0, 400, 300
)
for r in [N_A0, N_S1]:
    edge(r, N_G01)

# ---------- 十二拍 ----------
BEATS = [
    ("P1", "备料 · 台面", "今天炒饭",
     "它站在木台面上，身前摆着白瓷碗装的隔夜饭、两只鸡蛋、一小碟葱花、一小碟火腿丁，排成一列；它侧身抬头看饭堆，一只手正伸向鸡蛋。",
     ["它低头扫了一眼食材，伸手把两只鸡蛋拨到自己身前，再抬头看向画面右侧的锅。"],
     ["0–1 秒：低头扫视食材", "1–2 秒：伸手拨动两只鸡蛋", "2–3 秒：抬头看向右侧的锅"],
     "台面轻响、蛋壳轻碰碗沿"),
    ("P2", "微距 · 隔夜饭", "隔夜饭",
     "俯拍微距，白瓷碗里的隔夜饭铺满画面，米粒干爽、颗颗分离、表面一层薄油光；它的一只手从画面右下入画，指尖正捻起几粒米。",
     ["它用指尖捻起几粒隔夜饭，轻轻一搓，米粒散开又落回碗里。"],
     ["0–1 秒：指尖入画", "1–2 秒：捻起米粒搓开", "2–3 秒：米粒落回碗中，它收回手"],
     "米粒摩擦的细碎沙沙"),
    ("P3", "磕蛋", "两个蛋",
     "它双手抱着一只鸡蛋，把蛋举到白瓷碗的碗沿上，蛋壳刚接触碗沿。",
     ["它抱着鸡蛋在碗沿上利落一磕，蛋壳裂开，蛋液落进碗里，壳分成两半。"],
     ["0–1 秒：抱蛋举起", "1–2 秒：磕向碗沿、壳裂", "2–3 秒：蛋液落进碗，壳分开"],
     "蛋壳碎裂、蛋液落碗"),
    ("P4", "搅蛋", "打散",
     "它双手抱着一根木筷子的末端，筷子斜插进碗里的蛋液，蛋液表面刚开始打旋。",
     ["它抱着筷子末端，快速而稳定地搅动蛋液，蛋液被打散、泛起细小的泡。"],
     ["0–1 秒：筷子插入", "1–2.5 秒：稳定快速搅动、蛋液起泡", "2.5–3 秒：它停手，看向锅"],
     "搅打声、蛋液碰碗"),
    ("P5", "切丁", "切丁",
     "俯拍，木砧板上摊着一片火腿，一把比蛋仔还高的菜刀刀刃已经压在火腿上；它双手按在刀背顶端，身体前倾。",
     ["它按着刀背往下压，一刀切断火腿，挪一下再切，切出一排大小均匀的小丁。"],
     ["0–1 秒：压刀切下第一刀", "1–2.5 秒：挪动火腿再切两刀", "2.5–3 秒：小丁排开，它直起身"],
     "刀落砧板两声、清脆"),
    ("P6", "点火", "火",
     "低角仰拍，灶台占画面上方三分之二，它站在灶前的小板凳上，一只手已经搭在旋钮上。",
     ["它踮脚把旋钮拧开，蓝色火苗从灶眼窜起，火光映在蛋壳上。"],
     ["0–1 秒：手搭旋钮", "1–2 秒：拧开", "2–3 秒：蓝火窜起，它看着火"],
     "旋钮咔哒、燃气轰起"),
    ("P7", "倒油", "油热了",
     "锅在画面右侧，它站在板凳上抱着一只比它高的油瓶，瓶身已经倾斜，油线刚触到锅底。",
     ["它稳稳地倒油，油线拉成一条细线，见油面起细纹就收住瓶口。"],
     ["0–1.5 秒：倒油", "1.5–2.2 秒：油面起细纹", "2.2–3 秒：收住瓶口"],
     "倒油声、油面轻响"),
    ("P8", "下蛋液", "下锅",
     "它端着一只小碗，碗口对着锅，蛋液刚开始往下流。",
     ["蛋液落进热油，边缘立刻起泡、变成金黄；它微微眯起眼睛看着，不躲。"],
     ["0–1 秒：蛋液落下", "1–2 秒：边缘起泡变金黄", "2–3 秒：它眯眼、把碗收回"],
     "油爆声密集、蛋液下锅"),
    ("P9", "翻炒", "翻炒",
     "俯拍，白米饭刚倒进锅里，木柄锅铲插进饭里，它双手握着铲柄末端。",
     ["它推着锅铲把饭摊开，再翻炒，米粒一颗颗跳起，开始裹上蛋液。"],
     ["0–1 秒：铲子推进摊开", "1–2.5 秒：翻炒、米粒跳起", "2.5–3 秒：粒粒裹上蛋液的金色"],
     "饭粒落锅、铲子刮锅"),
    ("P10", "一铲 · 翻饭", "一铲",
     "它站在锅耳上，双手握着锅铲柄，铲头已经插进饭的底部。",
     ["它把整个身体的重量压下去，锅铲像杠杆一样把整片饭撬起来翻面，饭在空中展开，又落回锅里。"],
     ["0–1 秒：铲子插底、身体下压", "1–2 秒：整片饭被撬起", "2–3 秒：饭翻面落回锅，油光一闪"],
     "铲子受力、饭翻落的闷响"),
    ("P11", "调味", "一点点",
     "它抱着一只比它还高的酱油瓶，瓶口对着锅里的饭，瓶身刚倾斜。",
     ["它抖了两下，两滴酱油落进饭里，立刻把瓶口按回去。"],
     ["0–1 秒：倾斜瓶身", "1–2 秒：抖两滴", "2–3 秒：收瓶"],
     "两滴酱油落下的轻响"),
    ("P12", "装盘与尝", "自己炒自己",
     "俯拍，白瓷盘里堆着金黄的蛋炒饭，热气升起；它站在盘边，捧着一只小勺。",
     ["它舀一勺饭送进嘴里，眯起眼睛，把盘子往镜头方向推近一点。"],
     ["0–1 秒：舀饭", "1–2 秒：送入口、眯眼", "2–3 秒：把盘子推向镜头"],
     "勺子碰盘、轻轻咀嚼"),
]

KIDS, VIDS = {}, {}
for i, (name, label, sub, k_body, v_action, v_time, sound) in enumerate(BEATS):
    kid = f"node-k{name[1:].zfill(2)}"
    KIDS[name] = kid
    gen_image(
        kid, f"【关键帧】{name} {label} · 16:9",
        f"16:9 横屏电影感画面。{k_body}\n"
        f"角色：{CHAR}。\n{TONE}\n{SCENE}\n{SCALE}。\n"
        "真实光影、浅景深、微距质感；画面里不出现人类、不出现第二只蛋仔、不出现文字与标识。\n"
        f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{N_S1}}}}} 厨房环境与光线；{{{{{N_G01}}}}} 分镜第 {i+1} 格构图。\n"
        + NEG_IMG,
        [N_A0, N_S1, N_G01], 1240, i * 240, 360, 207
    )
    for r in [N_A0, N_S1, N_G01]:
        edge(r, kid)

for i, (name, label, sub, k_body, v_action, v_time, sound) in enumerate(BEATS):
    kid = KIDS[name]
    vid = f"node-v{name[1:].zfill(2)}"
    VIDS[name] = vid
    prompt = (
        f"【首帧锁定】首帧使用 {{{{{kid}}}}}；{LOCK}\n"
        f"【角色】{CHAR}；它不说话，只靠动作和表情。\n"
        f"{TONE}\n{SCENE}\n{SCALE}。\n"
        f"【动作】{v_action[0]}\n"
        f"【时间拍】{'；'.join(v_time)}。\n"
        f"【字幕预留】这一拍的字幕是「{sub}」，只在后期贴，画面里不出现任何文字。\n"
        f"【声音】{sound}；无人声台词。\n"
        f"【图片引用】{{{{{kid}}}}}=首帧构图；{{{{{N_A0}}}}}=角色外观；{{{{{N_S1}}}}}=厨房环境。\n"
        + NEG_VID
    )
    gen_video(vid, f"【待生成】{name} {label} · 3s", prompt, kid, [kid, N_A0, N_S1], 3, 1700, i * 260)
    for r in [kid, N_A0, N_S1]:
        edge(r, vid)

# ---------- 组（组＝跑序，组内并行，边界不重叠） ----------
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
group("03 分镜网格 · 定稿后再往下", [N_G01], 780, -20, 440, 340, "#E8B85D")
group("04 关键帧 K01–K12 · 每拍一张", [KIDS[n] for n, *_ in BEATS], 1220, -20, 460, 2900, "#6FA8DC")
group("05 视频 V01–V12 · 3s×12", [VIDS[n] for n, *_ in BEATS], 1680, -20, 460, 3160, "#DC775D")
group("06 制作说明 · 先读", [N_S0], -20, 392, 340, 800, "#B0B0B0")

# ---------- 画布 ----------
canvas = {
    "schemaVersion": 2,
    "type": "monet.canvas",
    "exportedAt": TS,
    "canvas": {
        "name": "小蛋仔做菜 · EP01 蛋炒饭 · 16:9 · 12拍×3s · 蛋小粉",
        "description": (
            "30s 横屏 16:9：12 拍，每拍生成 3s、剪到 2.5s。厨师＝蛋小粉，基调＝熟练不滑稽（反差来自体型与手艺，不来自翻车）。"
            "管线 B：厨景→道具→十二宫格→12 张关键帧→12 段视频。P10 翻饭改为站在锅耳上用铲子当杠杆撬整片饭。"
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
total = sum(3 for _ in BEATS)
print(f"已生成 {OUT.name}: {len(nodes)} 节点 / {len(edges)} 边 / {len(groups)} 组 / 数组 {total}s（剪后 30s）")
print("提示词长度：")
for n in nodes:
    if n["type"] in ("gen-image", "gen-video"):
        print(f"  {n['meta']['label']}: {len(n['params']['model_params']['prompt'])} 字符")
if problems:
    print("\n自检失败:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("自检通过")
