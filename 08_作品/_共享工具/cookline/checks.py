# -*- coding: utf-8 -*-
"""硬校验：每条都对应 rules/failures.json 里的一个历史翻车。

能判的写在这里；只能人看的，留在 HUMAN，不假装通过。
"""
from __future__ import annotations

import re
import math
from dataclasses import dataclass, field

from . import rules
from .compose import Plan, compose


@dataclass
class Issue:
    fid: str
    where: str
    message: str

    @property
    def severity(self) -> str:
        return rules.FAILURE_BY_ID[self.fid]["severity"]


@dataclass
class Report:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    humans: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, fid: str, where: str, message: str) -> None:
        issue = Issue(fid, where, message)
        if issue.severity == "error":
            self.errors.append(issue)
        elif issue.severity == "warn":
            self.warnings.append(issue)

    def warn(self, fid: str, where: str, message: str) -> None:
        self.warnings.append(Issue(fid, where, message))

    def ok(self, strict: bool = False) -> bool:
        return not self.errors and not (strict and self.warnings)

    def text(self, title: str = "", strict: bool = False) -> str:
        lines = []
        if title:
            lines.append(title)
        for label, items in (("ERROR", self.errors), ("WARN", self.warnings)):
            for i in items:
                lines.append(f"{label} {i.fid} {i.where}：{i.message}")
        for n in self.notes:
            lines.append(f"NOTE {n}")
        for h in self.humans:
            lines.append(f"HUMAN {h['id']} {h['title']}：{h['fix']}")
        ok = self.ok(strict)
        verdict = "通过" if ok else ("未通过" if self.errors else "WARN 未通过（strict）")
        lines.append(f"结果：{len(self.errors)} ERROR / {len(self.warnings)} WARN / {len(self.humans)} HUMAN；{verdict}")
        return "\n".join(lines)


def _txt(beat: dict) -> str:
    return f"{beat.get('start', '')}{beat.get('do', '')}{beat.get('end', '')}{beat.get('desc', '')}{beat.get('sub', '')}"


def _where(si: int, bi: int | None = None) -> str:
    if bi is None:
        return f"V{si + 1}"
    return f"V{si + 1} 第{bi + 1}拍"


def check(card: dict, plan: Plan | None = None, strict: bool = False) -> Report:
    rep = Report(humans=rules.human_checks())
    _check_format(card, rep)
    _check_areas(card, rep)
    if card.get("_legacy"):
        rep.notes.append("旧卡：单句拍、没有道具/手/状态账本；只做兼容审计，补齐 v2 后才能 build")
        _check_legacy_beats(card, rep)
        _check_character(card, rep, soft=True)
        _check_camera(card, rep)
        _check_sound(card, rep)
        _check_subtitles(card, rep)
        _check_dialogue(card, rep)
        _check_ending(card, rep)
        rep.warn("F07", "整卡", "旧卡没有道具/手部账本；F06/F07/F09/F10/F15 只能人工检查")
        return rep

    _check_beats(card, rep)
    _check_character(card, rep)
    _check_props(card, rep)
    _check_counts(card, rep)
    _check_state(card, rep)
    _check_hand(card, rep)
    _check_camera(card, rep)
    _check_sound(card, rep)
    _check_subtitles(card, rep)
    _check_dialogue(card, rep)
    _check_ending(card, rep)
    _check_eating(card, rep)

    if plan is None and not rep.errors:
        try:
            plan = compose(card)
        except Exception as exc:  # 结构坏了就不要拼提示词
            rep.add("F01", "整卡", f"提示词拼装失败：{exc}")
    if plan is not None:
        _check_prompts(card, plan, rep)
    return rep


# ---------------- 结构 ----------------

def _check_format(card: dict, rep: Report) -> None:
    fmt = card["format"]
    segs = card.get("segments") or []
    if not segs:
        rep.add("F01", "整卡", "还没有按本菜规划片段；至少创建一个制作段")
    keys = [str(seg.get("key") or "") for seg in segs]
    if len(keys) != len(set(keys)):
        rep.add("F01", "整卡", "片段 key 重复；请保证每段标识唯一")
    for si, seg in enumerate(segs):
        duration = float(seg.get("duration_seconds", 0) or 0)
        if seg.get("duration_invalid") or not math.isfinite(duration) or duration <= 0:
            rep.add("F01", _where(si), f"片段时长必须大于 0 秒，当前 {duration:g}")
        elif abs(duration - round(duration)) > 1e-6:
            rep.add("F01", _where(si), f"当前视频节点时长需为整秒，当前 {duration:g} 秒")
    if fmt.get("aspect") != "16:9":
        rep.add("F01", "整卡", f"本线固定 16:9，当前 {fmt.get('aspect')}")


def _check_legacy_beats(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        total = float(seg.get("duration_seconds", card["format"]["segment_seconds"]))
        beats = seg.get("beats") or []
        if not beats:
            continue
        if abs(beats[0]["start_sec"]) > 0.01 or abs(beats[-1]["end_sec"] - total) > 0.01:
            rep.warn("F04", _where(si), f"旧卡时间轴没有盖满本段 {total:g} 秒")
        for bi, b in enumerate(beats):
            if b["kind"] == "action" and len(b.get("do", "")) < 4:
                rep.warn("F01", _where(si, bi), "这一拍没有动作描述")
            if b["kind"] == "breathe" and len(b.get("desc", "")) < 6:
                rep.warn("F03", _where(si, bi), "空镜没有内容")


def _check_areas(card: dict, rep: Report) -> None:
    areas = card.get("areas") or []
    if len(areas) < 1:
        rep.add("F05", "整卡", "至少声明一个实际使用的台地")
    keys = [a["key"] for a in areas]
    if len(keys) != len(set(keys)):
        rep.add("F05", "整卡", "台地 key 重复")
    for a in areas:
        for f in ("desc", "layout", "props_here"):
            if not a.get(f):
                rep.add("F05", f"台地 {a['key']}", f"缺 {f}；站位与器具清单缺一项，模型就会自由发挥")
    for si, seg in enumerate(card.get("segments") or []):
        if seg["area"] not in keys:
            rep.add("F05", _where(si), f"台地 {seg['area']} 不在 areas 里")
        if seg.get("area2"):
            rep.add("F02", _where(si), f"一段里换了第二个台地（{seg['area2']}）；拆成两条或并成一个角落")
    # 配角不进空景；第一次出场不能就在最后一段
    companions = {c["key"]: c for c in card.get("companions") or []}
    for a in areas:
        for c in companions.values():
            if c.get("label") and c["label"] in (a.get("desc") or ""):
                rep.add("F05", f"台地 {a['key']}", f"空景描述里出现配角「{c['label']}」；配角走独立角色节点，不进空景")
    seen: set[str] = set()
    segs = card.get("segments") or []
    for si, seg in enumerate(segs):
        for key in seg.get("with") or []:
            if key in companions and key not in seen and si >= 2:
                rep.add("F09", _where(si), f"配角「{key}」第一次出场就在第 {si + 1} 段；前段要有铺垫")
            seen.add(key)


def _check_beats(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        total = float(seg.get("duration_seconds", card["format"]["segment_seconds"]))
        beats = seg.get("beats") or []
        if not beats:
            rep.add("F01", _where(si), "片段没有动作拍；写入本段实际发生的动作")
            continue
        for bi, b in enumerate(beats):
            if b.get("time_inferred"):
                rep.warn("F04", _where(si, bi), "本拍未给时间点，系统按拍数平均补齐；请按动作实际时长填写 t")
            if b["kind"] == "action":
                for f in ("start", "do", "end"):
                    if len(b.get(f, "")) < 6:
                        rep.add("F01", _where(si, bi), f"{f} 写得太短；必须写全起幅/动作/落幅三截")
                if not b.get("do"):
                    rep.add("F07", _where(si, bi), "只写了结果，没有产生结果的动作")
            else:
                if len(b.get("desc", "")) < 6:
                    rep.add("F03", _where(si, bi), "呼吸拍没有内容；空镜只拍火、蒸汽、光、静物")
                for word in rules.BREATHE_FORBIDDEN:
                    if word in b.get("desc", ""):
                        rep.add("F03", _where(si, bi), f"呼吸拍里出现动作「{word}」，会推进剧情")
                        break
        # 时间轴：完整覆盖本段且相邻镜头连续；拍长是否相同由本集节奏决定。
        if abs(beats[0]["start_sec"]) > 0.01:
            rep.add("F04", _where(si), "第一拍不从 0 秒开始")
        if abs(beats[-1]["end_sec"] - total) > 0.01:
            rep.add("F04", _where(si), f"最后一拍没到 {total} 秒")
        for a, b in zip(beats, beats[1:]):
            if abs(a["end_sec"] - b["start_sec"]) > 0.01:
                rep.add("F04", _where(si), f"{a['t']} 与 {b['t']} 之间有缝/重叠")
        for bi, b in enumerate(beats):
            if b["end_sec"] <= b["start_sec"]:
                rep.add("F04", _where(si, bi), "单拍时长必须大于 0")
            if b["start_sec"] < -0.01 or b["end_sec"] > total + 0.01:
                rep.add("F04", _where(si, bi), f"单拍时间超出本段 0–{total:g}s 范围")
        frames = seg.get("storyboard_frames") or []
        times = [float(frame["at"]) for frame in frames]
        if seg.get("storyboard_frames_invalid"):
            rep.add("F01", _where(si), "分镜帧时间点格式无效；请填数字秒数或 at 数值")
        if seg.get("storyboard_frames_inferred"):
            rep.add("F01", _where(si), "本段分镜帧仅按动作拍数自动推导；请明确本段帧数/时间点或填写 storyboard_frames")
        if not times:
            rep.add("F01", _where(si), "本段没有分镜帧；请显式规划或使用自动帧数")
        if any(t < -0.01 or t > total + 0.01 for t in times):
            rep.add("F01", _where(si), f"分镜时间点必须在本段 0–{total:g} 秒内")
        if len(times) != len(set(round(t, 3) for t in times)):
            rep.add("F01", _where(si), "分镜时间点重复；请调整帧位")
        if times != sorted(times):
            rep.add("F01", _where(si), "分镜帧必须按时间先后排列")


# ---------------- 角色 ----------------

def _check_character(card: dict, rep: Report, soft: bool = False) -> None:
    def _hit(fid: str, where: str, msg: str) -> None:
        if soft:
            rep.warn(fid, where, msg)
        else:
            rep.add(fid, where, msg)

    ch = card.get("character") or {}
    for f in ("name", "desc"):
        if not ch.get(f):
            _hit("F16", "角色", f"缺 {f}；角色卡不完整，比例和外观都会漂")
    h = ch.get("height_cm")
    if not h:
        _hit("F16", "角色", "缺身高；没有身高就没有尺度句")
    elif float(h) > 200:
        _hit("F16", "角色", f"身高 {h}cm 已接近人类尺寸；这条线是「小世界」不是巨人")
    if not ch.get("hands"):
        _hit("F12", "角色", "没写手的形状；多手/人手类负向会落空")
    refs = ch.get("refs") or []
    if not refs:
        _hit("F16", "角色", "没有角色参考图；跨集一致性没有锚")
    for r in refs:
        if not str(r.get("url", "")).startswith("https://"):
            _hit("F16", "角色", f"参考图 {r.get('label')} 不是 https 地址")


# ---------------- 道具账本 ----------------

def _area_of(card: dict, key: str) -> dict:
    for a in card.get("areas", []):
        if a["key"] == key:
            return a
    return {"key": key, "props_here": []}


def _check_props(card: dict, rep: Report) -> None:
    props = card.get("props") or []
    known = {p["key"] for p in props}
    labels = {str(p.get("label")) for p in props}
    known |= labels
    seen, dup = set(), set()
    for p in props:
        if p["key"] in seen:
            dup.add(p["key"])
        seen.add(p["key"])
        if not p.get("body"):
            rep.add("F05", f"道具 {p['key']}", "白底道具没有 body 描述")
    for d in dup:
        rep.add("F05", f"道具 {d}", "道具 key 重复")

    undeclared = 0
    prev_available: set[str] | None = None
    for si, seg in enumerate(card.get("segments") or []):
        area = _area_of(card, seg["area"])
        area_props = set(area.get("props_here") or [])
        carry = set(seg.get("carry") or [])
        if prev_available is not None:
            for c in carry:
                if c not in prev_available:
                    rep.add("F09", _where(si), f"carry 里的「{c}」上一段结束时不在手边，带不过来")
        available = set(area_props) | carry
        declared_any = bool(seg.get("carry"))
        entered_here: set[str] = set()
        b0 = seg["beats"][0] if seg["beats"] else None
        if b0 and b0["kind"] == "action":
            b0_props: list[str] = []
            for p in (b0.get("props") or []) + (b0.get("hand") or []):
                if p in known and p not in b0_props:
                    b0_props.append(p)
            if len(b0_props) > 4:
                rep.warn("F07", _where(si),
                         f"首拍白底道具 {len(b0_props)} 件，K 帧只挂前 4 件（{'、'.join(b0_props[:4])}）；建议精简首拍道具")
        for bi, b in enumerate(seg["beats"]):
            if b["kind"] != "action":
                continue
            visible = b.get("props") or []
            hands = b.get("hand") or []
            if b.get("props") is not None or b.get("hand") is not None:
                declared_any = True
            for p in list(visible) + list(hands):
                if not p:
                    continue
                if p in known and p not in area_props and p not in carry and p not in entered_here:
                    rep.add("F06", _where(si, bi), f"「{p}」不在本角落器具清单，也不是带进来的")
                if p not in available:
                    rep.add("F07", _where(si, bi), f"「{p}」凭空出现；起幅里先有，或用 enter 声明拿进来")
            for p in b.get("enter") or []:
                verbs = ("拿", "取", "抱", "端", "提", "捧", "摘", "捡", "舀", "倒", "放进", "放入", "抓起", "挑", "捞", "拨")
                if not any(v in b.get("do", "") for v in verbs):
                    rep.add("F07", _where(si, bi), f"enter 了「{p}」，但动作里看不见它被拿进来")
                available.add(p)
                entered_here.add(p)
            for p in b.get("exit") or []:
                available.discard(p)
            for p in hands:
                if len(hands) > 2:
                    rep.add("F12", _where(si, bi), f"同一拍拿了 {len(hands)} 件东西；它只有两只手")
                    break
        if not declared_any:
            undeclared += 1
        prev_available = available | area_props
    if undeclared:
        rep.add("F07", "整卡", f"{undeclared} 段没有道具/手部账本；F06/F07/F09/F10/F15 只能降级为人工检查")


# ---------------- 数量 ----------------

def _check_counts(card: dict, rep: Report) -> None:
    prev_after: dict | None = None
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            counts = b.get("counts") or {}
            if counts and prev_after:
                for k, v in counts.items():
                    if k in prev_after and v != prev_after[k]:
                        grew = isinstance(v, (int, float)) and isinstance(prev_after[k], (int, float)) and v > prev_after[k]
                        verbs = ("加", "放", "倒", "拿", "摘", "取", "买", "添", "多")
                        if grew and not any(w in b.get("do", "") for w in verbs):
                            rep.add("F10", _where(si, bi), f"「{k}」从 {prev_after[k]} 变成 {v}，但没有增加的动作")
                        elif not grew:
                            rep.add("F10", _where(si, bi), f"「{k}」数量从 {prev_after[k]} 变成 {v}，没有用掉/切开")
            if b.get("counts_after"):
                prev_after = dict(b["counts_after"])
            elif counts:
                prev_after = dict(counts)


# ---------------- 状态 ----------------

def _check_state(card: dict, rep: Report) -> None:
    inherited: dict[str, object] = {}
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            if b["kind"] != "action":
                continue
            start = b.get("state") or {}
            for k, v in start.items():
                if k in inherited and str(inherited[k]) != str(v):
                    rep.add("F09", _where(si, bi), f"「{k}」上一拍是 {inherited[k]}，本拍起幅变成 {v}，中间没有动作")
            # 容器闭着却要放入
            if any(w in b.get("do", "") for w in rules.INSERT_VERBS):
                closed = [k for k, v in {**inherited, **start}.items() if str(v) in rules.CLOSED_STATES]
                if closed:
                    rep.add("F08", _where(si, bi), f"「{closed[0]}」还闭着，本拍却要放入；先开盖，盖放到台面上")
            # 切好的又变整颗
            for k, v in start.items():
                last = inherited.get(k)
                if str(last) in rules.CUT_STATES and str(v) in rules.WHOLE_STATES:
                    rep.add("F11", _where(si, bi), f"「{k}」上一拍已切开，本拍又变整颗")
            # 火已着还生火
            fire = str(start.get("fire", start.get("火", inherited.get("fire", inherited.get("火", "")))))
            if fire in ("lit", "burning", "on", "着", "已着") and any(w in b.get("do", "") for w in ("生火", "点火", "点着", "吹着火")):
                rep.add("F18", _where(si, bi), "火已经着了，又写生火；改成添柴、看火、拨火")
            inherited.update(start)
            inherited.update(b.get("state_after") or {})


# ---------------- 手 ----------------

def _check_hand(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        prev_hand: list[str] = []
        prev_do = ""
        for bi, b in enumerate(seg["beats"]):
            if b["kind"] != "action":
                continue
            hand = b.get("hand")
            if hand is None:
                prev_hand, prev_do = [], b.get("do", "")
                continue
            if len(hand) > 2:
                rep.add("F12", _where(si, bi), f"同时拿了 {len(hand)} 件；它只有两只手")
            # 段首允许手上有上一段带过来的东西；换手只在段内判
            if bi > 0:
                removed = [h for h in prev_hand if h not in hand]
                added = [h for h in hand if h not in prev_hand]
                if removed and not any(w in prev_do for w in rules.PUTDOWN_VERBS):
                    rep.add("F15", _where(si, bi), f"上一拍手里是 {removed}，没写放下就换了；先放下再拿起")
                if added and not any(w in b.get("do", "") for w in rules.PICKUP_VERBS):
                    rep.add("F15", _where(si, bi), f"本拍手里多了 {added}，动作里没有拿起的动作")
            prev_hand, prev_do = list(hand), b.get("do", "")


# ---------------- 镜头 ----------------

def _check_camera(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        area = _area_of(card, seg["area"])
        for bi, b in enumerate(seg["beats"]):
            text = _txt(b)
            back = "背影" in text and not re.search(r"不拍[^。；]{0,4}背影", text)
            full_walk = "全身" in text and "走" in text and not re.search(r"不拍[^。；]{0,6}全身", text)
            full_hold = "正面全身" in text and "抱" in text and "不拍" not in text
            if back or full_walk or full_hold:
                rep.add("F13", _where(si, bi), "全身背影/正面抱物会长手；改特写（只拍手和道具）或正面/3-4 中景")
            if any(w in text for w in ("近景", "特写")) and (_is_stove(area) or "灶" in text):
                if "保留" not in text:
                    rep.add("F17", _where(si, bi), "灶边近景没写保留什么；写「中景、保留灶身/灶口/台面」")
                elif "灶" not in text:
                    rep.add("F17", _where(si, bi), "灶边近景要保留灶身与灶口火膛，不然会被改成火塘")


def _is_stove(area: dict) -> bool:
    return any(w in f"{area.get('key', '')}{area.get('name', '')}" for w in ("灶", "stove", "厨"))


# ---------------- 声音与字幕 ----------------

def _check_sound(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        s = seg.get("sound") or ""
        if not s:
            rep.add("F21", _where(si), "没写环境声；这条线靠环境声，不靠音乐")
        if "BGM" in s or "背景音乐" in s or "配乐" in s or ("音乐" in s and "没有音乐" not in s):
            rep.add("F21", _where(si), "声音里写了音乐；生成只用环境声，音乐后期加")


def _check_subtitles(card: dict, rep: Report) -> None:
    subs = (card.get("post") or {}).get("subtitles") or []
    if len(subs) > 8:
        rep.add("F19", "字幕", f"全片 {len(subs)} 条；参考片 8 条，越多越像教程")
    total = float(card.get("_total_seconds", 0))
    for s in subs:
        if not s.get("text"):
            rep.add("F19", "字幕", "空字幕条目")
        if s["end"] <= s["start"]:
            rep.add("F19", "字幕", f"「{s['text']}」时间轴反了")
        if s["end"] > total + 0.01:
            rep.add("F19", "字幕", f"「{s['text']}」超出片长")
        if len(str(s["text"])) > 8:
            rep.add("F19", "字幕", f"「{s['text']}」超过 8 字；白字只压 2–3 字")
    # 字幕文案与动作描述重合：模型会把这段字直接烧进画面（V1「一窝」）
    bodies = []
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            bodies.append((_where(si, bi), f"{b.get('start', '')}{b.get('do', '')}{b.get('end', '')}{b.get('desc', '')}"))
    for s in subs:
        text = str(s.get("text") or "")
        if len(text) < 2:
            continue
        for where, body in bodies:
            if text in body:
                rep.add("F19", where, f"字幕「{text}」已经在动作描述里；模型会烧字，字幕只放 SRT")
                break
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            body = f"{b.get('start', '')}{b.get('do', '')}{b.get('end', '')}{b.get('desc', '')}"
            if "「" in body or "」" in body:
                rep.add("F19", _where(si, bi), "动作描述里有引号；模型会把引号里的字画进画面")


def _check_dialogue(card: dict, rep: Report) -> None:
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            for f in ("line", "dialogue", "say"):
                if b.get(f):
                    rep.add("F20", _where(si, bi), f"有 {f} 字段；这条线不说话，台词只能后期")
    speech = str((card.get("character") or {}).get("speech") or "")
    if not speech:
        if card.get("_legacy"):
            rep.warn("F20", "角色", "没写发声方式；默认它不说话，只发一个很轻的音")
        else:
            rep.add("F20", "角色", "没写发声方式；默认它不说话，只发一个很轻的音")


# ---------------- 收尾 ----------------

def _check_eating(card: dict, rep: Report) -> None:
    """F30 成品跳切：有进食动作的段，账本里必须有食材道具（edible: true）入画。"""
    cooked = {p["key"] for p in (card.get("props") or []) if p.get("edible")}
    told = False
    for si, seg in enumerate(card.get("segments") or []):
        for bi, b in enumerate(seg["beats"]):
            if b["kind"] != "action" or not any(v in b.get("do", "") for v in rules.EAT_VERBS):
                continue
            seg_screen: set[str] = set()
            for bb in seg["beats"]:
                if bb["kind"] != "action":
                    continue
                seg_screen |= set(bb.get("props") or []) | set(bb.get("enter") or [])
            if seg_screen & cooked:
                continue
            if not cooked:
                rep.add("F30", _where(si, bi),
                        "有进食动作，但卡里没有任何 edible: true 的食材道具；给食材标 edible，并把取出/盛取写成可见动作")
            else:
                rep.add("F30", _where(si, bi),
                        f"有进食动作，但本段账本里没有食材（edible：{'、'.join(sorted(cooked))}）；把取出/盛取写成可见动作，让食材在本段入画")
            told = True
            break
        if told:
            break


def _check_ending(card: dict, rep: Report) -> None:
    segs = card.get("segments") or []
    if not segs:
        return
    last = segs[-1]
    beats = last["beats"]
    acts = [b for b in beats if b["kind"] == "action"]
    if not acts:
        return
    text = _txt(acts[-1])
    if beats and beats[-1]["kind"] == "breathe":
        text += _txt(beats[-1])
    if not any(w in text for w in rules.SHARE_WORDS):
        intent = str(last.get("ending_intent") or "").strip()
        if not intent or intent.lower().startswith(("todo", "tbd")):
            rep.add("F27", _where(len(segs) - 1), "请标明本集结尾意图；分享只是可选方式")


# ---------------- 提示词 ----------------

def _check_prompts(card: dict, plan: Plan, rep: Report) -> None:
    need_hand = ("多余手臂", "第三只手", "多双手")
    need_human = ("人类的手", "五指", "指甲")
    need_text = ("字幕", "文字")
    scale_key = "为它配好的小世界"
    subs = (card.get("post") or {}).get("subtitles") or []

    for art in plan.images:
        if art.kind in ("scene", "grid", "key"):
            if scale_key not in art.prompt:
                rep.add("F16", art.label, "提示词缺尺度常量")
        if art.kind in ("grid", "key"):
            for w in need_hand + need_human + need_text:
                if w not in art.prompt:
                    rep.add("F12" if w in need_hand else ("F14" if w in need_human else "F19"), art.label, f"负向缺「{w}」")
        if len(art.prompt) > 2000:
            rep.add("F22", art.label, f"提示词 {len(art.prompt)} 字，超 2000")

    for art in plan.videos:
        n = len(art.prompt)
        if n > 2000:
            rep.add("F22", art.label, f"提示词 {n} 字，超 2000；先压场景描述")
        elif n > 1850:
            rep.add("F22", art.label, f"提示词 {n} 字，接近 2000 上限")
        for w in need_hand + need_human + need_text:
            if w not in art.prompt:
                rep.add("F12" if w in need_hand else ("F14" if w in need_human else "F19"), art.label, f"负向缺「{w}」")
        if scale_key not in art.prompt:
            rep.add("F16", art.label, "缺尺度常量")
        for s in subs:
            t = str(s.get("text") or "")
            if not t or len(t) < 3:
                continue
            if t in art.prompt:
                rep.add("F19", art.label, f"字幕「{t}」出现在视频提示词里，会被烧进画面")
        if re.search(r"「[^」]{1,12}」", art.prompt):
            rep.add("F19", art.label, "提示词里有引号文案；模型会照画")
        if card["format"].get("reference_way") != "reference":
            rep.add("F24", art.label, "本线只验证过 reference 模式；不要改 frames")
        own = {art.id, f"node-g{art.seg + 1}", f"node-k{art.seg + 1}"}
        allowed = set(plan.roles["refs"].values()) | set(plan.roles["companions"].values()) | own
        for r in art.refs:
            if r not in allowed:
                rep.add("F23", art.label, f"参考图 {r} 不是本段 K/分镜/角色图；整帧会抢构图")
