"""Sea / aviation props (Flight 19) + photo post-its that pop onto the board."""
import math, random, os
from lib import S, F, P, place, circle, oval, rect, col, skia
from engine import TW as T, flat, IMG, TF, ASSETS
from lib3 import ln, K_, RED, hatch_rect
from lib4 import fig, qmark, sun

YEL = "#F2C230"
BLUE = "#1F5FB0"

# ---------------- planes ----------------
def avenger(s=1.0):
    """TBM Avenger, side view facing right, centred at 0,0, ~620 long."""
    e = [ln("M-300 -10 C-200 -30 -60 -60 120 -62 C200 -62 250 -50 270 -30 L270 20 C220 34 120 40 0 34 C-150 26 -250 12 -300 -10 Z", 8),
         ln("M-40 -60 C-30 -110 60 -120 120 -100 L150 -62", 7),           # long canopy
         ln("M-20 -60 L-10 -100 M40 -62 L45 -112 M95 -62 L100 -108", 5),
         ln("M-300 -10 L-330 -120 L-260 -120 L-220 -30", 8),               # tail fin
         ln("M-290 -2 L-200 30 L-180 6", 6),                               # tailplane
         ln("M20 20 L-60 80 L120 80 L150 30", 8),                          # wing
         ln("M270 -60 L270 40", 6), ln("M278 -110 L278 90", 7),            # nose + prop
         ln(oval(278, -10, 12, 18), 6), ln(circle(-100, -10, 26), 6),
         F(circle(-100, -10, 10), K_)]
    return place(e, 0, 0, s)

def avenger_top(s=1.0):
    """small top view, facing up (for formations / maps)."""
    e = [ln("M0 -110 L14 -80 L14 60 L50 80 L-50 80 L-14 60 L-14 -80 Z", 6),
         ln("M-14 -40 L-150 -10 L-150 10 L-14 4 M14 -40 L150 -10 L150 10 L14 4", 6),
         ln("M-30 -116 L30 -116", 5)]
    return place(e, 0, 0, s)

def formation(n=5, s=0.6, gap=170):
    out = []
    pos = [(0, 0), (-1, 1), (1, 1), (-2, 2), (2, 2)][:n]
    for i, (a, b) in enumerate(pos):
        out += place(avenger_top(), a * gap, b * gap * 0.8, s)
    return out

def mariner(s=1.0):
    """PBM Mariner flying boat, side view facing right, centred."""
    e = [ln("M-380 -20 C-250 -40 -60 -70 160 -70 C250 -68 300 -40 320 0 C300 40 200 60 60 60 C-60 60 -200 30 -300 10 Z", 8),
         ln("M-100 50 L100 60", 5),                                         # hull step
         ln("M200 -66 C220 -90 260 -80 280 -50", 6),                        # cockpit
         ln("M-380 -20 L-420 -150 M-420 -150 L-460 -170 L-380 -170 L-420 -150 M-420 -150 L-340 -40", 7),  # gull tail
         ln("M-60 -70 L-120 -150 L160 -150 L120 -70", 7),                   # gull wing root
         ln("M-140 -150 L-420 -160 M180 -150 L460 -160", 8),
         ln(oval(30, -150, 50, 22), 6), ln("M80 -150 L80 -112 M80 -190 L80 -150", 5),
         ln("M-380 -158 L-380 -100 L-410 -90 M420 -158 L420 -100 L450 -90", 5)]   # floats
    return place(e, 0, 0, s)

# ---------------- sea / sky ----------------
def waves(w=1600, y=0, rows=2, amp=24, c=BLUE, lw=7, seed=1):
    out = []
    for r in range(rows):
        d = f"M{-w/2} {y + r*60}"
        x = -w / 2; k = 0
        while x < w / 2:
            x2 = x + 120
            d += f" Q{x+60} {y + r*60 - amp*(1 if k % 2 == 0 else -0.4)} {x2} {y + r*60}"
            x = x2; k += 1
        out.append(ln(d, lw, c))
    return out

def storm_cloud(s=1.0, bolt=True):
    e = [ln("M-220 0 C-300 0 -300 -110 -210 -110 C-210 -200 -80 -220 -40 -150 C0 -230 160 -220 160 -120 C260 -130 280 0 190 0 Z", 8)]
    if bolt:
        e += [ln("M-20 10 L-70 120 L0 120 L-50 240", 9, YEL), F(P("M-20 10 L-70 120 L0 120 L-50 240 L20 100 L-40 100 L10 10 Z"), YEL)]
    e += [ln("M-160 30 L-180 90 M120 30 L100 90 M180 40 L160 100", 5)]
    return place(e, 0, 0, s)

def island(w=260):
    return [ln(f"M{-w/2} 0 C{-w/3} -50 {w/3} -50 {w/2} 0", 7), ln("M-10 -36 C-14 -90 -6 -130 0 -150", 6),
            ln("M0 -150 C-40 -160 -70 -140 -90 -120 M0 -150 C40 -165 70 -150 90 -130 M0 -150 C-10 -190 -40 -200 -60 -200", 5)]

def sunset(w=500):
    return [ln(f"M{-w/2} 0 L{w/2} 0", 7)] + [ln("M-110 0 C-110 -150 110 -150 110 0", 8, RED)] + \
           [ln(f"M{-70 + 35*k} -10 L{-70+35*k} -10", 2) for k in range(0)] + \
           [ln("M-200 -40 L-140 -40 M140 -40 L200 -40 M-170 -90 L-130 -80 M130 -80 L170 -90", 5)]

def moon_c(r=70):
    return [ln(f"M0 {-r} A{r} {r} 0 1 0 0 {r}", 7)] if False else \
           [ln(f"M10 {-r} C{-r*1.6} {-r} {-r*1.6} {r} 10 {r} C{-r*0.7} {r*0.7} {-r*0.7} {-r*0.7} 10 {-r}", 7)]

def ship(s=1.0):
    e = [ln("M-300 0 L-260 70 L260 70 L320 0 Z", 8), ln("M-180 0 L-180 -90 L60 -90 L60 0", 7),
         ln("M-140 -90 L-140 -160 L-90 -160 L-90 -90", 7), ln("M-120 -160 C-110 -200 -140 -220 -120 -250", 5),
         ln("M120 0 L120 -200 M60 -150 L180 -150", 6), ln(circle(-120, -45, 14), 5), ln(circle(-50, -45, 14), 5)]
    return place(e, 0, 0, s)

def fireball(s=1.0):
    pts = []
    rnd = random.Random(4)
    for i in range(18):
        a = i / 18 * 2 * math.pi; r = 160 if i % 2 == 0 else 95 + rnd.uniform(-10, 10)
        pts.append(f"{r*math.cos(a):.0f} {r*math.sin(a):.0f}")
    d = "M" + " L".join(pts) + " Z"
    e = [F(P(d), "#F08A24"), ln(d, 8, RED), F(circle(0, 0, 60), YEL)]
    return place(e, 0, 0, s)

def seafloor(w=1500):
    out = [ln(f"M{-w/2} 0 C{-w/4} -40 {w/4} 30 {w/2} -10", 8, BLUE)]
    for x in range(int(-w/2) + 80, int(w/2), 140):
        out.append(ln(f"M{x} -4 C{x+10} -60 {x-10} -90 {x+6} -120", 5, BLUE))
    return out

def bubbles(n=7, seed=2):
    r = random.Random(seed)
    return [ln(circle(r.uniform(-60, 60), -i * 70, r.uniform(10, 22)), 5, BLUE) for i in range(n)]

# ---------------- instruments / radio ----------------
def compass(broken=False, ang=40):
    e = [ln(circle(0, 0, 150), 10), ln(circle(0, 0, 122), 5),
         T("N", 0, -84, 50, "marker", RED), T("S", 0, 116, 44, "marker", K_), T("E", 98, 16, 44, "marker", K_), T("W", -98, 16, 44, "marker", K_)]
    a = math.radians(ang)
    tip = (math.sin(a) * 90, -math.cos(a) * 90)
    e += [ln(f"M{-tip[0]:.0f} {-tip[1]:.0f} L{tip[0]:.0f} {tip[1]:.0f}", 9), F(P(f"M{tip[0]:.0f} {tip[1]:.0f} L{tip[0]*0.6+14:.0f} {tip[1]*0.6:.0f} L{tip[0]*0.6-14:.0f} {tip[1]*0.6:.0f} Z"), RED)]
    if broken:
        e += [ln("M-60 -140 L-20 -60 L-60 -10 L10 70", 5), ln("M90 -100 L50 -40 L80 20", 5)]
    return e

def fuel_gauge(level=0.1):
    e = [ln("M-150 0 A150 150 0 0 1 150 0", 9) if False else ln("M-150 0 C-150 -200 150 -200 150 0", 9),
         T("E", -120, -20, 48, "marker", RED), T("F", 120, -20, 48, "marker", K_), T("FUEL", 0, 50, 46, "marker", K_)]
    a = math.pi * (1 - level)
    e += [ln(f"M0 0 L{math.cos(a)*120:.0f} {-math.sin(a)*120:.0f}", 9, RED), F(circle(0, 0, 14), K_)]
    return e

def radio_set():
    e = [ln("M-200 -220 L200 -220 L200 0 L-200 0 Z", 8), ln("M-170 -190 L30 -190 L30 -110 L-170 -110 Z", 6),
         ln("M-150 -150 L10 -150", 4), ln(circle(110, -150, 40), 7), ln(circle(-120, -55, 26), 6), ln(circle(-40, -55, 26), 6),
         ln(circle(60, -55, 26), 6), ln("M140 -220 L190 -380", 6), F(circle(190, -380, 10), K_)]
    return e

def mic():
    return [ln("M-40 -220 C-40 -290 40 -290 40 -220 L40 -140 C40 -100 -40 -100 -40 -140 Z", 8),
            ln("M-70 -170 C-70 -60 70 -60 70 -170", 7), ln("M0 -90 L0 -10 M-50 -10 L50 -10", 7),
            ln("M-30 -240 L30 -240 M-30 -205 L30 -205 M-30 -170 L30 -170", 4)]

def radio_waves(n=3, r0=60, c=K_, left=False):
    out = []
    for k in range(n):
        r = r0 + k * 45; sg = -1 if left else 1
        out.append(ln(f"M{sg*r*0.5:.0f} {-r*0.85:.0f} C{sg*r*1.1:.0f} {-r*0.4:.0f} {sg*r*1.1:.0f} {r*0.4:.0f} {sg*r*0.5:.0f} {r*0.85:.0f}", 6, c))
    return out

def static_zz(w=300, c=K_):
    d = f"M{-w/2} 0"; r = random.Random(3)
    for i in range(1, 16): d += f" L{-w/2 + w*i/15:.0f} {r.uniform(-50, 50):.0f}"
    return [ln(d, 6, c)]

def cockpit():
    """instrument panel seen from the pilot seat."""
    e = [ln("M-520 -60 C-300 -160 300 -160 520 -60 L520 260 L-520 260 Z", 9)]
    for i, x in enumerate((-330, -110, 110, 330)):
        e += [ln(circle(x, 60, 80), 7), ln(f"M{x} 60 L{x+40} {20 if i % 2 else 100}", 6)]
    e += [ln("M-60 260 L-60 140 L60 140 L60 260", 7), ln("M-420 -150 L-520 -420 M420 -150 L520 -420", 8)]
    return e

def headset_fig(expr="scared", s=1.0):
    e = fig("short", expr) + [ln("M-96 -900 C-96 -1010 96 -1010 96 -900", 9), F(oval(-100, -880, 20, 34), K_), F(oval(100, -880, 20, 34), K_),
                               ln("M-100 -850 C-90 -800 -60 -790 -30 -800", 6)]
    return place(e, 0, 0, s)

def pilot(expr="blank", s=1.0):
    """figure with a flight cap + goggles."""
    e = fig("none", expr) + [ln("M-94 -900 C-94 -1010 94 -1010 94 -900", 9), ln("M-90 -930 L90 -930", 6),
                             ln(circle(-36, -945, 20), 5), ln(circle(36, -945, 20), 5)]
    return place(e, 0, 0, s)

# ---------------- maps / documents ----------------
def florida(s=1.0):
    """very simple Florida outline (panhandle top-left), keys trailing bottom-left; origin ~ Fort Lauderdale."""
    d = ("M-520 -560 L-120 -560 C-90 -520 -60 -440 -40 -380 C-10 -280 20 -170 30 -60 C40 20 20 60 0 80 "
         "C-20 120 -60 140 -90 130 C-140 70 -180 -20 -200 -120 C-230 -260 -260 -380 -320 -440 C-380 -480 -460 -500 -520 -500 Z")
    e = [ln(d, 8)]
    for k in range(5):
        e.append(ln(oval(-120 - k * 45, 160 + k * 18, 18 - k * 2, 7), 5))
    return place(e, 0, 0, s)

def bahamas():
    return [ln(oval(0, 0, 70, 22), 6), ln(oval(120, 80, 40, 60), 6), ln(oval(-60, 140, 30, 18), 5), ln(oval(60, 220, 55, 20), 5)]

def triangle_map():
    e = [ln("M-300 220 L260 -40 L60 330 Z", 9, RED)]
    e += [T("MIAMI", -330, 280, 46, "marker", K_), T("BERMUDA", 300, -80, 46, "marker", K_), T("PUERTO RICO", 90, 400, 46, "marker", K_)]
    e += [F(circle(-300, 220, 12), K_), F(circle(260, -40, 12), K_), F(circle(60, 330, 12), K_)]
    return e

def report(title="NAVY REPORT", lines=7, stamp=None):
    e = [ln("M-200 -520 L200 -520 L200 0 L-200 0 Z", 8), T(title, 0, -450, 44, "marker", K_)]
    for k in range(lines):
        e.append(ln(f"M-150 {-380 + k*45} L{150 - (k % 3)*40} {-380 + k*45}", 4))
    if stamp:
        e += [ln("M-170 -170 L170 -170 L170 -70 L-170 -70 Z", 7, RED), T(stamp, 0, -100, 48, "marker", RED)]
    return e

def life_jacket():
    return [ln("M-90 -260 L-30 -260 L0 -200 L30 -260 L90 -260 L110 0 L-110 0 Z", 8), F(P("M-90 -260 L-30 -260 L-20 -230 L-60 -120 L-100 -100 Z"), "#E9852B"),
            ln("M-100 -100 L100 -100 M-104 -50 L104 -50", 6)]

def numbers_tag(text="#???"):
    return [ln("M-130 -60 L130 -60 L130 60 L-130 60 Z", 7), T(text, 0, 20, 56, "marker", RED)]

# ---------------- post-it photo ----------------
_PH = os.path.join(ASSETS, "photos")

def _bw(img_path, w, h, seed):
    from PIL import Image, ImageOps, ImageFilter, ImageEnhance
    import numpy as np
    im = Image.open(img_path).convert("L")
    im = ImageOps.fit(im, (w, h), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.25)
    a = np.asarray(im).astype(np.float32)
    rnd = np.random.default_rng(seed)
    a = a + rnd.normal(0, 9, a.shape)                                     # film grain
    yy, xx = np.mgrid[0:h, 0:w]; v = 1 - 0.35 * (((xx - w/2) / (w/2)) ** 2 + ((yy - h/2) / (h/2)) ** 2)
    a = np.clip(a * np.clip(v, 0.55, 1), 0, 255)
    rgb = np.stack([a * 0.98, a * 0.96, a * 0.92, np.full_like(a, 255)], -1).astype(np.uint8)   # slight warm tint
    return skia.Image.fromarray(rgb[:, :, [2, 1, 0, 3]].copy(), colorType=skia.kBGRA_8888_ColorType)

def postit_img(photo, caption="", w=430, seed=1):
    rnd = random.Random(seed)
    pad = 60; H_ = int(w * 1.08)
    surf = skia.Surface(w + pad * 2, H_ + pad * 2); c = surf.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    x0, y0 = pad, pad
    note = skia.Path(); note.moveTo(x0, y0); note.lineTo(x0 + w, y0); note.lineTo(x0 + w, y0 + H_ - 24)
    note.quadTo(x0 + w - 6, y0 + H_ - 4, x0 + w - 40, y0 + H_ + 2); note.lineTo(x0, y0 + H_); note.close()  # lifted corner
    c.save(); c.translate(6, 14)
    c.drawPath(note, skia.Paint(Color=skia.Color(0, 0, 0, 90), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12)))
    c.restore()
    c.drawPath(note, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, y0), (0, y0 + H_)], [skia.Color(252, 232, 120), skia.Color(240, 212, 84)])))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, 26), skia.Paint(Color=skia.Color(0, 0, 0, 14)))     # adhesive strip
    m = 26; pw = w - 2 * m; ph = int(pw * 0.78)
    img = _bw(os.path.join(_PH, photo), pw, ph, seed)
    c.drawRect(skia.Rect.MakeXYWH(x0 + m - 3, y0 + m + 10 - 3, pw + 6, ph + 6), skia.Paint(Color=skia.Color(30, 28, 26)))
    c.drawImage(img, x0 + m, y0 + m + 10)
    if caption:
        f = skia.Font(TF["marker"], 40); tw = f.measureText(caption)
        if tw > w - 30: f = skia.Font(TF["marker"], 40 * (w - 30) / tw); tw = f.measureText(caption)
        c.drawString(caption, x0 + (w - tw) / 2, y0 + m + 10 + ph + (H_ - ph - m - 10) / 2 + 16, f,
                     skia.Paint(Color=skia.Color(25, 25, 25), AntiAlias=True))
    # tape
    c.save(); c.translate(x0 + w / 2 + rnd.uniform(-30, 30), y0 + 2); c.rotate(rnd.uniform(-8, 8))
    c.drawRect(skia.Rect.MakeXYWH(-70, -18, 140, 38), skia.Paint(Color=skia.Color(236, 232, 215, 175), AntiAlias=True))
    c.restore()
    return surf.makeImageSnapshot()

def postit(photo, caption, x, y, w=430, rot=-4, seed=1):
    e = IMG(postit_img(photo, caption, w, seed), x, y, 1.0, rot)
    e.pop = True
    return [e]
