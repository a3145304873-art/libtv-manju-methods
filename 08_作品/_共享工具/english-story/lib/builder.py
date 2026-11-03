# -*- coding: utf-8 -*-
"""画布 builder：story.json → .monet。

id 用 md5(prefix + key)[:8]；换 prefix 等于换一条片子，节点 id 全变，
所以返修同步（monet_sync）必须沿用同一个 prefix。
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone

from . import prompts
from .model import card_range, load_assets, screen_range, token

TZ = timezone(timedelta(hours=8))
GROUP_STYLE = {"accent": None, "opacity": None, "borderColor": "#E68BB3"}


def _h(text, n=8):
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:n]


def nid(prefix, key):
    return "node-" + _h(f"{prefix}:{key}")


def oid(prefix, key):
    return "output-" + _h(f"{prefix}:{key}:out", 12)


def eid(prefix, src, dst):
    return "edge-" + _h(f"{prefix}:{src}>{dst}")


def gid(prefix, key):
    return "group-" + _h(f"{prefix}:{key}")


def now():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def _meta(x, y, w, h, label):
    return {"x": float(x), "y": float(y), "width": float(w), "height": float(h),
            "label": label, "resourceType": None}


def input_image(prefix, key, asset, label, x, y):
    out = {
        "id": oid(prefix, key),
        "status": "done",
        "error": None,
        "value": asset["url"],
        "cover": None,
        "name": asset.get("name") or f"{key}.png",
        "resolution": ({"width": asset["width"], "height": asset["height"]}
                       if asset.get("width") and asset.get("height") else None),
        "source": None,
        "batchId": None,
        "execution": None,
        "graphRunId": None,
        "iterationPath": None,
        "executorRunId": None,
        "stage": None,
        "deletedAt": None,
        "metadata": ({"size": asset["size"], "md5": asset["md5"]}
                     if asset.get("size") and asset.get("md5") else None),
    }
    return {
        "id": nid(prefix, key),
        "type": "input-image",
        "mainOutputId": out["id"],
        "meta": _meta(x, y, 300, 200, label),
        "outputs": [out],
        "params": None,
        "specialParams": None,
        "config": None,
    }


def gen_image(prefix, key, label, prompt, refs, x, y, w=300, h=200):
    return {
        "id": nid(prefix, key),
        "type": "gen-image",
        "mainOutputId": None,
        "meta": _meta(x, y, w, h, label),
        "outputs": [],
        "params": {
            "num": 1,
            "model_id": "gpt-image-2",
            "model_params": {
                "prompt": prompt,
                "reference_images": [{"node_id": r} for r in refs],
                "aspect_ratio": "16:9",
                "image_size": "1K",
                "width": 1024,
                "height": 1024,
                "quality": "medium",
                "output_format": "png",
                "moderation": "low",
                "auto_compress": True,
            },
        },
        "specialParams": None,
        "config": None,
    }


def gen_video(prefix, key, label, prompt, refs, first_frame, duration, video_cfg, x, y):
    return {
        "id": nid(prefix, key),
        "type": "gen-video",
        "mainOutputId": None,
        "meta": _meta(x, y, 340, 224, label),
        "outputs": [],
        "params": {
            "num": 1,
            "model_id": video_cfg.get("model_id", "seedance-2.0-mini"),
            "model_params": {
                "prompt": prompt,
                "_reference_way": "reference",
                "reference_images": [{"node_id": r} for r in refs],
                "reference_audios": [],
                "first_frame_image": {"node_id": first_frame} if first_frame else None,
                "resolution": video_cfg.get("resolution", "720p"),
                "aspect_ratio": video_cfg.get("aspect_ratio", "16:9"),
                "duration": int(duration),
                "generate_audio": bool(video_cfg.get("generate_audio", True)),
                "watermark": False,
            },
        },
        "specialParams": None,
        "config": None,
    }


def input_text(prefix, key, label, text, x, y):
    out_id = oid(prefix, key)
    return {
        "id": nid(prefix, key),
        "type": "input-text",
        "mainOutputId": out_id,
        "meta": _meta(x, y, 760, 540, label),
        "outputs": [{
            "id": out_id, "status": "done", "error": None, "value": text, "cover": None,
            "name": label, "resolution": None, "source": None, "batchId": None,
            "execution": None, "graphRunId": None, "iterationPath": None, "executorRunId": None,
            "stage": None, "deletedAt": None, "metadata": None,
        }],
        "params": None,
        "specialParams": None,
        "config": None,
    }


def _group(prefix, key, label, nodes):
    xs = [n["meta"]["x"] for n in nodes]
    ys = [n["meta"]["y"] for n in nodes]
    ws = [n["meta"]["width"] for n in nodes]
    hs = [n["meta"]["height"] for n in nodes]
    x, y = min(xs) - 20, min(ys) - 20
    w = max(a + b for a, b in zip(xs, ws)) - min(xs) + 40
    h = max(a + b for a, b in zip(ys, hs)) - min(ys) + 40
    return {
        "id": gid(prefix, key),
        "nodeIds": [n["id"] for n in nodes],
        "bounds": {"x": float(x), "y": float(y), "width": float(w), "height": float(h)},
        "label": label,
        "style": dict(GROUP_STYLE),
    }


def build_canvas(story, profile, prefix=None):
    """返回 (canvas_doc, info)。info 含 node_map / 各段时长 / prompt 长度。"""
    if profile.get("status") != "implemented":
        raise ValueError(f"profile {profile['id']} 还不是 implemented，只能 validate，不能 build")
    prefix = prefix or story["id"]
    assets = load_assets()
    missing = [k for k in ("R00", "R01P", "R02", "R02E") if k not in assets]
    if missing:
        raise ValueError(f"assets.json 缺基础角色资产：{missing}")
    scene_key = (story.get("scene") or {}).get("asset")
    if scene_key and scene_key not in assets:
        raise ValueError(f"assets.json 没有场景资产 {scene_key}")

    used = {k: nid(prefix, k) for k in
            ("R00", "R01P", "R02", "R02E", "A05", "G1", "K_A", "V1", "KC", "S0")}
    if scene_key:
        used[scene_key] = nid(prefix, scene_key)

    s_start, s_end = screen_range(profile)
    c_start, c_end = card_range(profile)
    card_in_video = bool((story.get("card") or {}).get("in_video"))
    duration = int(round(s_end - s_start))
    v_duration = int(round((profile.get("total") or s_end) if card_in_video else duration))

    nodes = []
    groups = []

    # 00 参考素材
    ref_nodes = [
        input_image(prefix, "R00", assets["R00"], "R00 四小只身高比例（复用）", 0, 0),
        input_image(prefix, "R01P", assets["R01P"], "【已生成】R01P 黄蛋毛绒版（复用）", 0, 260),
        input_image(prefix, "R02", assets["R02"], "R02 心易·水豚（复用）", 0, 520),
        input_image(prefix, "R02E", assets["R02E"], "R02E 心易眼睛参考（复用）", 0, 780),
    ]
    nodes += ref_nodes
    groups.append(_group(prefix, "refs", "00 参考素材 · 黄蛋/水豚/眼睛", ref_nodes))

    # 01 场景 / 道具
    asset_nodes = []
    if scene_key:
        asset_nodes.append(input_image(prefix, scene_key, assets[scene_key],
                                       f"{scene_key} 场景（复用）", 360, 0))
    prop_names = "/".join(p.get("name", "") for p in story.get("props") or [])
    asset_nodes.append(gen_image(
        prefix, "A05", f"【待生成】A05 道具图 · {prop_names}",
        prompts.a05_image_prompt(story), [], 360, 260))
    nodes += asset_nodes
    groups.append(_group(prefix, "assets", "01 场景/道具 · 场景复用＋道具图", asset_nodes))

    # 02 分镜图闸门（2026-11-03 起：先出 0/5/10s 三格，再跑视频）
    g_refs = [used["R01P"], used["R02"], used["R02E"], used["A05"]]
    if scene_key:
        g_refs.insert(0, used[scene_key])
    g_node = gen_image(prefix, "G1", "【待生成】G1 三格分镜 · 0/5/10s（先跑这张）",
                       prompts.storyboard_prompt(story, profile, used), g_refs, 720, 0)
    nodes.append(g_node)
    groups.append(_group(prefix, "board", "02 分镜图闸门 · G1（0/5/10s）", [g_node]))

    # 03 首帧
    k_refs = [used["R01P"], used["R02"], used["R02E"], used["A05"]]
    if scene_key:
        k_refs.insert(0, used[scene_key])
    k_node = gen_image(prefix, "K_A", "【待生成】K_A 首帧 · 石桌全景（道具全在）",
                       prompts.k_image_prompt(story, profile, used), k_refs, 720, 300)
    nodes.append(k_node)
    groups.append(_group(prefix, "first", "03 首帧 · K_A", [k_node]))

    # 04 视频
    v_refs = [used["R00"], used["R01P"], used["R02"], used["R02E"], used["A05"]]
    if scene_key:
        v_refs.insert(0, used[scene_key])
    if card_in_video:
        v_refs.append(used["KC"])
    v_label = f"【待生成】V1 · {v_duration}s · {len(story.get('beats') or [])} 拍" + ("＋卡尾" if card_in_video else "")
    v_node = gen_video(prefix, "V1", v_label,
                       prompts.video_prompt(story, profile, used), v_refs, used["K_A"],
                       v_duration, profile.get("video") or {}, 1080, 150)
    nodes.append(v_node)
    groups.append(_group(prefix, "video", f"04 视频 V1 · {v_duration}s" + ("＋卡尾" if card_in_video else ""), [v_node]))

    # 05 卡尾
    kc_label = f"【待生成】KC 单卡尾 · {story['card']['word']} / {story['card']['zh']} / {story['card']['meaning']}"
    if card_in_video:
        kc_label += "（V1 内嵌）"
    kc_node = gen_image(prefix, "KC", kc_label,
                        prompts.card_prompt(story), [], 1480, 150, 300, 200)
    nodes.append(kc_node)
    groups.append(_group(prefix, "card", "05 卡尾 · " + ("V1 内嵌" if card_in_video else "后期静帧"), [kc_node]))

    # 06 说明
    s0_node = input_text(prefix, "S0", "S0 制作说明 · 先读",
                         prompts.s0_text(story, profile, used), 720, 700)
    nodes.append(s0_node)
    groups.append(_group(prefix, "doc", "06 说明 · 先读", [s0_node]))

    # 边：从 reference_images / first_frame 派生，不手写两套
    edges, seen = [], set()
    for node in nodes:
        params = (node.get("params") or {}).get("model_params") or {}
        sources = [r["node_id"] for r in params.get("reference_images") or []]
        if params.get("first_frame_image"):
            sources.append(params["first_frame_image"]["node_id"])
        for src in sources:
            if (src, node["id"]) in seen:
                continue
            seen.add((src, node["id"]))
            edges.append({
                "id": eid(prefix, src, node["id"]),
                "sourceNodeId": src,
                "sourceHandle": "output",
                "targetNodeId": node["id"],
                "targetHandle": "input",
            })

    canvas = {
        "schemaVersion": 2,
        "type": "monet.canvas",
        "exportedAt": now(),
        "canvas": {
            "name": story.get("canvas_name") or f"蛋仔记单词 · {story['id']} · {story['word']['spelling']}",
            "description": prompts.s0_text(story, profile, used),
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
        },
    }
    info = {
        "prefix": prefix,
        "node_map": {n["meta"]["label"]: n["id"] for n in nodes},
        "node_ids": {k: v for k, v in used.items()},
        "duration": duration,
        "screen": [s_start, s_end],
        "card": [c_start, c_end],
        "prompt_lengths": {
            "A05": len(prompts.a05_image_prompt(story)),
            "G1": len(prompts.storyboard_prompt(story, profile, used)),
            "K_A": len(prompts.k_image_prompt(story, profile, used)),
            "V1": len(prompts.video_prompt(story, profile, used)),
            "KC": len(prompts.card_prompt(story)),
        },
        "token": token,
    }
    return canvas, info


def to_srt(subtitles):
    def ts(t):
        ms = int(round(float(t) * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    blocks = []
    for i, sub in enumerate(subtitles, 1):
        blocks.append(f"{i}\n{ts(sub['start'])} --> {ts(sub['end'])}\n{sub['text']}\n")
    return "\n".join(blocks)
