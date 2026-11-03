# -*- coding: utf-8 -*-
"""量一条成片的「炸白」到底几帧——别猜，量。

用法：
    python 量白闪.py <视频.mp4> [--fps 30]

做法：ffmpeg 抽成 96×54 灰度帧 → numpy 算每帧平均亮度 →
定位全片峰值，把「亮度 ≥ 峰值×(1-阈值)」的连续帧算作炸白组。
输出：每帧亮度表（可疑段）、炸白帧数、时长(ms)、峰值亮度、是全片第几帧。

判据（配合 02_画布/README.md）：
    1 帧          = 完美，剪辑不用动
    2–3 帧        = 可接受（66–100ms），不动
    ≥4 帧（>130ms）= 看起来像淡入，在原片的过渡帧上替换成「1 帧白 + 1 帧负片」
    完全没有      = 模型跳过了炸白（从实色直接进水墨），同样在过渡帧上插 1 帧白
注意：替换/插帧都要在**原来那一段连续画面里**做，不要为此把片子切成两段。
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

FFMPEG = r"C:\Users\N31738\AppData\Local\Programs\ffmpeg\bin\ffmpeg.exe"
W, H = 96, 54


def luma_series(path, fps):
    tmp = os.path.join(tempfile.gettempdir(), "flash_probe.y")
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", path, "-an",
           "-vf", f"fps={fps},scale={W}:{H},format=gray", "-f", "rawvideo", "-y", tmp]
    subprocess.run(cmd, check=True)
    a = np.fromfile(tmp, dtype=np.uint8).reshape(-1, H, W).astype(np.float32)
    os.remove(tmp)
    return a.mean(axis=(1, 2))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) < 2:
        print(__doc__)
        return
    path = sys.argv[1]
    fps = 30
    if "--fps" in sys.argv:
        fps = float(sys.argv[sys.argv.index("--fps") + 1])

    m = luma_series(path, fps)
    n = len(m)
    peak = float(m.max())
    peak_i = int(m.argmax())
    print(f"文件: {os.path.basename(path)}")
    print(f"帧数: {n}  时长: {n / fps:.2f}s  峰值亮度: {peak:.0f} @ 第 {peak_i} 帧 ({peak_i / fps:.2f}s)")

    if peak < 120:
        print("→ 全片没有真正的亮闪（峰值 < 120）：这条根本没有炸白，需要补。")
        return

    thr = peak * 0.85
    hot = m >= thr
    # 找包含峰值的连续亮帧组
    i = peak_i
    while i > 0 and hot[i - 1]:
        i -= 1
    j = peak_i
    while j < n - 1 and hot[j + 1]:
        j += 1
    count = j - i + 1
    ms = count / fps * 1000
    print(f"炸白组: 第 {i}–{j} 帧（{i / fps:.2f}–{(j + 1) / fps:.2f}s），共 {count} 帧 ≈ {ms:.0f}ms")
    print("亮度（可疑段 ±6 帧）:")
    for k in range(max(0, i - 6), min(n, j + 7)):
        mark = " ← " if i <= k <= j else "   "
        print(f"  f{k:04d} {k / fps:5.2f}s  {m[k]:6.1f}{mark}")

    if count <= 1:
        print("→ 1 帧：完美，剪辑不用动。")
    elif count <= 3:
        print(f"→ {count} 帧（{ms:.0f}ms）：可接受，建议不动。")
    else:
        print(f"→ {count} 帧（{ms:.0f}ms）：偏长，像淡入。在原来的过渡帧上替换成「1 帧白 + 1 帧负片」，不要切段。")


if __name__ == "__main__":
    main()
