from PIL import Image
import pathlib, collections
D = pathlib.Path("deck/shots")
targets = {
  "dir-a-cover.png": "#0B0E14",
  "dir-a-data.png": "#0B0E14",
  "dir-b-cover.png": "#F6F1E7",
  "dir-b-data.png": "#F6F1E7",
  "dir-c-cover.png": "#050A18",
  "dir-c-data.png": "#050A18",
}
accents = {
  "dir-a-cover.png": [(0x35,0xE0,0xC2,"teal"), (0xFF,0xB4,0x54,"amber")],
  "dir-a-data.png": [(0x35,0xE0,0xC2,"teal"), (0xFF,0xB4,0x54,"amber")],
  "dir-b-cover.png": [(0xC5,0x46,0x2D,"red")],
  "dir-b-data.png": [(0xC5,0x46,0x2D,"red")],
  "dir-c-cover.png": [(0x7C,0xF0,0xFF,"cyan"), (0xFF,0x7A,0xE0,"mag")],
  "dir-c-data.png": [(0x7C,0xF0,0xFF,"cyan"), (0xFF,0x7A,0xE0,"mag")],
}
def hex2rgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
for name, bghex in targets.items():
    im = Image.open(D/name).convert("RGB")
    w,h = im.size
    bg = hex2rgb(bghex)
    px = im.load()
    # sample corners
    corners = [px[6,6], px[w-7,6], px[6,h-7], px[w-7,h-7]]
    # count non-bg and bbox
    nonbg = 0; minx=w; miny=h; maxx=0; maxy=0
    accent_hits = collections.Counter()
    step = 4
    for y in range(0,h,step):
        for x in range(0,w,step):
            p = px[x,y]
            if abs(p[0]-bg[0])+abs(p[1]-bg[1])+abs(p[2]-bg[2]) > 40:
                nonbg += 1
                if x<minx:minx=x
                if x>maxx:maxx=x
                if y<miny:miny=y
                if y>maxy:maxy=y
            for (ar,ag,ab,label) in accents[name]:
                if abs(p[0]-ar)<=30 and abs(p[1]-ag)<=30 and abs(p[2]-ab)<=30:
                    accent_hits[label]+=1
    print(f"{name}: size={w}x{h} corners_ok={all(abs(c[0]-bg[0])+abs(c[1]-bg[1])+abs(c[2]-bg[2])<40 for c in corners)} bbox=({minx},{miny})-({maxx},{maxy}) nonbg_sampled={nonbg} accents={dict(accent_hits)}")
