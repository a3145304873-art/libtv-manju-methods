# -*- coding: utf-8 -*-
"""生成《燕云冲击帧》三帧构图板 v3（同一张 16:9 画布，左中右三格）。
纯 PIL 绘制：构图示意用——机位、剪影、光位、强调色、帧表。
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

random.seed(11)
PW, PH = 1600, 900
ICE = (150, 226, 236)
ICE_HI = (242, 252, 255)
GOLD = (232, 196, 138)
IRID_A = (120, 220, 230)
IRID_B = (222, 150, 210)
FONT_DIR = "C:/Windows/Fonts/"


def font(size, bold=False):
    return ImageFont.truetype(FONT_DIR + ("msyhbd.ttc" if bold else "msyh.ttc"), size)


def vgrad(w, h, stops):
    ys = np.arange(h) / max(h - 1, 1)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    out = np.zeros((h, 3), dtype=float)
    for c in range(3):
        out[:, c] = np.interp(ys, pos, cols[:, c])
    return Image.fromarray(np.repeat(out[:, None, :], w, axis=1).astype(np.uint8), "RGB")


def add_glow(base, layer, radius, gain=1.0):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    if gain != 1.0:
        r, gg, b, a = g.split()
        g = Image.merge("RGBA", (r, gg, b, a.point(lambda v: min(255, int(v * gain)))))
    return Image.alpha_composite(base.convert("RGBA"), g)


def taper(d, p0, p1, w0, w1, color):
    v = np.array(p1, float) - np.array(p0, float)
    L = np.linalg.norm(v)
    if L == 0:
        return
    n = np.array([-v[1], v[0]]) / L
    a, b = np.array(p0, float), np.array(p1, float)
    d.polygon([tuple(a + n * w0), tuple(b + n * w1),
               tuple(b - n * w1), tuple(a - n * w0)], fill=color)


def brush(d, pts, w0, w1, color):
    """沿折线画锥形笔触（起笔粗、收笔细），比直线更像素描"""
    pts = [np.array(p, float) for p in pts]
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0:
            v = pts[1] - p
        elif i == n - 1:
            v = p - pts[-2]
        else:
            v = pts[i + 1] - pts[i - 1]
        L = np.linalg.norm(v) or 1.0
        nv = np.array([-v[1], v[0]]) / L
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t
        left.append(tuple(p + nv * w))
        right.append(tuple(p - nv * w))
    d.polygon(left + right[::-1], fill=color)


def star(d, x, y, r, color, alpha=220, spikes=4):
    pts = []
    for i in range(spikes * 2):
        a = math.pi / spikes * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.2
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=color + (alpha,))


# ---------------------------------------------------------------- ① 雪落无声
def panel1():
    im = vgrad(PW, PH, [
        (0.00, (7, 8, 11)), (0.32, (13, 15, 20)), (0.50, (30, 31, 36)),
        (0.60, (86, 84, 78)), (0.625, (204, 200, 188)), (0.78, (214, 210, 198)),
        (1.00, (172, 169, 160)),
    ]).convert("RGBA")
    gl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    d = ImageDraw.Draw(gl)
    for _ in range(190):
        x, y = random.uniform(0, PW), random.uniform(0, 545)
        s = random.uniform(0.6, 2.2)
        d.ellipse([x, y, x + s, y + s], fill=(240, 244, 248, random.randint(16, 76)))
    for _ in range(46):
        x, y = random.uniform(0, PW), random.uniform(580, 900)
        d.line([(x, y), (x + random.uniform(50, 200), y + random.uniform(-3, 3))],
               fill=(255, 255, 255, random.randint(5, 16)), width=random.randint(1, 3))
    # 远景木桩
    for (bx, top, tilt) in [(108, 372, 4), (176, 330, -5), (238, 388, 6), (294, 352, -3), (344, 396, 2)]:
        d.polygon([(bx, top), (bx + 18, top + 5), (bx + 20 + tilt, 672), (bx + tilt, 668)],
                  fill=(30, 28, 25, 225))
        d.line([(bx + 18, top + 7), (bx + 20 + tilt, 670)], fill=(160, 152, 132, 42), width=2)

    # 地面投影
    d.ellipse([962, 736, 1218, 800], fill=(120, 116, 106, 90))
    d.ellipse([1002, 748, 1180, 786], fill=(96, 92, 84, 90))

    body = (13, 14, 18, 252)
    hair = (210, 207, 198, 252)
    # 后层：白发（圆头形 + 垂下的发尾）
    d.ellipse([1018, 240, 1102, 348], fill=hair)
    taper(d, (1090, 300), (1108, 470), 16, 4, hair)
    taper(d, (1064, 320), (1078, 500), 11, 3, hair)
    taper(d, (1036, 330), (1040, 474), 8, 2, hair)
    # 头（脸在白发框里，暗面）
    d.ellipse([1022, 262, 1082, 326], fill=(32, 30, 30, 255))
    d.arc([1022, 262, 1082, 326], 200, 20, fill=hair, width=9)
    # 颈 / 身
    d.rectangle([1040, 322, 1062, 344], fill=body)
    d.polygon([(1012, 340), (1090, 340), (1104, 470), (1114, 590), (990, 590), (1000, 470)], fill=body)
    # 袍摆（两片 + 中缝）
    d.polygon([(988, 584), (1046, 584), (1052, 792), (992, 794)], fill=body)
    d.polygon([(1058, 584), (1108, 584), (1120, 782), (1066, 788)], fill=body)
    d.polygon([(1046, 588), (1058, 588), (1062, 794), (1048, 794)], fill=(6, 6, 8, 255))
    # 双臂
    d.polygon([(1012, 352), (990, 470), (1012, 492), (1032, 372)], fill=body)
    d.polygon([(1090, 352), (1130, 420), (1152, 452), (1126, 470), (1084, 396)], fill=body)
    # 腰带 + 青绦
    d.polygon([(1000, 532), (1108, 528), (1112, 566), (1004, 570)], fill=(7, 7, 9, 255))
    d.line([(1060, 566), (1032, 700), (1010, 792)], fill=(74, 158, 168, 200), width=6)
    d.line([(1060, 566), (1032, 700), (1010, 792)], fill=(150, 226, 236, 110), width=2)
    # 衣摆飞白
    for (sx, ex, ey) in [(996, 950, 812), (1064, 1040, 816), (1114, 1160, 802)]:
        taper(d, (sx, 770), (ex, ey), 13, 2, body)

    # 剑：手 (1150,452) → 剑尖 (786,806)
    hand, tip = (1150, 452), (786, 806)
    taper(d, hand, tip, 11, 4, (22, 24, 28, 210))                 # 暗边，压在雪地上才读得出
    taper(d, hand, tip, 8, 3, (200, 238, 246, 255))
    taper(d, hand, tip, 3, 1, (252, 255, 255, 255))
    taper(d, hand, tip, 12, 5, (150, 226, 236, 55))
    d.ellipse([1134, 438, 1172, 476], fill=(14, 15, 19, 255))     # 握拳
    d.line([(1134, 440), (1172, 474)], fill=(70, 64, 48, 255), width=5)
    d.line([(1128, 432), (1170, 470)], fill=(40, 44, 50, 255), width=11)
    d.line([(1128, 432), (1170, 470)], fill=GOLD + (170,), width=3)
    d.line([(1148, 462), (1108, 486)], fill=(26, 26, 30, 255), width=12)   # 握柄

    im = Image.alpha_composite(im, gl)

    rim = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.line([(1082, 300), (1096, 340), (1108, 430), (1118, 520), (1122, 592)],
            fill=GOLD + (135,), width=4, joint="curve")
    rd.line([(1058, 250), (1086, 262)], fill=GOLD + (95,), width=3)
    im = add_glow(im, rim, 7, 1.1)

    sp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    star(sd, 786, 806, 34, ICE_HI, 200)
    star(sd, 838, 766, 13, ICE_HI, 140)
    for _ in range(30):
        x, y = 786 + random.uniform(-110, 110), 806 + random.uniform(-52, 30)
        s = random.uniform(1, 4.5)
        sd.ellipse([x, y, x + s, y + s], fill=(230, 248, 252, random.randint(35, 130)))
    im = add_glow(im, sp, 10, 1.3)
    return im.convert("RGB")


# ---------------------------------------------------------------- ② 一线
def panel2():
    base = Image.new("RGBA", (PW, PH), (6, 7, 9, 255))
    mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).ellipse([240, -120, 1560, 900], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(80))
    skin = vgrad(PW, PH, [(0.0, (226, 220, 205)), (0.40, (206, 200, 186)),
                          (0.72, (168, 163, 152)), (1.0, (120, 117, 108))])
    base = Image.composite(skin, base.convert("RGB"), mask).convert("RGBA")

    d = ImageDraw.Draw(base)
    # 颊侧转折（暗部）
    sh = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sh)
    shd.polygon([(300, 520), (560, 470), (640, 900), (300, 900)], fill=(40, 36, 32, 70))
    base = Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(50)))

    d = ImageDraw.Draw(base)
    # 眉（一笔带弧）
    brush(d, [(676, 232), (780, 208), (880, 200), (1030, 196)], 15, 4, (22, 20, 18, 235))
    # 眼：放大到极特写，杏仁眼白 + 虹膜 + 神光，上睑一笔压住
    ecx, ecy = 884, 344
    top = [(ecx + 204 * (2 * t / 44 - 1), ecy - 66 * math.sin(math.pi * t / 44)) for t in range(45)]
    bot = [(ecx + 204 * (2 * t / 44 - 1), ecy + 48 * math.sin(math.pi * t / 44)) for t in range(44, -1, -1)]
    d.polygon(top + bot, fill=(192, 186, 172, 255))
    d.ellipse([ecx - 46, ecy - 62, ecx + 74, ecy + 62], fill=(44, 56, 62, 255))     # 虹膜
    d.ellipse([ecx - 18, ecy - 34, ecx + 38, ecy + 34], fill=(10, 14, 18, 255))     # 瞳孔
    d.ellipse([ecx - 30, ecy - 44, ecx + 4, ecy - 8], fill=(246, 250, 250, 255))    # 神光
    d.ellipse([ecx + 26, ecy + 6, ecx + 50, ecy + 30], fill=GOLD + (225,))          # 曜金
    brush(d, [(ecx - 204, ecy - 6), (ecx - 100, ecy - 54), (ecx + 20, ecy - 62), (ecx + 196, ecy - 30)],
          14, 3, (16, 14, 13, 255))
    brush(d, [(ecx - 186, ecy + 40), (ecx - 40, ecy + 56), (ecx + 196, ecy + 10)],
          6, 2, (16, 14, 13, 165))
    # 颊侧阴影，托住眼睛
    sh2 = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    brush(ImageDraw.Draw(sh2), [(700, 470), (860, 505), (1040, 470)], 40, 6, (60, 54, 46, 60))
    base = Image.alpha_composite(base, sh2.filter(ImageFilter.GaussianBlur(28)))
    d = ImageDraw.Draw(base)

    # 发：几笔粗飞白
    gl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    for (p0, p1, w0, w1, col) in [
        ((236, -40), (620, 700), 17, 2, (240, 238, 229, 225)),
        ((300, -60), (700, 640), 11, 2, (244, 242, 234, 195)),
        ((176, 60), (520, 720), 9, 2, (232, 230, 221, 175)),
        ((1180, -60), (1010, 660), 15, 2, (240, 238, 229, 215)),
        ((1290, 40), (1080, 700), 10, 2, (236, 234, 226, 185)),
        ((1120, -80), (1048, 420), 7, 1, (244, 242, 234, 150)),
    ]:
        taper(gd, p0, p1, w0, w1, col)
    for (p0, p1) in [((270, 0), (640, 660)), ((1216, 0), (1040, 600))]:
        taper(gd, p0, p1, 3, 1, (14, 13, 12, 150))
    # 颊上墨点
    for _ in range(38):
        x, y = random.uniform(640, 860), random.uniform(400, 610)
        r = random.uniform(0.8, 7)
        gd.ellipse([x, y, x + r, y + r], fill=(18, 16, 15, random.randint(45, 200)))
    base = Image.alpha_composite(base, gl)

    # 刃：斜切
    ya, yb = 748, 624
    blade = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blade)
    bd.polygon([(-20, ya - 112), (PW + 20, yb - 112), (PW + 20, PH + 20), (-20, PH + 20)],
               fill=(26, 28, 33, 255))
    bd.polygon([(-20, ya - 96), (PW + 20, yb - 96), (PW + 20, yb - 6), (-20, ya + 6)],
               fill=(120, 122, 122, 255))
    bd.polygon([(-20, ya - 44), (PW + 20, yb - 52), (PW + 20, yb - 38), (-20, ya - 30)],
               fill=(158, 160, 158, 235))
    base = Image.alpha_composite(base, blade)

    sp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(sp)
    sdd.line([(-20, ya - 92), (PW + 20, yb - 92)], fill=(252, 250, 242, 255), width=3)
    sdd.line([(-20, ya - 82), (PW + 20, yb - 82)], fill=(226, 222, 210, 70), width=2)
    base = add_glow(base, sp, 6, 1.2)

    gp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gdd = ImageDraw.Draw(gp)
    gdd.line([(1024, yb - 90), (1258, yb - 102)], fill=GOLD + (235,), width=5)
    base = add_glow(base, gp, 10, 1.5)

    ice = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    idr = ImageDraw.Draw(ice)
    for (x, y, r) in [(1442, 586, 26), (1524, 552, 14), (1356, 612, 12)]:
        star(idr, x, y, r, ICE_HI, 190)
    for _ in range(16):
        x, y = random.uniform(1300, 1600), random.uniform(548, 640)
        s = random.uniform(1, 3)
        idr.ellipse([x, y, x + s, y + s], fill=(230, 248, 252, random.randint(50, 150)))
    base = add_glow(base, ice, 8, 1.2)
    return base.convert("RGB")


# ---------------------------------------------------------------- ③ 龙跃
def panel3():
    base = Image.new("RGBA", (PW, PH), (7, 8, 10, 255))
    glow = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([140, -160, 1200, 880], fill=(26, 80, 90, 100))
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(150)))

    guard_y, guard_x0, guard_x1 = 676, 1076, 1372
    p0 = np.array([1226.0, 686.0])
    p1 = np.array([322.0, 42.0])
    v = p1 - p0
    n = np.array([-v[1], v[0]]) / np.linalg.norm(v)

    def quad(w0, w1):
        return [tuple(p0 + n * w0), tuple(p1 + n * w1),
                tuple(p1 - n * w1), tuple(p0 - n * w0)]

    bl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bl)
    bd.polygon(quad(52, 10), fill=(150, 198, 210, 205))
    bd.polygon(quad(24, 4), fill=(218, 242, 248, 165))
    bd.line([tuple(p0 + n * 50), tuple(p1 + n * 9)], fill=(250, 254, 255, 255), width=5)
    bd.line([tuple(p0 - n * 46), tuple(p1 - n * 8)], fill=(112, 186, 200, 200), width=3)
    for t in np.linspace(0.08, 0.9, 9):
        b = p0 + v * t
        seg = b + n * (10 + 12 * math.sin(t * 8))
        bd.line([tuple(seg), tuple(seg + n * 14 + v * 0.012)], fill=(240, 252, 254, 105), width=2)
    base = Image.alpha_composite(base, bl)

    swirl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(swirl)
    for k, amp in enumerate((150, 108, 182)):
        pts = []
        for i in range(90):
            t = 0.04 + i / 89 * 0.96
            b = p0 + v * t
            off = n * (math.sin(t * 6.4 + k * 1.7) * amp * (0.3 + t))
            pts.append(tuple(b + off))
        sd.line(pts, fill=(176, 238, 246, 64), width=11 - k * 2, joint="curve")
        sd.line(pts, fill=(226, 248, 252, 34), width=3, joint="curve")
    base = add_glow(base, swirl, 13, 1.1)

    # 袖
    arm = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arm)
    ad.polygon([(1042, 744), (1206, 712), (1420, 940), (1040, 940)], fill=(230, 226, 214, 246))
    base = Image.alpha_composite(base, arm)

    # 剑柄（竖向出画）
    hg = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hg)
    hd.polygon([(1178, 690), (1268, 678), (1310, 940), (1216, 940)], fill=(24, 25, 30, 255))
    for t in range(4):
        y = 712 + t * 30
        hd.line([(1186, y), (1286, y - 10)], fill=(96, 76, 48, 170), width=3)
    base = Image.alpha_composite(base, hg)

    # 手：一块暗形 + 指缝（裁在右下角，只留“握住”的意思）
    hs = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    hsd = ImageDraw.Draw(hs)
    hsd.polygon([(1080, 900), (1108, 802), (1196, 768), (1292, 810), (1336, 900)],
                fill=(24, 25, 29, 252))
    for (x0, y0, x1, y1) in [(1114, 812, 1300, 792), (1116, 840, 1304, 820), (1118, 866, 1308, 846)]:
        hsd.line([(x0, y0), (x1, y1)], fill=(150, 146, 132, 60), width=3)
    taper(hsd, (1124, 846), (1208, 900), 22, 13, (26, 27, 31, 252))   # 拇指
    base = Image.alpha_composite(base, hs)

    # 护手（浅色，暗底上才读得出）
    gd = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    gdd = ImageDraw.Draw(gd)
    gdd.rounded_rectangle([guard_x0, guard_y, guard_x1, guard_y + 32], radius=13,
                          fill=(198, 194, 182, 255))
    gdd.line([(guard_x0 + 8, guard_y + 27), (guard_x1 - 8, guard_y + 27)],
             fill=(112, 108, 98, 255), width=5)
    base = Image.alpha_composite(base, gd)

    ir = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    idr = ImageDraw.Draw(ir)
    for i in range(96):
        t = i / 95
        x = guard_x0 + 4 + t * (guard_x1 - guard_x0 - 8)
        col = tuple(int(IRID_A[c] + (IRID_B[c] - IRID_A[c]) * (0.5 + 0.5 * math.sin(t * 6.28))) for c in range(3))
        idr.line([(x, guard_y + 22), (x, guard_y + 30)], fill=col + (235,), width=5)
    base = add_glow(base, ir, 8, 1.5)

    shards = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shards)
    for _ in range(20):
        cx, cy = random.uniform(300, 1120), random.uniform(60, 720)
        s = random.uniform(5, 18)
        a = random.uniform(0, math.tau)
        pts = [(cx + math.cos(a + i * 2.1) * s * random.uniform(0.45, 1.25),
                cy + math.sin(a + i * 2.1) * s * random.uniform(0.45, 1.25)) for i in range(3)]
        shd.polygon(pts, fill=(228, 248, 252, random.randint(26, 100)))
    base = add_glow(base, shards, 6, 1.1)

    sp = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(sp)
    for _ in range(30):
        x, y = random.uniform(1080, 1360), random.uniform(760, 900)
        r = random.uniform(1, 6)
        sdd.ellipse([x, y, x + r, y + r], fill=(20, 18, 16, random.randint(35, 140)))
    base = Image.alpha_composite(base, sp)
    return base.convert("RGB")


# ---------------------------------------------------------------- 画布
def build():
    W, H = 2640, 1006
    board = Image.new("RGB", (W, H), (13, 14, 17))
    d = ImageDraw.Draw(board)
    d.text((72, 46), "燕云冲击帧 · 三帧构图板", font=font(44, True), fill=(238, 235, 226))
    d.text((74, 108),
           "角色：白发剑客（白袍黑带／冰霜气劲）　武器：藏音·龙跃霄汉（冰泉 · 擎冰 · 炼虹 · 曜日）",
           font=font(24), fill=(150, 152, 158))
    d.line([(72, 162), (W - 72, 162)], fill=(48, 50, 56), width=2)

    panels = [panel1(), panel2(), panel3()]
    names = ["① 雪落无声", "② 一线", "③ 龙跃"]
    specs = [
        ["全身立势 · 35mm · 逆光", "左侧留白 · 剑尖触地炸开冰霜", "冲击：8 帧 / 白闪 1 帧"],
        ["刃口与眼 · 85mm 侧逆", "刃把画面切成 2:1 · 颊上墨点", "冲击：反光扫过 6 帧"],
        ["剑身与手 · 50mm 微距", "剑出画 · 炼虹只留一道", "冲击：碎冰炸开 10 帧"],
    ]
    bars = [
        [(0.00, 0.57, "pale"), (0.57, 0.60, "cyan"), (0.60, 1.00, "pale"), (0.575, 1, "tick")],
        [(0.00, 0.17, "pale"), (0.17, 0.20, "cyan"), (0.20, 0.73, "pale"),
         (0.73, 0.86, "cyan"), (0.86, 1.00, "pale"), (0.20, 1, "tick")],
        [(0.00, 0.29, "pale"), (0.29, 0.30, "black"), (0.30, 0.60, "pale"),
         (0.60, 0.62, "cyan"), (0.62, 1.00, "pale"), (0.61, 1, "tick")],
    ]

    x = 72
    for i in range(3):
        pw, ph = 800, 450
        board.paste(panels[i].resize((pw, ph), Image.LANCZOS), (x, 192))
        d.rectangle([x - 1, 191, x + pw, 193], fill=(62, 64, 70))
        d.rectangle([x - 1, 641, x + pw, 643], fill=(62, 64, 70))
        d.rectangle([x - 1, 192, x, 642], fill=(62, 64, 70))
        d.rectangle([x + pw - 1, 192, x + pw, 642], fill=(62, 64, 70))
        d.text((x + 2, 658), names[i], font=font(29, True), fill=(232, 228, 218))
        for j, s in enumerate(specs[i]):
            d.text((x + 2, 698 + j * 28), s, font=font(20), fill=(138, 140, 146))
        bx, by, bw, bh = x + 2, 800, pw - 4, 20
        d.rectangle([bx, by, bx + bw, by + bh], fill=(38, 40, 46))
        for (a, b, kind) in bars[i]:
            if kind == "tick":
                tx = bx + int(a * bw)
                d.rectangle([tx - 2, by - 7, tx + 2, by + bh + 7], fill=GOLD)
                continue
            col = {"pale": (152, 152, 154), "cyan": (86, 190, 206), "black": (18, 18, 22)}[kind]
            d.rectangle([bx + int(a * bw), by, bx + int(b * bw), by + bh], fill=col)
        d.text((bx, by + bh + 8), "0s", font=font(16), fill=(108, 110, 116))
        d.text((bx + bw - 22, by + bh + 8), "3s", font=font(16), fill=(108, 110, 116))
        d.text((bx + 150, by + bh + 8), "浅灰＝静帧　青＝冲击　金线＝1 帧白闪",
               font=font(16), fill=(108, 110, 116))
        x += pw + 40

    d.line([(72, 892), (W - 72, 892)], fill=(48, 50, 56), width=2)
    d.text((72, 914),
           "三格共用：白闪 1 帧（33ms）· 静帧占 2/3 · 强调色只给一处 · 大字 ≤4 字 · 母版 16:9 / 30fps",
           font=font(21), fill=(128, 130, 136))
    d.text((W - 300, 914), "构图示意 · 非最终画面", font=font(21), fill=(96, 98, 104))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "三帧构图板.png")
    board.save(out)
    print(out, board.size)


if __name__ == "__main__":
    build()
