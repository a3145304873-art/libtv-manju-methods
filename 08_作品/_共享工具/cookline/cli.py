# -*- coding: utf-8 -*-
"""cookline 命令行。"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from . import canvas as canvas_mod
from . import checks, gate, model, rules
from .compose import compose


def _p(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8", "replace"))


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def _load(path: str) -> dict:
    card = model.load(path)
    card["_path"] = str(path)
    return card


def cmd_check(args) -> int:
    card = _load(args.recipe)
    rep = checks.check(card, strict=args.strict)
    if args.json:
        _p(json.dumps({
            "ok": rep.ok(args.strict),
            "errors": [{"id": i.fid, "where": i.where, "message": i.message} for i in rep.errors],
            "warnings": [{"id": i.fid, "where": i.where, "message": i.message} for i in rep.warnings],
            "humans": [h["id"] for h in rep.humans],
        }, ensure_ascii=False, indent=2))
    else:
        _p(rep.text(f"检查 {Path(args.recipe).name}", strict=args.strict))
    return 0 if rep.ok(args.strict) else 1


def cmd_build(args) -> int:
    card = _load(args.recipe)
    rep = checks.check(card, strict=True)
    if not rep.ok(strict=True):
        _p(rep.text(f"构建前检查未过：{Path(args.recipe).name}", strict=True))
        _p("\n没有写文件。先把上面的 ERROR/WARN 清掉；WARN 也要清，闸门只放行 strict。")
        return 1
    plan = compose(card)
    out = Path(args.out) if args.out else Path(args.recipe).with_suffix(".monet")
    side_path = out.with_name(out.name + ".cookline.json")
    if out.exists() and not side_path.exists() and not args.force:
        _p(f"{out} 已存在，但不是 cookline 生成的；确认要覆盖加 --force")
        return 1

    ts = _now()
    canvas = canvas_mod.build(card, plan, ts)
    side = canvas_mod.sidecar(canvas, card, model.recipe_hash(card), ts)
    audit = canvas_mod.audit(canvas, card, side)
    if not audit.ok(strict=False):
        _p(audit.text(f"画布自检未过：{out.name}"))
        return 1

    canvas_mod.write(out, canvas)
    run = canvas_mod.runlist(canvas, card)
    out.with_name(out.name + ".runlist.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    side["canvas_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    side_path.write_text(json.dumps(side, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    srt = out.with_suffix(".srt")
    srt.write_text(plan.srt, encoding="utf-8")

    _p(f"已生成 {out.name}：{len(canvas['canvas']['nodes'])} 节点 / "
       f"{len(canvas['canvas']['edges'])} 边 / {len(canvas['canvas']['groups'])} 组")
    for v in plan.videos:
        _p(f"  {v.label.split(' · ')[0]}：{len(v.prompt)} 字")
    _p(f"  字幕：{srt.name}（{len(card.get('post', {}).get('subtitles') or [])} 条；只进后期）")
    rows, nxt = gate.status(Path(args.recipe), card)
    _p("闸门：" + " / ".join(f"{r['stage']}={r['state']}" for r in rows))
    if nxt:
        _p(f"下一步：cookline gate approve \"{args.recipe}\" --stage {nxt} --note \"看到了什么\"")
    return 0


def cmd_srt(args) -> int:
    card = _load(args.recipe)
    out = Path(args.out) if args.out else Path(args.recipe).with_suffix(".srt")
    out.write_text(compose(card).srt, encoding="utf-8")
    _p(f"已写 {out}")
    return 0


def cmd_approve(args) -> int:
    card = _load(args.recipe)
    rec = gate.approve(Path(args.recipe), card, args.stage, args.note, args.by)
    _p(f"已签核 {rec['stage']}（{rec['at']}）：{rec['note']}")
    rows, nxt = gate.status(Path(args.recipe), card)
    _p("闸门：" + " / ".join(f"{r['stage']}={r['state']}" for r in rows))
    if nxt:
        _p(f"下一道：cookline gate approve \"{args.recipe}\" --stage {nxt} --note \"看到了什么\"")
    else:
        _p(f"全部签核；派发用 cookline runlist \"{args.recipe}\" --stage videos")
    return 0


def cmd_status(args) -> int:
    card = _load(args.recipe)
    rows, nxt = gate.status(Path(args.recipe), card)
    for r in rows:
        rec = r["record"] or {}
        note = f"｜{rec.get('note')}" if rec.get("note") else ""
        _p(f"{r['stage']:<11} {r['state']:<9} {r['name']}{note}")
    _p(f"下一道：{nxt or '全部已签核（仍需人工看出片）'}")
    return 0


def cmd_runlist(args) -> int:
    card = _load(args.recipe)
    nodes = gate.runlist_nodes(Path(args.recipe), card, args.stage)
    canvas_path = gate.find_canvas(Path(args.recipe), card)
    labels = {}
    if canvas_path:
        data = json.loads(canvas_path.read_text(encoding="utf-8"))
        labels = {n["id"]: (n.get("meta") or {}).get("label", n["id"]) for n in data["canvas"]["nodes"]}
    _p(f"放行 {gate.STAGE_NAMES[args.stage]}：{len(nodes)} 个节点")
    for nid in nodes:
        _p(f"  {nid}  {labels.get(nid, '')}")
    _p("派发仍需用户明确说「跑」；本命令只放行，不扣费。")
    return 0


def cmd_doctor(args) -> int:
    data = json.loads(Path(args.canvas).read_text(encoding="utf-8"))
    card = _load(args.recipe) if args.recipe else None
    side_path = Path(str(args.canvas) + ".cookline.json")
    side = json.loads(side_path.read_text(encoding="utf-8")) if side_path.exists() else None
    rep = canvas_mod.audit(data, card, side)
    if not side:
        rep.notes.append("没有 cookline 边车；无法确认是否手改，也无法对比卡版本")
    _p(rep.text(f"审计 {Path(args.canvas).name}"))
    return 0 if rep.ok() else 1


def cmd_migrate(args) -> int:
    data = model.migrate(args.recipe, args.out)
    _p(f"已迁移 {args.recipe} → {args.out}；{len(data.get('segments') or [])} 段；"
       "旧卡没有 props/hand/state 账本，check 会给出降级警告")
    return 0


def cmd_new(args) -> int:
    tpl = Path(__file__).resolve().parent / "templates" / "recipe.skeleton.json"
    data = json.loads(tpl.read_text(encoding="utf-8"))
    data["series"] = args.series
    data["ep"] = args.ep
    data["dish"] = args.dish
    data["series_title"] = args.series_title or f"今天做{args.dish} 明天呢"
    data["character"]["name"] = args.character or data["character"]["name"]
    out = Path(args.out) if args.out else Path(f"{args.ep}-{args.dish}.json")
    if out.exists() and not args.force:
        _p(f"{out} 已存在；加 --force 覆盖")
        return 1
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _p(f"已写 {out}；先按做菜短片规划卡确定本菜流程与段数，再填 areas、props 和每段 duration_seconds/beats/storyboard_frames，最后 check")
    return 0


def cmd_rules(args) -> int:
    for f in rules.FAILURES:
        _p(f"{f['id']}  {f['severity']:<6} {f['layer']:<9} {f['title']}｜{f['fix']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cookline", description="做菜线：菜谱卡 → 校验 → 分镜闸门 → Monet 画布")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("check", help="校验菜谱卡")
    p.add_argument("recipe")
    p.add_argument("--strict", action="store_true", help="WARN 也算不合格（交付用）")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("build", help="生成 .monet / runlist / 边车 / srt")
    p.add_argument("recipe")
    p.add_argument("-o", "--out")
    p.add_argument("--force", action="store_true", help="覆盖非 cookline 生成的同名画布")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("srt", help="只出字幕")
    p.add_argument("recipe")
    p.add_argument("-o", "--out")
    p.set_defaults(func=cmd_srt)

    p = sub.add_parser("gate", help="分镜闸门签核")
    gsub = p.add_subparsers(dest="gate_cmd", required=True)
    a = gsub.add_parser("approve")
    a.add_argument("recipe")
    a.add_argument("--stage", required=True, choices=gate.STAGES)
    a.add_argument("--note", required=True)
    a.add_argument("--by", default="user")
    a.set_defaults(func=cmd_approve)
    s = gsub.add_parser("status")
    s.add_argument("recipe")
    s.set_defaults(func=cmd_status)

    p = sub.add_parser("runlist", help="过闸门后打印可派发节点")
    p.add_argument("recipe")
    p.add_argument("--stage", required=True, choices=gate.STAGES)
    p.set_defaults(func=cmd_runlist)

    p = sub.add_parser("doctor", help="审计任意 .monet 是否被手改/接线是否断")
    p.add_argument("canvas")
    p.add_argument("--recipe")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("migrate", help="旧菜谱卡迁到 v2")
    p.add_argument("recipe")
    p.add_argument("-o", "--out", required=True)
    p.set_defaults(func=cmd_migrate)

    p = sub.add_parser("new", help="按模板起一张新菜谱卡")
    p.add_argument("--series", required=True)
    p.add_argument("--ep", required=True)
    p.add_argument("--dish", required=True)
    p.add_argument("--series-title")
    p.add_argument("--character")
    p.add_argument("-o", "--out")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("rules", help="列出 29 条拦截")
    p.set_defaults(func=cmd_rules)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except gate.GateError as exc:
        _p(f"闸门拒绝：{exc}")
        return 1
    except FileNotFoundError as exc:
        _p(f"找不到文件：{exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
