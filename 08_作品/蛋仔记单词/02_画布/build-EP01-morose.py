# -*- coding: utf-8 -*-
"""Build 蛋仔记单词·谐音无厘头 EP01《morose＝没肉丝》Monet canvas.

Story (reskinned from B站 BV1cZnR6yEe9, 31s):
  黄蛋在蛋仔快餐店点“青椒肉丝饭，肉丝多一点”→ 打开只有青椒 →
  拨找 → 心易举卡 morose／没肉丝 → 黄蛋把青椒摆成“肉丝”形状，还是闷闷不乐。

1 word / 30s (2×15s)；Part A 点单/期待/落空，Part B 拨找/揭底/收梗。

Outputs:
  02_画布/EP01-morose-v1.monet
  ~/Downloads/EP01-morose-v1.monet

Rules per I06: node ids md5(prefix+key)[:8]; edges derived from
reference_images/first_frame; groups = run order; every {{node-x}} has
both a ref slot and an edge; no video->video, no audio->video.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent          # 02_画布
OUT = HERE
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "egg-homo-ep01-morose:v1"
IMAGE_MODEL = "gpt-image-2"
VIDEO_MODEL = "seedance-2.0-mini"

R00 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035437-5241228d6d235662-r00-e5-9b-9b-e5-b0-8f-e5-8f-aa-e8-ba-ab.jpg",
    "name": "R00-四小只身高比例.jpg",
    "width": 1600, "height": 650, "size": 77895,
    "md5": "b321a4a46247edafe03ddd2dc85b3605",
}
R01 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035438-8a7a8cba5091bb94-e8-a7-92-e8-89-b2-e9-bb-84-e8-9b-8b-e6-a.jpg",
    "name": "角色-黄蛋-标准.jpg",
    "width": 1118, "height": 1280, "size": 86469,
    "md5": "7939d7b1ed7e0315344a5eb2c13e6d1a",
}
R02 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035437-0d34f1caae5e8c3e-e8-a7-92-e8-89-b2-e7-b2-89-e8-9b-8b-e6-a.jpg",
    "name": "角色-粉蛋-标准.jpg",
    "width": 1117, "height": 1280, "size": 97490,
    "md5": "51dda2189f378bc9c464076bdeb31dc3",
}
T_A = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261023-081313-b0296f5161341655-t-a-e5-8d-a0-e4-bd-8d-1280x720.jpg",
    "name": "T_A-占位-1280x720.jpg",
    "width": 1280, "height": 720, "size": 59049,
    "md5": "731a5a04d57f812140cfd6c5e6301ce3",
}


def nid(key: str) -> str:
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode("utf-8")).hexdigest()[:8]


def oid(kind: str, key: str) -> str:
    return "output-" + hashlib.md5((PREFIX + ":" + kind + ":" + key).encode("utf-8")).hexdigest()[:10]


def make_input_image(key, label, info, x, y, width=320.0):
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


def make_gen_image(key, label, prompt, ref_keys, x, y, width=320.0, height=207.0):
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


def make_gen_video(key, label, prompt, ref_keys, ff_key, x, y, duration=15):
    return {
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 360.0, "height": 240.0,
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


A01_PROMPT = """16:9 纯白底道具设定图，只生成一张，两个物件并排。左：一个打开的白色快餐餐盒，里面是白米饭和青椒丝，没有一根肉丝；右：一把不锈钢勺子。真实材质，柔和接触阴影。
背景 #FFFFFF 纯白，无投影、无其他文字、无水印、无 logo、无手。
负向：肉丝、人类、手指、文字、水印、logo、比例失真、塑料感、餐盒变形。"""

A02_PROMPT = """16:9 横版空景，不出现任何角色。蛋仔快餐店一角：柜台、柜台后的菜单灯箱（灯箱上只有食物图片，没有文字）、几张矮桌与小凳、暖黄灯光、干净的地面；低机位贴桌视角，前景为 12cm 小角色留出空间；3D 卡通渲染+真实光影（皮克斯质感），柔和景深，35mm 颗粒。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

G01_PROMPT = """16:9 四宫格分镜预演图，2×2 等分，每格 16:9，细白分隔线；四格按左上→右上→左下→右下顺序，同一快餐店、同一角色、同一暖光；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射），35mm 颗粒；全图无文字、无字幕、无 logo、无水印。
左上（0–5s）：蛋仔快餐店柜台（参考 {{A02}}），黄蛋（参考 {{R01}}，比例参考 {{R00}}）踮脚指着菜单灯箱，心易（本集用粉蛋形象，参考 {{R02}}）在柜台后点头。
右上（5–11s）：黄蛋抱着打开的餐盒（参考 {{A01}}）坐在小桌边，眼睛发亮。
左下（11–15s）：餐盒里只有米饭和青椒丝，没有肉丝；黄蛋僵住。
右下（Part B 4–9s）：心易举一张空白词卡（版面留白，不出现文字），黄蛋拿勺子拨餐盒。
四格角色外形/服装/比例一致，不新增角色；暖光与桌面反光四格一致。
负向：文字、字幕、水印、logo、人类、手指、牙齿、裂壳、蛋液、蛋黄、肉丝、多余角色、分格错位、角色变形、餐盒变形、塑料高光过强、卡通描边、过曝。"""

KA_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。蛋仔快餐店柜台（光线与机位跟 {{A02}} 一致）：黄蛋（参考 {{R01}} 外形、{{R00}} 比例：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子黑条纹+白色毛绒靴）踮脚站在柜台前，短圆手臂指着菜单灯箱，眼睛发亮、期待；心易（参考 {{R02}}，粉蛋形象）在柜台后点头微笑。低机位贴柜微距，黄蛋约占画面高 1/4，暖黄灯光；3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo；菜单灯箱只有食物图片、没有文字。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、菜单文字、多余角色、过曝。"""

KC_PROMPT = """16:9 单词卡版式，只生成一张。卡片占画面中央 70%，米白纸面、圆角、轻微纸张纹理：顶部大号单词"morose"（黑色无衬线粗体，拼写必须准确：m-o-r-o-s-e）+ 音标 /məˈroʊs/；中部三行红色马克笔手写感大字"没、肉、丝"，下方一行黑色小字"adj. 闷闷不乐的"；暖黄快餐店灯光从右上照入，卡片投柔和阴影。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、图标变形。"""

PART_A_PROMPT = """【首帧锁定】首帧使用 {{K_A}}；第 0 秒就是这一帧：蛋仔快餐店柜台，黄蛋踮脚指着菜单灯箱，心易在柜台后点头。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不是穿搭/道具）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿，不吃不咬；情绪从期待到落空。
【心易】本集用粉蛋形象出演（参考 {{R02}}）：12cm 粉色蛋仔，粉色蛋壳、奶油色椭圆脸板、大圆眼、短圆手臂无手指、白色圆脚；快餐店店员＋老师位，平静、动作少。
【道具】快餐餐盒：白色纸盒，里面是白米饭＋青椒丝，没有肉丝；勺子：不锈钢。
【场景与尺度】蛋仔快餐店，柜台、菜单灯箱（只有食物图片、无文字）、矮桌小凳、暖黄灯光；低机位贴桌微距，黄蛋约占画面高 1/4；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=餐盒+勺子；{{A02}}=快餐店空景。
0–5 秒：{{K_A}}{{R02}}黄蛋踮脚指着菜单灯箱，说：“青椒肉丝饭，肉丝多一点！”；心易点头，从柜台下拿出餐盒递给他。
5–11 秒：{{A01}}黄蛋抱着餐盒坐到小桌边，眼睛发亮，短手把餐盒打开；餐盒里是白米饭和青椒丝。
11–15 秒：{{A01}}镜头推近餐盒——只有白米饭和青椒丝，一根肉丝都没有；黄蛋僵住，眼睛失去高光；镜尾定格 0.5 秒。
【特效延续】暖黄灯光、柜台反光延续到下一段。
【声音】快餐店环境声、柜台提示音、餐盒打开声、黄蛋倒吸气；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、肉丝、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、菜单文字、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

PART_B_PROMPT = """【首帧锁定】首帧使用 {{T_A}}（Part A 最后一帧：黄蛋盯着只有青椒的餐盒，僵住）；锁黄蛋与餐盒的位置/朝向/光线/背景，不重构图不换机位；第 0 秒从这一帧直接继续。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿。
【心易】本集用粉蛋形象出演（参考 {{R02}}）：12cm 粉色蛋仔，粉色蛋壳、奶油色椭圆脸板、大圆眼、短圆手臂无手指、白色圆脚；店员＋老师位。
【道具】餐盒：白米饭＋青椒丝，无肉丝；勺子。
【场景与尺度】同 Part A 快餐店小桌；低机位贴桌微距，两只蛋同高、各约占画面高 1/4；摄影机仍在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=餐盒+勺子；{{KC}}=词卡版式。
0–4 秒：{{T_A}}{{A01}}黄蛋拿勺子拨来拨去，翻遍餐盒，找不到肉丝；肩膀慢慢垮下去。
4–9 秒：{{R02}}{{KC}}心易从柜台后走过来，举卡（morose＋/məˈroʊs/＋红字“没、肉、丝”＋“adj. 闷闷不乐的”）；心易念：“morose，闷闷不乐的。谐音——没肉丝。”
9–13 秒：{{R01}}黄蛋：“没肉丝……所以 morose？”；心易：“对。没肉丝，闷闷不乐。”；黄蛋瘪嘴，趴到桌上。
13–15 秒：{{A01}}黄蛋把青椒丝一根根摆成“肉丝”的形状，摆完看着它，还是闷闷不乐；心易在旁边憋笑；镜尾定格 1.5 秒。
【特效延续】暖黄灯光、桌面反光延续；结尾不新增特效，定格干净。
【声音】勺子碰餐盒、青椒丝摩擦、心易念词、黄蛋复读、趴桌轻响；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、肉丝、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、菜单文字、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

NOTES = """【本画布做什么】
《蛋仔记单词》谐音无厘头 EP01《morose＝没肉丝》2×15 秒：黄蛋在蛋仔快餐店点“青椒肉丝饭，肉丝多一点”，打开只有青椒；心易举卡 morose；黄蛋把青椒摆成“肉丝”形状，还是闷闷不乐。
集型：谐音无厘头，1 个词／30 秒；套壳自 B站 31s 3D 卡通《肉丝没找到，morose 倒是记住了》。

【运行顺序】
1. 先跑 A01 餐盒+勺子、A02 快餐店空景（互不依赖，可同时）。
2. 跑 G01 四宫格预演（2×2）；看四格顺序、黄蛋/心易位置、餐盒状态。G01 只做预演，不接视频。
3. 跑 K_A（只取 G01 左上格构图）和 KC（词卡）。
4. 跑 Part A（15s）。看完最后一帧：餐盒里是否只有青椒、没有肉丝。
5. ⚠️ T_A 当前是一蛋一剑旧占位板：截 Part A 最后一帧上传替换（节点 id/token 不变）。替换前不要派发 Part B。
6. 跑 Part B（15s）。首帧就是 T_A，不要换别的图。
7. 剪辑：硬切；定格后切黑幕白字卡（约 1.5s）：morose／闷闷不乐的。台标、钩子后期贴。

【角色口径】
- 黄蛋头顶“黄色天线+圆球”是角色本体，不是穿搭/道具，保留。
- 蛋仔是蛋形潮玩，不是真蛋：不敲壳、不剥壳、不煮/煎、不出现蛋液蛋黄；没有牙齿，不吃不咬，只拨食物。
- 心易本集用粉蛋形象出演（参考 R02）；后续有标准图再换节点重跑。

【谐音铁律】
- 谐音“没肉丝”由心易在 Part B 说出，不解释英文；词卡才揭 morose。
- 反转由“打开只有青椒、没肉丝”驱动，不是角色听错。
- 词卡给真实词义“adj. 闷闷不乐的”；青椒摆“肉丝”是收梗，不改词义。
"""


def link(text: str) -> str:
    tokens = ("R00", "R01", "R02", "A01", "A02", "G01", "K_A", "KC", "T_A")
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
    nodes.append(make_input_image("R00", "R00 四小只身高比例（复用）", R00, 0, 0, width=320))
    nodes.append(make_input_image("R01", "R01 黄蛋标准（复用）", R01, 0, 200, width=300))
    nodes.append(make_input_image("R02", "R02 粉蛋标准 · 本集代心易（复用）", R02, 0, 580, width=300))

    nodes.append(make_gen_image("A01", "【待生成】A01 餐盒＋勺子（米饭青椒/无肉丝）· 1K",
                                link(A01_PROMPT), [], 400, 0))
    nodes.append(make_gen_image("A02", "【待生成】A02 蛋仔快餐店空景 · 1K",
                                link(A02_PROMPT), [], 400, 260))
    nodes.append(make_gen_image("G01", "【待生成】G01 四宫格预演 · 2×2 · 点单/期待/打开/心易 · 1K",
                                link(G01_PROMPT), ["R00", "R01", "R02", "A01", "A02"], 800, 0, height=180.0))
    nodes.append(make_gen_image("K_A", "【待生成】K_A Part A 首帧 · 黄蛋点单（踮脚指菜单）· 1K",
                                link(KA_PROMPT), ["G01", "R00", "R01", "R02", "A02"], 1200, 0, height=180.0))
    nodes.append(make_gen_image("KC", "【待生成】KC 词卡 · morose/没肉丝/闷闷不乐的 · 1K",
                                link(KC_PROMPT), [], 1200, 220, height=180.0))
    nodes.append(make_input_image(
        "T_A",
        "【待替换⚠】T_A Part A 尾帧 → Part B 首帧（截 Part A 最后一帧替换，替换前勿派发 Part B）",
        T_A, 1200, 470, width=320,
    ))

    part_a = link(PART_A_PROMPT)
    part_b = link(PART_B_PROMPT)
    for name, p in (("Part A", part_a), ("Part B", part_b)):
        if len(p) > 1900:
            raise SystemExit(f"{name} prompt {len(p)} chars > 1900 target (hard 2000)")

    nodes.append(make_gen_video(
        "PartA", "【待生成】Part A · 0–15s · 点单/期待/打开只有青椒",
        part_a, ["R00", "R01", "R02", "A01", "A02"], "K_A", 1650, 0, duration=15,
    ))
    nodes.append(make_gen_video(
        "PartB", "【待生成】Part B · 15–30s · 拨找/心易揭底/青椒摆肉丝",
        part_b, ["R00", "R01", "R02", "A01", "KC"], "T_A", 1650, 310, duration=15,
    ))

    nodes.append(make_text("S0", "S0 制作说明 · 先读", NOTES, 800, 720))

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
        group("g01", "01 道具/场景 · 先跑", ["A01", "A02"], "#8E8DE0"),
        group("g02", "02 四宫格预演 · G01 先跑", ["G01"], "#C9A227"),
        group("g03", "03 首帧/词卡 · K_A、KC", ["K_A", "KC"], "#E8B85D"),
        group("g04", "04 尾帧 · Part A 跑完截帧替换", ["T_A"], "#B08E6A"),
        group("g05", "05 视频 Part A · 15s", ["PartA"], "#DC775D"),
        group("g06", "06 视频 Part B · 15s（T_A 替换后）", ["PartB"], "#DC775D"),
        group("g07", "07 制作说明 · 先读", ["S0"], "#7FB07F"),
    ]

    # --- checks ---
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
            "name": "蛋仔记单词 · 谐音无厘头 EP01 morose v1 · 2×15s（含四宫格预演）",
            "description": "1 词／30 秒。黄蛋在蛋仔快餐店点“青椒肉丝饭，肉丝多一点”，打开只有青椒；心易举卡 morose；黄蛋把青椒摆成“肉丝”形状，还是闷闷不乐。套壳自 B站 31s 3D 卡通《肉丝没找到，morose 倒是记住了》。",
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / "EP01-morose-v1.monet"
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"{out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"Part A {len(part_a)} chars / Part B {len(part_b)} chars")
    print(f"-> {out}")
    print(f"-> {downloads}")


if __name__ == "__main__":
    main()
