# -*- coding: utf-8 -*-
"""Upload the 4A/5B character refs and the '失落的' card for the morose key-line canvas."""
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "04_素材" / "参考" / "15s-morose-关键句" / "upload.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"
AUTH = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
GROUP = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((BASE / "app-settings.json").read_text(encoding="utf-8"))
CANVAS_ID = (SETTINGS.get("lastCanvas") or {}).get("canvasId") or "canvas-e4318cc875"
AUTH_USER = AUTH.get("authUser") or GROUP["selectedAigwApp"].removeprefix("_dm_prod_")
API = "https://backend.monet.dreammaker.netease.com"
STORAGE = "https://storage.monet.dreammaker.netease.com"
HEADERS = {"X-Access-Token": AUTH["accessToken"], "X-Auth-User": AUTH_USER,
           "X-Aigw-App": GROUP["selectedAigwApp"], "X-Group-Id": GROUP["selectedGroupId"]}
FILES = [
    ("01_资产/角色", "候选-芽芽-4A-玄凤兜帽-经典灰-毛绒-v1.png"),
    ("01_资产/角色", "候选-芽芽-5A-得意-表情-v2-无星.png"),
    ("01_资产/角色", "候选-芽芽-5B-被抓包-表情-v2-无星.png"),
    ("01_资产/道具", "morose-card-tail-v3-失落的.png"),
    ("01_资产/品牌", "logo-icon-金色-中值去水印.png"),
]


def main():
    req = urllib.request.Request(f"{API}/api/storage/token", data=b"{}",
                                 headers={**HEADERS, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        tok = json.loads(r.read().decode())["data"]
    proxy = tok["proxy_base_url"].rstrip("/")
    out = {}
    for sub, name in FILES:
        src = ROOT / sub / name
        raw = src.read_bytes()
        with Image.open(src) as im:
            w, h = im.size
        headers = dict(HEADERS)
        headers.update({"Content-Type": "image/png", "X-Original-Name": urllib.parse.quote(src.name),
                        "Authorization": f"Bearer {tok['token']}", "X-Storage-Token": tok["token"]})
        url = f"{STORAGE}/v1/objects/{urllib.parse.quote(AUTH_USER)}/{urllib.parse.quote(CANVAS_ID)}/image/"
        req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            up = json.loads(r.read().decode())["data"]
        out[src.stem] = {"url": f"{proxy}/v1/objects{up['url']}", "name": src.name,
                         "size": len(raw), "width": w, "height": h,
                         "md5": hashlib.md5(raw).hexdigest()}
        print("uploaded", name, "->", out[src.stem]["url"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", OUT)


if __name__ == "__main__":
    main()
