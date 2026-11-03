# -*- coding: utf-8 -*-
"""Build 蛋仔反转剧（集型丙）Monet canvases.

Two episodes are encoded as data:
  EP01 watch  v. 看 / n. 手表   — 表盘睁眼，反过来盯黄蛋
  EP02 crush  v. 压碎 / n. 暗恋 — 被压扁的罐子爱上黄蛋

Usage:
  py -3 build_twist.py            # build both
  py -3 build_twist.py ep01       # build one

Outputs (repo + ~/Downloads):
  画布/蛋仔记单词-EP01-watch-反转剧-2x15s-v1.monet
  画布/蛋仔记单词-EP02-crush-反转剧-2x15s-v1.monet

Canvas rules follow 03_行业Skill/I06-Monet画布搭建.md:
  - node id = md5(prefix + ':' + key)[:8]; prefix changes per episode
  - edges are derived from reference_images / first_frame_image (single source)
  - groups = run order; no dependency edge inside a group
  - every {{node-x}} in prompt is backed by ref/ff + edge
  - no video->video, no audio->video, duration 3-16 int seconds
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # 衍生方案-蛋仔记单词
OUT = ROOT / "画布"
SHARED = ROOT.parents[0]                            # 工作流研究
FOUR_EGGS = json.loads(
    (SHARED / "衍生方案-四小只" / "参考" / "embed" / "uploaded.json").read_text(encoding="utf-8")
)["items"]
ONE_SWORD = json.loads(
    (SHARED / "衍生方案-一蛋一剑" / "参考" / "embed" / "uploaded.json").read_text(encoding="utf-8")
)
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
VIDEO_MODEL = "seedance-2.0-mini"
IMAGE_MODEL = "gpt-image-2"

R00 = FOUR_EGGS["R00-四小只身高比例.jpg"]
R01 = FOUR_EGGS["角色-黄蛋-标准.jpg"]
R02 = FOUR_EGGS["角色-粉蛋-标准.jpg"]
T_A = ONE_SWORD["t_a_placeholder"]
assert T_A.get("url"), "T_A placeholder url missing"

OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- node factories
def make_input_image(nid, out_id, label, info, x, y, width=320.0):
    ratio = info["height"] / info["width"]
    height = round(width * ratio, 1)
    return {
        "id": nid,
        "type": "input-image",
        "mainOutputId": out_id,
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": out_id, "status": "done", "error": None, "value": info["url"],
            "cover": None, "name": info["name"],
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


def make_gen_image(nid, label, prompt, ref_ids, x, y, width=320.0, height=207.0):
    return {
        "id": nid,
        "type": "gen-image",
        "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1,
            "model_id": IMAGE_MODEL,
            "model_params": {
                "prompt": prompt,
                "reference_images": [{"node_id": r} for r in ref_ids],
                "aspect_ratio": "16:9",
                "image_size": "1K",
                "width": 1024,
                "height": 1024,
                "quality": "medium",
                "output_format": "png",
                "moderation": "low",
                "auto_compress": True,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def make_gen_video(nid, label, prompt, ref_ids, first_frame, x, y, duration=15):
    return {
        "id": nid,
        "type": "gen-video",
        "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 360.0, "height": 240.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {
            "num": 1,
            "model_id": VIDEO_MODEL,
            "model_params": {
                "prompt": prompt,
                "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in ref_ids],
                "reference_audios": [],
                "first_frame_image": {"node_id": first_frame},
                "resolution": "720p",
                "aspect_ratio": "16:9",
                "duration": duration,
                "generate_audio": True,
                "watermark": False,
            },
        },
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def make_text(nid, out_id, label, text, x, y, width=760, height=600):
    return {
        "id": nid,
        "type": "input-text",
        "mainOutputId": out_id,
        "meta": {"x": float(x), "y": float(y), "width": float(width), "height": float(height),
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": out_id, "status": "done", "error": None, "value": text,
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


# ---------------------------------------------------------------- shared prompts
A03_PROMPT = """16:9 纯白底角色设定图，只生成一只。心易：12cm 白色蛋形潮玩，白色哑光蛋壳、奶油色椭圆脸板、小黑点圆眼、粉色圆形腮红、头顶粉色爱心天线（细杆+爱心）、身体中部一圈蓝灰色细环线、白色圆脚；正面与侧面两个视角，同一只、同一比例；3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射），轻微高光。
背景 #FFFFFF 纯白，无投影、无文字、无水印、无 logo。
负向：人类、手指、文字、水印、logo、比例失真、爱心变形、多余角色。"""


# ---------------------------------------------------------------- episodes
EPISODES = {
    "ep01": {
        "prefix": "egg-twist-ep01:v1",
        "file": "蛋仔记单词-EP01-watch-反转剧-2x15s-v1.monet",
        "canvas_name": "蛋仔记单词 · 集型丙 · EP01 watch · 反转剧 · 2×15s",
        "description": "无厘头反转剧单词小剧场：黄蛋戴上手表准备看时间，表盘睁开一只眼反过来盯着他。Part A 立预期/侵入/接管，Part B 揭双义。2×15s。",
        "has_r02": False,
        "a01_label": "【待生成】A01 反转实体 · 复古手表（表盘细缝伏笔）· 1K",
        "a02_label": "【待生成】A02 黄昏公园长椅空景 · 1K",
        "ka_label": "【待生成】K_A Part A 首帧 · 戴表看时间（表盘闭合不剧透）· 1K",
        "kc_label": "【待生成】KC 双栏词卡 · watch/看/手表 · 1K",
        "parta_label": "【待生成】Part A · 0–15s · 立预期/侵入/接管",
        "partb_label": "【待生成】Part B · 15–30s · 升级/揭底/回环/收梗",
        "a01_prompt": """16:9 纯白底道具设定图，只生成一张。一只复古黄铜色圆形手表，棕色皮表带，表带自然弯成一个松散的圈、平放在台面上，表盘正对镜头：米白色表盘、细黑刻度、指针指向 10:10；表盘中央偏上有一道极细的弧形刻线，像闭着的眼睑，第一眼只当装饰刻线。真实黄铜与皮革质感，轻微磨损，柔和接触阴影。
背景 #FFFFFF 纯白，无投影、无其他文字、无水印、无 logo、无手。
负向：睁开的眼睛、人脸、人类手指、品牌文字、乱码、水印、logo、比例失真、塑料感。""",
        "a02_prompt": """16:9 横版空景，不出现任何角色。黄昏城市公园一角：一张木质长椅（椅面高度约为画面中预留小角色身高的 1.2 倍），背后是低矮绿篱与暖黄路灯，远处树影与步道；暖橙色夕阳从画面右侧低角度射入，长影向左；低机位贴地视角，前景为 12cm 小角色留出空间；3D 卡通渲染+真实光影（皮克斯质感），柔和景深，35mm 颗粒。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。""",
        "ka_prompt": """16:9 电影感首帧，第 0 秒画面，只生成一张。黄昏公园长椅前（光线与机位跟 {{A02}} 一致）：黄蛋（参考 {{R01}} 外形、{{R00}} 比例：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子黑条纹+白色毛绒靴）站在长椅前，撸起袖子，正把一只手表（参考 {{A01}}）戴到手腕上；表盘正对镜头，表盘中央的细缝闭合；黄蛋表情自信、得意。低机位贴地微距，黄蛋约占画面高 1/4，夕阳长影；3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo。
负向：人类、手指、睁开的眼睛、字幕、水印、logo、比例失真、黄蛋变色、多余角色、过曝、手表变形。""",
        "kc_prompt": """16:9 双栏单词卡版式，只生成一张。卡片占画面中央 70%，米白纸面、圆角、轻微纸张纹理：顶部大号单词"watch"（黑色无衬线粗体，拼写必须准确：w-a-t-c-h）+ 音标 /wɒtʃ/；中部左右两栏对照——左栏一个黑色简笔眼睛图标（杏仁形外框＋圆点瞳孔）＋一行黑色"v. 看"，右栏一只黄铜手表小图（取自 {{A01}}，抠白底、缩小、不改变外形）＋一行黑色"n. 手表"，两栏之间一个黑色等号；黄昏暖光从右上照入，卡片投柔和阴影。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、图标变形、人类眼睛。""",
        "part_a_prompt": """【首帧锁定】首帧使用 {{K_A}}；第 0 秒就是这一帧：黄昏公园长椅前，黄蛋正把手表戴到手腕上，表盘对着镜头，细缝闭合。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；表情丰富、动作夸张，按"看时间"的正常逻辑行动。
【道具】手表：复古黄铜圆表＋棕色皮表带（参考 {{A01}}），表盘中央有一道细缝；细缝可以睁开成一只大眼睛（搪胶质感的卡通大眼，眼白＋棕色虹膜，不是人类眼睛）。
【场景与尺度】黄昏城市公园长椅前，暖橙夕光、长影向左；低机位贴地微距，黄蛋约占画面高 1/4；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{A01}}=手表道具；{{A02}}=公园长椅空景。
0–3 秒：{{K_A}}{{A01}}黄蛋撸起袖子、郑重戴表，扣上表带后得意地抬腕看时间；表盘滴答声。
3–9 秒：{{A01}}表盘中央的细缝缓缓睁开，变成一只大眼睛，直勾勾盯着黄蛋；黄蛋吓得后仰，把手表翻面、塞进袖子、藏到背后——那只眼睛始终从各种角度盯着他。
9–15 秒：{{R01}}黄蛋崩溃，把手表按在长椅上；手表伸出两只短小的黄铜色小手臂，把黄蛋的脸掰正、对着自己；黄蛋瞳孔地震、张嘴无声尖叫；镜尾定格 0.5 秒。
【特效延续】夕阳长影延续到下一段。
【声音】表带扣响、滴答声、衣料摩擦、黄蛋倒吸气与无声尖叫的气声；无 BGM。
负向：人类、手指、字幕、水印、logo、比例失真、黄蛋变色、手表变成手机、眼睛长在黄蛋脸上、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。""",
        "part_b_prompt": """【首帧锁定】首帧使用 {{T_A}}（Part A 最后一帧：黄蛋被手表的小手臂掰着脸，瞳孔地震）；锁黄蛋与手表的位置/朝向/光线/背景，不重构图不换机位；第 0 秒从这一帧直接继续。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴。
【心易】12cm 白色蛋仔（参考 {{A03}}）：白色蛋壳、奶油色椭圆脸板、小黑点眼、粉色腮红、头顶粉色爱心天线、身体一圈蓝灰细环线、白色圆脚；神态平静、动作少而慢。
【道具】手表：同 Part A，表盘是一只搪胶卡通大眼睛，另有两只黄铜小手臂。
【场景与尺度】同 Part A 黄昏公园长椅；低机位贴地微距，两只蛋同高、各约占画面高 1/4；摄影机仍在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{A03}}=心易标准；{{A01}}=手表道具；{{KC}}=双栏词卡版式。
0–4 秒：{{T_A}}{{A03}}手表松开黄蛋的脸、跳下长椅，绕着他走一圈，像教练打量选手；黄蛋僵在原地、眼神跟着表转；心易从画面右侧滚入。
4–9 秒：{{A03}}{{A01}}{{KC}}心易举起双栏词卡（左栏眼睛图标＋"v. 看"，右栏手表＋"n. 手表"）；心易平静清晰地念："watch，看；watch，手表。"
9–13 秒：{{R01}}黄蛋恍然，指着手表："So the watch watches me?!"；手表点头；心易答："Yes. The watch watches you."
13–15 秒：{{A01}}手表掏出一个小本子，给黄蛋打分；黄蛋挤出微笑、比出大拇指；镜尾定格 1.5 秒。
【特效延续】夕阳长影延续；结尾不新增特效，定格干净。
【声音】手表走路的"嗒嗒"、纸页、风；4–9 秒心易念："watch，看；watch，手表。"；9–13 秒黄蛋："So the watch watches me?!"、心易："Yes. The watch watches you."；无 BGM。
负向：人类、手指、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、心易变黄、爱心天线变形、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。""",
        "notes": """【本画布做什么】
《蛋仔反转剧》EP01《watch＝看／手表》2×15 秒：黄蛋戴上手表准备看时间，表盘睁开一只眼反过来盯着他；Part B 心易揭双义。
集型丙·反转剧：A 义先立住，B 义实物接管，落点句同时含两义。

【运行顺序】
1. 先跑 A01 手表、A02 长椅空景、A03 心易（互不依赖，可同时）。
2. 跑 K_A（Part A 首帧）和 KC（双栏词卡）。
3. 跑 Part A（15s）。看完最后一帧：手表是否把黄蛋的脸掰正、眼睛是否清楚。
4. ⚠️ T_A 当前是《一蛋一剑》旧占位板：截 Part A 最后一帧上传替换（节点 id 和 token 不变）。替换前不要派发 Part B。
5. 跑 Part B（15s）。首帧就是 T_A，不要换别的图。
6. 剪辑：硬切；定格后切黑幕白字卡（约 1.5s）：watch／看；手表。台标、钩子后期贴。

【反转铁律】
- A 义必须在前 3–9 秒真的发生（戴表、看时间），不能只靠台词。
- B 义必须有实物证据（表睁眼、伸小手臂），不是角色听错。
- K_A 不剧透：表盘细缝闭合，别让首帧先睁眼。
- 词卡、黑幕卡、台词三处释义一致；落点句"So the watch watches me?!"必须出现。""",
    },
    "ep02": {
        "prefix": "egg-twist-ep02:v1",
        "file": "蛋仔记单词-EP02-crush-反转剧-2x15s-v1.monet",
        "canvas_name": "蛋仔记单词 · 集型丙 · EP02 crush · 反转剧 · 2×15s",
        "description": "无厘头反转剧单词小剧场：黄蛋捧花赴约，紧张得一屁股坐扁易拉罐；被压扁的罐子鼓起来红着脸爱上他。Part A 立预期/侵入/接管，Part B 揭双义。2×15s。",
        "has_r02": False,
        "a01_label": "【待生成】A01 反转实体 · 银色易拉罐（无脸无腮红）· 1K",
        "a02_label": "【待生成】A02 黄昏派对长桌空景 · 1K",
        "ka_label": "【待生成】K_A Part A 首帧 · 捧花迈步（罐子不剧透）· 1K",
        "kc_label": "【待生成】KC 双栏词卡 · crush/压碎/暗恋 · 1K",
        "parta_label": "【待生成】Part A · 0–15s · 立预期/侵入/接管",
        "partb_label": "【待生成】Part B · 15–30s · 升级/揭底/回环/收梗",
        "a01_prompt": """16:9 纯白底道具设定图，只生成一张。一个标准银色铝制易拉罐，直立、拉环完好，罐身干净无品牌、无文字，表面有极细的拉丝与轻微凹痕，真实铝材反光，柔和接触阴影。
背景 #FFFFFF 纯白，无投影、无水印、无 logo、无手。
负向：文字、品牌、拉环变形、人脸、眼睛、腮红、人类手指、水印、logo、比例失真、塑料感。""",
        "a02_prompt": """16:9 横版空景，不出现任何角色。黄昏室内派对长桌一角：长桌铺米白桌布，桌上有彩色纸杯蛋糕、纸盘，彩旗从上方斜拉过，背景是暖黄串灯与气球；长桌旁放一张矮木凳（凳面高度约与小角色身高相当），凳面留空（放一个易拉罐的位置）；暖色夕光从画面右侧窗户低角度射入，长影向左；低机位贴地视角，前景为 12cm 小角色留出空间；3D 卡通渲染+真实光影（皮克斯质感），柔和景深，35mm 颗粒。
无人物、无动物、无文字、无 logo、无水印。
负向：人类、角色、动物、文字、水印、logo、过曝、塑料高光过强、比例失真。""",
        "ka_prompt": """16:9 电影感首帧，第 0 秒画面，只生成一张。黄昏派对长桌旁（光线与机位跟 {{A02}} 一致）：黄蛋（参考 {{R01}} 外形、{{R00}} 比例：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子黑条纹+白色毛绒靴）捧着一小束花、脸红、整理领结，深吸一口气向前迈步；约会对象不入画，画面右侧只留空位；长桌旁的矮木凳上放着一个普通银色易拉罐（参考 {{A01}}，无脸、无腮红）。低机位贴地微距，黄蛋约占画面高 1/4，暖色长影；3D 卡通渲染+真实光影，搪胶材质次表面散射。
无文字浮层、无水印、无 logo。
负向：人类、手指、字幕、水印、logo、比例失真、黄蛋变色、易拉罐有脸、多余角色、过曝。""",
        "kc_prompt": """16:9 双栏单词卡版式，只生成一张。卡片占画面中央 70%，米白纸面、圆角、轻微纸张纹理：顶部大号单词"crush"（黑色无衬线粗体，拼写必须准确：c-r-u-s-h）+ 音标 /krʌʃ/；中部左右两栏对照——左栏一个被压扁的银色易拉罐小图（参考 {{A01}} 的银色铝材与拉环，画成压扁形态，抠白底）＋一行黑色"v. 压碎"，右栏一个红色简笔爱心图标（饱满、无眼睛）＋一行黑色"n. 暗恋"，两栏之间一个黑色等号；暖色派对照明从右上照入，卡片投柔和阴影。
除上述内容外无其他文字、无水印、无 logo、无人类、无手。
负向：拼写错误、乱码、多余文字、水印、logo、比例失真、爱心长眼睛、人类手。""",
        "part_a_prompt": """【首帧锁定】首帧使用 {{K_A}}；第 0 秒就是这一帧：黄昏派对长桌旁，黄蛋捧着花、脸红、迈步，矮木凳上有一个普通易拉罐。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；紧张、脸红，按"赴约表白"的正常逻辑行动。
【道具】易拉罐：标准银色铝罐（参考 {{A01}}），无品牌无文字；0–9 秒是普通罐子，9 秒后被压扁的罐身慢慢鼓回，浮出两团粉色腮红与一双爱心眼。
【场景与尺度】黄昏派对长桌旁，暖色夕光、长影向左；低机位贴地微距，黄蛋约占画面高 1/4；摄影机在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{A01}}=易拉罐道具；{{A02}}=派对长桌空景。
0–3 秒：{{K_A}}黄蛋捧着花、脸红、整理领结，深吸一口气朝画面右侧走去（约会对象不入画）；心跳声。
3–9 秒：{{A01}}黄蛋踩到地上的彩纸、脚下一滑，一屁股坐到矮木凳上，把易拉罐压扁"咔嚓"；他慌忙把扁罐捡起来藏到背后。
9–15 秒：{{A01}}背后的扁罐慢慢鼓回圆形，罐身浮出两团粉色腮红和一双爱心眼，"叮"一声；黄蛋回头，石化；镜尾定格 0.5 秒。
【特效延续】暖色彩旗与长影延续到下一段。
【声音】心跳、彩纸摩擦、滑倒、压扁"咔嚓"、罐子回弹"叮"、黄蛋倒吸气；无 BGM。
负向：人类、手指、字幕、水印、logo、比例失真、黄蛋变色、易拉罐长出手脚、爱心眼变人类眼睛、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。""",
        "part_b_prompt": """【首帧锁定】首帧使用 {{T_A}}（Part A 最后一帧：黄蛋回头看着鼓起来、脸红冒爱心眼的易拉罐）；锁黄蛋与罐子的位置/朝向/光线/背景，不重构图不换机位；第 0 秒从这一帧直接继续。
【角色】黄蛋：12cm 黄色蛋仔，黄色蛋壳、浅奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴。
【心易】12cm 白色蛋仔（参考 {{A03}}）：白色蛋壳、奶油色椭圆脸板、小黑点眼、粉色腮红、头顶粉色爱心天线、身体一圈蓝灰细环线、白色圆脚；平静、动作少而慢。
【道具】心形易拉罐：罐身鼓回圆形、两团粉色腮红、一双爱心眼，能滚动、能递花；不出现人手人脚。
【场景与尺度】同 Part A 黄昏派对长桌旁；低机位贴地微距，两只蛋同高、各约占画面高 1/4；摄影机仍在南侧，不跳轴。
【基调】3D 卡通渲染+真实光影（皮克斯质感、搪胶材质、次表面散射）；35mm 颗粒；真实物理；无 BGM、无字幕、无文字浮层、无水印。
【图片引用】{{R00}}=四小只身高比例；{{R01}}=黄蛋标准；{{A03}}=心易标准；{{A01}}=易拉罐道具；{{KC}}=双栏词卡版式。
0–4 秒：{{T_A}}{{A01}}心形罐子滚到黄蛋脚边、蹭他的脚；黄蛋一寸寸后退。
4–9 秒：{{A03}}{{A01}}{{KC}}心易举起双栏词卡（左栏压扁罐＋"v. 压碎"，右栏爱心＋"n. 暗恋"）；心易平静清晰地念："crush，压碎；crush，暗恋。"
9–13 秒：{{R01}}黄蛋指着罐子："I crushed the can... and now the can has a crush on me?!"；心易："Exactly. Crush."
13–15 秒：{{A01}}罐子递上一朵被压扁的小花；黄蛋接也不是、不接也不是；镜尾定格 1.5 秒。
【特效延续】暖色彩旗与长影延续；结尾不新增特效，定格干净。
【声音】罐子滚动、纸花摩擦；4–9 秒心易念："crush，压碎；crush，暗恋。"；9–13 秒黄蛋："I crushed the can... and now the can has a crush on me?!"、心易："Exactly. Crush."；无 BGM。
负向：人类、手指、文字浮层、字幕、水印、logo、比例失真、黄蛋变色、心易变黄、爱心天线变形、罐子长出手脚、多余角色、塑料高光过强、卡通描边、过曝、瞬移、漂浮。""",
        "notes": """【本画布做什么】
《蛋仔反转剧》EP02《crush＝压碎／暗恋》2×15 秒：黄蛋捧花赴约，一屁股坐扁易拉罐；被压扁的罐子鼓起来红着脸爱上他；Part B 心易揭双义。
集型丙·反转剧：A 义先立住，B 义实物接管，落点句同时含两义。

【运行顺序】
1. 先跑 A01 易拉罐、A02 派对长桌空景、A03 心易（互不依赖，可同时）。
2. 跑 K_A（Part A 首帧）和 KC（双栏词卡）。
3. 跑 Part A（15s）。看完最后一帧：罐子是否鼓回、腮红和爱心眼是否清楚。
4. ⚠️ T_A 当前是《一蛋一剑》旧占位板：截 Part A 最后一帧上传替换（节点 id 和 token 不变）。替换前不要派发 Part B。
5. 跑 Part B（15s）。首帧就是 T_A，不要换别的图。
6. 剪辑：硬切；定格后切黑幕白字卡（约 1.5s）：crush／压碎；暗恋。台标、钩子后期贴。

【反转铁律】
- A 义必须在前 3–9 秒真的发生（赴约、坐扁罐子），不能只靠台词。
- B 义必须有实物证据（罐子鼓回、脸红、爱心眼），不是角色听错。
- K_A 不剧透：罐子无脸、无腮红，只是桌角一个普通易拉罐。
- 词卡、黑幕卡、台词三处释义一致；落点句"I crushed the can..."必须出现。""",
    },
}

TOKENS = ("R00", "R01", "R02", "A01", "A02", "A03", "K_A", "KC", "T_A")


def build(slug: str) -> Path:
    ep = EPISODES[slug]
    prefix = ep["prefix"]

    def nid(key: str) -> str:
        return "node-" + hashlib.md5((prefix + ":" + key).encode("utf-8")).hexdigest()[:8]

    def oid(kind: str, key: str) -> str:
        return "output-" + hashlib.md5((prefix + ":" + kind + ":" + key).encode("utf-8")).hexdigest()[:10]

    def link(text: str) -> str:
        for token in TOKENS:
            text = text.replace("{{" + token + "}}", "{{" + nid(token) + "}}")
        leftovers = re.findall(r"\{\{(?!node-)[^}]+\}\}", text)
        if leftovers:
            raise SystemExit(f"[{slug}] unreplaced tokens: {leftovers}")
        if "{{node-node-" in text:
            raise SystemExit(f"[{slug}] double prefix {{node-node-")
        return text

    ref_keys = ["R00", "R01"] + (["R02"] if ep["has_r02"] else [])

    nodes = []
    # column 00: reference assets
    nodes.append(make_input_image(nid("R00"), oid("input", "R00"),
                                  "R00 四小只身高比例（复用）", R00, 0, 0, width=320))
    nodes.append(make_input_image(nid("R01"), oid("input", "R01"),
                                  "R01 黄蛋标准（复用）", R01, 0, 200, width=300))
    if ep["has_r02"]:
        nodes.append(make_input_image(nid("R02"), oid("input", "R02"),
                                      "R02 粉蛋标准（复用）", R02, 0, 580, width=300))

    # column 01: assets
    nodes.append(make_gen_image(nid("A01"), ep["a01_label"], link(ep["a01_prompt"]), [], 400, 0))
    nodes.append(make_gen_image(nid("A02"), ep["a02_label"], link(ep["a02_prompt"]), [], 400, 260))
    nodes.append(make_gen_image(nid("A03"), "【待生成】A03 心易设定 · 1K", link(A03_PROMPT), [], 400, 520))

    # column 02: keyframe / card / tail placeholder
    ka_refs = ref_keys + ["A01", "A02"]
    nodes.append(make_gen_image(nid("K_A"), ep["ka_label"], link(ep["ka_prompt"]),
                                [nid(k) for k in ka_refs], 800, 0, height=180.0))
    nodes.append(make_gen_image(nid("KC"), ep["kc_label"], link(ep["kc_prompt"]),
                                [nid("A01")], 800, 220, height=180.0))
    nodes.append(make_input_image(
        nid("T_A"), oid("input", "T_A"),
        "【待替换⚠】T_A Part A 尾帧 → Part B 首帧（截 Part A 最后一帧替换，替换前勿派发 Part B）",
        T_A, 800, 470, width=320,
    ))

    # column 03: two video segments
    part_a = link(ep["part_a_prompt"])
    part_b = link(ep["part_b_prompt"])
    for name, p in (("Part A", part_a), ("Part B", part_b)):
        if len(p) > 1900:
            raise SystemExit(f"[{slug}] {name} prompt {len(p)} chars > 1900 target (hard 2000)")
    nodes.append(make_gen_video(
        nid("PartA"), ep["parta_label"], part_a, [nid(k) for k in ka_refs], nid("K_A"),
        1200, 0, duration=15,
    ))
    pb_refs = ref_keys + ["A01", "A03", "KC"]
    nodes.append(make_gen_video(
        nid("PartB"), ep["partb_label"], part_b, [nid(k) for k in pb_refs], nid("T_A"),
        1200, 310, duration=15,
    ))

    # notes
    nodes.append(make_text(nid("S0"), oid("text", "S0"), "S0 制作说明 · 先读", ep["notes"], 400, 800))

    # --- edges derived from refs / first frame (single source of truth)
    edges, seen = [], set()

    def edge(a: str, b: str):
        if (a, b) in seen:
            raise SystemExit(f"[{slug}] duplicate edge {a}->{b}")
        seen.add((a, b))
        edges.append({
            "id": "edge-" + hashlib.md5((a + ">" + b).encode("utf-8")).hexdigest()[:8],
            "sourceNodeId": a, "sourceHandle": "output",
            "targetNodeId": b, "targetHandle": "input",
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        })

    for n in nodes:
        if n["type"] != "gen-video":
            continue
        mp = n["params"]["model_params"]
        for r in mp["reference_images"]:
            edge(r["node_id"], n["id"])
        edge(mp["first_frame_image"]["node_id"], n["id"])
    for n in nodes:
        if n["type"] != "gen-image":
            continue
        for r in n["params"]["model_params"]["reference_images"]:
            edge(r["node_id"], n["id"])

    # --- groups = run order
    def group(key, label, keys, color, pad=30):
        ns = [next(n for n in nodes if n["id"] == nid(k)) for k in keys]
        x0 = min(n["meta"]["x"] for n in ns) - pad
        y0 = min(n["meta"]["y"] for n in ns) - pad
        x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
        y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
        return {
            "id": "group-" + hashlib.md5((prefix + ":group:" + key).encode("utf-8")).hexdigest()[:8],
            "nodeIds": [nid(k) for k in keys],
            "bounds": {"x": float(x0), "y": float(y0),
                       "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label,
            "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        }

    groups = [
        group("g00", "00 参考素材 · 复用 URL", ref_keys, "#E68BB3"),
        group("g01", "01 道具/场景/心易 · 先跑", ["A01", "A02", "A03"], "#8E8DE0"),
        group("g02", "02 首帧/词卡 · K_A、KC 先跑", ["K_A", "KC"], "#E8B85D"),
        group("g03", "03 尾帧 · Part A 跑完截帧替换", ["T_A"], "#B08E6A"),
        group("g04", "04 视频 Part A · 15s", ["PartA"], "#DC775D"),
        group("g05", "05 视频 Part B · 15s（T_A 替换后）", ["PartB"], "#DC775D"),
        group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
    ]

    # --- self checks (mirror 检查画布接线.py)
    ids = {n["id"] for n in nodes}
    assert len(ids) == len(nodes), f"[{slug}] duplicate node id"
    node_by_id = {n["id"]: n for n in nodes}
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        prompt = mp["prompt"]
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        if len(prompt) > (2000 if n["type"] == "gen-video" else 100000):
            raise SystemExit(f"[{slug}] prompt too long: {n['meta']['label']} {len(prompt)}")
        for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt):
            assert tok in node_by_id, f"[{slug}] missing token target {tok}"
            assert tok in refs or tok == ff, f"[{slug}] token {tok} not in refs/ff"
        for r in refs + ([ff] if ff else []):
            assert (r, n["id"]) in edge_set, f"[{slug}] ref without edge {r}->{n['id']}"
            rn = node_by_id[r]
            if rn["type"] == "input-image":
                assert rn["outputs"], f"[{slug}] empty input-image {rn['meta']['label']}"
        if mp.get("reference_audios"):
            raise SystemExit(f"[{slug}] reference_audios must be empty")
        if n["type"] == "gen-video":
            d = mp["duration"]
            assert isinstance(d, int) and 3 <= d <= 16, f"[{slug}] bad duration {d}"
            assert ff in prompt, f"[{slug}] first frame not named in prompt"
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by:
                raise SystemExit(f"[{slug}] groups overlap: {a['label']} / {b['label']}")
    grouped = [nid_ for g in groups for nid_ in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids), f"[{slug}] group coverage mismatch"

    canvas = {
        "schemaVersion": 2,
        "type": "monet.canvas",
        "exportedAt": NOW,
        "canvas": {
            "name": ep["canvas_name"],
            "description": ep["description"],
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    out = OUT / ep["file"]
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    downloads = Path.home() / "Downloads" / out.name
    shutil.copyfile(out, downloads)
    print(f"[{slug}] {out.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print(f"        Part A {len(part_a)} chars / Part B {len(part_b)} chars")
    print(f"        -> {out}")
    print(f"        -> {downloads}")
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    slugs = [arg] if arg in EPISODES else list(EPISODES)
    for slug in slugs:
        build(slug)


if __name__ == "__main__":
    main()
