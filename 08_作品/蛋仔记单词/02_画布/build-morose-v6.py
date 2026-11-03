# -*- coding: utf-8 -*-
"""Build morose v6: 黄蛋 only reaction; explanation lines to narration; one card tail.

Output: 02_画布/EP01-morose-meme-v6.monet
"""
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")
AUTHOR = "linguanxi"
SRC = HERE / "EP01-morose-meme-v5.monet"
OUT = HERE / "EP01-morose-meme-v6.monet"
CARD = json.loads((ROOT / "01_资产" / "道具" / "morose-card-upload.json").read_text(encoding="utf-8"))

d = json.loads(SRC.read_text(encoding="utf-8"))
c = d["canvas"]
nodes = c["nodes"]
by = {n["id"]: n for n in nodes}


def find(prefix):
    return next(n for n in nodes if prefix in n["meta"].get("label", ""))


ids = {}
for k, p in (("KC", "KC"), ("V2", "V2"), ("S0", "S0")):
    ids[k] = find(p)["id"]

# replace KC output with the single card
kc = by[ids["KC"]]
kc["meta"]["label"] = "KC 单卡尾 · morose / 没肉丝 → 郁闷的（后期用）"
kc["meta"]["width"] = 300.0
kc["meta"]["height"] = 169.0
kc["outputs"] = [{
    "id": kc["outputs"][0]["id"], "status": "done", "error": None, "value": CARD["url"],
    "cover": None, "name": CARD["name"], "resolution": {"width": CARD["width"], "height": CARD["height"]},
    "source": None, "batchId": None, "execution": None, "graphRunId": None,
    "iterationPath": None, "taskSource": None, "taskId": None,
    "executorRunId": None, "stage": None, "deletedAt": None,
    "createdAt": NOW, "createdBy": AUTHOR, "updatedAt": NOW, "updatedBy": AUTHOR,
    "metadata": {"size": CARD["size"], "md5": CARD["md5"]},
}]

V2 = """【风格】20s 玩梗记单词，横屏；小院石桌；**黄蛋只说反应短句；心易不说话**；无文字/无气泡；旁白后期加。**首帧＝T_A**：从 V1 最后一帧（黄蛋趴桌）继续，不换机位/不重摆/不换光。
【角色】黄蛋毛绒版（参考 [[R01P]]，外形/比例参考 [[R00]]）：黄色蛋形、奶油脸、棕眼、天线球、短手、白袜白鞋；毛绒/毛毡；只讲反应短句，不讲解释。心易（参考 [[R02]]，棕色水豚；眼睛严格按 [[R02E]]：大圆形、白色/奶油眼白、外圈粗深棕描边，内部没有黑瞳孔/没有棕色虹膜，像布偶刺绣/纽扣眼；不要黑豆眼/写实瞳孔/动漫高光）；不说话。
【道具】[[A05]]：打开的外卖餐盒，白米饭＋青椒丝，没有肉丝；勺子。
【场景】[[A02]] 小院石桌，午后暖光；与 T_A 同一位置/光线/构图。
0–3 秒：[[T_A]] 黄蛋从趴桌慢慢抬头，闷闷不乐：“没肉丝……所以我很 morose？”
3–5 秒：黄蛋坐直一点，看餐盒，不说话；心易看他。（解释由旁白）
5–7 秒：黄蛋指了指餐盒里的青椒丝，不说话；心易点头。
7–9 秒：黄蛋看镜头：“你记住了吗？”镜尾定格 1s。
【声音】黄蛋人声（只两句短句）；心易无声；环境声；旁白讲“morose，郁闷的。没肉丝，所以郁闷。”
负向：黄蛋讲长解释/加词、心易说话、视频内文字/气泡/字幕、黄蛋光滑塑料、心易黑豆眼/棕色虹膜/写实瞳孔/动漫高光、旧心易/猫耳/天线、肉丝出现、蛋壳裂开/蛋液、牙齿、logo、换机位/重摆/换光、慢速横移、渐变、白场、过曝。"""
n = by[ids["V2"]]
mp = n["params"]["model_params"]
mp["prompt"] = V2.replace("[[R01P]]", "{{" + find("R01P")["id"] + "}}")
for k, p in (("R00", "R00"), ("R02", "R02"), ("R02E", "R02E"), ("A05", "A05"), ("A02", "A02"), ("T_A", "T_A 占位")):
    mp["prompt"] = mp["prompt"].replace("[[" + k + "]]", "{{" + find(p)["id"] + "}}")
assert "[[" not in mp["prompt"]
mp["duration"] = 9
mp["generate_audio"] = True
n["outputs"] = []
n["meta"]["label"] = "【待生成】V2 · 9s · 没肉丝所以 morose（黄蛋只问；解释旁白）"
assert len(mp["prompt"]) <= 1900

c["name"] = "蛋仔记单词 · 玩梗样片「morose＝没肉丝」v6 · 20s（黄蛋短句＋旁白＋单卡尾）"
s0 = by[ids["S0"]]
s0["outputs"][0]["value"] = """【本画布做什么】
《蛋仔记单词》玩梗样片 v6：morose = 没肉丝 → 郁闷的。20s。
V1 8s + V2 9s（T_A 接尾帧）+ 单卡尾静帧 3s。
黄蛋只说反应短句；解释由旁白；心易不说话；单卡尾用 morose-card-tail。

【跑序】
1. 修 R02/R02E 为你当前账号可读。
2. 跑 R01P（黄蛋毛绒版）。
3. 跑 A05（餐盒，无肉丝）。
4. 跑 K_A；看眼睛、黄蛋毛绒。
5. 跑 V1（8s）；结尾趴桌稳定 1s。
6. 截 V1 尾帧 → 替换 T_A。
7. 跑 V2（9s，首帧＝T_A）。
8. 后期：V1+V2 → 单卡尾 3s；加旁白；心易“咔啵？”。

【台词/旁白】
V1 黄蛋：“青椒肉丝饭！”→“……怎么没有肉丝？”→“肉丝呢？”→“真的没有……”
V2 黄蛋：“没肉丝……所以我很 morose？”（问）→（3–7 不说话）→“你记住了吗？”
旁白：morose，郁闷的。没肉丝，所以郁闷。
尾：旁白“你记住了吗？”；心易“咔啵？”。

【口径】
- 黄蛋只讲反应短句；“morose，郁闷的”“没肉丝，所以郁闷”全部由旁白。
- 心易不说话；结尾咔啵除外。
- 视频内无文字/气泡；单卡尾后期静帧。
- 心易眼睛按 R02E；不对就重跑。
"""
s0["meta"]["label"] = "S0 制作说明 · 先读"

# validate topology unchanged
ids_set = {n["id"] for n in nodes}
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

OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copyfile(OUT, Path.home() / "Downloads" / OUT.name)
print(f"{OUT.name}: {len(nodes)} nodes / {len(c['edges'])} edges / {len(c['groups'])} groups")
print("->", OUT)
