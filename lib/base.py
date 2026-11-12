import cairo, math, random, subprocess, sys, os

W, H, FPS = 1080, 1920, 30
CX = W / 2
CYAN = (0.13, 0.89, 1.0)
ORANGE = (1.0, 0.54, 0.12)
YELLOW = (1.0, 0.82, 0.25)
WHITE = (1, 1, 1)
RED = (1.0, 0.3, 0.35)
NAVY = (0.03, 0.05, 0.13)
FONT = "Poppins"

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= a else 0.0)

def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3

def eio(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

def eback(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def rgba(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)

def glow_stroke(ctx, c, w, a=1.0, preserve=False):
    path = ctx.copy_path()
    for mult, al in ((5.0, 0.06), (2.6, 0.14), (1.6, 0.28)):
        ctx.new_path(); ctx.append_path(path)
        rgba(ctx, c, al * a); ctx.set_line_width(w * mult); ctx.stroke()
    ctx.new_path(); ctx.append_path(path)
    rgba(ctx, c, a); ctx.set_line_width(w)
    if preserve: ctx.stroke_preserve()
    else: ctx.stroke()

def glow_dot(ctx, x, y, r, c, a=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], 0.55 * a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g); ctx.arc(x, y, r * 4, 0, 2 * math.pi); ctx.fill()
    rgba(ctx, c, a); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    rgba(ctx, WHITE, 0.8 * a); ctx.arc(x, y, r * 0.45, 0, 2 * math.pi); ctx.fill()

def text_center(ctx, s, x, y, size, c=WHITE, a=1.0, weight=cairo.FONT_WEIGHT_BOLD):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    xb, yb, tw, th, xa, ya = ctx.text_extents(s)
    ctx.move_to(x - tw / 2 - xb, y + th / 2 - (th + yb))
    ctx.text_path(s)
    rgba(ctx, NAVY, 0.85 * a); ctx.set_line_width(size * 0.16); ctx.stroke_preserve()
    rgba(ctx, c, a); ctx.fill()

def dashed_line(ctx, x1, y1, x2, y2, c, w, a, dash=(18, 14), offset=0):
    ctx.set_dash(dash, offset)
    ctx.move_to(x1, y1); ctx.line_to(x2, y2)
    rgba(ctx, c, a); ctx.set_line_width(w); ctx.stroke()
    ctx.set_dash([])

def poly_partial(pts, p):
    """Return the point list covering fraction p of polyline length."""
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(segs) * clamp(p)
    out = [pts[0]]
    for i, s in enumerate(segs):
        if L >= s:
            out.append(pts[i + 1]); L -= s
        else:
            f = L / s if s else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                        pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            break
    return out

def point_at(pts, p):
    return poly_partial(pts, p)[-1]

def draw_poly(ctx, pts):
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)

# ---------------------------------------------------------------- background
random.seed(7)
STARS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.0, 3.2),
          random.uniform(0, 6.28), random.uniform(6, 22)) for _ in range(140)]

def make_bg():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.09)
    g.add_color_stop_rgb(0.55, 0.035, 0.06, 0.16)
    g.add_color_stop_rgb(1, 0.02, 0.03, 0.08)
    c.set_source(g); c.paint()
    r = cairo.RadialGradient(CX, 1120, 0, CX, 1120, 760)
    r.add_color_stop_rgba(0, 0.1, 0.35, 0.6, 0.22)
    r.add_color_stop_rgba(1, 0.1, 0.35, 0.6, 0)
    c.set_source(r); c.paint()
    return s

BG = make_bg()

def draw_bg(ctx, T):
    ctx.set_source_surface(BG); ctx.paint()
    for (x, y, r, ph, sp) in STARS:
        yy = (y - T * sp) % H
        tw = 0.35 + 0.35 * math.sin(T * 2.2 + ph)
        rgba(ctx, (0.7, 0.9, 1.0), tw); ctx.arc(x, yy, r, 0, 6.2832); ctx.fill()

# ---------------------------------------------------------------- headline text
def layout_words(ctx, words, size, maxw):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    space = ctx.text_extents(" ")[4]
    lines, cur, curw = [], [], 0
    for i, w in enumerate(words):
        ww = ctx.text_extents(w)[4]
        if cur and curw + space + ww > maxw:
            lines.append((cur, curw)); cur, curw = [], 0
        cur.append((i, w, ww)); curw += (space if len(cur) > 1 else 0) + ww
    if cur: lines.append((cur, curw))
    return lines, space

def draw_headline(ctx, t, text, hl, hlc, ycenter=430, size=96):
    words = text.split()
    lines, space = layout_words(ctx, words, size, 940)
    lh = size * 1.2
    y0 = ycenter - (len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = CX - lw / 2
        y = y0 + li * lh
        for (i, w, ww) in ln:
            st = 0.05 + i * 0.07
            p = prog(t, st, st + 0.32)
            if p > 0:
                sc = 0.55 + 0.45 * eback(p)
                a = clamp(p * 2.5)
                ctx.save()
                ctx.translate(x + ww / 2, y)
                ctx.scale(sc, sc)
                ctx.translate(-ww / 2, size * 0.36)
                ctx.move_to(0, 0); ctx.text_path(w)
                rgba(ctx, NAVY, 0.9 * a); ctx.set_line_width(16); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.stroke_preserve()
                col = hlc if i in hl else WHITE
                rgba(ctx, col, a); ctx.fill()
                ctx.restore()
            x += ww + space

# ---------------------------------------------------------------- icons
def draw_dish(ctx, x, y, s, ang, a=1.0, col=CYAN):
    if s <= 0.001: return
    """Offset dish in side view, facing direction ang (radians, 0=right)."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    # reflector
    ctx.move_to(0, -70); ctx.curve_to(-34, -30, -34, 30, 0, 70)
    ctx.curve_to(-18, 30, -18, -30, 0, -70); ctx.close_path()
    rgba(ctx, (0.75, 0.85, 0.95), 0.95 * a); ctx.fill_preserve()
    ctx.set_line_width(3); rgba(ctx, col, a); ctx.stroke()
    # arm
    ctx.move_to(-14, 50); ctx.line_to(78, 26)
    ctx.set_line_width(6); rgba(ctx, (0.6, 0.7, 0.8), a); ctx.stroke()
    # LNB
    ctx.save(); ctx.translate(82, 24); ctx.rotate(-0.35)
    ctx.rectangle(-12, -10, 26, 20); rgba(ctx, ORANGE, a); ctx.fill()
    ctx.rectangle(-20, -7, 9, 14); rgba(ctx, YELLOW, a); ctx.fill()
    ctx.restore()
    ctx.restore()

def draw_house(ctx, x, base, w, h, a=1.0):
    ctx.move_to(x - w / 2, base); ctx.line_to(x - w / 2, base - h)
    ctx.line_to(x, base - h - w * 0.35); ctx.line_to(x + w / 2, base - h)
    ctx.line_to(x + w / 2, base); ctx.close_path()
    rgba(ctx, (0.07, 0.11, 0.25), a); ctx.fill_preserve()
    rgba(ctx, CYAN, 0.35 * a); ctx.set_line_width(3); ctx.stroke()
    for wx in (-w * 0.22, w * 0.22):
        ctx.rectangle(x + wx - 18, base - h * 0.62, 36, 40)
        rgba(ctx, YELLOW, 0.55 * a); ctx.fill()

def draw_satellite(ctx, x, y, s, rot=0.0, a=1.0):
    if s <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    for sx in (-1, 1):
        ctx.move_to(sx * 26, 0); ctx.line_to(sx * 44, 0)
        rgba(ctx, (0.7, 0.8, 0.9), a); ctx.set_line_width(4); ctx.stroke()
        ctx.rectangle(sx * 44 if sx > 0 else -44 - 80, -22, 80, 44)
        rgba(ctx, (0.05, 0.3, 0.55), a); ctx.fill_preserve()
        rgba(ctx, CYAN, a); ctx.set_line_width(3); ctx.stroke()
        for k in range(1, 4):
            xx = (44 + 20 * k) * sx
            ctx.move_to(xx, -22); ctx.line_to(xx, 22)
        ctx.move_to(sx * 44, 0); ctx.line_to(sx * 124, 0)
        rgba(ctx, CYAN, 0.5 * a); ctx.set_line_width(1.5); ctx.stroke()
    ctx.rectangle(-26, -26, 52, 52); rgba(ctx, YELLOW, a); ctx.fill_preserve()
    rgba(ctx, ORANGE, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(0, 36, 14, 0, math.pi); rgba(ctx, WHITE, a); ctx.fill()
    ctx.restore()

def draw_earth_side(ctx, x, y, R, spin=0.0, a=1.0, lat_lines=True):
    g = cairo.RadialGradient(x - R * 0.35, y - R * 0.35, R * 0.1, x, y, R)
    g.add_color_stop_rgba(0, 0.1, 0.45, 0.85, a)
    g.add_color_stop_rgba(1, 0.02, 0.12, 0.35, a)
    ctx.arc(x, y, R, 0, 6.2832); ctx.set_source(g); ctx.fill()
    ctx.save(); ctx.arc(x, y, R, 0, 6.2832); ctx.clip()
    ctx.set_line_width(2.5)
    for k in range(12):
        lam = k * math.pi / 6 + spin
        if math.cos(lam) <= 0: continue
        sx = math.sin(lam)
        ctx.save(); ctx.translate(x, y)
        if abs(sx) > 0.01:
            ctx.scale(abs(sx), 1)
            if sx > 0: ctx.arc(0, 0, R, -math.pi / 2, math.pi / 2)
            else: ctx.arc(0, 0, R, math.pi / 2, 3 * math.pi / 2)
        else:
            ctx.move_to(0, -R); ctx.line_to(0, R)
        ctx.restore()
        rgba(ctx, CYAN, 0.28 * a); ctx.stroke()
    if lat_lines:
        for phi in (-60, -30, 30, 60):
            yy = y - R * math.sin(math.radians(phi)); hw = R * math.cos(math.radians(phi))
            ctx.move_to(x - hw, yy); ctx.line_to(x + hw, yy)
            rgba(ctx, CYAN, 0.2 * a); ctx.stroke()
    ctx.restore()
    ctx.arc(x, y, R, 0, 6.2832)
    glow_stroke(ctx, CYAN, 3, 0.9 * a)

def draw_lnb(ctx, x, y, s=1.0, a=1.0, rot=0.0):
    if s <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.rectangle(-22, -16, 44, 40); rgba(ctx, ORANGE, a); ctx.fill()
    ctx.move_to(-26, -16); ctx.line_to(26, -16); ctx.line_to(16, -34); ctx.line_to(-16, -34); ctx.close_path()
    rgba(ctx, YELLOW, a); ctx.fill()
    ctx.restore()

def draw_tv(ctx, x, y, on, a=1.0):
    ctx.save(); ctx.translate(x, y)
    ctx.rectangle(-95, -65, 190, 130)
    rgba(ctx, (0.08, 0.1, 0.2), a); ctx.fill_preserve()
    rgba(ctx, WHITE, 0.8 * a); ctx.set_line_width(5); ctx.stroke()
    if on > 0:
        cols = [CYAN, YELLOW, ORANGE, (0.4, 1, 0.6), (0.8, 0.4, 1)]
        for i, c in enumerate(cols):
            ctx.rectangle(-85 + i * 34, -55, 34, 110); rgba(ctx, c, 0.85 * on * a); ctx.fill()
    ctx.move_to(-40, 65); ctx.line_to(-55, 95); ctx.move_to(40, 65); ctx.line_to(55, 95)
    rgba(ctx, WHITE, 0.8 * a); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()

# ---------------------------------------------------------------- parabola utils
def parab_pts(vx, vy, f, x0, x1, n=80):
    return [(vx + x, vy - x * x / (4 * f)) for x in [x0 + (x1 - x0) * i / n for i in range(n + 1)]]

# ================================================================= scenes
def s_hook(ctx, t, d):
    base = 1640
    houses = [(230, 230, 210, -0.9), (540, 260, 300, 0.7), (850, 220, 230, -1.6)]
    target = -0.6  # pointing up-right
    for i, (x, w, h, start) in enumerate(houses):
        p = eo(prog(t, 0.05 + i * 0.08, 0.5 + i * 0.08))
        hh = h * p
        draw_house(ctx, x, base, w, hh, 1)
        if p > 0.95:
            roof = base - h - w * 0.35 * 0.5
            mx = x - w * 0.18
            ctx.move_to(mx, roof + 30); ctx.line_to(mx, roof - 70)
            rgba(ctx, (0.6, 0.7, 0.8)); ctx.set_line_width(6); ctx.stroke()
            q = eback(prog(t, 0.8 + i * 0.12, 1.6 + i * 0.12))
            ang = start + (target - start) * q
            draw_dish(ctx, mx, roof - 90, 0.95, ang)
    # compass arrow to the south (right side)
    pa = eo(prog(t, 1.7, 2.3))
    if pa > 0:
        y = 1000; x0 = 560; x1 = 560 + 380 * pa
        ctx.move_to(x0 - 300 * pa, y + 200 * pa); ctx.line_to(x1 - 40, y - 140 * pa)
        ctx.set_dash([20, 16], -t * 80)
        glow_stroke(ctx, YELLOW, 6, pa); ctx.set_dash([])
        ex, ey = x1 - 40, y - 140 * pa
        ctx.save(); ctx.translate(ex, ey); ctx.rotate(math.atan2(-340, 340))
        ctx.move_to(14, 0); ctx.line_to(-30, -24); ctx.line_to(-30, 24); ctx.close_path()
        rgba(ctx, YELLOW, pa); ctx.fill(); ctx.restore()
        r = 62 * eback(pa)
        ctx.arc(ex + 80, ey - 60, r, 0, 6.2832); rgba(ctx, YELLOW, pa); ctx.fill()
        text_center(ctx, "S", ex + 80, ey - 60, 72 * eback(pa), NAVY, pa)

def s_distance(ctx, t, d):
    ex, ey, R = CX, 1900, 420
    pe = eo(prog(t, 0, 0.6))
    draw_earth_side(ctx, ex, ey + 200 * (1 - pe), R, spin=t * 0.4)
    ps = eback(prog(t, 0.3, 0.9))
    sy = 760
    bob = math.sin(t * 2) * 6
    if ps > 0:
        draw_satellite(ctx, CX, sy + bob, 0.9 * ps, 0.08 * math.sin(t))
    pl = eio(prog(t, 0.8, 2.2))
    if pl > 0:
        top = sy + 60; bot = ey - R - 10
        yb = top + (bot - top) * pl
        dashed_line(ctx, CX + 0, top, CX, yb, CYAN, 5, 0.9, offset=-t * 60)
        ctx.move_to(CX - 30, top); ctx.line_to(CX + 30, top)
        rgba(ctx, CYAN, 0.9); ctx.set_line_width(5); ctx.stroke()
        if pl >= 1:
            ctx.move_to(CX - 30, bot); ctx.line_to(CX + 30, bot); ctx.stroke()
        km = int(36000 * pl / 100) * 100
        lab = f"{km:,}".replace(",", ".") + " km"
        # label box
        ctx.save()
        bx, by = CX + 70, (top + bot) / 2 - 45
        ctx.rectangle(bx, by, 330, 90); rgba(ctx, (0.04, 0.08, 0.2), 0.85); ctx.fill_preserve()
        rgba(ctx, CYAN, 0.9); ctx.set_line_width(3); ctx.stroke()
        ctx.restore()
        text_center(ctx, lab, bx + 165, by + 45, 56, YELLOW)
        if t > 2.4:
            pa = eo(prog(t, 2.4, 2.8))
            text_center(ctx, "Casi 3 Tierras en fila", bx + 165, by + 140, 38, WHITE, 0.8 * pa,
                        cairo.FONT_WEIGHT_NORMAL)

def s_orbit(ctx, t, d):
    cx, cy = CX, 1130
    R, Ro = 170, 400
    p0 = eo(prog(t, 0, 0.5))
    ang = -math.pi / 2 + t * 0.9  # same angular speed for both
    # orbit ring
    ctx.arc(cx, cy, Ro * p0, 0, 6.2832)
    ctx.set_dash([14, 14], -t * 30); rgba(ctx, CYAN, 0.5 * p0); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    # earth top view
    g = cairo.RadialGradient(cx - 50, cy - 50, 10, cx, cy, R)
    g.add_color_stop_rgb(0, 0.1, 0.45, 0.85); g.add_color_stop_rgb(1, 0.02, 0.12, 0.35)
    ctx.arc(cx, cy, R * p0, 0, 6.2832); ctx.set_source(g); ctx.fill()
    ctx.arc(cx, cy, R * p0, 0, 6.2832); glow_stroke(ctx, CYAN, 3, p0)
    for k in range(8):
        a = ang + k * math.pi / 4
        ctx.move_to(cx + 12 * math.cos(a), cy + 12 * math.sin(a))
        ctx.line_to(cx + R * p0 * math.cos(a), cy + R * p0 * math.sin(a))
    rgba(ctx, CYAN, 0.3 * p0); ctx.set_line_width(2.5); ctx.stroke()
    # point on earth (you) and satellite, aligned
    px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
    sx, sy = cx + Ro * math.cos(ang), cy + Ro * math.sin(ang)
    pl = eo(prog(t, 0.5, 1.0))
    if pl > 0:
        dashed_line(ctx, px, py, px + (sx - px) * pl, py + (sy - py) * pl, YELLOW, 5, 0.9, (12, 10), -t * 40)
        glow_dot(ctx, px, py, 12, ORANGE, pl)
        draw_satellite(ctx, sx, sy, 0.55 * eback(pl), ang + math.pi / 2)
    # rotation arrow
    pa = eo(prog(t, 1.0, 1.5))
    if pa > 0:
        ctx.arc(cx, cy, 540 - 60, -2.6, -0.55)
        glow_stroke(ctx, ORANGE, 5, pa * 0.9)
        ex, ey = cx + 480 * math.cos(-0.55), cy + 480 * math.sin(-0.55)
        ctx.save(); ctx.translate(ex, ey); ctx.rotate(-0.55 + math.pi / 2)
        ctx.move_to(18, 0); ctx.line_to(-14, -20); ctx.line_to(-14, 20); ctx.close_path()
        rgba(ctx, ORANGE, pa); ctx.fill(); ctx.restore()
        text_center(ctx, "1 vuelta = 24 h", cx, cy + 600, 50, ORANGE, pa)
        text_center(ctx, "Parece quieto en el cielo", cx, cy + 680, 40, WHITE, 0.8 * eo(prog(t, 1.8, 2.3)),
                    cairo.FONT_WEIGHT_NORMAL)

def s_south(ctx, t, d):
    ex, ey, R = 360, 1120, 250
    p0 = eo(prog(t, 0, 0.5))
    draw_earth_side(ctx, ex, ey, R * (0.6 + 0.4 * p0), spin=0.3 + t * 0.3, a=p0, lat_lines=False)
    pe = eo(prog(t, 0.4, 1.0))
    if pe > 0:
        dashed_line(ctx, ex - R - 40, ey, ex - R - 40 + (W - (ex - R - 40) + 20) * pe, ey, ORANGE, 4, 0.9, (16, 12))
        text_center(ctx, "Ecuador", ex - 40, ey + 45, 34, ORANGE, pe)
    sx, sy = 930, ey
    ps = eback(prog(t, 0.8, 1.3))
    if ps > 0:
        draw_satellite(ctx, sx, sy + math.sin(t * 2) * 5, 0.5 * ps, 0)
    # Spain at 40 N on the right limb
    lat = math.radians(40)
    spx, spy = ex + R * math.cos(lat), ey - R * math.sin(lat)
    pp = eo(prog(t, 1.1, 1.5))
    if pp > 0:
        glow_dot(ctx, spx, spy, 13, YELLOW, pp)
        text_center(ctx, "España", spx - 40, spy - 60, 40, YELLOW, pp)
        text_center(ctx, "N", ex, ey - R - 40, 40, WHITE, 0.8 * pp)
        text_center(ctx, "S", ex, ey + R + 42, 40, WHITE, 0.8 * pp)
    pa = eio(prog(t, 1.5, 2.4))
    if pa > 0:
        x2 = spx + (sx - 60 - spx) * pa; y2 = spy + (sy - 10 - spy) * pa
        ctx.move_to(spx, spy); ctx.line_to(x2, y2)
        glow_stroke(ctx, YELLOW, 6, 1)
        ang = math.atan2(sy - spy, sx - spx)
        ctx.save(); ctx.translate(x2, y2); ctx.rotate(ang)
        ctx.move_to(16, 0); ctx.line_to(-22, -18); ctx.line_to(-22, 18); ctx.close_path()
        rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
    pt = eo(prog(t, 2.4, 2.9))
    if pt > 0:
        text_center(ctx, "Mirar abajo = mirar al sur", CX, 1520, 46, CYAN, pt)

def s_weak(ctx, t, d):
    sx, sy = CX, 760
    draw_satellite(ctx, sx, sy + math.sin(t * 2) * 5, 0.8, 0)
    dy = 1560
    p0 = eo(prog(t, 0, 0.4))
    draw_dish(ctx, CX, dy, 1.3 * p0, -math.pi / 2, p0)
    # expanding waves
    for k in range(6):
        ph = ((t * 0.45 + k / 6) % 1.0)
        r = 80 + ph * 780
        alpha = (1 - ph) ** 1.5 * clamp(t * 3)
        ctx.arc(sx, sy + 40, r, math.radians(35), math.radians(145))
        rgba(ctx, CYAN, alpha); ctx.set_line_width(max(1.0, 14 * (1 - ph))); ctx.stroke()
    # signal meter
    pm = eo(prog(t, 1.2, 1.7))
    if pm > 0:
        mx, my = 140, 1150
        ctx.rectangle(mx - 40, my - 220, 80, 440)
        rgba(ctx, WHITE, 0.8 * pm); ctx.set_line_width(4); ctx.stroke()
        lvl = 0.08 + 0.03 * math.sin(t * 8)
        ctx.rectangle(mx - 32, my + 212 - 424 * lvl, 64, 424 * lvl)
        rgba(ctx, RED, pm); ctx.fill()
        text_center(ctx, "señal", mx, my + 270, 36, WHITE, pm, cairo.FONT_WEIGHT_NORMAL)

VX, VY, F = CX, 1500, 230

def draw_main_parabola(ctx, p, a=1.0):
    pts = parab_pts(VX, VY, F, -400, 400)
    sub = poly_partial(pts, p)
    if len(sub) > 1:
        draw_poly(ctx, sub); glow_stroke(ctx, CYAN, 9, a)

def s_mirror(ctx, t, d):
    p = eio(prog(t, 0.1, 1.4))
    draw_main_parabola(ctx, p)
    # tiny mirror sparkles
    if t > 1.4:
        for k, xr in enumerate((-300, -150, 150, 300)):
            ph = (t * 1.3 + k * 0.27) % 1.0
            x = VX + xr; y = VY - xr * xr / (4 * F)
            glow_dot(ctx, x, y - 4, 6 + 6 * math.sin(ph * math.pi), WHITE, math.sin(ph * math.pi))
    pl = eo(prog(t, 1.4, 1.9))
    if pl > 0:
        text_center(ctx, "forma de parábola", CX, VY + 110, 46, CYAN, pl)

RAYS = [-330, -240, -150, -60, 60, 150, 240, 330]

def ray_path(xr, top=740):
    hx, hy = VX + xr, VY - xr * xr / (4 * F)
    return [(hx, top), (hx, hy), (VX, VY - F)]

def draw_rays(ctx, t, start, a=1.0, col=YELLOW, loop_dots=True):
    hits = 0
    for i, xr in enumerate(RAYS):
        pts = ray_path(xr)
        p = eio(prog(t, start + i * 0.06, start + 1.1 + i * 0.06))
        if p <= 0: continue
        sub = poly_partial(pts, p)
        draw_poly(ctx, sub); glow_stroke(ctx, col, 3.5, 0.55 * a)
        if p >= 1: hits += 1
        if loop_dots and p >= 1:
            for k in range(2):
                q = ((t - start) * 0.55 + k * 0.5 + i * 0.11) % 1.0
                x, y = point_at(pts, q)
                glow_dot(ctx, x, y, 7, col, a)
    return hits / len(RAYS)

def s_reflect(ctx, t, d):
    draw_main_parabola(ctx, 1)
    frac = draw_rays(ctx, t, 0.2)
    fx, fy = VX, VY - F
    pulse = 1 + 0.15 * math.sin(t * 9)
    glow_dot(ctx, fx, fy, (8 + 18 * frac) * pulse, ORANGE, 0.3 + 0.7 * frac)
    pl = eo(prog(t, 1.6, 2.1))
    if pl > 0:
        text_center(ctx, "Foco", fx + 150, fy - 10, 52, ORANGE, pl)
        ctx.move_to(fx + 40, fy); ctx.line_to(fx + 85, fy)
        rgba(ctx, ORANGE, pl); ctx.set_line_width(4); ctx.stroke()

def s_lnb(ctx, t, d):
    draw_main_parabola(ctx, 1, 0.7)
    draw_rays(ctx, t + 3, 0, a=0.5)
    fx, fy = VX, VY - F
    pa = eback(prog(t, 0.1, 0.6))
    # arm
    ctx.move_to(VX + 300, VY - 300 * 300 / (4 * F)); ctx.line_to(fx + 20, fy + 25)
    rgba(ctx, (0.6, 0.7, 0.8), pa); ctx.set_line_width(7); ctx.stroke()
    draw_lnb(ctx, fx, fy + 10, 1.4 * pa, 1)
    pl = eo(prog(t, 0.5, 0.9))
    if pl > 0:
        ctx.move_to(fx - 45, fy); ctx.line_to(fx - 120, fy - 60)
        rgba(ctx, ORANGE, pl); ctx.set_line_width(4); ctx.stroke()
        text_center(ctx, "LNB", fx - 190, fy - 80, 60, ORANGE, pl)
    # cable to TV
    cable = [(fx, fy + 45), (fx, VY + 60), (fx + 300, VY + 60), (fx + 300, VY + 120)]
    pc = eio(prog(t, 0.9, 1.6))
    if pc > 0:
        draw_poly(ctx, poly_partial(cable, pc)); rgba(ctx, WHITE, 0.6); ctx.set_line_width(5); ctx.stroke()
    if pc >= 1:
        for k in range(3):
            q = ((t - 1.6) * 0.9 + k / 3) % 1.0
            x, y = point_at(cable, q); glow_dot(ctx, x, y, 8, CYAN)
    on = eo(prog(t, 1.9, 2.3))
    draw_tv(ctx, fx + 300, VY + 210, on, eo(prog(t, 1.2, 1.6)))

# offset geometry
OVX, OVY, OF = 330, 1580, 250
OX0, OX1 = 110, 430

def s_offset(ctx, t, d):
    pf = eo(prog(t, 0.0, 0.9))
    full = parab_pts(OVX, OVY, OF, -330, 700)
    sub = poly_partial(full, pf)
    if len(sub) > 1:
        ctx.set_dash([14, 12]); draw_poly(ctx, sub); rgba(ctx, CYAN, 0.45); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    if t > 0.7:
        text_center(ctx, "parábola gigante", 190, 1650, 36, CYAN, 0.7 * eo(prog(t, 0.7, 1.1)), cairo.FONT_WEIGHT_NORMAL)
    pp = eo(prog(t, 0.9, 1.5))
    if pp > 0:
        piece = parab_pts(OVX, OVY, OF, OX0, OX1)
        draw_poly(ctx, piece); glow_stroke(ctx, ORANGE, 12, pp)
    fx, fy = OVX, OVY - OF
    pr = prog(t, 1.5, 2.6)
    if pr > 0:
        for i, xr in enumerate((140, 200, 260, 320, 380)):
            hx, hy = OVX + xr, OVY - xr * xr / (4 * OF)
            pts = [(hx, 720), (hx, hy), (fx, fy)]
            p = eio(prog(t, 1.5 + i * 0.07, 2.5 + i * 0.07))
            draw_poly(ctx, poly_partial(pts, p)); glow_stroke(ctx, YELLOW, 3.5, 0.6)
            if p >= 1:
                q = ((t - 2.5) * 0.6 + i * 0.17) % 1.0
                x, y = point_at(pts, q); glow_dot(ctx, x, y, 7, YELLOW)
        draw_lnb(ctx, fx - 10, fy, 1.1 * eback(prog(t, 2.2, 2.6)), 1, rot=0.9)
    pl = eo(prog(t, 3.0, 3.4))
    if pl > 0:
        text_center(ctx, "tu antena", 830, 1490, 44, ORANGE, pl)

def mini_scene(ctx, cx, cy, offset, t, a):
    f = 110
    rays = []
    if not offset:
        vx, vy = cx, cy + 180
        piece = parab_pts(vx, vy, f, -170, 170)
        fx, fy = vx, vy - f
        xs = [-140, -90, -40, 0, 40, 90, 140]
    else:
        vx, vy = cx - 140, cy + 230
        piece = parab_pts(vx, vy, f, 60, 300)
        fx, fy = vx, vy - f
        xs = [80, 125, 170, 215, 260]
    draw_poly(ctx, piece); glow_stroke(ctx, CYAN if not offset else ORANGE, 7, a)
    top = cy - 250
    for xr in xs:
        hx, hy = vx + xr, vy - xr * xr / (4 * f)
        blocked = (not offset) and abs(xr) <= 40
        if blocked:
            ctx.move_to(hx, top); ctx.line_to(hx, fy - 25)
            rgba(ctx, YELLOW, 0.6 * a); ctx.set_line_width(4); ctx.stroke()
        else:
            ctx.move_to(hx, top); ctx.line_to(hx, hy); ctx.line_to(fx, fy)
            rgba(ctx, YELLOW, 0.6 * a); ctx.set_line_width(4); ctx.stroke()
    if not offset:
        ctx.rectangle(fx - 45, fy + 20, 90, (vy - fy) - 20)
        rgba(ctx, (0, 0, 0), 0.55 * a); ctx.fill()
        text_center(ctx, "sombra", fx, fy + 70, 30, RED, a, cairo.FONT_WEIGHT_NORMAL)
    draw_lnb(ctx, fx, fy, 0.9, a, rot=0 if not offset else 0.9)

def s_shadow(ctx, t, d):
    pa = eo(prog(t, 0.0, 0.5)); pb = eo(prog(t, 0.5, 1.0))
    mini_scene(ctx, 280, 1130, False, t, pa)
    mini_scene(ctx, 800, 1130, True, t, pb)
    pm = eback(prog(t, 1.4, 1.8))
    if pm > 0:
        # red X
        x, y, r = 280, 1520, 42 * pm
        ctx.move_to(x - r, y - r); ctx.line_to(x + r, y + r); ctx.move_to(x + r, y - r); ctx.line_to(x - r, y + r)
        glow_stroke(ctx, RED, 10, 1)
    pc = eback(prog(t, 1.8, 2.2))
    if pc > 0:
        x, y, r = 800, 1520, 42 * pc
        ctx.move_to(x - r, y); ctx.line_to(x - r * 0.25, y + r * 0.7); ctx.line_to(x + r, y - r * 0.8)
        glow_stroke(ctx, CYAN, 10, 1)
    text_center(ctx, "centrada", 280, 1630, 38, WHITE, 0.8 * pa, cairo.FONT_WEIGHT_NORMAL)
    text_center(ctx, "offset", 800, 1630, 38, WHITE, 0.8 * pb, cairo.FONT_WEIGHT_NORMAL)

def s_fact(ctx, t, d):
    # badge
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 200); ctx.scale(pb, pb); ctx.rotate(-0.05)
        ctx.rectangle(-150, -42, 300, 84); rgba(ctx, YELLOW); ctx.fill()
        ctx.restore()
        text_center(ctx, "¡DATO!", CX, 200, 56 * pb, NAVY)
    s = "0," + "0" * 11 + "1"
    n = int(len(s) * eio(prog(t, 0.8, 2.4)))
    if n > 0:
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        size = 92; ctx.set_font_size(size)
        full_w = ctx.text_extents(s + " W")[4]
        x = CX - full_w / 2; y = 1060
        for i, ch in enumerate(s[:n]):
            c = YELLOW if (i == len(s) - 1) else CYAN
            ctx.move_to(x, y); ctx.text_path(ch)
            rgba(ctx, NAVY, 0.9); ctx.set_line_width(12); ctx.stroke_preserve()
            rgba(ctx, c); ctx.fill()
            x += ctx.text_extents(ch)[4]
        if n == len(s):
            ctx.move_to(x + ctx.text_extents(" ")[4], y); ctx.text_path("W")
            rgba(ctx, WHITE); ctx.fill()
    pv = eo(prog(t, 2.6, 3.0))
    if pv > 0:
        text_center(ctx, "vatios", CX, 1160, 44, WHITE, 0.8 * pv, cairo.FONT_WEIGHT_NORMAL)
    pc = eo(prog(t, 3.0, 3.5))
    if pc > 0:
        # comparison: LED bulb vs dish
        bx, by = 300, 1430
        glow_dot(ctx, bx, by, 60 * pc, YELLOW, pc)
        text_center(ctx, "bombilla LED", bx, by + 130, 38, YELLOW, pc, cairo.FONT_WEIGHT_NORMAL)
        text_center(ctx, "10 W", bx, by + 180, 44, YELLOW, pc)
        dx, dy = 780, 1430
        glow_dot(ctx, dx, dy, 4, CYAN, pc)
        text_center(ctx, "tu antena", dx, dy + 130, 38, CYAN, pc, cairo.FONT_WEIGHT_NORMAL)
        text_center(ctx, "×10 billones menos", dx, dy + 180, 40, CYAN, pc)

def s_cta(ctx, t, d):
    base = 1640
    draw_house(ctx, 380, base, 300, 280 * eo(prog(t, 0, 0.5)))
    if t > 0.5:
        roof = base - 280 - 300 * 0.35 * 0.5
        mx = 380 - 60
        ctx.move_to(mx, roof + 30); ctx.line_to(mx, roof - 70)
        rgba(ctx, (0.6, 0.7, 0.8)); ctx.set_line_width(6); ctx.stroke()
        draw_dish(ctx, mx, roof - 90, 1.0 * eback(prog(t, 0.5, 0.9)), -0.6 + 0.08 * math.sin(t * 3))
    pb = eback(prog(t, 1.0, 1.5))
    if pb > 0:
        bx, by = 760, 960
        ctx.save(); ctx.translate(bx, by); ctx.scale(pb, pb)
        r = 40
        ctx.new_sub_path()
        ctx.arc(-170 + r, -90 + r, r, math.pi, 1.5 * math.pi); ctx.arc(170 - r, -90 + r, r, 1.5 * math.pi, 0)
        ctx.arc(170 - r, 90 - r, r, 0, 0.5 * math.pi)
        ctx.line_to(-40, 90); ctx.line_to(-110, 150); ctx.line_to(-100, 90)
        ctx.arc(-170 + r, 90 - r, r, 0.5 * math.pi, math.pi); ctx.close_path()
        rgba(ctx, CYAN); ctx.fill()
        for k in range(3):
            yy = -10 - 14 * max(0, math.sin(t * 6 - k * 0.8))
            ctx.arc(-70 + k * 70, yy + 10, 16, 0, 6.2832); rgba(ctx, NAVY); ctx.fill()
        ctx.restore()
    pt = eo(prog(t, 1.5, 2.0))
    if pt > 0:
        text_center(ctx, "¡Te leo en comentarios!", CX, 1760, 50, YELLOW, pt)

SCENES = [
    # (dur, text, highlight word indices, highlight color, func)
    (3.0, "¿Por qué las antenas parabólicas miran al sur?", {6, 7}, YELLOW, s_hook),
    (4.0, "Miran a un satélite a 36.000 km", {3, 5, 6}, CYAN, s_distance),
    (4.0, "Gira a la vez que la Tierra", {0, 6}, ORANGE, s_orbit),
    (4.0, "Desde España, queda al sur", {3, 4}, YELLOW, s_south),
    (4.0, "Su señal llega muy débil", {3, 4}, RED, s_weak),
    (4.0, "La antena es un espejo curvo", {4, 5}, CYAN, s_mirror),
    (4.5, "Rebota las ondas a un punto", {4, 5}, ORANGE, s_reflect),
    (4.0, "Ahí está el receptor: el LNB", {3, 5}, ORANGE, s_lnb),
    (4.5, "Tu antena es un trozo de parábola gigante", {6, 7}, ORANGE, s_offset),
    (4.0, "Así el receptor no le hace sombra", {5, 6}, CYAN, s_shadow),
    (5.0, "Llega una billonésima de vatio", {1, 2}, YELLOW, s_fact),
    (4.0, "¿Hacia dónde mira la antena de tu casa?", {0, 1, 2}, CYAN, s_cta),
]

def render_frame(idx, t, T):
    dur, text, hl, hlc, fn = SCENES[idx]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    draw_bg(ctx, T)
    env = min(prog(t, 0, 0.18), 1 - prog(t, dur - 0.16, dur)) if idx < len(SCENES) - 1 else prog(t, 0, 0.18)
    if idx == len(SCENES) - 1:
        env = min(env, 1 - prog(t, dur - 0.5, dur))
    ctx.push_group()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(ctx, t, dur)
    ty = 430 if idx != 10 else 470
    draw_headline(ctx, t, text, hl, hlc, ycenter=ty)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(env)
    return surf

def scene_start(idx):
    return sum(s[0] for s in SCENES[:idx])

def render_scene(idx, outdir):
    dur = SCENES[idx][0]
    n = int(round(dur * FPS))
    tmp = os.path.join(outdir, f"tmp_{idx:02d}.mp4")
    final = os.path.join(outdir, f"scene_{idx:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                          "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    T0 = scene_start(idx)
    for f in range(n):
        t = f / FPS
        s = render_frame(idx, t, T0 + t)
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        idx = int(sys.argv[2]); t = float(sys.argv[3])
        render_frame(idx, t, scene_start(idx) + t).write_to_png(sys.argv[4])
    elif mode == "scenes":
        for i in map(int, sys.argv[3:]):
            render_scene(i, sys.argv[2])
