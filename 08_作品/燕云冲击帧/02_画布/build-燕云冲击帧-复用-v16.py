# -*- coding: utf-8 -*-
"""燕云冲击帧 v16：复用你已生成的 14 个产物，不再重复生成

来源：你从 Monet 导出的 `燕云冲击帧 · 小动作近景（16_9）v14.monet`，里面这些节点已有输出：
  A0–A6（7 张资产）、K1–K3（起势）、E1–E3（尾帧）、V1（视频）
所以 v16 把它们的 **gen 节点换成 input 节点（直接挂已有 URL）**，下游连线不变：
  · 已生成 → 不再跑
  · V2/V3（你那边 failed）、I1–I3、W1–W3（还没跑）→ 保留生成节点

这样重跑只会花 5 次视频 + 3 张图，而不是 26 个节点。
"""
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OUT = HERE / "燕云冲击帧-复用-16x9-v16.monet"
DL = Path.home() / "Downloads" / OUT.name
MAN = json.loads((HERE / "已生成资产清单.json").read_text(encoding="utf-8"))
CREATED = "2026-10-30T16:40:00.000+08:00"
PREFIX = "ywsi"
BY = "linguanxi"


def load_mod(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


V15 = load_mod("yanwu_v15", "build-燕云冲击帧-发力-v15.py")
KEYS = ("P1", "P2", "S1", "A0", "A1", "A2", "A3", "A4", "A5", "A6",
        "K1", "K2", "K3", "E1", "E2", "E3", "V1", "V2", "V3",
        "I1", "I2", "I3", "W1", "W2", "W3", "S0")
ID = {k: "node-" + hashlib.md5((PREFIX + k).encode()).hexdigest()[:8] for k in KEYS}
RMAP = {V15.ID[k]: ID[k] for k in V15.ID}


def tok(k):
    return "{{" + ID[k] + "}}"


def rm(s):
    for old, new in RMAP.items():
        s = s.replace(old, new)
    return s


P_V2, P_V3 = rm(V15.P_V2), rm(V15.P_V3)
P_I1, P_I2, P_I3 = rm(V15.P_I1), rm(V15.P_I2), rm(V15.P_I3)
W_TPL = V15.W_TPL
S1, S0 = V15.S1, V15.S0

# 已生成产物：label 前缀 → key
KEY_BY_PREFIX = {"P1 原始": "P1", "P2 原始": "P2", "A0": "A0", "A1": "A1", "A2": "A2", "A3": "A3",
                 "A4": "A4", "A5": "A5", "A6": "A6", "K1": "K1", "K2": "K2", "K3": "K3",
                 "E1": "E1", "E2": "E2", "E3": "E3", "V1": "V1"}
FOUND = {}
for label, v in MAN.items():
    core = label.split("】")[-1]
    for pref, key in KEY_BY_PREFIX.items():
        if core.strip().startswith(pref):
            FOUND[key] = v
            break
print("复用:", sorted(FOUND))


def image_up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.png", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5")}


def video_up(key):
    v = FOUND[key]
    res = v.get("resolution") or {"width": 1280, "height": 720}
    md = v.get("metadata") or {}
    return {"name": f"{key}.mp4", "url": v["url"],
            "width": res.get("width", 1280), "height": res.get("height", 720),
            "size": md.get("size"), "md5": md.get("md5"), "cover": v.get("cover")}


def input_video(n, x, y, label, up, w=320, h=210):
    out = {
        "id": f"output-{n[5:13]}", "status": "done", "error": None,
        "value": up["url"], "cover": up.get("cover"), "name": up["name"],
        "resolution": {"width": up["width"], "height": up["height"]},
        "source": None, "batchId": None, "execution": None, "graphRunId": None,
        "iterationPath": None, "taskSource": None, "taskId": None,
        "executorRunId": None, "stage": None, "deletedAt": None,
        "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        "metadata": {"size": up.get("size"), "md5": up.get("md5")},
    }
    node = V15.V14.V10._base(n, "input-video", x, y, w, h, label)
    node["mainOutputId"] = out["id"]
    node["outputs"] = [out]
    return node


def main():
    F = V15.V14.V10
    gi, ii, it = F.gen_image, F.input_image, F.input_text
    nodes = [
        ii(ID["P1"], 20, 20, "【已生成·复用】P1 原始人物", image_up("P1")),
        ii(ID["P2"], 20, 240, "【已生成·复用】P2 原始武器", image_up("P2")),
        it(ID["S1"], 20, 470, 320, 470, "S1 角色与武器设定", S1),

        ii(ID["A0"], 420, 20, "【已生成·复用】A0 设定母版", image_up("A0")),
        ii(ID["A1"], 820, 20, "【已生成·复用】A1 脸部特写", image_up("A1")),
        ii(ID["A2"], 820, 340, "【已生成·复用】A2 正面全身（锚）", image_up("A2")),
        ii(ID["A5"], 820, 660, "【已生成·复用】A5 武器白底", image_up("A5")),
        ii(ID["A3"], 1220, 20, "【已生成·复用】A3 侧面", image_up("A3")),
        ii(ID["A4"], 1220, 340, "【已生成·复用】A4 背面", image_up("A4")),
        ii(ID["A6"], 1220, 660, "【已生成·复用】A6 握剑手", image_up("A6")),

        ii(ID["K1"], 1620, 20, "【已生成·复用】K1 ① 起势 · 剑收右腰", image_up("K1")),
        ii(ID["K2"], 1620, 340, "【已生成·复用】K2 ② 起势 · 剑举右肩后", image_up("K2")),
        ii(ID["K3"], 1620, 660, "【已生成·复用】K3 ③ 起势 · 剑尖垂右下", image_up("K3")),

        ii(ID["E1"], 2020, 20, "【已生成·复用】E1 ① 到位 · 刺出", image_up("E1")),
        ii(ID["E2"], 2020, 340, "【已生成·复用】E2 ② 到位 · 腰甩横贯", image_up("E2")),
        ii(ID["E3"], 2020, 660, "【已生成·复用】E3 ③ 到位 · 上挑", image_up("E3")),
    ]

    def vid(n, x, y, label, prompt, refs, first, last):
        return {
            "id": n, "type": "gen-video", "mainOutputId": None,
            "meta": {"x": x, "y": y, "width": 320, "height": 280, "label": label, "resourceType": None},
            "outputs": [],
            "params": {"num": 1, "model_id": "seedance-2.5", "model_params": {
                "_task_mode": "standard", "prompt": prompt, "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in refs],
                "reference_videos": [], "reference_audios": [],
                "first_frame_image": {"node_id": first},
                "last_frame_image": {"node_id": last} if last else None,
                "aspect_ratio": "16:9", "resolution": "720p", "duration": 5,
                "generate_audio": True, "seed": -1}},
            "specialParams": None, "config": None,
            "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY,
        }

    nodes += [
        input_video(ID["V1"], 2420, 20, "【已生成·复用】V1 ① 刺（成品）", video_up("V1")),
        vid(ID["V2"], 2420, 340, "【待生成·需重跑】V2 ② 斩", P_V2,
            [ID["A2"], ID["A5"], ID["E2"]], ID["K2"], ID["E2"]),
        vid(ID["V3"], 2420, 660, "【待生成·需重跑】V3 ③ 撩", P_V3,
            [ID["A2"], ID["A5"], ID["E3"]], ID["K3"], ID["E3"]),
        gi(ID["I1"], 2820, 20, "【待生成】I1 ① 冲击帧 · 向心放射", P_I1,
           [ID["E1"], ID["A2"], ID["A5"]]),
        gi(ID["I2"], 2820, 340, "【待生成】I2 ② 冲击帧 · 横向墨痕", P_I2,
           [ID["E2"], ID["A2"], ID["A5"]]),
        gi(ID["I3"], 2820, 660, "【待生成】I3 ③ 冲击帧 · 斜向墨痕", P_I3,
           [ID["E3"], ID["A2"], ID["A5"]]),
        vid(ID["W1"], 3220, 20, "【待生成】W1 ① 墨动 4s", W_TPL.format(img=tok("I1")), [ID["I1"]], ID["I1"], None),
        vid(ID["W2"], 3220, 340, "【待生成】W2 ② 墨动 4s", W_TPL.format(img=tok("I2")), [ID["I2"]], ID["I2"], None),
        vid(ID["W3"], 3220, 660, "【待生成】W3 ③ 墨动 4s", W_TPL.format(img=tok("I3")), [ID["I3"]], ID["I3"], None),
        it(ID["S0"], 420, 1050, 1520, 470, "S0 复用版说明 · 先读", S0),
    ]

    pairs = [
        (ID["A2"], ID["V2"]), (ID["A5"], ID["V2"]), (ID["K2"], ID["V2"]), (ID["E2"], ID["V2"]),
        (ID["A2"], ID["V3"]), (ID["A5"], ID["V3"]), (ID["K3"], ID["V3"]), (ID["E3"], ID["V3"]),
        (ID["E1"], ID["I1"]), (ID["A2"], ID["I1"]), (ID["A5"], ID["I1"]),
        (ID["E2"], ID["I2"]), (ID["A2"], ID["I2"]), (ID["A5"], ID["I2"]),
        (ID["E3"], ID["I3"]), (ID["A2"], ID["I3"]), (ID["A5"], ID["I3"]),
        (ID["I1"], ID["W1"]), (ID["I2"], ID["W2"]), (ID["I3"], ID["W3"]),
    ]

    by_id = {n["id"]: n for n in nodes}

    def bf(ids):
        xs = [by_id[x]["meta"]["x"] for x in ids]
        ys = [by_id[x]["meta"]["y"] for x in ids]
        xe = [by_id[x]["meta"]["x"] + by_id[x]["meta"]["width"] for x in ids]
        ye = [by_id[x]["meta"]["y"] + by_id[x]["meta"]["height"] for x in ids]
        return {"x": min(xs) - 18, "y": min(ys) - 46,
                "width": max(xe) - min(xs) + 36, "height": max(ye) - min(ys) + 46 + 22}

    groups = [
        ("00 素材（复用）", ["P1", "P2", "S1"], "#8E8DE0"),
        ("01 资产（已生成，直接复用）", ["A0", "A1", "A2", "A5"], "#5B8DE0"),
        ("02 资产派生（已生成）", ["A3", "A4", "A6"], "#5BE0C8"),
        ("03 起势 K（已生成）", ["K1", "K2", "K3"], "#5B8DE0"),
        ("04 到位 E（已生成）", ["E1", "E2", "E3"], "#E05B8D"),
        ("05 招式：V1 复用 / V2·V3 待重跑", ["V1", "V2", "V3"], "#E0A15B"),
        ("06 冲击帧 I（待生成）", ["I1", "I2", "I3"], "#5BE0C8"),
        ("07 墨动 W（待生成）", ["W1", "W2", "W3"], "#C8A15B"),
        ("08 说明", ["S0"], "#888888"),
    ]
    gl = []
    for k, (label, keys, color) in enumerate(groups):
        ids = [ID[x] for x in keys]
        gl.append({"id": f"g-ywsi-{k}", "nodeIds": ids, "bounds": bf(ids), "label": label,
                   "style": {"accent": None, "opacity": None, "borderColor": color},
                   "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY})

    doc = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": CREATED,
        "canvas": {
            "name": "燕云冲击帧 · 复用已生成（16:9）v16",
            "description": ("复用你已生成的 14 个产物（A0–A6、K1–K3、E1–E3、V1），已生成节点改为 input 直接挂 URL；"
                            "只剩 V2/V3 重跑 + I1–I3 出图 + W1–W3 墨动。"),
            "nodes": nodes,
            "edges": [{"id": "edge-" + hashlib.md5((str(k) + s + t).encode()).hexdigest()[:8],
                       "sourceNodeId": s, "sourceHandle": "output", "targetNodeId": t, "targetHandle": "input",
                       "createdAt": CREATED, "createdBy": BY, "updatedAt": CREATED, "updatedBy": BY}
                      for k, (s, t) in enumerate(pairs)],
            "groups": gl,
        },
    }

    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(OUT, DL)
    print("写出:", OUT)
    print("副本:", DL)
    print(f"节点 {len(nodes)} / 边 {len(pairs)} / 组 {len(gl)}")
    print("待生成:", [n["meta"]["label"] for n in nodes if n["type"].startswith("gen")])


if __name__ == "__main__":
    main()
