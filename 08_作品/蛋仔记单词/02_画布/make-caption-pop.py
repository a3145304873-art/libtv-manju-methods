from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math

root = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
capy = Image.open(root / "01_资产" / "角色" / "心易-水豚-标准.png").convert("RGB")
W, H = 1280, 720
FONT = r"C:\Windows\Fonts\msyhbd.ttc"


def font(sz):
    return ImageFont.truetype(FONT, sz)


def base():
    im = Image.new("RGB", (W, H), (238, 224, 204))
    dr = ImageDraw.Draw(im)
    for y in range(H):
        c = (244 - int(10 * y / H), 231 - int(14 * y / H), 211 - int(16 * y / H))
        dr.line((0, y, W, y), fill=c)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse((60, 80, 560, 660), fill=(255, 248, 236, 160))
    ov = ov.filter(ImageFilter.GaussianBlur(40))
    im.paste(ov, (0, 0), ov)
    card = Image.new("RGBA", (460, 600), (255, 255, 255, 235))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, 459, 599), radius=40, fill=(255, 255, 255, 235))
    c2 = capy.copy()
    c2.thumbnail((400, 560))
    card.paste(c2, ((460 - c2.width) // 2, (600 - c2.height) // 2))
    mask = Image.new("L", (460, 600), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 459, 599), radius=40, fill=255)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((115, 95, 575, 695), radius=40, fill=(0, 0, 0, 55))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    im.paste(shadow, (0, 0), shadow)
    im.paste(card, (115, 70), mask)
    return im


def caption_layer(text="like", sub="是“像”"):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    x0, y0 = 820, 140
    sd.text((x0, y0), text, font=font(88), fill=(0, 0, 0, 200))
    yy = y0 + 118
    for ch in sub:
        sd.text((x0 + 10, yy), ch, font=font(70), fill=(0, 0, 0, 200))
        yy += 72
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    layer.alpha_composite(sh)
    d = ImageDraw.Draw(layer)
    d.text((x0, y0), text, font=font(88), fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(70, 45, 35, 230))
    yy = y0 + 118
    for ch in sub:
        d.text((x0 + 10, yy), ch, font=font(70), fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(70, 45, 35, 230))
        yy += 72
    return layer


def render_frame(t):
    im = base()
    if t < 0.4 or t > 2.45:
        return im
    if t < 0.7:
        u = (t - 0.4) / 0.3
        s = 0.82 + 0.22 * u + 0.03 * math.sin(u * math.pi)
        a = min(1, u * 1.6)
        yoff = int(16 * (1 - u))
    elif t < 2.2:
        s, a, yoff = 1.0, 1.0, 0
    else:
        u = (t - 2.2) / 0.25
        s, a, yoff = 1.0 + 0.08 * u, max(0, 1 - u * 1.2), 0
    layer = caption_layer()
    cx, cy = 960, 330
    nw, nh = int(W * s), int(H * s)
    lay = layer.resize((nw, nh), Image.LANCZOS)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.alpha_composite(lay, (int(cx - cx * s), int(cy - cy * s + yoff)))
    if a < 1:
        alpha = tmp.getchannel("A").point(lambda v: int(v * a))
        tmp.putalpha(alpha)
    im = im.convert("RGBA")
    im.alpha_composite(tmp)
    return im.convert("RGB")


outdir = Path(r"C:\Users\N31738\AppData\Local\Temp\caption_pop")
outdir.mkdir(parents=True, exist_ok=True)
fps = 30
dur = 3.0
for i in range(int(fps * dur)):
    render_frame(i / fps).save(outdir / f"f_{i:03d}.png")
print("frames", len(list(outdir.glob("f_*.png"))))
sel = [int(x * fps) for x in (0.4, 0.55, 0.7, 1.2, 2.2, 2.35)]
thumbs = []
for i in sel:
    im = Image.open(outdir / f"f_{i:03d}.png")
    im.thumbnail((426, 240))
    thumbs.append((f"{i/fps:.2f}s", im))
sheet = Image.new("RGB", (426 * 3, (240 + 22) * 2), "white")
dr = ImageDraw.Draw(sheet)
for k, (lab, im) in enumerate(thumbs):
    r, c = divmod(k, 3)
    sheet.paste(im, (c * 426, r * (240 + 22)))
    dr.text((c * 426 + 4, r * (240 + 22) + 242), lab, fill="black")
sheet.save(outdir / "contact.jpg", quality=92)
print(outdir / "contact.jpg")


