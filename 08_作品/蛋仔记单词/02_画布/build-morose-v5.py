# -*- coding: utf-8 -*-
"""Build morose v5: 黄蛋 speaks the reaction lines; narration still teaches.

V1 8s: 黄蛋 "青椒肉丝饭！……怎么没有肉丝？" / "肉丝呢？"
V2 9s: from T_A: "没肉丝……所以我很 morose？" / "morose，郁闷的。"
Narration is post; 心易 only "咔啵?" at the tail; three-card tail 3s.

Output: 02_画布/EP01-morose-meme-v5.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP01-morose-meme-v4.monet"
OUT = HERE / "EP01-morose-meme-v5.monet"

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


ids = {}
for k, p in (("R00", "R00"), ("R01", "R01"), ("R02", "R02"), ("R02E", "R02E"), ("R01P", "R01P"),
             ("A02", "A02"), ("A05", "A05"), ("K_A", "K_A"), ("T_A", "T_A 占位"),
             ("V1", "V1"), ("V2", "V2"), ("S0", "S0")):
    ids[k] = find(p)["id"]


def link(s):
    for k in list(ids):
        s = s.replace("[[" + k + "]]", "{{" + ids[k] + "}}")
    assert "[[" not in s
    return s


EYE = "心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油色眼白、外圈粗深棕描边，内部没有黑瞳孔、没有棕色虹膜，像布偶刺绣/纽扣眼；不要黑豆眼/写实瞳孔/动漫高光）；心易不说话。"
V1 = f"""【风格】20s 玩梗记单词，横屏；小院石桌；**黄蛋说话（短句）；心易不说话**；无文字/无气泡；旁白后期加。镜头快推/短甩/急停。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；说话的人。{EYE}
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；双人中景。
0–2 秒：[[K_A]] 黄蛋双手打开餐盒，眼睛发亮：“青椒肉丝饭！”
2–4 秒：黄蛋看到只有青椒，愣住：“……怎么没有肉丝？”
4–6 秒：黄蛋拿勺子拨找：“肉丝呢？”
6–8 秒：黄蛋肩膀垮下，趴到桌边：“真的没有……”；**保持趴桌 1 秒，镜尾稳定**，给 V2 接尾帧。
【声音】黄蛋人声（短句）；心易无声；餐盒/勺子环境声；旁白后期。
负向：心易说话/加词、角色口型穿帮、视频内文字/气泡/字幕、黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、慢速横移、渐变、白场、过曝。"""
V2 = f"""【风格】20s 玩梗记单词，横屏；小院石桌；**黄蛋说话（短句）；心易不说话**；无文字/无气泡；旁白后期加。**首帧＝T_A**：从 V1 最后一帧（黄蛋趴桌）继续，不换机位/不重摆/不换光。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；说话的人。{EYE}
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；与 T_A 同一位置/光线/构图。
0–3 秒：[[T_A]] 黄蛋从趴桌慢慢抬头，闷闷不乐：“没肉丝……所以我很 morose？”
3–5 秒：黄蛋坐直一点：“morose，郁闷的。”
5–7 秒：黄蛋指餐盒里的青椒丝：“没肉丝，所以郁闷。”
7–9 秒：黄蛋看镜头：“你记住了吗？”镜尾定格 1s。
【声音】黄蛋人声（短句）；心易无声；环境声；旁白后期。
负向：心易说话/加词、角色口型穿帮、视频内文字/气泡/字幕、黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、换机位/重摆/换光、慢速横移、渐变、白场、过曝。"""
for key, prompt, dur in (("V1", V1, 8), ("V2", V2, 9)):
    n = by[ids[key]]
    mp = n["params"]["model_params"]
    mp["prompt"] = link(prompt)
    mp["duration"] = dur
    mp["generate_audio"] = True
    n["outputs"] = []
    n["meta"]["label"] = {
        "V1": "【待生成】V1 · 8s · 怎么没有肉丝（黄蛋说话）",
        "V2": "【待生成】V2 · 9s · 没肉丝所以 morose（黄蛋说话，首帧 T_A）",
    }[key]
    assert len(mp["prompt"]) <= 1900

c["name"] = "蛋仔记单词 · 玩梗样片「morose＝没肉丝」v5 · 20s（黄蛋说话＋旁白＋三卡尾）"
s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》玩梗样片 v5：morose = 没肉丝 → 郁闷的。20s。
V1 8s + V2 9s（T_A 接尾帧）+ 三卡尾静帧 3s。
黄蛋说话（短句，如“怎么没有肉丝”）；心易不说话，只在结尾“咔啵？”；讲解旁白后期。

【跑序】
1. 修 R02/R02E 为你当前账号可读。
2. 跑 R01P（黄蛋毛绒版）。
3. 跑 A05（餐盒，无肉丝）。
4. 跑 K_A；看眼睛、黄蛋毛绒。
5. 跑 V1（8s）；结尾趴桌稳定 1 秒。
6. 截 V1 尾帧 → 替换 T_A。
7. 跑 V2（9s，首帧＝T_A）；不要提前跑。
8. 后期：V1+V2 → 三卡尾 3s；加旁白；结尾心易“咔啵？”。

【台词】
V1：黄蛋“青椒肉丝饭！”→“……怎么没有肉丝？”→“肉丝呢？”→“真的没有……”
V2：黄蛋“没肉丝……所以我很 morose？”→“morose，郁闷的。”→“没肉丝，所以郁闷。”→“你记住了吗？”
旁白：讲 morose = 没肉丝 → 郁闷的；不抢黄蛋短句。
尾：旁白“你记住了吗？”；心易“咔啵？”。

【口径】
- 黄蛋只讲短句；不要长篇解释；解释由旁白。
- 心易不说话；结尾咔啵除外。
- 视频内无文字/气泡；三卡尾后期静帧。
- 心易眼睛按 R02E；不对就重跑。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# validate (no topology changes)
ids_set = {n["id"] for n in nodes}
assert len(ids_set) == len(nodes)
by_id = {n["id"]: n for n in nodes}
edge_set = {(e["sourceNodeId"], e["targetNodeId"]) for e in c["edges"]}
for n in nodes:
    if n["type"] not in ("gen-image", "gen-video"):
        continue
    mp = n["params"]["model_params"]
    refs = [r["node_id"] for r in (mp.get("reference_images") or [])]
    ff = (mp.get("first_frame_image") or {}).get("node_id")
    for tok in re.findall(r"\{\{(node-[0-9A-Za-z_\-]+)\}\}", mp["prompt"]):
        assert tok in by_id, f"missing {tok}"
        assert tok in refs or tok == ff, f"token {tok} not in refs/ff in {n['meta']['label']}"
    for r in refs + ([ff] if ff else []):
        assert (r, n["id"]) in edge_set, f"ref without edge {r}->{n['id']}"
    assert not mp.get("reference_audios")
    if n["type"] == "gen-video":
        assert ff in mp["prompt"]

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(c['edges'])} edges / {len(c['groups'])} groups")
print("->", OUT)
