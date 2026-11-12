import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from engine import *

AXY = 1030          # bore axis
SLIDE_BACK = 190
COP = [(0, (0.55, 0.25, 0.1)), (0.35, (1.0, 0.7, 0.45)), (0.7, (0.8, 0.42, 0.2)), (1, (0.45, 0.2, 0.08))]
POLY = [(0, (0.2, 0.21, 0.24)), (0.5, (0.12, 0.13, 0.15)), (1, (0.05, 0.05, 0.06))]
GAS = (1.0, 0.6, 0.15)

def cartridge(ctx, x, y, s=1.0, ang=0.0, a=1.0, with_bullet=True):
    """Small side-view cartridge, rim at local x=0, pointing +x."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.rectangle(0, -17, 80, 34); fill_grad(ctx, BRASS, 0, -17, 0, 17, a); ctx.fill()
    ctx.rectangle(-4, -18, 8, 36); fill_grad(ctx, BRASS, 0, -18, 0, 18, a); ctx.fill()
    if with_bullet:
        ctx.move_to(80, -15); ctx.line_to(105, -15); ctx.curve_to(130, -13, 140, -5, 142, 0)
        ctx.curve_to(140, 5, 130, 13, 105, 15); ctx.line_to(80, 15); ctx.close_path()
        fill_grad(ctx, COP, 0, -15, 0, 15, a); ctx.fill()
    ctx.restore()

def draw_pistol(ctx, t, st):
    a = st.get('a', 1.0)
    so = -SLIDE_BACK * st.get('slide', 0.0)
    # --- frame & grip (polymer)
    ctx.move_to(250, 1110); ctx.line_to(1000, 1110); ctx.line_to(1000, 1160); ctx.line_to(660, 1160)
    ctx.curve_to(650, 1300, 620, 1310, 470, 1300); ctx.curve_to(450, 1250, 440, 1200, 445, 1160)
    ctx.line_to(430, 1160); ctx.line_to(330, 1650); ctx.line_to(150, 1650); ctx.line_to(225, 1200); ctx.line_to(230, 1110); ctx.close_path()
    fill_grad(ctx, POLY, 150, 1110, 450, 1650, a); ctx.fill_preserve()
    rgba(ctx, (0.4, 0.42, 0.48), 0.6 * a); ctx.set_line_width(3); ctx.stroke()
    # trigger guard hole
    ctx.move_to(480, 1180); ctx.curve_to(470, 1260, 600, 1270, 630, 1180); ctx.close_path()
    rgba(ctx, (0.03, 0.04, 0.09), a); ctx.fill()
    # grip texture
    for k in range(10):
        y = 1260 + k * 36
        ctx.move_to(195 - (y - 1260) * 0.21 + 20, y); ctx.line_to(330 - (y - 1260) * 0.21 + 40, y)
    rgba(ctx, (0.3, 0.32, 0.36), 0.5 * a); ctx.set_line_width(3); ctx.stroke()
    # magazine (cutaway window)
    ctx.save()
    def gx(y):
        l = 225 + (150 - 225) * (y - 1200) / 450; r = 430 + (330 - 430) * (y - 1160) / 490
        return l, r
    l0, r0 = gx(1175); l1, r1 = gx(1630)
    ctx.move_to(l0 + 18, 1175); ctx.line_to(r0 - 18, 1175); ctx.line_to(r1 - 18, 1630); ctx.line_to(l1 + 18, 1630); ctx.close_path()
    rgba(ctx, (0.05, 0.06, 0.12), 0.9 * a); ctx.fill()
    n = st.get('mag', 6)
    for k in range(n):
        yy = 1205 + k * 34
        l, r = gx(yy); xc = (l + r) / 2
        cartridge(ctx, xc - 55 + (6 if k % 2 else -6), yy, 0.78, 0, a)
    ctx.restore()
    # --- barrel
    ctx.rectangle(420, AXY - 32, 590, 64); fill_grad(ctx, STEEL, 0, AXY - 32, 0, AXY + 32, a); ctx.fill()
    ctx.rectangle(420, AXY - 15, 590, 30); rgba(ctx, (0.08, 0.08, 0.1), a); ctx.fill()
    # rifling hint
    for k in range(18):
        x = 560 + k * 25 + (t * 0) % 25
        ctx.move_to(x, AXY - 15); ctx.line_to(x + 14, AXY + 15)
    rgba(ctx, (0.35, 0.37, 0.42), 0.6 * a); ctx.set_line_width(2); ctx.stroke()
    # recoil spring
    ctx.move_to(640, 1085)
    L = 340 + so * 0.0
    for i in range(41):
        ctx.line_to(640 + i * 8.5, 1085 + (10 if i % 2 else -10))
    rgba(ctx, (0.7, 0.72, 0.78), a); ctx.set_line_width(4); ctx.stroke()
    # --- cartridge in chamber / bullet & gas
    if st.get('chambered', True):
        cartridge(ctx, 428, AXY, 1.0, 0, a, with_bullet=st.get('bullet_x') is None)
    bx = st.get('bullet_x')
    gas = st.get('gas', 0)
    if gas > 0:
        x1 = (bx if bx is not None else 520)
        g = cairo.LinearGradient(430, 0, x1, 0)
        g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.9 * gas * a); g.add_color_stop_rgba(1, 1, 0.5, 0.1, 0.6 * gas * a)
        ctx.set_source(g); ctx.rectangle(440, AXY - 14, max(0, min(x1, 1010) - 440), 28); ctx.fill()
    if bx is not None and bx < 1200:
        ctx.save(); ctx.translate(bx, AXY)
        ctx.move_to(0, -14); ctx.line_to(30, -14); ctx.curve_to(55, -12, 62, -4, 64, 0); ctx.curve_to(62, 4, 55, 12, 30, 14); ctx.line_to(0, 14); ctx.close_path()
        fill_grad(ctx, COP, 0, -14, 0, 14, a); ctx.fill(); ctx.restore()
    if st.get('flash', 0) > 0:
        f = st['flash']
        g = cairo.RadialGradient(1030, AXY, 5, 1030, AXY, 160 * f)
        g.add_color_stop_rgba(0, 1, 1, 0.8, f); g.add_color_stop_rgba(0.4, 1, 0.7, 0.2, 0.7 * f); g.add_color_stop_rgba(1, 1, 0.4, 0.1, 0)
        ctx.set_source(g); ctx.arc(1030, AXY, 160 * f, 0, 6.3); ctx.fill()
    # --- slide (semi-transparent cutaway) moves back by so
    ctx.save(); ctx.translate(so, 0)
    ctx.move_to(220, 950); ctx.line_to(560, 950); ctx.line_to(560, 985); ctx.line_to(720, 985); ctx.line_to(720, 950)
    ctx.line_to(1010, 950); ctx.line_to(1010, 1108); ctx.line_to(220, 1108); ctx.close_path()
    fill_grad(ctx, [(0, (0.55, 0.58, 0.64)), (0.3, (0.85, 0.88, 0.93)), (1, (0.3, 0.32, 0.37))], 0, 950, 0, 1108, 0.42 * a); ctx.fill_preserve()
    rgba(ctx, (0.85, 0.9, 1.0), 0.85 * a); ctx.set_line_width(4); ctx.stroke()
    for k in range(6):
        ctx.move_to(235 + k * 14, 960); ctx.line_to(235 + k * 14, 1098)
    rgba(ctx, (0.85, 0.9, 1.0), 0.4 * a); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(975, 935, 20, 16); ctx.rectangle(245, 935, 30, 16); rgba(ctx, (0.6, 0.62, 0.68), a); ctx.fill()
    # breech face
    ctx.rectangle(395, 990, 30, 80); fill_grad(ctx, STEEL, 395, 0, 425, 0, a); ctx.fill()
    # striker + spring
    sp = st.get('striker', 0.0)   # 0 cocked, 1 forward
    sx = 280 + 115 * sp
    ctx.rectangle(sx - 120, AXY - 8, 140, 16); fill_grad(ctx, STEEL, 0, AXY - 8, 0, AXY + 8, a); ctx.fill()
    ctx.move_to(sx + 20, AXY - 4); ctx.line_to(sx + 32, AXY); ctx.line_to(sx + 20, AXY + 4); ctx.close_path(); rgba(ctx, (0.8, 0.82, 0.86), a); ctx.fill()
    ctx.move_to(260, AXY)
    for i in range(17):
        xx = 260 + (sx - 270) * i / 16
        ctx.line_to(xx, AXY + (16 if i % 2 else -16))
    rgba(ctx, YELLOW, 0.85 * a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    # --- trigger
    tr = st.get('trig', 0.0)
    ctx.save(); ctx.translate(540, 1165); ctx.rotate(0.35 * tr)
    ctx.move_to(-10, 0); ctx.curve_to(-20, 40, -10, 80, 10, 100); ctx.line_to(22, 95); ctx.curve_to(10, 70, 6, 40, 14, 0); ctx.close_path()
    fill_grad(ctx, DARK, -20, 0, 20, 0, a); ctx.fill()
    ctx.restore()
    # --- ejected case
    eq = st.get('eject')
    if eq is not None and eq > 0:
        ex = 470 + 520 * eq; ey = 990 - 600 * eq + 700 * eq * eq
        cartridge(ctx, ex, ey, 1.0, eq * 9, a * clamp((1 - eq) * 4), with_bullet=False)
    fq = st.get('feed')
    if fq is not None:
        fx = 250 + (428 - 250) * fq; fy = 1180 + (AXY - 1180) * fq
        cartridge(ctx, fx, fy, 1.0, -0.25 * (1 - fq) * math.sin(fq * math.pi), a)

def big_cartridge(ctx, cx, cy, s, explode=0.0, burn=0.0, striker=None, t=0.0, a=1.0, labels=0.0):
    # case cross-section, rim at left
    L, R = 300 * s, 70 * s
    x0 = cx - 260 * s
    dx = 120 * s * explode
    # case walls
    ctx.rectangle(x0 - dx, cy - R, L, 2 * R); fill_grad(ctx, BRASS, 0, cy - R, 0, cy + R, a); ctx.fill()
    ctx.rectangle(x0 - dx + 30 * s, cy - R + 12 * s, L - 30 * s, 2 * R - 24 * s); rgba(ctx, (0.06, 0.05, 0.04), a); ctx.fill()
    ctx.rectangle(x0 - dx - 12 * s, cy - R - 6 * s, 24 * s, 2 * R + 12 * s); fill_grad(ctx, BRASS, 0, cy - R, 0, cy + R, a); ctx.fill()
    # powder grains
    rnd = random.Random(4)
    for k in range(70):
        gx = x0 - dx + 40 * s + rnd.random() * (L - 60 * s); gy = cy - R + 18 * s + rnd.random() * (2 * R - 36 * s)
        b = burn
        c = (0.25 + 0.75 * b, 0.25 + 0.4 * b, 0.25 - 0.15 * b)
        ctx.arc(gx, gy, (6 - 3 * b) * s, 0, 6.3); rgba(ctx, c, a * (1 - 0.6 * b)); ctx.fill()
    if burn > 0:
        g = cairo.RadialGradient(x0 - dx + 40 * s, cy, 5, x0 - dx + 40 * s, cy, L * burn * 1.1)
        g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.9 * a); g.add_color_stop_rgba(0.6, 1, 0.55, 0.1, 0.6 * a); g.add_color_stop_rgba(1, 1, 0.3, 0.05, 0)
        ctx.set_source(g); ctx.rectangle(x0 - dx + 30 * s, cy - R + 12 * s, L - 30 * s, 2 * R - 24 * s); ctx.fill()
    # primer
    ctx.rectangle(x0 - dx - 12 * s, cy - 22 * s, 40 * s, 44 * s); fill_grad(ctx, STEEL, 0, cy - 22 * s, 0, cy + 22 * s, a); ctx.fill()
    ctx.rectangle(x0 - dx + 14 * s, cy - 14 * s, 12 * s, 28 * s); rgba(ctx, RED, a); ctx.fill()
    # bullet
    bx = x0 + L - 40 * s + dx + 160 * s * clamp((burn - 0.55) / 0.45)
    ctx.move_to(bx, cy - 62 * s); ctx.line_to(bx + 120 * s, cy - 62 * s); ctx.curve_to(bx + 220 * s, cy - 55 * s, bx + 250 * s, cy - 20 * s, bx + 258 * s, cy)
    ctx.curve_to(bx + 250 * s, cy + 20 * s, bx + 220 * s, cy + 55 * s, bx + 120 * s, cy + 62 * s); ctx.line_to(bx, cy + 62 * s); ctx.close_path()
    fill_grad(ctx, COP, 0, cy - 62 * s, 0, cy + 62 * s, a); ctx.fill()
    if striker is not None:
        sx = x0 - dx - 12 * s - 20 + striker
        ctx.rectangle(sx - 300, cy - 16, 300, 32); fill_grad(ctx, STEEL, 0, cy - 16, 0, cy + 16, a); ctx.fill()
        ctx.move_to(sx, cy - 16); ctx.line_to(sx + 22, cy); ctx.line_to(sx, cy + 16); ctx.close_path(); fill_grad(ctx, STEEL, 0, cy - 16, 0, cy + 16, a); ctx.fill()
    if labels > 0:
        items = [("bala", bx + 130 * s, cy - 62 * s, bx + 130 * s, cy - 230 * s, ORANGE),
                 ("vaina", x0 - dx + L * 0.75, cy + R, x0 - dx + L * 0.85, cy + 200 * s, YELLOW),
                 ("pólvora", x0 - dx + L * 0.55, cy - 20 * s, x0 - dx + L * 0.3, cy - 230 * s, (0.75, 0.75, 0.8)),
                 ("fulminante", x0 - dx, cy + 20 * s, max(200, x0 - dx + 40 * s), cy + 330 * s, RED)]
        for i, (name, ax, ay, lx, ly, c) in enumerate(items):
            p = clamp(labels * 4 - i)
            if p <= 0: continue
            ctx.move_to(ax, ay); ctx.line_to(ax + (lx - ax) * p, ay + (ly - ay) * p); rgba(ctx, c, p); ctx.set_line_width(4); ctx.stroke()
            glow_dot(ctx, ax, ay, 7, c, p)
            label(ctx, name, lx, ly + (-30 if ly < cy else 30), 46, c, p, box=True)

# ------------------------------------------------------------------ scenes
def s_hook(ctx, t, d):
    p = eo(prog(t, 0, 0.6))
    ctx.save(); ctx.translate(-40, 0)
    draw_pistol(ctx, t, {'a': p})
    ctx.restore()
    sc = 0.5 + 0.5 * math.sin(t * 4)
    label(ctx, "vista por dentro", 760, 1450, 44, CYAN, eo(prog(t, 0.8, 1.2)), box=True)

def s_cart(ctx, t, d):
    ex = eio(prog(t, 1.2, 2.0))
    big_cartridge(ctx, CX + 70, 1180, 1.12, explode=ex, labels=prog(t, 1.6, 3.6), a=eo(prog(t, 0, 0.4)))

def s_trigger(ctx, t, d):
    tr = eio(prog(t, 0.4, 1.2)); st = eo(prog(t, 1.4, 1.55))
    draw_pistol(ctx, t, {'trig': tr, 'striker': st})
    label(ctx, "gatillo", 700, 1350, 46, YELLOW, eo(prog(t, 0.3, 0.7)), box=True)
    label(ctx, "percutor", 300, 870, 46, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)
    if 1.4 < t < 1.9: glow_dot(ctx, 420, AXY, 22, (0.8, 0.95, 1), 1 - prog(t, 1.4, 1.9))

def s_primer(ctx, t, d):
    hit = eio(prog(t, 0.3, 0.6))
    big_cartridge(ctx, 600, 1180, 1.15, striker=-200 + 200 * hit)
    if t > 0.6:
        f = 1 - prog(t, 0.6, 2.0)
        spark(ctx, 600 - 260 * 1.15 + 20, 1180, 2.0, t, f)
    label(ctx, "percutor", 170, 1050, 44, WHITE, eo(prog(t, 0.2, 0.6)), NORM, box=True)
    label(ctx, "¡chispa!", 380, 1420, 54, YELLOW, eo(prog(t, 0.7, 1.0)), box=True)

def s_powder(ctx, t, d):
    burn = eio(prog(t, 0.3, 2.8))
    big_cartridge(ctx, CX - 60, 1180, 1.15, burn=burn)
    if burn > 0.3:
        for k in range(3):
            y = 1180 + (k - 1) * 45
            ctx.move_to(560, y); ctx.line_to(640 + 40 * burn, y); glow_stroke(ctx, YELLOW, 6, burn)
            arrow_head(ctx, 650 + 40 * burn, y, 0, 30, YELLOW, burn)
    label(ctx, "gases a mucha presión", CX, 1500, 46, ORANGE, eo(prog(t, 1.4, 1.8)), box=True)
    label(ctx, "(no explota: arde muy rápido)", CX, 1580, 36, WHITE, eo(prog(t, 2.0, 2.4)), NORM)

def s_push(ctx, t, d):
    q = eio(prog(t, 0.3, 1.6))
    bx = 508 + (1250 - 508) * q
    flash = max(0, 1 - abs(t - 1.35) * 3) if t > 1.0 else 0
    draw_pistol(ctx, t, {'striker': 1, 'trig': 1, 'bullet_x': bx, 'gas': clamp(1.2 - q * 0.6), 'flash': flash})
    label(ctx, "cañón", 820, 900, 46, CYAN, eo(prog(t, 0.4, 0.8)), box=True)

def barrel_tube(ctx, t, a=1.0, spin=1.0):
    cy = 1150; x0, x1 = 80, 1000; R = 120
    ctx.rectangle(x0, cy - R, x1 - x0, 2 * R); fill_grad(ctx, STEEL, 0, cy - R, 0, cy + R, 0.35 * a); ctx.fill()
    ctx.rectangle(x0, cy - 80, x1 - x0, 160); rgba(ctx, (0.04, 0.05, 0.1), 0.85 * a); ctx.fill()
    # helical grooves (projection of a helix)
    for k in range(6):
        pts = []
        ph = k * math.pi / 3
        for i in range(200):
            x = x0 + i * (x1 - x0) / 199
            th = ph + (x - x0) / 140
            if math.cos(th) > 0:
                pts.append((x, cy + 80 * math.sin(th)))
            else:
                if len(pts) > 1:
                    draw_poly(ctx, pts); rgba(ctx, (0.75, 0.8, 0.9), 0.7 * a); ctx.set_line_width(5); ctx.stroke()
                pts = []
        if len(pts) > 1:
            draw_poly(ctx, pts); rgba(ctx, (0.75, 0.8, 0.9), 0.7 * a); ctx.set_line_width(5); ctx.stroke()
    return cy

def s_rifling(ctx, t, d):
    cy = barrel_tube(ctx, t)
    bx = 120 + ((t * 260) % 640)
    # spinning bullet
    ctx.save(); ctx.translate(bx, cy)
    ctx.move_to(0, -76); ctx.line_to(90, -76); ctx.curve_to(170, -70, 200, -25, 210, 0); ctx.curve_to(200, 25, 170, 70, 90, 76); ctx.line_to(0, 76); ctx.close_path()
    fill_grad(ctx, COP, 0, -76, 0, 76); ctx.fill()
    ctx.save(); ctx.rectangle(0, -76, 120, 152); ctx.clip()
    for k in range(6):
        th = t * 12 + k * math.pi / 3
        if math.cos(th) > 0:
            y = 76 * math.sin(th)
            ctx.move_to(0, y - 8); ctx.line_to(120, y + 8)
            rgba(ctx, (0.4, 0.15, 0.05), 0.8); ctx.set_line_width(6); ctx.stroke()
    ctx.restore(); ctx.restore()
    ctx.arc(bx + 100, cy, 140, -2.4, -0.6); glow_stroke(ctx, YELLOW, 6, 1)
    arrow_head(ctx, bx + 100 + 140 * math.cos(-0.6), cy + 140 * math.sin(-0.6), -0.6 + math.pi / 2, 36, YELLOW)
    label(ctx, "estrías", 300, 920, 48, CYAN, eo(prog(t, 0.3, 0.7)), box=True)
    label(ctx, "girar = vuela más recta", CX, 1450, 48, YELLOW, eo(prog(t, 1.2, 1.6)), box=True)

def s_recoil(ctx, t, d):
    sl = eio(prog(t, 0.3, 0.9))
    ej = prog(t, 0.6, 2.0)
    draw_pistol(ctx, t, {'striker': 1, 'trig': 1, 'slide': sl, 'chambered': False, 'eject': ej, 'mag': 6})
    pa = eo(prog(t, 0.3, 0.7))
    ctx.move_to(900, 880); ctx.line_to(600, 880); glow_stroke(ctx, GREEN, 8, pa)
    arrow_head(ctx, 590, 880, math.pi, 40, GREEN, pa)
    label(ctx, "corredera", 820, 810, 46, GREEN, pa, box=True)
    label(ctx, "sale la vaina vacía", 780, 1420, 40, YELLOW, eo(prog(t, 1.2, 1.6)), NORM, box=True)

def s_reload(ctx, t, d):
    fq = eio(prog(t, 0.6, 1.8))
    fq = fq
    sl = 1 - eio(prog(t, 0.6, 1.8))
    draw_pistol(ctx, t, {'striker': 0, 'trig': 0, 'slide': sl, 'chambered': fq >= 1, 'feed': fq if fq < 1 else None, 'mag': 5})
    label(ctx, "cargador", 120, 1720, 44, ORANGE, eo(prog(t, 0.3, 0.7)), box=True)
    label(ctx, "lista otra vez", 780, 1420, 44, GREEN, eo(prog(t, 2.0, 2.4)), box=True)

def s_fact(ctx, t, d):
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 140); ctx.scale(pb, pb); ctx.rotate(-0.04)
        rr(ctx, -170, -42, 340, 84, 20); rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
        label(ctx, "¡DATO!", CX, 140, 54 * pb, NAVY)
    rows = [("avión de pasajeros", 900, CYAN), ("sonido", 1235, WHITE), ("bala (9 mm)", 1300, YELLOW)]
    for i, (name, v, c) in enumerate(rows):
        y = 900 + i * 260
        p = eio(prog(t, 0.5 + i * 0.5, 1.6 + i * 0.5))
        wmax = 860
        ctx.rectangle(110, y, wmax * v / 1300 * p, 90)
        fill_grad(ctx, [(0, (c[0] * 0.5, c[1] * 0.5, c[2] * 0.5)), (1, c)], 110, 0, 110 + wmax, 0, 1); ctx.fill()
        label(ctx, name, 110 + 10, y - 40, 40, c, eo(prog(t, 0.4 + i * 0.5, 0.8 + i * 0.5)), NORM) if False else None
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, NORM); ctx.set_font_size(42)
        ctx.move_to(110, y - 18); rgba(ctx, c, eo(prog(t, 0.4 + i * 0.5, 0.8 + i * 0.5))); ctx.show_text(name)
        if p > 0.2:
            label(ctx, f"{int(v * p):,} km/h".replace(",", "."), 110 + wmax * v / 1300 * p - 120, y + 45, 40, NAVY, 1)
    label(ctx, "Unos 360 metros cada segundo", CX, 1700, 42, WHITE, eo(prog(t, 2.8, 3.2)), NORM, box=True)

def s_cta(ctx, t, d):
    pb = eback(prog(t, 0.3, 0.8))
    if pb > 0:
        bx, by = CX, 1000
        ctx.save(); ctx.translate(bx, by); ctx.scale(pb, pb)
        rr(ctx, -200, -100, 400, 200, 44); rgba(ctx, CYAN); ctx.fill()
        ctx.move_to(-70, 95); ctx.line_to(-150, 180); ctx.line_to(-10, 95); ctx.fill()
        for k in range(3):
            yy = -18 * max(0, math.sin(t * 6 - k * 0.8))
            ctx.arc(-80 + k * 80, yy, 22, 0, 6.3); rgba(ctx, NAVY); ctx.fill()
        ctx.restore()
    label(ctx, "¡Te leo en comentarios!", CX, 1350, 48, YELLOW, eo(prog(t, 0.9, 1.3)), box=True)
    label(ctx, "Las armas reales no son juguetes.", CX, 1620, 38, WHITE, eo(prog(t, 1.3, 1.7)), NORM)
    label(ctx, "Esto es solo ciencia y física.", CX, 1680, 38, WHITE, eo(prog(t, 1.4, 1.8)), NORM)

SCENES = [
    (3.0, "¿Qué pasa dentro de una pistola al disparar?", {3, 5}, ORANGE, s_hook),
    (4.5, "Todo empieza en el cartucho", {4}, YELLOW, s_cart),
    (3.5, "El gatillo suelta el percutor", {1, 4}, YELLOW, s_trigger),
    (3.5, "Golpea el fulminante: salta una chispa", {1, 5}, YELLOW, s_primer),
    (4.0, "La pólvora arde en milésimas de segundo", {1, 4, 5}, ORANGE, s_powder),
    (3.5, "Los gases empujan la bala por el cañón", {1, 4, 7}, ORANGE, s_push),
    (4.0, "Las estrías la hacen girar como un balón", {1, 4}, CYAN, s_rifling),
    (3.5, "El retroceso empuja la corredera atrás", {1, 4}, GREEN, s_recoil),
    (4.0, "Sale la vaina y entra otro cartucho", {2, 6}, YELLOW, s_reload),
    (4.5, "La bala va a unos 1.300 km/h", {5, 6}, YELLOW, s_fact, 430),
    (4.0, "¿Qué máquina quieres ver por dentro?", {1}, CYAN, s_cta),
]

if __name__ == "__main__":
    run(SCENES)

