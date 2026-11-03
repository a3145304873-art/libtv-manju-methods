# -*- coding: utf-8 -*-
"""燕云冲击帧 v3：招式 → 实色定格 → 单独水墨冲击帧（Monet schemaVersion 2）

改动理由（2026-10-30 用户提问「首帧到尾帧逻辑是不是更好，冲击帧是不是单独生图」）：
  平台视频节点只有 first_frame_image ＋ reference_images，没有尾帧输入
  （两库 2609 个生成节点字段普查，见 00_方案/04-首尾帧与冲击帧分图.md）。
  所以"首帧→尾帧"只能这样落地：
    起势 K（首帧）→ 招式 V（4s，结尾停在**实色定格**，视频内不转水墨）
    → 截 V 的末帧替换 T（占位图）→ I 从 T **转绘**出水墨冲击帧 → 剪辑：定格→1帧白→水墨帧保持。
  好处：定格姿势可控、水墨帧与定格帧姿势必然一致、冲击帧是独立一张图（可换、可重出）。

结构（6 组，按跑序）：
  00 上传与设定   P1 人物 / P2 武器 / S1
  01 起势首帧     K1 / K2 / K3
  02 招式视频     V1 / V2 / V3（seedance-2.0-mini · 4s · 16:9 · 720p，止于实色定格）
  03 定格帧       T1 / T2 / T3（占位：跑完 V 后取末帧替换，节点 ID 不变）
  04 冲击帧       I1 / I2 / I3（从 T 转绘成水墨，2K）
  05 说明         S0

用法：python build-燕云冲击帧-首尾帧-v3.py
"""
import glob
import hashlib
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-劈砍刺-16x9-v6.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T10:30:00.000+08:00"
PREFIX = "ywsx"          # v3 专用前缀，与 v1/v2 节点 ID 不撞
BY = "linguanxi"

P1_UP = {
    "name": "P1-人物-白发剑客.png",
    "url": ("https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/"
            "canvas-e4318cc875/image/20261027-122555-bb6fa0be7e68df3f-p1-e4-ba-ba-e7-89-a9-"
            "e7-99-bd-e5-8f-91-e.png"),
    "width": 526, "height": 533, "size": 572149,
    "md5": "7e5dbc051eff3e58b92f5a973c017d1a",
}
P2_UP = {
    "name": "P2-武器-龙跃霄汉.png",
    "url": ("https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/"
            "canvas-e4318cc875/image/20261027-122556-5df2712152eae9b4-p2-e6-ad-a6-e5-99-a8-"
            "e9-be-99-e8-b7-83-e.png"),
    "width": 632, "height": 711, "size": 528519,
    "md5": "df2829d66050b0a95f9c6819ac355f86",
}


def load_placeholders():
    """从「四小只 v18 尾帧占位」画布里读三个已上传的尾帧占位图（同账号 storage，可跨画布复用）。"""
    pats = [r"E:\漫剧项目\ai-drama\_共享\工作流研究\**\*v18*尾帧占位*.monet",
            r"E:\漫剧项目\ai-drama\_共享\工作流研究\**\*尾帧占位*.monet"]
    path = None
    for pat in pats:
        hits = glob.glob(pat, recursive=True)
        if hits:
            path = hits[0]
            break
    if not path:
        raise SystemExit("找不到尾帧占位来源画布（四小只 v18-尾帧占位）")
    c = json.load(open(path, encoding="utf-8"))["canvas"]
    ups = []
    for n in c["nodes"]:
        lab = (n.get("meta") or {}).get("label") or ""
        if n.get("type") == "input-image" and "占位" in lab and (n.get("outputs") or []):
            o = n["outputs"][0]
            ups.append({
                "name": o.get("name") or "尾帧占位.jpg",
                "url": o["value"],
                "width": (o.get("resolution") or {}).get("width", 1280),
                "height": (o.get("resolution") or {}).get("height", 720),
                "size": (o.get("metadata") or {}).get("size"),
                "md5": (o.get("metadata") or {}).get("md5"),
            })
    if len(ups) < 3:
        raise SystemExit(f"占位图不足 3 张（拿到 {len(ups)}）")
    return ups[:3], Path(path).name


def nid(key):
    return "node-" + hashlib.md5((PREFIX + key).encode("utf-8")).hexdigest()[:8]


ID = {k: nid(k) for k in
      ("P1", "P2", "S1", "K1", "K2", "K3", "V1", "V2", "V3",
       "T1", "T2", "T3", "I1", "I2", "I3", "S0")}


def tok(key):
    return "{{" + ID[key] + "}}"


S1_TEXT = """【角色与武器设定 · 只读不改】
人物：年轻男性剑客，白发（长过肩、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，双臂缠绕冰霜气劲；
面部清瘦、眉压低、眼神冷静；本组不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑，剑身半透、内部有龙形霜纹，护手一道极细虹彩（青→品红），
护手根部结着玉绿色冰晶簇，剑尖明光偏暖（曜日）。
配色：墨黑＋纸白＋冰青（主）；玉绿与曜金各 <5%；全组不用红。

【本组结构】每镜三段资产：
  K＝起势（招式开始前）
  V＝招式（4s，走完整条招式，结尾停在**实色定格**，视频内不转水墨）
  T＝从 V 截下来的定格帧（占位，跑完 V 后替换）
  I＝把 T 改画成的**水墨红黑冲击帧**（单独一张图）

——换角色/武器：替换 P1/P2，并同步改 K/V/I 九个节点提示词里的人物与武器描述。
"""

S0_TEXT = """【燕云冲击帧 · 三条 4s｜招式 → 实色定格 → 水墨冲击帧】

为什么是结构（2026-10-30 改）：
平台视频节点只有「首帧＋参考图」，没有尾帧输入（两库 2609 个生成节点字段核查）。
所以"首帧→尾帧"只能这样落地：让视频自己走到定格，再把那一帧截出来驱动水墨图。
好处：定格姿势可控；水墨帧从真实末帧转绘，姿势必然一致；冲击帧是独立一张图，可换可重出。

跑序（组＝跑序，组内并行）：
00 上传（P1/P2 已预填，可直接跑）
→ 01 起势首帧 K1/K2/K3
→ 02 招式视频 V1/V2/V3（4s：劈/砍/刺，结尾停在实色定格，**不要**在视频里让它转水墨）
→ 03 截帧：从每条 V 取最后一帧，替换 T1/T2/T3 的占位图（节点 ID 不变，只换 output 里的图）
→ 04 冲击帧 I1/I2/I3（把 T 改画成水墨红黑；T 没换之前别跑，出来会是占位卡的画）

每镜剪辑（30fps）：
① V 演完 → 停在定格帧
② 定格帧 → 1 帧白（或 1 白 1 负片）→ 切冲击帧 I
③ I 保持 1.8–2.3s：参考片的冲击帧段就是全静止的，不需要动
④ 末尾渐暗 3 帧；三条之间 2 帧黑硬接

白闪帧数别猜：python 02_画布/量白闪.py <成片.mp4>

模型：生图 gpt-image-2（K 用 1K/medium，I 用 2K/high）；视频 seedance-2.0-mini
（最短 4s；16:9 · 720p · 带音 · 不挂音频引用）

纪律：**红只活在 I（冲击帧）里**，K/V 一律无红；K/V 写实、I 水墨红黑，两套风格不要互相污染；
一镜只有一个招式，招式一次走完不重复；劈允许前倾与重心下沉，但不许弓步、蹲下、脚离地。
"""

# ---------------------------------------------------------------- 起势（K）
P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍黑带/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑外形/龙形霜纹/护手虹彩）。
【画面】中景全身，**起势·劈的准备**：双手握剑（右手主握、左手指节扣在柄尾），剑举过头顶右上方、剑尖朝后上；
身体后倾、重心压在右腿，整个人蓄着往下砸的势；剑尚未劈出。雪原，风吹白发与衣摆。
【构图/机位】16:9 横版，平视略低；人物占画面高约 75%，站右三分；左侧三分之一是雪地留白与四五根旧木桩。
【光影/材质】侧逆光，冷调；人压成暗块，白发边缘与剑刃吃冷白边光；剑尖一点暖金。
负向：已经劈下、剑在身前、残影、单手握剑、多手多剑、人物过小、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_K2 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍/冰霜）；{tok('P2')}＝武器（锁冰晶剑外形/护手虹彩）。
【画面】中景半身，**起势·砍的准备**：剑收在身体右侧、与腰同高，刃口朝外；上身向右拧紧蓄力、左肩朝镜头；
右肘收在肋侧，随时横向扫出；风把白发吹向左侧。
【构图/机位】16:9 横版，半身（腰以上），人物占画面高约 85%，站右三分；左侧留出雪与风的方向。
【光影/材质】侧逆光，冷调；手背与剑身受一道冷白边光；脸大半在暗部。
负向：已经横扫、剑在左侧、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_K3 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/冰霜）；{tok('P2')}＝武器（锁冰晶剑身/护手）。
【画面】近景（胸以上＋持剑手），**起势·刺的准备**：剑收在右侧腰际、剑尖朝前（朝镜头略偏左）；
身体半侧、重心压在后腿，像蹬地前的蓄；脸在暗部，只露一只眼与一道眉。
【构图/机位】16:9 横版，近景，人物占画面高约 90%，脸在右三分；左下角是右手的剑柄与半截剑身。
【光影/材质】侧逆光，冷调；剑身一道冷白反光；脸只有眼窝受光。
负向：已经刺出、剑身横贯画面、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

# ---------------------------------------------------------------- 招式（V，止于实色定格）
P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：第 0 秒就是"双手举剑过头顶右上、身体后倾"的蓄势，机位/朝向/光向完全不变，不要一开始就已经劈下。
【引用图片说明】{tok('K1')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【镜头语言】16:9 · 4 秒；一镜到底，固定机位，仅 1.02 倍极缓推。全程双脚不离地、不弓步、不蹲下。
0.0–0.5 秒：保持起势；肩背再收一分，风把白发推到脸侧，剑锋在头顶停着。
0.5–1.5 秒：**唯一一个招式——劈**：剑从头顶右上沿身体中线向下劈落，划出一条完整的垂直弧线，到身前腰下停住；
同时上身前倾约 15°、膝盖微屈、重心下沉一档（**不弓步、不蹲下、脚不离地**）；衣摆向前翻起。招式一次走完，不重复劈砍。
1.5–4.0 秒：**保持劈完的姿势不动**（实色，不要变色）：剑停在身前下方、刃口朝下，只有衣摆落定、雪粒掠过；镜头固定。
【风格】全片实色电影感，**不要变水墨、不要黑白、不要灰化**——风格在 I 里换。
【声音】举剑时衣料摩擦；劈下时一记破空；触底一记闷响；随后环境风声。
【负向】第二个招式、连续劈砍、跳起、腾空、旋转、弓步、蹲下、俯身过低、镜头摇晃、定格时人物继续动、
转水墨、水墨化、黑白化、画面变灰、发光眼、红、大面积金色光效、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

P_V2 = f"""【首帧锁定】首帧使用 {tok('K2')}：第 0 秒是"剑收在右侧腰际、上身右拧"的蓄势，机位/半身景别/朝向完全不变。
【引用图片说明】{tok('K2')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【镜头语言】16:9 · 4 秒；半身，一镜到底，固定机位，不推不摇。双脚不离地、不弓步。
0.0–0.5 秒：保持起势；上身再向右拧紧一点，剑刃朝外，风把白发吹向左侧。
0.5–1.5 秒：**唯一一个招式——砍**：剑从身体右侧向左横扫，划出一条**水平的弧线**，
停在左前方、与肩同高、刃口朝外；上身由右拧转正、再向左多转约 15°，衣摆与白发向左甩出。招式一次走完，不来回砍。
1.5–4.0 秒：**保持横扫收势不动**（实色）：剑横在左前方，只有衣摆与白发慢慢落定、雪粒掠过；镜头固定。
【风格】全片实色电影感，**不要变水墨、不要黑白、不要灰化**。
【声音】转身时衣料与金属摩擦；横扫一记「唰」；收势一声轻响；随后风声。
【负向】剑未动、第二个招式、连续横扫、来回砍、跳起、旋转、镜头运动、切镜、定格时继续挥动、
转水墨、水墨化、黑白化、画面变灰、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

P_V3 = f"""【首帧锁定】首帧使用 {tok('K3')}：第 0 秒是"剑收右腰、半转身"的蓄势，机位/近景景别/朝向完全不变。
【引用图片说明】{tok('K3')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【镜头语言】16:9 · 4 秒；近景，一镜到底，固定机位，不推不摇。双脚不离地。
0.0–0.5 秒：保持起势；呼吸可见，剑尖在腰侧微微下沉，风把白发刮过面颊。
0.5–1.5 秒：**唯一一个招式——刺**：后腿蹬地、拧腰、右臂直线向前贯出，剑沿**纵深**刺出（朝镜头略偏左），
近大远小明显、剑身透视缩短；右臂完全伸直、肩线斜切画面；停在刺出最远的一帧，不收不回。
1.5–4.0 秒：**保持刺到最远的姿势不动**（实色）：剑尖停在最前，只有发丝与衣袂被风带起、雪粒掠过；镜头固定。
【风格】全片实色电影感，**不要变水墨、不要黑白、不要灰化**。
【声音】一记吸气；出剑破空短促；到点一记闷响；随后风声。
【负向】剑收回、第二个招式、连续刺击、跳起、旋转、镜头运动、切镜、定格时继续动、
转水墨、水墨化、黑白化、画面变灰、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

# ---------------------------------------------------------------- 水墨冲击帧（I，转绘自 T）
P_I1 = f"""16:9 横版水墨·**红黑**冲击帧插画，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（人物位置、剑的角度、景别都不许改）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形。
【任务】把 {tok('T1')} 这一帧**改画成水墨红黑冲击帧**：宣纸上的大写意，不是写实转绘。
【构图·爆点】爆点＝**剑尖（画面下方中线）**：从剑尖向下炸开一团猩红墨爆（泼溅、飞白、撕裂笔触）；
一道**垂直墨瀑**自画面上方向下砸落、贯穿画面，充当速度线；人物是中轴焦墨块，白发与衣摆拉成飞白、向前下方甩出。
【色彩】宣纸白底＋焦墨＋猩红，红只在剑尖爆点与墨瀑尾端（约 15%）；无其他彩色。
【质感】浓墨泼洒、破笔、飞白、溅点；纸纹纤维可见；无一笔平滑渐变。
【限制】严格平面（纸上绘画感）；细节极简。
负向：赛璐璐、放射几何线、写实、照片、3D渲染、体积光、景深、胶片颗粒、青绿金紫、柔和渐变、碎纹理、多人物、文字、水印、logo、游戏UI。
"""

P_I2 = f"""16:9 横版水墨·**红黑**冲击帧插画，只生成一张。
【引用图片说明】{tok('T2')}＝姿势与构图的唯一依据（横斩收势、半身景别、剑的指向不许改）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形。
【任务】把 {tok('T2')} 这一帧**改画成水墨红黑冲击帧**。
【构图·爆点】爆点＝**剑尖（画面左侧）**：从剑尖向左炸开一团猩红墨爆；
一道**横向墨痕**从画面左侧贯穿到右侧、充当速度线（与剑身同向）；人物左拧收势，衣摆与白发向左甩成飞白笔触。
【色彩】纸白＋焦墨＋猩红，红只在剑尖爆点与墨痕尾端（约 15%）；无其他彩色。
【质感】浓墨泼洒、破笔、飞白、溅点；纸纹可见；无平滑渐变。
【限制】严格平面；细节极简。
负向：赛璐璐、放射几何线、写实、照片、3D、体积光、景深、颗粒、青绿金紫、渐变、碎纹理、多人物、文字、水印、logo、游戏UI。
"""

P_I3 = f"""16:9 横版水墨·**红黑**冲击帧插画，只生成一张。
【引用图片说明】{tok('T3')}＝姿势与构图的唯一依据（刺到最远、近景、剑的透视角度不许改）；{tok('P1')}＝人物特征（眼型与白发走向）；{tok('P2')}＝武器外形。
【任务】把 {tok('T3')} 这一帧**改画成水墨红黑冲击帧**。
【构图·爆点】爆点＝**剑尖（画面中心偏左、贴近镜头）**：墨从剑尖向四周**向心放射**，像一道浪朝镜头扑来；
剑身近大远小、透视缩短；人物半张脸在焦墨里，眼里一点纸白神光；衣摆与发丝向后拉成飞白。
【色彩】纸白＋焦墨＋猩红，红只在剑尖前一小片（约 12%）；无其他彩色。
【质感】浓墨泼洒、破笔、飞白；纸纹可见；无平滑渐变。
【限制】严格平面；极简：剑一笔、人两笔、眼一点。
负向：赛璐璐、放射几何线、写实、照片、3D、体积光、景深、颗粒、青绿金紫、渐变、碎纹理、多人物、文字、水印、logo、游戏UI。
"""


# ---------------------------------------------------------------- 节点工厂
def _base(n, t, x, y, w, h, label):
    return {
        "id": n, "type": t, "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": w, "height": h, "label": label, "resourceType": None},
        "outputs": [], "params": None, "specialParams": None, "config": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
    }


def input_image(n, x, y, label, up, w=320, h=200):
    out = {
        "id": f"output-{n[5:13]}", "status": "done", "error": None,
        "value": up["url"], "cover": None, "name": up["name"],
        "resolution": {"width": up["width"], "height": up["height"]},
        "source": None, "batchId": None, "execution": None, "graphRunId": None,
        "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        "metadata": {"size": up["size"], "md5": up["md5"]},
    }
    node = _base(n, "input-image", x, y, w, h, label)
    node["mainOutputId"] = out["id"]
    node["outputs"] = [out]
    return node


def input_text(n, x, y, w, h, label, text):
    out = {
        "id": f"output-{n[5:13]}", "status": "done", "error": None,
        "value": text, "cover": None, "name": label,
        "resolution": None, "source": None, "batchId": None, "execution": None,
        "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        "metadata": None,
    }
    node = _base(n, "input-text", x, y, w, h, label)
    node["mainOutputId"] = out["id"]
    node["outputs"] = [out]
    return node


def gen_image(n, x, y, label, prompt, refs, size="1K", quality="medium"):
    node = _base(n, "gen-image", x, y, 320, 280, label)
    node["params"] = {
        "num": 1, "model_id": "gpt-image-2",
        "model_params": {
            "prompt": prompt,
            "reference_images": [{"node_id": r} for r in refs],
            "aspect_ratio": "16:9", "image_size": size,
            "width": 1024, "height": 1024, "quality": quality,
            "output_format": "png", "moderation": "low", "auto_compress": True,
        },
    }
    return node


def gen_video(n, x, y, label, prompt, refs, first):
    node = _base(n, "gen-video", x, y, 320, 280, label)
    node["params"] = {
        "num": 1, "model_id": "seedance-2.0-mini",
        "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": r} for r in refs],
            "reference_audios": [],
            "first_frame_image": {"node_id": first},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": 4,
            "generate_audio": True, "watermark": False,
        },
    }
    return node


def build():
    i = ID
    ups, src_name = load_placeholders()
    nodes = [
        input_image(i["P1"], 20, 20, "【已预填】P1 人物 · 白发剑客", P1_UP),
        input_image(i["P2"], 20, 240, "【已预填】P2 武器 · 龙跃霄汉", P2_UP),
        input_text(i["S1"], 20, 470, 320, 400, "S1 角色与武器设定", S1_TEXT),

        gen_image(i["K1"], 420, 20, "【待生成】K1 ① 起势 · 劈（举剑过头）1K", P_K1, [i["P1"], i["P2"]]),
        gen_image(i["K2"], 420, 330, "【待生成】K2 ② 起势 · 砍（右侧蓄）1K", P_K2, [i["P1"], i["P2"]]),
        gen_image(i["K3"], 420, 640, "【待生成】K3 ③ 起势 · 刺（收腰）1K", P_K3, [i["P1"], i["P2"]]),

        gen_video(i["V1"], 820, 20, "【待生成】V1 ① 4s · 劈 ↓", P_V1,
                  [i["P1"], i["P2"]], i["K1"]),
        gen_video(i["V2"], 820, 330, "【待生成】V2 ② 4s · 砍 ↔", P_V2,
                  [i["P1"], i["P2"]], i["K2"]),
        gen_video(i["V3"], 820, 640, "【待生成】V3 ③ 4s · 刺 →", P_V3,
                  [i["P1"], i["P2"]], i["K3"]),

        input_image(i["T1"], 1220, 20, "【占位】T1 ① 定格帧 · 跑完 V1 取末帧替换", ups[0]),
        input_image(i["T2"], 1220, 330, "【占位】T2 ② 定格帧 · 跑完 V2 取末帧替换", ups[1]),
        input_image(i["T3"], 1220, 640, "【占位】T3 ③ 定格帧 · 跑完 V3 取末帧替换", ups[2]),

        gen_image(i["I1"], 1620, 20, "【待生成】I1 ① 冲击帧 · 垂直墨瀑 2K", P_I1,
                  [i["T1"], i["P1"], i["P2"]], size="2K", quality="high"),
        gen_image(i["I2"], 1620, 330, "【待生成】I2 ② 冲击帧 · 横向墨痕 2K", P_I2,
                  [i["T2"], i["P1"], i["P2"]], size="2K", quality="high"),
        gen_image(i["I3"], 1620, 640, "【待生成】I3 ③ 冲击帧 · 向心放射 2K", P_I3,
                  [i["T3"], i["P1"], i["P2"]], size="2K", quality="high"),

        input_text(i["S0"], 20, 1030, 1520, 420, "S0 制作说明", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["K1"]), (i["P2"], i["K1"]),
        (i["P1"], i["K2"]), (i["P2"], i["K2"]),
        (i["P1"], i["K3"]), (i["P2"], i["K3"]),
        (i["P1"], i["V1"]), (i["P2"], i["V1"]), (i["K1"], i["V1"]),
        (i["P1"], i["V2"]), (i["P2"], i["V2"]), (i["K2"], i["V2"]),
        (i["P1"], i["V3"]), (i["P2"], i["V3"]), (i["K3"], i["V3"]),
        (i["T1"], i["I1"]), (i["P1"], i["I1"]), (i["P2"], i["I1"]),
        (i["T2"], i["I2"]), (i["P1"], i["I2"]), (i["P2"], i["I2"]),
        (i["T3"], i["I3"]), (i["P1"], i["I3"]), (i["P2"], i["I3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bounds_for(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        {"id": "group-ywsw-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 上传与设定（已预填）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywsw-1", "nodeIds": [i["K1"], i["K2"], i["K3"]],
         "bounds": bounds_for([i["K1"], i["K2"], i["K3"]]),
         "label": "01 起势首帧 K1/K2/K3（劈/砍/刺）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywsw-2", "nodeIds": [i["V1"], i["V2"], i["V3"]],
         "bounds": bounds_for([i["V1"], i["V2"], i["V3"]]),
         "label": "02 招式视频 4s · 止于实色定格",
         "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "group-ywsw-3", "nodeIds": [i["T1"], i["T2"], i["T3"]],
         "bounds": bounds_for([i["T1"], i["T2"], i["T3"]]),
         "label": "03 定格帧 T · 占位，截末帧替换后再跑 04",
         "style": {"accent": None, "opacity": None, "borderColor": "#C8C2B4"}},
        {"id": "group-ywsw-4", "nodeIds": [i["I1"], i["I2"], i["I3"]],
         "bounds": bounds_for([i["I1"], i["I2"], i["I3"]]),
         "label": "04 冲击帧 I · 水墨红黑（改画自定格帧）",
         "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywsw-5", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "05 制作说明",
         "style": {"accent": None, "opacity": None, "borderColor": "#888888"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 劈砍刺 三招（16:9）v6",
            "description": ("白发剑客 × 藏音·龙跃霄汉：K 起势 → V 招式（4s，写实，止于实色定格）→ 截末帧替换 T → I 改画成水墨红黑冲击帧 → 剪辑接 1 帧白＋冲击帧定格。三镜＝劈↓ / 砍↔ / 刺→。"
                            "平台无尾帧输入，故用「截帧驱动下一张图」实现首尾帧逻辑。"
                            f"占位图取自 {src_name}。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywsw-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
                "targetNodeId": t, "targetHandle": "input",
                "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
            } for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }
    return doc


def self_check(doc):
    import re
    c = doc["canvas"]
    nodes, edges, groups = c["nodes"], c["edges"], c["groups"]
    by_id = {n["id"]: n for n in nodes}
    problems = []
    if len(by_id) != len(nodes):
        problems.append("节点 ID 重复")
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    node_group = {}
    for g in groups:
        for n in g["nodeIds"]:
            if n in node_group:
                problems.append(f"节点重复分组: {n}")
            node_group[n] = g["label"]
    for n in nodes:
        if n["id"] not in node_group:
            problems.append(f"节点不在分组: {n['id']}")
    gmap = {g["label"]: g["nodeIds"] for g in groups}
    for s, t in edge_set:
        for lab, ids in gmap.items():
            if s in ids and t in ids:
                problems.append(f"同组内依赖边: [{lab}] {s}->{t}")
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = (n.get("params") or {}).get("model_params") or {}
        prompt = mp.get("prompt") or ""
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        label = n["meta"]["label"]
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for tk in toks:
            if tk not in by_id:
                problems.append(f"引用节点不存在: {label} -> {tk}")
            if tk not in refs and tk != ff:
                problems.append(f"引用未挂字段: {label} -> {tk}")
        if "{{node-node-" in prompt:
            problems.append(f"双前缀: {label}")
        for r in refs + ([ff] if ff else []):
            if (r, n["id"]) not in edge_set:
                problems.append(f"字段挂了没连线: {label} <- {r}")
            rn = by_id.get(r)
            if rn and rn["type"] == "input-image" and not rn.get("outputs"):
                problems.append(f"被引用的上传节点是空的: {label} <- {r}")
        if n["type"] == "gen-video":
            if ff and ff not in toks:
                problems.append(f"首帧未在正文点名: {label}")
            if len(prompt) > 2000:
                problems.append(f"prompt 超 2000 字: {label} ({len(prompt)})")
            if mp.get("duration") != 4:
                problems.append(f"时长不是 4s: {label}")
    for a_i, a in enumerate(groups):
        ba = a["bounds"]
        for b in groups[a_i + 1:]:
            bb = b["bounds"]
            if (ba["x"] < bb["x"] + bb["width"] and ba["x"] + ba["width"] > bb["x"]
                    and ba["y"] < bb["y"] + bb["height"] and ba["y"] + ba["height"] > bb["y"]):
                problems.append(f"分组 bounds 重叠: {a['label']} / {b['label']}")
    return problems, edges


def main():
    doc = build()
    problems, edges = self_check(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    c = doc["canvas"]
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(c['nodes'])} / 边 {len(edges)} / 组 {len(c['groups'])}")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()
