"""report drawings in the same scene that collide (object level: each beat is one object)"""
import sys, story
scenes, STORY = story.load(sys.argv[1] if len(sys.argv) > 1 else 'slenderman')
from scenes import *
ALLOW = {(2, 0), (1, 3), (10, 0)}   # photo frame, monitor screen, Payton under the leaves            # scene 2 beat 0 is the photo frame: things inside it are fine
def bb(els):
    r=None
    for e in els:
        if e.kind=="text": b=skia.Rect.MakeLTRB(e.x0,e.y-e.size,e.x0+e.tw,e.y+e.size*0.3)
        elif e.kind=="image":
            hw,hh=e.img.width()*e.scale/2,e.img.height()*e.scale/2; b=skia.Rect.MakeLTRB(e.x-hw,e.y-hh,e.x+hw,e.y+hh)
        else: b=e.path.computeTightBounds()
        r=b if r is None else skia.Rect.MakeLTRB(min(r.left(),b.left()),min(r.top(),b.top()),max(r.right(),b.right()),max(r.bottom(),b.bottom()))
    return r
def groups(beat):
    """split a beat into separate objects by clustering element boxes"""
    objs=[]
    for e in beat.els:
        b=bb([e]); placed=False
        for o in objs:
            r=o[1]
            if b.left()<r.right()+30 and b.right()>r.left()-30 and b.top()<r.bottom()+30 and b.bottom()>r.top()-30:
                o[0].append(e); o[1]=bb(o[0]); placed=True; break
        if not placed: objs.append([[e],b])
    return [o[1] for o in objs]
sc=build(); n=0
for i,s in enumerate(sc):
    items=[(j,g) for j,b in enumerate(s.beats) if b.els for g in groups(b)]
    for a in range(len(items)):
        for c_ in range(a+1,len(items)):
            (ja,A),(jc,C)=items[a],items[c_]
            if ja==jc or (i,ja) in ALLOW or (i,jc) in ALLOW: continue
            ix=max(0,min(A.right(),C.right())-max(A.left(),C.left())); iy=max(0,min(A.bottom(),C.bottom())-max(A.top(),C.top()))
            small=min(A.width()*A.height(),C.width()*C.height())
            if small>0 and ix*iy/small>0.03:
                n+=1; print(f"scene {i} beat {ja} x beat {jc}: {ix*iy/small:.0%}  {[int(v) for v in (A.left(),A.top(),A.right(),A.bottom())]} vs {[int(v) for v in (C.left(),C.top(),C.right(),C.bottom())]}")
print("collisions:", n)
