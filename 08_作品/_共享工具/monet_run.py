# -*- coding: utf-8 -*-
"""Monet 派发器（运行节点生成）—— 首次实现，2026-11-03

背景：`monet_pull/push/sync` 只能读、导入、覆盖；**派发**（POST /nodes/generate）此前未打通。
本脚本按 `@monet/types` 里的接口契约试派发：

    请求体形状来自 OutputGenerationParams（其文档写明"即前端调用 POST /nodes/generate 传入的原始请求体"）：
        { node_id, node_type, canvas_id, num, model_id, model_params, references }

用法：
    py -3 monet_run.py --canvas canvas-xxxx --node node-xxxx          # 派发一次
    py -3 monet_run.py --canvas canvas-xxxx --node node-xxxx --wait   # 派发并轮询到出结果
    py -3 monet_run.py --canvas canvas-xxxx --node node-xxxx --dump   # 只打印将要发送的请求体

安全：
    · 只派发**指定节点**，不会整组跑；
    · --dump 不发请求；
    · 失败时打印服务端返回，便于修正 schema。
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://backend.monet.dreammaker.netease.com"
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"


def headers():
    auth = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
    group = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
    return {
        "X-Access-Token": auth["accessToken"],
        "X-Auth-User": auth["authUser"],
        "X-Aigw-App": group.get("selectedAigwApp", ""),
        "X-Group-Id": group.get("selectedGroupId", ""),
    }


def api(method, path, body=None, timeout=90):
    h = headers()
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"error": raw[:800]}
    except Exception as e:
        return -1, {"error": str(e)}


def get_canvas(cid):
    st, d = api("GET", f"/api/canvas/{cid}")
    if st != 200 or not d.get("success"):
        raise SystemExit(f"读画布失败 {st}: {json.dumps(d, ensure_ascii=False)[:300]}")
    return d["data"]


def build_body(canvas, node_id):
    nodes = {n["id"]: n for n in canvas.get("nodes") or []}
    node = nodes.get(node_id)
    if not node:
        raise SystemExit(f"画布里没有节点 {node_id}")
    p = node.get("params") or {}
    refs = [e for e in (canvas.get("edges") or []) if e.get("targetNodeId") == node_id]
    inputs = []
    for e in refs:
        src = nodes.get(e.get("sourceNodeId"))
        if not src:
            continue
        outs = src.get("outputs") or []
        inputs.append({
            "node_id": src["id"],
            "node_type": src.get("type"),
            "value": (outs[0].get("value") if outs else None),
            "name": (outs[0].get("name") if outs else None),
        })
    body = {
        "canvas_id": canvas["id"],
        "node_id": node_id,
        "node_type": node.get("type"),
        "num": p.get("num", 1),
        "model_id": p.get("model_id"),
        "model_params": p.get("model_params") or {},
        "references": inputs,
    }
    return node, body


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--canvas", required=True)
    ap.add_argument("--node", required=True)
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    canvas = get_canvas(args.canvas)
    node, body = build_body(canvas, args.node)
    print("节点:", node.get("type"), (node.get("meta") or {}).get("label"))
    print("模型:", body["model_id"], "| num:", body["num"], "| 引用:", len(body["references"]))
    print("prompt 字数:", len((body["model_params"] or {}).get("prompt") or ""))
    if args.dump:
        print(json.dumps(body, ensure_ascii=False, indent=1)[:2000])
        return

    st, d = api("POST", "/api/nodes/generate", body)
    print("POST /api/nodes/generate →", st)
    print(json.dumps(d, ensure_ascii=False)[:600])
    if not args.wait or st not in (200, 201):
        return

    t0 = time.time()
    while time.time() - t0 < args.timeout:
        time.sleep(8)
        try:
            c = get_canvas(args.canvas)
        except SystemExit:
            continue
        n = next((x for x in c.get("nodes") or [] if x["id"] == args.node), None)
        outs = (n or {}).get("outputs") or []
        st_ = outs[0].get("status") if outs else None
        print(f"  [{int(time.time()-t0):3d}s] outputs={len(outs)} status={st_}")
        if outs and st_ in ("done", "failed"):
            print(json.dumps(outs[0], ensure_ascii=False)[:600])
            return
    print("等待超时，可稍后用 monet_pull.py 拉结果")


if __name__ == "__main__":
    main()
