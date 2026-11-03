# -*- coding: utf-8 -*-
"""Build morose restaurant version: A06 small eatery + A07 one-shred plate.

Reuses generated R01P/A05/R00/R01/R02 from the user's morose v3.
New: A06 interior, A07 plate, K_A/V1/T_A/V2, single-card tail.
黄蛋 reacts; 心易 clerk/chef B-plot; narration post.

Output: 02_画布/EP01-morose-restaurant-v1.monet
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
USER = Path(r"C:\Users\N31738\Downloads\蛋仔记单词 · 玩梗样片「morose＝没肉丝」v3 · 20s（锁眼＋T_A 接尾帧）.monet")
OUT = HERE / "EP01-morose-restaurant-v1.monet"
REF = json.loads((ROOT / "01_资产" / "角色" / "morose-refs-upload.json").read_text(encoding="utf-8"))
CARD = json.loads((ROOT / "01_资产" / "道具" / "morose-card-upload.json").read_text(encoding="utf-8"))
PREFIX = "morose-restaurant:v1"

ud = json.loads(USER.read_text(encoding="utf-8-sig"))["canvas"]
unodes = ud["nodes"]


def ufind(prefix):
    return next(n for n in unodes if prefix in n["meta"].get("label", ""))


def uoutput(prefix):
    n = ufind(prefix)
    done = [o for o in n.get("outputs") or [] if o.get("status") == "done"]
    assert done, prefix
    return done[-1], n


def nid(key):
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode()).hexdigest()[:8]


def oid(key):
    return "output-" + hashlib.md5((PREFIX + ":out:" + key).encode()).hexdigest()[:10]


def input_from_user(key, label, prefix, x, y, width=300.0):
    out, src = uoutput(prefix)
    res = out.get("resolution") or {}
    h = round(width * res.get("height", 720) / res.get("width", 1280), 1)
    return {
        "id": nid(key), "type": "input-image", "mainOutputId": oid(key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": h,
                 "label": label, "resourceType": None},
        "outputs": [{**out, "id": oid(key)}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_from_user(key, label, prefix, x, y, width=300.0):
    out, src = uoutput(prefix)
    n = json.loads(json.dumps(src))
    n["id"] = nid(key)
    n["mainOutputId"] = None
    n["meta"] = {"x": float(x), "y": float(y), "width": width, "height": 197.0,
                 "label": label, "resourceType": None}
    n["outputs"] = []
    n["createdAt"] = n["updatedAt"] = NOW
    n["createdBy"] = n["updatedBy"] = AUTHOR
    return n


def input_image(key, label, info, x, y, width=300.0):
    h = round(width * info["height"] / info["width"], 1)
    return {
        "id": nid(key), "type": "input-image", "mainOutputId": oid(key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": h,
                 "label": label, "resourceType": None},
        "outputs": [{"id": oid(key), "status": "done", "error": None, "value": info["url"], "cover": None,
                     "name": info["name"], "resolution": {"width": info["width"], "height": info["height"]},
                     "source": None, "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": {"size": info["size"], "md5": info["md5"]}}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_image(key, label, prompt, refs, x, y, width=300.0, height=197.0):
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


def gen_video(key, label, prompt, refs, ff, x, y, duration):
    return {
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 340.0, "height": 224.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": nid(k)} for k in refs],
            "reference_audios": [], "first_frame_image": {"node_id": nid(ff)},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": duration,
            "generate_audio": True, "watermark": False,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def text_node(key, label, text, x, y, width=760, height=540):
    return {
        "id": nid(key), "type": "input-text", "mainOutputId": oid(key),
        "meta": {"x": float(x), "y": float(y), "width": float(width), "height": float(height),
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
    assert "[[" not in s
    return s


A06_PROMPT = """16:9 电影感内景空景，只生成一张。街边小饭馆/快餐店内部：木质柜台＋收银机＋出菜口＋后厨窗口（背景有炒锅/灶台），几张木桌/塑料凳，墙上菜单只有食物图片、无文字/无价格；暖黄灯，窗外傍晚街景虚化；3D卡通+真实光影（皮克斯/搪胶）。
无人物、无手、无文字、无logo/水印。
负向：人物、手、文字、价格、logo、水印、真实照片、过曝、杂乱。"""
A07_PROMPT = """16:9 纯白底道具设定图：一个小白碟，碟里只有一根青椒肉丝（一根肉丝＋一根青椒丝）。3D卡通+真实光影，轻微投影；无角色/手/文字/logo/水印。
负向：多根肉丝、满盘、角色、手、文字、logo、水印、真实照片。"""
KA_PROMPT = """16:9 电影感首帧，第0秒，只生成一张。小饭馆柜台（参考 [[A06]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，站在柜台前，短手指向墙上菜单图片；心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油眼白、外圈粗深棕描边，内部没有黑瞳孔/没有棕色虹膜，像布偶刺绣/纽扣眼）在画面右1/3，站在柜台后，看向黄蛋；柜台上放着打开的打包盒（参考 [[A05]]）。两人都不说话、嘴巴闭合；无文字/气泡/字幕。暖黄灯，傍晚，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、角色说话、文字、气泡、字幕、logo、人类、比例失真、过曝。"""
V1_PROMPT = """【风格】20s 玩梗记单词，横屏；小饭馆内景；黄蛋说话（短句）；心易只发“咔啵”，不说话；无文字/气泡；旁白后期。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；顾客。心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油眼白、外圈粗深棕描边，内部无黑瞳孔/无棕色虹膜）；店员/厨师，只发“咔啵”，不说话。
【场景】[[A06]] 小饭馆柜台/后厨窗口/木桌，暖黄灯，傍晚。
【道具】[[A05]] 打包盒（白饭＋青椒，无肉丝）。
0–2 秒：[[K_A]] 黄蛋站在柜台前，指墙上菜单图片：“青椒肉丝饭，肉丝多一点！”
2–4 秒：心易点头，冲后厨喊：“咔啵！”（收到）
4–6 秒：心易从出菜口拿打包盒，装袋/递出；黄蛋接。
6–8 秒：黄蛋端着餐盒走向木桌；**尾帧停在半路/桌边，稳定 1 秒**，给 V2 接尾帧。
【声音】黄蛋人声（短句）；心易只有“咔啵”；环境声；旁白后期。
负向：视频内文字/气泡/字幕、心易说人话/加词、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧黄蛋光滑塑料、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""
V2_PROMPT = """【风格】20s 玩梗记单词，横屏；小饭馆内景；黄蛋说话（短句）；心易只发“咔啵”，不说话；无文字/气泡；旁白后期。**首帧＝T_A**：从 V1 最后一帧（黄蛋端盒走到桌边）继续，不换机位/不重摆/不换光。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；顾客。心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油眼白、外圈粗深棕描边，内部无黑瞳孔/无棕色虹膜）；店员/厨师，只发“咔啵”，不说话。
【场景】[[A06]] 小饭馆柜台/后厨窗口/木桌，暖黄灯，傍晚；与 T_A 同一空间/光线。
【道具】[[A05]] 打包盒（白饭＋青椒，无肉丝）；[[A07]] 小白碟＋一根肉丝。
0–2 秒：[[T_A]] 黄蛋在桌边打开打包盒，只有青椒：“……怎么没有肉丝？”
2–4 秒：心易在柜台后僵住/探头：“咔啵？”（心虚）
4–6 秒：心易缩回后厨窗口：“咔——啵”（等一下）
6–8 秒：心易端小白碟（一根肉丝）放桌上：“咔啵！”（补救）
8–9 秒：黄蛋看那一根，更郁闷；心易低头/拍肩：“咔……啵……”镜尾定格 1s。
【声音】黄蛋人声（短句）；心易只有“咔啵”；环境声；旁白后期。
负向：视频内文字/气泡/字幕、心易说人话/加词、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧黄蛋光滑塑料、满盘肉丝、蛋壳裂开/蛋液、牙齿、logo、换机位/重摆/换光、慢速横移、渐变、白场、过曝。"""


def main():
    nodes = [
        input_from_user("R00", "R00 四小只身高比例（复用）", "R00", 0, 0),
        input_from_user("R01", "R01 黄蛋标准（复用）", "R01", 0, 200, width=280),
        input_from_user("R02", "R02 心易·水豚（复用）", "R02", 0, 560, width=280),
        input_image("R02E", "R02E 心易眼睛参考（复用）", REF["心易-水豚-眼睛参考"], 0, 1000),
        input_from_user("R01P", "【已生成】R01P 黄蛋毛绒版（复用）", "R01P", 360, 0, width=240),
        input_from_user("A05", "【已生成】A05 打包盒（复用）", "A05", 360, 260, width=240),
        gen_image("A06", "【待生成】A06 小饭馆内景 · 柜台/后厨窗口/木桌（菜单无字）", A06_PROMPT, [], 360, 580),
        gen_image("A07", "【待生成】A07 小白碟＋一根肉丝", A07_PROMPT, [], 360, 800),
        gen_image("K_A", "【待生成】K_A 首帧 · 柜台点单", link(KA_PROMPT, ["R00", "R01P", "R02", "R02E", "A06", "A05"]), ["R00", "R01P", "R02", "R02E", "A06", "A05"], 760, 0),
        input_image("T_A", "T_A 占位 · 先跑 V1，再替换成 V1 最后一帧", REF["T_A-占位-替换V1尾帧"], 760, 260),
        gen_video("V1", "【待生成】V1 · 8s · 点单/后厨/端走", link(V1_PROMPT, ["R00", "R01P", "R02", "R02E", "A06", "A05", "K_A"]), ["R00", "R01P", "R02", "R02E", "A06", "A05"], "K_A", 1200, 0, 8),
        gen_video("V2", "【待生成】V2 · 9s · 没肉丝/后厨补救（首帧 T_A）", link(V2_PROMPT, ["R00", "R01P", "R02", "R02E", "A06", "A05", "A07", "T_A"]), ["R00", "R01P", "R02", "R02E", "A06", "A05", "A07"], "T_A", 1200, 300, 9),
        input_image("KC", "KC 单卡尾 · morose / 没肉丝 → 郁闷的（后期用）", CARD, 1200, 600),
    ]
    nodes.append(text_node("S0", "S0 制作说明 · 先读", """【本画布做什么】
《蛋仔记单词》玩梗样片·小饭馆版：morose = 没肉丝 → 郁闷的。20s。
V1 8s（点单/后厨/端走）＋ T_A ＋ V2 9s（没肉丝/心易补救）＋ 单卡尾 3s。
黄蛋说短句；心易只“咔啵”；旁白后期；视频内无字。

【跑序】
1. 跑 A06 小饭馆内景（菜单无字）。
2. 跑 A07 小白碟＋一根肉丝（可选）。
3. 跑 K_A 首帧。
4. 跑 V1（8s）；结尾停在黄蛋端盒走到桌边，稳定 1s。
5. 截 V1 尾帧 → 替换 T_A。
6. 跑 V2（9s，首帧 T_A）。
7. 后期：V1+V2 → 单卡尾 3s；加旁白；心易“咔啵？”。

【分工】
- 黄蛋：顾客；短句“青椒肉丝饭，肉丝多一点”“怎么没有肉丝”“就一根？”“你记住了吗”。
- 心易：店员/厨师；咔啵！收到 → 咔啵？心虚 → 咔——啵等一下 → 咔啵！补救 → 咔……啵……抱歉。
- 旁白：morose，郁闷的。没肉丝，所以郁闷。
- R01P/A05/R00/R01/R02/R02E 复用，不重跑。

【场景】
小饭馆：柜台＋出菜口＋后厨窗口＋木桌；菜单只有食物图片，无文字/价格；暖黄灯，傍晚。
""", 760, 600))
    nodes[-1]["meta"]["x"] = 760.0
    nodes[-1]["meta"]["y"] = 600.0

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
        group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", ["R00", "R01", "R02", "R02E"], "#E68BB3"),
        group("g01", "01 已生成 · 黄蛋毛绒/打包盒", ["R01P", "A05"], "#D8A657"),
        group("g02", "02 小饭馆/一根肉丝 · 先跑", ["A06", "A07"], "#8E8DE0"),
        group("g03", "03 首帧/尾帧 · K_A、T_A", ["K_A", "T_A"], "#E8B85D"),
        group("g04", "04 视频 V1 · 8s · 点单/端走", ["V1"], "#DC775D"),
        group("g05", "05 视频 V2 · 9s · 补救", ["V2"], "#DC775D"),
        group("g06", "06 单卡尾/说明 · 后期", ["KC", "S0"], "#7FB07F"),
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
        if n["type"] == "gen-video":
            mp = n["params"]["model_params"]
            for r in mp["reference_images"]:
                edge(r["node_id"], n["id"])
            edge(mp["first_frame_image"]["node_id"], n["id"])
        elif n["type"] == "gen-image":
            for r in n["params"]["model_params"]["reference_images"]:
                edge(r["node_id"], n["id"])

    # validate
    ids_set = {n["id"] for n in nodes}
    by_id = {n["id"]: n for n in nodes}
    edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in edges}
    for n in nodes:
        if n["type"] not in ("gen-image", "gen-video"):
            continue
        mp = n["params"]["model_params"]
        refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
            assert tok in by_id, f"missing {tok}"
            assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
        for r in refs + ([ff] if ff else []):
            assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
        assert not mp.get("reference_audios")
        if n["type"] == "gen-video":
            assert ff in mp["prompt"]
            assert 3 <= mp["duration"] <= 16
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by_, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
                raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
    grouped = [i for g in groups for i in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids_set), "group coverage mismatch"

    canvas = {"schemaVersion": 2, "type": "monet.canvas", "exportedAt": NOW,
              "canvas": {"name": "蛋仔记单词 · 玩梗样片「morose＝没肉丝」小饭馆版 v1 · 20s",
                         "description": "morose 小饭馆版：柜台点单→端盒到桌→没肉丝→心易补救；黄蛋短句；旁白；单卡尾。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()


