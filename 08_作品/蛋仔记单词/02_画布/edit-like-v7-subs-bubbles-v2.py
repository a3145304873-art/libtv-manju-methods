# -*- coding: utf-8 -*-
"""v2: strict audio-timed bubbles, larger high-contrast text, 1280x720."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
MEDIA = Path(r"E:\libtv漫剧\08_作品\_共享工具\pulls\canvas-d88dd727ec\media")
OUTDIR = ROOT / "03_成片"
TMP = Path(r"C:\Users\N31738\AppData\Local\Temp\like_v7_edit_v2")
OUTDIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
W, H = 1280, 720
FONT = r"C:\Windows\Fonts\msyhbd.ttc"

vids = sorted(MEDIA.glob("*.mp4"))
assert len(vids) == 3
V1, V2, V3 = vids

# Timings from Whisper segments (actual audio), not the original plan.
BUBBLES = [
    ("like 是“像”", 0.00, 0.80, ["like 是“像”"]),
    ("加 like = 像它", 1.45, 2.10, ["加 like = 像它"]),
    ("rocklike？", 2.10, 2.86, ["rocklike？"]),
    ("真不错！", 7.10, 7.85, ["真不错！"]),
    ("snakelike？", 10.05, 10.58, ["snakelike？"]),
    ("真棒！", 14.12, 14.62, ["真棒！"]),
    ("doglike？", 16.05, 16.58, ["doglike？"]),
    ("真棒！", 20.95, 21.50, ["真棒！"]),
]

def bubble_png(lines, path):
    font = ImageFont.truetype(FONT, 36)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    tw = max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines)
    lh = 44
    bw = max(240, tw + 70)
    bh = lh * len(lines) + 38
    x, y = 24, 20
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x + 5, y + 7, x + bw + 5, y + bh + 7), radius=24, fill=(0, 0, 0, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    tmp.alpha_composite(sh)
    d = ImageDraw.Draw(tmp)
    d.rounded_rectangle((x, y, x + bw, y + bh), radius=24, fill=(255, 252, 246, 252),
                        outline=(95, 65, 48, 255), width=4)
    tx = x + int(bw * 0.55)
    tail = [(tx, y + bh - 3), (tx + 16, y + bh + 38), (tx + 38, y + bh - 3)]
    d.polygon(tail, fill=(255, 252, 246, 252))
    d.line(tail + [tail[0]], fill=(95, 65, 48, 255), width=4, joint="curve")
    d.line([(tx + 3, y + bh - 3), (tx + 35, y + bh - 3)], fill=(255, 252, 246, 255), width=7)
    ty = y + 15
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=font)
        lw = bb[2] - bb[0]
        d.text((x + (bw - lw) // 2, ty), ln, font=font, fill=(42, 32, 26, 255))
        ty += lh
    tmp.save(path)

bubble_paths = []
for i, (_, _, _, lines) in enumerate(BUBBLES):
    p = TMP / f"bubble_{i}.png"
    bubble_png(lines, p)
    bubble_paths.append(p)

# ASS 1280x720, 36px bold white with thick dark outline; two lines max.
ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft YaHei,40,&H00FFFFFF,&H000000FF,&H002A1E16,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,28,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:02.90,0:00:07.10,Sub,,0,0,0,,{\\fad(80,80)}rock 是石头——\\Nrocklike 就是像石头一样，坚固的！
Dialogue: 0,0:00:10.58,0:00:14.10,Sub,,0,0,0,,{\\fad(80,80)}snake 是蛇——\\Nsnakelike 就是像蛇一样，蜿蜒的！
Dialogue: 0,0:00:16.66,0:00:20.95,Sub,,0,0,0,,{\\fad(80,80)}dog 是狗——\\Ndoglike 就是像狗一样，忠诚的！
Dialogue: 0,0:00:21.60,0:00:22.80,Sub,,0,0,0,,{\\fad(80,80)}你记住了多少？
"""
ass_path = TMP / "subs.ass"
ass_path.write_text(ASS, encoding="utf-8-sig")

inputs = ["-i", str(V1), "-i", str(V2), "-i", str(V3)]
for p in bubble_paths:
    inputs += ["-i", str(p)]

fc = ["[0:v]scale=1280:720,setsar=1[v0]",
      "[1:v]scale=1280:720,setsar=1[v1]",
      "[2:v]scale=1280:720,setsar=1[v2]",
      "[v0][v1][v2]concat=n=3:v=1:a=0[vbase]",
      "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]"]
prev = "vbase"
for i, (_, start, end, _) in enumerate(BUBBLES):
    inp = i + 3
    out = f"o{i}"
    fc.append(f"[{prev}][{inp}:v]overlay=0:0:enable='gte(t,{start})*lt(t,{end})'[{out}]")
    prev = out
fc.append(f"[{prev}]ass=subs.ass[vout]")

cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", *inputs,
       "-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "[a]",
       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-r", "24", "-y",
       str(OUTDIR / "蛋仔记单词-like-23s-v7-字幕气泡-v3.mp4")]
print("rendering", OUTDIR / "蛋仔记单词-like-23s-v7-字幕气泡-v3.mp4")
subprocess.run(cmd, check=True, cwd=str(TMP))
print("done")

