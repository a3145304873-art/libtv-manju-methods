# -*- coding: utf-8 -*-
"""v10: extend V2 to 13s so the in-video narration fits; total 24s."""
import json
import shutil
from pathlib import Path

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
SRC = ROOT / "02_画布" / "EP01-morose-restaurant-v9-invideo-narration.monet"
OUT = ROOT / "02_画布" / "EP01-morose-restaurant-v10-long.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]


def find(prefix):
    return next(n for n in c["nodes"] if prefix in n["meta"].get("label", ""))


V2 = find("【待生成】V2")
S0 = find("S0")
mp = V2["params"]["model_params"]
mp["duration"] = 13
old = """0–2 秒：{{%s}} 黄蛋站在木桌旁，餐盒**关着**，已经在**木桌桌面**上；他把手放在盒盖上。
2–4 秒：黄蛋打开盒盖——里面只有青椒，没有肉丝：“……怎么没有肉丝？”
4–6 秒：心易在柜台后僵住，探头：“咔啵？”
6–7 秒：黄蛋看向心易：“肉丝呢？”
6–8 秒：心易慢慢缩回后厨窗口：“咔——啵”；**不拿任何食物出来，不补救**；**画外旁白起**：“没有肉丝，morose，闷闷不乐的。”
8–9 秒：黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；**不说话**；**画外旁白**：“你记住了吗？”镜尾定格 1s。""" % find("T_A")["id"]
new = """0–2 秒：{{%s}} 黄蛋站在木桌旁，餐盒**关着**，已经在**木桌桌面**上；他把手放在盒盖上。
2–4 秒：黄蛋打开盒盖——里面只有青椒，没有肉丝：“……怎么没有肉丝？”
4–6 秒：心易在柜台后僵住，探头：“咔啵？”
6–7 秒：黄蛋看向心易：“肉丝呢？”
7–9 秒：心易慢慢缩回后厨窗口：“咔——啵”；**不拿任何食物出来，不补救**。
9–12 秒：黄蛋看着那盒青椒，沉默、郁闷，肩膀垮下；**不说话**；**画外旁白**：“没有肉丝，morose，闷闷不乐的。”
12–13 秒：黄蛋沉默；**画外旁白**：“你记住了吗？”镜尾定格 1s。""" % find("T_A")["id"]
assert old in mp["prompt"], "V2 old block not found"
mp["prompt"] = mp["prompt"].replace(old, new)
mp["prompt"] = mp["prompt"].replace(
    "**画外旁白（独立成年女声，不是黄蛋/心易）在视频内生成**：6–8 “没有肉丝，morose，闷闷不乐的。”8–9 “你记住了吗？”",
    "**画外旁白（独立成年女声，不是黄蛋/心易）在视频内生成**：9–12 “没有肉丝，morose，闷闷不乐的。”12–13 “你记住了吗？”",
)
V2["meta"]["label"] = "【待生成】V2 · 13s · 没肉丝/旁白（首帧 T_A）"
assert len(mp["prompt"]) <= 1900

s0 = S0["outputs"][0]
s0["value"] = s0["value"].replace("V1 8s + V2 9s（T_A 接尾帧）+ 单卡尾静帧 3s", "V1 8s + V2 13s（T_A 接尾帧）+ 单卡尾静帧 3s")
s0["value"] += """

【时长 v10】
V1 8s + V2 13s + 单卡 3s ＝ 24s。
V2 9s 装不下旁白；延长到 13s：9–12 旁白“没有肉丝，morose，闷闷不乐的。”12–13“你记住了吗？”。
旁白仍在 V2 视频内生成，不是后期。
"""
c["name"] = "蛋仔记单词 · morose 小饭馆版 v10 · 加长到24s · 视频内旁白"
OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved", OUT, "V2 duration", mp["duration"], "len", len(mp["prompt"]))
