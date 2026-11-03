# -*- coding: utf-8 -*-
"""每条历史翻车一个反例：证明校验能拦住，而不是只在文档里写着。"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from cookline import checks, model

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "templates" / "recipe.demo.json"


def fresh() -> dict:
    return model.load(DEMO)


def run(card: dict) -> checks.Report:
    return checks.check(card, strict=True)


def ids(rep: checks.Report) -> set[str]:
    return {i.fid for i in rep.errors} | {i.fid for i in rep.warnings}


def test_demo_is_clean():
    rep = run(fresh())
    assert rep.errors == [], rep.text()
    assert rep.warnings == [], rep.text()


def test_f01_segment_count():
    card = fresh()
    card["segments"] = card["segments"][:3]
    assert "F01" in ids(run(card))


def test_f01_beat_count():
    card = fresh()
    card["segments"][0]["beats"] = card["segments"][0]["beats"][:3]
    assert "F01" in ids(run(card))


def test_f03_breathe_advances_plot():
    card = fresh()
    card["segments"][0]["beats"][3]["desc"] = "空镜：她拿起竹篮走出画面"
    assert "F03" in ids(run(card))


def test_f02_two_areas_in_one_segment():
    card = fresh()
    card["segments"][3]["area2"] = "garden"
    assert "F02" in ids(run(card))


def test_f04_equal_beats():
    card = fresh()
    spans = [(0.0, 3.75), (3.75, 7.5), (7.5, 11.25), (11.25, 15.0)]
    for b, (s, e) in zip(card["segments"][0]["beats"], spans):
        b["t"] = f"{s:g}–{e:g}"
        b["start_sec"], b["end_sec"] = s, e
    assert "F04" in ids(run(card))


def test_f05_missing_layout():
    card = fresh()
    card["areas"][0]["layout"] = ""
    assert "F05" in ids(run(card))


def test_f06_prop_not_in_area():
    card = fresh()
    card["segments"][3]["beats"][0]["props"].append("菜刀")
    got = ids(run(card))
    assert "F06" in got or "F07" in got


def test_f07_prop_from_nowhere():
    card = fresh()
    card["segments"][3]["beats"][0]["props"].append("盐碟")
    assert "F07" in ids(run(card))


def test_f08_container_closed():
    card = fresh()
    beat = card["segments"][2]["beats"][1]
    beat["state"]["陶盆"] = "covered"
    assert "F08" in ids(run(card))


def test_f09_state_jump():
    card = fresh()
    card["segments"][2]["beats"][1]["state"]["火"] = "out"
    assert "F09" in ids(run(card))


def test_f09_companion_first_seen_in_last_segment():
    card = fresh()
    card["segments"][0]["with"] = []
    assert "F09" in ids(run(card))


def test_f10_count_jump():
    card = fresh()
    beat = card["segments"][1]["beats"][1]
    beat["counts"] = {"鸡蛋": 3}
    assert "F10" in ids(run(card))


def test_f11_cut_back_to_whole():
    card = fresh()
    card["segments"][2]["beats"][0]["state"] = {"小葱": "whole"}
    assert "F11" in ids(run(card))


def test_f12_three_hands():
    card = fresh()
    card["segments"][2]["beats"][2]["hand"] = ["木柄锅铲", "竹篮", "陶油壶"]
    assert "F12" in ids(run(card))


def test_f13_full_body_back():
    card = fresh()
    card["segments"][1]["beats"][0]["do"] += "；全身背影走向灶台"
    assert "F13" in ids(run(card))


def test_f15_hand_swap_without_pickup():
    card = fresh()
    beat = card["segments"][2]["beats"][2]
    beat["do"] = "它把篮里的饭倒进锅，推散、翻炒"
    assert "F15" in ids(run(card))


def test_f17_stove_closeup_strips_set():
    card = fresh()
    beat = card["segments"][2]["beats"][1]
    beat["start"] = "近景：锅里的油开始冒烟"
    assert "F17" in ids(run(card))


def test_f18_relight_fire():
    card = fresh()
    card["segments"][3]["beats"][0]["do"] = "它重新生火，再把饭翻面"
    assert "F18" in ids(run(card))


def test_f19_subtitle_in_action():
    card = fresh()
    card["post"]["subtitles"].append({"start": 20, "end": 22, "text": "打散"})
    card["segments"][1]["beats"][2]["do"] += "，把蛋液打散"
    assert "F19" in ids(run(card))


def test_f19_quoted_text():
    card = fresh()
    card["segments"][0]["beats"][0]["do"] += "，篮子上写着「一窝」"
    assert "F19" in ids(run(card))


def test_f20_dialogue():
    card = fresh()
    card["segments"][1]["beats"][0]["line"] = "看好了"
    assert "F20" in ids(run(card))


def test_f21_music():
    card = fresh()
    card["segments"][2]["sound"] = "轻音乐、柴火声"
    assert "F21" in ids(run(card))


def test_f16_giant_character():
    card = fresh()
    card["character"]["height_cm"] = 300
    assert "F16" in ids(run(card))


def test_f30_eating_without_food_on_screen():
    card = fresh()
    card["props"][3]["edible"] = True  # 鸡蛋
    card["segments"][3]["beats"][2]["do"] = "她咬一口慢慢嚼"
    assert "F30" in ids(run(card))


def test_f30_passes_when_food_declared_in_segment():
    card = fresh()
    card["props"][3]["edible"] = True  # 鸡蛋
    card["segments"][3]["beats"][2]["do"] = "她咬一口慢慢嚼"
    card["segments"][3]["beats"][2]["props"] = ["陶盘", "陶碟", "鸡蛋"]
    got = ids(run(card))
    assert "F30" not in got  # F07/F27 会另报，这里只看 F30


def test_f22_prompt_too_long():
    card = fresh()
    card["areas"][2]["desc"] += "，还有" + "很多细节" * 120
    assert "F22" in ids(run(card))


def test_f24_frames_mode():
    card = fresh()
    card["format"]["reference_way"] = "frames"
    assert "F24" in ids(run(card))


def test_f27_ending_without_share():
    card = fresh()
    beat = card["segments"][3]["beats"][2]
    beat["start"] = "起幅：它端着陶盘站在草窝边"
    beat["do"] = "它把陶盘放在灶台上，转身收工"
    beat["end"] = "落幅：它站在灶台边"
    card["segments"][3]["beats"][3]["desc"] = "空镜：灶台熄了，白汽散尽，画面里没有动作"
    assert "F27" in ids(run(card))


def test_legacy_xinyi_audits_without_wall_of_errors():
    legacy = ROOT.parents[1] / "心易做菜" / "02_画布" / "recipes" / "EP01-等土豆熟.json"
    if not legacy.exists():
        pytest.skip("legacy card not present")
    card = model.load(legacy)
    assert card["_legacy"] is True
    rep = checks.check(card)
    assert len(rep.errors) <= 1, rep.text()
    assert any("旧卡" in n for n in rep.notes)


def test_legacy_egg_fried_rice_is_flagged_for_subtitle_overlap():
    legacy = ROOT.parents[1] / "小蛋仔做菜" / "02_画布" / "recipes" / "EP01-蛋炒饭.json"
    if not legacy.exists():
        pytest.skip("legacy card not present")
    rep = checks.check(model.load(legacy))
    assert any(i.fid == "F19" for i in rep.errors)
