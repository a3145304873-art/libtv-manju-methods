# -*- coding: utf-8 -*-
"""做菜线常量与翻车登记表。

原则：能写成常量的，不让模型自由发挥；能代码拦的，不靠提示词自觉。
"""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "0.1.1"
SCHEMA = "cookline/recipe@2"

ROOT = Path(__file__).resolve().parent
FAILURES = json.loads((ROOT / "rules" / "failures.json").read_text(encoding="utf-8"))["failures"]
FAILURE_BY_ID = {f["id"]: f for f in FAILURES}

# ---------------- 格式：对标秃秃／菇子柒的七段式 ----------------
DEFAULT_FORMAT = {
    "segments": 4,
    "segment_seconds": 15,
    "beats": 4,               # 3 动作 + 1 呼吸
    "aspect": "16:9",
    "grid_cells": 3,          # 分镜图 0 / 5 / 10 秒三格
    "video_model": "seedance-2.0-mini",
    "image_model": "gpt-image-2",
    "resolution": "720p",
    "reference_way": "reference",
}

SEGMENT_ROLES = ["取", "理", "火", "揭与分"]

# ---------------- 提示词常量 ----------------

CAUSAL = (
    "画面里出现的东西和状态，都必须由本镜看得见的动作产生——"
    "蛋液只能从磕开的蛋壳里流出来，丁只能由落下的刀切出来，火只能在点火之后出现，"
    "油只能在壶倾斜之后进锅；不许结果先于过程，不许道具凭空出现或消失"
)

QUANTITY = (
    "每种食材按一到两人份，油只铺薄薄一层、不超过锅深十分之一；"
    "碗、碟、刀、锅的数量和位置在一段之内不增不减"
)

CONTINUITY = (
    "镜头之间接着上一镜往下走——切好的东西不再变回整颗，用掉的原料不凭空回来，"
    "手里的东西要和本镜动作对应，换手要看见放下再拿起；"
    "上一镜结束时是什么状态，下一镜开始就必须还是那个状态"
)

TOOL_RULE = (
    "工具：刀只握刀柄、垂直落下切进食物，不按刀背、不悬空；"
    "木棍、筷子写清形状，不许变成木勺、勺子或锅铲；用完放回原处"
)

NEG_HANDS = "多余手臂、第三只手、多双手、四只手、六只手、背后长手"

NEG_TEXT = "字幕、文字、水印、logo、标题、标签、贴纸、画中字、分行字幕"

NEG_IMG_BASE = (
    "人类、人手、人类手掌、五指手指、指甲、人的小臂、握刀的真人手、毛发、"
    "卡通扁平渲染、塑料玩具感、比例失真、角色复制、第二只角色、道具重复、"
    "文字、水印、logo、边框、过曝、广告打光、多个光源、道具穿模、厨具悬空、"
    "蛋液来自未磕开的蛋、完好蛋壳旁出现蛋液、丁凭空出现、油量过多淹没食材、"
    "火未点即有火焰、现代电器、不锈钢台面、塑料收纳盒、瓷砖大白墙、杂物堆积、"
    "脏污油腻、微缩模型俯视感、切好的原料又变回整颗、整颗原料出现在已切好的砧板上、"
    "原料凭空回来、手持物跳变、未放下就换工具、砧板出现在地面、灶与桌的位置互换、"
    "背景换到另一个地方、出现该角落没有的器具"
)

NEG_VID_BASE = (
    "人类、人手、五指、指甲、真人手握刀、多余角色、第二只角色、卡通扁平、塑料玩具感、"
    "比例失真、瞬移、变形、角色复制、道具复制、字幕、文字、水印、BGM旋律、说话、"
    "镜头旋转、镜头漂移、翻车动作、鬼畜重复、道具穿模、无因之果、"
    "食材凭空出现或消失、油量过多、火未点即有火、现代电器、不锈钢、塑料收纳盒、"
    "杂物堆积、切好的菜变回整颗、手持物跳变、砧板位置移动、背景换景"
)

NEG_STOVE = "火塘、石圈、锅放在地上、平地灶、灶台消失"

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
        "基调：治愈、安静、慢。它安安静静地把一件事做完，动作利落但不表演、不夸张、不看镜头；"
        "治愈来自干净的环境、柔和的光、放大的环境声，以及做完之后把吃的分出去"
    )


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
