"""Build the soundtrack and mux it with the rendered video.
Usage: python inkside/engine/mix.py <story> <video_noaudio.mp4> <out.mp4>

Layers: voice  +  real marker sound while the hand draws  +  eraser on scene changes
        +  quiet music / ambience bed (ducked under the voice)  +  story cues (scenes.CUES).
Sound files come from inkside/sfx/cache (downloaded by sfx/fetch_sfx.py). Missing files are skipped."""
import os, sys, subprocess, random
import numpy as np
import story

SR = 44100
scenes, STORY = story.load(sys.argv[1])
import engine
VID, OUT = sys.argv[2], sys.argv[3]
SFX = os.path.join(engine.ROOT, "sfx")
import json
_MAN = json.load(open(os.path.join(SFX, "manifest.json")))["sounds"]

def load(path, mono=True):
    if not path or not os.path.exists(path): return None
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

def sfx(key): return load(os.path.join(SFX, _MAN[key]["path"])) if key in _MAN else None

def fade(x, a=0.03, b=0.08):
    x = x.copy(); na, nb = min(len(x), int(a * SR)), min(len(x), int(b * SR))
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x

def put(track, clip, t, gain):
    if clip is None: return
    i = int(t * SR)
    if i >= len(track): return
    n = min(len(clip), len(track) - i)
    track[i:i + n] += clip[:n] * gain

def norm(x):
    p = np.percentile(np.abs(x), 99.5) if len(x) else 1
    return x / max(p, 1e-4)

sc = scenes.build()
total = scenes.TOTAL
N = int(getattr(scenes, "AUDIO_TOTAL", total) * SR) + SR
mix = np.zeros(N, np.float32)

# --- voice
vpath = next((os.path.join(STORY, f) for f in ("voice.wav", "voice.mp3") if os.path.exists(os.path.join(STORY, f))), None)
voice = load(vpath)
if voice is not None:
    voice = norm(voice) * 0.9
    put(mix, voice, 0, 1.0)
    env = np.convolve(np.abs(np.pad(voice, (0, max(0, N - len(voice))))[:N]), np.ones(SR // 5) / (SR // 5), "same")
    duck = 1 - 0.6 * np.clip(env / (env.max() + 1e-6) * 3, 0, 1)
else:
    duck = np.ones(N, np.float32)

rnd = random.Random(7)
# --- marker: short real snippets while the pen touches the board
marks = [m for m in (sfx("marker_1"), sfx("marker_2")) if m is not None]
if marks:
    marks = [norm(m) for m in marks]
    for e in engine.ALL:
        if e.kind == "image": continue
        d = e.t1 - e.ts
        if d < 0.05: continue
        src = rnd.choice(marks); L = int(d * SR)
        if L >= len(src): L = len(src) - 1
        s0 = rnd.randint(0, max(0, len(src) - L - 1))
        put(mix, fade(src[s0:s0 + L], 0.02, 0.04), e.ts, getattr(scenes, "MARKER_GAIN", 0.11))
# --- eraser on every scene change
er = sfx("eraser_1")
if er is not None:
    er = norm(er)
    for s in sc[1:]:
        L = int(engine.PAN * SR); s0 = rnd.randint(0, max(0, len(er) - L - 1))
        put(mix, fade(er[s0:s0 + L], 0.08, 0.25), s.t0, getattr(scenes, "ERASER_GAIN", 0.22))

# --- music + ambience bed, looped, ducked under the voice
def bed(key, gain):
    x = sfx(key)
    if x is None: return
    x = norm(x); out = np.zeros(N, np.float32); i = 0; xf = int(2 * SR)
    while i < N:
        seg = x[:min(len(x), N - i)].copy()
        if i > 0:   # crossfade loops
            k = min(xf, len(seg)); seg[:k] *= np.linspace(0, 1, k); out[i:i + k] *= np.linspace(1, 0, k)
        out[i:i + len(seg)] += seg; i += max(1, len(x) - xf)
    out[: 2 * SR] *= np.linspace(0, 1, 2 * SR); out[-3 * SR:] *= np.linspace(1, 0, 3 * SR)
    mix[:] += out * duck * gain
bed(getattr(scenes, "MUSIC", "music_2"), getattr(scenes, "MUSIC_GAIN", 0.10))
if getattr(scenes, "AMBIENCE", None): bed(scenes.AMBIENCE, getattr(scenes, "AMBIENCE_GAIN", 0.05))

# --- story cues: (time, sound key, gain, max seconds)
for t, key, gain, mx in (scenes.CUES() if callable(getattr(scenes, "CUES", None)) else []):
    x = sfx(key)
    if x is None: continue
    x = norm(x)[: int(mx * SR)]
    put(mix, fade(x, 0.02, min(0.6, mx / 3)), t, gain)

mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.98), -1, 1)
wav = OUT + ".wav"
import wave
w = wave.open(wav, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", VID, "-i", wav, "-filter_complex", "[1:a]loudnorm=I=-15:TP=-1.5[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-shortest", OUT],
               check=True)
os.remove(wav)
print("mixed ->", OUT, "| sfx found:", sum(os.path.exists(os.path.join(SFX, v["path"])) for v in _MAN.values()))
