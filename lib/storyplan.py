"""Pure-python story planner (no cairo): BEATS -> SCENES with automatic short shots."""
import re
DISPATCH = [None]
DANGER = set(); GOOD = set()

def split_text(txt, maxw=7):
    out = []
    for s in re.findall(r'[^.?!]+[.?!]*', txt):
        w = s.split()
        if not w: continue
        if len(w) <= maxw: out.append(' '.join(w)); continue
        buf = []
        for p_ in re.split(r'(?<=,)\s+', s.strip()):
            pw = p_.split()
            if buf and len(buf) + len(pw) > maxw:
                out.append(' '.join(buf)); buf = []
            buf += pw
            while len(buf) > maxw + 1:
                out.append(' '.join(buf[:maxw])); buf = buf[maxw:]
        if buf: out.append(' '.join(buf))
    return out

def build(BEATS, wps=2.25, state=None, cut_tpls=('land', 'gas', 'close'), react_tpls=('land', 'gas')):
    scenes = []; state = dict(state or {})
    for bi, (tpl, P, txt) in enumerate(BEATS):
        for k, v in P.items():
            if k in state: state[k] = v
        chunks = split_text(txt); boff = 0.0
        for ci, ch in enumerate(chunks):
            n = len(ch.split()); dur = max(2.0, n / wps + 0.45)
            if tpl == 'choice' and ci == len(chunks) - 1 and not P.get('cta'): dur += 3.0
            if tpl == 'title': dur = max(dur, 2.4)
            Q = dict(P); Q.update(state)
            words = [w.strip('.,?!').lower() for w in ch.split()]
            Q.update(ci=ci, boff=boff, text=ch, tpl=tpl, start=sum(x[0] for x in scenes))
            Q['shot'] = P.get('shot') or ['wide', 'close', 'low', 'mid', 'dutch'][(bi + ci) % 5]
            Q['shotB'] = ['close', 'dutch', 'wide', 'low', 'mid'][(bi + ci + 2) % 5]
            if Q['shotB'] == Q['shot']: Q['shotB'] = 'wide' if Q['shot'] == 'close' else 'close'
            Q['danger'] = any(w in DANGER for w in words) or P.get('fear', 0) >= 0.8
            Q['react'] = tpl in react_tpls and (Q['danger'] or 'emote' in P) and ci % 2 == 0
            Q['cut'] = tpl in cut_tpls
            if 'emote' not in P: Q['emote'] = '!' if Q['danger'] else ('?' if '?' in ch else None)
            fn = lambda ctx, t, d, Q=Q: DISPATCH[0](ctx, t, d, Q)
            style = [0, 1, 2, 3][bi % 4] if ci == 0 else 'dissolve'
            scenes.append((dur, "", set(), (1, 1, 1), fn, 0, style)); boff += dur
    return scenes
