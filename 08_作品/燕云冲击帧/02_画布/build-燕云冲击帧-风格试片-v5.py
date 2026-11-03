# -*- coding: utf-8 -*-
"""燕云冲击帧 · 风格试片 v5：同一帧，五种冲击帧风格并行出图

目的（2026-10-30）：外部参考只是参考之一，道之极本身是「水墨＋红黑」。
所以先不定风格，用同一张定格帧 T1 跑五种风格，看图再选。
只做 ① 横剑前指 一镜——风格定了再铺另外两镜，省生成费。

结构（6 组，按跑序）：
  00 上传与设定   P1 人物 / P2 武器 / S1
  01 起势首帧     K1
  02 招式视频     V1（4s，写实，止于实色定格）
  03 定格帧       T1（占位，跑完 V1 取末帧替换）
  04 五种冲击帧   I-A 水墨红黑 / I-B 焦墨拓印 / I-C 素墨 / I-D 红黑2D / I-E 冰青金（并行）
  05 说明         S0
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
OUT = HERE / "燕云冲击帧-风格试片-v5.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-10-30T10:50:00.000+08:00"
PREFIX = "ywst"
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


def load_placeholder():
    pats = [r"E:\漫剧项目\ai-drama\_共享\工作流研究\**\*尾帧占位*.monet"]
    path = None
    for pat in pats:
        hits = glob.glob(pat, recursive=True)
        if hits:
            path = hits[0]
            break
    if not path:
        raise SystemExit("找不到尾帧占位来源画布")
    c = json.load(open(path, encoding="utf-8"))["canvas"]
    for n in c["nodes"]:
        lab = (n.get("meta") or {}).get("label") or ""
        if n.get("type") == "input-image" and "占位" in lab and (n.get("outputs") or []):
            o = n["outputs"][0]
            return ({
                "name": o.get("name") or "尾帧占位.jpg",
                "url": o["value"],
                "width": (o.get("resolution") or {}).get("width", 1280),
                "height": (o.get("resolution") or {}).get("height", 720),
                "size": (o.get("metadata") or {}).get("size"),
                "md5": (o.get("metadata") or {}).get("md5"),
            }, Path(path).name)
    raise SystemExit("占位节点没找到")


def nid(key):
    return "node-" + hashlib.md5((PREFIX + key).encode("utf-8")).hexdigest()[:8]


KEYS = ("P1", "P2", "S1", "K1", "V1", "T1", "IA", "IB", "IC", "ID", "IE", "S0")
ID = {k: nid(k) for k in KEYS}


def tok(key):
    return "{{" + ID[key] + "}}"


S1_TEXT = """【角色与武器设定 · 只读】
人物：年轻男性剑客，白发（长过肩、发尾散乱），白色宽袖长袍＋黑色内衬，黑色腰封与革带，双臂缠绕冰霜气劲；
面部清瘦、眉压低、眼神冷静；本组不戴斗笠。
武器：藏音·龙跃霄汉——冰晶长剑，剑身半透、内部有龙形霜纹，护手一道极细虹彩（青→品红），
护手根部结着玉绿色冰晶簇，剑尖明光偏暖（曜日）。

【本画布只做一件事】同一张定格帧 T1，跑五种冲击帧风格，选一个再铺另外两镜。
五种风格只改 I，K/V 不动（写实、无红）。
"""

S0_TEXT = """【风格试片 · 同一帧五种冲击帧】

怎么跑（组＝跑序）：
00 上传（P1/P2 已预填）
→ 01 起势 K1
→ 02 招式 V1（4s，写实，结尾停在实色定格）
→ 03 截帧：从 V1 取最后一帧，替换 T1 的占位图（节点 ID 不变，只换 output 里的图）
→ 04 五种冲击帧整组跑（并行，互不影响）：同一条 prompt 骨架，只换风格锁。
    I-A 水墨红黑（道之极式）　I-B 焦墨拓印　I-C 素墨（无彩）
    I-D 红黑 2D（外部参考那套）　I-E 冰青金（最贴角色，无红）

怎么看：
1. 先看**姿势有没有被改**——五种都必须和 T1 完全同姿势；改了的那张直接淘汰（说明"改画"变成了"重画"）。
2. 再看**像不像燕云**——D 最燃但最不像；E 最像但最不"冲击"；A/C 在中间。
3. 最后看**放大到 2K 的边缘**：赛璐璐（D）要硬边，水墨（A/C/E）要笔触可见，糊了就重跑。

选完之后：把选中的风格锁套到 ②③ 两镜，其余四种留着当备选（不要删节点，标【备用】）。

剪辑（选定风格后）：V 定格 → 1 帧白 → 冲击帧保持 1.8–2.3s → 渐暗 3 帧。
白闪帧数用 02_画布/量白闪.py 量，别猜。
"""

# ---------------------------------------------------------------- K / V
P_K1 = f"""16:9 横版电影级首帧，只生成一张。
【引用图片说明】{tok('P1')}＝人物（锁脸/白发/白袍黑带/冰霜气劲）；{tok('P2')}＝武器（锁冰晶剑外形/龙形霜纹/护手虹彩）。
【画面】中景全身，**起势**：人物侧身站定，剑**竖向举在身体右侧、挡住半张脸**，只露一只眼；
双膝微屈、重心在右腿；剑尚未出招。白发与衣摆被右后方来风吹动，脚下有雪纹。
【构图/机位】16:9 横版，平视略低；人物占画面高约 75%，站右三分；左侧三分之一是雪地留白与四五根旧木桩。
【光影/材质】侧逆光，冷调；人物压成暗块，白发边缘与剑刃吃冷白边光；剑尖一点暖金。
负向：已经在挥剑、出招、残影、多手多剑、人物过小、红、彩色光效、文字、水印、logo、游戏UI、卡通。
"""

P_V1 = f"""【首帧锁定】首帧使用 {tok('K1')}：第 0 秒就是"侧身、剑竖在右侧挡半张脸"的起势，机位/朝向/光向完全不变，不要一开始就已经出招。
【引用图片说明】{tok('K1')}＝首帧（起势）；{tok('P1')}＝人物；{tok('P2')}＝武器。
【人物与武器】白发剑客，白袍黑腰封，双臂冰霜气劲；藏音·龙跃霄汉（冰晶长剑，护手一道虹彩）。
【镜头语言】16:9 · 4 秒；一镜到底，固定机位，仅 1.02 倍极缓推。全程挺拔站立、双脚不离地、不弯腰不下蹲。
0.0–0.5 秒：保持起势；白发与衣摆被右后方来风轻推，剑不动。
0.5–1.5 秒：**唯一一个招式——横剑前指**：剑从脸前落下至胸前的同一瞬翻腕横持，右臂抬起至与肩平、完全伸直，
剑尖直指画左；同时身体由侧转正、双腿与肩同宽站稳、下颌微收、眼神锁定画左；长发衣摆向画右后方扬起。招式一次走完，不重复挥砍。
1.5–4.0 秒：**保持这个结束姿势不动**（实色，不要变色）：只有衣摆与发丝被风轻推、雪粒从画面掠过；镜头固定。
【风格】全片保持实色电影感，**不要变水墨、不要黑白、不要灰化**——风格在 04 里换。
【声音】衣料轻响与一声剑鸣，到点一记短促金属声，随后环境风声。
【负向】第二个招式、连续挥砍、跳起、腾空、旋转、弯腰、下蹲、弓步、镜头摇晃、定格时人物继续动、
转水墨、水墨化、黑白化、画面变灰、发光眼、红、大面积金色光效、游戏UI、文字、水印、logo、卡通渲染、多余角色、分屏。
"""

# ---------------------------------------------------------------- 五种冲击帧
P_IA = f"""16:9 横版黑白水墨·**红黑水墨**冲击帧插画，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（人物位置、剑的角度、景别都不许改）；{tok('P1')}＝人物特征（白发、白袍黑带）；{tok('P2')}＝武器外形。
【任务】把 {tok('T1')} 这一帧**改画成水墨红黑冲击帧**：宣纸上的大写意，不是写实转绘。
【构图·爆点】爆点＝剑尖（画左）：从剑尖炸开一团**猩红墨爆**（泼溅、飞白、撕裂笔触），
一道浓墨巨浪从剑尖向左上冲出画外、充当速度线；人物是中轴偏右的焦墨块，白发拉成飞白笔触、向画右后方甩出。
【色彩】宣纸白底＋焦墨＋猩红，红只出现在剑尖爆点与飞白尾迹（约 15%）；无其他彩色。
【质感】浓墨泼洒、破笔、飞白、溅点；纸纹与纤维可见；无一笔平滑渐变。
【限制】严格平面（纸上绘画感），细节极简、干净不杂乱。
负向：赛璐璐、放射几何线、写实、照片、3D渲染、体积光、景深、胶片颗粒、青绿金紫、柔和渐变、碎纹理、多人物、文字、水印、logo、游戏UI。
"""

P_IB = f"""16:9 横版**焦墨拓印**冲击帧，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（不许改姿势与机位）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形。
【任务】把 {tok('T1')} 这一帧**改画成焦墨拓印版**：像木刻/碑拓，刀刻的硬边，不是毛笔晕染。
【构图·爆点】爆点＝剑尖（画左）：以剑尖为中心，黑底被刻出一束**白色刻线**向外放射；
剑本身是一道**纯白刻痕**横贯画面；人物为大块纯黑，只在受光处留白刻线；红只做一枚印记大小（约 3%，点在剑尖）。
【色彩】黑占 85%，白为刻线，红为唯一彩色（极小）；无灰阶过渡，只有黑/白/红。
【质感】硬边、干、纸面拓印质感；边缘有刀口毛边；零渐变、零晕染。
【限制】严格平面；细节极简。
负向：灰阶、柔和渐变、水墨晕染、泼墨、写实、照片、3D、体积光、景深、颗粒、青绿金、多人物、文字、水印、logo、游戏UI。
"""

P_IC = f"""16:9 横版**素墨**（纯水墨、无彩色）冲击帧插画，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（不许改姿势与机位）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形。
【任务】把 {tok('T1')} 这一帧**改画成素墨**：只用焦、浓、淡、清四层墨，一点彩色都不要。
【构图·爆点】爆点＝剑尖（画左）：以剑尖为中心，淡墨向外一圈圈扩散（晕染）作为冲击波；
剑是一道焦墨横线、刃口留白；人物焦墨剪影，白发用飞白；留白占六成，画面安静但压得住。
【色彩】只有墨与纸白；**全集无红、无任何彩色**（若必须一点神采，只在瞳孔留一点纸白，不加色）。
【质感】文人水墨：淡墨晕染＋焦墨提神；纸纹可见；笔触柔和但有骨。
【限制】严格平面；细节极简。
负向：彩色、红色、赛璐璐、放射几何线、写实、照片、3D、体积光、景深、颗粒、多人物、文字、水印、logo、游戏UI。
"""

P_ID = f"""16:9 横版，硬核二次元／黑白漫画上色的单帧**冲击帧**插画，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（不许改姿势与机位）；{tok('P1')}＝人物特征；{tok('P2')}＝武器外形。
【任务】把 {tok('T1')} 这一帧**改画成红黑白 2D 冲击帧**：二维动画质感，不是水墨、不是写实。
【构图·爆点】以剑尖（画左）为爆点：**粗犷密集的速度线**从画面四角向剑尖强行汇聚；剑是纯白刃劈开画面；
中心一点对称能量漩涡（纯白芯、猩红外缘）；人物硬边黑块＋纯白高光。
【色彩】纯黑底占 60% 以上；猩红＋纯白双高光；可点极少量明黄；禁止中间调与彩色渐变；红约 15–20%。
【质感】赛璐璐硬边色块，边缘锐利；干笔飞白；无柔和渐变、无体积光、无颗粒、无景深。
【限制】严格 2D 平面；细节极简、干净不杂乱。
负向：水墨、纸纹、写实、照片、3D渲染、柔和渐变、体积光、景深、胶片颗粒、青绿紫、复杂细节、多人物、文字、水印、logo、游戏UI。
"""

P_IE = f"""16:9 横版**水墨·冰青金**冲击帧插画，只生成一张。
【引用图片说明】{tok('T1')}＝姿势与构图的唯一依据（不许改姿势与机位）；{tok('P1')}＝人物特征（白发/白袍/冰霜气劲）；{tok('P2')}＝武器外形（冰晶剑、护手虹彩）。
【任务】把 {tok('T1')} 这一帧**改画成水墨冰青版**：水墨为底，冰霜为魂，与本角色设定一致。
【构图·爆点】爆点＝剑尖（画左）：从剑尖炸开一簇**冰棱与霜晶**（半透棱面、锐角），以冰棱当速度线向外放射；
一道浓墨横扫过画面作为剑势；人物焦墨剪影，白发留白、衣摆飞白；红**一点都不要**。
【色彩】墨黑＋纸白＋冰青（#9FE0EA 附近）＋少量曜金（#E8C48A，只在剑尖与瞳孔）；冷调、清冽。
【质感】水墨笔触＋冰晶半透棱面（不要写实玻璃）；纸纹可见；无柔和体积光。
【限制】严格平面；细节极简。
负向：红色、血浆、赛璐璐、放射几何线、写实、照片、3D渲染、体积光、景深、颗粒、金紫大色块、多人物、文字、水印、logo、游戏UI。
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


def gen_image(n, x, y, label, prompt, refs, size="2K", quality="high"):
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
    up, src_name = load_placeholder()
    nodes = [
        input_image(i["P1"], 20, 20, "【已预填】P1 人物 · 白发剑客", P1_UP),
        input_image(i["P2"], 20, 240, "【已预填】P2 武器 · 龙跃霄汉", P2_UP),
        input_text(i["S1"], 20, 470, 320, 420, "S1 角色与武器设定", S1_TEXT),

        gen_image(i["K1"], 420, 20, "【待生成】K1 起势 · 横剑前指 1K", P_K1,
                  [i["P1"], i["P2"]], size="1K", quality="medium"),
        gen_video(i["V1"], 420, 380, "【待生成】V1 4s · 横剑前指（止于实色定格）", P_V1,
                  [i["P1"], i["P2"]], i["K1"]),

        input_image(i["T1"], 820, 20, "【占位】T1 定格帧 · 跑完 V1 取末帧替换", up),

        gen_image(i["IA"], 1220, 20, "【待生成】I-A 水墨红黑（道之极式）", P_IA,
                  [i["T1"], i["P1"], i["P2"]]),
        gen_image(i["IB"], 1220, 340, "【待生成】I-B 焦墨拓印", P_IB,
                  [i["T1"], i["P1"], i["P2"]]),
        gen_image(i["IC"], 1220, 660, "【待生成】I-C 素墨（无彩）", P_IC,
                  [i["T1"], i["P1"], i["P2"]]),
        gen_image(i["ID"], 1580, 20, "【待生成】I-D 红黑 2D（外部参考）", P_ID,
                  [i["T1"], i["P1"], i["P2"]]),
        gen_image(i["IE"], 1580, 340, "【待生成】I-E 冰青金（最贴角色）", P_IE,
                  [i["T1"], i["P1"], i["P2"]]),

        input_text(i["S0"], 820, 1040, 740, 520, "S0 怎么跑 · 怎么看", S0_TEXT),
    ]

    pairs = [
        (i["P1"], i["K1"]), (i["P2"], i["K1"]),
        (i["P1"], i["V1"]), (i["P2"], i["V1"]), (i["K1"], i["V1"]),
    ]
    for k in ("IA", "IB", "IC", "ID", "IE"):
        pairs += [(i["T1"], i[k]), (i["P1"], i[k]), (i["P2"], i[k])]

    by_id = {n["id"]: n for n in nodes}

    def bounds_for(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    styles = [i[k] for k in ("IA", "IB", "IC", "ID", "IE")]
    groups = [
        {"id": "group-ywst-0", "nodeIds": [i["P1"], i["P2"], i["S1"]],
         "bounds": bounds_for([i["P1"], i["P2"], i["S1"]]),
         "label": "00 上传与设定（已预填）",
         "style": {"accent": None, "opacity": None, "borderColor": "#8E8DE0"}},
        {"id": "group-ywst-1", "nodeIds": [i["K1"]],
         "bounds": bounds_for([i["K1"]]),
         "label": "01 起势 K1",
         "style": {"accent": None, "opacity": None, "borderColor": "#5B8DE0"}},
        {"id": "group-ywst-2", "nodeIds": [i["V1"]],
         "bounds": bounds_for([i["V1"]]),
         "label": "02 招式视频 4s · 止于实色定格",
         "style": {"accent": None, "opacity": None, "borderColor": "#E0A15B"}},
        {"id": "group-ywst-3", "nodeIds": [i["T1"]],
         "bounds": bounds_for([i["T1"]]),
         "label": "03 定格帧 T1 · 截末帧替换后再跑 04",
         "style": {"accent": None, "opacity": None, "borderColor": "#C8C2B4"}},
        {"id": "group-ywst-4", "nodeIds": styles,
         "bounds": bounds_for(styles),
         "label": "04 五种冲击帧 · 并行跑，同姿势只换风格",
         "style": {"accent": None, "opacity": None, "borderColor": "#5BE0C8"}},
        {"id": "group-ywst-5", "nodeIds": [i["S0"]],
         "bounds": bounds_for([i["S0"]]),
         "label": "05 说明",
         "style": {"accent": None, "opacity": None, "borderColor": "#888888"}},
    ]
    for g in groups:
        g["createdAt"] = CREATED
        g["createdBy"] = BY
        g["updatedAt"] = CREATED
        g["updatedBy"] = BY

    return {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 风格试片 五选一（16:9）v5",
            "description": ("同一张定格帧 T1 跑五种冲击帧：A 水墨红黑 / B 焦墨拓印 / C 素墨无彩 / "
                            "D 红黑 2D / E 冰青金。只做①横剑前指一镜，选完风格再铺另外两镜。"
                            f"占位图取自 {src_name}。"),
            "nodes": nodes,
            "edges": [{
                "id": f"edge-ywst-{k:03d}", "sourceNodeId": s, "sourceHandle": "output",
                "targetNodeId": t, "targetHandle": "input",
                "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
            } for k, (s, t) in enumerate(pairs)],
            "groups": groups,
        },
    }


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
        if n["type"] == "gen-image" and n["meta"]["label"].startswith("【待生成】I"):
            print(f"  {n['meta']['label']}  {len(n['params']['model_params']['prompt'])} 字")
    if problems:
        print("自检问题:")
        for p in problems:
            print("  [X]", p)
    else:
        print("自检通过 OK")


if __name__ == "__main__":
    main()


