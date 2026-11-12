import cairo, math, random, subprocess, sys, os
from base import (W, H, FPS, CX, CYAN, ORANGE, YELLOW, WHITE, RED, NAVY, FONT, clamp, prog, eo, eio, eback,
                  rgba, glow_stroke, glow_dot, dashed_line, poly_partial, point_at, draw_poly, parab_pts,
                  layout_words, draw_bg)
import globe as G

BOLD = cairo.FONT_WEIGHT_BOLD
NORM = cairo.FONT_WEIGHT_NORMAL
GREEN = (0.35, 1.0, 0.55)

def label(ctx, s, x, y, size, c=WHITE, a=1.0, weight=BOLD, box=False):
    if a <= 0: return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    xb, yb, tw, th, xa, ya = ctx.text_extents(s)
    if box:
        px, py = size * 0.45, size * 0.28
        rr(ctx, x - tw / 2 - px, y - size * 0.62 - py, tw + 2 * px, size * 1.24 + 2 * py, size * 0.3)
        rgba(ctx, (0.03, 0.06, 0.16), 0.88 * a); ctx.fill_preserve()
        rgba(ctx, c, 0.9 * a); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(x - tw / 2 - xb, y - yb - th / 2)
    ctx.text_path(s)
    rgba(ctx, NAVY, 0.9 * a); ctx.set_line_width(size * 0.18); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke_preserve()
    rgba(ctx, c, a); ctx.fill()

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def arrow_head(ctx, x, y, ang, size, c, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    ctx.move_to(size * 0.6, 0); ctx.line_to(-size * 0.6, -size * 0.55); ctx.line_to(-size * 0.6, size * 0.55)
    ctx.close_path(); rgba(ctx, c, a); ctx.fill(); ctx.restore()

def lin(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops:
        if len(c) == 3: g.add_color_stop_rgb(o, *c)
        else: g.add_color_stop_rgba(o, *c)
    return g

# ------------------------------------------------------------------ headline
def draw_headline(ctx, t, text, hl, hlc, ycenter=400, size=112):
    words = text.split()
    lines, space = layout_words(ctx, words, size, 990)
    lh = size * 1.14
    y0 = ycenter - (len(lines) - 1) * lh / 2
    for li, (ln, lw) in enumerate(lines):
        x = CX - lw / 2; y = y0 + li * lh
        for (i, w, ww) in ln:
            st = 0.04 + i * 0.06
            p = prog(t, st, st + 0.3)
            if p > 0:
                sc = 0.55 + 0.45 * eback(p); a = clamp(p * 2.5)
                ctx.save(); ctx.translate(x + ww / 2, y); ctx.scale(sc, sc); ctx.translate(-ww / 2, size * 0.36)
                ctx.move_to(0, 0); ctx.text_path(w)
                rgba(ctx, (0, 0, 0), 0.55 * a); ctx.set_line_width(22); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.stroke_preserve()
                rgba(ctx, hlc if i in hl else WHITE, a); ctx.fill()
                ctx.restore()
            x += ww + space

# ------------------------------------------------------------------ realistic objects
def draw_sat(ctx, x, y, s, rot=0.0, a=1.0):
    """Realistic satellite. Its antenna dish points to local +y (down) before rotation."""
    if s <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.push_group()
    # booms
    for sx in (-1, 1):
        ctx.rectangle(40 if sx > 0 else -62, -4, 22, 8)
    ctx.set_source(lin(0, -4, 0, 4, [(0, (0.8, 0.82, 0.85)), (1, (0.4, 0.42, 0.45))])); ctx.fill()
    # solar panels
    for sx in (-1, 1):
        x0 = 60 if sx > 0 else -60 - 210
        ctx.rectangle(x0, -38, 210, 76)
        ctx.set_source(lin(x0, -38, x0 + 210, 38, [(0, (0.10, 0.18, 0.42)), (0.45, (0.20, 0.36, 0.70)),
                                                    (0.55, (0.12, 0.22, 0.50)), (1, (0.05, 0.10, 0.28))]))
        ctx.fill()
        ctx.set_line_width(1.6); rgba(ctx, (0.55, 0.7, 0.95), 0.55)
        for k in range(1, 7):
            ctx.move_to(x0 + k * 30, -38); ctx.line_to(x0 + k * 30, 38)
        for k in (1, 2):
            ctx.move_to(x0, -38 + k * 25.3); ctx.line_to(x0 + 210, -38 + k * 25.3)
        ctx.stroke()
        ctx.rectangle(x0, -38, 210, 76); rgba(ctx, (0.85, 0.88, 0.92)); ctx.set_line_width(3); ctx.stroke()
    # body side face (3D)
    ctx.move_to(40, -42); ctx.line_to(56, -54); ctx.line_to(56, 34); ctx.line_to(40, 46); ctx.close_path()
    ctx.set_source(lin(40, 0, 56, 0, [(0, (0.55, 0.38, 0.08)), (1, (0.35, 0.22, 0.04))])); ctx.fill()
    ctx.move_to(-40, -42); ctx.line_to(-24, -54); ctx.line_to(56, -54); ctx.line_to(40, -42); ctx.close_path()
    ctx.set_source(lin(0, -54, 0, -42, [(0, (1.0, 0.88, 0.5)), (1, (0.9, 0.7, 0.25))])); ctx.fill()
    # body front gold foil
    ctx.rectangle(-40, -42, 80, 88)
    ctx.set_source(lin(-40, -42, 40, 46, [(0, (1.0, 0.85, 0.4)), (0.35, (0.85, 0.6, 0.15)),
                                          (0.6, (1.0, 0.8, 0.35)), (1, (0.6, 0.4, 0.08))])); ctx.fill()
    rnd = random.Random(3); ctx.set_line_width(1.2)
    for _ in range(14):
        x1, y1 = rnd.uniform(-38, 38), rnd.uniform(-40, 44)
        ctx.move_to(x1, y1); ctx.line_to(x1 + rnd.uniform(-14, 14), y1 + rnd.uniform(-14, 14))
    rgba(ctx, (1, 0.95, 0.7), 0.5); ctx.stroke()
    # dish pointing down (+y)
    ctx.move_to(0, 46); ctx.line_to(0, 60); rgba(ctx, (0.7, 0.7, 0.7)); ctx.set_line_width(5); ctx.stroke()
    ctx.save(); ctx.translate(0, 70); ctx.scale(1, 0.38)
    ctx.arc(0, 0, 36, 0, 2 * math.pi); ctx.restore()
    ctx.set_source(lin(-36, 0, 36, 0, [(0, (0.75, 0.78, 0.8)), (0.4, (1, 1, 1)), (1, (0.6, 0.62, 0.66))])); ctx.fill()
    ctx.move_to(0, 70); ctx.line_to(0, 88); rgba(ctx, (0.5, 0.5, 0.5)); ctx.set_line_width(3); ctx.stroke()
    # small antenna on top
    ctx.move_to(-10, -54); ctx.line_to(-10, -80); rgba(ctx, (0.85, 0.85, 0.85)); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(-10, -82, 5, 0, 6.28); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

def draw_dish3d(ctx, x, y, s, ang, a=1.0):
    """3/4 view of an offset home dish. Facing direction ang (0 = right). (x,y) = mount point."""
    if s <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    ctx.push_group()
    # back bracket
    ctx.rectangle(-46, -9, 30, 18); ctx.set_source(lin(0, -9, 0, 9, [(0, (0.55, 0.57, 0.6)), (1, (0.25, 0.27, 0.3))])); ctx.fill()
    # arm
    ctx.move_to(-10, 64); ctx.line_to(104, 22)
    ctx.set_source(lin(0, 0, 0, 70, [(0, (0.75, 0.77, 0.8)), (1, (0.35, 0.37, 0.4))])); ctx.set_line_width(9); ctx.stroke()
    # plate rim (back side)
    ctx.save(); ctx.scale(0.36, 1); ctx.arc(0, 0, 80, 0, 2 * math.pi); ctx.restore()
    ctx.set_source(lin(-30, -80, 30, 80, [(0, (0.62, 0.65, 0.7)), (1, (0.3, 0.32, 0.36))])); ctx.fill()
    # concave face
    ctx.save(); ctx.translate(5, 0); ctx.scale(0.30, 1); ctx.arc(0, 0, 74, 0, 2 * math.pi); ctx.restore()
    g = cairo.RadialGradient(14, -18, 4, 4, 0, 80)
    g.add_color_stop_rgb(0, 0.98, 0.99, 1.0); g.add_color_stop_rgb(0.6, 0.80, 0.83, 0.88); g.add_color_stop_rgb(1, 0.55, 0.58, 0.63)
    ctx.set_source(g); ctx.fill()
    # LNB
    ctx.save(); ctx.translate(108, 20); ctx.rotate(math.pi + 0.15)
    rr(ctx, -6, -11, 40, 22, 6)
    ctx.set_source(lin(0, -11, 0, 11, [(0, (0.35, 0.37, 0.4)), (0.5, (0.15, 0.16, 0.18)), (1, (0.08, 0.08, 0.1))])); ctx.fill()
    ctx.move_to(-6, -11); ctx.line_to(-20, -16); ctx.line_to(-20, 16); ctx.line_to(-6, 11); ctx.close_path()
    ctx.set_source(lin(0, -16, 0, 16, [(0, (1, 1, 1)), (1, (0.75, 0.76, 0.8))])); ctx.fill()
    ctx.restore()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

def draw_building(ctx, x, base, w, h, seed, a=1.0, roof=True):
    rnd = random.Random(seed)
    ctx.rectangle(x - w / 2, base - h, w, h)
    ctx.set_source(lin(x - w / 2, 0, x + w / 2, 0, [(0, (0.10, 0.13, 0.25, a)), (0.7, (0.07, 0.09, 0.19, a)), (1, (0.04, 0.05, 0.12, a))]))
    ctx.fill()
    # roof ledge
    ctx.rectangle(x - w / 2 - 8, base - h - 12, w + 16, 14)
    rgba(ctx, (0.16, 0.2, 0.34), a); ctx.fill()
    ctx.move_to(x - w / 2 - 8, base - h - 12); ctx.line_to(x + w / 2 + 8, base - h - 12)
    rgba(ctx, CYAN, 0.35 * a); ctx.set_line_width(2); ctx.stroke()
    cols = max(2, int(w // 70)); rows = int(h // 90)
    ww = w / cols
    for r in range(rows):
        for c in range(cols):
            wx = x - w / 2 + c * ww + ww * 0.22; wy = base - h + 40 + r * 90
            lit = rnd.random() < 0.55
            ctx.rectangle(wx, wy, ww * 0.56, 50)
            if lit:
                ctx.set_source(lin(0, wy, 0, wy + 50, [(0, (1.0, 0.85, 0.5, 0.95 * a)), (1, (1.0, 0.65, 0.3, 0.85 * a))]))
            else:
                rgba(ctx, (0.05, 0.07, 0.14), a)
            ctx.fill()

def draw_reflector(ctx, pts, a=1.0, thick=26, edge=CYAN):
    if len(pts) < 2: return
    ctx.push_group()
    draw_poly(ctx, pts)
    ctx.set_line_width(thick + 6); rgba(ctx, (0.18, 0.2, 0.24)); ctx.stroke()
    draw_poly(ctx, pts)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ctx.set_source(lin(min(xs), 0, max(xs) + 1, 0, [(0, (0.55, 0.58, 0.63)), (0.3, (0.92, 0.94, 0.97)),
                                                     (0.55, (0.62, 0.65, 0.7)), (0.8, (0.88, 0.9, 0.94)), (1, (0.5, 0.53, 0.58))]))
    ctx.set_line_width(thick); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    top = [(px, py - thick / 2 - 2) for px, py in pts]
    draw_poly(ctx, top); glow_stroke(ctx, edge, 3, 0.8 * a)

def draw_lnb_real(ctx, x, y, s=1.0, rot=0.0, a=1.0):
    """LNB whose feed-horn opens toward local +y (down) before rotation; (x,y) = horn mouth."""
    if s <= 0.001: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.push_group()
    # body
    rr(ctx, -20, -110, 40, 74, 8)
    ctx.set_source(lin(-20, 0, 20, 0, [(0, (0.12, 0.13, 0.15)), (0.35, (0.42, 0.44, 0.48)), (1, (0.08, 0.08, 0.1))])); ctx.fill()
    # connector
    ctx.rectangle(-7, -132, 14, 24)
    ctx.set_source(lin(-7, 0, 7, 0, [(0, (0.7, 0.6, 0.3)), (0.5, (1, 0.9, 0.55)), (1, (0.6, 0.5, 0.25))])); ctx.fill()
    # horn (white plastic cap)
    ctx.move_to(-20, -38); ctx.line_to(20, -38); ctx.line_to(34, 0); ctx.line_to(-34, 0); ctx.close_path()
    ctx.set_source(lin(-34, 0, 34, 0, [(0, (0.8, 0.82, 0.86)), (0.4, (1, 1, 1)), (1, (0.68, 0.7, 0.75))])); ctx.fill()
    ctx.save(); ctx.scale(1, 0.25); ctx.arc(0, 0, 34, 0, 2 * math.pi); ctx.restore()
    rgba(ctx, (0.25, 0.27, 0.3)); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

def draw_tv_real(ctx, x, y, w, on, t, a=1.0):
    h = w * 0.58
    ctx.push_group()
    rr(ctx, x - w / 2, y - h / 2, w, h, 10)
    rgba(ctx, (0.08, 0.08, 0.1)); ctx.fill()
    ix, iy, iw, ih = x - w / 2 + 10, y - h / 2 + 10, w - 20, h - 20
    ctx.rectangle(ix, iy, iw, ih); rgba(ctx, (0.02, 0.03, 0.06)); ctx.fill()
    if on > 0:
        ctx.save(); ctx.rectangle(ix, iy, iw, ih); ctx.clip()
        ctx.rectangle(ix, iy, iw, ih)
        ctx.set_source(lin(0, iy, 0, iy + ih, [(0, (0.15, 0.45, 0.9, on)), (0.6, (0.6, 0.85, 1.0, on)), (0.61, (0.2, 0.55, 0.25, on)), (1, (0.1, 0.35, 0.15, on))]))
        ctx.fill()
        # sun + mountains
        glow_dot(ctx, ix + iw * 0.75, iy + ih * 0.3, ih * 0.1, YELLOW, on)
        ctx.move_to(ix, iy + ih * 0.62); ctx.line_to(ix + iw * 0.3, iy + ih * 0.3); ctx.line_to(ix + iw * 0.55, iy + ih * 0.62)
        ctx.close_path(); rgba(ctx, (0.25, 0.3, 0.45), on); ctx.fill()
        ctx.restore()
    rr(ctx, x - w / 2, y - h / 2, w, h, 10); rgba(ctx, (0.4, 0.42, 0.48)); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(x - w * 0.15, y + h / 2 + 30); ctx.line_to(x + w * 0.15, y + h / 2 + 30)
    ctx.move_to(x, y + h / 2); ctx.line_to(x, y + h / 2 + 30)
    rgba(ctx, (0.4, 0.42, 0.48)); ctx.set_line_width(8); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def draw_deco(ctx, x, y, w, t, a=1.0):
    h = w * 0.22
    ctx.push_group()
    rr(ctx, x - w / 2, y - h / 2, w, h, 8)
    ctx.set_source(lin(0, y - h / 2, 0, y + h / 2, [(0, (0.25, 0.27, 0.32)), (0.2, (0.12, 0.13, 0.16)), (1, (0.05, 0.05, 0.07))])); ctx.fill()
    glow_dot(ctx, x + w * 0.38, y, 5, GREEN, 0.6 + 0.4 * math.sin(t * 6))
    ctx.rectangle(x - w * 0.35, y - 8, w * 0.3, 16); rgba(ctx, (0.02, 0.1, 0.12)); ctx.fill()
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, BOLD); ctx.set_font_size(16)
    ctx.move_to(x - w * 0.33, y + 6); rgba(ctx, CYAN); ctx.show_text("CH 001")
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

# ------------------------------------------------------------------ scenes
def s_hook(ctx, t, d):
    base = 1780
    bl = [(150, 250, 520, 1, -1.2), (420, 260, 720, 2, 0.5), (720, 280, 600, 3, -1.9), (980, 220, 460, 4, 0.9)]
    target = -0.75
    for i, (x, w, h, seed, start) in enumerate(bl):
        p = eo(prog(t, 0.0 + i * 0.07, 0.45 + i * 0.07))
        draw_building(ctx, x, base + (1 - p) * 400, w, h, seed)
        if p >= 1:
            q = eback(prog(t, 0.6 + i * 0.12, 1.3 + i * 0.12))
            ang = start + (target - start) * q
            mx = x - w * 0.15; my = base - h - 12
            ctx.move_to(mx, my); ctx.line_to(mx, my - 80)
            ctx.set_source(lin(mx - 4, 0, mx + 4, 0, [(0, (0.6, 0.62, 0.66)), (1, (0.3, 0.32, 0.35))])); ctx.set_line_width(8); ctx.stroke()
            draw_dish3d(ctx, mx + 20, my - 95, 1.15, ang)
    pa = eo(prog(t, 1.7, 2.3))
    if pa > 0:
        cx, cy = 820, 760
        r = 95 * eback(pa)
        g = cairo.RadialGradient(cx, cy, r * 0.3, cx, cy, r * 2.2)
        g.add_color_stop_rgba(0, 1, 0.82, 0.25, 0.45 * pa); g.add_color_stop_rgba(1, 1, 0.82, 0.25, 0)
        ctx.set_source(g); ctx.arc(cx, cy, r * 2.2, 0, 6.3); ctx.fill()
        ctx.arc(cx, cy, r, 0, 6.3); rgba(ctx, YELLOW, pa); ctx.fill()
        label(ctx, "SUR", cx, cy, 64 * eback(pa), NAVY, pa)
        ctx.move_to(300, 1050); ctx.line_to(300 + (cx - 120 - 300) * pa, 1050 + (cy + 70 - 1050) * pa)
        ctx.set_dash([24, 18], -t * 90); glow_stroke(ctx, YELLOW, 7, pa); ctx.set_dash([])

def s_space(ctx, t, d):
    gx, gy, R = 500, 1300, 430
    p0 = eo(prog(t, 0, 0.6))
    lon0, lat0 = 5, 28
    G.draw_globe(ctx, gx, gy + (1 - p0) * 300, R * (0.85 + 0.15 * p0), lon0, lat0, cshift=t * 0.004, a=p0)
    sx, sy = 860, 770
    ps = eback(prog(t, 0.3, 0.9))
    ex, ey, vis = G.project(45, 8, gx, gy, R, lon0, lat0)
    if ps > 0:
        # beam cone toward Europe
        pb = eo(prog(t, 0.8, 1.5))
        if pb > 0:
            ctx.move_to(sx, sy + 40)
            ctx.line_to(sx + (ex - 200 - sx) * pb, sy + (ey + 40 - sy) * pb)
            ctx.line_to(sx + (ex + 120 - sx) * pb, sy + (ey + 150 - sy) * pb)
            ctx.close_path()
            ctx.set_source(lin(sx, sy, ex, ey, [(0, (0.13, 0.89, 1.0, 0.55 * pb)), (1, (0.13, 0.89, 1.0, 0.12 * pb))])); ctx.fill()
            if pb >= 1:
                ctx.save(); ctx.translate(ex - 40, ey + 95); ctx.rotate(-0.5); ctx.scale(1, 0.45)
                ctx.arc(0, 0, 170, 0, 6.3); ctx.restore()
                rgba(ctx, CYAN, 0.18 + 0.08 * math.sin(t * 5)); ctx.fill()
        ang = math.atan2(ey - sy, ex - sx) - math.pi / 2
        draw_sat(ctx, sx, sy + math.sin(t * 2) * 6, 0.85 * ps, ang)
    pl = eo(prog(t, 1.5, 2.0))
    label(ctx, "Satélite de TV", 830, 620, 46, YELLOW, pl)
    label(ctx, "Europa", ex - 60, ey + 100, 44, WHITE, pl)

def s_distance(ctx, t, d):
    gx, gy, R = CX, 2080, 560
    pe = eo(prog(t, 0, 0.6))
    G.draw_globe(ctx, gx, gy + 250 * (1 - pe), R, 0, 40, cshift=t * 0.004)
    sy = 760
    ps = eback(prog(t, 0.2, 0.8))
    draw_sat(ctx, CX, sy + math.sin(t * 2) * 6, 0.85 * ps, 0)
    top, bot = sy + 110, gy - R - 6
    pl = eio(prog(t, 0.7, 2.0))
    if pl > 0:
        yb = top + (bot - top) * pl
        lx = 760
        dashed_line(ctx, lx, top, lx, yb, CYAN, 5, 0.9, (16, 12), -t * 60)
        ctx.move_to(lx - 30, top); ctx.line_to(lx + 30, top); rgba(ctx, CYAN); ctx.set_line_width(5); ctx.stroke()
        if pl >= 1:
            ctx.move_to(lx - 30, bot); ctx.line_to(lx + 30, bot); ctx.stroke()
        km = int(36000 * pl / 100) * 100
        label(ctx, f"{km:,}".replace(",", ".") + " km", lx + 10, (top + bot) / 2, 58, YELLOW, 1, box=True)
    # three earths in a row
    n = 3; r3 = (bot - top) / (2 * n) * 0.94
    for k in range(n):
        pk = eback(prog(t, 2.0 + k * 0.25, 2.4 + k * 0.25))
        if pk > 0:
            cy = bot - r3 - k * 2 * r3 / 0.94
            G.draw_globe(ctx, 380, cy, r3 * pk, 30 + k * 60, 20, glow=False)
    pt = eo(prog(t, 2.9, 3.3))
    label(ctx, "≈ 3 Tierras", 380 - r3 - 120, (top + bot) / 2, 40, WHITE, pt, box=True)

def s_spin(ctx, t, d):
    cx, cy, R, Ro = CX, 1180, 270, 470
    p0 = eo(prog(t, 0, 0.5))
    frac = prog(t, 0.6, 3.6)          # 0..1 = 24 h
    lon0 = -90 - 360 * eio(frac) * 1.0
    ctx.arc(cx, cy, Ro, 0, 6.2832); ctx.set_dash([14, 14]); rgba(ctx, CYAN, 0.45 * p0); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    G.draw_globe(ctx, cx, cy, R * (0.7 + 0.3 * p0), lon0, 90, cshift=0, light=(-0.95, 0.25, 0.2), a=p0)
    lam_s, lam_e = 19.2, -3.7   # Astra 19.2E, Madrid
    ds = math.radians(lam_s - lon0); de = math.radians(lam_e - lon0)
    sx, sy = cx + Ro * math.sin(ds), cy + Ro * math.cos(ds)
    f = math.cos(math.radians(40.4))
    ex, ey = cx + R * f * math.sin(de), cy + R * f * math.cos(de)
    pl = eo(prog(t, 0.4, 0.8))
    if pl > 0:
        ctx.move_to(ex, ey); ctx.line_to(sx, sy); rgba(ctx, YELLOW, 0.8 * pl); ctx.set_line_width(4); ctx.set_dash([10, 8]); ctx.stroke(); ctx.set_dash([])
        glow_dot(ctx, ex, ey, 10, YELLOW, pl)
        draw_sat(ctx, sx, sy, 0.42 * pl, math.atan2(cy - sy, cx - sx) - math.pi / 2)
    # clock
    pc = eo(prog(t, 0.3, 0.7))
    if pc > 0:
        hrs = 24 * frac
        label(ctx, f"{int(hrs):02d}:00 h", CX, 1780, 64, ORANGE, pc, box=True)
        ctx.arc(cx, cy, Ro + 70, -math.pi / 2, -math.pi / 2 + 2 * math.pi * max(frac, 0.001))
        glow_stroke(ctx, ORANGE, 6, pc)
    label(ctx, "Polo Norte", cx, cy, 30, WHITE, 0.7 * pc, NORM)

def s_still(ctx, t, d):
    # night sky over a rooftop; stars rotate around the pole, satellite stays fixed
    px, py = 120, 640
    rot = t * 0.18
    rnd = random.Random(11)
    for k in range(150):
        r = rnd.uniform(80, 1700); a0 = rnd.uniform(0, 2 * math.pi); b = rnd.uniform(0.3, 1)
        x = px + r * math.cos(a0 + rot); y = py + r * math.sin(a0 + rot)
        if 0 < x < W and 560 < y < 1700:
            ctx.arc(px, py, r, a0, a0 + rot)
            rgba(ctx, (0.7, 0.85, 1.0), 0.25 * b); ctx.set_line_width(2); ctx.stroke()
            ctx.arc(x, y, 2.6 * b, 0, 6.3); rgba(ctx, WHITE, b); ctx.fill()
    base = 1800
    draw_building(ctx, 560, base, 700, 220, 9)
    mx, my = 470, base - 232
    ctx.move_to(mx, my); ctx.line_to(mx, my - 90)
    ctx.set_source(lin(mx - 4, 0, mx + 4, 0, [(0, (0.6, 0.62, 0.66)), (1, (0.3, 0.32, 0.35))])); ctx.set_line_width(9); ctx.stroke()
    satx, saty = 900, 900
    ang = math.atan2(saty - (my - 100), satx - mx)
    draw_dish3d(ctx, mx + 20, my - 105, 1.5, ang)
    pa = eo(prog(t, 0.5, 1.0))
    ctx.move_to(mx + 130, my - 170); ctx.line_to(satx, saty)
    ctx.set_dash([12, 12], -t * 50); rgba(ctx, CYAN, 0.6 * pa); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    glow_dot(ctx, satx, saty, 9 + 2 * math.sin(t * 5), CYAN, pa)
    label(ctx, "satélite", satx, saty - 60, 42, CYAN, pa)
    label(ctx, "las estrellas giran…", 300, 820, 38, WHITE, 0.85 * eo(prog(t, 1.2, 1.6)), NORM, box=True)
    label(ctx, "…el satélite no", 760, 1060, 38, CYAN, eo(prog(t, 1.9, 2.3)), BOLD, box=True)

def s_south(ctx, t, d):
    gx, gy, R = 430, 1180, 380
    lon0, lat0 = 2, 22
    p0 = eo(prog(t, 0, 0.5))
    G.draw_globe(ctx, gx, gy, R * (0.8 + 0.2 * p0), lon0, lat0, cshift=t * 0.004, a=p0)
    pe = eo(prog(t, 0.4, 1.1))
    if pe > 0:
        pts = []
        for lo in range(-90, 91, 3):
            x, y, v = G.project(0, lon0 + lo, gx, gy, R, lon0, lat0)
            if v: pts.append((x, y))
        sub = poly_partial(pts, pe)
        if len(sub) > 1:
            ctx.set_dash([16, 10]); draw_poly(ctx, sub); glow_stroke(ctx, ORANGE, 4, 1); ctx.set_dash([])
        label(ctx, "Ecuador", gx - 140, gy + 210, 40, ORANGE, pe, box=True)
    spx, spy, _ = G.project(40.4, -3.7, gx, gy, R, lon0, lat0)
    # satellite: direction of a geostationary point at 19.2E, drawn closer than real (not to scale)
    qx, qy, _ = G.project(0, 19.2, gx, gy, R, lon0, lat0)
    sx, sy = gx + (qx - gx) * 2.9, gy + (qy - gy) * 2.9
    sx, sy = min(sx, 940), sy
    sx, sy = 900, 1500
    pp = eo(prog(t, 1.0, 1.4))
    if pp > 0:
        glow_dot(ctx, spx, spy, 14, YELLOW, pp)
        label(ctx, "España", spx - 30, spy - 62, 44, YELLOW, pp, box=True)
    ps = eback(prog(t, 1.2, 1.7))
    draw_sat(ctx, sx, sy, 0.5 * ps, math.atan2(spy - sy, spx - sx) - math.pi / 2)
    pa = eio(prog(t, 1.6, 2.4))
    if pa > 0:
        x2 = spx + (sx - 70 - spx) * pa; y2 = spy + (sy - 50 - spy) * pa
        ctx.move_to(spx, spy); ctx.line_to(x2, y2); glow_stroke(ctx, YELLOW, 7, 1)
        arrow_head(ctx, x2, y2, math.atan2(sy - spy, sx - spx), 40, YELLOW)
    pc = eo(prog(t, 2.2, 2.7))
    if pc > 0:
        cx, cy = 900, 780
        ctx.move_to(cx, cy - 90); ctx.line_to(cx, cy + 90); rgba(ctx, WHITE, 0.8 * pc); ctx.set_line_width(5); ctx.stroke()
        arrow_head(ctx, cx, cy - 95, -math.pi / 2, 30, WHITE, 0.8 * pc)
        arrow_head(ctx, cx, cy + 95, math.pi / 2, 30, YELLOW, pc)
        label(ctx, "N", cx, cy - 145, 44, WHITE, pc); label(ctx, "S", cx, cy + 145, 50, YELLOW, pc)
    label(ctx, "(distancias no a escala)", 760, 1720, 30, WHITE, 0.6 * pc, NORM)

def s_waves(ctx, t, d):
    sx, sy = CX, 720
    draw_sat(ctx, sx, sy + math.sin(t * 2) * 5, 0.75, 0)
    # travelling sine wave down to the bottom
    lam = 150; amp = 50
    y0, y1 = sy + 90, 1720
    pw = eio(prog(t, 0.2, 1.2))
    yend = y0 + (y1 - y0) * pw
    if pw > 0:
        ctx.move_to(sx, y0)
        y = y0
        while y < yend:
            ctx.line_to(sx + amp * math.sin(2 * math.pi * (y - y0) / lam - t * 9), y); y += 4
        glow_stroke(ctx, CYAN, 6, 1)
    pr = eo(prog(t, 1.3, 1.8))
    if pr > 0:
        # wavelength ruler
        yy = 1150
        ph = (t * 9 / (2 * math.pi)) * lam
        ya = yy; yb = yy + lam
        rx = sx + 110
        ctx.move_to(rx, ya); ctx.line_to(rx, yb); rgba(ctx, YELLOW, pr); ctx.set_line_width(4); ctx.stroke()
        for yv in (ya, yb):
            ctx.move_to(rx - 18, yv); ctx.line_to(rx + 18, yv); ctx.stroke()
        label(ctx, "≈ 2,5 cm", rx + 150, yy + lam / 2, 50, YELLOW, pr, box=True)
        label(ctx, "microondas", sx - 230, 1000, 50, CYAN, pr, box=True)
    pw2 = eo(prog(t, 2.0, 2.5))
    if pw2 > 0:
        # wifi router
        rx, ry = 220, 1560
        rr(ctx, rx - 90, ry - 26, 180, 52, 12)
        ctx.set_source(lin(0, ry - 26, 0, ry + 26, [(0, (0.95, 0.96, 0.98, pw2)), (1, (0.6, 0.62, 0.66, pw2))])); ctx.fill()
        for k in (-1, 1):
            ctx.move_to(rx + 60 * k, ry - 26); ctx.line_to(rx + 75 * k, ry - 100)
        rgba(ctx, (0.3, 0.3, 0.35), pw2); ctx.set_line_width(8); ctx.stroke()
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1
            ctx.arc(rx, ry - 40, 40 + ph * 120, math.radians(215), math.radians(325))
            rgba(ctx, CYAN, (1 - ph) * pw2); ctx.set_line_width(6); ctx.stroke()
        label(ctx, "wifi: también microondas", rx + 20, ry + 90, 36, WHITE, pw2, NORM)

def s_weak(ctx, t, d):
    sx, sy = CX, 700
    draw_sat(ctx, sx, sy + math.sin(t * 2) * 5, 0.7, 0)
    for k in range(7):
        ph = ((t * 0.45 + k / 7) % 1.0)
        r = 90 + ph * 1100
        al = (1 - ph) ** 1.6 * clamp(t * 3)
        ctx.arc(sx, sy + 60, r, math.radians(30), math.radians(150))
        rgba(ctx, CYAN, al); ctx.set_line_width(max(1.0, 16 * (1 - ph))); ctx.stroke()
    base = 1800
    draw_building(ctx, 700, base, 360, 200, 5)
    draw_dish3d(ctx, 640, base - 300, 1.1, -math.pi / 2 + 0.3)
    ctx.move_to(620, base - 212); ctx.line_to(620, base - 290)
    rgba(ctx, (0.5, 0.52, 0.56)); ctx.set_line_width(8); ctx.stroke()
    pm = eo(prog(t, 0.9, 1.4))
    if pm > 0:
        mx, my = 170, 1250
        rr(ctx, mx - 60, my - 300, 120, 600, 20)
        rgba(ctx, (0.03, 0.06, 0.15), 0.9 * pm); ctx.fill_preserve()
        rgba(ctx, WHITE, 0.8 * pm); ctx.set_line_width(4); ctx.stroke()
        lvl = 0.05 + 0.02 * math.sin(t * 8)
        for k in range(10):
            on = k / 10 < lvl + 0.02
            rr(ctx, mx - 44, my + 270 - (k + 1) * 56, 88, 46, 8)
            rgba(ctx, RED if on else (0.15, 0.18, 0.28), pm if on else 0.6 * pm); ctx.fill()
        label(ctx, "SEÑAL", mx, my - 350, 42, WHITE, pm)

def s_lupa(ctx, t, d):
    lx, ly, lw = CX, 1120, 330
    # sun
    glow_dot(ctx, CX, 760, 48, YELLOW, eo(prog(t, 0, 0.4)))
    xs = [-270, -190, -110, -35, 35, 110, 190, 270]
    fy = 1560
    pr = prog(t, 0.4, 1.6)
    for i, xo in enumerate(xs):
        pts = [(lx + xo, 840), (lx + xo, ly + 0.0), (lx, fy)]
        p = eio(prog(t, 0.4 + i * 0.04, 1.6 + i * 0.04))
        if p > 0:
            draw_poly(ctx, poly_partial(pts, p)); glow_stroke(ctx, YELLOW, 3.5, 0.75)
    # paper
    ctx.move_to(220, 1520); ctx.line_to(860, 1520); ctx.line_to(960, 1640); ctx.line_to(120, 1640); ctx.close_path()
    ctx.set_source(lin(0, 1520, 0, 1640, [(0, (0.85, 0.82, 0.74)), (1, (0.6, 0.57, 0.5))])); ctx.fill()
    # hot spot
    ph = eo(prog(t, 1.6, 2.4))
    if ph > 0:
        glow_dot(ctx, lx, fy + 20, 16 * ph + 3 * math.sin(t * 20), (1, 0.95, 0.7), ph)
        for k in range(4):
            q = (t * 0.6 + k / 4) % 1
            ctx.arc(lx + 30 * math.sin(q * 6 + k), fy - q * 220, 12 + 26 * q, 0, 6.3)
            rgba(ctx, (0.8, 0.8, 0.85), 0.3 * (1 - q) * ph); ctx.fill()
    # lens
    ctx.save(); ctx.translate(lx, ly); ctx.scale(1, 0.24)
    ctx.arc(0, 0, lw, 0, 6.3); ctx.restore()
    g = cairo.LinearGradient(lx - lw, ly - 70, lx + lw, ly + 70)
    g.add_color_stop_rgba(0, 0.7, 0.9, 1.0, 0.45); g.add_color_stop_rgba(0.5, 0.9, 1.0, 1.0, 0.15); g.add_color_stop_rgba(1, 0.5, 0.75, 0.95, 0.4)
    ctx.set_source(g); ctx.fill_preserve()
    rgba(ctx, (0.25, 0.25, 0.28)); ctx.set_line_width(18); ctx.stroke_preserve()
    rgba(ctx, (0.75, 0.77, 0.8)); ctx.set_line_width(6); ctx.stroke()
    # handle
    ctx.move_to(lx + lw + 4, ly + 10); ctx.line_to(lx + lw + 120, ly + 140)
    rgba(ctx, (0.35, 0.18, 0.08)); ctx.set_line_width(40); ctx.stroke()
    label(ctx, "lupa", lx - lw - 30, ly - 90, 46, CYAN, eo(prog(t, 1.0, 1.4)), box=True)
    label(ctx, "¡todo en un punto!", CX, 1740, 46, YELLOW, ph, box=True)

VX, VY, F = CX, 1700, 300
HALF = 470
def main_parab(): return parab_pts(VX, VY, F, -HALF, HALF, 120)
RAYS = [-420, -330, -240, -150, -60, 60, 150, 240, 330, 420]

def rays(ctx, t, start, a=1.0, top=760):
    hits = 0
    for i, xr in enumerate(RAYS):
        hx, hy = VX + xr, VY - xr * xr / (4 * F)
        pts = [(hx, top), (hx, hy - 14), (VX, VY - F)]
        p = eio(prog(t, start + i * 0.05, start + 1.1 + i * 0.05))
        if p <= 0: continue
        draw_poly(ctx, poly_partial(pts, p)); glow_stroke(ctx, YELLOW, 3.5, 0.55 * a)
        if p >= 1:
            hits += 1
            for k in range(2):
                q = ((t - start) * 0.5 + k * 0.5 + i * 0.13) % 1.0
                x, y = point_at(pts, q); glow_dot(ctx, x, y, 7, YELLOW, a)
    return hits / len(RAYS)

def s_reflect(ctx, t, d):
    pp = eio(prog(t, 0, 0.7))
    draw_reflector(ctx, poly_partial(main_parab(), pp))
    frac = rays(ctx, t, 0.5)
    fx, fy = VX, VY - F
    glow_dot(ctx, fx, fy, (8 + 22 * frac) * (1 + 0.12 * math.sin(t * 10)), ORANGE, 0.3 + 0.7 * frac)
    label(ctx, "plato (parábola)", VX, VY + 90, 44, CYAN, eo(prog(t, 0.5, 0.9)), box=True)
    pl = eo(prog(t, 1.9, 2.3))
    if pl > 0:
        ctx.move_to(fx + 45, fy); ctx.line_to(fx + 120, fy - 50); rgba(ctx, ORANGE, pl); ctx.set_line_width(4); ctx.stroke()
        label(ctx, "FOCO", fx + 210, fy - 70, 54, ORANGE, pl, box=True)

def s_lnb(ctx, t, d):
    # zoomed: dish + LNB at focus
    draw_reflector(ctx, main_parab(), 0.9)
    rays(ctx, t + 4, 0, a=0.45)
    fx, fy = VX, VY - F
    # arm from dish edge to LNB
    ax, ay = VX + 380, VY - 380 * 380 / (4 * F)
    pa = eo(prog(t, 0.1, 0.5))
    ctx.move_to(ax, ay); ctx.line_to(ax + (fx + 25 - ax) * pa, ay + (fy - 80 - ay) * pa)
    ctx.set_source(lin(0, fy, 0, ay, [(0, (0.75, 0.77, 0.8)), (1, (0.4, 0.42, 0.45))])); ctx.set_line_width(12); ctx.stroke()
    draw_lnb_real(ctx, fx, fy + 6, 1.7 * eback(prog(t, 0.3, 0.8)))
    glow_dot(ctx, fx, fy + 4, 10 * (1 + 0.2 * math.sin(t * 9)), ORANGE, 0.9)
    pl = eo(prog(t, 0.8, 1.2))
    if pl > 0:
        ctx.move_to(fx - 70, fy - 120); ctx.line_to(fx - 150, fy - 190); rgba(ctx, ORANGE, pl); ctx.set_line_width(4); ctx.stroke()
        label(ctx, "LNB", fx - 220, fy - 220, 64, ORANGE, pl, box=True)
        label(ctx, "Low Noise Block", fx - 220, fy - 130, 30, WHITE, 0.8 * pl, NORM)

def s_chain(ctx, t, d):
    # LNB -> cable -> deco -> TV
    lx, ly = 220, 980
    draw_lnb_real(ctx, lx, ly, 1.5, 0)
    for k in range(3):  # incoming weak waves into horn
        ph = (t * 1.1 + k / 3) % 1
        ctx.arc(lx, ly + 260 - ph * 200, 30 + 60 * (1 - ph), math.radians(200), math.radians(340))
        rgba(ctx, CYAN, ph * 0.8); ctx.set_line_width(4); ctx.stroke()
    cable = [(lx, ly - 200), (lx, ly - 250), (560, ly - 250), (560, 1290), (540, 1310), (540, 1330)]
    cable = [(lx, ly - 200), (lx, ly - 260), (620, ly - 260), (620, 1300)]
    pc = eio(prog(t, 0.3, 1.0))
    if pc > 0:
        draw_poly(ctx, poly_partial(cable, pc)); rgba(ctx, (0.1, 0.1, 0.12)); ctx.set_line_width(14); ctx.stroke()
        draw_poly(ctx, poly_partial(cable, pc)); rgba(ctx, (0.35, 0.36, 0.4)); ctx.set_line_width(8); ctx.stroke()
    if pc >= 1:
        for k in range(4):
            q = ((t - 1.0) * 0.8 + k / 4) % 1.0
            x, y = point_at(cable, q); glow_dot(ctx, x, y, 9, CYAN)
    # amplification badge
    pa = eback(prog(t, 0.6, 1.0))
    if pa > 0:
        label(ctx, "LNB", lx + 150, ly - 90, 50, ORANGE, pa, box=True)
    pd = eo(prog(t, 1.0, 1.4))
    draw_deco(ctx, 620, 1340, 380, t, pd)
    label(ctx, "decodificador", 620, 1440, 40, WHITE, 0.9 * pd, NORM)
    cab2 = [(620, 1380), (620, 1460)]
    on = eo(prog(t, 2.0, 2.5))
    draw_tv_real(ctx, 620, 1660, 520, on, t, eo(prog(t, 1.4, 1.8)))

OVX, OVY, OF = 290, 1700, 300
OX0, OX1 = 110, 470

def s_offset(ctx, t, d):
    pf = eo(prog(t, 0.0, 0.9))
    full = parab_pts(OVX, OVY, OF, -320, 780, 120)
    sub = poly_partial(full, pf)
    if len(sub) > 1:
        ctx.set_dash([16, 12]); draw_poly(ctx, sub); rgba(ctx, CYAN, 0.5); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    label(ctx, "parábola gigante", 200, 1790, 38, CYAN, 0.9 * eo(prog(t, 0.6, 1.0)), NORM)
    pp = eo(prog(t, 0.9, 1.5))
    if pp > 0:
        draw_reflector(ctx, parab_pts(OVX, OVY, OF, OX0, OX1, 60), pp, edge=ORANGE)
    fx, fy = OVX, OVY - OF
    if t > 1.5:
        for i, xr in enumerate((150, 220, 290, 360, 430)):
            hx, hy = OVX + xr, OVY - xr * xr / (4 * OF)
            pts = [(hx, 760), (hx, hy - 14), (fx, fy)]
            p = eio(prog(t, 1.5 + i * 0.07, 2.4 + i * 0.07))
            draw_poly(ctx, poly_partial(pts, p)); glow_stroke(ctx, YELLOW, 3.5, 0.6)
            if p >= 1:
                q = ((t - 2.4) * 0.6 + i * 0.17) % 1.0
                x, y = point_at(pts, q); glow_dot(ctx, x, y, 7, YELLOW)
        ang = math.atan2(OVY - 290 * 290 / (4 * OF) - fy, OVX + 290 - fx) - math.pi / 2
        draw_lnb_real(ctx, fx, fy, 1.0 * eback(prog(t, 2.1, 2.5)), ang)
    pl = eo(prog(t, 2.7, 3.1))
    label(ctx, "tu antena", 900, 1560, 48, ORANGE, pl, box=True)
    # real dish icon for association
    pd = eback(prog(t, 3.0, 3.5))
    if pd > 0:
        draw_dish3d(ctx, 860, 900, 1.2 * pd, -0.6)

def s_shadow(ctx, t, d):
    def panel(cx, offset, a, ok):
        f = 120
        if not offset:
            vx, vy = cx, 1450; xs = [-170, -115, -60, 0, 60, 115, 170]; px0, px1 = -200, 200
        else:
            vx, vy = cx - 170, 1520; xs = [80, 130, 180, 230, 280, 330]; px0, px1 = 60, 360
        fx, fy = vx, vy - f
        top = 760
        for xr in xs:
            hx, hy = vx + xr, vy - xr * xr / (4 * f)
            if (not offset) and abs(xr) <= 60:
                ctx.move_to(hx, top); ctx.line_to(hx, fy - 120)
            else:
                ctx.move_to(hx, top); ctx.line_to(hx, hy - 10); ctx.line_to(fx, fy)
            rgba(ctx, YELLOW, 0.65 * a); ctx.set_line_width(4); ctx.stroke()
        if not offset:
            ctx.move_to(fx - 70, fy - 110); ctx.line_to(fx + 70, fy - 110); ctx.line_to(fx + 85, vy - 70 * 70 / (4 * f)); ctx.line_to(fx - 85, vy - 85 * 85 / (4 * f)); ctx.close_path()
            rgba(ctx, (0, 0, 0), 0.6 * a); ctx.fill()
            label(ctx, "sombra", fx, fy + 20, 34, RED, a)
        draw_reflector(ctx, parab_pts(vx, vy, f, px0, px1, 60), a, thick=18, edge=CYAN if not offset else ORANGE)
        rot = 0 if not offset else math.atan2(vy - 220 * 220 / (4 * f) - fy, vx + 220 - fx) - math.pi / 2
        draw_lnb_real(ctx, fx, fy, 0.8, rot, a)
    pa = eo(prog(t, 0, 0.5)); pb = eo(prog(t, 0.4, 0.9))
    panel(270, False, pa, False); panel(820, True, pb, True)
    pm = eback(prog(t, 1.3, 1.7))
    if pm > 0:
        x, y, r = 270, 1640, 48 * pm
        ctx.move_to(x - r, y - r); ctx.line_to(x + r, y + r); ctx.move_to(x + r, y - r); ctx.line_to(x - r, y + r)
        glow_stroke(ctx, RED, 12, 1)
    pc = eback(prog(t, 1.7, 2.1))
    if pc > 0:
        x, y, r = 800, 1640, 48 * pc
        ctx.move_to(x - r, y); ctx.line_to(x - r * 0.25, y + r * 0.7); ctx.line_to(x + r, y - r * 0.8)
        glow_stroke(ctx, GREEN, 12, 1)
    label(ctx, "centrada", 270, 1760, 40, WHITE, 0.85 * pa, NORM)
    label(ctx, "offset (ovalada)", 800, 1760, 40, WHITE, 0.85 * pb, NORM)

def s_fact(ctx, t, d):
    pb = eback(prog(t, 0, 0.4))
    if pb > 0:
        ctx.save(); ctx.translate(CX, 190); ctx.scale(pb, pb); ctx.rotate(-0.04)
        rr(ctx, -200, -50, 400, 100, 20); rgba(ctx, YELLOW); ctx.fill(); ctx.restore()
        label(ctx, "¡DATO!", CX, 190, 64 * pb, NAVY)
    s = "0," + "0" * 11 + "1"
    n = int(len(s) * eio(prog(t, 0.7, 2.0)))
    if n > 0:
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, BOLD); size = 104; ctx.set_font_size(size)
        full_w = ctx.text_extents(s + " W")[4]
        x = CX - full_w / 2; y = 1010
        for i, ch in enumerate(s[:n]):
            ctx.move_to(x, y); ctx.text_path(ch)
            rgba(ctx, (0, 0, 0), 0.6); ctx.set_line_width(14); ctx.stroke_preserve()
            rgba(ctx, YELLOW if i == len(s) - 1 else CYAN); ctx.fill()
            x += ctx.text_extents(ch)[4]
        if n == len(s):
            ctx.move_to(x + 20, y); ctx.text_path("W"); rgba(ctx, WHITE); ctx.fill()
    label(ctx, "vatios", CX, 1090, 46, WHITE, 0.85 * eo(prog(t, 2.0, 2.4)), NORM)
    pc = eo(prog(t, 2.4, 2.9))
    if pc > 0:
        bx, by = 290, 1400
        # bulb
        g = cairo.RadialGradient(bx, by, 10, bx, by, 260)
        g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.6 * pc); g.add_color_stop_rgba(1, 1, 0.9, 0.5, 0)
        ctx.set_source(g); ctx.arc(bx, by, 260, 0, 6.3); ctx.fill()
        ctx.arc(bx, by - 10, 75, math.radians(140), math.radians(40))
        ctx.line_to(bx + 34, by + 95); ctx.line_to(bx - 34, by + 95); ctx.close_path()
        ctx.set_source(lin(bx - 75, 0, bx + 75, 0, [(0, (1, 0.95, 0.75, pc)), (0.5, (1, 1, 0.95, pc)), (1, (1, 0.85, 0.5, pc))])); ctx.fill()
        ctx.rectangle(bx - 34, by + 95, 68, 50); ctx.set_source(lin(bx - 34, 0, bx + 34, 0, [(0, (0.5, 0.5, 0.55, pc)), (0.5, (0.9, 0.9, 0.95, pc)), (1, (0.45, 0.45, 0.5, pc))])); ctx.fill()
        label(ctx, "bombilla LED: 10 W", bx, by + 210, 38, YELLOW, pc)
        dx, dy = 800, 1400
        draw_dish3d(ctx, dx - 40, dy, 1.0 * pc, -0.6)
        glow_dot(ctx, dx + 50, dy - 60, 4, CYAN, pc)
        label(ctx, "a tu antena le llega", dx, dy + 170, 36, CYAN, pc, NORM)
        label(ctx, "10 billones de veces menos", dx - 20, dy + 220, 36, CYAN, pc)

def s_cta(ctx, t, d):
    base = 1820
    draw_building(ctx, 380, base + 400 * (1 - eo(prog(t, 0, 0.5))), 420, 420, 21)
    if t > 0.5:
        mx, my = 300, base - 432
        ctx.move_to(mx, my); ctx.line_to(mx, my - 90)
        ctx.set_source(lin(mx - 4, 0, mx + 4, 0, [(0, (0.6, 0.62, 0.66)), (1, (0.3, 0.32, 0.35))])); ctx.set_line_width(9); ctx.stroke()
        draw_dish3d(ctx, mx + 20, my - 105, 1.5 * eback(prog(t, 0.5, 0.9)), -0.75 + 0.06 * math.sin(t * 3))
    pb = eback(prog(t, 0.9, 1.4))
    if pb > 0:
        bx, by = 760, 940
        ctx.save(); ctx.translate(bx, by); ctx.scale(pb, pb)
        r = 44; w2, h2 = 210, 110
        ctx.new_sub_path()
        ctx.arc(-w2 + r, -h2 + r, r, math.pi, 1.5 * math.pi); ctx.arc(w2 - r, -h2 + r, r, 1.5 * math.pi, 0)
        ctx.arc(w2 - r, h2 - r, r, 0, 0.5 * math.pi)
        ctx.line_to(-40, h2); ctx.line_to(-130, h2 + 80); ctx.line_to(-110, h2)
        ctx.arc(-w2 + r, h2 - r, r, 0.5 * math.pi, math.pi); ctx.close_path()
        rgba(ctx, CYAN); ctx.fill()
        for k in range(3):
            yy = -18 * max(0, math.sin(t * 6 - k * 0.8))
            ctx.arc(-85 + k * 85, yy, 20, 0, 6.2832); rgba(ctx, NAVY); ctx.fill()
        ctx.restore()
    label(ctx, "¡Te leo en comentarios!", 790, 1310, 46, YELLOW, eo(prog(t, 1.4, 1.9)), box=True)

SCENES = [
    (3.0, "¿Por qué todas las parabólicas miran al sur?", {6, 7}, YELLOW, s_hook),
    (3.0, "La tele llega desde el espacio", {5}, CYAN, s_space),
    (4.0, "Desde un satélite a 36.000 km", {2, 4, 5}, CYAN, s_distance),
    (4.0, "Da una vuelta cada 24 horas", {4, 5}, ORANGE, s_spin),
    (3.5, "Como la Tierra: desde casa parece quieto", {5, 6}, CYAN, s_still),
    (4.0, "Flota sobre el ecuador, al sur de España", {3, 4, 5}, YELLOW, s_south),
    (3.5, "Emite microondas, como tu wifi", {1}, CYAN, s_waves),
    (3.5, "Pero llegan muy, muy débiles", {2, 3, 4}, RED, s_weak),
    (4.0, "Hay que concentrarlas, como con una lupa", {2, 6}, YELLOW, s_lupa),
    (4.0, "La parábola rebota todo hacia un punto", {1, 5, 6}, ORANGE, s_reflect),
    (4.0, "En ese punto, el foco, está el LNB", {4, 7}, ORANGE, s_lnb),
    (4.0, "Amplifica la señal y la manda al deco", {0, 7}, CYAN, s_chain),
    (4.0, "Es ovalada: un trozo de parábola gigante", {1, 5, 6}, ORANGE, s_offset),
    (3.5, "Así el LNB no tapa la señal", {3, 4}, GREEN, s_shadow),
    (4.5, "Llega una billonésima de vatio", {1, 2}, YELLOW, s_fact),
    (3.0, "¿Hacia dónde mira la antena de tu casa?", {0, 1, 2}, CYAN, s_cta),
]

def render_frame(idx, t, T):
    dur, text, hl, hlc, fn = SCENES[idx]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw_bg(ctx, T)
    env = min(prog(t, 0, 0.16), 1 - prog(t, dur - 0.14, dur))
    if idx == len(SCENES) - 1:
        env = min(prog(t, 0, 0.16), 1 - prog(t, dur - 0.5, dur))
    ctx.push_group()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(ctx, t, dur)
    draw_headline(ctx, t, text, hl, hlc, ycenter=400 if idx != 14 else 440)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(env)
    return surf

def scene_start(idx): return sum(s[0] for s in SCENES[:idx])

def render_scene(idx, outdir):
    dur = SCENES[idx][0]; n = int(round(dur * FPS))
    tmp = os.path.join(outdir, f"tmp_{idx:02d}.mp4"); final = os.path.join(outdir, f"scene_{idx:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    T0 = scene_start(idx)
    for f in range(n):
        t = f / FPS
        p.stdin.write(bytes(render_frame(idx, t, T0 + t).get_data()))
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, final)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        idx = int(sys.argv[2]); t = float(sys.argv[3])
        render_frame(idx, t, scene_start(idx) + t).write_to_png(sys.argv[4])
    elif mode == "scenes":
        for i in map(int, sys.argv[3:]): render_scene(i, sys.argv[2])
