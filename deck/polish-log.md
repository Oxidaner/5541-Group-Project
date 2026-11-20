# Polish Log — COMP5541 ViT deck (Direction C)

- Direction: C — Attention Field (deep blue / cyan-magenta glow). Approved by user: "C吧".
- Deliverable: 13 slides, 1920x1080, all English, HTML -> PPTX.

## Round 1 (draft -> full deck)
Built 13 slides, regenerated all result figures in a matching dark style
(magma attention & confusion, coolwarm position similarity, cyan/magenta efficiency charts).
Tooling note: this runtime's model cannot view images, so visual polish is done
programmatically — pixel sampling (Pillow) + Chrome DevTools Protocol geometry checks.

Verified:
- Every slide renders at exactly 1920x1080, body has no scroll (scrollW/H = 1920x1080).
- Kicker + title text present on all 13 slides (pixel sampling of text regions).
- Figure slides contain real content in their expected regions (attention, position,
  confusion, tradeoff, curves).
- Accent colors present where expected (cyan kicker, magenta best-bar / big number).
- No element overflows the canvas (CDP: 0 text-overflow, 0 layout overflow;
  only the intentional cover glow circle is clipped by design).

## Round 2 (fixes applied)
- Added missing kicker + title to slides 2-13 (initial pass only had cover/partial titles).
- Redrew confusion matrix in magma (dark-friendly) instead of Blues (invisible diagonal on dark).
- Bumped figure fonts (confusion, position, efficiency) for readability at display size.
- Rebalanced slide 8 (attention: figure left, three callouts right) and slide 11
  (two efficiency figures side by side at equal height).
- Re-checked geometry after fixes: clean.

## Known caveats
- Deck text is baked into slide images (full-bleed PNGs) for design fidelity; the
  PPTX is image-based, not editable text.
- Attention slide uses one test example (true vs predicted label) — noted on-slide.
