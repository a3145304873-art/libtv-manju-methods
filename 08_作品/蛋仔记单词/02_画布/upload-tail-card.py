"""Upload the three-card tail still to Monet."""
import hashlib, json, os, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "01_资产" / "道具" / "三卡-木桌-tail.png"
OUT = ROOT / "01_资产" / "道具" / "tail-upload.json"
BASE = Path(os.environ.get("APPDATA", "")) / "@monet" / "desktop-prod"
AUTH = json.loads((BASE / "auth.json").read_text(encoding="utf-8"))
GROUP = json.loads((BASE / "dm-group.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((BASE / "app-settings.json").read_text(encoding="utf-8"))
CANVAS_ID = (SETTINGS.get("lastCanvas") or {}).get("canvasId") or "canvas-e4318cc875"
AUTH_USER = AUTH.get("authUser") or GROUP["selectedAigwApp"].removeprefix("_dm_prod_")
API = "https://backend.monet.dreammaker.netease.com"
STORAGE = "https://storage.monet.dreammaker.netease.com"
H = {"X-Access-Token": AUTH["accessToken"], "X-Auth-User": AUTH_USER,
     "X-Aigw-App": GROUP["selectedAigwApp"], "X-Group-Id": GROUP["selectedGroupId"]}

req = urllib.request.Request(f"{API}/api/storage/token", data=b"{}", headers={**H, "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=30) as r:
    tok = json.loads(r.read().decode())["data"]
raw = SRC.read_bytes()
with Image.open(SRC) as im:
    w, h = im.size
headers = dict(H)
headers.update({"Content-Type": "image/png", "X-Original-Name": urllib.parse.quote(SRC.name),
                "Authorization": f"Bearer {tok['token']}", "X-Storage-Token": tok["token"]})
url = f"{STORAGE}/v1/objects/{urllib.parse.quote(AUTH_USER)}/{urllib.parse.quote(CANVAS_ID)}/image/"
req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
with urllib.request.urlopen(req, timeout=180) as r:
    up = json.loads(r.read().decode())["data"]
item = {"url": f"{tok['proxy_base_url'].rstrip('/')}/v1/objects{up['url']}", "name": SRC.name,
        "size": len(raw), "width": w, "height": h, "md5": hashlib.md5(raw).hexdigest()}
OUT.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(item, ensure_ascii=False, indent=2))
