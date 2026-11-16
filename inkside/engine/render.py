import sys, subprocess, time, os
import story
scenes, STORY = story.load(sys.argv[1])
from scenes import *
a, b, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
sc = build(); hand = load_hands()
surf = skia.Surface(W, H); c = surf.getCanvas()
ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                       "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",out], stdin=subprocess.PIPE)
f0, f1 = int(a*FPS), int(b*FPS); t0=time.time()
import math
prev=None; big=[]
for f in range(f0, f1):
    tip = render_frame(c, sc, f / FPS, hand)
    if tip and prev and tip[2] == prev[2]:
        d = math.hypot(tip[0]-prev[0], tip[1]-prev[1])
        if d > 60: big.append((round(f/FPS,2), int(d)))
    prev = tip
    ff.stdin.write(surf.makeImageSnapshot().tobytes())
print("frames with hand step >60px:", len(big), sorted(big, key=lambda x:-x[1])[:8])
ff.stdin.close(); ff.wait(); print(out, f1-f0, "frames", round(time.time()-t0,1), "s")
