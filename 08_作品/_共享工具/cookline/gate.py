# -*- coding: utf-8 -*-
"""分镜闸门：把「网格没定稿不要跑关键帧」变成会拒绝的机制。

签核绑定三样东西：菜谱卡哈希、画布文件哈希、画布提示词 digest。
卡一改、画布一手改，旧签核立刻失效，runlist 不再放行。
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from . import canvas as canvas_mod
from . import checks
from .model import recipe_hash

STAGES = ["assets", "storyboard", "keys", "videos"]
STAGE_NAMES = {
    "assets": "01 场景 + 02 道具",
    "storyboard": "03 分镜图（分镜闸门）",
    "keys": "04 段首帧",
    "videos": "05 视频段",
}


class GateError(RuntimeError):
    pass


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gates_path(recipe_path: Path) -> Path:
    return recipe_path.with_name(recipe_path.stem + ".gates.json")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_canvas(recipe_path: Path, card: dict) -> Path | None:
    """找同一道菜、同一份卡构建出来的最新画布。

    菜谱卡通常在 02_画布/recipes/，画布在 02_画布/；所以从卡目录和它的上一级各找一遍。
    """
    want = recipe_hash(card)
    roots = [recipe_path.parent]
    if recipe_path.parent.parent.exists():
        roots.append(recipe_path.parent.parent)
    best, best_mtime = None, -1.0
    seen = set()
    for root in roots:
        for side in root.rglob("*.monet.cookline.json"):
            if side in seen:
                continue
            seen.add(side)
            try:
                data = _read_json(side)
            except Exception:
                continue
            if data.get("recipe_sha256") != want:
                continue
            canvas_path = side.with_name(side.name[: -len(".cookline.json")])
            if canvas_path.exists() and canvas_path.stat().st_mtime > best_mtime:
                best, best_mtime = canvas_path, canvas_path.stat().st_mtime
    return best


def load(recipe_path: Path) -> dict:
    p = gates_path(recipe_path)
    if not p.exists():
        return {"recipe": recipe_path.name, "gates": []}
    return _read_json(p)


def _record_for(data: dict, stage: str) -> dict | None:
    for g in data.get("gates", []):
        if g.get("stage") == stage:
            return g
    return None


def _fresh(rec: dict | None, card: dict, canvas_path: Path | None) -> bool:
    if not rec or not canvas_path or not canvas_path.exists():
        return False
    return rec.get("recipe_sha256") == recipe_hash(card) and rec.get("canvas_sha256") == _sha_file(canvas_path)


def approve(recipe_path: Path, card: dict, stage: str, note: str, by: str = "user") -> dict:
    if stage not in STAGES:
        raise GateError(f"未知闸门 {stage}；可用：{'、'.join(STAGES)}")
    if len(note.strip()) < 4:
        raise GateError("签核必须写一句看到了什么（至少 4 个字），不能只点同意")
    rep = checks.check(card, strict=True)
    if not rep.ok(strict=True):
        raise GateError("校验没过，不能签核：\n" + rep.text(strict=True))

    canvas_path = find_canvas(recipe_path, card)
    if not canvas_path:
        raise GateError("找不到用这份卡构建的画布；先跑 cookline build")
    side_path = canvas_path.with_name(canvas_path.name + ".cookline.json")
    side = _read_json(side_path) if side_path.exists() else {}
    run_path = canvas_path.with_name(canvas_path.name + ".runlist.json")
    if not run_path.exists():
        raise GateError("找不到 runlist；先跑 cookline build")

    data = load(recipe_path)
    for prev in STAGES[: STAGES.index(stage)]:
        rec = _record_for(data, prev)
        if not _fresh(rec, card, canvas_path):
            raise GateError(f"上一道闸门「{STAGE_NAMES[prev]}」还没签核或已失效；先过它")

    rec = {
        "stage": stage,
        "at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "by": by,
        "note": note.strip(),
        "recipe_sha256": recipe_hash(card),
        "canvas_sha256": _sha_file(canvas_path),
        "canvas": canvas_path.name,
        "prompt_digest": side.get("prompt_digest"),
    }
    data["recipe"] = recipe_path.name
    data["canvas"] = canvas_path.name
    data["gates"] = [g for g in data.get("gates", []) if g.get("stage") != stage] + [rec]
    data["gates"].sort(key=lambda g: STAGES.index(g["stage"]) if g.get("stage") in STAGES else 99)
    _write_json(gates_path(recipe_path), data)
    return rec


def status(recipe_path: Path, card: dict) -> tuple[list[dict], str | None]:
    canvas_path = find_canvas(recipe_path, card)
    data = load(recipe_path)
    rows = []
    for stage in STAGES:
        rec = _record_for(data, stage)
        if not rec:
            state = "PENDING"
        elif _fresh(rec, card, canvas_path):
            state = "APPROVED"
        else:
            state = "STALE"
        rows.append({"stage": stage, "name": STAGE_NAMES[stage], "state": state, "record": rec})
    nxt = next((r["stage"] for r in rows if r["state"] != "APPROVED"), None)
    return rows, nxt


def runlist_nodes(recipe_path: Path, card: dict, stage: str) -> list[str]:
    if stage not in STAGES:
        raise GateError(f"未知阶段 {stage}；可用：{'、'.join(STAGES)}")
    canvas_path = find_canvas(recipe_path, card)
    if not canvas_path:
        raise GateError("找不到用这份卡构建的画布；先跑 cookline build")
    run_path = canvas_path.with_name(canvas_path.name + ".runlist.json")
    if not run_path.exists():
        raise GateError("找不到 runlist；先跑 cookline build")
    run = _read_json(run_path)
    if run.get("recipe_sha256") != recipe_hash(card):
        raise GateError("卡改过但画布没重建；先跑 cookline build")
    rows, _ = status(recipe_path, card)
    idx = STAGES.index(stage)
    for row in rows[: idx + 1]:
        if row["state"] == "APPROVED":
            continue
        if row["state"] == "STALE":
            raise GateError(f"「{row['name']}」的签核已失效（卡或画布变了），重新签核")
        raise GateError(f"「{row['name']}」还没签核；按顺序先过它")
    return (run.get("stages") or {}).get(stage, [])
