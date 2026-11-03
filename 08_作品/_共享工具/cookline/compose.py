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


def _area(recipe: dict, key: str) -> dict:
    for a in recipe.get("areas", []):
        if a["key"] == key:
            return a
    return {"key": key, "name": key, "desc": "", "layout": "", "props_here": []}


def _is_stove(area: dict) -> bool:
    text = f"{area.get('key', '')}{area.get('name', '')}"
    return any(w in text for w in ("灶", "stove", "kitchen", "厨"))


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


def _rhythm(seconds: int, beats: list[dict]) -> str:
    n = len(beats)
    if beats and beats[-1]["kind"] == "breathe":
        return (f"【节奏】本段 {seconds} 秒 {n} 个镜头：前 {n - 1} 个做动作，做完停一下再切；"
                "最后一个是空镜，不推进剧情，只让火、蒸汽、光或静物自己动。"
                "不加速、不炫技运镜，镜头基本不动。")
    return (f"【节奏】本段 {seconds} 秒 {n} 个镜头，都是动作；一拍一件事，做完停一下再切。"
            "不加速、不炫技运镜，镜头基本不动。")


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
                "画面要唯美：浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；木头、陶土、竹子、苔藓的材质要能分辨。\n"
                "画面干净，只有必须的东西：没有现代电器、没有不锈钢、没有塑料收纳盒、没有杂物堆。\n"
                f"{token_line}无文字、无 logo、无水印。\n" + rules.negative_img()
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
                "正面微侧、居中构图、完整入画，柔和顶光，物品下方有自然的接触阴影；真实自然材质，不塑料、不卡通。\n"
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
        stove_neg = rules.NEG_STOVE if _is_stove(area) else ""
        near = any(w in f"{b.get('start', '')}{b.get('do', '')}{b.get('end', '')}" for b in seg["beats"] for w in ("近景", "特写"))
        neg_extra = "、".join(x for x in (stove_neg, "拆景" if near else "", char_neg) if x)

        gid = f"node-g{si + 1}"
        kid = f"node-k{si + 1}"
        vid = f"node-v{si + 1}"
        grid_nodes.append(gid)
        key_nodes.append(kid)

        cells = [0.0, 5.0, 10.0, 15.0][: int(fmt.get("grid_cells", 3))]
        cell_lines = "\n".join(
            f"第 {j + 1} 格（{int(t)} 秒）：{_cell_text(seg, t)}" for j, t in enumerate(cells)
        )
        first_props = ", ".join(seg["beats"][0].get("props") or []) or "全部道具"
        grid_refs = [ref_nodes[i] for i in sorted(ref_nodes)] + [scene_nodes[seg["area"]]] + mate_nodes
        grid_tokens = f"{char_tokens}；{{{{{scene_nodes[seg['area']]}}}}}=该角落的环境与光线；"
        if mate_tokens:
            grid_tokens += mate_tokens
        images.append(ImageArtifact(
            id=gid, label=f"【待生成】G{si + 1} 第 {si + 1} 段分镜 · {seg['title']}",
            prompt=(
                f"16:9 分镜设计图，一行 {len(cells)} 格，格与格之间有细白分隔线，格内不写字、不加标注。\n"
                "第 1 格是本段开场，必须出现本段会用到的全部道具和它的站位；后两格是动作落点。\n"
                f"本段道具：{first_props}。\n"
                f"{scale}。{tone.rstrip('。')}。\n"
                f"场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}\n"
                f"因果律：{rules.CAUSAL}。用量：{rules.QUANTITY}。手：{hand_rule}。场记：{rules.CONTINUITY}。{rules.TOOL_RULE}。\n"
                f"{cell_lines}\n"
                "格子里只出现这一只角色，不出现人类、不出现文字与标识。\n"
                f"参考图：{grid_tokens}\n{mate_line}\n角色：{char_line}\n"
                + rules.negative_img(neg_extra)
            ),
            refs=grid_refs, kind="grid", seg=si, area=seg["area"], width=460, height=300,
        ))

        # 白底道具只接进本段 K 帧：首拍 props/hand 里出现、且建了白底节点的，≤4 件；不接视频、不接分镜。
        b0 = seg["beats"][0]
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
                f"{scale}。{tone.rstrip('。')}。\n场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}\n"
                f"因果律：{rules.CAUSAL}。用量：{rules.QUANTITY}。手：{hand_rule}。场记：{rules.CONTINUITY}。{rules.TOOL_RULE}。\n"
                "浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；不出现人类、不出现第二只角色、不出现文字。\n"
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
                shot_lines.append(f"{b['t']} 秒：{b['start']}｜{b['do']}｜{b['end']}")
        sound = seg.get("sound", "").rstrip("。；; ")
        tail = []
        if "没有音乐" not in sound:
            tail.append("没有音乐")
        if "没有台词" not in sound:
            tail.append("没有台词")
        sound_line = sound + ("；" + "、".join(tail) if tail else "") + "。"
        blocks = {
            "首帧": f"【首帧锁定】首帧使用 {{{{{kid}}}}}：第 0 秒就是这一帧，锁角色位置、朝向、光线与道具状态。",
            "分镜": f"【分镜表】{{{{{gid}}}}} 是本段分镜，一格一个镜头；只参考构图与顺序，不要出现分格边框。",
            "角色": f"【角色】{char_line}",
            "尺度": f"{scale}。{tone.rstrip('。')}。",
            "场景": f"场景：{area['desc']}\n{area.get('layout', '')}\n{_props_line(area)}",
            "因果": f"【因果】{rules.CAUSAL}。",
            "用量": f"【用量】{rules.QUANTITY}。",
            "手": f"【手】{hand_rule}。",
            "工具": f"【工具】{rules.TOOL_RULE}。",
            "场记": f"【场记】{rules.CONTINUITY}。",
            "节奏": _rhythm(int(fmt["segment_seconds"]), seg["beats"]),
            "镜头": "【镜头】\n" + "\n".join(shot_lines),
            "声音": f"【声音】{sound_line}",
            "字幕": "【字幕】字幕只在后期贴，画面里不出现任何文字；不生成任何字幕。",
            "引用": f"【图片引用】{{{{{kid}}}}}=首帧；{{{{{gid}}}}}=分镜表；{char_tokens}；{mate_tokens}",
            "参考模式": "【参考模式】全部走全能参考，不挂首尾帧槽；不要用上一段的整帧当参考。",
            "负向": rules.negative_vid(neg_extra),
        }
        prompt = "\n".join(blocks.values())
        vrefs = [kid, gid] + [ref_nodes[i] for i in sorted(ref_nodes)] + mate_nodes
        videos.append(VideoArtifact(
            id=vid, label=f"【待生成】V{si + 1} {seg['title']} · {seg['range']} · {int(fmt['segment_seconds'])}s",
            prompt=prompt, refs=vrefs, seg=si, duration=int(fmt["segment_seconds"]), blocks=blocks,
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
    total = int(fmt["segment_seconds"]) * len(segs)
    beats_note = (
        f"每段 {fmt['beats'] - 1} 个动作拍 + 1 个呼吸拍"
        if str(fmt.get("style")) == "16"
        else f"每段 {fmt['beats']} 个动作拍（12 拍慢档，无空镜）"
    )
    corners_note = (
        "【为什么是四个角落】原片从不在一个房间里做完一顿饭：取料在外、处理在桌、火在灶、分享在窝。\n"
        "镜头在角落之间跳，但雾气、苔藓、木纹、色温始终一致，所以还是同一个世界。\n\n"
        if len(recipe.get("areas") or []) >= 4
        else "【台地】镜头在台地之间跳，但雾气、木纹、色温始终一致，所以还是同一个世界。\n\n"
    )
    s0 = (
        f"【本画布】《{recipe.get('series', '')}》{recipe.get('ep', '')}《{recipe['dish']}》："
        f"{fmt['aspect']}、{total} 秒＝{len(segs)} 段 × {fmt['segment_seconds']} 秒。\n"
        f"格式：秃秃（小蘑菇）式七段——取 / 理 / 配 / 火 / 揭 / 分；{beats_note}。\n"
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
        "2. 四段是否同一个世界（雾、光向、木纹、色温）；\n"
        "3. 动作是不是「一拍一件事」，呼吸拍是否真空；\n"
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
