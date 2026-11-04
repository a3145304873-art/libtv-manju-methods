# -*- coding: utf-8 -*-
"""做菜线常量与翻车登记表。

原则：能写成常量的，不让模型自由发挥；能代码拦的，不靠提示词自觉。
"""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "0.2.0"
SCHEMA = "cookline/recipe@2"

ROOT = Path(__file__).resolve().parent
FAILURES = json.loads((ROOT / "rules" / "failures.json").read_text(encoding="utf-8"))["failures"]
FAILURE_BY_ID = {f["id"]: f for f in FAILURES}

# ---------------- 默认值：作为旧卡/新卡的回退值，不规定创作段数 ----------------
DEFAULT_FORMAT = {
    "segments": 0,             # 由 segments[] 实际长度计算
    "segment_seconds": 15,     # 仅供旧卡兼容；新卡逐段填写 duration_seconds
    "beats": 4,                # 旧字段兼容；新卡各段拍数独立
    "aspect": "16:9",
    "grid_cells": 3,           # 旧卡兼容回退；新卡按段指定 storyboard_frames
    "video_model": "seedance-2.0-mini",
    "image_model": "gpt-image-2",
    "resolution": "720p",
    "reference_way": "reference",
}

SEGMENT_ROLES: list[str] = []

# ---------------- 提示词常量 ----------------

CAUSAL = (
    "食材、工具和场景状态只能通过符合本菜工艺的可见动作产生或改变；"
    "不许结果先于过程，不许道具凭空出现或消失"
)

QUANTITY = (
    "食材种类、数量与用量以本卡菜谱和账本为准；"
    "数量或容器状态变化必须有对应可见动作，镜头间不得无故增减"
)

CONTINUITY = (
    "镜头之间接着上一镜往下走——切好的东西不再变回整颗，用掉的原料不凭空回来，"
    "手里的东西要和本镜动作对应，换手要看见放下再拿起；"
    "上一镜结束时是什么状态，下一镜开始就必须还是那个状态"
)

TOOL_RULE = (
    "每件工具按本卡标明的形态与用途操作，不得在动作中变形或互相替代；"
    "拿起、放下和换工具都要有可见动作"
)

NEG_HANDS = "多余手臂、第三只手、多双手、四只手、六只手、背后长手"

NEG_TEXT = "字幕、文字、水印、logo、标题、标签、贴纸、画中字、分行字幕"

NEG_IMG_BASE = (
    "人类、人手、人类手掌、五指手指、指甲、人的小臂、握刀的真人手、毛发、"
    "比例失真、角色复制、第二只角色、道具重复、"
    "文字、水印、logo、边框、道具穿模、厨具悬空、"
    "未加工食材直接变成加工完成的状态、火未点即有火焰、杂物堆积、"
    "脏污油腻、微缩模型俯视感、切好的原料又变回整颗、整颗原料出现在已切好的砧板上、"
    "原料凭空回来、手持物跳变、未放下就换工具、砧板出现在地面、灶与桌的位置互换、"
    "背景换到另一个地方、出现该角落没有的器具"
)

NEG_VID_BASE = (
    "人类、人手、五指、指甲、真人手握刀、多余角色、第二只角色、"
    "比例失真、瞬移、变形、角色复制、道具复制、字幕、文字、水印、BGM旋律、说话、"
    "动作错误或重复、道具穿模、无因之果、"
    "食材凭空出现或消失、火未点即有火、"
    "杂物堆积、切好的菜变回整颗、手持物跳变、砧板位置移动、背景换景"
)

BREATHE_FORBIDDEN = (
    "拿起", "放下", "端起", "倒入", "倒进", "放进", "放入", "切开", "切成", "切好",
    "掰开", "盖上", "掀开", "打开", "走向", "走到", "推给", "递给", "装盘", "翻炒",
    "撒", "舀", "挖", "洗", "剥", "揉", "搅",
)

INSERT_VERBS = ("放入", "放进", "下锅", "装盘", "倒进", "倒入", "塞进", "投入", "盛进")
PUTDOWN_VERBS = ("放下", "放在", "放回", "搁下", "搁在", "丢下", "递给", "推到一边")
PICKUP_VERBS = ("拿起", "端起", "抱起", "握住", "抓住", "接过", "捧起", "提起", "握", "抱住")
EAT_VERBS = ("咬", "嚼", "吃", "喝", "尝")
SHARE_WORDS = ("分", "留", "一半", "端给", "推给", "拨", "碟", "盘里", "分享", "给小狗")

WHOLE_STATES = ("whole", "intact", "整颗", "完整", "整只", "整条", "未切")
CUT_STATES = ("cut", "diced", "sliced", "切好", "切碎", "丁", "片", "丝", "碎")
CLOSED_STATES = ("closed", "covered", "盖着", "盖好", "关着", "合上", "闭上", "封住")


def scale(character: dict) -> str:
    height = character.get("height_cm")
    who = f"它身高约 {height} 厘米，" if height else ""
    return (
        f"尺度：{who}这是一个为它配好的小世界——锅、盆、坛子这些大件比它高，"
        "但擀面杖、碗、刀、碟、篮都是按它的身量配的，它抱得动、端得稳、够得着；"
        "不要把道具画成人类尺寸的巨物，也不要把画面做成微缩模型的俯视感"
    )


def tone(recipe: dict) -> str:
    return recipe.get("format", {}).get("tone") or (
        "基调按本集设计；动作、镜头、光线和声音服务于这道菜及角色当下的生活情境，"
        "不预设慢节奏、治愈氛围或分享结尾"
    )


def quantity(recipe: dict) -> str:
    constraints = recipe.get("cooking_constraints") or []
    if isinstance(constraints, str):
        constraints = [constraints]
    extra = "；".join(str(x).strip() for x in constraints if str(x).strip())
    return QUANTITY + (f"；本菜特别要求：{extra}" if extra else "")


def hands(character: dict) -> str:
    shape = character.get("hands") or "两只短圆的、没有手指的手"
    return (
        f"它只有{shape}，夹、抱、按、推都用这两只手；"
        "画面里绝不出现人类的手、手掌、五指、指甲、人的小臂或穿袖子的手"
    )


def character_line(character: dict) -> str:
    name = character.get("name", "角色")
    desc = character.get("desc", "").strip()
    speech = character.get("speech") or "不说话，只发一个很轻的音"
    eyes = character.get("eyes")
    parts = [f"{name}。{desc}".strip()]
    if eyes:
        parts.append(f"眼睛：{eyes}")
    parts.append(f"声音：{speech}，没有台词。")
    return "\n".join(parts)


def _neg(parts: list[str], extra: str = "") -> str:
    raw = "、".join(p for p in parts if p)
    if extra:
        raw += "、" + extra
    terms = [t.strip() for t in raw.split("、") if t.strip()]
    return "负向：" + "、".join(dict.fromkeys(terms)) + "。"


def negative_img(extra: str = "") -> str:
    return _neg([NEG_IMG_BASE, NEG_HANDS, NEG_TEXT], extra)


def negative_vid(extra: str = "") -> str:
    return _neg([NEG_VID_BASE, NEG_HANDS, NEG_TEXT], extra)


def human_checks() -> list[dict]:
    return [f for f in FAILURES if f["layer"] == "human"]
