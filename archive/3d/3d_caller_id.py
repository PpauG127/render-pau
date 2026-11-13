"""3D test Short (Blender): 'Caller ID: Me' — 1080x1920, 24 fps, ~40 s. Shots rendered with Cycles, captions composited with cairo."""
import os, sys, math, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
FPS = 24
PER_JOB = 1
RX, RY = 720, 1280          # render size (upscaled to 1080x1920)
SAMPLES = int(os.environ.get('SAMPLES', 20))

# (seconds, caption, camera key)
SHOTS = [
    (3.8, "My phone rang at 3 AM. The caller ID said… ME.", 'phone'),
    (4.2, "I answered. It was my own voice: Don't open the door.", 'couch'),
    (2.6, "Then someone knocked.", 'door'),
    (3.0, "Knock. Knock. Knock.", 'pov'),
    (4.0, "Whatever happens, the voice said, don't let him in.", 'face'),
    (3.0, "I looked through the peephole.", 'peep'),
    (3.6, "Outside, soaking wet… was me.", 'porch'),
    (3.6, "He mouthed two words: It's. Inside.", 'twin'),
    (5.2, "Then I realized the voice wasn't coming from the phone.", 'behind'),
    (4.4, "It was coming from right behind me.", 'eyes'),
]
SCENES = SHOTS
STARTS = [sum(s[0] for s in SHOTS[:i]) for i in range(len(SHOTS))]
TOTAL = sum(s[0] for s in SHOTS)
F = lambda sec: int(round(sec * FPS)) + 1

def build():
    import bpy
    from mathutils import Vector
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 2
    sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = RX, RY
    sc.render.fps = FPS
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items] else 'None'
    sc.render.film_transparent = False
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.01, 0.015, 0.03, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6

    def mat(name, col, rough=0.6, emit=None, estr=0.0, metal=0.0):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal
        if emit is not None:
            b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
        return m

    def box(name, loc, scale, m, bevel=0.0):
        bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name; o.scale = scale
        o.data.materials.append(m)
        if bevel:
            md = o.modifiers.new('b', 'BEVEL'); md.width = bevel; md.segments = 3
        return o

    M = dict(floor=mat('floor', (0.18, 0.12, 0.08), 0.45), wall=mat('wall', (0.32, 0.34, 0.4), 0.9),
             wood=mat('wood', (0.25, 0.15, 0.08), 0.5), couch=mat('couch', (0.12, 0.16, 0.3), 0.85),
             skin=mat('skin', (0.85, 0.86, 0.9), 0.5), eye=mat('eye', (1, 1, 1), 0.15), pupil=mat('pupil', (0.01, 0.01, 0.01), 0.1),
             screen=mat('screen', (0.1, 0.3, 0.9), 0.2, (0.3, 0.6, 1.0), 6.0), dark=mat('dark', (0.02, 0.02, 0.025), 0.4),
             metal=mat('metal', (0.7, 0.7, 0.72), 0.25, metal=1.0), red=mat('red', (0.9, 0.05, 0.05), 0.4, (1, 0.05, 0.05), 25.0),
             gap=mat('gap', (1, 0.8, 0.5), 0.5, (1, 0.75, 0.45), 12.0), lampshade=mat('shade', (1, 0.8, 0.55), 0.6, (1, 0.7, 0.4), 3.0),
             wet=mat('wet', (0.7, 0.72, 0.78), 0.12), brick=mat('brick', (0.3, 0.12, 0.08), 0.8))

    # ---------------- living room (x: -4..4, y: -4..4)
    box('floor', (0, 0, -0.05), (6, 6, 0.05), M['floor'])
    box('back', (0, 4, 1.5), (6, 0.05, 1.5), M['wall'])
    box('left', (-4, 0, 1.5), (0.05, 6, 1.5), M['wall'])
    box('right', (4, 0, 1.5), (0.05, 6, 1.5), M['wall'])
    # front wall with door opening (door at x=0..1, wall y=-4)
    box('frontL', (-2.5, -4, 1.5), (2, 0.05, 1.5), M['wall']); box('frontR', (3, -4, 1.5), (1.5, 0.05, 1.5), M['wall'])
    box('frontT', (0.5, -4, 2.6), (0.9, 0.05, 0.4), M['wall'])
    door_pivot = bpy.data.objects.new('door_pivot', None); bpy.context.collection.objects.link(door_pivot); door_pivot.location = (-0.4, -4, 0)
    door = box('door', (0.45, 0, 1.1), (0.45, 0.05, 1.1), M['wood'], 0.01); door.parent = door_pivot
    knob = box('knob', (0.82, 0.08, 1.0), (0.04, 0.04, 0.04), M['metal']); knob.parent = door_pivot
    peep = box('peep', (0.45, 0.07, 1.6), (0.025, 0.02, 0.025), M['metal']); peep.parent = door_pivot
    gapo = box('gap', (0.45, -4.02, 0.01), (0.45, 0.02, 0.01), M['gap'])
    # couch + table + phone + lamp
    box('couch_base', (-1.5, 2.6, 0.25), (1.4, 0.6, 0.25), M['couch'], 0.08)
    box('couch_back', (-1.5, 3.15, 0.7), (1.4, 0.15, 0.5), M['couch'], 0.08)
    for sx in (-1, 1): box(f'arm{sx}', (-1.5 + sx * 1.35, 2.6, 0.55), (0.12, 0.6, 0.25), M['couch'], 0.05)
    box('table', (-1.3, 1.2, 0.4), (0.7, 0.45, 0.03), M['wood'], 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1): box('leg', (-1.3 + sx * 0.6, 1.2 + sy * 0.38, 0.2), (0.03, 0.03, 0.2), M['wood'])
    phone = box('phone', (-1.1, 1.1, 0.445), (0.08, 0.16, 0.01), M['dark'], 0.006)
    scr = box('screen', (-1.1, 1.1, 0.456), (0.07, 0.145, 0.002), M['screen'])
    bpy.ops.object.text_add(location=(-1.1, 1.13, 0.46)); txt = bpy.context.object; txt.data.body = 'ME'; txt.data.align_x = 'CENTER'
    txt.data.size = 0.06; txt.data.materials.append(mat('txt', (1, 1, 1), 0.3, (1, 1, 1), 8.0))
    bpy.ops.object.text_add(location=(-1.1, 1.05, 0.46)); t2 = bpy.context.object; t2.data.body = 'calling...'; t2.data.align_x = 'CENTER'
    t2.data.size = 0.025; t2.data.materials.append(mat('txt2', (1, 1, 1), 0.3, (0.8, 0.9, 1), 4.0))
    box('lampbase', (-3.2, 3.2, 0.6), (0.05, 0.05, 0.6), M['metal'])
    bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.2, depth=0.4, location=(-3.2, 3.2, 1.35)); ls = bpy.context.object; ls.data.materials.append(M['lampshade'])
    bpy.ops.object.light_add(type='POINT', location=(-3.2, 3.2, 1.3)); lamp = bpy.context.object.data; lamp.energy = 200; lamp.color = (1, 0.62, 0.35); lamp.shadow_soft_size = 0.2
    lamp_obj = bpy.context.object
    # window with cold moonlight on left wall
    box('window', (-3.97, 0.5, 1.6), (0.02, 0.7, 0.6), mat('win', (0.2, 0.3, 0.5), 0.1, (0.3, 0.45, 0.8), 1.5))
    bpy.ops.object.light_add(type='AREA', location=(-3.6, 0.5, 1.6), rotation=(0, math.radians(90), 0)); a = bpy.context.object.data; a.energy = 260; a.color = (0.45, 0.6, 1.0); a.size = 1.4
    # phone light
    bpy.ops.object.light_add(type='POINT', location=(-1.1, 1.1, 0.6)); pl = bpy.context.object.data; pl.energy = 8; pl.color = (0.4, 0.6, 1); pl.shadow_soft_size = 0.05
    phone_light = bpy.context.object
    bpy.ops.object.light_add(type='POINT', location=(2.6, 3.0, 2.2)); rl = bpy.context.object.data; rl.energy = 40; rl.color = (1, 0.15, 0.1); rl.shadow_soft_size = 0.5
    # hallway (behind couch, dark opening at back wall right)
    box('hall', (2.4, 4.2, 1.2), (0.7, 0.3, 1.2), M['dark'])

    # ---------------- porch (outside, y < -4)
    box('porch', (0.5, -5.5, -0.05), (2.5, 1.5, 0.05), M['wet'])
    box('ext_wall', (0.5, -4.08, 1.5), (3, 0.02, 1.5), M['brick'])
    bpy.ops.object.light_add(type='SPOT', location=(0.5, -4.5, 2.6), rotation=(math.radians(20), 0, 0)); sp = bpy.context.object.data
    sp.energy = 380; sp.color = (1, 0.82, 0.55); sp.spot_size = math.radians(70); sp.spot_blend = 0.6
    porch_light = bpy.context.object
    bpy.ops.object.light_add(type='AREA', location=(0.5, -7.5, 3.5), rotation=(math.radians(60), 0, 0)); bl = bpy.context.object.data; bl.energy = 140; bl.color = (0.4, 0.55, 1.0); bl.size = 4

    # ---------------- characters
    def character(name, loc, m_body, eyes_emit=False):
        root = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(root); root.location = loc
        J = {'root': root}
        def joint(n, parent, offset):
            e = bpy.data.objects.new(f'{name}_{n}', None); bpy.context.collection.objects.link(e); e.parent = parent; e.location = offset
            J[n] = e; return e
        def seg(parent, length, r, m, down=True):
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=(0, 0, -length / 2 if down else length / 2), vertices=16)
            o = bpy.context.object; o.parent = parent; o.data.materials.append(m)
            bpy.ops.object.shade_smooth()
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 1.05, location=(0, 0, -length if down else length), segments=16, ring_count=8)
            s = bpy.context.object; s.parent = parent; s.data.materials.append(m); bpy.ops.object.shade_smooth()
            return o
        hips = joint('hips', root, (0, 0, 0.95))
        spine = joint('spine', hips, (0, 0, 0)); seg(spine, 0.62, 0.075, m_body, down=False)
        neck = joint('neck', spine, (0, 0, 0.66))
        head = joint('head', neck, (0, 0, 0.22))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 0), segments=32, ring_count=16)
        h = bpy.context.object; h.parent = head; h.data.materials.append(m_body); bpy.ops.object.shade_smooth()
        for sx in (-1, 1):
            e = joint(f'eye{sx}', head, (sx * 0.085, -0.17, 0.03))
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, segments=24, ring_count=12); o = bpy.context.object; o.parent = e
            o.data.materials.append(mat('glow', (1, 0.95, 0.6), 0.3, (1, 0.9, 0.3), 30.0) if eyes_emit else M['eye']); bpy.ops.object.shade_smooth()
            if not eyes_emit:
                pp = joint(f'pup{sx}', e, (0, -0.052, 0))
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, segments=16, ring_count=8); o = bpy.context.object; o.parent = pp; o.data.materials.append(M['pupil'])
                bw = joint(f'brow{sx}', head, (sx * 0.085, -0.19, 0.12))
                bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.parent = bw; o.scale = (0.06, 0.01, 0.012); o.data.materials.append(M['pupil'])
        mo = joint('mouth', head, (0, -0.2, -0.09))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, segments=16, ring_count=8); o = bpy.context.object; o.parent = mo; o.scale = (1, 0.4, 0.5); o.data.materials.append(M['pupil'])
        for sx, n in ((-1, 'L'), (1, 'R')):
            sh = joint(f'sh{n}', spine, (sx * 0.06, 0, 0.58)); seg(sh, 0.3, 0.05, m_body)
            el = joint(f'el{n}', sh, (0, 0, -0.3)); seg(el, 0.28, 0.045, m_body)
            hp = joint(f'hip{n}', hips, (sx * 0.08, 0, 0)); seg(hp, 0.46, 0.06, m_body)
            kn = joint(f'kn{n}', hp, (0, 0, -0.46)); seg(kn, 0.46, 0.055, m_body)
        return J

    me = character('me', (-1.5, 2.45, -0.4), M['skin'])
    twin = character('twin', (0.5, -5.2, 0.0), M['wet'])
    shadow = character('shadow', (2.4, 3.9, 0.0), M['dark'], eyes_emit=True)
    for J in (me, twin, shadow):
        J['root'].rotation_mode = 'XYZ'

    def key(o, frame, rot=None, loc=None, scale=None):
        if rot is not None:
            o.rotation_euler = [math.radians(v) for v in rot]; o.keyframe_insert('rotation_euler', frame=frame)
        if loc is not None:
            o.location = loc; o.keyframe_insert('location', frame=frame)
        if scale is not None:
            o.scale = scale; o.keyframe_insert('scale', frame=frame)

    def pose(J, frame, **P):
        # P: angles in degrees for joints; supports sit, arms, head, eye scale (fear)
        for k, v in P.items():
            if k in J: key(J[k], frame, rot=v)
        if 'fear' in P:
            f = P['fear']
            for sx in (-1, 1):
                if f'eye{sx}' in J: key(J[f'eye{sx}'], frame, scale=(1 + 0.35 * f,) * 3)
                if f'brow{sx}' in J: key(J[f'brow{sx}'], frame, rot=(0, sx * -20 * f, 0), loc=(sx * 0.085, -0.19, 0.12 + 0.05 * f))
            if 'mouth' in J: key(J['mouth'], frame, scale=(1 - 0.3 * f, 1, 1 + 1.6 * f))
        if 'look' in P:
            lx, ly = P['look']
            for sx in (-1, 1):
                if f'pup{sx}' in J: key(J[f'pup{sx}'], frame, loc=(lx * 0.02, -0.052, ly * 0.02))

    S = [F(s) for s in STARTS] + [F(TOTAL)]
    SIT = dict(hipL=(-90, 0, -5), hipR=(-90, 0, 5), knL=(90, 0, 0), knR=(90, 0, 0))
    # me: sitting, reaches phone, holds to ear
    pose(me, 1, spine=(0, 0, 0), head=(-10, 0, 0), shL=(0, 0, -10), elL=(0, 0, 0), shR=(-40, 0, 20), elR=(-20, 0, 0), fear=0, look=(0, -0.6), **SIT)
    pose(me, S[1], shR=(-150, 0, 25), elR=(-120, 0, 0), head=(0, 0, 10), fear=0.3, **SIT)
    pose(me, S[2], fear=0.6, look=(0, 0))
    pose(me, S[3], head=(0, 0, -25), fear=0.9, look=(-1, 0))
    pose(me, S[4] + 30, head=(5, 0, -10), fear=1.0, look=(0.6, 0.2))
    pose(me, S[5], **SIT)
    # walks to door during shot 5->6
    key(me['root'], S[5], loc=(-1.5, 2.45, -0.4), rot=(0, 0, 0))
    key(me['root'], S[5] + 2, loc=(0.4, -3.35, 0.0), rot=(0, 0, 0))
    pose(me, S[5] + 2, hipL=(0, 0, 0), hipR=(0, 0, 0), knL=(0, 0, 0), knR=(0, 0, 0), spine=(-12, 0, 0), head=(-5, 0, 0), fear=0.8, look=(0, 0),
         shR=(-150, 0, 25), elR=(-120, 0, 0), shL=(-40, 0, -10), elL=(-60, 0, 0))
    pose(me, S[8], spine=(0, 0, 0), head=(0, 0, 0), fear=0.9, look=(0, 0))
    pose(me, S[8] + 60, head=(0, 0, 20), fear=1.0, look=(1, 0))
    # twin outside: shivering, hands on door, mouth moving
    pose(twin, 1, shL=(-60, 0, -35), elL=(-70, 0, 0), shR=(-60, 0, 35), elR=(-70, 0, 0), head=(5, 0, 0), fear=1.0, look=(0, 0))
    key(twin['root'], 1, rot=(0, 0, 0))
    for k in range(S[6], S[8], 3):
        key(twin['spine'], k, rot=(0, 0, 2 if (k // 3) % 2 else -2))
    for k in range(S[7], S[8], 6):
        key(twin['mouth'], k, scale=(0.8, 1, 2.6 if (k // 6) % 2 else 0.8))
    # shadow figure: eyes appear in shot 8
    for sx in (-1, 1):
        key(shadow[f'eye{sx}'], 1, scale=(0.01,) * 3); key(shadow[f'eye{sx}'], S[8] + 40, scale=(0.01,) * 3)
        key(shadow[f'eye{sx}'], S[8] + 52, scale=(1, 1, 0.55)); key(shadow[f'eye{sx}'], S[9] + 30, scale=(1.2, 1, 0.45))
    key(shadow['root'], 1, loc=(2.4, 3.9, 0.0), rot=(0, 0, 15)); key(shadow['root'], S[10], loc=(0.9, -1.8, 0.0), rot=(0, 0, 5))
    # door knocks, lamp flicker, phone glow
    for k, f0 in enumerate((S[2] + 18, S[2] + 34, S[3] + 6, S[3] + 26, S[3] + 46)):
        key(door_pivot, f0 - 2, rot=(0, 0, 0)); key(door_pivot, f0, rot=(2.5, 0, 0)); key(door_pivot, f0 + 3, rot=(0, 0, 0))
    for f0 in range(1, S[10], 5):
        lamp.energy = 200 if (f0 % 37) > 6 or f0 < S[3] else 15; lamp.keyframe_insert('energy', frame=f0)
    # ---------------- cameras per shot (location, look-at, lens, end location)
    CAM = {
        'phone': ((-1.1, 0.55, 0.75), (-1.1, 1.1, 0.45), 50, (-1.1, 0.75, 0.62)),
        'couch': ((-1.0, -0.4, 1.3), (-1.5, 2.45, 1.3), 40, (-1.2, 0.3, 1.32)),
        'door': ((1.5, -1.0, 1.2), (0.0, -4.0, 1.1), 28, (1.3, -1.4, 1.15)),
        'pov': ((-0.4, 0.6, 1.4), (0.05, -4.0, 1.2), 30, (-0.1, -1.6, 1.4)),
        'face': ((-1.5, 1.55, 1.42), (-1.5, 2.45, 1.38), 70, (-1.5, 1.75, 1.42)),
        'peep': ((0.9, -2.0, 1.75), (0.4, -4.0, 1.6), 32, (0.75, -2.5, 1.7)),
        'porch': ((0.5, -7.6, 1.4), (0.5, -5.2, 1.3), 35, (0.5, -7.0, 1.4)),
        'twin': ((0.5, -6.2, 1.45), (0.5, -5.2, 1.42), 60, (0.5, -6.0, 1.45)),
        'behind': ((0.95, -3.95, 1.75), (1.9, 3.2, 1.5), 30, (0.9, -3.8, 1.72)),
        'eyes': ((0.7, -3.9, 1.8), (0.9, -1.8, 1.8), 45, (0.75, -3.5, 1.8)),
    }
    cams = {}
    for i, (dur, _, ck) in enumerate(SHOTS):
        p0, tgt, lens, p1 = CAM[ck]
        bpy.ops.object.camera_add(location=p0); c = bpy.context.object; c.name = f'cam{i}'; c.data.lens = lens
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 2.2
        tr = c.constraints.new('TRACK_TO'); e = bpy.data.objects.new(f'tgt{i}', None); bpy.context.collection.objects.link(e); e.location = tgt
        tr.target = e; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
        c.data.dof.focus_object = e
        key(c, S[i], loc=p0); key(c, S[i + 1], loc=p1)
        # handheld micro-shake
        c.rotation_mode = 'XYZ'
        cams[i] = c
        m = sc.timeline_markers.new(f's{i}', frame=S[i]); m.camera = c
    return sc, S

def render_shot(i, outdir):
    import bpy, cairo
    os.makedirs(outdir, exist_ok=True)
    sc, S = build()
    f0, f1 = S[i], S[i + 1] - 1
    sc.camera = bpy.data.objects[f'cam{i}']
    tmpdir = f'/tmp/frames3d_{i:02d}'; os.makedirs(tmpdir, exist_ok=True)
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
    from stick import caption, rgba, AMB, ACC, label, clamp, eback
    W, H = 1080, 1920
    tmp = os.path.join(outdir, f'tmp_{i:02d}.mp4'); final = os.path.join(outdir, f'scene_{i:02d}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    dur, text, _ = SHOTS[i]
    for f in range(f0, f1 + 1):
        t = (f - f0) / FPS
        src = cairo.ImageSurface.create_from_png(os.path.join(tmpdir, f'{f:05d}.png'))
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        ctx.save(); ctx.scale(W / src.get_width(), H / src.get_height()); ctx.set_source_surface(src); ctx.get_source().set_filter(cairo.FILTER_BEST); ctx.paint(); ctx.restore()
        v = cairo.RadialGradient(W / 2, H * 0.5, 400, W / 2, H * 0.5, 1250)
        v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.55); ctx.set_source(v); ctx.paint()
        if i == 0 and t < 0.2:
            rgba(ctx, (0, 0, 0), 1 - t / 0.2); ctx.paint()
        caption(ctx, t, text, 0.15, dur - 0.15, y=1380, size=88, chunk=3)
        g = (TOTAL and (STARTS[i] + t) / TOTAL)
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
