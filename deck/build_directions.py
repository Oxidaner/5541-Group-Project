# -*- coding: utf-8 -*-
import pathlib, random
random.seed(5541)
D = pathlib.Path("deck")

def patch_grid_svg(n, size, lit, base="#141B29", litc="#35E0C2", hot="#FFB454", lit2=None, stroke="#0B0E14"):
    # lit: dict {(r,c): 'accent'|'hot'|'dim'} ; lit2 secondary color set
    cell = size / n
    rects = []
    for r in range(n):
        for c in range(n):
            key = (r, c)
            if key in lit:
                col = hot if lit[key] == "hot" else (lit2 if lit[key] == "lit2" else litc)
                op = 1.0
            else:
                col = base
                op = 1.0
            x = round(c * cell + 1, 1)
            y = round(r * cell + 1, 1)
            w = round(cell - 2, 1)
            rects.append(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" fill="{col}" opacity="{op}"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">' + "".join(rects) + "</svg>"

def dot_grid_svg(n, size, heat):
    # attention-like glow grid: blurred circles colored by heat value 0..1
    cell = size / n
    out = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="g" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#7CF0FF"/><stop offset="100%" stop-color="#7CF0FF" stop-opacity="0"/></radialGradient></defs>']
    for r in range(n):
        for c in range(n):
            v = heat.get((r, c), 0.0)
            if v <= 0.05:
                continue
            cx = (c + 0.5) * cell
            cy = (r + 0.5) * cell
            rad = cell * (0.35 + 0.65 * v)
            col = "#7CF0FF" if v < 0.65 else "#FF7AE0"
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="{col}" opacity="{0.15+0.6*v:.2f}" filter="blur(6px)"/>')
    out.append("</svg>")
    return "".join(out)

# ---------- shared meta ----------
FONT_CSS = '<link rel="stylesheet" href="fonts.css">'

def slide(body_css, body, bg="#0B0E14"):
    return f"""<!doctype html><html><head><meta charset="utf-8">
{FONT_CSS}
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:{bg}}}
.slide{{position:relative;width:1920px;height:1080px;overflow:hidden}}
{body_css}
</style></head><body><div class="slide">{body}</div></body></html>"""

# ============================================================
# DIRECTION A — PATCHWORK CONSOLE (dark teal / ink, Swiss grid)
# ============================================================
A_BG = "#0B0E14"
A_INK = "#E9EDF5"
A_DIM = "#8B94A7"
A_TEAL = "#35E0C2"
A_AMBER = "#FFB454"
A_LINE = "#1D2433"

# lit patches: a diagonal path plus an attention "hot" cluster
A_lit = {}
for i in range(16):
    A_lit[(i, i)] = "accent"
for i in range(16):
    A_lit[(i, 15 - i)] = "dim2"
A_lit[(8, 8)] = "hot"
A_lit[(4, 11)] = "hot"
A_lit[(11, 4)] = "accent"
A_lit[(2, 2)] = "accent"
A_lit[(13, 13)] = "accent"
# override dim2 color to a soft teal-blue
A_lit2 = "#274A5C"

A_cover_grid = patch_grid_svg(16, 680, A_lit, base="#151C2C", litc=A_TEAL, hot=A_AMBER, lit2=A_lit2, stroke=A_BG)

A_cover_css = f"""
.kick{{position:absolute;left:90px;top:84px;font:500 20px/1 'JetBrains Mono',monospace;letter-spacing:.32em;color:{A_TEAL}}}
.title{{position:absolute;left:86px;top:190px;font:700 104px/1.02 'Space Grotesk',sans-serif;color:{A_INK};letter-spacing:-.01em}}
.title .accent{{color:{A_TEAL}}}
.title .hot{{color:{A_AMBER}}}
.sub{{position:absolute;left:90px;top:470px;width:840px;font:400 30px/1.5 'Inter',sans-serif;color:{A_DIM}}}
.meta{{position:absolute;left:90px;top:920px;display:flex;gap:56px;font:400 21px/1 'JetBrains Mono',monospace;color:{A_DIM}}}
.meta b{{color:{A_INK};font-weight:700}}
.meta .am{{color:{A_AMBER}}}
.gridwrap{{position:absolute;right:110px;top:180px}}
.gridcap{{position:absolute;right:110px;top:900px;width:680px;text-align:center;font:400 17px/1 'JetBrains Mono',monospace;letter-spacing:.18em;color:{A_DIM}}}
.ghost{{position:absolute;right:-60px;top:60px;font:700 260px/1 'Space Grotesk',sans-serif;color:{A_TEAL};opacity:.05;letter-spacing:-.02em}}
.rule{{position:absolute;left:90px;top:150px;width:120px;height:3px;background:{A_AMBER}}}
"""
A_cover_body = f"""
<div class="ghost">16×16</div>
<div class="kick">COMP 5541 &nbsp;·&nbsp; PAPER REPRODUCTION</div>
<div class="rule"></div>
<div class="title">AN IMAGE IS<br>WORTH <span class="accent">16×16</span> <span class="hot">WORDS</span></div>
<div class="sub">Reproducing the Vision Transformer — ViT-B/32 — on CIFAR-10,<br>probing what moves when the network learns to see.</div>
<div class="meta">
  <div>PAPER &nbsp;<b>ViT · ICLR 2021</b></div>
  <div>LOCAL TEST &nbsp;<b>97.57%</b></div>
  <div>REFERENCE &nbsp;<b>98.79%</b></div>
  <div>GAP &nbsp;<span class="am"><b>−1.22&thinsp;pp</b></span></div>
</div>
<div class="gridwrap">{A_cover_grid}</div>
<div class="gridcap">PATCH EMBEDDING &nbsp;·&nbsp; P = 32 &nbsp;·&nbsp; 49 TOKENS + CLS</div>
"""

# A data slide: horizontal bars 90..99
A_rows = [
    ("Linear probe — frozen features", 96.13, "7.7k"),
    ("Classification head only", 94.70, "7.7k"),
    ("Last block · 300 steps", 91.51, "7.1M"),
    ("Last block · 3,000 steps", 92.56, "7.1M"),
    ("Full fine-tune · 300 steps", 92.83, "87.5M"),
    ("Full fine-tune · LR-scaled", 95.63, "87.5M"),
    ("Full fine-tune · paper LR", 97.57, "87.5M"),
]
def bars_html(rows, ref, lo=89.0, hi=99.2):
    b = []
    y0 = 260; rh = 86; gap = 18
    for i, (name, val, params) in enumerate(rows):
        y = y0 + i * (rh + gap)
        w = 820 * (val - lo) / (hi - lo)
        best = val == max(r[1] for r in rows)
        col = A_AMBER if best else A_TEAL
        b.append(f'<div class="row" style="top:{y}px"><div class="rname">{name}<span class="rparam">{params}</span></div><div class="rtrack"><div class="rfill" style="width:{w:.0f}px;background:{col}"></div></div><div class="rval" style="color:{col if best else A_INK}">{val:.2f}%</div></div>')
    refx = 120 + 820 * (ref - lo) / (hi - lo)
    return "".join(b), refx

A_bars, A_refx = bars_html(A_rows, 98.79)
A_data_css = f"""
.kick{{position:absolute;left:90px;top:70px;font:500 19px/1 'JetBrains Mono',monospace;letter-spacing:.3em;color:{A_TEAL}}}
.title{{position:absolute;left:86px;top:130px;font:700 62px/1.05 'Space Grotesk',sans-serif;color:{A_INK};letter-spacing:-.01em}}
.sub{{position:absolute;left:90px;top:215px;font:400 23px/1 'Inter',sans-serif;color:{A_DIM}}}
.chart{{position:absolute;left:120px;top:260px;width:1040px}}
.row{{position:absolute;left:0;width:1040px;height:86px}}
.rname{{position:absolute;left:0;top:8px;width:340px;font:500 21px/1.2 'Space Grotesk',sans-serif;color:{A_INK}}}
.rparam{{display:block;font:400 16px/1.4 'JetBrains Mono',monospace;color:{A_DIM}}}
.rtrack{{position:absolute;left:360px;top:26px;width:820px;height:34px;background:{A_LINE};border-radius:2px}}
.rfill{{position:absolute;left:0;top:0;height:34px;border-radius:2px}}
.rval{{position:absolute;left:1204px;top:22px;width:150px;text-align:right;font:700 30px/1 'JetBrains Mono',monospace}}
.refline{{position:absolute;top:250px;width:2px;height:700px;background:{A_AMBER};opacity:.9}}
.reflabel{{position:absolute;top:950px;font:500 17px/1 'JetBrains Mono',monospace;letter-spacing:.08em;color:{A_AMBER}}}
.foot{{position:absolute;left:90px;top:1010px;font:400 17px/1.4 'JetBrains Mono',monospace;color:{A_DIM}}}
.axis{{position:absolute;left:120px;top:1030px;font:400 16px/1 'JetBrains Mono',monospace;color:{A_DIM}}}
"""
A_data_body = f"""
<div class="kick">RESULTS &nbsp;·&nbsp; CIFAR-10 TEST ACCURACY</div>
<div class="title">How much of the network must move?</div>
<div class="sub">Fine-tuning protocol vs. test accuracy — ViT-B/32 · 224 px · batch 64.</div>
<div class="chart">{A_bars}</div>
<div class="refline" style="left:{A_refx:.0f}px"></div>
<div class="reflabel" style="left:{A_refx+14:.0f}px">PAPER REFERENCE · 98.79% · 384 px · 10k steps</div>
<div class="foot">Local runs use 224 px inputs and shorter budgets — a resource-scaled reproduction, not an exact replay of the paper protocol.</div>
"""

# ============================================================
# DIRECTION B — JOURNAL EDITION (warm paper, serif print)
# ============================================================
B_BG = "#F6F1E7"
B_INK = "#16130E"
B_RED = "#C5462D"
B_DIM = "#7A6F5F"
B_LINE = "#16130E2E"

B_lit = {(r,c): "accent" for r in range(8) for c in range(8) if (r+c) % 3 == 0}
B_lit[(0,0)] = "hot"; B_lit[(7,7)] = "hot"; B_lit[(0,7)] = "hot"; B_lit[(7,0)] = "hot"
B_emblem = patch_grid_svg(8, 170, B_lit, base="#E4DCC9", litc=B_RED, hot=B_INK, lit2=B_RED, stroke=B_BG)

B_cover_css = f"""
.mast{{position:absolute;left:90px;top:66px;right:90px;display:flex;justify-content:space-between;font:600 17px/1 'Inter',sans-serif;letter-spacing:.28em;color:{B_DIM};text-transform:uppercase}}
.mast .no{{color:{B_RED}}}
.title{{position:absolute;left:86px;top:250px;font:400 118px/1.0 'Fraunces',serif;color:{B_INK};letter-spacing:-.015em}}
.title .it{{font-style:italic;color:{B_RED}}}
.rule{{position:absolute;left:90px;top:640px;width:1740px;height:2px;background:{B_INK}}}
.lede{{position:absolute;left:90px;top:690px;width:760px;font:400 27px/1.55 'Inter',sans-serif;color:{B_DIM}}}
.lede b{{color:{B_INK};font-weight:600}}
.emblem{{position:absolute;right:170px;top:170px}}
.stamp{{position:absolute;right:380px;top:560px;font:500 15px/1 'Inter',sans-serif;letter-spacing:.22em;color:{B_DIM};text-transform:uppercase}}
.meta{{position:absolute;left:90px;top:920px;display:flex;gap:0px;font:500 21px/1 'JetBrains Mono',monospace;color:{B_INK}}}
.meta .cell{{border-left:2px solid {B_LINE};padding:0 36px}}
.meta .cell:first-child{{border-left:none;padding-left:0}}
.meta small{{display:block;font:500 15px/1.6 'Inter',sans-serif;letter-spacing:.16em;color:{B_DIM};text-transform:uppercase}}
.meta .red{{color:{B_RED}}}
"""
B_cover_body = f"""
<div class="mast"><span>COMP 5541 &nbsp;·&nbsp; Project Note <span class="no">Nº 03</span></span><span>ICLR 2021 · Dosovitskiy et al.</span></div>
<div class="emblem">{B_emblem}</div>
<div class="stamp">Patch emblem · P = 32</div>
<div class="title">An Image Is Worth<br><span class="it">16 × 16</span> Words</div>
<div class="rule"></div>
<div class="lede"><b>Reproducing the Vision Transformer</b> on CIFAR-10 — four fine-tuning protocols, one attention map, and the gap between a laptop and a landmark.</div>
<div class="meta">
  <div class="cell"><small>Local test accuracy</small>97.57%</div>
  <div class="cell"><small>Paper reference</small>98.79%</div>
  <div class="cell"><small>Gap</small><span class="red">−1.22 pp</span></div>
  <div class="cell"><small>Model</small>ViT-B/32</div>
  <div class="cell"><small>Dataset</small>CIFAR-10</div>
</div>
"""

# B data slide: printed table
B_trows = [
    ("Linear probe — frozen features", "7.7k", "—", "96.13%"),
    ("Classification head only", "7.7k", "500", "94.70%"),
    ("Last block", "7.1M", "300", "91.51%"),
    ("Last block (long)", "7.1M", "3,000", "92.56%"),
    ("Full fine-tune", "87.5M", "300", "92.83%"),
    ("Full fine-tune · LR-scaled", "87.5M", "1,000", "95.63%"),
    ("Full fine-tune · paper LR", "87.5M", "1,000", "97.57%"),
]
B_table = "".join(
    f'<div class="tr" style="top:{300 + i*84}px"><span class="c1">{n}</span><span class="c2">{p}</span><span class="c3">{s}</span><span class="c4{" red" if i==6 else ""}">{v}</span></div>'
    for i,(n,p,s,v) in enumerate(B_trows)
)
B_data_css = f"""
.mast{{position:absolute;left:90px;top:62px;font:600 16px/1 'Inter',sans-serif;letter-spacing:.28em;color:{B_DIM};text-transform:uppercase}}
.title{{position:absolute;left:86px;top:120px;font:400 76px/1 'Fraunces',serif;color:{B_INK};letter-spacing:-.015em}}
.rule{{position:absolute;left:90px;top:250px;width:1740px;height:2px;background:{B_INK}}}
.th{{position:absolute;top:258px;font:600 16px/1 'Inter',sans-serif;letter-spacing:.2em;color:{B_DIM};text-transform:uppercase}}
.c1{{position:absolute;left:90px;width:780px;font:500 24px/1 'Fraunces',serif;color:{B_INK}}}
.c2{{position:absolute;left:950px;width:220px;text-align:right;font:400 22px/1 'JetBrains Mono',monospace;color:{B_DIM}}}
.c3{{position:absolute;left:1250px;width:200px;text-align:right;font:400 22px/1 'JetBrains Mono',monospace;color:{B_DIM}}}
.c4{{position:absolute;left:1540px;width:290px;text-align:right;font:600 26px/1 'JetBrains Mono',monospace;color:{B_INK}}}
.c4.red{{color:{B_RED}}}
.tr{{position:absolute;height:60px;border-top:1px solid {B_LINE}}}
.ref{{position:absolute;left:90px;top:906px;font:500 22px/1 'Fraunces',serif;color:{B_INK}}}
.ref span{{color:{B_RED}}}
.foot{{position:absolute;left:90px;top:980px;width:1500px;font:400 18px/1.5 'Inter',sans-serif;color:{B_DIM}}}
"""
B_data_body = f"""
<div class="mast">Results · CIFAR-10 test accuracy by protocol</div>
<div class="title">Accuracy, by protocol</div>
<div class="rule"></div>
<div class="th c1">Configuration</div><div class="th c2">Params</div><div class="th c3">Steps</div><div class="th c4">Test acc.</div>
{B_table}
<div class="ref">Paper reference — <span>98.79%</span> · 384 px · 10,000 steps · ViT-B/32</div>
<div class="foot">Every local run evaluates the same held-out test split; the best checkpoint is chosen on validation. Test labels are never used for tuning.</div>
"""

# ============================================================
# DIRECTION C — ATTENTION FIELD (deep blue, glow)
# ============================================================
C_BG = "#050A18"
C_INK = "#F2F6FF"
C_DIM = "#9AA8C7"
C_CYAN = "#7CF0FF"
C_MAG = "#FF7AE0"

C_heat = {}
for r in range(9):
    for c in range(9):
        v = 0.15 + 0.55 * (1 - abs(r - c) / 9.0)
        C_heat[(r, c)] = max(0, v)
C_heat[(4,4)] = 1.0; C_heat[(2,6)] = 0.9; C_heat[(6,2)] = 0.85; C_heat[(0,0)] = 0.7; C_heat[(8,8)] = 0.7
C_glow = dot_grid_svg(9, 900, C_heat)

C_cover_css = f"""
.bg{{position:absolute;left:510px;top:60px;opacity:.9}}
.grad{{position:absolute;inset:0;background:radial-gradient(1200px 700px at 50% 42%, rgba(124,240,255,.10), transparent 60%)}}
.kick{{position:absolute;left:90px;top:80px;font:500 19px/1 'JetBrains Mono',monospace;letter-spacing:.34em;color:{C_CYAN}}}
.title{{position:absolute;left:86px;top:250px;width:1750px;text-align:center;font:700 96px/1.06 'Inter',sans-serif;color:{C_INK};letter-spacing:-.02em}}
.title .glow{{color:{C_CYAN}}}
.title .mag{{color:{C_MAG}}}
.sub{{position:absolute;left:400px;top:540px;width:1120px;text-align:center;font:400 27px/1.5 'Inter',sans-serif;color:{C_DIM}}}
.stat{{position:absolute;top:760px;left:0;width:1920px;text-align:center}}
.stat .big{{font:700 120px/1 'Inter',sans-serif;color:{C_INK};letter-spacing:-.02em}}
.stat .big small{{font:500 30px/1 'JetBrains Mono',monospace;color:{C_DIM};letter-spacing:.1em;display:block;margin-bottom:16px}}
.stat .gap{{font:400 24px/1 'JetBrains Mono',monospace;color:{C_CYAN};letter-spacing:.08em}}
"""
C_cover_body = f"""
<div class="grad"></div>
<div class="bg">{C_glow}</div>
<div class="kick">COMP 5541 · REPRODUCTION STUDY</div>
<div class="title">AN IMAGE IS WORTH <span class="glow">16×16</span> <span class="mag">WORDS</span></div>
<div class="sub">The Vision Transformer (ViT-B/32) reproduced on CIFAR-10 — what attention reveals when a patch grid becomes a sentence.</div>
<div class="stat"><div class="big"><small>LOCAL TEST ACCURACY</small>97.57%</div><div class="gap">PAPER REFERENCE 98.79% · GAP −1.22 PP</div></div>
"""

# C data slide: accuracy spectrum as glowing line + stat cards
C_rows = [
    ("Linear probe", 96.13), ("Head only", 94.70), ("Last block", 91.51),
    ("Last block ·3k", 92.56), ("Full 300", 92.83), ("Full LR-scaled", 95.63), ("Full paper LR", 97.57),
]
def spectrum(rows, ref):
    lo, hi = 88.0, 99.5
    W = 1500; L = 90
    dots = []
    for i,(n,v) in enumerate(rows):
        x = L + W * (v - lo)/(hi - lo)
        y = 560 - (i % 4) * 70
        best = v == max(x[1] for x in rows)
        col = C_MAG if best else C_CYAN
        dots.append(f'<div class="dot" style="left:{x:.0f}px;top:{y}px;background:{col};box-shadow:0 0 30px {col}"></div>')
        dots.append(f'<div class="dlab" style="left:{x-110:.0f}px;top:{y+34}px;width:220px">{n}<br><b style="color:{col}">{v:.2f}%</b></div>')
    rx = L + W * (ref - lo)/(hi - lo)
    return "".join(dots), rx
C_dots, C_rx = spectrum(C_rows, 98.79)
C_data_css = f"""
.kick{{position:absolute;left:90px;top:70px;font:500 19px/1 'JetBrains Mono',monospace;letter-spacing:.3em;color:{C_CYAN}}}
.title{{position:absolute;left:86px;top:128px;font:700 64px/1 'Inter',sans-serif;color:{C_INK};letter-spacing:-.015em}}
.sub{{position:absolute;left:90px;top:215px;font:400 22px/1 'Inter',sans-serif;color:{C_DIM}}}
.line{{position:absolute;left:90px;top:560px;width:1500px;height:2px;background:linear-gradient(90deg, rgba(124,240,255,.1), rgba(124,240,255,.8), rgba(255,122,224,.8))}}
.dot{{position:absolute;width:16px;height:16px;border-radius:50%;transform:translate(-8px,-7px)}}
.dlab{{position:absolute;text-align:center;font:400 17px/1.5 'JetBrains Mono',monospace;color:{C_DIM}}}
.dlab b{{font-weight:700}}
.refline{{position:absolute;top:430px;width:2px;height:260px;background:{C_CYAN};opacity:.55}}
.reflabel{{position:absolute;top:412px;font:500 16px/1 'JetBrains Mono',monospace;letter-spacing:.06em;color:{C_CYAN}}}
.axis{{position:absolute;left:90px;top:790px;width:1500px;display:flex;justify-content:space-between;font:400 18px/1 'JetBrains Mono',monospace;color:{C_DIM}}}
.foot{{position:absolute;left:90px;top:980px;font:400 18px/1.4 'JetBrains Mono',monospace;color:{C_DIM}}}
"""
C_data_body = f"""
<div class="kick">RESULTS · ACCURACY LADDER</div>
<div class="title">Every protocol earns its place on the spectrum</div>
<div class="sub">Test accuracy, 88–99.5% scale — the reference sits alone at the bright end.</div>
<div class="line"></div>
{C_dots}
<div class="refline" style="left:{C_rx:.0f}px"></div>
<div class="reflabel" style="left:{C_rx-150:.0f}px">PAPER · 98.79%</div>
<div class="axis"><span>88%</span><span>91%</span><span>94%</span><span>97%</span><span>99.5%</span></div>
<div class="foot">224 px inputs · batch 64 · best-of-validation checkpoints · fixed test split.</div>
"""

files = {
    "dir-a-cover.html": slide(A_cover_css, A_cover_body, A_BG),
    "dir-a-data.html": slide(A_data_css, A_data_body, A_BG),
    "dir-b-cover.html": slide(B_cover_css, B_cover_body, B_BG),
    "dir-b-data.html": slide(B_data_css, B_data_body, B_BG),
    "dir-c-cover.html": slide(C_cover_css, C_cover_body, C_BG),
    "dir-c-data.html": slide(C_data_css, C_data_body, C_BG),
}
for name, html in files.items():
    (D / name).write_text(html)
    print("wrote", name, len(html), "bytes")
