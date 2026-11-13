"""3D Short (Blender/Cycles): 'I Woke Up With Four Arms' — 1080x1920, 24 fps, ~40 s.
Semi-realistic procedural character 'Max' (messy orange hair, teal tee). Captions composited with cairo."""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
FPS = 24
PER_JOB = 1
RX, RY = 720, 1280
SAMPLES = int(os.environ.get('SAMPLES', 16))

SHOTS = [  # seconds, narration/caption, set
    (3.4, "I woke up this morning with four arms.", 'bed'),
    (3.6, "At first, I panicked. Then I got curious.", 'bedclose'),
    (4.0, "Breakfast? Two pans, four eggs, zero problems.", 'kitchen'),
    (4.4, "I typed with two hands and drank coffee with the other two.", 'desk'),
    (3.4, "At the gym, I lifted twice the weight.", 'gym'),
    (3.2, "Juggling? Way too easy.", 'juggle'),
    (3.6, "I played drums like an entire band.", 'drums'),
    (4.2, "Life was perfect. Until I tried to put on a shirt.", 'shirt'),
    (3.4, "That night, I fell asleep smiling.", 'night'),
    (4.6, "Then I woke up… with six.", 'six'),
]
SCENES = SHOTS
STARTS = [sum(s[0] for s in SHOTS[:i]) for i in range(len(SHOTS))]
TOTAL = sum(s[0] for s in SHOTS)
F = lambda sec: int(round(sec * FPS)) + 1
SETX = dict(bed=0, bedclose=0, night=0, six=0, kitchen=20, desk=40, gym=60, juggle=80, drums=100, shirt=120)

def build():
    import bpy
    R = math.radians
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True; sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = RX, RY; sc.render.fps = FPS
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.03, 0.035, 0.05, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.5

    def mat(name, col, rough=0.6, emit=None, estr=0.0, metal=0.0, sss=0.0):
        m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
        if sss:
            try:
                b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (0.9, 0.4, 0.25)
                b.inputs['Subsurface Scale'].default_value = 0.02
            except KeyError: pass
        if emit is not None:
            b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
        return m
    M = dict(skin=mat('skin', (0.82, 0.5, 0.36), 0.45, sss=0.25), shirt=mat('shirt', (0.03, 0.42, 0.45), 0.8),
             jeans=mat('jeans', (0.1, 0.15, 0.3), 0.85), shoe=mat('shoe', (0.9, 0.9, 0.9), 0.5), hair=mat('hair', (0.7, 0.22, 0.04), 0.55),
             eye=mat('eye', (0.95, 0.95, 0.95), 0.1), iris=mat('iris', (0.15, 0.45, 0.25), 0.1), pupil=mat('pupil', (0.01, 0.01, 0.01), 0.05),
             mouth=mat('mouth', (0.18, 0.03, 0.03), 0.4), wood=mat('wood', (0.35, 0.2, 0.1), 0.55), white=mat('white', (0.85, 0.85, 0.82), 0.7),
             dark=mat('dark', (0.04, 0.04, 0.05), 0.4), metal=mat('metal', (0.75, 0.75, 0.78), 0.25, metal=1.0), red=mat('red', (0.8, 0.1, 0.08), 0.4),
             blanket=mat('blanket', (0.55, 0.12, 0.12), 0.9), wall=mat('wall', (0.55, 0.56, 0.6), 0.9), floor=mat('floor', (0.32, 0.22, 0.14), 0.5),
             screen=mat('screen', (0.2, 0.4, 0.9), 0.2, (0.4, 0.65, 1.0), 4.0), led=mat('led', (1, 0.1, 0.1), 0.4, (1, 0.1, 0.05), 12.0),
             gold=mat('gold', (0.9, 0.7, 0.25), 0.25, metal=1.0), grass=mat('grass', (0.15, 0.4, 0.12), 0.9),
             sky=mat('sky', (0.4, 0.6, 0.9), 0.9, (0.45, 0.65, 1.0), 1.2), mirror=mat('mirror', (0.95, 0.95, 0.97), 0.02, metal=1.0),
             egg=mat('egg', (0.98, 0.98, 0.95), 0.4), yolk=mat('yolk', (1, 0.65, 0.05), 0.3), drum=mat('drum', (0.7, 0.05, 0.1), 0.3),
             skinhead=mat('drumhead', (0.92, 0.9, 0.85), 0.6))

    def prim(kind, loc=(0, 0, 0), scale=(1, 1, 1), m=None, parent=None, rot=(0, 0, 0), sub=1, smooth=True, **kw):
        ops = dict(cube=bpy.ops.mesh.primitive_cube_add, sphere=bpy.ops.mesh.primitive_uv_sphere_add,
                   cyl=bpy.ops.mesh.primitive_cylinder_add, cone=bpy.ops.mesh.primitive_cone_add, torus=bpy.ops.mesh.primitive_torus_add)
        if kind == 'sphere': kw.setdefault('segments', 24); kw.setdefault('ring_count', 12)
        if kind == 'cyl': kw.setdefault('vertices', 20)
        ops[kind](location=loc, rotation=rot, **kw)
        o = bpy.context.object; o.scale = scale
        if m: o.data.materials.append(m)
        if parent: o.parent = parent
        if sub and kind == 'cube':
            md = o.modifiers.new('s', 'SUBSURF'); md.levels = sub; md.render_levels = sub
        if smooth: bpy.ops.object.shade_smooth()
        return o

    def empty(name, parent=None, loc=(0, 0, 0)):
        e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.parent = parent; e.location = loc
        e.rotation_mode = 'XYZ'; return e

    def key(o, f, rot=None, loc=None, scale=None):
        if rot is not None: o.rotation_euler = [R(v) for v in rot]; o.keyframe_insert('rotation_euler', frame=f)
        if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
        if scale is not None: o.scale = scale if isinstance(scale, tuple) else (scale,) * 3; o.keyframe_insert('scale', frame=f)

    # ---------------------------------------------------------------- character 'Max'
    C = {}
    root = empty('max'); C['root'] = root
    hips = empty('hips', root, (0, 0, 0.95)); C['hips'] = hips
    prim('cube', (0, 0, 0.03), (0.18, 0.115, 0.1), M['jeans'], hips)
    spine = empty('spine', hips, (0, 0, 0.08)); C['spine'] = spine
    torso = prim('cube', (0, 0, 0.29), (0.2, 0.12, 0.3), M['shirt'], spine, sub=0)
    bv = torso.modifiers.new('bv', 'BEVEL'); bv.width = 0.12; bv.segments = 6
    md = torso.modifiers.new('s', 'SUBSURF'); md.levels = 1; md.render_levels = 1
    neck = empty('neck', spine, (0, 0, 0.56)); C['neck'] = neck
    prim('cyl', (0, 0, 0.06), (0.048, 0.048, 0.14), M['skin'], neck, radius=1, depth=1)
    head = empty('head', neck, (0, 0, 0.2)); C['head'] = head
    prim('sphere', (0, 0, 0), (0.105, 0.115, 0.13), M['skin'], head, radius=1)
    prim('sphere', (0, -0.012, -0.08), (0.08, 0.085, 0.06), M['skin'], head, radius=1)   # jaw
    prim('sphere', (0, -0.113, -0.005), (0.016, 0.022, 0.03), M['skin'], head, radius=1)  # nose
    for sx in (-1, 1):
        prim('sphere', (sx * 0.103, 0.01, 0.0), (0.012, 0.025, 0.035), M['skin'], head, radius=1)   # ears
    # messy hair: cap + tufts
    prim('sphere', (0, 0.012, 0.035), (0.112, 0.122, 0.115), M['hair'], head, radius=1)
    import random as _r
    rnd = _r.Random(5)
    for k in range(14):
        an = rnd.uniform(-2.6, 2.6); el = rnd.uniform(0.2, 1.2)
        x, y, z = 0.1 * math.sin(an) * math.cos(el * 0.6), 0.1 * math.cos(an) * math.cos(el * 0.6) + 0.02, 0.06 + 0.07 * math.sin(el)
        prim('cone', (x, y, z), (0.03, 0.03, 0.07), M['hair'], head, rot=(R(rnd.uniform(-50, 50)), R(rnd.uniform(-50, 50)), 0), radius1=1, depth=1, vertices=8)
    C['eyes'] = []
    for sx in (-1, 1):
        e = empty(f'eye{sx}', head, (sx * 0.042, -0.092, 0.018)); C[f'eye{sx}'] = e
        prim('sphere', (0, 0, 0), (0.026,) * 3, M['eye'], e, radius=1)
        ir = empty(f'iris{sx}', e, (0, -0.02, 0)); C[f'iris{sx}'] = ir
        prim('sphere', (0, 0, 0), (0.014, 0.008, 0.014), M['iris'], ir, radius=1)
        prim('sphere', (0, -0.005, 0), (0.007, 0.005, 0.007), M['pupil'], ir, radius=1)
        lid = empty(f'lid{sx}', e); C[f'lid{sx}'] = lid
        prim('sphere', (0, 0, 0), (0.029,) * 3, M['skin'], lid, radius=1, segments=24, ring_count=12)
        # lid: half sphere via scale trick -> we rotate a squashed sphere above the eye
        b = empty(f'brow{sx}', head, (sx * 0.044, -0.1, 0.06)); C[f'brow{sx}'] = b
        prim('cube', (0, 0, 0), (0.026, 0.006, 0.006), M['hair'], b, sub=1)
    mo = empty('mouth', head, (0, -0.1, -0.06)); C['mouth'] = mo
    prim('sphere', (0, 0, 0), (0.028, 0.01, 0.008), M['mouth'], mo, radius=1)
    # arms: pairs 0 (top), 1 (middle), 2 (hidden until the end)
    def arm(pair, side):
        z = [0.5, 0.33, 0.17][pair]
        sh = empty(f'sh{pair}{side}', spine, (side * 0.2, 0, z)); C[f'sh{pair}{side}'] = sh
        prim('sphere', (0, 0, 0), (0.055,) * 3, M['shirt'], sh, radius=1)
        prim('cyl', (0, 0, -0.07), (0.05, 0.05, 0.14), M['shirt'], sh, radius=1, depth=1)
        prim('cyl', (0, 0, -0.2), (0.038, 0.038, 0.16), M['skin'], sh, radius=1, depth=1)
        el = empty(f'el{pair}{side}', sh, (0, 0, -0.28)); C[f'el{pair}{side}'] = el
        prim('sphere', (0, 0, 0), (0.037,) * 3, M['skin'], el, radius=1)
        prim('cyl', (0, 0, -0.12), (0.033, 0.033, 0.24), M['skin'], el, radius=1, depth=1)
        wr = empty(f'wr{pair}{side}', el, (0, 0, -0.25)); C[f'wr{pair}{side}'] = wr
        prim('sphere', (0, 0, -0.045), (0.033, 0.018, 0.05), M['skin'], wr, radius=1)
        prim('sphere', (side * -0.03, -0.012, -0.03), (0.01, 0.01, 0.025), M['skin'], wr, radius=1, rot=(0, R(side * 30), 0))
        return sh
    for pair in (0, 1, 2):
        for side in (-1, 1): arm(pair, side)
    for side in (-1, 1):
        hp = empty(f'hip{side}', hips, (side * 0.09, 0, 0)); C[f'hip{side}'] = hp
        prim('cyl', (0, 0, -0.22), (0.07, 0.07, 0.46), M['jeans'], hp, radius=1, depth=1)
        kn = empty(f'kn{side}', hp, (0, 0, -0.45)); C[f'kn{side}'] = kn
        prim('cyl', (0, 0, -0.22), (0.055, 0.055, 0.44), M['jeans'], kn, radius=1, depth=1)
        an = empty(f'an{side}', kn, (0, 0, -0.45)); C[f'an{side}'] = an
        prim('cube', (0, -0.05, -0.03), (0.05, 0.11, 0.04), M['shoe'], an, sub=1)

    def face(f, fear=0.0, smile=0.0, blink=0.0, look=(0, 0)):
        for sx in (-1, 1):
            key(C[f'eye{sx}'], f, scale=1 + 0.25 * fear)
            key(C[f'iris{sx}'], f, loc=(look[0] * 0.01, -0.02, look[1] * 0.008))
            # lid sits above eye; blink moves it down over the eye
            key(C[f'lid{sx}'], f, loc=(0, -0.001, 0), scale=(1.0 if blink > 0.5 else 0.0001))
            key(C[f'brow{sx}'], f, loc=(sx * 0.044, -0.1, 0.06 + 0.018 * fear - 0.004 * smile), rot=(0, sx * (-15 * fear + 8 * smile), 0))
        key(C['mouth'], f, scale=(1 + 0.4 * smile - 0.3 * fear, 1, 1 + 3.5 * fear + 0.6 * smile))

    def arms(f, P):
        """P: dict pair/side -> (shoulder rot, elbow rot)."""
        for (pair, side), (s, e) in P.items():
            key(C[f'sh{pair}{side}'], f, rot=s); key(C[f'el{pair}{side}'], f, rot=e)

    REST = {(p, s): ((0, s * (-12 - 6 * p), 0), (-10, 0, 0)) for p in (0, 1, 2) for s in (-1, 1)}
    def legs_stand(f):
        key(C['hips'], f, loc=(0, 0, 0.95))
        for s in (-1, 1): key(C[f'hip{s}'], f, rot=(0, 0, 0)); key(C[f'kn{s}'], f, rot=(0, 0, 0)); key(C[f'an{s}'], f, rot=(0, 0, 0))
    def legs_sit(f):
        key(C['hips'], f, loc=(0, 0, 0.5))
        for s in (-1, 1): key(C[f'hip{s}'], f, rot=(-90, 0, s * -4)); key(C[f'kn{s}'], f, rot=(90, 0, 0)); key(C[f'an{s}'], f, rot=(0, 0, 0))
    def legs_bed(f):
        key(C['hips'], f, loc=(0, 0, 0.55))
        for s in (-1, 1): key(C[f'hip{s}'], f, rot=(-90, 0, 0)); key(C[f'kn{s}'], f, rot=(0, 0, 0)); key(C[f'an{s}'], f, rot=(0, 0, 0))

    # ---------------------------------------------------------------- sets
    def light(kind, loc, energy, color, rot=(0, 0, 0), size=1.0):
        bpy.ops.object.light_add(type=kind, location=loc, rotation=[R(v) for v in rot]); L = bpy.context.object
        L.data.energy = energy; L.data.color = color
        if kind == 'AREA': L.data.size = size
        else: L.data.shadow_soft_size = size * 0.3
        return L
    def room(x0, wallcol=None):
        prim('cube', (x0, 0, -0.05), (4, 4, 0.05), M['floor'], sub=0, smooth=False)
        prim('cube', (x0, 2.5, 1.5), (4, 0.05, 1.5), wallcol or M['wall'], sub=0, smooth=False)
        prim('cube', (x0 - 3, 0, 1.5), (0.05, 4, 1.5), wallcol or M['wall'], sub=0, smooth=False)
    # bedroom (x=0)
    room(0)
    prim('cube', (0, 0.9, 0.25), (0.75, 1.1, 0.2), M['white'], sub=1)            # mattress
    prim('cube', (0, 2.0, 0.6), (0.8, 0.06, 0.55), M['wood'], sub=1)             # headboard
    prim('cube', (0, 1.75, 0.5), (0.45, 0.2, 0.08), M['white'], sub=2)           # pillow
    blanket = prim('cube', (0, 0.3, 0.66), (0.78, 0.75, 0.08), M['blanket'], sub=2)
    prim('cube', (1.25, 1.6, 0.3), (0.25, 0.25, 0.3), M['wood'], sub=1)
    clock = prim('cube', (1.25, 1.55, 0.7), (0.12, 0.05, 0.07), M['dark'], sub=1)
    bpy.ops.object.text_add(location=(1.25, 1.49, 0.68), rotation=(R(90), 0, 0)); t = bpy.context.object; t.data.body = '7:00'
    t.data.align_x = 'CENTER'; t.data.size = 0.07; t.data.materials.append(M['led'])
    prim('cube', (-2.97, 0.6, 1.6), (0.02, 0.7, 0.6), mat('win', (0.9, 0.8, 0.6), 0.2, (1, 0.85, 0.6), 3.0), sub=0)
    sun_bed = light('AREA', (-2.6, 0.6, 1.8), 420, (1, 0.82, 0.6), rot=(0, -80, 0), size=1.5)
    fill_bed = light('AREA', (1.5, -2.5, 2.5), 120, (0.7, 0.8, 1), rot=(60, 0, 30), size=3)
    moon_bed = light('AREA', (-2.6, 0.6, 1.8), 0, (0.4, 0.55, 1.0), rot=(0, -80, 0), size=1.5)
    # kitchen (x=20)
    room(20)
    prim('cube', (20, 0.9, 0.45), (1.3, 0.35, 0.45), M['white'], sub=1)
    prim('cube', (20, 0.9, 0.92), (1.35, 0.38, 0.03), mat('counter', (0.15, 0.15, 0.17), 0.3), sub=1)
    light('AREA', (20, -1.2, 2.6), 380, (1, 0.9, 0.78), rot=(50, 0, 0), size=2.5)
    light('POINT', (21.5, 1.0, 2.0), 60, (1, 0.7, 0.4), size=1)
    # desk (x=40)
    room(40)
    prim('cube', (40, 0.75, 0.74), (0.8, 0.4, 0.03), M['wood'], sub=1)
    for sx in (-1, 1): prim('cube', (40 + sx * 0.75, 0.75, 0.37), (0.03, 0.35, 0.37), M['wood'], sub=0)
    prim('cube', (40, 0.62, 0.785), (0.22, 0.15, 0.008), M['metal'], sub=0)
    scr = prim('cube', (40, 0.78, 0.93), (0.22, 0.008, 0.14), M['dark'], sub=0, rot=(R(-12), 0, 0))
    prim('cube', (40, 0.772, 0.93), (0.2, 0.004, 0.125), M['screen'], sub=0, rot=(R(-12), 0, 0))
    light('AREA', (40, -1.5, 2.4), 300, (0.95, 0.92, 1), rot=(55, 0, 0), size=2.5)
    light('POINT', (40, 0.6, 1.0), 25, (0.4, 0.6, 1), size=0.5)
    # gym (x=60)
    room(60, mat('gymwall', (0.15, 0.16, 0.18), 0.8))
    prim('cube', (60, 2.3, 1.2), (2.5, 0.05, 0.05), M['metal'], sub=0)
    light('SPOT', (60, -0.5, 3.2), 900, (1, 0.95, 0.9), rot=(10, 0, 0), size=1)
    light('AREA', (61.5, -2, 2), 120, (0.5, 0.7, 1), rot=(60, 0, 40), size=2)
    # juggling park (x=80)
    prim('cube', (80, 0, -0.05), (8, 8, 0.05), M['grass'], sub=0, smooth=False)
    prim('cube', (80, 5, 3), (10, 0.05, 4), M['sky'], sub=0, smooth=False)
    for k in range(5):
        prim('sphere', (76 + k * 2.2, 4.0, 0.6 + (k % 2) * 0.3), (0.7, 0.5, 0.8), M['grass'], radius=1)
    light('SUN', (80, 0, 5), 4.0, (1, 0.95, 0.85), rot=(40, 10, 30))
    # drums (x=100)
    room(100, mat('stage', (0.08, 0.06, 0.1), 0.8))
    prim('cyl', (100, 0.9, 0.35), (0.35, 0.35, 0.3), M['drum'], radius=1, depth=1, rot=(R(90), 0, 0))     # kick
    prim('cyl', (100, 0.62, 0.35), (0.33, 0.33, 0.02), M['skinhead'], radius=1, depth=1, rot=(R(90), 0, 0))
    for (dx, dz, r) in ((-0.32, 0.72, 0.15), (0.32, 0.72, 0.15), (-0.15, 0.88, 0.12), (0.15, 0.88, 0.12)):
        prim('cyl', (100 + dx, 0.45, dz), (r, r, 0.08), M['drum'], radius=1, depth=1, rot=(R(-20), 0, 0))
        prim('cyl', (100 + dx, 0.45, dz + 0.045), (r * 0.95, r * 0.95, 0.005), M['skinhead'], radius=1, depth=1, rot=(R(-20), 0, 0))
    for dx in (-0.65, 0.65):
        prim('cyl', (100 + dx, 0.6, 1.25), (0.22, 0.22, 0.006), M['gold'], radius=1, depth=1, rot=(R(-15), 0, 0))
        prim('cyl', (100 + dx, 0.6, 0.62), (0.01, 0.01, 1.25), M['metal'], radius=1, depth=1)
    prim('cyl', (100, -0.25, 0.25), (0.18, 0.18, 0.5), M['dark'], radius=1, depth=1)   # stool
    stage_spots = [light('SPOT', (100 + dx, -1.2, 3.0), 500, c, rot=(30, dx * 8, 0), size=0.5)
                   for dx, c in ((-1.2, (1, 0.25, 0.5)), (1.2, (0.25, 0.5, 1)), (0, (1, 0.9, 0.7)))]
    # shirt / mirror (x=120)
    room(120)
    prim('cube', (120, 1.6, 1.2), (0.55, 0.03, 0.9), M['wood'], sub=0)
    prim('cube', (120, 1.565, 1.2), (0.5, 0.005, 0.85), M['mirror'], sub=0)
    light('AREA', (120, -1.5, 2.6), 380, (1, 0.93, 0.85), rot=(50, 0, 0), size=2.5)
    light('POINT', (121.2, 0.4, 1.8), 60, (1, 0.75, 0.5), size=1)

    # ---------------------------------------------------------------- props attached to hands
    def attach(obj, wrist_name, loc=(0, 0, -0.07), rot=(0, 0, 0)):
        obj.parent = C[wrist_name]; obj.location = loc; obj.rotation_euler = [R(v) for v in rot]; return obj
    pans = []
    for side in (-1, 1):
        p = prim('cyl', (0, 0, 0), (0.13, 0.13, 0.02), M['dark'], radius=1, depth=1); attach(p, f'wr0{side}', (0, -0.18, -0.08), (90, 0, 0))
        h = prim('cyl', (0, 0, 0), (0.015, 0.015, 0.16), M['dark'], radius=1, depth=1); attach(h, f'wr0{side}', (0, -0.05, -0.08), (90, 0, 0))
        e = prim('sphere', (0, 0, 0), (0.06, 0.06, 0.012), M['egg'], radius=1); attach(e, f'wr0{side}', (0, -0.2, -0.105))
        yk = prim('sphere', (0, 0, 0), (0.025, 0.025, 0.012), M['yolk'], radius=1); attach(yk, f'wr0{side}', (0, -0.2, -0.115))
        pans += [p, h, e, yk]
    eggs = []
    for side in (-1, 1):
        eg = prim('sphere', (0, 0, 0), (0.025, 0.025, 0.033), M['egg'], radius=1); attach(eg, f'wr1{side}', (0, -0.02, -0.08)); eggs.append(eg)
    mug = prim('cyl', (0, 0, 0), (0.04, 0.04, 0.05), M['white'], radius=1, depth=1); attach(mug, 'wr01', (0, -0.04, -0.08))
    bells = []
    for pair in (0, 1):
        for side in (-1, 1):
            bar = prim('cyl', (0, 0, 0), (0.012, 0.012, 0.18), M['metal'], radius=1, depth=1); attach(bar, f'wr{pair}{side}', (0, -0.02, -0.08), (0, 90, 0))
            for d in (-0.09, 0.09):
                wgt = prim('cyl', (0, 0, 0), (0.05, 0.05, 0.04), M['dark'], radius=1, depth=1); attach(wgt, f'wr{pair}{side}', (d, -0.02, -0.08), (0, 90, 0))
                bells.append(wgt)
            bells.append(bar)
    sticks = []
    for pair in (0, 1):
        for side in (-1, 1):
            st = prim('cyl', (0, 0, 0), (0.008, 0.008, 0.38), M['wood'], radius=1, depth=1); attach(st, f'wr{pair}{side}', (0, -0.15, -0.08), (75, 0, 0))
            sticks.append(st)
    balls = [prim('sphere', (80, 0, 0), (0.06,) * 3, m, radius=1) for m in (M['red'], mat('b2', (0.1, 0.4, 0.9), 0.3), mat('b3', (1, 0.8, 0.1), 0.3), mat('b4', (0.2, 0.8, 0.3), 0.3))]
    shirt = prim('cube', (0, 0, 0), (0.22, 0.15, 0.2), mat('shirt2', (0.9, 0.85, 0.2), 0.85), C['head'], sub=2); shirt.location = (0, 0, 0.0)
    phone_like = None

    def visible(objs, frames_on):
        """Show objects only during given (f0, f1) ranges by scaling."""
        for o in objs:
            base = tuple(o.scale)
            key(o, 1, scale=(0.0001,) * 3)
            for f0, f1 in frames_on:
                key(o, f0 - 1, scale=(0.0001,) * 3); key(o, f0, scale=base); key(o, f1, scale=base); key(o, f1 + 1, scale=(0.0001,) * 3)

    S = [F(s) for s in STARTS] + [F(TOTAL)]
    rng = lambda i: (S[i], S[i + 1] - 1)
    # third pair of arms hidden until the last shot
    for side in (-1, 1):
        key(C[f'sh2{side}'], 1, scale=0.0001); key(C[f'sh2{side}'], S[9] + 14, scale=0.0001)
        key(C[f'sh2{side}'], S[9] + 22, scale=1.15); key(C[f'sh2{side}'], S[9] + 28, scale=1.0)
    visible(pans + eggs, [rng(2)]); visible([mug], [rng(3)]); visible(bells, [rng(4)]); visible(sticks, [rng(6)])
    visible([shirt], [rng(7)]); visible(balls, [rng(5)])

    def place(i, loc, rot=(0, 0, 0)):
        f0, f1 = rng(i)
        key(root, f0, loc=loc, rot=rot); key(root, f1, loc=loc, rot=rot)

    # ---------------- animation per shot
    def cyc(i, step=2):
        f0, f1 = rng(i)
        for f in range(f0, f1 + 1, step): yield f, (f - f0) / FPS

    # 0 bed: sitting up in bed, yawns, stretches four arms up
    place(0, (0, 0.95, 0.0))
    for f, t in cyc(0):
        k = min(1, max(0, (t - 0.8) / 1.0))
        legs_bed(f); key(C['spine'], f, rot=(-10 + 10 * k, 0, 0)); key(C['head'], f, rot=(-15 + 25 * k, 0, 0))
        up = {(p, s): ((0, s * (-12 - 150 * k + 8 * p), 0), (-10 - 20 * (1 - k), 0, 0)) for p in (0, 1) for s in (-1, 1)}
        arms(f, {**REST, **up}); face(f, fear=0, smile=0.2 * k, blink=max(0, 1 - t * 1.2), look=(0, 0.5 * k))
    # 1 close-up panic -> curious
    place(1, (0, 0.95, 0.0))
    for f, t in cyc(1):
        legs_bed(f); panic = 1 if t < 1.8 else max(0, 1 - (t - 1.8) * 2)
        P = {}
        for p in (0, 1):
            for s in (-1, 1):
                wob = math.sin(t * 18 + p * 2 + s) * 35 * panic
                P[(p, s)] = ((-60 * panic + wob, s * (-40 - 30 * p) + wob * 0.5, 0), (-60 * panic - 20 * (1 - panic), 0, 0))
        if panic < 0.5:
            P[(1, 1)] = ((-70, -20, 0), (-90, 0, 0)); P[(0, 1)] = ((-40, -50, 0), (-60, 0, 0))
        arms(f, {**REST, **P}); key(C['head'], f, rot=(8 * math.sin(t * 9) * panic, 0, 20 * math.sin(t * 6) * panic + 18 * (1 - panic)))
        face(f, fear=panic, smile=0.6 * (1 - panic), look=(math.sin(t * 7), -0.3))
    # 2 kitchen: two pans shaking, lower hands cracking eggs
    place(2, (20, 0.25, 0.0))
    for f, t in cyc(2):
        legs_stand(f); key(C['spine'], f, rot=(8, 0, 0)); key(C['head'], f, rot=(15, 0, 8 * math.sin(t * 2)))
        sh = 12 * math.sin(t * 14)
        P = {(0, -1): ((-60 + sh, 10, 0), (-30, 0, 0)), (0, 1): ((-60 - sh, -10, 0), (-30, 0, 0)),
             (1, -1): ((-45, 5, 0), (-60 + 25 * math.sin(t * 8), 0, 0)), (1, 1): ((-45, -5, 0), (-60 + 25 * math.sin(t * 8 + 1.5), 0, 0))}
        arms(f, {**REST, **P}); face(f, smile=0.8, look=(0, 0.8), blink=1 if (t % 2.2) < 0.08 else 0)
    # 3 desk: lower hands typing, upper right drinks coffee, upper left waves mouse
    place(3, (40, 0.25, 0.0))
    for f, t in cyc(3):
        legs_sit(f); key(C['hips'], f, loc=(0, 0, 0.5)); key(C['spine'], f, rot=(5, 0, 0))
        drink = max(0, math.sin(t * 1.6)) ** 2
        P = {(1, -1): ((-70 + 4 * math.sin(t * 30), 8, 0), (-30, 0, 0)), (1, 1): ((-70 + 4 * math.sin(t * 30 + 1), -8, 0), (-30, 0, 0)),
             (0, 1): ((-40 - 30 * drink, -20 + 10 * drink, 0), (-110 * drink - 20, 0, 0)), (0, -1): ((-50, 25, 0), (-40 + 10 * math.sin(t * 3), 0, 0))}
        arms(f, {**REST, **P}); key(C['head'], f, rot=(10 - 15 * drink, 0, 0)); face(f, smile=0.5, look=(0, 0.6 * (1 - drink)))
    for f in range(S[4] - 1, S[4] + 1): key(C['hips'], f, loc=(0, 0, 0.95))
    key(C['hips'], S[3] - 1, loc=(0, 0, 0.95))
    # 4 gym: alternating curls
    place(4, (60, 0, 0.0))
    for f, t in cyc(4):
        legs_stand(f); key(C['spine'], f, rot=(0, 0, 0))
        P = {(p, s): ((0, s * (-15 - 5 * p), 0), (-20 - 110 * max(0, math.sin(t * 5 + p * math.pi / 2 + (s > 0) * math.pi)), 0, 0)) for p in (0, 1) for s in (-1, 1)}
        arms(f, {**REST, **P}); face(f, fear=0.2, smile=0.6 + 0.3 * math.sin(t * 5), look=(0, 0))
        key(C['head'], f, rot=(0, 0, 5 * math.sin(t * 5)))
    # 5 juggling: balls on arcs in front of chest
    place(5, (80, 0, 0.0))
    f0, f1 = rng(5)
    for f, t in cyc(5, 1):
        legs_stand(f)
        P = {(p, s): ((-55 + 15 * math.sin(t * 9 + p * 1.5 + (s > 0) * 3), s * (-20 - 10 * p), 0), (-50, 0, 0)) for p in (0, 1) for s in (-1, 1)}
        arms(f, {**REST, **P}) if f % 2 == 0 else None
        if f % 2 == 0: face(f, smile=0.9, look=(math.sin(t * 6), -1))
        for k, b in enumerate(balls):
            ph = (t * 1.6 + k / 4) % 1
            x = 80 + 0.28 * math.cos(ph * 2 * math.pi + k); z = 1.35 + 0.55 * math.sin(ph * math.pi) - 0.1 * (k % 2)
            key(b, f, loc=(x, -0.3, z))
    # 6 drums: sitting, four sticks hitting drums
    place(6, (100, -0.25, 0.0))
    for f, t in cyc(6):
        legs_sit(f); key(C['hips'], f, loc=(0, 0, 0.5)); key(C['head'], f, rot=(10 * abs(math.sin(t * 8)), 0, 10 * math.sin(t * 4)))
        P = {(p, s): ((-50 - 30 * abs(math.sin(t * 8 + p * 1.6 + (s > 0) * 0.8)), s * (-25 - 15 * p), 0), (-50, 0, 0)) for p in (0, 1) for s in (-1, 1)}
        arms(f, {**REST, **P}); face(f, smile=1.0, blink=0, look=(0, 0.5))
        for L_ in stage_spots:
            L_.data.energy = 300 + 400 * abs(math.sin(t * 4 + L_.location.x)); L_.data.keyframe_insert('energy', frame=f)
    for f in (S[7] - 1, S[7]): key(C['hips'], f, loc=(0, 0, 0.95))
    key(C['hips'], S[6] - 1, loc=(0, 0, 0.95))
    # 7 shirt: stuck, shirt over head, arms flailing
    place(7, (120, 0.4, 0.0), rot=(0, 0, 180 - 15))
    for f, t in cyc(7):
        legs_stand(f); key(C['spine'], f, rot=(0, 0, 12 * math.sin(t * 6)))
        P = {(0, -1): ((0, 160, 0), (-20, 0, 0)), (0, 1): ((0, -160, 0), (-20, 0, 0)),
             (1, -1): ((-40 + 40 * math.sin(t * 11), 50, 0), (-50, 0, 0)), (1, 1): ((-40 + 40 * math.sin(t * 11 + 2), -50, 0), (-50, 0, 0))}
        arms(f, {**REST, **P}); key(C['head'], f, rot=(0, 15 * math.sin(t * 7), 0)); face(f, fear=0.8, look=(0, 0))
        key(shirt, f, rot=(0, 10 * math.sin(t * 7), 0), loc=(0, 0, 0.02 + 0.02 * math.sin(t * 9)))
    # 8 night: asleep smiling in bed
    place(8, (0, 0.95, 0.0))
    for f, t in cyc(8):
        legs_bed(f); key(C['spine'], f, rot=(-75, 0, 0)); key(C['head'], f, rot=(-10, 0, 20))
        P = {(p, s): ((0, s * (-15), 0), (-5, 0, 0)) for p in (0, 1) for s in (-1, 1)}
        P[(0, 1)] = ((-150, -20, 0), (-90, 0, 0))
        arms(f, {**REST, **P}); face(f, smile=0.9, blink=1)
    for L_, e0, e1 in ((sun_bed, 420, 0), (moon_bed, 0, 260), (fill_bed, 120, 30)):
        for i in range(10):
            f0, f1 = rng(i); en = e1 if i == 8 else e0
            L_.data.energy = en; L_.data.keyframe_insert('energy', frame=f0); L_.data.keyframe_insert('energy', frame=f1)
    # 9 six arms reveal
    place(9, (0, 0.95, 0.0))
    for f, t in cyc(9):
        k = min(1, max(0, (t - 0.9) / 0.6))
        legs_bed(f); key(C['spine'], f, rot=(-10, 0, 0)); key(C['head'], f, rot=(0, 0, 25 * math.sin(t * 5) * k))
        P = {(p, s): ((-30 * k + 20 * math.sin(t * 10 + p) * k, s * (-40 - 25 * p) * k + s * -12 * (1 - k), 0), (-40 * k, 0, 0)) for p in (0, 1, 2) for s in (-1, 1)}
        arms(f, P); face(f, fear=k, look=(math.sin(t * 8) * k, -0.2), blink=max(0, 1 - t * 2))

    # ---------------- cameras
    CAM = {
        0: ((0.9, -0.7, 1.4), (0, 0.95, 1.1), 30, (0.6, -0.4, 1.35)),
        1: ((0.0, -0.1, 1.4), (0, 0.95, 1.38), 40, (0.05, 0.15, 1.38)),
        2: ((20.9, -1.7, 1.75), (20, 0.3, 1.3), 28, (20.5, -1.4, 1.7)),
        3: ((40.7, -0.9, 1.3), (40, 0.3, 1.05), 32, (40.5, -0.6, 1.25)),
        4: ((60.0, -1.6, 1.5), (60, 0, 1.25), 28, (60.3, -1.3, 1.4)),
        5: ((80.4, -1.6, 1.5), (80, 0, 1.45), 30, (79.8, -1.4, 1.5)),
        6: ((100.9, -1.6, 1.6), (100, 0.2, 0.95), 26, (100.4, -1.4, 1.5)),
        7: ((120.9, -0.8, 1.6), (120, 0.8, 1.45), 28, (120.7, -0.6, 1.55)),
        8: ((0.0, -0.5, 2.3), (0, 0.95, 0.8), 30, (0.0, -0.2, 2.1)),
        9: ((0.0, -0.4, 1.3), (0, 0.95, 1.2), 30, (0.0, -0.9, 1.35)),
    }
    for i in range(len(SHOTS)):
        p0, tgt, lens, p1 = CAM[i]
        bpy.ops.object.camera_add(location=p0); c = bpy.context.object; c.name = f'cam{i}'; c.data.lens = lens
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 2.8
        e = empty(f'tgt{i}', None, tgt); tr = c.constraints.new('TRACK_TO'); tr.target = e; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
        c.data.dof.focus_object = e
        key(c, S[i], loc=p0); key(c, S[i + 1] - 1, loc=p1)
    return sc, S

def render_shot(i, outdir):
    import bpy
    os.makedirs(outdir, exist_ok=True)
    sc, S = build()
    f0, f1 = S[i], S[i + 1] - 1
    sc.camera = bpy.data.objects[f'cam{i}']
    tmpdir = f'/tmp/fa_frames_{i:02d}'; os.makedirs(tmpdir, exist_ok=True)
    sc.render.image_settings.file_format = 'PNG'
    for f in range(f0, f1 + 1):
        fp = os.path.join(tmpdir, f'{f:05d}.png')
        if os.path.exists(fp): continue
        sc.frame_set(f); sc.render.filepath = fp
        bpy.ops.render.render(write_still=True)
    composite(i, tmpdir, f0, f1, outdir)

def composite(i, tmpdir, f0, f1, outdir):
    import cairo
    os.environ['FMT'] = ''
    from stick import caption, rgba, ACC, label, clamp, eback, AMB
    W, H = 1080, 1920
    tmp = os.path.join(outdir, f'tmp_{i:02d}.mp4'); final = os.path.join(outdir, f'scene_{i:02d}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    dur, text, _ = SHOTS[i]
    words = [w.strip('.,?!…').upper() for w in text.split()]
    big = 'FOUR' if 'FOUR' in words else ('SIX' if 'SIX' in words else None)
    for f in range(f0, f1 + 1):
        t = (f - f0) / FPS
        src = cairo.ImageSurface.create_from_png(os.path.join(tmpdir, f'{f:05d}.png'))
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        ctx.save(); ctx.scale(W / src.get_width(), H / src.get_height()); ctx.set_source_surface(src); ctx.get_source().set_filter(cairo.FILTER_BEST); ctx.paint(); ctx.restore()
        v = cairo.RadialGradient(W / 2, H * 0.5, 450, W / 2, H * 0.5, 1300)
        v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.45); ctx.set_source(v); ctx.paint()
        if big and t > dur * 0.45:
            k = clamp((t - dur * 0.45) / 0.2)
            ctx.save(); ctx.translate(W / 2, 330); ctx.rotate(-0.06); ctx.scale(0.4 + 0.6 * eback(k), 0.4 + 0.6 * eback(k))
            label(ctx, big + ' ARMS' if big == 'FOUR' else 'SIX?!', 0, 0, 160, ACC if big == 'SIX' else AMB, k); ctx.restore()
        caption(ctx, t, text, 0.12, dur - 0.15, y=1420, size=86, chunk=3)
        g = (STARTS[i] + t) / TOTAL
        ctx.rectangle(0, H - 8, W, 8); rgba(ctx, (1, 1, 1), 0.15); ctx.fill(); ctx.rectangle(0, H - 8, W * g, 8); rgba(ctx, ACC); ctx.fill()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, final)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'count':
        print(len(SHOTS), TOTAL)
    elif mode == 'scenes':
        for i in map(int, sys.argv[3:]): render_shot(i, sys.argv[2])
    elif mode == 'still':
        import bpy
        i = int(sys.argv[2]); t = float(sys.argv[3])
        sc, S = build(); sc.camera = bpy.data.objects[f'cam{i}']
        sc.frame_set(S[i] + int(t * FPS)); sc.render.filepath = sys.argv[4]
        bpy.ops.render.render(write_still=True)
