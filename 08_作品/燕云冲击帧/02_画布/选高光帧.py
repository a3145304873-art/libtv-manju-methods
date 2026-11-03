# -*- coding: utf-8 -*-
"""选高光帧：从一条生成的武打视频里，自动找出「动作最快的一段 + 到位那一帧 + 定格帧」。

为什么需要它：
  高光帧不是靠肉眼挑的——一条 4 秒的视频里，动作可能只占 0.4 秒，而且不一定在中间。
  这个脚本用帧差找出运动峰值，再把「峰值 → 到位 → 定格」三个位置标出来，
  后面剪辑只需要照它给的时间线接：起势 → 动作 → 1 帧白 → 冲击帧。

用法：
    python 选高光帧.py --in V1.mp4 [--fps 24] [--out-dir frames] [--thr 3.0]

输出：
    · frames/高光帧.png    动作到位那一帧（原分辨率）
    · frames/定格帧.png    之后第一帧停住的画面
    · 屏幕打印 JSON 时间线（可直接喂给剪辑）
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

FFMPEG = r"C:\Users\N31738\AppData\Local\Programs\ffmpeg\bin\ffmpeg.exe"
W, H = 96, 54


def frames(path, fps):
    tmp = os.path.join(os.environ.get("TEMP", "."), "hf_probe.y")
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", path, "-an",
                    "-vf", f"fps={fps},scale={W}:{H},format=gray",
                    "-f", "rawvideo", "-y", tmp], check=True)
    a = np.fromfile(tmp, dtype=np.uint8).reshape(-1, H, W).astype(np.float32)
    os.remove(tmp)
    return a


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--fps", type=float, default=24)
    ap.add_argument("--out-dir", default="frames")
    ap.add_argument("--thr", type=float, default=3.0, help="帧差阈值，高于它算在动")
    a = ap.parse_args()

    g = frames(a.inp, a.fps)
    n = len(g)
    d = np.r_[0, np.abs(g[1:] - g[:-1]).mean(axis=(1, 2))]
    # 三帧滑动平均，抗噪
    ds = np.convolve(d, np.ones(3) / 3, mode="same")

    peak = int(np.argmax(ds))
    thr = a.thr
    lo = peak
    while lo > 0 and ds[lo - 1] > thr:
        lo -= 1
    hi = peak
    while hi < n - 1 and ds[hi + 1] > thr:
        hi += 1

    # 到位帧：动作段最后 1/6 处（力刚放完）；定格帧：之后第一段连续静止
    land = max(lo, int(hi - max(1, (hi - lo) // 6)))
    hold = None
    i = hi
    while i < n - 1:
        if ds[i] < thr * 0.5 and ds[i + 1] < thr * 0.5:
            hold = i
            break
        i += 1
    hold = hold if hold is not None else min(n - 1, hi + 2)

    os.makedirs(a.out_dir, exist_ok=True)
    for name, fr in (("高光帧", land), ("定格帧", hold)):
        t = fr / a.fps
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", f"{t:.3f}", "-i", a.inp, "-frames:v", "1", "-update", "1",
                        os.path.join(a.out_dir, f"{name}.png")], check=True)

    total = n / a.fps
    timeline = {
        "源": {"时长": round(total, 2), "帧数": n, "fps": a.fps},
        "动作段": {"起": round(lo / a.fps, 2), "止": round(hi / a.fps, 2),
                   "时长": round((hi - lo) / a.fps, 2)},
        "峰值帧": {"帧": peak, "秒": round(peak / a.fps, 2)},
        "高光帧(到位)": {"帧": land, "秒": round(land / a.fps, 2)},
        "定格帧": {"帧": hold, "秒": round(hold / a.fps, 2)},
        "建议剪辑": [
            f"0 → {lo / a.fps:.2f}s：起势（原速）",
            f"{lo / a.fps:.2f} → {land / a.fps:.2f}s：动作（可抽 1 帧加速）",
            f"{land / a.fps:.2f}s：停 1 帧（冻结）",
            "接 1 帧白 → 墨凝 12 帧 → 冲击帧定格 1.5s → 渐暗 3 帧",
        ],
    }
    print(json.dumps(timeline, ensure_ascii=False, indent=2))
    print("\n高光帧/定格帧已写入:", os.path.abspath(a.out_dir))


if __name__ == "__main__":
    main()
