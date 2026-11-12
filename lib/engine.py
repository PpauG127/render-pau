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
    def render_frame(idx, t, T):
        dur, text, hl, hlc, fn = SCENES[idx][:5]
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        draw_bg(ctx, T)
        env = min(prog(t, 0, 0.16), 1 - prog(t, dur - 0.14, dur))
        if idx == len(SCENES) - 1:
            env = min(prog(t, 0, 0.16), 1 - prog(t, dur - 0.5, dur))
        ctx.push_group()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        fn(ctx, t, dur)
        yc = SCENES[idx][5] if len(SCENES[idx]) > 5 else 400
        draw_headline(ctx, t, text, hl, hlc, ycenter=yc)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(env)
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
