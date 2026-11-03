# -*- coding: utf-8 -*-
"""燕云冲击帧 · 三条 4s「招式 → 瞬间定格 → 水墨」画布 v2（Monet schemaVersion 2）

改版依据（2026-10-29 用户纠正）：冲击帧＝招式打完那一瞬间的定格，不是静态站姿海报。
所以每一镜的骨架是：起势（首帧 K）→ 唯一一个招式走完整条轨迹 → 招式到点的**那一帧**定格、
同帧炸白并整幅转水墨 → 水墨定格保持（尾帧目标 I）。
K 与 I 是**同一个招式的一头一尾**，姿势不同；V 负责把中间那 1 秒走完。

结构（5 组，按跑序）：
  00 上传与设定   P1 人物 / P2 武器 / S1 设定
  01 起势首帧     K1 横剑前指 / K2 拔剑上撩 / K3 回身直刺
  02 定格水墨     I1 / I2 / I3（各自＝该招式结束姿势的水墨版）
  03 三条视频     V1 / V2 / V3（seedance-2.0-mini · 4s · 16:9 · 720p）
  04 说明         S0

用法：python build-燕云冲击帧-三招-v2.py
"""
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
OUT = HERE / "燕云冲击帧-三招-16x9-v2.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-29T21:00:00.000+08:00"
PREFIX = "ywsy"          # 新前缀：v2 与 v1 同存时节点 ID 不许撞
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


def nid(key):
    return "node-" + hashlib.md5((PREFIX + key).encode("utf-8")).hexdigest()[:8]


ID = {k: nid(k) for k in
      ("P1", "P2", "S1", "K1", "K2", "K3", "I1", "I2", "I3", "V1", "V2", "V3", "S0")}


def tok(key):
    return "{{" + ID[key] + "}}"


S1_TEXT = """【角色与武器设定 · 只读不改】
人物：年轻男性剑客，白发（长过肩、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，双臂缠绕冰霜气劲；
面部清瘦、眉压低、眼神冷静；本组不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑，剑身半透、内部有龙形霜纹，护手一道极细虹彩（青→品红），
护手根部结着玉绿色冰晶簇，剑尖明光偏暖（曜日）。
配色：墨黑＋纸白＋冰青（主）；玉绿与曜金各 <5%；全组不用红。

【本组骨架】每镜＝一个完整招式：起势（K）→ 招式走完（V，约 1 秒）→ 招式到点那一帧定格、
同帧炸白并整幅转水墨 → 水墨定格（I）。K 与 I 是同一个招式的一头一尾，不是同一张图。

——换角色/武器：替换 P1/P2，并同步改 K/I/V 九个节点提示词里的人物与武器描述。
——招式跑偏（手型/剑路不对）时：补一张姿势参考图（P3）再出 v3 接线，不要手改画布连线。
"""

S0_TEXT = """【燕云冲击帧 · 三条 4s｜招式 → 瞬间定格 → 水墨】

三条各是一个完整招式，不是三张站姿海报：
  ① 横剑前指（中景全身）　② 拔剑上撩（半身）　③ 回身直刺（近景）

跑序（组＝跑序，组内并行）：
00 上传（P1/P2 已预填同账号存储，可直接跑）
→ 01 三张**起势**首帧（K1/K2/K3）：这是招式开始前的姿势，不是打完的姿势，跑的时候盯这一点
→ 02 三张**定格**水墨（I1/I2/I3）：这是该招式**结束**姿势的水墨版，依赖 01
→ 03 三条视频（V1/V2/V3）：把中间那 1 秒的招式走完，在到点那一帧定格转水墨

每镜 4s 节拍：
0.0–0.5 起势保持（只有风）
0.5–1.6 唯一一个招式，一次走完（拧腰/重心/剑路都要写清）
1.6–1.7 招式到点的一瞬 → 全屏炸白 1–2 帧，同帧整幅转水墨
1.7–4.0 水墨定格保持（按 I）：只有墨点飘落

剪辑三步（先量再决定，别猜）：
① 母版直接用 4s；要 3s → 头剪 0.5s（起势）+ 尾剪 0.5s（定格从 2.3s 压到 1.8s），不要剪掉招式本身
② 量白闪：python 02_画布/量白闪.py <成片.mp4>
   1 帧＝不动；2–3 帧＝接受；≥4 帧或干脆没有炸白，才在原来那段里替换「1 帧白 + 1 帧负片」（不切段）
③ 三条之间用 2 帧黑硬接，别叠化

模型锁定：生图 gpt-image-2（K 用 1K/medium，I 用 2K/high）；视频 seedance-2.0-mini
（最短 4s；16:9 · 720p · 带音 · 不挂音频引用）

纪律：全组不用红；曜金只给剑尖与刃口；虹彩只给护手；一镜只有一个招式；招式必须一次走完、不重复挥砍。
"""

# ---------------------------------------------------------------- ① 横剑前指
P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍黑带/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑外形/龙形霜纹/护手虹彩）。
【画面】中景全身，**起势**：人物侧身站定，剑**竖向举在身体右侧、挡住半张脸**，只露一只眼；
双膝微屈、重心在右腿；剑尚未出招。白发与衣摆被右后方来风吹动，脚下有雪纹。
【构图/机位】16:9 横版，平视略低；人物占画面高约 75%，站右三分；左侧三分之一是雪地留白与四五根旧木桩。
【光影/材质】侧逆光，冷调；人物压成暗块，白发边缘与剑刃吃冷白边光；剑尖一点暖金。
负向：已经在挥剑、出招、残影、多手多剑、全身远景过小、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_I1 = f"""16:9 横版黑白水墨武侠插画，只生成一张（视频尾部的水墨定格，也是封面候选）。
【引用图片说明】{tok('P1')}＝人物（锁白发/白袍轮廓，转水墨笔意）；{tok('P2')}＝武器（锁冰晶剑外形）；
{tok('K1')}＝同一个人、同一个招式，只借人物特征与画幅，**姿势要换成招式结束**。
【画面】**招式结束姿势**：人物已把剑从脸前落下并翻腕横持，右臂抬到与肩平、完全伸直，剑身横向、
剑尖直指画左、落在画面左侧三分之一；身体已由侧转正、双腿与肩同宽站稳；长发与衣摆向画右后方大幅拖尾（与剑势相反）。
【笔墨】一条浓墨动势线沿剑轴向左出画，沿途飞白与溅墨；雪地用大片留白＋淡墨横扫；
剑尖一点暖金；木桩用极淡墨线勾四五根。
【风格】书法式大写意：浓墨、飞白、破笔、溅点；宣纸纹理；不精细刻画五官；黑、纸白、冷灰＋一点暖金。
【构图】中景，人物占高约 80%；剑横向切过画面中部，斜势 15°。
负向：静态站姿、双手垂放、剑不出鞘、彩色、写实照片、3D渲染、精细插画、红、复杂背景、多人物、文字、水印、logo。
"""

P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：第 0 秒就是"侧身、剑竖在右侧挡半张脸"的起势，机位/朝向/光向完全不变，不要一开始就已经出招。
【引用图片说明】{tok('K1')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器；{tok('I1')}＝结尾水墨定格目标（招式结束姿势）。
【人物与武器】白发剑客，白袍黑腰封，双臂冰霜气劲；藏音·龙跃霄汉（冰晶长剑，护手一道虹彩）。
【镜头语言】16:9 · 4 秒；一镜到底，固定机位，仅 1.02 倍极缓推。全程挺拔站立、双脚不离地、不弯腰不下蹲。
0.0–0.5 秒：保持起势；白发与衣摆被右后方来风轻推，剑不动。
0.5–1.6 秒：**唯一一个招式——横剑前指**：剑从脸前落下至胸前的同一瞬翻腕横持，右臂抬起至与肩平、完全伸直，
剑尖直指画左；同时身体由侧转正、双腿与肩同宽站稳、下颌微收、眼神锁定画左；长发衣摆向画右后方扬起。招式一次走完，不重复挥砍。
1.6–1.7 秒：招式到点的一瞬定格——全屏炸白 1–2 帧。
1.7–4.0 秒：白光褪去，整幅画面已变成 {tok('I1')} 的黑白水墨：保持"横剑前指"的结束姿势，
只有墨点飘落与墨线尾端晕开；镜头固定，不再回到实色。
【水墨规则】结尾是整幅画风转换（按 {tok('I1')}），不是墨元素叠在实色画面上；白闪是转化点。
【声音】衣料轻响与一声剑鸣；到点一记短促金属声；白闪收静；水墨段低频余韵。
【负向】原地不动、第二个招式、连续挥砍、跳起、腾空、旋转、弯腰、下蹲、弓步、镜头摇晃、全程实色、水墨段残留彩色、白闪后切镜头、发光眼、红、大面积金色光效、游戏UI、文字、水印、logo、卡通渲染、多余角色、瞬移、分屏。
"""

# ---------------------------------------------------------------- ② 拔剑上撩
P_K2 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍/冰霜）；{tok('P2')}＝武器（锁冰晶剑外形/护手虹彩）。
【画面】半身，**起势**：人物侧身站定，右手按在剑柄上、剑**尚未出鞘**（剑在腰侧／斜背，鞘身可见）；
肩背微沉、肘部收起，像发力前一瞬的蓄；白发垂在肩前，风从右后来。
【构图/机位】16:9 横版，半身（腰以上），人物占画面高约 85%，站右三分；左侧留出雪的暗部与风的方向。
【光影/材质】侧逆光，冷调；手背与剑柄受一道冷白边光；面部只在暗部里有一点轮廓光。
负向：剑已出鞘、已举起、挥砍残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_I2 = f"""16:9 横版黑白水墨武侠插画，只生成一张（视频尾部的水墨定格）。
【引用图片说明】{tok('P1')}＝人物（锁白发/白袍轮廓，转水墨）；{tok('P2')}＝武器（锁冰晶剑）；{tok('K2')}＝同一人同一招式，只借特征与画幅，**姿势换成出鞘上撩到顶**。
【画面】**招式结束姿势**：剑已出鞘并上撩至最高点——右臂举过肩、剑身斜指右上、刃口朝天；
身体被剑势带得微微仰起，衣袂与白发向上翻卷；一道飞白弧线从腰侧划到剑尖，表示拔剑的轨迹；墨点沿弧线飞溅。
【笔墨】剑身一笔浓墨、刃口留一道白（飞白）；护手一道极细虹彩（全画唯一彩色，面积 <2%）。
【风格】大写意，宣纸纹理；黑占六成、纸白四成。
【构图】半身，剑与手臂占右上三角，脸在左下暗部只露一只眼。
负向：剑未出鞘、双手垂放、静态站姿、彩色、精细插画、写实、金属反光质感、多余人物、文字、水印、logo、卡通、游戏UI。
"""

P_V2 = f"""【首帧锁定】首帧使用 {tok('K2')}：第 0 秒是"手按剑柄、剑未出鞘"的起势，机位/半身景别/朝向完全不变。
【引用图片说明】{tok('K2')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器；{tok('I2')}＝结尾水墨定格目标（出鞘上撩到顶）。
【镜头语言】16:9 · 4 秒；半身，一镜到底，固定机位，不推不摇。双脚不离地。
0.0–0.6 秒：保持起势；肩背再沉一分，手指扣紧剑柄，风把白发吹到脸侧。
0.6–1.5 秒：**唯一一个招式——拔剑上撩**：剑出鞘，沿身体右侧向上撩起，划出一道连续弧线，
右臂举过肩、剑身斜指右上、刃口朝天；身体被剑势带得微微仰起，衣袂与白发向上翻卷。招式一次完成，不重复。
1.5–1.6 秒：招式到顶的一瞬定格——全屏炸白 1–2 帧。
1.6–4.0 秒：白光褪去，整幅已变成 {tok('I2')} 的黑白水墨：保持"上撩到顶"的结束姿势，飞白弧线留在画面里，
只有墨点飘落；镜头固定，不再回到实色。
【水墨规则】结尾整幅转水墨（按 {tok('I2')}），不是墨叠加在实色上。
【声音】金属摩擦一声（出鞘），到顶一记清响；白闪收静；水墨段余响渐弱。
【负向】剑未出鞘、第二个招式、连续挥砍、双手放下、跳起、旋转、镜头运动、切镜、全程实色、水墨段残留实色、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

# ---------------------------------------------------------------- ③ 回身直刺
P_K3 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/冰霜）；{tok('P2')}＝武器（锁冰晶剑身/护手）。
【画面】近景（胸以上＋持剑手），**起势**：人物半转过身，剑收在右侧腰际、剑尖向后；
脸在暗部，只露出一只眼与一道眉；风把白发刮过面颊。
【构图/机位】16:9 横版，近景，人物占画面高约 90%，脸在右三分；左下角是右手的剑柄与半截剑身。
【光影/材质】侧逆光，冷调；剑身有一道冷白反光；脸只有眼窝受光。
负向：已经刺出、剑身横贯画面、残影、多手多剑、全身、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_I3 = f"""16:9 横版黑白水墨武侠插画，只生成一张（视频尾部的水墨定格）。
【引用图片说明】{tok('P1')}＝人物（锁眼型与白发走向）；{tok('P2')}＝武器（锁冰晶剑身）；{tok('K3')}＝同一人同一招式，只借特征与画幅，**姿势换成刺出到最远**。
【画面】**招式结束姿势**：人已拧腰直刺到最远——剑身从画面右下斜贯到左上出画，一笔浓墨扫出，刃口留白作高光；
右臂完全伸直；身体完全拧到位、肩线斜切画面；脸仍在暗部，只露一只眼，眼里一点纸白神光；墨点沿剑路向后飞溅。
【笔墨】极简：剑一笔、人两笔、眼一点；留白占六成；护手一道细虹彩可省。
【构图】近景，剑占满对角线（约 −35°），眼在右三分上方。
负向：剑收回、未刺出、静态站姿、彩色、精细插画、写实、金属质感、多余人物、文字、水印、logo、卡通、游戏UI。
"""

P_V3 = f"""【首帧锁定】首帧使用 {tok('K3')}：第 0 秒是"半转身、剑收腰际"的起势，机位/近景景别/朝向完全不变。
【引用图片说明】{tok('K3')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器；{tok('I3')}＝结尾水墨定格目标（刺出到最远）。
【镜头语言】16:9 · 4 秒；近景，一镜到底，固定机位，不推不摇。双脚不离地。
0.0–0.5 秒：保持起势；呼吸可见，剑尖在腰后微微下沉，风把白发刮过面颊。
0.5–1.5 秒：**唯一一个招式——回身直刺**：拧腰带动右臂，剑从腰际向画面前方（略偏左上）一次贯出，
右臂完全伸直、肩线斜切画面，身体拧到位；剑身从画面右下斜贯到左上。招式一次完成，不收不回。
1.5–1.6 秒：剑到最远的一瞬定格——全屏炸白 1–2 帧。
1.6–4.0 秒：白光褪去，整幅已变成 {tok('I3')} 的黑白水墨：保持"刺出到最远"的结束姿势，墨点沿剑路向后飘；
镜头固定，不再回到实色。
【水墨规则】结尾整幅转水墨（按 {tok('I3')}）。
【声音】一记吸气，出剑破空一声，到点一记闷响；白闪收静；水墨段余响。
【负向】剑收回、原地不动、第二个招式、连续刺击、跳起、旋转、镜头运动、切镜、全程实色、水墨段残留实色、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
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
    nodes = [
        input_image(i["P1"], 20, 20, "【已预填】P1 人物 · 白发剑客", P1_UP),
        input_image(i["P2"], 20, 240, "【已预填】P2 武器 · 龙跃霄汉", P2_UP),
        input_text(i["S1"], 20, 470, 320, 400, "S1 角色与武器设定", S1_TEXT),

        gen_image(i["K1"], 420, 20, "【待生成】K1 ① 起势 · 横剑前指 1K", P_K1, [i["P1"], i["P2"]]),
        gen_image(i["K2"], 420, 330, "【待生成】K2 ② 起势 · 拔剑上撩 1K", P_K2, [i["P1"], i["P2"]]),
        gen_image(i["K3"], 420, 640, "【待生成】K3 ③ 起势 · 回身直刺 1K", P_K3, [i["P1"], i["P2"]]),

        gen_image(i["I1"], 820, 20, "【待生成】I1 ① 定格 · 横指水墨 2K", P_I1,
                  [i["P1"], i["P2"], i["K1"]], size="2K", quality="high"),
        gen_image(i["I2"], 820, 330, "【待生成】I2 ② 定格 · 上撩水墨 2K", P_I2,
                  [i["P1"], i["P2"], i["K2"]], size="2K", quality="high"),
        gen_image(i["I3"], 820, 640, "【待生成】I3 ③ 定格 · 直刺水墨 2K", P_I3,
                  [i["P1"], i["P2"], i["K3"]], size="2K", quality="high"),

        gen_video(i["V1"], 1220, 20, "【待生成】V1 ① 4s · 横剑前指", P_V1,
                  [i["P1"], i["P2"], i["I1"]], i["K1"]),
        gen_video(i["V2"], 1220, 330, "【待生成】V2 ② 4s · 拔剑上撩", P_V2,
                  [i["P1"], i["P2"], i["I2"]], i["K2"]),
        gen_video(i["V3"], 1220, 640, "【待生成】V3 ③ 4s · 回身直刺", P_V3,
                  [i["P1"], i["P2"], i["I3"]], i["K3"]),

        input_text(i["S0"], 20, 1030, 1120, 420, "S0 制作说明", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["K1"]), (i["P2"], i["K1"]),
        (i["P1"], i["K2"]), (i["P2"], i["K2"]),
        (i["P1"], i["K3"]), (i["P2"], i["K3"]),
        (i["P1"], i["I1"]), (i["P2"], i["I1"]), (i["K1"], i["I1"]),
        (i["P1"], i["I2"]), (i["P2"], i["I2"]), (i["K2"], i["I2"]),
        (i["P1"], i["I3"]), (i["P2"], i["I3"]), (i["K3"], i["I3"]),
        (i["P1"], i["V1"]), (i["P2"], i["V1"]), (i["K1"], i["V1"]), (i["I1"], i["V1"]),
        (i["P1"], i["V2"]), (i["P2"], i["V2"]), (i["K2"], i["V2"]), (i["I2"], i["V2"]),
        (i["P1"], i["V3"]), (i["P2"], i["V3"]), (i["K3"], i["V3"]), (i["I3"], i["V3"]),
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
        {"id": "group-ywsy-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 上传与设定（已预填）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywsy-1", "nodeIds": [i["K1"], i["K2"], i["K3"]],
         "bounds": bounds_for([i["K1"], i["K2"], i["K3"]]),
         "label": "01 起势首帧 K1/K2/K3 · 整组跑",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywsy-2", "nodeIds": [i["I1"], i["I2"], i["I3"]],
         "bounds": bounds_for([i["I1"], i["I2"], i["I3"]]),
         "label": "02 定格水墨 I1/I2/I3",
         "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywsy-3", "nodeIds": [i["V1"], i["V2"], i["V3"]],
         "bounds": bounds_for([i["V1"], i["V2"], i["V3"]]),
         "label": "03 视频 4s · V1/V2/V3",
         "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "group-ywsy-4", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "04 制作说明",
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
            "name": "燕云冲击帧 · 三条 招式定格 4s（16:9）v2",
            "description": ("白发剑客 × 藏音·龙跃霄汉：三镜各是一个完整招式——起势(K) → 招式走完(V 1 秒) → "
                            "到点那一帧定格、同帧炸白并整幅转水墨 → 水墨定格(I)。"
                            "K 与 I 是同一招式的头尾，姿势不同。P1/P2 已预填同账号存储，导入即跑。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywsy-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
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
                problems.append(f"同组内依赖边: [{lab}] {s}→{t}")
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
    for n in c["nodes"]:
        if n["type"] == "gen-video":
            ln = len(n["params"]["model_params"]["prompt"])
            print(f"  {n['meta']['label']} prompt {ln} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()
