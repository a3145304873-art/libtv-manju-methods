# -*- coding: utf-8 -*-
"""墨凝：把一张水墨冲击帧变成「墨从爆点涌出、凝成人形」的 10–12 帧序列。

依据（2026-10-30 逐帧拆解《道之极》）：参考的墨爆不是"墨向外炸"，而是
白场 → 墨团 → 轮廓浮现 → 水墨人物，12 帧、每帧结构差 0.32–0.84。
关键三点：
  1. 遮罩边缘要"墨须"（极坐标噪声 → 放射状分叉），不能是圆形；
  2. 分两段：前半「墨团」（模糊 + 高对比、没有细节），后半细节浮现；
  3. 爆点由 --point 指定（默认剑尖），墨从那里长出来。

用法：
    python 墨凝.py --in 冲击帧.png --out-dir frames/ [--frames 12] [--point 0.34,0.52] [--seed 7]
输出：frames/m00.png … m11.png（直接喂 ffmpeg -framerate 30）
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter


def smoothstep(e0, e1, x):
    d = e1 - e0
    if abs(d) < 1e-6:
        d = 1e-6
    t = np.clip((x - e0) / d, 0, 1)
    return t * t * (3 - 2 * t)


def value_noise(h, w, cells, seed, wrap_x=True):
    """低分辨率随机格 + 双线性放大 → 平滑噪声（0–1）"""
    rng = np.random.default_rng(seed)
    g = rng.random((cells, cells)).astype(np.float32)
    if wrap_x:
        g[:, -1] = g[:, 0]
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) / 255.0
    a = (a - a.min()) / (np.ptp(a) + 1e-6)
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--frames", type=int, default=12)
    ap.add_argument("--point", default="0.34,0.52")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--warp", type=float, default=0.10)
    a = ap.parse_args()

    src = Image.open(a.inp).convert("RGB")
    W, H = src.size
    arr = np.asarray(src).astype(np.float32)
    px, py = [float(v) for v in a.point.split(",")]
    cx, cy = px * W, py * H

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy) / np.hypot(max(cx, W - cx), max(cy, H - cy))
    th = (np.arctan2(dy, dx) + np.pi) / (2 * np.pi)      # 0–1 环向

    # 极坐标噪声：环向 × 径向 → 放射状"墨须"
    n_coarse = value_noise(H, W, 24, a.seed)             # 大分叉
    n_fine = value_noise(H, W, 96, a.seed + 1)           # 边缘碎
    streak = (np.sin(th * np.pi * 2 * 9 + n_coarse * 6.0) * 0.5 + 0.5)
    field = r + 0.20 * (n_coarse - 0.5) + 0.09 * (n_fine - 0.5) + 0.05 * (streak - 0.5)

    # 前半段的内容：模糊 + 高对比的"墨团"，没有细节
    blur = src.filter(ImageFilter.GaussianBlur(7))
    b = np.asarray(blur).astype(np.float32)
    b = np.clip((b - 128) * 1.35 + 128, 0, 255)          # 加对比，压掉细节
    sharp = arr

    os.makedirs(a.out_dir, exist_ok=True)
    N = a.frames
    for i in range(N):
        p = (i + 1) / N
        radius = 0.10 + 1.00 * (p ** 0.95)
        mask = smoothstep(radius + 0.05, radius - 0.05, field)      # 1=已在墨里
        # 两段式：前 55% 用墨团，之后细节浮现
        q = 0.0 if p <= 0.65 else (p - 0.65) / 0.35
        content = b * (1 - q) + sharp * q
        # 早期整体压暗一点，让"墨还在涌"读得出来
        content = content * (0.72 + 0.28 * min(1.0, p / 0.6))
        # 墨还在流动：内容随帧做缓慢位移，幅度递减（否则结构差掉得太快，像"擦除"）
        amp = a.warp * (1.0 - p) ** 0.7 * min(W, H)
        wx = (n_coarse * 2 - 1) * amp
        wy = (n_fine * 2 - 1) * amp
        sy = np.clip((yy + wy).astype(np.int32), 0, H - 1)
        sx = np.clip((xx + wx).astype(np.int32), 0, W - 1)
        content = content[sy, sx]
        out = content * mask[..., None] + 255.0 * (1 - mask[..., None])
        # 收尾仍在变：极缓推近 + 渐暗（参考的定格段结构差 0.32→0.05 一直在动）
        z = 1.0 + 0.03 * (i / max(N - 1, 1))
        cw, ch = W / z, H / z
        box = ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)
        out = np.asarray(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
                         .resize((W, H), Image.LANCZOS).crop(
                             (int((W-cw)/2), int((H-ch)/2), int((W+cw)/2), int((H+ch)/2))
                         ).resize((W, H), Image.LANCZOS)).astype(np.float32)
        out *= (1.0 - 0.06 * max(0.0, (p - 0.7) / 0.3))
        Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(
            os.path.join(a.out_dir, f"m{i:02d}.png"))
    print(f"写出 {N} 帧 -> {a.out_dir}")


if __name__ == "__main__":
    main()




