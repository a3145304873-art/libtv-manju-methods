# -*- coding: utf-8 -*-
"""Monet 画布拉取器（只读）

用途：不导出、不截图，直接把 Monet 账号里的画布状态和已生成结果拉到本地，
      供审查/对照/重做。

用法：
    py -3 monet_pull.py --list
    py -3 monet_pull.py --pull <canvasId 或 名称片段> [--media images|all|none] [--limit N]

只读：只发 GET（列表、详情）与取 storage token 的 POST；不导入、不派发、不改画布。
凭据：运行时从 %APPDATA%\\@monet\\desktop-prod\\auth.json 读取，不复制、不落盘。
输出：pulls/<canvasId>/canvas.json + manifest.json + media/*
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://backend.monet.dreammaker.netease.com"
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"
OUT_ROOT = Path(__file__).resolve().parent / "pulls"


def load_headers():
    auth = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
    group = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
    return {
        "X-Access-Token": auth["accessToken"],
        "X-Auth-User": auth["authUser"],
        "X-Aigw-App": group.get("selectedAigwApp", ""),
        "X-Group-Id": group.get("selectedGroupId", ""),
    }


def api_get(path, headers):
    req = urllib.request.Request(API + path, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def list_canvases(headers):
    d = api_get("/api/canvases", headers)
    items = (d.get("data") or {}).get("items") or []
    return items


def pick_canvas(items, selector):
    exact = [c for c in items if c.get("id") == selector]
    if exact:
        return exact[0]
    hits = [c for c in items if selector.lower() in (c.get("name") or "").lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise SystemExit(f"没找到画布：{selector}")
    names = "\n".join(f"  {c['id']}  {c.get('name')}" for c in hits)
    raise SystemExit(f"匹配到 {len(hits)} 个，请写更具体或直接用 id：\n{names}")


def ext_of(url, fallback="bin"):
    path = urllib.parse.urlparse(url).path
    m = re.search(r"\.(png|jpg|jpeg|webp|mp4|mov|mp3|wav)$", path, re.I)
    return m.group(1).lower() if m else fallback


def safe(name, limit=60):
    name = re.sub(r'[\\/:*?"<>|\s]+', "_", name).strip("_")
    return name[:limit] or "node"


_STORAGE_TOKEN = None


def api_post(path, headers, payload=b"{}"):
    h = dict(headers)
    h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=payload, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def storage_token(headers):
    global _STORAGE_TOKEN
    if not _STORAGE_TOKEN:
        _STORAGE_TOKEN = api_post("/api/storage/token", headers)["data"]["token"]
    return _STORAGE_TOKEN


def download(url, dst, headers):
    tok = storage_token(headers)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + tok,
        "User-Agent": "monet-pull/1.0",
    }, method="GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return len(data)


def pull(canvas_id, headers, media="images", limit=0):
    detail = api_get(f"/api/canvas/{canvas_id}", headers)["data"]
    out_dir = OUT_ROOT / canvas_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "canvas.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    rows, jobs = [], []
    for n in detail.get("nodes") or []:
        label = (n.get("meta") or {}).get("label") or n.get("id")
        for o in n.get("outputs") or []:
            url = o.get("value") or ""
            if not url.startswith("http"):
                continue
            ext = ext_of(url)
            kind = "video" if ext in ("mp4", "mov") else "audio" if ext in ("mp3", "wav") else "image"
            if media == "none":
                continue
            if media == "images" and kind != "image":
                continue
            dst = out_dir / "media" / f"{safe(label)}_{o.get('id','out')}.{ext}"
            jobs.append((n.get("id"), label, n.get("type"), kind, o.get("status"), url, dst))

    if limit:
        jobs = jobs[:limit]

    for nid, label, ntype, kind, status, url, dst in jobs:
        try:
            size = download(url, dst, headers)
            rows.append({"node": nid, "label": label, "type": ntype, "kind": kind,
                         "status": status, "url": url, "file": str(dst.relative_to(out_dir)), "bytes": size})
            print(f"  ↓ {dst.name}  {size//1024} KB")
        except Exception as e:
            rows.append({"node": nid, "label": label, "kind": kind, "status": status, "url": url,
                         "file": None, "error": str(e)})
            print(f"  ! 下载失败 {label}: {e}")

    manifest = {
        "canvas": {k: detail.get(k) for k in ("id", "name", "description", "revision", "updatedAt")},
        "counts": {"nodes": len(detail.get("nodes") or []), "edges": len(detail.get("edges") or []),
                   "groups": len(detail.get("groups") or [])},
        "outputs": rows,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n画布：{detail.get('name')}")
    print(f"节点 {len(detail.get('nodes') or [])} / 边 {len(detail.get('edges') or [])} / 组 {len(detail.get('groups') or [])}；"
          f"下载 {len(rows)} 个输出")
    print(f"目录：{out_dir}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Monet 画布只读拉取")
    ap.add_argument("--list", action="store_true", help="列出画布")
    ap.add_argument("--pull", metavar="CANVAS", help="按 id 或名称片段拉取")
    ap.add_argument("--media", choices=["images", "all", "none"], default="images")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    headers = load_headers()
    if args.list or not args.pull:
        items = list_canvases(headers)
        items.sort(key=lambda c: c.get("updatedAt") or "", reverse=True)
        print(f"{len(items)} 个画布（按更新时间）：")
        for c in items:
            print(f"  {c['id']}  rev={c.get('revision')}  {c.get('updatedAt','')[:19]}  {c.get('name')}")
        return
    canvas = pick_canvas(list_canvases(headers), args.pull)
    pull(canvas["id"], headers, args.media, args.limit)


if __name__ == "__main__":
    main()
