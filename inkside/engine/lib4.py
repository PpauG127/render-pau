"""Quick silhouette people + extra topic icons (whiteboard line style)."""
import math, random
from lib3 import *
from engine import TW as T, flat, P, F, S, place, circle, oval, skia, TF

def _rev(segs, start):
    """reverse a list of cubic segments [(c1,c2,end)] that begins at `start`."""
    pts = [start] + [s[2] for s in segs]
    out = []
    for i in range(len(segs) - 1, -1, -1):
        c1, c2, _ = segs[i]
        out.append((c2, c1, pts[i]))
    return out

def _mir(p): return (-p[0], p[1])

def _contour(left_start, left):
    """left: cubic segments from the neck (left) down to the crotch; mirrored to close the body."""
    right = [(_mir(a), _mir(b), _mir(c)) for a, b, c in _rev(left, left_start)]
    d = f"M{left_start[0]} {left_start[1]} "
    for a, b, c in left + right:
        d += f"C{a[0]} {a[1]} {b[0]} {b[1]} {c[0]} {c[1]} "
    return d

ARMS = {
 "down": [((-60, -758), (-120, -748), (-140, -700)), ((-158, -620), (-166, -520), (-160, -440)),
          ((-162, -396), (-118, -392), (-120, -440)), ((-124, -520), (-118, -600), (-112, -650))],
}

def fig(hair="none", expr="blank", pose="down", s=1.0):
    """simple outline person (feet at 0, ~1000 tall): head + one body contour + tiny face + hair outline."""
    e = [ln(circle(0, -890, 92), 8)]
    # face
    if expr == "sinister":
        e += [ln("M-46 -912 L-14 -900", 6), ln("M14 -900 L46 -912", 6), F(oval(-28, -888, 7, 5), K_), F(oval(28, -888, 7, 5), K_),
              ln("M-24 -846 Q4 -830 28 -850", 6)]
    elif expr == "scared":
        e += [F(oval(-28, -892, 8, 12), K_), F(oval(28, -892, 8, 12), K_), ln(oval(0, -846, 10, 14), 6)]
    elif expr == "happy":
        e += [F(oval(-28, -892, 7, 11), K_), F(oval(28, -892, 7, 11), K_), ln("M-24 -852 Q0 -830 26 -852", 6)]
    elif expr == "sad":
        e += [F(oval(-28, -890, 7, 10), K_), F(oval(28, -890, 7, 10), K_), ln("M-20 -840 Q0 -854 22 -840", 6)]
    elif expr == "blank":
        e += [F(oval(-28, -890, 7, 10), K_), F(oval(28, -890, 7, 10), K_)]
    # hair outline only
    if hair == "bob":
        e += [ln("M-96 -880 C-110 -1000 110 -1006 96 -880 L98 -810", 7), ln("M-96 -880 L-98 -810", 7),
              ln("M-70 -960 C-40 -936 30 -936 70 -960", 6)]
    elif hair == "pony":
        e += [ln("M-90 -930 C-60 -990 40 -1000 80 -950", 6),
              ln("M78 -960 C150 -950 168 -860 140 -770 C134 -750 120 -756 122 -780 C138 -850 128 -910 92 -930", 7)]
        bow = P("M66 -980 C88 -1018 118 -1000 104 -974 C130 -972 134 -938 104 -950 C98 -934 78 -944 76 -960 Z")
        e += [ln(bow, 6), F(bow, RED)]
    elif hair == "long":
        e += [ln("M-94 -900 C-110 -1004 110 -1004 94 -900 C100 -820 100 -760 92 -700", 7),
              ln("M-94 -900 C-100 -820 -100 -760 -92 -700", 7), ln("M-10 -982 C-40 -950 -70 -930 -88 -900", 5)]
    elif hair == "short":
        e += [ln("M-88 -920 C-70 -1000 70 -1000 88 -920", 7), ln("M-88 -920 C-40 -960 40 -960 88 -920", 5)]
    # body contour
    neck = (-24, -798)
    body = [((-24, -786), (-24, -770), (-26, -760))]
    if pose in ("down", "point", "walk"):
        body += ARMS["down"]
    elif pose == "up":
        body += [((-60, -764), (-110, -770), (-140, -820)), ((-160, -860), (-176, -930), (-170, -980)),
                 ((-164, -1006), (-134, -1000), (-136, -970)), ((-130, -900), (-112, -830), (-104, -740))]
    body += [((-104, -600), (-100, -500), (-96, -440))]
    if pose == "walk":
        body += [((-120, -320), (-150, -160), (-176, -30)), ((-180, -10), (-150, 0), (-110, 0)),
                 ((-100, -100), (-60, -260), (0, -372))]
    else:
        body += [((-106, -300), (-98, -150), (-92, -24)), ((-100, 0), (-60, 4), (-24, 0)),
                 ((-20, -120), (-14, -260), (0, -372))]
    d = _contour(neck, body)
    e.append(ln(d, 8))
    if pose == "point":
        e += [ln("M140 -700 C220 -690 300 -686 380 -684", 8), ln("M112 -650 C200 -650 290 -652 380 -650", 8),
              ln("M380 -684 C410 -684 432 -676 440 -668 L386 -662 C404 -656 404 -646 380 -650", 7)]
    return place(e, 0, 0, s) if s != 1 else e

def lying_fig(expr="blank"):
    els = fig("long", expr)
    m = skia.Matrix(); m.setRotate(-90); m.postScale(0.5, 0.5)
    return [e.transformed(m) for e in flat(els)]

def kid(x, y, s=0.45, **kw):
    return place(fig(**kw), x, y, s)

# ---------- topic icons ----------
def money_bag():
    bag = "M-40 -200 C-160 -120 -170 40 0 40 C170 40 160 -120 40 -200 Z"
    return [ln(bag, 8), ln("M-50 -200 L50 -200 M-30 -240 L30 -240 L50 -200 M-30 -240 L-50 -200", 7), T("$", 0, -20, 140, "marker", K_)]

def fist():
    return [ln("M-90 -60 C-100 -150 -40 -170 0 -160 C40 -170 100 -150 90 -60 L80 40 L-80 40 Z", 8),
            ln("M-60 -150 L-60 -100 M-20 -160 L-20 -104 M20 -160 L20 -104 M60 -150 L60 -100", 5),
            ln("M-80 40 L-90 130 M80 40 L90 130", 8)]

def cross(w=200):
    return [ln(f"M{-w} {-w} L{w} {w}", 18, RED), ln(f"M{w} {-w} L{-w} {w}", 18, RED)]

def trophy():
    return [ln("M-90 -260 L90 -260 C90 -150 50 -100 0 -96 C-50 -100 -90 -150 -90 -260 Z", 8),
            ln("M-90 -230 C-150 -230 -150 -150 -70 -140", 7), ln("M90 -230 C150 -230 150 -150 70 -140", 7),
            ln("M-14 -96 L-20 -40 M14 -96 L20 -40", 7), ln("M-70 -40 L70 -40 L70 0 L-70 0 Z", 8)]

def ghost():
    return [ln("M-60 60 L-60 -30 C-60 -110 60 -110 60 -30 L60 60 L40 44 L20 60 L0 44 L-20 60 L-40 44 Z", 7),
            F(oval(-20, -30, 9, 13), K_), F(oval(20, -30, 9, 13), K_), ln(oval(0, 8, 9, 12), 5)]

def photo(w=360, h=260, ghosty=True):
    e = [ln(f"M{-w/2} {-h} L{w/2} {-h} L{w/2} 0 L{-w/2} 0 Z", 8), ln(f"M{-w/2+20} {-h+20} L{w/2-20} {-h+20} L{w/2-20} -20 L{-w/2+20} -20 Z", 5)]
    if ghosty: e += place(ghost(), 0, -h / 2 - 6, 0.9)
    return e

def eye():
    return [ln("M-200 0 Q0 -150 200 0 Q0 150 -200 0 Z", 9), ln(circle(0, 0, 66), 8), F(circle(0, 0, 30), K_),
            ln("M-150 -100 L-180 -150 M-60 -130 L-70 -190 M60 -130 L70 -190 M150 -100 L180 -150", 6)]

def cake(candles=12):
    e = [ln("M-200 -120 L200 -120 L200 0 L-200 0 Z", 8), ln("M-200 -120 C-150 -80 -100 -140 -50 -96 C0 -60 50 -140 100 -96 C150 -60 180 -120 200 -110", 6),
         ln("M-240 0 L240 0", 8)]
    for i in range(5):
        x = -140 + i * 70
        e += [ln(f"M{x} -120 L{x} -190", 7), F(P(f"M{x} -226 C{x+12} -210 {x+10} -196 {x} -194 C{x-10} -196 {x-12} -210 {x} -226 Z"), RED)]
    return e

def pin():
    p = P("M0 0 C-30 -60 -80 -100 -80 -160 C-80 -210 -44 -246 0 -246 C44 -246 80 -210 80 -160 C80 -100 30 -60 0 0 Z")
    return [ln(p, 8), F(p, RED), ln(circle(0, -160, 28), 7)]

def sun():
    e = [ln(circle(0, 0, 70), 8)]
    for k in range(10):
        a = k * math.pi / 5
        e.append(ln(f"M{math.cos(a)*100:.0f} {math.sin(a)*100:.0f} L{math.cos(a)*140:.0f} {math.sin(a)*140:.0f}", 7))
    return e

def clock(h="6h"):
    return [ln(circle(0, 0, 130), 9), ln("M0 0 L0 -90 M0 0 L60 30", 9), ln("M0 -130 L0 -110 M130 0 L110 0 M0 130 L0 110 M-130 0 L-110 0", 6),
            T(h, 0, 230, 90, "marker", RED)]

def globe():
    return [ln(circle(0, 0, 150), 8), ln(oval(0, 0, 70, 150), 6), ln("M-150 0 L150 0", 6), ln("M-128 -78 L128 -78 M-128 78 L128 78", 5)]

def laugh():
    return [ln(circle(0, 0, 120), 8), ln("M-70 20 Q0 110 70 20 Z", 7), ln("M-60 -40 Q-40 -60 -20 -40 M20 -40 Q40 -60 60 -40", 7),
            T("HA HA", 0, -170, 70, "marker")]

def stethoscope():
    return [ln("M-60 -120 C-80 0 80 0 60 -120", 8), ln("M0 -10 L0 80", 8), ln(circle(0, 104, 26), 7)]

def big_cross():
    p = P("M-25 -75 L25 -75 L25 -25 L75 -25 L75 25 L25 25 L25 75 L-25 75 L-25 25 L-75 25 L-75 -25 L-25 -25 Z")
    return [ln(p, 7), F(p, RED)]

def qmark(size=120, c=RED):
    return [T("?", 0, 0, size, "marker", c)]

def door_open():
    return [ln("M-120 0 L-120 -380 L120 -380 L120 0", 9), ln("M-120 -380 L-40 -350 L-40 30 L-120 0", 8), ln(circle(-56, -170, 8), 5),
            ln("M140 -200 L240 -200 M210 -230 L240 -200 L210 -170", 8)]

def road_sign(text="I-94"):
    p = P("M-120 -300 L120 -300 L120 -160 L-120 -160 Z")
    return [ln(p, 8), ln("M0 -160 L0 0", 9), T(text, 0, -200, 80, "marker")]

def mansion():
    """dark mansion hidden in the forest: two towers, pointed roofs, lit windows."""
    e = [ln("M-260 0 L-260 -300 L260 -300 L260 0 Z", 8), ln("M-300 -290 L0 -460 L300 -290", 8),
         ln("M-380 0 L-380 -420 L-260 -420 L-260 0", 8), ln("M-400 -410 L-320 -560 L-240 -410", 8),
         ln("M260 0 L260 -420 L380 -420 L380 0", 8), ln("M240 -410 L320 -560 L400 -410", 8),
         ln("M-50 0 L-50 -130 Q0 -170 50 -130 L50 0", 7)]
    for (x, y) in ((-200, -240), (-110, -240), (60, -240), (150, -240), (-350, -350), (290, -350)):
        w = P(f"M{x} {y} L{x+50} {y} L{x+50} {y+70} L{x} {y+70} Z"); e += [ln(w, 5), F(w, "#F2C230")]
    return e

def target_ring():
    return [ln(circle(0, 0, 120), 9, RED), ln(circle(0, 0, 70), 7, RED)]

def clipping(headline, sub="", w=620, seed=1):
    """Fictional newspaper clipping (own headline, fake body columns), torn edges + tape, rendered as an image."""
    import random as _r
    rnd = _r.Random(seed)
    H_ = int(w * 0.78); pad = 50
    surf = skia.Surface(w + pad * 2, H_ + pad * 2); c = surf.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    # torn paper outline
    p = skia.Path(); x0, y0, x1, y1 = pad, pad, pad + w, pad + H_
    pts = []
    for i in range(0, 41): pts.append((x0 + w * i / 40, y0 + rnd.uniform(-5, 5)))
    for i in range(1, 31): pts.append((x1 + rnd.uniform(-5, 5), y0 + H_ * i / 30))
    for i in range(1, 41): pts.append((x1 - w * i / 40, y1 + rnd.uniform(-5, 5)))
    for i in range(1, 30): pts.append((x0 + rnd.uniform(-5, 5), y1 - H_ * i / 30))
    p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close()
    c.drawPath(p, skia.Paint(Color=skia.Color(0, 0, 0, 70), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
    c.drawPath(p, skia.Paint(Color=skia.Color(242, 236, 222), AntiAlias=True))
    c.save(); c.clipPath(p)
    for _ in range(900):   # paper grain / age spots
        c.drawCircle(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0.5, 2.2),
                     skia.Paint(Color=skia.Color(150, 130, 90, rnd.randint(8, 30)), AntiAlias=True))
    ink = skia.Paint(Color=skia.Color(30, 28, 26), AntiAlias=True)
    mast = skia.Font(TF["serif"], 26)
    c.drawString("THE EVENING CHRONICLE", x0 + 24, y0 + 44, mast, ink)
    c.drawRect(skia.Rect.MakeLTRB(x0 + 24, y0 + 56, x1 - 24, y0 + 59), ink)
    # headline (wrapped)
    hf = skia.Font(TF["news"], 50); words = headline.upper().split(); lines, cur = [], ""
    for wd in words:
        tst = (cur + " " + wd).strip()
        if hf.measureText(tst) > w - 48 and cur: lines.append(cur); cur = wd
        else: cur = tst
    lines.append(cur); y = y0 + 112
    for ln_ in lines:
        c.drawString(ln_, x0 + 24, y, hf, ink); y += 54
    if sub:
        c.drawString(sub, x0 + 24, y + 2, skia.Font(TF["serif"], 22), skia.Paint(Color=skia.Color(70, 66, 60), AntiAlias=True)); y += 30
    # photo box + fake text columns
    ph = skia.Rect.MakeLTRB(x0 + 24, y + 6, x0 + w * 0.45, y1 - 24)
    c.save(); c.clipRect(ph)
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear([(0, ph.top()), (0, ph.bottom())],
                                                                 [skia.Color(170, 166, 158), skia.Color(95, 92, 86)])))
    dk = skia.Paint(Color=skia.Color(45, 43, 40), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeCap=skia.Paint.kRound_Cap)
    for k in range(4):   # bare trees, newspaper-photo style
        tx = ph.left() + ph.width() * (0.15 + 0.25 * k) + rnd.uniform(-10, 10); base = ph.bottom()
        dk.setStrokeWidth(7); c.drawLine(tx, base, tx + rnd.uniform(-6, 6), ph.top() + ph.height() * 0.15, dk)
        dk.setStrokeWidth(3)
        for j in range(4):
            yb_ = ph.top() + ph.height() * (0.25 + 0.15 * j); sgn = 1 if j % 2 else -1
            c.drawLine(tx, yb_, tx + sgn * rnd.uniform(18, 34), yb_ - rnd.uniform(14, 30), dk)
    for _ in range(400):
        c.drawCircle(rnd.uniform(ph.left(), ph.right()), rnd.uniform(ph.top(), ph.bottom()), 1.2,
                     skia.Paint(Color=skia.Color(30, 30, 30, rnd.randint(10, 50))))
    c.restore()
    col_x = x0 + w * 0.45 + 18; yy = y + 14
    gray = skia.Paint(Color=skia.Color(110, 104, 96), AntiAlias=True)
    while yy < y1 - 26:
        ln_w = (x1 - 24 - col_x) * rnd.uniform(0.75, 1.0)
        c.drawRect(skia.Rect.MakeXYWH(col_x, yy, ln_w, 5), gray); yy += 13
    c.restore()
    # tape
    for (tx, ty, ang) in ((x0 + 40, y0 - 4, -18), (x1 - 40, y0 - 4, 16)):
        c.save(); c.translate(tx, ty); c.rotate(ang)
        c.drawRect(skia.Rect.MakeXYWH(-55, -16, 110, 34), skia.Paint(Color=skia.Color(235, 230, 205, 170), AntiAlias=True))
        c.restore()
    return surf.makeImageSnapshot()

def news(headline, x, y, w=560, rot=-3, sub="", seed=1):
    from engine import IMG
    return [IMG(clipping(headline, sub, w, seed), x, y, 1.0, rot)]
