# -*- coding: utf-8 -*-
"""构建、画布审计与闸门的端到端测试。"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from cookline import canvas as canvas_mod
from cookline import checks, cli, gate, model
from cookline.compose import compose

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "templates" / "recipe.demo.json"


def _prepare(tmp: Path) -> Path:
    recipe = tmp / "recipe.json"
    shutil.copyfile(DEMO, recipe)
    return recipe


def _build(recipe: Path, out: Path) -> int:
    return cli.main(["build", str(recipe), "-o", str(out)])


def test_build_writes_canvas_runlist_sidecar_srt(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["canvas"]["nodes"]) == 33
    assert len(data["canvas"]["groups"]) == 7
    videos = [n for n in data["canvas"]["nodes"] if n["type"] == "gen-video"]
    assert len(videos) == 4
    assert all(len(v["params"]["model_params"]["prompt"]) < 2000 for v in videos)
    assert out.with_name(out.name + ".runlist.json").exists()
    assert out.with_name(out.name + ".cookline.json").exists()
    assert "昨天的饭" in out.with_suffix(".srt").read_text(encoding="utf-8")

    card = model.load(recipe)
    side = json.loads(out.with_name(out.name + ".cookline.json").read_text(encoding="utf-8"))
    assert side["recipe_sha256"] == model.recipe_hash(card)
    assert side["prompt_digest"] == canvas_mod.prompt_digest(data)
    assert canvas_mod.audit(data, card, side).ok()


def test_gate_order_and_runlist(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    card = model.load(recipe)

    with pytest.raises(gate.GateError):
        gate.approve(recipe, card, "storyboard", "跳过场景")
    gate.approve(recipe, card, "assets", "场景同雾同光向，道具白手")
    with pytest.raises(gate.GateError):
        gate.runlist_nodes(recipe, card, "storyboard")
    gate.approve(recipe, card, "storyboard", "第一格道具齐，站位对")
    gate.approve(recipe, card, "keys", "四张 K 构图都对")
    gate.approve(recipe, card, "videos", "跑前最后确认")
    nodes = gate.runlist_nodes(recipe, card, "videos")
    assert nodes == ["node-v1", "node-v2", "node-v3", "node-v4"]


def test_editing_card_makes_gate_stale(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    card = model.load(recipe)
    gate.approve(recipe, card, "assets", "场景与道具确认")

    raw = json.loads(recipe.read_text(encoding="utf-8"))
    raw["series_title"] += "（改）"
    recipe.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    changed = model.load(recipe)
    rows, _ = gate.status(recipe, changed)
    assert rows[0]["state"] == "STALE"
    with pytest.raises(gate.GateError):
        gate.runlist_nodes(recipe, changed, "assets")


def test_doctor_detects_hand_edit(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    card = model.load(recipe)
    side = json.loads(out.with_name(out.name + ".cookline.json").read_text(encoding="utf-8"))
    data = json.loads(out.read_text(encoding="utf-8"))
    for n in data["canvas"]["nodes"]:
        if n["id"] == "node-v1":
            n["params"]["model_params"]["prompt"] += "\n手改一句"
            break
    rep = canvas_mod.audit(data, card, side)
    assert not rep.ok()
    assert any(i.fid == "F26" and "digest" in i.message for i in rep.errors)


def test_audit_catches_missing_human_hand_negative(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    card = model.load(recipe)
    data = json.loads(out.read_text(encoding="utf-8"))
    for n in data["canvas"]["nodes"]:
        if n["id"] == "node-v1":
            mp = n["params"]["model_params"]
            mp["prompt"] = mp["prompt"].replace("人类的手", "人类", 1)
            break
    rep = canvas_mod.audit(data, card, None)
    assert any(i.fid == "F14" for i in rep.errors)


def test_audit_catches_cross_segment_reference(tmp_path):
    recipe = _prepare(tmp_path)
    out = tmp_path / "recipe.monet"
    assert _build(recipe, out) == 0
    card = model.load(recipe)
    data = json.loads(out.read_text(encoding="utf-8"))
    for n in data["canvas"]["nodes"]:
        if n["id"] == "node-v1":
            refs = n["params"]["model_params"]["reference_images"]
            for r in refs:
                if r["node_id"] == "node-k1":
                    r["node_id"] = "node-k2"
            break
    rep = canvas_mod.audit(data, card, None)
    assert any(i.fid == "F23" for i in rep.errors)


def test_character_negatives_reach_video_prompts():
    card = model.load(DEMO)
    card["character"]["negatives"] = ["黑瞳", "眨眼", "橘子掉落"]
    plan = compose(card)
    assert plan.videos
    for video in plan.videos:
        assert "黑瞳" in video.prompt
        assert "眨眼" in video.prompt
        assert "橘子掉落" in video.prompt


def test_keyframe_wires_beat0_props_and_videos_do_not():
    card = model.load(DEMO)
    plan = compose(card)
    prop_ids = {art.id for art in plan.images if art.kind == "prop"}
    keys = {art.seg: art for art in plan.images if art.kind == "key"}
    assert keys[0].seg == 0
    # K1 首拍 props = [陶盆, 木勺, 竹篮] → 三件白底道具全部接入并点名
    assert {"node-p1", "node-p2", "node-p3"} <= set(keys[0].refs)
    for art in plan.images:
        if art.kind != "key":
            continue
        for r in art.refs:
            if r in prop_ids:
                assert f"{{{{{r}}}}}" in art.prompt
    # 道具不进视频、不进分镜（EP01 口径：经 K 帧流入视频）
    for video in plan.videos:
        assert not (set(video.refs) & prop_ids)
    for art in plan.images:
        if art.kind == "grid":
            assert not (set(art.refs) & prop_ids)


def test_build_refuses_legacy_card(tmp_path):
    legacy = ROOT.parents[1] / "心易做菜" / "02_画布" / "recipes" / "EP01-等土豆熟.json"
    if not legacy.exists():
        pytest.skip("legacy card not present")
    assert cli.main(["build", str(legacy), "-o", str(tmp_path / "legacy.monet")]) == 1


def test_three_beat_card_is_a_legal_slow_format(tmp_path):
    """12 拍慢档：3 拍/段，全是动作，不要求呼吸拍。"""
    raw = json.loads(DEMO.read_text(encoding="utf-8"))
    raw["format"]["beats"] = 3
    raw["format"]["style"] = "12"
    for seg in raw["segments"]:
        seg["beats"] = [b for b in seg["beats"] if b["kind"] == "action"]
        seg["beats"][0]["t"] = "0–4"
        seg["beats"][1]["t"] = "4–9"
        seg["beats"][2]["t"] = "9–15"
    recipe = tmp_path / "slow.json"
    recipe.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    card = model.load(recipe)
    rep = checks.check(card, strict=True)
    assert rep.ok(strict=True), rep.text()
