# -*- coding: utf-8 -*-
"""Monet 画布导入器（写入，默认只在测试画布上验证）

用法：
    py -3 monet_push.py --test <x.monet> [--keep]
    py -3 monet_push.py --import <x.monet> --name "画布名"
    py -3 monet_push.py --delete <canvasId>

流程（与桌面端导入一致）：
    1. POST /api/canvases {name}      → 新建空画布
    2. PATCH /api/canvas/:id/actions  → ADD_NODE / UPSERT_EDGE / UPSERT_GROUP
    3. GET  /api/canvas/:id           → 回读校验

安全：--test 默认建临时画布、验证后删除；--import 只新建，不覆盖任何现有画布。
凭据：运行时从本机 auth.json 读，不落盘。
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

API = "https://backend.monet.dreammaker.netease.com"
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"
TZ = timezone(timedelta(hours=8))


def headers():
    auth = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
    group = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
    return {
        "X-Access-Token": auth["accessToken"],
        "X-Auth-User": auth["authUser"],
        "X-Aigw-App": group.get("selectedAigwApp", ""),
        "X-Group-Id": group.get("selectedGroupId", ""),
    }


def api(method, path, body=None):
    h = headers()
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")
        return e.code, {"error": raw[:500]}


def act(kind, key, payload, seed):
    return {
        "id": "act-" + hashlib.md5((seed + kind + key).encode("utf-8")).hexdigest()[:12],
        "type": kind,
        "timestamp": datetime.now(TZ).isoformat(timespec="milliseconds"),
        "payload": payload,
    }


NODE_DROP = {"createdAt", "createdBy", "updatedAt", "updatedBy"}
OUT_DROP = {"taskSource", "taskId", "createdAt", "createdBy", "updatedAt", "updatedBy", "size", "md5"}


def clean_node(n):
    node = {k: v for k, v in n.items() if k not in NODE_DROP}
    node["outputs"] = [{k: v for k, v in o.items() if k not in OUT_DROP} for o in (n.get("outputs") or [])]
    # 服务端要求 mainOutputId 必须命中本节点 outputs；空输出 / 旧指针都会 422 或整节点失败
    out_ids = [o.get("id") for o in node["outputs"] if o.get("id")]
    if not out_ids:
        node["mainOutputId"] = None
    elif node.get("mainOutputId") not in out_ids:
        node["mainOutputId"] = out_ids[0]
    return node


def clean_edge(e):
    return {k: v for k, v in e.items() if k not in NODE_DROP}


def clean_group(g):
    return {k: v for k, v in g.items() if k not in NODE_DROP}


def build_actions(doc, subset=None):
    nodes = doc["canvas"]["nodes"]
    edges = doc["canvas"]["edges"]
    groups = doc["canvas"]["groups"]
    if subset:
        keep = set(subset)
        nodes = [n for n in nodes if n["id"] in keep]
        groups = [g for g in groups if set(g["nodeIds"]) & keep]
        edges = [e for e in edges if e["sourceNodeId"] in keep and e["targetNodeId"] in keep]
    seed = doc["canvas"]["name"]
    actions = []
    for n in nodes:
        actions.append(act("ADD_NODE", n["id"], {"node": clean_node(n)}, seed))
    for e in edges:
        actions.append(act("UPSERT_EDGE", e["id"], {"edge": clean_edge(e)}, seed))
    for g in groups:
        actions.append(act("UPSERT_GROUP", g["id"], {"group": clean_group(g)}, seed))
    return actions, len(nodes), len(edges), len(groups)


def create_canvas(name):
    st, d = api("POST", "/api/canvases", {"name": name})
    if st not in (200, 201) or not d.get("success"):
        raise SystemExit(f"建画布失败 {st}: {d}")
    return d["data"]["id"]


def patch(canvas_id, actions):
    st, d = api("PATCH", f"/api/canvas/{canvas_id}/actions", {"actions": actions})
    return st, d


def verify(canvas_id):
    st, d = api("GET", f"/api/canvas/{canvas_id}")
    if st != 200 or not d.get("success"):
        return st, None
    return st, d["data"]


def delete(canvas_id):
    st, d = api("DELETE", f"/api/canvas/{canvas_id}")
    return st, d


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", metavar="MONET")
    ap.add_argument("--import", dest="imp", metavar="MONET")
    ap.add_argument("--name")
    ap.add_argument("--delete", metavar="CANVAS_ID")
    ap.add_argument("--yes", action="store_true", help="--delete 必须显式加 --yes 才会真删")
    ap.add_argument("--keep", action="store_true", help="--test 后保留画布")
    args = ap.parse_args()

    if args.delete:
        if not args.yes:
            st, d = api("GET", f"/api/canvas/{args.delete}")
            if st == 200 and d.get("success"):
                c = d["data"]
                print(f"将要删除：{args.delete}「{c.get('name')}」"
                      f"（{len(c.get('nodes') or [])} 节点 / {len(c.get('edges') or [])} 边 / {len(c.get('groups') or [])} 组）")
            else:
                print(f"读不到 {args.delete}（{st}）；请先用 monet_pull.py --list 核对 id")
            print("确认无误后重跑：--delete <canvasId> --yes")
            return
        st, d = delete(args.delete)
        print("DELETE", st, json.dumps(d, ensure_ascii=False)[:300])
        return

    if args.test:
        doc = load(args.test)
        # 子集：角色图 + 场景（生成或复用均可）+ 第一条视频，及其边/组
        nodes = doc["canvas"]["nodes"]
        pick = []
        for n in nodes:
            lab = (n.get("meta") or {}).get("label") or ""
            if n["type"] == "input-image" and len(pick) < 2:
                pick.append(n["id"])
            elif n["type"] in ("input-image", "gen-image") and "场景" in lab and n["id"] not in pick:
                pick.append(n["id"])
            elif n["type"] == "gen-video":
                pick.append(n["id"])
                break
        if len(pick) < 3:
            raise SystemExit(f"没凑齐测试子集：{pick}")
        actions, nn, ne, ng = build_actions(doc, subset=pick)
        name = "TEST-导入验证-" + datetime.now(TZ).strftime("%m%d%H%M")
        cid = create_canvas(name)
        print(f"建画布 {cid}「{name}」；准备写 {nn} 节点 / {ne} 边 / {ng} 组")
        st, d = patch(cid, actions)
        print("PATCH", st, json.dumps(d, ensure_ascii=False)[:400])
        st, detail = verify(cid)
        if detail:
            print(f"回读 {st}: 节点 {len(detail.get('nodes') or [])} / 边 {len(detail.get('edges') or [])} / 组 {len(detail.get('groups') or [])}")
            for n in detail.get("nodes") or []:
                print("  -", n["type"], (n.get("meta") or {}).get("label"))
        if not args.keep:
            st, d = delete(cid)
            print("DELETE", st, "（测试画布已删）" if st == 200 else d)
        else:
            print("保留测试画布：", cid)
        return

    if args.imp:
        doc = load(args.imp)
        name = args.name or doc["canvas"]["name"]
        actions, nn, ne, ng = build_actions(doc)
        cid = create_canvas(name)
        print(f"建画布 {cid}「{name}」；准备写 {nn} 节点 / {ne} 边 / {ng} 组")
        st, d = patch(cid, actions)
        print("PATCH", st, json.dumps(d, ensure_ascii=False)[:400])
        st, detail = verify(cid)
        if detail:
            print(f"回读 {st}: 节点 {len(detail.get('nodes') or [])} / 边 {len(detail.get('edges') or [])} / 组 {len(detail.get('groups') or [])}")
            print("canvasId:", cid)
        else:
            print("回读失败", st)
        return

    print(__doc__)


if __name__ == "__main__":
    main()
