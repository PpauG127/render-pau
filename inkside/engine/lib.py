"""Reusable drawings. Each function returns a list of El in local coordinates."""
from engine import *

SKIN = "#F6D2B5"
def art(strokes, fills):
    """lines first, then color; color is painted under all of this object's lines"""
    zs = [e.zk for e in strokes]
    if zs:
        base = min(zs) - 0.9
        for i, f in enumerate(fills):
            f.zk = base + i * 1e-4
    return strokes + fills

def L(*ds, w=6, c=K):
    return [S(d, w, c) for d in ds]

# ---------------- people ----------------
HAIR = {
 "bob":  "M-92 -280 C-110 -420 110 -420 92 -280 L96 -232 L54 -236 L58 -322 C20 -350 -30 -350 -60 -318 L-56 -236 L-96 -232 Z",
 "pony": "M-86 -300 C-100 -410 100 -410 86 -300 C70 -340 -20 -360 -80 -300 Z",
 "short": "M-84 -300 C-100 -410 100 -410 84 -300 C60 -350 -60 -350 -84 -300 Z",
 "long": "M-90 -290 C-108 -420 108 -420 90 -290 L98 -170 L60 -176 L58 -322 C20 -350 -30 -350 -60 -318 L-60 -176 L-98 -170 Z",
}
def girl(hair="bob", hair_c="#3A2A20", shirt="#7A4FB5", pants="#2E3A59", face="smile", label=None, hat=False,
         arms="down", flip=False):
    st, fi = [], []
    head = circle(0, -300, 78)
    st.append(S(head)); fi.append(F(head, SKIN))
    hp = P(HAIR[hair]); st.append(S(hp)); fi.append(F(hp, hair_c))
    if hair == "pony":
        tail = P("M70 -360 C140 -360 150 -280 120 -220 C110 -260 100 -300 70 -330 Z")
        st.append(S(tail)); fi.append(F(tail, hair_c))
    # face
    if face in ("smile", "happy", "scared", "sad"):
        st += [S(oval(-28, -292, 7, 10), 0), S(oval(28, -292, 7, 10), 0)]
        fi += [F(oval(-28, -292, 8, 11), "#151515"), F(oval(28, -292, 8, 11), "#151515")]
    if face == "sinister":
        st += L("M-44 -300 L-12 -290", "M12 -290 L44 -300", w=7)
        st.append(S("M-34 -258 Q0 -236 34 -258", 5))
    elif face in ("smile", "happy"):
        st.append(S("M-26 -262 Q0 -238 26 -262", 5))
    elif face == "scared":
        st += L("M-44 -322 L-16 -330", "M16 -330 L44 -322", w=5)
        o = oval(0, -252, 12, 16); st.append(S(o, 5)); fi.append(F(o, "#5a1a1a"))
    elif face == "sad":
        st.append(S("M-22 -248 Q0 -264 22 -248", 5))
    elif face == "blank":
        pass
    # body
    shirt_p = P("M-50 -222 L50 -222 L68 -96 L-68 -96 Z")
    st.append(S(shirt_p)); fi.append(F(shirt_p, shirt))
    legs = P("M-52 -96 L52 -96 L44 -6 L8 -6 L2 -60 L-4 -60 L-10 -6 L-44 -6 Z")
    st.append(S(legs)); fi.append(F(legs, pants))
    for sx in (-26, 26):
        sh = oval(sx, -2, 26, 12); st.append(S(sh, 5)); fi.append(F(sh, "#222222"))
    # arms
    if arms == "down":
        a = ["M-50 -212 L-86 -120", "M50 -212 L86 -120"]; hands = [(-90, -110), (90, -110)]
    elif arms == "up":
        a = ["M-50 -212 L-110 -300", "M50 -212 L110 -300"]; hands = [(-116, -312), (116, -312)]
    elif arms == "front":
        a = ["M-50 -212 L-60 -150 L-10 -150", "M50 -212 L60 -150 L14 -150"]; hands = [(0, -150)]
    else:  # reach
        a = ["M-50 -212 L-86 -120", "M50 -212 L150 -200"]; hands = [(-90, -110), (162, -200)]
    st += [S(x, 14, "#151515") for x in a]
    for hx, hy in hands:
        h = circle(hx, hy, 15); st.append(S(h, 5)); fi.append(F(h, SKIN))
    if hat:
        hp = P("M-40 -372 L0 -470 L40 -372 Z"); st.append(S(hp, 5)); fi.append(F(hp, "#F2C230"))
        st.append(S(circle(0, -476, 10), 5))
    els = art(st, fi)
    if flip:
        m = skia.Matrix(); m.setScale(-1, 1); els = [e.transformed(m) for e in els]
    if label:
        els.append(T(label, 0, 70, 54, "brush"))
    return els

def silhouette(scale=1.0):
    """Small black kid silhouette."""
    p = skia.Path(); p.addCircle(0, -300, 70)
    p.addPath(P("M-55 -225 L55 -225 L70 -100 L45 0 L10 0 L0 -80 L-10 0 L-45 0 L-70 -100 Z"))
    return [S(p, 5), F(p, "#1b1b1b")]

def slender(height=1.0, arms="down", tentacles=False):
    st, fi = [], []
    if tentacles:
        for d in ["M-40 -720 C-200 -820 -260 -700 -380 -760", "M-40 -680 C-220 -640 -260 -520 -360 -540",
                  "M40 -720 C200 -830 260 -700 380 -770", "M40 -680 C230 -640 250 -520 370 -560"]:
            st.append(S(d, 16, "#151515"))
    head = oval(0, -830, 50, 64); st.append(S(head)); fi.append(F(head, "#F4F4F4"))
    suit = P("M-58 -755 L58 -755 L50 -390 L-50 -390 Z"); st.append(S(suit)); fi.append(F(suit, "#1d1d1d"))
    shirt = P("M-20 -755 L0 -690 L20 -755 Z"); st.append(S(shirt, 4)); fi.append(F(shirt, "#FFFFFF"))
    tie = P("M-6 -748 L6 -748 L11 -620 L0 -598 L-11 -620 Z"); st.append(S(tie, 3)); fi.append(F(tie, "#8E1B1B"))
    legs = P("M-48 -392 L-6 -392 L-14 0 L-40 0 Z M6 -392 L48 -392 L40 0 L14 0 Z"); st.append(S(legs)); fi.append(F(legs, "#1d1d1d"))
    if arms == "down":
        ar = ["M-56 -740 C-90 -600 -96 -470 -92 -330", "M56 -740 C90 -600 96 -470 92 -330"]
        fingers = ["M-92 -330 L-100 -270", "M-92 -330 L-86 -268", "M92 -330 L100 -270", "M92 -330 L86 -268"]
    else:  # reaching forward (to the left)
        ar = ["M-56 -740 C-160 -700 -260 -640 -330 -620", "M56 -740 C90 -600 96 -470 92 -330"]
        fingers = ["M-330 -620 L-392 -640", "M-330 -620 L-394 -610", "M-330 -620 L-380 -584", "M92 -330 L100 -270", "M92 -330 L86 -268"]
    st += [S(a, 20, "#151515") for a in ar] + [S(f, 7, "#151515") for f in fingers]
    els = art(st, fi)
    if height != 1.0:
        els = place(els, 0, 0, height)
    return els

def tree(h=1.0, c="#4B3A2E"):
    st, fi = [], []
    trunk = P("M-24 0 C-18 -160 -28 -320 -10 -460 L10 -460 C20 -320 22 -160 28 0 Z")
    st.append(S(trunk)); fi.append(F(trunk, c))
    for d in ["M-12 -300 C-60 -360 -90 -380 -140 -460", "M-90 -390 L-130 -380", "M10 -360 C60 -410 90 -450 120 -540",
              "M80 -440 L130 -450", "M-6 -440 C-20 -500 -10 -540 -30 -600", "M0 -200 C40 -230 70 -240 100 -300"]:
        st.append(S(d, 9, "#2B2018"))
    els = art(st, fi)
    return place(els, 0, 0, h) if h != 1 else els

def forest(y=980, xs=(120, 330, 1580, 1800), hs=(1.25, 1.0, 1.1, 1.3)):
    out = []
    for x, h in zip(xs, hs): out += place(tree(), x, y, h)
    return out

def ground(y=980, c="#3E5B2E"):
    return [S(f"M0 {y} C400 {y-14} 800 {y+12} 1200 {y-6} C1500 {y-16} 1750 {y+8} 1920 {y}", 7)]

# ---------------- props ----------------
def monitor(text_lines=(), title=""):
    st, fi = [], []
    scr = rect(-300, -400, 600, 380, 18); st.append(S(scr, 8)); fi.append(F(scr, "#2F3B4A"))
    inner = rect(-268, -370, 536, 320, 6); st.append(S(inner, 4)); fi.append(F(inner, "#EEF2F7"))
    st += L("M-40 -20 L-60 60 L60 60 L40 -20", w=8); st.append(S("M-120 64 L120 64", 10))
    els = art(st, fi)
    if title:
        els.append(T(title, 0, -300, 44, "marker", "#2F3B4A"))
    for i, t in enumerate(text_lines):
        els.append(T(t, 0, -220 + i * 62, 46, "brush"))
    return els

def calendar(month="JUNE", day="10", year="2009"):
    st, fi = [], []
    page = rect(-170, -220, 340, 380, 16); st.append(S(page, 8)); fi.append(F(page, "#FFFFFF"))
    top = rect(-170, -220, 340, 100, 16); st.append(S(top, 8)); fi.append(F(top, "#D7262E"))
    st += [S(circle(-90, -230, 14), 6), S(circle(90, -230, 14), 6)]
    els = art(st, fi)
    els += [T(month, 0, -148, 56, "marker", "#FFFFFF"), T(day, 0, 40, 170, "marker"), T(year, 0, 120, 60, "brush")]
    return els

def photo(w=520, h=360, gray=True):
    st, fi = [], []
    fr = rect(-w/2 - 24, -h - 24, w + 48, h + 48, 4); st.append(S(fr, 6)); fi.append(F(fr, "#FBF7EE"))
    pic = rect(-w/2, -h, w, h); st.append(S(pic, 5)); fi.append(F(pic, "#B9B9B9" if gray else "#CFE3F5"))
    return art(st, fi)

def house(night=False):
    st, fi = [], []
    body = rect(-180, -260, 360, 260); st.append(S(body, 8)); fi.append(F(body, "#E9D3B0"))
    roof = P("M-220 -250 L0 -440 L220 -250 Z"); st.append(S(roof, 8)); fi.append(F(roof, "#9A3B2E"))
    door = rect(-40, -140, 80, 140, 6); st.append(S(door, 6)); fi.append(F(door, "#6B4428"))
    for x in (-140, 70):
        w_ = rect(x, -210, 70, 64, 4); st.append(S(w_, 6)); fi.append(F(w_, "#F7D65A" if night else "#BFE0F5"))
    return art(st, fi)

def moon(x=0, y=0, r=70):
    p = P(f"M{x+r*0.2} {y-r} C{x-r*1.4} {y-r*0.8} {x-r*1.4} {y+r*1.1} {x+r*0.4} {y+r} C{x-r*0.5} {y+r*0.5} {x-r*0.6} {y-r*0.5} {x+r*0.2} {y-r} Z")
    return art([S(p, 6)], [F(p, "#F5E7A3")])

def skate():
    st, fi = [], []
    boot = P("M-80 -170 L20 -170 L30 -80 C80 -76 120 -60 120 -30 L-90 -30 Z")
    st.append(S(boot, 7)); fi.append(F(boot, "#E85D9A"))
    st.append(S("M-100 -30 L130 -30", 9))
    for x in (-60, 0, 70):
        wh = circle(x, -6, 22); st.append(S(wh, 6)); fi.append(F(wh, "#F2C230"))
    st += L("M-60 -150 L0 -150", "M-60 -125 L0 -125", "M-60 -100 L4 -100", w=5)
    return art(st, fi)

def froyo():
    st, fi = [], []
    cup = P("M-80 -120 L80 -120 L56 0 L-56 0 Z"); st.append(S(cup, 7)); fi.append(F(cup, "#7EC8E3"))
    swirl = P("M-86 -120 C-100 -170 -40 -190 -50 -200 C-30 -250 40 -250 40 -210 C80 -200 100 -150 86 -120 Z")
    st.append(S(swirl, 7)); fi.append(F(swirl, "#F7C6D9"))
    st.append(S("M0 -240 C10 -270 30 -280 20 -300", 6))
    sp = P("M30 -200 L110 -300 L124 -290 L44 -190 Z"); st.append(S(sp, 5)); fi.append(F(sp, "#FFFFFF"))
    return art(st, fi)

def notebook(text="PLAN"):
    st, fi = [], []
    b = rect(-150, -200, 300, 220, 10); st.append(S(b, 7)); fi.append(F(b, "#FFF6C8"))
    for i in range(5): st.append(S(f"M-130 {-150 + i*34} L130 {-150 + i*34}", 3, "#7AA7D8"))
    for i in range(6): st.append(S(circle(-150, -180 + i * 36, 8), 4))
    els = art(st, fi); els.append(T(text, 10, -60, 70, "marker", "#D7262E")); return els

def knife():
    st, fi = [], []
    blade = P("M0 0 L260 -40 C300 -46 330 -30 340 -10 L0 30 Z"); st.append(S(blade, 6)); fi.append(F(blade, "#D9DEE3"))
    handle = rect(-150, -6, 150, 44, 14); st.append(S(handle, 6)); fi.append(F(handle, "#3A2A20"))
    st += [S(circle(-110, 16, 6), 4), S(circle(-50, 16, 6), 4)]
    return art(st, fi)

def heart(c="#D7262E"):
    p = P("M0 60 C-140 -40 -120 -170 -40 -170 C-10 -170 0 -140 0 -120 C0 -140 10 -170 40 -170 C120 -170 140 -40 0 60 Z")
    return art([S(p, 8)], [F(p, c)])

def anatomical_heart():
    st, fi = [], []
    body = P("M-140 -40 C-170 -180 -40 -230 10 -180 C80 -250 200 -170 160 -20 C130 90 20 170 -20 220 C-80 150 -120 60 -140 -40 Z")
    st.append(S(body, 8)); fi.append(F(body, "#C9343A"))
    art_ = P("M-30 -200 C-40 -270 -10 -320 30 -330 L44 -300 C10 -290 -4 -250 2 -196 Z")
    st.append(S(art_, 6)); fi.append(F(art_, "#8E1B1B"))
    art2 = P("M40 -190 C60 -250 110 -280 150 -270 L148 -238 C110 -246 80 -220 70 -180 Z")
    st.append(S(art2, 6)); fi.append(F(art2, "#3B6FB6"))
    st.append(S("M-60 -120 C-20 -60 30 -20 60 60", 5, "#7A1515"))
    return art(st, fi)

def hospital(label="HOSPITAL"):
    st, fi = [], []
    b = rect(-320, -420, 640, 420); st.append(S(b, 8)); fi.append(F(b, "#F3F3F3"))
    for r_ in range(3):
        for c_ in range(4):
            w_ = rect(-270 + c_ * 140, -380 + r_ * 110, 90, 70, 4); st.append(S(w_, 5)); fi.append(F(w_, "#BFE0F5"))
    d = rect(-60, -120, 120, 120, 4); st.append(S(d, 6)); fi.append(F(d, "#8AA4B8"))
    els = art(st, fi)
    if label: els += place(sign(label, 520, 90, "#2F5D8A"), 0, -470)
    return els

def red_cross(s=1):
    p = P("M-25 -75 L25 -75 L25 -25 L75 -25 L75 25 L25 25 L25 75 L-25 75 L-25 25 L-75 25 L-75 -25 L-25 -25 Z")
    return place(art([S(p, 6)], [F(p, "#D7262E")]), 0, 0, s)

def sign(text, w=420, h=90, c="#2E7D4F", tc="#FFFFFF", size=None):
    b = rect(-w / 2, -h / 2, w, h, 12)
    return art([S(b, 7)], [F(b, c)]) + [T(text, 0, h * 0.2, size or h * 0.55, "marker", tc)]

def police_car():
    st, fi = [], []
    body = P("M-260 -60 L-200 -60 L-140 -140 L120 -140 L180 -60 L260 -60 L260 30 L-260 30 Z")
    st.append(S(body, 8)); fi.append(F(body, "#FFFFFF"))
    low = rect(-260, -20, 520, 50); st.append(S(low, 6)); fi.append(F(low, "#1F2F5A"))
    win = P("M-130 -126 L-10 -126 L-10 -64 L-180 -64 Z M10 -126 L112 -126 L160 -64 L10 -64 Z")
    st.append(S(win, 5)); fi.append(F(win, "#BFE0F5"))
    lr = rect(-50, -170, 50, 26, 6); lb = rect(0, -170, 50, 26, 6)
    st += [S(lr, 5), S(lb, 5)]; fi += [F(lr, "#D7262E"), F(lb, "#2F6FD6")]
    for x in (-160, 160):
        wh = circle(x, 34, 44); st.append(S(wh, 7)); fi.append(F(wh, "#222222"))
    els = art(st, fi); els.append(T("POLICE", 0, 22, 40, "marker", "#FFFFFF")); return els

def bike():
    st = []
    st += [S(circle(-110, 0, 70), 7), S(circle(110, 0, 70), 7)]
    st += L("M-110 0 L-30 -110 L80 -110 L110 0", "M-30 -110 L0 0 L80 -110", "M-40 -130 L-10 -130", "M80 -110 L70 -150 L110 -160", w=7)
    return st

def bed():
    st, fi = [], []
    frame = rect(-300, -120, 600, 90, 10); st.append(S(frame, 8)); fi.append(F(frame, "#DDE6EE"))
    st += L("M-290 -30 L-290 40", "M290 -30 L290 40", "M300 -120 L300 -230", w=10)
    sheet = P("M-140 -130 L300 -130 L300 -70 L-140 -70 Z"); st.append(S(sheet, 6)); fi.append(F(sheet, "#9FC7E8"))
    pil = oval(-220, -140, 70, 34); st.append(S(pil, 6)); fi.append(F(pil, "#FFFFFF"))
    return art(st, fi)

def gavel():
    st, fi = [], []
    head = rect(-120, -200, 240, 90, 20); st.append(S(head, 8)); fi.append(F(head, "#7A4A2A"))
    hd = rect(-14, -110, 28, 230, 10); st.append(S(hd, 7)); fi.append(F(hd, "#9A6236"))
    base = rect(-160, 150, 320, 50, 12); st.append(S(base, 7)); fi.append(F(base, "#5C3A22"))
    return art(st, fi)

def search_bar(text):
    st, fi = [], []
    bar = rect(-520, -60, 1040, 120, 60); st.append(S(bar, 7)); fi.append(F(bar, "#FFFFFF"))
    st += [S(circle(-450, -6, 24), 6), S("M-433 11 L-410 34", 8)]
    els = art(st, fi); els.append(T(text, -380, 22, 66, "brush", align="left")); return els

def ankle_monitor():
    st, fi = [], []
    leg = P("M-60 -400 L60 -400 L60 -60 C120 -40 200 -30 200 20 L-70 20 Z")
    st.append(S(leg, 7)); fi.append(F(leg, SKIN))
    strap = rect(-70, -170, 140, 50, 6); st.append(S(strap, 6)); fi.append(F(strap, "#333333"))
    box = rect(-40, -190, 80, 90, 10); st.append(S(box, 6)); fi.append(F(box, "#555555"))
    led = circle(0, -150, 9); fi.append(F(led, "#3BD16F")); st.append(S(led, 3))
    return art(st, fi)

def scissors():
    st = L("M0 0 L160 -120", "M0 0 L170 -60", w=10)
    st += [S(circle(-40, 20, 30), 8), S(circle(-30, -40, 30), 8)]
    return st

def truck_stop():
    st, fi = [], []
    b = rect(-360, -260, 720, 260); st.append(S(b, 8)); fi.append(F(b, "#4A4F5C"))
    roof = rect(-400, -300, 800, 50, 6); st.append(S(roof, 7)); fi.append(F(roof, "#D7262E"))
    for x in (-300, -120, 60, 220):
        w_ = rect(x, -210, 110, 90, 4); st.append(S(w_, 5)); fi.append(F(w_, "#F7D65A"))
    pole = rect(440, -420, 20, 420); st.append(S(pole, 6)); fi.append(F(pole, "#666666"))
    s_ = rect(370, -520, 160, 110, 10); st.append(S(s_, 7)); fi.append(F(s_, "#F2C230"))
    els = art(st, fi); els.append(T("TRUCK STOP", 0, -262, 40, "marker", "#FFFFFF")); els.append(T("24h", 450, -448, 50, "marker"))
    return els

def comment_box(lines):
    st, fi = [], []
    b = rect(-420, -60, 840, 120 + 90 * len(lines), 24); st.append(S(b, 7)); fi.append(F(b, "#FFFFFF"))
    av = circle(-340, 0, 34); st.append(S(av, 5)); fi.append(F(av, "#9AA5B1"))
    els = art(st, fi)
    els.append(T("Who is to blame?", -280, 18, 54, "marker", align="left"))
    for i, l in enumerate(lines):
        cb = rect(-330, 70 + i * 90, 50, 50, 8)
        els += [S(cb, 5), T(l, -250, 112 + i * 90, 58, "brush", align="left")]
    return els

def subscribe_btn():
    b = rect(-260, -70, 520, 140, 30)
    return art([S(b, 8)], [F(b, "#D7262E")]) + [T("SUBSCRIBE", 0, 26, 74, "marker", "#FFFFFF")]

def money_bag():
    st, fi = [], []
    bag = P("M-40 -200 C-160 -120 -170 40 0 40 C170 40 160 -120 40 -200 Z"); st.append(S(bag, 8)); fi.append(F(bag, "#D9B26A"))
    tie = P("M-50 -210 L50 -210 L30 -240 L-30 -240 Z"); st.append(S(tie, 6)); fi.append(F(tie, "#B88A3E"))
    els = art(st, fi); els.append(T("$", 0, -30, 150, "marker", "#2E6B3A")); return els

def fist():
    st, fi = [], []
    f = P("M-90 -60 C-100 -150 -40 -170 0 -160 C40 -170 100 -150 90 -60 L80 40 L-80 40 Z")
    st.append(S(f, 8)); fi.append(F(f, SKIN))
    st += L("M-60 -150 L-60 -100", "M-20 -160 L-20 -104", "M20 -160 L20 -104", "M60 -150 L60 -100", w=5)
    sl = rect(-90, 40, 180, 90, 6); st.append(S(sl, 7)); fi.append(F(sl, "#3B6FB6"))
    return art(st, fi)

def cross_out(w=260):
    return [S(f"M{-w} {-w} L{w} {w}", 22, "#D7262E"), S(f"M{w} {-w} L{-w} {w}", 22, "#D7262E")]

def play_icon():
    b = rect(-120, -80, 240, 160, 30)
    tri = P("M-30 -44 L50 0 L-30 44 Z")
    return art([S(b, 7), S(tri, 6)], [F(b, "#D7262E"), F(tri, "#FFFFFF")])

def gamepad():
    b = P("M-150 -60 C-180 -60 -200 60 -160 80 C-120 100 -100 40 -60 40 L60 40 C100 40 120 100 160 80 C200 60 180 -60 150 -60 Z")
    st = [S(b, 7), S("M-110 -10 L-50 -10", 8), S("M-80 -40 L-80 20", 8), S(circle(70, -20, 12), 5), S(circle(110, 10, 12), 5)]
    return art(st, [F(b, "#7A4FB5")])

def paper():
    b = P("M-110 -150 L60 -150 L110 -100 L110 150 L-110 150 Z")
    st = [S(b, 7), S("M60 -150 L60 -100 L110 -100", 5)] + [S(f"M-80 {-80 + i*44} L80 {-80 + i*44}", 4) for i in range(5)]
    return art(st, [F(b, "#FFFFFF")])

def browser():
    b = rect(-170, -130, 340, 260, 14); top = rect(-170, -130, 340, 50, 14)
    st = [S(b, 7), S(top, 5)] + [S(circle(-140 + i * 30, -105, 8), 4) for i in range(3)]
    st += [S("M-130 -30 L130 -30", 5), S("M-130 20 L80 20", 5), S("M-130 70 L110 70", 5)]
    return art(st, [F(b, "#FFFFFF"), F(top, "#9AA5B1")])

def globe():
    g = circle(0, 0, 150)
    st = [S(g, 8), S(oval(0, 0, 70, 150), 5), S("M-150 0 L150 0", 5), S("M-130 -75 L130 -75", 4), S("M-130 75 L130 75", 4)]
    return art(st, [F(g, "#7EC8E3")])

def leaves(n=14, w=420, seed=3):
    import random
    rnd = random.Random(seed); st, fi = [], []
    for i in range(n):
        x = rnd.uniform(-w / 2, w / 2); y = rnd.uniform(-60, 10); r = rnd.uniform(-60, 60)
        lf = P("M0 0 C20 -30 60 -30 80 0 C60 30 20 30 0 0 Z")
        m = skia.Matrix(); m.setTranslate(x, y); m.preRotate(r); lf.transform(m)
        st.append(S(lf, 4)); fi.append(F(lf, rnd.choice(["#C9762B", "#A9442A", "#8A6A2A", "#6F7B2E"])))
    for i in range(6):
        x = rnd.uniform(-w / 2, w / 2)
        st.append(S(f"M{x} {-40} L{x + rnd.uniform(-120, 120)} {rnd.uniform(-90, 0)}", 7, "#5A3C22"))
    return art(st, fi)

def lying_girl():
    """Girl lying on the ground, seen from the side (head on the left)."""
    st, fi = [], []
    head = circle(-260, -60, 62); st.append(S(head)); fi.append(F(head, SKIN))
    hair = P("M-320 -70 C-330 -150 -190 -150 -200 -70 C-230 -100 -290 -100 -320 -70 Z")
    st.append(S(hair)); fi.append(F(hair, "#7A4A2A"))
    st += [S("M-270 -66 L-250 -66", 5)]
    body = P("M-200 -100 L0 -100 L0 -20 L-200 -20 Z"); st.append(S(body)); fi.append(F(body, "#3B82C4"))
    legs = P("M0 -96 L200 -84 L200 -36 L0 -24 Z"); st.append(S(legs)); fi.append(F(legs, "#2E3A59"))
    return art(st, fi)

def stethoscope():
    return [S("M-60 -120 C-80 0 80 0 60 -120", 9, "#333333"), S("M0 -10 L0 80", 9, "#333333"),
            S(circle(0, 100, 26), 8, "#333333")]

def road(y=900):
    r = P(f"M0 {y} L1920 {y} L1920 {y+180} L0 {y+180} Z")
    els = art([S(r, 6)], [F(r, "#5A5F68")])
    for x in range(40, 1920, 260): els.append(S(f"M{x} {y+90} L{x+140} {y+90}", 10, "#F2C230"))
    return els

def red_drip_title(text, x, y, size=150):
    return [T(text, x, y, size, "marker", "#D7262E")]
