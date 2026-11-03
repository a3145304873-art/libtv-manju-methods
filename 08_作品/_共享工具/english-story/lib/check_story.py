# -*- coding: utf-8 -*-
"""故事层校验：词、谐音、义接、时间、道具、台词、卡尾、评分。

这一层只读 story.json，不需要画布；LLM 出稿后第一道门。
"""
import re

from .model import (CheckResult, LINK_TYPES, WORD_KEYS, all_lines, beats_abs, card_range,
                    screen_range, speaker_id)
from .rules import RULES

XINYI_OK = re.compile(r"^咔[—\-–~～]*啵[。！!？?～~]*$")
EXPLAIN_WORDS = ("意思是", "的意思", "词义", "翻译", "英文是", "念作", "读作")
FORBIDDEN_KEYS = ("on_screen_text", "bubble_text", "caption_text", "screen_text")
PUNCT = re.compile(r"[\s，。！？、；：“”‘’（）()《》…—\-–·,.!?;:\"'\[\]{}|/\\]+")


def _s(value):
    return value if isinstance(value, str) else ""


def _norm(text):
    return PUNCT.sub("", _s(text))


def _walk_keys(obj, keys, path=""):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k in keys:
                hits.append(p)
            hits.extend(_walk_keys(v, keys, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(_walk_keys(v, keys, f"{path}[{i}]"))
    return hits


def check_story(story, profile):
    res = CheckResult(subject=f"story:{story.get('id', '?')}")

    # G01 词条
    word = story.get("word") or {}
    for key in WORD_KEYS:
        if not _s(word.get(key)).strip():
            res.add("G01", f"word.{key} 为空", "word")
    # G19 拼写规范
    spelling = _s(word.get("spelling"))
    if spelling and (spelling != spelling.lower() or spelling != spelling.strip()):
        res.add("G19", f"spelling 不是小写无空格：{spelling!r}", "word.spelling")
    ipa = _s(word.get("ipa"))
    if ipa and not (ipa.startswith("/") and ipa.endswith("/")):
        res.add("G19", f"ipa 不是 /…/ 形式：{ipa!r}", "word.ipa")

    # G02 自然话
    hook = story.get("hook") or {}
    if not _s(hook.get("line")).strip():
        res.add("G02", "hook.line 为空", "hook.line")
    if not _s(hook.get("who_says")).strip():
        res.add("G02", "hook.who_says 为空（谁会在该场景说这句话）", "hook.who_says")
    if len(_s(hook.get("why_natural")).strip()) < 10:
        res.add("G02", "hook.why_natural 少于 10 字，等于没证明自然", "hook.why_natural")

    # G03 义接
    link = _s(hook.get("meaning_link"))
    if link not in LINK_TYPES:
        res.add("G03", f"meaning_link={link!r} 不在 {LINK_TYPES}", "hook.meaning_link")
    if len(_s(hook.get("why_meaning")).strip()) < 8:
        res.add("G03", "hook.why_meaning 少于 8 字，义接没落地", "hook.why_meaning")

    # G15 场景
    scene = story.get("scene") or {}
    if not _s(scene.get("name")).strip():
        res.add("G15", "scene.name 为空", "scene.name")
    if len(_s(scene.get("why")).strip()) < 10:
        res.add("G15", "scene.why 少于 10 字：必须说明为什么这个场景让字面动作成立", "scene.why")

    # G05 道具
    props = story.get("props") or []
    max_props = int(profile.get("max_props", 3))
    if len(props) > max_props:
        res.add("G05", f"道具 {len(props)} 件，超过上限 {max_props}", "props")
    for i, prop in enumerate(props):
        where = f"props[{i}]"
        if not _s(prop.get("name")).strip():
            res.add("G05", "道具没有名字", where)
        if not _s(prop.get("form")).strip():
            res.add("G05", f"道具“{prop.get('name')}”没写形态（模型会换成别的）", where)
        if prop.get("first_frame") is not True:
            res.add("G05", f"道具“{prop.get('name')}”没有 first_frame=true", where)

    # G04 时间轴
    screen_start, screen_end = screen_range(profile)
    segs = story.get("segments") if not profile.get("shots") else None
    if profile.get("shots"):
        beats = story.get("beats") or []
        shape = profile["shots"]["shape"]
        if len(beats) != len(shape):
            res.add("G04", f"拍数 {len(beats)}，profile 要求 {len(shape)}", "beats")
        cursor = screen_start
        for i, beat in enumerate(beats):
            where = f"beats[{i}]"
            start, end = float(beat.get("start", -1)), float(beat.get("end", -1))
            if abs(start - cursor) > 1e-6:
                res.add("G04", f"第 {i + 1} 拍起点 {start}，应接上一拍 {cursor}", where)
            if end <= start:
                res.add("G04", f"第 {i + 1} 拍时长非正：{start}–{end}", where)
            elif i < len(shape) and abs((end - start) - shape[i]) > 1e-6:
                res.add("G04", f"第 {i + 1} 拍 {end - start}s，profile 要求 {shape[i]}s", where)
            cursor = end
        if abs(cursor - screen_end) > 1e-6:
            res.add("G04", f"画面在 {cursor}s 结束，profile 要求 {screen_end}s", "beats")
    else:
        want = profile.get("segments") or []
        got = segs or []
        if len(got) != len(want):
            res.add("G04", f"段数 {len(got)}，profile 要求 {len(want)}", "segments")
        for i, seg in enumerate(got):
            where = f"segments[{i}]"
            s, e = float(seg.get("start", -1)), float(seg.get("end", -1))
            if not seg.get("id"):
                res.add("G04", "段缺 id", where)
            if e <= s:
                res.add("G04", f"段时长非正：{s}–{e}", where)
            beats = seg.get("beats") or []
            if not beats:
                res.add("G04", f"{seg.get('id')} 没有拍", where)
            cursor = s
            for j, beat in enumerate(beats):
                bs, be = float(beat.get("start", -1)), float(beat.get("end", -1))
                if abs(bs + s - cursor) > 1e-6:
                    res.add("G04", f"{seg.get('id')} 第 {j + 1} 拍起点不接上一拍", f"{where}.beats[{j}]")
                if be <= bs:
                    res.add("G04", f"{seg.get('id')} 第 {j + 1} 拍时长非正", f"{where}.beats[{j}]")
                cursor = s + be
            if abs(cursor - e) > 1e-6:
                res.add("G04", f"{seg.get('id')} 拍到 {cursor}s，段尾是 {e}s", where)

    # G06/G07/G08 台词
    cast = set(profile.get("cast") or [])
    speakers = set()
    lines = all_lines(story, profile)
    for line in lines:
        speaker, text = line["speaker"], _s(line["text"])
        speakers.add(speaker)
        where = f"{line['start']}–{line['end']}s {speaker}"
        if speaker == "narrator":
            if not profile.get("narration"):
                res.add("G06", f"该 profile 没有旁白位，却出现旁白：{text}", where)
            continue
        if speaker not in cast:
            res.add("G06", f"未知说话人 {speaker!r}：{text}", where)
            continue
        if speaker == "xinyi":
            if not XINYI_OK.match(text.strip()):
                res.add("G06", f"心易说了非咔啵台词：{text!r}", where)
            if re.search(r"[（(【].*[）)】]", text):
                res.add("G07", f"咔啵带括号释义：{text!r}", where)
        elif speaker == "huangdan":
            for bad in EXPLAIN_WORDS:
                if bad in text:
                    res.add("G08", f"黄蛋讲解释（出现“{bad}”）：{text}", where)

    # G09 单词必须被黄蛋说出（meme20）
    if profile.get("require_word_in_line") and spelling:
        huang = [l for l in lines if l["speaker"] == "huangdan"]
        if not any(spelling.lower() in _s(l["text"]).lower() for l in huang):
            res.add("G09", f"黄蛋台词里一次都没出现 {spelling}", "beats")

    # G10 旁白
    narration = story.get("narration")
    if profile.get("narration"):
        if not isinstance(narration, dict):
            res.add("G10", "profile 要求旁白，但 story.narration 缺失", "narration")
        else:
            text = _s(narration.get("text"))
            if not text:
                res.add("G10", "旁白文本为空", "narration.text")
            if spelling and spelling.lower() not in text.lower():
                res.add("G10", f"旁白没点名单词 {spelling}", "narration.text")
            if _s(word.get("meaning")) and _s(word.get("meaning")) not in text:
                res.add("G10", "旁白没给出中文词义", "narration.text")
            if not _s(narration.get("voice")).strip():
                res.add("G10", "旁白没声明声线（必须是独立声线，不是角色）", "narration.voice")
            if narration.get("in_video") is not True:
                res.add("G10", "旁白 in_video 不是 true：本线要求视频内生成，不做后期", "narration.in_video")

    # G11 卡尾
    card = story.get("card") or {}
    keys = set(card.keys()) - {"in_video"}  # in_video 是摆放控制字段，不是卡面内容
    if keys != {"word", "zh", "meaning"}:
        res.add("G11", f"card 字段是 {sorted(keys)}，只允许 word/zh/meaning 三行", "card")
    for key in ("word", "zh", "meaning"):
        if not _s(card.get(key)).strip():
            res.add("G11", f"card.{key} 为空", f"card.{key}")
    if spelling and _s(card.get("word")) and _s(card.get("word")).lower() != spelling.lower():
        res.add("G11", f"card.word={card.get('word')!r} 与目标词 {spelling!r} 不一致", "card.word")

    # G12 评分
    scores = story.get("scores") or {}
    total = 0
    for key in ("natural", "meaning", "visual", "character"):
        val = scores.get(key)
        if not isinstance(val, int) or not 0 <= val <= 25:
            res.add("G12", f"scores.{key}={val!r}，应为 0–25 整数", f"scores.{key}")
        else:
            total += val
    if total < 80:
        res.add("G12", f"总分 {total} < 80，不允许 build", "scores")

    # G13 不补救
    continuity = story.get("continuity") or {}
    if continuity.get("no_rescue") is not True:
        res.add("G13", "continuity.no_rescue 未置 true：心易不做补救", "continuity.no_rescue")

    # G14 不报下一个词
    next_word = _s(story.get("next_word")).lower()
    if next_word:
        for line in lines:
            if next_word in _s(line["text"]).lower():
                res.add("G14", f"台词提前报了下一个词 {next_word}：{line['text']}", f"{line['start']}s")

    # G16 字幕（卡内嵌时允许落在卡尾段，文本池含锚点句）
    sub_start, sub_end = 0.0, screen_end
    card_in = bool((story.get("card") or {}).get("in_video"))
    if card_in:
        sub_end = card_range(profile)[1]
    line_norms = [(_norm(l["text"]), l) for l in lines]
    signoff_obj = story.get("signoff")
    if card_in and isinstance(signoff_obj, dict) and _s(signoff_obj.get("text")):
        line_norms.append((_norm(signoff_obj["text"]),
                           {"speaker": signoff_obj.get("speaker"), "text": signoff_obj.get("text")}))
    for i, sub in enumerate(story.get("subtitles") or []):
        where = f"subtitles[{i}]"
        s, e = float(sub.get("start", -1)), float(sub.get("end", -1))
        if s < sub_start or e > sub_end + 1e-6:
            res.add("G16", f"字幕 {s}–{e}s 超出画面段 0–{sub_end}s", where)
        if e <= s:
            res.add("G16", f"字幕时长为负或 0：{s}–{e}", where)
        text = _norm(sub.get("text"))
        if not text:
            res.add("G16", "字幕文本为空", where)
        elif not any(text in ln for ln, _ in line_norms):
            res.add("G16", f"字幕“{sub.get('text')}”不是任何一句台词的子串", where)

    # G17 画面文字字段
    for path in _walk_keys(story, FORBIDDEN_KEYS):
        res.add("G17", f"出现画面文字字段 {path}：视频内无字", path)

    # G18 心易不是背景板
    xinyi_beats = 0
    for item in beats_abs(story, profile):
        beat = item["beat"]
        if beat.get("speaker") == "xinyi" or "心易" in _s(beat.get("action")):
            xinyi_beats += 1
    if xinyi_beats < 2:
        res.add("G18", f"心易参与的拍只有 {xinyi_beats} 个，至少 2 个", "beats")

    # G21 局势转折
    turn = story.get("turn")
    beat_count = len(story.get("beats") or [])
    if not isinstance(turn, dict):
        res.add("G21", "缺 story.turn：需要一处改变局势的转折，不是同类出丑的重复", "turn")
    else:
        at = turn.get("at")
        upper = max(2, beat_count - 1)
        if not isinstance(at, int) or not 2 <= at <= upper:
            res.add("G21", f"turn.at={at!r}，应为第 3 拍起的拍序号（2–{upper}，0 起）", "turn.at")
        for key, minlen in (("before", 4), ("after", 4), ("why", 12)):
            if len(_s(turn.get(key)).strip()) < minlen:
                res.add("G21", f"turn.{key} 少于 {minlen} 字", f"turn.{key}")

    # G22 小愿望/小落差
    stakes = story.get("stakes")
    if not isinstance(stakes, dict):
        res.add("G22", "缺 story.stakes：一个小愿望＋一个小落差（不要求对抗）", "stakes")
    else:
        for key in ("want", "cost"):
            if len(_s(stakes.get(key)).strip()) < 6:
                res.add("G22", f"stakes.{key} 少于 6 字（要画面可拍的小愿望/小落差）", f"stakes.{key}")

    # G23 疑似对抗框架（强度提醒）
    gamble_words = ("赌", "押上", "押注", "押了", "赔", "惩罚", "输赢")
    gamble_texts = []
    for item in beats_abs(story, profile):
        beat = item["beat"]
        gamble_texts.append(_s(beat.get("action")))
        gamble_texts.append(_s(beat.get("line")))
    stake_obj = story.get("stakes")
    if isinstance(stake_obj, dict):
        gamble_texts.append(_s(stake_obj.get("want")))
        gamble_texts.append(_s(stake_obj.get("cost")))
    found = [w for w in gamble_words if w in "".join(gamble_texts)]
    if found:
        res.add("G23", f"出现 {'、'.join(found)}：确认这是无厘头小插曲而不是赌局（强度上限＝微微的不顺）", "beats/stakes")

    # G24 收尾锚点句（卡内嵌模式必填）
    card_in_video = bool((story.get("card") or {}).get("in_video"))
    signoff = story.get("signoff")
    if card_in_video:
        if not isinstance(signoff, dict):
            res.add("G24", "缺 story.signoff：卡尾要有「word 谐音 词义。你记住了吗？」的标志性锚点句", "signoff")
        else:
            text = _s(signoff.get("text"))
            speaker = speaker_id(signoff.get("speaker"))
            if speaker not in set(profile.get("cast") or []):
                res.add("G24", f"signoff.speaker={signoff.get('speaker')!r} 不在角色表", "signoff.speaker")
            if spelling and spelling.lower() not in text.lower():
                res.add("G24", "signoff.text 没有点出目标词", "signoff.text")
            if "记住了" not in text:
                res.add("G24", "signoff.text 没有“你记住了吗”收尾", "signoff.text")

    # G20 类型
    if not isinstance(story.get("props", []), list):
        res.add("G20", "props 必须是数组", "props")
    if not isinstance(story.get("subtitles", []), list):
        res.add("G20", "subtitles 必须是数组", "subtitles")
    if not isinstance(story.get("scores", {}), dict):
        res.add("G20", "scores 必须是对象", "scores")

    return res
