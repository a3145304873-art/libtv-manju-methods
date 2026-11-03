# -*- coding: utf-8 -*-
"""story / profile / finding 的数据模型与载入。"""
import json
from dataclasses import dataclass, field
from pathlib import Path

from .rules import RULES

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = PLUGIN_ROOT / "profiles"
ASSETS_FILE = PLUGIN_ROOT / "assets.json"

WORD_KEYS = ("spelling", "ipa", "zh", "meaning")
LINK_TYPES = ("object", "consequence", "function")
SPEAKER_ALIAS = {"黄蛋": "huangdan", "心易": "xinyi", "旁白": "narrator"}
LINK_LABEL = {
    "object": "字面对象就是词义",
    "consequence": "这句话的后果就是词义",
    "function": "这句话的作用就是词义",
}


@dataclass
class Finding:
    rule: str
    level: str
    message: str
    where: str = ""

    @property
    def title(self):
        return RULES.get(self.rule, {}).get("title", "")

    @property
    def fix(self):
        return RULES.get(self.rule, {}).get("fix", "")

    @property
    def case(self):
        return RULES.get(self.rule, {}).get("case", "")

    def as_dict(self):
        return {
            "rule": self.rule,
            "level": self.level,
            "title": self.title,
            "message": self.message,
            "where": self.where,
            "fix": self.fix,
            "case": self.case,
        }


@dataclass
class CheckResult:
    subject: str
    findings: list = field(default_factory=list)

    def add(self, rid, message, where=""):
        level = RULES.get(rid, {}).get("level", "WARN")
        self.findings.append(Finding(rid, level, message, where))

    def extend(self, findings):
        self.findings.extend(findings)

    def count(self, level):
        return sum(1 for f in self.findings if f.level == level)

    @property
    def ok(self):
        return self.count("ERROR") == 0

    @property
    def status(self):
        if self.count("ERROR"):
            return "FAIL"
        if self.count("WARN"):
            return "PASS_WITH_WARNINGS"
        return "PASS"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_profile(profile_id):
    path = PROFILE_DIR / f"{profile_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"未知 profile: {profile_id}（{path}）")
    return read_json(path)


def speaker_id(name):
    """story 里可以写中文名，内部统一成 huangdan/xinyi/narrator。"""
    if not isinstance(name, str):
        return ""
    return SPEAKER_ALIAS.get(name.strip(), name.strip())


def _normalize_speakers(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("speaker"), str):
            obj["speaker"] = speaker_id(obj["speaker"])
        for value in obj.values():
            _normalize_speakers(value)
    elif isinstance(obj, list):
        for value in obj:
            _normalize_speakers(value)


def load_story(path):
    story = read_json(path)
    story.setdefault("schema", 1)
    _normalize_speakers(story)
    return story


def load_assets():
    return read_json(ASSETS_FILE)["assets"]


def screen_range(profile):
    s = profile["screen"]
    return float(s["start"]), float(s["end"])


def card_range(profile):
    c = profile["card"]
    return float(c["start"]), float(c["end"])


def segments_of(story, profile):
    """返回 [(seg_id, start, end, [beats...]), ...]，harmonic15 视为单段。"""
    if profile.get("shots"):
        s, e = screen_range(profile)
        return [(None, s, e, list(story.get("beats") or []))]
    segs = []
    for seg in story.get("segments") or []:
        segs.append((seg.get("id"), float(seg["start"]), float(seg["end"]), list(seg.get("beats") or [])))
    return segs


def beats_abs(story, profile):
    """展平后的拍，时间为整支片绝对时间。"""
    out = []
    for seg_id, seg_start, seg_end, beats in segments_of(story, profile):
        for i, b in enumerate(beats):
            out.append({
                "seg": seg_id,
                "index": i,
                "start": round(float(b["start"]) + (0 if profile.get("shots") else seg_start), 3),
                "end": round(float(b["end"]) + (0 if profile.get("shots") else seg_start), 3),
                "beat": b,
            })
    return out


def all_lines(story, profile):
    """所有台词（含旁白），带说话人与绝对时间。"""
    lines = []
    for item in beats_abs(story, profile):
        b = item["beat"]
        for key in ("line", "lines"):
            val = b.get(key)
            if not val:
                continue
            if isinstance(val, str):
                val = [val]
            for text in val:
                lines.append({
                    "speaker": b.get("speaker", ""),
                    "text": text,
                    "start": item["start"],
                    "end": item["end"],
                    "seg": item["seg"],
                })
    narration = story.get("narration")
    if narration and narration.get("text"):
        n = float(narration.get("start") or 0)
        e = float(narration.get("end") or n + 1)
        lines.append({"speaker": "narrator", "text": narration["text"], "start": n, "end": e, "seg": narration.get("seg")})
    for line in lines:
        line["speaker"] = speaker_id(line["speaker"])
    return lines


def word_rel(story, subdir=""):
    return (Path(subdir) if subdir else Path()) / f"{story['id']}"


def token(node_id):
    return "{{" + node_id + "}}"
