"""Word-level timing for the current story (inkside/stories/<story>/parts.json).
parts[i] = list of (text, t0, t1) chunks of script line i (non-blank lines)."""
import json, os
STORY = os.environ["INK_STORY"]
parts = json.load(open(os.path.join(STORY, "parts.json")))

def wt(i, word, nth=1, after=0.0):
    """time (s) when `word` is spoken in script line i."""
    w = word.lower(); seen = 0
    for (p, t0, t1) in parts[i]:
        low = p.lower(); pos = 0
        while True:
            j = low.find(w, pos)
            if j < 0: break
            seen += 1
            if seen == nth:
                return max(t0, t0 + (t1 - t0) * j / max(1, len(p)) - 0.15) + after
            pos = j + 1
    raise KeyError(f"'{word}' not in line {i}")
