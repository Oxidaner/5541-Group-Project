from pptx import Presentation
from pptx.util import Emu
p = Presentation("COMP5541_ViT_Reproduction.pptx")
print("slides:", len(p.slides))
print("size:", p.slide_width, "x", p.slide_height, "=", round(p.slide_width/914400,3), "x", round(p.slide_height/914400,3), "in")
for i, s in enumerate(p.slides, 1):
    pics = [sh for sh in s.shapes if sh.shape_type == 13]
    if pics:
        pic = pics[0]
        print(f"  slide {i}: {len(pics)} pic, {pic.width}x{pic.height} emu ({round(pic.width/914400,2)}x{round(pic.height/914400,2)} in)")
    else:
        print(f"  slide {i}: NO PICTURE")
