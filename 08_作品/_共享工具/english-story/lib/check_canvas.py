# -*- coding: utf-8 -*-
"""画布层 + prompt 层 + 资产层校验。

等价于作品区一直在用的 `检查画布接线.py`（9E/11W），并补上英语故事线的
内容门禁（角色锁、手、道具、状态、字幕、时长）。不依赖外部仓库路径。
"""
import re

from .model import CheckResult, card_range, screen_range, token

TOKEN_RE = re.compile(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}")
BAD_TOKEN_RE = re.compile(r"\{\{(?!node-)[^{}]{1,80}\}\}")
PLAIN_AT_RE = re.compile(r"@[^\s，。]{1,12}")
IMAGE_TYPES = {"input-image", "gen-image"}
VIDEO_TYPES = {"input-video", "gen-video"}


def _prompt(node):
    params = (node.get("params") or {}).get("model_params") or {}
    return params.get("prompt") or ""


def _refs(node):
    params = (node.get("params") or {}).get("model_params") or {}
    out = [r.get("node_id") for r in params.get("reference_images") or []]
    first = (params.get("first_frame_image") or {}).get("node_id")
    return out, first


def _label(node):
    return (node.get("meta") or {}).get("label") or node.get("id")


def check_canvas(canvas, story=None, profile=None):
    doc = canvas.get("canvas") if isinstance(canvas.get("canvas"), dict) else canvas
    nodes = doc.get("nodes") or []
    edges = doc.get("edges") or []
    groups = doc.get("groups") or []
    res = CheckResult(subject=f"canvas:{doc.get('name', '?')}")

    by_id = {}
    for node in nodes:
        nid = node.get("id")
        if nid in by_id:
            res.add("C01", f"节点 ID 重复：{nid}")
        by_id[nid] = node

    # ---- 边基础 ----
    seen = set()
    for edge in edges:
        src, dst = edge.get("sourceNodeId"), edge.get("targetNodeId")
        if src not in by_id or dst not in by_id:
            res.add("C02", f"边端点不存在：{src} → {dst}")
        if (src, dst) in seen:
            res.add("C08", f"重复边：{_label(by_id.get(src, {}))} → {_label(by_id.get(dst, {}))}")
        seen.add((src, dst))

    out_edges, in_edges = {}, {}
    for edge in edges:
        out_edges.setdefault(edge.get("sourceNodeId"), []).append(edge)
        in_edges.setdefault(edge.get("targetNodeId"), []).append(edge)

    # ---- 禁止边 ----
    for edge in edges:
        src, dst = by_id.get(edge.get("sourceNodeId")), by_id.get(edge.get("targetNodeId"))
        if not src or not dst:
            continue
        st, dt = src.get("type"), dst.get("type")
        if st in VIDEO_TYPES and dt in VIDEO_TYPES:
            res.add("C06", f"video→video 边：{_label(src)} → {_label(dst)}")
        if st in {"input-audio", "gen-audio"} and dt in VIDEO_TYPES:
            res.add("C06", f"audio→video 边：{_label(src)} → {_label(dst)}")
        if st in VIDEO_TYPES and "尾帧" in _label(dst):
            res.add("C06", f"视频→尾帧来源边：{_label(src)} → {_label(dst)}")

    # ---- 组 ----
    group_of = {}
    for group in groups:
        ids = group.get("nodeIds") or []
        for nid in ids:
            group_of[nid] = group.get("id")
        for nid in ids:
            if nid not in by_id:
                res.add("C07", f"组 {group.get('label')} 含不存在的节点 {nid}")
        label = group.get("label") or ""
        if not re.match(r"^(\d{2}|第\s*\d+\s*步)", label):
            res.add("C17", f"组名不是“00/01…”或“第 N 步”：{label}")
        bounds = group.get("bounds") or {}
        if bounds and ids:
            bx, by = float(bounds.get("x", 0)), float(bounds.get("y", 0))
            bw, bh = float(bounds.get("width", 0)), float(bounds.get("height", 0))
            for nid in ids:
                if nid not in by_id:
                    continue
                meta = by_id[nid]["meta"]
                if (meta["x"] < bx - 1 or meta["y"] < by - 1
                        or meta["x"] + meta["width"] > bx + bw + 1
                        or meta["y"] + meta["height"] > by + bh + 1):
                    res.add("C19", f"组 {label} 的框没盖住节点 {meta.get('label')}")
                    break
    for edge in edges:
        src, dst = edge.get("sourceNodeId"), edge.get("targetNodeId")
        if src in group_of and dst in group_of and group_of[src] == group_of[dst]:
            res.add("C07", f"组内有依赖边：{_label(by_id[src])} → {_label(by_id[dst])}")

    # 组框两两重叠（画布上框会叠在一起，跑序看不清）
    boxes = []
    for group in groups:
        b = group.get("bounds") or {}
        if b:
            boxes.append((group.get("label"), float(b.get("x", 0)), float(b.get("y", 0)),
                          float(b.get("width", 0)), float(b.get("height", 0))))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if (a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
                    and a[2] < b[2] + b[4] and b[2] < a[2] + a[4]):
                res.add("C19", f"分组 bounds 重叠：{a[0]} / {b[0]}")

    # ---- 引用双接入 ----
    for node in nodes:
        nid = node.get("id")
        prompt = _prompt(node)
        if not prompt:
            continue
        if BAD_TOKEN_RE.search(prompt):
            res.add("C03", f"{_label(node)}：有非 {{node-…}} 格式的引用残留")
        tokens = set(TOKEN_RE.findall(prompt))
        for ref in tokens:
            if ref not in by_id:
                res.add("C03", f"{_label(node)} 引用了不存在的节点 {ref}")
        refs, first = _refs(node)
        ref_set = set(refs) | ({first} if first else set())
        for ref in tokens - ref_set:
            res.add("C04", f"{_label(node)}：prompt 点名 {ref}，但没挂 reference_images/first_frame")
        for ref in ref_set - tokens - ({first} if first else set()):
            res.add("C13", f"{_label(node)}：挂了 {ref}，正文却没有 {{node-…}} 点名")
        if first:
            if "【首帧锁定】" not in prompt:
                res.add("C12", f"{_label(node)}：挂了首帧但正文没有【首帧锁定】")
            if first not in tokens:
                res.add("C12", f"{_label(node)}：首帧 {first} 没在正文点名")
        for ref in ref_set:
            if ref not in by_id:
                res.add("C04", f"{_label(node)}：挂的 {ref} 不存在")
                continue
            if not any(e.get("sourceNodeId") == ref and e.get("targetNodeId") == nid for e in edges):
                res.add("C04", f"{_label(node)}：{ref} 没有节点边")
            target = by_id[ref]
            if target.get("type") == "input-image":
                outs = target.get("outputs") or []
                if not outs or not (outs[0] or {}).get("value"):
                    res.add("C05", f"{_label(node)} 引用的 {_label(target)} 没有输出（空节点）")

    # ---- 节点自身 ----
    for node in nodes:
        nid = node.get("id")
        label = _label(node)
        prompt = _prompt(node)
        main = node.get("mainOutputId")
        out_ids = {o.get("id") for o in node.get("outputs") or []}
        if main and main not in out_ids:
            res.add("C16", f"{label}：mainOutputId 不命中 outputs（导入会丢节点）")
        if node.get("type") == "input-image":
            outs = node.get("outputs") or []
            url = (outs[0] or {}).get("value") if outs else None
            if not url:
                res.add("A04", f"{label}：input-image 没有 URL")
            elif not str(url).startswith(("http://", "https://")):
                res.add("C18", f"{label}：URL 不是 http(s)（base64/dataURI 会撑爆画布）")
        if not prompt:
            continue
        if len(prompt) > 2000:
            res.add("C09", f"{label}：prompt {len(prompt)} 字符，超过平台 2000 上限")
        elif len(prompt) > 1900:
            res.add("P08", f"{label}：prompt {len(prompt)} 字符，目标 ≤1900")
        if PLAIN_AT_RE.search(prompt):
            res.add("C15", f"{label}：出现纯文本 @ 引用（不算真引用，模型会忽略）")
        params = (node.get("params") or {}).get("model_params") or {}
        if params.get("reference_audios"):
            res.add("C10", f"{label}：挂了 reference_audios（平台会整批失败）")
        if node.get("type") == "gen-video":
            duration = params.get("duration")
            if not isinstance(duration, int) or not 3 <= duration <= 16:
                res.add("C11", f"{label}：duration={duration!r} 不是 3–16 整数")

        # ---- prompt 内容门禁 ----
        if node.get("type") == "gen-video":
            _check_video_prompt(res, node, label, prompt, story, profile)
        elif node.get("type") == "gen-image":
            _check_image_prompt(res, node, label, prompt, story)

    # ---- 分镜图闸门（2026-11-03）----
    if profile is not None and profile.get("storyboard"):
        boards = [n for n in nodes if n.get("type") == "gen-image" and "分镜" in _label(n)]
        if not boards:
            res.add("C20", "画布没有分镜图节点（0/5/10s 三格）：视频前没有闸门")
        for board in boards:
            prompt = _prompt(board)
            if "第一格" not in prompt:
                res.add("P14", f"{_label(board)}：没写“第一格”")
            if "站位" not in prompt:
                res.add("P14", f"{_label(board)}：没写站位")
            if story is not None:
                for prop in story.get("props") or []:
                    name = prop.get("name")
                    if name and name not in prompt:
                        res.add("P14", f"{_label(board)}：第一格缺道具“{name}”")

    # ---- 资产层 ----
    if story is not None:
        why = story.get("assets_why") or {}
        new_assets = [n for n in nodes if n.get("type") == "gen-image"
                      and not _label(n).startswith(("KC", "S0"))]
        if why and len(why) < len(new_assets):
            res.add("A03", f"新生成节点 {len(new_assets)} 个，assets_why 只解释 {len(why)} 个")
    for node in nodes:
        if node.get("type") == "gen-image" and "复用" in _label(node):
            res.add("A02", f"{_label(node)}：复用资产却建了 gen-image，应改 input-image")
    return res


def _negative_part(prompt):
    if "【负向】" not in prompt:
        return ""
    return prompt.split("【负向】", 1)[1]


def _check_video_prompt(res, node, label, prompt, story, profile):
    # P01 心易锁眼
    if "白色圆形眼片" not in prompt or "没有黑色瞳孔" not in prompt:
        res.add("P01", f"{label}：缺心易锁眼正向句（白圆眼片/中心无瞳孔）")
    if "不眨眼" not in prompt:
        res.add("P01", f"{label}：没写心易不眨眼")
    # P02 负向泛化
    neg = _negative_part(prompt)
    for match in re.finditer("瞳孔", neg):
        window = neg[max(0, match.start() - 6):match.start()]
        if "心易的" not in window:
            res.add("P02", f"{label}：负向出现泛化的“瞳孔”，会误伤黄蛋（只写“心易的瞳孔”）")
            break
    # P03 手
    if "两只短手" not in prompt:
        res.add("P03", f"{label}：没写“只有两只短手”")
    for word in ("多余手臂", "第三只手", "多双手"):
        if word not in neg:
            res.add("P03", f"{label}：负向缺“{word}”")
            break
    # P04 首帧
    if "【首帧锁定】" not in prompt:
        res.add("P04", f"{label}：没有【首帧锁定】行")
    # P05 道具
    if story is not None:
        for prop in story.get("props") or []:
            name = prop.get("name")
            if name and name not in prompt:
                res.add("P05", f"{label}：道具“{name}”没在 prompt 里出现（首帧可能缺道具）")
    # P06 状态承接
    if story is not None:
        state = (story.get("continuity") or {}).get("scene_state") or []
        if state:
            for verb in ("生火", "点火", "开灯", "放水", "倒水"):
                if verb in prompt:
                    res.add("P06", f"{label}：场景状态已存在，prompt 却写“{verb}”")
                    break
    # P07 不生成文字（卡内嵌时按“除卡尾静帧外”的限定写法验收）
    card_in_video = bool(story is not None and (story.get("card") or {}).get("in_video"))
    if card_in_video:
        if "不出现任何文字" not in prompt or "卡尾段" not in prompt or "不增不减" not in prompt:
            res.add("P07", f"{label}：卡内嵌模式，负向必须写“除卡尾静帧外不出现任何文字＋卡尾段文字只按卡面呈现”")
    elif "不生成任何文字" not in prompt and "视频内文字" not in neg:
        res.add("P07", f"{label}：负向没写不生成文字/字幕/气泡")
    # P09 时长（卡内嵌时含卡尾，取 profile.total）
    if profile is not None:
        _, screen_end = screen_range(profile)
        want = int(round((profile.get("total") or screen_end) if card_in_video else screen_end))
        duration = ((node.get("params") or {}).get("model_params") or {}).get("duration")
        if duration != want:
            res.add("P09", f"{label}：duration={duration}，本档应为 {want}s" + ("（含卡尾）" if card_in_video else ""))
    # P10 咔啵括号
    if "咔啵（" in prompt or "咔啵(" in prompt:
        res.add("P10", f"{label}：prompt 里出现“咔啵（”，模型会把括号里的字念出来")
    # P11 旁白
    if profile is not None and profile.get("narration"):
        if "画外旁白" not in prompt or "不是黄蛋/心易" not in prompt:
            res.add("P11", f"{label}：旁白声线没声明（独立声线、不是黄蛋/心易）")


def _check_image_prompt(res, node, label, prompt, story):
    if story is not None and "道具" in label:
        word = (story.get("word") or {})
        for value in (word.get("spelling"), word.get("zh")):
            if value and value in prompt:
                res.add("P13", f"{label}：道具图 prompt 出现“{value}”，模型会把字烧进白底图")
                break
