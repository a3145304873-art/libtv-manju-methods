# -*- coding: utf-8 -*-
"""Build a 玩梗记单词 sample: morose = 没肉丝 -> 郁闷的.

20s, 2×10s. Same capybara 心易 + plush 黄蛋 shell; no in-video text;
post-production horizontal captions. A05 takeout box (no meat shreds).

Output: 02_画布/EP01-morose-meme-v2.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
PREFIX = "egg-morose-meme:v1"
OUT = HERE / "EP01-morose-meme-v2.monet"

R00 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035437-5241228d6d235662-r00-e5-9b-9b-e5-b0-8f-e5-8f-aa-e8-ba-ab.jpg",
    "name": "R00-四小只身高比例.jpg", "width": 1600, "height": 650, "size": 77895,
    "md5": "b321a4a46247edafe03ddd2dc85b3605",
}
R01 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-e4318cc875/image/20261022-035438-8a7a8cba5091bb94-e8-a7-92-e8-89-b2-e9-bb-84-e8-9b-8b-e6-a.jpg",
    "name": "角色-黄蛋-标准.jpg", "width": 1118, "height": 1280, "size": 86469,
    "md5": "7939d7b1ed7e0315344a5eb2c13e6d1a",
}
R02 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/mailgo.n31738/canvas-d240c8bf55/image/20261102-032549-6dfb56a52913e945-e5-bf-83-e6-98-93-e6-b0-b4-e8-b1-9a-e6-a.png",
    "name": "心易-水豚-标准.png", "width": 400, "height": 600, "size": 258953,
    "md5": "100cfe8f4f09ec467008f61a0ab30d7d",
}
A02 = {
    "url": "https://storage.monet.dreammaker.netease.com/v1/objects/fengshuhao01/canvas-143621ad40/image/20261030-091451-7adbbcb1b5f01f2c-55a7fc3aca10c44a88745d.png",
    "name": "55a7fc3aca10c44a88745d.png", "width": 1280, "height": 720, "size": 0,
    "md5": "",
}


def nid(key):
    return "node-" + hashlib.md5((PREFIX + ":" + key).encode("utf-8")).hexdigest()[:8]


def oid(kind, key):
    return "output-" + hashlib.md5((PREFIX + ":" + kind + ":" + key).encode("utf-8")).hexdigest()[:10]


def input_image(key, label, info, x, y, width=300.0):
    h = round(width * info["height"] / info["width"], 1)
    return {
        "id": nid(key), "type": "input-image", "mainOutputId": oid("input", key),
        "meta": {"x": float(x), "y": float(y), "width": width, "height": h,
                 "label": label, "resourceType": None},
        "outputs": [{"id": oid("input", key), "status": "done", "error": None,
                     "value": info["url"], "cover": None, "name": info["name"],
                     "resolution": {"width": info["width"], "height": info["height"]},
                     "source": None, "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": {"size": info["size"], "md5": info["md5"]}}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_image(key, label, prompt, ref_keys, x, y, width=300.0, height=170.0):
    return {
        "id": nid(key), "type": "gen-image", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": width, "height": height,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
            "prompt": prompt, "reference_images": [{"node_id": nid(k)} for k in ref_keys],
            "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 1024,
            "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def gen_video(key, label, prompt, ref_keys, ff, x, y, duration=10):
    return {
        "id": nid(key), "type": "gen-video", "mainOutputId": None,
        "meta": {"x": float(x), "y": float(y), "width": 340.0, "height": 220.0,
                 "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": nid(k)} for k in ref_keys],
            "reference_audios": [], "first_frame_image": {"node_id": nid(ff)},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": duration,
            "generate_audio": True, "watermark": False,
        }},
        "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


def text_node(key, label, text, x, y, width=760, height=540):
    return {
        "id": nid(key), "type": "input-text", "mainOutputId": oid("text", key),
        "meta": {"x": float(x), "y": float(y), "width": float(width), "height": float(height),
                 "label": label, "resourceType": None},
        "outputs": [{"id": oid("text", key), "status": "done", "error": None, "value": text,
                     "cover": None, "name": label, "resolution": None, "source": None,
                     "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": None}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


A05_PROMPT = """16:9 纯白底道具设定图，一个打开的白色外卖餐盒：里面白米饭＋青椒丝，**没有肉丝**；旁边一把白色塑料勺。3D卡通渲染+真实光影（皮克斯/搪胶），轻微高光；无角色、无手、无文字/logo/水印。
负向：肉丝、肉、角色、手、文字、logo、水印、真实照片。"""

R01P_PROMPT = """16:9 纯白底角色设定图，只生成一只黄蛋（毛绒版），全身正面。
保留黄蛋身份：黄色蛋形身体、奶油色椭圆大脸板、棕色大圆眼、头顶黄色天线+黄色圆球、短圆手臂无手指、白色袜子（黑条纹）+白色毛绒靴；没有牙齿。
材质改成和参考水豚玩偶一致的短毛绒/毛毡玩偶质感：表面细短绒毛、可见纤维、柔和缝线、哑光；脸板是奶油色毛毡/布；眼睛是亮面塑料/刺绣；天线球是布球；袜子/鞋是白布；边缘有轻微绒毛轮廓；柔光棚拍，轻微投影。
不要：光滑塑料/搪胶、真实鸡蛋、蛋壳裂开、蛋黄/蛋液、牙齿、人类手指、猫耳/水豚耳朵、橘子、文字/logo/水印。
负向：光滑塑料、真实照片、人类、手指、牙齿、裂壳、蛋液、蛋黄、文字、logo、水印、比例失真。"""

KA_PROMPT = """16:9 电影感首帧，第0秒，只生成一张。小院石桌（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，双手扶着打开的白色外卖餐盒（参考 [[A05]]），眼睛发亮、期待；心易（参考 [[R02]]，棕色水豚）在画面右1/3，看向餐盒。无文字、无气泡、无字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、旧心易/粉蛋/猫耳/天线、文字、气泡、字幕、logo、人类、比例失真、过曝。"""
KB_PROMPT = """16:9 电影感首帧，第0秒，只生成一张。小院石桌（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，坐在小凳/趴在桌边，面前是打开的餐盒（参考 [[A05]]），手里拿勺子拨青椒丝，眼神失落；心易（参考 [[R02]]，棕色水豚）在画面右1/3，同情地看他。无文字、无气泡、无字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、旧心易/粉蛋/猫耳/天线、文字、气泡、字幕、logo、人类、比例失真、过曝。"""

V1_PROMPT = """【风格】20s 玩梗记单词，横屏；小院石桌；黄蛋说话；心易只发“咔啵”；**视频内无文字/无气泡/无字幕**，白字后期加。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡质感；说话的人。心易（参考 [[R02]]，棕色水豚）：只发“咔啵”，不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，**没有肉丝**；勺子。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–2 秒：[[K_A]] 黄蛋双手打开餐盒，眼睛发亮：“青椒肉丝饭！”心易看餐盒。
2–5 秒：黄蛋看到只有青椒，愣住：“……肉丝呢？”拿勺子拨找。
5–7 秒：心易歪头：“咔啵？”黄蛋：“真的没肉丝……”
7–10 秒：黄蛋肩膀垮下，趴到桌边；镜尾定格 0.5s。
【声音】黄蛋人声；心易只有“咔啵”；餐盒/勺子环境声；无 BGM。
负向：视频内文字/气泡/字幕、黄蛋光滑塑料、心易说人话/加词、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""

V2_PROMPT = """【风格】20s 玩梗记单词，横屏；小院石桌；黄蛋说话；心易只发“咔啵”；**视频内无文字/无气泡/无字幕**，白字后期加。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡质感；说话的人。心易（参考 [[R02]]，棕色水豚）：只发“咔啵”，不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光。
0–3 秒：[[K_B]] 黄蛋趴在桌边，闷闷不乐：“没肉丝，所以我很 morose——郁闷的。”
3–5 秒：心易点头：“咔啵！”黄蛋：“morose，郁闷的。”
5–8 秒：黄蛋坐直一点：“没肉丝，所以郁闷；记住 morose。”
8–10 秒：黄蛋看镜头：“你记住了吗？”镜尾定格 1s。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、黄蛋光滑塑料、心易说人话/加词、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""

NOTES = """【本画布做什么】
《蛋仔记单词》玩梗版样片：morose = 没肉丝 → 郁闷的。20s（2×10s）。
黄蛋＝毛绒版，说话；心易＝棕色水豚，只发“咔啵”；视频内无文字/气泡；白字横排后期加。

【跑序】
1. 先修 R02（心易水豚）为你当前 Monet 账号可读的 URL；跨账号可能空。
2. 跑 R01P（黄蛋毛绒版）；看质感。
3. 跑 A05 餐盒（白饭＋青椒，无肉丝）。
4. 跑 K_A / K_B。
5. 跑 V1（10s）/ V2（10s）。
6. 后期加横排白字；不加气泡。

【口径】
- 1 个词／20s；谐音“没肉丝”只做记忆钩子；落点必须是 morose = 郁闷的。
- 黄蛋只拨食物，不吃；没有牙齿；不敲壳/不蛋液。
- 心易只发“咔啵”；不说话。
- A05 里不能出现肉丝；否则梗不成立。
"""
PART_A = """【风格】20s 玩梗记单词，横屏；小院石桌；黄蛋说话；心易只发“咔啵”；**视频内无文字/无气泡/无字幕**，白字后期加。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡质感；说话的人。心易（参考 [[R02]]，棕色水豚）：只发“咔啵”，不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，**没有肉丝**；勺子。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–2 秒：[[K_A]] 黄蛋双手打开餐盒，眼睛发亮：“青椒肉丝饭！”心易看餐盒。
2–5 秒：黄蛋看到只有青椒，愣住：“……肉丝呢？”拿勺子拨找。
5–7 秒：心易歪头：“咔啵？”黄蛋：“真的没肉丝……”
7–10 秒：黄蛋肩膀垮下，趴到桌边；镜尾定格 0.5s。
【声音】黄蛋人声；心易只有“咔啵”；餐盒/勺子环境声；无 BGM。
负向：视频内文字/气泡/字幕、黄蛋光滑塑料、心易说人话/加词、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""


def link(s):
    for k in ("R00", "R01", "R02", "R01P", "A02", "A05", "K_A", "K_B"):
        s = s.replace("[[" + k + "]]", "{{" + nid(k) + "}}")
    assert "[[" not in s
    return s


def main():
    nodes = [
        input_image("R00", "R00 四小只身高比例（复用）", R00, 0, 0),
        input_image("R01", "R01 黄蛋标准（复用）", R01, 0, 200, width=280),
        input_image("R02", "R02 心易·水豚（Monet URL；跨账号需替换）", R02, 0, 560, width=280),
        input_image("A02", "A02 小院 · 石桌/花坛/狗窝（复用）", A02, 360, 0),
        gen_image("R01P", "【待生成】R01P 黄蛋毛绒版 · 同水豚短毛绒质感", R01P_PROMPT, ["R01"], 360, 620),
        gen_image("A05", "【待生成】A05 外卖餐盒 · 白饭＋青椒，无肉丝＋勺子", A05_PROMPT, [], 360, 220),
        gen_image("K_A", "【待生成】K_A 首帧 · 黄蛋打开餐盒期待", link(KA_PROMPT), ["R00", "R01P", "R02", "A02", "A05"], 760, 0),
        gen_image("K_B", "【待生成】K_B 首帧 · 没肉丝，黄蛋失落", link(KB_PROMPT), ["R00", "R01P", "R02", "A02", "A05"], 760, 220),
        gen_video("V1", "【待生成】V1 · 10s · 打开餐盒/没肉丝", link(V1_PROMPT), ["R00", "R01P", "R02", "A02", "A05"], "K_A", 1200, 0),
        gen_video("V2", "【待生成】V2 · 10s · morose = 郁闷的", link(V2_PROMPT), ["R00", "R01P", "R02", "A02", "A05"], "K_B", 1200, 260),
        text_node("S0", "S0 制作说明 · 先读", NOTES, 760, 600),
    ]
    edges, seen = [], set()

    def edge(a, b):
        if (a, b) in seen:
            raise SystemExit(f"dup edge {a}->{b}")
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

    def group(key, label, keys, color, pad=20):
        ns = [next(n for n in nodes if n["id"] == nid(k)) for k in keys]
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
        group("g00", "00 参考素材 · 黄蛋/水豚/比例", ["R00", "R01", "R02"], "#E68BB3"),
        group("g01", "01 黄蛋毛绒版 · 先跑", ["R01P"], "#D8A657"),
        group("g02", "02 小院/餐盒 · 先跑", ["A02", "A05"], "#8E8DE0"),
        group("g03", "03 首帧 · K_A、K_B", ["K_A", "K_B"], "#E8B85D"),
        group("g04", "04 视频 V1 · 10s · 没肉丝", ["V1"], "#DC775D"),
        group("g05", "05 视频 V2 · 10s · 郁闷的", ["V2"], "#DC775D"),
        group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
    ]

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
            assert tok in refs or tok == ff, f"token {tok} not in refs/ff"
        for r in refs + ([ff] if ff else []):
            assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
        assert not mp.get("reference_audios")
        if n["type"] == "gen-video":
            assert ff in mp["prompt"]
    for i, a in enumerate(groups):
        for b in groups[i + 1:]:
            ax, ay, aw, ah = a["bounds"].values()
            bx, by_, bw, bh = b["bounds"].values()
            if ax < bx + bw and ax + aw > bx and ay < by_ + bh and ay + ah > by_:
                raise SystemExit(f"groups overlap: {a['label']} / {b['label']}")
    grouped = [i for g in groups for i in g["nodeIds"]]
    assert sorted(grouped) == sorted(ids_set)

    canvas = {"schemaVersion": 2, "type": "monet.canvas", "exportedAt": NOW,
              "canvas": {"name": "蛋仔记单词 · 玩梗样片「morose＝没肉丝」v2 · 20s",
                         "description": "morose 玩梗版：黄蛋毛绒版＋水豚心易；没肉丝→郁闷的；视频无字，白字后期。",
                         "nodes": nodes, "edges": edges, "groups": groups}}
    OUT.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
    print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
    print("->", OUT)
    print("->", Path.home() / "Downloads" / OUT.name)


if __name__ == "__main__":
    main()



