"""Real-whiteboard 'Draw My Life' style: black marker line art, almost no colour, big simple people."""
import math, random
from lib import S, F, P, place, circle, oval, rect, skia, col, El
from engine import TW as T, flat

K_ = "#161616"
RED = "#E0393E"
LW = 8          # main marker width

def ln(d, w=LW, c=K_):
    return S(d, w, c)

def blob_fill(d, c):
    """small accent colour (marker coloured)."""
    return F(d, c)

def hatch_rect(x, y, w, h, gap=34, ang=1.0, lw=5):
    """diagonal hatching inside an axis-aligned rect (/// lines)."""
    out = []
    k = ang
    for s in range(int(-h * k), int(w) + 1, gap):
        # line x = s + t, y = y+h - t/k  for t in ...
        x0, y0 = x + s, y + h
        x1, y1 = x + s + h * k, y
        # clip to rect
        if x0 < x: y0 -= (x - x0) / k; x0 = x
        if x1 > x + w: y1 += (x1 - (x + w)) / k; x1 = x + w
        if x1 - x0 < 6: continue
        out.append(ln(f"M{x0:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}", lw))
    return out

# ---------------- people ----------------
# Figure is ~5 heads tall, feet at y=0, head top at y=-1000 (reference: classic whiteboard 'Draw My Life' girl).
def face(expr):
    e = []
    def eye(cx, look=0, narrow=False, big=False):
        if narrow:
            return [ln(f"M{cx-17} -888 Q{cx} -898 {cx+17} -888", 6), F(oval(cx + look, -887, 6, 4), K_)]
        ry = 13 if big else 10
        return [ln(f"M{cx-17} -890 Q{cx} -{906 if big else 902} {cx+17} -890", 5), F(oval(cx + look, -889, 7, ry), K_),
                ln(f"M{cx+15*(1 if cx>0 else -1)} -893 L{cx+23*(1 if cx>0 else -1)} -901", 4)]
    if expr == "sinister":
        e += eye(-31, 3, True) + eye(31, 3, True)
        e += [ln("M-52 -918 L-14 -904", 6), ln("M14 -904 L52 -918", 6), ln("M-26 -840 Q4 -824 30 -846", 6)]
    elif expr == "scared":
        e += eye(-31, 0, big=True) + eye(31, 0, big=True)
        e += [ln("M-50 -922 Q-32 -932 -14 -920", 5), ln("M14 -920 Q32 -932 50 -922", 5), ln(oval(0, -838, 12, 16), 6)]
    elif expr == "sad":
        e += eye(-31) + eye(31)
        e += [ln("M-50 -912 Q-32 -918 -14 -926", 5), ln("M14 -926 Q32 -918 50 -912", 5), ln("M-18 -834 Q0 -846 20 -834", 6)]
    elif expr == "blank":
        e += eye(-31) + eye(31)
        e += [ln("M-48 -918 Q-32 -922 -14 -918", 5), ln("M14 -918 Q32 -922 48 -918", 5), ln("M-12 -838 L14 -838", 6)]
    else:
        e += eye(-31) + eye(31)
        e += [ln("M-48 -920 Q-32 -928 -14 -920", 5), ln("M14 -920 Q32 -928 48 -920", 5),
              ln("M-22 -844 Q0 -824 24 -846", 6)]
    e += [ln("M4 -884 Q-6 -864 4 -858", 5)]
    return e

def head_shape():
    return [ln("M-78 -880 C-82 -960 -40 -1000 0 -1000 C40 -1000 82 -960 78 -880 C76 -836 44 -800 0 -798 C-44 -800 -76 -836 -78 -880 Z"),
            ln("M-78 -892 C-92 -896 -94 -868 -78 -862", 5), ln("M78 -892 C92 -896 94 -868 78 -862", 5)]

def hair(style):
    if style == "long":
        return [ln("M-82 -890 C-98 -990 -30 -1030 10 -1024 C70 -1014 100 -960 86 -880 C92 -800 98 -740 86 -676"),
                ln("M-82 -890 C-92 -810 -98 -742 -88 -680"),
                ln("M-6 -1020 C-26 -984 -58 -952 -78 -906", 6), ln("M-6 -1020 C24 -984 60 -962 84 -936", 6),
                ln("M-100 -800 C-104 -760 -100 -720 -94 -690", 4), ln("M100 -800 C104 -760 102 -720 96 -690", 4),
                ln("M-60 -980 C-74 -960 -80 -940 -82 -920", 4)]
    if style == "bob":
        p = P("M-92 -870 C-112 -1004 112 -1014 94 -870 L98 -806 C80 -794 68 -804 64 -822 L62 -930 "
              "C20 -946 -30 -946 -64 -930 L-64 -822 C-68 -804 -80 -794 -98 -806 Z")
        return [ln(p, 7), F(p, K_)]
    if style == "pony":
        bow = P("M64 -990 C88 -1032 120 -1012 104 -984 C132 -982 138 -944 104 -958 C98 -942 76 -952 74 -968 Z")
        return [ln("M-82 -894 C-96 -1004 70 -1032 86 -920"), ln("M-80 -900 C-40 -950 30 -966 84 -926", 6),
                ln("M86 -976 C150 -960 166 -870 136 -770 C128 -750 116 -760 118 -782 C136 -860 126 -920 90 -950"),
                ln("M104 -940 C126 -900 128 -850 120 -800", 4), ln(bow, 6), F(bow, RED)]
    return [ln("M-80 -900 C-88 -1004 88 -1012 82 -900"),
            ln("M-80 -900 C-60 -930 -20 -954 20 -950 C50 -946 72 -932 82 -900", 6),
            ln("M-40 -990 L-30 -960 M0 -1000 L6 -962 M36 -994 L34 -958", 4)]

def body(arms="down", shirt_accent=None):
    e = [ln("M-24 -806 L-26 -760", 6), ln("M24 -806 L26 -760", 6), ln("M-26 -760 Q0 -736 26 -760", 6)]
    # t-shirt: sloping shoulders, short sleeves, torso narrowing to the waist
    e += [ln("M-26 -760 C-70 -756 -112 -748 -132 -720 C-148 -694 -158 -664 -160 -630 L-112 -618"),
          ln("M26 -760 C70 -756 112 -748 132 -720 C148 -694 158 -664 160 -630 L112 -618"),
          ln("M-110 -676 C-102 -600 -94 -530 -90 -468"), ln("M110 -676 C102 -600 94 -530 90 -468"),
          ln("M-90 -468 C-30 -458 30 -458 90 -468", 7)]
    if shirt_accent:
        p = P("M-26 -760 C-70 -756 -112 -748 -132 -720 L-110 -676 C-102 -600 -94 -530 -90 -468 C-30 -458 30 -458 90 -468 "
              "C94 -530 102 -600 110 -676 L132 -720 C112 -748 70 -756 26 -760 Q0 -736 -26 -760 Z")
        e.append(F(p, shirt_accent))
    # jeans with a waistband, knees and turned-up hems
    e += [ln("M-90 -468 C-104 -400 -102 -250 -88 -40"), ln("M90 -468 C104 -400 102 -250 88 -40"),
          ln("M-6 -370 C-12 -250 -20 -150 -24 -40"), ln("M6 -370 C12 -250 20 -150 24 -40"),
          ln("M-6 -370 Q0 -380 6 -370", 6), ln("M-90 -440 L90 -440", 5),
          ln("M-86 -62 L-26 -62", 5), ln("M26 -62 L86 -62", 5),
          ln("M-60 -230 Q-50 -220 -40 -230", 4), ln("M40 -230 Q50 -220 60 -230", 4)]
    # shoes
    e += [ln("M-90 -40 C-104 -14 -100 2 -64 2 C-26 2 -14 -8 -24 -40", 7),
          ln("M24 -40 C14 -8 26 2 64 2 C100 2 104 -14 90 -40", 7)]
    def arm_down(sx):
        return [ln(f"M{-160*sx} -630 C{-166*sx} -560 {-168*sx} -500 {-162*sx} -444"),
                ln(f"M{-112*sx} -618 C{-118*sx} -560 {-122*sx} -500 {-122*sx} -450"),
                ln(f"M{-162*sx} -444 C{-172*sx} -404 {-152*sx} -372 {-134*sx} -374 C{-116*sx} -376 {-112*sx} -404 {-122*sx} -450", 7),
                ln(f"M{-122*sx} -432 C{-108*sx} -426 {-104*sx} -410 {-114*sx} -402", 5)]
    e += arm_down(1)
    if arms == "down":
        e += arm_down(-1)
    elif arms == "point":
        e += [ln("M160 -690 C220 -684 290 -680 360 -676"), ln("M112 -626 C200 -640 280 -644 360 -640"),
              ln("M360 -676 C392 -676 420 -668 438 -664 C452 -660 450 -646 436 -646 L392 -648", 7),
              ln("M360 -640 C380 -632 400 -628 404 -640", 6)]
    elif arms == "wave":
        e += [ln("M160 -630 C190 -680 220 -760 228 -840"), ln("M112 -618 C150 -660 180 -740 186 -830"),
              ln("M186 -830 C176 -880 186 -930 200 -940 C214 -950 230 -930 234 -900 C240 -870 236 -850 228 -840", 7),
              ln("M196 -936 L190 -976 M210 -942 L210 -986 M224 -936 L230 -978", 5),
              ln("M250 -980 Q268 -956 262 -930", 5), ln("M276 -970 Q294 -944 286 -916", 5)]
    return e

def person(hair_style="long", expr="happy", arms="down", accent=None, hat=False):
    els = head_shape() + face(expr) + hair(hair_style) + body(arms, accent)
    if hat:
        hp = P("M-56 -996 L0 -1130 L56 -996 Z")
        els += [ln(hp, 7), F(hp, RED), F(circle(0, -1136, 14), K_)]
    return [ (e if True else e) for e in els]

def rescale(els):
    """old layouts were tuned for an ~800-unit figure; keep scene coordinates working."""
    return place(els, 0, 0, 0.8)

def motion_lines(x, y, s=1.0, flip=False):
    sx = -1 if flip else 1
    return [ln(f"M{x} {y} Q{x+14*sx*s} {y+22*s} {x} {y+44*s}", 5), ln(f"M{x+18*sx*s} {y-8*s} Q{x+36*sx*s} {y+22*s} {x+18*sx*s} {y+52*s}", 5)]

def _who_unused(name, x, y, s=1.0, **kw):
    """full person placed with feet at (x,y)."""
    return place(person(**kw), x, y, s)

# ---------------- Slender Man ----------------
def slender(s=1.0, tentacles=False, reach=False):
    e = []
    if tentacles:
        for sx in (-1, 1):
            for k in range(3):
                y0 = -820 + k * 50
                e.append(ln(f"M{40*sx} {y0} C{(200+k*40)*sx} {y0-180+k*60} {(270+k*30)*sx} {y0+30} {(430+k*20)*sx} {y0-100+k*70}", 9))
    hd = P("M-52 -1010 C-58 -1080 58 -1080 52 -1010 C50 -950 30 -920 0 -918 C-30 -920 -50 -950 -52 -1010 Z")
    e.append(ln(hd))
    suit = P("M-70 -912 L70 -912 C80 -760 76 -600 66 -460 L-66 -460 C-76 -600 -80 -760 -70 -912 Z")
    e += [ln(suit), F(suit, K_)]
    tie = P("M-7 -906 L7 -906 L13 -760 L0 -736 L-13 -760 Z")
    e += [F(P("M-26 -912 L0 -820 L26 -912 Z"), "#FFFFFF"), ln("M-26 -912 L0 -820 L26 -912", 5), F(tie, RED), ln(tie, 4)]
    legs = P("M-56 -460 L-10 -460 L-18 -10 L-46 -10 Z M10 -460 L56 -460 L46 -10 L18 -10 Z")
    e += [ln(legs), F(legs, K_)]
    if reach:
        e += [ln("M-66 -900 C-180 -860 -290 -800 -380 -780", 22)]
        e += [ln(f"M-380 -780 L{-380+dx} {-780+dy}", 6) for dx, dy in ((-70, -20), (-76, 4), (-66, 26))]
    else:
        e += [ln("M-70 -900 C-104 -780 -112 -620 -108 -420", 22), ln("M70 -900 C104 -780 112 -620 108 -420", 22)]
        for sx in (-1, 1):
            e += [ln(f"M{108*sx} -420 Q{(110+dx)*sx} -360 {(106+dx*1.5)*sx} -320", 6) for dx in (-10, 0, 10)]
    return place(e, 0, 0, s * 0.95)

# ---------------- simple line props ----------------
def tree(s=1.0, seed=1):
    """bare tree, few confident strokes: tapered trunk, 4 branches, a few twigs."""
    rnd = random.Random(seed)
    e = [ln("M-30 0 C-20 -120 -24 -300 -12 -470", 9), ln("M30 0 C22 -120 24 -300 12 -470", 9),
         ln("M-30 0 C-46 6 -66 4 -84 12", 7), ln("M30 0 C50 4 70 2 90 10", 7)]
    for (x, y, ang, L_) in ((-12, -470, -2.0, 180), (12, -470, -1.1, 190), (-18, -330, -2.6, 150), (20, -290, -0.5, 160)):
        x2, y2 = x + L_ * math.cos(ang), y + L_ * math.sin(ang)
        e.append(ln(f"M{x} {y} Q{(x+x2)/2+rnd.uniform(-12,12):.0f} {(y+y2)/2+rnd.uniform(-12,12):.0f} {x2:.0f} {y2:.0f}", 8))
        a2 = ang + rnd.choice((-0.5, 0.5))
        e.append(ln(f"M{x2:.0f} {y2:.0f} L{x2 + L_*0.45*math.cos(a2):.0f} {y2 + L_*0.45*math.sin(a2):.0f}", 6))
    return place(e, 0, 0, s)

def ground(y=1000, x0=0, x1=1920):
    return [ln(f"M{x0} {y} C{x0+(x1-x0)*0.3} {y-12} {x0+(x1-x0)*0.6} {y+10} {x1} {y-4}", 6)]

def frame_pic(x, y, w, h, hatch=True):
    e = [ln(f"M{x} {y} L{x+w} {y} L{x+w} {y+h} L{x} {y+h} Z", 7),
         ln(f"M{x+24} {y+24} L{x+w-24} {y+24} L{x+w-24} {y+h-24} L{x+24} {y+h-24} Z", 6)]
    if hatch: e += hatch_rect(x + 24, y + 24, w - 48, h - 48, 46)
    return e

def calendar(month="JUNE", day="10", year="2009"):
    e = [ln("M-170 -220 L170 -220 L170 160 L-170 160 Z", 7), ln("M-170 -130 L170 -130", 7),
         ln(circle(-90, -230, 14), 6), ln(circle(90, -230, 14), 6)]
    e += [T(month, 0, -150, 64, "marker", RED), T(day, 0, 40, 170, "marker"), T(year, 0, 120, 60, "brush")]
    return e

def monitor(lines=(), title=""):
    e = [ln("M-300 -400 L300 -400 L300 -20 L-300 -20 Z", 8), ln("M-270 -370 L270 -370 L270 -50 L-270 -50 Z", 5),
         ln("M-40 -20 L-60 60 L60 60 L40 -20", 7), ln("M-120 64 L120 64", 9)]
    if title: e.append(T(title, 0, -300, 46, "marker", RED))
    for i, t in enumerate(lines): e.append(T(t, 0, -220 + i * 62, 48, "brush"))
    return e

def house():
    return [ln("M-180 0 L-180 -260 L180 -260 L180 0 Z"), ln("M-220 -250 L0 -440 L220 -250"),
            ln("M-40 0 L-40 -140 L40 -140 L40 0", 6), ln("M-140 -210 L-70 -210 L-70 -146 L-140 -146 Z", 6),
            ln("M70 -210 L140 -210 L140 -146 L70 -146 Z", 6), ln("M-105 -210 L-105 -146 M-140 -178 L-70 -178", 4),
            ln("M105 -210 L105 -146 M70 -178 L140 -178", 4)]

def moon(x, y, r=60):
    return [ln(f"M{x+r*0.2} {y-r} C{x-r*1.4} {y-r*0.8} {x-r*1.4} {y+r*1.1} {x+r*0.4} {y+r} C{x-r*0.5} {y+r*0.5} {x-r*0.6} {y-r*0.5} {x+r*0.2} {y-r} Z", 6)]

def skate():
    """classic quad roller skate, side view: high boot, laces, toe stop, two wheels."""
    boot = "M-70 -260 C-60 -200 -60 -150 -66 -96 L110 -96 C130 -110 128 -140 100 -150 C60 -162 30 -170 20 -200 L14 -262 Z"
    e = [ln(boot, 8), ln("M-74 -96 L120 -96 L116 -70 L-70 -70 Z", 7), ln("M-78 -260 L22 -262", 7)]
    e += [ln(f"M{-50+i*8} {-240+i*30} L{8+i*4} {-246+i*30}", 4) for i in range(5)]           # laces
    e += [ln("M-60 -70 L-60 -44 M80 -70 L80 -44", 7), ln("M110 -80 C140 -80 146 -54 126 -48 L112 -56", 7)]   # trucks + toe stop
    for x in (-60, 80):
        e += [ln(circle(x, -14, 34), 8), ln(circle(x, -14, 10), 5)]
    e += [ln("M-46 -130 Q-10 -122 30 -130", 4)]
    return e

def froyo():
    """frozen-yogurt cup: tapered paper cup, soft-serve swirl in three tiers, plastic spoon."""
    sw = P("M-96 -150 C-110 -186 -70 -200 -40 -196 C-60 -236 -10 -262 20 -246 C30 -286 80 -282 74 -246 "
           "C110 -236 116 -196 92 -186 C120 -176 112 -146 96 -150 Z")
    e = [ln("M-100 -150 L100 -150 L74 0 L-74 0 Z", 8), ln("M-96 -126 L96 -126", 5), ln(sw, 8), F(sw, "#F6A6C1"),
         ln("M-60 -196 Q0 -180 60 -200", 4), ln("M-20 -246 Q20 -232 60 -244", 4)]
    e += [ln("M50 -220 L120 -330", 9), ln(oval(128, -344, 14, 22), 6)]
    e += [T("FROYO", 0, -48, 42, "marker", RED)]
    return e

def notebook(text="PLAN"):
    return [ln("M-150 -200 L150 -200 L150 20 L-150 20 Z", 7)] + \
           [ln(circle(-150, -180 + i * 36, 8), 4) for i in range(6)] + [T(text, 10, -60, 76, "marker", RED)]

def knife():
    """kitchen knife: curved blade with bevel line, bolster, handle with three rivets."""
    e = [ln("M0 -4 L280 -44 C320 -48 344 -30 350 -8 C300 6 160 22 0 34 Z", 8), ln("M10 6 C110 -4 220 -16 330 -18", 4),
         ln("M-14 -10 L6 -10 L6 40 L-14 40 Z", 6),
         ln("M-14 -6 L-170 -2 C-186 0 -190 34 -172 38 L-14 40", 8)]
    e += [ln(circle(x, 18, 6), 4) for x in (-140, -96, -52)]
    return e

def heart_shape(c=RED):
    p = P("M0 60 C-140 -40 -120 -170 -40 -170 C-10 -170 0 -140 0 -120 C0 -140 10 -170 40 -170 C120 -170 140 -40 0 60 Z")
    return [ln(p, 8), F(p, c)]

def anatomical_heart():
    body = P("M-140 -40 C-170 -180 -40 -230 10 -180 C80 -250 200 -170 160 -20 C130 90 20 170 -20 220 C-80 150 -120 60 -140 -40 Z")
    return [ln(body, 8), ln("M-30 -200 C-40 -270 -10 -320 30 -330 L44 -300 C10 -290 -4 -250 2 -196", 7),
            ln("M40 -190 C60 -250 110 -280 150 -270 L148 -238 C110 -246 80 -220 70 -180", 7),
            ln("M-60 -120 C-20 -60 30 -20 60 60", 5), F(body, "#F4B6B8")]

def hospital(label=""):
    e = [ln("M-320 0 L-320 -420 L320 -420 L320 0 Z"), ln("M-60 0 L-60 -120 L60 -120 L60 0", 6)]
    for r_ in range(2):
        for c_ in range(4):
            x = -270 + c_ * 140; y = -380 + r_ * 120
            e.append(ln(f"M{x} {y} L{x+90} {y} L{x+90} {y+64} L{x} {y+64} Z", 5))
    cr = P("M-20 -500 L20 -500 L20 -470 L50 -470 L50 -430 L20 -430 L20 -400 L-20 -400 L-20 -430 L-50 -430 L-50 -470 L-20 -470 Z")
    if label != "none":
        e += [ln(cr, 6), F(cr, RED)]
    return e

def police_car():
    return [ln("M-260 -60 L-200 -60 L-140 -140 L120 -140 L180 -60 L260 -60 L260 30 L-260 30 Z", 8),
            ln("M-130 -126 L-10 -126 L-10 -64 L-180 -64 Z M10 -126 L112 -126 L160 -64 L10 -64 Z", 5),
            ln(circle(-160, 34, 44), 8), ln(circle(160, 34, 44), 8), ln("M-50 -170 L50 -170 L50 -144 L-50 -144 Z", 5),
            F(P("M-50 -170 L0 -170 L0 -144 L-50 -144 Z"), RED), T("POLICE", 0, 6, 48, "marker")]

def road(y=900, x0=0, x1=1920):
    e = [ln(f"M{x0} {y} L{x1} {y}", 7), ln(f"M{x0} {y+150} L{x1} {y+150}", 7)]
    for x in range(x0 + 60, x1 - 100, 340): e.append(ln(f"M{x} {y+75} L{x+130} {y+75}", 8))
    return e

def bike():
    return [ln(circle(-110, 0, 70), 7), ln(circle(110, 0, 70), 7),
            ln("M-110 0 L-30 -110 L80 -110 L110 0 M-30 -110 L0 0 L80 -110 M-40 -130 L-10 -130 M80 -110 L70 -150 L110 -160", 7)]

def bed():
    return [ln("M-300 -120 L300 -120 L300 -30 L-300 -30 Z", 8), ln("M-290 -30 L-290 40 M290 -30 L290 40 M300 -120 L300 -230", 9),
            ln("M-140 -130 L300 -130", 6), ln(oval(-220, -140, 70, 34), 6)]

def gavel():
    """judge's gavel: barrel head with bands, turned handle, round sound block."""
    e = [ln("M-130 -220 L130 -220 C146 -220 150 -110 130 -110 L-130 -110 C-146 -110 -150 -220 -130 -220 Z", 8),
         ln("M-130 -220 C-114 -220 -110 -110 -130 -110", 6), ln("M130 -220 C114 -220 110 -110 130 -110", 6),
         ln("M-70 -218 L-70 -112 M70 -218 L70 -112", 6),
         ln("M-14 -110 L-12 140 C-12 160 12 160 12 140 L14 -110", 8), ln("M-18 -40 L18 -40 M-18 60 L18 60", 5)]
    e += [ln("M-170 190 C-170 160 170 160 170 190 L170 220 C170 250 -170 250 -170 220 Z", 8), ln("M-170 190 C-170 220 170 220 170 190", 6)]
    return e

def bubble(text, x, y, w=620, h=150, size=64):
    return [ln(f"M{x-w/2+40} {y-h/2} L{x+w/2-40} {y-h/2} Q{x+w/2} {y-h/2} {x+w/2} {y-h/2+40} L{x+w/2} {y+h/2-40} "
               f"Q{x+w/2} {y+h/2} {x+w/2-40} {y+h/2} L{x-w*0.1} {y+h/2} L{x-w*0.35} {y+h/2+60} L{x-w*0.25} {y+h/2} "
               f"L{x-w/2+40} {y+h/2} Q{x-w/2} {y+h/2} {x-w/2} {y+h/2-40} L{x-w/2} {y-h/2+40} Q{x-w/2} {y-h/2} {x-w/2+40} {y-h/2} Z", 7),
            T(text, x, y + size * 0.33, size, "brush")]

def spiky(text_lines, x, y, w=560, h=300, size=90):
    """red spiky shout bubble like '¡NO AL BULLING!'"""
    pts = []
    n = 22
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1.0 if i % 2 == 0 else 0.86
        pts.append((x + math.cos(a) * w / 2 * r, y + math.sin(a) * h / 2 * r))
    d = "M" + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + " Z"
    out = [ln(d, 7, RED)]
    for i, t in enumerate(text_lines):
        out.append(T(t, x, y - (len(text_lines) - 1) * size * 0.55 + i * size * 1.1 + size * 0.33, size, "marker"))
    return out

def ankle_monitor():
    """lower leg and foot (side view) with an electronic ankle monitor strapped on."""
    e = [ln("M-50 -420 C-56 -300 -60 -200 -56 -90 C-54 -40 -40 -10 -20 0 L200 0 C226 0 230 -30 204 -40 "
            "C150 -60 90 -70 60 -100 C46 -140 46 -300 50 -420", 9),
         ln("M150 0 L150 -16 M178 0 L178 -14", 4), ln("M-20 -60 Q-6 -50 4 -60", 4)]
    e += [ln("M-66 -200 C-60 -186 60 -186 66 -200 L66 -160 C60 -146 -60 -146 -66 -160 Z", 7)]
    box = P("M-46 -226 L46 -226 L46 -126 L-46 -126 Z")
    e += [ln(box, 8), F(box, "#2B2B2B"), F(circle(0, -196, 9), "#33CC66"), ln("M-30 -150 L30 -150", 4, "#FFFFFF")]
    return e

def scissors():
    return [ln("M0 0 L160 -120", 9), ln("M0 0 L170 -60", 9), ln(circle(-40, 20, 30), 8), ln(circle(-30, -40, 30), 8)]

def truck_stop():
    """24h truck stop: diner with sign, fuel canopy with pumps, a semi truck parked."""
    e = [ln("M-420 0 L-420 -230 L-60 -230 L-60 0 Z"), ln("M-440 -260 L-40 -260 L-40 -228 L-440 -228 Z", 7)]
    for x in (-390, -290, -190):
        e.append(ln(f"M{x} -190 L{x+80} -190 L{x+80} -110 L{x} -110 Z", 5))
    e += [ln("M-110 0 L-110 -150 L-70 -150 L-70 0", 6), T("DINER", -240, -236, 30, "marker")]
    e += [ln("M40 -300 L420 -300 L420 -270 L40 -270 Z", 8), ln("M80 -270 L80 0 M380 -270 L380 0", 8)]
    for x in (170, 290):
        e += [ln(f"M{x-30} 0 L{x-30} -120 L{x+30} -120 L{x+30} 0", 6), ln(f"M{x-16} -100 L{x+16} -100 L{x+16} -70 L{x-16} -70 Z", 4)]
    e += [ln("M470 0 L470 -460", 9), ln("M400 -560 L560 -560 L560 -440 L400 -440 Z", 8), T("24h", 480, -478, 70, "marker", RED)]
    return e

def search_bar(text):
    return [ln("M-480 -60 L480 -60 Q540 -60 540 0 Q540 60 480 60 L-480 60 Q-540 60 -540 0 Q-540 -60 -480 -60 Z", 7),
            ln(circle(-460, -6, 24), 6), ln("M-443 11 L-420 34", 8), T(text, -380, 22, 70, "brush", align="left")]

def comment_box(lines):
    e = [ln("M-440 -80 L440 -80 L440 380 L-440 380 Z", 7), T("WHO IS TO BLAME?", 0, -6, 70, "marker", RED)]
    for i, l in enumerate(lines):
        y = 80 + i * 100
        e += [ln(f"M-330 {y} L-280 {y} L-280 {y+50} L-330 {y+50} Z", 5), T(l, -240, y + 44, 64, "brush", align="left")]
    return e

def subscribe_btn():
    b = P("M-260 -70 L260 -70 L260 70 L-260 70 Z")
    return [ln(b, 8), F(b, RED), T("SUBSCRIBE", 0, 26, 74, "marker", "#FFFFFF")]

def paper():
    return [ln("M-110 -150 L60 -150 L110 -100 L110 150 L-110 150 Z", 7), ln("M60 -150 L60 -100 L110 -100", 5)] + \
           [ln(f"M-80 {-80 + i*44} L80 {-80 + i*44}", 4) for i in range(5)]

def play_icon():
    t = P("M-30 -44 L50 0 L-30 44 Z")
    return [ln("M-120 -80 L120 -80 L120 80 L-120 80 Z", 7), ln(t, 6), F(t, RED)]

def gamepad():
    return [ln("M-150 -60 C-180 -60 -200 60 -160 80 C-120 100 -100 40 -60 40 L60 40 C100 40 120 100 160 80 C200 60 180 -60 150 -60 Z", 7),
            ln("M-110 -10 L-50 -10 M-80 -40 L-80 20", 8), ln(circle(70, -20, 12), 6), ln(circle(110, 10, 12), 6)]

def browser():
    return [ln("M-170 -130 L170 -130 L170 130 L-170 130 Z", 7), ln("M-170 -80 L170 -80", 5),
            ln("M-130 -30 L130 -30 M-130 20 L80 20 M-130 70 L110 70", 5)]

def leaves(n=12, w=480, seed=3):
    rnd = random.Random(seed); out = []
    for i in range(n):
        x = rnd.uniform(-w / 2, w / 2); y = rnd.uniform(-70, 0); r = rnd.uniform(-60, 60)
        lf = P("M0 0 C20 -30 60 -30 80 0 C60 30 20 30 0 0 Z")
        m = skia.Matrix(); m.setTranslate(x, y); m.preRotate(r); lf.transform(m)
        out.append(ln(lf, 5))
    for i in range(5):
        x = rnd.uniform(-w / 2, w / 2)
        out.append(ln(f"M{x:.0f} -40 L{x + rnd.uniform(-120, 120):.0f} {rnd.uniform(-90, 0):.0f}", 6))
    return out

def lying(expr="blank"):
    els = rescale(person("long", expr))
    m = skia.Matrix(); m.setRotate(-90); m.postScale(0.55, 0.55)
    return [e.transformed(m) for e in els]
