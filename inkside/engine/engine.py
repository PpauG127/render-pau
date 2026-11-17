"""Whiteboard 'Draw My Life' animation engine (skia-python -> ffmpeg)."""
import math, re, random
import numpy as np
import skia

W, H, FPS = 1920, 1080, 60
K = 0xFF151515
WHITE = 0xFFFFFFFF
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../inkside
ASSETS = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(ASSETS, "fonts") + "/"
TF = {
    "marker": skia.Typeface.MakeFromFile(FONT_DIR + "permanent-marker.ttf"),
    "brush": skia.Typeface.MakeFromFile(FONT_DIR + "caveat-brush.ttf"),
    "news": skia.Typeface.MakeFromFile(FONT_DIR + "oswald-bold.ttf"),
    "serif": skia.Typeface.MakeFromFile(FONT_DIR + "pt-serif.ttf"),
}

def col(h, a=255):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

# ---------------- path helpers ----------------
_tok = re.compile(r"[MLQCZmlqcz]|-?\d*\.?\d+(?:e-?\d+)?")

def P(d):
    """Tiny SVG-path parser (absolute M L Q C Z)."""
    p = skia.Path()
    toks = _tok.findall(d)
    i, cmd = 0, None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t.upper(); i += 1
            if cmd == "Z":
                p.close(); continue
        if cmd == "M":
            p.moveTo(num(), num()); cmd = "L"
        elif cmd == "L":
            p.lineTo(num(), num())
        elif cmd == "Q":
            p.quadTo(num(), num(), num(), num())
        elif cmd == "C":
            p.cubicTo(num(), num(), num(), num(), num(), num())
    return p

def circle(cx, cy, r):
    p = skia.Path(); p.addCircle(cx, cy, r); return p

def oval(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)); return p

def rect(x, y, w, h, r=0):
    p = skia.Path()
    if r: p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    else: p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p

def path_len(p):
    m = skia.PathMeasure(p, False); L = 0.0
    while True:
        L += m.getLength()
        if not m.nextContour(): break
    return L

def partial(p, d):
    """Return (prefix path of length d, (x,y) of the tip)."""
    m = skia.PathMeasure(p, False); out = skia.Path(); acc = 0.0; tip = None
    while True:
        L = m.getLength()
        if L > 0:
            if acc + L <= d:
                m.getSegment(0, L, out, True); tip = m.getPosTan(L)[0]
            else:
                m.getSegment(0, d - acc, out, True); tip = m.getPosTan(d - acc)[0]
                return out, (tip.x(), tip.y())
            acc += L
        if not m.nextContour(): break
    return out, ((tip.x(), tip.y()) if tip else None)

def roughen(path, amp, seed, want_pts=False):
    """Hand-drawn marker line: dense resample + low-frequency wobble + loose (non-closed) ends."""
    rnd = random.Random(seed)
    out = skia.Path(); contours = []
    m = skia.PathMeasure(path, False)
    while True:
        L = m.getLength()
        if L > 1:
            pts = []
            ph1, ph2, ph3 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
            n = max(3, int(L / 9))
            for i in range(n + 1):
                d = L * i / n
                (pos, tan) = m.getPosTan(d)
                off = amp * (0.6 * math.sin(d / 120 + ph1) + 0.3 * math.sin(d / 55 + ph2) + 0.1 * math.sin(d / 23 + ph3))
                x, y = pos.x() - tan.y() * off, pos.y() + tan.x() * off
                if i == 0: out.moveTo(x, y)
                else: out.lineTo(x, y)
                pts.append((x, y))
            if not m.isClosed() and L > 40:   # a real hand rarely stops exactly on target
                (pos, tan) = m.getPosTan(L)
                over = rnd.uniform(3, 11); bend = rnd.uniform(-0.25, 0.25)
                for j in range(1, 4):
                    f = over * j / 3
                    x, y = pos.x() + (tan.x() - tan.y() * bend) * f, pos.y() + (tan.y() + tan.x() * bend) * f
                    out.lineTo(x, y); pts.append((x, y))
            if m.isClosed():   # marker overshoots a little past the start
                for i in range(1, 4):
                    (pos, tan) = m.getPosTan(min(L, 6.0 * i))
                    x, y = pos.x() + tan.y() * amp * 0.8, pos.y() - tan.x() * amp * 0.8
                    out.lineTo(x, y); pts.append((x, y))
            contours.append(pts)
        if not m.nextContour(): break
    return (out, contours) if want_pts else out

def _profile(pts, w, seed):
    """per-point widths: pressure taper at both ends + uneven ink."""
    rnd = random.Random(seed)
    ph1, ph2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    a = np.array(pts, dtype=float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(a, axis=0).T))] if len(a) > 1 else np.zeros(1)
    L = seg[-1] if len(seg) else 0
    taper = np.minimum(1, np.minimum(seg / 22.0, (L - seg) / 30.0)).clip(0, 1) ** 0.55
    noise = 1 + 0.2 * np.sin(seg / 80 + ph1) + 0.06 * np.sin(seg / 33 + ph2)
    return a, seg, w * (0.38 + 0.62 * taper) * noise

def _ribbon(a, widths):
    """variable-width outline polygon for a polyline."""
    if len(a) < 2: return None
    d = np.gradient(a, axis=0); n = np.hypot(d[:, 0], d[:, 1]); n[n == 0] = 1
    nx, ny = -d[:, 1] / n, d[:, 0] / n
    left = np.c_[a[:, 0] + nx * widths / 2, a[:, 1] + ny * widths / 2]
    right = np.c_[a[:, 0] - nx * widths / 2, a[:, 1] - ny * widths / 2][::-1]
    p = skia.Path(); p.moveTo(*left[0])
    for x, y in left[1:]: p.lineTo(x, y)
    for x, y in right: p.lineTo(x, y)
    p.close()
    p.setFillType(skia.PathFillType.kWinding)
    caps = skia.Path(); caps.addCircle(a[0, 0], a[0, 1], widths[0] / 2); caps.addCircle(a[-1, 0], a[-1, 1], widths[-1] / 2)
    return skia.Op(p, caps, skia.PathOp.kUnion_PathOp) or p

# ---------------- elements ----------------
_ZN = [0]
class El:
    """kind: stroke | fill | text.  zk = paint order (fills sit just under the outline drawn before them)."""
    def __init__(self, kind, path=None, color=K, width=6, text=None, x=0, y=0,
                 size=80, font="marker", align="center", weight=None):
        _ZN[0] += 1
        self.zk = _ZN[0] - (1.5 if kind == "fill" else 0)
        self.kind, self.path, self.color, self.width = kind, path, color, width
        self.text, self.x, self.y, self.size, self.font, self.align = text, x, y, size, font, align
        if kind == "image":
            self.length = 0
            return
        if kind == "text":
            f = skia.Font(TF[font], size)
            self.tw = f.measureText(text)
            self.x0 = x - self.tw / 2 if align == "center" else x
            self.length = self.tw * 1.4
        elif kind == "stroke":
            self.length = path_len(path)
        else:
            b = path.computeTightBounds()
            self.bounds = b
            self.zig = self._zigzag(b)
            self.zlen = path_len(self.zig)
            self.length = self.zlen * 0.3
        if weight is not None:
            self.length = weight

    def _zigzag(self, b, step=20):
        z = skia.Path()
        x0, x1 = b.left() - 10, b.right() + 10
        y = b.top() - 10; z.moveTo(x0, y); flip = False
        while y < b.bottom() + step:
            y += step
            z.lineTo(x0 if flip else x1, y); flip = not flip
        return z

    def transformed(self, m: skia.Matrix):
        e = El.__new__(El); e.__dict__.update(self.__dict__)
        if self.kind == "image":
            pt = m.mapXY(self.x, self.y); e.x, e.y = pt.x(), pt.y()
            e.scale = self.scale * math.hypot(m.getScaleX(), m.getSkewY()); return e
        if self.kind == "text":
            pt = m.mapXY(self.x, self.y); s = m.getScaleX()
            e = El("text", text=self.text, x=pt.x(), y=pt.y(), size=self.size * s, font=self.font,
                      align=self.align, color=self.color)
        else:
            p = skia.Path(self.path); p.transform(m)
            sc = math.hypot(m.getScaleX(), m.getSkewY())
            e = El("stroke", p, self.color, self.width * sc) if self.kind == "stroke" else El("fill", p, self.color)
        e.zk = self.zk
        return e

def IMG(img, x, y, scale=1.0, rot=0.0):
    """a printed object (newspaper clipping, photo...) that gets slapped onto the board"""
    e = El("image"); e.img, e.x, e.y, e.scale, e.rot = img, x, y, scale, rot; e.color = K
    return e

def S(d, w=6, c=K):  return El("stroke", P(d) if isinstance(d, str) else d, col(c) if isinstance(c, str) else c, w)
def F(d, c):         return El("fill", P(d) if isinstance(d, str) else d, col(c) if isinstance(c, str) else c)
def T(text, x, y, size=80, font="marker", c=K, align="center"):
    return El("text", text=text, x=x, y=y, size=size, font=font, color=col(c) if isinstance(c, str) else c, align=align)

_HF = {}
def _hfont(name="futural"):
    if name not in _HF:
        from HersheyFonts import HersheyFonts
        f = HersheyFonts(); f.load_default_font(name); f.normalize_rendering(100); _HF[name] = f
    return _HF[name]

def HT(text, x, y, size=80, c=K, align="center", font="futural", w=None, seed=0):
    """Hand-lettered text with single-stroke glyphs: the pen really writes every letter."""
    f = _hfont(font); rnd = random.Random(hash(text) % 9999 + seed)
    k = size / 100.0
    glyphs, cx = [], 0.0
    for ch in text:
        if ch == " ":
            cx += 38; continue
        st = list(f.strokes_for_text(ch))
        if not st:
            cx += 30; continue
        xs = [p[0] for s_ in st for p in s_]
        x0, x1 = min(xs), max(xs)
        glyphs.append((cx - x0, st)); cx += (x1 - x0) + 16
    total = cx - 16
    ox = x - total * k / 2 if align == "center" else x
    color = col(c) if isinstance(c, str) else c
    out = []
    for gx, st in glyphs:
        p = skia.Path()
        rot = math.radians(rnd.uniform(-3.5, 3.5)); sc = rnd.uniform(0.94, 1.06); dy = rnd.uniform(-3, 3)
        for s_ in st:
            for i, (px, py) in enumerate(s_):
                lx, ly = (px + gx) * k, -(py - 25) * k * sc
                cxg = (gx + 20) * k
                rx = cxg + (lx - cxg) * math.cos(rot) - ly * math.sin(rot)
                ry = (lx - cxg) * math.sin(rot) + ly * math.cos(rot)
                X, Y = ox + rx, y + ry + dy
                if i == 0: p.moveTo(X, Y)
                else: p.lineTo(X, Y)
        out.append(El("stroke", p, color, w or max(5, size * 0.12)))
    return out

def flat(els):
    out = []
    for e in els:
        if isinstance(e, (list, tuple)): out += flat(e)
        else: out.append(e)
    return out

def TW(text, x, y, size=80, font="marker", c=K, align="center"):
    """drop-in for T(): written by the pen with single-stroke letters."""
    k = 0.8 if font == "brush" else 1.0
    return HT(text, x, y, size * k, c, align)

def place(els, x=0, y=0, s=1.0, rot=0):
    els = flat(els)
    m = skia.Matrix(); m.setTranslate(x, y); m.preRotate(rot); m.preScale(s, s)
    return [e.transformed(m) for e in els]

def shape(d, fill, w=6):
    """Outline + color fill for the same path (fill appended later by caller ordering)."""
    p = P(d) if isinstance(d, str) else d
    return S(p, w), F(p, fill)

# ---------------- hand ----------------
def build_hand():
    """Cartoon right hand holding a black marker, seen from above; tip at (ox,oy)."""
    SW, SH = 1700, 1500
    s = skia.Surface(SW, SH); c = s.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    ox, oy = 40, 260
    c.translate(ox, oy)
    skin, skin2, line = col("#F3C9A6"), col("#E2AE88"), col("#8A5536")
    def fill(p, color): c.drawPath(p, skia.Paint(Color=color, AntiAlias=True))
    def edge(p, w=4):
        c.drawPath(p, skia.Paint(Color=line, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                                 StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))
    def blob(d, color=skin, w=4):
        p = P(d); fill(p, color); edge(p, w); return p
    # shadow
    sh = P("M60 -40 C150 -120 260 -60 330 20 L1640 1150 L1300 1460 L200 260 C120 190 40 80 60 -40 Z"); sh.offset(26, 30)
    c.drawPath(sh, skia.Paint(Color=skia.Color(0, 0, 0, 45), AntiAlias=True,
                              MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18)))
    # forearm + back of hand
    blob("M110 -30 C170 -110 270 -90 330 -20 C380 40 420 80 1640 1100 L1640 1460 L1240 1460 "
         "C700 900 300 360 220 280 C150 210 80 120 110 -30 Z")
    edge(P("M250 40 Q300 90 330 150"), 3)
    # marker (tip at 0,0, going up-right)
    fill(P("M-2 2 L10 -14 L30 -2 L16 12 Z"), col("#111111"))                   # felt tip
    fill(P("M12 -12 L150 -200 L196 -168 L32 2 Z"), col("#202020"))            # barrel
    fill(P("M24 -14 L150 -186 L164 -176 L36 -6 Z"), col("#5A5A5A"))           # shine
    fill(P("M150 -200 L176 -236 L222 -204 L196 -168 Z"), col("#D7262E"))      # red cap end
    # thumb (under/left of marker)
    blob("M40 30 C20 10 22 -20 46 -30 C76 -40 120 -20 160 10 C190 32 186 70 160 80 C120 90 70 64 40 30 Z")
    edge(P("M46 -14 Q56 -24 70 -20"), 3)
    # index finger over the marker
    blob("M58 -70 C66 -96 100 -112 130 -104 C170 -92 220 -60 240 -30 C252 -8 236 14 210 10 "
         "C170 4 120 -10 90 -26 C68 -38 52 -50 58 -70 Z")
    edge(P("M74 -84 Q84 -94 98 -92"), 3)
    edge(P("M150 -70 Q160 -56 158 -40"), 3)
    # middle finger tucked
    blob("M150 10 C170 -6 220 0 250 20 C270 36 262 66 236 70 C200 74 160 56 150 10 Z", skin2)
    img = s.makeImageSnapshot()
    return img, (ox, oy)

def load_hands():
    """marker hands (black / red, 4 poses each) + eraser hand; shadows are baked into the PNGs (pad 60px)."""
    import json
    PAD = 60
    def frames(d):
        fr = json.load(open(os.path.join(ASSETS, "hands", d, "frames.json")))
        return [(skia.Image.open(os.path.join(ASSETS, "hands", d, f"s{k}.png")), (fr[k]["tip"][0] + PAD, fr[k]["tip"][1] + PAD))
                for k in sorted(fr)]
    e = json.load(open(os.path.join(ASSETS, "hands", "eraser", "eraser.json")))["tip"]
    hb = os.path.exists(os.path.join(ASSETS, "hands", "blue"))
    return {"draw": frames("black"), "red": frames("red"), "blue": frames("blue" if hb else "red"),
            "eraser": [(skia.Image.open(os.path.join(ASSETS, "hands", "eraser", "s.png")), (e[0] + PAD, e[1] + PAD))]}

# ---------------- timeline ----------------
class Beat:
    def __init__(self, t, els, dur=None, speed=1.0):
        self.t, self.els, self.dur, self.speed = t, flat(els), dur, speed

class Scene:
    def __init__(self, t0, beats, zoom=0.05):
        self.t0, self.beats, self.zoom = t0, sorted(beats, key=lambda b: b.t), zoom
        self.t1 = None

CONTENT = 0.88          # drawings sit inside the decorated frame
_FRAME = []
ALL = []
REST = (W + 160, H + 260)
PAN = 1.4   # time used by the eraser hand at the start of each new scene

def _endpoints(e):
    if e.kind == "image":
        return (e.x, e.y), (e.x, e.y)
    if e.kind == "text":
        return (e.x0, e.y - e.size * 0.3), (e.x0 + e.tw, e.y - e.size * 0.3)
    p = e.zig if e.kind == "fill" else e.path
    L = e.zlen if e.kind == "fill" else e.length
    a = partial(p, 0.01)[1] or (0, 0); b = partial(p, L)[1] or a
    return a, b

def _wt(e):
    if e.kind == "stroke" and (e.width < 4.2 or e.length < 60): return e.length * 0.25
    return e.length

def schedule(scenes, total, speed=2400.0):
    """Time every element. Beats start on their keyword, but a crowded beat may start a little earlier
    (backward pass) so the hand never has to rush; nothing spills into the next scene."""
    global ALL
    ALL = []
    for i, sc in enumerate(scenes):
        sc.t1 = scenes[i + 1].t0 if i + 1 < len(scenes) else total
        sc.idx = i
        # --- prepare geometry + weights
        prev_pt = None
        for b in sc.beats:
            for e in b.els:
                if e.kind == "stroke" and not getattr(e, "_rough", False):
                    e.path, cts = roughen(e.path, 1.8 + e.width * 0.2, int(e.zk * 7) % 100000, True)
                    e.contours = [_profile(c_, e.width, int(e.zk * 13 + k)) for k, c_ in enumerate(cts)]
                    e.length = path_len(e.path); e._rough = True
            b.trav = []
            for e in b.els:
                a_, z_ = _endpoints(e)
                e.start_pt, e.end_pt = a_, z_
                dist = math.hypot(a_[0] - prev_pt[0], a_[1] - prev_pt[1]) if prev_pt else 0.0
                b.trav.append(dist * 0.55 if _wt(e) > 0 else 0.0)
                if _wt(e) > 0: prev_pt = z_
            b.L = (sum(_wt(e) for e in b.els) + sum(b.trav)) or 1
            b.need = b.L / speed
        # --- timing: backward (pull crowded beats earlier) then forward (keep order, respect the eraser)
        first = sc.t0 + ((PAN + 0.3) if i > 0 else 0)
        end_lim = sc.t1 - 0.15
        lim = end_lim; plan = [0] * len(sc.beats)
        for j in range(len(sc.beats) - 1, -1, -1):
            plan[j] = min(sc.beats[j].t, lim - sc.beats[j].need); lim = plan[j]
        S = []; cur = first
        for j, b_ in enumerate(sc.beats):
            st = max(cur, plan[j]); S.append(st); cur = st + b_.need
        if cur > end_lim:                                   # too much for this scene: squeeze evenly, never spill
            f = (end_lim - first) / max(1e-3, cur - first)
            S = [first + (x - first) * f for x in S]
        prev_pt = None
        for j, b in enumerate(sc.beats):
            nxt = S[j + 1] if j + 1 < len(S) else end_lim
            window = max(0.25, (nxt - S[j]) * (0.95 if j + 1 < len(S) else 1.0))
            window = min(window, max(0.25, end_lim - S[j]))
            if b.dur: window = b.dur
            b.win = window
            t = S[j]
            for e, tr in zip(b.els, b.trav):
                d = window * (_wt(e) + tr) / b.L
                travel = window * tr / b.L
                e.prev_pt = prev_pt if (prev_pt and d > 0 and tr > 0) else None
                if e.prev_pt is None: travel = 0
                if d > 0: prev_pt = e.end_pt
                e.t0, e.ts, e.t1 = t, t + travel, t + d
                e.scene = sc
                if d > 0: e.gidx = len(ALL); ALL.append(e)
                t += d

def ease(x): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, x)))

_wobble = None

def stroke_paint(e):
    return skia.Paint(Color=e.color, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=e.width,
                      StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)

def _chunks(c, a, wd, color, upto_idx=None):
    """variable-width line drawn as short overlapping round-capped chunks."""
    n = len(a) if upto_idx is None else upto_idx
    if n < 2: return
    step = 2
    for i in range(0, n - 1, step):
        j = min(n - 1, i + step)
        p = skia.Path(); p.moveTo(*a[i])
        for k in range(i + 1, j + 1): p.lineTo(*a[k])
        c.drawPath(p, skia.Paint(Color=color, AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                 StrokeWidth=float(wd[i:j + 1].mean()), StrokeCap=skia.Paint.kRound_Cap,
                                 StrokeJoin=skia.Paint.kRound_Join))

def draw_marker(c, path, e, upto=None):
    if not hasattr(e, "contours"):
        c.drawPath(path, stroke_paint(e)); return None
    color = e.color
    if getattr(e, "_sketch", None) is None:
        e._sketch = (e.length > 260 and e.width >= 6 and (int(e.zk * 17) % 5 == 0))
    if e._sketch:
        c.save(); c.translate(2.2, 1.6)
        for a, seg, wd in e.contours:
            n = len(a) if upto is None else max(2, int(np.searchsorted(seg, upto)))
            _chunks(c, a[:n], wd[:n] * 0.45, skia.ColorSetA(color, 110))
        c.restore()
    if upto is None:
        if getattr(e, "_pic", None) is None:
            rec = skia.PictureRecorder(); cc = rec.beginRecording(skia.Rect.MakeLTRB(-4000, -4000, 8000, 8000))
            for a, seg, wd in e.contours: _chunks(cc, a, wd, color)
            e._pic = rec.finishRecordingAsPicture()
        c.drawPicture(e._pic); return None
    acc = 0.0; tip = None
    for a, seg, wd in e.contours:
        L = seg[-1]
        if acc + L <= upto:
            _chunks(c, a, wd, color); tip = tuple(a[-1])
        else:
            k = max(2, int(np.searchsorted(seg, upto - acc)) + 1)
            _chunks(c, a, wd, color, k); tip = tuple(a[k - 1])
        acc += L
        if acc >= upto: break
    return tip

def marker_fill(c, e):
    """solid dark area coloured with a marker: dense jittery zigzag, tiny gaps of board showing."""
    if getattr(e, "_mf", None) is None:
        b = e.path.computeTightBounds(); rnd = random.Random(int(e.zk * 3))
        z = skia.Path(); x0, x1 = b.left() - 12, b.right() + 12; y = b.top() - 8; z.moveTo(x0, y); flip = False
        while y < b.bottom() + 12:
            y += rnd.uniform(6, 9)
            z.lineTo((x0 if flip else x1) + rnd.uniform(-10, 10), y + rnd.uniform(-3, 3)); flip = not flip
        e._mf = z
    c.drawPath(e.path, skia.Paint(Color=skia.Color(24, 24, 26), AntiAlias=True))
    c.save(); c.clipPath(e.path, doAntiAlias=True)
    c.drawPath(e._mf, skia.Paint(Color=skia.Color(52, 52, 56, 150), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                 StrokeWidth=3, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))
    c.restore()

SEQ = {"draw": [0, 1, 3, 0, 3, 1, 2], "red": [0, 2, 3, 0, 3, 2, 1], "blue": [0, 2, 3, 0, 3, 2, 1], "eraser": [0]}
def is_red(color):
    return skia.ColorGetR(color) > 150 and skia.ColorGetG(color) < 110 and skia.ColorGetB(color) < 110

def is_blue(color):
    return skia.ColorGetB(color) > 140 and skia.ColorGetR(color) < 110

def hand_of(e):
    kind = "draw" if e.kind == "fill" else ("red" if is_red(e.color) else ("blue" if is_blue(e.color) else "draw"))
    seq = SEQ[kind]
    return kind, seq[(getattr(e, "gidx", 0) // 3) % len(seq)]      # change grip only every few pen lifts

def is_dark(color):
    return skia.ColorGetR(color) + skia.ColorGetG(color) + skia.ColorGetB(color) < 160

def fill_streaks(c, e):
    if skia.ColorGetR(e.color) + skia.ColorGetG(e.color) + skia.ColorGetB(e.color) > 640: return
    c.save(); c.clipPath(e.path, doAntiAlias=True)
    c.drawPath(e.zig, skia.Paint(Color=skia.ColorSetA(skia.Color(0, 0, 0), 14), AntiAlias=True,
                                 Style=skia.Paint.kStroke_Style, StrokeWidth=18, StrokeCap=skia.Paint.kRound_Cap))
    c.restore()

def draw_scene(c, sc, t):
    """Draw scene state at time t; return hand tip or None."""
    tip = None
    els = sorted((e for b in sc.beats for e in b.els), key=lambda e: e.zk)
    for e in els:
        if t < e.t0: continue
        if e.kind == "image":
            if getattr(e, "pop", False):   # smooth pop: grows from 70% with a soft overshoot, settles its tilt
                u = min(1, (t - e.t0) / 0.55); c1 = 1.25
                back = 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2
                sc_ = e.scale * (0.7 + 0.3 * back); k = min(1, u / 0.22)
                rot = e.rot + 6 * (1 - ease(u))
            else:
                k = ease(min(1, (t - e.t0) / 0.45))
                sc_ = e.scale * (1.12 - 0.12 * k); rot = e.rot * k + 3 * (1 - k)
            c.save(); c.translate(e.x, e.y); c.rotate(rot); c.scale(sc_, sc_)
            c.drawImage(e.img, -e.img.width() / 2, -e.img.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), paint=skia.Paint(Alphaf=k))
            c.restore(); continue
        if t < e.ts:
            k = ease((t - e.t0) / max(1e-6, e.ts - e.t0))
            (ax, ay), (bx, by) = e.prev_pt, e.start_pt
            tip = (ax + (bx - ax) * k, ay + (by - ay) * k - 25 * math.sin(math.pi * k)) + hand_of(e)
            continue
        p = min(1, (t - e.ts) / max(1e-6, e.t1 - e.ts))
        p = 0.65 * p + 0.35 * ease(p)
        if e.kind == "fill":
            paint = skia.Paint(Color=e.color, AntiAlias=True)
            big = e.length > 0
            dark = is_dark(e.color)
            if p >= 1:
                if dark: marker_fill(c, e)
                else:
                    c.drawPath(e.path, paint)
                    if big: fill_streaks(c, e)
            else:
                c.saveLayer()
                if dark: marker_fill(c, e)
                else:
                    c.drawPath(e.path, paint)
                    if big: fill_streaks(c, e)
                seg, tp = partial(e.zig, e.zlen * p)
                c.drawPath(seg, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=30,
                                           StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                           BlendMode=skia.BlendMode.kDstIn, Color=WHITE))
                c.restore()
                if tp:
                    # follow the colouring with a calmer, averaged hand path
                    d0 = e.zlen * p
                    pa = partial(e.zig, max(0.01, d0 - 70))[1] or tp; pb = partial(e.zig, min(e.zlen, d0 + 70))[1] or tp
                    tip = ((pa[0] + tp[0] + pb[0]) / 3, (pa[1] + tp[1] + pb[1]) / 3) + hand_of(e)
        elif e.kind == "stroke":
            if p >= 1: draw_marker(c, e.path, e)
            else:
                tp = draw_marker(c, None, e, e.length * p)
                if tp is None: tp = partial(e.path, e.length * p)[1]
                if tp: tip = (tp[0], tp[1]) + hand_of(e)
        else:
            f = skia.Font(TF[e.font], e.size)
            paint = skia.Paint(Color=e.color, AntiAlias=True)
            if p >= 1:
                c.drawString(e.text, e.x0, e.y, f, paint)
            else:
                c.save()
                xr = e.x0 + e.tw * p
                c.clipRect(skia.Rect.MakeLTRB(e.x0 - 20, e.y - e.size * 1.3, xr, e.y + e.size * 0.5))
                c.drawString(e.text, e.x0, e.y, f, paint)
                c.restore()
                tip = (xr, e.y - e.size * 0.3 + 12 * math.sin(t * 40), "draw")
    return tip

_BOARD = []
def board():
    if not _BOARD:
        rng = np.random.default_rng(3)
        n = rng.normal(0, 1, (H // 4, W // 4))
        # wrap-around blur => tileable horizontally
        for _ in range(3):
            n = (n + np.roll(n, 1, 1) + np.roll(n, -1, 1) + np.roll(n, 1, 0) + np.roll(n, -1, 0)) / 5
        n = np.kron(n, np.ones((4, 4)))[:H, :W]
        base = 246 + n * 3.0
        img = np.dstack([base - 1, base, base + 1.5]).clip(0, 255).astype(np.uint8)
        rgba = np.dstack([img[:, :, 2], img[:, :, 1], img[:, :, 0], np.full((H, W), 255, np.uint8)])
        _BOARD.append(skia.Image.fromarray(rgba, colorType=skia.kBGRA_8888_ColorType))
        # light reflection, fixed to the camera
        s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.ColorTRANSPARENT)
        for x0, w, a in ((350, 260, 22), (720, 90, 14), (1500, 200, 12)):
            p = skia.Path(); p.moveTo(x0, 0); p.lineTo(x0 + w, 0); p.lineTo(x0 + w - 420, H); p.lineTo(x0 - 420, H); p.close()
            c.drawPath(p, skia.Paint(Color=skia.Color(255, 255, 255, a), AntiAlias=True,
                                     MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60)))
        vg = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.75, [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 12)])
        c.drawPaint(skia.Paint(Shader=vg))
        _BOARD.append(s.makeImageSnapshot())
    return _BOARD

def ghosts(c, seed):
    """faint leftovers of erased marker, different per board area"""
    rnd = random.Random(seed)
    pt = skia.Paint(Color=skia.Color(120, 120, 130, 9), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                    StrokeWidth=26, StrokeCap=skia.Paint.kRound_Cap)
    for _ in range(4):
        x, y = rnd.uniform(100, W - 300), rnd.uniform(100, H - 200)
        p = skia.Path(); p.moveTo(x, y)
        for k in range(3):
            p.quadTo(x + rnd.uniform(-160, 160), y + rnd.uniform(-90, 90), x + rnd.uniform(-220, 220), y + rnd.uniform(-120, 120))
        c.drawPath(p, pt)

def scene_bbox(sc):
    r = None
    for b in sc.beats:
        for e in b.els:
            if e.kind == "image":
                hw, hh = e.img.width() * e.scale / 2, e.img.height() * e.scale / 2
                bb = skia.Rect.MakeLTRB(e.x - hw, e.y - hh, e.x + hw, e.y + hh)
            elif e.kind == "text":
                bb = skia.Rect.MakeLTRB(e.x0, e.y - e.size, e.x0 + e.tw, e.y + e.size * 0.3)
            else:
                bb = e.path.computeTightBounds()
            r = bb if r is None else skia.Rect.MakeLTRB(min(r.left(), bb.left()), min(r.top(), bb.top()),
                                                         max(r.right(), bb.right()), max(r.bottom(), bb.bottom()))
    return r

ERASE_STYLES = ["rows_down", "circles", "columns", "diagonal", "rows_up", "spiral"]

def erase_path(sc):
    """A different human-like wiping pattern per scene: rows, circles, columns, diagonals, bottom-up, spiral."""
    if getattr(sc, "_ep", None) is None:
        b = scene_bbox(sc); z = (1 + sc.zoom) * CONTENT; rnd = random.Random(sc.idx * 31 + 7)
        x0 = max(-40, W / 2 + (b.left() - W / 2) * z - 40); x1 = min(W + 40, W / 2 + (b.right() - W / 2) * z + 40)
        y0 = max(20, H / 2 + (b.top() - H / 2) * z + 40); y1 = min(H + 40, H / 2 + (b.bottom() - H / 2) * z)
        # never the same style twice in a row
        order = ERASE_STYLES[:]; random.Random(99).shuffle(order)
        style = order[sc.idx % len(order)]
        sc._erase_style = style
        p = skia.Path()
        def wavy_rows(ys, left):
            xa = x0 + rnd.uniform(0, 60) if left else x1 - rnd.uniform(0, 60)
            p.moveTo(xa, ys[0])
            for i, y in enumerate(ys):
                xb = (x1 - rnd.uniform(0, 90)) if left else (x0 + rnd.uniform(0, 90)); tilt = rnd.uniform(-45, 45)
                p.cubicTo(xa + (xb - xa) * 0.33, y + rnd.uniform(-40, 40) + tilt, xa + (xb - xa) * 0.66,
                          y + rnd.uniform(-40, 40) - tilt, xb, y + rnd.uniform(-20, 20))
                if i + 1 < len(ys):
                    ny = ys[i + 1]; dx = 70 if left else -70
                    p.quadTo(xb + dx, (y + ny) / 2, xb, ny)
                xa = xb; left = not left
        def steps(a0, a1, lo=150, hi=220):
            v = [a0]
            while v[-1] < a1: v.append(min(a1, v[-1] + rnd.uniform(lo, hi)))
            return v
        if style in ("rows_down", "rows_up"):
            ys = steps(y0, y1)
            wavy_rows(ys if style == "rows_down" else ys[::-1], rnd.random() < 0.5)
        elif style == "columns":
            xs = steps(x0 + 60, x1 - 60, 170, 240); up = rnd.random() < 0.5
            ya = y1 if up else y0; p.moveTo(xs[0], ya)
            for i, x in enumerate(xs):
                yb = y0 if up else y1
                p.cubicTo(x + rnd.uniform(-45, 45), ya + (yb - ya) * 0.33, x + rnd.uniform(-45, 45), ya + (yb - ya) * 0.66,
                          x + rnd.uniform(-20, 20), yb)
                if i + 1 < len(xs):
                    nx = xs[i + 1]; p.quadTo((x + nx) / 2, yb + (-60 if up else 60), nx, yb)
                ya = yb; up = not up
        elif style == "circles":
            ys = steps(y0 + 40, y1, 190, 230); left = rnd.random() < 0.5; first = True
            for row, y in enumerate(ys):
                xs_ = (x0 + 60, x1 - 60) if left else (x1 - 60, x0 + 60)
                dist = abs(xs_[1] - xs_[0]); n = max(2, int(dist / 150)); r = rnd.uniform(95, 125)
                for k in range(n * 12 + 1):
                    u = k / (n * 12); ang = u * n * 2 * math.pi * (1 if left else -1)
                    x = xs_[0] + (xs_[1] - xs_[0]) * u + r * math.cos(ang + math.pi)
                    yy = y + r * 0.8 * math.sin(ang + math.pi)
                    if first: p.moveTo(x, yy); first = False
                    else: p.lineTo(x, yy)
                left = not left
        elif style == "diagonal":
            span = (x1 - x0) + (y1 - y0); k = 0.0; flip = False; first = True; last = None
            while k <= span:
                a_ = (x0 + min(k, x1 - x0), y0 + max(0, k - (x1 - x0)))
                b_ = (x0 + max(0, k - (y1 - y0)), y0 + min(k, y1 - y0))
                s0, s1 = (a_, b_) if not flip else (b_, a_)
                if first: p.moveTo(*s0); first = False
                else: p.quadTo((last[0] + s0[0]) / 2 + 40, (last[1] + s0[1]) / 2 + 40, *s0)
                mx, my = (s0[0] + s1[0]) / 2 + rnd.uniform(-30, 30), (s0[1] + s1[1]) / 2 + rnd.uniform(-30, 30)
                p.quadTo(mx, my, *s1); last = s1; k += rnd.uniform(170, 230); flip = not flip
        else:  # spiral: big loops from the outside in
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
            turns = max(2, int(min(rx, ry) / 150) + 1); N = turns * 40
            for k in range(N + 1):
                u = k / N; ang = u * turns * 2 * math.pi + rnd.uniform(-0.02, 0.02)
                f = 1.38 * (1 - u * 0.97)
                x, y = cx + rx * f * math.cos(ang), cy + ry * f * math.sin(ang)
                if k == 0: p.moveTo(x, y)
                else: p.lineTo(x, y)
        # quick scrub on a random spot (not every time)
        if rnd.random() < 0.6:
            cx, cy = rnd.uniform(x0 + 200, max(x0 + 201, x1 - 200)), rnd.uniform(y0 + 80, max(y0 + 81, y1 - 80))
            for k in range(2):
                p.quadTo(cx + 110, cy - 60, cx, cy - 10); p.quadTo(cx - 110, cy + 60, cx + 20, cy + 10)
        sc._ep = (p, path_len(p))
    return sc._ep

def _cam_pt(sc, pt, t):
    z = (1 + sc.zoom * ease((t - sc.t0) / max(0.1, sc.t1 - sc.t0))) * CONTENT
    return (W / 2 + (pt[0] - W / 2) * z, H / 2 + (pt[1] - H / 2) * z)

def _lerp(a, b, k, arc=0.0):
    k = ease(k)
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k - arc * math.sin(math.pi * k))

def idle_hand(t):
    """where the marker hand is when nothing is being drawn: glide between drawings, or leave / enter the board."""
    import bisect
    if not ALL: return None
    starts = getattr(idle_hand, "_s", None)
    if starts is None or len(starts) != len(ALL):
        ALL.sort(key=lambda e: e.t0); idle_hand._s = starts = [e.t0 for e in ALL]
    j = bisect.bisect_right(starts, t)
    prev = ALL[j - 1] if j > 0 else None
    nxt = ALL[j] if j < len(ALL) else None
    if prev and t < prev.t1: return None               # something is being drawn
    who = hand_of(nxt) if nxt else (hand_of(prev) if prev else ("draw", 0))
    r = _idle_xy(t, prev, nxt)
    return (r[0], r[1]) + who if r else None

def _idle_xy(t, prev, nxt):
    pA = _cam_pt(prev.scene, prev.end_pt, prev.t1) if prev else REST
    tA = prev.t1 if prev else -9
    pB = _cam_pt(nxt.scene, nxt.start_pt, nxt.t0) if nxt else REST
    tB = nxt.t0 if nxt else 1e9
    same = prev and nxt and prev.scene is nxt.scene
    if same and hand_of(prev)[0] != hand_of(nxt)[0] and tB - tA > 0.9:
        same = False                                  # swap markers: leave the board and come back with the other one
    if same and nxt.prev_pt is not None and tB - tA < 1.6:
        return pA                                   # pause; the next stroke's own travel moves the hand
    if same and tB - tA < 1.6:
        return _lerp(pA, pB, (t - tA) / max(1e-3, tB - tA), 40)
    enter = 0.55 if (same or not nxt or nxt.scene.idx == 0) else min(0.55, max(0.2, tB - (nxt.scene.t0 + PAN)))
    if tA + 0.55 > tB - enter and same:          # not enough time to leave and come back: glide across
        return _lerp(pA, pB, (t - tA) / max(1e-3, tB - tA), 60)
    if t - tA < 0.55: return _lerp(pA, REST, (t - tA) / 0.55)
    if tB - t < enter: return _lerp(REST, pB, 1 - (tB - t) / enter)
    return None

_ARM = None
def hand_angle(tip, t):
    """rotate the photo around the pen tip so the forearm always points to a shoulder below the board,
    plus a little living wobble -> the wrist seems to move."""
    kind = tip[2] if tip[2] in ("draw", "eraser") else "draw"
    sh = (W + 260, H + 760) if kind == "draw" else (W * 0.62, H + 900)
    def tgt(px, py): return math.degrees(math.atan2(sh[1] - py, sh[0] - px))
    rot = 0.65 * (tgt(tip[0], tip[1]) - tgt(W * 0.55, H * 0.5))
    rot += 2.2 * math.sin(t * 1.9) + 1.1 * math.sin(t * 5.3 + 1.0)
    return max(-28, min(28, rot))

def render_frame(c, scenes, t, hand):
    tex, light = board()
    idx = max([i for i, s in enumerate(scenes) if s.t0 <= t] or [0])
    sc = scenes[idx]
    dt = t - sc.t0
    c.drawImage(tex, 0, 0)
    def cam(s, tt):
        z = (1 + s.zoom * ease((tt - s.t0) / max(0.1, s.t1 - s.t0))) * CONTENT
        c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
        return z
    tip = None
    erasing = idx > 0 and dt < PAN
    if erasing:
        prev = scenes[idx - 1]
        ep, el = erase_path(prev)
        k = min(1, max(0, (dt - 0.15) / (PAN - 0.4)))
        c.saveLayer()
        c.save(); cam(prev, prev.t1); draw_scene(c, prev, prev.t1 + 99); c.restore()
        k = min(1, max(0, k + 0.035 * math.sin(k * math.pi * 6)))      # uneven speed, like a real arm
        seg, tp = partial(ep, max(0.01, el * k))
        c.drawPath(seg, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=290,
                                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                   BlendMode=skia.BlendMode.kDstOut, Color=skia.Color(0, 0, 0, 255)))
        c.restore()
        if tp:
            p0 = partial(ep, 0.01)[1]
            if dt < 0.15: tp = _lerp(REST, p0, dt / 0.15)
            elif dt > PAN - 0.25:
                pe = partial(ep, el)[1]; tp = _lerp(pe, REST, (dt - (PAN - 0.25)) / 0.25)
            tip = (tp[0], tp[1], "eraser", 0)
    else:
        c.save(); z = cam(sc, t); tp = draw_scene(c, sc, t); c.restore()
        if tp:
            tip = (W / 2 + (tp[0] - W / 2) * z, H / 2 + (tp[1] - H / 2) * z) + tuple(tp[2:])
        else:
            ih = idle_hand(t)
            if ih: tip = ih
    c.drawImage(light, 0, 0)
    if not _FRAME:
        import os
        fp = os.path.join(os.environ.get("INK_STORY", ""), "frame.png")      # per-story frame wins
        if not os.path.exists(fp): fp = os.path.join(ASSETS, "frame.png")
        _FRAME.append(skia.Image.open(fp) if os.path.exists(fp) else None)
    if _FRAME[0] is not None: c.drawImage(_FRAME[0], 0, 0)
    if tip and hand:
        h = hand[tip[2]]
        pose = tip[3] if len(tip) > 3 else 0
        img, (hx, hy) = h[pose % len(h)]
        c.save(); c.translate(tip[0], tip[1]); c.rotate(hand_angle(tip, t))
        c.drawImage(img, -hx, -hy)
        c.restore()
    return tip
