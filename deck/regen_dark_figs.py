# -*- coding: utf-8 -*-
"""Regenerate key figures in the dark 'Attention Field' style using the project venv."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = pathlib.Path("deck/assets")
OUT.mkdir(parents=True, exist_ok=True)
ROOT = pathlib.Path("results")

# ---------------- dark style ----------------
DARK = {
    "figure.facecolor": "#080F28",
    "savefig.facecolor": "#080F28",
    "axes.facecolor": "#0B1330",
    "axes.edgecolor": "#8FA0C4",
    "axes.labelcolor": "#EAF2FF",
    "text.color": "#EAF2FF",
    "xtick.color": "#9AA8C7",
    "ytick.color": "#9AA8C7",
    "grid.color": "#2A3A66",
    "grid.alpha": 0.35,
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "figure.titlesize": 13,
}
plt.rcParams.update(DARK)

CYAN = "#7CF0FF"
MAG = "#FF7AE0"
AMBER = "#FFB454"
BLUE = "#63C7FF"

def efficiency_figures():
    comp = json.loads((ROOT / "efficiency_comparison.json").read_text())
    base, mod = comp["conditions"]
    hist = []
    for name in (base["name"], mod["name"]):
        rows = [json.loads(l) for l in (ROOT / name / "history.jsonl").read_text().splitlines()]
        hist.append(rows)
    colors = [BLUE, MAG]
    labels = ["Baseline", "PatchDropout 25%"]
    times = [base["train_seconds_including_validation"], mod["train_seconds_including_validation"]]
    red = comp["train_time_reduction_fraction"]
    scores = [base["test_accuracy"] * 100, mod["test_accuracy"] * 100]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), layout="constrained")
    axes[0].barh(range(2), times, color=colors, height=0.5)
    axes[0].set(yticks=range(2), yticklabels=labels, xlim=(0, max(times) * 1.22),
                xlabel="Training + validation + checkpoint I/O (s)",
                title=f"Training time: {red*100:.1f}% reduction")
    axes[0].invert_yaxis()
    for i, value in enumerate(times):
        axes[0].text(value + 5, i, f"{value:.1f}", va="center", fontsize=10)
    for i, result in enumerate((base, mod)):
        axes[1].scatter(result["test_accuracy"] * 100, i, color=colors[i], s=85)
        axes[1].annotate(f'{result["test_accuracy"]*100:.2f}%',
                         (result["test_accuracy"] * 100, i), xytext=(0, 12),
                         textcoords="offset points", ha="center")
    axes[1].set(yticks=range(2), yticklabels=labels, ylim=(-.6, 1.6),
                xlim=(min(scores) - .5, max(scores) + .5),
                xlabel="Official CIFAR-10 test accuracy (%)",
                title="Accuracy after validation selection")
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=.2)
    fig.savefig(OUT / "eff_tradeoff.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout="constrained")
    for name, history, color in zip(labels, hist, colors):
        rows = [r for r in history if "validation_accuracy" in r]
        for ax, x_key in zip(axes, ("step", "elapsed_seconds")):
            ax.plot([r[x_key] for r in rows], [100 * r["validation_accuracy"] for r in rows],
                    "o-", label=name, color=color)
            ax.set(ylabel="Validation accuracy (%)")
            ax.grid(alpha=.2)
    axes[0].set(xlabel="Training step", title="Same 1,000-step training budget")
    axes[1].set(xlabel="Elapsed training time (s)", title="Validation accuracy versus time")
    axes[1].legend(fontsize=8)
    fig.savefig(OUT / "eff_curves.png", dpi=180)
    plt.close(fig)
    print("efficiency figures done")

# ---------------- reuse analyze_results for model-based figures ----------------
import analyze_results as ar
ar.FIGURES = OUT

def position():
    ar.position_plot()
    print("position done")

def attention():
    ar.attention_plot("full_finetune_paper_lr_1000")
    print("attention done")

def confusion():
    ar.confusion_and_errors("full_finetune_paper_lr_1000")
    print("confusion done")

if __name__ == "__main__":
    efficiency_figures()
    position()
    attention()
    confusion()
    print("ALL DONE")
