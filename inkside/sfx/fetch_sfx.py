"""Download every sound in manifest.json into sfx/<category>/<name>.mp3 (skips files already present).
Usage: python inkside/sfx/fetch_sfx.py"""
import json, os, urllib.request, sys
HERE = os.path.dirname(os.path.abspath(__file__))
man = json.load(open(os.path.join(HERE, "manifest.json")))["sounds"]
ok = bad = 0
for key, s in man.items():
    dst = os.path.join(HERE, s["path"]); os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000: ok += 1; continue
    req = urllib.request.Request(s["url"], headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
        "Referer": "https://pixabay.com/"})
    try:
        open(dst, "wb").write(urllib.request.urlopen(req, timeout=60).read()); ok += 1
    except Exception as e:
        bad += 1; print("FAILED", key, e, file=sys.stderr)
print(f"sfx: {ok} ok, {bad} failed")
