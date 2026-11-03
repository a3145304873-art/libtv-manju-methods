# -*- coding: utf-8 -*-
"""prompt 组装：所有会踩坑的写法只在这里出现一次。

原则：
- 角色锁、负向、手、字幕禁写，全都由函数拼，不让人手抄；
- 每段只写本段实际用到的图；
- token 与 reference_images 由同一份 tokens 映射生成，避免“挂参未点名”。
"""
from .model import token

SPEAKER_CN = {"huangdan": "黄蛋", "xinyi": "心易", "narrator": "旁白"}

XINYI_LOCK = (
    "心易（参考 {r02}，棕色水豚；眼睛严格按 {r02e}）：白色圆形眼片，中心没有黑色瞳孔/眼珠/虹膜；"
    "外圈一圈深棕色细描边；眼片中心保持空白，没有高光点；眼片形状、外圈深棕线、中心空白全程不变；"
    "眼睛入画时全程睁开，白色圆形眼片完整可见；不眨眼、不眯眼、不抬眼皮、不皱眉、不闭眼、不笑眼；"
    "情绪只靠歪头/身体/手势/咔啵。"
)

XINYI_NEG = (
    "心易的黑瞳、心易的眼珠、心易的虹膜、心易的瞳孔、心易的高光点、心易的眼皮、心易的眼睑、"
    "心易的眉毛、心易的眨眼、心易的眯眼、心易的半闭眼、心易的闭眼、心易的笑眼、心易的眼神变化、"
    "心易的眼睛大特写"
)

HUANGDAN_LOCK = (
    "黄蛋（参考 {r01p}）：毛绒版，保留黄身/奶油脸/棕眼/天线球/白袜白鞋；短毛绒/毛毡质感；"
    "不限制黄蛋的眼睛，可以眨眼、可以做表情；黄蛋只有两只短手、两只脚。"
)

COMMON_NEG = (
    "视频内文字、字幕、气泡、画面内任何文字/数字/logo/水印；"
    "多余手臂、第三只手、多双手、多余手指；道具数量变化、道具凭空出现/消失；"
    "人物穿模、场景切换、镜头跳轴、机位变化；写实血液/爆浆/红肿；"
    "黄蛋讲解释、心易说人话"
)

START_VERB = ("生火", "点火", "开灯", "放水", "倒水", "埋锅", "点火烧")


def _t(tokens, key):
    return token(tokens[key])


def char_block(tokens):
    return XINYI_LOCK.format(r02=_t(tokens, "R02"), r02e=_t(tokens, "R02E")) + "\n" + \
        HUANGDAN_LOCK.format(r01p=_t(tokens, "R01P"))


def scene_block(story, tokens):
    scene = story.get("scene") or {}
    asset = scene.get("asset")
    ref = f"参考 {_t(tokens, asset)}，" if asset and asset in tokens else ""
    note = scene.get("asset_note") or ""
    return f"【场景】{ref}{scene.get('name', '')}。{note}"


def props_block(story, tokens):
    props = story.get("props") or []
    trig = story.get("trigger") or {}
    lines = []
    if props:
        lines.append(f"【道具】参考 {_t(tokens, 'A05')}（道具图）：")
        for prop in props:
            lines.append(f"- {prop.get('name')}：{prop.get('form')}；{prop.get('at')}。")
    if trig:
        lines.append(f"- 触发物 {trig.get('name')}：{trig.get('form')}；{trig.get('at')}。{trig.get('note', '')}")
    lines.append(f"- 道具固定 {len(props)} 件，首帧全在；不新增、不消失、不变数量。")
    return "\n".join(lines)


def _line_text(beat):
    text = beat.get("line")
    speaker = beat.get("speaker")
    if not text:
        return ""
    cn = SPEAKER_CN.get(speaker, speaker)
    if speaker == "xinyi":
        return f"{cn}：“{text}”（只发这一声，不加任何括号释义）"
    return f"{cn}：“{text}”"


def beats_block(story, profile, tokens, first_frame_key="K_A"):
    from .model import segments_of

    out = []
    first = True
    for seg_id, seg_start, seg_end, beats in segments_of(story, profile):
        if seg_id:
            out.append(f"【{seg_id}】")
        for beat in beats:
            start = float(beat["start"]) + (0 if profile.get("shots") else seg_start)
            end = float(beat["end"]) + (0 if profile.get("shots") else seg_start)
            head = f"{start:g}–{end:g} 秒：{beat.get('shot', '')}。"
            if first and first_frame_key and first_frame_key in tokens:
                head = f"从首帧 {_t(tokens, first_frame_key)} 开始。" + head
                first = False
            body = beat.get("action", "")
            line = _line_text(beat)
            sfx = beat.get("sfx")
            tail = ""
            if sfx:
                tail = f" 音效：{sfx}。"
            if line:
                joiner = "" if line.endswith(("。", "！", "？", "”")) else "。"
                line = " " + line + joiner
            out.append(head + body + line + tail)
    return "\n".join(out)


def sound_block(story, profile):
    sfx_list = []
    for beat in story.get("beats") or []:
        for item in str(beat.get("sfx") or "").replace("；", "、").split("、"):
            item = item.strip()
            if item and item not in sfx_list:
                sfx_list.append(item)
    sfx_text = "、".join(sfx_list[:3]) if sfx_list else "环境自然声"
    if profile.get("narration"):
        narration = story.get("narration") or {}
        return (
            "【声音】黄蛋人声（中文短句）；心易只有“咔啵”；"
            f"画外旁白：{narration.get('text', '')}（{narration.get('voice', '独立成年女声')}，"
            "不是黄蛋/心易的声音，在视频内生成，不是后期）；"
            f"音效与环境声：{sfx_text}；无 BGM；无字幕。"
        )
    tail = ""
    if (story.get("card") or {}).get("in_video"):
        so = story.get("signoff") or {}
        so_text = str(so.get("text") or "").strip()
        if so_text:
            tail = f"12–15s 黄蛋画外音（见卡尾拍），不是旁白。"
    return (
        "【声音】黄蛋人声（中文短句，只说他自己的台词）；心易只有“咔啵”（每句 1 次，不加括号释义）；"
        f"音效与环境声：{sfx_text}；无 BGM；无旁白；无字幕。" + tail
    )


def negative_block(story, profile):
    card_in_video = bool((story.get("card") or {}).get("in_video"))
    no_text = ("除卡尾静帧外，画面内不出现任何文字、不生成任何字幕、不生成任何气泡；"
               "卡尾段文字只按参考卡面呈现，不增不减不换字" if card_in_video
               else "不生成任何文字、不生成任何字幕、不生成任何气泡")
    items = [COMMON_NEG, XINYI_NEG, no_text]
    if profile.get("narration"):
        items.append("旁白由黄蛋/心易念、旁白缺失、旁白后期、旁白声线变成角色")
    else:
        items.append("旁白、画外音、解说")
    items.extend(story.get("negatives") or [])
    return "【负向】" + "；".join(items) + "。"


def a05_image_prompt(story):
    props = story.get("props") or []
    trig = story.get("trigger") or {}
    lines = [
        "16:9 白底道具图，只生成一张，物品平铺不重叠。",
    ]
    for prop in props:
        lines.append(f"- {prop.get('name')}：{prop.get('form')}。")
    if trig:
        lines.append(f"- {trig.get('name')}：{trig.get('form')}。")
    lines.append("白底、无人物、无手、无文字、无 logo、无水印；3D 卡通＋真实光影（皮克斯/搪胶）。")
    lines.append("负向：人物、手、文字、数字、logo、水印、背景环境、多余道具。")
    return "\n".join(lines)


def k_image_prompt(story, profile, tokens):
    props = story.get("props") or []
    prop_names = "、".join(p.get("name", "") for p in props)
    trig = story.get("trigger") or {}
    state = (story.get("continuity") or {}).get("scene_state") or []
    frame = story.get("first_frame") or {}
    composition = str(frame.get("composition") or "").strip()
    if not composition:
        scene_name = (story.get("scene") or {}).get("name", "")
        composition = f"{scene_name}。{prop_names}按上面标注的 0.0s 位置全部入画，黄蛋与心易都可见。"
        if trig.get("name"):
            composition += f" {trig['name']}{trig.get('at', '')}。"
    light = str(frame.get("light") or "").strip() or "光线统一；中景，人物全身可见，不切特写。"
    lines = [
        "16:9 电影感单帧，只生成一张；这是整支片的首帧，构图、站位、光线后面都不换。",
        char_block(tokens),
        scene_block(story, tokens),
        props_block(story, tokens),
        f"构图：{composition}",
        f"光线与景别：{light}",
        f"首帧状态：{'；'.join(state)}。" if state else "",
        "画面内不出现任何文字、数字、logo、水印、气泡、字幕。",
        f"负向：视频内文字/字幕/气泡、{XINYI_NEG}、多余手臂、第三只手、多双手、缺道具、道具位置错误。",
    ]
    return "\n".join(x for x in lines if x)


def video_prompt(story, profile, tokens):
    from .model import screen_range

    _, screen_end = screen_range(profile)
    card_in_video = bool((story.get("card") or {}).get("in_video"))
    duration = int(round((profile.get("total") or screen_end) if card_in_video else screen_end))
    lines = [
        f"{story['word']['spelling']} 谐音故事，{duration}s，单场景，一镜到底不换景。",
        f"【首帧锁定】首帧＝{_t(tokens, 'K_A')}：严格保持首帧的位置、朝向、尺度、光线、道具摆位，不重新构图。",
        f"【比例】黄蛋与心易的身高比例参考 {_t(tokens, 'R00')}（只取比例，不改构图、不改站位）。",
        char_block(tokens),
        scene_block(story, tokens),
        props_block(story, tokens),
        beats_block(story, profile, tokens),
    ]
    if card_in_video:
        signoff = story.get("signoff") or {}
        signoff_text = str(signoff.get("text") or "").strip()
        voice = (f"同时黄蛋画外音（他的声音，不是旁白）：『{signoff_text}』"
                 if signoff_text else "")
        lines.append(
            f"12–15 秒：硬切至卡尾静帧：画面切到 {_t(tokens, 'KC')} 卡面，卡面占满画面，"
            "卡面文字与卡面图完全一致、不增不减不换字，静止 3 秒；环境声轻收。"
            + (f" {voice}" if voice else "")
        )
    lines += [
        sound_block(story, profile),
        negative_block(story, profile),
        "同一机位同一构图；3 个快切允许硬切，其余连续" + ("；卡尾段允许硬切至卡面" if card_in_video else "") + "。",
    ]
    return "\n".join(lines)


def storyboard_prompt(story, profile, tokens):
    """三格分镜闸门（2026-11-03 起）：0/5/10s，第一格必须含全部道具与站位。"""
    beats = story.get("beats") or []

    def at(second):
        for beat in beats:
            if float(beat["start"]) <= second < float(beat["end"]):
                return beat
        return beats[-1] if beats else {}

    props = story.get("props") or []
    prop_list = "、".join(f"{p.get('name')}（{p.get('at', '')}）" for p in props)
    trig = story.get("trigger") or {}
    cells = []
    cn = ("第一格", "第二格", "第三格")
    for i, second in enumerate((0, 5, 10)):
        beat = at(second)
        note = ""
        if i == 0:
            note = (f"这一格必须包含全部道具：{prop_list}"
                    + (f"、{trig.get('name')}（{trig.get('at', '')}）" if trig.get("name") else "")
                    + "；两人的站位、朝向、光线在这一格定死。")
        cells.append(f"{cn[i]}（{second}s，{beat.get('shot', '')}）：{beat.get('action', '')}{note}")
    lines = [
        "16:9 三格分镜预演图，横向三等分，从左到右 0s / 5s / 10s；只生成一张。",
        char_block(tokens),
        scene_block(story, tokens),
        props_block(story, tokens),
        *cells,
        "三格同一机位、同一光线、同一构图；格与格之间只变动作，不变站位、不变道具数量。",
        "格线用细白线分隔；画面内不出现任何文字、数字、字幕、气泡、logo。",
        f"负向：{XINYI_NEG}、文字、字幕、气泡、多余手臂、第三只手、多双手、缺道具、道具位置错误、换景。",
    ]
    return "\n".join(x for x in lines if x)


def card_prompt(story):
    card = story["card"]
    return (
        "16:9 单张词卡静帧，只生成一张。米白卡纸居中，浅灰细边，桌面/小院背景虚化、午后暖光。\n"
        f"卡面只三行：第一行红色手写感单词 “{card['word']}”；第二行黑色 “{card['zh']} → {card['meaning']}”。\n"
        "没有小字、没有标语、没有解释、没有二维码、没有 logo、没有水印、没有多余装饰。\n"
        "文字必须完全按上面写，拼写正确，不许多字少字。"
    )


def s0_text(story, profile, tokens):
    from .model import LINK_LABEL, card_range, screen_range

    s_start, s_end = screen_range(profile)
    c_start, c_end = card_range(profile)
    props = "、".join(p.get("name", "") for p in story.get("props") or []) or "无"
    card_in_video = bool((story.get("card") or {}).get("in_video"))
    v_len = int(round(profile["total"] if card_in_video else s_end))
    if card_in_video:
        run_order = f"""【跑序】
1. 跑 A05 道具图（白底、无手、无字；不带目标词，避免烧字）。
2. 跑 G1 三格分镜（0/5/10s）；第一格必须含全部道具（{props}）与两人站位，确认后再往下。
3. 跑 K_A 首帧（构图必须和 G1 第一格一致）。
4. 跑 KC 卡面（V1 会引用它，先跑）；文字不对就重跑或改 PIL 版。
5. 跑 V1（{v_len}s，含 12–15s 卡尾硬切）；结尾接卡面，不回人物。
6. 后期只加 SRT；除卡尾段外视频内无字。"""
    else:
        run_order = f"""【跑序】
1. 跑 A05 道具图（白底、无手、无字；不带目标词，避免烧字）。
2. 跑 G1 三格分镜（0/5/10s）；第一格必须含全部道具（{props}）与两人站位，确认后再往下。
3. 跑 K_A 首帧（构图必须和 G1 第一格一致）。
4. 跑 V1（{int(s_end)}s）；结尾停住 1s，人物不回位。
5. 跑 KC 卡尾；文字不对就重跑或改 PIL 版。
6. 后期：V1 + 卡尾 3s；SRT 单独加；视频内无字。"""
    beats = "\n".join(
        f"{float(b['start']):g}–{float(b['end']):g}s｜{b.get('shot', '')}｜{b.get('action', '')}"
        + (f"｜{SPEAKER_CN.get(b.get('speaker'), '')}：{b.get('line')}" if b.get("line") else "")
        for b in story.get("beats") or []
    )
    return f"""【本画布做什么】
《蛋仔记单词》{profile['title']}：{story['word']['spelling']} = {story['word']['zh']} → {story['word']['meaning']}。
{story['title']}；{s_start:g}–{s_end:g}s 画面（{len(story.get('beats') or [])} 拍）＋ {c_start:g}–{c_end:g}s 单卡尾{'（内嵌在 V1 里）' if card_in_video else '（后期叠）'}。

{run_order}

【分工】
- 黄蛋：只说他自己的反应短句；不解释英文、不讲词义。
- 心易：不说话，只“咔啵”；眼睛按 R02E（白片＋棕圈、中心空白、全程睁开）。
- 本档无旁白：词只在卡尾出现。

【逐拍】
{beats}

【谐音与义接】
- 谐音句：{story['hook']['line']}（{story['hook']['who_says']}）
- 义接类型：{LINK_LABEL.get(story['hook']['meaning_link'], story['hook']['meaning_link'])}——{story['hook']['why_meaning']}
- 场景：{story['scene']['name']}——{story['scene']['why']}

【资产保留】
复用：R00 / R01P / R02 / R02E / A02；新生成：A05 / G1 / K_A / V1 / KC。
已生成的不要清空 outputs、不要改回“待生成”。

【门禁】
交付前：py -3 cli.py check out/{story['id']}.monet
有 ERROR 不导入；有 WARNING 看报告逐条确认。
"""
