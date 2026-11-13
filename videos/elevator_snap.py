import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from stick import *

FEET = 1890; SM = 1.6; CAP_Y = 830

def led(ctx, text, x, y, size, col=ACC, a=1.0, glitch=0.0):
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    xb, yb, tw, th, _, _ = ctx.text_extents(text)
    for k, al in ((10, 0.15), (5, 0.3), (0, 1.0)):
        ctx.move_to(x - tw / 2 - xb + (random.uniform(-12, 12) if glitch else 0), y - yb - th / 2)
        ctx.text_path(text)
        if k:
            rgba(ctx, col, al * a); ctx.set_line_width(k * 2); ctx.stroke()
        else:
            rgba(ctx, col, a); ctx.fill()

def interior(ctx, t, floor="40", light=1.0, red=0.0, glitch=0.0, a=1.0):
    # ceiling
    ctx.move_to(0, 0); ctx.line_to(W, 0); ctx.line_to(W - 90, 300); ctx.line_to(90, 300); ctx.close_path()
    fill_grad(ctx, [(0, (0.05, 0.05, 0.07)), (1, (0.1, 0.11, 0.13))], 0, 0, 0, 300, a); ctx.fill()
    rr(ctx, 330, 170, 420, 60, 20); rgba(ctx, (1, 0.97, 0.88), (0.25 + 0.75 * light) * a); ctx.fill()
    g = cairo.RadialGradient(CX, 230, 20, CX, 230, 700)
    g.add_color_stop_rgba(0, 1, 0.95, 0.85, 0.35 * light * a); g.add_color_stop_rgba(1, 1, 0.95, 0.85, 0)
    # back wall with brushed panels
    ctx.rectangle(90, 300, W - 180, 1340)
    fill_grad(ctx, WALL, 90, 0, W - 90, 0, a); ctx.fill()
    for xx in range(90, W - 90, 6):
        ctx.move_to(xx, 300); ctx.line_to(xx, 1640)
    rgba(ctx, (1, 1, 1), 0.025 * a); ctx.set_line_width(1); ctx.stroke()
    # side walls (perspective)
    for sx in (0, 1):
        x0 = 0 if sx == 0 else W
        x1 = 90 if sx == 0 else W - 90
        ctx.move_to(x0, 0); ctx.line_to(x1, 300); ctx.line_to(x1, 1640); ctx.line_to(x0, 1920); ctx.close_path()
        fill_grad(ctx, [(0, (0.08, 0.09, 0.11)), (1, (0.13, 0.14, 0.17))], x0, 0, x1, 0, a); ctx.fill()
    # doors
    for k in range(2):
        x0 = 300 + k * 240
        ctx.rectangle(x0, 560, 240, 1080)
        fill_grad(ctx, [(0, (0.38, 0.4, 0.45)), (0.3, (0.62, 0.65, 0.7)), (0.6, (0.42, 0.44, 0.49)), (1, (0.3, 0.32, 0.36))], x0, 0, x0 + 240, 0, a); ctx.fill()
    ctx.move_to(CX, 560); ctx.line_to(CX, 1640); rgba(ctx, (0.05, 0.05, 0.07), a); ctx.set_line_width(5); ctx.stroke()
    ctx.rectangle(290, 550, 500, 1090); rgba(ctx, (0.2, 0.21, 0.25), a); ctx.set_line_width(12); ctx.stroke()
    # floor indicator
    rr(ctx, 410, 400, 260, 120, 16); rgba(ctx, (0.02, 0.02, 0.03), a); ctx.fill()
    led(ctx, floor, CX, 460, 86, ACC, a, glitch)
    # button panel
    rr(ctx, 860, 860, 110, 360, 14); fill_grad(ctx, [(0, (0.5, 0.52, 0.56)), (1, (0.3, 0.31, 0.34))], 860, 0, 970, 0, a); ctx.fill()
    for i in range(6):
        ctx.arc(915, 910 + i * 55, 17, 0, 6.3); rgba(ctx, (0.85, 0.75, 0.4) if i == 1 else (0.15, 0.16, 0.18), a); ctx.fill()
    # handrail
    for x0, x1 in ((90, 290), (790, 990)):
        rr(ctx, x0, 1240, x1 - x0, 22, 11); fill_grad(ctx, [(0, (0.85, 0.87, 0.9)), (1, (0.4, 0.42, 0.46))], 0, 1240, 0, 1262, a); ctx.fill()
    # floor
    ctx.move_to(90, 1640); ctx.line_to(W - 90, 1640); ctx.line_to(W, 1920); ctx.line_to(0, 1920); ctx.close_path()
    fill_grad(ctx, [(0, (0.12, 0.12, 0.14)), (1, (0.05, 0.05, 0.06))], 0, 1640, 0, 1920, a); ctx.fill()
    ctx.set_source(g); ctx.paint()
    if light < 1:
        rgba(ctx, (0, 0, 0.01), 0.75 * (1 - light) * a); ctx.paint()
    if red > 0:
        g2 = cairo.RadialGradient(CX, 230, 50, CX, 230, 1500)
        g2.add_color_stop_rgba(0, 1, 0.1, 0.1, 0.45 * red * a); g2.add_color_stop_rgba(1, 0.6, 0, 0, 0.25 * red * a)
        ctx.set_source(g2); ctx.paint()

def shake(ctx, k, t):
    if k > 0: ctx.translate(k * 18 * math.sin(t * 91), k * 14 * math.cos(t * 77))

# ------------------------------------------------------------------ shaft (cutaway)
def shaft(ctx, t, car_y=900, n_ropes=6, snapped=0, rope_show=1.0, brakes=0.0, gov_spin=0.0, speed_trip=0.0, a=1.0, highlight=0.0):
    ctx.rectangle(150, 0, 780, H); fill_grad(ctx, [(0, (0.05, 0.055, 0.07)), (0.5, (0.09, 0.1, 0.12)), (1, (0.05, 0.055, 0.07))], 150, 0, 930, 0, a); ctx.fill()
    for x in (150, 918):
        ctx.rectangle(x, 0, 12, H); rgba(ctx, (0.2, 0.21, 0.24), a); ctx.fill()
    for y in range(0, H, 240):   # floor slabs passing by
        ctx.rectangle(150, y, 780, 10); rgba(ctx, (0.16, 0.17, 0.2), a); ctx.fill()
    for x in (300, 780):          # guide rails
        ctx.rectangle(x - 8, 0, 16, H); fill_grad(ctx, [(0, (0.4, 0.42, 0.46)), (0.5, (0.8, 0.82, 0.86)), (1, (0.35, 0.37, 0.4))], x - 8, 0, x + 8, 0, a); ctx.fill()
    # machine & sheave
    sx, sy = CX, 300
    rr(ctx, 380, 170, 320, 70, 10); fill_grad(ctx, DARK, 0, 170, 0, 240, a); ctx.fill()
    ctx.arc(sx, sy, 80, 0, 6.3); fill_grad(ctx, STEEL, sx - 80, sy - 80, sx + 80, sy + 80, a); ctx.fill()
    for k in range(6):
        an = t * 0.5 + k * math.pi / 3
        ctx.move_to(sx, sy); ctx.line_to(sx + 70 * math.cos(an), sy + 70 * math.sin(an))
    rgba(ctx, (0.3, 0.3, 0.33), a); ctx.set_line_width(6); ctx.stroke()
    # governor wheel (left) + rope
    gx, gy = 225, 300
    ctx.arc(gx, gy, 45, 0, 6.3); fill_grad(ctx, BRASS, gx - 45, gy - 45, gx + 45, gy + 45, a); ctx.fill()
    for k in range(4):
        an = gov_spin + k * math.pi / 2
        ctx.move_to(gx, gy); ctx.line_to(gx + 40 * math.cos(an), gy + 40 * math.sin(an))
    rgba(ctx, (0.35, 0.25, 0.05), a); ctx.set_line_width(5); ctx.stroke()
    if speed_trip > 0:
        glow_dot(ctx, gx, gy, 30, AMB, speed_trip * a)
    ctx.move_to(gx - 45, gy); ctx.line_to(gx - 45, H); ctx.move_to(gx + 45, gy); ctx.line_to(gx + 45, car_y + 340)
    rgba(ctx, (0.6, 0.55, 0.4), 0.8 * a); ctx.set_line_width(3); ctx.stroke()
    # ropes
    xs = [CX - 60 + i * 120 / max(1, n_ropes - 1) for i in range(n_ropes)]
    for i, x in enumerate(xs):
        if i < snapped:
            ctx.move_to(x, sy + 80); ctx.line_to(x + 10 * math.sin(t * 5 + i), sy + 260)
            rgba(ctx, (0.6, 0.6, 0.62), 0.6 * a); ctx.set_line_width(5); ctx.stroke()
            continue
        k = clamp(rope_show * n_ropes - i)
        if k <= 0: continue
        ctx.move_to(x, sy + 60); ctx.line_to(x, sy + 60 + (car_y - sy - 60) * k)
        rgba(ctx, (0.75, 0.77, 0.8), a); ctx.set_line_width(7); ctx.stroke()
        if highlight > 0:
            ctx.move_to(x, sy + 60); ctx.line_to(x, car_y); glow_stroke(ctx, AMB, 3, highlight * a)
    # car
    cw, ch = 420, 380; cx0 = CX - cw / 2
    rr(ctx, cx0, car_y, cw, ch, 10); fill_grad(ctx, [(0, (0.45, 0.47, 0.52)), (0.5, (0.7, 0.72, 0.77)), (1, (0.35, 0.37, 0.41))], cx0, 0, cx0 + cw, 0, a); ctx.fill()
    rr(ctx, cx0 + 25, car_y + 25, cw - 50, ch - 50, 8); rgba(ctx, (0.08, 0.09, 0.11), a); ctx.fill()
    ctx.rectangle(cx0 + 25, car_y + 25, cw - 50, 16); rgba(ctx, (1, 0.95, 0.8), 0.7 * a); ctx.fill()
    stickman(ctx, CX, car_y + ch - 30, 0.62, 'scared' if speed_trip < 0.5 and brakes < 0.5 and snapped >= n_ropes else 'idle',
             fear=0.6 if snapped else 0.0, mouth='o' if snapped >= n_ropes and brakes < 0.9 else 'flat', a=a)
    # safety brakes on rails
    for x, sgn in ((300, 1), (780, -1)):
        bx = x + sgn * 12 * (1 - brakes)
        ctx.move_to(bx, car_y + ch - 60); ctx.line_to(bx + sgn * 40, car_y + ch - 80); ctx.line_to(bx + sgn * 40, car_y + ch); ctx.line_to(bx, car_y + ch - 10); ctx.close_path()
        fill_grad(ctx, DARK, bx, 0, bx + sgn * 40, 0, a); ctx.fill()
        ctx.move_to(x + sgn * 40, car_y + ch - 40); ctx.line_to(cx0 if sgn > 0 else cx0 + cw, car_y + ch - 40)
        rgba(ctx, (0.3, 0.31, 0.34), a); ctx.set_line_width(10); ctx.stroke()
        if brakes > 0:
            glow_dot(ctx, x + sgn * 20, car_y + ch - 40, 22, AMB, brakes * a)

# ------------------------------------------------------------------ scenes
def cap(ctx, t, d, text, first=False):
    caption(ctx, t, text, 0.05 if first else 0.35, d - 0.2, y=CAP_Y)

def s1(ctx, t, d):
    snap = t > 1.7
    k = max(0, 1 - (t - 1.7) / 0.6) if snap else 0
    ctx.save(); shake(ctx, k, t)
    interior(ctx, t, "40", light=1 - 0.6 * k, glitch=k)
    stickman(ctx, CX, FEET, SM, 'phone' if not snap else lerp_pose('phone', 'scared', clamp((t - 1.7) / 0.2)),
             look=(0.6, 1) if not snap else (0, -0.6), fear=0 if not snap else 1, mouth='flat' if not snap else 'o',
             blink=blink_at(t), phone=True, t=t)
    ctx.restore()
    flash(ctx, 0.6 * k)
    heart_meter(ctx, t, 78 if not snap else 78 + 40 * clamp((t - 1.7) / 0.8))
    cap(ctx, t, d, "Floor 40. Then… SNAP.", True)

def s2(ctx, t, d):
    fl = 0.25 + 0.75 * (1 if math.sin(t * 23) * math.sin(t * 7) > -0.2 else 0)
    ctx.save(); shake(ctx, 0.5 * max(0, 1 - t), t)
    interior(ctx, t, "40", light=fl, red=0.5 + 0.5 * math.sin(t * 6) ** 2, glitch=0.3)
    stickman(ctx, CX, FEET, SM, 'scared', look=(math.sin(t * 3), -0.5), fear=1, mouth='o', sweat=1, t=t)
    ctx.restore()
    heart_meter(ctx, t, 118 + 20 * t / d)
    cap(ctx, t, d, "The elevator jolts. The lights flicker.")

def s3(ctx, t, d):
    interior(ctx, t, str(max(1, 40 - int(t * 14))), light=0.6, red=1.0, glitch=1.0)
    for k in range(14):   # speed lines (falling feeling)
        x = 60 + (k * 137) % 960; y = (k * 211 - t * 2600) % 2100 - 100
        ctx.move_to(x, y); ctx.line_to(x, y + 220); rgba(ctx, WHITE, 0.25); ctx.set_line_width(4); ctx.stroke()
    stickman(ctx, CX, FEET - 120 - 30 * math.sin(t * 4), SM, 'scared', look=(0, -1), fear=1, mouth='o', rot=0.08 * math.sin(t * 3), sweat=1, t=t)
    label(ctx, "IN YOUR HEAD", CX, 620, 40, ACC, eo(prog(t, 0.4, 0.8)), box=True)
    heart_meter(ctx, t, 140 + 25 * t / d)
    cap(ctx, t, d, "Your brain screams one word: FREE FALL.")

def s4(ctx, t, d):
    interior(ctx, t, "40", light=0.5, red=0.4)
    opts = [(220, 'jump', "JUMP?", 0.4), (CX, 'idle', "LIE FLAT?", 1.3), (860, 'pray', "PRAY?", 2.2)]
    for x, pose, lab, st in opts:
        p = eback(prog(t, st, st + 0.35))
        if p <= 0: continue
        if lab == "LIE FLAT?":
            stickman(ctx, x - 120, 1840, 0.62 * p, 'idle', rot=-math.pi / 2, fear=0.8, mouth='wavy', a=1)
        else:
            stickman(ctx, x, 1780 + (-40 * abs(math.sin(t * 6)) if pose == 'jump' else 0), 0.62 * p, pose, fear=0.8, mouth='wavy')
        label(ctx, lab, x, 1180, 54, AMB, p, box=True)
    heart_meter(ctx, t, 160)
    cap(ctx, t, d, "Should you jump before impact? Lie flat? Pray?")

def s5(ctx, t, d):
    z = 2.8 - 1.8 * eio(prog(t, 0.2, 2.4))
    ctx.save(); ctx.translate(CX, 1100); ctx.scale(z, z); ctx.translate(-CX, -1090)
    shaft(ctx, t, car_y=900)
    ctx.restore()
    heart_meter(ctx, t, 150)
    cap(ctx, t, d, "Hold on. Let's look outside the box.")

def s6(ctx, t, d):
    show = eio(prog(t, 0.8, 2.6))
    shaft(ctx, t, 900, 6, rope_show=show, highlight=prog(t, 2.6, 3.0))
    n = int(round(6 * show))
    if n: label(ctx, f"×{n} CABLES", 850, 640, 50, AMB, 1, box=True)
    heart_meter(ctx, t, 140)
    cap(ctx, t, d, "It doesn't hang from one cable. It hangs from four to eight.")

def s7(ctx, t, d):
    sn = min(5, int(max(0, t - 0.6) / 0.45))
    shaft(ctx, t, 900, 6, snapped=sn, highlight=0.6 if sn == 5 else 0)
    if sn and (t - 0.6) % 0.45 < 0.12 and sn <= 5:
        glow_dot(ctx, CX - 60 + (sn - 1) * 24, 520, 40, ACC, 0.9)
    if sn == 5: label(ctx, "1 CABLE = WHOLE CAR", CX, 1460, 50, AMB, 1, box=True)
    heart_meter(ctx, t, 128)
    cap(ctx, t, d, "And each one can hold the whole car by itself.")

def s8(ctx, t, d):
    fall = max(0, t - 0.6)
    v = min(14, 22 * fall)
    cy = 900 + 60 * fall * fall
    trip = clamp((t - 2.7) / 0.3)
    shaft(ctx, t, min(cy, 1250), 6, snapped=6, gov_spin=t * (2 + 10 * fall), speed_trip=trip)
    if trip > 0: label(ctx, "GOVERNOR TRIPS!", 225, 470, 40, AMB, trip, box=True)
    speed_meter(ctx, v * 1.6, 25, x=850, y=1780, r=120)
    heart_meter(ctx, t, 150)
    cap(ctx, t, d, "Even if every cable snapped, a speed sensor, the governor, would trip.")

def s9(ctx, t, d):
    b = eo(prog(t, 0.2, 0.7))
    stop = eio(prog(t, 0.2, 1.4))
    shaft(ctx, t, 1250 + 60 * stop, 6, snapped=6, brakes=b, gov_spin=4 * (1 - stop))
    speed_meter(ctx, 22 * (1 - stop), 25, x=850, y=1780, r=120)
    if stop >= 1: label(ctx, "STOPPED", CX, 1150, 60, (0.3, 0.95, 0.5), eback(prog(t, 1.4, 1.7)), box=True)
    heart_meter(ctx, t, 140 - 30 * stop)
    cap(ctx, t, d, "Steel brakes clamp the rails. The car stops.")

def s10(ctx, t, d):
    rr(ctx, 90, 980, 900, 620, 20); rgba(ctx, (0.02, 0.02, 0.03)); ctx.fill()
    for i in range(14):
        rr(ctx, 110 + i * 63, 1000, 32, 26, 5); rr(ctx, 110 + i * 63, 1554, 32, 26, 5)
    rgba(ctx, (0.25, 0.25, 0.28)); ctx.fill()
    ctx.save(); ctx.rectangle(110, 1040, 860, 500); ctx.clip()
    ctx.translate(0, 0)
    yy = 1040 + ((t * 900) % 700) - 300
    rr(ctx, 400, yy, 280, 240, 10); fill_grad(ctx, STEEL, 400, 0, 680, 0); ctx.fill()
    for k in range(10):
        rnd = random.Random(int(t * 25) + k)
        sx = 400 if k % 2 else 680
        ctx.move_to(sx, yy + 200); ctx.line_to(sx + rnd.uniform(-90, 90), yy + 200 - rnd.uniform(40, 160))
        rgba(ctx, AMB); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    label(ctx, "MOVIES", 250, 940, 44, WHITE, 1, NORM)
    ps = eback(prog(t, 1.4, 1.75))
    if ps > 0:
        ctx.save(); ctx.translate(CX, 1290); ctx.rotate(-0.2); ctx.scale(ps * 1.2, ps * 1.2)
        rr(ctx, -260, -70, 520, 140, 16); rgba(ctx, ACC, 0.9); ctx.set_line_width(12); ctx.stroke()
        ctx.restore()
        ctx.save(); ctx.translate(CX, 1290); ctx.rotate(-0.2)
        label(ctx, "FICTION", 0, 0, 100 * ps, ACC, 1)
        ctx.restore()
    heart_meter(ctx, t, 100)
    cap(ctx, t, d, "Movie scenes with sparks flying? Pure fiction.")

def s11(ctx, t, d):
    interior(ctx, t, "40", light=1.0)
    k = eo(prog(t, 0.6, 1.4))
    stickman(ctx, CX, FEET, SM, lerp_pose('scared', 'relief', k), look=(0, 0), fear=1 - k, mouth='o' if k < 0.5 else 'smile', blink=blink_at(t, 1.8))
    if t > 2.0:
        label(ctx, "1 CABLE. YOU NEVER MOVED.", CX, 620, 44, (0.3, 0.95, 0.5), eo(prog(t, 2.0, 2.4)), box=True)
    heart_meter(ctx, t, 120 - 40 * k)
    cap(ctx, t, d, "That snap? One cable. You never even moved.")

def s12(ctx, t, d):
    interior(ctx, t, "40", light=1.0)
    k = eo(prog(t, 0.3, 0.8))
    stickman(ctx, CX, FEET, SM, lerp_pose('relief', 'shrug', k), look=(0, 0.3), mouth='smile', blink=blink_at(t, 1.5))
    heart_meter(ctx, t, 78)
    cap(ctx, t, d, "Would you still take the stairs?")

SCENES = [
    (3.0, "", set(), WHITE, s1),
    (3.0, "", set(), WHITE, s2),
    (3.0, "", set(), WHITE, s3),
    (3.6, "", set(), WHITE, s4),
    (3.0, "", set(), WHITE, s5),
    (4.2, "", set(), WHITE, s6),
    (3.5, "", set(), WHITE, s7),
    (4.4, "", set(), WHITE, s8),
    (3.4, "", set(), WHITE, s9),
    (3.2, "", set(), WHITE, s10),
    (3.4, "", set(), WHITE, s11),
    (2.8, "", set(), WHITE, s12),
]

if __name__ == "__main__":
    run(SCENES, theme='noir', fades=False)
