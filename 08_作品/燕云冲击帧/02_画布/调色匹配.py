# -*- coding: utf-8 -*-
"""调色匹配：把一张图的明暗分布对齐到参考帧，红/暖色单独保留。

用途：生成的冲击帧"不够高级"时，先别重画——把它的直方图匹配到参考帧，
通常就够用了。匹配只动亮度分布与红通道，不改构图。

用法：
    python 调色匹配.py --ref <参考图> --in <待调图> --out <输出.png> [--red 0.18]
示例：
    python 调色匹配.py --ref ..\\01_资产\\参考-冲击帧3-水墨定格-用户提供.png ^
                        --in  ..\\01_资产\\生成-I1-冲击帧.png ^
                        --out ..\\03_成片\\I1-匹配后.png

判据（和参考帧比）：墨(<16%)、纸(>86%)、平均亮度 三项应接近；有色占比可略高。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def load(p, size):
    return np.asarray(Image.open(p).convert("RGB").resize(size, Image.LANCZOS)).astype(np.float32)


def lum(a):
    return a @ LUMA


def stats(a):
    l = lum(a) / 255.0
    mx, mn = a.max(axis=2) / 255.0, a.min(axis=2) / 255.0
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return dict(ink=(l < 0.16).mean() * 100, mid=((l >= 0.16) & (l <= 0.86)).mean() * 100,
                paper=(l > 0.86).mean() * 100, colored=(sat > 0.25).mean() * 100,
                sat=sat.mean() * 100, mean=l.mean() * 100)


def match(src, ref, red_gain=0.18):
    s_l, r_l = lum(src), lum(ref)
    qs = np.linspace(0, 100, 257)
    s_q, r_q = np.percentile(s_l, qs), np.percentile(r_l, qs)
    new_l = np.interp(s_l, s_q, r_q)
    out = src * (new_l / np.maximum(s_l, 1.0))[..., None]
    mx, mn = out.max(axis=2), out.min(axis=2)
    red_mask = ((out[..., 0] > out[..., 1] * 1.12) & (mx - mn > 12)).astype(np.float32)
    out[..., 0] = np.clip(out[..., 0] * (1 + red_gain * red_mask), 0, 255)
    return np.clip(out, 0, 255)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", type=float, default=0.18)
    a = ap.parse_args()

    ref_img = Image.open(a.ref).convert("RGB")
    size = ref_img.size if ref_img.width >= 640 else (1280, 720)
    src = load(a.inp, size)
    ref = load(a.ref, size)
    out = match(src, ref, a.red)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    Image.fromarray(out.astype(np.uint8)).save(a.out)

    for name, arr in (("参考", ref), ("原图", src), ("匹配后", out)):
        s = stats(arr)
        print(f"{name:4s} 墨<16%={s['ink']:5.1f}  中间调={s['mid']:5.1f}  纸>86%={s['paper']:5.1f}  "
              f"有色={s['colored']:5.1f}%  平均饱和={s['sat']:5.1f}  平均亮度={s['mean']:5.1f}")
    print("写出:", a.out)


if __name__ == "__main__":
    main()
