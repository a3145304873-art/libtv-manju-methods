# -*- coding: utf-8 -*-
"""把 .monet 渲染成一张预览图（看清分组、节点、接线方向），便于导入前先审。"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    SRC = Path(sys.argv[1])
else:
    SRC = max(HERE.glob("*.monet"), key=lambda p: p.stat().st_mtime)
VER = SRC.stem.split("-")[-1]
OUT = HERE / f"画布预览-{VER}.png"

TYPE_COLOR = {
    "input-image": (142, 141, 224),
    "input-text": (136, 136, 136),
    "gen-image": (91, 141, 224),
    "gen-video": (224, 161, 91),
}
TYPE_TAG = {
    "input-image": "上传·图",
    "input-text": "文字",
    "gen-image": "生图",
    "gen-video": "生视频",
}
FONT = "C:/Windows/Fonts/"


def f(size, bold=False):
    return ImageFont.truetype(FONT + ("msyhbd.ttc" if bold else "msyh.ttc"), size)


def main():
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    c = doc["canvas"]
    nodes, edges, groups = c["nodes"], c["edges"], c["groups"]
    by_id = {n["id"]: n for n in nodes}

    xs = [n["meta"]["x"] for n in nodes] + [g["bounds"]["x"] for g in groups]
    ys = [n["meta"]["y"] for n in nodes] + [g["bounds"]["y"] for g in groups]
    xe = [n["meta"]["x"] + n["meta"]["width"] for n in nodes] + \
         [g["bounds"]["x"] + g["bounds"]["width"] for g in groups]
    ye = [n["meta"]["y"] + n["meta"]["height"] for n in nodes] + \
         [g["bounds"]["y"] + g["bounds"]["height"] for g in groups]
    pad = 40
    S = 0.92
    W = int((max(xe) - min(xs) + pad * 2) * S)
    H = int((max(ye) - min(ys) + pad * 2 + 90) * S)

    img = Image.new("RGB", (W, H), (14, 15, 18))
    d = ImageDraw.Draw(img)

    def P(x, y):
        return ((x - min(xs) + pad) * S, (y - min(ys) + pad + 90) * S)

    d.text((24, 22), f"燕云冲击帧 · 画布预览 {VER}", font=f(30, True), fill=(238, 235, 226))
    d.text((24, 62), f"{len(nodes)} 节点 / {len(edges)} 边 / {len(groups)} 组　组＝跑序，组内并行，组间连线即依赖", font=f(18), fill=(140, 142, 148))

    # 组
    for g in groups:
        b = g["bounds"]
        x0, y0 = P(b["x"], b["y"])
        x1, y1 = P(b["x"] + b["width"], b["y"] + b["height"])
        col = (g.get("style") or {}).get("borderColor") or "#777"
        rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, outline=rgb, width=2,
                            fill=(20, 21, 26))
        d.text((x0 + 10, y0 + 8), g["label"], font=f(19, True), fill=rgb)

    # 边
    for e in edges:
        s, t = by_id[e["sourceNodeId"]], by_id[e["targetNodeId"]]
        sx = s["meta"]["x"] + s["meta"]["width"]
        sy = s["meta"]["y"] + s["meta"]["height"] / 2
        tx = t["meta"]["x"]
        ty = t["meta"]["y"] + t["meta"]["height"] / 2
        p0, p1 = P(sx, sy), P(tx, ty)
        mx = (p0[0] + p1[0]) / 2
        d.line([p0, (mx, p0[1]), (mx, p1[1]), p1], fill=(58, 61, 68), width=2, joint="curve")
        d.polygon([(p1[0] - 7, p1[1] - 4), (p1[0], p1[1]), (p1[0] - 7, p1[1] + 4)],
                  fill=(90, 94, 102))

    # 节点
    for n in nodes:
        m = n["meta"]
        x0, y0 = P(m["x"], m["y"])
        x1, y1 = P(m["x"] + m["width"], m["y"] + m["height"])
        rgb = TYPE_COLOR.get(n["type"], (150, 150, 150))
        d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(27, 29, 35),
                            outline=rgb, width=2)
        d.rectangle([x0, y0, x0 + 5, y1], fill=rgb)
        d.text((x0 + 13, y0 + 8), TYPE_TAG.get(n["type"], n["type"]), font=f(14), fill=rgb)
        label = m["label"]
        # 折行
        line, lines = "", []
        for ch in label:
            if d.textlength(line + ch, font=f(16)) > (x1 - x0 - 24):
                lines.append(line)
                line = ch
            else:
                line += ch
        lines.append(line)
        for i, ln in enumerate(lines[:4]):
            d.text((x0 + 13, y0 + 30 + i * 21), ln, font=f(16), fill=(228, 225, 216))

    d.text((24, H - 34),
           "按组号顺序跑 01→02→03→04 　　组内并行、组间串行　　P1/P2 已预填，导入即可跑",
           font=f(17), fill=(126, 128, 134))
    img.save(OUT)
    print(OUT, img.size)


if __name__ == "__main__":
    main()


