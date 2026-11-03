from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import subprocess, shutil, math

VIDEO = Path(r"C:\Users\N31738\Downloads\学单词mp4.mp4")
WORK = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\04_素材\分析\学单词-字幕气泡")
FRAMES = WORK / "frames"
OUT_FRAMES = WORK / "out_frames"
OUT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\04_素材\分析\学单词-字幕气泡测试.mp4")
for d in (WORK, FRAMES, OUT_FRAMES):
    d.mkdir(parents=True, exist_ok=True)

# extract 30fps frames
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(VIDEO), "-vf", "fps=30", "-start_number", "0", str(FRAMES / "f_%04d.png"), "-y"], check=True)
frames = sorted(FRAMES.glob("f_*.png"))
print("frames", len(frames))
W, H = Image.open(frames[0]).size
print("size", W, H)

FONT_TEXT = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_BUB = r"C:\Windows\Fonts\STKAITI.TTF"
CREAM = (255, 248, 236)
BROWN = (122, 90, 68)
INK = (58, 44, 36)
WHITE = (255, 255, 255)


def text_font(sz):
    return ImageFont.truetype(FONT_TEXT, sz)


def bub_font(sz):
    return ImageFont.truetype(FONT_BUB, sz)


def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if draw.textlength(test, font=font) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def draw_subtitle(im, text, alpha=1.0):
    if not text:
        return im
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = text_font(27)
    lines = wrap(d, text, f, W - 90)
    lines = lines[:2]
    line_h = 34
    total = len(lines) * line_h
    y = H - 26 - total
    for line in lines:
        tw = d.textlength(line, font=f)
        x = (W - tw) / 2
        d.text((x, y), line, font=f, fill=WHITE, stroke_width=3, stroke_fill=(35, 25, 20))
        y += line_h
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    im = im.convert("RGBA")
    im.alpha_composite(layer)
    return im.convert("RGB")


def draw_bubble(im, lines, alpha=1.0, scale=1.0):
    bw, bh = 300, 120
    layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # shadow
    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((18, 20, bw - 10, bh - 10), fill=(0, 0, 0, 45))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    layer.alpha_composite(sh)
    # cloud / wavy bubble
    cx, cy = bw // 2, bh // 2 - 4
    rx, ry = bw // 2 - 10, bh // 2 - 12
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        rr = 1 + 0.035 * math.sin(9 * a + 0.7)
        pts.append((cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)))
    d.polygon(pts, fill=CREAM)
    d.line(pts + [pts[0]], fill=BROWN, width=3, joint="curve")
    # tail right (bubble sits left of 心易)
    ty = bh - 38
    d.polygon([(bw - 26, ty - 12), (bw + 10, ty + 6), (bw - 26, ty + 18)], fill=CREAM, outline=BROWN)
    d.line([(bw - 25, ty - 12), (bw - 25, ty + 18)], fill=CREAM, width=5)
    # tiny leaf
    d.ellipse((bw - 50, 8, bw - 32, 24), fill=(143, 174, 123), outline=(90, 120, 70))
    # text
    f = bub_font(22)
    line_h = 28
    total = len(lines) * line_h
    y = (bh - 18 - total) // 2 + 3
    for line in lines:
        tw = d.textlength(line, font=f)
        x = (bw - 18 - tw) / 2
        d.text((x, y), line, font=f, fill=INK)
        y += line_h
    if scale != 1.0:
        nw, nh = int(bw * scale), int(bh * scale)
        layer = layer.resize((nw, nh), Image.LANCZOS)
        bw, bh = nw, nh
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    x = 18
    y = 18
    im = im.convert("RGBA")
    im.alpha_composite(layer, (x, y))
    return im.convert("RGB")


# time-based overlays
BUBBLES = [
    (0.05, 0.65, ["like 是“像”"]),
    (0.70, 1.28, ["一个词加 like，", "就是“像它一样”"]),
    (1.33, 1.95, ["rocklike?"]),
    (6.00, 6.75, ["snakelike?"]),
    (10.00, 10.78, ["doglike?"]),
]
SUBS = [
    (1.80, 2.80, "Rock 是石头"),
    (2.80, 4.10, "Rocklike 就是像石头一样，坚固的！"),
    (5.00, 6.00, "真不错！"),
    (6.60, 7.60, "Snake 是蛇"),
    (7.60, 9.20, "Snakelike 就是像蛇一样，蜿蜒的！"),
    (9.20, 10.00, "真棒！"),
    (10.80, 11.80, "Dog 是狗"),
    (11.80, 13.60, "Doglike 就是像狗一样，忠诚的！"),
    (13.60, 14.60, "你记住了多少？"),
]


def bubble_at(t):
    for start, end, lines in BUBBLES:
        if start <= t <= end:
            age = t - start
            remain = end - t
            alpha = 1.0
            scale = 1.0
            if age < 0.16:
                u = age / 0.16
                alpha = u
                scale = 0.86 + 0.14 * u + 0.03 * math.sin(u * math.pi)
            if remain < 0.12:
                u = remain / 0.12
                alpha = min(alpha, u)
                scale = 1.0 + 0.05 * (1 - u)
            return lines, alpha, scale
    return None, 0, 1


def sub_at(t):
    for start, end, text in SUBS:
        if start <= t <= end:
            return text
    return None


for i, fpath in enumerate(frames):
    t = i / 30.0
    im = Image.open(fpath).convert("RGB")
    lines, alpha, scale = bubble_at(t)
    if lines:
        im = draw_bubble(im, lines, alpha, scale)
    text = sub_at(t)
    if text:
        im = draw_subtitle(im, text)
    im.save(OUT_FRAMES / f"f_{i:04d}.png")

print("composited", len(frames))
subprocess.run([
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-framerate", "30", "-i", str(OUT_FRAMES / "f_%04d.png"),
    "-i", str(VIDEO),
    "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
    "-c:a", "copy", "-shortest", "-y", str(OUT)
], check=True)
print("out", OUT, OUT.stat().st_size)






