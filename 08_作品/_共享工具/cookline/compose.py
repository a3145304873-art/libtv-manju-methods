# -*- coding: utf-8 -*-
"""菜谱卡 → 提示词、分镜、SRT 与画布节点。

所有提示词只从这里出；不允许在作品目录里手写一次性的提示词。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import rules


@dataclass
class ImageArtifact:
    id: str
    label: str
    prompt: str
    refs: list[str]
    kind: str
    width: int = 360
    height: int = 240
    seg: int = -1
    area: str = ""
    url: str = ""
    name: str = ""
    w: int = 0
    h: int = 0
    x: float = 0
    y: float = 0


@dataclass
class VideoArtifact:
    id: str
    label: str
    prompt: str
    refs: list[str]
    seg: int
    duration: int
    blocks: dict = field(default_factory=dict)
    width: int = 360
    height: int = 260
    x: float = 0
    y: float = 0


@dataclass
class Plan:
    recipe: dict
    images: list[ImageArtifact]
    videos: list[VideoArtifact]
    notes: list[tuple[str, str, str]]
    srt: str
    roles: dict


def _clean(text: str) -> str:
    t = str(text or "").strip()
    for prefix in ("起幅：", "起幅:", "落幅：", "落幅:", "空镜：", "空镜:"):
        if t.startswith(prefix):
            t = t[len(prefix):]
    return t.strip("。；; ")


def _beat_at(seg: dict, t: float) -> dict | None:
    for b in seg["beats"]:
        if b["start_sec"] - 1e-6 <= t < b["end_sec"] - 1e-6:
            return b
    return seg["beats"][-1] if seg["beats"] else None


def _cell_text(seg: dict, t: float) -> str:
    b = _beat_at(seg, t)
    if not b:
        return ""
    if b["kind"] == "breathe":
        return _clean(b.get("desc", ""))
    if abs(t - b["start_sec"]) < 0.05:
        return _clean(b.get("start", ""))
    return f"{_clean(b.get('do', ''))}；{_clean(b.get('end', ''))}"


def _frame_text(seg: dict, frame: dict) -> str:
    return frame.get("description") or _cell_text(seg, float(frame["at"]))


def _area(recipe: dict, key: str) -> dict:
    for a in recipe.get("areas", []):
        if a["key"] == key:
            return a
    return {"key": key, "name": key, "desc": "", "layout": "", "props_here": []}


def _companions(recipe: dict, seg: dict) -> list[dict]:
    by_key = {c["key"]: c for c in recipe.get("companions", [])}
    return [by_key[k] for k in seg.get("with", []) if k in by_key]


def _char_tokens(recipe: dict, ref_nodes: dict) -> str:
    refs = recipe["character"].get("refs", [])
    return "；".join(f"{{{{{ref_nodes[i]}}}}}={r['label']}" for i, r in enumerate(refs))


def _props_line(area: dict) -> str:
    items = area.get("props_here") or []
    if not items:
        return "本角落的器具：未声明；不要多出别的器具。"
    return f"本角落的器具：{'、'.join(items)}；只有这些，不要多出别的器具。"


def _constraint_text(*values) -> str:
    out = []
    for value in values:
        if isinstance(value, str):
            value = [value]
        for item in value or []:
            text = str(item).strip()
            if text and text not in out:
                out.append(text)
    return "、".join(out)


def _rhythm(seg: dict) -> str:
    custom = str(seg.get("rhythm") or "").strip()
    if custom:
        return f"【节奏】{custom}"
    return ("【节奏】时长按本段动作、等待和情绪变化安排，不平均分配；"
            "是否停顿、连续运动或切镜按逐拍设计执行，不额外添加统一节拍。")


def compose(recipe: dict) -> Plan:
    fmt = recipe["format"]
    ch = recipe["character"]
    areas = recipe.get("areas", [])
    segs = recipe.get("segments", [])
    props = recipe.get("props", [])
    images: list[ImageArtifact] = []
    videos: list[VideoArtifact] = []
    ref_nodes: dict[int, str] = {}

    # 00 角色与配角
    for i, ref in enumerate(ch.get("refs", [])):
        nid = f"node-a{i}"
        ref_nodes[i] = nid
        images.append(ImageArtifact(
            id=nid, label=f"A{i} {ch.get('name', '角色')}·{ref['label']}（已上传）",
            prompt="", refs=[], kind="char", url=ref["url"], name=f"{ch.get('name', '角色')}-{ref['label']}",
            w=ref["width"], h=ref["height"], width=300, height=360,
        ))
    comp_nodes: dict[str, str] = {}
    for i, c in enumerate(recipe.get("companions", [])):
        nid = f"node-c{i + 1}"
        comp_nodes[c["key"]] = nid
        if c.get("ref_url"):
            images.append(ImageArtifact(
                id=nid, label=f"C{i + 1} {c['label']}（已上传）", prompt="", refs=[],
                kind="companion", url=c["ref_url"], name=f"{c['key']}.png", w=1024, h=1024,
                width=300, height=300,
            ))
        else:
            images.append(ImageArtifact(
                id=nid, label=f"【待生成】C{i + 1} {c['label']} · 白底三视图",
                prompt=(f"纯白底角色三视图，只生成一只角色。{c.get('prompt') or c.get('desc', '')}\n"
                        "正面、侧面、背面，同一角色、同一比例、同一配色，完整入画；柔和顶光、真实投影，"
                        "造型圆润不写实。\n无文字、无 logo、无水印。\n" + rules.negative_img()),
                refs=[], kind="companion", width=300, height=240,
            ))

    char_tokens = _char_tokens(recipe, ref_nodes)
    scale = rules.scale(ch)
    tone = rules.tone(recipe)
    global_style = str(fmt.get("visual_style") or "").strip()
    cooking_quantity = rules.quantity(recipe)
    hand_rule = rules.hands(ch)
    char_line = rules.character_line(ch)
    char_neg = "、".join(str(x) for x in (ch.get("negatives") or []) if x)

    # 01 场景
    scene_nodes: dict[str, str] = {}
    scene_by_i: list[str] = []
    for i, a in enumerate(areas):
        nid = f"node-s{i + 1}"
        scene_nodes[a["key"]] = nid
        scene_by_i.append(nid)
        refs = list(ref_nodes.values())
        token_line = f"参考图：{char_tokens} 只用于确认它的身量比例，画面里不出现角色。\n" if refs else ""
        images.append(ImageArtifact(
            id=nid, label=f"【待生成】S{i + 1} 场景 · {a['name']} · 16:9 空景",
            prompt=(
                f"16:9 场景设定空景，不出现任何角色。{a['desc']}\n{_props_line(a)}\n"
                f"{scale}。{tone}。\n"
                f"画面风格：{a.get('visual_style') or global_style or tone}。按场景所需呈现食材、器具与环境材质，不自动添加薄雾、浮尘或湿润效果。\n"
                "画面干净，只有本台地与本段需要的东西，不额外堆放杂物。\n"
                f"{token_line}无文字、无 logo、无水印。\n"
                + rules.negative_img(_constraint_text(fmt.get("visual_negatives"), a.get("visual_negatives")))
            ),
            refs=refs, kind="scene", seg=i, area=a["key"], width=420, height=236,
        ))

    # 02 道具
    prop_nodes: list[str] = []
    prop_node_by_key: dict[str, str] = {}
    for i, p in enumerate(props):
        nid = f"node-p{i + 1}"
        prop_nodes.append(nid)
        prop_node_by_key[p["key"]] = nid
        images.append(ImageArtifact(
            id=nid, label=f"【待生成】P{i + 1} {p['label']} · 白底道具",
            prompt=(
                f"纯白底道具图，只出现一件物品，不出现角色、不出现手。{p['body']}。\n"
                "正面微侧、居中构图、完整入画，柔和顶光，物品下方有自然的接触阴影；材质和表面状态按本菜与场景设计。\n"
                "无文字、无 logo、无水印、无边框。\n" + rules.negative_img()
            ),
            refs=[], kind="prop", width=300, height=200,
        ))

    # 03/04/05 分镜、首帧、视频
    grid_nodes: list[str] = []
    key_nodes: list[str] = []
    for si, seg in enumerate(segs):
        area = _area(recipe, seg["area"])
        mates = _companions(recipe, seg)
        mate_nodes = [comp_nodes[m["key"]] for m in mates if m["key"] in comp_nodes]
        mate_line = ("【配角】" + "；".join(m["desc"].rstrip("。") for m in mates) + "。") if mates else ""
        mate_tokens = "".join(f"{{{{{comp_nodes[m['key']]}}}}}={m['label']}；" for m in mates if m["key"] in comp_nodes)
        near = any(w in f"{b.get('start', '')}{b.get('do', '')}{b.get('end', '')}" for b in seg["beats"] for w in ("近景", "特写"))
        style_neg = _constraint_text(fmt.get("visual_negatives"), area.get("visual_negatives"), seg.get("visual_negatives"))
        neg_extra = _constraint_text("拆景" if near else "", char_neg, style_neg)
        segment_design = "\n".join(x for x in (
            f"本段目的：{seg.get('purpose')}" if seg.get("purpose") else "",
            f"本段情绪：{seg.get('mood')}" if seg.get("mood") else "",
            f"本段段尾意图：{seg.get('ending_intent')}" if seg.get("ending_intent") else "",
        ) if x)
        segment_style = seg.get("visual_style") or area.get("visual_style") or global_style

        gid = f"node-g{si + 1}"
        kid = f"node-k{si + 1}"
        vid = f"node-v{si + 1}"
        grid_nodes.append(gid)
        key_nodes.append(kid)

        frames = seg["storyboard_frames"]
        cells = [float(frame["at"]) for frame in frames]
        cols = min(4, len(cells))
        rows = (len(cells) + cols - 1) // cols
        cell_lines = "\n".join(
            f"第 {j + 1} 格（{t:g} 秒）：{_frame_text(seg, frame)}"
            for j, (t, frame) in enumerate(zip(cells, frames))
        )
        first_beat = seg["beats"][0]
        first_prop_keys = list(dict.fromkeys(
            (first_beat.get("props") or []) + (first_beat.get("hand") or []) + (first_beat.get("enter") or [])
        ))
        first_props = ", ".join(first_prop_keys) or "按首拍场景清单呈现；后续物件只在可见拿入动作后出现"
        grid_refs = [ref_nodes[i] for i in sorted(ref_nodes)] + [scene_nodes[seg["area"]]] + mate_nodes
        grid_tokens = f"{char_tokens}；{{{{{scene_nodes[seg['area']]}}}}}=该角落的环境与光线；"
        if mate_tokens:
            grid_tokens += mate_tokens
        images.append(ImageArtifact(
            id=gid, label=f"【待生成】G{si + 1} 第 {si + 1} 段分镜 · {seg['title']}",
            prompt=(
                f"16:9 分镜设计图，{rows} 行 × {cols} 列，共 {len(cells)} 格，按顺序阅读；格与格之间有细白分隔线，格内不写字、不加标注。\n"
                "第 1 格是本段开场，呈现开场即在场的道具与角色站位；后续才使用的物件按分镜中可见的拿入动作出现。\n"
                f"本段道具：{first_props}。\n"
                f"{scale}。{tone.rstrip('。')}。画面风格：{segment_style or tone}\n{segment_design}\n"
                f"场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}\n"
                f"因果律：{rules.CAUSAL}。用量：{cooking_quantity}。手：{hand_rule}。场记：{rules.CONTINUITY}。{rules.TOOL_RULE}。\n"
                f"{cell_lines}\n"
                "格子里只出现这一只角色，不出现人类、不出现文字与标识。\n"
                f"参考图：{grid_tokens}\n{mate_line}\n角色：{char_line}\n"
                + rules.negative_img(neg_extra)
            ),
            refs=grid_refs, kind="grid", seg=si, area=seg["area"], width=460, height=300,
        ))

        # 白底道具只接进本段 K 帧：首拍 props/hand 里出现、且建了白底节点的，≤4 件；不接视频、不接分镜。
        b0 = first_beat
        k_prop_keys: list[str] = []
        for key in (b0.get("props") or []) + (b0.get("hand") or []) + (b0.get("enter") or []):
            if key in prop_node_by_key and key not in k_prop_keys:
                k_prop_keys.append(key)
        if len(k_prop_keys) > 4:
            k_prop_keys = k_prop_keys[:4]
        k_prop_ids = [prop_node_by_key[k] for k in k_prop_keys]
        k_prop_tokens = "".join(
            f"{{{{{prop_node_by_key[k]}}}}}={next(p['label'] for p in props if p['key'] == k)}；"
            for k in k_prop_keys
        )
        k_refs = [ref_nodes[i] for i in sorted(ref_nodes)] + [scene_nodes[seg["area"]], gid] + k_prop_ids + mate_nodes
        k_tokens = f"{char_tokens}；{{{{{scene_nodes[seg['area']]}}}}}=环境与光线；{{{{{gid}}}}}=第一格构图；"
        if k_prop_tokens:
            k_tokens += k_prop_tokens + "白底道具图只定外观，位置与状态按站位和首拍来；"
        if mate_tokens:
            k_tokens += mate_tokens
        images.append(ImageArtifact(
            id=kid, label=f"【关键帧】K{si + 1} 第 {si + 1} 段首帧 · {_clean(seg['beats'][0].get('start', ''))[:12]}",
            prompt=(
                f"16:9 横屏电影感画面。{_clean(seg['beats'][0].get('start', ''))}。\n角色：{char_line}\n"
                f"{scale}。{tone.rstrip('。')}。画面风格：{segment_style or tone}\n{segment_design}\n"
                f"场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}\n"
                f"因果律：{rules.CAUSAL}。用量：{cooking_quantity}。手：{hand_rule}。场记：{rules.CONTINUITY}。{rules.TOOL_RULE}。\n"
                "不出现人类、不出现第二只角色、不出现文字。\n"
                f"参考图：{k_tokens}\n{mate_line}\n"
                + rules.negative_img(neg_extra)
            ),
            refs=k_refs, kind="key", seg=si, area=seg["area"], width=400, height=270,
        ))

        # 视频：逐拍写全，但绝不写具体字幕字
        shot_lines = []
        for b in seg["beats"]:
            if b["kind"] == "breathe":
                shot_lines.append(f"{b['t']} 秒：空镜。{_clean(b.get('desc', ''))}")
            else:
                camera = f"【镜头】{b['camera']}｜" if b.get("camera") else ""
                shot_lines.append(f"{b['t']} 秒：{camera}{b['start']}｜{b['do']}｜{b['end']}")
        sound = seg.get("sound", "").rstrip("。；; ")
        tail = []
        if "没有音乐" not in sound:
            tail.append("没有音乐")
        if "没有台词" not in sound:
            tail.append("没有台词")
        sound_line = sound + ("；" + "、".join(tail) if tail else "") + "。"
        blocks = {
            "本段设计": "\n".join(x for x in (
                f"【本段目的】{seg.get('purpose')}" if seg.get("purpose") else "",
                f"【情绪方向】{seg.get('mood')}" if seg.get("mood") else "",
                f"【段尾意图】{seg.get('ending_intent')}" if seg.get("ending_intent") else "",
            ) if x),
            "首帧": f"【首帧锁定】首帧使用 {{{{{kid}}}}}：第 0 秒就是这一帧，锁角色位置、朝向、光线与道具状态。",
            "分镜": f"【分镜表】{{{{{gid}}}}} 是本段分镜，一格一个镜头；只参考构图与顺序，不要出现分格边框。",
            "角色": f"【角色】{char_line}",
            "尺度": f"{scale}。{tone.rstrip('。')}。画面风格：{segment_style or tone}",
            "场景": f"场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}",
            "因果": f"【因果】{rules.CAUSAL}。",
            "用量": f"【用量】{cooking_quantity}。",
            "手": f"【手】{hand_rule}。",
            "工具": f"【工具】{rules.TOOL_RULE}。",
            "场记": f"【场记】{rules.CONTINUITY}。",
            "节奏": _rhythm(seg),
            "镜头": f"【镜头】段落组织：{seg.get('camera', '按本段分镜和逐拍镜头要求执行')}。\n" + "\n".join(shot_lines),
            "声音": f"【声音】{sound_line}",
            "字幕": "【字幕】字幕只在后期贴，画面里不出现任何文字；不生成任何字幕。",
            "引用": f"【图片引用】{{{{{kid}}}}}=首帧；{{{{{gid}}}}}=分镜表；{char_tokens}；{mate_tokens}",
            "参考模式": "【参考模式】全部走全能参考，不挂首尾帧槽；不要用上一段的整帧当参考。",
            "负向": rules.negative_vid(neg_extra),
        }
        prompt = "\n".join(blocks.values())
        vrefs = [kid, gid] + [ref_nodes[i] for i in sorted(ref_nodes)] + mate_nodes
        videos.append(VideoArtifact(
            id=vid, label=f"【待生成】V{si + 1} {seg['title']} · {seg['range']} · {seg['duration_seconds']:g}s",
            prompt=prompt, refs=vrefs, seg=si, duration=int(round(seg["duration_seconds"])), blocks=blocks,
        ))

    srt = make_srt(recipe)
    notes = _notes(recipe, grid_nodes, key_nodes)
    return Plan(
        recipe=recipe, images=images, videos=videos, notes=notes, srt=srt,
        roles={"refs": ref_nodes, "companions": comp_nodes, "scenes": scene_nodes,
               "props": prop_nodes, "grids": grid_nodes, "keys": key_nodes},
    )


def _notes(recipe: dict, grids: list[str], keys: list[str]) -> list[tuple[str, str, str]]:
    fmt = recipe["format"]
    segs = recipe["segments"]
    total = float(recipe.get("_total_seconds", 0))
    segment_notes = "；".join(
        f"V{i + 1} {seg['title']} {seg['duration_seconds']:g}s/{len(seg['beats'])}拍/{len(seg['storyboard_frames'])}格"
        for i, seg in enumerate(segs)
    )
    corners_note = (
        "【场景组织】每个 area 是画布中的一个空间锚点；仅在本集需要换台地时切换，"
        "角色、道具、光线和环境状态按卡片保持连续。\n\n"
    )
    s0 = (
        f"【本画布】《{recipe.get('series', '')}》{recipe.get('ep', '')}《{recipe['dish']}》："
        f"{fmt['aspect']}、总长 {total:g} 秒，共 {len(segs)} 段；各段时长、动作拍和分镜格数按本菜规划。\n"
        f"逐段规格：{segment_notes}。\n"
        f"系列名：{recipe.get('series_title', '')}\n\n"
        "【跑序】01 场景 → 02 道具（并行）→ 03 分镜图 → 04 段首帧 → 05 视频段。\n"
        "分镜图没过闸门不跑关键帧；关键帧没过闸门不跑视频。\n"
        "闸门用 cookline gate 签核；卡一改，旧签核自动失效。\n\n"
        + corners_note +
        "【比例】这是一个为它配好的小世界：锅盆比它高，但工具都按它身量配，它抱得动、够得着。\n"
        "不要画成人类巨物，也不要画成模型俯视。\n\n"
        "【改法】改提示词改菜谱卡 JSON 后重跑 cookline build，不手改 .monet。"
    )
    q0 = (
        "【本片的拦截面】\n"
        "schema　F01 段拍结构 / F05 站位与器具 / F20 不说话\n"
        "compiler F12 多手 / F14 人手 / F16 比例 / F24 参考模式\n"
        "validator F02–F11、F13、F15、F17–F19、F21–F23、F27、F30\n"
        "gate　　F25 未过闸门 / F26 手改画布\n"
        "human　F28 跨集漂移 / F29 表演与治愈感\n\n"
        "【人必须看的】\n"
        "1. 分镜第一格是否包含本段全部道具与站位；\n"
        "2. 各段是否保持角色、场景与道具连续；\n"
        "3. 每拍动作、停顿和分镜帧是否符合本段节奏；\n"
        "4. 出片后按 rules/failures.json 逐条过，新翻车补进登记表。\n\n"
        "【已经交给代码的】时长、镜数、道具首帧、数量、手、字幕、参考图、提示词字数。"
    )
    return [
        ("node-s0readme", "S0 制作说明 · 先读", s0),
        ("node-q0check", "Q0 质检范围 · 人看什么", q0),
    ]


def _fmt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_srt(recipe: dict) -> str:
    subs = recipe.get("post", {}).get("subtitles") or []
    lines = []
    for i, s in enumerate(subs, 1):
        if not s.get("text"):
            continue
        lines += [str(i), f"{_fmt_time(s['start'])} --> {_fmt_time(s['end'])}", s["text"], ""]
    return "\n".join(lines)
