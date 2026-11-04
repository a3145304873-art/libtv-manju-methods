# -*- coding: utf-8 -*-
"""Build the 1x4 expression-sheet canvas for the cockatiel-hood Eggy.

One image, four busts of the same character: smug / caught / surprised / deadpan.
Character anchor: 5A (single brow + star highlight). Style anchors: REF1/REF2.
Output: 02_画布/二号位-玄凤兜帽-表情表-v1.monet
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
PREFIX = "yaya-expression-sheet:v1"
OUT = HERE / "二号位-玄凤兜帽-表情表-v1.monet"
REF = json.loads((ROOT / "04_素材" / "参考" / "二号位-风格参考" / "upload.json").read_text(encoding="utf-8"))
U5 = json.loads((ROOT / "04_素材" / "参考" / "二号位-风格参考" / "upload-5a.json").read_text(encoding="utf-8"))
REF5A = U5["候选-芽芽-5A-得意-表情-v1"]


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


def gen_image(key, label, prompt, refs, x, y, width=420.0, height=236.0):
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


def text_node(key, label, text, x, y, width=760.0, height=500.0):
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


PROMPT = """16:9 纯白底角色表情表，一张图，横向 1×4 四格；四格是同一只“芽芽”的四个半身像（头＋连帽＋上胸），同一角色、同一配色、同一角度，只有表情不同；格与格之间细浅灰分隔线；无文字、无标签、无水印。
角色以 [[REF5A]] 为准：奶油白蛋形身体、暖灰玄凤连帽、黄色羽冠、蜜桃腮斑、小粉钩喙（闭合装饰）、帽上两颗小圆点眼睛；脸板奶油色、大圆眼；签名特征固定：只有观众左眼上方一道细短深灰棕毛毡眉；两眼都是白色圆形高光（正常高光，不要星形/四角星/星星眼）；同一只眼睛、同一位置，四格不变。
以 [[REF1]]、[[REF2]] 为蛋仔形体/质感参考（蛋形、大脸板、短圆手、毛茸茸短绒/毛毡；不要狗/猫帽、M、具体配色）。
四格表情（从左到右）：
1 得意/懂王：左眼半眯、右眼睁大、单眉挑起、歪嘴笑露一点红舌；帽上小眼侧看、冠羽翘/歪。
2 被抓包/心虚：两眼睁大、瞳孔看左侧、眉挑更高、波浪线嘴、右太阳穴小汗滴；帽上小眼瞪大、冠羽耷拉。
3 惊讶/兴奋：两眼圆睁、嘴小圆“o”、单眉高挑、高光更亮/眼睛更圆；帽上小眼圆睁、冠羽竖起。
4 无语/冷面：左眼半眯、右眼平视、单眉压低/平、嘴一条平线；帽上小眼半眯、冠羽平/歪。
风格：毛茸茸短绒/毛毡、哑光、纤维可见；不是鸟体、不是翅膀手；无狗/猫帽、无 M、无文字。
负向：四只不同的角色、换色、换帽、换脸型、多余角色、鸟体、翅膀手、羽毛手、扇贝边、狗、猫、狗帽、猫帽、M 标志、牙齿、写实舌头、两条眉毛、粗眉、人类眉毛、四角星高光、星形高光、星星眼、文字、标签、字幕、logo、水印、光滑搪胶、塑料高光、3D 乙烯基、vinyl、写实眼、过曝、比例失真、灰底、渐变底、地面阴影、场景、道具。"""

S0_TEXT = """【这张画布做什么】
一张横向 1×4 表情表：同一只芽芽，四个半身像，只换表情。
从左到右：得意 / 被抓包 / 惊讶 / 无语。
角色锚：REF5A（5A 那张，锁单眉/星高光/帽上小脸）；REF1/REF2 只借蛋仔形体/毛绒。

【跑序】
1. 00 参考图组已上传。
2. 跑 01 的 6 表情表（单节点）。
3. 先看四格是不是同一只：同色/同帽/同脸型/同单眉位置/同星高光位置。
4. 再看四张脸能不能区分；128px 缩略图还能不能看出不同。

【如果漂移】
四格角色不一致，不硬修一张图；退回分张生成（5A/5B 已有，再补 5C/5D），后期 PIL 横向拼 1×4。

【不要做】
不要四只不同角色；不要换色/换帽/换脸型；不要文字/标签；不要狗/猫帽/M；不要鸟体/翅膀手。"""


def main():
    nodes = [
        input_image("REF1", "REF1 狗帽蛋仔 · 只借蛋仔形体", REF["ref-01-狗帽蛋仔"], 0, 0),
        input_image("REF2", "REF2 猫帽蛋仔 · 只借蛋仔形体", REF["ref-02-猫帽蛋仔"], 0, 250),
        input_image("REF5A", "REF5A 5A 得意 · 角色锚（单眉/星高光/帽）", REF5A, 0, 500),
        gen_image("R6", "【待生成】6 表情表 · 1×4（得意/被抓包/惊讶/无语）", link(PROMPT, ["REF1", "REF2", "REF5A"]), ["REF1", "REF2", "REF5A"], 380, 0),
        text_node("S0", "S0 说明 · 表情表怎么选", S0_TEXT, 380, 300),
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
        group("g00", "00 参考图 · 角色锚/形体", ["REF1", "REF2", "REF5A"], "#E68BB3"),
        group("g01", "01 生图 · 1×4 表情表", ["R6"], "#8E8DE0"),
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
              "canvas": {"name": "蛋仔记单词 · 二号位玄凤兜帽 · 表情表 1×4 v1",
                         "description": "一张横向 1×4 表情表：得意/被抓包/惊讶/无语；5A 角色锚；REF1/2 风格锚。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()
