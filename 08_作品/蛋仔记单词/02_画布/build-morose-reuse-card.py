# -*- coding: utf-8 -*-
"""Reuse the user's generated morose v3 assets and add the single-card tail.

- Keeps R01P, A05, K_A, V1, V2, T_A outputs exactly as generated.
- Removes the two duplicate helper images (image.png / 尾帧_...).
- Adds KC single-card tail (post still) and notes.
- Does NOT regenerate V1/V2.

Output: 02_画布/EP01-morose-meme-v3-reuse-card.monet
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
SRC = Path(r"C:\Users\N31738\Downloads\蛋仔记单词 · 玩梗样片「morose＝没肉丝」v3 · 20s（锁眼＋T_A 接尾帧）.monet")
OUT = HERE / "EP01-morose-meme-v3-reuse-card.monet"
CARD = json.loads((ROOT / "01_资产" / "道具" / "morose-card-upload.json").read_text(encoding="utf-8"))

d = json.loads(SRC.read_text(encoding="utf-8-sig"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


# remove duplicate helpers not used by groups/edges
bad = [n["id"] for n in nodes if n["meta"].get("label", "") in ("image.png",) or n["meta"].get("label", "").startswith("尾帧_")]
nodes[:] = [n for n in nodes if n["id"] not in bad]
by = {n["id"]: n for n in nodes}
print("removed", len(bad))

ids = {}
for k, p in (("R00", "R00"), ("R01", "R01"), ("R02", "R02"), ("R02E", "R02E"),
             ("R01P", "R01P"), ("A02", "A02"), ("A05", "A05"),
             ("K_A", "K_A"), ("T_A", "T_A 占位"), ("V1", "V1"), ("V2", "V2"), ("S0", "S0")):
    ids[k] = find(p)["id"]
by[ids["V2"]]["meta"]["y"] = 300.0

# generated labels
for k in ("R01P", "A05", "K_A", "V1", "V2"):
    n = by[ids[k]]
    if n.get("outputs"):
        n["meta"]["label"] = n["meta"]["label"].replace("【待生成】", "【已生成】", 1)
# T_A keep its label (it has placeholder + real tail)

# add single-card tail
kc_id = "node-" + hashlib.md5(("morose-reuse-card:v1:KC").encode()).hexdigest()[:8]
kc = {
    "id": kc_id, "type": "input-image",
    "mainOutputId": "output-" + hashlib.md5(b"KC-card-reuse").hexdigest()[:10],
    "meta": {"x": 1160.0, "y": 640.0, "width": 300.0, "height": 169.0,
             "label": "KC 单卡尾 · morose / 没肉丝 → 郁闷的（后期用）", "resourceType": None},
    "outputs": [{
        "id": "output-" + hashlib.md5(b"KC-card-reuse").hexdigest()[:10],
        "status": "done", "error": None, "value": CARD["url"], "cover": None,
        "name": CARD["name"], "resolution": {"width": CARD["width"], "height": CARD["height"]},
        "source": None, "batchId": None, "execution": None, "graphRunId": None,
        "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
        "metadata": {"size": CARD["size"], "md5": CARD["md5"]},
    }],
    "params": None, "specialParams": None, "config": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
}
ids["KC"] = kc_id
nodes.append(kc)
by[kc_id] = kc

# groups: existing 6 + tail/notes
def group(key, label, keys, color, pad=20):
    ns = [by[ids[k]] for k in keys]
    x0 = min(n["meta"]["x"] for n in ns) - pad
    y0 = min(n["meta"]["y"] for n in ns) - pad
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in ns) + pad
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in ns) + pad
    return {"id": "group-" + hashlib.md5(("morose-reuse-card:v1:group:" + key).encode()).hexdigest()[:8],
            "nodeIds": [ids[k] for k in keys],
            "bounds": {"x": float(x0), "y": float(y0), "width": float(x1 - x0), "height": float(y1 - y0)},
            "label": label, "style": {"accent": None, "opacity": None, "borderColor": color},
            "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR}

groups = [
    group("g00", "00 参考素材 · 黄蛋/水豚/眼睛", ["R00", "R01", "R02", "R02E"], "#E68BB3"),
    group("g01", "01 黄蛋毛绒版 · 已生成", ["R01P"], "#D8A657"),
    group("g02", "02 小院/餐盒 · 已生成", ["A02", "A05"], "#8E8DE0"),
    group("g03", "03 首帧/尾帧 · K_A、T_A · 已生成", ["K_A", "T_A"], "#E8B85D"),
    group("g04", "04 视频 V1 · 已生成", ["V1"], "#DC775D"),
    group("g05", "05 视频 V2 · 已生成", ["V2"], "#DC775D"),
    group("g06", "06 单卡尾/说明 · 后期", ["KC", "S0"], "#7FB07F"),
]
c["groups"] = groups

# edges exact
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
c["name"] = "蛋仔记单词 · morose v3 复用版＋单卡尾 · 已生成资产不重跑"

s0 = by[ids["S0"]]
s0["meta"]["x"] = 1160.0
s0["meta"]["y"] = 840.0
s0["outputs"][0]["value"] = """【本画布做什么】
基于用户已生成的 morose v3 复用：R01P / A05 / K_A / V1 / V2 / T_A 全部保留，不重生成。
只新增：KC 单卡尾（morose / 没肉丝 → 郁闷的），后期静帧 3s。

【现状】
- V1 10s、V2 10s 是 v3 版：V1 台词是“……肉丝呢？”，V2 黄蛋讲了“morose，郁闷的 / 没肉丝，所以郁闷”。
- 和 v6 标准（黄蛋只说“怎么没有肉丝”，解释全旁白）不完全一致。
- 先复用，不重跑；若要严格 v6，只需重配 V2 音频或重跑 V2，V1 可保留/后期补一句。
- 后期可把 V1 裁到 8s、V2 裁到 9s，再接单卡 3s＝20s；或保留 10＋10＋3＝23s。

【跑序】
- 不需要再跑 R01P/A05/K_A/V1/V2/T_A。
- 只用 KC 单卡尾：后期接在 V2 后 3s。
- 若要补旁白：在 V2 上压低/替换黄蛋解释，或重配 V2；不要和现有黄蛋声叠。

【注意】
- T_A 已是 V1 真尾帧；不要再替换。
- 单卡尾是后期静帧；不生成视频。
- 心易眼睛 R02E 已生成；若 K_A 眼不对，重跑 K_A（但会破坏复用）。
"""
s0["meta"]["label"] = "S0 制作说明 · 复用版先读"

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
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
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

