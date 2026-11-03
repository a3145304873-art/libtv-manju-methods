# -*- coding: utf-8 -*-
"""菜谱卡 + 提示词 → Monet .monet 画布；以及画布审计。"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import rules
from .checks import Report
from .compose import Plan

BY = "cookline"


def _h(text: str, n: int = 12) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def _output_id(node_id: str, value: str) -> str:
    return "output-" + _h(f"{node_id}|{value}", 10)


def _edge_id(src: str, dst: str) -> str:
    return "edge-" + _h(f"{src}>{dst}", 12)


def _meta(x: float, y: float, w: float, h: float, label: str) -> dict:
    return {"x": float(x), "y": float(y), "width": float(w), "height": float(h),
            "label": label, "resourceType": None}


def _input_image(art, ts: str) -> dict:
    oid = _output_id(art.id, art.url)
    return {
        "id": art.id, "type": "input-image", "mainOutputId": oid,
        "meta": _meta(art.x, art.y, art.width, art.height, art.label),
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": art.url, "cover": None,
            "name": art.name, "resolution": {"width": art.w, "height": art.h},
            "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None, "executorRunId": None,
            "stage": None, "deletedAt": None, "createdAt": ts, "createdBy": BY,
            "updatedAt": ts, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _gen_image(art, card: dict, ts: str) -> dict:
    fmt = card["format"]
    return {
        "id": art.id, "type": "gen-image", "mainOutputId": None,
        "meta": _meta(art.x, art.y, art.width, art.height, art.label),
        "outputs": [],
        "params": {"num": 1, "model_id": fmt.get("image_model", "gpt-image-2"),
                   "model_params": {
                       "prompt": art.prompt,
                       "reference_images": [{"node_id": r} for r in art.refs],
                       "aspect_ratio": "16:9", "image_size": "1K",
                       "width": 1024, "height": 576, "quality": "medium",
                       "output_format": "png", "moderation": "low", "auto_compress": True}},
        "specialParams": None, "config": None,
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _gen_video(art, card: dict, ts: str) -> dict:
    fmt = card["format"]
    ref_way = fmt.get("reference_way", "reference")
    first = None
    if ref_way == "frames":
        first = {"node_id": art.refs[0]} if art.refs else None
    return {
        "id": art.id, "type": "gen-video", "mainOutputId": None,
        "meta": _meta(art.x, art.y, art.width, art.height, art.label),
        "outputs": [],
        "params": {"num": 1, "model_id": fmt.get("video_model", "seedance-2.0-mini"),
                   "model_params": {
                       "prompt": art.prompt, "_reference_way": ref_way,
                       "reference_images": [{"node_id": r} for r in art.refs],
                       "reference_audios": [],
                       "first_frame_image": first,
                       "last_frame_image": None,
                       "resolution": fmt.get("resolution", "720p"),
                       "aspect_ratio": "16:9", "duration": art.duration,
                       "generate_audio": True, "watermark": False}},
        "specialParams": None, "config": None,
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _input_text(node_id: str, label: str, text: str, x: float, y: float, ts: str) -> dict:
    oid = _output_id(node_id, text)
    return {
        "id": node_id, "type": "input-text", "mainOutputId": oid,
        "meta": _meta(x, y, 340, 420, label),
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": text, "cover": None, "name": label,
            "resolution": None, "source": None, "batchId": None, "execution": None,
            "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _edge(src: str, dst: str, ts: str) -> dict:
    return {
        "id": _edge_id(src, dst), "sourceNodeId": src, "sourceHandle": "output",
        "targetNodeId": dst, "targetHandle": "input",
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _bounds(nodes: list[dict], pad_side: float = 24, pad_top: float = 44, pad_bottom: float = 24) -> dict:
    x0 = min(n["meta"]["x"] for n in nodes)
    y0 = min(n["meta"]["y"] for n in nodes)
    x1 = max(n["meta"]["x"] + n["meta"]["width"] for n in nodes)
    y1 = max(n["meta"]["y"] + n["meta"]["height"] for n in nodes)
    return {"x": x0 - pad_side, "y": y0 - pad_top,
            "width": (x1 - x0) + pad_side * 2, "height": (y1 - y0) + pad_top + pad_bottom}


def _group(label: str, nodes: list[dict], color: str, ts: str) -> dict:
    return {
        "id": "group-" + _h(label, 10), "nodeIds": [n["id"] for n in nodes],
        "bounds": _bounds(nodes), "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": ts, "createdBy": BY, "updatedAt": ts, "updatedBy": BY,
    }


def _layout(plan: Plan) -> None:
    """按跑序分列摆放：参考 / 台地 / 道具 / 分镜 / 首帧 / 视频 / 说明。"""
    refs = [i for i in plan.images if i.kind in ("char", "companion")]
    scenes = [i for i in plan.images if i.kind == "scene"]
    props = [i for i in plan.images if i.kind == "prop"]
    grids = [i for i in plan.images if i.kind == "grid"]
    keys = [i for i in plan.images if i.kind == "key"]

    y = 80
    for art in refs:
        art.x, art.y = 40, y
        y += art.height + 60
    refs_bottom = y

    y = 80
    for art in scenes:
        art.x, art.y = 500, y
        y += art.height + 44
    scenes_bottom = y

    y = scenes_bottom + 60
    for art in props:
        art.x, art.y = 500, y
        y += art.height + 36

    y = 80
    for art in grids:
        art.x, art.y = 1020, y
        y += art.height + 40

    y = 80
    for art in keys:
        art.x, art.y = 1540, y
        y += art.height + 40

    y = 80
    for art in plan.videos:
        art.x, art.y = 2040, y
        y += art.height + 40


def build(card: dict, plan: Plan, ts: str) -> dict:
    _layout(plan)
    fmt = card["format"]
    nodes: list[dict] = []
    edges: list[dict] = []

    for art in plan.images:
        if art.kind in ("char", "companion") and art.url:
            nodes.append(_input_image(art, ts))
        else:
            nodes.append(_gen_image(art, card, ts))
        for r in art.refs:
            edges.append(_edge(r, art.id, ts))

    for art in plan.videos:
        nodes.append(_gen_video(art, card, ts))
        for r in art.refs:
            edges.append(_edge(r, art.id, ts))

    note_nodes = []
    n_y = max((n["meta"]["y"] + n["meta"]["height"] for n in nodes if n["type"] != "gen-video"), default=80) + 80
    for nid, label, text in plan.notes:
        node = _input_text(nid, label, text, 40, n_y, ts)
        nodes.append(node)
        note_nodes.append(node)
        n_y += node["meta"]["height"] + 40

    by_id = {n["id"]: n for n in nodes}
    groups = []
    if [i for i in plan.images if i.kind in ("char", "companion")]:
        groups.append(_group("00 参考 · 角色与配角", [by_id[i.id] for i in plan.images if i.kind in ("char", "companion")], "#E68BB3", ts))
    if [i for i in plan.images if i.kind == "scene"]:
        groups.append(_group("01 场景 · 按台地出图 · 先跑", [by_id[i.id] for i in plan.images if i.kind == "scene"], "#8E8DE0", ts))
    if [i for i in plan.images if i.kind == "prop"]:
        groups.append(_group("02 道具白底 · 并行", [by_id[i.id] for i in plan.images if i.kind == "prop"], "#7FB07F", ts))
    if [i for i in plan.images if i.kind == "grid"]:
        groups.append(_group("03 分镜图 · 定稿后再往下", [by_id[i.id] for i in plan.images if i.kind == "grid"], "#E8B85D", ts))
    if [i for i in plan.images if i.kind == "key"]:
        groups.append(_group("04 段首帧", [by_id[i.id] for i in plan.images if i.kind == "key"], "#6FA8DC", ts))
    if plan.videos:
        groups.append(_group("05 视频段 · 先只跑 V1", [by_id[v.id] for v in plan.videos], "#DC775D", ts))
    if note_nodes:
        groups.append(_group("06 说明 · 先读", note_nodes, "#B0B0B0", ts))

    total = int(fmt["segment_seconds"]) * len(card.get("segments") or [])
    name = card.get("canvas_name") or (
        f"{card.get('series', '')} · {card.get('ep', '')} {card['dish']} · {fmt['aspect']} · "
        f"{len(card.get('segments') or [])}段×{fmt['segment_seconds']}s · 蘑菇格式"
    )
    description = card.get("description") or (
        f"{total}s＝{len(card.get('segments') or [])} 段×{fmt['segment_seconds']}s；七段式：取/理/配/火/揭/分；"
        "四台地；比例协调；"
        f"{fmt.get('video_model')} / {fmt.get('reference_way')}。由 cookline {rules.VERSION} 从菜谱卡生成；"
        "改卡重跑，不手改。"
    )
    return {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": ts,
        "canvas": {"name": name, "description": description,
                   "nodes": nodes, "edges": edges, "groups": groups},
    }


def prompt_digest(canvas: dict) -> str:
    parts = []
    for n in canvas.get("canvas", {}).get("nodes", []):
        mp = (n.get("params") or {}).get("model_params") or {}
        if mp.get("prompt"):
            parts.append(f"{n['id']}\t{mp['prompt']}")
    return hashlib.sha256("\n".join(sorted(parts)).encode("utf-8")).hexdigest()


def runlist(canvas: dict, card: dict) -> dict:
    stages = {"assets": [], "storyboard": [], "keys": [], "videos": []}
    for n in canvas["canvas"]["nodes"]:
        nid = n["id"]
        if n["type"] == "gen-image" and nid.startswith("node-s"):
            stages["assets"].append(nid)
        elif n["type"] == "gen-image" and nid.startswith("node-p"):
            stages["assets"].append(nid)
        elif n["type"] == "gen-image" and nid.startswith("node-g"):
            stages["storyboard"].append(nid)
        elif n["type"] == "gen-image" and nid.startswith("node-k"):
            stages["keys"].append(nid)
        elif n["type"] == "gen-video":
            stages["videos"].append(nid)
    return {
        "generator": f"cookline/{rules.VERSION}",
        "recipe_sha256": hashlib.sha256(
            json.dumps({k: v for k, v in card.items() if not str(k).startswith("_")},
                       ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "stages": stages,
    }


def sidecar(canvas: dict, card: dict, recipe_sha: str, built_at: str) -> dict:
    return {
        "generator": f"cookline/{rules.VERSION}",
        "built_at": built_at,
        "recipe_sha256": recipe_sha,
        "prompt_digest": prompt_digest(canvas),
        "canvas_sha256": hashlib.sha256(
            json.dumps(canvas, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
    }


def write(path: str | Path, canvas: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(canvas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------- 审计 ----------------

def audit(canvas: dict, card: dict | None = None, side: dict | None = None) -> Report:
    rep = Report()
    if not isinstance(canvas, dict) or canvas.get("type") != "monet.canvas":
        rep.add("F26", "画布", "不是 monet.canvas")
        return rep
    body = canvas.get("canvas") or {}
    nodes = body.get("nodes") or []
    edges = body.get("edges") or []
    groups = body.get("groups") or []
    by_id = {n.get("id"): n for n in nodes}
    if len(by_id) != len(nodes):
        rep.add("F26", "画布", "节点 ID 重复")

    for e in edges:
        if e.get("sourceNodeId") not in by_id or e.get("targetNodeId") not in by_id:
            rep.add("F26", "画布", f"悬空边 {e.get('id')}")

    for n in nodes:
        mp = (n.get("params") or {}).get("model_params") or {}
        prompt = mp.get("prompt") or ""
        if n["type"] == "gen-video" and (mp.get("_reference_way") or "reference") == "reference":
            if mp.get("first_frame_image") or mp.get("last_frame_image"):
                rep.add("F24", n["id"], "reference 模式还挂着首/尾帧槽")
        if n["type"] in ("gen-image", "gen-video") and not prompt:
            rep.add("F26", n["id"], "生成节点没有提示词")
        if prompt:
            if len(prompt) > 2000:
                rep.add("F22", n["id"], f"提示词 {len(prompt)} 字，超 2000")
            for w in ("多余手臂", "第三只手", "多双手", "人类的手", "五指", "指甲", "字幕"):
                if w not in prompt and n["type"] == "gen-video":
                    rep.add("F12" if w in ("多余手臂", "第三只手", "多双手") else ("F14" if w in ("人类的手", "五指", "指甲") else "F19"),
                            n["id"], f"负向缺「{w}」")
            if n["type"] == "gen-video" and "为它配好的小世界" not in prompt:
                rep.add("F16", n["id"], "视频提示词缺尺度常量")
            toks = set(re.findall(r"\{\{(node-[^\}]+)\}\}", prompt))
            srcs = {e["sourceNodeId"] for e in edges if e["targetNodeId"] == n["id"]}
            for t in toks:
                if t not in by_id:
                    rep.add("F26", n["id"], f"token {t} 没有节点")
                if t not in srcs:
                    rep.add("F26", n["id"], f"token {t} 没有连线")
            for r in [x["node_id"] for x in mp.get("reference_images") or []]:
                if r not in by_id:
                    rep.add("F26", n["id"], f"参考图 {r} 不存在")
                if r not in srcs:
                    rep.add("F26", n["id"], f"参考图 {r} 没连线")
            if n["type"] == "gen-video":
                own = re.search(r"node-v(\d+)", n["id"])
                idx = own.group(1) if own else ""
                for r in [x["node_id"] for x in mp.get("reference_images") or []]:
                    m = re.search(r"node-[kg](\d+)", r)
                    if m and idx and m.group(1) != idx:
                        rep.add("F23", n["id"], f"挂了第 {m.group(1)} 段的 K/分镜当参考，构图会打架")

    if card:
        total = int(card["format"]["segment_seconds"]) * len(card.get("segments") or [])
        for n in nodes:
            if n["type"] == "gen-video":
                d = ((n.get("params") or {}).get("model_params") or {}).get("duration")
                if int(d or 0) != int(card["format"]["segment_seconds"]):
                    rep.add("F24", n["id"], f"时长 {d}s 与卡里的 {card['format']['segment_seconds']}s 不一致")
        subs = [str(s.get("text") or "") for s in (card.get("post") or {}).get("subtitles") or []]
        for n in nodes:
            prompt = ((n.get("params") or {}).get("model_params") or {}).get("prompt") or ""
            for t in subs:
                if len(t) >= 3 and t in prompt:
                    rep.add("F19", n["id"], f"字幕「{t}」在提示词里")
        if total <= 0:
            rep.add("F01", "画布", "总时长为 0")

    for i, g in enumerate(groups):
        b = g.get("bounds") or {}
        if not all(k in b for k in ("x", "y", "width", "height")):
            rep.add("F26", g.get("label", "组"), "组没有 bounds")
            continue
        for j in range(i + 1, len(groups)):
            c = groups[j].get("bounds") or {}
            if b["x"] < c.get("x", 0) + c.get("width", 0) and c.get("x", 0) < b["x"] + b["width"] and \
               b["y"] < c.get("y", 0) + c.get("height", 0) and c.get("y", 0) < b["y"] + b["height"]:
                rep.add("F26", g.get("label", "组"), f"组重叠：{g.get('label')} ↔ {groups[j].get('label')}")
        for nid in g.get("nodeIds") or []:
            n = by_id.get(nid)
            if not n:
                rep.add("F26", g.get("label", "组"), f"组里引用了不存在的节点 {nid}")
                continue
            m = n["meta"]
            if not (b["x"] <= m["x"] and m["x"] + m["width"] <= b["x"] + b["width"] and
                    b["y"] <= m["y"] and m["y"] + m["height"] <= b["y"] + b["height"]):
                rep.add("F26", g.get("label", "组"), f"节点 {nid} 超出组")

    if side:
        if side.get("prompt_digest") and side["prompt_digest"] != prompt_digest(canvas):
            rep.add("F26", "画布", "prompt digest 不符：画布被手改过，或边车不是这一版")
        if side.get("recipe_sha256") and card:
            from .model import recipe_hash
            if side["recipe_sha256"] != recipe_hash(card):
                rep.add("F26", "画布", "卡改过但画布没重建；先 build，再签核")
    return rep
