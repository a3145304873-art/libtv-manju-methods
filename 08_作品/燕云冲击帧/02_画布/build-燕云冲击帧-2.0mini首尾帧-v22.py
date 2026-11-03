# -*- coding: utf-8 -*-
"""燕云冲击帧 v17：只锁「资产」，姿势帧与视频重出

用户意见（2026-10-30）：V1 适配不好、几张首尾帧不合适 → 这些不用，优先复用能用的。
所以：
  · **复用**：A0 设定母版 / A1 脸 / A2 正面全身 / A3 侧面 / A4 背面 / A5 武器 / A6 握剑手（7 张，已生成，直接挂 URL）
  · **重出**：K1–K3 起势、E1–E3 到位（1K，便宜）、I1–I3 冲击帧（1K）、V1–V3 招式（5s，贵但要重跑）
  · **可选**：W1–W3 墨动（标【可选·先不跑】——墨动可以用 墨凝.py + 静帧推近在后期做）
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-2.0mini首尾帧-16x9-v22.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单.json").read_text(encoding="utf-8"))
CREATED = "2026-10-30T17:10:00.000+08:00"
PREFIX = "ywso"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V15 = load_mod("yanwu_v15b", "build-燕云冲击帧-发力-v15.py")
KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "E1", "E2", "E3", "V1", "V2", "V3",
        "I1", "I2", "I3", "W1", "W2", "W3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}
RMAP = {V15.ID[k]: ID[k] for k in V15.ID}


def tok(k):
    return "{{" + ID[k] + "}}"


def rm(s):
    for old, new in RMAP.items():
        s = s.replace(old, new)
    return s


HEAD = "16:9 横版电影级"
INK = "黑白单色水墨，高对比插画"
COMMON_NEG = "彩色、红色、写实照片、3D 渲染、平视、剑在身侧、居中对称、背景实体、文字、水印、logo、游戏UI"

P_K1 = f"""{HEAD}首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝全身（锁服装/比例）；{tok('A5')}＝武器。
【机位】**低机位仰视**近景（镜头在胸口高度、略向上仰）；人物在**右侧三分**。
【画面·起势】**侧身（右手侧朝镜头）**，右手持剑收在**右腰侧**、剑尖朝前下方（还没递出）；右臂屈着蓄力；左臂收在身后；重心**压后腿**；
上半张脸在暗部、只露一只眼；背景深度虚化、近黑。
【构图】头顶贴上缘、下缘裁到大腿；白只在左上一点；**前景留空**（给剑留位置）。
【光】右上方一束边缘光打脸与肩；实色、冷调；无红。
负向：正脸、剑已递出、剑在身前、全身入画、平视、{COMMON_NEG}。
"""

P_K2 = f"""{HEAD}首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【机位】**低机位仰视**半身；人物在右侧三分。
【画面·起势】上身**向右拧到接近背对镜头**，右手举剑过右肩、**右肘高于肩**、剑身斜向画外右上、剑尖出画；
左肩朝镜头、只露侧脸；重心在右腿。
【构图】头顶贴上缘、下缘裁到腰；前景留空。
【光】右上方边缘光；实色、冷调；无红。
负向：正对镜头、身体没转、剑在身前、全身入画、平视、{COMMON_NEG}。
"""

P_K3 = f"""{HEAD}首帧，只生成一张。
【引用图片说明】{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【机位】**低机位仰视**近景；人物在右侧三分。
【画面·起势】**低头**，右手持剑自然下垂、剑尖垂在**画面右下**（右臂在身体右侧、不外撇）；手腕微微内扣、右肩下沉；重心**明显下沉**一档；
上半张脸在暗部。
【构图】头顶贴上缘、下缘裁到胸；前景留空。
【光】右上方边缘光；实色、冷调；无红。
负向：抬头、剑在身前、全身入画、平视、{COMMON_NEG}。
"""

P_E1 = f"""{HEAD}**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K1')}＝起势（同机位同人，把剑送到正前方）；{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【机位】同机位、同低角度仰视。
【画面·到位】身体转正、右臂前送；**前景巨大的剑身占画面左侧三分之一、夸张透视缩短、剑尖直指观者**；
剑身自画面左下向右上斜出、**从下巴下方掠过、不遮眼**；以留白作金属高光、**刃口一条完整亮线**、带横向反光。
中景是人物上半身（右侧黄金分割），面部与右手为焦点；衣摆与发丝向后扬；重心压前腿。
【构图】三层景深：前景剑（大、边缘略虚）→ 中景人（清晰）→ 背景墨势（虚）。
【光】同起势；剑身留白高光。
负向：平视、剑在身侧、剑横着、没有前景剑、全身入画、{COMMON_NEG}。
"""

P_E2 = f"""{HEAD}**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K2')}＝起势（同机位同人，把剑横甩到前景）；{tok('A2')}＝全身；{tok('A5')}＝武器。
【机位】同机位、同低角度仰视。
【画面·到位】腰胯甩到左前、上身转正；**剑身前横贯画面下三分之一、剑尖出画左缘**，夸张透视、近大远小；
中景是人物上半身，脸朝镜头、右手与剑格清晰；衣摆与白发向左甩开；重心移到两腿之间。
【构图】三层景深：前景横贯的剑身 → 中景人 → 背景横墨。
【光】同上；剑身留白高光。
负向：上身仍背对、剑在右侧、剑竖着、没有前景剑、全身入画、{COMMON_NEG}。
"""

P_E3 = f"""{HEAD}**结束姿势**（尾帧图），只生成一张。
【引用图片说明】{tok('K3')}＝起势（同机位同人，把剑从下往上挑起来）；{tok('A1')}＝脸；{tok('A2')}＝全身；{tok('A5')}＝武器。
【机位】同机位、同低角度仰视。
【画面·到位】**抬头**；剑身从画面右下**向上挑出**、占右侧三分之一、**剑尖出画右上角**、夸张透视；
中景是人物上半身，脸朝镜头、下颌抬起；衣摆与白发向上翻卷；身体上拔（膝伸直、胯提起）。
【构图】三层景深：前景上挑的剑身 → 中景人 → 背景向上的墨浪。
【光】同上；剑身留白高光。
负向：低头、剑在下方、剑横着、没有前景剑、全身入画、{COMMON_NEG}。
"""

V_FORCE = ("【发力】腰胯先动、剑后到；重心在两腿之间明显转移；脚下雪面被蹬开、雪尘扬起；"
           "衣摆与发丝被带起；剑到位的一瞬有极短震颤。")
V_SPEED = ("【速度】动作在 0.4–0.5 秒内完成，快到只剩一个残影；其余时间保持不动、只留余势。"
           "禁止慢动作、匀速平移、只动一下、身体僵直。")

P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：侧身、剑收左下、低机位仰视的起势，机位/景别/光向完全不变。
【尾帧锁定】最后一帧必须停在 {tok('E1')}：剑身扑面、剑尖直指观者、重心压前腿。（该节点已同时挂 last_frame_image 与参考位）
【引用图片说明】{tok('K1')}＝首帧；{tok('E1')}＝尾帧；{tok('A2')}＝人物；{tok('A5')}＝武器。
【镜头语言】16:9 · 4 秒；低机位固定，不推不摇。
0.0–0.6 秒：保持起势，只有呼吸。
0.6–1.1 秒：**唯一招式——突刺**：后腿蹬地、腰胯先转、右臂把剑直线送出，剑尖直指观者；重心压到前腿。
{V_FORCE}
{V_SPEED}
1.1–4.0 秒：保持到位，只有雪尘落下、衣摆余势。
【风格】实色电影感，不要变水墨、不要黑白、不要加红。
【负向】慢动作、匀速平移、只动一下、身体僵直、挥砍、第二个动作、镜头运动、切镜、水墨、黑白、红、游戏UI、文字、水印、logo、卡通。
"""

P_V2 = f"""【首帧锁定】首帧使用 {tok('K2')}：剑举右肩后、上身右拧的起势，机位/景别/光向完全不变。
【尾帧锁定】最后一帧必须停在 {tok('E2')}：剑横贯前景、剑尖出画左缘。（已同时挂 last_frame_image 与参考位）
【引用图片说明】{tok('K2')}＝首帧；{tok('E2')}＝尾帧；{tok('A2')}＝人物；{tok('A5')}＝武器。
【镜头语言】16:9 · 4 秒；低机位固定，不推不摇。
0.0–0.6 秒：保持起势，腰胯绷着。
0.6–1.1 秒：**唯一招式——横斩**：腰胯先向左甩、上身跟着转、剑最后到，横贯到前景、剑尖出画左缘；重心移到两腿之间。
{V_FORCE}
{V_SPEED}
1.1–4.0 秒：保持到位，只有雪尘落下。
【风格】实色电影感，不要变水墨、不要黑白、不要加红。
【负向】慢动作、匀速平移、只动一下、身体僵直、来回砍、第二个动作、镜头运动、切镜、水墨、黑白、红、游戏UI、文字、水印、logo、卡通。
"""

P_V3 = f"""【首帧锁定】首帧使用 {tok('K3')}：剑尖垂左下、重心下沉的起势，机位/景别/光向完全不变。
【尾帧锁定】最后一帧必须停在 {tok('E3')}：剑从下向上挑出、剑尖出画右上、身体上拔。（已同时挂 last_frame_image 与参考位）
【引用图片说明】{tok('K3')}＝首帧；{tok('E3')}＝尾帧；{tok('A2')}＝人物；{tok('A5')}＝武器。
【镜头语言】16:9 · 4 秒；低机位固定，不推不摇。
0.0–0.6 秒：保持起势，重心沉着。
0.6–1.1 秒：**唯一招式——上挑**：手腕上挑、剑从右下挑到右上出画；身体被带得上拔（膝伸直、胯提起）。
{V_FORCE}
{V_SPEED}
1.1–4.0 秒：保持到位，只有雪尘落下。
【风格】实色电影感，不要变水墨、不要黑白、不要加红。
【负向】慢动作、匀速平移、只动一下、身体僵直、大幅上撩、第二个动作、镜头运动、切镜、水墨、黑白、红、游戏UI、文字、水印、logo、卡通。
"""

INK_TPL = """{INK}，古风男性剑客，只生成一张。
【引用图片说明】{E}＝姿势与构图的唯一依据（不许改姿势与机位）；{A2}＝人物特征；{A5}＝武器外形。
【人物】白发凌乱随风、面容冷峻、眼神锐利带杀气；肤色与面部亮部留白，靠水墨晕染表现五官立体。
【服装】白袍宽袖侠客长袍，衣纹以枯笔飞白与浓墨勾线交织；深色交领、深色宽腰封、右手黑护腕；
衣角与发丝随风扬起。
【动作】{ACT}
【构图·三层景深】前景（左侧至中下）：{FG}；中景（右侧黄金分割）：角色上半身，面部与右手为视觉焦点，
剑格与手连接处清晰、衣摆下垂；背景：大面积泼墨、狂草笔触、墨滴飞溅，**无具体实体**。
【光影】强黑白对比，留白即高光；光从右上方打向面部与剑身，边缘光锐利。
【限制】低机位仰视；黑白无彩。
负向：彩色、红色、写实照片、3D 渲染、平视、剑在身侧、背景实体（雪原/木桩/建筑）、居中对称、文字、水印、logo、游戏UI。
"""

P_I1 = INK_TPL.format(INK=INK, E=tok("E1"), A2=tok("A2"), A5=tok("A5"),
    ACT="侧身拔剑突刺——右手握剑柄、剑身平举向前递出，力量感与冲锋感极强。",
    FG="巨大的剑身占画面约三分之一，夸张透视缩短、**剑尖直指观者**；剑身以留白作金属高光，带横向反光与水墨泼洒痕")
P_I2 = INK_TPL.format(INK=INK, E=tok("E2"), A2=tok("A2"), A5=tok("A5"),
    ACT="横斩收势——腰胯甩到位、剑身横贯身前。",
    FG="巨大的剑身横贯画面下三分之一、剑尖出画左缘，夸张透视、近大远小；剑身留白高光、横墨痕贯穿")
P_I3 = INK_TPL.format(INK=INK, E=tok("E3"), A2=tok("A2"), A5=tok("A5"),
    ACT="上挑到位——手腕上挑、剑从下向上挑起，身体上拔。",
    FG="巨大的剑身自画面右下向上挑出、剑尖出画右上角，夸张透视；剑身留白高光、斜向墨浪向上甩")
W_TPL, S1, S0 = V15.W_TPL, V15.S1, V15.S0

# 只复用资产与原始素材（姿势帧/视频 按用户意见重出）
REUSE = {"P1": "P1 原始", "P2": "P2 原始", "A0": "A0", "A1": "A1", "A2": "A2",
         "A3": "A3", "A4": "A4", "A5": "A5", "A6": "A6"}
FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1].strip()
    for key, pref in REUSE.items():
        if core.startswith(pref):
            FOUND[key] = v
            break


def up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


def main():
    F = V15.V14.V10
    gi, ii, it = F.gen_image, F.input_image, F.input_text
    nodes = [
        ii(ID["P1"], 20, 20, "【已生成·复用】P1 原始人物", up("P1")),
        ii(ID["P2"], 20, 240, "【已生成·复用】P2 原始武器", up("P2")),
        it(ID["S1"], 20, 470, 320, 470, "S1 角色与武器设定", S1),

        ii(ID["A0"], 420, 20, "【已生成·复用】A0 设定母版", up("A0")),
        ii(ID["A1"], 820, 20, "【已生成·复用】A1 脸部特写", up("A1")),
        ii(ID["A2"], 820, 340, "【已生成·复用】A2 正面全身（锚）", up("A2")),
        ii(ID["A5"], 820, 660, "【已生成·复用】A5 武器白底", up("A5")),
        ii(ID["A3"], 1220, 20, "【已生成·复用】A3 侧面", up("A3")),
        ii(ID["A4"], 1220, 340, "【已生成·复用】A4 背面", up("A4")),
        ii(ID["A6"], 1220, 660, "【已生成·复用】A6 握剑手", up("A6")),

        gi(ID["K1"], 1620, 20, "【待生成·重出】K1 ① 起势 · 剑收右腰（低机位）", P_K1,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["K2"], 1620, 340, "【待生成·重出】K2 ② 起势 · 剑举右肩后（低机位）", P_K2,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["K3"], 1620, 660, "【待生成·重出】K3 ③ 起势 · 剑尖垂右下（低机位）", P_K3,
           [ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),

        gi(ID["E1"], 2020, 20, "【待生成·重出】E1 ① 到位 · 剑尖直指观者", P_E1,
           [ID["K1"], ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["E2"], 2020, 340, "【待生成·重出】E2 ② 到位 · 剑横贯前景", P_E2,
           [ID["K2"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
        gi(ID["E3"], 2020, 660, "【待生成·重出】E3 ③ 到位 · 剑挑出画右上", P_E3,
           [ID["K3"], ID["A1"], ID["A2"], ID["A5"]], size="1K", quality="medium"),
    ]

    def vid(n, x, y, label, prompt, refs, first, last):
        return {
            "id": n, "type": "gen-video", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
                "_task_mode": "standard", "prompt": prompt, "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in refs],
                "reference_videos": [], "reference_audios": [],
                "first_frame_image": {"node_id": first},
                "last_frame_image": {"node_id": last} if last else None,
                "aspect_ratio": "16:9", "resolution": "720p", "duration": 4,
                "generate_audio": True, "seed": -1}},
            "specialParams": None, "config": None,
            "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        }

    nodes += [
        vid(ID["V1"], 2420, 20, "【待生成·重出】V1 ① 4s · 刺", P_V1,
            [ID["A2"], ID["A5"], ID["E1"]], ID["K1"], ID["E1"]),
        vid(ID["V2"], 2420, 340, "【待生成·重出】V2 ② 4s · 斩", P_V2,
            [ID["A2"], ID["A5"], ID["E2"]], ID["K2"], ID["E2"]),
        vid(ID["V3"], 2420, 660, "【待生成·重出】V3 ③ 4s · 撩", P_V3,
            [ID["A2"], ID["A5"], ID["E3"]], ID["K3"], ID["E3"]),
        gi(ID["I1"], 2820, 20, "【待生成】I1 ① 冲击帧 · 黑白·剑指观者", P_I1,
           [ID["E1"], ID["A2"], ID["A5"]]),
        gi(ID["I2"], 2820, 340, "【待生成】I2 ② 冲击帧 · 黑白·横贯前景", P_I2,
           [ID["E2"], ID["A2"], ID["A5"]]),
        gi(ID["I3"], 2820, 660, "【待生成】I3 ③ 冲击帧 · 黑白·斜向上挑", P_I3,
           [ID["E3"], ID["A2"], ID["A5"]]),
        vid(ID["W1"], 3220, 20, "【可选·先不跑】W1 ① 墨动", W_TPL.format(img=tok("I1")), [ID["I1"]], ID["I1"], None),
        vid(ID["W2"], 3220, 340, "【可选·先不跑】W2 ② 墨动", W_TPL.format(img=tok("I2")), [ID["I2"]], ID["I2"], None),
        vid(ID["W3"], 3220, 660, "【可选·先不跑】W3 ③ 墨动", W_TPL.format(img=tok("I3")), [ID["I3"]], ID["I3"], None),
        it(ID["S0"], 420, 1050, 1520, 470, "S0 复用资产版 · 先读", S0),
    ]

    for _n in nodes:
        if _n["type"] == "gen-image":
            _p = _n["params"]["model_params"]["prompt"]
            if ("【构图" in _p) and ("【握法】" not in _p):
                _p = _p.replace("【构图", '【握法】右手正握剑柄：虎口朝剑格、食指扣在剑格下沿、其余三指环握、掌心贴柄；剑格在拳前约两指、剑身自拳背上方伸出；手腕与前臂成一条直线、不许折腕。左手并起食指与中指成剑指，护在右腕外侧（不许碰剑身、不许出现第三只手）。' + "\n【构图", 1)
            if _p.startswith(("16:9 横版电影级")) and ("【剪影】" not in _p) and ("结束姿势" not in _p):
                _p = _p.replace("【光】", '【剪影】剑与身体成一条斜线（不许平行）；肩一高一低、胯一前一后；头发、衣摆、流苏全部朝同一侧被带起。' + "\n【光】", 1)
            _n["params"]["model_params"]["prompt"] = _p

    pairs = [
        (ID["A1"], ID["K1"]), (ID["A2"], ID["K1"]), (ID["A5"], ID["K1"]),
        (ID["A1"], ID["K2"]), (ID["A2"], ID["K2"]), (ID["A5"], ID["K2"]),
        (ID["A1"], ID["K3"]), (ID["A2"], ID["K3"]), (ID["A5"], ID["K3"]),
        (ID["K1"], ID["E1"]), (ID["A1"], ID["E1"]), (ID["A2"], ID["E1"]), (ID["A5"], ID["E1"]),
        (ID["K2"], ID["E2"]), (ID["A2"], ID["E2"]), (ID["A5"], ID["E2"]),
        (ID["K3"], ID["E3"]), (ID["A1"], ID["E3"]), (ID["A2"], ID["E3"]), (ID["A5"], ID["E3"]),
        (ID["A2"], ID["V1"]), (ID["A5"], ID["V1"]), (ID["K1"], ID["V1"]), (ID["E1"], ID["V1"]),
        (ID["A2"], ID["V2"]), (ID["A5"], ID["V2"]), (ID["K2"], ID["V2"]), (ID["E2"], ID["V2"]),
        (ID["A2"], ID["V3"]), (ID["A5"], ID["V3"]), (ID["K3"], ID["V3"]), (ID["E3"], ID["V3"]),
        (ID["E1"], ID["I1"]), (ID["A2"], ID["I1"]), (ID["A5"], ID["I1"]),
        (ID["E2"], ID["I2"]), (ID["A2"], ID["I2"]), (ID["A5"], ID["I2"]),
        (ID["E3"], ID["I3"]), (ID["A2"], ID["I3"]), (ID["A5"], ID["I3"]),
        (ID["I1"], ID["W1"]), (ID["I2"], ID["W2"]), (ID["I3"], ID["W3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        ("00 素材（复用）", ["P1", "P2", "S1"], "#8E8DE0"),
        ("01 资产（已生成·复用）", ["A0", "A1", "A2", "A5"], "#5B8DE0"),
        ("02 资产派生（已生成·复用）", ["A3", "A4", "A6"], "#5BE0C8"),
        ("03 起势 K（重出）", ["K1", "K2", "K3"], "#E05B8D"),
        ("04 到位 E（重出）", ["E1", "E2", "E3"], "#E05B8D"),
        ("05 招式 V（重出）", ["V1", "V2", "V3"], "#E0A15B"),
        ("06 冲击帧 I（重出）", ["I1", "I2", "I3"], "#5BE0C8"),
        ("07 墨动 W（可选）", ["W1", "W2", "W3"], "#C8A15B"),
        ("08 说明", ["S0"], "#888888"),
    ]
    gl = []
    for k, (label, keys, color) in enumerate(groups):
        ids = [ID[x] for x in keys]
        gl.append({"id": f"g-ywsj-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
                   "style": {"accent": None, "opacity": None, "borderColor": color},
                   "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY})

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 2.0-mini 首尾帧（16:9）v22",
            "description": ("复用已生成的 A0–A6（7 张资产），姿势帧 K/E、冲击帧 I、招式 V 全部重出；"
                            "W 墨动标为可选（可后期用 墨凝.py 做）。"),
            "nodes": nodes,
            "edges": [{"id": "edge-" + hashlib.md5((str(k) + s + t).encode()).hexdigest()[:8],
                       "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
                       "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY}
                      for k, (s, t) in enumerate(pairs)],
            "groups": gl,
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(gl)}")
    print("复用:", sorted(FOUND))
    print("要跑:", [n["meta"]["label"] for n in nodes if n["type"].startswith("gen")])


if __name__ == "__main__":
    main()

