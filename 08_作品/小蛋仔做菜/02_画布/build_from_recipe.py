# -*- coding: utf-8 -*-
"""菜谱卡 → Monet 画布生成器（小蛋仔做菜 · 秃秃格式）

用法：
    py -3 build_from_recipe.py <菜谱卡.json> [-o 输出.monet]

管线（每次给一道菜，跑一次）：
    1. 写菜谱卡 JSON（七段式：取 / 理 / 配 / 火 / 揭 / 分，4 段 × (3 动作 + 1 呼吸)）
    2. 本脚本读卡 → 生成 .monet（含全部提示词、组、边、自检）
    3. Monet 导入 → 按组跑 场景 → 道具 → 网格 → 关键帧 → 视频

设计约束全部内置：比例协调、因果律、用量、无人手、环境音、呼吸拍。
"""
import json
import random
import re
import sys
from pathlib import Path

TS = "2026-10-29T21:00:00.000+08:00"
BY = "libtv-workspace"

# ---------------- 全季共用常量 ----------------
CHAR = ("蛋小粉：一只约 30 厘米高的粉色搪胶蛋仔（大约一只猫的高度），圆形蛋身、正面一片奶油色椭圆脸盘、"
        "绿色星星眼、细弯眉、小嘴、粉色圆腮、头顶一根带小圆球的粉色触角、短圆手臂、白色小袜靴；"
        "外观严格照参考图，不增不减不变色，无人类五官、无手指、无衣物")

SCALE = ("尺度：这是一个为它配好的小世界——锅、盆、坛子这些大件比它高，但擀面杖、碗、刀、碟、篮都是按它的身量配的，"
         "它抱得动、端得稳、够得着；不要把道具画成人类尺寸的巨物，也不要把画面做成微缩模型的俯视感")

TONE = ("基调：治愈、安静、慢。它安安静静地把一件事做完，动作利落但不表演、不夸张、不看镜头；"
        "治愈来自干净的环境、柔和的光、放大的环境声，以及「做完之后把吃的分出去」")

CAUSAL = ("因果律：画面里出现的东西和状态，都必须由本镜看得见的动作产生——"
          "蛋液只能从磕开的蛋壳里流出来，丁只能由落下的刀切出来，火只能在点火之后出现，"
          "油只能在壶倾斜之后进锅；不许结果先于过程，不许道具凭空出现或消失")

QUANTITY = ("用量：每种食材用量按一到两人份，油只铺薄薄一层、不超过锅深十分之一；"
            "碗、碟、刀、锅的数量和位置在一段之内不增不减")

HANDS = ("手：它只有两只短圆的、没有手指的手，夹、抱、按、推都用这两只圆手；"
         "画面里绝不出现人类的手、手掌、五指、指甲、人的小臂或穿袖子的手")

CONTINUITY = ("场记：镜头之间必须接着上一镜往下走——切好的东西不再变回整颗，用掉的原料不凭空回来，"
              "手里的东西要与本镜动作对应（该拿油壶就是油壶，该拿铲就是铲，换手要看见放下再拿起），"
              "砧板、碗、锅、碟的位置全程不变；上一镜结束时是什么状态，下一镜开始就必须还是那个状态")

NEG_IMG = ("负向：人类、人手、人类手掌、五指手指、指甲、人的小臂、握刀的真人手、手指、毛发、卡通扁平渲染、塑料玩具感、"
           "比例失真、角色复制、第二只蛋仔、道具重复、文字、水印、logo、边框、过曝、广告打光、多个光源、道具穿模、"
           "厨具悬空、蛋液来自未磕开的蛋、完好蛋壳旁出现蛋液、丁凭空出现、油量过多淹没食材、火未点即有火焰、"
           "现代电器、不锈钢台面、塑料收纳盒、瓷砖大白墙、杂物堆积、脏污油腻、微缩模型俯视感、浅景深缺失、切好的原料又变回整颗、整颗番茄出现在已切好的砧板上、原料凭空回来、手持物跳变、未放下就换工具、砧板出现在地面、灶与桌的位置互换、背景换到另一个地方、出现该角落没有的器具。")

NEG_VID = ("负向：人类、人手、五指、指甲、真人手握刀、多余角色、第二只蛋仔、卡通扁平、塑料玩具感、比例失真、瞬移、变形、"
           "角色复制、道具复制、字幕、文字、水印、BGM旋律、说话、镜头旋转、镜头漂移、翻车动作、鬼畜重复、道具穿模、"
           "无因之果、食材凭空出现或消失、油量过多、火未点即有火、现代电器、不锈钢、塑料收纳盒、杂物堆积、切好的菜变回整颗、手持物跳变、砧板位置移动、背景换景。")

nodes, edges, groups = [], [], []


def rid(prefix):
    return f"{prefix}-{random.getrandbits(32):08x}"


def add_node(n):
    nodes.append(n)
    return n


def input_image(nid, label, url, name, w, h, x, y, nw, nh):
    oid = f"output-{random.getrandbits(32):08x}"
    add_node({
        "id": nid, "type": "input-image", "mainOutputId": oid,
        "meta": {"x": x, "y": y, "width": nw, "height": float(nh), "label": label, "resourceType": None},
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": url, "cover": None, "name": name,
            "resolution": {"width": w, "height": h}, "source": None, "batchId": None, "execution": None,
            "graphRunId": None, "iterationPath": None, "taskSource": None, "taskId": None,
            "executorRunId": None, "stage": None, "deletedAt": None,
            "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_image(nid, label, prompt, refs, x, y, nw=320, nh=207):
    add_node({
        "id": nid, "type": "gen-image", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": float(nw), "height": float(nh), "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "gpt-image-2", "model_params": {
            "prompt": prompt,
            "reference_images": [{"node_id": r} for r in refs],
            "aspect_ratio": "16:9", "image_size": "1K", "width": 1024, "height": 576,
            "quality": "medium", "output_format": "png", "moderation": "low", "auto_compress": True}},
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def gen_video(nid, label, prompt, first_frame, refs, duration, x, y):
    add_node({
        "id": nid, "type": "gen-video", "mainOutputId": None,
        "meta": {"x": x, "y": y, "width": 360.0, "height": 240.0, "label": label, "resourceType": None},
        "outputs": [],
        "params": {"num": 1, "model_id": "seedance-2.0-mini", "model_params": {
            "prompt": prompt, "_reference_way": "reference",
            "reference_images": [{"node_id": r} for r in refs],
            "reference_audios": [],
            "first_frame_image": {"node_id": first_frame},
            "resolution": "720p", "aspect_ratio": "16:9", "duration": duration,
            "generate_audio": True, "watermark": False}},
        "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def input_text(nid, label, text, x, y, nw, nh):
    oid = f"output-{random.getrandbits(32):08x}"
    add_node({
        "id": nid, "type": "input-text", "mainOutputId": oid,
        "meta": {"x": x, "y": y, "width": float(nw), "height": float(nh), "label": label, "resourceType": None},
        "outputs": [{
            "id": oid, "status": "done", "error": None, "value": text, "cover": None, "name": label,
            "resolution": None, "source": None, "batchId": None, "execution": None, "graphRunId": None,
            "iterationPath": None, "taskSource": None, "taskId": None, "executorRunId": None, "stage": None,
            "deletedAt": None, "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY, "metadata": None,
        }],
        "params": None, "specialParams": None, "config": None,
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def edge(src, dst):
    edges.append({
        "id": rid("edge"), "sourceNodeId": src, "sourceHandle": "output",
        "targetNodeId": dst, "targetHandle": "input",
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })


def group(label, ids, x, y, w, h, color):
    groups.append({
        "id": rid("group"), "nodeIds": ids,
        "bounds": {"x": x, "y": y, "width": w, "height": h},
        "label": label,
        "style": {"accent": None, "opacity": None, "borderColor": color},
        "createdAt": TS, "createdBy": BY, "updatedAt": TS, "updatedBy": BY,
    })



def validate_recipe(r):
    """菜谱卡结构校验：缺一项就不许编译，避免把问题带到生成阶段。"""
    errs = []
    for k in ("ep", "dish", "series_title", "character", "areas", "segments"):
        if not r.get(k):
            errs.append(f"缺少字段 {k}")
    areas = {a.get("key"): a for a in r.get("areas", [])}
    if len(areas) < 2:
        errs.append("至少要有 2 个场景角落")
    for k, a in areas.items():
        for f in ("name", "desc", "layout", "props_here"):
            if not a.get(f):
                errs.append(f"场景 {k} 缺 {f}（场景必须自带站位与器具清单）")
    comps = {c.get("key") for c in r.get("companions", [])}
    if len(r.get("segments", [])) != 4:
        errs.append(f"必须 4 段，当前 {len(r.get('segments', []))}")
    for i, seg in enumerate(r.get("segments", []), 1):
        if seg.get("area") not in areas:
            errs.append(f"第 {i} 段的场景 {seg.get('area')} 不在 areas 里")
        if "with" not in seg:
            errs.append(f"第 {i} 段缺 with 字段（没有配角就写空数组）")
        for w in seg.get("with", []):
            if w not in comps:
                errs.append(f"第 {i} 段引用了不存在的配角 {w}")
        if not seg.get("sound"):
            errs.append(f"第 {i} 段缺 sound")
        shots = seg.get("shots", [])
        if len(shots) != 4:
            errs.append(f"第 {i} 段必须 4 拍，当前 {len(shots)}")
            continue
        for j, sh in enumerate(shots[:3], 1):
            if sh.get("kind") != "action":
                errs.append(f"第 {i} 段第 {j} 拍必须是 action")
            for f in ("start", "do", "end"):
                if not sh.get(f):
                    errs.append(f"第 {i} 段第 {j} 拍缺 {f}（因果三截）")
            sh["short"] = sh.get("short") or sh.get("do", "")[:8]
        if shots[3].get("kind") != "breathe" or not shots[3].get("desc"):
            errs.append(f"第 {i} 段第 4 拍必须是带 desc 的 breathe 空镜")
    if errs:
        print("菜谱卡校验失败：")
        for e in errs:
            print(" -", e)
        sys.exit(1)


# ---------------- 组装 ----------------
def build(recipe, out):
    validate_recipe(recipe)
    dish = recipe["dish"]
    areas = recipe["areas"]                 # [{key,name,desc}]
    props = recipe.get("props", [])         # [{id,label,body}]
    segs = recipe["segments"]               # 4 段，每段 {area,title,shots:[3 action + 1 breathe],subs}

    N_A0 = "node-a0hero"
    input_image(N_A0, "A0 蛋小粉标准（已上传·复用四小只）", recipe["character"]["ref_url"],
                "角色-粉蛋-标准.jpg", 1305, 1495, 0, 0, 300, 345)

    # 配角（如小狗）：独立角色节点，只在需要的段里引用，不进场景空景、不当白底道具
    comp = {}
    for c in recipe.get("companions", []):
        comp[c["key"]] = c
        cid = c["id"]
        if c.get("ref_url"):
            input_image(cid, f"{c['label']}（已上传）", c["ref_url"], f"{c['key']}.jpg", 1024, 1024, 0, 1180, 300, 300)
        else:
            gen_image(
                cid, f"【待生成】{c['label']} · 白底三视图",
                f"纯白底角色三视图，只生成一只角色。{c['prompt']}\n"
                "正面、侧面、背面，同一角色、同一比例、同一配色，完整入画；柔和顶光、真实投影、"
                "毛绒与布料质感清晰，造型圆润不写实。\n无文字、无 logo、无水印。\n" + NEG_IMG,
                [], 0, 1180, 300, 220
            )

    N_S0 = "node-s0readme"
    s0 = (
        f"【本画布】《小蛋仔做菜》{recipe['ep']}《{dish}》：16:9、{len(segs)*15} 秒＝{len(segs)} 段 × 15 秒。\n"
        f"格式：秃秃（小蘑菇）式七段——取 / 理 / 配 / 火 / 揭 / 分；每段 3 个动作拍 + 1 个呼吸拍。\n"
        f"系列名：{recipe['series_title']}\n\n"
        "【跑序】01 场景 → 02 道具（并行）→ 03 网格 → 04 段首帧 → 05 视频段。\n"
        "网格没定稿不跑关键帧；关键帧没定稿不跑视频。\n\n"
        "【为什么是四个角落】原片从不在一个房间里做完一顿饭：取料在外、处理在桌、火在灶、分享在窝。\n"
        "镜头在角落之间跳，但雾气、苔藓、木纹、色温始终一致，所以还是同一个世界。\n\n"
        "【比例】这是一个为它配好的小世界：锅盆比它高，但工具都按它身量配，它抱得动、够得着。\n"
        "不要画成人类巨物，也不要画成模型俯视。\n\n"
        "【改法】改提示词改菜谱卡 JSON 后重跑 build_from_recipe.py，不手改 .monet。"
    )
    input_text(N_S0, "S0 制作说明 · 先读", s0, 0, 1640, 320, 780)

    # 场景：每个角落一张
    scene_ids = {}
    for i, a in enumerate(areas):
        nid = f"node-s{i+1}{a['key']}"
        scene_ids[a["key"]] = nid
        gen_image(
            nid, f"【待生成】S{i+1} 场景 · {a['name']} · 16:9 空景",
            f"16:9 场景设定空景，不出现任何角色。{a['desc']}\n"
            f"{SCALE}。{TONE}。\n"
            "画面要唯美：浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；木头、陶土、竹子、苔藓的材质要能分辨。\n"
            "画面干净，只有必须的东西：没有现代电器、没有不锈钢、没有塑料收纳盒、没有杂物堆。\n"
            f"参考图：{{{{{N_A0}}}}} 只用于确认它的身量比例，画面里不出现角色。\n"
            "无文字、无 logo、无水印。\n" + NEG_IMG,
            [N_A0], 340, i * 240, 420, 236
        )
        edge(N_A0, nid)
    scene_h = len(areas) * 240 + 20

    # 道具
    prop_ids = []
    for i, p in enumerate(props):
        prop_ids.append(p["id"])
        gen_image(
            p["id"], f"【待生成】{p['id']} {p['label']} · 白底道具",
            f"纯白底道具图，只出现一件物品，不出现角色、不出现手。{p['body']}。\n"
            "正面微侧、居中构图、完整入画，柔和顶光，物品下方有自然的接触阴影；真实自然材质，不塑料、不卡通。\n"
            "无文字、无 logo、无水印、无边框。\n" + NEG_IMG,
            [], 340, scene_h + 40 + i * 200, 300, 190
        )
    prop_h = len(props) * 200 + 20

    # 网格 + 段首帧 + 视频
    grid_ids, key_ids, vid_ids = [], [], []
    for i, seg in enumerate(segs):
        gid = f"node-g{i+1}sheet"
        kid = f"node-k{i+1}first"
        vid = f"node-v{i+1}seg"
        grid_ids.append(gid); key_ids.append(kid); vid_ids.append(vid)
        area = next(a for a in areas if a["key"] == seg["area"])
        mates = [comp[k] for k in seg.get("with", []) if k in comp]
        extra = [m["id"] for m in mates]
        mate_line = ("【配角】" + "；".join(m["desc"] for m in mates) + "。") if mates else ""
        mate_tok = "".join(f"{{{{{m['id']}}}}}={m['label']}；" for m in mates)

        cells = [f"{s['start']}｜{s['do']}｜{s['end']}" for s in seg["shots"][:3]] + [seg["shots"][3]["desc"]]

        gen_image(
            gid, f"【待生成】G{i+1} 第 {i+1} 段四宫格 · {seg['title']}",
            "请生成一张两列两行的分镜设计图，一张大图中包含四个按顺序排列的画面，从左到右、从上到下阅读；"
            "前三格是一件事的三个瞬间，第四格是没有动作的空镜（只有火、蒸汽、光或静物）。\n"
            f"场景：{area['desc']}\n{area.get('layout','')}\n本角落的器具：{'、'.join(area.get('props_here', []))}；只有这些，不要多出别的器具。\n{SCALE}。{TONE}。{CAUSAL}。{QUANTITY}。{HANDS}。{CONTINUITY}。\n"
            "每格只画动作完成后的样子；刀握在刀柄上垂直落下；火只在灶眼；每格都要能看出它站在哪里。\n"
            + "\n".join(f"第 {j+1} 格：{c}。" for j, c in enumerate(cells)) +
            "\n格子里只出现这一只蛋仔，不出现人类、不出现文字与标识；格与格之间不要加标注或分隔线。\n"
            f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{scene_ids[seg['area']]}}}}} 该角落的环境与光线；{mate_tok}\n"            f"{mate_line}\n"
            f"角色：{CHAR}。\n" + NEG_IMG,
            [N_A0, scene_ids[seg["area"]]] + extra, 800, i * 320, 400, 300
        )
        for r in [N_A0, scene_ids[seg["area"]]] + extra:
            edge(r, gid)

        gen_image(
            kid, f"【关键帧】K{i+1} 第 {i+1} 段首帧 · {seg['shots'][0]['short']}",
            f"16:9 横屏电影感画面。{seg['shots'][0]['start']}。\n"
            f"角色：{CHAR}。\n{SCALE}。{TONE}。\n场景：{area['desc']}\n{area.get('layout','')}\n本角落的器具：{'、'.join(area.get('props_here', []))}；只有这些，不要多出别的器具。\n"
            f"{CAUSAL}。{QUANTITY}。{HANDS}。{CONTINUITY}。\n"
            "浅景深、一层薄雾、光里有浮尘、器物表面有湿润感；不出现人类、不出现第二只蛋仔、不出现文字。\n"
            f"参考图：{{{{{N_A0}}}}} 角色外观；{{{{{scene_ids[seg['area']]}}}}} 环境与光线；{{{{{gid}}}}} 第一格构图；{mate_tok}\n"            f"{mate_line}\n"
            + NEG_IMG,
            [N_A0, scene_ids[seg["area"]], gid] + extra, 1240, i * 240, 360, 207
        )
        for r in [N_A0, scene_ids[seg["area"]], gid] + extra:
            edge(r, kid)

        shot_txt = "\n".join(f"{s['t']} 秒：{s.get('start','')}｜{s.get('do','')}｜{s.get('end','')}"
                             if s.get("kind") != "breathe" else f"{s['t']} 秒：空镜。{s['desc']}"
                             for s in seg["shots"])
        subs = "／".join([s["sub"] for s in seg["shots"] if s.get("sub")])
        prompt = (
            f"【首帧锁定】首帧使用 {{{{{kid}}}}}：第 0 秒就是这一帧，锁角色位置/朝向/光线与道具状态。\n"
            f"【分镜表】{{{{{gid}}}}} 是本段分镜，一格一个镜头；只参考构图与顺序，不要出现分格边框。\n"
            f"【角色】{CHAR}；它不说话，只靠动作和表情。\n"
            f"{SCALE}。{TONE}。\n场景：{area['desc']}\n{area.get('layout','')}\n本角落的器具：{'、'.join(area.get('props_here', []))}；只有这些，不要多出别的器具。\n"
            f"【因果】{CAUSAL}。\n【用量】{QUANTITY}。\n【手】{HANDS}。\n【场记】{CONTINUITY}。\n"
            "【节奏】本段 15 秒 4 个镜头：前三个各约 3.3 秒做一个动作，做完停一下再切；第四个是 5 秒空镜，"
            "不推进剧情，只让火、蒸汽、光或静物自己动。不加速、不炫技运镜，镜头基本不动。\n"
            f"【镜头】\n{shot_txt}\n"
            f"【声音】{seg['sound']}；没有音乐、没有台词。\n"
            f"【字幕预留】字幕只在后期贴（{subs}），画面里不出现任何文字。\n"
            f"【图片引用】{{{{{kid}}}}}=首帧；{{{{{gid}}}}}=分镜表；{{{{{N_A0}}}}}=角色外观；{mate_tok}\n"            f"{mate_line}\n"
            + NEG_VID
        )
        gen_video(vid, f"【待生成】V{i+1} {seg['title']} · {seg['range']} · 15s", prompt, kid,
                  [kid, gid, N_A0] + extra, 15, 1700, i * 280)
        for r in [kid, gid, N_A0] + extra:
            edge(r, vid)

    # 组
    group("00 参考 · 角色与配角", [N_A0] + [c["id"] for c in recipe.get("companions", [])], -20, -20, 340, 1560, "#E68BB3")
    group("01 场景 · 按角落出图 · 先跑", list(scene_ids.values()), 320, -20, 460, scene_h, "#8E8DE0")
    group("02 道具白底 · 并行", prop_ids, 320, scene_h + 20, 460, prop_h, "#7FB07F")
    group("03 四宫格 · 定稿后再往下", grid_ids, 780, -20, 440, len(segs) * 330, "#E8B85D")
    group("04 段首帧", key_ids, 1220, -20, 400, len(segs) * 250, "#6FA8DC")
    group("05 视频段 · 先只跑 V1", vid_ids, 1680, -20, 400, len(segs) * 290, "#DC775D")
    group("06 制作说明 · 先读", [N_S0], -20, 1632, 340, 800, "#B0B0B0")

    canvas = {
        "schemaVersion": 2, "type": "monet.canvas", "exportedAt": TS,
        "canvas": {
            "name": recipe.get("canvas_name") or f"小蛋仔做菜 · {recipe['ep']} {dish} · 16:9 · {len(segs)}段×15s · 秃秃格式",
            "description": recipe.get("description") or
            f"{len(segs)*15}s＝{len(segs)} 段×15s，每段 3 动作拍（3.3s）+1 呼吸拍（5s）。七段式：取/理/配/火/揭/分；"
            "院子动线四角落；比例协调；seedance-2.0-mini。由 build_from_recipe.py 从菜谱卡生成。",
            "nodes": nodes, "edges": edges, "groups": groups,
        },
    }

    # 自检
    problems = []
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        if n["type"] in ("gen-image", "gen-video"):
            mp = n["params"]["model_params"]
            refs = [r["node_id"] for r in mp.get("reference_images", [])]
            ff = (mp.get("first_frame_image") or {}).get("node_id")
            toks = set(re.findall(r"\{\{(node-[^\}]+)\}\}", mp.get("prompt", "")))
            for r in refs + ([ff] if ff else []):
                if r not in by_id:
                    problems.append(f"{n['id']}: 引用不存在 {r}")
                if r not in toks and r != ff:
                    problems.append(f"{n['id']}: 参考图 {r} 未在 prompt 中提及")
            for t in toks:
                if t not in by_id:
                    problems.append(f"{n['id']}: token {t} 无节点")
                srcs = {e["sourceNodeId"] for e in edges if e["targetNodeId"] == n["id"]}
                if t not in srcs:
                    problems.append(f"{n['id']}: token {t} 没有连线")
            if n["type"] == "gen-video":
                if len(mp["prompt"]) > 2000:
                    problems.append(f"{n['id']}: prompt {len(mp['prompt'])} 超 2000")
                srcs = {e["sourceNodeId"] for e in edges if e["targetNodeId"] == n["id"]}
                if ff not in srcs:
                    problems.append(f"{n['id']}: 首帧没有连线")
                for e in edges:
                    if e["sourceNodeId"] == n["id"] and by_id.get(e["targetNodeId"], {}).get("type") == "gen-video":
                        problems.append(f"{n['id']}: video→video 边")
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            a, b = groups[i]["bounds"], groups[j]["bounds"]
            if a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] and \
               a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]:
                problems.append(f"组重叠: {groups[i]['label']} ↔ {groups[j]['label']}")
    for g in groups:
        for nid in g["nodeIds"]:
            m, b = by_id[nid]["meta"], g["bounds"]
            if not (b["x"] <= m["x"] and m["x"] + m["width"] <= b["x"] + b["width"] and
                    b["y"] <= m["y"] and m["y"] + m["height"] <= b["y"] + b["height"]):
                problems.append(f"节点 {nid} 超出组 {g['label']}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {out.name}: {len(nodes)} 节点 / {len(edges)} 边 / {len(groups)} 组 / {len(segs)}x15s")
    for n in nodes:
        if n["type"] == "gen-video":
            print(f"  {n['meta']['label']}: {len(n['params']['model_params']['prompt'])} 字符")
    if problems:
        print("自检失败:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("自检通过")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    card = Path(sys.argv[1])
    recipe = json.loads(card.read_text(encoding="utf-8"))
    out = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "-o" else \
        card.parent / f"{recipe['ep']}-{recipe['dish']}-v1.monet"
    build(recipe, out)
