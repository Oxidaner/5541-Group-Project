# -*- coding: utf-8 -*-
"""Redraw the confusion matrix in a dark-friendly colormap (mako)."""
import json, pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.facecolor": "#080F28", "savefig.facecolor": "#080F28",
    "axes.facecolor": "#0B1330", "axes.edgecolor": "#8FA0C4",
    "axes.labelcolor": "#EAF2FF", "text.color": "#EAF2FF",
    "xtick.color": "#9AA8C7", "ytick.color": "#9AA8C7",
    "font.size": 10,
})
CLASSES = ("airplane","automobile","bird","cat","deer","dog","frog","horse","ship","truck")
m = json.loads(pathlib.Path("results/full_finetune_paper_lr_1000/metrics.json").read_text())
cm = np.array(m["confusion_matrix"], dtype=float)
norm = cm / cm.sum(axis=1, keepdims=True)
fig, ax = plt.subplots(figsize=(7.2, 6.4), layout="constrained")
im = ax.imshow(norm, cmap="magma", vmin=0, vmax=1)
ax.set_xticks(range(10)); ax.set_yticks(range(10))
ax.set_xticklabels(CLASSES, rotation=40, ha="right", rotation_mode="anchor")
ax.set_yticklabels(CLASSES)
ax.set_xlabel("Predicted class"); ax.set_ylabel("True class")
ax.set_title("Full fine-tune (paper LR) — fraction per true class", pad=10)
cbar = fig.colorbar(im, ax=ax, fraction=0.046)
cbar.set_label("Fraction per true class")
fig.savefig("deck/assets/full_finetune_paper_lr_1000_confusion_matrix.png", dpi=170)
plt.close(fig)
print("confusion redrawn")
