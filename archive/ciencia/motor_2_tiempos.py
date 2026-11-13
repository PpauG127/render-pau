import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from engine import *

EX = CX            # engine x center
CCY = 1470         # crank center y
CR = 105           # crank radius
LROD = 320
PH = 190           # piston height
PIN = 95           # pin below piston top
BORE = 300
HEAD = 870         # inside of cylinder head
CYL_BOT = 1300
EXH = (1075, 1160)     # exhaust port y range (right wall)
TRF = (1115, 1165)     # transfer port y range (left wall)
XL, XR = EX - BORE / 2, EX + BORE / 2
FRESH = (0.25, 0.65, 1.0)
SMOKE = (0.55, 0.55, 0.6)

def piston_top(th):
    s = CR * math.sin(th); c = CR * math.cos(th)
    pin_y = CCY - (c + math.sqrt(LROD ** 2 - s ** 2))
    return pin_y - PIN, pin_y

def openness(top, rng):
    return clamp((top - rng[0]) / (rng[1] - rng[0]))

def chamber_color(th):
    d = math.degrees(th) % 360
    top, _ = piston_top(th)
    ex = openness(top, EXH)
    if d < 25:
        f = d / 25
        return (1.0, 0.95 - 0.25 * f, 0.6 - 0.45 * f), 0.95
    if ex <= 0 and d < 180:
        f = (d - 25) / 80
        return (1.0, 0.55 - 0.25 * clamp(f), 0.12), 0.85 - 0.3 * clamp(f)
    if d < 180 or openness(top, TRF) > 0:
        return SMOKE, 0.45
    # compression of fresh mix
    f = (d - 180) / 180
    return FRESH, 0.25 + 0.5 * f

INTAKE_PATH = [(120, 1830), (250, 1720), (345, 1640), (430, 1560), (500, 1500)]
TRANSFER_PATH = [(470, 1420), (360, 1390), (325, 1300), (325, 1170), (360, 1140), (430, 1120), (500, 1040), (560, 990)]
EXHAUST_PATH = [(520, 1000), (620, 1050), (690, 1110), (800, 1110), (900, 1130), (1000, 1200), (1080, 1260)]

def draw_engine(ctx, th, t, rate=1.0, a=1.0, show_flow=True, port_glow=0.0, smoke=0.0):
    top, pin_y = piston_top(th)
    piny = pin_y
    cx, cy = EX + CR * math.sin(th), CCY - CR * math.cos(th)
    # --- crankcase body
    ctx.arc(EX, CCY, 250, 0, 6.3); fill_grad(ctx, DARK, EX - 250, 0, EX + 250, 0, a); ctx.fill()
    ctx.arc(EX, CCY, 220, 0, 6.3); rgba(ctx, (0.04, 0.05, 0.1), a); ctx.fill()
    # crankcase gas
    d = math.degrees(th) % 360
    up = math.sin(th) < 0     # piston moving up when th in (180,360)
    dens = 0.22 + 0.18 * (1 - (math.cos(th) + 1) / 2)
    ctx.arc(EX, CCY, 220, 0, 6.3); rgba(ctx, FRESH, dens * a); ctx.fill()
    # --- transfer channel (left)
    ctx.move_to(XL - 70, TRF[0]); ctx.line_to(XL, TRF[0]); ctx.line_to(XL, TRF[1]); ctx.line_to(XL - 20, TRF[1])
    ctx.line_to(XL - 20, CYL_BOT + 60); ctx.line_to(EX - 120, CCY - 160); ctx.line_to(EX - 190, CCY - 120); ctx.line_to(XL - 70, CYL_BOT + 40); ctx.close_path()
    rgba(ctx, (0.04, 0.05, 0.1), a); ctx.fill_preserve(); rgba(ctx, FRESH, 0.25 * a); ctx.fill()
    # --- cylinder walls with fins
    for side in (-1, 1):
        x0 = XL - 90 if side < 0 else XR
        ctx.rectangle(x0, HEAD - 20, 90, CYL_BOT - HEAD + 20)
        fill_grad(ctx, DARK, x0, 0, x0 + 90, 0, a); ctx.fill()
        for k in range(8):
            fy = HEAD + 10 + k * 34
            fx = x0 - 70 if side < 0 else x0 + 90
            if fy > EXH[0] - 30 and side > 0: continue
            if fy > TRF[0] - 30 and side < 0: continue
            ctx.rectangle(fx, fy, 70, 14); fill_grad(ctx, STEEL, 0, fy, 0, fy + 14, a); ctx.fill()
    # transfer channel cut through left wall
    ctx.rectangle(XL - 70, TRF[0], 70, TRF[1] - TRF[0]); rgba(ctx, (0.05, 0.08, 0.16), a); ctx.fill()
    ctx.rectangle(XL - 70, TRF[1], 50, CYL_BOT - TRF[1] + 40); rgba(ctx, (0.05, 0.08, 0.16), a); ctx.fill()
    ctx.rectangle(XL - 70, TRF[0], 70, CYL_BOT - TRF[0] + 40); rgba(ctx, FRESH, 0.22 * a); ctx.fill()
    # exhaust port + pipe
    ctx.rectangle(XR, EXH[0], 90, EXH[1] - EXH[0]); rgba(ctx, (0.05, 0.06, 0.1), a); ctx.fill()
    ctx.move_to(XR + 90, EXH[0]); ctx.line_to(900, EXH[0] - 10); ctx.curve_to(1000, EXH[0] - 10, 1060, EXH[0] + 40, 1100, EXH[0] + 100)
    ctx.line_to(1100, EXH[1] + 150); ctx.curve_to(1040, EXH[1] + 60, 980, EXH[1] + 20, 900, EXH[1] + 10); ctx.line_to(XR + 90, EXH[1]); ctx.close_path()
    fill_grad(ctx, STEEL, 0, EXH[0] - 20, 0, EXH[1] + 60, 0.9 * a); ctx.fill()
    ctx.move_to(XR + 90, EXH[0] + 14); ctx.line_to(900, EXH[0] + 6); ctx.curve_to(990, EXH[0] + 6, 1040, EXH[0] + 60, 1080, EXH[0] + 110)
    ctx.line_to(1080, EXH[1] + 110); ctx.curve_to(1030, EXH[1] + 50, 970, EXH[1] + 4, 900, EXH[1] - 6); ctx.line_to(XR + 90, EXH[1] - 14); ctx.close_path()
    rgba(ctx, (0.06, 0.06, 0.09), a); ctx.fill()
    # cylinder bore background
    ctx.rectangle(XL, HEAD, BORE, CYL_BOT - HEAD + 30); rgba(ctx, (0.04, 0.05, 0.1), a); ctx.fill()
    # combustion chamber gas
    col, al = chamber_color(th)
    ctx.rectangle(XL, HEAD, BORE, top - HEAD); rgba(ctx, col, al * a); ctx.fill()
    if math.degrees(th) % 360 < 30:
        g = cairo.RadialGradient(EX, HEAD + 20, 5, EX, HEAD + 20, 260)
        f = 1 - (math.degrees(th) % 360) / 30
        g.add_color_stop_rgba(0, 1, 1, 0.85, f * a); g.add_color_stop_rgba(1, 1, 0.6, 0.1, 0)
        ctx.set_source(g); ctx.rectangle(XL, HEAD, BORE, top - HEAD); ctx.fill()
    # head
    ctx.move_to(XL - 90, HEAD); ctx.line_to(XL - 90, HEAD - 80); ctx.curve_to(XL, HEAD - 130, XR, HEAD - 130, XR + 90, HEAD - 80)
    ctx.line_to(XR + 90, HEAD); ctx.close_path(); fill_grad(ctx, STEEL, XL - 90, 0, XR + 90, 0, a); ctx.fill()
    for k in range(3):
        ctx.rectangle(XL - 60 + k * 0, HEAD - 150 - k * 0, 0, 0)
    # spark plug
    metal_rect(ctx, EX - 22, HEAD - 210, 44, 110, [(0, (0.95, 0.95, 0.97)), (0.5, (1, 1, 1)), (1, (0.7, 0.7, 0.75))], False, 8, a)
    metal_rect(ctx, EX - 30, HEAD - 110, 60, 50, BRASS, False, 4, a)
    metal_rect(ctx, EX - 6, HEAD - 60, 12, 55, STEEL, False, 2, a)
    # piston
    metal_rect(ctx, XL + 4, top, BORE - 8, PH, [(0, (0.55, 0.57, 0.62)), (0.35, (0.95, 0.96, 0.98)), (0.6, (0.72, 0.74, 0.78)), (1, (0.45, 0.47, 0.52))], False, 6, a)
    for k in range(3):
        ctx.move_to(XL + 4, top + 16 + k * 16); ctx.line_to(XR - 4, top + 16 + k * 16)
    rgba(ctx, (0.25, 0.27, 0.3), a); ctx.set_line_width(4); ctx.stroke()
    # rod
    ang = math.atan2(cx - EX, piny - cy)
    ctx.save(); ctx.translate(EX, piny)
    ctx.move_to(-22, 0); ctx.line_to(cx - EX - 30, cy - piny); ctx.line_to(cx - EX + 30, cy - piny); ctx.line_to(22, 0); ctx.close_path()
    fill_grad(ctx, STEEL, -40, 0, 40, 0, a); ctx.fill()
    ctx.restore()
    ctx.arc(EX, piny, 24, 0, 6.3); fill_grad(ctx, DARK, EX - 24, 0, EX + 24, 0, a); ctx.fill()
    # crank web (disc + counterweight opposite the pin)
    ctx.new_path(); ctx.arc(EX, CCY, 160, 0, 6.3); fill_grad(ctx, STEEL, EX - 160, CCY - 160, EX + 160, CCY + 160, a); ctx.fill()
    ctx.new_path(); ctx.move_to(EX, CCY)
    base_ang = math.atan2(cy - CCY, cx - EX) + math.pi
    ctx.arc(EX, CCY, 158, base_ang - 1.1, base_ang + 1.1); ctx.close_path()
    fill_grad(ctx, DARK, EX - 160, CCY, EX + 160, CCY, 0.8 * a); ctx.fill()
    ctx.arc(EX, CCY, 50, 0, 6.3); fill_grad(ctx, DARK, EX - 50, 0, EX + 50, 0, a); ctx.fill()
    ctx.arc(cx, cy, 44, 0, 6.3); fill_grad(ctx, STEEL, cx - 44, cy - 44, cx + 44, cy + 44, a); ctx.fill_preserve()
    rgba(ctx, (0.1, 0.1, 0.12), a); ctx.set_line_width(3); ctx.stroke()
    # reed valve / intake pipe
    ctx.move_to(60, 1840); ctx.line_to(330, 1600); ctx.line_to(380, 1650); ctx.line_to(110, 1890); ctx.close_path()
    fill_grad(ctx, DARK, 60, 1600, 380, 1890, a); ctx.fill()
    ctx.move_to(85, 1865); ctx.line_to(350, 1625); rgba(ctx, (0.05, 0.08, 0.16), a); ctx.set_line_width(36); ctx.stroke()
    ctx.move_to(85, 1865); ctx.line_to(350, 1625); rgba(ctx, FRESH, 0.25 * a); ctx.set_line_width(36); ctx.stroke()
    # --- flows
    if show_flow:
        if up:
            flow_dots(ctx, INTAKE_PATH, t, 6, 1.0, FRESH, 8, a)
        tr = openness(top, TRF)
        if tr > 0 and math.sin(th) > -0.5:
            flow_dots(ctx, TRANSFER_PATH, t, 7, 1.4, FRESH, 9, a * tr)
        ex = openness(top, EXH)
        if ex > 0:
            flow_dots(ctx, EXHAUST_PATH, t, 7, 1.6, (0.8, 0.8, 0.85) if d > 140 else ORANGE, 9, a * ex)
    if port_glow > 0:
        for (x, y0, y1) in ((XR, EXH[0], EXH[1]), (XL - 70, TRF[0], TRF[1])):
            ctx.rectangle(x, y0, 90 if x == XR else 70, y1 - y0)
            glow_stroke(ctx, YELLOW, 5, port_glow)
    if smoke > 0:
        rnd = random.Random(5)
        for k in range(10):
            q = (t * 0.5 + k / 10) % 1
            x = 1090 + 40 * math.sin(k + t) - q * 50
            y = 1380 + q * 260
            ctx.arc(x, y, 30 + q * 110, 0, 6.3); rgba(ctx, (0.65, 0.7, 0.85), 0.35 * (1 - q) * smoke); ctx.fill()

def spark_if(ctx, th, t, a=1.0):
    dd = math.degrees(th) % 360
    if dd > 352 or dd < 6:
        spark(ctx, EX, HEAD + 8, 1.4, t, a)

def cycle(t, speed):
    return t * speed

# ------------------------------------------------------------------ scenes
def s_hook(ctx, t, d):
    th = t * 2 * math.pi * 2.2
    p = eo(prog(t, 0, 0.5))
    ctx.save(); ctx.translate(math.sin(t * 70) * 3, 0)
    draw_engine(ctx, th, t, a=p, smoke=0.6)
    spark_if(ctx, th, t, p)
    ctx.restore()

def s_parts(ctx, t, d):
    th = 0.6 + t * 1.2
    draw_engine(ctx, th, t, show_flow=False)
    top, piny = piston_top(th)
    items = [("bujía", EX + 60, HEAD - 160, 230, 760, YELLOW, 0.3),
             ("pistón", XR - 30, top + 60, 860, top + 60, ORANGE, 0.7),
             ("biela", EX + 30, (piny + CCY) / 2, 860, (piny + CCY) / 2 + 40, CYAN, 1.1),
             ("cigüeñal", EX + 140, CCY + 60, 860, CCY + 230, GREEN, 1.5),
             ("cilindro", XL - 80, HEAD + 60, 180, HEAD + 60, WHITE, 1.9)]
    for name, x0, y0, x1, y1, c, st in items:
        p = eo(prog(t, st, st + 0.35))
        if p > 0:
            ctx.move_to(x0, y0); ctx.line_to(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p)
            rgba(ctx, c, p); ctx.set_line_width(4); ctx.stroke()
            glow_dot(ctx, x0, y0, 8, c, p)
            label(ctx, name, x1, y1, 46, c, p, box=True)

def s_motion(ctx, t, d):
    th = t * 2.4
    draw_engine(ctx, th, t, show_flow=False)
    top, _ = piston_top(th)
    pa = eo(prog(t, 0.3, 0.7))
    x = 140
    ctx.move_to(x, 980); ctx.line_to(x, 1260); rgba(ctx, ORANGE, pa); ctx.set_line_width(8); ctx.stroke()
    arrow_head(ctx, x, 970, -math.pi / 2, 40, ORANGE, pa); arrow_head(ctx, x, 1270, math.pi / 2, 40, ORANGE, pa)
    glow_dot(ctx, x, top + 30, 14, ORANGE, pa)
    label(ctx, "sube y baja", x + 10, 1330, 40, ORANGE, pa, box=True)
    pb = eo(prog(t, 1.0, 1.4))
    if pb > 0:
        ctx.arc(EX, CCY, 290, th - math.pi / 2 - 1.2, th - math.pi / 2)
        glow_stroke(ctx, GREEN, 7, pb)
        an = th - math.pi / 2
        arrow_head(ctx, EX + 290 * math.cos(an), CCY + 290 * math.sin(an), an + math.pi / 2, 40, GREEN, pb)
        label(ctx, "gira", EX + 330, CCY + 300, 46, GREEN, pb, box=True)

def s_compress(ctx, t, d):
    th = math.radians(185 + 165 * eio(prog(t, 0.2, d - 0.3)))
    draw_engine(ctx, th, t)
    top, _ = piston_top(th)
    label(ctx, "compresión", EX, (HEAD + top) / 2, 44, FRESH, eo(prog(t, 0.5, 0.9)), box=True)
    arrow_head(ctx, 120 + 0, 1000, -math.pi / 2, 0.1, WHITE, 0)
    label(ctx, "entra mezcla", 230, 1560, 40, FRESH, eo(prog(t, 1.2, 1.6)), box=True)
    ctx.move_to(EX + 200, top + 100); ctx.line_to(EX + 200, top + 10)
    glow_stroke(ctx, WHITE, 6, eo(prog(t, 0.3, 0.6)) * 0.8)
    arrow_head(ctx, EX + 200, top, -math.pi / 2, 30, WHITE, eo(prog(t, 0.3, 0.6)) * 0.8)

def s_spark(ctx, t, d):
    th = math.radians(350 + 30 * eio(prog(t, 0.2, d - 0.2)))
    draw_engine(ctx, th, t)
    dd = math.degrees(th) % 360
    if dd > 355 or dd < 8:
        spark(ctx, EX, HEAD + 8, 1.8, t)
    pb = eback(prog(t, 1.6, 2.0))
    if pb > 0:
        label(ctx, "¡BUM!", 860, 720, 90 * pb, YELLOW, 1)
    label(ctx, "chispa", 230, HEAD - 150, 46, (0.75, 0.9, 1.0), eo(prog(t, 0.4, 0.8)), box=True)

def s_power(ctx, t, d):
    th = math.radians(10 + 110 * eio(prog(t, 0.1, d - 0.2)))
    draw_engine(ctx, th, t)
    top, _ = piston_top(th)
    pa = 1 - prog(t, 2.6, 3.2)
    for k in (-1, 0, 1):
        x = EX + k * 90
        ctx.move_to(x, top - 120); ctx.line_to(x, top - 20); glow_stroke(ctx, YELLOW, 7, pa)
        arrow_head(ctx, x, top - 10, math.pi / 2, 34, YELLOW, pa)
    label(ctx, "empuje", 200, top - 40, 50, ORANGE, eo(prog(t, 0.4, 0.8)) * pa, box=True)

def s_scavenge(ctx, t, d):
    th = math.radians(105 + 150 * eio(prog(t, 0.1, d - 0.2)))
    draw_engine(ctx, th, t)
    label(ctx, "sale el humo", 900, 980, 44, (0.8, 0.8, 0.85), eo(prog(t, 0.3, 0.7)), box=True)
    label(ctx, "entra mezcla", 180, 1030, 44, FRESH, eo(prog(t, 1.0, 1.4)), box=True)

def s_count(ctx, t, d):
    for i, (cx, name, per, col) in enumerate(((290, "2 tiempos", 1, ORANGE), (790, "4 tiempos", 2, CYAN))):
        cy = 1150
        ang = t * 2 * math.pi * 0.9
        ctx.arc(cx, cy, 170, 0, 6.3); fill_grad(ctx, STEEL, cx - 170, cy - 170, cx + 170, cy + 170); ctx.fill()
        ctx.arc(cx, cy, 140, 0, 6.3); rgba(ctx, (0.05, 0.06, 0.12)); ctx.fill()
        px, py = cx + 110 * math.sin(ang), cy - 110 * math.cos(ang)
        ctx.move_to(cx, cy); ctx.line_to(px, py); rgba(ctx, col); ctx.set_line_width(14); ctx.stroke()
        glow_dot(ctx, px, py, 16, col)
        revs = ang / (2 * math.pi)
        booms = int(revs / per + 1e-6)
        frac = (revs / per) % 1
        if frac < 0.15 and revs > 0.5:
            glow_dot(ctx, cx, cy - 280, 50 * (1 - frac / 0.15) + 12, YELLOW, 1 - frac / 0.15)
            label(ctx, "¡BUM!", cx, cy - 280, 50, YELLOW, 1 - frac / 0.15)
        label(ctx, name, cx, cy + 250, 52, col, 1, box=True)
        label(ctx, f"vueltas: {int(revs)}", cx, cy + 350, 40, WHITE, 1, NORM)
        label(ctx, f"explosiones: {booms}", cx, cy + 410, 40, YELLOW, 1)

def s_ports(ctx, t, d):
    th = t * 1.6 + 1.5
    draw_engine(ctx, th, t, port_glow=0.6 + 0.4 * math.sin(t * 6))
    label(ctx, "lumbreras", 860, 1250, 50, YELLOW, eo(prog(t, 0.5, 0.9)), box=True)
    label(ctx, "(agujeros en la pared)", 860, 1330, 34, WHITE, eo(prog(t, 0.8, 1.2)), NORM)

def jerrycan(ctx, x, y, s, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rr(ctx, -120, -150, 240, 300, 26); fill_grad(ctx, [(0, (0.95, 0.25, 0.2)), (0.5, (0.8, 0.1, 0.1)), (1, (0.45, 0.05, 0.05))], -120, 0, 120, 0, a); ctx.fill()
    ctx.move_to(-90, -100); ctx.line_to(90, 100); ctx.move_to(90, -100); ctx.line_to(-90, 100)
    rgba(ctx, (0.5, 0.05, 0.05), a); ctx.set_line_width(10); ctx.stroke()
    rr(ctx, -80, -200, 90, 50, 12); rgba(ctx, (0.6, 0.08, 0.08), a); ctx.fill()
    metal_rect(ctx, 40, -210, 50, 60, STEEL, False, 6, a)
    ctx.restore()

def s_oil(ctx, t, d):
    jerrycan(ctx, 330, 1350, 1.4)
    label(ctx, "gasolina", 330, 1640, 44, WHITE, 1, NORM, box=True)
    # oil bottle pouring
    p = eo(prog(t, 0.4, 1.0))
    bx, by = 760, 900
    ctx.save(); ctx.translate(bx, by); ctx.rotate(-0.9 * p)
    rr(ctx, -70, -130, 140, 240, 20); fill_grad(ctx, [(0, (0.15, 0.35, 0.15)), (0.5, (0.3, 0.6, 0.3)), (1, (0.1, 0.25, 0.1))], -70, 0, 70, 0); ctx.fill()
    rr(ctx, -25, -185, 50, 60, 8); rgba(ctx, (0.9, 0.85, 0.2)); ctx.fill()
    label(ctx, "ACEITE", 0, 0, 30, WHITE)
    ctx.restore()
    if t > 1.0:
        sx, sy = bx - 170, by - 90
        for k in range(8):
            q = (t * 1.5 + k / 8) % 1
            glow_dot(ctx, sx - 120 * q, sy + 280 * q * q + 40 * q, 9, YELLOW, 0.9)
    pm = eback(prog(t, 1.8, 2.3))
    label(ctx, "mezcla 50:1", 760, 1350, 64 * pm, YELLOW, pm, box=True)
    label(ctx, "(2 % de aceite)", 760, 1450, 38, WHITE, pm, NORM)

def s_smoke(ctx, t, d):
    th = t * 2 * math.pi * 1.5
    draw_engine(ctx, th, t, smoke=1.0)
    spark_if(ctx, th, t)
    label(ctx, "parte de la mezcla", 780, 1730, 38, WHITE, eo(prog(t, 0.6, 1.0)), NORM, box=True)
    label(ctx, "se escapa sin quemar", 780, 1800, 42, RED, eo(prog(t, 0.8, 1.2)), BOLD, box=True)

def s_fact(ctx, t, d):
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 140); ctx.scale(pb, pb); ctx.rotate(-0.04)
        rr(ctx, -170, -42, 340, 84, 20); rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
        label(ctx, "¡DATO!", CX, 140, 54 * pb, NAVY)
    base = 1600
    hgt = 900 * eo(prog(t, 0.5, 1.6))
    x0, w = 330, 520
    if hgt > 2:
        ctx.rectangle(x0, base - hgt, w, hgt); fill_grad(ctx, DARK, x0, 0, x0 + w, 0); ctx.fill()
        for k in range(7):
            cxk = x0 + 40 + k * 68
            ctx.rectangle(cxk, base - hgt + 40, 46, hgt * 0.55)
            fill_grad(ctx, STEEL, cxk, 0, cxk + 46, 0, 0.8); ctx.fill()
        ctx.rectangle(x0 - 20, base - hgt * 0.35, w + 40, 30); fill_grad(ctx, BRASS, 0, base - hgt * 0.35, 0, base - hgt * 0.35 + 30); ctx.fill()
    # person
    pp = eo(prog(t, 1.4, 1.8))
    if pp > 0:
        ph = 900 * 1.75 / 13.5
        px = 940
        ctx.arc(px, base - ph + 12, 12, 0, 6.3); rgba(ctx, YELLOW, pp); ctx.fill()
        ctx.move_to(px, base - ph + 26); ctx.line_to(px, base - ph * 0.45); ctx.move_to(px, base - ph * 0.45); ctx.line_to(px - 12, base)
        ctx.move_to(px, base - ph * 0.45); ctx.line_to(px + 12, base); ctx.move_to(px - 16, base - ph * 0.7); ctx.line_to(px + 16, base - ph * 0.7)
        rgba(ctx, YELLOW, pp); ctx.set_line_width(6); ctx.stroke()
        label(ctx, "tú", px, base - ph - 40, 36, YELLOW, pp)
    # height bar
    if hgt > 2:
        ctx.move_to(250, base); ctx.line_to(250, base - hgt); rgba(ctx, CYAN); ctx.set_line_width(5); ctx.stroke()
        label(ctx, "13,5 m", 170, base - hgt / 2, 46, CYAN, eo(prog(t, 1.2, 1.6)), box=True)
    ctx.move_to(60, base); ctx.line_to(1020, base); rgba(ctx, WHITE, 0.5); ctx.set_line_width(3); ctx.stroke()
    label(ctx, "2.300 toneladas", CX, 1690, 44, YELLOW, eo(prog(t, 1.9, 2.3)))
    label(ctx, "107.000 caballos · mueve portacontenedores", CX, 1760, 34, WHITE, eo(prog(t, 2.3, 2.7)), NORM)

def s_cta(ctx, t, d):
    th = t * 2 * math.pi * 0.8
    ctx.save(); ctx.translate(-200, 120); ctx.scale(1, 1)
    ctx.restore()
    draw_engine(ctx, th, t, a=0.35, show_flow=False)
    for i, (x, s, c) in enumerate(((300, "2T", ORANGE), (780, "4T", CYAN))):
        p = eback(prog(t, 0.3 + i * 0.2, 0.8 + i * 0.2))
        if p > 0:
            ctx.arc(x, 1150, 150 * p, 0, 6.3); rgba(ctx, c, 0.9); ctx.fill()
            label(ctx, s, x, 1150, 110 * p, NAVY)
    label(ctx, "VS", CX, 1150, 70, WHITE, eo(prog(t, 0.8, 1.1)))
    label(ctx, "¡Te leo en comentarios!", CX, 1500, 48, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)

SCENES = [
    (3.0, "¿Qué pasa dentro de un motor de 2 tiempos?", {5, 6, 7}, ORANGE, s_hook),
    (4.0, "Sus piezas: pistón, biela y cigüeñal", {2, 3, 5}, ORANGE, s_parts),
    (4.0, "El pistón sube y baja, el cigüeñal gira", {1, 6, 7}, GREEN, s_motion),
    (4.5, "Tiempo 1: sube y comprime la mezcla", {0, 1, 4}, CYAN, s_compress),
    (3.5, "La bujía hace saltar una chispa", {1, 5}, YELLOW, s_spark),
    (4.0, "Tiempo 2: la explosión empuja el pistón", {0, 1, 3}, ORANGE, s_power),
    (4.5, "Abajo sale el humo y entra mezcla nueva", {3, 6, 7}, CYAN, s_scavenge),
    (4.0, "¡Una explosión en cada vuelta!", {1, 4}, YELLOW, s_count),
    (4.0, "Sin válvulas: el pistón abre y cierra", {0, 1}, YELLOW, s_ports),
    (4.0, "El aceite va mezclado con la gasolina", {1, 3}, YELLOW, s_oil),
    (3.5, "Por eso echan humo y contaminan más", {3, 5, 6}, RED, s_smoke),
    (5.0, "El mayor motor del mundo: 2 tiempos", {1, 2, 5, 6}, YELLOW, s_fact, 430),
    (3.5, "¿2 tiempos o 4 tiempos? ¡Comenta!", {0, 1, 3, 4}, CYAN, s_cta),
]

if __name__ == "__main__":
    run(SCENES)
