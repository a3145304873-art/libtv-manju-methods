# -*- coding: utf-8 -*-
"""Build morose v3: add R02E eye reference + T_A tail-frame chain.

- K_A/V1/V2 use R02E to lock 心易's button eyes.
- V1 ends on a stable pose; user replaces T_A with V1's last frame; V2 starts from T_A.
- No K_B (V2 is chained from T_A).
- Keeps A02/A05/R01P/R00/R01/R02.

Output: 02_画布/EP01-morose-meme-v3.monet
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
SRC = HERE / "EP01-morose-meme-v2.monet"
OUT = HERE / "EP01-morose-meme-v3.monet"
REF = json.loads((ROOT / "01_资产" / "角色" / "morose-refs-upload.json").read_text(encoding="utf-8"))

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


ids = {}
for k, p in (("R00", "R00"), ("R01", "R01"), ("R02", "R02"), ("R01P", "R01P"),
             ("A02", "A02"), ("A05", "A05"), ("K_A", "K_A"), ("K_B", "K_B"),
             ("V1", "V1"), ("V2", "V2"), ("S0", "S0")):
    ids[k] = find(p)["id"]
by[ids["S0"]]["meta"]["y"] = 700.0
for k in ("K_B",):
    nodes.remove(by[ids[k]])
    by.pop(ids[k], None)
    ids.pop(k)


def link(s):
    for k in list(ids):
        s = s.replace("[[" + k + "]]", "{{" + ids[k] + "}}")
    assert "[[" not in s
    return s


def input_image(key, label, info, x, y):
    nid = "node-" + hashlib.md5(("egg-morose-meme:v3:" + key).encode()).hexdigest()[:8]
    ids[key] = nid
    return {
        "id": nid, "type": "input-image", "mainOutputId": "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10],
        "meta": {"x": float(x), "y": float(y), "width": 300.0, "height": 300.0,
                 "label": label, "resourceType": None},
        "outputs": [{"id": "output-" + hashlib.md5((key + ":out").encode()).hexdigest()[:10],
                     "status": "done", "error": None, "value": info["url"], "cover": None,
                     "name": info["name"], "resolution": {"width": info["width"], "height": info["height"]},
                     "source": None, "batchId": None, "execution": None, "graphRunId": None,
                     "iterationPath": None, "taskSource": None, "taskId": None,
                     "executorRunId": None, "stage": None, "deletedAt": None,
                     "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
                     "metadata": {"size": info["size"], "md5": info["md5"]}}],
        "params": None, "specialParams": None, "config": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    }


r02e = input_image("R02E", "R02E 心易眼睛参考 · 白眼球＋深棕圈（锁眼）", REF["心易-水豚-眼睛参考"], 0, 1000)
ta = input_image("T_A", "T_A 占位 · 先跑 V1，再替换成 V1 最后一帧", REF["T_A-占位-替换V1尾帧"], 760, 320)
nodes.extend([r02e, ta])
by[r02e["id"]] = r02e
by[ta["id"]] = ta

EYE = "心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]）：大圆形眼睛，白色/奶油色眼白，外圈粗深棕描边，内部没有黑色瞳孔、没有棕色虹膜，像布偶的刺绣/纽扣眼；不要黑豆眼、写实瞳孔、动漫高光。"
KA = """16:9 电影感首帧，第0秒，只生成一张。小院石桌（参考 [[A02]]）：双人中景，黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）在画面左1/3，双手扶着打开的白色外卖餐盒（参考 [[A05]]），眼睛发亮、期待；心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油眼白、外圈粗深棕描边、内部没有黑瞳孔/没有棕色虹膜、像布偶刺绣纽扣眼）在画面右1/3，看向餐盒。无文字、无气泡、无字幕。低机位，午后暖光，3D卡通+真实光影。
负向：旧黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/粉蛋/猫耳/天线、文字、气泡、字幕、logo、人类、比例失真、过曝。"""
V1 = """【风格】20s 玩梗记单词，横屏；小院石桌；黄蛋说话；心易只发“咔啵”；视频内无文字/无气泡/无字幕，白字后期加。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡质感；说话的人。[[R02]] 心易＝棕色水豚；[[R02E]] 锁眼：大圆形、白色/奶油眼白、外圈粗深棕描边、内部没有黑瞳孔/没有棕色虹膜、像布偶刺绣纽扣眼；只发“咔啵”，不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–2 秒：[[K_A]] 黄蛋双手打开餐盒，眼睛发亮：“青椒肉丝饭！”心易看餐盒。
2–5 秒：黄蛋看到只有青椒，愣住：“……肉丝呢？”拿勺子拨找。
5–7 秒：心易歪头：“咔啵？”黄蛋：“真的没肉丝……”
7–10 秒：黄蛋肩膀垮下，趴到桌边；**保持趴桌姿势 1 秒，镜尾稳定**，给 V2 接尾帧。
【声音】黄蛋人声；心易只有“咔啵”；餐盒/勺子环境声；无 BGM。
负向：视频内文字/气泡/字幕、黄蛋光滑塑料、心易说人话/加词、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""
V2 = """【风格】20s 玩梗记单词，横屏；小院石桌；黄蛋说话；心易只发“咔啵”；视频内无文字/无气泡/无字幕，白字后期加。**首帧＝T_A**：必须从 V1 最后一帧（黄蛋趴桌）继续，不能换机位/不能重摆/不能换光。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡质感；说话的人。[[R02]] 心易＝棕色水豚；[[R02E]] 锁眼：大圆形、白色/奶油眼白、外圈粗深棕描边、内部没有黑瞳孔/没有棕色虹膜、像布偶刺绣纽扣眼；只发“咔啵”，不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。\n【场景】[[A02]] 小院石桌，午后暖光；与 T_A 同一位置/光线/构图。
0–3 秒：[[T_A]] 黄蛋从趴桌姿势慢慢抬头，闷闷不乐：“没肉丝，所以我很 morose——郁闷的。”
3–5 秒：心易点头：“咔啵！”黄蛋：“morose，郁闷的。”
5–8 秒：黄蛋坐直一点：“没肉丝，所以郁闷；记住 morose。”
8–10 秒：黄蛋看镜头：“你记住了吗？”镜尾定格 1s。
【声音】黄蛋人声；心易只有“咔啵”；环境声；无 BGM。
负向：视频内文字/气泡/字幕、黄蛋光滑塑料、心易说人话/加词、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、换机位/重摆/换光、慢速横移、渐变、白场、过曝。"""

for key, prompt, refs, ff in (
    ("K_A", KA, ["R00", "R01P", "R02", "R02E", "A02", "A05"], None),
    ("V1", V1, ["R00", "R01P", "R02", "R02E", "A02", "A05"], "K_A"),
    ("V2", V2, ["R00", "R01P", "R02", "R02E", "A02", "A05"], "T_A"),
):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["reference_images"] = [{"node_id": ids[k]} for k in refs]
    if ff:
        mp["first_frame_image"] = {"node_id": ids[ff]}
    n["outputs"] = []
    n["meta"]["label"] = {
        "K_A": "【待生成】K_A 首帧 · 黄蛋打开餐盒期待（锁眼）",
        "V1": "【待生成】V1 · 10s · 没肉丝（锁眼，尾帧稳定）",
        "V2": "【待生成】V2 · 10s · 郁闷的（首帧＝T_A）",
    }[key]

# groups
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {"id": "group-" + hashlib.md5(("egg-morose-meme:v3:group:" + key).encode()).hexdigest()[:8],
            "nodeIds": [ids[k] for k in keys],
            "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", ["R00", "R01", "R02", "R02E"], "#E68BB3"),
    group("g01", "01 黄蛋毛绒版 · 先跑", ["R01P"], "#D8A657"),
    group("g02", "02 小院/餐盒 · 先跑", ["A02", "A05"], "#8E8DE0"),
    group("g03", "03 首帧/尾帧 · K_A、T_A", ["K_A", "T_A"], "#E8B85D"),
    group("g04", "04 视频 V1 · 10s · 没肉丝", ["V1"], "#DC775D"),
    group("g05", "05 视频 V2 · 10s · 郁闷的（首帧 T_A）", ["V2"], "#DC775D"),
    group("g06", "06 制作说明 · 先读", ["S0"], "#7FB07F"),
]
c["groups"] = groups

# edges
required = set()
for n in nodes:
    if n.get("type") == "gen-video":
        mp = n["params"]["model_params"]
        for r in mp.get("reference_images", []):
            required.add((r["node_id"], n["id"]))
        ff = (mp.get("first_frame_image") or {}).get("node_id")
        if ff:
            required.add((ff, n["id"]))
    elif n.get("type") == "gen-image":
        for r in n["params"]["model_params"].get("reference_images", []):
            required.add((r["node_id"], n["id"]))
edges = [{"id": "edge-" + hashlib.md5((a + ">" + b).encode()).hexdigest()[:8],
          "sourceNodeId": a, "sourceHandle": "output",
          "targetNodeId": b, "targetHandle": "input",
          "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}
         for a, b in sorted(required)]
c["edges"] = edges
c["name"] = "蛋仔记单词 · 玩梗样片「morose＝没肉丝」v3 · 20s（锁眼＋T_A 接尾帧）"
s0 = by[ids["S0"]]
s0["meta"]["y"] = 700.0
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》玩梗样片 v3：morose = 没肉丝 → 郁闷的。20s（2×10s）。
黄蛋毛绒版说话；心易水豚只发“咔啵”；视频无字，白字横排后期。
v3 解决两件事：① 心易眼睛锁 R02E；② V1→V2 用 T_A 接尾帧，不再割裂。

【跑序（必须按顺序）】
1. 先修 R02：心易水豚图要在你当前 Monet 账号可读；跨账号可能空。
2. 跑 R01P（黄蛋毛绒版）。
3. 跑 A05（餐盒，确认没有肉丝）。
4. 跑 K_A（首帧；眼睛按 R02E）。
5. 跑 V1（10s）；结尾黄蛋趴桌稳定 1 秒。
6. 截 V1 最后一帧；在 Monet 里替换 T_A 占位图（只换图，token 不变）。
7. 再跑 V2（10s，首帧＝T_A）；不要提前跑。
8. 后期加横排白字；不做气泡。

【锁眼口径】
- 心易眼睛：大圆形、白色/奶油眼白、外圈粗深棕描边、内部没有黑瞳孔/没有棕色虹膜；像布偶刺绣/纽扣眼。
- 不要：黑豆眼、棕色虹膜、写实瞳孔、动漫高光。
- R02E 是眼睛参考；K_A/V1/V2 都引用它。

【接尾帧口径】
- V1 最后一帧必须停在黄蛋趴桌的稳定姿势；V2 首帧就是 T_A。
- V2 不能换机位、不能重摆、不能换光；从 T_A 姿势抬头继续。
- T_A 没替换前，不要跑 V2。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# validate
ids_set = {n["id"] for n in nodes}
assert len(ids_set) == len(nodes)
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

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(edges)} edges / {len(groups)} groups")
print("->", OUT)






