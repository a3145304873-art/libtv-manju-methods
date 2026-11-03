# -*- coding: utf-8 -*-
"""Build 蛋仔记单词 · -like 三词样片「蛋仔的日常」Monet canvas.

Pilot: rocklike / snakelike / doglike, 2×12s (24s).
Shell: cozy living room + everyday scenes (park stone table / balcony garden / entryway).
Snake: a real cute small snake (A06), not a toy/hose.
Transitions: fast whip pan / direct scene change, no photo studio, no flash.

Outputs:
  02_画布/EP02-like-daily-pilot-v1.monet
  ~/Downloads/EP02-like-daily-pilot-v1.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "egg-like-daily-pilot:v1"
IMAGE_MODEL = "gpt-image-2"
VIDEO_MODEL = "seedance-2.0-mini"

R00 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035437-5241228d6d235662-r00-e5-9b-9b-e5-b0-8f-e5-8f-aa-e8-ba-ab.jpg",
    "name": "R00-四小只身高比例.jpg", "width": 1600, "height": 650, "size": 77895,
    "md5": "b321a4a46247edafe03ddd2dc85b3605",
}
R01 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035438-8a7a8cba5091bb94-e8-a7-92-e8-89-b2-e9-bb-84-e8-9b-8b-e6-a.jpg",
    "name": "角色-黄蛋-标准.jpg", "width": 1118, "height": 1280, "size": 86469,
    "md5": "7939d7b1ed7e0315344a5eb2c13e6d1a",
}
R02 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035437-0d34f1caae5e8c3e-e8-a7-92-e8-89-b2-e7-b2-89-e8-9b-8b-e6-a.jpg",
    "name": "角色-粉蛋-标准.jpg", "width": 1117, "height": 1280, "size": 97490,
    "md5": "51dda2189f378bc9c464076bdeb31dc3",
}


def nid(key: str) -> str:
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode("utf-8")).hexdigest()[:8]


def oid(kind: str, key: str) -> str:
    return "output-" + hashlib.md5((PREFIX + ":" + kind + ":" + key).encode("utf-8")).hexdigest()[:10]


def make_input_image(key, label, info, x, y, width=300.0):
    ratio = info["height"] / info["width"]
    height = round(width * ratio, 1)
    return {
        "id": nid(key), "type": "input-image", "mainOutputId": oid("input", key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": oid("input", key), "status": "done", "error": None,
            "value": info["url"], "cover": None, "name": info["name"],
            "resolution": {"width": info["width"], "height": info["height"]},
            "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            "metadata": {"size": info["size"], "md5": info["md5"]},
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def make_gen_image(key, label, prompt, ref_keys, x, y, width=300.0, height=170.0):
    return {
        "id": nid(key), "type": "gen-image", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1, "model_id": IMAGE_MODEL,
            "model_params": {
                "prompt": prompt,
                "reference_images": [{"node_id": nid(k)} for k in ref_keys],
                "aspect_ratio": "16:9", "image_size": "1K",
                "width": 1024, "height": 1024, "quality": "medium",
                "output_format": "png", "moderation": "low", "auto_compress": True,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def make_gen_video(key, label, prompt, ref_keys, ff_key, x, y, duration=12):
    return {
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 340.0, "height": 220.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1, "model_id": VIDEO_MODEL,
            "model_params": {
                "prompt": prompt, "_reference_way": "reference",
                "reference_images": [{"node_id": nid(k)} for k in ref_keys],
                "reference_audios": [],
                "first_frame_image": {"node_id": nid(ff_key)},
                "resolution": "720p", "aspect_ratio": "16:9",
                "duration": duration, "generate_audio": True, "watermark": False,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def make_text(key, label, text, x, y, width=760, height=600):
    return {
        "id": nid(key), "type": "input-text", "mainOutputId": oid("text", key),
        "meta": {"x": float(x), "y": float(y), "width": float(width), "height": float(height),
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": oid("text", key), "status": "done", "error": None, "value": text,
            "cover": None, "name": label, "resolution": None, "source": None,
            "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


A01_PROMPT = """16:9 纯白底道具设定图，三个道具并排：①一块圆润的灰色小石头（道具，约蛋仔手掌大小，表面有可爱高光）；②一条红色狗绳；③三张空白词卡（米白卡片、浅灰边）。3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo、无手。
负向：真实照片、恐怖、人类、手指、文字、水印、logo、比例失真、玩具蛇、水管。"""

A02_PROMPT = """16:9 蛋仔的客厅：布艺沙发、木茶几、地毯、绿植、落地窗、午后暖光；茶几上放三张空白词卡；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），低机位，柔和景深。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

A03_PROMPT = """16:9 小区公园一角：一张圆石桌/石凳、几棵树、草地、日光斑驳；低机位；3D 卡通渲染+真实光影（皮克斯质感），柔和景深。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

A04_PROMPT = """16:9 蛋仔家阳台小花园：一排花盆、绿植、浇水壶、水泥栏杆、午后光；低机位，前景留出小蛇滑过的空间；3D 卡通渲染+真实光影（皮克斯质感），柔和景深。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真、玩具蛇。"""

A05_PROMPT = """16:9 蛋仔家玄关：鞋柜、狗窝、狗绳挂钩、门口地垫；一只金毛犬坐在狗窝旁，摇尾、吐舌；暖光、低机位；3D 卡通渲染+真实光影（皮克斯质感），柔和景深。
无人物、无文字、无 logo、无水印。
负向：人类、角色、文字、水印、logo、恐怖、真实照片、过曝、比例失真。"""

A06_PROMPT = """16:9 纯白底角色设定图，只生成一只小蛇：圆头、大眼、绿色鳞片、浅黄肚皮、小小的分叉舌头；可爱、无尖牙、不恐怖；身体盘成一圈、微微抬头；体长约蛋仔 2–3 倍；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo、无手。
负向：真实蛇、恐怖、尖牙、毒牙、人类、手指、文字、水印、logo、比例失真、玩具蛇。"""

G01_PROMPT = """16:9 四宫格分镜预演图，2×2 等分，每格 16:9，细白分隔线；四格按左上→右上→左下→右下顺序，同一角色、同一暖光；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），全图无文字/字幕/logo/水印。
左上：蛋仔客厅（参考 {{A02}}），心易（粉蛋，参考 {{R02}}）举词卡，黄蛋（参考 {{R01}}）抱着小石头（参考 {{A01}}）摆“坚固”姿势。
右上：小区公园石桌（参考 {{A03}}），石桌特写、落灰。
左下：回到客厅/阳台方向（参考 {{A04}}），黄蛋做蛇形波浪手臂动作，小蛇（参考 {{A06}}）从花盆间探出。
右下：玄关（参考 {{A05}}），金毛摇尾。
四格角色/动物一致，不新增角色；快节奏甩镜/直接转场，不是慢摇。
负向：文字、字幕、水印、logo、人类、手指、牙齿、裂壳、蛋液、蛋黄、多余角色、分格错位、角色变形、动物变恐怖、玩具蛇、塑料高光过强、卡通描边、过曝。"""

KA_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。蛋仔客厅（光线与机位跟 {{A02}} 一致）：双人中景，黄蛋（参考 {{R01}} 外形、{{R00}} 比例）在画面左 1/3，怀里抱着一块灰色小石头（参考 {{A01}}），摆出“坚固”的姿势；心易（参考 {{R02}}，粉蛋形象）在画面右 1/3，举着一张空白词卡（参考 {{A01}}）；茶几上有三张空白词卡。低机位，午后暖光，3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo；词卡留白。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、词卡文字、动物提前出现、多余角色、过曝。"""

KB_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态）。蛋仔客厅/玄关（同 {{A02}}）：双人中景，黄蛋（参考 {{R01}}）在画面左 1/3，手里拿着红色狗绳（参考 {{A01}}），摆出“忠诚/摇尾”的姿势；心易（参考 {{R02}}，粉蛋形象）在画面右 1/3，举着空白词卡；背景有鞋柜/狗窝/门口地垫。低机位，暖光，3D 卡通渲染+真实光影。
无文字浮层、无水印、无 logo；词卡留白。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、词卡文字、狗提前出现、多余角色、过曝。"""

KC_PROMPT = """16:9 三张词卡摆在木茶几上，只生成一张。三张等大、略错落；米白卡片、浅灰边；每张写：第一张“rocklike / 像石头一样（坚固的）”；第二张“snakelike / 像蛇一样（蜿蜒的）”；第三张“doglike / 像狗一样（忠诚的）”。黑色手写感字，红色关键词。客厅背景虚化，午后暖光。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、文字重叠、串卡。"""

PART_A_PROMPT = """【风格】蛋仔的日常：客厅＋小区石桌＋阳台＋玄关；快节奏、有动感；不是慢速横移、不是照相馆、不是武林。镜头快推、甩镜、急停、低角度、远到近；甩镜或直接切到下一个日常场景。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿；负责摆pose/做动作。
【心易】本集用粉蛋形象出演（参考 {{R02}}）：12cm 粉色蛋仔，粉色蛋壳、奶油色椭圆脸板、大圆眼、短圆手臂无手指、白色圆脚；老师/提问者，举词卡。
【动物】小狗：金毛（Part B 出现），热情摇尾；小蛇：真实可爱小蛇（参考 {{A06}}），圆头大眼、无尖牙、绿色鳞片，从花盆间蜿蜒滑出；不开口。
【道具】A01：灰色小石头、红色狗绳、三张空白词卡；A02：客厅；A03：公园石桌；A04：阳台花园；A05：玄关金毛；A06：小蛇。
【场景与尺度】客厅双人中景低机位，两蛋同高、各约占画面高 1/4；日常场景低机位、主体占画面 2/3；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=三道具；{{A02}}=客厅；{{A03}}=公园石桌；{{A04}}=阳台花园；{{A06}}=小蛇。
0–1 秒：{{K_A}}{{R02}}{{A02}}客厅双人中景；心易举词卡快推近：“rocklike 是什么？”
1–3 秒：{{R01}}{{A01}}甩镜到黄蛋；他抱着小石头，摆出僵硬/坚固的姿势：“rocklike 像石头一样，坚固的！”
3–4.5 秒：{{A03}}甩镜或直接转到小区公园石桌；手掌拍石桌，石头一震、落灰；心易画外：“像石头一样，坚固的！”
4.5–5.5 秒：甩回客厅；心易：“snakelike 是什么？”
5.5–7.5 秒：{{R01}}{{A06}}黄蛋整条手臂做蛇形波浪，指向阳台方向：“snakelike 像蛇一样，蜿蜒的！”
7.5–9 秒：{{A04}}{{A06}}甩镜/直接转到阳台花园；小蛇从花盆间蜿蜒滑出、绕浇水壶；心易画外：“像蛇一样，蜿蜒的！”
9–10.5 秒：甩回客厅；心易：“真不错！最后一个——doglike！”
10.5–12 秒：{{R01}}{{A01}}黄蛋举起红色狗绳，摆出“忠诚/摇尾”姿势；镜尾定格 1 秒。
【声音】甩镜风声、石头落灰、蛇滑过花盆、心易提问/画外词义、黄蛋三次回答；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、慢速横移、环绕、渐变、白场、照相馆、闪光、玩具蛇、水管、动物说人话、动物变恐怖、文字浮层、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

PART_B_PROMPT = """【风格】蛋仔的日常：客厅/玄关；快节奏；不是慢速横移、不是照相馆、不是武林。镜头快推、甩镜、急停、低角度；甩镜或直接切到玄关。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿。
【心易】粉蛋形象（参考 {{R02}}）：粉色蛋壳、奶油色脸板、大圆眼、白色圆脚；老师/提问者，举词卡。
【动物】金毛（参考 {{A05}}），从门口跑进来、摇尾/吐舌；不开口。
【道具】A01：红色狗绳、空白词卡；A02：客厅；A05：玄关金毛；KC：三张词卡版式（后期贴）。
【场景与尺度】客厅/玄关双人中景低机位，两蛋同高；玄关金毛占画面 2/3；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=狗绳/词卡；{{A02}}=客厅；{{A05}}=玄关金毛；{{KC}}=三张词卡版式（后期贴）。
0–1 秒：{{K_B}}{{R02}}客厅/玄关双人中景；心易举词卡：“doglike 是什么？”
1–3 秒：{{R01}}{{A01}}黄蛋拿着红色狗绳，做“忠诚/摇尾”姿势：“doglike 像狗一样，忠诚的！”
3–4.5 秒：{{A05}}甩镜/直接转到玄关；金毛从门口跑进来、摇尾/吐舌；心易画外：“像狗一样，忠诚的！”
4.5–5.5 秒：甩回客厅；心易：“真棒！”
5.5–9 秒：{{A02}}{{KC}}三张空白词卡摆在茶几上；心易画外逐个复习：rocklike 像石头一样（坚固的）／snakelike 像蛇一样（蜿蜒的）／doglike 像狗一样（忠诚的）；黄蛋逐个点头；卡面留白，后期贴 KC。
9–12 秒：{{R01}}{{R02}}两人一起：“你记住了多少？”；三张词卡定格；镜尾定格 1.5 秒。
【声音】甩镜风声、金毛喘气/摇尾、心易复习、两人“你记住了多少”；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、慢速横移、环绕、渐变、白场、照相馆、闪光、玩具蛇、水管、动物说人话、动物变恐怖、词卡文字、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

NOTES = """【本画布做什么】
《蛋仔记单词》-like 三词样片「蛋仔的日常」：rocklike／snakelike／doglike，2×12s（24s）。
客厅提问＋小区石桌/阳台小花园/玄关；甩镜/直接转场；小蛇是真实可爱小蛇（A06），不是玩具蛇/水管。
不是照相馆，不是武林，不是慢速横移。

【运行顺序】
1. 先跑 A01 三道具、A02 客厅、A03 公园石桌、A04 阳台、A05 玄关金毛、A06 小蛇（互不依赖，可同跑）。
2. 跑 G01 四宫格；看“客厅→石桌/阳台/玄关”的甩镜/转场节奏。G01 只做预演，不进视频。
3. 跑 K_A（客厅首帧：黄蛋抱石、心易举词卡）、K_B（玄关首帧：黄蛋拿狗绳）、KC（三张词卡版式）。
4. 跑 Part A（12s，首帧 K_A）；看完：甩镜是否干净、石桌/小蛇是否切到、动作是否有动感。
5. 跑 Part B（12s，首帧 K_B）；看完：金毛、三张词卡、两人“你记住了多少”。
6. 后期：三张词卡后期贴 KC；字幕/黑幕卡/钩子后期贴。

【角色口径】
- 黄蛋天线+圆球是本体，不可拆；不做鸟叼天线球。
- 蛋仔没有牙齿，不敲壳/剥壳/煮煎/蛋液；石头可以拍，蛋身不裂。
- 心易用粉蛋；短手臂举词卡/狗绳。
- 小蛇：真实可爱小蛇，圆头大眼、无尖牙、不恐怖；不是玩具蛇、不是水管。
- 金毛：真实可爱金毛；不开口。

【节奏】
- 快推、甩镜、急停、低角度、远到近；甩镜/直接切到下一个日常场景；不要慢速横移/环绕/白场。
- 每个词 5–6s：Q 1s → A 2s → 甩镜/场景 1.5s → 甩回 0.5–1s。
- 24s 是样片；成立后扩 8 词（4×12s≈48s）。

【风险】
- 甩镜到另一个场景，Seedance 可能做成瞬移/糊成一片；第一条先看“甩出去—落下”是否干净。
- 若甩镜不稳，改“每个词一条 6s 视频＋后期甩镜/切”，或把日常场景做成独立插入镜头。
- 词卡文字不要交给视频模型，后期贴 KC。
"""


def link(text: str) -> str:
    tokens = ("R00", "R01", "R02", "A01", "A02", "A03", "A04", "A05", "A06", "G01", "K_A", "K_B", "KC")
    for token in tokens:
        text = text.replace("{{" + token + "}}", "{{" + nid(token) + "}}")
    leftovers = re.findall(r"\{\{(?!node-)[^}]+\}\}", text)
    if leftovers:
        raise SystemExit(f"unreplaced tokens: {leftovers}")
    if "{{node-node-" in text:
        raise SystemExit("double prefix {{node-node-")
    return text


def main():
    nodes = []
    nodes.append(make_input_image("R00", "R00 四小只身高比例（复用）", R00, 0, 0, width=300))
    nodes.append(make_input_image("R01", "R01 黄蛋标准（复用）", R01, 0, 200, width=280))
    nodes.append(make_input_image("R02", "R02 粉蛋标准 · 本集代心易（复用）", R02, 0, 560, width=280))

    nodes.append(make_gen_image("A01", "【待生成】A01 三道具 · 石头/狗绳/词卡 · 1K", link(A01_PROMPT), [], 360, 0))
    nodes.append(make_gen_image("A02", "【待生成】A02 蛋仔客厅 · 1K", link(A02_PROMPT), [], 360, 200))
    nodes.append(make_gen_image("A03", "【待生成】A03 小区公园石桌 · 1K", link(A03_PROMPT), [], 360, 400))
    nodes.append(make_gen_image("A04", "【待生成】A04 阳台小花园 · 1K", link(A04_PROMPT), [], 360, 600))
    nodes.append(make_gen_image("A05", "【待生成】A05 玄关＋金毛 · 1K", link(A05_PROMPT), [], 360, 800))
    nodes.append(make_gen_image("A06", "【待生成】A06 小蛇设定 · 真实可爱小蛇 · 1K", link(A06_PROMPT), [], 360, 1000))
    nodes.append(make_gen_image("G01", "【待生成】G01 四宫格 · 客厅/石桌/阳台小蛇/玄关 · 1K",
                                link(G01_PROMPT), ["R00", "R01", "R02", "A01", "A02", "A03", "A04", "A05", "A06"], 740, 0, height=170.0))
    nodes.append(make_gen_image("K_A", "【待生成】K_A Part A 首帧 · 黄蛋抱石/心易词卡 · 1K",
                                link(KA_PROMPT), ["G01", "R00", "R01", "R02", "A01", "A02"], 1140, 0, height=170.0))
    nodes.append(make_gen_image("K_B", "【待生成】K_B Part B 首帧 · 黄蛋拿狗绳/心易词卡 · 1K",
                                link(KB_PROMPT), ["G01", "R00", "R01", "R02", "A01", "A02"], 1140, 220, height=170.0))
    nodes.append(make_gen_image("KC", "【待生成】KC 三张词卡 · rocklike/snakelike/doglike · 1K",
                                link(KC_PROMPT), [], 1140, 440, height=170.0))

    part_a = link(PART_A_PROMPT)
    part_b = link(PART_B_PROMPT)
    for name, p in (("Part A", part_a), ("Part B", part_b)):
        if len(p) > 1900:
            raise SystemExit(f"{name} prompt {len(p)} chars > 1900 target (hard 2000)")

    nodes.append(make_gen_video(
        "V1", "【待生成】Part A · 12s · rocklike＋snakelike＋doglike 预告",
        part_a, ["R00", "R01", "R02", "A01", "A02", "A03", "A04", "A06"], "K_A", 1580, 0, duration=12,
    ))
    nodes.append(make_gen_video(
        "V2", "【待生成】Part B · 12s · doglike＋三张词卡＋收尾",
        part_b, ["R00", "R01", "R02", "A01", "A02", "A05", "KC"], "K_B", 1580, 300, duration=12,
    ))

    nodes.append(make_text("S0", "S0 制作说明 · 先读", NOTES, 740, 760))

    edges, seen = [], set()

    def edge(a, b):
        if (a, b) in seen:
            raise SystemExit(f"duplicate edge {a}->{b}")
        seen.add((a, b))
        edges.append({
            "id": "edge-" + hashlib.md5((a + ">" + b).encode("utf-8")).hexdigest()[:8],
            "sourceNodeId": a, "sourceHandle": "output",
            "targetNodeId": b, "targetHandle": "input",
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        })

    for n in nodes:
        if n["type"] == "gen-video":
            mp = n["params"]["model_params"]
            for r in mp["reference_images"]:
                edge(r["node_id"], n["id"])
            edge(mp["first_frame_image"]["node_id"], n["id"])
        elif n["type"] == "gen-image":
            for r in n["params"]["model_params"]["reference_images"]:
                edge(r["node_id"], n["id"])

    def group(key, label, keys, color, pad=30):
        ns = [next(n for n in nodes if n["id"] == nid(k)) for k in keys]
        x0 = min(n["meta"]["x"] for n in ns) - pad
        y0 = min(n["meta"]["y"] for n in ns) - pad
        x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
        y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
        return {
            "id": "group-" + hashlib.md5((PREFIX + ":group:" + key).encode("utf-8")).hexdigest()[:8],
            "nodeIds": [nid(k) for k in keys],
            "bounds": {"x": float(x0), "y": float(y0),
                       "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label,
            "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        }

    groups = [
        group("g00", "00 参考素材 · 黄蛋/粉蛋/身高比例", ["R00", "R01", "R02"], "#E68BB3"),
        group("g01", "01 道具/客厅/石桌/阳台/玄关/小蛇 · 先跑", ["A01", "A02", "A03", "A04", "A05", "A06"], "#8E8DE0"),
        group("g02", "02 四宫格预演 · G01 先跑", ["G01"], "#C9A227"),
        group("g03", "03 首帧/词卡 · K_A、K_B、KC", ["K_A", "K_B", "KC"], "#E8B85D"),
        group("g04", "04 视频 Part A · 12s", ["V1"], "#DC775D"),
        group("g05", "05 视频 Part B · 12s", ["V2"], "#DC775D"),
        group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
    ]

    ids = {n["id"] for n in nodes}
    assert len(ids) == len(nodes)
    by_id = {n["id"]: n for n in nodes}
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        prompt = mp["prompt"]
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt):
            assert tok in by_id, f"missing token target {tok}"
            assert tok in refs or tok == ff, f"token {tok} not in refs/ff"
        for r in refs + ([ff] if ff else []):
            assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
            if by_id[r]["type"] == "input-image":
                assert by_id[r]["outputs"], f"empty input-image {by_id[r]['meta']['label']}"
        assert not mp.get("reference_audios"), "reference_audios must be empty"
        if n["type"] == "gen-video":
            d = mp["duration"]
            assert isinstance(d, int) and 3 <= d <= 16
            assert ff in prompt, "first frame not named in prompt"
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by:
                raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
    grouped = [i for g in groups for i in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids), "group coverage mismatch"

    canvas = {
        "schemaVersion": 2,
        "type": "monet.canvas",
        "exportedAt": NOW,
        "canvas": {
            "name": "蛋仔记单词 · -like 三词样片「蛋仔的日常」v1 · 2×12s",
            "description": "三词样片：rocklike／snakelike／doglike；客厅提问＋小区石桌/阳台小花园/玄关；甩镜/直接转场；小蛇是真实可爱小蛇，不是玩具蛇。",
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / "EP02-like-daily-pilot-v1.monet"
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"{out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"Part A {len(part_a)} chars / Part B {len(part_b)} chars")
    print(f"-> {out}")
    print(f"-> {downloads}")


if __name__ == "__main__":
    main()


