# -*- coding: utf-8 -*-
"""Build the 17s morose key-line canvas.

V1 8s: Xinyi performs silently (want / Yaya's hands hand over the box / open box / no shredded pork / droop).
T_A -> V2 6s: Yaya rises from behind the table, says the only causal line "没有肉丝，很失落——所以 morose，就是失落的意思。"; Xinyi ka-bo.
Card 3s. Total 17s.

Output: 02_画布/EP01-morose-关键句-16s-v1.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "morose-keyline-16s:v1"
OUT = HERE / "EP01-morose-关键句-16s-v1.monet"

UP = json.loads((ROOT / "04_素材" / "参考" / "15s-morose-关键句" / "upload.json").read_text(encoding="utf-8"))
XIN = json.loads((ROOT / "01_资产" / "角色" / "心易-水豚-upload.json").read_text(encoding="utf-8"))
MOR = json.loads((ROOT / "01_资产" / "角色" / "morose-refs-upload.json").read_text(encoding="utf-8"))
R02 = XIN
R02E = MOR["心易-水豚-眼睛参考"]
TA = MOR["T_A-占位-替换V1尾帧"]
R4A = UP["候选-芽芽-4A-玄凤兜帽-经典灰-毛绒-v1"]
LOGO = UP["logo-icon-金色-中值去水印"]


def nid(key):
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode()).hexdigest()[:8]


def oid(key):
    return "output-" + hashlib.md5((PREFIX + ":out:" + key).encode()).hexdigest()[:10]


def input_image(key, label, info, x, y, width=260.0):
    h = round(width * info["height"] / info["width"], 1)
    return {
        "id": nid(key), "type": "input-image", "mainOutputId": oid(key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": h,
                 "label": label, "resourceType": None},
        "outputs": [{
            "id": oid(key), "status": "done", "error": None, "value": info["url"], "cover": None,
            "name": info["name"], "resolution": {"width": info["width"], "height": info["height"]},
            "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            "metadata": {"size": info["size"], "md5": info["md5"]},
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_image(key, label, prompt, refs, x, y, width=340.0, height=224.0):
    return {
        "id": nid(key), "type": "gen-image", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
            "prompt": prompt, "reference_images": [{"node_id": nid(k)} for k in refs],
            "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 1024,
            "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_video(key, label, prompt, refs, ff, x, y, duration):
    return {
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 340.0, "height": 224.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": nid(k)} for k in refs],
            "reference_audios": [], "first_frame_image": {"node_id": nid(ff)},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": duration,
            "generate_audio": True, "watermark": False,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def text_node(key, label, text, x, y, width=460.0, height=500.0):
    return {
        "id": nid(key), "type": "input-text", "mainOutputId": oid(key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [{"id": oid(key), "status": "done", "error": None, "value": text,
                     "cover": None, "name": label, "resolution": None, "source": None,
                     "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": None}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def link(s, keys):
    for k in keys:
        s = s.replace("[[" + k + "]]", "{{" + nid(k) + "}}")
    assert "[[" not in s, "unreplaced token"
    return s


A06_PROMPT = """16:9 电影感内景空景，只生成一张。街边小饭馆/快餐店内部：木质柜台＋收银机＋出菜口＋后厨窗口（背景有炒锅/灶台），几张木桌/塑料凳，墙上菜单只有食物图片、无文字/无价格；柜台后的墙上有一个小的金色 V/M 店标（参考 [[LOGO]]，金属/哑光，无文字）；暖黄灯，窗外傍晚街景虚化；3D卡通+真实光影（皮克斯/搪胶）。无人物、无手、无文字；除金色 V/M 店标外无其他 logo/水印。
负向：人物、手、文字、价格、其他logo、logo文字、水印、真实照片、过曝、杂乱。"""
A10_PROMPT = """16:9 纯白底道具设定图：一块小饭馆菜单板/菜单牌，板上 4 个食物图片格（无文字、无价格），其中一格是青椒肉丝（青椒丝＋肉丝），其他格是简单的菜（番茄炒蛋/青菜/汤）；菜单板角落一个小金色 V/M 店标（参考 [[LOGO]]，无文字）；3D卡通+真实光影，轻微投影；无角色/手/文字；除金色 V/M 店标外无其他 logo/水印。
负向：文字、价格、角色、手、其他logo、logo文字、水印、真实照片、菜单乱码、多格文字。"""
B01C_PROMPT = """16:9 纯色暖灰背景（#8A7A6A），画面中央一个横向宽展开的思考泡：宽约70%、高约32%，圆角/云朵形，底部三个小圆点尾巴；扁平2D插画/矢量感，奶白色泡身，细深灰描边，极浅投影，没有厚度、没有毛绒、没有3D高光、没有立体边；
泡里一个横向椭圆白碟（碟边深灰、清楚），碟里清楚的青椒肉丝：几根粗的棕色肉丝＋几根绿色青椒丝，食物占碟面大部分；食物上面一个粗的红色X（两条红色斜线，清楚压住食物）；
无文字、无字母、无logo、无水印；不是手绘线稿、不是漫画描边、不是对话框；食物必须清楚可见，不能空白。
负向：3D、毛绒、厚边、立体厚度、圆球泡、竖高泡、空白气泡、空碟、白底白泡、食物太小、看不清、文字、字母、logo、水印、手绘线稿、漫画描边、对话框、人类、角色、手、真实照片、过曝、杂乱。"""
A09_PROMPT = """16:9 纯白底道具设定图：一个关着的白色外卖餐盒，盒盖合上，放在桌面；盒盖正面一个小金色 V/M 店标（参考 [[LOGO]]，无文字）；3D卡通+真实光影，轻微投影；无角色/手/文字；除金色 V/M 店标外无其他 logo/水印。
负向：打开的盒、食物露出、角色、手、文字、其他logo、logo文字、水印、真实照片。"""
A05_PROMPT = """16:9 纯白底道具设定图：一个打开的白色外卖餐盒，盒内白饭＋青椒，没有肉丝；盒侧/盒盖内侧一个小金色 V/M 店标（参考 [[LOGO]]，无文字）；3D卡通+真实光影，轻微投影；无角色/手/文字；除金色 V/M 店标外无其他 logo/水印。
负向：肉丝、角色、手、文字、其他logo、logo文字、水印、真实照片。"""
TAIL_PROMPT = """16:9 电影感产品静帧：木桌上一个空的外卖餐盒，盒盖放在旁边；盒盖正面/盒侧有金色 V/M 店标（参考 [[A05]] 的盒、[[LOGO]] 的标）；盒内只有青椒/空；暖光，浅景深；无文字、无角色、无手；产品镜头；3D卡通+真实光影。
负向：文字、字母、角色、手、logo文字、其他logo、真实照片、过曝、杂乱。"""

KA_PROMPT = """16:9 电影感首帧，第0秒，只生成一张。小饭馆柜台/桌边（参考 [[A06]]）：心易单人（参考 [[R02]]，眼睛严格按 [[R02E]]：白片＋深棕细圈、无瞳孔/虹膜/高光、不眨眼）在画面左1/3，站在桌边，两只短手指向墙上的菜单板（参考 [[A10]]）上的青椒肉丝图片；画面里只有心易一个角色，没有芽芽、没有其他人的手；心易头部右侧留出空白，方便后面加思考泡；桌上只有一把细长勺子，没有餐盒（餐盒稍后由芽芽的手从画右递入）；心易嘴巴闭合、不说话；无文字/气泡/字幕。暖黄灯，傍晚，3D卡通+真实光影。
负向：餐盒、打开/关着的盒子、肉丝、芽芽入镜/芽芽的手、其他人的手、心易说话、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、芽芽狗帽/猫帽/M标志、多余手臂/手指、文字/字幕/logo、人类、比例失真、过曝。"""

V1_PROMPT = """【规格与影像】8秒，16:9，Seedance 2.0 mini，720P，现场声音开启。3D卡通/毛绒质感（皮克斯/搪胶），真实光影、真实重力与接触重量；24帧观感、轻微运动模糊、柔和高光过渡与有纹理的暗部；自然有呼吸的表演，不是塑料CG、不是平面卡通、不是定格模型。画面干净，无文字/字幕/水印。
【实际素材引用】[[K_A]] 锁首帧：心易在画面左1/3、站在桌边、手指菜单，桌上只有一把细长勺子、没有餐盒，头部右侧留白；机位/光位/桌面高度从首帧起不换。[[A06]] 只锁小饭馆柜台、后厨窗口、墙上金色V/M店标和暖黄灯，不继承任何人物或手。[[A10]] 只锁菜单板：4个食物图片格、其中一格青椒肉丝、角落金色V/M，无文字。[[A09]] 只锁关着的白色外卖盒与盒盖上的金色V/M；这只盒由芽芽的手从画右递入，不是桌上原有。[[A05]] 只锁打开后的盒内：白饭＋青椒、没有肉丝；盒侧/盖内金色V/M。[[B01C]] 只锁思考泡样式：横版、扁平2D、宽>高、奶白泡身、细描边、横向椭圆盘＋青椒肉丝＋粗红X，无文字；泡是心易的想法，不是实物道具。[[R02]] 锁心易身份/体型/短手短脚；[[R02E]] 锁眼：白片＋深棕细圈、无瞳孔/虹膜/高光、不眨眼。[[R4A]] 只锁芽芽的两只短圆手/前臂：奶油色、白色手套尖、上臂蜜桃色肉垫、无手指；参考图里的头/帽/脸/身体/腿一律不进入本段，只取手部/前臂。
【现场光影与风】现场光：小饭馆暖黄顶灯＋后厨窗口暖光，心易在画面左1/3的桌边，桌面有柔和顶光；芽芽的手从画右的暗部伸入，手背有暖光边缘，不另打棚拍补光。前后镜共享同一灯位、衰减、遮挡和接触阴影；桌面反光弱，盒子/勺子有真实接触阴影。空间是傍晚小饭馆，空气基本静止，只有手递盒、掀盖、放盖、勺子碰盒带起轻微气流；不出现风、不出现室外街景大变化。
【空间轴线】机位在顾客侧、面对柜台和菜单墙；心易在画面左1/3，桌子横向占中下部；菜单在墙上偏左；勺子放在桌子右侧；芽芽在桌子右后方（画面右缘外/桌沿后），只把两只手从画右伸到桌面中央；递盒方向为画右→画中，心易从画左/画中接；芽芽的手撤回画右桌沿后。全程不越轴、不反打、不换到柜台内侧。
【逐镜时间线】
S1｜0.0–2.2秒｜中景｜35毫米/F4，固定：心易站在桌边，两只短手指向[[A10]]菜单板上的青椒肉丝图片，眼睛亮，发“咔啵！”（兴奋，非人话；嘴只轻轻开合，不做人话口型）；桌上只有勺子，没有餐盒；头部右侧留白；画面里没有芽芽。
S2｜2.2–4.0秒｜中近景｜50毫米/F4，同侧固定：两只奶油色短圆手（[[R4A]] 手部设计：白色手套尖、上臂蜜桃色肉垫、无手指）从画右伸入，托着关着的[[A09]]白色外卖盒（盒盖金色V/M朝上），把盒放到桌面中央；心易用两只短手接住盒子；递盒的手撤回画右桌沿后。画面里只能看到芽芽的两只短圆手＋前臂（肘部以下），不出现整条手臂、肩膀、身体、头、帽子；不是人类大手、不是单只大手；交接瞬间画面最多四只手（心易两只＋芽芽两只），不出现第三只/第五只。
S3｜4.0–6.2秒｜近景｜65毫米/F4，同侧微俯：心易把盒盖掀开，盖放在桌面、金色V/M朝上；盒内是[[A05]]的白饭＋青椒，没有肉丝；她拿细长勺子拨了两下青椒，找肉丝，没找到；耳朵从立到耷，发“咔啵？”（疑惑）；盒子、盖、勺子各一件，不增加。
S4｜6.2–8.0秒｜近景｜65毫米/F4，同侧固定：心易把勺子放回桌面，肩膀垮下，低头看盒；头右侧出现一个横向宽展开的扁平2D思考泡（参考[[B01C]]）：宽>高、奶白泡身、细描边、没有厚度/毛绒/3D高光；泡里一个横向椭圆盘，盘里青椒肉丝（棕色肉丝＋绿色青椒），上面粗红X；无文字；泡是她的想法，不是说话；停留约0.9秒后开始淡出，7.5秒完全消失；结尾0.5秒无泡，停在心易独自失落的姿势，稳定0.5秒；画面里没有芽芽。
【唯一声音窗口】0.0–0.4秒饭馆环境底噪；0.8–1.4秒心易“咔啵！”（兴奋，非人话）；2.2–2.8秒盒子落桌、手臂轻擦；4.0–4.6秒掀盖、4.6–5.2秒盖放桌；5.2–5.8秒心易“咔啵？”（疑惑）；5.4–5.8秒勺子碰盒两声；其余为安静环境声。无人类对白、无旁白、无BGM、无配乐、无字幕。
【连续性与尾状态】心易始终只有两只短手；芽芽只出现两只手/前臂，且递完就撤回桌沿后；盒子一只、盒盖一只、勺子一把，数量不变；盒盖在4.0秒前一直关着，盒内4.0秒后只有青椒、没有肉丝；思考泡只出现一次、无文字、不是实物；结尾心易独自失落，盒打开、盖在桌、勺在桌，头右侧留白、无泡，画面里没有芽芽；此尾帧就是T_A，下一段从这里接。所有动作正常速度，不重演、不镜像、不复制角色。
负向：芽芽露脸/帽子/身体/腿、整条手臂/长臂/肩膀/单只大手/人类手、第三只手、多双手、心易说人话/加词/人类口型、心易黑豆眼/瞳孔/高光、盒内有肉丝、空白气泡、空碟、泡里无食物、泡是3D/毛绒/厚边/竖高、文字/字幕/气泡文字、换机位/重拍/换光、慢速横移/渐变/白场/过曝。"""

V2_PROMPT = """【规格与影像】6秒，16:9，Seedance 2.0 mini，720P，现场声音开启。3D卡通/毛绒质感（皮克斯/搪胶），真实光影、真实重力与接触重量；24帧观感、轻微运动模糊、柔和高光过渡；自然有呼吸的表演，不是塑料CG、不是平面卡通、不是定格模型。画面干净，无文字/字幕/水印。
【实际素材引用】[[T_A]] 锁首帧：心易独自失落、盒打开只有青椒、盒盖在桌、勺子在桌，画面里没有芽芽；机位/光位/桌面高度从首帧起不换。[[A06]] 只锁小饭馆背景、后厨窗口、墙上金色V/M店标和暖黄灯，不继承任何人物/手。[[A05]] 只锁桌上的开盒：白饭＋青椒、没有肉丝；盒盖/盒侧金色V/M。[[R02]] 锁心易身份/体型/短手短脚；[[R02E]] 锁眼：白片＋深棕细圈、无瞳孔/虹膜/高光、不眨眼。[[R4A]] 锁芽芽全身基础形象：奶油蛋形身体、暖灰玄凤兜帽、黄色羽冠、蜜桃腮斑、小粉钩喙（闭合装饰）、短圆蛋仔手（白色手套尖/蜜桃色肉垫）、白色小靴、金色小叶徽章；无星形高光、无星星眼；表情由视频模型演，不用5A/5B表情图。
【现场光影与风】现场光与V1完全相同：暖黄顶灯＋后厨窗口暖光，心易在画面左1/3，芽芽从画面右侧桌沿后升起；两人共享同一灯位、衰减、遮挡和接触阴影，不另打补光；芽芽的帽顶/羽冠先接暖光边缘，脸从暗部进入光里。空间是傍晚小饭馆，空气基本静止，只有芽芽升起带起桌布/手臂轻动，无风、无室外大变化。
【空间轴线】机位仍在顾客侧、面对柜台和菜单墙；心易在画面左1/3，桌子横向占中下部；芽芽在画面右侧、桌子后方的桌沿后，先露帽顶/羽冠，再露眼睛/脸，再升到上半身；他不从画外走进来、不绕到心易身后、不越轴；心易不移动，只在结尾抬头看画右；盒子/盖/勺位置不变。
【逐镜时间线】
S1｜0.0–0.6秒｜中近景｜50毫米/F4，固定：画面右侧桌沿后，芽芽的黄色羽冠/暖灰帽顶先出现，接着眼睛和脸升起，最后上半身探出；他停在画面右侧、桌沿后，双手扶桌沿；表情由视频模型演：得意/笃定，眼睛半眯、嘴角上扬、肩膀松，不夸张；不出现星形高光/星星眼/人类粗眉/牙齿/舌头。
S2｜0.6–4.8秒｜近景｜65毫米/F4，同侧固定：芽芽看着心易和桌上的[[A05]]开盒，说唯一一句：“没有肉丝，很失落——所以 morose，就是失落的意思。”前半句得意/点破，后半句收成认真；只这一句，把因果说清；不朗诵、不邀功、不指向菜单、不加“她说”；口型只对这句话。
S3｜4.8–6.0秒｜近景｜65毫米/F4，同侧微推：心易抬头看画右的芽芽，发“咔……啵……”（低、慢、难过；非人话；嘴只轻轻开合）；芽芽收住，嘴巴闭合，不再说话；结尾停在两人同框/心易的失落表情，稳定0.4秒；画面里没有思考泡、没有文字。
【唯一声音窗口】0.0–0.5秒芽芽升起时桌沿/手臂轻擦；0.6–4.6秒芽芽唯一一句人声“没有肉丝，很失落——所以 morose，就是失落的意思。”；4.8–5.6秒心易“咔……啵……”（非人话）；其余为饭馆安静环境声。无旁白、无第二句人声、无BGM、无配乐、无字幕。
【连续性与尾状态】芽芽只有一只，心易只有一只；芽芽从桌沿后升起，不从画外走入；他的两只手就是V1递盒的那两只（同一手型/手臂），本段不再递物；盒子/盖/勺位置与T_A一致，不新增道具；心易不换位；结尾两人同框，盒仍打开、只有青椒，思考泡不出现；不镜像、不复制角色、不换机位/光。
负向：芽芽提前在首帧、芽芽从画外走入/绕到心易身后、芽芽额外多说/朗诵/邀功、芽芽表情夸张/崩坏/星形高光/星星眼/人类粗眉/牙齿/舌头、心易说人话/加词/人类口型、心易黑豆眼/瞳孔/高光、盒内有肉丝、文字/字幕/气泡、换机位/重摆/换光、慢速横移/渐变/白场/过曝。"""

S0_TEXT = """【本画布做什么】
morose 关键句版 17s（v1.2）：V1 心易指菜单点青椒肉丝；芽芽只伸出两只手，把关着的盒递给她（不露脸）；心易开盒，只有青椒、没有肉丝，头右侧出现横版扁平2D思考泡（肉丝＋红X）；V2 芽芽从桌沿后升起、露全身，把因果说清：“没有肉丝，很失落——所以 morose，就是失落的意思。”；尾部是带 logo 的空盒产品镜头＋屏幕字，不用纸卡。
V1 8s（指菜单/芽芽手递盒/开盒/思考泡/失落）＋ T_A ＋ V2 6s（芽芽升起/因果句）＋ 尾部 3s（TAIL＋屏幕字）＝17s。

【品牌】
金色 V/M 是“心易俱乐部”快餐店的店标：A06 店招 / A10 菜单 / A09+A05 盒盖；LOGO 是形状参考，AI 生成在道具上，不手贴。

【跑序】
1. 先跑 A06/A10/A09/A05/B01C/TAIL（TAIL 可最后跑；B01C 必须是横版、扁平2D、肉丝＋红X，不能空白/不能3D厚泡）。
2. 跑 K_A 首帧（只有心易，没有芽芽、没有餐盒；桌上只有勺子；心易指菜单，头右侧留白）。
3. 跑 V1 8s（0–2.2 指菜单；2.2–4.0 芽芽的两只短圆手/前臂从画右递关盒；4.0–6.2 开盒只有青椒；6.2–8.0 横版扁平思考泡＋失落；7.5s 后泡完全消失，结尾无泡）。
4. 截 V1 尾帧 → 替换 T_A。
5. 跑 V2 6s（首帧 T_A；芽芽从桌沿后升起、露全身；表情由视频模型演：得意/笃定→认真；只说一句，把“没肉丝→很失落→morose=失落”说清）。
6. 尾部：TAIL 产品镜头＋屏幕字“morose / 没肉丝，很失落 / 所以 morose＝失落的”；字后期/AI 核对；不用纸卡 KC。

【硬规则】
心易只咔啵；K_A/V1 不露芽芽的脸/帽/身体，V1 只有芽芽的两只短圆手/前臂（肘部以下）递盒；点单靠指菜单上的青椒肉丝图片，不靠台词；思考泡是横版、扁平2D、无文字、不是对白气泡；V2 芽芽从桌沿后升起（不是从画外走入），只说一句“没有肉丝，很失落——所以 morose，就是失落的意思。”；表情由视频模型演，不用 5A/5B；不说“她说”；无文字/字幕；盒内无肉丝；logo 只在店招/菜单/盒盖；尾部字不能错。
【静音测试】心易指菜单→芽芽的手递盒→开盒只有青椒→头旁肉丝＋红X→低头；静音也懂“她没吃到、失落”。V2 芽芽升起后把因果说清：没肉丝→很失落→morose=失落。"""


def main():
    nodes = [
        input_image("R02", "R02 心易·水豚标准（复用）", R02, 0, 0, width=220),
        input_image("R02E", "R02E 心易眼睛参考（复用）", R02E, 0, 420, width=220),
        input_image("R4A", "R4A 芽芽 4A 经典灰兜帽（无星）", R4A, 0, 700, width=220),
        input_image("LOGO", "LOGO 心易俱乐部·金色V/M（店标参考）", LOGO, 0, 1240, width=180),
        gen_image("A06", "【待生成】A06 小饭馆内景 · 柜台/店标/后厨窗口", link(A06_PROMPT, ["LOGO"]), ["LOGO"], 360, 0, width=300, height=169),
        gen_image("A10", "【待生成】A10 菜单板 · 青椒肉丝＋金色店标", link(A10_PROMPT, ["LOGO"]), ["LOGO"], 360, 200, width=300, height=169),
        gen_image("A09", "【待生成】A09 关盒 · 盒盖金色店标", link(A09_PROMPT, ["LOGO"]), ["LOGO"], 360, 400, width=300, height=169),
        gen_image("A05", "【待生成】A05 开盒 · 只有青椒＋金色店标", link(A05_PROMPT, ["LOGO"]), ["LOGO"], 360, 600, width=300, height=169),
        gen_image("B01C", "【待生成】B01C 思考泡 · 横版扁平2D · 青椒肉丝＋红X", B01C_PROMPT, [], 360, 800, width=300, height=169),
        gen_image("K_A", "【待生成】K_A 首帧 · 菜单/勺子/心易指（无盒/无芽芽）", link(KA_PROMPT, ["A06", "A10", "R02", "R02E"]), ["A06", "A10", "R02", "R02E"], 760, 0),
        input_image("T_A", "T_A 占位 · 先跑 V1，再替换成 V1 最后一帧", TA, 760, 260, width=300),
        gen_video("V1", "【待生成】V1 · 8s · 指菜单/芽芽手递盒/开盒/扁平泡/失落", link(V1_PROMPT, ["K_A", "A06", "A10", "A09", "A05", "B01C", "R02", "R02E", "R4A"]), ["A06", "A10", "A09", "A05", "B01C", "R02", "R02E", "R4A"], "K_A", 1180, 0, 8),
        gen_video("V2", "【待生成】V2 · 6s · 芽芽从桌沿后升起/表情由视频演/讲清没肉丝→morose", link(V2_PROMPT, ["T_A", "A06", "A05", "R02", "R02E", "R4A"]), ["A06", "A05", "R02", "R02E", "R4A"], "T_A", 1180, 300, 6),
        gen_image("TAIL", "【待生成】TAIL 尾部产品镜头 · 带店标空盒＋盒盖", link(TAIL_PROMPT, ["A05", "LOGO"]), ["A05", "LOGO"], 760, 600, width=340, height=191),
        text_node("S0", "S0 制作说明 · 先读", S0_TEXT, 1140, 600, width=400, height=500),
    ]
    by = {n["id"]: n for n in nodes}

    def group(key, label, keys, color, pad=20):
        ns = [by[nid(k)] for k in keys]
        x0 = min(n["meta"]["x"] for n in ns) - pad
        y0 = min(n["meta"]["y"] for n in ns) - pad
        x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
        y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
        return {"id": "group-" + hashlib.md5((PREFIX + ":group:" + key).encode()).hexdigest()[:8],
                "nodeIds": [nid(k) for k in keys],
                "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
                "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

    groups = [
        group("g00", "00 角色/品牌参考", ["R02", "R02E", "R4A", "LOGO"], "#E68BB3"),
        group("g01", "01 场景/道具/气泡 · 先跑", ["A06", "A10", "A09", "A05", "B01C"], "#8E8DE0"),
        group("g02", "02 首帧/尾帧 · K_A、T_A", ["K_A", "T_A"], "#E8B85D"),
        group("g03", "03 V1 · 8s · 指菜单/递盒/开盒/失落", ["V1"], "#DC775D"),
        group("g04", "04 V2 · 6s · 芽芽升起/因果句", ["V2"], "#DC775D"),
        group("g05", "05 尾部/说明 · 后期", ["TAIL", "S0"], "#7FB07F"),
    ]

    edges, seen = [], set()

    def edge(a, b):
        if (a, b) in seen:
            return
        seen.add((a, b))
        edges.append({"id": "edge-" + hashlib.md5((a + ">" + b).encode()).hexdigest()[:8],
                      "sourceNodeId": a, "sourceHandle": "output",
                      "targetNodeId": b, "targetHandle": "input",
                      "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR})

    for n in nodes:
        if n["type"] == "gen-video":
            mp = n["params"]["model_params"]
            for r in mp["reference_images"]:
                edge(r["node_id"], n["id"])
            edge(mp["first_frame_image"]["node_id"], n["id"])
        elif n["type"] == "gen-image":
            for r in n["params"]["model_params"]["reference_images"]:
                edge(r["node_id"], n["id"])

    ids_set = {n["id"] for n in nodes}
    by_id = {n["id"]: n for n in nodes}
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
            assert tok in by_id, f"missing {tok}"
            assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
        for r in refs + ([ff] if ff else []):
            assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
        assert not mp.get("reference_audios")
        if n["type"] == "gen-video":
            assert ff in mp["prompt"]
            assert 3 <= mp["duration"] <= 16
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by_, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
                raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
    grouped = [i for g in groups for i in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids_set), "group coverage mismatch"

    canvas = {"schemaVersion": 2, "type": "monet.canvas", "exportedAt": NOW,
              "canvas": {"name": "蛋仔记单词 · morose 关键句 16s v1",
                         "description": "V1 心易指菜单→芽芽双手递关盒（不露脸）→开盒只有青椒→横版扁平2D思考泡（B01C 肉丝＋X）→独自失落；V2 芽芽从桌沿后升起、把“没肉丝→很失落→morose=失落”说清；尾部 TAIL 带 logo 空盒产品镜头＋屏幕字；V1 8s＋V2 6s＋尾部 3s＝17s；不用纸卡。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()
