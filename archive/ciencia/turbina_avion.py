import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from engine import *

AX = CX
Y_IN = 720      # intake lip
Y_FAN = 840
Y_CORE = 980    # core inlet splitter
Y_COMB = (1270, 1390)
Y_TURB = (1400, 1530)
Y_END = 1720
HOT = (1.0, 0.55, 0.12)

def core_half(y):
    """Half-width of the core flow path (outer) at height y."""
    pts = [(Y_CORE, 200), (1080, 185), (1260, 120), (1270, 150), (1390, 150), (1400, 130), (1530, 175), (1720, 120)]
    for (y0, w0), (y1, w1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return w0 + (w1 - w0) * (y - y0) / max(1, y1 - y0)
    return pts[-1][1] if y > pts[-1][0] else pts[0][1]

def hub_half(y):
    pts = [(Y_CORE, 70), (1260, 75), (1400, 60), (1530, 80), (1720, 20)]
    for (y0, w0), (y1, w1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return w0 + (w1 - w0) * (y - y0) / max(1, y1 - y0)
    return 70

def rotor_band(ctx, y, h, r_in, r_out, phase, col_stops, nblades=14, a=1.0, glow=0.0, hot=False, bg=0.55):
    for side in (-1, 1):
        x0 = AX + side * r_in; x1 = AX + side * r_out
        ctx.rectangle(min(x0, x1), y - h / 2, abs(x1 - x0), h)
        fill_grad(ctx, col_stops, 0, y - h / 2, 0, y + h / 2, bg * a); ctx.fill()
    # blades seen from the side: slivers at x = R sin(angle)
    for k in range(nblades):
        an = phase + k * 2 * math.pi / nblades
        c = math.cos(an)
        if c <= 0: continue
        s = math.sin(an)
        for side in (-1, 1):
            xm = AX + side * (r_in + (r_out - r_in) * 0.5)
            # draw blade as quad spanning r_in..r_out, offset in y by s (twist look)
            ctx.move_to(AX + side * r_in, y + s * h * 0.35 - h * 0.3 * c)
            ctx.line_to(AX + side * r_out, y + s * h * 0.5 - h * 0.45 * c)
            ctx.line_to(AX + side * r_out, y + s * h * 0.5 + h * 0.45 * c)
            ctx.line_to(AX + side * r_in, y + s * h * 0.35 + h * 0.3 * c)
            ctx.close_path()
            br = 0.45 + 0.55 * c
            if hot: rgba(ctx, (1.0 * br, 0.55 * br, 0.25 * br), a)
            else: rgba(ctx, (0.85 * br, 0.88 * br, 0.95 * br), a)
            ctx.fill()
    if glow > 0:
        for side in (-1, 1):
            ctx.rectangle(min(AX + side * r_in, AX + side * r_out), y - h / 2, abs(r_out - r_in), h)
            glow_stroke(ctx, YELLOW, 3, glow)

def draw_turbofan(ctx, t, spin=1.0, a=1.0, hl=None, flow=True, flame=1.0, shaft_glow=0.0, bypass_hl=0.0, core_dim=0.0):
    hl = hl or {}
    ph = t * 9 * spin
    # nacelle walls
    for side in (-1, 1):
        ctx.move_to(AX + side * 400, Y_IN + 20)
        ctx.curve_to(AX + side * 440, Y_IN - 30, AX + side * 470, Y_IN - 10, AX + side * 470, Y_IN + 60)
        ctx.line_to(AX + side * 455, 1330); ctx.line_to(AX + side * 400, 1350); ctx.line_to(AX + side * 395, Y_IN + 60); ctx.close_path()
        fill_grad(ctx, STEEL, AX + side * 470, 0, AX + side * 395, 0, a); ctx.fill()
    # bypass duct interior
    ctx.rectangle(AX - 395, Y_IN + 40, 790, 1350 - Y_IN - 40); fill_grad(ctx, [(0, (0.07, 0.1, 0.2)), (0.5, (0.03, 0.05, 0.11)), (1, (0.07, 0.1, 0.2))], AX - 395, 0, AX + 395, 0, a); ctx.fill()
    # core cowl
    for side in (-1, 1):
        ctx.move_to(AX + side * 205, Y_CORE); ctx.line_to(AX + side * 240, 1100); ctx.line_to(AX + side * 235, 1500)
        ctx.line_to(AX + side * 185, 1540); ctx.line_to(AX + side * core_half(1530) , 1530); ctx.line_to(AX + side * core_half(Y_CORE), Y_CORE); ctx.close_path()
        fill_grad(ctx, DARK, AX + side * 240, 0, AX + side * 180, 0, a); ctx.fill()
    # core flow path background
    ctx.move_to(AX - core_half(Y_CORE), Y_CORE)
    yy = Y_CORE
    while yy <= Y_END: ctx.line_to(AX - core_half(yy), yy); yy += 10
    yy = Y_END
    while yy >= Y_CORE: ctx.line_to(AX + core_half(yy), yy); yy -= 10
    ctx.close_path(); rgba(ctx, (0.04, 0.05, 0.1), a); ctx.fill()
    # hot gas glow in combustor/turbine/nozzle
    if flame > 0:
        g = cairo.LinearGradient(0, Y_COMB[0], 0, Y_END + 200)
        g.add_color_stop_rgba(0, 1, 0.8, 0.3, 0.0)
        g.add_color_stop_rgba(0.12, 1, 0.65, 0.2, 0.75 * flame * a)
        g.add_color_stop_rgba(0.5, 1, 0.4, 0.1, 0.5 * flame * a)
        g.add_color_stop_rgba(1, 0.9, 0.2, 0.1, 0)
        ctx.move_to(AX - core_half(Y_COMB[0]), Y_COMB[0])
        yy = Y_COMB[0]
        while yy <= Y_END: ctx.line_to(AX - core_half(yy), yy); yy += 10
        ctx.line_to(AX - 140, Y_END + 220); ctx.line_to(AX + 140, Y_END + 220)
        yy = Y_END
        while yy >= Y_COMB[0]: ctx.line_to(AX + core_half(yy), yy); yy -= 10
        ctx.close_path(); ctx.set_source(g); ctx.fill()
    # compressor stages
    for i in range(9):
        y = 1000 + i * 30
        rotor_band(ctx, y, 18, hub_half(y), core_half(y) - 4, ph * (1.0 if i < 3 else 1.6) + i, STEEL, 16, a * (1 - 0.6 * core_dim), hl.get('comp', 0))
    # combustor liners
    for side in (-1, 1):
        ctx.new_path(); rr(ctx, (AX + 90) if side > 0 else (AX - 150), Y_COMB[0] + 5, 60, Y_COMB[1] - Y_COMB[0] - 10, 18)
        rgba(ctx, (0.25, 0.27, 0.3), 0.8 * a); ctx.set_line_width(5); ctx.stroke()
        if flame > 0:
            for k in range(5):
                q = (t * 2.5 + k / 5) % 1
                fx = AX + side * (120 + 8 * math.sin(t * 20 + k))
                fy = Y_COMB[0] + 20 + q * (Y_COMB[1] - Y_COMB[0] - 30)
                glow_dot(ctx, fx, fy, 14 * (1 - q * 0.5), (1, 0.85 - 0.4 * q, 0.3), flame * a * (1 - q * 0.6))
    if hl.get('comb', 0) > 0:
        ctx.rectangle(AX - core_half(1300) - 10, Y_COMB[0], 2 * core_half(1300) + 20, Y_COMB[1] - Y_COMB[0])
        glow_stroke(ctx, YELLOW, 4, hl['comb'])
    # turbine stages
    for i in range(4):
        y = Y_TURB[0] + 15 + i * 33
        rotor_band(ctx, y, 20, hub_half(y), core_half(y) - 4, ph * 1.6 + i * 0.7, [(0, (0.6, 0.35, 0.2)), (1, (0.4, 0.2, 0.1))], 16, a, hl.get('turb', 0), hot=True)
    # shaft
    ctx.rectangle(AX - 16, Y_FAN, 32, Y_TURB[1] - Y_FAN)
    fill_grad(ctx, STEEL, AX - 16, 0, AX + 16, 0, a); ctx.fill()
    if shaft_glow > 0:
        ctx.move_to(AX, Y_TURB[1]); ctx.line_to(AX, Y_FAN); glow_stroke(ctx, GREEN, 8, shaft_glow)
    # hub/inner cone
    ctx.move_to(AX - 70, Y_CORE); ctx.line_to(AX - 75, 1260); ctx.line_to(AX - 60, 1400); ctx.line_to(AX - 80, 1530)
    ctx.line_to(AX, Y_END + 40); ctx.line_to(AX + 80, 1530); ctx.line_to(AX + 60, 1400); ctx.line_to(AX + 75, 1260); ctx.line_to(AX + 70, Y_CORE); ctx.close_path()
    fill_grad(ctx, DARK, AX - 80, 0, AX + 80, 0, 0.55 * a); ctx.fill()
    # fan
    rotor_band(ctx, Y_FAN, 90, 80, 392, ph * 0.55, STEEL, 12, a, hl.get('fan', 0), bg=0.12)
    # spinner
    ctx.move_to(AX - 85, Y_FAN + 20); ctx.curve_to(AX - 80, Y_FAN - 70, AX - 20, Y_FAN - 120, AX, Y_FAN - 125)
    ctx.curve_to(AX + 20, Y_FAN - 120, AX + 80, Y_FAN - 70, AX + 85, Y_FAN + 20); ctx.close_path()
    fill_grad(ctx, STEEL, AX - 85, 0, AX + 85, 0, a); ctx.fill()
    ctx.save(); ctx.translate(AX, Y_FAN - 40)
    sw = ph * 0.55
    ctx.move_to(60 * math.sin(sw), -60); ctx.curve_to(40 * math.sin(sw + 1), -20, 30 * math.sin(sw + 2), 20, 70 * math.sin(sw + 1.5), 50)
    ctx.restore(); rgba(ctx, WHITE, 0.6 * a); ctx.set_line_width(5); ctx.stroke()
    # flows
    if flow:
        # bypass
        for side in (-1, 1):
            for lane in (0, 1):
                xl = AX + side * (290 + lane * 60)
                path = [(xl, 520), (xl, Y_FAN - 40), (xl, Y_FAN + 60), (xl - side * 10, 1350), (xl - side * 30, 1900)]
                ca = (0.4 + 0.6 * bypass_hl) * a
                flow_dots(ctx, path, t, 7, 0.9, CYAN, 7 + 3 * bypass_hl, ca, phase=lane * 0.3 + side * 0.1)
        # core
        for side in (-1, 1):
            n = 14
            for k in range(n):
                q = (t * 0.55 + k / n + (0.03 if side > 0 else 0)) % 1
                y = 560 + q * (Y_END + 180 - 560)
                if y < Y_CORE:
                    x = AX + side * (150 - 40 * (y - 560) / (Y_CORE - 560) * 0) - side * 0
                    x = AX + side * (160 if y < Y_FAN else 140)
                else:
                    x = AX + side * (hub_half(y) + core_half(y)) / 2 if y < Y_END else AX + side * 70
                if y < Y_CORE: c, r = CYAN, 7
                elif y < Y_COMB[0]: c, r = (0.7, 0.85, 1.0), 6 - 2 * (y - Y_CORE) / (Y_COMB[0] - Y_CORE)
                elif y < Y_TURB[0]: c, r = (1.0, 0.85, 0.3), 9
                else: c, r = HOT, 9
                glow_dot(ctx, x, y, max(3, r), c, a * (1 - core_dim * 0.7))

def front_fan(ctx, cx, cy, R, t, a=1.0):
    ctx.arc(cx, cy, R + 50, 0, 6.3); fill_grad(ctx, STEEL, cx - R, cy - R - 50, cx + R, cy + R + 50, a); ctx.fill()
    ctx.arc(cx, cy, R + 8, 0, 6.3); rgba(ctx, (0.03, 0.04, 0.08), a); ctx.fill()
    n = 22; rot = t * 4
    for k in range(n):
        an = rot + k * 2 * math.pi / n
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(an)
        ctx.move_to(R * 0.22, -10); ctx.curve_to(R * 0.5, -40, R * 0.8, -30, R, -55)
        ctx.line_to(R, 30); ctx.curve_to(R * 0.7, 20, R * 0.45, 30, R * 0.22, 25); ctx.close_path()
        ctx.restore()
        br = 0.6 + 0.4 * math.cos(an - 0.8)
        g = cairo.LinearGradient(cx, cy, cx + R * math.cos(an), cy + R * math.sin(an))
        g.add_color_stop_rgba(0, 0.4 * br, 0.42 * br, 0.48 * br, a); g.add_color_stop_rgba(1, 0.85 * br, 0.88 * br, 0.95 * br, a)
        ctx.set_source(g); ctx.fill()
    ctx.arc(cx, cy, R * 0.24, 0, 6.3)
    g = cairo.RadialGradient(cx - 30, cy - 30, 5, cx, cy, R * 0.24)
    g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, 0.4, 0.42, 0.48, a); ctx.set_source(g); ctx.fill()
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot)
    ctx.move_to(0, 0)
    for i in range(30):
        u = i / 29; ctx.line_to(R * 0.2 * u * math.cos(u * 5), R * 0.2 * u * math.sin(u * 5))
    ctx.restore(); rgba(ctx, WHITE, a); ctx.set_line_width(6); ctx.stroke()

# ------------------------------------------------------------------ scenes
def s_hook(ctx, t, d):
    p = eback(prog(t, 0, 0.5))
    front_fan(ctx, CX, 1180, 400 * p, t, 1)
    for k in range(12):
        q = (t * 0.8 + k / 12) % 1
        an = k * 0.52
        r = 700 * (1 - q)
        glow_dot(ctx, CX + r * math.cos(an), 1180 + r * math.sin(an), 6, CYAN, q)

def s_four(ctx, t, d):
    draw_turbofan(ctx, t, flame=eo(prog(t, 1.6, 2.2)))
    steps = [("1 aspira", Y_FAN, CYAN, 0.4), ("2 comprime", 1130, (0.7, 0.85, 1.0), 0.9), ("3 quema", 1330, YELLOW, 1.4), ("4 expulsa", 1600, ORANGE, 1.9)]
    for name, y, c, st in steps:
        p = eo(prog(t, st, st + 0.35))
        if p > 0:
            ctx.move_to(AX + 250, y); ctx.line_to(AX + 250 + 120 * p, y); rgba(ctx, c, p); ctx.set_line_width(4); ctx.stroke()
            label(ctx, name, 900, y, 44, c, p, box=True)

def s_fan(ctx, t, d):
    draw_turbofan(ctx, t, hl={'fan': 0.6 + 0.4 * math.sin(t * 6)})
    label(ctx, "ventilador", 880, Y_FAN - 120, 46, CYAN, eo(prog(t, 0.5, 0.9)), box=True)
    label(ctx, "aire", 150, 680, 50, CYAN, eo(prog(t, 0.3, 0.7)), box=True)

def s_comp(ctx, t, d):
    draw_turbofan(ctx, t, hl={'comp': 0.6 + 0.4 * math.sin(t * 6)})
    label(ctx, "compresor", 860, 1130, 46, (0.7, 0.85, 1.0), eo(prog(t, 0.4, 0.8)), box=True)
    label(ctx, "~40 veces más presión", CX, 1880, 44, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)

def s_comb(ctx, t, d):
    draw_turbofan(ctx, t, hl={'comb': 0.6 + 0.4 * math.sin(t * 6)}, flame=eo(prog(t, 0.3, 1.0)))
    label(ctx, "cámara de combustión", 820, 1330, 40, YELLOW, eo(prog(t, 0.6, 1.0)), box=True)
    label(ctx, "+ queroseno", 200, 1330, 40, ORANGE, eo(prog(t, 0.9, 1.3)), box=True)

def s_turb(ctx, t, d):
    draw_turbofan(ctx, t, hl={'turb': 0.6 + 0.4 * math.sin(t * 6)})
    label(ctx, "turbina", 870, 1465, 48, ORANGE, eo(prog(t, 0.4, 0.8)), box=True)

def s_shaft(ctx, t, d):
    g = 0.6 + 0.4 * math.sin(t * 6)
    draw_turbofan(ctx, t, shaft_glow=eo(prog(t, 0.3, 0.8)) * g, hl={'fan': 0.5 * eo(prog(t, 1.0, 1.4)), 'turb': 0.5})
    pa = eo(prog(t, 0.6, 1.4))
    if pa > 0:
        for k in range(4):
            q = (t * 0.9 + k / 4) % 1
            glow_dot(ctx, AX, Y_TURB[1] - q * (Y_TURB[1] - Y_FAN), 12, GREEN, pa)
    label(ctx, "eje", 200, 1150, 52, GREEN, eo(prog(t, 0.5, 0.9)), box=True)

def s_newton(ctx, t, d):
    lift = 60 * eio(prog(t, 1.0, 2.5))
    ctx.save(); ctx.translate(0, -lift)
    draw_turbofan(ctx, t)
    ctx.restore()
    pa = eo(prog(t, 0.3, 0.8))
    for k in (-1, 0, 1):
        x = AX + k * 150
        ctx.move_to(x, 1750 - lift); ctx.line_to(x, 1880); glow_stroke(ctx, ORANGE, 8, pa)
        arrow_head(ctx, x, 1890, math.pi / 2, 40, ORANGE, pa)
    pb = eo(prog(t, 1.0, 1.4))
    ctx.move_to(940, 1300); ctx.line_to(940, 900); glow_stroke(ctx, GREEN, 12, pb)
    arrow_head(ctx, 940, 880, -math.pi / 2, 60, GREEN, pb)
    label(ctx, "empuje", 940, 1360, 44, GREEN, pb, box=True)
    label(ctx, "acción y reacción", 190, 1500, 36, WHITE, eo(prog(t, 2.0, 2.4)), NORM, box=True)

def s_bypass(ctx, t, d):
    draw_turbofan(ctx, t, bypass_hl=1.0, core_dim=0.5)
    pa = eo(prog(t, 0.6, 1.0))
    label(ctx, "aire que rodea", 220, 1900 - 80, 40, CYAN, pa, box=True)
    label(ctx, "el núcleo", 220, 1900 - 20, 40, CYAN, pa)
    label(ctx, "≈ 80 %", 860, 1830, 60, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)

def s_fact(ctx, t, d):
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 140); ctx.scale(pb, pb); ctx.rotate(-0.04)
        rr(ctx, -170, -42, 340, 84, 20); rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
        label(ctx, "¡DATO!", CX, 140, 54 * pb, NAVY)
    # thermometer
    tx, ty0, ty1 = 300, 820, 1640
    rr(ctx, tx - 45, ty0, 90, ty1 - ty0, 45); rgba(ctx, (0.85, 0.88, 0.95), 0.25); ctx.fill_preserve(); rgba(ctx, WHITE, 0.8); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(tx, ty1 + 40, 80, 0, 6.3); rgba(ctx, RED); ctx.fill()
    lvl = eio(prog(t, 0.4, 2.0))
    ht = (ty1 - ty0 - 40) * lvl
    rr(ctx, tx - 28, ty1 - ht, 56, ht + 40, 28)
    fill_grad(ctx, [(0, (1, 0.85, 0.3)), (1, (1, 0.2, 0.15))], 0, ty1 - ht, 0, ty1, 1); ctx.fill()
    temp = int(1600 * lvl / 50) * 50
    label(ctx, f"{temp:,} °C".replace(",", "."), tx, ty1 - ht - 70, 60, YELLOW, clamp(lvl * 3), box=True)
    # melting line
    my = ty1 - (ty1 - ty0 - 40) * 0.8
    pm = eo(prog(t, 1.4, 1.8))
    ctx.move_to(tx + 60, my); ctx.line_to(1000, my); ctx.set_dash([16, 10]); rgba(ctx, CYAN, pm); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    label(ctx, "aquí se fundiría", 720, my - 50, 40, CYAN, pm, box=True)
    label(ctx, "el metal de las palas", 720, my + 30, 36, WHITE, pm, NORM)
    # blade
    pbl = eo(prog(t, 2.2, 2.7))
    if pbl > 0:
        bx, by = 720, 1450
        ctx.move_to(bx - 70, by + 130); ctx.curve_to(bx - 110, by, bx - 60, by - 150, bx + 10, by - 170)
        ctx.curve_to(bx + 60, by - 120, bx + 70, by, bx + 60, by + 130); ctx.close_path()
        fill_grad(ctx, [(0, (1, 0.6, 0.25)), (1, (0.6, 0.25, 0.1))], bx - 100, by, bx + 70, by, pbl); ctx.fill()
        label(ctx, "¡y no se funden!", bx, by + 210, 46, YELLOW, pbl, box=True)

def s_holes(ctx, t, d):
    bx, by = CX, 1200
    # hot flow behind
    for k in range(16):
        q = (t * 0.7 + k / 16) % 1
        y = 700 + q * 1100
        x = 200 + (k * 73) % 700
        glow_dot(ctx, x, y, 10, HOT, 0.6 * (1 - abs(q - 0.5) * 2))
    # big blade
    ctx.move_to(bx - 200, by + 420); ctx.curve_to(bx - 300, by + 50, bx - 180, by - 380, bx + 20, by - 430)
    ctx.curve_to(bx + 160, by - 330, bx + 200, by, bx + 170, by + 420); ctx.close_path()
    fill_grad(ctx, [(0, (0.95, 0.7, 0.45)), (0.4, (1, 0.85, 0.6)), (1, (0.55, 0.3, 0.15))], bx - 260, by, bx + 200, by); ctx.fill_preserve()
    rgba(ctx, (0.3, 0.15, 0.05)); ctx.set_line_width(4); ctx.stroke()
    ctx.rectangle(bx - 240, by + 420, 440, 90); fill_grad(ctx, STEEL, bx - 240, 0, bx + 200, 0); ctx.fill()
    holes = []
    for r in range(7):
        for c in range(4):
            holes.append((bx - 150 + c * 80 + (r % 2) * 30, by - 300 + r * 100))
    for (hx, hy) in holes:
        ctx.arc(hx, hy, 9, 0, 6.3); rgba(ctx, (0.15, 0.08, 0.04)); ctx.fill()
    pa = eo(prog(t, 0.6, 1.2))
    if pa > 0:
        for i, (hx, hy) in enumerate(holes):
            q = (t * 1.3 + i * 0.13) % 1
            ctx.move_to(hx, hy); ctx.curve_to(hx + 20 * q, hy + 30 * q, hx + 30 * q, hy + 60 * q, hx + 25 * q, hy + 90 * q)
            rgba(ctx, CYAN, pa * (1 - q)); ctx.set_line_width(6); ctx.stroke()
    label(ctx, "aire frío", 880, 900, 48, CYAN, pa, box=True)
    label(ctx, "pala de turbina", 220, 1720, 40, ORANGE, eo(prog(t, 0.2, 0.6)), NORM, box=True)

def s_cta(ctx, t, d):
    front_fan(ctx, 400, 1250, 280 * eback(prog(t, 0, 0.5)), t, 1)
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
    (3.0, "¿Cómo empuja una turbina a un avión?", {3, 4, 6}, CYAN, s_hook),
    (4.0, "Por dentro hace 4 cosas", {3, 4}, YELLOW, s_four, 380),
    (4.0, "1. El ventilador aspira muchísimo aire", {2, 5}, CYAN, s_fan, 380),
    (4.0, "2. El compresor lo aprieta", {2, 4}, (0.7, 0.85, 1.0), s_comp, 380),
    (4.0, "3. Se mezcla con combustible y arde", {4, 6}, ORANGE, s_comb, 380),
    (4.0, "4. Los gases calientes giran la turbina", {3, 6}, ORANGE, s_turb, 380),
    (4.0, "Y la turbina mueve el ventilador", {2, 5}, GREEN, s_shaft, 380),
    (4.0, "Echa aire atrás y el avión va adelante", {2, 7}, GREEN, s_newton, 360),
    (4.0, "El ventilador da la mayor parte del empuje", {1, 4, 5, 7}, CYAN, s_bypass, 380),
    (4.5, "Sus gases derretirían las palas de metal", {2}, RED, s_fact, 430),
    (4.5, "Las salva aire frío por miles de agujeritos", {3, 4, 7}, CYAN, s_holes),
    (3.5, "¿Qué avión te gustaría ver por dentro?", {1}, CYAN, s_cta),
]

if __name__ == "__main__":
    run(SCENES)
