# -*- coding: utf-8 -*-
"""燕云冲击帧 · 三条 4s 画布构建脚本（Monet schemaVersion 2）

结构（5 组，按跑序）：
  00 上传与设定   P1 人物 / P2 武器 / S1 设定文字（已预填同账号存储 URL，可直接跑）
  01 实写首帧     K1 全身立势 / K2 刃口与眼 / K3 剑身与手
  02 水墨定格     I1/I2/I3（各自参考对应 K，作为视频尾部的水墨目标）
  03 三段视频     V1/V2/V3（seedance-2.0-mini · 4s · 16:9 · 720p）
  04 说明         S0（跑序、剪辑纪律、模型锁定）

接线纪律（I06）：
  - 引用双接入：prompt 里每个 {{node-x}} 必须同时挂在 reference_images/first_frame 且有边；
  - 边只画数据流方向；同组内不得有依赖边；每个节点必须属于某个组且 bounds 不重叠；
  - 接线数据只在本脚本派生一次，不手写第二套。

用法：python build-燕云冲击帧-三帧-v1.py
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
OUT = HERE / "燕云冲击帧-三帧-16x9-v1.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-29T20:10:00.000+08:00"
PREFIX = "ywcj"          # 本作品专用前缀，避免与其它画布节点 ID 相撞
BY = "linguanxi"

# 已上传的参考图（同账号 storage，公开可跨画布复用；md5 已核对）
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


# ---------------------------------------------------------------- 文本提示词
S1_TEXT = f"""【角色与武器设定 · 只读不改】
人物：年轻男性剑客，白发（长过肩、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，双臂缠绕冰霜气劲；
面部清瘦、眉压低、眼神冷静；本组统一不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑，剑身半透、内部有龙形霜纹，护手一道极细虹彩（青→品红），
护手根部结着玉绿色冰晶簇，剑尖处明光偏暖（曜日）。
配色：墨黑＋纸白＋冰青（主）；玉绿与曜金各占 <5%；全组不用红。
禁止：红眼、彩色光效、卡通描边、游戏 UI、水印、logo。

——换角色/武器：替换 P1 / P2 两张图，并同步改 K/I/V 九个节点提示词里的人物与武器描述。
——换画幅：本画布是 16:9 母版；9:16 要重构图（人物与剑尖会出画），不要直接裁。
"""

S0_TEXT = """【燕云冲击帧 · 三条 4s｜先读】
本画布＝三条独立的 4s 冲击帧（seedance 最短 4s；要 3s 就剪头），同角色同武器，构图递进：① 全身立势 → ② 刃口与眼 → ③ 剑身与手。

跑序（组＝跑序，组内并行）：
00 上传（P1/P2 已预填同账号存储，可直接跑；若与你的截图不一致就拖图替换）
→ 01 三张实写首帧整组跑（K1/K2/K3），先把三张构图跑对
→ 02 三张水墨定格整组跑（I1/I2/I3，依赖 01；01 不满意就别跑 02）
→ 03 三段视频整组跑（V1/V2/V3，依赖 01＋02）。

每段成片节拍（4s）：静帧微动 → 唯一一个动作 → 全屏炸白 1–2 帧 → 尾部整幅转水墨定格。
要 3s 版：掐头静帧——V1 剪 1.0s（→3.0s）、V2 剪 0.6s（→3.4s，别剪过 0.8s，会把眨眼吃掉）、V3 剪 0.9s（→3.1s）。

剪辑三步（白闪先量再决定，别猜）：
① 剪头：V1 剪 1.0s、V2 剪 0.6s、V3 剪 0.9s → 成片 3.0–3.4s；
② 量白闪：python 02_画布/量白闪.py <成片.mp4>
   1 帧＝不动；2–3 帧＝接受；≥4 帧或干脆没有炸白，才在原来那段里替换「1 帧白 + 1 帧负片」（不切段、不另拼一段）；
③ 三段落之间用 2 帧黑硬接，别叠化。

模型锁定：生图 gpt-image-2（K 用 1K/medium，I 用 2K/high）；视频 seedance-2.0-mini（最短 4s → 三条都按 4s 写；16:9 · 720p · 带音 · 不挂音频引用）。

纪律：全组不用红；曜金只给剑尖与刃口；虹彩只给护手；一条片子只发生一个事件；静帧占三分之二。
"""

# ---------------------------------------------------------------- 图：实写首帧
P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍黑带/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑外形/龙形霜纹/护手虹彩）。
【画面】全身立势：人物立于雪原，身体略侧对镜头，右手垂剑、剑尖指向左下地面；无招式、无动作，
只有白发与衣摆被右后方来风吹动；脚下有一圈被风刮出的雪纹。
【构图/机位】16:9 横版，平视略低；人物站右三分线，脚在画面下缘 0.86 处；左侧三分之一是空白雪地，
立四五根旧木桩；剑尖落点对齐左下三分线；主斜线从剑尖到左上留白约 30°。
【光影/材质】逆光，天光压在人物背后，人整体压成暗块；只有白发边缘、肩线、剑刃吃一道冷白边光；
剑尖一点暖金。背景深度虚化，雪粒可见。
负向：红、彩色光效、发光眼、多手多剑、弯腰、下蹲、弓步、人物过小、文字、水印、logo、游戏UI、卡通。
"""

P_K2 = f"""16:9 横版电影级极特写，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑刃口/霜纹/护手）。
【画面】极特写：画面上半幅是脸的下半与一只眼（右眼），眼睛在右三分处，睫毛与眼窝结构清晰，
瞳孔里有一点冷白神光；画面下半幅被一道剑刃斜切压住，刃口是一线冷白高光，刃身有极淡冰纹与霜；
颊侧有 3–5 点干涸的墨点与尘。
【构图/机位】16:9 横版，视线略低于眼平；刃线斜率约 −18°，刃口高光穿过黄金分割；
眼睛下沿距刃口约 1/8 画面高。
【光影/材质】侧逆光，脸八成在暗部，只有眼窝受光；刃口一道暖金反光；黑白灰关系为主，饱和度极低。
负向：彩色、发光眼、红眼、血浆、卡通大眼、对称构图、正脸正视镜头、文字、水印、logo、游戏UI、3D渲染感。
"""

P_K3 = f"""16:9 横版电影级微距，只生成一张。
【引用图片说明】{tok('P2')}＝武器（锁冰晶剑身/龙形霜纹/护手虹彩与玉绿晶簇）；{tok('P1')}＝人物（锁白袍袖口与手）。
【画面】微距：一把冰晶长剑从右下角斜贯到左上出画，剑身半透、内部龙形霜纹清晰，刃口带冷白高光；
护手在画面右侧 0.78 宽度处被右边缘裁掉四分之一，护手上一道极细虹彩；
右下角是一只握柄的手（只见手背与两指），白袍袖口被裁掉一半。
【构图/机位】16:9 横版，镜头贴近剑身；剑轴 −52°，占满对角线；背景全黑，只有极淡冷光雾。
【光影/材质】黑底＋剑身自发光：冷（冰泉）为主，剑尖 1/10 处转暖金；霜粒 10–20 点悬浮。
负向：彩色背景、塑料感、卡通描边、多余人物、全剑入画、平视正面、文字、水印、logo、游戏UI。
"""

# ---------------------------------------------------------------- 图：水墨定格
P_I1 = f"""16:9 横版黑白水墨武侠插画，只生成一张（视频尾部的水墨定格，也是封面候选）。
【引用图片说明】{tok('P1')}＝人物（锁白发/白袍轮廓，转水墨笔意）；{tok('P2')}＝武器（锁冰晶剑外形）；
{tok('K1')}＝构图与姿势基准（同一机位、同一站势）。
【画面】与首帧同一构图：人物立于雪原，右手垂剑、剑尖触地；白发与衣摆浓墨泼洒、向画右后方拖尾；
雪原用大片留白＋淡墨横扫表示风迹；剑尖触地处炸开一圈墨霜（破笔＋溅点），一点暖金落在剑尖；
左侧留白三分之一，木桩用极淡墨线勾四五根。
【风格】书法式大写意：浓墨、飞白、破笔、溅点；宣纸纹理；不精细刻画五官；
全画只有黑、纸白、冷灰，加一点暖金。
【构图】人物占画面高约 80%，右三分；主斜线 30°。
负向：彩色、写实照片、3D渲染、精细插画、红、复杂背景、多人物、文字、水印、logo、卡通、游戏UI。
"""

P_I2 = f"""16:9 横版黑白水墨，只生成一张（视频尾部的水墨定格）。
【引用图片说明】{tok('P1')}＝人物（锁眼型与白发走向）；{tok('K2')}＝构图基准（同一机位、同一刃线角度）。
【画面】同一构图的水墨版：上半幅一只眼，用两笔浓墨压出杏形，眼白留纸白，瞳孔一点浓墨，神光一点纸白；
下半幅一道刃口，用一笔枯墨横扫，刃口留一道白线（飞白），刃身几道淡墨冰纹；颊侧溅 3–5 点墨。
【风格】极简水墨，留白占七成；只有黑、纸白、灰；不画毛发细节，一两笔带过。
负向：彩色、写实、精细插画、红、对称、多眼、文字、水印、logo、卡通、游戏UI。
"""

P_I3 = f"""16:9 横版黑白水墨，只生成一张（视频尾部的水墨定格）。
【引用图片说明】{tok('P2')}＝武器（锁冰晶剑身/龙形走势/护手）；{tok('K3')}＝构图与剑轴基准。
【画面】同一构图的墨版：剑从右下斜贯左上出画，剑身用大笔枯墨扫出，内部龙形走势用细墨线勾；
刃口一笔留白作高光；护手处一道极细虹彩（青→品红，全画唯一彩色，面积 <2%）；
右下角手握柄用一块浓墨带过，白袍袖口留白；霜粒用溅点表示。
【风格】大写意，宣纸纹理，黑占六成、纸白四成。
负向：彩色背景、精细插画、写实、金属反光质感、多余人物、全剑入画、文字、水印、logo、卡通、游戏UI。
"""

# ---------------------------------------------------------------- 视频
P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：第 0 秒就是"雪原立势、右手垂剑、剑尖指地"的全身构图，机位/朝向/光向完全不变，不要换成别的机位。
【引用图片说明】{tok('K1')}＝首帧；{tok('P1')}＝人物（锁白发/白袍/冰霜）；{tok('P2')}＝武器（锁冰晶剑）；{tok('I1')}＝结尾水墨定格目标（同一构图）。
【人物与武器】白发剑客，白袍黑腰封，双臂冰霜气劲；藏音·龙跃霄汉（冰晶长剑，护手一道虹彩）。
【镜头语言】16:9 · 4 秒；一镜到底，固定机位，仅 1.02 倍极缓推。全程挺拔站立，不弯腰不下蹲，双脚不离地。
0.0–1.4 秒：保持首帧：白发与衣摆被右后方来风轻推，雪粒横飞；剑不动，人不动。
1.4–1.6 秒：剑尖触地的一瞬，霜从触点向外爬开，炸起一圈雪雾。
1.6–1.7 秒：全屏炸白 1–2 帧。
1.7–2.2 秒：白光褪去，整幅画面开始变成 {tok('I1')} 的黑白水墨：人物与剑保持同一姿势。
2.2–4.0 秒：进入 {tok('I1')} 的水墨定格：只有墨点飘落、墨线尾端晕开、纸纹极轻呼吸；镜头固定，不再回到实色。
【水墨规则】结尾是整幅画风转换（按 {tok('I1')}），不是墨元素叠在实色画面上；白闪是转化点。
【声音】风声起，剑尖触地一声闷响，白闪一瞬收静，水墨段低频余韵渐弱；无 BGM、无台词。
【负向】弯腰、驼背、下蹲、弓步、第二个动作、跳跃、旋转、镜头摇晃、全程实色、水墨段残留彩色、白闪后切镜头、发光眼、红、大面积金色光效、游戏第三人称机位、游戏UI、文字、水印、logo、卡通渲染、多余角色、血、瞬移、分屏。
"""

P_V2 = f"""【首帧锁定】首帧使用 {tok('K2')}：第 0 秒就是"半张脸＋一只眼、刃口斜压下半幅"的极特写，机位与刃线角度完全不变。
【引用图片说明】{tok('K2')}＝首帧；{tok('P1')}＝人物（锁眼型/白发）；{tok('P2')}＝武器（锁刃口/冰纹）；{tok('I2')}＝结尾水墨定格目标。
【镜头语言】16:9 · 4 秒；极特写，固定机位，不推不摇。
0.0–0.8 秒：保持首帧，眼不动，刃口高光极微呼吸。
0.8–1.1 秒：眨一次眼（约 3 帧），睫毛压下再抬，瞳孔里的神光不灭。
1.1–1.5 秒：一道暖金反光沿刃口从右向左扫过（刃身不动，只有反光在走）。
1.5–1.7 秒：反光收束到刃尖的一瞬，全屏炸白 1–2 帧。
1.7–2.2 秒：白光褪去，整幅画面开始变成 {tok('I2')} 的黑白水墨极特写：眼与刃口位置不变。
2.2–4.0 秒：进入 {tok('I2')} 的水墨定格：只有墨点与飞白微微浮动；不再回到实色。
【水墨规则】结尾整幅转水墨（按 {tok('I2')}），不是墨叠加在实色上。
【声音】一缕极轻的铁鸣起，眨眼一记轻响，白闪收静，水墨段留一点余响；无 BGM、无台词。
【负向】彩色、发光眼、红眼、血浆、大眼卡通、镜头运动、切镜、第二个动作、水墨段残留实色、游戏UI、文字、水印、logo、3D渲染感、多余角色、分屏。
"""

P_V3 = f"""【首帧锁定】首帧使用 {tok('K3')}：第 0 秒就是"冰晶剑从右下斜贯左上出画、手在右下角"的微距构图，剑轴角度完全不变。
【引用图片说明】{tok('K3')}＝首帧；{tok('P2')}＝武器（锁剑身/龙形霜纹/护手虹彩）；{tok('P1')}＝人物（锁袖口与手）；{tok('I3')}＝结尾水墨定格目标。
【镜头语言】16:9 · 4 秒；微距，固定机位，不推不摇。
0.0–1.0 秒：保持首帧：剑身内部霜纹极缓流动，护手虹彩微微游移，霜粒悬浮。
1.0–1.2 秒：手腕轻转一记，剑身冰晶亮一下。
1.2–1.7 秒：碎冰沿剑身向两端炸开，霜粒飞出画面。
1.7–1.8 秒：全屏炸白 1–2 帧。
1.8–2.3 秒：白光褪去，整幅画面开始变成 {tok('I3')} 的黑白水墨微距：剑与手位置不变，护手那道虹彩保留。
2.3–4.0 秒：进入 {tok('I3')} 的水墨定格：飞白与墨点浮动；不再回到实色。
【水墨规则】结尾整幅转水墨（按 {tok('I3')}）。
【声音】极轻的冰裂起，手腕一转一声脆响，碎冰炸开细密声，白闪收静；无 BGM、无台词。
【负向】彩色背景、金属塑料质感、镜头运动、走位、第二个动作、切镜、水墨段残留实色、游戏UI、文字、水印、logo、多重剑影、多余人物、分屏。
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

        gen_image(i["K1"], 420, 20, "【待生成】K1 ① 雪落无声 · 立势 1K", P_K1, [i["P1"], i["P2"]]),
        gen_image(i["K2"], 420, 330, "【待生成】K2 ② 一线 · 刃与眼 1K", P_K2, [i["P1"], i["P2"]]),
        gen_image(i["K3"], 420, 640, "【待生成】K3 ③ 龙跃 · 剑与手 1K", P_K3, [i["P2"], i["P1"]]),

        gen_image(i["I1"], 820, 20, "【待生成】I1 ① 水墨定格 2K", P_I1,
                  [i["P1"], i["P2"], i["K1"]], size="2K", quality="high"),
        gen_image(i["I2"], 820, 330, "【待生成】I2 ② 水墨定格 2K", P_I2,
                  [i["P1"], i["K2"]], size="2K", quality="high"),
        gen_image(i["I3"], 820, 640, "【待生成】I3 ③ 水墨定格 2K", P_I3,
                  [i["P2"], i["K3"]], size="2K", quality="high"),

        gen_video(i["V1"], 1220, 20, "【待生成】V1 ① 4s · 炸霜→水墨", P_V1,
                  [i["P1"], i["P2"], i["I1"]], i["K1"]),
        gen_video(i["V2"], 1220, 330, "【待生成】V2 ② 4s · 刃光→水墨", P_V2,
                  [i["P1"], i["P2"], i["I2"]], i["K2"]),
        gen_video(i["V3"], 1220, 640, "【待生成】V3 ③ 4s · 碎冰→水墨", P_V3,
                  [i["P1"], i["P2"], i["I3"]], i["K3"]),

        input_text(i["S0"], 20, 1030, 1120, 420, "S0 制作说明", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["K1"]), (i["P2"], i["K1"]),
        (i["P1"], i["K2"]), (i["P2"], i["K2"]),
        (i["P2"], i["K3"]), (i["P1"], i["K3"]),
        (i["P1"], i["I1"]), (i["P2"], i["I1"]), (i["K1"], i["I1"]),
        (i["P1"], i["I2"]), (i["K2"], i["I2"]),
        (i["P2"], i["I3"]), (i["K3"], i["I3"]),
        (i["P1"], i["V1"]), (i["P2"], i["V1"]), (i["K1"], i["V1"]), (i["I1"], i["V1"]),
        (i["P1"], i["V2"]), (i["P2"], i["V2"]), (i["K2"], i["V2"]), (i["I2"], i["V2"]),
        (i["P1"], i["V3"]), (i["P2"], i["V3"]), (i["K3"], i["V3"]), (i["I3"], i["V3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bounds_for(ids):
        xs = [by_id[i]["meta"]["x"] for i in ids]
        ys = [by_id[i]["meta"]["y"] for i in ids]
        xe = [by_id[i]["meta"]["x"] + by_id[i]["meta"]["width"] for i in ids]
        ye = [by_id[i]["meta"]["y"] + by_id[i]["meta"]["height"] for i in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        {"id": "group-ywcj-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 上传与设定（已预填）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywcj-1", "nodeIds": [i["K1"], i["K2"], i["K3"]],
         "bounds": bounds_for([i["K1"], i["K2"], i["K3"]]),
         "label": "01 首帧 K1/K2/K3 · 整组跑",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywcj-2", "nodeIds": [i["I1"], i["I2"], i["I3"]],
         "bounds": bounds_for([i["I1"], i["I2"], i["I3"]]),
         "label": "02 水墨定格 I1/I2/I3",
         "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywcj-3", "nodeIds": [i["V1"], i["V2"], i["V3"]],
         "bounds": bounds_for([i["V1"], i["V2"], i["V3"]]),
         "label": "03 视频 4s · V1/V2/V3",
         "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "group-ywcj-4", "nodeIds": [i["S0"]],
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
            "name": "燕云冲击帧 · 三条 4s（16:9）v1",
            "description": ("白发剑客 × 藏音·龙跃霄汉：三条 4s（seedance 最短档）冲击帧，构图递进 全身→眼→剑。"
                            "K 实写首帧 → I 水墨定格 → V 视频（静帧微动→唯一动作→炸白→尾部水墨直出）。"
                            "P1/P2 已预填同账号存储，导入即跑。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywcj-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
                "targetNodeId": t, "targetHandle": "input",
                "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
            } for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }
    return doc


def self_check(doc):
    """与 检查画布接线.py 同口径的关键自检，先在本脚本里炸掉，别等交付前才发现。"""
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
        import re
        toks = set(re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", prompt))
        for tk in toks:
            if tk not in by_id:
                problems.append(f"引用节点不存在: {label} → {tk}")
            if tk not in refs and tk != ff:
                problems.append(f"引用未挂字段(无效引用块): {label} → {tk}")
        if "{{node-node-" in prompt:
            problems.append(f"双前缀: {label}")
        for r in refs + ([ff] if ff else []):
            if (r, n["id"]) not in edge_set:
                problems.append(f"字段挂了没连线: {label} ← {r}")
            rn = by_id.get(r)
            if rn and rn["type"] == "input-image" and not rn.get("outputs"):
                problems.append(f"被引用的上传节点是空的: {label} ← {r}")
        if n["type"] == "gen-video":
            if ff and ff not in toks:
                problems.append(f"首帧未在正文点名: {label}")
            if len(prompt) > 2000:
                problems.append(f"prompt 超 2000 字: {label} ({len(prompt)})")
            if mp.get("duration") != 4:
                problems.append(f"时长不是 4s: {label}")
    # bounds 重叠
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
            print(f"  {n['meta']['label'][:16]} prompt {ln} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()



