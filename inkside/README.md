# Inkside Stories (whiteboard horror channel)

Separate from the stickman project at the repo root. Nothing here triggers `render.yml`.

```
inkside/
  engine/      drawing engine (skia) + render.py, mix.py, overlap.py, preview.py
  assets/      hands (black, red, eraser), frame.png, fonts
  sfx/         manifest.json (Pixabay links) + fetch_sfx.py → sfx/cache/ (gitignored)
  stories/<slug>/  script.txt, voice.(wav|mp3), parts.json (word timings), scenes.py (drawings + CUES)
```

Workflow per video: story → script (EN) → user records voice → align words (parts.json) → scenes.py → render.

Local:  `python engine/render.py <slug> 0 10 /tmp/a.mp4` · `python engine/overlap.py <slug>` · `python sfx/fetch_sfx.py`
GitHub: Actions → **render-inkside** → Run workflow (story = slug). The video appears in Releases.

Sound files are Pixabay Content License: they are downloaded at render time, never committed.
