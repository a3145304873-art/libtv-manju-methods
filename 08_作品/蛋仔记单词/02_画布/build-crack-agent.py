# -*- coding: utf-8 -*-
"""Build local Monet canvas for the LibTV-Agent crack workflow.

Source : 04_素材/libtv-agent-crack/*.json  (LibTV Agent node prompts, revised)
Template: 02_画布/EP01-morose-关键句-16s-v1.monet  (node/edge schema + asset nodes)
Output : 02_画布/crack-LibTV-Agent抄版-v1.monet

改动相对 Agent 原稿：
  1) 纯净复刻：A3/A4/A5/A6/A7/S1 六段提示词全部照抄 LibTV 原文（仅把 {{Node i-…}} 换成 {{node-…}}），
     不加负向、不改阶段描述；已逐段字符比对确认一字不差（见 00_方案/60 第九节）。
  2) S2 原稿未产出（等 S1 尾帧）→ 本脚本按同一结构补写，首帧挂 T_A 占位；这是唯一非照抄节点。
  3) 视频节点用本项目常用 seedance-2.0-mini（Agent 原稿选 wanx3.0），图片用 gpt-image-2。
"""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "04_素材" / "libtv-agent-crack"
TEMPLATE = HERE / "EP01-morose-关键句-16s-v1.monet"
R00_SRC = HERE / "EP01-morose-meme-v4.monet"
OUT = HERE / "crack-LibTV-Agent抄版-v1.monet"

NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"


def nid(label):
    return "node-" + hashlib.sha1(label.encode("utf-8")).hexdigest()[:8]


def edge(a, b):
    h = hashlib.sha1(("%s>%s" % (a, b)).encode("utf-8")).hexdigest()[:8]
    return {
        "id": "edge-" + h, "sourceNodeId": a, "sourceHandle": "output",
        "targetNodeId": b, "targetHandle": "input",
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def agent_prompt(fname):
    d = load(RAW / fname)
    p = d["data"]["params"].get("prompt")
    if isinstance(p, list):
        p = "\n".join(p)
    return p or ""


def main():
    tpl = load(TEMPLATE)
    c = tpl["canvas"]
    by_label = {n["meta"]["label"]: n for n in c["nodes"]}

    # ---- 本地节点 ID ----
    L = {
        "R02": nid("crack/R02 心易"),
        "R02E": nid("crack/R02E 眼睛"),
        "R4A": nid("crack/R4A 芽芽4A"),
        "R00": nid("crack/R00 比例"),
        "A3": nid("crack/A3 料理台"),
        "A4": nid("crack/A4 全蛋"),
        "A5": nid("crack/A5 裂蛋"),
        "A6": nid("crack/A6 首帧"),
        "S1": nid("crack/S1 镜头一"),
        "TA": nid("crack/TA 尾帧占位"),
        "S2": nid("crack/S2 镜头二"),
        "A7": nid("crack/A7 片尾"),
        "S0": nid("crack/S0 说明"),
    }
    # LibTV 节点 → 本地节点
    MAP = {
        "i-Qne6Qz3F3J": L["R02"], "i-2mrdVFsHBp": L["R02E"], "i-7Z4rrw5Ebo": L["R4A"],
        "i-pEOy4U0OEL": L["R00"], "i-22fgwhvt6atw": L["A3"], "i-8ejxytgzuau4": L["A4"],
        "i-8x45zzzbu9cs": L["A5"], "i-7syq75ug6ksx": L["A6"], "i-zrtckghshjar": L["A7"],
    }

    def rewrite(text):
        def sub(m):
            return "{{%s}}" % MAP[m.group(1)]
        return re.sub(r"\{\{Node (i-[0-9A-Za-z]+)\}\}", sub, text)

    # ---- 素材节点（复用已有 output，换 id）----
    def copy_asset(src_label, new_id, x, y, label):
        import copy
        src = by_label[src_label]
        n = copy.deepcopy(src)
        n["id"] = new_id
        n["meta"] = dict(n["meta"], label=label, x=x, y=y)
        return n

    r00_src = None
    for n in load(R00_SRC)["canvas"]["nodes"]:
        if "R00" in (n["meta"].get("label") or ""):
            r00_src = n
            break
    r00 = json.loads(json.dumps(r00_src))
    r00["id"] = L["R00"]
    r00["meta"] = dict(r00["meta"], label="R00 四小只身高比例（只借比例）", x=0.0, y=1240.0)

    nodes = [
        copy_asset("R02 心易·水豚标准（复用）", L["R02"], 0.0, 0.0, "R02 心易·水豚标准（复用）"),
        copy_asset("R02E 心易眼睛参考（复用）", L["R02E"], 0.0, 420.0, "R02E 心易眼睛参考（复用）"),
        copy_asset("R4A 芽芽 4A 经典灰兜帽（无星）", L["R4A"], 0.0, 700.0, "R4A 芽芽 4A 经典灰兜帽"),
        r00,
        copy_asset("T_A 占位 · 先跑 V1，再替换成 V1 最后一帧", L["TA"], 760.0, 700.0,
                   "T_A 占位 · 先跑 S1，再替换成 S1 最后一帧"),
    ]

    # ---- 文本节点 ----
    s0 = """crack（一捏就裂）· LibTV Agent 抄版 v1

来源：LibTV Agent（TV Director）在 LibTV 画布 0d70eb6b1fe74562a632f798cfc02f4c 搭的 6 节点；
本画布为本地版本，提示词按 Agent 修正后稿转录，并做三处本地修订（见 00_方案/60 与 61）。

跑序：
1) A3 料理台 + A4 全蛋 → 各出 1 张即可
2) A5 裂蛋（引 A4）+ A6 首帧（引 R02/R02E/R4A/R00/A3/A4）
3) S1 8s（首帧＝A6）
4) S1 出片后，把它的最后一帧存成图片替换 T_A 占位
5) S2 9s（首帧＝T_A）
6) A7 片尾卡（引 R02/R02E/R4A/R00/A3/A5）→ 合成 19.5s

规矩：画面内一律不生成文字；词 crack 首现＝13.0s；心易只发「咔啵」；芽芽全片只说一句。"""
    nodes.append({
        "id": L["S0"], "type": "input-text", "mainOutputId": None,
        "meta": {"x": 0.0, "y": -260.0, "width": 300.0, "height": 300.0,
                 "label": "S0 制作说明 · 先读", "resourceType": None},
        "outputs": [], "params": {"content": s0}, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    })

    # ---- 提示词 ----
    a3 = agent_prompt("i-22fgwhvt6atw.json")
    a4 = agent_prompt("i-8ejxytgzuau4.json")
    a5 = rewrite(agent_prompt("i-8x45zzzbu9cs.json"))
    a6 = rewrite(agent_prompt("i-7syq75ug6ksx.json"))
    a7 = rewrite(agent_prompt("i-zrtckghshjar.json"))
    s1 = rewrite(agent_prompt("v-vqzpnk397xg7.json"))

    # 纯净复刻：A3/A4/A5/A6/A7/S1 全部照抄 LibTV 原文（仅把 {{Node i-…}} 换成 {{node-…}}）
    neg_img = ""

    s2 = """【首帧】画面{{%TA}}用于本镜的起始画面、两人当前构图与光线，从这一帧接着演。
【人物】心易{{%R02}}用于棕色水豚玩偶的全身外貌与毛绒质感：圆身无脖子、奶油色大脸板、白色圆眼片外圈一道深棕色细线、眼片中心空白无瞳孔无高光、橘色椭圆腮红、一字嘴、头顶带绿叶的小橘子；心易{{%R02E}}的眼部局部参考与{{%R02}}共同定义同一个心易，成片中始终只有一个，全程不眨眼。芽芽{{%R4A}}用于米白蛋形身体与浅灰玄凤鹦鹉连帽的高羽冠、帽侧圆形腮斑、小钩喙、帽下正常比例的大眼睛与胸前金色叶状标记，不采用其白色背景。各人物的外貌、动作和站位不互相交换。{{%R00}}只用于两人身高比例与体量关系，不采用图中任何角色的外观与配色。
【道具】开裂白煮蛋{{%A5}}用于裂缝形状与渗出的蛋白，不采用其灰色背景；本镜只有这一颗蛋，完整蛋不再出现。
【场景】原木料理台{{%A3}}用于场景空间与晨光光线。
【动作与声音】心易全程只发拟声「咔啵」，不说人话；芽芽只说下面这一句含词的话。
【阶段一】开始时：承接上一拍——心易僵在原地捧着裂蛋，芽芽羽冠竖起、帽侧腮斑加深。心易捧着裂蛋慢慢转向芽芽，另一只短手抬起来挡在脸前，肩膀往下塌。结束时：心易侧身对芽芽，一只短手挡在脸前、一只短手捧裂蛋。
【阶段二】承接上一阶段：芽芽先低头看蛋，视线沿那道从蛋顶到蛋腰的裂缝走一遍；再抬头看心易；高羽冠一节一节伏下去，帽侧腮斑退回浅色；小钩喙轻轻碰一下心易的手背。结束时：钩喙贴着手背，开口前一刻。
【阶段三】承接上一阶段：芽芽用稚嫩清亮、尾音上扬的小童声线说：{别难过啦——是你捏得太用力，它才会 crack。} 说话时心易保持短手挡脸、眼片朝下。结束时：台词说完，两人姿势未变。
【阶段四】承接上一阶段：芽芽把裂蛋从心易掌心里托出来放回台面，裂缝还在渗蛋白；心易把两只短手一起覆在蛋上，不动。镜头保持机位与光线不变，由中近景缓拉至双人中景，画面里始终保留台面与蛋的位置关系，不给心易的脸部与眼睛做特写。结束时：双人中景，蛋在台面中央，心易覆手不动。
保持人物身份、数量、服装、道具归属、空间方向和声音关系稳定。
3D 毛绒质感卡通渲染，角色造型圆润、深棕色粗描边，色彩以暖黄与米白为主，清晨窗光低对比柔光，背景轻微虚化，画面干净无任何文字。
【禁止出现】多余的手臂、第三只手、多双手、多只脚；任何字幕、文字、字母、数字、水印与标志；心易的黑瞳、瞳孔、虹膜与高光点，以及眨眼与眼皮；中途换机位、重新摆位、改变光线与色温；两个角色的外貌、配色、配饰或站位互相交换；画面里出现第三个角色或人群。
无背景音乐。"""
    for k, v in {"%R02E": L["R02E"], "%R02": L["R02"], "%R4A": L["R4A"],
                 "%R00": L["R00"], "%TA": L["TA"], "%A5": L["A5"],
                 "%A3": L["A3"]}.items():
        s2 = s2.replace(k, v)

    # ---- 生成节点 ----
    def gen_image(key, label, prompt, refs, x, y, w=300.0, h=169.0):
        return {
            "id": L[key], "type": "gen-image", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": w, "height": h,
                     "label": "【待生成】" + label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
                "prompt": prompt,
                "reference_images": [{"node_id": L[k]} for k in refs],
                "aspect_ratio": "9:16", "image_size": "1K",
                "width": 1024, "height": 1024, "quality": "medium",
                "output_format": "png", "moderation": "low", "auto_compress": True,
            }},
            "specialParams": None, "config": None,
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        }

    def gen_video(key, label, prompt, refs, first_frame, duration, x, y):
        return {
            "id": L[key], "type": "gen-video", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": 340.0, "height": 224.0,
                     "label": "【待生成】" + label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
                "prompt": prompt,
                "_reference_way": "reference",
                "reference_images": [{"node_id": L[k]} for k in refs],
                "reference_audios": [],
                "first_frame_image": {"node_id": L[first_frame]},
                "resolution": "720p", "aspect_ratio": "9:16",
                "duration": duration,
            }},
            "specialParams": None, "config": None,
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        }

    nodes += [
        gen_image("A3", "A3 厨房料理台 · 空镜", a3, [], 360.0, 0.0),
        gen_image("A4", "A4 白煮蛋 · 完整", a4, [], 360.0, 200.0),
        gen_image("A5", "A5 白煮蛋 · 开裂", a5, ["A4"], 360.0, 400.0),
        gen_image("A6", "A6 镜头一 · 首帧", a6, ["R02", "R02E", "R4A", "R00", "A3", "A4"], 760.0, 0.0),
        gen_video("S1", "S1 镜头一 · 8s · 剥壳→一捏即裂",
                  s1, ["R02", "R02E", "R4A", "R00", "A3", "A4", "A5"], "A6", 8, 1180.0, 0.0),
        gen_image("A7", "A7 片尾卡 · 无字底板",
                  a7, ["R02", "R02E", "R4A", "R00", "A3", "A5"], 1180.0, 300.0),
        gen_video("S2", "S2 镜头二 · 9s · 芽芽说 crack",
                  s2, ["R02", "R02E", "R4A", "R00", "A3", "A5"], "TA", 9, 1180.0, 700.0),
    ]

    # ---- 连线 ----
    pairs = [
        (L["A4"], L["A5"]),
        (L["R02"], L["A6"]), (L["R02E"], L["A6"]), (L["R4A"], L["A6"]),
        (L["R00"], L["A6"]), (L["A3"], L["A6"]), (L["A4"], L["A6"]),
        (L["A6"], L["S1"]), (L["R02"], L["S1"]), (L["R02E"], L["S1"]),
        (L["R4A"], L["S1"]), (L["R00"], L["S1"]), (L["A3"], L["S1"]),
        (L["A4"], L["S1"]), (L["A5"], L["S1"]),
        (L["TA"], L["S2"]), (L["R02"], L["S2"]), (L["R02E"], L["S2"]),
        (L["R4A"], L["S2"]), (L["R00"], L["S2"]), (L["A3"], L["S2"]),
        (L["A5"], L["S2"]),
        (L["R02"], L["A7"]), (L["R02E"], L["A7"]), (L["R4A"], L["A7"]),
        (L["R00"], L["A7"]), (L["A3"], L["A7"]), (L["A5"], L["A7"]),
    ]
    edges = [edge(a, b) for a, b in pairs]

    canvas = {
        "name": "蛋仔记单词 · crack 一捏就裂 · LibTV Agent 抄版 v1",
        "description": "由 LibTV Agent（TV Director）工作流转录的本地版本；19.5s（8＋9＋2.5），词 crack 首现 13.0s。",
        "nodes": nodes, "edges": edges, "groups": [
            {
                "id": "group-" + hashlib.sha1(b"crack/ref").hexdigest()[:8],
                "nodeIds": [L["R02"], L["R02E"], L["R4A"], L["R00"]],
                "bounds": {"x": -20.0, "y": -20.0, "width": 260.0, "height": 1431.5},
                "label": "00 角色/比例参考（复用，不生成）",
                "style": {"accent": None, "opacity": None, "borderColor": "#E68BB3"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
            {
                "id": "group-" + hashlib.sha1(b"crack/scene").hexdigest()[:8],
                "nodeIds": [L["A3"], L["A4"]],
                "bounds": {"x": 340.0, "y": -20.0, "width": 340.0, "height": 400.0},
                "label": "01 场景/道具 · 先跑",
                "style": {"accent": None, "opacity": None, "borderColor": "#7FB2E5"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
            {
                "id": "group-" + hashlib.sha1(b"crack/frames").hexdigest()[:8],
                "nodeIds": [L["A5"], L["A6"], L["TA"]],
                "bounds": {"x": 340.0, "y": 400.0, "width": 780.0, "height": 520.0},
                "label": "02 裂蛋/首帧/尾帧 · A5、A6、T_A",
                "style": {"accent": None, "opacity": None, "borderColor": "#D9B36C"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
            {
                "id": "group-" + hashlib.sha1(b"crack/s1").hexdigest()[:8],
                "nodeIds": [L["S1"]],
                "bounds": {"x": 1160.0, "y": -20.0, "width": 380.0, "height": 264.0},
                "label": "03 S1 · 8s · 剥壳→一捏即裂",
                "style": {"accent": None, "opacity": None, "borderColor": "#9ED16F"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
            {
                "id": "group-" + hashlib.sha1(b"crack/s2").hexdigest()[:8],
                "nodeIds": [L["S2"]],
                "bounds": {"x": 1160.0, "y": 680.0, "width": 380.0, "height": 264.0},
                "label": "04 S2 · 9s · 芽芽说 crack",
                "style": {"accent": None, "opacity": None, "borderColor": "#9ED16F"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
            {
                "id": "group-" + hashlib.sha1(b"crack/tail").hexdigest()[:8],
                "nodeIds": [L["A7"], L["S0"]],
                "bounds": {"x": 0.0, "y": -320.0, "width": 1420.0, "height": 300.0},
                "label": "05 尾卡/说明 · 后期",
                "style": {"accent": None, "opacity": None, "borderColor": "#B0B0B0"},
                "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
            },
        ],
    }
    out = {"schemaVersion": tpl["schemaVersion"], "type": tpl["type"],
           "exportedAt": NOW, "canvas": canvas}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written:", OUT)
    print("nodes:", len(nodes), "edges:", len(edges))


if __name__ == "__main__":
    main()
