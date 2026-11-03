# -*- coding: utf-8 -*-
"""v9: narration generated inside V2 video (no post narration)."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v8-card-visible.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v9-invideo-narration.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]


def find(prefix):
    return next(n for n in c["nodes"] if prefix in n["meta"].get("label", ""))


V1 = find("【待生成】V1")
V2 = find("【待生成】V2")
S0 = find("S0")

# V1: no narration
mp = V1["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace("无文字/气泡；旁白后期。", "无文字/气泡；**V1 无旁白**，旁白在 V2 视频内生成。")
mp["prompt"] = mp["prompt"].replace("环境声；旁白后期。", "环境声；V1 无旁白。")

# V2: in-video narrator
mp = V2["params"]["model_params"]
mp["prompt"] = mp["prompt"].replace("无文字/气泡；旁白后期。", "无文字/气泡；**画外旁白在视频内生成，不是后期**。")
mp["prompt"] = mp["prompt"].replace(
    "4–6 秒：心易在柜台后僵住，探头：“咔啵？”\n6–7 秒：黄蛋看向心易：“肉丝呢？”\n7–8 秒：心易慢慢缩回后厨窗口：“咔——啵”；**不拿任何食物出来，不补救**。\n8–9 秒：黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；**不说话**；镜尾定格 1s。",
    "4–6 秒：心易在柜台后僵住，探头：“咔啵？”\n"
    "6–7 秒：黄蛋看向心易：“肉丝呢？”\n"
    "6–8 秒：心易慢慢缩回后厨窗口：“咔——啵”；**不拿任何食物出来，不补救**；**画外旁白起**：“没有肉丝，morose，闷闷不乐的。”\n"
    "8–9 秒：黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；**不说话**；**画外旁白**：“你记住了吗？”镜尾定格 1s。",
)
mp["prompt"] = mp["prompt"].replace(
    "【声音】黄蛋人声（短句）；心易只有“咔啵”；环境声；旁白后期。",
    "【声音】黄蛋人声（短句）；心易只有“咔啵”；环境声；**画外旁白（独立成年女声，不是黄蛋/心易）在视频内生成**：6–8 “没有肉丝，morose，闷闷不乐的。”8–9 “你记住了吗？”无 BGM；旁白不是后期。",
)
mp["prompt"] = mp["prompt"].replace(
    "负向：视频内文字/气泡/字幕、",
    "负向：视频内文字/气泡/字幕、旁白由黄蛋/心易念、旁白缺失、旁白后期、旁白声线变成角色、",
)
assert "画外旁白在视频内生成" in mp["prompt"]

# S0
s0 = S0["outputs"][0]
s0["value"] = s0["value"].replace("旁白后期", "旁白在 V2 视频内生成（不是后期）")
s0["value"] += """

【旁白：视频内生成】
- 旁白不做后期；V2 视频内生成独立成年女声画外音。
- 6–8：“没有肉丝，morose，闷闷不乐的。”
- 8–9：“你记住了吗？”
- 提示词明确：画外旁白不是黄蛋/心易的声音；黄蛋只说短句，心易只咔啵。
- 若模型把旁白分给黄蛋/心易、漏掉旁白、或变成对白：重跑 V2；仍不行再兜底用 AI TTS 旁白（仍不是人工后期）。
"""
S0["meta"]["label"] = "S0 制作说明 · 先读"

c["name"] = "蛋仔记单词 · morose 小饭馆版 v9 · 视频内旁白 · 20s"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", OUT)
for n in (V1, V2):
    print(n["meta"]["label"], len(n["params"]["model_params"]["prompt"]))
