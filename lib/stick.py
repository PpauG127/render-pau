"""Story-channel kit: stickman, word-by-word captions, HUD meters, noir palette."""
import cairo, math, random
from engine import *

ACC = (0.95, 0.18, 0.22)      # red accent
AMB = (1.0, 0.78, 0.2)        # yellow accent
INK = (0.94, 0.95, 0.98)      # stickman white
WALL = [(0, (0.16, 0.18, 0.22)), (0.5, (0.11, 0.12, 0.15)), (1, (0.06, 0.07, 0.09))]

# ------------------------------------------------------------------ stickman
POSES = {
    'idle':    dict(la=(0.15, 0.1), ra=(-0.15, -0.1), ll=(0.12, 0.0), rl=(-0.12, 0.0)),
    'phone':   dict(la=(0.15, 0.1), ra=(-0.5, -2.3), ll=(0.12, 0.0), rl=(-0.12, 0.0)),
    'scared':  dict(la=(2.3, 0.5), ra=(-2.3, -0.5), ll=(0.3, 0.1), rl=(-0.3, -0.1)),
    'brace':   dict(la=(1.2, 1.4), ra=(-1.2, -1.4), ll=(0.7, -1.4), rl=(-0.7, 1.4), dy=60),
    'jump':    dict(la=(2.8, 0.2), ra=(-2.8, -0.2), ll=(0.5, -1.2), rl=(-0.5, 1.2), dy=-120),
    'pray':    dict(la=(0.9, 1.9), ra=(-0.9, -1.9), ll=(1.5, -1.6), rl=(-1.5, 1.6), dy=110),
    'relief':  dict(la=(0.35, 0.2), ra=(-0.35, -0.2), ll=(0.1, 0.0), rl=(-0.1, 0.0)),
    'shrug':   dict(la=(1.0, -1.7), ra=(-1.0, 1.7), ll=(0.12, 0.0), rl=(-0.12, 0.0)),
    'sit':     dict(la=(0.5, 0.4), ra=(-0.5, -0.4), ll=(1.5, 0.05), rl=(1.38, 0.12)),
    'hug':     dict(la=(-0.6, -1.7), ra=(0.6, 1.7), ll=(1.5, 0.05), rl=(1.38, 0.12)),
    'wave':    dict(la=(0.5, 0.4), ra=(-2.9, -0.4), ll=(1.5, 0.05), rl=(1.38, 0.12)),
    'aim':     dict(la=(0.5, 0.4), ra=(-2.2, 0.0), ll=(1.5, 0.05), rl=(1.38, 0.12)),
    'point':   dict(la=(0.15, 0.1), ra=(-1.57, 0.0), ll=(0.12, 0.0), rl=(-0.12, 0.0)),
}

def lerp_pose(a, b, k):
    A, B = POSES[a] if isinstance(a, str) else a, POSES[b] if isinstance(b, str) else b
    out = {}
    for key in set(A) | set(B):
        va, vb = A.get(key, 0), B.get(key, 0)
        if isinstance(va, tuple) or isinstance(vb, tuple):
            va = va if isinstance(va, tuple) else (0, 0); vb = vb if isinstance(vb, tuple) else (0, 0)
            out[key] = tuple(x + (y - x) * k for x, y in zip(va, vb))
        else:
            out[key] = va + (vb - va) * k
    return out

def stickman(ctx, x, y, s=1.0, pose='idle', look=(0, 0), fear=0.0, mouth='flat', blink=0.0, rot=0.0, a=1.0,
             phone=False, sweat=0.0, t=0.0, col=INK, shadow=True, tilt=0.0, squash=0.0, emote=None, shiver=0.0):
    P = POSES[pose] if isinstance(pose, str) else pose
    jx = shiver * 6 * math.sin(t * 70)
    ctx.save(); ctx.translate(x + jx * s, y + P.get('dy', 0) * s); ctx.rotate(rot); ctx.scale(s * (1 + 0.5 * squash), s * (1 - squash))
    ctx.push_group()
    # ground shadow
    if shadow:
        ctx.save(); ctx.scale(1, 0.18); ctx.arc(0, 10 / 0.18, 95, 0, 6.3); ctx.restore()
        rgba(ctx, (0, 0, 0), 0.45); ctx.fill()
    lw = 17
    ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    hip = (0, -150); sh = (0, -285)
    def limb(origin, ang, l1, l2):
        a1, a2 = ang
        e = (origin[0] + l1 * math.sin(a1), origin[1] + l1 * math.cos(a1))
        h = (e[0] + l2 * math.sin(a1 + a2), e[1] + l2 * math.cos(a1 + a2))
        ctx.move_to(*origin); ctx.line_to(*e); ctx.line_to(*h)
        return h
    rgba(ctx, col)
    hl = limb(hip, P['ll'], 78, 78); ctx.stroke()
    hr = limb(hip, P['rl'], 78, 78); ctx.stroke()
    ctx.move_to(*hip); ctx.line_to(*sh); ctx.stroke()
    pl = limb(sh, P['la'], 70, 66); ctx.stroke()
    pr = limb(sh, P['ra'], 70, 66); ctx.stroke()
    for h in (pl, pr):
        ctx.arc(h[0], h[1], 11, 0, 6.3); ctx.fill()
    if phone:
        ctx.save(); ctx.translate(pr[0] + 6, pr[1] - 22); ctx.rotate(-0.2)
        rr(ctx, -20, -34, 40, 68, 7); rgba(ctx, (0.08, 0.08, 0.1)); ctx.fill()
        rr(ctx, -16, -29, 32, 58, 5); rgba(ctx, (0.35, 0.65, 1.0), 0.95); ctx.fill()
        ctx.restore()
        g = cairo.RadialGradient(pr[0], pr[1] - 30, 5, pr[0], pr[1] - 30, 120)
        g.add_color_stop_rgba(0, 0.4, 0.7, 1, 0.25); g.add_color_stop_rgba(1, 0.4, 0.7, 1, 0)
        ctx.set_source(g); ctx.paint()
    # head (own transform: tilt)
    hy = -360
    ctx.save(); ctx.translate(0, hy + 50); ctx.rotate(tilt); ctx.translate(0, -hy - 50)
    g = cairo.RadialGradient(-20, hy - 25, 5, 0, hy, 72)
    g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, col[0] * 0.78, col[1] * 0.8, col[2] * 0.85)
    ctx.arc(0, hy, 70, 0, 6.3); ctx.set_source(g); ctx.fill()
    # eyes
    er = 17 + 9 * fear
    for sx in (-1, 1):
        ex, ey = sx * 25 + look[0] * 6, hy - 8 + look[1] * 4
        ctx.save(); ctx.translate(ex, ey); ctx.scale(1, max(0.08, 1 - blink) * (1.15 + 0.2 * fear))
        ctx.arc(0, 0, er, 0, 6.3); rgba(ctx, WHITE); ctx.fill_preserve()
        rgba(ctx, (0.1, 0.1, 0.14)); ctx.set_line_width(3); ctx.stroke()
        pr_ = 8 - 2 * fear
        ctx.arc(look[0] * 6, look[1] * 6, pr_, 0, 6.3); rgba(ctx, (0.05, 0.05, 0.08)); ctx.fill()
        ctx.arc(look[0] * 6 - 3, look[1] * 6 - 3, 2.5, 0, 6.3); rgba(ctx, WHITE); ctx.fill()
        ctx.restore()
        # brows: worried = inner end up
        ctx.move_to(ex - sx * 18, ey - er - 10 - 10 * fear); ctx.line_to(ex + sx * 18, ey - er - 6 + 4 * fear)
        rgba(ctx, (0.15, 0.15, 0.2)); ctx.set_line_width(5); ctx.stroke()
    # mouth
    my = hy + 35
    rgba(ctx, (0.15, 0.15, 0.2)); ctx.set_line_width(5)
    if mouth == 'o':
        ctx.save(); ctx.translate(0, my); ctx.scale(1, 1.3); ctx.arc(0, 0, 9 + 5 * fear, 0, 6.3); ctx.restore(); ctx.fill()
    elif mouth == 'smile':
        ctx.arc(0, my - 12, 18, 0.35, math.pi - 0.35); ctx.stroke()
    elif mouth == 'wavy':
        ctx.move_to(-16, my)
        for i in range(1, 9): ctx.line_to(-16 + i * 4, my + (3 if i % 2 else -3))
        ctx.stroke()
    else:
        ctx.move_to(-12, my); ctx.line_to(12, my); ctx.stroke()
    if sweat > 0:
        for k, (sx, sy) in enumerate(((60, hy - 30), (-62, hy - 10))):
            q = (t * 0.8 + k * 0.5) % 1
            yy = sy + q * 40
            ctx.move_to(sx, yy - 14); ctx.curve_to(sx + 8, yy, sx + 8, yy + 8, sx, yy + 8); ctx.curve_to(sx - 8, yy + 8, sx - 8, yy, sx, yy - 14)
            rgba(ctx, (0.55, 0.8, 1.0), sweat * (1 - q)); ctx.fill()
    if emote == 'tears':
        for sx in (-1, 1):
            q = (t * 1.2) % 1
            ctx.move_to(sx * 25, hy + 12); ctx.line_to(sx * 32, hy + 30 + 60 * q)
            rgba(ctx, (0.5, 0.8, 1.0), 0.8); ctx.set_line_width(8); ctx.stroke()
    ctx.restore()
    if emote in ('!', '?', '!!'):
        pp = min(1.0, (t % 10) * 6)
        ctx.save(); ctx.translate(95, hy - 120); ctx.rotate(0.2 * math.sin(t * 9)); ctx.scale(pp, pp)
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(120)
        ctx.move_to(-30, 40); ctx.text_path(emote)
        rgba(ctx, (0, 0, 0), 0.9); ctx.set_line_width(14); ctx.stroke_preserve()
        rgba(ctx, ACC if emote != '?' else AMB); ctx.fill()
        ctx.restore()
    if emote == 'shock':
        for k in range(8):
            an = -math.pi / 2 + (k - 3.5) * 0.28
            r0 = 95 + 10 * math.sin(t * 20)
            ctx.move_to(r0 * math.cos(an), hy + r0 * math.sin(an)); ctx.line_to((r0 + 45) * math.cos(an), hy + (r0 + 45) * math.sin(an))
        rgba(ctx, AMB); ctx.set_line_width(7); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

def blink_at(t, every=2.7, off=0.0):
    q = (t + off) % every
    return max(0.0, 1 - abs(q - 0.08) / 0.08) if q < 0.16 else 0.0

# ------------------------------------------------------------------ captions
def caption(ctx, t, text, t0, t1, y=1480, size=92, chunk=3, hl=AMB):
    words = text.split()
    if not words: return
    wts = [len(w.strip('.,?!…')) + 2.5 for w in words]
    tot = sum(wts); times = []; acc = t0
    for wv in wts:
        times.append(acc); acc += (t1 - t0) * wv / tot
    times.append(t1)
    cur = max(i for i in range(len(words)) if times[i] <= max(t, t0)) if t >= t0 else -1
    if cur < 0: return
    g0 = (cur // chunk) * chunk
    grp = list(range(g0, min(len(words), g0 + chunk)))
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    space = ctx.text_extents(" ")[4] * 1.6
    widths = [ctx.text_extents(words[i].upper())[4] for i in grp]
    total = sum(widths) + space * (len(grp) - 1)
    fit = min(1.0, 940 / max(1, total))
    ctx.save(); ctx.translate(CX, y); ctx.scale(fit, fit); ctx.translate(-CX, -y)
    x = CX - total / 2
    for i, w in zip(grp, widths):
        if i > cur: break
        s = words[i].upper()
        p = clamp((t - times[i]) / 0.12)
        sc = 0.7 + 0.3 * eback(p) + (0.08 if i == cur else 0)
        ctx.save(); ctx.translate(x + w / 2, y); ctx.scale(sc, sc); ctx.translate(-w / 2, size * 0.36)
        ctx.move_to(0, 0); ctx.text_path(s)
        rgba(ctx, (0, 0, 0), 0.95); ctx.set_line_width(20); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
        rgba(ctx, hl if i == cur else WHITE); ctx.fill()
        ctx.restore()
        x += w + space
    ctx.restore()

# ------------------------------------------------------------------ HUD meters
def heart_meter(ctx, t, bpm, x=40, y=170, a=1.0):
    if a <= 0: return
    rr(ctx, x, y, 330, 120, 22); rgba(ctx, (0.02, 0.02, 0.04), 0.75 * a); ctx.fill_preserve()
    danger = clamp((bpm - 90) / 70)
    col = (0.4 + 0.55 * danger, 0.9 - 0.7 * danger, 0.5 - 0.3 * danger)
    rgba(ctx, col, 0.9 * a); ctx.set_line_width(3); ctx.stroke()
    beat = (t * bpm / 60) % 1
    hs = 1 + 0.25 * max(0, 1 - beat * 5)
    ctx.save(); ctx.translate(x + 55, y + 60); ctx.scale(hs * 1.6, hs * 1.6)
    ctx.move_to(0, 10); ctx.curve_to(-22, -6, -12, -22, 0, -10); ctx.curve_to(12, -22, 22, -6, 0, 10)
    ctx.restore(); rgba(ctx, ACC, a); ctx.fill()
    label(ctx, f"{int(bpm)}", x + 165, y + 50, 56, col, a)
    label(ctx, "BPM", x + 270, y + 55, 30, WHITE, 0.8 * a, NORM)
    # ecg trace
    ctx.move_to(x + 110, y + 100)
    for i in range(60):
        xx = x + 110 + i * 3.5
        ph = (beat - i / 60 * 1.5) % 1
        yy = y + 100 - (26 if ph < 0.04 else (-10 if ph < 0.08 else 0))
        ctx.line_to(xx, yy)
    rgba(ctx, col, 0.9 * a); ctx.set_line_width(3); ctx.stroke()

def speed_meter(ctx, v, vmax=40, x=CX, y=1700, r=140, a=1.0, unit="mph"):
    if a <= 0: return
    ctx.arc(x, y, r, math.pi, 2 * math.pi); rgba(ctx, (0.02, 0.02, 0.04), 0.8 * a); ctx.fill()
    for k in range(3):
        a0 = math.pi + k * math.pi / 3
        ctx.arc(x, y, r - 18, a0, a0 + math.pi / 3)
        rgba(ctx, ((0.3, 0.9, 0.5), AMB, ACC)[k], 0.85 * a); ctx.set_line_width(20); ctx.stroke()
    ang = math.pi + math.pi * clamp(v / vmax)
    ctx.move_to(x, y); ctx.line_to(x + (r - 30) * math.cos(ang), y + (r - 30) * math.sin(ang))
    rgba(ctx, WHITE, a); ctx.set_line_width(7); ctx.stroke()
    ctx.arc(x, y, 12, 0, 6.3); rgba(ctx, WHITE, a); ctx.fill()
    label(ctx, f"{int(v)} {unit}", x, y + 50, 46, WHITE, a)

def flash(ctx, k, col=(1, 1, 1)):
    if k > 0:
        ctx.save(); ctx.identity_matrix(); rgba(ctx, col, k); ctx.paint(); ctx.restore()
