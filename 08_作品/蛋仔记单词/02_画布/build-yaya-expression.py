# -*- coding: utf-8 -*-
"""Build the 二号位 芽芽 cockatiel-hood expression canvas.

5A: smug / know-it-all (default)
5B: caught / guilty (reaction)
Base: 4A classic-gray hood + Eggy body/face/hands.
Output: 02_画布/二号位-玄凤兜帽-表情-v1.monet
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
PREFIX = "yaya-expression:v1"
OUT = HERE / "二号位-玄凤兜帽-表情-v1.monet"
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


STYLE = """参考图 [[REF1]]、[[REF2]] 只取蛋仔形体/质感：蛋形身体、头身一体、大头、大奶油色脸板、大圆眼、短圆手臂＋白色手套/肉垫、白色小靴、毛茸茸短毛绒/毛毡、柔光、纯白背景；不要复制狗/猫帽、狗耳/猫耳、M 标志、具体配色。"""

BODY = """
身体：奶油白/米白蛋形毛绒身体，头身一体，没有脖子，头约占全身一半；13cm 玩具比例；
手：两只短圆蛋仔手臂，奶油白，上臂一块暖灰/蜜桃色小肉垫，末端白色手套/肉垫，无手指；不是翅膀、不是羽毛、不要扇贝边；
腿/鞋：两条短腿，白色毛绒小靴，靴口暖灰边；胸口一枚小叶子徽章（金色/奶油色），不要 M 标志；
连帽：暖灰色玄凤鹦鹉连帽衫；帽顶一撮高耸的黄色羽冠；帽两侧蜜桃色圆腮斑；帽前额一个小钩喙（灰粉色，闭合，装饰，不用于说话）；帽前额两颗小圆点眼睛（装饰）；"""

A_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + BODY + """
表情（5A 得意/懂王）：
脸板奶油色；大圆眼；观众左眼半眯（上眼皮略降），观众右眼睁大；两眼都是白色圆形高光（正常高光，不要星形/四角星/星星眼）；
只有观众左眼上方一道细短的深灰棕色毛毡眉毛，挑起；不是两条眉毛、不是人类粗眉；
歪嘴笑：观众左嘴角上扬、右嘴角平/略下压，嘴微张，露出一点红色舌头，无牙；
帽上的两颗小圆点眼睛向观众右侧看（侧眼）；帽顶羽冠翘起、略向观众左侧歪；
材质：短毛绒/毛毡，毛茸茸、哑光、纤维可见；纯白背景，无阴影，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：对称笑脸、两条眉毛、粗眉、人类眉毛、牙齿、写实舌头、大哭、鸟体、翅膀手、羽毛手、扇贝边、狗、猫、狗帽、猫帽、M 标志、心易、水豚、橘子、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、四角星高光、星形高光、星星眼、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

B_PROMPT = """16:9 纯白底角色设定图，只生成一只“芽芽”，单个角色，正面偏 3/4 站姿，全身入画。
""" + STYLE + BODY.replace("手：两只短圆蛋仔手臂，奶油白，上臂一块暖灰/蜜桃色小肉垫，末端白色手套/肉垫，无手指；不是翅膀、不是羽毛、不要扇贝边；",
    "手：两只短圆蛋仔手臂，抬到胸前，掌心朝外，像在说“等一下/不是我”；上臂一块暖灰/蜜桃色小肉垫，末端白色手套/肉垫，无手指；不是翅膀、不是羽毛、不要扇贝边；") + """
表情（5B 被抓包/心虚）：
脸板奶油色；大圆眼；两只眼睛睁大，瞳孔都看向观众左侧（侧眼）；两眼都是白色圆形高光（正常高光，不要星形/四角星/星星眼）；
只有观众左眼上方一道细短的深灰棕色毛毡眉毛，挑得更高；不是两条眉毛、不是人类粗眉；
波浪线嘴：一条小小的波浪形/锯齿形嘴线，闭口，不露舌，无牙；
观众右侧太阳穴旁一滴小汗滴（浅蓝色，卡通/毛毡感，只在表情里，不是身体部件）；
帽上的两颗小圆点眼睛瞪大；帽顶羽冠耷拉、向一侧歪；
材质：短毛绒/毛毡，毛茸茸、哑光、纤维可见；纯白背景，无阴影，无第二只角色，无文字、无字幕、无 logo、无水印。
负向：对称笑脸、两条眉毛、粗眉、人类眉毛、牙齿、红舌、大哭、鸟体、翅膀手、羽毛手、扇贝边、狗、猫、狗帽、猫帽、M 标志、心易、水豚、橘子、长脖子、长腿、手指、脚趾、多余手臂、第三只手、多双手、两只以上的脚、四角星高光、星形高光、星星眼、文字、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

S0_TEXT = """【这张画布做什么】
4A 经典灰兜帽的签名表情测试，两张：
- 5A 得意/懂王：单边挑眉、一眼半眯、星形高光、歪嘴笑；帽上小脸侧看、冠羽翘。
- 5B 被抓包/心虚：两眼睁大侧看、眉挑更高、波浪线嘴、小汗滴；双手抬到胸前；帽上小脸瞪大、冠羽耷。

【签名特征】
- 只有一只眼睛上方一道细短毛毡眉（单边挑眉）。
- 一只眼睛四角星高光，一只圆点高光。
- 嘴不对称：歪嘴笑 / 波浪线嘴。
- 帽上小脸（两点眼＋小喙）有自己的表情，常和主脸唱反调。

【跑序】
1. 00 参考图组已上传。
2. 01 组 5A/5B 独立，可并行跑。
3. 先看 128px 能不能区分“得意” vs “被抓包”；再看单眉/星高光/歪嘴/波浪嘴。
4. 选默认表情（建议 5A）和反应表情（5B）；不满意可换冷面/呆萌/困倦。

【不要做】
不要对称笑脸；不要两条粗眉；不要牙齿/写实舌；不要鸟体/翅膀手；不要狗/猫帽；不要心易入镜；不要文字/字幕。"""


def main():
    nodes = [
        input_image("REF1", "REF1 狗帽蛋仔 · 只借蛋仔形体", REF["ref-01-狗帽蛋仔"], 0, 0),
        input_image("REF2", "REF2 猫帽蛋仔 · 只借蛋仔形体", REF["ref-02-猫帽蛋仔"], 0, 340),
        gen_image("R5A", "【待生成】5A 得意/懂王 · 表情设定", link(A_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 0),
        gen_image("R5B", "【待生成】5B 被抓包/心虚 · 表情设定", link(B_PROMPT, ["REF1", "REF2"]), ["REF1", "REF2"], 400, 280),
        text_node("S0", "S0 说明 · 表情怎么选", S0_TEXT, 800, 0),
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
        group("g01", "01 生图 · 5A/5B 对比（并行）", ["R5A", "R5B"], "#8E8DE0"),
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
              "canvas": {"name": "蛋仔记单词 · 二号位玄凤兜帽 · 表情设定 v1",
                         "description": "4A 基础加签名表情：单边挑眉/星形高光/歪嘴笑/帽上小脸；5A 得意 vs 5B 被抓包。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()
