# -*- coding: utf-8 -*-
"""Build the 二号位 芽芽 cockatiel-hood Eggy 4A/4B character-sheet canvas.

4A: cream egg body + warm-gray cockatiel hood.
4B: cream egg body + warm-beige cockatiel hood.

Both keep the Eggy body/face/mouth and short round arms with white mitten tips
(the user explicitly wants the Eggy hands). The hood carries the cockatiel cues.
Output: 02_画布/二号位-玄凤兜帽蛋仔-设定-v1.monet
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
PREFIX = "yaya-cockatiel-hood:v1"
OUT = HERE / "二号位-玄凤兜帽蛋仔-设定-v1.monet"
REF = json.loads((ROOT / "04_素材" / "参考" / "二号位-风格参考" / "upload.json").read_text(encoding="utf-8"))


def nid(key):
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode()).hexdigest()[:8]


def oid(key):
    return "output-" + hashlib.md5((PREFIX + ":out:" + key).encode()).hexdigest()[:10]


def input_image(key, label, info, x, y, width=300.0):
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


def text_node(key, label, text, x, y, width=760.0, height=680.0):
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


STYLE = """参考图 [[REF1]]、[[REF2]] 只取蛋仔形体/质感：蛋形身体、头身一体、大头、大奶油色脸板、大圆眼、张嘴笑红舌无牙、短圆手臂＋白色手套/肉垫、白色小靴、毛茸茸短毛绒/毛毡、柔光、纯白背景；不要复制狗/猫帽、狗耳/猫耳、M 标志、具体配色。"""

A_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + """
芽芽是“蛋仔穿玄凤鹦鹉连帽衫”，不是鸟体：
身体：奶油白/米白蛋形毛绒身体，头身一体，没有脖子，头约占全身一半；13cm 玩具比例；
脸：奶油色大圆脸板，占正面大部分；大圆眼：白眼球＋琥珀棕虹膜＋黑瞳孔＋一个白高光；毛绒玩偶的固定眼片/刺绣眼，可眨眼；张嘴笑，红色舌头，无牙；说话用脸板的嘴；
连帽：暖灰色玄凤鹦鹉连帽衫，帽子覆盖头顶和后脑；帽顶一撮高耸的黄色羽冠（3–5 根尖羽，向后弯），是羽毛冠，不是叶子/植物芽；帽前额一个小钩喙（灰粉色，喙尖向下弯，闭合，装饰，不用于说话）；帽两侧各一块蜜桃色圆腮斑；帽前额两只小圆点眼睛（装饰，不是说话眼）；
手：两只短圆蛋仔手臂，奶油白，上臂一块暖灰/蜜桃色小肉垫，末端白色手套/肉垫，无手指；不是翅膀、不是羽毛、不要扇贝边；
腿/鞋：两条短腿，白色毛绒小靴，靴口暖灰边，无脚趾；
胸口：一枚小叶子徽章（金色/奶油色），不要 M 标志；
材质：短毛绒/毛毡，毛茸茸、哑光、纤维可见，边缘有细绒光；不是光滑搪胶、不是塑料、不是 3D 乙烯基；
纯白背景，无阴影地面，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：鸟体、鸟身、翅膀手、羽毛手、扇贝边、鸭嘴、鸡喙、大鹦鹉喙、狗、猫、狗帽、猫帽、狗耳、猫耳、M 标志、小鸡、鸭子、企鹅、猫头鹰、叶子冠、植物芽、叶子尾、橘子、心易、水豚、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、牙齿、写实舌头、张开的口腔内部、心易的白片无瞳、深棕大眼圈、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

B_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + """
芽芽是“蛋仔穿玄凤鹦鹉连帽衫”，不是鸟体：
身体：奶油白/米白蛋形毛绒身体，头身一体，没有脖子，头约占全身一半；13cm 玩具比例；
脸：奶油色大圆脸板，占正面大部分；大圆眼：白眼球＋琥珀棕虹膜＋黑瞳孔＋一个白高光；毛绒玩偶的固定眼片/刺绣眼，可眨眼；张嘴笑，红色舌头，无牙；说话用脸板的嘴；
连帽：暖杏色/浅驼色玄凤鹦鹉连帽衫，帽檐一圈深一点的杏色边；帽子覆盖头顶和后脑；帽顶一撮高耸的黄色羽冠（3–5 根尖羽，向后弯），是羽毛冠，不是叶子/植物芽；帽前额一个小钩喙（灰粉色，喙尖向下弯，闭合，装饰，不用于说话）；帽两侧各一块蜜桃色圆腮斑；帽前额两只小圆点眼睛（装饰，不是说话眼）；
手：两只短圆蛋仔手臂，奶油白，上臂一块暖杏/蜜桃色小肉垫，末端白色手套/肉垫，无手指；不是翅膀、不是羽毛、不要扇贝边；
腿/鞋：两条短腿，白色毛绒小靴，靴口暖杏边，无脚趾；
胸口：一枚小叶子徽章（金色/奶油色），不要 M 标志；
材质：短毛绒/毛毡，毛茸茸、哑光、纤维可见，边缘有细绒光；不是光滑搪胶、不是塑料、不是 3D 乙烯基；
纯白背景，无阴影地面，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：鸟体、鸟身、翅膀手、羽毛手、扇贝边、鸭嘴、鸡喙、大鹦鹉喙、狗、猫、狗帽、猫帽、狗耳、猫耳、M 标志、小鸡、鸭子、企鹅、猫头鹰、叶子冠、植物芽、叶子尾、橘子、心易、水豚、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、牙齿、写实舌头、张开的口腔内部、心易的白片无瞳、深棕大眼圈、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

S0_TEXT = """【这张画布做什么】
二号位“芽芽”= 蛋仔穿玄凤连帽衫，不是鸟体。两个色系：
- 4A 经典灰兜帽：奶油身体＋暖灰玄凤帽＋黄羽冠＋蜜桃腮斑。
- 4B 暖杏色兜帽：奶油身体＋暖杏/浅驼帽＋黄羽冠＋蜜桃腮斑。

【为什么改】
3A/3B 鸟体被反馈“太丑、手不像蛋仔”。这一版保住：蛋形身体、大脸板、大眼、张嘴笑、短圆手臂＋白手套/肉垫、白靴；玄凤只做帽子。

【跑序】
1. 00 参考图组已上传。
2. 01 组 4A/4B 独立，可并行跑。
3. 先看手/身体/脸是不是蛋仔，再看帽子是不是一眼玄凤。
4. 选一个色系，或要求修手/帽。

【判断点】
- 手：短圆、无手指、白手套/肉垫、上臂小肉垫；不是翅膀/羽毛/扇贝边。
- 身体：蛋形，不是鸟体；无鸟翅/鸟尾。
- 脸：大脸板、大眼、张嘴笑红舌无牙；说话用这张嘴。
- 帽：高羽冠、腮斑、小钩喙；帽上小喙闭合装饰，不抢说话嘴。
- 128px：先看像不像蛋仔，再看像不像玄凤。
- 不要狗/猫帽、M 标志、文字、第二只角色。

【不要做】
不要鸟体/翅膀手；不要狗/猫帽；不要心易入镜；不要文字/字幕。"""


def main():
    nodes = [
        input_image("REF1", "REF1 狗帽蛋仔 · 只借蛋仔形体", REF["ref-01-狗帽蛋仔"], 0, 0),
        input_image("REF2", "REF2 猫帽蛋仔 · 只借蛋仔形体", REF["ref-02-猫帽蛋仔"], 0, 340),
        gen_image("R4A", "【待生成】4A 玄凤兜帽蛋仔·经典灰 · 毛绒设定图", link(A_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 0),
        gen_image("R4B", "【待生成】4B 玄凤兜帽蛋仔·暖杏色 · 毛绒设定图", link(B_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 280),
        text_node("S0", "S0 说明 · 兜帽蛋仔怎么选", S0_TEXT, 800, 0),
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
        group("g00", "00 参考图 · 只借蛋仔形体", ["REF1", "REF2"], "#E68BB3"),
        group("g01", "01 生图 · 4A/4B 对比（并行）", ["R4A", "R4B"], "#8E8DE0"),
        group("g02", "02 说明 · 先读", ["S0"], "#7FB07F"),
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
        if n["type"] == "gen-image":
            for r in n["params"]["model_params"]["reference_images"]:
                edge(r["node_id"], n["id"])

    ids_set = {n["id"] for n in nodes}
    by_id = {n["id"]: n for n in nodes}
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    for n in nodes:
        if n["type"] != "gen-image":
            continue
        mp = n["params"]["model_params"]
        refs = [r["node_id"] for r in mp["reference_images"]]
        for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
            assert tok in by_id, f"missing {tok}"
            assert tok in refs, f"token {tok} not in refs in {n['meta']['label']}"
        for r in refs:
            assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
        assert not mp.get("reference_audios")
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by_, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
                raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
    grouped = [i for g in groups for i in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids_set), "group coverage mismatch"

    canvas = {"schemaVersion": 2, "type": "monet.canvas", "exportedAt": NOW,
              "canvas": {"name": "蛋仔记单词 · 二号位玄凤兜帽蛋仔 · 毛绒设定对比 v1",
                         "description": "蛋仔身体/脸/短圆手 + 玄凤连帽；4A 经典灰 / 4B 暖杏；说话用蛋仔嘴，帽上小喙装饰。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()
