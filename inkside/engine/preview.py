import sys
import sys, story
scenes, STORY = story.load(sys.argv[1] if len(sys.argv) > 1 else 'slenderman')
from scenes import *
sc = build(); hand = load_hands()
surf = skia.Surface(W, H); c = surf.getCanvas()
from PIL import Image
imgs=[]
for i, s in enumerate(sc):
    render_frame(c, sc, s.t1 - 0.05, None)
    imgs.append(Image.fromarray(surf.makeImageSnapshot().toarray()[:,:,:3][:,:,::-1] if False else surf.makeImageSnapshot().toarray()[:,:,[2,1,0,3]]).convert("RGB").resize((480,270)))
cols=6; rows=(len(imgs)+cols-1)//cols
sheet=Image.new("RGB",(cols*484,rows*274),"gray")
for i,im in enumerate(imgs): sheet.paste(im,((i%cols)*484,(i//cols)*274))
sheet.save("sheet.png"); print(len(sc),"scenes")
