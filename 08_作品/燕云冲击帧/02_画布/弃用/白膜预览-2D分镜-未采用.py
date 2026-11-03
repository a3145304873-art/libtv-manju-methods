# -*- coding: utf-8 -*-
"""白膜动作预览：用程序画一个白人偶，把四套"蓄—爆—收"的动作与节奏渲成 mp4。

为什么用程序画：
  AI 生成的白膜不一定听话（它可能又给你一个站着不动的人偶）。
  先用程序把"关节怎么走、什么时候快"定死，得到一段可播放的动作样片——
  它既能当审片用，也能直接当 reference_video 喂给模型。

输出：03_成片/白膜预览/B1..B4.mp4（960×540 / 24fps / 4s）
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FF = r"C:\Users\N31738\AppData\Local\Programs\ffmpeg\bin\ffmpeg.exe"
W, H, FPS, DUR = 960, 540, 24, 4.0
BG = (168, 168, 168)
BODY = (245, 245, 245)
EDGE = (60, 60, 60)
SWORD = (70, 70, 70)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03_成片", "白膜预览")


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    return t * t * (3 - 2 * t)


def pose_at(keys, t):
    """keys: [(time, pose_dict)]，pose_dict 里是角度（度）。按时间插值。"""
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(len(keys) - 1):
        t0, p0 = keys[i]
        t1, p1 = keys[i + 1]
        if t <= t1:
            u = ease((t - t0) / max(t1 - t0, 1e-6))
            return {k: lerp(p0.get(k, 0), p1.get(k, 0), u) for k in set(p0) | set(p1)}
    return keys[-1][1]


def draw_figure(d, p):
    cx, cy = W / 2, H * 0.62          # 髋部
    lean = p["lean"]                   # 躯干前倾
    # 躯干
    neck = (cx + math.sin(math.radians(lean)) * 150, cy - math.cos(math.radians(lean)) * 150)
    d.line([cx, cy, neck[0], neck[1]], fill=BODY, width=26)
    # 头
    hr = 30
    hx = neck[0] + math.sin(math.radians(lean + p["head"])) * (hr + 6)
    hy = neck[1] - math.cos(math.radians(lean + p["head"])) * (hr + 6)
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=BODY, outline=EDGE, width=3)
    # 腿（基本固定）
    for sgn in (-1, 1):
        hip = (cx + sgn * 18, cy)
        knee = (cx + sgn * 26, cy + 95)
        foot = (cx + sgn * 34, cy + 190)
        d.line([hip, knee], fill=BODY, width=22)
        d.line([knee, foot], fill=BODY, width=18)
    # 手臂：从肩出发，两段
    for side, sgn in (("r", 1), ("l", -1)):
        sh = (neck[0] + sgn * 30, neck[1] + 26)
        a1 = p["a_" + side]
        e = (sh[0] + math.sin(math.radians(a1)) * 80, sh[1] + math.cos(math.radians(a1)) * 80)
        a2 = a1 + p["f_" + side]
        w = (e[0] + math.sin(math.radians(a2)) * 72, e[1] + math.cos(math.radians(a2)) * 72)
        d.line([sh, e], fill=BODY, width=20)
        d.line([e, w], fill=BODY, width=17)
        if side == "r":
            # 剑：从手腕沿前臂延长方向
            a3 = a2 + p.get("sword", 0)
            tip = (w[0] + math.sin(math.radians(a3)) * 150, w[1] + math.cos(math.radians(a3)) * 150)
            d.line([w, tip], fill=SWORD, width=6)
            d.ellipse([w[0] - 8, w[1] - 8, w[0] + 8, w[1] + 8], fill=EDGE)


# 角度约定：a_/f_ 是从"手臂垂下"起算的度数，正值向前/向上摆
ACTS = {}

# B1 抬臂 → 前挥 → 翻腕划弧
ACTS["B1"] = [
    (0.0, dict(lean=4, head=0, a_r=10, f_r=8, a_l=6, f_l=6, sword=0)),
    (1.2, dict(lean=2, head=-3, a_r=95, f_r=55, a_l=8, f_l=8, sword=-20)),
    (1.6, dict(lean=18, head=4, a_r=110, f_r=4, a_l=20, f_l=10, sword=0)),
    (2.6, dict(lean=12, head=8, a_r=48, f_r=-38, a_l=35, f_l=15, sword=-55)),
    (4.0, dict(lean=10, head=8, a_r=44, f_r=-40, a_l=33, f_l=15, sword=-58)),
]
# B2 双臂前伸 → 逐段回收 → 转头收势
ACTS["B2"] = [
    (0.0, dict(lean=-4, head=0, a_r=-10, f_r=10, a_l=-12, f_l=12, sword=0)),
    (1.0, dict(lean=-8, head=-6, a_r=30, f_r=40, a_l=30, f_l=35, sword=10)),
    (1.4, dict(lean=22, head=2, a_r=105, f_r=2, a_l=100, f_l=4, sword=0)),
    (2.6, dict(lean=16, head=2, a_r=70, f_r=45, a_l=66, f_l=48, sword=0)),
    (4.0, dict(lean=14, head=18, a_r=62, f_r=50, a_l=60, f_l=52, sword=0)),
]
# B3 横扫 → 向身后收
ACTS["B3"] = [
    (0.0, dict(lean=6, head=-8, a_r=40, f_r=60, a_l=10, f_l=10, sword=-70)),
    (1.2, dict(lean=2, head=-10, a_r=25, f_r=75, a_l=6, f_l=10, sword=-95)),
    (1.6, dict(lean=16, head=6, a_r=95, f_r=-10, a_l=20, f_l=15, sword=-10)),
    (2.8, dict(lean=8, head=4, a_r=44, f_r=-48, a_l=30, f_l=15, sword=-40)),
    (4.0, dict(lean=6, head=4, a_r=40, f_r=-50, a_l=28, f_l=15, sword=-42)),
]
# B4 腰后抽出 → 递出 → 翻腕下压
ACTS["B4"] = [
    (0.0, dict(lean=0, head=-6, a_r=38, f_r=95, a_l=8, f_l=8, sword=40)),
    (1.0, dict(lean=6, head=-2, a_r=60, f_r=30, a_l=10, f_l=8, sword=10)),
    (1.5, dict(lean=18, head=4, a_r=112, f_r=2, a_l=25, f_l=12, sword=0)),
    (2.6, dict(lean=14, head=6, a_r=70, f_r=-30, a_l=30, f_l=14, sword=-45)),
    (4.0, dict(lean=12, head=6, a_r=66, f_r=-32, a_l=28, f_l=14, sword=-48)),
]


def render(name, keys):
    d = os.path.join(os.environ.get("TEMP", "."), "bm_" + name)
    os.makedirs(d, exist_ok=True)
    n = int(FPS * DUR)
    for i in range(n):
        t = i / FPS
        p = pose_at(keys, t)
        im = Image.new("RGB", (W, H), BG)
        dr = ImageDraw.Draw(im)
        # 地面线
        dr.line([0, H * 0.92, W, H * 0.92], fill=(120, 120, 120), width=2)
        # 极轻的推近
        zoom = 1.0 + 0.03 * (t / DUR)
        draw_figure(dr, p)
        if zoom > 1.001:
            im = im.resize((int(W * zoom), int(H * zoom)), Image.LANCZOS)
            x = (im.width - W) // 2
            y = (im.height - H) // 2
            im = im.crop((x, y, x + W, y + H))
        # 秒数
        dr2 = ImageDraw.Draw(im)
        dr2.text((16, 12), "%s  %.1fs" % (name, t), fill=(70, 70, 70))
        im.save(os.path.join(d, "f%03d.png" % i))
    os.makedirs(OUT, exist_ok=True)
    mp4 = os.path.join(OUT, name + ".mp4")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(FPS),
                    "-i", os.path.join(d, "f%03d.png"), "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", mp4], check=True)
    print("写出:", mp4)


if __name__ == "__main__":
    for k, v in ACTS.items():
        render(k, v)
