# -*- coding: utf-8 -*-
"""菜谱卡读取、归一化与旧卡迁移。"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

from . import rules

_RANGE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(?:[–—~\-至]|到)\s*([0-9]+(?:\.[0-9]+)?)")


def parse_range(text) -> tuple[float, float] | None:
    if text is None:
        return None
    m = _RANGE.match(str(text))
    if not m:
        return None
    start, end = float(m.group(1)), float(m.group(2))
    if end <= start:
        return None
    return start, end


def load(path: str | Path) -> dict:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8-sig"))
    card = normalize(raw)
    card["_source"] = str(p)
    return card


def _as_refs(character: dict) -> list[dict]:
    refs = character.get("refs")
    if refs:
        out = []
        for i, r in enumerate(refs):
            if isinstance(r, str):
                r = {"url": r}
            out.append({
                "label": r.get("label") or f"参考图{i + 1}",
                "url": r.get("url") or "",
                "width": int(r.get("width") or r.get("w") or 1024),
                "height": int(r.get("height") or r.get("h") or 1024),
            })
        return out
    if character.get("ref_url"):
        return [{
            "label": character.get("ref_label") or "标准图",
            "url": character["ref_url"],
            "width": int(character.get("ref_width") or 1305),
            "height": int(character.get("ref_height") or 1495),
        }]
    return []


def _clean_beat(beat: dict, index: int, last: bool) -> dict:
    b = dict(beat)
    b["kind"] = b.get("kind") or ("breathe" if last else "action")
    if b["kind"] == "action":
        if b.get("text") and not b.get("do"):
            b["do"] = str(b["text"]).strip()
            b["legacy_text"] = True
        for k in ("start", "do", "end"):
            b[k] = str(b.get(k) or "").strip()
    else:
        b["desc"] = str(b.get("desc") or "").strip()
    b.setdefault("sub", "")
    for k in ("props", "enter", "exit", "hand"):
        if b.get(k) is not None:
            b[k] = [str(x) for x in b[k]]
    for k in ("counts", "counts_after", "state", "state_after"):
        if isinstance(b.get(k), dict):
            b[k] = {str(kk): vv for kk, vv in b[k].items()}
    return b


def normalize(raw: dict) -> dict:
    r = copy.deepcopy(raw)
    raw_fmt = raw.get("format") or {}
    r["_legacy"] = bool(raw_fmt.get("legacy")) or ("schema" not in raw and "format" not in raw)
    segs = r.get("segments") or []
    fmt = dict(rules.DEFAULT_FORMAT)
    fmt.update(raw_fmt)
    fmt["segments"] = int(fmt.get("segments") or 4)
    if segs:
        first = segs[0].get("beats") or segs[0].get("shots") or []
        # 拍数按卡推断：16 拍（3 动作+呼吸）或 12 拍（3 动作，慢档）都合法。
        fmt["beats"] = int(raw_fmt.get("beats") or len(first) or 4)
    fmt["style"] = str(fmt.get("style") or ("16" if int(fmt["beats"]) == 4 else "12"))
    r["format"] = fmt

    ch = r.setdefault("character", {})
    ch["refs"] = _as_refs(ch)
    ch["height_cm"] = ch.get("height_cm") or ch.get("height") or 30

    for i, a in enumerate(r.get("areas") or []):
        a.setdefault("key", f"area{i + 1}")
        a["key"] = str(a["key"])
        a.setdefault("name", a["key"])
        a.setdefault("desc", "")
        a.setdefault("layout", "")
        a.setdefault("props_here", [])
        a["props_here"] = [str(x) for x in a["props_here"]]

    props = []
    for i, p in enumerate(r.get("props") or []):
        p = dict(p)
        key = str(p.get("key") or p.get("label") or p.get("id") or f"prop{i + 1}")
        p["key"] = key
        p.setdefault("label", key)
        p.setdefault("body", "")
        props.append(p)
    r["props"] = props

    for i, c in enumerate(r.get("companions") or []):
        c.setdefault("key", c.get("id") or f"companion{i + 1}")
        c.setdefault("label", c["key"])
        c.setdefault("desc", "")

    total = float(fmt["segment_seconds"]) * len(segs)
    for si, seg in enumerate(segs):
        seg["beats"] = seg.get("beats") or seg.get("shots") or []
        seg["carry"] = [str(x) for x in (seg.get("carry") or [])]
        seg["with"] = [str(x) for x in (seg.get("with") or [])]
        seg.setdefault("key", f"v{si + 1}")
        seg.setdefault("title", rules.SEGMENT_ROLES[si] if si < len(rules.SEGMENT_ROLES) else f"第{si + 1}段")
        seg.setdefault("area", "")
        seg.setdefault("sound", "")
        seg.setdefault("range", f"{si * fmt['segment_seconds']}–{(si + 1) * fmt['segment_seconds']}s")
        beats = []
        for bi, b in enumerate(seg["beats"]):
            b = _clean_beat(b, bi, bi == len(seg["beats"]) - 1)
            rng = parse_range(b.get("t"))
            if rng is None:
                step = float(fmt["segment_seconds"]) / max(len(seg["beats"]), 1)
                rng = (round(bi * step, 3), round((bi + 1) * step, 3))
                b["t"] = f"{rng[0]:g}–{rng[1]:g}"
            b["start_sec"], b["end_sec"] = rng
            b["abs_start"] = si * float(fmt["segment_seconds"]) + rng[0]
            b["abs_end"] = si * float(fmt["segment_seconds"]) + rng[1]
            beats.append(b)
        seg["beats"] = beats
        # 旧卡的 subs 是整段一个字符串数组；按顺序落到动作拍上，仍只进 SRT。
        legacy_subs = [str(x) for x in (seg.get("subs") or []) if str(x).strip()]
        actions = [b for b in beats if b["kind"] == "action"]
        for idx, text in enumerate(legacy_subs):
            if idx < len(actions) and not actions[idx].get("sub"):
                actions[idx]["sub"] = text

    post = r.setdefault("post", {})
    if "subtitles" not in post:
        subs = []
        for seg in segs:
            for b in seg["beats"]:
                if b.get("sub"):
                    s = b["abs_start"] + 0.3
                    e = min(b["abs_end"] - 0.3, s + 2.4)
                    if e <= s + 0.6:
                        e = s + 0.6
                    subs.append({"start": round(s, 2), "end": round(e, 2), "text": b["sub"]})
        post["subtitles"] = subs
    for s in post.get("subtitles") or []:
        s["start"] = float(s.get("start") or 0)
        s["end"] = float(s.get("end") or 0)
        s["text"] = str(s.get("text") or "")
    r["_total_seconds"] = total
    return r


def recipe_hash(card: dict) -> str:
    """只对内容取哈希，不算路径与内部字段；卡一改，签核自动失效。"""
    clean = {k: v for k, v in card.items() if not str(k).startswith("_")}
    blob = json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def migrate(path: str | Path, out: str | Path) -> dict:
    card = load(path)
    clean = {k: v for k, v in card.items() if not str(k).startswith("_")}
    clean["schema"] = rules.SCHEMA
    clean["migrated_from"] = str(path)
    clean.setdefault("format", {})
    clean["format"]["legacy"] = True
    Path(out).write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return clean
