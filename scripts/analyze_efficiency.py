"""Validate the controlled comparison and draw accuracy/runtime tradeoffs."""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from vit_experiment import RESULTS, write_json


def read(path):
    return json.loads(path.read_text())


def main():
    names = ("efficiency_baseline_1000", "efficiency_patchdrop25_1000")
    configs = [read(RESULTS / name / "config.json") for name in names]
    metrics = [read(RESULTS / name / "metrics.json") for name in names]
    histories = [[json.loads(line) for line in (RESULTS / name / "history.jsonl").read_text().splitlines()]
                 for name in names]
    ignored = {"name", "patch_drop_rate", "training_tokens"}
    assert {k: v for k, v in configs[0].items() if k not in ignored} == {
        k: v for k, v in configs[1].items() if k not in ignored
    }, "The controlled configurations differ beyond patch dropout."
    predictions = [np.load(RESULTS / name / "predictions.npz") for name in names]
    y = predictions[0]["labels"]
    assert len(y) == 10_000
    np.testing.assert_array_equal(y, predictions[1]["labels"])
    correct = []
    for name, config, result, history, pred in zip(names, configs, metrics, histories, predictions):
        assert config["defer_test"]
        assert result["test_size"] == len(y)
        assert np.isfinite(pred["probabilities"]).all()
        np.testing.assert_allclose(pred["probabilities"].sum(axis=1), 1, atol=1e-5)
        is_correct = pred["predictions"] == y
        correct.append(is_correct)
        assert result["test_accuracy"] == is_correct.mean()
        validation = [row for row in history if "validation_accuracy" in row]
        best = max(validation, key=lambda row: row["validation_accuracy"])
        assert best["step"] == result["selected_step"]
        assert best["validation_accuracy"] == result["best_validation_accuracy"]
        assert max(row["step"] for row in history) == config["steps"]
    baseline, modified = metrics
    runtime_reduction = 1 - modified["train_seconds_including_validation"] / baseline["train_seconds_including_validation"]
    val_difference = 100 * (modified["best_validation_accuracy"] - baseline["best_validation_accuracy"])
    old = np.load(RESULTS / "full_finetune_paper_lr_1000/predictions.npz")
    old_history = [json.loads(line) for line in
                   (RESULTS / "full_finetune_paper_lr_1000/history.jsonl").read_text().splitlines()]
    def without_time(rows):
        return [{k: v for k, v in row.items() if k != "elapsed_seconds"} for row in rows]
    summary = {
        "method": "training-only PatchDropout, rate 0.25, timm 1.0.22",
        "conditions": metrics,
        "train_time_reduction_fraction": runtime_reduction,
        "train_speedup_ratio": baseline["train_seconds_including_validation"] / modified["train_seconds_including_validation"],
        "saved_training_seconds": baseline["train_seconds_including_validation"] - modified["train_seconds_including_validation"],
        "validation_difference_percentage_points": val_difference,
        "test_difference_percentage_points": 100 * (modified["test_accuracy"] - baseline["test_accuracy"]),
        "predefined_goal_met": bool(runtime_reduction >= .1 and val_difference >= -.3 - 1e-9),
        "paired_test_counts": {
            "both_correct": int(np.sum(correct[0] & correct[1])),
            "baseline_only_correct": int(np.sum(correct[0] & ~correct[1])),
            "patchdrop_only_correct": int(np.sum(~correct[0] & correct[1])),
            "both_wrong": int(np.sum(~correct[0] & ~correct[1])),
        },
        "baseline_historical_prediction_disagreements": int(np.sum(old["predictions"] != predictions[0]["predictions"])),
        "baseline_historical_history_equal_excluding_time": without_time(old_history) == without_time(histories[0]),
        "timing_scope": "1,000 training steps including loading, validation and checkpoint writes; excludes initialization and final test",
        "limitations": "One seed and one complete run per condition; same previously inspected CIFAR-10 test set; exploratory, not significance evidence; no inference or measured peak-memory improvement claimed.",
    }
    write_json(RESULTS / "efficiency_comparison.json", summary)

    fig_dir = RESULTS / "figures"
    fig_dir.mkdir(exist_ok=True)
    colors = ["#1877B9", "#D66B31"]
    labels = ["Baseline\n50 training tokens", "PatchDropout 25%\n37 training tokens"]
    times = [r["train_seconds_including_validation"] for r in metrics]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), layout="constrained")
    axes[0].barh(range(2), times, color=colors, height=.5)
    axes[0].set(yticks=range(2), yticklabels=labels, xlim=(0, max(times)*1.22),
                xlabel="Training + validation + checkpoint I/O (s)",
                title=f"Training time: {runtime_reduction*100:.1f}% reduction")
    axes[0].invert_yaxis()
    for i, value in enumerate(times):
        axes[0].text(value+5, i, f"{value:.1f}", va="center", fontsize=10)
    for i, result in enumerate(metrics):
        axes[1].scatter(result["test_accuracy"]*100, i, color=colors[i], s=85)
        axes[1].annotate(f'{result["test_accuracy"]*100:.2f}%',
                         (result["test_accuracy"]*100, i), xytext=(0, 12),
                         textcoords="offset points", ha="center")
    scores = [r["test_accuracy"]*100 for r in metrics]
    axes[1].set(yticks=range(2), yticklabels=["Baseline", "PatchDropout"],
                ylim=(-.6, 1.6), xlim=(min(scores)-.5, max(scores)+.5),
                xlabel="Official CIFAR-10 test accuracy (%)",
                title="Accuracy after validation selection")
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=.2)
    fig.savefig(fig_dir / "efficiency_tradeoff.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7), layout="constrained")
    for name, history, color in zip(("Baseline", "PatchDropout 25%"), histories, colors):
        rows = [row for row in history if "validation_accuracy" in row]
        for ax, x_key in zip(axes, ("step", "elapsed_seconds")):
            ax.plot([r[x_key] for r in rows], [100*r["validation_accuracy"] for r in rows],
                    "o-", label=name, color=color)
            ax.set(ylabel="Validation accuracy (%)")
            ax.grid(alpha=.2)
    axes[0].set(xlabel="Training step", title="Same 1,000-step training budget")
    axes[1].set(xlabel="Elapsed training time (s)", title="Validation accuracy versus time")
    axes[1].legend(fontsize=8)
    fig.savefig(fig_dir / "efficiency_validation_curves.png", dpi=180)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
