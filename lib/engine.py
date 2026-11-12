"""Shared renderer for the channel's Shorts."""
import cairo, math, random, subprocess, sys, os
from base import (W, H, FPS, CX, CYAN, ORANGE, YELLOW, WHITE, RED, NAVY, FONT, clamp, prog, eo, eio, eback,
                  rgba, glow_stroke, glow_dot, dashed_line, poly_partial, point_at, draw_poly, draw_bg)
from render2 import label, rr, arrow_head, lin, draw_headline, BOLD, NORM, GREEN

BLUE = (0.3, 0.55, 1.0)
MAGRED = (0.95, 0.25, 0.3)
MAGBLUE = (0.2, 0.45, 1.0)
STEEL = [(0, (0.45, 0.48, 0.53)), (0.3, (0.88, 0.9, 0.94)), (0.55, (0.6, 0.63, 0.68)), (0.8, (0.82, 0.85, 0.9)), (1, (0.4, 0.43, 0.48))]
COPPER = [(0, (0.55, 0.25, 0.08)), (0.4, (0.98, 0.62, 0.32)), (0.7, (0.78, 0.4, 0.15)), (1, (0.45, 0.2, 0.06))]
BRASS = [(0, (0.6, 0.45, 0.12)), (0.4, (1.0, 0.85, 0.45)), (0.7, (0.8, 0.62, 0.22)), (1, (0.5, 0.36, 0.08))]
DARK = [(0, (0.14, 0.15, 0.18)), (0.4, (0.34, 0.36, 0.4)), (1, (0.08, 0.08, 0.1))]

def fill_grad(ctx, stops, x0, y0, x1, y1, a=1.0):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops:
        g.add_color_stop_rgba(o, c[0], c[1], c[2], a)
    ctx.set_source(g)

def metal_rect(ctx, x, y, w, h, stops=STEEL, vertical=True, r=0, a=1.0, outline=True):
    if r: rr(ctx, x, y, w, h, r)
    else: ctx.rectangle(x, y, w, h)
    if vertical: fill_grad(ctx, stops, x, y, x, y + h, a)
    else: fill_grad(ctx, stops, x, y, x + w, y, a)
    ctx.fill_preserve() if outline else ctx.fill()
    if outline:
        rgba(ctx, (0.05, 0.06, 0.08), 0.8 * a); ctx.set_line_width(2.5); ctx.stroke()

def flow_dots(ctx, path, t, n, speed, c, r=6, a=1.0, phase=0.0):
    for k in range(n):
        q = (t * speed + k / n + phase) % 1.0
        x, y = point_at(path, q)
        glow_dot(ctx, x, y, r, c, a * min(1, q * 6, (1 - q) * 6))

def spark(ctx, x, y, s, t, a=1.0):
    rnd = random.Random(int(t * 30))
    for k in range(10):
        ang = rnd.uniform(0, 6.283); L = rnd.uniform(20, 60) * s
        ctx.move_to(x, y); ctx.line_to(x + L * math.cos(ang), y + L * math.sin(ang))
    rgba(ctx, (0.75, 0.9, 1.0), a); ctx.set_line_width(3); ctx.stroke()
    glow_dot(ctx, x, y, 14 * s, (0.8, 0.95, 1.0), a)

_JOB = None
def _job(i):
    _JOB(i)

def run(SCENES, headline_y=None):
    XT = 0.65   # transition length (s): scene i blends from scene i-1 during its first XT seconds

    def layer(idx, t, T):
        dur, text, hl, hlc, fn = SCENES[idx][:5]
        L = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(L)
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        # slow camera push + drift: the picture never stands still
        k = clamp(t / dur)
        z = 1.0 + 0.045 * eio(k)
        c.translate(CX + 10 * math.sin(T * 0.45), 1150 + 8 * math.sin(T * 0.37 + 1))
        c.scale(z, z); c.rotate(0.006 * math.sin(T * 0.3))
        c.translate(-CX, -1150)
        c.push_group()
        fn(c, t, dur)
        c.pop_group_to_source(); c.paint()
        c.identity_matrix()
        yc = SCENES[idx][5] if len(SCENES[idx]) > 5 else 400
        draw_headline(c, t - (0.32 if idx > 0 else 0.0), text, hl, hlc, ycenter=yc)
        return L

    def paint_layer(ctx, L, a=1.0, sc=1.0, dx=0.0, dy=0.0, blur=0, clip_r=None):
        if a <= 0.003: return
        ctx.save()
        if clip_r is not None:
            ctx.arc(CX, 1150, max(1, clip_r), 0, 6.2832); ctx.clip()
        ctx.translate(CX + dx, 1150 + dy); ctx.scale(sc, sc); ctx.translate(-CX, -1150)
        if blur:
            n = 4
            for i in range(n):
                ctx.set_source_surface(L, blur * (i - (n - 1) / 2) / n, 0); ctx.paint_with_alpha(a / n * 1.15)
        else:
            ctx.set_source_surface(L, 0, 0); ctx.paint_with_alpha(a)
        ctx.restore()

    def small_copy(src, f):
        sm = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // f, H // f)
        c = cairo.Context(sm); c.scale(1 / f, 1 / f); c.set_source_surface(src, 0, 0)
        c.get_source().set_filter(cairo.FILTER_GOOD); c.paint()
        return sm

    def paint_small(ctx, sm, f, a, dx=0, dy=0, op=None, color=None):
        ctx.save(); ctx.translate(dx, dy); ctx.scale(f, f)
        if op is not None: ctx.set_operator(op)
        pat = cairo.SurfacePattern(sm); pat.set_filter(cairo.FILTER_BILINEAR)
        if color is not None:
            ctx.set_source_rgba(color[0], color[1], color[2], a); ctx.mask(pat)
        else:
            ctx.set_source(pat); ctx.paint_with_alpha(a)
        ctx.restore()

    NEB = [(200, 500, 520, (0.1, 0.5, 0.9), 0.13, 0.11), (900, 1300, 620, (0.45, 0.2, 0.8), 0.10, 0.07),
           (350, 1700, 480, (0.0, 0.7, 0.8), 0.08, 0.09), (850, 300, 400, (0.9, 0.45, 0.1), 0.05, 0.13)]
    BOKEH = [(random.Random(i).uniform(0, W), random.Random(i + 50).uniform(0, H), random.Random(i + 99).uniform(14, 40),
              random.Random(i + 7).uniform(8, 25)) for i in range(14)]

    def render_frame(idx, t, T):
        dur = SCENES[idx][0]
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        draw_bg(ctx, T)
        for (x, y, r, c, al, sp) in NEB:   # slow drifting nebula light
            xx = x + 120 * math.sin(T * sp); yy = y + 90 * math.cos(T * sp * 1.3)
            g = cairo.RadialGradient(xx, yy, 0, xx, yy, r)
            g.add_color_stop_rgba(0, c[0], c[1], c[2], al); g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
            ctx.set_source(g); ctx.paint()
        # ---- foreground (scene layers + transitions)
        fg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        fc = cairo.Context(fg)
        cur = layer(idx, t, T)
        if idx > 0 and t < XT:
            p = eio(t / XT)
            pdur = SCENES[idx - 1][0]
            prev = layer(idx - 1, pdur + t, T)
            style = idx % 4
            if style == 0:      # zoom through
                paint_layer(fc, prev, (1 - p) ** 2, 1 + 0.35 * p)
                paint_layer(fc, cur, p, 0.82 + 0.18 * p)
            elif style == 1:    # vertical slide with motion blur
                paint_layer(fc, prev, (1 - p) ** 2, 1, 0, -700 * p)
                paint_layer(fc, cur, min(1, p * 1.6), 1, 0, 700 * (1 - p))
            elif style == 2:    # whip pan
                bl = 140 * math.sin(p * math.pi)
                paint_layer(fc, prev, (1 - p) ** 2, 1, -900 * p, 0, blur=bl)
                paint_layer(fc, cur, p, 1, 900 * (1 - p), 0, blur=bl)
            else:               # circular reveal
                paint_layer(fc, prev, (1 - p) ** 1.5, 1 + 0.08 * p)
                paint_layer(fc, cur, 1, 1.06 - 0.06 * p, clip_r=1250 * p)
                fc.arc(CX, 1150, 1250 * p, 0, 6.2832); rgba(fc, CYAN, 0.8 * (1 - p)); fc.set_line_width(10); fc.stroke()
        else:
            paint_layer(fc, cur)
        # ---- realism pass: soft contact shadow, the layer, bloom
        sm = small_copy(fg, 8)
        paint_small(ctx, sm, 8, 0.6, 0, 28, color=(0, 0, 0.02))
        ctx.set_source_surface(fg, 0, 0); ctx.paint()
        sb = small_copy(fg, 6)
        paint_small(ctx, sb, 6, 0.33, op=cairo.OPERATOR_ADD)
        # foreground bokeh dust (depth)
        for (x, y, r, sp) in BOKEH:
            yy = (y - T * sp) % (H + 200) - 100; xx = x + 30 * math.sin(T * 0.3 + y)
            g = cairo.RadialGradient(xx, yy, 0, xx, yy, r)
            g.add_color_stop_rgba(0, 0.7, 0.9, 1, 0.10); g.add_color_stop_rgba(1, 0.7, 0.9, 1, 0)
            ctx.set_source(g); ctx.arc(xx, yy, r, 0, 6.2832); ctx.fill()
        # vignette
        v = cairo.RadialGradient(CX, 1000, 500, CX, 1000, 1250)
        v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0.02, 0.55)
        ctx.set_source(v); ctx.paint()
        # only the very start and the very end fade (no hard cuts anywhere)
        f = 1.0
        if idx == 0: f = min(f, prog(t, 0, 0.25))
        if idx == len(SCENES) - 1: f = min(f, 1 - prog(t, dur - 0.5, dur))
        if f < 1:
            ctx.set_source_rgba(0.01, 0.02, 0.06, 1 - f); ctx.paint()
        return surf

    def start(idx): return sum(s[0] for s in SCENES[:idx])

    def render_scene(idx, outdir):
        dur = SCENES[idx][0]; n = int(round(dur * FPS))
        tmp = os.path.join(outdir, f"tmp_{idx:02d}.mp4"); final = os.path.join(outdir, f"scene_{idx:02d}.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                              "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        T0 = start(idx)
        for f in range(n):
            t = f / FPS
            p.stdin.write(bytes(render_frame(idx, t, T0 + t).get_data()))
        p.stdin.close()
        if p.wait() == 0: os.replace(tmp, final)

    mode = sys.argv[1]
    if mode == "still":
        idx = int(sys.argv[2]); t = float(sys.argv[3])
        render_frame(idx, t, start(idx) + t).write_to_png(sys.argv[4])
    elif mode == "sheet":
        from PIL import Image
        out = sys.argv[2]
        ims = []
        for i, s in enumerate(SCENES):
            tt = s[0] * 0.8
            render_frame(i, tt, start(i) + tt).write_to_png("/tmp/_f.png")
            ims.append(Image.open("/tmp/_f.png").convert("RGB").resize((405, 720)))
        cols = 5; rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (405 * cols, 720 * rows))
        for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 405, (i // cols) * 720))
        sh.save(out)
    elif mode == "scenes":
        os.makedirs(sys.argv[2], exist_ok=True)
        for i in map(int, sys.argv[3:]): render_scene(i, sys.argv[2])
    elif mode == "all":
        import multiprocessing as mp
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        global _JOB
        _JOB = lambda i: render_scene(i, out)
        order = sorted(range(len(SCENES)), key=lambda i: -SCENES[i][0])   # longest first
        with mp.get_context("fork").Pool(os.cpu_count()) as pool:
            pool.map(_job, order, chunksize=1)
    elif mode == "count":
        print(len(SCENES), sum(s[0] for s in SCENES))
