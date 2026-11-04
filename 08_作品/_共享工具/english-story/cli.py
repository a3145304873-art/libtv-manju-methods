# -*- coding: utf-8 -*-
"""english-story · 英语故事画布插件

一条命令跑完：故事校验 → 建 .monet → 画布门禁 → 报告。
不生成图片/视频、不导入 Monet、不派发；这些仍然要人点头。
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from lib import builder, report
from lib.check_canvas import check_canvas
from lib.check_story import check_story
from lib.model import (PLUGIN_ROOT, beats_abs, card_range, load_profile, load_story,
                       screen_range)
from lib.rules import RULES

OUT_DIR = PLUGIN_ROOT / "out"


def _utf8():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _story_path(text):
    path = Path(text)
    if path.is_file():
        return path
    candidate = PLUGIN_ROOT / "stories" / text
    if candidate.is_file():
        return candidate
    if not text.endswith(".json"):
        candidate = PLUGIN_ROOT / "stories" / f"{text}.json"
        if candidate.is_file():
            return candidate
    raise SystemExit(f"找不到 story：{text}")


def _profile_of(story):
    return load_profile(story["profile"])


def _print_result(result):
    print(f"[{result.status}] {result.subject}  "
          f"ERROR {result.count('ERROR')} / WARN {result.count('WARN')} / INFO {result.count('INFO')}")
    for f in result.findings:
        where = f" @ {f.where}" if f.where else ""
        print(f"  {f.level:5s} {f.rule} {f.title}: {f.message}{where}")
        if f.fix:
            print(f"        修复：{f.fix}")


def cmd_validate(args):
    story = load_story(_story_path(args.story))
    profile = _profile_of(story)
    result = check_story(story, profile)
    _print_result(result)
    if args.json:
        print(json.dumps(report.render_json([result]), ensure_ascii=False, indent=2))
    return 0 if result.ok else 2


def cmd_check(args):
    canvas = json.loads(Path(args.canvas).read_text(encoding="utf-8-sig"))
    story = load_story(_story_path(args.story)) if args.story else None
    profile = _profile_of(story) if story else None
    result = check_canvas(canvas, story, profile)
    _print_result(result)
    return 0 if result.ok else 2


def cmd_build(args):
    story_path = _story_path(args.story)
    story = load_story(story_path)
    profile = _profile_of(story)

    story_result = check_story(story, profile)
    _print_result(story_result)
    if not story_result.ok and not args.force:
        print("\n故事层有阻断项，拒绝建画布。确认要强推加 --force。")
        return 2

    canvas, info = builder.build_canvas(story, profile, prefix=args.prefix)
    canvas_result = check_canvas(canvas, story, profile)
    _print_result(canvas_result)

    out_dir = Path(args.out_dir) if args.out_dir else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    monet_path = out_dir / f"{story['id']}.monet"
    srt_path = out_dir / f"{story['id']}.srt"
    monet_path.write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
    srt_path.write_text(builder.to_srt(story.get("subtitles") or []), encoding="utf-8")

    meta = {
        "story": story["id"],
        "profile": profile["id"],
        "word": story["word"]["spelling"],
        "nodes": len(canvas["canvas"]["nodes"]),
        "edges": len(canvas["canvas"]["edges"]),
        "groups": len(canvas["canvas"]["groups"]),
        "prompt_lengths": info["prompt_lengths"],
        "canvas": str(monet_path),
    }
    md_path, json_path = report.write_report(
        out_dir / story["id"], [story_result, canvas_result],
        f"{story['id']} · 英语故事画布校验", meta)

    if args.copy_to:
        target = Path(args.copy_to) / monet_path.name
        shutil.copy2(monet_path, target)
        print(f"\n已复制：{target}")

    print(f"\n画布：{monet_path}")
    print(f"SRT ：{srt_path}")
    print(f"报告：{md_path}")
    print(f"      {json_path}")
    print(f"节点 {meta['nodes']} / 边 {meta['edges']} / 组 {meta['groups']}")
    return 0 if (story_result.ok and canvas_result.ok) else (1 if canvas_result.count("ERROR") == 0 else 2)


def _shape_text(profile):
    if profile.get("shots"):
        shape = profile["shots"]["shape"]
        return f"{len(shape)} 拍，{'+'.join(str(x) for x in shape)} = {sum(shape)}s；卡尾 {profile['card']['start']}–{profile['card']['end']}s"
    segs = profile.get("segments") or []
    parts = [f"{s['id']} {s['start']}–{s['end']}s" for s in segs]
    return "；".join(parts) + f"；卡尾 {profile['card']['start']}–{profile['card']['end']}s"


def cmd_brief(args):
    profile = load_profile(args.profile)
    story_rules = [(rid, rule) for rid, rule in RULES.items()
                   if rid.startswith("G") and rule["level"] == "ERROR"]
    story_rules.sort(key=lambda x: x[0])
    rule_lines = "\n".join(f"| {rid} | {rule['title']} | {rule['fix']} | {rule['case']} |"
                           for rid, rule in story_rules)
    scene = args.scene or "（由梗和拍摄需要决定的场景）"
    zh = args.zh or "（由本集笑点决定）"
    template = {
        "schema": 3,
        "id": f"{args.word}-{profile['id']}",
        "profile": profile["id"],
        "status": "draft",
        "title": f"{args.word}·英语玩梗短剧",
        "word": {"spelling": args.word, "ipa": args.ipa or "/--/", "zh": zh,
                 "meaning": args.meaning, "pos": "n.",
                 "source": {"dictionary": "（词典/权威来源）", "url": "（词条链接）",
                            "checked_at": "（YYYY-MM-DD）", "scope": "（本集采用的词性与义项）"}},
        "joke_design": {
            "purpose": "用好玩的记忆梗把目标词的读音/词形和本集词义连接起来；不写成课堂讲解",
            "candidates": [
                {"id": "A", "type": "homophone|sound_or_spelling|double_meaning|word_family|literal_misread|visual_gag|other",
                 "idea": "（一句话讲清梗）", "laugh_point": "（观众在哪一拍笑，反差/误会/包袱是什么）",
                 "word_connection": "（目标词的读音/词形/词族怎样触发这个梗）",
                 "meaning_bridge": "（这个梗怎样让观众把目标词连到本集准确词义）"},
                {"id": "B", "type": "另一种不同的玩梗方式", "idea": "（另一条梗概）",
                 "laugh_point": "（落笑点的位置）", "word_connection": "（目标词的读音/词形/词族怎样触发这个梗）",
                 "meaning_bridge": "（这个梗怎样让观众把目标词连到本集准确词义）"}],
            "selected": "A", "decision": "（为什么它最好笑、最自然，也最能把词和词义钩在一起）",
            "execution": "（这条梗具体落在哪个 beat/action/line；不要只写在方案字段里）"},
        "hook": {"line": "", "who_says": "", "why_natural": "",
                 "meaning_link": "", "why_meaning": ""},
        "stakes": {"want": "（黄蛋这 12s 想要的具体目标，画面可拍）",
                   "cost": "（出局的代价：输了丢什么，画面可拍）"},
        "turn": {"at": 3, "before": "（转折前局势）", "after": "（转折后局势）",
                 "why": "（为什么意外且改变局势，不是同类出丑的重复，≥12 字）"},
        "scene": {"name": scene, "why": "（为什么这个场景让字面动作成立）", "asset": "A02"},
        "first_frame": {"composition": "（首帧构图：两人站位、每件道具 0.0s 在哪、触发物在哪）",
                        "light": "（光线/时段/景别，如：夏夜暖黄院灯；中景全身）"},
        "props": [{"name": "（道具）", "form": "（形状/材质/不是什么）", "first_frame": True,
                   "at": "（0.0s 在哪）"}],
        "trigger": {"name": "（触发物）", "form": "（长什么样）", "at": "（0.0s 在哪）", "note": ""},
        "beats": [{"start": 0, "end": 3, "shot": "（景别）", "action": "（画面动作）",
                   "speaker": "黄蛋", "line": "（台词）", "sfx": "（音效）"}],
        "card": {"word": args.word, "zh": zh, "meaning": args.meaning},
        "signoff": {"speaker": "", "text": ""},
        "subtitles": [{"start": 0.8, "end": 2.0, "text": "（台词子串）"}],
        "scores": {"funny": 0, "word_fit": 0, "visual": 0, "character": 0},
        "continuity": {"no_spoiler_next": True,
                       "scene_state": ["（0.0s 已经就位的状态）"], "hands": "两只短手"},
        "negatives": ["（这条故事特有的负向）"],
        "assets_why": {"A05": "新道具图", "K_A": "新首帧", "KC": "新卡"},
        "notes": [],
    }
    text = f"""# 故事生成任务书 · {profile["title"]}

> 输入：{args.word} / {args.ipa or "/--/"} / 联想短句「{zh}」/ 词义「{args.meaning}」/ 场景：{scene}
> 你只产出 **一个 story JSON**；不要写画布、不要生成图/视频、不要导入。

## 一、结构

- {_shape_text(profile)}
- 道具 ≤ {profile.get("max_props")} 件，第一帧全在画面里
- 单场景；不换景、不加第三个角色
- 卡尾只三行：`{args.word}` / `{zh}` / `{args.meaning}`，无小字

## 一、内容目标：先做梗，再把英语做准确

- 这是一条“玩梗学单词”的短剧，不是课堂讲解。笑点是记忆钩子：观众看完应能把目标词的读音/词形和本集词义联系起来；不要求角色讲课或塞入复习题。
- 先核对词典拼写、IPA、词性和本集可能用到的义项，来源写入 `word.source`。这是防止英语错误的底线，不是剧情主线。
- 在 `joke_design` 至少比较两种不同记忆梗：自然谐音优先；也可用词形/拼写联想、双关/多义、词族串梗或语义场景。纯粹与目标词无关的视觉笑料不算候选。
- 每个候选写清梗概、笑点落点、词形/读音怎样触发、如何连到准确词义；选中的梗必须真正进入 beat/action/line。比较“好不好笑、是否自然、能否帮助回想词义、英语有没有错”。
- 邵氏武侠英语是可选表现型；武侠冲突和夸张表演承载记忆梗，词卡给准确拼写/音标/词义。邪修长课的主题词群/复习可放系列层，外部 Skill 的候选比较和成片 QA 可借鉴；单集保持短剧表达，不变成课堂讲解。

## 一点五、叙事建议（无厘头小插曲是可选引擎，不是唯一配方）

可用「仪式感 × 小事的反差」，也可用谐音误会、双关反转、词族连锁或围绕记忆钩子的视觉荒诞。按梗挑结构，不要每集都写成“黄蛋有小愿望—出小意外—心易一下收尾”。

以下是按梗选用的结构工具，不是每集固定拍点：开头尽快出现有趣局面；中段让谐音/词形联想/词族/语义连接更明显或升级；转折只在能制造新笑点时加入；结尾可用 punchline 或回扣强化词义记忆。角色动作、愿望、补位和复习提问都不设配额。

- 无厘头三个可用品：**把小物当对手**、**字面认真化**、**过时的仪式感**。
- 验收问句：开头是否尽快抛出有趣局面？包袱是否清楚、有新意？结尾是否落得干脆？强迫性的输赢/惩罚如果不是梗的必要部分就删掉。
- `00_方案/35-无厘头小插曲结构-v1.md` 是一种结构参考，遇到适合的小事反差时再用。

## 二、角色（硬规则）

- 黄蛋：毛绒版；台词服务梗和角色反应，不讲词义课{ "；至少说一次 " + args.word if profile.get("require_word_in_line") else "" }。
- 心易：棕色水豚，固定无台词人设；只能发“咔啵”，不得出现人话、内心独白或由旁白代她发言。她通过动作/表情参与记忆梗，不额外规定动作次数。
- { "旁白：按本档承担必要信息，独立成年声线，视频内生成，不是后期。" if profile.get("narration") else "本档没有旁白：台词可自然玩词，准确词卡放在卡尾。" }
- 视频内无文字、无字幕、无气泡；字幕只进 SRT。

## 三、故事层门禁（违反即退回）

| 规则 | 检查项 | 修复 | 出处 |
|---|---|---|---|
{rule_lines}

## 四、创意自检（用于比较方案，不是自动过稿分数）

- funny 好不好笑：能否一句话讲出包袱，笑点是否具体
- word_fit 梗和目标词/词义是否贴合：读音/拼写与义项的连接是否自然、能否回想
- visual 是否能在 {profile["total"]}s 内看懂并拍出来
- character 是否像角色会做的事，而不是为了凑动作配额
- 自评分数不能代替主创选稿；门禁只阻断可客观判断的错误，不以自报总分替代创意判断。

## 五、输出模板

```json
{json.dumps(template, ensure_ascii=False, indent=2)}
```

## 六、交稿前自检

```powershell
py -3 cli.py validate --story stories/{args.word}-{profile["id"]}.json
```

有 ERROR 就按报告改；全绿再交。
"""
    out_dir = Path(args.out_dir) if args.out_dir else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{args.word}-{profile['id']}.brief.md"
    path.write_text(text, encoding="utf-8")

    dispatch = f"""# 子代理执行说明 · {args.word}（{profile["id"]}）

你负责写**一版** story JSON。方向由主代理填在【方向】处，其余一切以任务书和叙事基准为准。

## 第一步：按顺序读三个文件（相对工作区根）
1. 叙事参考（无厘头小插曲是可选结构，不是唯一配方）：
   08_作品/蛋仔记单词/00_方案/35-无厘头小插曲结构-v1.md
2. 任务书（结构/角色/门禁/评分/JSON 模板）：
   08_作品/_共享工具/english-story/out/{args.word}-{profile["id"]}.brief.md
3. 字段风格参考（已过门禁的样例）：
   08_作品/_共享工具/english-story/stories/pest-15s.json

【方向：由主代理填写——logline + 玩梗机制 + 笑点落拍 + 结尾】

## 第二步：先写骨架再展开
logline / 使用的记忆梗 / 目标词如何连接词义 / 笑点如何升级或反转 / punchline 落点。自检：梗是否自然、是否具体好懂、是否能帮助回想词义、是否能在本 profile 内拍出来；不要为了填固定的“小愿望—小意外—心易收尾”强加桥段。

## 第三步：写文件并自校验
写入 08_作品/_共享工具/english-story/stories/{args.word}-{profile["id"]}-【变体名】.json，然后运行：

    cd 08_作品/_共享工具/english-story
    py -3 cli.py validate --story stories/<变体名>.json

ERROR 改到 0（最多 5 轮）；改不动就如实报剩余项。

## 纪律与交回
- 只写自己这一个文件；不改 assets.json/脚本；不建画布、不生成素材；
- 交回一段话：文件路径 / 骨架 / 一句话笑点 / 目标词与梗的关系 / 道具 / 四项创意自评 / validate 末行。
"""
    dispatch_path = out_dir / f"{args.word}-{profile['id']}.dispatch.md"
    dispatch_path.write_text(dispatch, encoding="utf-8")
    print(f"任务书：{path}")
    print(f"子代理说明：{dispatch_path}")
    return 0


def cmd_all(args):
    code = cmd_validate(args)
    if code == 2 and not args.force:
        return code
    return cmd_build(args)


def main(argv=None):
    _utf8()
    parser = argparse.ArgumentParser(
        prog="english-story",
        description="英语故事画布插件：故事校验 / 建 .monet / 画布门禁")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("brief", help="生成给 LLM/子代理的故事任务书")
    p.add_argument("--word", required=True)
    p.add_argument("--zh", default="", help="可选中文谐音/联想短句；留空时按玩梗方案决定")
    p.add_argument("--meaning", required=True, help="中文词义")
    p.add_argument("--ipa", default="")
    p.add_argument("--scene", default="")
    p.add_argument("--profile", default="harmonic15")
    p.add_argument("--out-dir", default="")
    p.set_defaults(func=cmd_brief)

    p = sub.add_parser("validate", help="只做故事层校验")
    p.add_argument("--story", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("build", help="校验 + 建画布 + 画布门禁 + 报告")
    p.add_argument("--story", required=True)
    p.add_argument("--prefix", default=None, help="节点 ID 前缀，默认用 story.id；返修必须沿用")
    p.add_argument("--out-dir", default="")
    p.add_argument("--copy-to", default="", help="额外复制 .monet 到哪里（如 Downloads）")
    p.add_argument("--force", action="store_true", help="有阻断项也强推（不建议）")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("check", help="只做画布/prompt 门禁")
    p.add_argument("--canvas", required=True)
    p.add_argument("--story", default="", help="带上 story 才能查道具/状态/时长")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("all", help="validate + build")
    p.add_argument("--story", required=True)
    p.add_argument("--prefix", default=None)
    p.add_argument("--out-dir", default="")
    p.add_argument("--copy-to", default="")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_all)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
