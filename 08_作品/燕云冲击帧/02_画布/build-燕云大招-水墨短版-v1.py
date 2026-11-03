# -*- coding: utf-8 -*-
"""燕云大招 v5：8s 直出 · 四候选（万剑归宗 / 泼墨吞世 / 千丈寒剑 / 冰龙贯野）

用户 2026-11-03 调整轨迹：
  ① 外部 9 条参考全是文生视频直出（无首尾帧链）→ 撤 K 帧链；
  ② 只挂角色和武器 → reference 模式挂 A1 脸 + A2 全身 + A5 武器；
  ③ 画风：国漫写实为底；候选覆盖“万剑归宗 / 恢弘水墨 / 仙侠参照”三种方向；
  ④ 身高 185cm 暂定写进 prompt。

结构：
  00 素材（P1/P2 来源记录 · S1B 设定）
  01 资产（A1 角色 / A5 武器，已生成·复用，挂给 V1–V4）
  02 大招直出（V1 万剑归宗 / V2 泼墨吞世 / V3 千丈寒剑·天开 / V4 冰龙贯野，互不依赖）
  03 说明 S0C
长度依据：外部 30s 参考是循环/拼贴（29.38s=5.3s×5.5；30.05s=5.34s×6），
唯一单条叙事 3.94s；8s 单条成立，30s 用剪辑循环。
"""
import hashlib
import json
import shutil
from pathlib import Path

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云大招-水墨短版-8s-大招v1.monet"
DL = Path.home() / "Downloads" / OUT.name
CREATED = "2026-11-03T17:05:00.000+08:00"
PREFIX = "ywdz"
BY = "linguanxi"

KEYS = ("P1", "P2", "S1B", "A1", "A2", "A5", "V1", "V2", "V3", "V4", "S0C")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}

# ---------------- 已生成资产（复用，不出新图） ----------------
MAN = json.loads((HERE / "已生成资产清单-v3.json").read_text(encoding="utf-8"))
REUSE = {"A1": "A1", "A2": "A2", "A5": "A5"}
FOUND = {}
for _label, _v in MAN.items():
    _core = _label.split("】")[-1].strip()
    for _key, _pref in REUSE.items():
        if _key not in FOUND and _core.startswith(_pref):
            FOUND[_key] = _v
            break
assert set(FOUND) == set(REUSE), f"资产清单缺项: {set(REUSE) - set(FOUND)}"


def tok(k):
    return "{{" + ID[k] + "}}"


def oid(k):
    return "output-" + ID[k].split("-")[1]


def input_image(k, x, y, label, url, width, height, size, md5):
    return {
        "id": ID[k], "type": "input-image", "mainOutputId": oid(k),
        "meta": {"x": x, "y": y, "width": 320, "height": 200, "label": label, "resourceType": None},
        "outputs": [{
            "id": oid(k), "status": "done", "error": None, "value": url,
            "cover": None, "name": f"{k}.png",
            "resolution": {"width": width, "height": height},
            "metadata": {"size": size, "md5": md5},
        }],
        "params": None, "specialParams": None, "config": None,
    }


def reuse_image(k, x, y, note):
    v = FOUND[k]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return input_image(k, x, y, f"【已生成·复用】{note}", v["url"],
                       res.get("width", 1280), res.get("height", 720),
                       md.get("size"), md.get("md5"))


def input_text(k, x, y, w, h, label, text):
    return {
        "id": ID[k], "type": "input-text", "mainOutputId": oid(k),
        "meta": {"x": x, "y": y, "width": w, "height": h, "label": label, "resourceType": None},
        "outputs": [{
            "id": oid(k), "status": "done", "error": None, "value": text,
            "cover": None, "name": label, "resolution": None, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
    }


def gen_video(k, x, y, label, prompt, refs, duration=8):
    """直出：reference 模式只挂角色/武器锚，无首尾帧，不锁构图。"""
    return {
        "id": ID[k], "type": "gen-video", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": ID[r]} for r in refs],
            "reference_videos": [], "reference_audios": [],
            "first_frame_image": None, "last_frame_image": None,
            "aspect_ratio": "16:9", "resolution": "720p",
            "duration": duration, "generate_audio": True, "seed": -1,
        }},
        "specialParams": None, "config": None,
    }


# ---------------- 公共段 ----------------
REF_LINE = (f"【引用图片说明】{tok('A1')}＝角色脸（保持同一人）；{tok('A2')}＝全身与服装比例"
            f"（白发束起、白袍黑腰封、双臂薄冰、身形颀长）；{tok('A5')}＝武器（藏音·龙跃霄汉："
            f"冰泉色剑身、擎冰刃口、炼虹剑颚、曜日一点明光；剑身不整体发光，只留一道冷白高光；全片只有这一把剑）。")
CHARA_LINE = ("【角色】主角是身高约一米八五的青年剑客，身形颀长挺拔、肩宽腰窄，白发束起，"
              "白袍黑腰封，双臂覆薄冰，气质冷峻；右手单手握剑，虎口贴剑格，左手掐剑诀。"
              "大远景中人物与奇观比例悬殊，人小势大。")
SCENE_LINE = "【场景】雪原古战场，残破石台与断裂巨柱半埋雪里，远处群山与枯林，暴雪低吹。"
SPEED_LINE = ("【速度与打击】节奏先慢后爆：蓄势拍用慢动作压住，出手拍骤然爆发、快到肉眼难辨，"
              "多用“瞬间、极速、闪现、快到肉眼难辨、骤然爆发、残影”等速度描述；"
              "命中瞬间插入冲击帧与 0.1s 抽帧顿挫，镜头猛沉后急速回弹；"
              "出手段全程极限高速动态模糊与残影拖尾；所有音效随动作瞬间触发，命中配破空音爆。")
SOUND_LINE = ("【声音】无 BGM：蓄势段 风/低频/剑鸣；展开段 冰裂/低鸣/剑阵嗡鸣或龙吟；"
              "命中段 爆响/低频下潜/金石碎裂；收势段 余响/风/冰尘或墨尘飘落。")
NEG_BASE = ("【负向】不出现第二把剑、不多手、不换左手、不整体发光、不红眼、不出现红色、不出现西方翼龙、"
            "不出现对手尸体/血液、不生成字幕/UI/水印、不穿模、不全程慢动作")
NEG_XIANXIA = NEG_BASE + "；不出现水墨、二次元赛璐璐描边元素。"
NEG_SHUIMO = NEG_BASE + "；不出现二次元赛璐璐描边画风，水墨只以特效形式出现在写实画面里。"

# ---------------- 四候选 ----------------
V1 = f"""16:9，8 秒，东方仙侠大招《万剑归宗》，一条直出。
{REF_LINE}
【通用基底】顶级东方仙侠特效大片，IMAX 电影级画质，国漫写实 CG；冷冽青蓝色调，刺目金白剑芒；写实金属、冰雪与布料材质，体积光；4K，24fps，无穿模，动作凌厉，运镜恢弘丝滑。
{SPEED_LINE}
{CHARA_LINE}
{SCENE_LINE}
0-2秒｜拔剑蓄势：微距特写转慢动作——古剑震颤、寒光凛冽，一声剑鸣响彻雪原；他缓缓拔剑，剑尖垂地，周身冰雾升腾；全段压住节奏，只为下一拍爆发。
2-4秒｜万剑悬列：镜头极速后拉升起至遮天大全景——千百柄寒冰飞剑自雪原冰纹中破空而起，快到肉眼难辨、拖出冰蓝残影，悬浮列成旋转立体剑阵，遮蔽天光；亿万剑气交织，金属共振嗡鸣如潮。
4-6秒｜万剑齐发：他挥剑下压，万剑如天河倒灌倾泻轰击大地——齐发瞬间快到只剩光，命中点连续插入白闪冲击帧与 0.1s 抽帧顿挫，镜头猛沉后急速回弹；纯物理贯穿，雪原被犁出纵横冰壑，剑气织成刺眼光网，冰晶碎屑如暴雪倒卷，破空音爆连成一片。
6-8秒｜剑冢收势：大远景摇摄：万剑斜插遍野成无尽剑冢，剑雨仍连绵落下；他独立阵心、负手而立，人小势大；暴雪渐落，画面定格。
【核心特效】遮天剑阵、万剑倾泻、剑气光网、无尽剑冢。
{SOUND_LINE}
{NEG_XIANXIA}"""

V2 = f"""16:9，8 秒，恢弘水墨大招《泼墨吞世》，一条直出。
{REF_LINE}
【通用基底】顶级国漫写实 CG，电影级画质；人物与雪原为写实光影，特效为浓墨水墨——墨色泼洒、飞白笔触、水墨巨龙与水墨画卷在写实体积光里展开；黑白墨色为主，曜金一点；4K，24fps，无穿模，运镜恢弘。
{SPEED_LINE}
{CHARA_LINE}
{SCENE_LINE}
0-2秒｜凝神：面部特写用慢动作压住——他闭目，周身雪粒悬停；骤然睁眼，瞳孔后墨色自画面四角晕染开来，写实雪原开始被墨色浸染。
2-4秒｜泼墨成龙：大袖一挥快到只剩残影——磅礴浓墨自剑锋狂涌爆出，刹那间凝成一条遮天水墨巨龙（东方龙，蛇形长身、四爪、鹿角）缠绕盘旋，龙躯横扫之处雪原瞬息化作黑白水墨山水，飞白如风。
4-6秒｜吞世：水墨长龙挟画卷之势横扫吞没天地，快到只剩一道墨影掠过；群山、枯林、残柱接连被镇入黑白水墨长卷，画卷闭合瞬间插入 0.1s 抽帧顿挫与一记闷雷；曜金在龙眼处只留一点。
6-8秒｜画卷收势：大远景俯拍极远景：整片天地被镇平成一幅水墨长卷；墨色缓缓褪去、世界自画卷中苏醒，他负手立于坑边剑尖点地，墨尘飘落；定格。
【核心特效】泼墨成龙、水墨浸染天地、遮天水墨画卷、墨尘飘落。
{SOUND_LINE}
{NEG_SHUIMO}"""

V3 = f"""16:9，8 秒，东方仙侠大招《千丈寒剑·天开》，一条直出。
{REF_LINE}
【通用基底】顶级东方仙侠史诗大片，IMAX 电影级质感，国漫写实 CG；青铜巨链与黑曜石、冰雪写实材质，神圣金光与冷冽青蓝对冲；4K，24fps，无穿模，运镜恢弘。
{SPEED_LINE}
{CHARA_LINE}
{SCENE_LINE}
0-2秒｜蓄势：面部与剑格特写用慢动作压住——他闭目，周身雪粒悬停静止；骤然睁眼，瞳孔映出剑光，剑鸣刺耳。
2-4秒｜挥剑指天：他纵身跃起挥剑指天——起跳到剑指苍穹快到肉眼难辨，带多重残影；镜头极速后拉，一道千丈寒冰巨剑自剑尖向上轰然延伸、直贯云霄，剑身由亿点冰晶构成，云层被剑气剖开成环形漩涡；天地只剩这一道竖光。
4-6秒｜天裂：巨剑捅破天穹的瞬间插入全屏冲击帧与 0.15s 抽帧，径向曝光炸开，镜头猛沉后急速回弹——天空出现巨大的放射状冰裂，裂缝后透出曜金色天光与古老天门轮廓；冰晶如流星四溅；他在半空旋身落回地面，单膝点地，剑尖拄地，落点砸出环形雪浪。
6-8秒｜定格：大远景摇摄：千丈巨剑仍立在天地之间，缓缓消散成冰尘，天裂合拢，雪原被照成金色轮廓；他起身负手而立，白发白袍猎猎；画面定格。
【核心特效】千丈冰剑贯天、天穹放射冰裂、天门金光、流星冰晶。
{SOUND_LINE}
{NEG_XIANXIA}"""

V4 = f"""16:9，8 秒，国漫写实大招《冰龙贯野》，一条直出。
{REF_LINE}
【通用基底】顶级国漫写实风，电影级 CG 画质，IMAX 质感；写实冰霜、布料、金属与冰雪材质，体积光与景深，粒子细节丰富；冷冽青蓝灰色调，冰蓝，曜金一点；4K，24fps，无穿模，动作凌厉，运镜恢弘丝滑。
{SPEED_LINE}
{CHARA_LINE}
{SCENE_LINE}
0-2秒｜蓄势：低机位近景用慢动作压住——从握剑的手推到剑格，再抬到他的一只眼；冰霜沿剑脊爬，剑身轻颤；脚下雪面冰纹亮起一圈，向四周蔓延；风声抽空，只剩低频与剑鸣；他抬眼。
2-4秒｜阵开：镜头极速后拉并升起至大全景——七层冰晶剑阵刹那展开、冰柱拔地而起快到肉眼难辨；他举剑过肩，动作带残影；身后暴雪凝成一条巨大的寒冰龙形剑气——东方龙，蛇形长身、四爪、鹿角，龙首越过他的肩，龙躯冷光映亮半座雪山。
4-6秒｜龙扑命中：他挥剑下劈，冰龙沿剑势俯冲砸进大地——俯冲段快到只剩一道白光，砸地瞬间插入冲击帧与 0.1s 抽帧，镜头猛沉后急速回弹并震屏 2 帧；冰晶与剑气对撞成刺目白核，冲击波掀翻积雪成环状雪浪，碎石与冰棱浮空，白袍下摆与远处枯枝按距离延迟抖动，破空音爆炸响。
6-8秒｜收势：强光散去，大地上一个直径数十米的冰裂巨坑，坑壁插满冰棱；他立于坑边，剑尖点地；冰龙碎成漫天冰尘随暴雪落下；大远景定格，群山回响。
【核心特效】冰晶剑阵、寒冰龙形剑气、冰裂巨坑、悬浮冰棱。
{SOUND_LINE}
{NEG_XIANXIA}"""

# ---------------- 文本 ----------------
S1B = """【画风】国漫写实为底；候选覆盖 仙侠特效大片 / 恢弘水墨 两种质感（见各候选的通用基底）。
【角色】白发剑客，身高约一米八五（暂定），身形颀长挺拔、肩宽腰窄，白发束起，白袍黑腰封，双臂薄冰，冷峻；右手单手握剑，虎口贴剑格，左手掐剑诀。
【武器】藏音·龙跃霄汉：剑；冰泉色剑身、擎冰刃口、炼虹剑颚、曜日一点明光；剑身不整体发光，只留一道冷白高光；全片只有一把剑。
【色彩】冷冽青蓝灰；冰蓝；曜金一点；不出现红（水墨候选为黑白墨色+曜金）。
【场景】雪原古战场，残破石台与断裂巨柱，群山枯林，暴雪。"""

S0C = """【v5 · 先读】
四候选互不依赖，各 1 条 8s 直出，参照你给的参考：
V1 万剑归宗（参照“百万仙剑/剑冢”）／V2 泼墨吞世（恢弘水墨，参照“泼墨吞世”，写实底+水墨特效）／
V3 千丈寒剑·天开（参照“千丈光剑+天门”）／V4 冰龙贯野（武器冰系，国漫写实）。
【跑序】02 组可整组跑或单点；先各抽 1 条，选中的方向再抽 1 条对比；每节点最多 2 抽。
【身高】185cm 为暂定占位，确认后改各候选 prompt 里“身高约一米八五”一处即可（四个候选各一处）。
【30s】外部 30s 参考是 5.3s 循环×5.5 / 5.34s 拼贴×6，不是单条 30s；用选中的 8s 在剪辑里循环 3–4 次。
【回退】直出若脸不像/构图散，回退方案见 30 号文档 §6（K 帧首尾帧，需同步改画风）。"""

# ---------------- 节点 ----------------
nodes = [
    input_image("P1", 20, 20, "【来源记录】P1 角色（白发剑客）",
                "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261027-122555-bb6fa0be7e68df3f-p1-e4-ba-ba-e7-89-a9-e7-99-bd-e5-8f-91-e.png",
                526, 533, 572149, "7e5dbc051eff3e58b92f5a973c017d1a"),
    input_image("P2", 20, 250, "【来源记录】P2 武器（藏音·龙跃霄汉）",
                "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261027-122556-5df2712152eae9b4-p2-e6-ad-a6-e5-99-a8-e9-be-99-e8-b7-83-e.png",
                632, 711, 528519, "df2829d66050b0a95f9c6819ac355f86"),
    input_text("S1B", 20, 480, 320, 460, "S1 角色/武器/画风设定", S1B),
    reuse_image("A1", 420, 20, "A1 脸部（挂 V1–V4）"),
    reuse_image("A2", 780, 20, "A2 全身（挂 V1–V4 锁服装比例）"),
    reuse_image("A5", 420, 340, "A5 武器（挂 V1–V4）"),
    gen_video("V1", 1180, 20, "【候选】V1 万剑归宗 8s", V1, ["A1", "A2", "A5"], 8),
    gen_video("V2", 1180, 340, "【候选】V2 泼墨吞世 8s", V2, ["A1", "A2", "A5"], 8),
    gen_video("V3", 1560, 20, "【候选】V3 千丈寒剑·天开 8s", V3, ["A1", "A2", "A5"], 8),
    gen_video("V4", 1560, 340, "【候选】V4 冰龙贯野 8s", V4, ["A1", "A2", "A5"], 8),
    input_text("S0C", 20, 1060, 640, 460, "S0 变更说明/跑序（先读）", S0C),
]

# ---------------- 边：全部从引用字段派生 ----------------
pairs = []
for n in nodes:
    if n["type"] == "gen-video":
        mp = n["params"]["model_params"]
        for key in ("first_frame_image", "last_frame_image"):
            if mp.get(key):
                pairs.append((mp[key]["node_id"], n["id"]))
        for r in mp["reference_images"]:
            pairs.append((r["node_id"], n["id"]))
seen = set()
pairs = [p for p in pairs if not (p in seen or seen.add(p))]

by_id = {n["id"]: n for n in nodes}


def bf(ids):
    ids = [x for x in ids if x in by_id]
    xs = [by_id[x]["meta"]["x"] for x in ids]
    ys = [by_id[x]["meta"]["y"] for x in ids]
    xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
    ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
    return {"x": min(xs) - 18, "y": min(ys) - 46,
            "width": max(xe) - min(xs) + 36,
            "height": max(ye) - min(ys) + 46 + 22}


groups = [
    ("00 素材（不用跑）", ["P1", "P2", "S1B"], "#8E8DE0"),
    ("01 资产（已生成·复用 A1/A2/A5）", ["A1", "A2", "A5"], "#5B8DE0"),
    ("02 大招直出·四候选", ["V1", "V2", "V3", "V4"], "#E0A15B"),
    ("03 说明（不用跑）", ["S0C"], "#888888"),
]
gl = []
for k, (label, keys, color) in enumerate(groups):
    ids = [ID[x] for x in keys]
    gl.append({"id": f"g-ywdz-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
               "style": {"accent": None, "opacity": None, "borderColor": color}})

doc = {
    "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
    "canvas": {
        "name": "燕云大招 · 水墨短版 v1（8s）",
        "description": ("国漫写实为底 · 8s 直出 · 四候选：V1 万剑归宗 / V2 泼墨吞世（恢弘水墨） / "
                        "V3 千丈寒剑·天开 / V4 冰龙贯野。reference 模式挂 A1 脸 + A2 全身 + A5 武器；身高 185cm 暂定。"
                        "30s 参考是循环/拼贴，不是单条 30s；8s 单条，30s 用剪辑循环。"),
        "nodes": nodes,
        "edges": [{"id": "edge-" + hashlib.md5((s + t).encode()).hexdigest()[:8],
                   "sourceNodeId": s, "sourceHandle": "output",
                   "targetNodeId": t, "targetHandle": "input"} for s, t in pairs],
        "groups": gl,
    },
}

# ---------------- 自检 ----------------
def tok_by_id(nid):
    return "{{" + nid + "}}"


for n in nodes:
    if n["type"] == "gen-video":
        p = n["params"]["model_params"]
        assert not p["first_frame_image"] and not p["last_frame_image"], "直出节点不应有首尾帧"
        assert "一米八五" in p["prompt"], f"缺身高描述: {n['id']}"
        for r in p["reference_images"]:
            assert tok_by_id(r["node_id"]) in p["prompt"], f"V prompt 缺引用: {n['id']}"

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
DL.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(OUT, DL)
print("写出:", OUT)
print("副本:", DL)
print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(gl)}")
print("待生成视频:", [n["meta"]["label"] for n in nodes if n["type"] == "gen-video"])
