# -*- coding: utf-8 -*-
"""Build 蛋仔记单词·构词合成 EP02《-like 家族》Monet canvas.

Q&A family episode:
  doglike   = dog + like   = 像狗一样（忠诚的）
  catlike   = cat + like   = 像猫一样（优雅的）
  birdlike  = bird + like  = 像鸟一样（轻盈的）
  childlike = child + like = 像孩子一样（天真的）

Part A: doglike / catlike / birdlike three Q&A rounds.
Part B: childlike + four-column card + group shot.

Note: 心易 uses 粉蛋 (R02), not the old white heart-antenna egg.
Note: the bird steals a yellow prop ball, NOT 黄蛋's antenna ball.

Outputs:
  02_画布/EP02-like-family-v3.monet
  ~/Downloads/EP02-like-family-v3.monet
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "egg-like-ep02:v3"
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


A01_PROMPT = """16:9 纯白底角色设定图，只生成并排一排三只小动物，同一比例（每只约为 12cm 蛋仔身高的 1–1.3 倍），完整入画：①小狗：奶黄色、吐舌、尾巴摇成风扇、热情；②猫：灰白相间、眼神高冷、尾巴优雅上翘；③小鸟：圆滚滚蓝色小鸟、翅膀短短、不叼东西；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo。
负向：真实照片质感、恐怖、尖牙利爪、文字、水印、logo、比例失真、多余动物。"""

A02_PROMPT = """16:9 横版空景，不出现任何角色和动物。黄昏魔法池塘：金色夕照水面、几片睡莲叶、一圈芦苇、岸边草地缓坡上铺着一块红白格野餐垫，垫角放一颗黄色小皮球（道具）；低机位贴地视角，前景为 12cm 小角色留出空间；3D 卡通渲染+真实光影（皮克斯质感），35mm 颗粒，柔和景深。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

G01_PROMPT = """16:9 四宫格分镜预演图，2×2 等分，每格 16:9，细白分隔线；四格按左上→右上→左下→右下顺序，同一黄昏池塘、同一角色、同一暖光；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射），35mm 颗粒；全图无文字、无字幕、无 logo、无水印。
左上（起幅）：双人中景，黄蛋（参考 {{R01}}，比例参考 {{R00}}）举着单词书问话，心易（本集用粉蛋形象，参考 {{R02}}）伸出短圆手臂指向画面右侧画外；狗还没出现。
右上（镜头已右移）：狗特写，低机位，狗占画面 2/3，背景虚化；狗扑向镜头、舔、摇尾。
左下（镜头已左移回）：与左上同一机位/构图；黄蛋问话，心易再指画面右侧。
右下（镜头再右移）：猫特写，猫高冷走过/舔爪。
四格是连续运镜的四个落点，不是硬切；角色/动物外形一致，不新增角色；右侧空间分层（狗近、猫中、鸟后）。
负向：文字、字幕、水印、logo、人类、手指、牙齿、裂壳、蛋液、蛋黄、多余角色、分格错位、角色变形、动物变恐怖、硬切、跳切、塑料高光过强、卡通描边、过曝。"""

KA_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。黄昏魔法池塘边野餐垫（光线与机位跟 {{A02}} 一致）：双人中景，黄蛋（参考 {{R01}} 外形、{{R00}} 比例：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子黑条纹+白色毛绒靴）在画面左 1/3，举着一本打开的单词书，张嘴发问；心易（参考 {{R02}}，粉蛋形象）在画面右 1/3，伸出短圆手臂指向画面右侧画外；垫角有一颗黄色小皮球；右侧草地/石凳/树枝留出动物空间，动物都还没出现。低机位贴地微距，黄蛋约占画面高 1/4，金色夕照；3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo；单词书内页不出现可读文字。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、书页文字、动物提前出现、多余角色、过曝。"""

KC_PROMPT = """16:9 四栏单词卡版式，只生成一张。卡片占画面中央 80%，米白纸面、圆角、轻微纸张纹理；顶部一行黑色小字“-like 家族”；下方四栏等宽，从左到右：
第一栏：黑色粗体“doglike”＋灰色“dog + like”＋黑色中字“像狗一样（忠诚的）”；
第二栏：黑色粗体“catlike”＋灰色“cat + like”＋黑色中字“像猫一样（优雅的）”；
第三栏：黑色粗体“birdlike”＋灰色“bird + like”＋黑色中字“像鸟一样（轻盈的）”；
第四栏：黑色粗体“childlike”＋灰色“child + like”＋黑色中字“像孩子一样（天真的）”。
黄昏暖光从右上照入，卡片投柔和阴影；四栏之间有细灰分隔线。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、文字重叠、串栏。"""

PART_A_PROMPT = """【运镜】一镜到底的连续机位运动，不是硬切：镜头从双人中景（黄蛋左、心易右）沿心易短圆手臂指向的方向，向右横移/摇摄（track right），经过右侧草地到狗特写；推近、停留；再沿原路向左横移/摇摄（track left）回到同一双人中景；黄蛋问 catlike，心易再指右；镜头再右移到猫特写；再左移回双人中景；黄蛋问 birdlike；镜头再向右/向上移到鸟特写，鸟叼球飞走。全程不切、不跳切、不叠化、不环绕、不瞬移。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿；提问者。
【心易】本集用粉蛋形象出演（参考 {{R02}}）：12cm 粉色蛋仔，粉色蛋壳、奶油色椭圆脸板、大圆眼、短圆手臂无手指、白色圆脚；讲解者，伸短臂指画面右侧画外。
【三只动物】造型以 {{A01}} 为准，不说话（只有叫声）：小狗（奶黄、热情摇尾吐舌）在右侧近处草地；猫（灰白、高冷）在右中景石凳；小鸟（蓝色、短翅）在右后景树枝/石头上。
【场景与尺度】黄昏魔法池塘边野餐垫；双人中景低机位贴地，两蛋同高、各约占画面高 1/4；动物特写低机位，动物占画面 2/3，背景虚化；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=三只动物；{{A02}}=池塘野餐空景。
0–2.5 秒：{{K_A}}{{R02}}双人中景起幅；黄蛋举书问：“doglike？”；心易伸短臂指向画面右侧画外，说：“dog——狗；like——像。像狗一样。”；镜头开始向右横移。
2.5–5 秒：{{A01}}镜头沿手臂方向右移到右侧草地，推到狗特写；狗扑向镜头、舔、摇尾；心易画外音：“就是忠诚的。”
5–7.5 秒：镜头沿原路向左横移/摇摄回同一双人中景；黄蛋问：“catlike？”；心易再指右，说：“cat——猫；like——像。像猫一样。”
7.5–10 秒：{{A01}}镜头右移到右中景石凳，推到猫特写；猫高冷走过/舔爪/瞥镜头；心易画外音：“就是优雅的。”
10–12.5 秒：镜头向左横移回同一双人中景；黄蛋问：“birdlike？”；心易再指右，说：“bird——鸟；like——像。像鸟一样。”
12.5–15 秒：{{A01}}镜头向右/向上移到右后景树枝，推到鸟特写；小鸟叼起野餐垫上的黄色小皮球飞走；心易画外音：“就是轻盈的。”；镜尾定格 0.5 秒。
【特效延续】野餐垫、草地反光延续。
【声音】书页、狗叫、猫叫、鸟振翅、心易三次拆词与三次画外词义、黄蛋三次提问；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、硬切、跳切、叠化、环绕、瞬移、动物说人话、鸟叼天线球、天线球脱落、动物变恐怖、书页文字、多余角色、塑料高光过强、卡通描边、过曝、漂浮。"""

PART_B_PROMPT = """【运镜】一镜到底的连续机位运动，不是硬切：首帧是鸟特写；镜头向左横移/摇摄（track left），经过右侧空间回到双人中景；黄蛋问 childlike，心易用书角指他；镜头推近黄蛋；再横移/下摇到野餐垫上的空白卡；卡特写停留；最后拉远/后移到大远景。全程不切、不跳切、不叠化、不环绕、不瞬移。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不可拆）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿。
【心易】讲解者（参考 {{R02}}，粉蛋形象）：一手持书，用书角指黄蛋本人。
【三只动物】造型以 {{A01}} 为准；结尾三只围在野餐垫旁，小鸟把黄色小皮球放回垫上。
【卡】野餐垫上放一张空白卡（卡面留白/卡背）；四栏字由后期贴 {{KC}} 静帧，不让视频模型写卡面文字。
【场景与尺度】同 Part A 黄昏池塘边；双人中景低机位贴地，两蛋同高、各约占画面高 1/4；卡/动物特写低机位；摄影机仍在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=三只动物；{{KC}}=四栏词卡版式（后期贴）。
镜头1（0–3 秒）：{{T_A}}{{R02}}首帧鸟特写；镜头向左横移/摇摄，经过右侧空间回到双人中景；黄蛋问：“childlike？”；心易用书角指黄蛋本人，说：“child——孩子；like——像。像孩子一样；childlike 就是——像孩子一样的，天真的。”
镜头2（3–6 秒）：镜头推近黄蛋；黄蛋愣一秒，随即破涕为笑；心易画外：“就是天真的。”
镜头3（6–11 秒）：镜头横移/下摇到野餐垫上的空白卡；卡特写；心易画外逐个复习 doglike／catlike／birdlike／childlike，每词报词义；卡面留白，后期贴 KC。
镜头4（11–15 秒）：镜头拉远/后移到大远景；狗、猫、鸟围在野餐垫旁；小鸟把黄色小皮球放回垫上；黄蛋举球；心易点头；镜尾定格 1.5 秒。
【特效延续】草地反光、野餐垫延续；结尾定格干净。
【声音】书页、心易讲解与复习（每词都有 X＋like 和词义）、黄蛋提问与笑、狗叫猫叫鸟振翅；无 BGM。
负向：人类、手指、牙齿、裂壳、蛋液、蛋黄、真实鸡蛋、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变形、硬切、跳切、叠化、环绕、瞬移、动物说人话、鸟叼天线球、天线球脱落、动物变恐怖、书页文字、多余角色、塑料高光过强、卡通描边、过曝、漂浮。"""

NOTES = """【本画布做什么】
《蛋仔记单词》构词合成 EP02《-like 家族》v3 连续运镜版：一问一答，doglike／catlike／birdlike／childlike 四词一条；黄蛋问，心易指画外，镜头沿手臂移到动物，再沿原路移回提问者。
集型：构词合成·词缀家族（多词一条）；不是拼词，不是谐音。

【运镜铁律】
- 不是硬切：镜头从双人中景（黄蛋左、心易右）沿心易短臂指向的方向，向右横移/摇摄到动物特写；再沿原路向左横移/摇摄回同一机位。
- 全程连续机位运动，不切、不跳切、不叠化、不环绕、不瞬移；说话人构图每次回到同一机位。
- 动物在右侧分层：狗近处草地、猫中景石凳、鸟后景树枝/石头；镜头沿右侧空间依次移动。
- 鸟叼的是野餐垫上的黄色小皮球道具，不是天线球；天线球不可拆。

【运行顺序】
1. A01 三只动物 → A02 池塘野餐空景（右侧留出分层空间）。（互不依赖，可同跑）
2. G01 四宫格（起幅/狗/回双人/猫）；K_A 只取左上格构图。
3. K_A 首帧（双人中景、心易指右、动物未出）；KC 四栏卡（后期贴）。
4. Part A（15s，首帧 K_A；连续运镜）。
5. ⚠️ 截 Part A 最后一帧（鸟特写）替换 T_A；替换前勿派发 Part B。
6. Part B（15s，首帧 T_A；镜头向左移回双人中景）。
7. 剪辑：后期字幕、KC 静帧、黑幕四行卡、钩子。

【卡的处理】
- 视频里只拍心易翻卡/卡背/空白卡；四栏字由后期贴 KC 静帧 3–5s。

【风险】
- 一条 15s 里三次“右移→动物→左移回”，模型可能把回程做成瞬移/切/环绕。第一条先看回程是否连续、双人构图是否回位。
- 若运镜不稳，改“每个词一个视频节点”（3 段），词间用短横移/剪辑接；**人→动物不要硬切**。
- 4 词/30s＋三次往返偏紧；若吞词，减到 3 词或加到 45s。
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

    nodes.append(make_gen_image("A01", "【待生成】A01 三只动物设定（狗/猫/鸟）· 1K",
                                link(A01_PROMPT), [], 400, 0))
    nodes.append(make_gen_image("A02", "【待生成】A02 黄昏池塘野餐空景 · 1K",
                                link(A02_PROMPT), [], 400, 260))
    nodes.append(make_gen_image("G01", "【待生成】G01 四宫格预演 · 2×2 · doglike/catlike/birdlike/childlike · 1K",
                                link(G01_PROMPT), ["R00", "R01", "R02", "A01", "A02"], 800, 0, height=180.0))
    nodes.append(make_gen_image("K_A", "【待生成】K_A Part A 首帧 · 黄蛋举书问 doglike（狗未扑）· 1K",
                                link(KA_PROMPT), ["G01", "R00", "R01", "R02", "A02"], 1200, 0, height=180.0))
    nodes.append(make_gen_image("KC", "【待生成】KC 四栏卡 · doglike/catlike/birdlike/childlike · 1K",
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
        "PartA", "【待生成】Part A · 0–15s · doglike/catlike/birdlike 三轮问答",
        part_a, ["R00", "R01", "R02", "A01", "A02"], "K_A", 1650, 0, duration=15,
    ))
    nodes.append(make_gen_video(
        "PartB", "【待生成】Part B · 15–30s · childlike＋四栏卡＋合影",
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
        group("g01", "01 动物/场景 · 先跑", ["A01", "A02"], "#8E8DE0"),
        group("g02", "02 四宫格预演 · G01 先跑", ["G01"], "#C9A227"),
        group("g03", "03 首帧/四栏卡 · K_A、KC", ["K_A", "KC"], "#E8B85D"),
        group("g04", "04 尾帧 · Part A 跑完截帧替换", ["T_A"], "#B08E6A"),
        group("g05", "05 视频 Part A · 15s", ["PartA"], "#DC775D"),
        group("g06", "06 视频 Part B · 15s（T_A 替换后）", ["PartB"], "#DC775D"),
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
            "name": "蛋仔记单词 · 构词合成 EP02 -like 家族 v3 · 2×15s（含四宫格预演）",
            "description": "多词一条／30 秒：一问一答，doglike＝像狗一样（忠诚的）、catlike＝像猫一样（优雅的）、birdlike＝像鸟一样（轻盈的）、childlike＝像孩子一样（天真的）。Part A 三轮、Part B 第四轮＋四栏卡。心易用粉蛋；鸟叼黄色小皮球，不叼天线球。",
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / "EP02-like-family-v3.monet"
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"{out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"Part A {len(part_a)} chars / Part B {len(part_b)} chars")
    print(f"-> {out}")
    print(f"-> {downloads}")


if __name__ == "__main__":
    main()
