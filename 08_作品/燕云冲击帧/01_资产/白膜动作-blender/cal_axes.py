# -*- coding: utf-8 -*-
"""轴向标定：隔离测试每个语义参数到底把肢体推向哪个世界方向。只打印，不渲染。"""
import bpy
import math

D = math.radians
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
from mathutils import Vector

V = Vector

SPEC = [
    ("root", (0, 0, 1.02), None),
    ("spine", (0, 0, 1.16), "root"),
    ("chest", (0, 0, 1.36), "spine"),
    ("shoR", (0.10, 0, 1.47), "chest"),
    ("elbR", (0.16, -0.02, 1.18), "shoR"),
    ("handR", (0.185, -0.04, 0.92), "elbR"),
    ("shoL", (-0.10, 0, 1.47), "chest"),
    ("elbL", (-0.16, -0.02, 1.18), "shoL"),
]
J = {}
for name, loc, par in SPEC:
    e = bpy.data.objects.new("J_" + name, None)
    e.location = loc
    sc.collection.objects.link(e)
    J[name] = e
bpy.context.view_layer.update()
for name, loc, par in SPEC:
    if par:
        e = J[name]
        mw = e.matrix_world.copy()
        e.parent = J[par]
        e.matrix_parent_inverse = J[par].matrix_world.inverted() @ mw @ e.matrix_basis.inverted()
bpy.context.view_layer.update()

HANG = {"shoR", "elbR", "handR", "shoL", "elbL"}
UP = {"spine", "chest"}


def setp(name, fwd=0.0, side=0.0, twist=0.0):
    o = J[name]
    if name in HANG:
        o.rotation_euler = (-D(fwd), -D(side), D(twist))
    else:
        o.rotation_euler = (D(fwd), D(side), D(twist))
    bpy.context.view_layer.update()


def clear():
    for o in J.values():
        o.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()


def tip(name):
    """该关节链末端（hand 尾端/chest 顶端）的世界坐标"""
    p = J[name].matrix_world.translation
    return p


def hand_end():
    o = J["handR"]
    return o.matrix_world @ V((0, 0, -0.075))


print("== 基线（全零）==")
clear()
print("  handR_end ", [round(v, 2) for v in hand_end()])
print("  chest     ", [round(v, 2) for v in tip("chest")])

print("== shoR 只给 side=+60（fwd=0,twist=0）==")
clear(); setp("shoR", side=60)
print("  handR_end ", [round(v, 2) for v in hand_end()])

print("== shoR 只给 side=-60 ==")
clear(); setp("shoR", side=-60)
print("  handR_end ", [round(v, 2) for v in hand_end()])

print("== shoR 只给 fwd=+60 ==")
clear(); setp("shoR", fwd=60)
print("  handR_end ", [round(v, 2) for v in hand_end()])

print("== cheст 只给 twist=+30 ==")
clear(); setp("chest", twist=30)
print("  shoR pos  ", [round(v, 2) for v in tip("shoR")])

print("== cheст 只给 side=+30 ==")
clear(); setp("chest", side=30)
print("  chest_head", [round(v, 2) for v in tip("chest")])

print("== root yaw=+40 ==")
clear()
J["root"].rotation_euler = (0, 0, D(40))
bpy.context.view_layer.update()
print("  shoR pos  ", [round(v, 2) for v in tip("shoR")])
print("CAL-DONE")
