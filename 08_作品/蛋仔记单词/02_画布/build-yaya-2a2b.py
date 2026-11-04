# -*- coding: utf-8 -*-
"""Build the 二号位 芽芽 2A/2B character-sheet comparison canvas.

2A: cream egg body + misty-green leaf-bird hood; face-plate mouth talks,
    small beak on the hood is decorative.
2B: misty-green egg bird body, no hood; amber beak is the mouth.

Both gen-image nodes use the same two style references (upload.json).
Output: 02_画布/二号位-芽芽-2A2B-白底设定-v1.monet
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
PREFIX = "yaya-2a2b:v1"
OUT = HERE / "二号位-芽芽-2A2B-白底设定-v1.monet"
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


def text_node(key, label, text, x, y, width=760.0, height=620.0):
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


STYLE = """参考图 [[REF1]]、[[REF2]] 只取形体：蛋形身体、头身一体、大头、大脸板、大眼睛、张嘴笑红舌无牙、短手短脚、白色小靴、头顶小球、柔光、纯白背景；材质改成毛茸茸的短毛绒/毛毡，哑光、纤维可见，不是光滑搪胶/塑料/3D 乙烯基；不要复制狗/猫帽、狗耳/猫耳、M 标志、具体配色。"""

A_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + """
芽芽 2A：奶油白/米白毛绒蛋形身体，头身一体，没有脖子，头约占全身一半；13cm 玩具比例；
穿雾青绿毛毡叶子鸟连帽衫：帽子覆盖头顶和后脑，帽前额一个小三角琥珀喙（闭合，装饰，不是说话嘴），帽顶一株卷叶芽、芽尖一颗小琥珀球；帽后下方一片大叶形尾羽，深青绿，中央浅色缝线叶脉；
奶油色大圆脸板，占正面大部分，边缘一圈浅绿细边；
大圆眼：白眼球＋琥珀棕虹膜＋黑瞳孔＋一个白高光；毛绒玩偶的固定眼片/刺绣眼工艺，可眨眼、可做表情；不是写实眼、不是光滑塑料反光；
张嘴笑，红色舌头，无牙；说话时用脸板的嘴开合，帽子上的喙不动；
两只短圆毛绒手臂，奶油白，末端雾青绿毛毡手套，无手指；两条短腿，白袜＋白色毛毡小靴，靴口雾青绿边，无脚趾；
胸口一枚毛毡/刺绣小叶子徽章（金色/奶油色），不要 M 标志；
短毛绒/毛毡质感，毛茸茸、哑光、纤维可见，边缘有细绒光；不是光滑搪胶、不是塑料、不是 3D 乙烯基、不是写实鸟；
纯白背景，无阴影地面，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：狗帽、猫帽、狗耳、猫耳、狗嘴、猫脸、M 标志、参考图角色、第二只角色、心易、水豚、橘子、写实鸟、真实羽毛、鸟爪、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、牙齿、写实舌头、心易的白片无瞳、深棕大眼圈、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

B_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + """
芽芽 2B：雾青绿（偏蓝的叶绿，不是草绿）毛绒蛋形身体，头身一体，没有脖子，头约占全身一半；13cm 玩具比例；没有连帽衫、没有帽子；
奶油色大圆脸板，占正面大部分；脸板上是大圆眼：白眼球＋琥珀棕虹膜＋黑瞳孔＋一个白高光；毛绒玩偶的固定眼片/刺绣眼工艺，可眨眼；不是写实眼、不是光滑塑料反光；
小三角毛毡喙，琥珀橘色，就是嘴，可开合说话；无牙、无舌、不出现口腔内部；脸板上没有第二张嘴；
头顶一株毛毡卷叶芽，芽尖一颗小琥珀球；身后一片大叶形毛毡尾羽，深青绿，中央浅色缝线叶脉；
两只短圆毛绒手臂，雾青绿，末端奶油白毛毡手套，无手指；两条短腿，白袜＋白色毛毡小靴，靴口雾青绿边，无脚趾；
胸口一枚毛毡/刺绣小叶子徽章（金色/奶油色），不要 M 标志；
短毛绒/毛毡质感，毛茸茸、哑光、纤维可见，边缘有细绒光；不是光滑搪胶、不是塑料、不是 3D 乙烯基、不是写实鸟；
纯白背景，无阴影地面，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：连帽、帽子、帽上喙、两张嘴、狗帽、猫帽、狗耳、猫耳、狗嘴、猫脸、M 标志、参考图角色、第二只角色、心易、水豚、橘子、写实鸟、真实羽毛、鸟爪、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、牙齿、舌头、张开的口腔内部、心易的白片无瞳、深棕大眼圈、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

S0_TEXT = """【这张画布做什么】
二号位“芽芽”白底角色设定图，两个方向同图对比：
- 2A：奶油白蛋仔＋雾青绿叶子鸟连帽；脸板的嘴说话，帽上小三角喙闭合装饰。
- 2B：雾青绿蛋形鸟体，无帽；琥珀喙就是嘴。

【参考图怎么用】
REF1/REF2 只取形体：蛋形比例、大脸板、大眼、张嘴笑、短手短脚、小靴、头顶球；材质改成毛茸茸短毛绒/毛毡，哑光、纤维可见。
不复制：狗/猫帽、狗/猫耳、M 标志、具体配色、参考图角色身份。

【跑序】
1. 00 参考图组已上传，通常已是 done。
2. 01 组里 2A/2B 独立，可并行跑；两张都出 1 张先看。
3. 看 128px 剪影、眼睛、嘴/喙、材质、和心易的区分。
4. 选一个方向；不要两张都当定稿。

【判断点】
- 2A：帽上喙有没有被误当成说话嘴？脸板的嘴是否清楚？
- 2B：有没有偷偷长出帽子/第二张嘴？喙是否像嘴而不是鼻子？
- 两张：有没有狗/猫帽、M 标志、长脖子、长腿、手指、写实羽毛？
- 材质：毛茸茸短毛绒/毛毡；不是光滑搪胶、不是塑料高光。
- 同框：暖棕毛绒心易 vs 奶油/雾青绿毛绒芽芽，能不能一眼分开？

【不要做】
不要狗/猫角色；不要 M 标志；不要第二只角色；不要文字/字幕；不要心易入镜。
生成后混了狗/猫帽或 M，直接重跑，不要把参考图当角色设定图用。"""


def main():
    nodes = [
        input_image("REF1", "REF1 狗帽蛋仔 · 只取风格", REF["ref-01-狗帽蛋仔"], 0, 0),
        input_image("REF2", "REF2 猫帽蛋仔 · 只取风格", REF["ref-02-猫帽蛋仔"], 0, 340),
        gen_image("R2A", "【待生成】2A 叶鸟连帽 · 毛绒设定图", link(A_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 0),
        gen_image("R2B", "【待生成】2B 蛋形鸟体 · 毛绒设定图", link(B_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 280),
        text_node("S0", "S0 说明 · 2A/2B 怎么选", S0_TEXT, 800, 0),
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
        group("g00", "00 参考图 · 只取风格", ["REF1", "REF2"], "#E68BB3"),
        group("g01", "01 生图 · 2A/2B 对比（并行）", ["R2A", "R2B"], "#8E8DE0"),
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
              "canvas": {"name": "蛋仔记单词 · 二号位芽芽 · 2A/2B 白底设定对比 v1",
                         "description": "2A 叶鸟连帽 vs 2B 蛋形鸟体；同一组参考图只借形体；毛绒材质；两张并行生图，选一个方向。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()
