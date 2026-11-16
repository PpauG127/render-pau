"""Word-level timing for the current story (inkside/stories/<story>/parts.json).
parts[i] = list of (text, t0, t1) chunks of script line i (non-blank lines).
Chunks can be whole phrases (TTS) or single words (forced alignment of a real voice)."""
import json, os
STORY = os.environ["INK_STORY"]
parts = json.load(open(os.path.join(STORY, "parts.json")))

def line_end(i):
    return parts[i][-1][2]

def line_start(i):
    return parts[i][0][1]

def wt(i, word, nth=1, after=0.0):
    """time (s) when `word` (or phrase) starts being spoken in script line i."""
    text, spans = "", []
    for (p, t0, t1) in parts[i]:
        if text: text += " "
        spans.append((len(text), len(text) + len(p), t0, t1)); text += p
    low, w, seen, pos = text.lower(), word.lower(), 0, 0
    while True:
        j = low.find(w, pos)
        if j < 0: raise KeyError(f"'{word}' not in line {i}: {text}")
        seen += 1
        if seen == nth:
            for a, b, t0, t1 in spans:
                if a <= j < b + 1:
                    return max(t0 - 0.12, t0 + (t1 - t0) * (j - a) / max(1, b - a) - 0.12) + after
        pos = j + 1
