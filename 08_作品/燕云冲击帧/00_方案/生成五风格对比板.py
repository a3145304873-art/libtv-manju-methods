# -*- coding: utf-8 -*-
"""五种冲击帧风格对比板：色板 / 明暗比例 / 笔触语言 / 真实参考锚。

说明：A、C 两格用真实参考片抽帧（道之极墨爆、拔剑水墨定格）当锚；
B、D、E 三格是**构图与配色示意**（程序绘制），不是成图，别当效果看。
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)                      # 08_作品/燕云冲击帧
REF = os.path.join(WORK, "04_素材")
OUT = os.path.join(HERE, "五风格对比板.png")
FONT = "C:/Windows/Fonts/"


def f(size, bold=False):
    return ImageFont.truetype(FONT + ("msyhbd.ttc" if bold else "msyh.ttc"), size)


def vgrad(w, h, stops):
    ys = np.arange(h) / max(h - 1, 1)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    out = np.zeros((h, 3))
    for c in range(3):
        out[:, c] = np.interp(ys, pos, cols[:, c])
    return Image.fromarray(np.repeat(out[:, None, :], w, axis=1).astype(np.uint8), "RGB")


TW, TH = 430, 242


def crop_ref(name, box=None):
    p = os.path.join(REF, name)
    im = Image.open(p).convert("RGB")
    if box:
        im = im.crop(box)
    w, h = im.size
    s = max(TW / w, TH / h)
    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    x = (im.width - TW) // 2
    y = (im.height - TH) // 2
    return im.crop((x, y, x + TW, y + TH))


def swatch_a():
    return crop_ref("关键帧-冲击帧2-墨爆-2.40s.png", (240, 60, 1500, 780))


def swatch_c():
    return crop_ref("关键帧-冲击帧3-水墨定格-3.00s.png", (200, 40, 1500, 800))


def swatch_b():
    """焦墨拓印示意：黑 85%，白刻线，一点红"""
    im = Image.new("RGB", (TW, TH), (9, 9, 9))
    d = ImageDraw.Draw(im)
    cx, cy = TW * 0.28, TH * 0.55
    for i in range(26):
        a = -0.9 + i * 0.07
        r = 90 + i * 4
        d.line([(cx, cy), (cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r)],
               fill=(240, 238, 230), width=1)
    # 人物黑块 + 白刻痕剑
    d.polygon([(TW * 0.62, TH * 0.15), (TW * 0.80, TH * 0.18), (TW * 0.86, TH * 0.9),
               (TW * 0.58, TH * 0.92)], fill=(4, 4, 4))
    d.line([(TW * 0.5, TH * 0.62), (TW * 0.9, TH * 0.42)], fill=(245, 243, 235), width=5)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(179, 20, 26))
    return im


def swatch_d():
    """红黑 2D 示意：纯黑底 + 猩红爆点 + 白色速度线 + 能量漩涡"""
    im = Image.new("RGB", (TW, TH), (5, 5, 6))
    glow = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = TW * 0.24, TH * 0.55
    for r in range(60, 8, -8):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(224, 20, 28, int(200 * (1 - r / 70))))
    for i in range(46):
        a = random.uniform(0, math.tau)
        r0 = random.uniform(40, 70)
        r1 = random.uniform(160, 340)
        gd.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                 (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
                fill=(255, 255, 255, random.randint(30, 110)), width=random.randint(1, 2))
    im = Image.alpha_composite(im.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(1.2)))
    d = ImageDraw.Draw(im)
    d.polygon([(TW * 0.66, TH * 0.1), (TW * 0.84, TH * 0.14), (TW * 0.9, TH * 0.94),
               (TW * 0.62, TH * 0.96)], fill=(3, 3, 4))
    d.line([(TW * 0.3, TH * 0.62), (TW * 0.92, TH * 0.36)], fill=(255, 255, 255), width=6)
    return im.convert("RGB")


def swatch_e():
    """冰青金示意：纸白 + 墨笔 + 冰棱 + 一点曜金"""
    im = vgrad(TW, TH, [(0, (232, 228, 216)), (1, (206, 203, 192))]).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.polygon([(TW * 0.58, TH * 0.12), (TW * 0.78, TH * 0.16), (TW * 0.86, TH * 0.95),
               (TW * 0.54, TH * 0.97)], fill=(22, 24, 26, 255))
    d.line([(TW * 0.3, TH * 0.64), (TW * 0.9, TH * 0.4)], fill=(90, 96, 100, 220), width=5)
    cx, cy = TW * 0.28, TH * 0.6
    for i in range(16):
        a = random.uniform(0, math.tau)
        r = random.uniform(20, 90)
        pts = [(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8),
               (cx + math.cos(a + 0.12) * r * 0.7, cy + math.sin(a + 0.12) * r * 0.7)]
        d.polygon(pts, fill=(159, 224, 234, random.randint(70, 170)))
    d.ellipse([TW * 0.885, TH * 0.395, TW * 0.905, TH * 0.415], fill=(232, 196, 138, 255))
    return im.convert("RGB")


STYLES = [
    dict(code="A", name="水墨红黑", tag="道之极那一挂：纸上墨爆 + 猩红",
         thumb=swatch_a, real=True,
         pal=[("纸 #E8E4D8", (232, 228, 216)), ("焦墨 #14140F", (20, 20, 15)),
              ("猩红 #C4161C", (196, 22, 28))],
         ratio=[(0.55, (30, 30, 26)), (0.30, (232, 228, 216)), (0.15, (196, 22, 28))],
         spec=["笔触：泼墨、破笔、飞白、溅点，纸纹可见",
               "速度感：用一道墨浪代替速度线",
               "红：只在剑尖爆点 + 飞白尾迹，约 15%"]),
    dict(code="B", name="焦墨拓印", tag="最狠最冷：黑压到 85%，白是刀刻",
         thumb=swatch_b, real=False,
         pal=[("黑 #0B0B0B", (11, 11, 11)), ("刻线白 #F2F0E8", (242, 240, 232)),
              ("印记红 #B3141A", (179, 20, 26))],
         ratio=[(0.85, (11, 11, 11)), (0.12, (242, 240, 232)), (0.03, (179, 20, 26))],
         spec=["笔触：木刻/碑拓，刀口毛边，零晕染",
               "速度感：白色刻线放射，硬边切割",
               "红：只有一枚印记大小，约 3%"]),
    dict(code="C", name="素墨（无彩）", tag="最克制：只有墨的浓淡，赌的是气",
         thumb=swatch_c, real=True,
         pal=[("焦墨 #1A1A16", (26, 26, 22)), ("淡墨 #6B6B60", (107, 107, 96)),
              ("纸白 #EDE9DC", (237, 233, 220))],
         ratio=[(0.34, (26, 26, 22)), (0.66, (237, 233, 220)), (0.0, (107, 107, 96))],
         spec=["笔触：淡墨晕染 + 焦墨提神，文人水墨",
               "速度感：淡墨一圈圈扩散当冲击波",
               "红：完全没有；最多瞳孔一点纸白"]),
    dict(code="D", name="红黑 2D", tag="最燃也最不像燕云：二次元硬边",
         thumb=swatch_d, real=False,
         pal=[("纯黑 #050506", (5, 5, 6)), ("猩红 #E0141C", (224, 20, 28)),
              ("纯白 #FFFFFF", (255, 255, 255)), ("明黄 #F2C230", (242, 194, 48))],
         ratio=[(0.62, (5, 5, 6)), (0.10, (255, 255, 255)), (0.28, (224, 20, 28))],
         spec=["笔触：赛璐璐硬边色块，零渐变、零颗粒",
               "速度感：粗犷放射线 + 中心能量漩涡",
               "红：可到 15–20%，另可点明黄"]),
    dict(code="E", name="冰青金", tag="最贴角色：墨底 + 冰青 + 一点曜金，无红",
         thumb=swatch_e, real=False,
         pal=[("墨 #16181A", (22, 24, 26)), ("冰青 #9FE0EA", (159, 224, 234)),
              ("曜金 #E8C48A", (232, 196, 138)), ("纸白 #E6E4DC", (230, 228, 220))],
         ratio=[(0.40, (22, 24, 26)), (0.34, (230, 228, 220)), (0.26, (159, 224, 234))],
         spec=["笔触：水墨笔触 + 冰晶半透棱面",
               "速度感：冰棱碎裂向外放射",
               "红：一点都不要；暖金只在剑尖与瞳孔"]),
]


def main():
    W = 40 + len(STYLES) * 470
    H = 1180
    board = Image.new("RGB", (W, H), (14, 15, 18))
    d = ImageDraw.Draw(board)

    d.text((40, 34), "冲击帧 · 五种风格对比板", font=f(42, True), fill=(238, 235, 226))
    d.text((42, 92), "同一张定格帧（招式打完那一帧），只换风格锁；A / C 是真实参考片抽帧，B / D / E 是构图与配色示意",
           font=f(20), fill=(146, 148, 155))
    d.line([(40, 130), (W - 40, 130)], fill=(48, 50, 56), width=2)

    for i, s in enumerate(STYLES):
        x = 40 + i * 470
        thumb = s["thumb"]()
        board.paste(thumb, (x, 156))
        d.rectangle([x - 1, 155, x + TW, 157], fill=(60, 62, 68))
        d.rectangle([x - 1, 396, x + TW, 398], fill=(60, 62, 68))
        d.rectangle([x - 1, 156, x, 398], fill=(60, 62, 68))
        d.rectangle([x + TW - 1, 156, x + TW, 398], fill=(60, 62, 68))
        if not s["real"]:
            d.rectangle([x + TW - 116, 164, x + TW - 8, 188], fill=(0, 0, 0))
            d.text((x + TW - 110, 167), "构图示意", font=f(15), fill=(220, 190, 120))

        d.text((x, 414), f"{s['code']}　{s['name']}", font=f(30, True), fill=(236, 232, 222))
        d.text((x, 456), s["tag"], font=f(18), fill=(150, 152, 158))

        # 色板
        cw = 104
        for j, (lab, rgb) in enumerate(s["pal"]):
            cx = x + j * (cw + 6)
            d.rectangle([cx, 498, cx + cw, 540], fill=rgb, outline=(70, 72, 78))
            d.text((cx, 546), lab, font=f(13), fill=(160, 162, 168))

        # 明暗比例条
        bx, by, bw, bh = x, 586, TW, 18
        acc = 0
        for frac, rgb in s["ratio"]:
            w = int(bw * frac)
            d.rectangle([bx + acc, by, bx + acc + w, by + bh], fill=rgb, outline=(50, 52, 58))
            acc += w
        d.text((bx, by + 24), "　".join(
            f"{int(f * 100)}%" for f, _ in s["ratio"]), font=f(14), fill=(140, 142, 148))

        # 规格
        for k, line in enumerate(s["spec"]):
            d.text((x, 646 + k * 34), line, font=f(17), fill=(198, 195, 186))

        # 一句话判断
        verdict = {
            "A": "推荐：既有冲击帧的狠，又是水墨，能对上道之极。",
            "B": "适合冷、狠、不留情的角色；风险是太暗，抖音小屏看不清。",
            "C": "适合克制/悲情段落；冲击力最弱，靠留白撑。",
            "D": "最抓眼，但离燕云最远；适合投放钩子，不适合品牌片。",
            "E": "最稳的品牌向；但「冲击帧」的味道最淡，需要靠构图补。",
        }[s["code"]]
        d.text((x, 770), verdict, font=f(17), fill=(170, 200, 190))

    d.line([(40, 850), (W - 40, 850)], fill=(48, 50, 56), width=2)
    d.text((40, 872), "怎么选（按顺序，别跳）", font=f(22, True), fill=(230, 226, 216))
    rules = [
        "1　先看姿势：五种都必须和定格帧完全同姿势。改姿势的那张直接淘汰——说明「改画」变成了「重画」。",
        "2　再看像不像燕云：D 最燃最不像，E 最像最不狠，A / C 在中间。这是取舍，不是对错。",
        "3　最后看 2K 边缘：D 要硬边不能糊，A / C / E 要笔触可见不能糊成一片。糊了就重跑。",
        "4　选定后：把该风格的风格锁套到 ②③ 两镜，其余四种节点留着标【备用】，别删。",
    ]
    for k, r in enumerate(rules):
        d.text((40, 912 + k * 34), r, font=f(18), fill=(190, 188, 180))

    d.text((40, H - 46), "生成入口：02_画布/燕云冲击帧-风格试片-v5.monet（同一 T1 并行出五种）",
           font=f(17), fill=(120, 122, 128))

    board.save(OUT)
    print(OUT, board.size)


if __name__ == "__main__":
    main()
