# -*- coding: utf-8 -*-
"""门禁自测：每个反例都必须被对应规则抓住。

门禁本身也要有证据，否则“全绿”只说明检查器是空的。
运行：py -3 -m unittest discover -s tests -v
"""
import copy
import sys
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN))

from lib import builder  # noqa: E402
from lib.check_canvas import check_canvas  # noqa: E402
from lib.check_story import check_story  # noqa: E402
from lib.model import load_profile, load_story  # noqa: E402


def baseline_story():
    story = load_story(PLUGIN / "stories" / "pest-15s.json")
    return story, load_profile(story["profile"])


def hits(result):
    return {f.rule for f in result.findings if f.level in ("ERROR", "WARN")}


class StoryGates(unittest.TestCase):
    def test_baseline_passes(self):
        story, profile = baseline_story()
        self.assertTrue(check_story(story, profile).ok)

    def test_xinyi_speaks_human(self):
        story, profile = baseline_story()
        story["beats"][4]["line"] = "你连蚊子都打不到。"
        self.assertIn("G06", hits(check_story(story, profile)))

    def test_xinyi_bracket(self):
        story, profile = baseline_story()
        story["beats"][4]["line"] = "咔啵（收到了）"
        self.assertIn("G07", hits(check_story(story, profile)))

    def test_huangdan_explains(self):
        story, profile = baseline_story()
        story["beats"][1]["line"] = "pest 的意思是害虫。"
        self.assertIn("G08", hits(check_story(story, profile)))

    def test_timing_shape(self):
        story, profile = baseline_story()
        story["beats"][0]["end"] = 4
        self.assertIn("G04", hits(check_story(story, profile)))

    def test_subtitle_out_of_range(self):
        story, profile = baseline_story()
        story["subtitles"].append({"start": 13.0, "end": 14.0, "text": "害虫"})
        self.assertIn("G16", hits(check_story(story, profile)))

    def test_on_screen_text(self):
        story, profile = baseline_story()
        story["beats"][0]["on_screen_text"] = "pest"
        self.assertIn("G17", hits(check_story(story, profile)))

    def test_no_rescue_off(self):
        story, profile = baseline_story()
        story["continuity"]["no_rescue"] = False
        self.assertIn("G13", hits(check_story(story, profile)))

    def test_missing_turn(self):
        story, profile = baseline_story()
        del story["turn"]
        self.assertIn("G21", hits(check_story(story, profile)))

    def test_turn_out_of_range(self):
        story, profile = baseline_story()
        story["turn"]["at"] = 0
        self.assertIn("G21", hits(check_story(story, profile)))

    def test_missing_stakes(self):
        story, profile = baseline_story()
        del story["stakes"]
        self.assertIn("G22", hits(check_story(story, profile)))

    def test_gambling_framing_warn(self):
        story, profile = baseline_story()
        story["stakes"]["cost"] = "输了就把小金杯赔给对方"
        self.assertIn("G23", hits(check_story(story, profile)))

    def test_missing_signoff_when_card_in_video(self):
        story, profile = baseline_story()
        story["card"]["in_video"] = True
        self.assertIn("G24", hits(check_story(story, profile)))

    def test_signoff_valid_passes(self):
        story, profile = baseline_story()
        story["card"]["in_video"] = True
        story["signoff"] = {"speaker": "黄蛋", "text": "pest，拍死它，害虫。你记住了吗？"}
        self.assertNotIn("G24", hits(check_story(story, profile)))

    def test_baseline_has_no_gamble_words(self):
        story, profile = baseline_story()
        self.assertNotIn("G23", hits(check_story(story, profile)))

    def test_card_extra_row(self):
        story, profile = baseline_story()
        story["card"]["tagline"] = "跟着黄蛋记单词"
        self.assertIn("G11", hits(check_story(story, profile)))

    def test_scores_low(self):
        story, profile = baseline_story()
        story["scores"] = {"natural": 10, "meaning": 10, "visual": 10, "character": 10}
        self.assertIn("G12", hits(check_story(story, profile)))

    def test_prop_without_first_frame(self):
        story, profile = baseline_story()
        story["props"][0]["first_frame"] = False
        self.assertIn("G05", hits(check_story(story, profile)))

    def test_hook_without_evidence(self):
        story, profile = baseline_story()
        story["hook"]["why_natural"] = "好听"
        self.assertIn("G02", hits(check_story(story, profile)))


class CanvasGates(unittest.TestCase):
    def setUp(self):
        story, profile = baseline_story()
        self.story = story
        self.profile = profile
        self.canvas, self.info = builder.build_canvas(story, profile)

    def test_baseline_passes(self):
        self.assertTrue(check_canvas(self.canvas, self.story, self.profile).ok)

    def _video(self):
        return next(n for n in self.canvas["canvas"]["nodes"] if n["type"] == "gen-video")

    def test_token_without_reference(self):
        video = self._video()
        refs = video["params"]["model_params"]["reference_images"]
        video["params"]["model_params"]["reference_images"] = [
            r for r in refs if r["node_id"] != self.info["node_ids"]["R00"]]
        self.assertIn("C04", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_missing_edge(self):
        before = len(self.canvas["canvas"]["edges"])
        self.canvas["canvas"]["edges"].pop()
        self.assertEqual(len(self.canvas["canvas"]["edges"]), before - 1)
        self.assertIn("C04", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_forbidden_video_edge(self):
        video_id = self.info["node_ids"]["V1"]
        self.canvas["canvas"]["edges"].append({
            "id": "edge-deadbeef", "sourceNodeId": video_id,
            "targetNodeId": video_id, "sourceHandle": "output", "targetHandle": "input"})
        self.assertIn("C06", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_first_frame_not_named(self):
        video = self._video()
        video["params"]["model_params"]["prompt"] = video["params"]["model_params"]["prompt"].replace(
            "【首帧锁定】", "")
        self.assertIn("C12", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_generic_pupil_in_negative(self):
        video = self._video()
        video["params"]["model_params"]["prompt"] += "\n负向：瞳孔、高光点。"
        self.assertIn("P02", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_missing_hand_lock(self):
        video = self._video()
        video["params"]["model_params"]["prompt"] = video["params"]["model_params"]["prompt"].replace(
            "两只短手", "手")
        self.assertIn("P03", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_wrong_duration(self):
        video = self._video()
        video["params"]["model_params"]["duration"] = 10
        self.assertIn("P09", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_missing_prop(self):
        video = self._video()
        video["params"]["model_params"]["prompt"] = video["params"]["model_params"]["prompt"].replace(
            "水果盘", "盘子")
        self.assertIn("P05", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_group_with_internal_edge(self):
        groups = self.canvas["canvas"]["groups"]
        video_group = next(g for g in groups if "视频" in g["label"])
        k_id = self.info["node_ids"]["K_A"]
        video_group["nodeIds"].append(k_id)
        self.assertIn("C07", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_bad_asset_url(self):
        node = next(n for n in self.canvas["canvas"]["nodes"] if n["type"] == "input-image")
        node["outputs"][0]["value"] = "data:image/png;base64,AAAA"
        self.assertIn("C18", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_prop_sheet_with_word(self):
        prop = next(n for n in self.canvas["canvas"]["nodes"]
                    if n["type"] == "gen-image" and "道具" in n["meta"]["label"])
        prop["params"]["model_params"]["prompt"] += "\n参考词：pest。"
        self.assertIn("P13", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_missing_storyboard(self):
        nodes = self.canvas["canvas"]["nodes"]
        idx = next(i for i, n in enumerate(nodes) if "分镜" in n["meta"]["label"])
        nodes.pop(idx)
        self.assertIn("C20", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_storyboard_first_cell_missing_prop(self):
        board = next(n for n in self.canvas["canvas"]["nodes"] if "分镜" in n["meta"]["label"])
        prompt = board["params"]["model_params"]["prompt"]
        board["params"]["model_params"]["prompt"] = prompt.replace("苍蝇拍", "拍子")
        self.assertIn("P14", hits(check_canvas(self.canvas, self.story, self.profile)))

    def test_card_in_video_wiring(self):
        story = copy.deepcopy(self.story)
        story["card"]["in_video"] = True
        canvas, info = builder.build_canvas(story, self.profile)
        video = next(n for n in canvas["canvas"]["nodes"] if n["type"] == "gen-video")
        mp = video["params"]["model_params"]
        self.assertEqual(mp["duration"], 15)
        kc_id = next(n["id"] for n in canvas["canvas"]["nodes"]
                     if n["type"] == "gen-image" and "KC" in n["meta"]["label"])
        self.assertIn(kc_id, [r["node_id"] for r in mp["reference_images"]])
        self.assertIn(kc_id, mp["prompt"])
        self.assertTrue(any(e["sourceNodeId"] == kc_id for e in canvas["canvas"]["edges"]))

    def test_card_post_by_default(self):
        canvas, info = builder.build_canvas(self.story, self.profile)
        video = next(n for n in canvas["canvas"]["nodes"] if n["type"] == "gen-video")
        mp = video["params"]["model_params"]
        self.assertEqual(mp["duration"], 12)
        kc_id = next(n["id"] for n in canvas["canvas"]["nodes"]
                     if n["type"] == "gen-image" and "KC" in n["meta"]["label"])
        self.assertNotIn(kc_id, [r["node_id"] for r in mp["reference_images"]])


class PromptLength(unittest.TestCase):
    def test_prompt_under_target(self):
        story, profile = baseline_story()
        _, info = builder.build_canvas(story, profile)
        for key, length in info["prompt_lengths"].items():
            self.assertLessEqual(length, 1900, f"{key} prompt {length} 超 1900")


if __name__ == "__main__":
    unittest.main()
