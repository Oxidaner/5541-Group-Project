from PIL import Image
import pathlib, collections
D = pathlib.Path("deck/shots")

def stats(name):
    im = Image.open(D/name).convert("RGB")
    w,h = im.size
    px = im.load()
    # bg ~ #050A18..#0A1230; compute bbox of "ink" (bright or saturated pixels)
    minx,miny,maxx,maxy = w,h,0,0
    ink = 0; total = 0
    # also count bright (text) pixels
    bright = 0
    for y in range(0,h,3):
        for x in range(0,w,3):
            p = px[x,y]
            total += 1
            lum = 0.299*p[0]+0.587*p[1]+0.114*p[2]
            if lum > 60 or max(p)-min(p) > 40:
                ink += 1
                if x<minx:minx=x
                if x>maxx:maxx=x
                if y<miny:miny=y
                if y>maxy:maxy=y
            if lum > 170:
                bright += 1
    return dict(size=(w,h), bbox=(minx,miny,maxx,maxy), ink=ink, bright=bright, inkpct=round(100*ink/total,1))

for i in range(1,14):
    name = f"s{i:02d}.png"
    s = stats(name)
    print(f"{name}: {s}")

# region density checks for figure slides
def region(name, x0,y0,x1,y1):
    im = Image.open(D/name).convert("RGB"); px=im.load()
    nonbg=0; tot=0; bright=0
    for y in range(y0,y1,3):
        for x in range(x0,x1,3):
            p=px[x,y]; tot+=1
            lum=0.299*p[0]+0.587*p[1]+0.114*p[2]
            if lum>60 or max(p)-min(p)>40: nonbg+=1
            if lum>170: bright+=1
    return round(100*nonbg/tot,1), round(100*bright/tot,1)

print("--- region nonbg%, bright% ---")
print("s08 attention fig:", region("s08.png", 180,300,1740,924))
print("s09 position fig:", region("s09.png", 96,300,796,903))
print("s10 confusion fig:", region("s10.png", 96,300,782,900))
print("s11 tradeoff fig:", region("s11.png", 96,508,1080,855))
print("s11 curves fig:", region("s11.png", 1112,508,1824,771))
print("s06 bars region:", region("s06.png", 120,300,1200,846))
print("s06 score panel:", region("s06.png", 1400,300,1920,886))
