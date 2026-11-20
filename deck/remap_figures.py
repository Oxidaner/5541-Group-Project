# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
import pathlib

SRC = pathlib.Path("results/figures")
OUT = pathlib.Path("deck/assets")
OUT.mkdir(parents=True, exist_ok=True)

BG = np.array([8, 15, 40], dtype=np.float32)      # #080F28 deep navy
TXT = np.array([234, 242, 255], dtype=np.float32) # #EAF2FF near-white
CYAN = np.array([99, 199, 255], dtype=np.float32)  # #63C7FF
AMBER = np.array([255, 180, 84], dtype=np.float32) # #FFB454
MAG = np.array([255, 122, 224], dtype=np.float32)

def remap(im):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    mx = a.max(-1); mn = a.min(-1)
    sat = mx - mn

    near_white = lum > 244
    near_black = lum < 45
    grayish = sat < 26
    blueish = (b > r * 1.22) & (b > g * 1.10) & (b - r > 10)
    orangeish = (r > g * 1.22) & (r > b * 1.28) & (r - b > 18) & (r > 90)

    out = np.empty_like(a)
    # default: grayscale inversion
    inv = np.clip(238.0 - lum, 0, 255)
    out[..., 0] = inv; out[..., 1] = inv; out[..., 2] = inv

    # near black -> light text
    out[near_black] = TXT
    # near white -> bg
    out[near_white] = BG
    # blue-ish -> cyan ramp
    m = blueish & ~near_white & ~near_black
    t = np.clip((255.0 - lum) / 255.0 * 1.15, 0, 1)[m][..., None]
    out[m] = BG * (1 - t) + CYAN * t
    # orange-ish -> amber ramp
    m = orangeish & ~near_white & ~near_black
    t = np.clip((255.0 - lum) / 255.0 * 1.15, 0, 1)[m][..., None]
    out[m] = BG * (1 - t) + AMBER * t
    return Image.fromarray(out.astype(np.uint8))

jobs = {
    "attention": "full_finetune_paper_lr_1000_attention.png",
    "confusion": "full_finetune_paper_lr_1000_confusion_matrix.png",
    "position": "position_similarity.png",
    "eff_tradeoff": "efficiency_tradeoff.png",
    "eff_curves": "efficiency_validation_curves.png",
    "acc_cmp": "test_accuracy_comparison.png",
}
for key, fname in jobs.items():
    im = Image.open(SRC / fname)
    im2 = remap(im)
    im2.save(OUT / f"{key}.png")
    # diagnostics
    a = np.asarray(im2.convert("RGB"))
    corners = [tuple(a[2, 2]), tuple(a[2, -3]), tuple(a[-3, 2]), tuple(a[-3, -3])]
    nonbg = int((np.abs(a.astype(int) - BG.astype(int)).sum(-1) > 40).sum())
    has_light = int((np.abs(a.astype(int) - TXT.astype(int)).sum(-1) < 60).sum())
    # saturated pixels
    satpix = int(((a[..., 0].astype(int) - a[..., 2].astype(int)) > 60).sum())
    print(f"{key}: {im.size} -> {im2.size} corners={corners} nonbg={nonbg} lightpx={has_light} cyan/amberpx={satpix}")
