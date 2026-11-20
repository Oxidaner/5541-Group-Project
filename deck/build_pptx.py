# -*- coding: utf-8 -*-
"""Build PPTX from full-bleed slide screenshots + a review contact sheet."""
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
import pathlib

SHOTS = pathlib.Path("deck/shots")
out_pptx = pathlib.Path("COMP5541_ViT_Reproduction.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
for i in range(1, 14):
    slide = prs.slides.add_slide(blank)
    slide.shapes.add_picture(str(SHOTS / f"s{i:02d}.png"), 0, 0,
                             width=prs.slide_width, height=prs.slide_height)
prs.save(str(out_pptx))
print("saved", out_pptx, out_pptx.stat().st_size, "bytes")

# contact sheet: 4 cols x 4 rows
thumb_w, thumb_h = 480, 270
cols, rows = 4, 4
sheet = Image.new("RGB", (cols*thumb_w + 10*(cols+1), rows*thumb_h + 10*(rows+1)), (4, 7, 20))
for i in range(1, 14):
    im = Image.open(SHOTS / f"s{i:02d}.png").convert("RGB").resize((thumb_w, thumb_h))
    r, c = (i-1)//cols, (i-1)%cols
    sheet.paste(im, (10+c*(thumb_w+10), 10+r*(thumb_h+10)))
sheet.save("deck/shots/contact_sheet.png")
print("saved deck/shots/contact_sheet.png")
