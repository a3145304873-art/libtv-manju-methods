"""Upload the new 心易 (cat-ear) reference image to Monet storage.

Reads the local Monet desktop auth, requests a storage token, uploads the
white-background PNG, and writes the permanent URL + metadata to
01_资产/角色/心易-猫耳版-upload.json. Tokens are never printed.
"""
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]          # 蛋仔记单词
SRC = ROOT / "01_资产" / "角色" / "心易-猫耳版-白底.png"
OUT = ROOT / "01_资产" / "角色" / "心易-猫耳版-upload.json"
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


def post_json(url: str, body: bytes):
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    d = post_json(f"{API_BASE}/api/storage/token", b"{}")
    if not d.get("success") or not (d.get("data") or {}).get("token"):
        raise RuntimeError("storage token request failed")
    tok = d["data"]
    proxy = tok["proxy_base_url"].rstrip("/")
    raw = SRC.read_bytes()
    with Image.open(SRC) as im:
        width, height = im.size
    headers = dict(HEADERS)
    headers.update({
        "Content-Type": "image/png",
        "X-Original-Name": urllib.parse.quote(SRC.name),
        "Authorization": f"Bearer {tok['token']}",
        "X-Storage-Token": tok["token"],
    })
    url = f"{STORAGE}/v1/objects/{urllib.parse.quote(AUTH_USER)}/{urllib.parse.quote(CANVAS_ID)}/image/"
    req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        up = json.loads(r.read().decode("utf-8"))
    if not up.get("success") or not (up.get("data") or {}).get("url"):
        raise RuntimeError(f"upload failed: {up}")
    obj = up["data"]
    item = {
        "url": f"{proxy}/v1/objects{obj['url']}",
        "name": SRC.name,
        "size": len(raw),
        "width": width,
        "height": height,
        "md5": hashlib.md5(raw).hexdigest(),
        "server_name": obj.get("filename") or "",
        "canvasId": CANVAS_ID,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: item[k] for k in ("url", "name", "width", "height", "size", "md5")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

