# -*- coding: utf-8 -*-
"""白膜（blockout）生成器 v2 · Blender 脚本 —— 一条片子只有一个动作

修正（2026-11-02 用户）：参考片里其实**只有一个动作**，之前的"蓄—爆—收"四拍太复杂。
  剑之极：光点炸开 → 星芒 → 眼睛（一个动作：炸）
  道之极：抬手（一个动作：抬）
  拔剑　：抽剑（一个动作：抽）

所以每条白膜只保留 **一个主关节的一次位移**，加一次同向的余势（收势），不叠加第二个动作。

  B1 起手　：只做「抬眼 + 腕提十五度」（头与腕，各一次）
  B2 星芒　：无人物，只做「一个光球膨胀 → 炸成尖刺 → 缩成一只眼」
  B3 拔剑　：只做「右前臂抽出半尺」（肩几乎不动）
  B4 变装　：只做「一次挥剑弧线」（肩肘一起走，收在同一条弧上）

用法：
    blender -b -P 白膜生成-Blender.py -- --out "<输出目录>" --res 960 540 --fps 24
"""
import math
import os
import subprocess
import sys

import bpy
from mathutils import Euler

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

argv = sys.argv
out_dir, RES, FPS = None, (960, 540), 24
for i, a in enumerate(argv):
    if a == "--out" and i + 1 < len(argv):
        out_dir = argv[i + 1]
    if a == "--res" and i + 3 < len(argv):
        RES = (int(argv[i + 1]), int(argv[i + 2]))
    if a == "--fps" and i + 1 < len(argv):
        FPS = int(argv[i + 1])
out_dir = out_dir or os.path.join(os.path.expanduser("~"), "白膜输出")
os.makedirs(out_dir, exist_ok=True)

DUR, N = 4.0, int(4.0 * 24)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "FLAT"
sc.display.shading.color_type = "SINGLE"
sc.display.shading.single_color = (0.94, 0.94, 0.94)
sc.display.shading.show_object_outline = True
sc.display.shading.object_outline_color = (0.25, 0.25, 0.25)
sc.world = bpy.data.worlds.new("W")
sc.world.color = (0.66, 0.66, 0.66)
sc.render.resolution_x, sc.render.resolution_y = RES
sc.render.fps = FPS


def empty(name, loc, parent=None):
    bpy.ops.object.empty_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.empty_display_size = 0.06
    if parent:
        o.parent = parent
    return o


def limb(name, r, length, loc, parent):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=loc)
    o = bpy.context.object
    o.name = name
    o.parent = parent
    o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def ball(name, r, loc, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    o = bpy.context.object
    o.name = name
    o.parent = parent
    o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


# ---------------- 人偶
J = {}
hips = empty("hips", (0, 0, 1.00))
limb("torso", 0.15, 0.55, (0, 0, 1.28), hips)
chest = empty("chest", (0, 0, 1.56), hips)
J["chest"] = chest
limb("neck", 0.06, 0.10, (0, 0, 1.62), chest)
head_pivot = empty("head_pivot", (0, 0, 1.62), chest)
J["head"] = head_pivot
ball("head", 0.13, (0, 0, 0.13), head_pivot)

for side, sx in (("R", 1), ("L", -1)):
    sh = empty("shoulder" + side, (sx * 0.20, 0, 1.50), chest)
    J["sh" + side] = sh
    limb("upperArm" + side, 0.055, 0.30, (0, 0, -0.15), sh)
    el = empty("elbow" + side, (0, 0, -0.30), sh)
    J["el" + side] = el
    limb("foreArm" + side, 0.048, 0.28, (0, 0, -0.14), el)
    wr = empty("wrist" + side, (0, 0, -0.28), el)
    J["wr" + side] = wr
    if side == "R":
        ball("handR", 0.055, (0, 0, 0), wr)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.55), scale=(0.012, 0.012, 0.55))
        sw = bpy.context.object
        sw.parent = wr

for side, sx in (("R", 1), ("L", -1)):
    hp = empty("hipJ" + side, (sx * 0.11, 0, 1.00), hips)
    limb("thigh" + side, 0.07, 0.45, (0, 0, -0.23), hp)
    kn = empty("knee" + side, (0, 0, -0.46), hp)
    limb("shin" + side, 0.06, 0.42, (0, 0, -0.21), kn)

bpy.ops.object.camera_add(location=(0, -4.2, 1.15), rotation=(math.radians(90), 0, 0))
cam = bpy.context.object
cam.data.lens = 50
sc.camera = cam

# ---------------- 光球（只给 B2 用）
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.35))
GLOW = bpy.context.object
GLOW.name = "glow"
GLOW.scale = (0.001, 0.001, 0.001)

D = math.radians


def clear_all_keys():
    for o in bpy.data.objects:
        if o.animation_data:
            o.animation_data_clear()
    for o in (GLOW,):
        o.scale = (0.001, 0.001, 0.001)


def reset_pose():
    for k in ("chest", "head", "shR", "elR", "shL", "elL", "wrR"):
        J[k].rotation_euler = Euler((0, 0, 0), "XYZ")


def kf(o, frame, path="rotation_euler"):
    o.keyframe_insert(path, frame=frame)


# ---------------- 四套：一条只有一个动作
def build_B1():
    """抬眼 + 腕提 15°：只有头和腕各一次位移"""
    reset_pose()
    for f, head, wrist in ((0, 0, 0), (int(2.0 * FPS), -18, -15), (N - 1, -20, -16)):
        sc.frame_set(f)
        J["head"].rotation_euler = Euler((D(head), 0, 0), "XYZ")
        kf(J["head"], f)
        J["wrR"].rotation_euler = Euler((D(wrist), 0, 0), "XYZ")
        kf(J["wrR"], f)


def build_B3():
    """右前臂抽出半尺：肩几乎不动"""
    reset_pose()
    for f, sh, el in ((0, 38, 95), (int(1.6 * FPS), 46, 30), (N - 1, 48, 26)):
        sc.frame_set(f)
        J["shR"].rotation_euler = Euler((D(sh), 0, 0), "XYZ")
        kf(J["shR"], f)
        J["elR"].rotation_euler = Euler((D(el), 0, 0), "XYZ")
        kf(J["elR"], f)


def build_B4():
    """一次挥剑：肩肘沿同一条弧到顶，再在同一条弧上收一点"""
    reset_pose()
    for f, sh, el, wr in ((0, 40, 60, 0), (int(1.5 * FPS), 110, 0, 0), (N - 1, 96, -18, -30)):
        sc.frame_set(f)
        J["shR"].rotation_euler = Euler((D(sh), 0, 0), "XYZ")
        kf(J["shR"], f)
        J["elR"].rotation_euler = Euler((D(el), 0, 0), "XYZ")
        kf(J["elR"], f)
        J["wrR"].rotation_euler = Euler((D(wr), 0, 0), "XYZ")
        kf(J["wrR"], f)


def build_B2():
    """没有人物：光球膨胀炸开，再缩成一只眼"""
    reset_pose()
    for i in range(N):
        t = i / FPS
        if t < 1.0:
            s = 0.02 + 0.10 * (t / 1.0)
        elif t < 1.4:
            u = (t - 1.0) / 0.4
            s = 0.12 + 1.05 * (u * u)
        elif t < 2.6:
            u = (t - 1.4) / 1.2
            s = 1.17 - 0.97 * u
        else:
            s = 0.20 - 0.02 * ((t - 2.6) / 1.4)
        GLOW.scale = (s, s * 0.55, s * 0.55)   # 横向的星芒感
        GLOW.keyframe_insert("scale", frame=i)


def render(name, builder, hide_human=False):
    clear_all_keys()
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name != "glow":
            o.hide_render = hide_human
    GLOW.hide_render = not hide_human if name != "B2" else False
    if name == "B2":
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name != "glow":
                o.hide_render = True
    builder()
    sc.frame_start, sc.frame_end = 0, N - 1
    seq = os.path.join(out_dir, "_seq_" + name)
    os.makedirs(seq, exist_ok=True)
    for f in range(N):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(seq, "f%03d.png" % f)
        bpy.ops.render.render(write_still=True)
    mp4 = os.path.join(out_dir, name + ".mp4")
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-framerate", str(FPS), "-i", os.path.join(seq, "f%03d.png"),
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", mp4], check=True)
        print("写出:", mp4)
    except Exception as e:
        print("ffmpeg 合成失败（PNG 序列仍在）:", seq, e)


if __name__ == "__main__":
    render("B1", build_B1)
    render("B2", build_B2)
    render("B3", build_B3)
    render("B4", build_B4)
    print("全部完成:", out_dir)
