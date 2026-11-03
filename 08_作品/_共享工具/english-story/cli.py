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
    scene = args.scene or "（由梗决定，选最能让字面动作成立的场景）"
    template = {
        "schema": 1,
        "id": f"{args.word}-{profile['id']}",
        "profile": profile["id"],
        "status": "draft",
        "title": f"{args.word}《{args.zh}》",
        "word": {"spelling": args.word, "ipa": args.ipa or "/--/", "zh": args.zh,
                 "meaning": args.meaning, "pos": "n."},
        "hook": {"line": "（那个人真会说的一句话，含谐音）", "who_says": "黄蛋",
                 "why_natural": "（谁、在什么场景、为什么会这么说）",
                 "meaning_link": "object|consequence|function",
                 "why_meaning": "（字面怎么落到词义）"},
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
        "card": {"word": args.word, "zh": args.zh, "meaning": args.meaning},
        "signoff": {"speaker": "黄蛋",
                    "text": "（word 谐音 词义。你记住了吗？——卡在视频里时必填的锚点句）"},
        "subtitles": [{"start": 0.8, "end": 2.0, "text": "（台词子串）"}],
        "scores": {"natural": 0, "meaning": 0, "visual": 0, "character": 0},
        "continuity": {"no_rescue": True, "no_spoiler_next": True,
                       "scene_state": ["（0.0s 已经就位的状态）"], "hands": "两只短手"},
        "negatives": ["（这条故事特有的负向）"],
        "assets_why": {"A05": "新道具图", "K_A": "新首帧", "KC": "新卡"},
        "notes": [],
    }
    text = f"""# 故事生成任务书 · {profile["title"]}

> 输入：{args.word} / {args.ipa or "/--/"} / 谐音「{args.zh}」/ 词义「{args.meaning}」/ 场景：{scene}
> 你只产出 **一个 story JSON**；不要写画布、不要生成图/视频、不要导入。

## 一、结构

- {_shape_text(profile)}
- 道具 ≤ {profile.get("max_props")} 件，第一帧全在画面里
- 单场景；不换景、不加第三个角色
- 卡尾只三行：`{args.word}` / `{args.zh}` / `{args.meaning}`，无小字

## 一点五、叙事配方（无厘头小插曲，必读）

**冲突强度上限＝微微的不顺。** 配方是「仪式感 × 小事的反差」：

| 段 | 内容 |
| --- | --- |
| 起（P1–P2） | 日常进行中＋一个**小愿望**（小到可笑：吃今天第一颗栗子／把字摆正） |
| 插（P3–P4） | **小插曲**：字面行动引发的一个小意外——物理或误会层面，不对抗 |
| 转（P5） | 心易一下：拨正／推给／按住**已有物**（不补救、不加新东西） |
| 合（P6） | 轻落点定格＋卡尾锚点句（word 谐音 词义。你记住了吗？——系列记忆锚） |

- 无厘头三个可用品：**把小物当对手**、**字面认真化**、**过时的仪式感**。
- 验收问句：「这 12s 里有没有人赢/输/受罚？」——有，就回到赌局老路（G23 会报警）。
- 详见 `00_方案/35-无厘头小插曲结构-v1.md`。

## 二、角色（硬规则）

- 黄蛋：毛绒版；只说反应短句；不讲解释、不讲词义{ "；至少说一次 " + args.word if profile.get("require_word_in_line") else "" }。
- 心易：棕色水豚；只发“咔啵”（不许说人话、不许加括号释义）；不做补救。
- { "旁白：讲全部解释，独立成年声线，视频内生成，不是后期。" if profile.get("narration") else "本档没有旁白：词只在卡尾出现。" }
- 视频内无文字、无字幕、无气泡；字幕只进 SRT。

## 三、故事层门禁（违反即退回）

| 规则 | 检查项 | 修复 | 出处 |
|---|---|---|---|
{rule_lines}

## 四、评分（每项 0–25，总分 <80 不采用）

- natural 自然度：这句话在该场景真会说
- meaning 义接：字面对象/后果/作用能落到词义
- visual 画面：{profile["total"]}s 内可拍、道具少、动作清楚
- character 人设：黄蛋努力笨拙、心易一下即中

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
1. 叙事基准（无厘头小插曲结构，冲突强度上限在这里）：
   08_作品/蛋仔记单词/00_方案/35-无厘头小插曲结构-v1.md
2. 任务书（结构/角色/门禁/评分/JSON 模板）：
   08_作品/_共享工具/english-story/out/{args.word}-{profile["id"]}.brief.md
3. 字段风格参考（已过门禁的样例）：
   08_作品/_共享工具/english-story/stories/pest-15s.json

【方向：由主代理填写——logline + 小愿望 + 插曲 + 落点】

## 第二步：先写 4 行骨架再展开
logline / 小愿望（stakes.want）/ 插曲与转折（turn）/ 落点。自检两条：
- 全片**没有人赢走/输掉/受罚任何东西**（赌局框架禁止）；
- 骨架与"喊口号→出丑→心易收拾"有本质区别。

## 第三步：写文件并自校验
写入 08_作品/_共享工具/english-story/stories/{args.word}-{profile["id"]}-【变体名】.json，然后运行：

    cd 08_作品/_共享工具/english-story
    py -3 cli.py validate --story stories/<变体名>.json

ERROR 改到 0（最多 5 轮）；改不动就如实报剩余项。

## 纪律与交回
- 只写自己这一个文件；不改 assets.json/脚本；不建画布、不生成素材；
- 交回一段话：文件路径 / 4 行骨架 / 一句话故事 / 义接 / 道具 / 四项自评与总分 / validate 末行。
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
    p.add_argument("--zh", required=True, help="中文谐音")
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
