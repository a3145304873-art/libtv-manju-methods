# -*- coding: utf-8 -*-
"""Build 蛋仔记单词 · -like 三词样片「蛋仔的小院」Monet canvas.

Correction: no long whip to distant empty scenes. One everyday courtyard,
three corners; characters are at the location; camera points to the stone /
snake / dog in the same space, with the character still in frame.

Words: rocklike / snakelike / doglike.
Videos: 8s + 8s + 10s = 26s.
Snake: a real cute small snake (A03), not toy/hose.
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
PREFIX = "egg-like-yard-pilot:v3"
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
    "url": "https://tmpfiles.org/dl/1793353000.77611c27214c9179/wfAJHlmhfBvq/--.png",
    "name": "心易-猫耳版-白底.png",
    "width": 1254, "height": 1254, "size": 679469,
    "md5": "f178c73ec700fe30ef24d9b37ad307e4520d1efe25e5c5ae58d4123b06cd0e38",
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


def make_gen_video(key, label, prompt, ref_keys, ff_key, x, y, duration=8):
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


A01_PROMPT = """16:9 纯白底道具设定图，两个道具并排：①一条红色狗绳；②三张空白词卡（米白卡片、浅灰边）。3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo、无手。
负向：真实照片、恐怖、人类、手指、文字、水印、logo、比例失真。"""

A02_PROMPT = """16:9 蛋仔家的小院，一个完整院子：左侧圆石桌/石凳，右侧花坛/花盆/浇水壶，后方狗窝/狗绳挂钩/门口地垫，中间草地/石板路，午后暖光；低机位；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），柔和景深。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

A03_PROMPT = """16:9 纯白底角色设定图，只生成一只小蛇：圆头、大眼、绿色鳞片、浅黄肚皮、小小的分叉舌头；可爱、无尖牙、不恐怖；身体盘成一圈、微微抬头；体长约蛋仔 2–3 倍；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo、无手。
负向：真实蛇、恐怖、尖牙、毒牙、人类、手指、文字、水印、logo、比例失真、玩具蛇。"""

A04_PROMPT = """16:9 纯白底角色设定图，只生成一只金毛犬：坐姿、摇尾、吐舌、可爱；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo、无手。
负向：真实照片、恐怖、人类、手指、文字、水印、logo、比例失真。"""

G01_PROMPT = """16:9 四宫格分镜预演图，2×2 等分，每格 16:9，细白分隔线；四格按左上→右上→左下→右下顺序，同一小院、同一角色、同一暖光；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质），全图无文字/字幕/logo/水印。
左上：小院石桌角（参考 {{A02}}），黄蛋（参考 {{R01}}）在石桌旁拍桌，心易（白色猫耳蛋仔，参考 {{R02}}）举词卡。
右上：小院花坛角（参考 {{A02}}），黄蛋在花坛旁，小蛇（参考 {{A03}}）从花丛滑出。
左下：小院狗窝/门口角（参考 {{A02}}），黄蛋拿狗绳（参考 {{A01}}），金毛（参考 {{A04}}）在狗窝旁摇尾。
右下：小院桌上三张空白词卡（参考 {{A01}}）。
四格人物/动物一致，不新增角色；镜头短推/下摇指向对象，人物仍在画面里。
负向：文字、字幕、水印、logo、人类、手指、牙齿、裂壳、蛋液、蛋黄、多余角色、分格错位、角色变形、动物变恐怖、玩具蛇、塑料高光过强、卡通描边、过曝。"""

KA_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。小院石桌角（光线与机位跟 {{A02}} 一致）：双人中景，黄蛋（参考 {{R01}} 外形、{{R00}} 比例）在画面左 1/3，手掌按在圆石桌上，摆“坚固”姿势；心易（参考 {{R02}}，白色猫耳蛋仔）在画面右 1/3，举着一张空白词卡；背景有树/花盆/小院。低机位，午后暖光，3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo；词卡留白。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、心易变形、词卡文字、动物提前出现、多余角色、过曝。"""

KB_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 右上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。小院花坛角（同 {{A02}}）：双人中景，黄蛋（参考 {{R01}}）在画面左 1/3，整条手臂做蛇形波浪、指向花坛；心易（参考 {{R02}}，白色猫耳蛋仔）在画面右 1/3，举着空白词卡；花丛里有一只小蛇（参考 {{A03}}，圆头大眼、无尖牙、可爱）。低机位，暖光，3D 卡通渲染+真实光影。
无文字浮层、无水印、无 logo；词卡留白。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、心易变形、词卡文字、恐怖蛇、尖牙、玩具蛇、多余角色、过曝。"""

K_C_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左下格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。小院狗窝/门口角（同 {{A02}}）：双人中景，黄蛋（参考 {{R01}} 外形、{{R00}} 比例）在画面左 1/3，手里拿着红色狗绳（参考 {{A01}}），摆出“忠诚/摇尾”的姿势；心易（参考 {{R02}}，白色猫耳蛋仔）在画面右 1/3，举着空白词卡；狗窝旁坐着一只金毛（参考 {{A04}}，摇尾/吐舌）。低机位，午后暖光，3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo；词卡留白。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、心易变形、词卡文字、多余角色、过曝。"""

KC_PROMPT = """16:9 三张词卡摆在木桌上，只生成一张。三张等大、略错落；米白卡片、浅灰边；每张写：第一张“rocklike / 像石头一样（坚固的）”；第二张“snakelike / 像蛇一样（蜿蜒的）”；第三张“doglike / 像狗一样（忠诚的）”。黑色手写感字，红色关键词。小院背景虚化，午后暖光。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、文字重叠、串卡。"""

KC_PROMPT_2 = """16:9 三张词卡摆在木桌上，只生成一张。三张等大、略错落；米白卡片、浅灰边；每张写：第一张“rocklike / 像石头一样（坚固的）”；第二张“snakelike / 像蛇一样（蜿蜒的）”；第三张“doglike / 像狗一样（忠诚的）”。黑色手写感字，红色关键词。小院背景虚化，午后暖光。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、文字重叠、串卡。"""

# KC_PROMPT_2 is identical; kept for readability only.

PART_A_PROMPT = """【风格】蛋仔家的小院，三个角落；人物在场景里，镜头只做短推/下摇/侧移指向对象；不甩到远处、不切空景/画外物体。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿；在石桌旁拍桌。
【心易】心易（参考 {{R02}}，白色猫耳蛋仔）：白色/奶油色蛋壳；猫耳兜帽（耳内黄色）；头顶金白小呆毛；兜帽上有猫脸（棕色鼻子/嘴、两颊小棕点）；奶油色椭圆大脸板、橙金色大眼、张嘴笑/粉舌；短白手臂带金色条纹；肚皮金色 V 徽记、金色锯齿边；白色金边靴。心易提问、黄蛋回答。
【场景】小院石桌角：圆石桌/石凳、树、花盆、午后暖光；低机位；黄蛋和心易都在画面里。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=心易猫耳版；{{A02}}=小院。
0–1 秒：{{K_A}}{{R02}}石桌旁双人中景；心易举词卡快推近：“rocklike 是什么？”
1–3 秒：{{R01}}黄蛋手掌按在圆石桌上，摆出僵硬/坚固的姿势：“rocklike 像石头一样，坚固的！”
3–4.5 秒：镜头短推/下摇到石桌；黄蛋的手还在画面边缘/桌上；石桌一震、落灰；不要切到空景/画外物体。
4.5–6 秒：镜头回黄蛋/心易；心易：“真不错！”。
6–8 秒：黄蛋转身朝花坛方向走两步；镜尾停在他迈步。
【声音】推镜、石头落灰、心易提问/夸奖、黄蛋回答；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、字幕、水印、logo、比例失真、黄蛋变色、心易变形、长距离甩镜、瞬移、空景、画外物体、慢速横移、环绕、渐变、白场、照相馆、闪光、玩具蛇、水管、动物说人话、多余角色、塑料高光过强、卡通描边、过曝、漂浮。"""

PART_B_PROMPT = """【风格】蛋仔家的小院，花坛角；人物在场景里，小蛇在同一个花坛里；镜头短推/下摇指向小蛇，人物仍在画面里/边缘；不切空景/画外物体。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿；整臂做蛇形波浪。
【心易】心易（参考 {{R02}}，白色猫耳蛋仔）：白色/奶油色蛋壳；猫耳兜帽（耳内黄色）；头顶金白小呆毛；兜帽上有猫脸（棕色鼻子/嘴、两颊小棕点）；奶油色椭圆大脸板、橙金色大眼、张嘴笑/粉舌；短白手臂带金色条纹；肚皮金色 V 徽记、金色锯齿边；白色金边靴。心易提问、黄蛋回答。
【小蛇】真实可爱小蛇（参考 {{A03}}）：圆头大眼、绿色鳞片、浅黄肚皮、无尖牙、不恐怖；在花丛里蜿蜒滑出；不开口。
【场景】小院花坛角：一排花盆、绿植、浇水壶、午后暖光；低机位；黄蛋/心易/小蛇在同一空间。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=心易猫耳版；{{A02}}=小院；{{A03}}=小蛇。
0–1 秒：{{K_B}}{{R02}}花坛旁双人中景；心易：“snakelike 是什么？”
1–3 秒：{{R01}}{{A03}}黄蛋整条手臂做蛇形波浪、指向花坛：“snakelike 像蛇一样，蜿蜒的！”
3–4.5 秒：镜头下摇/短推到花坛；黄蛋的手还在画面边缘；小蛇从花丛间蜿蜒滑出；不要切到空景/画外物体。
4.5–6 秒：镜头回黄蛋/心易；心易：“真棒！”。
6–8 秒：黄蛋转身朝狗窝方向走两步；镜尾停在他迈步。
【声音】推镜、蛇滑过花丛、心易提问/夸奖、黄蛋回答；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、字幕、水印、logo、比例失真、黄蛋变色、心易变形、长距离甩镜、瞬移、空景、画外物体、慢速横移、环绕、渐变、白场、照相馆、闪光、玩具蛇、水管、恐怖蛇、尖牙、动物说人话、多余角色、塑料高光过强、卡通描边、过曝、漂浮。"""

PART_C_PROMPT = """【风格】蛋仔家的小院，狗窝/门口角；人物在场景里，金毛在同一个空间；镜头短推/下摇指向金毛，人物仍在画面里/边缘；不切空景/画外物体；最后三张词卡。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿；举狗绳。
【心易】心易（参考 {{R02}}，白色猫耳蛋仔）：白色/奶油色蛋壳；猫耳兜帽（耳内黄色）；头顶金白小呆毛；兜帽上有猫脸（棕色鼻子/嘴、两颊小棕点）；奶油色椭圆大脸板、橙金色大眼、张嘴笑/粉舌；短白手臂带金色条纹；肚皮金色 V 徽记、金色锯齿边；白色金边靴。心易提问、黄蛋回答。
【金毛】真实可爱金毛（参考 {{A04}}）：坐姿、摇尾、吐舌；不开口。
【场景】小院狗窝/门口角：狗窝、狗绳挂钩、门口地垫、午后暖光；低机位；黄蛋/心易/金毛在同一空间。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=心易猫耳版；{{A01}}=狗绳/词卡；{{A02}}=小院；{{A04}}=金毛；{{KC}}=三张词卡版式（后期贴）。
0–1 秒：{{K_C}}{{R02}}狗窝旁双人中景；心易：“doglike 是什么？”
1–3 秒：{{R01}}{{A01}}黄蛋举起红色狗绳，摆出“忠诚/摇尾”姿势：“doglike 像狗一样，忠诚的！”
3–4.5 秒：镜头短推/下摇到狗窝/门口；黄蛋在画面边缘；金毛摇尾/吐舌；不要切到空景/画外物体。
4.5–6 秒：镜头回黄蛋/心易；心易：“真棒！”。
6–9 秒：{{A02}}{{KC}}三张空白词卡摆在小院桌上；心易画外复习：rocklike 像石头一样（坚固的）／snakelike 像蛇一样（蜿蜒的）／doglike 像狗一样（忠诚的）；黄蛋点头；卡面留白，后期贴 KC。
9–10 秒：{{R01}}{{R02}}两人一起：“你记住了多少？”；三张词卡定格；镜尾定格 1.5 秒。
【声音】推镜、金毛喘气/摇尾、心易复习、两人“你记住了多少”；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、心易变形、长距离甩镜、瞬移、空景、画外物体、慢速横移、环绕、渐变、白场、照相馆、闪光、玩具蛇、水管、动物说人话、词卡文字、多余角色、塑料高光过强、卡通描边、过曝、漂浮。"""

NOTES = """【本画布做什么】
《蛋仔记单词》-like 三词样片「蛋仔的小院」：rocklike／snakelike／doglike，8＋8＋10s＝26s。
一个日常小院三个角落：石桌/花坛/狗窝；人物在场景里，镜头只做短推/下摇/侧移指向石桌/小蛇/金毛；不甩到远处、不切空景/画外物体。
小蛇是真实可爱小蛇（A03），不是玩具蛇/水管。

【运行顺序】
1. 先跑 A01 道具、A02 小院、A03 小蛇、A04 金毛（互不依赖，可同跑）。
2. 跑 G01 四宫格；看“石桌/花坛/狗窝”三个角落和人物位置。G01 只做预演，不进视频。
3. 跑 K_A（石桌首帧）、K_B（花坛首帧，含小蛇）、K_C（狗窝首帧，含金毛）、KC（三张词卡版式）。
4. 跑 V1（8s，首帧 K_A）；看镜头短推/下摇到石桌时，黄蛋的手/人是否还在画面里。
5. 跑 V2（8s，首帧 K_B）；看下摇到花坛时，小蛇是否在同一空间滑出、人物是否还在边缘。
6. 跑 V3（10s，首帧 K_C）；看金毛、三张词卡、两人“你记住了多少”。
7. 后期：三张词卡后期贴 KC；字幕/黑幕卡/钩子后期贴。

【角色口径】
- 黄蛋天线+圆球是本体，不可拆；没有牙齿；不敲壳/剥壳/煮煎/蛋液；石桌可以拍，蛋身不裂。
- 心易用白色猫耳蛋仔（R02），提问；黄蛋回答；短手臂举词卡/狗绳。
- 小蛇：真实可爱小蛇，圆头大眼、无尖牙、不恐怖；不是玩具蛇、不是水管。
- 金毛：真实可爱金毛；不开口。

【运镜】
- 人物在场景里；镜头短推/下摇/侧移指向对象；人物留在画面里/边缘；不切空景/画外物体。
- 三条视频之间是剪辑点；每条开头人物已在对应角落；不靠长甩镜连接。
- 不要慢速横移/环绕/白场/闪光。

【风险】
- 模型可能把“下摇到石桌/小蛇/金毛”做成切到空景；第一条先看人物是否还在画面里。
- 若人物被切走，改“人物蹲下/伸手入画”的构图，保证人和对象同框。
- 26s 是样片；成立后扩 8 词，按“一个院子多个角落”排。
"""


def link(text: str) -> str:
    tokens = ("R00", "R01", "R02", "A01", "A02", "A03", "A04", "G01", "K_A", "K_B", "K_C", "KC")
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
    nodes.append(make_input_image("R02", "R02 心易·猫耳版（内嵌图）", R02, 0, 560, width=280))

    nodes.append(make_gen_image("A01", "【待生成】A01 道具 · 狗绳/三张词卡 · 1K", link(A01_PROMPT), [], 360, 0))
    nodes.append(make_gen_image("A02", "【待生成】A02 小院 · 石桌/花坛/狗窝 · 1K", link(A02_PROMPT), [], 360, 200))
    nodes.append(make_gen_image("A03", "【待生成】A03 小蛇设定 · 真实可爱小蛇 · 1K", link(A03_PROMPT), [], 360, 400))
    nodes.append(make_gen_image("A04", "【待生成】A04 金毛设定 · 1K", link(A04_PROMPT), [], 360, 600))
    nodes.append(make_gen_image("G01", "【待生成】G01 四宫格 · 石桌/花坛小蛇/狗窝金毛/词卡 · 1K",
                                link(G01_PROMPT), ["R00", "R01", "R02", "A01", "A02", "A03", "A04"], 740, 0, height=170.0))
    nodes.append(make_gen_image("K_A", "【待生成】K_A V1 首帧 · 石桌旁黄蛋拍桌/心易词卡 · 1K",
                                link(KA_PROMPT), ["G01", "R00", "R01", "R02", "A02"], 1140, 0, height=170.0))
    nodes.append(make_gen_image("K_B", "【待生成】K_B V2 首帧 · 花坛旁黄蛋蛇形/心易词卡/小蛇 · 1K",
                                link(KB_PROMPT), ["G01", "R00", "R01", "R02", "A02", "A03"], 1140, 200, height=170.0))
    nodes.append(make_gen_image("K_C", "【待生成】K_C V3 首帧 · 狗窝旁黄蛋狗绳/心易词卡/金毛 · 1K",
                                link(K_C_PROMPT), ["G01", "R00", "R01", "R02", "A01", "A02", "A04"], 1140, 400, height=170.0))
    nodes.append(make_gen_image("KC", "【待生成】KC 三张词卡 · rocklike/snakelike/doglike · 1K",
                                link(KC_PROMPT), [], 1140, 640, height=170.0))

    v1 = link(PART_A_PROMPT)
    v2 = link(PART_B_PROMPT)
    v3 = link(PART_C_PROMPT)
    for name, p in (("V1", v1), ("V2", v2), ("V3", v3)):
        if len(p) > 1900:
            raise SystemExit(f"{name} prompt {len(p)} chars > 1900 target (hard 2000)")

    nodes.append(make_gen_video(
        "V1", "【待生成】V1 · 8s · rocklike · 石桌角",
        v1, ["R00", "R01", "R02", "A02"], "K_A", 1580, 0, duration=8,
    ))
    nodes.append(make_gen_video(
        "V2", "【待生成】V2 · 8s · snakelike · 花坛角",
        v2, ["R00", "R01", "R02", "A02", "A03"], "K_B", 1580, 300, duration=8,
    ))
    nodes.append(make_gen_video(
        "V3", "【待生成】V3 · 10s · doglike＋三张词卡＋收尾",
        v3, ["R00", "R01", "R02", "A01", "A02", "A04", "KC"], "K_C", 1580, 600, duration=10,
    ))

    nodes.append(make_text("S0", "S0 制作说明 · 先读", NOTES, 740, 900))

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
        group("g00", "00 参考素材 · 黄蛋/心易/身高比例", ["R00", "R01", "R02"], "#E68BB3"),
        group("g01", "01 道具/小院/小蛇/金毛 · 先跑", ["A01", "A02", "A03", "A04"], "#8E8DE0"),
        group("g02", "02 四宫格预演 · G01 先跑", ["G01"], "#C9A227"),
        group("g03", "03 首帧/词卡 · K_A、K_B、K_C、KC", ["K_A", "K_B", "K_C", "KC"], "#E8B85D"),
        group("g04", "04 视频 V1 · 8s · rocklike", ["V1"], "#DC775D"),
        group("g05", "05 视频 V2 · 8s · snakelike", ["V2"], "#DC775D"),
        group("g06", "06 视频 V3 · 10s · doglike＋收尾", ["V3"], "#DC775D"),
        group("g07", "07 制作说明 · 先读", ["S0"], "#7FB07F"),
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
            "name": "蛋仔记单词 · -like 三词样片「蛋仔的小院」v3 · 8＋8＋10s",
            "description": "三词样片：rocklike／snakelike／doglike；一个小院三个角落（石桌/花坛/狗窝），人物在场景里，镜头短推/下摇指向对象；不甩到远处、不切空景/画外物体。",
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / "EP02-like-yard-pilot-v3.monet"
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"{out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"V1 {len(v1)} / V2 {len(v2)} / V3 {len(v3)} chars")
    print(f"-> {out}")
    print(f"-> {downloads}")


if __name__ == "__main__":
    main()


