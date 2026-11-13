"""Render-side story pipeline: shot cuts, reactions, kinetic keywords, danger pulse, captions, progress bar."""
from stick import *
import storyplan as SP

def word_times(text, t0, t1):
    words = text.split(); wts = [len(w.strip('.,?!')) + 2.5 for w in words]; tot = sum(wts); out = []; acc = t0
    for w, v in zip(words, wts):
        out.append((w, acc)); acc += (t1 - t0) * v / tot
    return out

def install(TEMPLATES, hud, total, close_tpl='close', cap_y=None, cap_size=74):
    cap_y = cap_y or (930 if LANDSCAPE else 830)
    def SCENE(ctx, t, d, Q):
        tpl = Q['tpl']
        wt = word_times(Q['text'], 0.3, d - 0.15)
        key = next(((w, tw) for w, tw in wt if w.strip('.,?!').lower() in SP.DANGER | SP.GOOD or any(c.isdigit() for c in w)), None)
        shake = 1 - (t - key[1]) / 0.35 if key and 0 <= t - key[1] < 0.35 else 0.0
        cut = d * 0.52 if Q.get('cut') and d >= 2.2 else None
        after = cut is not None and t >= cut
        punch = max(0.0, 1 - (t - cut) / 0.2) if after else 0.0
        ctx.save(); z = 1 + 0.07 * punch
        ctx.translate(W / 2 + 14 * shake * math.sin(t * 90), H / 2 + 10 * shake * math.cos(t * 77)); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2)
        if after and Q['react']:
            TEMPLATES[close_tpl](ctx, t, d, dict(Q, fear=max(Q.get('fear', 0), 0.8), mouth='o'), snap=t - cut)
        elif after:
            TEMPLATES[tpl](ctx, t, d, dict(Q, shot=Q['shotB']))
        else:
            TEMPLATES[tpl](ctx, t, d, Q)
        ctx.restore()
        if punch > 0: rgba(ctx, (1, 1, 1), 0.22 * punch); ctx.paint()
        if Q['danger']:
            pulse = 0.5 + 0.5 * math.sin(t * 6)
            v = cairo.RadialGradient(W / 2, H / 2, 0.2 * max(W, H), W / 2, H / 2, 0.6 * max(W, H))
            v.add_color_stop_rgba(0, 0.8, 0, 0, 0); v.add_color_stop_rgba(1, 0.8, 0.02, 0.05, 0.35 + 0.2 * pulse)
            ctx.set_source(v); ctx.paint()
        if key and t >= key[1] and tpl not in ('choice', 'fact', 'title'):
            k = clamp((t - key[1]) / 0.18); word = key[0].strip('.,?!').upper()
            ctx.save(); ctx.translate(W / 2, 250 if LANDSCAPE else 620); ctx.rotate(-0.05 + 0.02 * math.sin(t * 5))
            sc = 0.4 + 0.6 * eback(k); ctx.scale(sc, sc)
            label(ctx, word, 0, 0, 150, ACC if word.lower() in SP.DANGER else AMB, min(1.0, k * 2) * (1 - clamp((t - key[1] - 1.6) / 0.3)))
            ctx.restore()
        hud(ctx, t, Q)
        caption(ctx, t, Q['text'], 0.3, d - 0.15, y=cap_y, size=cap_size, chunk=4)
        pr = (Q['start'] + t) / total
        ctx.rectangle(0, H - 10, W, 10); rgba(ctx, (1, 1, 1), 0.15); ctx.fill()
        ctx.rectangle(0, H - 10, W * pr, 10); rgba(ctx, ACC); ctx.fill()
    SP.DISPATCH[0] = SCENE
