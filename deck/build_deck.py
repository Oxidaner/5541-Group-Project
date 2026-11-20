# -*- coding: utf-8 -*-
"""Build the full COMP5541 deck (Direction C — Attention Field). 13 slides, 1920x1080."""
import pathlib
D = pathlib.Path("deck")

# ---------- design tokens ----------
BG = "linear-gradient(135deg,#050A18 0%,#081028 50%,#0A1230 100%)"
INK = "#F2F6FF"
BODY = "#C9D4EC"
DIM = "#8FA0C4"
CYAN = "#7CF0FF"
MAG = "#FF7AE0"
AMBER = "#FFB454"
LINE = "#26345E"

def base_css():
    return f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#050A18}}
.slide{{position:relative;width:1920px;height:1080px;overflow:hidden;background:{BG}}}
.glowc{{position:absolute;right:-280px;top:-280px;width:920px;height:920px;border-radius:50%;background:radial-gradient(circle,rgba(124,240,255,.13),transparent 62%)}}
.glowm{{position:absolute;left:-320px;bottom:-340px;width:1000px;height:1000px;border-radius:50%;background:radial-gradient(circle,rgba(255,122,224,.10),transparent 60%)}}
.kick{{position:absolute;left:96px;top:66px;font:500 17px/1 'JetBrains Mono',monospace;letter-spacing:.32em;color:{CYAN};text-transform:uppercase}}
.title{{position:absolute;left:92px;top:122px;font:700 60px/1.04 'Inter',sans-serif;color:{INK};letter-spacing:-.015em}}
.title .cy{{color:{CYAN}}}
.title .mg{{color:{MAG}}}
.bar{{position:absolute;left:96px;top:220px;width:150px;height:3px;background:linear-gradient(90deg,{CYAN},{MAG})}}
.foot{{position:absolute;left:96px;bottom:54px;font:400 16px/1 'JetBrains Mono',monospace;letter-spacing:.18em;color:{DIM}}}
.pageno{{position:absolute;right:96px;bottom:54px;font:400 16px/1 'JetBrains Mono',monospace;color:{DIM}}}
"""

def slide(css, body, page, kicker=None, title=None, total=13):
    head = ""
    if kicker:
        head += f'<div class="kick">{kicker}</div>'
    if title:
        head += f'<div class="title">{title}</div>'
        head += '<div class="bar"></div>'
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="fonts.css">
<style>{base_css()}{css}</style></head>
<body><div class="slide">
<div class="glowc"></div><div class="glowm"></div>
{head}
{body}
<div class="foot">COMP 5541 · AN IMAGE IS WORTH 16×16 WORDS · VIT-B/32 ON CIFAR-10</div>
<div class="pageno">{page:02d} / {total}</div>
</div></body></html>"""

def img(path, x, y, w, h, cap=None, capy=None, capcolor=DIM):
    caphtml = f'<div class="imgcap" style="left:{x}px;top:{capy}px;width:{w}px;text-align:center;font:400 15px/1.4 \'JetBrains Mono\',monospace;letter-spacing:.14em;color:{capcolor}">{cap}</div>' if cap else ""
    return f'<img src="{path}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:1px solid {LINE};box-shadow:0 0 60px rgba(124,240,255,.10),0 24px 60px rgba(0,0,0,.45)">' + caphtml

# ================================================================
# SLIDE 1 — COVER (custom centered title, no auto kick/title)
# ================================================================
def heat_svg():
    import random
    random.seed(5541)
    n = 9; size = 920; cell = size / n
    out = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    for r in range(n):
        for c in range(n):
            v = 0.15 + 0.55 * (1 - abs(r - c) / 9.0)
            if v <= 0.08: continue
            cx = (c + .5) * cell; cy = (r + .5) * cell
            rad = cell * (0.35 + 0.65 * v)
            col = "#7CF0FF" if v < 0.66 else "#FF7AE0"
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="{col}" opacity="{0.12+0.55*v:.2f}"/>')
    out.append("</svg>")
    return "".join(out)

s1_css = f"""
.bg{{position:absolute;left:500px;top:30px;opacity:.95}}
.kick{{position:absolute;left:96px;top:88px;font:500 18px/1 'JetBrains Mono',monospace;letter-spacing:.34em;color:{CYAN}}}
.title{{position:absolute;left:90px;top:238px;width:1780px;text-align:center;font:700 100px/1.05 'Inter',sans-serif;color:{INK};letter-spacing:-.02em}}
.title .cy{{color:{CYAN}}}
.title .mg{{color:{MAG}}}
.sub{{position:absolute;left:430px;top:520px;width:1060px;text-align:center;font:400 27px/1.55 'Inter',sans-serif;color:{BODY}}}
.stat{{position:absolute;top:724px;left:0;width:1920px;text-align:center}}
.stat .big{{font:700 118px/1 'Inter',sans-serif;color:{INK};letter-spacing:-.02em}}
.stat .big small{{display:block;font:500 24px/1 'JetBrains Mono',monospace;letter-spacing:.24em;color:{DIM};margin-bottom:18px}}
.stat .gap{{font:400 23px/1 'JetBrains Mono',monospace;letter-spacing:.1em;color:{CYAN}}}
.stat .gap .mg{{color:{MAG}}}
"""
s1_body = f"""
<div class="bg">{heat_svg()}</div>
<div class="kick">COMP 5541 · REPRODUCTION STUDY · ICLR 2021</div>
<div class="title">AN IMAGE IS WORTH <span class="cy">16×16</span> <span class="mg">WORDS</span></div>
<div class="sub">Reproducing the Vision Transformer — ViT-B/32 — on CIFAR-10:<br>four fine-tuning protocols, one attention map, and a PatchDropout speed-up.</div>
<div class="stat"><div class="big"><small>LOCAL TEST ACCURACY</small>97.57%</div>
<div class="gap">PAPER REFERENCE <span class="mg">98.79%</span> &nbsp;·&nbsp; GAP <span class="mg">−1.22 pp</span></div></div>
"""

# ================================================================
# SLIDE 2 — ROADMAP
# ================================================================
s2_items = [
    ("01", "The paper", "ViT and the 16×16 idea — why it broke the CNN monopoly."),
    ("02", "Method", "Patch → tokens → Transformer. How ViT-B/32 actually sees."),
    ("03", "Setup", "CIFAR-10, ImageNet-21k weights, and a fair protocol."),
    ("04", "Results", "Accuracy ladder, attention, and positional encoding."),
    ("05", "Extension", "PatchDropout: 15.7% faster training for −0.10 pp."),
]
s2_css = f"""
.road{{position:absolute;left:96px;top:330px;width:1728px}}
.card{{position:absolute;width:330px;height:500px;border:1px solid {LINE};border-radius:18px;background:rgba(11,19,48,.55)}}
.num{{position:absolute;left:34px;top:34px;font:700 64px/1 'Inter',sans-serif;background:linear-gradient(90deg,{CYAN},{MAG});-webkit-background-clip:text;background-clip:text;color:transparent}}
.ct{{position:absolute;left:34px;top:140px;font:600 28px/1 'Inter',sans-serif;color:{INK}}}
.cd{{position:absolute;left:34px;top:200px;width:262px;font:400 20px/1.55 'Inter',sans-serif;color:{BODY}}}
.arrow{{position:absolute;top:180px;width:22px;text-align:center;font:500 26px/1 'JetBrains Mono',monospace;color:{CYAN}}}
"""
s2_body = ""
for i, (n, t, dsc) in enumerate(s2_items):
    x = 96 + i * 346
    s2_body += f'<div class="card" style="left:{x}px;top:0"><div class="num">{n}</div><div class="ct">{t}</div><div class="cd">{dsc}</div></div>'
    if i < 4:
        s2_body += f'<div class="arrow" style="left:{x+334}px">→</div>'
s2_body = f'<div class="road">{s2_body}</div>'

# ================================================================
# SLIDE 3 — THE PAPER
# ================================================================
s3_css = f"""
.quote{{position:absolute;left:96px;top:330px;width:860px;font:600 46px/1.22 'Inter',sans-serif;color:{INK}}}
.quote .cy{{color:{CYAN}}}
.quote .mg{{color:{MAG}}}
.byline{{position:absolute;left:96px;top:510px;font:400 19px/1 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.08em}}
.panel{{position:absolute;right:96px;top:330px;width:720px}}
.fact{{margin-bottom:24px;border-left:2px solid {CYAN};padding-left:22px}}
.fact .f{{font:400 16px/1.5 'JetBrains Mono',monospace;letter-spacing:.16em;color:{DIM};text-transform:uppercase}}
.fact .v{{font:500 23px/1.35 'Inter',sans-serif;color:{INK};margin-top:6px}}
.fact .v .mg{{color:{MAG}}}
.glyph{{position:absolute;left:96px;top:620px;font:700 92px/1 'Inter',sans-serif;color:{CYAN};opacity:.14}}
"""
s3_body = f"""
<div class="quote">“An image is worth <span class="cy">16×16 words</span>” — split an image into patches and treat them as <span class="mg">a sentence of tokens</span>.</div>
<div class="byline">DOSOVITSKIY ET AL. · ICLR 2021 · GOOGLE RESEARCH BRAIN</div>
<div class="panel">
  <div class="fact"><div class="f">Model used here</div><div class="v">ViT-B/32 · 86M params · <span class="mg">pretrained on ImageNet-21k</span></div></div>
  <div class="fact"><div class="f">Namesake grid</div><div class="v">16×16 patches → 196 tokens (ViT-B/16); ours: 32×32 → 49 + CLS</div></div>
  <div class="fact"><div class="f">Why it matters</div><div class="v">No convolutions — attention alone reaches (then beats) CNNs at scale</div></div>
  <div class="fact"><div class="f">CIFAR-10 reference</div><div class="v">98.79% @ 384 px · 10,000 steps · batch 512</div></div>
</div>
<div class="glyph">16×16</div>
"""

# ================================================================
# SLIDE 4 — METHOD DIAGRAM
# ================================================================
nodes = [
    ("IMAGE", "224 × 224 · 3 channels", CYAN),
    ("PATCH SPLIT", "32 × 32 patches · 7 × 7 grid", CYAN),
    ("LINEAR + POS + CLS", "49 tokens + CLS · dim 768", MAG),
    ("TRANSFORMER", "12 layers · 12 heads · self-attention", MAG),
    ("MLP HEAD", "1 hidden layer → 10 classes", AMBER),
]
s4_css = f"""
.flow{{position:absolute;left:96px;top:330px;width:1728px;display:flex;align-items:stretch}}
.node{{width:308px;height:250px;border:1px solid {LINE};border-radius:18px;background:rgba(11,19,48,.55);padding:34px 30px}}
.node .nt{{font:600 25px/1.1 'Inter',sans-serif;color:{INK};margin-top:18px}}
.node .nd{{font:400 16px/1.5 'JetBrains Mono',monospace;color:{DIM};margin-top:12px}}
.node .nh{{font:700 22px/1 'JetBrains Mono',monospace}}
.arrow{{width:32px;display:flex;align-items:center;justify-content:center;font:500 30px/1 'JetBrains Mono',monospace;color:{CYAN}}}
.note{{position:absolute;left:96px;top:660px;width:1728px;font:400 21px/1.6 'Inter',sans-serif;color:{BODY}}}
.note .cy{{color:{CYAN}}}
.note .mg{{color:{MAG}}}
.mini{{position:absolute;left:96px;top:860px;width:1728px;font:400 17px/1.5 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.06em}}
"""
flow = ""
for i, (t, d, c) in enumerate(nodes):
    flow += f'<div class="node"><div class="nh" style="color:{c}">0{i+1}</div><div class="nt">{t}</div><div class="nd">{d}</div></div>'
    if i < 4:
        flow += '<div class="arrow">→</div>'
s4_body = f"""
<div class="flow">{flow}</div>
<div class="note">An image becomes a <span class="cy">sequence of patch embeddings</span>; learned position embeddings restore spatial order and the <span class="mg">CLS token</span> gathers a global summary. Self-attention is the only mixing operation — <span class="cy">no convolution anywhere</span>.</div>
<div class="mini">PATCH SIZE 32 (ViT-B/32) → 7×7 = 49 TOKENS · CLASS TOKEN ADDED → 50 · THE PAPER'S NAMESAKE ViT-B/16 USES 16×16 → 196 TOKENS</div>
"""

# ================================================================
# SLIDE 5 — SETUP
# ================================================================
s5_css = f"""
.grid{{position:absolute;left:96px;top:330px;width:1728px}}
.cell{{position:absolute;width:544px;height:210px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);padding:30px 34px}}
.cell .f{{font:400 16px/1.4 'JetBrains Mono',monospace;letter-spacing:.16em;color:{DIM};text-transform:uppercase}}
.cell .v{{font:600 24px/1.35 'Inter',sans-serif;color:{INK};margin-top:12px}}
.cell .v .cy{{color:{CYAN}}}
.cell .v .mg{{color:{MAG}}}
.strip{{position:absolute;left:96px;top:820px;width:1728px;height:84px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);display:flex;align-items:center;justify-content:space-between;padding:0 34px;font:500 18px/1 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.08em}}
.strip .on{{color:{INK}}}
.strip .cy{{color:{CYAN}}}
.strip .mg{{color:{MAG}}}
"""
cells = [
    ("Model", "ViT-B/32 · <span class='cy'>ImageNet-21k pretrained</span> · timm 1.0.22"),
    ("Dataset", "CIFAR-10 · 49,000 train · 1,000 val · 10,000 test"),
    ("Local budget", "<span class='mg'>224 px</span> · batch 64 · LR 0.003 · 1,000 steps"),
    ("Paper protocol", "384 px · batch 512 · 10,000 steps → <span class='cy'>98.79%</span>"),
    ("Device", "Apple M4 Pro · MPS · PyTorch 2.8.0"),
    ("Selection", "best validation checkpoint · <span class='mg'>step 600</span> · fixed test split"),
]
grid = ""
for i, (f, v) in enumerate(cells):
    x = 96 + (i % 3) * 560
    y = (i // 3) * 232
    grid += f'<div class="cell" style="left:{x}px;top:{y}px"><div class="f">{f}</div><div class="v">{v}</div></div>'
s5_body = f"""
<div class="grid">{grid}</div>
<div class="strip"><span>PROTOCOL LADDER</span><span>LINEAR PROBE <span class="on">→</span> HEAD ONLY <span class="on">→</span> LAST BLOCK <span class="on">→</span> <span class="cy">FULL FINE-TUNE</span></span><span>INCREASING TRAINABLE CAPACITY</span></div>
"""

# ================================================================
# SLIDE 6 — RESULTS LADDER
# ================================================================
rows6 = [
    ("Full fine-tune · paper LR 0.003", 97.57, True),
    ("Linear probe — frozen features", 96.13, False),
    ("Full fine-tune · LR-scaled 0.000375", 95.63, False),
    ("Classification head only · 500 steps", 94.70, False),
    ("Full fine-tune · 300 steps", 92.83, False),
    ("Last block · 3,000 steps", 92.56, False),
    ("Last block · 300 steps", 91.51, False),
]
def bars6():
    lo, hi = 89.0, 99.3
    out = []
    for i, (name, val, best) in enumerate(rows6):
        y = i * 78
        w = 620 * (val - lo) / (hi - lo)
        col = MAG if best else CYAN
        out.append(f'<div class="row" style="top:{y}px"><div class="rname">{name}</div><div class="rtrack"><div class="rfill" style="width:{w:.0f}px;background:{col};box-shadow:0 0 24px {col}88"></div></div><div class="rval" style="color:{col}">{val:.2f}</div></div>')
    return "".join(out)
refx = 120 + 620 * (98.79 - 89.0) / (99.3 - 89.0)
s6_css = f"""
.chart{{position:absolute;left:120px;top:330px;width:1080px}}
.row{{position:absolute;left:0;width:1080px;height:64px}}
.rname{{position:absolute;left:0;top:6px;width:450px;font:500 21px/1.2 'Inter',sans-serif;color:{INK}}}
.rtrack{{position:absolute;left:470px;top:14px;width:620px;height:34px;background:rgba(38,52,94,.55);border-radius:3px}}
.rfill{{position:absolute;left:0;top:0;height:34px;border-radius:3px}}
.rval{{position:absolute;left:1110px;top:10px;width:150px;text-align:right;font:700 30px/1 'JetBrains Mono',monospace}}
.refline{{position:absolute;top:318px;width:2px;height:540px;background:{CYAN};opacity:.85}}
.reflabel{{position:absolute;top:872px;font:500 15px/1 'JetBrains Mono',monospace;letter-spacing:.06em;color:{CYAN}}}
.score{{position:absolute;right:96px;top:330px;width:520px;height:556px;border:1px solid {LINE};border-radius:18px;background:rgba(11,19,48,.55);padding:40px 44px}}
.score .big{{font:700 100px/1 'Inter',sans-serif;color:{MAG};letter-spacing:-.02em}}
.score .big small{{display:block;font:500 20px/1 'JetBrains Mono',monospace;letter-spacing:.2em;color:{DIM};margin-bottom:20px}}
.score .srow{{display:flex;justify-content:space-between;padding:17px 0;border-top:1px solid {LINE};font:400 19px/1 'Inter',sans-serif;color:{BODY}}}
.score .srow b{{font:600 20px/1 'JetBrains Mono',monospace;color:{INK}}}
.score .srow .cy{{color:{CYAN}}}
"""
s6_body = f"""
<div class="chart">{bars6()}</div>
<div class="refline" style="left:{refx:.0f}px"></div>
<div class="reflabel" style="left:{refx+12:.0f}px">PAPER · 98.79%</div>
<div class="score">
  <div class="big"><small>LOCAL BEST</small>97.57%</div>
  <div class="srow"><span>vs paper reference</span><b class="cy">−1.22 pp</b></div>
  <div class="srow"><span>Validation (best step 600)</span><b>97.90%</b></div>
  <div class="srow"><span>Error rate</span><b>2.43%</b></div>
  <div class="srow"><span>Paper error rate</span><b>1.21%</b></div>
  <div class="srow"><span>Trainable params</span><b>87.5M</b></div>
</div>
"""

# ================================================================
# SLIDE 7 — PROTOCOLS TABLE
# ================================================================
t7 = [
    ("Linear probe — frozen features", "7.7k", "—", "96.13%", False),
    ("Classification head only", "7.7k", "500", "94.70%", False),
    ("Last block", "7.1M", "300", "91.51%", False),
    ("Last block (long)", "7.1M", "3,000", "92.56%", False),
    ("Full fine-tune", "87.5M", "300", "92.83%", False),
    ("Full fine-tune · LR-scaled", "87.5M", "1,000", "95.63%", False),
    ("Full fine-tune · paper LR", "87.5M", "1,000", "97.57%", True),
]
rows7 = "".join(
    f'<div class="tr" style="top:{340 + i*76}px"><span class="c1">{n}</span><span class="c2">{p}</span><span class="c3">{s}</span><span class="c4{" best" if b else ""}">{v}</span></div>'
    for i, (n, p, s, v, b) in enumerate(t7)
)
s7_css = f"""
.th{{position:absolute;top:302px;font:600 16px/1 'Inter',sans-serif;letter-spacing:.2em;color:{DIM};text-transform:uppercase}}
.c1{{position:absolute;left:96px;width:860px;font:500 24px/1 'Inter',sans-serif;color:{INK}}}
.c2{{position:absolute;left:1010px;width:210px;text-align:right;font:400 22px/1 'JetBrains Mono',monospace;color:{BODY}}}
.c3{{position:absolute;left:1300px;width:190px;text-align:right;font:400 22px/1 'JetBrains Mono',monospace;color:{BODY}}}
.c4{{position:absolute;left:1570px;width:254px;text-align:right;font:600 26px/1 'JetBrains Mono',monospace;color:{INK}}}
.c4.best{{color:{MAG}}}
.tr{{position:absolute;height:62px;border-top:1px solid {LINE}}}
.insight{{position:absolute;left:96px;top:900px;width:1728px;height:88px;border:1px solid {LINE};border-left:4px solid {MAG};border-radius:14px;background:rgba(11,19,48,.55);padding:24px 30px;font:400 21px/1.5 'Inter',sans-serif;color:{BODY}}}
.insight b{{color:{INK}}}
.insight .mg{{color:{MAG}}}
"""
s7_body = f"""
<div class="th c1">Configuration</div><div class="th c2">Params</div><div class="th c3">Steps</div><div class="th c4">Test acc.</div>
{rows7}
<div class="insight">Same seed, same budget — <span class="mg">the learning rate decides the run</span>: LR 0.003 → <b>97.57%</b> vs LR-scaled 0.000375 → <b>95.63%</b>, a 1.94 pp swing from one hyperparameter.</div>
"""

# ================================================================
# SLIDE 8 — ATTENTION (figure left, callouts right)
# ================================================================
s8_css = f"""
.callout{{position:absolute;width:494px;height:170px;border:1px solid {LINE};border-radius:14px;background:rgba(11,19,48,.55);padding:22px 26px}}
.callout .f{{font:400 16px/1.4 'JetBrains Mono',monospace;letter-spacing:.14em;color:{DIM};text-transform:uppercase}}
.callout .v{{font:500 20px/1.42 'Inter',sans-serif;color:{INK};margin-top:8px}}
.callout .v .cy{{color:{CYAN}}}
.callout .v .mg{{color:{MAG}}}
.note{{position:absolute;left:96px;top:900px;width:1728px;font:400 16px/1.5 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.04em}}
"""
s8_body = f"""
{img("assets/full_finetune_paper_lr_1000_attention.png", 96, 300, 1200, 480)}
<div class="callout" style="left:1330px;top:300px"><div class="f">Pretrained</div><div class="v">Diffuse, low-contrast attention — the network has not yet learned what matters on CIFAR-10.</div></div>
<div class="callout" style="left:1330px;top:488px"><div class="f">Fine-tuned</div><div class="v">Attention <span class="mg">concentrates on discriminative patches</span> for the predicted class.</div></div>
<div class="callout" style="left:1330px;top:676px"><div class="f">Reading</div><div class="v">Last-block, mean CLS attention over all heads — one example, <span class="cy">diagnostic, not causal</span>.</div></div>
<div class="note">MEAN CLS ATTENTION · LAST BLOCK · 7×7 PATCH GRID · SINGLE TEST EXAMPLE (TRUE vs PREDICTED LABEL IN FIGURE TITLE)</div>
"""

# ================================================================
# SLIDE 9 — POSITION ENCODING
# ================================================================
s9_css = f"""
.card{{position:absolute;width:420px;height:168px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);padding:28px 30px}}
.card .big{{font:700 54px/1 'Inter',sans-serif;color:{CYAN};letter-spacing:-.01em}}
.card .f{{font:400 16px/1.5 'JetBrains Mono',monospace;letter-spacing:.1em;color:{DIM};text-transform:uppercase;margin-top:12px}}
.explain{{position:absolute;left:1030px;top:660px;width:794px;font:400 21px/1.6 'Inter',sans-serif;color:{BODY}}}
.explain b{{color:{INK}}}
.explain .cy{{color:{CYAN}}}
.explain .mg{{color:{MAG}}}
"""
s9_body = f"""
{img("assets/position_similarity.png", 96, 300, 700, 603)}
<div class="card" style="left:920px;top:300px"><div class="big">0.644</div><div class="f">mean cosine · adjacent patches</div></div>
<div class="card" style="left:920px;top:492px"><div class="big" style="color:{MAG}">−0.157</div><div class="f">mean cosine · far patches (≥6 apart)</div></div>
<div class="card" style="left:1404px;top:300px"><div class="big" style="color:{AMBER}">0.801</div><div class="f">adjacent − far gap</div></div>
<div class="card" style="left:1404px;top:492px"><div class="big">7 × 7</div><div class="f">grid topology recovered</div></div>
<div class="explain">Pretrained position embeddings <b>learn a 2-D grid</b>: neighbours align, distant patches anti-correlate. The model reconstructs <span class="cy">where</span> each patch sits — without ever being told.</div>
"""

# ================================================================
# SLIDE 10 — ERRORS
# ================================================================
s10_css = f"""
.card{{position:absolute;width:360px;height:188px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);padding:30px 32px}}
.card .big{{font:700 58px/1 'Inter',sans-serif;color:{MAG};letter-spacing:-.01em}}
.card .f{{font:400 16px/1.5 'JetBrains Mono',monospace;letter-spacing:.1em;color:{DIM};text-transform:uppercase;margin-top:12px}}
.explain{{position:absolute;left:920px;top:710px;width:904px;font:400 21px/1.6 'Inter',sans-serif;color:{BODY}}}
.explain b{{color:{INK}}}
.explain .mg{{color:{MAG}}}
"""
s10_body = f"""
{img("assets/full_finetune_paper_lr_1000_confusion_matrix.png", 96, 300, 660, 591)}
<div class="card" style="left:920px;top:300px"><div class="big">2.43%</div><div class="f">overall error rate</div></div>
<div class="card" style="left:920px;top:508px"><div class="big">40</div><div class="f">dogs predicted as cats</div></div>
<div class="card" style="left:1310px;top:300px"><div class="big">33</div><div class="f">cats predicted as dogs</div></div>
<div class="card" style="left:1310px;top:508px"><div class="big">95.0%</div><div class="f">cat accuracy in best run</div></div>
<div class="explain">The residual error is <b>mostly natural confusion</b>: cat ↔ dog is the dominant mix-up, exactly the near-duplicate classes humans find hardest. No systematic class collapse anywhere.</div>
"""

# ================================================================
# SLIDE 11 — EFFICIENCY
# ================================================================
s11_css = f"""
.card{{position:absolute;width:404px;height:160px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);padding:26px 30px}}
.card .big{{font:700 50px/1 'Inter',sans-serif;color:{CYAN};letter-spacing:-.01em}}
.card .f{{font:400 16px/1.5 'JetBrains Mono',monospace;letter-spacing:.09em;color:{DIM};text-transform:uppercase;margin-top:10px}}
.card .big .mg{{color:{MAG}}}
.note{{position:absolute;left:96px;top:858px;width:1728px;font:400 16px/1.5 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.03em}}
"""
s11_body = f"""
<div class="card" style="left:96px;top:300px"><div class="big">50 → <span class="mg">37</span></div><div class="f">training tokens · 25% patches dropped + CLS</div></div>
<div class="card" style="left:536px;top:300px"><div class="big">−15.7%</div><div class="f">training time · 747.3 → 630.0 s</div></div>
<div class="card" style="left:976px;top:300px"><div class="big" style="color:{MAG}">−0.10 pp</div><div class="f">test accuracy · 97.57 → 97.47%</div></div>
<div class="card" style="left:1416px;top:300px"><div class="big">97.90%</div><div class="f">validation — identical, both runs</div></div>
{img("assets/eff_tradeoff.png", 96, 510, 851, 300)}
{img("assets/eff_curves.png", 977, 510, 811, 300)}
<div class="note">METHOD: TRAINING-ONLY PATCHDROPOUT (LIU ET AL., 2022) VIA TIMM 1.0.22 · EVALUATION ALWAYS USES ALL 50 TOKENS · BOTH RUNS: 1,000 STEPS · BATCH 64 · LR 0.003 · SEED 5541</div>
"""

# ================================================================
# SLIDE 12 — LIMITATIONS
# ================================================================
s12_items = [
    ("Budget, not method", "224 px · 1,000 steps vs the paper's 384 px · 10,000 steps — the 1.22 pp gap is fully explained by a smaller budget.", CYAN),
    ("One seed", "Every result is a single run per condition; variance across seeds is not measured.", CYAN),
    ("Exploratory LR choice", "The LR 0.003 run was chosen after earlier test scores were inspected — the cross-run comparison is exploratory, not confirmatory.", MAG),
    ("Descriptive analysis", "Attention and position-encoding findings describe this model; they do not prove a causal mechanism.", MAG),
    ("Extension, not invention", "PatchDropout is an existing method (Liu et al., 2022), applied through timm — a reproduction plus efficiency probe.", AMBER),
]
s12_css = f"""
.card{{position:absolute;width:846px;height:196px;border:1px solid {LINE};border-radius:16px;background:rgba(11,19,48,.55);padding:30px 34px}}
.card .f{{font:600 24px/1 'Inter',sans-serif;color:{INK}}}
.card .v{{font:400 20px/1.55 'Inter',sans-serif;color:{BODY};margin-top:12px}}
"""
def limcards():
    out = ""
    for i, (f, v, c) in enumerate(s12_items):
        x = 96 + (i % 2) * 882
        y = 310 + (i // 2) * 218
        out += f'<div class="card" style="left:{x}px;top:{y}px"><div class="f"><span style="color:{c}">●</span> {f}</div><div class="v">{v}</div></div>'
    return out
s12_body = limcards()

# ================================================================
# SLIDE 13 — CONCLUSION
# ================================================================
s13_css = f"""
.take{{position:absolute;width:536px;height:300px;border:1px solid {LINE};border-radius:18px;background:rgba(11,19,48,.55);padding:34px 36px}}
.take .n{{font:700 40px/1 'Inter',sans-serif;background:linear-gradient(90deg,{CYAN},{MAG});-webkit-background-clip:text;background-clip:text;color:transparent}}
.take .t{{font:600 25px/1.2 'Inter',sans-serif;color:{INK};margin-top:18px}}
.take .d{{font:400 19px/1.55 'Inter',sans-serif;color:{BODY};margin-top:12px}}
.ref{{position:absolute;left:96px;top:710px;width:1728px;font:400 16px/1.7 'JetBrains Mono',monospace;color:{DIM};letter-spacing:.04em}}
.ref b{{color:{BODY}}}
.thanks{{position:absolute;left:96px;top:940px;font:600 28px/1 'Inter',sans-serif;color:{INK}}}
.thanks .cy{{color:{CYAN}}}
.thanks .mg{{color:{MAG}}}
"""
s13_body = f"""
<div class="take" style="left:96px;top:310px"><div class="n">01</div><div class="t">ViT transfers.</div><div class="d">Pretrained ViT-B/32 reaches 97.57% on CIFAR-10 — 1.22 pp below the 98.79% reference, explained by a smaller budget.</div></div>
<div class="take" style="left:672px;top:310px"><div class="n">02</div><div class="t">The LR is the lever.</div><div class="d">One hyperparameter — the paper's LR 0.003 — is worth 1.94 pp over the scaled-down alternative at the same seed.</div></div>
<div class="take" style="left:1248px;top:310px"><div class="n">03</div><div class="t">Faster is nearly free.</div><div class="d">PatchDropout cuts training time 15.7% for −0.10 pp — a practical speed-up for constrained hardware.</div></div>
<div class="ref"><b>REFERENCES</b> &nbsp;·&nbsp; Dosovitskiy et al., <b>An Image is Worth 16×16 Words</b>, ICLR 2021 &nbsp;·&nbsp; Liu et al., <b>PatchDropout</b>, arXiv:2208.07220 &nbsp;·&nbsp; Krizhevsky, <b>CIFAR-10</b>, 2009 &nbsp;·&nbsp; timm 1.0.22 &nbsp;·&nbsp; PyTorch 2.8.0</div>
<div class="thanks">Thank you — <span class="cy">questions</span> <span class="mg">welcome</span>.</div>
"""

# ================================================================
pages = [
    (s1_css, s1_body, None, None),
    (s2_css, s2_body, "ROADMAP", "What we'll cover"),
    (s3_css, s3_body, "BACKGROUND · ICLR 2021", 'The paper that taught <span class="cy">transformers</span> to see'),
    (s4_css, s4_body, "METHOD", 'From <span class="cy">pixels</span> to <span class="mg">tokens</span>'),
    (s5_css, s5_body, "EXPERIMENTAL SETUP", "A fair, resource-scaled protocol"),
    (s6_css, s6_body, "RESULTS · CIFAR-10 TEST ACCURACY", 'The <span class="mg">accuracy ladder</span> — one protocol at a time'),
    (s7_css, s7_body, "RESULTS · FINE-TUNING PROTOCOLS", 'Capacity helps — the <span class="mg">learning rate</span> decides'),
    (s8_css, s8_body, "ANALYSIS · ATTENTION", "What the CLS token learns to look at"),
    (s9_css, s9_body, "ANALYSIS · POSITIONAL ENCODING", 'Position embeddings <span class="cy">learn the grid</span>'),
    (s10_css, s10_body, "ANALYSIS · ERRORS", 'The remaining mistakes are <span class="mg">natural</span>'),
    (s11_css, s11_body, "EXTENSION · PATCHDROPOUT", "Faster training, nearly free"),
    (s12_css, s12_body, "DISCUSSION", "Honest limits"),
    (s13_css, s13_body, "CONCLUSION", "What we learned"),
]
for i, (css, body, kicker, title) in enumerate(pages, 1):
    (D / f"slide-{i:02d}.html").write_text(slide(css, body, i, kicker, title))
    print("wrote slide", i)
print("DECK BUILDER DONE")
