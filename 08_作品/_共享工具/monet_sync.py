# -*- coding: utf-8 -*-
"""Monet 画布覆盖同步器（同一 canvasId，保留已生成输出）

用法：
    py -3 monet_sync.py --canvas <canvasId> --file <x.monet> --dry-run
    py -3 monet_sync.py --canvas <canvasId> --file <x.monet>            # 先建版本快照，再覆盖
    py -3 monet_sync.py --canvas <canvasId> --file <x.monet> --no-version

做三件事：
    1. 读现有画布，列出哪些节点已经有可用输出（status=done 且有 URL）；
    2. 与新 .monet 按节点 ID 做 diff：新增 ADD_NODE、改了参数 PATCH_NODE、删掉 REMOVE_NODE；
       边/组 UPSERT/REMOVE；
    3. 在同一个 canvasId 上 PATCH，输出（图片/视频 URL）原样保留，只重跑真正改过的节点。

前提：新 .monet 的节点 ID 必须和原画布一致（同一生成器、同一 PREFIX）。
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from monet_push import api, patch, verify, clean_node, clean_edge, clean_group, act

TZ = timezone(timedelta(hours=8))


def node_out_count(n):
    return sum(1 for o in (n.get("outputs") or []) if o.get("value") and o.get("status") == "done")


def diff_actions(old, new, seed, with_meta=False, labels_only=False):
    old_nodes = {n["id"]: n for n in old.get("nodes") or []}
    new_nodes = {n["id"]: n for n in new.get("nodes") or []}
    old_edges = {e["id"]: e for e in old.get("edges") or []}
    new_edges = {e["id"]: e for e in new.get("edges") or []}
    old_groups = {g["id"]: g for g in old.get("groups") or []}
    new_groups = {g["id"]: g for g in new.get("groups") or []}

    if labels_only:
        actions, kept, patched = [], 0, 0
        for nid, n in new_nodes.items():
            o = old_nodes.get(nid)
            if not o:
                continue
            if n["meta"].get("label") != o["meta"].get("label"):
                meta = dict(o["meta"])
                meta["label"] = n["meta"]["label"]
                actions.append(act("PATCH_NODE", nid, {"nodeId": nid,
                                                       "patches": [{"op": "replace", "path": "meta", "value": meta}]}, seed))
                patched += 1
            else:
                kept += 1
        return actions, {"kept": kept, "patched": patched, "added": 0, "removed": 0,
                         "edges": len(old_edges), "groups": len(old_groups)}

    fields = ("params", "specialParams", "config") + (("meta",) if with_meta else ())
    actions = []
    kept, patched, added, removed = 0, 0, 0, 0
    for nid, n in new_nodes.items():
        if nid not in old_nodes:
            actions.append(act("ADD_NODE", nid, {"node": clean_node(n)}, seed))
            added += 1
            continue
        o = old_nodes[nid]
        patches = []
        for field in fields:
            if n.get(field) != o.get(field):
                patches.append({"op": "replace", "path": field, "value": n.get(field)})
        if patches:
            actions.append(act("PATCH_NODE", nid, {"nodeId": nid, "patches": patches}, seed))
            patched += 1
        else:
            kept += 1
    for nid in old_nodes:
        if nid not in new_nodes:
            actions.append(act("REMOVE_NODE", nid, {"nodeId": nid}, seed))
            removed += 1

    for eid, e in new_edges.items():
        o = old_edges.get(eid)
        if not o or any(o.get(k) != e.get(k) for k in ("sourceNodeId", "targetNodeId", "sourceHandle", "targetHandle")):
            actions.append(act("UPSERT_EDGE", eid, {"edge": clean_edge(e)}, seed))
    for eid in old_edges:
        if eid not in new_edges:
            actions.append(act("REMOVE_EDGE", eid, {"edgeId": eid}, seed))

    for gid, g in new_groups.items():
        o = old_groups.get(gid)
        if not o or any(o.get(k) != g.get(k) for k in ("nodeIds", "bounds", "label", "style")):
            actions.append(act("UPSERT_GROUP", gid, {"group": clean_group(g)}, seed))
    for gid in old_groups:
        if gid not in new_groups:
            actions.append(act("REMOVE_GROUP", gid, {"groupId": gid}, seed))

    stats = {"kept": kept, "patched": patched, "added": added, "removed": removed,
             "edges": len(old_edges), "groups": len(old_groups)}
    return actions, stats


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--canvas", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-version", action="store_true", help="覆盖前不建版本快照")
    ap.add_argument("--with-meta", action="store_true", help="同时同步节点坐标（默认不覆盖画布里的摆放）")
    ap.add_argument("--labels-only", action="store_true", help="只改节点标签，不动参数/坐标/结构")
    args = ap.parse_args()

    doc = json.loads(Path(args.file).read_text(encoding="utf-8-sig"))
    st, d = api("GET", f"/api/canvas/{args.canvas}")
    if st != 200 or not d.get("success"):
        raise SystemExit(f"读画布失败 {st}: {d}")
    old = d["data"]
    new = doc["canvas"]

    ready = sum(node_out_count(n) for n in old.get("nodes") or [])
    nodes_with_out = sum(1 for n in old.get("nodes") or [] if node_out_count(n))
    print(f"画布「{old.get('name')}」：{len(old.get('nodes') or [])} 节点，"
          f"{nodes_with_out} 个节点已有输出（{ready} 个可用）")
    actions, stats = diff_actions(old, new, new.get("name") or args.canvas, args.with_meta, args.labels_only)
    print(f"diff：保留 {stats['kept']} / 改参数 {stats['patched']} / 新增 {stats['added']} / 删除 {stats['removed']}；"
          f"边 {stats['edges']} / 组 {stats['groups']}；动作 {len(actions)} 条")
    if not actions:
        print("没有差异，不用写。")
        return
    if args.dry_run:
        for a in actions[:20]:
            print("  -", a["type"], json.dumps(a["payload"], ensure_ascii=False)[:100])
        print("dry-run，未写入。")
        return

    if not args.no_version:
        vname = "pre-sync-" + datetime.now(TZ).strftime("%m%d%H%M")  # API 限 20 字
        vst, vd = api("POST", f"/api/canvas/{args.canvas}/history", {"name": vname})
        print("版本快照：", vst, "ok" if vst in (200, 201) and vd.get("success") else json.dumps(vd, ensure_ascii=False)[:200])

    st, d = patch(args.canvas, actions)
    print("PATCH", st, json.dumps(d, ensure_ascii=False)[:300])
    st, detail = verify(args.canvas)
    if detail:
        print(f"回读 {st}: 节点 {len(detail.get('nodes') or [])} / 边 {len(detail.get('edges') or [])} / 组 {len(detail.get('groups') or [])}；"
              f"可用输出 {sum(node_out_count(n) for n in detail.get('nodes') or [])} 个")
    else:
        print("回读失败", st)


if __name__ == "__main__":
    main()
