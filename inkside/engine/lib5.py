"""Horror props (Bloody Mary and later stories): mirrors, candles, skulls, queens, witches..."""
import math, random
from lib import S, F, P, place, circle, oval, rect, col
from engine import TW as T, flat
from lib3 import ln, K_, RED, hatch_rect, motion_lines
from lib4 import fig, eye, qmark

GRAY = "#8C8C8C"

def mirror(w=360, h=500, frame=True):
    """oval mirror, bottom at y=0, centre at (0,-h/2)."""
    cy = -h / 2
    e = [ln(oval(0, cy, w / 2, h / 2), 9)]
    if frame:
        e += [ln(oval(0, cy, w / 2 + 26, h / 2 + 26), 7)]
        for a in range(0, 360, 45):
            x, y = (w / 2 + 13) * math.cos(math.radians(a)), cy + (h / 2 + 13) * math.sin(math.radians(a))
            e += [ln(circle(x, y, 9), 5)]
    e += [ln(f"M{-w*.28} {cy-h*.22} L{-w*.12} {cy-h*.34}", 5), ln(f"M{-w*.3} {cy-h*.1} L{-w*.06} {cy-h*.28}", 5)]
    return e

def mary_face(s=1.0, drips=True):
    """the woman in the mirror: long hair, hollow eyes, red tears. centre at 0,0 (face ~ 260 tall)."""
    e = [ln("M0 -150 C70 -150 92 -80 88 -10 C84 70 50 128 0 138 C-50 128 -84 70 -88 -10 C-92 -80 -70 -150 0 -150 Z", 7)]
    hair = ("M-10 -168 C-120 -170 -150 -60 -140 60 C-134 160 -150 230 -170 300 M10 -168 C120 -170 150 -60 140 60 "
            "C134 160 150 230 170 300 M-60 -150 C-90 -60 -96 60 -110 250 M60 -150 C90 -60 96 60 110 250 "
            "M-20 -160 C-40 -100 -46 -40 -40 30 M30 -158 C50 -90 52 -30 46 40")
    e += [ln(hair, 6)]
    for sx in (-1, 1):
        x = sx * 34
        d = f"M{x-24} -30 C{x-10} -46 {x+14} -44 {x+24} -28 C{x+12} -14 {x-12} -12 {x-24} -30 Z"
        e += [ln(d, 5), F(d, K_)]
        if drips:
            e += [ln(f"M{x-4} -14 L{x-6} 70", 7, RED), ln(f"M{x+8} -16 L{x+10} 40", 6, RED)]
    e += [ln("M-14 60 C-4 50 6 50 14 60 C10 84 -10 84 -14 60 Z", 5), F("M-14 60 C-4 50 6 50 14 60 C10 84 -10 84 -14 60 Z", K_)]
    return place(e, 0, 0, s) if s != 1 else e

def mirror_mary(w=360, h=500):
    return mirror(w, h) + place(mary_face(), 0, -h / 2 + 10, h / 560)

def candle(flame=True):
    e = [ln("M-34 0 L-34 -170 C-20 -182 20 -182 34 -170 L34 0 Z", 8), ln("M-34 -170 C-20 -158 20 -158 34 -170", 5),
         ln("M0 -176 L0 -196", 5), ln("M-34 -120 C-26 -110 -26 -96 -34 -88", 4)]
    if flame:
        f = "M0 -196 C30 -230 16 -270 0 -300 C-16 -270 -30 -230 0 -196 Z"
        e += [ln(f, 6), F(f, RED)]
    return e

def bulb(off=True):
    e = [ln("M-60 -40 C-110 -120 -70 -230 0 -230 C70 -230 110 -120 60 -40 L50 0 L-50 0 Z", 8),
         ln("M-44 20 L44 20 M-38 40 L38 40", 7)]
    if off: e += [ln("M-150 -250 L150 50", 12, RED)]
    else: e += [ln("M-120 -200 L-160 -230 M0 -270 L0 -320 M120 -200 L160 -230", 6)]
    return e

def sink():
    return [ln("M-200 0 L200 0 C190 90 -190 90 -200 0 Z", 8), ln("M-120 70 L-90 320 M120 70 L90 320", 8),
            ln("M-30 0 L-30 -60 C-30 -90 40 -90 40 -60", 7), ln("M-60 -20 L0 -20", 6)]

def crown(c=K_):
    d = "M-120 0 L-140 -150 L-70 -70 L0 -170 L70 -70 L140 -150 L120 0 Z"
    return [ln(d, 8, c), ln("M-120 -30 L120 -30", 5, c), F(circle(0, -170, 12), RED), F(circle(-140, -150, 10), RED), F(circle(140, -150, 10), RED)]

def queen(expr="blank"):
    return fig("long", expr) + place(crown(), 0, -985, .55)

def cradle():
    """empty bassinet with a hood, on rockers."""
    return [ln("M-220 -40 C-220 70 220 70 220 -40 Z", 8), ln("M-220 -40 C-230 -210 -40 -230 10 -40", 8),
            ln("M-170 -40 C-160 -150 -60 -170 -30 -40", 5), ln("M-120 10 C-40 30 60 30 160 0", 5),
            ln("M-240 110 C-100 160 100 160 240 110", 8), ln("M-120 50 L-130 130 M120 50 L130 130", 7)]

def flames(w=420, n=6, seed=1):
    r = random.Random(seed); e = []
    for i in range(n):
        x = -w / 2 + w * (i + .5) / n; hgt = r.uniform(130, 230); ww = w / n * 1.25
        d = f"M{x-ww/2} 0 C{x-ww/2} {-hgt*.5} {x-ww*.1} {-hgt*.6} {x} {-hgt} C{x+ww*.2} {-hgt*.6} {x+ww/2} {-hgt*.5} {x+ww/2} 0 Z"
        e += [ln(d, 6, RED)]
    e += [ln(f"M{-w/2-20} 0 L{w/2+20} 0", 8)]
    return e

def witch_hat():
    d = "M-150 0 C-60 -20 60 -20 150 0 C80 10 -80 10 -150 0 Z M-70 -4 C-40 -120 -10 -230 40 -300 C30 -200 50 -100 70 -4"
    return [ln(d, 8), ln("M-66 -40 C-20 -50 30 -50 66 -40", 12, RED)]

def witch(expr="sinister"):
    return fig("long", expr) + place(witch_hat(), 0, -955, .8)

def stake():
    return [ln("M-14 0 L-14 -700 L14 -700 L14 0", 8), ln("M-120 -560 L120 -560", 8)]

def spellbook():
    return [ln("M-180 0 L-180 -240 C-100 -260 -20 -250 0 -230 C20 -250 100 -260 180 -240 L180 0 C100 -20 20 -14 0 10 C-20 -14 -100 -20 -180 0 Z", 8),
            ln("M0 -230 L0 10", 6), ln(circle(-90, -130, 40), 5), ln("M-90 -170 L-90 -90 M-130 -130 L-50 -130", 4),
            ln("M40 -190 L140 -190 M40 -150 L140 -150 M40 -110 L120 -110", 4)]

def grave(text="?"):
    return [ln("M-130 0 L-130 -260 C-130 -400 130 -400 130 -260 L130 0", 9), ln("M-200 0 L200 0", 8),
            T(text, 0, -220, 90, "marker", K_)]

def car():
    return [ln("M-300 -60 L-300 -130 C-280 -150 -220 -160 -170 -160 L-110 -250 L120 -250 L200 -160 C260 -158 300 -140 300 -100 L300 -60 Z", 8),
            ln("M-90 -235 L-30 -235 L-30 -165 L-145 -165 Z M0 -235 L100 -235 L160 -165 L0 -165 Z", 6),
            ln(circle(-180, -50, 54), 8), ln(circle(180, -50, 54), 8), F(circle(-180, -50, 18), K_), F(circle(180, -50, 18), K_)]

def crash(w=240):
    pts = []
    for i in range(16):
        a = i / 16 * 2 * math.pi; r = w if i % 2 == 0 else w * .5
        pts.append(f"{r*math.cos(a):.0f} {r*math.sin(a):.0f}")
    d = "M" + " L".join(pts) + " Z"
    return [ln(d, 8, RED), T("CRASH!", 0, 20, 70, "marker", K_)]

def stairs(n=6, step=70):
    d = "M-260 0"
    x, y = -260, 0
    for i in range(n):
        y -= step; d += f" L{x} {y}"; x += 90; d += f" L{x} {y}"
    return [ln(d, 8), ln(f"M-260 0 L{x} 0 L{x} {y}", 6)]

def arrow(x0, y0, x1, y1, c=RED, w=9):
    a = math.atan2(y1 - y0, x1 - x0); h = 34
    return [ln(f"M{x0} {y0} L{x1} {y1}", w, c),
            ln(f"M{x1-h*math.cos(a-.5):.0f} {y1-h*math.sin(a-.5):.0f} L{x1} {y1} L{x1-h*math.cos(a+.5):.0f} {y1-h*math.sin(a+.5):.0f}", w, c)]

def skull():
    d = "M0 -260 C-130 -260 -170 -150 -150 -70 C-140 -30 -110 -20 -100 10 L-80 70 L80 70 L100 10 C110 -20 140 -30 150 -70 C170 -150 130 -260 0 -260 Z"
    e = [ln(d, 8)]
    for sx in (-1, 1):
        dd = f"M{sx*25} -120 C{sx*30} -170 {sx*110} -170 {sx*100} -110 C{sx*95} -70 {sx*30} -70 {sx*25} -120 Z"
        e += [ln(dd, 6), F(dd, K_)]
    e += [ln("M0 -60 L-18 -20 L18 -20 Z", 5), ln("M-60 40 L-60 70 M-20 40 L-20 70 M20 40 L20 70 M60 40 L60 70", 5)]
    return e

def heart_ring():
    gem = "M-34 -76 L0 -120 L34 -76 L0 -54 Z"
    return [ln(circle(0, 0, 70), 9), ln(gem, 6), F(gem, RED)]

def man_face():
    return [ln(circle(0, 0, 120), 8), ln("M-110 -40 C-90 -150 90 -150 110 -40 C60 -90 -60 -90 -110 -40 Z", 6),
            F(oval(-40, 0, 9, 13), K_), F(oval(40, 0, 9, 13), K_), ln("M-40 55 Q0 80 40 55", 6), ln("M0 0 L-8 35 L6 35", 5)]

def card(w=520, h=360):
    return [ln(f"M{-w/2} {-h} L{w/2} {-h} L{w/2} 0 L{-w/2} 0 Z", 8), ln(f"M{-w/2+18} {-h+18} L{w/2-18} {-h+18} L{w/2-18} -18 L{-w/2+18} -18 Z", 4)]

def witch_shadow():
    d = ("M0 0 L-60 -300 C-70 -360 -30 -400 -10 -420 L-90 -430 C-40 -450 0 -470 10 -560 C30 -470 70 -450 120 -430 L40 -420 "
         "C60 -380 80 -330 60 -300 L120 0 Z")
    return [ln(d, 6), F(d, K_)]

def glasses():
    return [ln(circle(-40, 0, 32), 6), ln(circle(40, 0, 32), 6), ln("M-8 0 L8 0", 5)]

def scientist():
    return fig("short", "blank") + place(glasses(), 0, -890, 1.0) + [ln("M120 -560 L260 -560 L260 -340 L120 -340 Z", 7),
                                                                   ln("M150 -500 L230 -500 M150 -450 L230 -450 M150 -400 L210 -400", 4)]

def people_grid(cols=10, rows=5, gap=60):
    e = []
    for r in range(rows):
        for c in range(cols):
            x, y = (c - (cols - 1) / 2) * gap, r * gap * 1.3
            e += [ln(circle(x, y - 22, 12), 4), ln(f"M{x-16} {y+14} C{x-16} {y-6} {x+16} {y-6} {x+16} {y+14}", 4)]
    return e

def timer(text="10:00"):
    return [ln(circle(0, -150, 150), 9), ln("M-30 -320 L30 -320 M0 -320 L0 -300", 8), ln("M0 -150 L0 -240 M0 -150 L70 -110", 8),
            T(text, 0, 80, 90, "marker", K_)]

def melt_face():
    return [ln("M0 -150 C80 -150 100 -60 96 0 C100 60 120 120 80 150 C60 120 40 170 0 140 C-30 180 -60 120 -80 160 C-110 110 -100 40 -96 0 C-100 -80 -80 -150 0 -150 Z", 7),
            ln("M-50 -40 C-40 -20 -20 -10 -20 10", 6), ln("M50 -50 C40 -20 30 0 34 20", 6), ln("M-30 70 C-10 100 20 80 30 110", 6)]

def old_woman():
    return [ln(circle(0, 0, 110), 7), ln("M-90 -60 C-60 -150 60 -150 90 -60 M-60 -120 C-40 -170 40 -170 60 -120", 6), ln(circle(0, -150, 34), 6),
            F(oval(-35, -10, 7, 9), K_), F(oval(35, -10, 7, 9), K_), ln("M-55 -30 L-20 -28 M20 -28 L55 -30 M-30 50 Q0 40 30 50 M-70 20 L-50 30 M70 20 L50 30", 5)]

def cat():
    return [ln("M-90 40 C-110 -40 -90 -90 -70 -100 L-80 -170 L-20 -110 L20 -110 L80 -170 L70 -100 C90 -90 110 -40 90 40 C40 80 -40 80 -90 40 Z", 7),
            F(oval(-35, -30, 8, 14), K_), F(oval(35, -30, 8, 14), K_), ln("M-10 10 L10 10 L0 22 Z M-110 0 L-40 10 M-110 30 L-40 20 M110 0 L40 10 M110 30 L40 20", 4)]

def pig():
    return [ln(oval(0, 0, 110, 95), 7), ln(oval(0, 20, 44, 30), 6), F(oval(-14, 20, 6, 10), K_), F(oval(14, 20, 6, 10), K_),
            F(oval(-40, -30, 7, 10), K_), F(oval(40, -30, 7, 10), K_), ln("M-80 -70 L-100 -130 L-40 -90 M80 -70 L100 -130 L40 -90", 6)]

def monster():
    e = [ln("M0 -170 C120 -170 150 -50 130 40 C110 130 60 170 0 170 C-60 170 -110 130 -130 40 C-150 -50 -120 -170 0 -170 Z", 8),
         ln("M-100 -150 L-150 -240 L-60 -170 M100 -150 L150 -240 L60 -170", 7)]
    for sx in (-1, 1):
        d = f"M{sx*20} -40 L{sx*80} -60 L{sx*70} -10 Z"
        e += [ln(d, 5), F(d, RED)]
    e += [ln("M-70 60 L-50 90 L-30 60 L-10 90 L10 60 L30 90 L50 60 L70 90", 6), ln("M-80 50 C-30 120 30 120 80 50", 6)]
    return e

def brain():
    d = ("M-170 40 C-220 0 -210 -90 -150 -110 C-150 -170 -80 -200 -30 -170 C10 -210 90 -200 110 -150 C170 -150 210 -80 180 -30 "
         "C220 20 190 90 130 90 C110 130 40 140 0 110 C-40 140 -120 130 -130 90 C-160 90 -180 70 -170 40 Z")
    return [ln(d, 8), ln("M0 -170 C-20 -100 20 -40 0 110", 6), ln("M-120 -80 C-80 -60 -90 0 -50 10 M70 -100 C110 -80 90 -20 130 0 M-110 40 C-70 30 -40 60 -30 90 M60 30 C90 60 70 80 100 90", 5)]

def pair_facing():
    a = fig("short", "blank"); b = fig("long", "blank")
    return place(a, -200, 0, .5) + place(b, 200, 0, .5) + [ln("M-120 -450 L-10 -450", 5, RED), ln("M120 -440 L10 -440", 5, RED)]

def bone(broken=True):
    e = [ln("M-200 -20 L-20 -20 M-200 20 L-30 20 M30 -20 L200 -20 M20 20 L200 20", 8),
         ln("M-200 -20 C-250 -70 -280 0 -240 0 C-280 0 -250 70 -200 20", 8), ln("M200 -20 C250 -70 280 0 240 0 C280 0 250 70 200 20", 8)]
    if broken: e += [ln("M-20 -20 L0 0 L-30 20 M30 -20 L10 0 L20 20", 6, RED), ln("M-40 -70 L-10 -40 M40 -70 L10 -40 M0 -90 L0 -50", 5)]
    return e

def stall(num="3"):
    return [ln("M-180 0 L-180 -520 L180 -520 L180 0", 9), ln("M-150 -490 L150 -490 L150 -30 L-150 -30 Z", 6),
            ln(circle(110, -260, 14), 6), T(num, 0, -360, 140, "marker", RED)]

def knock():
    return [T("KNOCK", 0, 0, 70, "marker", K_), T("KNOCK", 40, 90, 70, "marker", K_), T("KNOCK", 80, 180, 70, "marker", K_)]

def dots(n=3):
    return [ln(circle(i * 60 - (n - 1) * 30, 0, 10), 9) for i in range(n)]


# ---------------- Annabelle props ----------------
def rag_doll(expr="smile", s=1.0):
    """generic rag doll (button eyes, yarn hair, stitched smile, dress). feet at 0, ~620 tall."""
    e = [ln(circle(0, -500, 95), 8)]
    for k in range(9):                                   # yarn hair loops
        a = math.radians(200 + k * 17.5); x, y = 100 * math.cos(a), -500 + 100 * math.sin(a)
        e += [ln(circle(x, y, 26), 6, RED)]
    for sx in (-1, 1):
        e += [ln(circle(sx * 34, -510, 18), 6), ln(f"M{sx*34-8} -518 L{sx*34+8} -502 M{sx*34+8} -518 L{sx*34-8} -502", 4)]
    if expr == "smile":
        e += [ln("M-40 -465 Q0 -430 40 -465", 6)] + [ln(f"M{x} -462 L{x} -444", 3) for x in (-28, -12, 4, 20)]
    else:                                                # evil
        e += [ln("M-50 -470 Q0 -415 50 -470", 7)] + [ln(f"M{x} -464 L{x} -436", 3) for x in (-36, -18, 0, 18, 36)]
        e += [ln("M-60 -545 L-14 -528 M14 -528 L60 -545", 6)]
    e += [ln("M-40 -405 L-120 -100 L120 -100 L40 -405 Z", 8), ln("M-120 -100 C-60 -80 60 -80 120 -100", 5),
          ln("M-50 -380 C-110 -350 -150 -300 -160 -240 M50 -380 C110 -350 150 -300 160 -240", 8),
          ln(circle(-165, -225, 20), 6), ln(circle(165, -225, 20), 6)]
    for sx in (-1, 1):
        e += [ln(f"M{sx*40} -100 L{sx*44} -20 L{sx*80} -10 L{sx*86} 0 L{sx*20} 0 L{sx*16} -100", 7)]
        e += [ln(f"M{sx*18} {-80+k*20} L{sx*42} {-80+k*20}", 4, RED) for k in range(3)]
    return place(e, 0, 0, s) if s != 1 else e

def glass_box(w=420, h=560, sign=True):
    e = [ln(f"M{-w/2} 0 L{-w/2} {-h} L{w/2} {-h} L{w/2} 0 Z", 9), ln(f"M{-w/2-30} 0 L{w/2+30} 0 L{w/2+30} 50 L{-w/2-30} 50 Z", 8),
         ln(f"M{-w/2+40} {-h+60} L{-w/2+100} {-h+150} M{-w/2+40} {-h+130} L{-w/2+80} {-h+180}", 5)]
    if sign:
        e += [ln(f"M-170 {-h-150} L170 {-h-150} L170 {-h-30} L-170 {-h-30} Z", 7),
              T("DO NOT OPEN", 0, -h - 70, 54, "marker", RED)]
    return e

def note(text="HELP US", w=300, h=190, rot=0):
    e = [ln(f"M{-w/2} {-h} L{w/2} {-h+10} L{w/2-10} 0 L{-w/2+6} -6 Z", 7), T(text, 0, -h / 2 + 18, 52, "marker", RED)]
    return e

def crystal_ball():
    return [ln(circle(0, -130, 110), 8), ln("M-90 -40 L-120 0 L120 0 L90 -40", 8), ln("M-50 -190 C-30 -210 0 -215 20 -210", 5)]

def priest(expr="blank"):
    return fig("short", expr) + [ln("M-26 -790 L26 -790", 10, K_), ln("M0 -660 L0 -540 M-40 -620 L40 -620", 8)]

def bed2():
    return [ln("M-420 -120 L420 -120 L420 -40 L-420 -40 Z", 8), ln("M-420 -40 L-420 40 M420 -40 L420 40", 8),
            ln("M-420 -120 L-420 -300 M420 -120 L420 -220", 8), ln("M-380 -190 C-380 -230 -260 -230 -260 -190 C-260 -150 -380 -150 -380 -190", 6)]

def claws(n=7, w=240, h=260, c=RED):
    return [ln(f"M{-w/2 + k*w/(n-1):.0f} {-h/2} L{-w/2 + k*w/(n-1) + 30:.0f} {h/2}", 8, c) for k in range(n)]

def small_hands():
    return [ln("M-60 0 C-60 -40 -20 -50 -10 -20 M-50 -30 L-70 -60 M-35 -38 L-45 -70 M-20 -40 L-22 -72", 6),
            ln("M60 0 C60 -40 20 -50 10 -20 M50 -30 L70 -60 M35 -38 L45 -70 M20 -40 L22 -72", 6)]

def shelves():
    e = [ln("M-400 0 L-400 -560 L400 -560 L400 0 Z", 8)] + [ln(f"M-400 {-y} L400 {-y}", 6) for y in (190, 380)]
    e += [ln(circle(-280, -260, 40), 5), ln("M-120 -190 L-120 -300 L-60 -300 L-60 -190", 5), ln("M120 -380 L150 -470 L180 -380 Z", 5),
          ln(circle(280, -440, 50), 5), ln("M-300 0 L-300 -90 L-200 -90 L-200 0", 5), ln("M200 -190 C200 -260 300 -260 300 -190", 5)]
    return e

def motorcycle():
    return [ln(circle(-170, -70, 70), 8), ln(circle(170, -70, 70), 8), ln("M-170 -70 L-60 -170 L80 -170 L170 -70 M-60 -170 L0 -70 L80 -170", 7),
            ln("M80 -170 L120 -240 L170 -240", 7), ln("M-90 -190 L10 -190", 9)]

def clapper():
    return [ln("M-200 -220 L200 -220 L200 0 L-200 0 Z", 8), ln("M-200 -220 L180 -320 L200 -280 L-180 -180", 8),
            ln("M-120 -258 L-80 -200 M-40 -280 L0 -220 M40 -298 L80 -238 M120 -308 L150 -262", 6)]

def porcelain_doll():
    e = [ln(circle(0, -500, 95), 8), ln("M-95 -520 C-90 -630 90 -630 95 -520 C110 -460 120 -400 110 -340 M-95 -520 C-110 -460 -120 -400 -110 -340", 7),
         F(oval(-34, -505, 14, 18), K_), F(oval(34, -505, 14, 18), K_), ln("M-30 -455 Q0 -440 30 -455", 6),
         ln("M20 -590 L0 -540 L22 -520 L4 -480", 5), ln("M-40 -405 L-130 -60 L130 -60 L40 -405 Z", 8),
         ln("M-130 -60 C-80 -30 -30 -80 0 -50 C30 -80 80 -30 130 -60", 6)]
    return e

def phone(text="MISSING"):
    return [ln("M-130 -420 L130 -420 L130 0 L-130 0 Z", 8), ln("M-110 -390 L110 -390 L110 -60 L-110 -60 Z", 5),
            ln(circle(0, -30, 14), 5), T(text, 0, -240, 52, "marker", RED)]

def tv(): 
    return [ln("M-220 -320 L220 -320 L220 0 L-220 0 Z", 8), ln("M-190 -290 L130 -290 L130 -30 L-190 -30 Z", 6),
            ln(circle(175, -230, 16), 5), ln(circle(175, -150, 16), 5), ln("M-80 -320 L-140 -420 M80 -320 L140 -420", 6),
            ln("M-120 0 L-140 50 M120 0 L140 50", 7)]

def ticket(text="TICKET"):
    return [ln("M-160 -100 L160 -100 L160 -60 C130 -60 130 -20 160 -20 L160 20 L-160 20 L-160 -20 C-130 -20 -130 -60 -160 -60 Z", 7),
            T(text, 0, -26, 48, "marker", K_)]

def book(title=""):
    return [ln("M-140 0 L-140 -300 L140 -300 L140 0 Z", 8), ln("M-110 0 L-110 -300", 6), T(title, 15, -160, 44, "marker", K_)]

def holy_water():
    return [ln("M-50 0 L-50 -180 C-50 -220 -20 -230 -20 -260 L20 -260 C20 -230 50 -220 50 -180 L50 0 Z", 8),
            ln("M-20 -260 L-20 -290 L20 -290 L20 -260", 6), ln("M0 -150 L0 -60 M-30 -120 L30 -120", 6),
            ln("M80 -200 L110 -230 M90 -150 L130 -160 M70 -250 L90 -290", 5)]

def puppet_bar():
    return [ln("M-200 0 L200 0 M0 -60 L0 60", 9)] + [ln(f"M{x} 0 L{x} 330", 3) for x in (-180, -60, 60, 180)]

def key():
    return [ln(circle(-120, 0, 50), 8), ln("M-70 0 L150 0 M100 0 L100 40 M140 0 L140 50", 8)]

def couch():
    return [ln("M-260 0 L-260 -160 L260 -160 L260 0 Z", 8), ln("M-300 -40 L-300 -200 L-260 -200 M300 -40 L300 -200 L260 -200", 8),
            ln("M-220 -160 L-220 -280 L220 -280 L220 -160", 7), ln("M-240 0 L-240 30 M240 0 L240 30", 7)]
