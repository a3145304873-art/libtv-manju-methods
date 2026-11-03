# -*- coding: utf-8 -*-
"""Build 蛋仔记单词·谐音反转 EP01《agony＝爱过你》Monet canvas.

Story: 雨夜失恋痛哭 → 照片里是一颗贴爱心贴纸的大蒜 → 眼泪是辣的。
Part A 立场面/埋谐音/反转；Part B 心易（本集暂用粉蛋形象）揭底。

Outputs:
  02_画布/EP01-agony-v1.monet
  ~/Downloads/EP01-agony-v1.monet

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
PREFIX = "egg-homo-ep01-agony:v1"
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


A01_PROMPT = """16:9 纯白底道具设定图，只生成一张，两个物件并排。左：一颗完整的大蒜，蒜皮乳白带淡紫条纹，顶部收尖；右：一张拍立得照片，白色相纸边框，照片里是一颗大蒜，蒜头上贴着一枚红色爱心贴纸，照片表面有雨滴。真实材质，柔和接触阴影。
背景 #FFFFFF 纯白，无投影、无其他文字、无水印、无 logo、无手。
负向：人类、手指、多余文字、水印、logo、比例失真、塑料感、蒜头发芽、照片变形。"""

A02_PROMPT = """16:9 横版空景，不出现任何角色。雨夜城市街头：湿漉漉的柏油路面反射暖黄路灯，路灯光晕，远处街道与行道树虚化，雨丝斜落，地面有水洼；低机位贴地视角，前景为 12cm 小角色留出空间；3D 卡通渲染+真实光影（皮克斯质感），柔和景深，35mm 颗粒。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。"""

G01_PROMPT = """16:9 四宫格分镜预演图，2×2 等分，每格 16:9，细白分隔线；四格按左上→右上→左下→右下顺序，同一场景、同一角色、同一光线；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射），35mm 颗粒；全图无文字、无字幕、无 logo、无水印。
左上（0–3s）：雨夜街头（参考 {{A02}}），黄蛋（参考 {{R01}}，比例参考 {{R00}}）跪在湿路面，双手捧着一张背面朝镜头的拍立得照片，仰头哭，路灯光晕在背后。
右上（3–9s）：同一机位，黄蛋从怀里掏出一颗大蒜（参考 {{A01}}）咬一口，眼泪狂飙，仍对着照片哭。
左下（9–15s）：照片翻到正面——照片里是一颗蒜头贴红色爱心贴纸（参考 {{A01}}）；黄蛋举着照片张嘴喊，泪流满面。
右下（Part B 4–9s）：心易（本集用粉蛋形象，参考 {{R02}}）撑小透明伞，举一张空白词卡（版面留白，不出现文字），神情平静。
四格角色外形/服装/比例一致，不新增角色；雨丝与湿路面反光四格一致。
负向：文字、字幕、水印、logo、人类、手指、多余角色、分格错位、角色变形、蒜头变洋葱、照片正面提前露出、塑料高光过强、卡通描边、过曝。"""

KA_PROMPT = """16:9 电影感首帧，第 0 秒画面，只生成一张。构图参考 {{G01}} 左上格（只取构图/机位/光线/角色姿态，不出现其他三格、不出现分格线）。雨夜街头（光线与机位跟 {{A02}} 一致）：黄蛋（参考 {{R01}} 外形、{{R00}} 比例：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子黑条纹+白色毛绒靴）跪在湿路面上，双手捧着一张拍立得照片，照片背面朝镜头（看不到画面）；他仰头，眼睛闭着，眼泪混着雨水，嘴巴张开无声痛哭。低机位贴地微距，黄蛋约占画面高 1/4，路灯光晕在背后；3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo。
负向：人类、手指、字幕、水印、logo、比例失真、黄蛋变色、照片正面朝镜头、多余角色、过曝、雨滴成块。"""

KC_PROMPT = """16:9 单词卡版式，只生成一张。卡片占画面中央 70%，米白纸面、圆角、轻微纸张纹理：顶部大号单词"agony"（黑色无衬线粗体，拼写必须准确：a-g-o-n-y）+ 音标 /ˈæɡəni/；中部三行红色马克笔手写感大字"爱、过、你"，下方一行黑色小字"n. 极度痛苦"；卡片右下角贴一张小照片（参考 {{A01}}：蒜头贴爱心贴纸的拍立得，缩小、不改变内容）；雨夜暖光从右上照入，卡片投柔和阴影。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、蒜头变形、照片内容错误。"""

PART_A_PROMPT = """【首帧锁定】首帧使用 {{K_A}}；第 0 秒就是这一帧：雨夜街头，黄蛋跪地，双手捧着一张背面朝镜头的拍立得照片，仰头哭。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体，不是穿搭/道具）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；本段情绪从悲痛到被辣到流泪。
【道具】拍立得照片：白色相纸边框，正面是一颗蒜头贴红色爱心贴纸（本段 0–9 秒背面朝镜头，9 秒后才翻到正面）；大蒜：完整一颗，乳白带淡紫条纹。
【场景与尺度】雨夜城市街头，湿路面反射路灯光、雨丝斜落；低机位贴地微距，黄蛋约占画面高 1/4；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{A01}}=大蒜+照片道具；{{A02}}=雨夜街头空景。
0–3 秒：{{K_A}}{{A01}}黄蛋跪在雨里，双手捧着照片（背面朝镜头），仰头，眼泪混着雨水，无声痛哭；雨声。
3–9 秒：{{A01}}他抽噎着，从怀里掏出一颗大蒜，咬了一大口；眼泪瞬间狂飙；他继续对着照片哭，越哭越凶。
9–15 秒：{{A01}}照片翻到正面——照片里是一颗蒜头，贴着红色爱心贴纸；黄蛋又咬一口蒜，举着照片，沙哑地喊："爱过你！"；镜尾定格 0.5 秒。
【特效延续】雨丝、湿路面反光延续到下一段。
【声音】雨声、咬蒜的脆响、抽泣、沙哑喊"爱过你"；无 BGM。
负向：人类、手指、字幕、水印、logo、比例失真、黄蛋变色、照片正面提前露出、蒜头变成洋葱、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

PART_B_PROMPT = """【首帧锁定】首帧使用 {{T_A}}（Part A 最后一帧：黄蛋举着蒜头照片，泪流满面，喊完"爱过你"）；锁黄蛋与照片的位置/朝向/光线/背景，不重构图不换机位；第 0 秒从这一帧直接继续。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球（角色本体）、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；脸上雨水与泪。
【心易】本集暂用粉蛋形象出演（参考 {{R02}}）：12cm 粉色蛋仔，粉色蛋壳、奶油色椭圆脸板、大圆眼、短圆手臂无手指、白色圆脚；身份仍是"心易"老师位，神态平静、动作少而慢；撑一把小透明伞。
【道具】拍立得照片：正面是蒜头贴红色爱心贴纸；大蒜：完整一颗。
【场景与尺度】同 Part A 雨夜街头；低机位贴地微距，两只蛋同高、各约占画面高 1/4；摄影机仍在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{R02}}=粉蛋标准（代心易）；{{A01}}=大蒜+照片道具；{{KC}}=词卡版式。
0–4 秒：{{T_A}}{{R02}}心易撑着小透明伞从画面右侧滚入，停在黄蛋身边，递上纸巾；黄蛋还在流泪，接过纸巾。
4–9 秒：{{R02}}{{A01}}{{KC}}心易举起词卡（agony＋/ˈæɡəni/＋红字"爱、过、你"＋"n. 极度痛苦"）；心易平静清晰地念："agony，极度痛苦。谐音——爱过你。"
9–13 秒：{{R01}}黄蛋指着照片，又哭又笑："爱过你……所以这就是 agony？"；心易："对。爱过你，也痛。"；黄蛋又咬一口蒜，泪如泉涌。
13–15 秒：{{A01}}照片上的蒜头也"流泪"（雨滴从蒜头滑落）；黄蛋把照片抱在怀里，打了个嗝；镜尾定格 1.5 秒。
【特效延续】雨丝、湿路面反光延续；结尾不新增特效，定格干净。
【声音】雨声、纸巾摩擦、咬蒜脆响、打嗝；4–9 秒心易念："agony，极度痛苦。谐音——爱过你。"；9–13 秒黄蛋："爱过你……所以这就是 agony？"、心易："对。爱过你，也痛。"；无 BGM。
负向：人类、手指、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、粉蛋变色变形、心易长出爱心天线、蒜头变成洋葱、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。"""

NOTES = """【本画布做什么】
《蛋仔记单词》谐音反转 EP01《agony＝爱过你》2×15 秒：雨夜失恋痛哭，照片里是一颗贴爱心贴纸的大蒜，眼泪是辣的；Part B 心易（暂用粉蛋形象）揭谐音。
集型：谐音反转——先把中文谐音演成正常场面，再反转成字面意思，词卡揭英文。

【运行顺序】
1. 先跑 A01 大蒜+照片、A02 雨夜街头（互不依赖，可同时）。
2. 跑 G01 四宫格预演（2×2）；看四格顺序、黄蛋/粉蛋外形、蒜头与照片状态是否对。G01 只做预演，不接视频。
3. 跑 K_A（只取 G01 左上格构图/机位/光线）和 KC（词卡）。
4. 跑 Part A（15s）。看完最后一帧：照片正面是否露出蒜头+爱心贴纸，黄蛋是否举着照片。
5. ⚠️ T_A 当前是一蛋一剑旧占位板：截 Part A 最后一帧上传替换（节点 id/token 不变）。替换前不要派发 Part B。
6. 跑 Part B（15s）。首帧就是 T_A，不要换别的图。
7. 剪辑：硬切；定格后切黑幕白字卡（约 1.5s）：agony／极度痛苦。台标、钩子后期贴。

【角色口径】
- 黄蛋头顶"黄色天线+圆球"是角色本体，不是穿搭/道具，保留。
- 心易本集暂用粉蛋形象出演（参考 R02）；后续有标准图再换节点重跑。

【谐音铁律】
- 谐音"爱过你"只在 Part A 9–15s 出现一次，不解释英文。
- 反转由"照片里是大蒜"驱动，不是角色听错。
- 词卡给真实词义"n. 极度痛苦"；谐音只做钩子。
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

    nodes.append(make_gen_image("A01", "【待生成】A01 大蒜＋拍立得照片（蒜头贴爱心）· 1K",
                                link(A01_PROMPT), [], 400, 0))
    nodes.append(make_gen_image("A02", "【待生成】A02 雨夜街头空景 · 1K",
                                link(A02_PROMPT), [], 400, 260))
    nodes.append(make_gen_image("G01", "【待生成】G01 四宫格预演 · 2×2 · 左上→右下 4 拍 · 1K",
                                link(G01_PROMPT), ["R00", "R01", "R02", "A01", "A02"], 800, 0, height=180.0))
    nodes.append(make_gen_image("K_A", "【待生成】K_A Part A 首帧 · 跪地捧照片（背面朝镜头）· 1K",
                                link(KA_PROMPT), ["G01", "R00", "R01", "A01", "A02"], 1200, 0, height=180.0))
    nodes.append(make_gen_image("KC", "【待生成】KC 词卡 · agony/爱过你/极度痛苦 · 1K",
                                link(KC_PROMPT), ["A01"], 1200, 220, height=180.0))
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
        "PartA", "【待生成】Part A · 0–15s · 失恋/大蒜/喊爱过你",
        part_a, ["R00", "R01", "A01", "A02"], "K_A", 1650, 0, duration=15,
    ))
    nodes.append(make_gen_video(
        "PartB", "【待生成】Part B · 15–30s · 心易揭底/回环/收梗",
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
            "name": "蛋仔记单词 · 谐音反转 EP01 agony · 2×15s（含四宫格预演）",
            "description": "无厘头谐音反转：雨夜失恋痛哭，照片里是一颗贴爱心贴纸的大蒜，眼泪是辣的。Part A 立场面/埋谐音/反转，Part B 心易（暂用粉蛋形象）揭底。G01 四宫格只做预演，K_A 取左上格，不接视频。2×15s。",
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / "EP01-agony-v1.monet"
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"{out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"Part A {len(part_a)} chars / Part B {len(part_b)} chars")
    print(f"-> {out}")
    print(f"-> {downloads}")


if __name__ == "__main__":
    main()
