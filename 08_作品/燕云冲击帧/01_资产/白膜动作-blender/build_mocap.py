# -*- coding: utf-8 -*-
"""燕云冲击帧 · 白膜动作示范片生成 v4（大动作幅度版）

v4 依据参考片（冲击帧3 拔剑段 / 冲击帧2 道之极）的真实动作特征重做幅度：
  参考动作签名 → 宽站姿压低 · 躯干强拧转 · 单臂完全伸展 · 巨刃斜贯画面出画 · 收势余摆
  本版落实：剑 0.92m → 1.30m；手臂摆幅 ~200°；躯干拧转 ±40~55°；爆段加过冲帧；
            站姿腿分开 20~26° 并屈膝压低（下沉量按几何算，脚不悬空）。

四条片对应画布 燕云冲击帧-白膜动作-16x9-v39.monet 的白模节点：
  01 划弧斩   ↔ node-31fffa42  蓄:抬臂后坐 → 爆:斜劈过体前 → 收:过冲后划弧落体侧
  02 双臂推收 ↔ node-6b4e76bc  蓄:深蹲双臂后拉开胸 → 爆:双臂直线推出+上身前压 → 收:分段回收 → 转头沉颌
  03 横扫收剑 ↔ node-8405fdad  蓄:侧身沉剑于体后 → 爆:横向大扫全画幅 → 收:过冲后收剑于身后
  04 抽剑递剑 ↔ node-e459eed1  蓄:拧身藏剑于腰后 → 爆:抽出直递镜头最前 → 收:翻腕下压

规格：4s@24fps=96帧、1920x1080、纯中灰背景、哑光白人形、镜头固定、全身居中。
绑定：普通空物体 FK 关节链（不用骨骼父级，避免 5.2 矩阵约定问题）。
"""
import bpy
import math
import os

D = math.radians
COS = math.cos
OUT_DIR = r"E:\libtv漫剧\08_作品\燕云冲击帧\01_资产\白膜动作-blender"
FPS = 24
END = 96  # 4.0s
WHITE = (0.93, 0.93, 0.93, 1.0)
SWORD_LEN = 1.30  # v4：参考片巨刃比例

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.fps = FPS
scene.render.fps_base = 1.0
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
# 本机 5.2 提取版 FFMPEG 枚举受限 → PNG 序列 + 外部 ffmpeg 合成
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"

sh = scene.display.shading
for a, v in (("light", "STUDIO"), ("color_type", "OBJECT"), ("background_type", "WORLD"),
             ("show_cavity", True), ("cavity_type", "BOTH"), ("show_shadows", True),
             ("shadow_type", "FLOOR"), ("shadow_intensity", 0.35)):
    try:
        if hasattr(sh, a):
            setattr(sh, a, v)
    except Exception as e:
        print("SET-FAIL", a, e)

world = bpy.data.worlds.new("World")
scene.world = world
world.color = (0.5, 0.5, 0.5)

from mathutils import Vector

V = Vector

# 相机（固定；v4 后退到 6.2m 给巨刃大摆幅留画框）
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.0, -6.2, 1.05)
cam.rotation_euler = (V((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"
floor.color = (0.44, 0.44, 0.44, 1.0)

# ---------------------------------------------------------------- 关节
JOINTS = {
    "root":  ((0, 0, 1.02), None),
    "spine": ((0, 0, 1.16), "root"),
    "chest": ((0, 0, 1.36), "spine"),
    "neck":  ((0, 0, 1.50), "chest"),
    "head":  ((0, 0, 1.58), "neck"),
    "shoR":  ((0.10, 0, 1.47), "chest"),
    "elbR":  ((0.16, -0.02, 1.18), "shoR"),
    "handR": ((0.185, -0.04, 0.92), "elbR"),
    "shoL":  ((-0.10, 0, 1.47), "chest"),
    "elbL":  ((-0.16, -0.02, 1.18), "shoL"),
    "handL": ((-0.185, -0.04, 0.92), "elbL"),
    "hipR":  ((0.095, 0, 0.97), "root"),
    "kneeR": ((0.10, -0.01, 0.54), "hipR"),
    "ankR":  ((0.10, -0.02, 0.12), "kneeR"),
    "hipL":  ((-0.095, 0, 0.97), "root"),
    "kneeL": ((-0.10, -0.01, 0.54), "hipL"),
    "ankL":  ((-0.10, -0.02, 0.12), "kneeL"),
}
J = {}
for name, (loc, par) in JOINTS.items():
    e = bpy.data.objects.new("J_" + name, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.04
    e.location = loc
    scene.collection.objects.link(e)
    J[name] = e

# matrix_world 在挂父级瞬间会被重算，必须先存"挂之前"的世界矩阵
bpy.context.view_layer.update()
for name, (loc, par) in JOINTS.items():
    if par:
        e = J[name]
        mw = e.matrix_world.copy()
        e.parent = J[par]
        e.matrix_parent_inverse = J[par].matrix_world.inverted() @ mw @ e.matrix_basis.inverted()
bpy.context.view_layer.update()

HANG = {"shoR", "elbR", "handR", "shoL", "elbL", "handL", "hipR", "kneeR", "ankR", "hipL", "kneeL", "ankL"}
ROOT_Z = JOINTS["root"][0][2]


def K(name, f, fwd=0.0, side=0.0, twist=0.0):
    """语义关键帧：fwd 正=朝镜头/前方摆，side 正=朝画面右(+X)，twist=绕段轴扭转"""
    o = J[name]
    if name in HANG:
        o.rotation_euler = (-D(fwd), -D(side), D(twist))
    else:
        o.rotation_euler = (D(fwd), D(side), D(twist))
    o.keyframe_insert("rotation_euler", frame=f)


def root_yaw(f, deg):
    J["root"].rotation_euler = (0, 0, D(deg))
    J["root"].keyframe_insert("rotation_euler", frame=f)


def root_shift(f, dx=0.0, dy=0.0, dz=0.0):
    J["root"].location = (dx, dy, ROOT_Z + dz)
    J["root"].keyframe_insert("location", frame=f)


def stance(f, crouch=12.0, spread=20.0, extra_drop=0.0, dy=0.0, dx=0.0, yaw=None):
    """宽站姿：腿分开 + 屈膝压低。下沉量按几何算 → 脚不悬空。
    crouch: 屈膝角(度)  spread: 两腿外展角(度)  额外下沉/前后位移可加"""
    K("hipR", f, fwd=crouch, side=spread)
    K("kneeR", f, fwd=-crouch)
    K("ankR", f, fwd=crouch * 0.15)
    K("hipL", f, fwd=crouch, side=-spread)
    K("kneeL", f, fwd=-crouch)
    K("ankL", f, fwd=crouch * 0.15)
    # 精确下沉量：腿向量 (0,0,-L) 经 Rx(crouch)·Ry(spread) 后 z=-L·cos·cos
    drop = 0.85 * (1 - COS(D(crouch)) * COS(D(spread))) - 0.02 + extra_drop
    root_shift(f, dx=dx, dy=dy, dz=-drop)
    if yaw is not None:
        root_yaw(f, yaw)


def reset_pose():
    for o in J.values():
        o.rotation_euler = (0, 0, 0)
    J["root"].location = (0, 0, ROOT_Z)
    for o in J.values():
        if o.animation_data:
            o.animation_data.action = None
    act = bpy.data.actions.new("Action")
    for o in J.values():
        o.animation_data_create()
        o.animation_data.action = act


# ---------------------------------------------------------------- 白膜网格
def capsule(name, p1, p2, r, color=WHITE):
    p1, p2 = V(p1), V(p2)
    d = p2 - p1
    L = max(d.length, 0.02)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20, radius=r, depth=L,
        location=(p1 + p2) / 2, rotation=d.to_track_quat("Z", "Y").to_euler())
    cyl = bpy.context.object
    parts = [cyl]
    for p in (p1, p2):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=r, location=p)
        parts.append(bpy.context.object)
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = cyl
    bpy.ops.object.join()
    m = bpy.context.object
    m.name = name
    m.color = color
    return m


def bind(mesh, joint_name):
    bpy.context.view_layer.update()
    mw = mesh.matrix_world.copy()
    e = J[joint_name]
    mesh.parent = e
    mesh.matrix_parent_inverse = e.matrix_world.inverted() @ mw @ mesh.matrix_basis.inverted()


bind(capsule("m_pelvis", (0, 0, 0.98), (0, 0, 1.14), 0.135), "root")
bind(capsule("m_torso", (0, 0, 1.14), (0, 0, 1.40), 0.15), "spine")
bind(capsule("m_chest", (0, 0, 1.38), (0, 0, 1.50), 0.16), "chest")
bind(capsule("m_neck", (0, 0, 1.50), (0, 0, 1.58), 0.05), "neck")
bind(capsule("m_head", (0, 0, 1.60), (0, 0, 1.70), 0.115), "head")
bind(capsule("m_upArmR", (0.10, 0, 1.47), (0.16, -0.02, 1.18), 0.052), "shoR")
bind(capsule("m_loArmR", (0.16, -0.02, 1.18), (0.185, -0.04, 0.92), 0.046), "elbR")
bind(capsule("m_handR", (0.185, -0.04, 0.92), (0.20, -0.05, 0.845), 0.052), "handR")
bind(capsule("m_upArmL", (-0.10, 0, 1.47), (-0.16, -0.02, 1.18), 0.052), "shoL")
bind(capsule("m_loArmL", (-0.16, -0.02, 1.18), (-0.185, -0.04, 0.92), 0.046), "elbL")
bind(capsule("m_handL", (-0.185, -0.04, 0.92), (-0.20, -0.05, 0.845), 0.052), "handL")
bind(capsule("m_thighR", (0.095, 0, 0.97), (0.10, -0.01, 0.54), 0.078), "hipR")
bind(capsule("m_shinR", (0.10, -0.01, 0.54), (0.10, -0.02, 0.12), 0.058), "kneeR")
bind(capsule("m_footR", (0.10, -0.05, 0.10), (0.10, -0.20, 0.05), 0.05), "ankR")
bind(capsule("m_thighL", (-0.095, 0, 0.97), (-0.10, -0.01, 0.54), 0.078), "hipL")
bind(capsule("m_shinL", (-0.10, -0.01, 0.54), (-0.10, -0.02, 0.12), 0.058), "kneeL")
bind(capsule("m_footL", (-0.10, -0.05, 0.10), (-0.10, -0.20, 0.05), 0.05), "ankL")

# 剑：刃 1.30m，握把在 handR，刃沿小臂延长线向下（刃心在 grip 下方半刃长处）
GRIP_Z = 0.92
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12, radius=0.018, depth=SWORD_LEN,
    location=(0.185, -0.06, GRIP_Z - SWORD_LEN / 2))
blade = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.185, -0.06, GRIP_Z - 0.02))
guard = bpy.context.object
guard.scale = (0.016, 0.11, 0.028)
bpy.ops.object.select_all(action="DESELECT")
blade.select_set(True)
guard.select_set(True)
bpy.context.view_layer.objects.active = blade
bpy.ops.object.join()
sword = bpy.context.object
sword.name = "Sword"
sword.color = WHITE
bind(sword, "handR")
SWORD_TIP_LOCAL = V((0, 0, -SWORD_LEN / 2))  # 刃尖在本地 -Z（剑对象原点=刃心）

# ---------------------------------------------------------------- 逐帧审计
def audit(clip, need_sword):
    """逐帧评估：剑尖最低点 + 可见网格包围盒，防止穿地/飞出画
    只看 hide_render=False 的物体（隐藏的剑不算）"""
    min_tip, tip_f = 9.9, 0
    min_z, min_obj, min_f = 9.9, "", 0
    max_z, max_f = -9.9, 0
    max_x = 0.0
    meshes = [o for o in bpy.data.objects
              if o.type == "MESH" and o.name != "Floor" and not o.hide_render]
    for f in range(1, END + 1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        if need_sword and not sword.hide_render:
            tip = sword.matrix_world @ SWORD_TIP_LOCAL
            if tip.z < min_tip:
                min_tip, tip_f = tip.z, f
        for o in meshes:
            for c in o.bound_box:
                w = o.matrix_world @ V(c)
                if w.z < min_z:
                    min_z, min_obj, min_f = w.z, o.name, f
                max_z = max(max_z, w.z)
                max_x = max(max_x, abs(w.x))
    print("AUDIT %s | 最低 %.3f(%s@f%d) | 剑尖 %.3f@f%d | 最高 %.2f | 最远|x| %.2f"
          % (clip, min_z, min_obj, min_f, min_tip, tip_f, max_z, max_x))
    if need_sword and min_tip < -0.02:
        print("  !! WARN 剑尖穿地 %.3f @f%d" % (min_tip, tip_f))
    if min_z < -0.05:
        print("  !! WARN 网格穿地 %.3f (%s@f%d)" % (min_z, min_obj, min_f))
    if os.environ.get("MOCAP_TIPS") and need_sword:
        for f in (1, 26, 30, 40, 45, 58, 70):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            hand = J["handR"].matrix_world @ V((0, 0, -0.075))
            tip = sword.matrix_world @ SWORD_TIP_LOCAL
            d = (tip - hand).normalized()
            print("  TIP f%-3d hand(%.2f,%.2f,%.2f) tip(%.2f,%.2f,%.2f) dir(%.2f,%.2f,%.2f)"
                  % (f, hand.x, hand.y, hand.z, tip.x, tip.y, tip.z, d.x, d.y, d.z))


PREVIEW = bool(os.environ.get("MOCAP_PREVIEW"))
AUDIT_ONLY = bool(os.environ.get("MOCAP_AUDIT"))
PREVIEW_FRAMES = [1, 26, 30, 40, 45, 56, 70]


def render_clip(name):
    if AUDIT_ONLY:
        print("AUDIT-ONLY skip render", name)
        return
    if PREVIEW:
        scene.render.resolution_percentage = 50
        step = 1
    else:
        scene.render.resolution_percentage = 100
        step = 4  # 每 4 帧一渲仅用于快速预览时会覆盖，下面按需处理
    if PREVIEW:
        out = os.path.join(OUT_DIR, "preview")
        os.makedirs(out, exist_ok=True)
        for f in PREVIEW_FRAMES:
            scene.frame_set(f)
            bpy.context.view_layer.update()
            scene.render.filepath = os.path.join(out, "%s_f%03d.png" % (name, f))
            bpy.ops.render.render(write_still=True)
        print("PREVIEW-DONE", name)
        return
    scene.frame_start = 1
    scene.frame_end = END
    frames_dir = os.path.join(OUT_DIR, "frames", name)
    os.makedirs(frames_dir, exist_ok=True)
    scene.render.filepath = os.path.join(frames_dir, "f")
    print("RENDER-START", name)
    bpy.ops.render.render(animation=True)
    print("RENDER-DONE", name, frames_dir)


def breathing(f0, base_fwd=0.0):
    K("chest", f0, fwd=base_fwd)
    K("chest", f0 + 14, fwd=base_fwd - 3)
    K("chest", f0 + 28, fwd=base_fwd)


# ================================================================ 01 划弧斩（右上举 → 左下斜劈）
# 幅度要点：整条弧走 side（画面平面内的俯仰弧），side 0=垂下 90=水平 180=举顶，负=画面左
reset_pose()
sword.hide_render = True
stance(1, crouch=14, spread=20, yaw=-15)
K("shoR", 1, side=25); K("elbR", 1, fwd=40)
K("chest", 1, twist=-8)
# 蓄：右臂举过右肩、肘折起、身体拧转后坐
K("shoR", 26, side=138, fwd=-8); K("elbR", 26, fwd=72)
K("chest", 26, twist=-26, side=8)
stance(26, crouch=24, spread=22, dy=0.10, yaw=-34)
# 蓄末微顿
K("shoR", 30, side=146, fwd=-8); K("elbR", 30, fwd=68)
K("chest", 30, twist=-30, side=10)
stance(30, crouch=26, spread=22, dy=0.11, yaw=-38)
# 爆：过顶弧甩到画面左、手到肩高之外（画布要求"前挥到与肩平"）
K("shoR", 40, side=262, fwd=18); K("elbR", 40); K("handR", 40, twist=-20)
K("chest", 40, twist=22, side=-12)
stance(40, crouch=18, spread=25, dy=-0.12, yaw=0)
# 过冲：再甩过目标位
K("shoR", 45, side=275, fwd=20); K("elbR", 45, fwd=-6)
K("chest", 45, twist=30, side=-16)
stance(45, crouch=16, spread=25, dy=-0.14, yaw=6)
# 收：顺弧继续往下、落回体侧（画布要求"划一道弧收到体侧"）
K("shoR", 56, side=300, fwd=6); K("elbR", 56, fwd=45)
K("chest", 56, twist=14, side=-6)
stance(56, crouch=20, spread=22, yaw=8)
# 定
K("shoR", 70, side=340); K("elbR", 70, fwd=55)
K("head", 70, fwd=8, side=6)
K("chest", 70, twist=4)
stance(70, crouch=16, spread=21, yaw=0)
breathing(72, 0)
audit("01 划弧斩", False)
render_clip("白膜-01-划弧斩")

# ================================================================ 02 双臂推收（两侧大张 → 中线推出）
# 幅度要点：双臂从 ±82° 大开拉到 ±8° 收拢，横向收拢 148° 在正面机位完全可读
reset_pose()
sword.hide_render = True
stance(1, crouch=14, spread=20, yaw=0)
K("shoR", 1, side=20, fwd=-6); K("elbR", 1, fwd=30)
K("shoL", 1, side=-20, fwd=-6); K("elbL", 1, fwd=30)
# 蓄：深蹲、双臂大张向后折、背拱
K("shoR", 26, side=70, fwd=-25); K("elbR", 26, fwd=88)
K("shoL", 26, side=-70, fwd=-25); K("elbL", 26, fwd=88)
K("chest", 26, fwd=-30)
stance(26, crouch=30, spread=24, dy=0.20)
K("shoR", 30, side=74, fwd=-26); K("elbR", 30, fwd=92)
K("shoL", 30, side=-74, fwd=-26); K("elbL", 30, fwd=92)
K("chest", 30, fwd=-34)
stance(30, crouch=32, spread=24, dy=0.22)
# 爆：双臂向前外侧伸出（手宽于肩 → 手臂成两条可见斜线）、上身前压、起身前顶
K("shoR", 40, side=52, fwd=88); K("elbR", 40); K("handR", 40, fwd=20)
K("shoL", 40, side=-52, fwd=88); K("elbL", 40); K("handL", 40, fwd=20)
K("chest", 40, fwd=26)
stance(40, crouch=16, spread=22, dy=-0.20)
# 过冲
K("shoR", 45, side=58, fwd=100); K("elbR", 45, fwd=-6)
K("shoL", 45, side=-58, fwd=100); K("elbL", 45, fwd=-6)
K("chest", 45, fwd=34)
stance(45, crouch=14, spread=22, dy=-0.22)
# 收：先小臂再大臂
K("elbR", 54, fwd=105); K("elbL", 54, fwd=105)
K("shoR", 62, side=30, fwd=30); K("shoL", 62, side=-30, fwd=30)
K("elbR", 62, fwd=62); K("elbL", 62, fwd=62)
K("chest", 62, fwd=-6)
stance(62, crouch=22, spread=22, dy=0.02)
# 2.6s 头猛转向镜头、下颌一沉
K("head", 62, fwd=0, side=0)
K("head", 67, fwd=18, side=10)
K("head", 72, fwd=15, side=10)
K("shoR", 72, side=26, fwd=14); K("elbR", 72, fwd=48)
K("shoL", 72, side=-26, fwd=14); K("elbL", 72, fwd=48)
stance(72, crouch=18, spread=21)
breathing(74, 0)
audit("02 双臂推收", False)
render_clip("白膜-02-双臂推收")

# ================================================================ 03 横扫收剑（举刃过右 → 斜贯全画幅左扫 → 收于身后）
# 幅度要点：elevation 从 side=126（右高位）扫到 -80（左下方），全弧 ~206° 在画面平面内；
#          中段 f36 折肘 95°，让刃从"折在身前"越过正下方（避免 1.3m 刃插地），
#          到 f40 再甩开 —— 折→放的鞭打感也是真实发力的样子。
reset_pose()
sword.hide_render = False
K("shoR", 1, side=70, fwd=-16); K("elbR", 1, fwd=45); K("handR", 1, twist=20)
K("shoL", 1, side=-14); K("elbL", 1, fwd=34)
K("chest", 1, twist=-10)
stance(1, crouch=18, spread=22, yaw=-14)
# 蓄：刃举到右高位、身体侧向拧转
K("shoR", 26, side=118, fwd=-18); K("elbR", 26, fwd=22); K("handR", 26, twist=28)
K("chest", 26, twist=-20)
stance(26, crouch=26, spread=24, dy=0.06, yaw=-26)
K("shoR", 30, side=126, fwd=-18); K("elbR", 30, fwd=18)
K("chest", 30, twist=-22)
stance(30, crouch=28, spread=24, dy=0.06, yaw=-28)
# 中段：折肘让刃收到身前，越过正下方（防穿地）
K("shoR", 36, side=40, fwd=8); K("elbR", 36, fwd=95); K("handR", 36, twist=0)
K("chest", 36, twist=0)
stance(36, crouch=22, spread=24, dy=0.0, yaw=-4)
# 爆：手臂甩开、刃斜贯到左下方
K("shoR", 40, side=-58, fwd=26); K("elbR", 40, fwd=6); K("handR", 40, twist=-25)
K("chest", 40, twist=20, side=-10)
stance(40, crouch=18, spread=24, dy=-0.12, yaw=10)
# 过冲：再甩过目标位
K("shoR", 45, side=-80, fwd=30); K("elbR", 45, fwd=-4); K("handR", 45, twist=-40)
K("chest", 45, twist=30, side=-14)
stance(45, crouch=16, spread=24, dy=-0.14, yaw=16)
# 收：向下向身后收回
K("shoR", 58, side=-40, fwd=4); K("elbR", 58, fwd=55)
K("chest", 58, twist=10)
stance(58, crouch=20, spread=23, yaw=4)
# 定：刃收于体侧后方（肘折起把刃放平）
K("shoR", 70, side=20, fwd=-12); K("elbR", 70, fwd=88); K("handR", 70, twist=20)
K("chest", 70, twist=-8)
stance(70, crouch=22, spread=22, yaw=-14)
breathing(72, -6)
audit("03 横扫收剑", True)
render_clip("白膜-03-横扫收剑")

# ================================================================ 04 抽剑递剑（拧身藏剑腰后 → 抽出直递镜头）
reset_pose()
sword.hide_render = False
# 起势：拧身，右臂垂在体后、肘折 120° 使刃朝上后方（背剑式，天然不触地）
K("shoR", 1, side=8, fwd=-20); K("elbR", 1, fwd=-120); K("handR", 1, twist=30)
K("shoL", 1, side=-26, fwd=8); K("elbL", 1, fwd=40)
K("chest", 1, twist=12)
stance(1, crouch=22, spread=22, yaw=16)
# 蓄：手再往后拉、刃完全藏到身后、重心后坐
K("shoR", 24, side=10, fwd=-26); K("elbR", 24, fwd=-132); K("handR", 24, twist=36)
K("chest", 24, twist=18)
stance(24, crouch=30, spread=24, dy=0.10, yaw=24)
K("shoR", 29, side=10, fwd=-28); K("elbR", 29, fwd=-136)
K("chest", 29, twist=20)
stance(29, crouch=32, spread=24, dy=0.11, yaw=26)
# 中段：肩先送出去、肘仍折着 —— 刃从"背后朝上"转到"身前朝上"，全程不过地面
# 过渡（关键）：刃朝向 ≈ 肩角+肘角，让两者之和从 -164° 连续降到 -264°，
# 全程经过"正上方"而不穿过地面 —— 肘角连续展开到 -360°（视觉上仍是直臂）。
K("shoR", 34, side=10, fwd=10); K("elbR", 34, fwd=-205)
K("chest", 34, twist=4, fwd=6)
stance(34, crouch=26, spread=23, dy=0.04, yaw=10)
K("shoR", 37, side=10, fwd=60); K("elbR", 37, fwd=-280)
stance(37, crouch=22, spread=23, dy=0.0, yaw=8)
# 爆：肩送到最前、刃前指到镜头（sum -264 ≈ 前方水平）
K("shoR", 40, side=10, fwd=96); K("elbR", 40, fwd=-360)
K("handR", 40, twist=-10, fwd=12)
K("chest", 40, twist=-12, fwd=18)
stance(40, crouch=18, spread=23, dy=-0.20, yaw=-6)
# 过冲：再多递一点
K("shoR", 45, side=6, fwd=108); K("elbR", 45, fwd=-364)
K("chest", 45, twist=-16, fwd=24)
stance(45, crouch=16, spread=23, dy=-0.22, yaw=-10)
# 收：翻腕、手向下压
K("handR", 54, twist=-140, fwd=10)
K("shoR", 56, side=8, fwd=58); K("elbR", 56, fwd=-330)
K("chest", 56, fwd=2, twist=4)
stance(56, crouch=20, spread=22, yaw=0)
# 定：剑尖下压体前（sum ≈ -300，前下方 30°）
K("shoR", 68, side=12, fwd=26); K("elbR", 68, fwd=-326)
K("handR", 68, twist=-120, fwd=-14)
K("chest", 68, fwd=-8)
stance(68, crouch=20, spread=21, yaw=-4)
breathing(70, -8)
audit("04 抽剑递剑", True)
render_clip("白膜-04-抽剑递剑")

# ---------------------------------------------------------------- 收尾
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "白膜动作.blend"))
with open(os.path.join(OUT_DIR, "_DONE.txt"), "w", encoding="utf-8") as fh:
    fh.write("4 clips rendered (v4 large amplitude)\n")
print("ALL-DONE")
