"""Upload the exact PIL bubble reference images to Monet storage."""
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "01_资产" / "道具"
OUT = DIR / "bubbles-upload.json"
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"
AUTH = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
GROUP = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((BASE / "app-settings.json").read_text(encoding="utf-8"))
CANVAS_ID = (SETTINGS.get("lastCanvas") or {}).get("canvasId") or "canvas-e4318cc875"
AUTH_USER = AUTH.get("authUser") or GROUP["selectedAigwApp"].removeprefix("_dm_prod_")
API_BASE = "https://backend.monet.dreammaker.netease.com"
STORAGE = "https://storage.monet.dreammaker.netease.com"

HEADERS = {
    "X-Access-Token": AUTH["accessToken"],
    "X-Auth-User": AUTH_USER,
    "X-Aigw-App": GROUP["selectedAigwApp"],
    "X-Group-Id": GROUP["selectedGroupId"],
}

FILES = [
    "心易-开场三气泡.png",
    "心易-气泡-rocklike.png",
    "心易-气泡-snakelike.png",
    "心易-气泡-doglike.png",
]


def main():
    req = urllib.request.Request(f"{API_BASE}/api/storage/token", data=b"{}", headers={**HEADERS, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
    tok = d["data"]
    proxy = tok["proxy_base_url"].rstrip("/")
    items = {}
    for name in FILES:
        src = DIR / name
        raw = src.read_bytes()
        with Image.open(src) as im:
            width, height = im.size
        headers = dict(HEADERS)
        headers.update({
            "Content-Type": "image/png",
            "X-Original-Name": urllib.parse.quote(src.name),
            "Authorization": f"Bearer {tok['token']}",
            "X-Storage-Token": tok["token"],
        })
        url = f"{STORAGE}/v1/objects/{urllib.parse.quote(AUTH_USER)}/{urllib.parse.quote(CANVAS_ID)}/image/"
        req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=180) as r:
            up = json.loads(r.read().decode("utf-8"))
        obj = up["data"]
        items[src.stem] = {
            "url": f"{proxy}/v1/objects{obj['url']}",
            "name": src.name,
            "size": len(raw),
            "width": width,
            "height": height,
            "md5": hashlib.md5(raw).hexdigest(),
        }
        print("uploaded", name, "->", items[src.stem]["url"])
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", OUT)


if __name__ == "__main__":
    main()
