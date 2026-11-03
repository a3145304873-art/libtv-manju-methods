# -*- coding: utf-8 -*-
"""Post-edit the 23s -like v7: Chinese subtitles for 黄蛋 + word bubbles for 心易."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(r"E:\libtv漫剧\08_作品\蛋仔记单词")
MEDIA = Path(r"E:\libtv漫剧\08_作品\_共享工具\pulls\canvas-d88dd727ec\media")
OUTDIR = ROOT / "03_成片"
TMP = Path(r"C:\Users\N31738\AppData\Local\Temp\like_v7_edit")
OUTDIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
W, H = 864, 496
FONT = r"C:\Windows\Fonts\msyhbd.ttc"

vids = sorted(MEDIA.glob("*.mp4"))
assert len(vids) == 3, vids
V1, V2, V3 = vids

# bubbles: text, start, end, two-line?
BUBBLES = [
    ("like 是“像”", 0.15, 1.20, ["like 是“像”"]),
    ("一个词加 like", 1.20, 3.40, ["一个词加 like，", "就是“像它一样”"]),
    ("rocklike 是什么？", 3.40, 5.00, ["rocklike 是什么？"]),
    ("真不错！", 8.40, 9.30, ["真不错！"]),
    ("snakelike 是什么？", 10.15, 10.70, ["snakelike 是什么？"]),
    ("真棒！", 13.68, 14.50, ["真棒！"]),
    ("doglike 是什么？", 16.20, 16.70, ["doglike 是什么？"]),
    ("真棒！", 19.76, 20.60, ["真棒！"]),
]

def bubble_png(lines, path):
    font = ImageFont.truetype(FONT, 22)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    # measure
    tw = max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines)
    lh = 28
    bw = max(150, tw + 44)
    bh = lh * len(lines) + 24
    x, y = 16, 14
    # shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x + 4, y + 5, x + bw + 4, y + bh + 5), radius=18, fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    tmp.alpha_composite(sh)
    # bubble
    d = ImageDraw.Draw(tmp)
    d.rounded_rectangle((x, y, x + bw, y + bh), radius=18, fill=(255, 250, 240, 245),
                        outline=(120, 86, 62, 255), width=3)
    # tail
    tx = x + int(bw * 0.55)
    tail = [(tx, y + bh - 2), (tx + 12, y + bh + 26), (tx + 30, y + bh - 2)]
    d.polygon(tail, fill=(255, 250, 240, 245))
    d.line(tail + [tail[0]], fill=(120, 86, 62, 255), width=3, joint="curve")
    d.line([(tx + 2, y + bh - 2), (tx + 28, y + bh - 2)], fill=(255, 250, 240, 255), width=5)
    # text
    ty = y + 12
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=font)
        lw = bb[2] - bb[0]
        d.text((x + (bw - lw) // 2, ty), ln, font=font, fill=(55, 42, 34, 255))
        ty += lh
    tmp.save(path)

bubble_paths = []
for i, (_, _, _, lines) in enumerate(BUBBLES):
    p = TMP / f"bubble_{i}.png"
    bubble_png(lines, p)
    bubble_paths.append(p)

# subtitles ASS
ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 864
PlayResY: 496
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft YaHei,24,&H00FFFFFF,&H000000FF,&H003A2D24,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,28,28,22,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:05.00,0:00:08.40,Sub,,0,0,0,,{\\fad(80,80)}rock 是石头——\\Nrocklike 就是像石头一样，坚固的！
Dialogue: 0,0:00:10.60,0:00:13.60,Sub,,0,0,0,,{\\fad(80,80)}snake 是蛇——\\Nsnakelike 就是像蛇一样，蜿蜒的！
Dialogue: 0,0:00:16.60,0:00:19.60,Sub,,0,0,0,,{\\fad(80,80)}dog 是狗——\\Ndoglike 就是像狗一样，忠诚的！
Dialogue: 0,0:00:20.50,0:00:21.60,Sub,,0,0,0,,{\\fad(80,80)}你记住了多少？
"""
ass_path = TMP / "subs.ass"
ass_path.write_text(ASS, encoding="utf-8-sig")

# ffmpeg: concat + overlays + subtitles
inputs = ["-i", str(V1), "-i", str(V2), "-i", str(V3)]
for p in bubble_paths:
    inputs += ["-i", str(p)]

fc = ["[0:v][1:v][2:v]concat=n=3:v=1:a=0[vbase]",
      "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]"]
prev = "vbase"
for i, (_, start, end, _) in enumerate(BUBBLES):
    inp = i + 3
    out = f"v{i}"
    fc.append(f"[{prev}][{inp}:v]overlay=0:0:enable='gte(t,{start})*lt(t,{end})'[{out}]")
    prev = out
fc.append(f"[{prev}]ass=subs.ass[vout]")

cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", *inputs,
       "-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "[a]",
       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-r", "24", "-y", str(OUTDIR / "蛋仔记单词-like-23s-v7-字幕气泡.mp4")]
print("running", cmd[:6], "...")
subprocess.run(cmd, check=True, cwd=str(TMP))
print("done", OUTDIR / "蛋仔记单词-like-23s-v7-字幕气泡.mp4")
