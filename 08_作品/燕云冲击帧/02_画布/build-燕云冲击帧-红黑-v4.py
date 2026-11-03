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
OUT = HERE / "燕云冲击帧-红黑冲击帧-16x9-v4.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T10:30:00.000+08:00"
PREFIX = "ywsv"          # v3 专用前缀，与 v1/v2 节点 ID 不撞
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
  I＝把 T 转绘成的**水墨冲击帧**（单独一张图）

【两套风格，故意的】
  K/V＝写实电影感（游戏 IP 质感，无红、无水墨）
  I＝硬核二次元红黑白冲击帧（放射构图、赛璐璐硬边、猩红＋纯白）
【红只活在冲击帧里】K 与 V 一律不许出现红色；红只出现在 I 的爆点与飞白尾迹上。

——换角色/武器：替换 P1/P2，并同步改 K/V/I 九个节点提示词里的人物与武器描述。
"""

S0_TEXT = """【燕云冲击帧 · 三条 4s｜招式(写实) → 实色定格 → 冲击帧(红黑白 2D)】

为什么是结构（2026-10-30 改）：
平台视频节点只有「首帧＋参考图」，没有尾帧输入（两库 2609 个生成节点字段核查）。
所以"首帧→尾帧"只能这样落地：让视频自己走到定格，再把那一帧截出来驱动水墨图。
好处：定格姿势可控；水墨帧从真实末帧转绘，姿势必然一致；冲击帧是独立一张图，可换可重出。

跑序（组＝跑序，组内并行）：
00 上传（P1/P2 已预填，可直接跑）
→ 01 起势首帧 K1/K2/K3
→ 02 招式视频 V1/V2/V3（4s，结尾停在实色定格，**不要**在视频里让它转水墨）
→ 03 截帧：从每条 V 取最后一帧，替换 T1/T2/T3 的占位图（节点 ID 不变，只换 output 里的图）
→ 04 冲击帧 I1/I2/I3（把 T 改画成红黑白 2D 冲击帧；T 没换之前别跑，出来会是占位卡的画）

每镜剪辑（30fps）：
① V 演完 → 停在定格帧
② 定格帧 → 1 帧白（或 1 白 1 负片）→ 切冲击帧 I
③ I 保持 1.8–2.3s：参考片的冲击帧段就是全静止的，不需要动
④ 末尾渐暗 3 帧；三条之间 2 帧黑硬接

白闪帧数别猜：python 02_画布/量白闪.py <成片.mp4>

模型：生图 gpt-image-2（K 用 1K/medium，I 用 2K/high）；视频 seedance-2.0-mini
（最短 4s；16:9 · 720p · 带音 · 不挂音频引用）

纪律：**红只允许出现在 I（冲击帧）**，K/V 一律无红；K/V 写实、I 二维，两套风格不要互相污染；
一镜只有一个招式，招式一次走完不重复。
"""

# ---------------------------------------------------------------- 起势（K）
P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍黑带/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑外形/龙形霜纹/护手虹彩）。
【画面】中景全身，**起势**：人物侧身站定，剑**竖向举在身体右侧、挡住半张脸**，只露一只眼；
双膝微屈、重心在右腿；剑尚未出招。白发与衣摆被右后方来风吹动，脚下有雪纹。
【构图/机位】16:9 横版，平视略低；人物占画面高约 75%，站右三分；左侧三分之一是雪地留白与四五根旧木桩。
【光影/材质】侧逆光，冷调；人物压成暗块，白发边缘与剑刃吃冷白边光；剑尖一点暖金。
负向：已经在挥剑、出招、残影、多手多剑、人物过小、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_K2 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍/冰霜）；{tok('P2')}＝武器（锁冰晶剑外形/护手虹彩）。
【画面】半身，**起势**：人物侧身站定，右手按在剑柄上、剑**尚未出鞘**（剑在腰侧／斜背，鞘身可见）；
肩背微沉、肘部收起，像发力前一瞬的蓄；白发垂在肩前，风从右后来。
【构图/机位】16:9 横版，半身（腰以上），人物占画面高约 85%，站右三分；左侧留出雪的暗部与风的方向。
【光影/材质】侧逆光，冷调；手背与剑柄受一道冷白边光；面部只在暗部里有一点轮廓光。
负向：剑已出鞘、已举起、挥砍残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_K3 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/冰霜）；{tok('P2')}＝武器（锁冰晶剑身/护手）。
【画面】近景（胸以上＋持剑手），**起势**：人物半转过身，剑收在右侧腰际、剑尖向后；
脸在暗部，只露出一只眼与一道眉；风把白发刮过面颊。
【构图/机位】16:9 横版，近景，人物占画面高约 90%，脸在右三分；左下角是右手的剑柄与半截剑身。
【光影/材质】侧逆光，冷调；剑身有一道冷白反光；脸只有眼窝受光。
负向：已经刺出、剑身横贯画面、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

# ---------------------------------------------------------------- 招式（V，止于实色定格）
P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：第 0 秒就是"侧身、剑竖在右侧挡半张脸"的起势，机位/朝向/光向完全不变，不要一开始就已经出招。
【引用图片说明】{tok('K1')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【人物与武器】白发剑客，白袍黑腰封，双臂冰霜气劲；藏音·龙跃霄汉（冰晶长剑，护手一道虹彩）。
【镜头语言】16:9 · 4 秒；一镜到底，固定机位，仅 1.02 倍极缓推。全程挺拔站立、双脚不离地、不弯腰不下蹲。
0.0–0.5 秒：保持起势；白发与衣摆被右后方来风轻推，剑不动。
0.5–1.5 秒：**唯一一个招式——横剑前指**：剑从脸前落下至胸前的同一瞬翻腕横持，右臂抬起至与肩平、完全伸直，
剑尖直指画左；同时身体由侧转正、双腿与肩同宽站稳、下颌微收、眼神锁定画左；长发衣摆向画右后方扬起。招式一次走完，不重复挥砍。
1.5–4.0 秒：**保持这个结束姿势不动**（实色，不要变色）：只有衣摆与发丝被风轻推、雪粒从画面掠过；
镜头固定，人物与剑的位置一帧都不许变。
【风格】全片保持实色电影感，**不要变成水墨、不要黑白、不要灰化**——水墨在后期接。
【声音】衣料轻响与一声剑鸣，到点一记短促金属声，随后环境风声。
【负向】第二个招式、连续挥砍、跳起、腾空、旋转、弯腰、下蹲、弓步、镜头摇晃、定格时人物继续动、
转水墨、水墨化、黑白化、画面变灰、线条化、颜料感、发光眼、红、大面积金色光效、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

P_V2 = f"""【首帧锁定】首帧使用 {tok('K2')}：第 0 秒是"手按剑柄、剑未出鞘"的起势，机位/半身景别/朝向完全不变。
【引用图片说明】{tok('K2')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【镜头语言】16:9 · 4 秒；半身，一镜到底，固定机位，不推不摇。双脚不离地。
0.0–0.6 秒：保持起势；肩背再沉一分，手指扣紧剑柄，风把白发吹到脸侧。
0.6–1.5 秒：**唯一一个招式——拔剑上撩**：剑出鞘，沿身体右侧向上撩起，划出一道连续弧线，
右臂举过肩、剑身斜指右上、刃口朝天；身体被剑势带得微微仰起，衣袂与白发向上翻卷。招式一次完成，不重复。
1.5–4.0 秒：**保持上撩到顶的姿势不动**（实色）：只有衣袂与白发在顶端缓缓落定，雪粒掠过；
镜头固定，姿势一帧都不许变。
【风格】全片保持实色电影感，**不要转水墨、不要黑白、不要灰化**。
【声音】金属摩擦一声（出鞘），到顶一记清响，随后风声。
【负向】剑未出鞘、第二个招式、连续挥砍、双手放下、跳起、旋转、镜头运动、切镜、定格时继续挥动、
转水墨、水墨化、黑白化、画面变灰、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

P_V3 = f"""【首帧锁定】首帧使用 {tok('K3')}：第 0 秒是"半转身、剑收腰际"的起势，机位/近景景别/朝向完全不变。
【引用图片说明】{tok('K3')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【镜头语言】16:9 · 4 秒；近景，一镜到底，固定机位，不推不摇。双脚不离地。
0.0–0.5 秒：保持起势；呼吸可见，剑尖在腰后微微下沉，风把白发刮过面颊。
0.5–1.5 秒：**唯一一个招式——回身直刺**：拧腰带动右臂，剑从腰际向画面前方（略偏左上）一次贯出，
右臂完全伸直、肩线斜切画面，身体拧到位；剑身从画面右下斜贯到左上。招式一次完成，不收不回。
1.5–4.0 秒：**保持刺到最远的姿势不动**（实色）：只有发丝与衣袂被风带起，雪粒掠过；
镜头固定，姿势一帧都不许变。
【风格】全片保持实色电影感，**不要转水墨、不要黑白、不要灰化**。
【声音】一记吸气，出剑破空一声，到点一记闷响，随后风声。
【负向】剑收回、第二个招式、连续刺击、跳起、旋转、镜头运动、切镜、定格时继续动、
转水墨、水墨化、黑白化、画面变灰、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

# ---------------------------------------------------------------- 水墨冲击帧（I，转绘自 T）
P_I1 = f"""16:9 横版，硬核二次元／黑白漫画上色的单帧**冲击帧**插画。只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（人物位置、剑的角度、景别都不许改）；{tok('P1')}＝人物特征（白发、白袍黑带）；{tok('P2')}＝武器外形（冰晶长剑）。
【任务】把 {tok('T1')} 这一帧**改画成冲击帧**：二维平面动画质感，不是写实转绘、不是水墨画。
【构图·爆点】以**剑尖（画左）为爆点**做放射构图：粗犷密集的速度线从画面四角向剑尖强行汇聚；
剑身是一条笔直的**纯白刃**把画面劈成两半；人物在中轴偏右，白发与衣摆被拉成撕裂的墨笔触、向画右后方甩出；
中心有一点对称的能量漩涡（纯白芯、猩红外缘）。
【色彩】纯黑底占画面 60% 以上；猩红与纯白是唯二高光色；黑、红、白三色，**禁止中间调与彩色渐变**；
红只出现在剑尖爆点、飞白尾迹与漩涡外缘（面积约 15%），可点极少量明黄。
【质感】硬边缘色块（赛璐璐），边缘锐利；干笔飞白与泼墨飞溅；无柔和渐变、无体积光、无胶片颗粒、无景深。
【限制】严格 2D 平面；细节极简，画面干净不杂乱；禁止碎小纹理、颗粒、无意义斑点。
负向：写实、照片、3D渲染、柔和渐变、体积光、景深、胶片颗粒、彩色（蓝绿金紫）、复杂细节、碎纹理、多人物、文字、水印、logo、游戏UI。
"""

P_I2 = f"""16:9 横版，硬核二次元／黑白漫画上色的单帧**冲击帧**插画。只生成一张。
【引用图片说明】{tok('T2')}＝姿势与构图的唯一依据（上撩到顶的姿势、半身景别、剑的指向不许改）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形与护手虹彩。
【任务】把 {tok('T2')} 这一帧**改画成冲击帧**：二维平面动画质感。
【构图·爆点】以**剑尖（右上）为爆点**：速度线从画面左下向右上汇聚；出鞘的轨迹留下一道**猩红撕裂弧**（从腰侧划到剑尖），
弧上有干笔飞白；人物与剑是硬边黑色块＋纯白高光；中心一处小能量漩涡（白芯红外缘）。
【色彩】纯黑底 60% 以上；猩红＋纯白双高光；禁止中间调与彩色渐变；红集中在撕裂弧与爆点（约 20%）。
【质感】赛璐璐硬边；干笔飞白；无柔和渐变、无体积光、无颗粒、无景深。
【限制】严格 2D 平面；细节极简、干净不杂乱。
负向：写实、照片、3D渲染、柔和渐变、体积光、景深、胶片颗粒、彩色（蓝绿金紫）、复杂细节、碎纹理、多人物、文字、水印、logo、游戏UI。
"""

P_I3 = f"""16:9 横版，硬核二次元／黑白漫画上色的单帧**冲击帧**插画。只生成一张。
【引用图片说明】{tok('T3')}＝姿势与构图的唯一依据（刺到最远的姿势、近景、剑贯出画面的角度不许改）；{tok('P1')}＝人物特征（眼型与白发走向）；{tok('P2')}＝武器外形。
【任务】把 {tok('T3')} 这一帧**改画成冲击帧**：二维平面动画质感。
【构图·爆点】以**剑尖出画处（左上）为爆点**：剑路是一条纯白刃贯穿对角线，速度线沿剑路成束向后（右下）拖出；
人物半张脸在纯黑里，**眼里一点猩红**；爆点处一小片纯白过曝，外缘猩红外扩。
【色彩】纯黑底 60% 以上；猩红＋纯白；禁止中间调与彩色渐变；红只在爆点外缘与眼里的那一点（约 12%）。
【质感】赛璐璐硬边；干笔飞白；无柔和渐变、无体积光、无颗粒、无景深。
【限制】严格 2D 平面；极简：剑一笔、人两笔、眼一点；干净不杂乱。
负向：写实、照片、3D渲染、柔和渐变、体积光、景深、胶片颗粒、彩色（蓝绿金紫）、复杂细节、碎纹理、多人物、文字、水印、logo、游戏UI。
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

        gen_image(i["K1"], 420, 20, "【待生成】K1 ① 起势 · 横剑前指 1K", P_K1, [i["P1"], i["P2"]]),
        gen_image(i["K2"], 420, 330, "【待生成】K2 ② 起势 · 拔剑上撩 1K", P_K2, [i["P1"], i["P2"]]),
        gen_image(i["K3"], 420, 640, "【待生成】K3 ③ 起势 · 回身直刺 1K", P_K3, [i["P1"], i["P2"]]),

        gen_video(i["V1"], 820, 20, "【待生成】V1 ① 4s · 横剑前指（止于实色定格）", P_V1,
                  [i["P1"], i["P2"]], i["K1"]),
        gen_video(i["V2"], 820, 330, "【待生成】V2 ② 4s · 拔剑上撩（止于实色定格）", P_V2,
                  [i["P1"], i["P2"]], i["K2"]),
        gen_video(i["V3"], 820, 640, "【待生成】V3 ③ 4s · 回身直刺（止于实色定格）", P_V3,
                  [i["P1"], i["P2"]], i["K3"]),

        input_image(i["T1"], 1220, 20, "【占位】T1 ① 定格帧 · 跑完 V1 取末帧替换", ups[0]),
        input_image(i["T2"], 1220, 330, "【占位】T2 ② 定格帧 · 跑完 V2 取末帧替换", ups[1]),
        input_image(i["T3"], 1220, 640, "【占位】T3 ③ 定格帧 · 跑完 V3 取末帧替换", ups[2]),

        gen_image(i["I1"], 1620, 20, "【待生成】I1 ① 冲击帧·红黑白放射 2K", P_I1,
                  [i["T1"], i["P1"], i["P2"]], size="2K", quality="high"),
        gen_image(i["I2"], 1620, 330, "【待生成】I2 ② 冲击帧·撕裂弧 2K", P_I2,
                  [i["T2"], i["P1"], i["P2"]], size="2K", quality="high"),
        gen_image(i["I3"], 1620, 640, "【待生成】I3 ③ 冲击帧·剑路贯穿 2K", P_I3,
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
         "label": "01 起势首帧 K1/K2/K3",
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
         "label": "04 冲击帧 I · 红黑白 2D（改画自定格帧）",
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
            "name": "燕云冲击帧 · 红黑白冲击帧 4s（16:9）v4",
            "description": ("白发剑客 × 藏音·龙跃霄汉：K 起势 → V 招式（4s，写实、止于实色定格）→ 截末帧替换 T → I 把 T 改画成硬核二次元红黑白冲击帧 → 剪辑接 1 帧白＋冲击帧定格。"
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
