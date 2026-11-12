import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from engine import *

def magnet_bar(ctx, x, y, w, h, ang=0.0, a=1.0, left_n=True, labels=True):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    cols = (MAGRED, MAGBLUE) if left_n else (MAGBLUE, MAGRED)
    for i, c in enumerate(cols):
        x0 = -w / 2 + i * w / 2
        ctx.rectangle(x0, -h / 2, w / 2, h)
        g = cairo.LinearGradient(0, -h / 2, 0, h / 2)
        g.add_color_stop_rgba(0, min(1, c[0] + 0.3), min(1, c[1] + 0.3), min(1, c[2] + 0.3), a)
        g.add_color_stop_rgba(0.5, c[0], c[1], c[2], a)
        g.add_color_stop_rgba(1, c[0] * 0.5, c[1] * 0.5, c[2] * 0.5, a)
        ctx.set_source(g); ctx.fill()
    rr(ctx, -w / 2, -h / 2, w, h, 6); rgba(ctx, (0, 0, 0), 0.5 * a); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    if labels:
        ca, sa = math.cos(ang), math.sin(ang)
        for i, s in enumerate(("N", "S") if left_n else ("S", "N")):
            d = -w / 4 if i == 0 else w / 4
            label(ctx, s, x + d * ca, y + d * sa, h * 0.55, WHITE, a)

def field_lines(ctx, x, y, w, t, a=1.0, n=3, flip=False):
    # loops from N (left) to S (right) above and below
    for side in (-1, 1):
        for k in range(n):
            hgt = (90 + k * 85) * side
            p0 = (x - w / 2 + 10, y); p3 = (x + w / 2 - 10, y)
            pts = []
            for i in range(41):
                u = i / 40
                bx = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * (x - w * 0.9 - k * 60) + 3 * (1 - u) * u * u * (x + w * 0.9 + k * 60) + u ** 3 * p3[0]
                by = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * (y + hgt * 1.6) + 3 * (1 - u) * u * u * (y + hgt * 1.6) + u ** 3 * p3[1]
                pts.append((bx, by))
            if flip: pts = pts[::-1]
            draw_poly(ctx, pts); rgba(ctx, CYAN, 0.35 * a); ctx.set_line_width(3); ctx.stroke()
            flow_dots(ctx, pts, t, 3, 0.35, CYAN, 5, a, phase=k * 0.17)

def coil_bar(ctx, x, y, L, th, ang, polA, a=1.0, glow=1.0):
    """Electromagnet bar centered at (x,y); end A at angle ang. polA: 'N' or 'S' or None."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(-ang)
    metal_rect(ctx, -L, -th / 2, 2 * L, th, STEEL, True, 8, a)
    n = 14
    for i in range(n):
        xx = -L * 0.75 + i * (1.5 * L / (n - 1))
        ctx.save(); ctx.translate(xx, 0); ctx.scale(0.28, 1)
        ctx.arc(0, 0, th * 0.62, 0, 2 * math.pi); ctx.restore()
        fill_grad(ctx, COPPER, xx - 10, -th, xx + 10, th, a); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()
    if polA:
        ca, sa = math.cos(ang), -math.sin(ang)
        for sgn, pol in ((1, polA), (-1, "S" if polA == "N" else "N")):
            px, py = x + sgn * L * 0.93 * ca, y + sgn * L * 0.93 * sa
            c = MAGRED if pol == "N" else MAGBLUE
            glow_dot(ctx, px, py, 26 * glow, c, 0.9 * a)
            label(ctx, pol, px, py, 40, WHITE, a)

def stator(ctx, cx, cy, R, a=1.0):
    for side, c, s in ((-1, MAGRED, "N"), (1, MAGBLUE, "S")):
        a0 = math.pi * 0.72 if side < 0 else -math.pi * 0.28
        ctx.new_path()
        ctx.arc(cx, cy, R + 90, a0, a0 + math.pi * 0.56)
        ctx.arc_negative(cx, cy, R + 10, a0 + math.pi * 0.56, a0)
        ctx.close_path()
        g = cairo.RadialGradient(cx, cy, R, cx, cy, R + 90)
        g.add_color_stop_rgba(0, min(1, c[0] + .25), min(1, c[1] + .25), min(1, c[2] + .25), a)
        g.add_color_stop_rgba(1, c[0] * .55, c[1] * .55, c[2] * .55, a)
        ctx.set_source(g); ctx.fill_preserve()
        rgba(ctx, (0, 0, 0), 0.5 * a); ctx.set_line_width(3); ctx.stroke()
        label(ctx, s, cx + side * (R + 50), cy, 64, WHITE, a)

def commutator(ctx, cx, cy, ang, t, a=1.0, flash=0.0):
    r = 70
    # brushes
    for side in (-1, 1):
        metal_rect(ctx, (cx + r + 2) if side > 0 else (cx - r - 42), cy - 22, 40, 44, DARK, False, 4, a)
    for k in range(2):
        a0 = -ang + k * math.pi + 0.12
        ctx.new_path(); ctx.arc(cx, cy, r, a0, a0 + math.pi - 0.24); ctx.arc_negative(cx, cy, r - 26, a0 + math.pi - 0.24, a0); ctx.close_path()
        fill_grad(ctx, COPPER, cx - r, cy - r, cx + r, cy + r, a); ctx.fill()
    ctx.arc(cx, cy, 18, 0, 6.3); fill_grad(ctx, STEEL, cx - 18, cy, cx + 18, cy, a); ctx.fill()
    if flash > 0:
        glow_dot(ctx, cx - r - 4, cy, 20, YELLOW, flash); glow_dot(ctx, cx + r + 4, cy, 20, YELLOW, flash)

def polarity(phi):
    s = math.sin(phi)
    return "N" if s >= 0 else "S"

def motor_scene(ctx, cx, cy, phi, t, a=1.0, polA="auto", glow=1.0):
    R = 290
    ctx.arc(cx, cy, R + 120, 0, 6.3); fill_grad(ctx, DARK, cx, cy - R, cx, cy + R, 0.5 * a); ctx.fill()
    stator(ctx, cx, cy, R, a)
    p = polarity(phi) if polA == "auto" else polA
    coil_bar(ctx, cx, cy, R - 30, 70, phi, p, a, glow)
    ctx.arc(cx, cy, 22, 0, 6.3); fill_grad(ctx, STEEL, cx - 22, cy, cx + 22, cy, a); ctx.fill()

# ------------------------------------------------------------------ scenes
def s_hook(ctx, t, d):
    cx, cy = 470, 1150
    p = eback(prog(t, 0, 0.5))
    if p <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(p, p); ctx.translate(-cx, -cy)
    # body
    metal_rect(ctx, cx - 260, cy - 170, 420, 340, STEEL, True, 40)
    for k in range(7):
        ctx.rectangle(cx - 220 + k * 52, cy - 170, 20, 340)
        fill_grad(ctx, DARK, 0, cy - 170, 0, cy + 170, 0.35); ctx.fill()
    ctx.save(); ctx.translate(cx + 160, cy); ctx.scale(0.32, 1); ctx.arc(0, 0, 170, 0, 6.3); ctx.restore()
    fill_grad(ctx, STEEL, cx + 110, 0, cx + 210, 0); ctx.fill()
    # shaft
    metal_rect(ctx, cx + 180, cy - 18, 220, 36, STEEL, True, 8)
    # propeller (disc view)
    px = cx + 400
    spin = t * 25
    for k in range(3):
        ang = spin + k * 2 * math.pi / 3
        ctx.save(); ctx.translate(px, cy); ctx.scale(0.3, 1); ctx.rotate(ang)
        ctx.move_to(0, 0); ctx.curve_to(60, -60, 260, -40, 300, 0); ctx.curve_to(240, 30, 60, 40, 0, 0); ctx.restore()
        fill_grad(ctx, [(0, (0.1, 0.6, 0.9)), (1, (0.05, 0.3, 0.6))], px - 100, cy - 300, px + 100, cy + 300, 0.85); ctx.fill()
    ctx.save(); ctx.translate(px, cy); ctx.scale(0.3, 1); ctx.arc(0, 0, 300, 0, 6.3); ctx.restore()
    rgba(ctx, CYAN, 0.15); ctx.fill()
    # wires
    for k, c in enumerate(((0.9, 0.15, 0.15), (0.12, 0.12, 0.14))):
        ctx.move_to(cx - 260, cy - 60 + k * 120); ctx.curve_to(cx - 380, cy - 60 + k * 120, cx - 360, cy + 300, cx - 300 + k * 60, cy + 420)
        rgba(ctx, c); ctx.set_line_width(14); ctx.stroke()
    ctx.restore()
    # electric sparks
    if t > 0.6:
        for k in range(3):
            q = (t * 2 + k / 3) % 1
            glow_dot(ctx, cx - 300 - 40 * k, cy + 200 + 60 * q, 8, YELLOW, 1 - q)
    label(ctx, "motor eléctrico", cx - 50, cy + 260, 46, CYAN, eo(prog(t, 1.0, 1.4)), box=True)

def draw_phone(ctx, x, y, s, t, a):
    ctx.save(); ctx.translate(x + 4 * math.sin(t * 60) * s, y); ctx.scale(s, s)
    rr(ctx, -70, -140, 140, 280, 24); fill_grad(ctx, DARK, -70, 0, 70, 0, a); ctx.fill()
    rr(ctx, -60, -125, 120, 250, 14); fill_grad(ctx, [(0, (0.1, 0.4, 0.8)), (1, (0.05, 0.15, 0.4))], 0, -125, 0, 125, a); ctx.fill()
    ctx.restore()
    for k in (-1, 1):
        ctx.move_to(x + k * 95 * s, y - 50 * s); ctx.line_to(x + k * 95 * s, y + 50 * s)
        ctx.move_to(x + k * 115 * s, y - 30 * s); ctx.line_to(x + k * 115 * s, y + 30 * s)
    rgba(ctx, CYAN, a); ctx.set_line_width(5); ctx.stroke()

def draw_car(ctx, x, y, s, t, a):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-200, 30); ctx.line_to(-200, -10); ctx.curve_to(-190, -40, -150, -45, -110, -50)
    ctx.curve_to(-70, -100, 40, -105, 90, -55); ctx.curve_to(150, -50, 200, -40, 205, 0); ctx.line_to(205, 30); ctx.close_path()
    fill_grad(ctx, [(0, (0.95, 0.96, 1)), (0.5, (0.7, 0.74, 0.8)), (1, (0.35, 0.38, 0.45))], 0, -100, 0, 30, a); ctx.fill()
    ctx.move_to(-95, -50); ctx.curve_to(-60, -88, 20, -90, 70, -55); ctx.close_path()
    rgba(ctx, (0.1, 0.2, 0.35), a); ctx.fill()
    for wx in (-120, 130):
        ctx.arc(wx, 30, 40, 0, 6.3); rgba(ctx, (0.08, 0.08, 0.1), a); ctx.fill()
        ctx.arc(wx, 30, 20, 0, 6.3); fill_grad(ctx, STEEL, wx - 20, 0, wx + 20, 0, a); ctx.fill()
        for k in range(5):
            an = t * 12 + k * 1.256
            ctx.move_to(wx, 30); ctx.line_to(wx + 18 * math.cos(an), 30 + 18 * math.sin(an))
        rgba(ctx, (0.2, 0.2, 0.25), a); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def draw_fan(ctx, x, y, s, t, a):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, 0); ctx.line_to(0, 200); rgba(ctx, (0.6, 0.62, 0.66), a); ctx.set_line_width(16); ctx.stroke()
    ctx.save(); ctx.scale(1, 0.25); ctx.arc(0, 800, 90, 0, 6.3); ctx.restore(); fill_grad(ctx, STEEL, -90, 0, 90, 0, a); ctx.fill()
    for k in range(4):
        an = t * 14 + k * math.pi / 2
        ctx.save(); ctx.rotate(an); ctx.scale(1, 0.45); ctx.arc(70, 0, 68, 0, 6.3); ctx.restore()
        rgba(ctx, (0.2, 0.75, 1.0), 0.75 * a); ctx.fill()
    ctx.arc(0, 0, 150, 0, 6.3); rgba(ctx, (0.75, 0.8, 0.88), 0.7 * a); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(0, 0, 22, 0, 6.3); fill_grad(ctx, STEEL, -22, 0, 22, 0, a); ctx.fill()
    ctx.restore()

def s_where(ctx, t, d):
    items = [(draw_phone, 250, 870, 1.3, "móvil"), (draw_fan, 780, 880, 1.3, "ventilador"), (draw_car, CX, 1520, 2.2, "coche eléctrico")]
    for i, (fn, x, y, s, name) in enumerate(items):
        p = eback(prog(t, 0.2 + i * 0.3, 0.7 + i * 0.3))
        if p > 0:
            fn(ctx, x, y, s * p, t, 1)
            label(ctx, name, x, y + (175 if i == 0 else (280 if i == 1 else 120)) * s, 46, WHITE, p, NORM, box=True)

def s_magnet(ctx, t, d):
    p = eback(prog(t, 0, 0.5))
    magnet_bar(ctx, CX, 1150, 640 * p, 180 * p)
    fa = eo(prog(t, 0.6, 1.2))
    if fa > 0: field_lines(ctx, CX, 1150, 640, t, fa)
    label(ctx, "campo magnético", CX, 1650, 48, CYAN, eo(prog(t, 1.2, 1.6)), box=True)

def s_poles(ctx, t, d):
    # attract (top)
    q = eio(prog(t, 0.5, 1.3))
    gap = 260 - 230 * q
    magnet_bar(ctx, CX - 170 - gap / 2, 900, 300, 100, 0, 1, True)
    magnet_bar(ctx, CX + 170 + gap / 2, 900, 300, 100, 0, 1, True)
    if q >= 1: glow_dot(ctx, CX, 900, 16, GREEN, 0.6 + 0.4 * math.sin(t * 10))
    label(ctx, "se atraen", CX, 1040, 50, GREEN, eo(prog(t, 1.0, 1.4)), box=True)
    # repel (bottom)
    r = eio(prog(t, 1.6, 2.4))
    gap2 = 40 + 220 * r
    magnet_bar(ctx, CX - 170 - gap2 / 2, 1400, 300, 100, 0, 1, True)
    magnet_bar(ctx, CX + 170 + gap2 / 2, 1400, 300, 100, 0, 1, False)
    if r > 0:
        for sgn in (-1, 1):
            arrow_head(ctx, CX + sgn * (gap2 / 2 + 340 + 40), 1400, 0 if sgn > 0 else math.pi, 40, RED, r)
    label(ctx, "se repelen", CX, 1540, 50, RED, eo(prog(t, 2.1, 2.5)), box=True)

def s_electro(ctx, t, d):
    cx, cy = CX, 1080
    metal_rect(ctx, cx - 300, cy - 50, 600, 100, STEEL, True, 10)
    for i in range(18):
        xx = cx - 250 + i * 500 / 17
        ctx.save(); ctx.translate(xx, cy); ctx.scale(0.25, 1); ctx.arc(0, 0, 72, 0, 6.3); ctx.restore()
        fill_grad(ctx, COPPER, xx - 12, cy - 70, xx + 12, cy + 70); ctx.set_line_width(9); ctx.stroke()
    # wires to battery
    bx, by = CX, 1560
    wire = [(cx - 250, cy + 70), (cx - 250, by), (bx - 110, by)]
    wire2 = [(bx + 110, by), (cx + 250, by), (cx + 250, cy + 70)]
    for wpts, c in ((wire, (0.15, 0.15, 0.18)), (wire2, (0.85, 0.15, 0.15))):
        draw_poly(ctx, wpts); rgba(ctx, c); ctx.set_line_width(12); ctx.stroke()
    metal_rect(ctx, bx - 110, by - 50, 220, 100, [(0, (0.15, 0.15, 0.17)), (0.5, (0.35, 0.36, 0.4)), (1, (0.1, 0.1, 0.12))], True, 12)
    ctx.rectangle(bx + 60, by - 50, 50, 100); fill_grad(ctx, BRASS, 0, by - 50, 0, by + 50); ctx.fill()
    label(ctx, "+", bx + 140, by - 70, 50, RED); label(ctx, "pila", bx - 20, by, 36, WHITE, 1, NORM)
    on = prog(t, 0.6, 0.9)
    if on > 0:
        flow_dots(ctx, wire2[::-1][::-1], t, 4, 0.8, YELLOW, 7, on)
        flow_dots(ctx, wire, t, 4, -0.8, YELLOW, 7, on)
        fa = eo(prog(t, 1.0, 1.6))
        field_lines(ctx, cx, cy, 600, t, fa, n=2)
        for sgn, s, c in ((-1, "N", MAGRED), (1, "S", MAGBLUE)):
            glow_dot(ctx, cx + sgn * 300, cy, 30, c, fa); label(ctx, s, cx + sgn * 300, cy, 44, WHITE, fa)
    label(ctx, "electroimán", CX, 760, 52, CYAN, eo(prog(t, 1.4, 1.8)), box=True)
    label(ctx, "cable de cobre enrollado", CX, 1330, 36, ORANGE, eo(prog(t, 0.3, 0.7)), NORM)

def s_setup(ctx, t, d):
    p = eo(prog(t, 0, 0.6))
    motor_scene(ctx, CX, 1150, math.radians(90), t, p, "N", 1.0)
    label(ctx, "imanes fijos", CX, 1600, 42, WHITE, eo(prog(t, 0.6, 1.0)), NORM, box=True)
    label(ctx, "electroimán que gira", CX, 1700, 42, ORANGE, eo(prog(t, 1.0, 1.4)), NORM, box=True)

def s_turn(ctx, t, d):
    q = eio(prog(t, 0.4, 2.0))
    phi = math.radians(90 - 90 * q)
    motor_scene(ctx, CX, 1150, phi, t, 1, "N")
    if t < 2.0:
        ex, ey = CX + 220 * math.cos(phi), 1150 - 220 * math.sin(phi)
        ctx.arc(CX, 1150, 320, -math.radians(80), -math.radians(15))
        glow_stroke(ctx, YELLOW, 6, 1 - prog(t, 1.6, 2.0))
        arrow_head(ctx, CX + 320 * math.cos(math.radians(15)), 1150 - 320 * math.sin(math.radians(15)), math.radians(105), 34, YELLOW, 1 - prog(t, 1.6, 2.0))
    label(ctx, "N atrae a S", CX, 1600, 46, GREEN, eo(prog(t, 0.6, 1.0)), box=True)

def s_stuck(ctx, t, d):
    phi = math.radians(8 * math.exp(-t * 1.5) * math.cos(t * 9))
    motor_scene(ctx, CX, 1150, phi, t, 1, "N")
    ps = eback(prog(t, 0.6, 1.0))
    if ps > 0:
        x, y, r = CX, 1640, 70 * ps
        ctx.new_path()
        for k in range(8):
            an = math.pi / 8 + k * math.pi / 4
            ctx.line_to(x + r * math.cos(an), y + r * math.sin(an))
        ctx.close_path(); rgba(ctx, RED); ctx.fill()
        label(ctx, "STOP", x, y, 34 * ps, WHITE)

def s_commutator(ctx, t, d):
    w = 1.6
    phi = math.radians(90) - t * w
    pol = polarity(phi)
    s = math.sin(phi)
    flash = max(0, 1 - abs(s) * 6)
    motor_scene(ctx, CX, 1050, phi, t, 1, pol, 1 + 0.6 * flash)
    commutator(ctx, CX, 1560, phi, t, 1, flash)
    label(ctx, "conmutador", CX, 1700, 42, ORANGE, eo(prog(t, 0.3, 0.7)), box=True)
    label(ctx, "escobillas", CX + 230, 1480, 32, WHITE, eo(prog(t, 0.6, 1.0)), NORM)
    if flash > 0.3: label(ctx, "¡cambia!", CX + 300, 760, 46, YELLOW, flash)

def s_spin(ctx, t, d):
    w = 3 + 14 * eio(prog(t, 0, 2.5))
    phi = math.radians(90) - (3 * t + 7 * max(0, t - 0.8) ** 2)
    motor_scene(ctx, CX, 1150, phi, t, 1, polarity(phi))
    for k in range(3):
        ctx.arc(CX, 1150, 400 + k * 30, -phi, -phi + 1.0)
        rgba(ctx, CYAN, 0.4 - k * 0.1); ctx.set_line_width(5); ctx.stroke()

def s_real(ctx, t, d):
    cx, cy, R = CX, 1170, 400
    p = eo(prog(t, 0, 0.5))
    ctx.arc(cx, cy, R, 0, 6.3); fill_grad(ctx, STEEL, cx - R, cy - R, cx + R, cy + R, p); ctx.fill()
    ctx.arc(cx, cy, R - 40, 0, 6.3); rgba(ctx, (0.05, 0.06, 0.1), p); ctx.fill()
    n = 9
    act = (t * 2.2) % n
    for k in range(n):
        an = k * 2 * math.pi / n
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(an)
        metal_rect(ctx, 210, -34, 160, 68, DARK, False, 6, p)
        for j in range(5):
            rr(ctx, 230 + j * 26, -52, 20, 104, 8)
            fill_grad(ctx, COPPER, 0, -52, 0, 52, p); ctx.fill()
        ctx.restore()
        dist = min((act - k) % n, (k - act) % n)
        on = max(0, 1 - dist)
        if on > 0:
            glow_dot(ctx, cx + 290 * math.cos(an), cy + 290 * math.sin(an), 30, CYAN, on * p)
    rot = t * 2.2 * 2 * math.pi / n
    ctx.arc(cx, cy, 190, 0, 6.3); fill_grad(ctx, DARK, cx - 190, cy - 190, cx + 190, cy + 190, p); ctx.fill()
    for k in range(6):
        an = rot + k * math.pi / 3
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(an)
        rr(ctx, 120, -30, 60, 60, 8); rgba(ctx, MAGRED if k % 2 else MAGBLUE, p); ctx.fill()
        ctx.restore()
    ctx.arc(cx, cy, 50, 0, 6.3); fill_grad(ctx, STEEL, cx - 50, cy, cx + 50, cy, p); ctx.fill()
    label(ctx, "bobinas", cx + 300, cy - 470, 42, ORANGE, eo(prog(t, 0.8, 1.2)), box=True)
    label(ctx, "rotor con imanes", cx, cy + 480, 42, CYAN, eo(prog(t, 1.2, 1.6)), box=True)

def s_fact(ctx, t, d):
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 140); ctx.scale(pb, pb); ctx.rotate(-0.04)
        rr(ctx, -170, -42, 340, 84, 20); rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
        label(ctx, "¡DATO!", CX, 140, 54 * pb, NAVY)
    cx, cy, R = CX, 1240, 300
    pf = eio(prog(t, 0.5, 2.0)) * 0.53
    ctx.arc(cx, cy, R, 0, 6.3); rgba(ctx, (0.12, 0.16, 0.3)); ctx.fill()
    if pf > 0:
        ctx.move_to(cx, cy); ctx.arc(cx, cy, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * pf); ctx.close_path()
        fill_grad(ctx, [(0, (0.3, 0.95, 1.0)), (1, (0.05, 0.5, 0.8))], cx - R, cy - R, cx + R, cy + R); ctx.fill()
    ctx.arc(cx, cy, R * 0.55, 0, 6.3); rgba(ctx, (0.03, 0.05, 0.13)); ctx.fill()
    label(ctx, f"{int(round(pf * 100))} %", cx, cy, 110, YELLOW)
    label(ctx, "de toda la electricidad del mundo", CX, 1640, 40, WHITE, eo(prog(t, 2.0, 2.4)), NORM)
    label(ctx, "la usan motores eléctricos", CX, 1700, 44, CYAN, eo(prog(t, 2.2, 2.6)))
    label(ctx, "Fuente: IEA (2023)", CX, 1780, 28, WHITE, 0.6 * eo(prog(t, 2.4, 2.8)), NORM)

def s_cta(ctx, t, d):
    draw_fan(ctx, 380, 1150, 1.6 * eback(prog(t, 0, 0.5)), t * 1.5, 1)
    pb = eback(prog(t, 0.6, 1.1))
    if pb > 0:
        bx, by = 800, 860
        ctx.save(); ctx.translate(bx, by); ctx.scale(pb, pb)
        rr(ctx, -170, -90, 340, 180, 40); rgba(ctx, CYAN); ctx.fill()
        ctx.move_to(-60, 85); ctx.line_to(-130, 160); ctx.line_to(-10, 85); ctx.fill()
        for k in range(3):
            yy = -16 * max(0, math.sin(t * 6 - k * 0.8))
            ctx.arc(-70 + k * 70, yy, 18, 0, 6.3); rgba(ctx, NAVY); ctx.fill()
        ctx.restore()
    label(ctx, "¡Te leo en comentarios!", CX, 1700, 46, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)

SCENES = [
    (3.0, "¿Cómo gira un motor sin gasolina?", {3, 5}, CYAN, s_hook),
    (3.5, "Está en tu móvil, coche y ventilador", {3, 4, 6}, CYAN, s_where),
    (3.5, "Todo empieza con un imán", {4}, MAGRED, s_magnet),
    (4.0, "Polos opuestos se atraen, iguales se repelen", {2, 4}, YELLOW, s_poles),
    (4.0, "La electricidad crea otro imán", {1, 4}, CYAN, s_electro),
    (4.0, "Ponemos el electroimán entre dos imanes", {1, 2}, ORANGE, s_setup),
    (3.5, "Sus polos lo atraen y gira", {4}, GREEN, s_turn),
    (3.5, "Problema: se quedaría parado aquí", {0, 3}, RED, s_stuck),
    (5.0, "El conmutador invierte la corriente cada media vuelta", {1, 2}, ORANGE, s_commutator),
    (3.0, "Así gira sin parar", {1, 3}, CYAN, s_spin),
    (4.0, "Los motores reales tienen muchas bobinas", {4, 5}, ORANGE, s_real),
    (5.0, "Más de la mitad de la electricidad mundial", {0, 1, 2, 3}, YELLOW, s_fact, 480),
    (3.5, "¿Qué motor de tu casa gira más rápido?", {1, 6, 7}, CYAN, s_cta),
]

if __name__ == "__main__":
    run(SCENES)
