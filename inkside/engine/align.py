"""Align a recorded voice to script.txt -> parts.json  ([[word,t0,t1],...] per non-blank line).
usage: python align.py <story_dir>   (needs voice.wav; writes v16.raw, asr.json, parts.json)"""
import sys, os, json, re, subprocess, difflib
import numpy as np
from pocketsphinx import Decoder

d = sys.argv[1]
raw = os.path.join(d, "v16.raw")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(d, "voice.wav"), "-ac", "1", "-ar", "16000", "-f", "s16le", raw], check=True)
a = np.fromfile(raw, np.int16)
SR = 16000

# cut at quiet points roughly every 18 s
win = SR // 50
en = np.sqrt(np.convolve(a.astype(np.float32) ** 2, np.ones(win) / win, "same"))
cuts, pos = [0], 0
while pos + 22 * SR < len(a):
    lo, hi = pos + 14 * SR, pos + 22 * SR
    c = lo + int(np.argmin(en[lo:hi]))
    cuts.append(c); pos = c
cuts.append(len(a))

asr = []
if os.path.exists(os.path.join(d, "asr.json")):
    asr = json.load(open(os.path.join(d, "asr.json")))
else:
    dec = Decoder()
    fr = dec.config["frate"] if "frate" in dec.config else 100
    for s, e in zip(cuts, cuts[1:]):
        dec.start_utt(); dec.process_raw(a[s:e].tobytes(), full_utt=True); dec.end_utt()
        for sg in dec.seg():
            w = re.sub(r"\(\d+\)$", "", sg.word)
            if w.startswith("<") or w.startswith("[") or w == "<sil>": continue
            asr.append([w.lower(), s / SR + sg.start_frame / fr, s / SR + (sg.end_frame + 1) / fr])
    json.dump(asr, open(os.path.join(d, "asr.json"), "w"))

lines = [l.strip() for l in open(os.path.join(d, "script.txt")) if l.strip()]
toks = []  # (line, word)
for i, l in enumerate(lines):
    for w in l.split(): toks.append((i, w))
norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))
A = [norm(w) for _, w in toks]
B = [w for w, _, _ in asr]
T = [None] * len(toks)
for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
    for k in range(blk.size):
        T[blk.a + k] = asr[blk.b + k][1:]
hit = sum(t is not None for t in T)
# interpolate gaps by character length
total = len(a) / SR
i = 0
while i < len(T):
    if T[i] is None:
        j = i
        while j < len(T) and T[j] is None: j += 1
        t0 = T[i - 1][1] if i else 0.0
        t1 = T[j][0] if j < len(T) else total
        L = [len(toks[k][1]) + 1 for k in range(i, j)]
        tot = sum(L); c = t0
        for k, l in zip(range(i, j), L):
            dt = (t1 - t0) * l / tot
            T[k] = [c, c + dt]; c += dt
        i = j
    else:
        i += 1
parts = [[] for _ in lines]
for (li, w), t in zip(toks, T):
    parts[li].append([w, round(t[0], 3), round(t[1], 3)])
json.dump(parts, open(os.path.join(d, "parts.json"), "w"))
print(f"matched {hit}/{len(toks)} = {100*hit/len(toks):.0f}%  lines {len(lines)}  end {parts[-1][-1][2]:.1f}s / {total:.1f}s")
