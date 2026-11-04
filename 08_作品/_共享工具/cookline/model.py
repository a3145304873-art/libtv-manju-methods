# -*- coding: utf-8 -*-
"""菜谱卡读取、归一化与旧卡迁移。"""
from __future__ import annotations

import copy
import hashlib
import json
import math
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
    fmt["segments"] = len(segs)
    if segs:
        first = segs[0].get("beats") or segs[0].get("shots") or []
        # 保留首段拍数作为旧格式兼容提示；新格式允许各段拍数不同。
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

    elapsed = 0.0
    for si, seg in enumerate(segs):
        seg["beats"] = seg.get("beats") or seg.get("shots") or []
        seg["carry"] = [str(x) for x in (seg.get("carry") or [])]
        seg["with"] = [str(x) for x in (seg.get("with") or [])]
        seg.setdefault("key", f"v{si + 1}")
        seg.setdefault("title", f"第{si + 1}段")
        seg.setdefault("area", "")
        seg.setdefault("sound", "")
        duration = seg.get("duration_seconds", seg.get("duration"))
        if duration is None:
            old_range = parse_range(seg.get("range"))
            duration = (old_range[1] - old_range[0]) if old_range else (fmt.get("segment_seconds") or 0)
        try:
            seg["duration_seconds"] = float(duration)
        except (TypeError, ValueError):
            seg["duration_seconds"] = 0.0
            seg["duration_invalid"] = True
        if not math.isfinite(seg["duration_seconds"]):
            seg["duration_seconds"] = 0.0
            seg["duration_invalid"] = True
        seg["start_sec"] = elapsed
        seg["end_sec"] = elapsed + seg["duration_seconds"]
        seg["range"] = f"{seg['start_sec']:g}–{seg['end_sec']:g}s"
        beats = []
        for bi, b in enumerate(seg["beats"]):
            b = _clean_beat(b, bi, bi == len(seg["beats"]) - 1)
            rng = parse_range(b.get("t"))
            if rng is None:
                b["time_inferred"] = True
                step = seg["duration_seconds"] / max(len(seg["beats"]), 1)
                rng = (round(bi * step, 3), round((bi + 1) * step, 3))
                b["t"] = f"{rng[0]:g}–{rng[1]:g}"
            b["start_sec"], b["end_sec"] = rng
            b["abs_start"] = seg["start_sec"] + rng[0]
            b["abs_end"] = seg["start_sec"] + rng[1]
            beats.append(b)
        seg["beats"] = beats
        frames = seg.get("storyboard_frames")
        if frames:
            normalized_frames = []
            for fi, frame in enumerate(frames):
                if isinstance(frame, (int, float, str)):
                    frame = {"at": frame}
                at = frame.get("at", frame.get("t", 0))
                try:
                    if isinstance(at, str):
                        parsed = parse_range(at)
                        at = parsed[0] if parsed else float(at.strip().rstrip("s秒"))
                    at = float(at)
                    if not math.isfinite(at):
                        raise ValueError("non-finite storyboard time")
                except (TypeError, ValueError):
                    at = -1.0
                    seg["storyboard_frames_invalid"] = True
                normalized_frames.append({
                    "at": at,
                    "description": str(frame.get("description") or frame.get("visual") or "").strip(),
                    "label": str(frame.get("label") or f"{fi + 1}"),
                })
            seg["storyboard_frames"] = normalized_frames
        else:
            cells = fmt.get("grid_cells")
            if cells is not None:
                count = max(1, int(cells))
                times = [round(i * seg["duration_seconds"] / count, 3) for i in range(count)]
            elif len(beats) == 1:
                seg["storyboard_frames_inferred"] = True
                times = [0.0, seg["duration_seconds"]]
            else:
                seg["storyboard_frames_inferred"] = True
                times = [0.0] + [round((b["start_sec"] + b["end_sec"]) / 2, 3) for b in beats[1:]]
            seg["storyboard_frames"] = [
                {"at": t, "description": "", "label": f"{fi + 1}"}
                for fi, t in enumerate(times)
            ]
        # 旧卡的 subs 是整段一个字符串数组；按顺序落到动作拍上，仍只进 SRT。
        legacy_subs = [str(x) for x in (seg.get("subs") or []) if str(x).strip()]
        actions = [b for b in beats if b["kind"] == "action"]
        for idx, text in enumerate(legacy_subs):
            if idx < len(actions) and not actions[idx].get("sub"):
                actions[idx]["sub"] = text
        elapsed += seg["duration_seconds"]

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
    r["_total_seconds"] = elapsed
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
