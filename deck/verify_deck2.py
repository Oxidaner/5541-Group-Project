from PIL import Image
import pathlib
D = pathlib.Path("deck/shots")

def region_stats(im, x0,y0,x1,y1):
    px=im.load(); tot=0; bright=0; cyan=0; magenta=0
    for y in range(y0,y1,3):
        for x in range(x0,x1,3):
            p=px[x,y]; tot+=1
            r,g,b=p
            lum=0.299*r+0.587*g+0.114*b
            if lum>170: bright+=1
            if b>150 and b-r>40 and b-g>20: cyan+=1
            if r>180 and b>140 and r-g>40: magenta+=1
    return dict(tot=tot, bright=round(100*bright/tot,1), cyan=round(100*cyan/tot,1), magenta=round(100*magenta/tot,1))

for i in range(1,14):
    name=f"s{i:02d}.png"
    im=Image.open(D/name).convert("RGB")
    w,h=im.size
    kick=region_stats(im, 96,60,1200,95)
    title=region_stats(im, 92,115,1800,205)
    # content bbox excluding glows (sample every 3px, lum>60 or sat>40)
    px=im.load()
    minx,miny,maxx,maxy=w,h,0,0
    for y in range(0,h,4):
        for x in range(0,w,4):
            p=px[x,y]; r,g,b=p
            lum=0.299*r+0.587*g+0.114*b
            if lum>60 or max(p)-min(p)>40:
                if x<minx:minx=x
                if x>maxx:maxx=x
                if y<miny:miny=y
                if y>maxy:maxy=y
    print(f"{name}: size={w}x{h} kick.bright={kick['bright']} kick.cyan={kick['cyan']} title.bright={title['bright']} bbox=({minx},{miny},{maxx},{maxy})")

print("--- figures ---")
checks = [
 ("s08.png", 96,300,1296,780, "attention fig"),
 ("s09.png", 96,300,796,903, "position fig"),
 ("s10.png", 96,300,756,891, "confusion fig"),
 ("s11.png", 96,510,947,810, "tradeoff fig"),
 ("s11.png", 977,510,1788,810, "curves fig"),
 ("s06.png", 120,330,1260,862, "bars"),
 ("s06.png", 1304,330,1824,886, "score panel"),
 ("s07.png", 96,340,1824,872, "table"),
]
for name,x0,y0,x1,y1,label in checks:
    im=Image.open(D/name).convert("RGB")
    s=region_stats(im,x0,y0,x1,y1)
    print(f"{label}: bright={s['bright']} cyan={s['cyan']} magenta={s['magenta']}")
