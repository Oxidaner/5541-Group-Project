"""Create ViT feature, attention, and error-analysis figures."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import timm
from PIL import Image
from torchvision import transforms
from torchvision.datasets import CIFAR10

ROOT = Path(__file__).resolve().parent
MODEL = "vit_base_patch32_224.orig_in21k"
CHECKPOINT = ROOT / "artifacts/pretrained/ViT-B_32_imagenet21k.npz"
FIGURES = ROOT / "results/figures"
CLASSES = ("airplane", "automobile", "bird", "cat", "deer",
           "dog", "frog", "horse", "ship", "truck")


def model_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_model(run):
    model = timm.create_model(MODEL)
    model.load_pretrained(str(CHECKPOINT))
    model.reset_classifier(10)
    checkpoint = torch.load(ROOT / "results" / run / "best.pt",
                            map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["state_dict"])
    return model.to(model_device()).eval()


def position_plot():
    model = timm.create_model(MODEL)
    model.load_pretrained(str(CHECKPOINT))
    model.eval()
    position = model.pos_embed[0, 1:].float()
    assert position.shape == (49, 768)
    norm = torch.nn.functional.normalize(position, dim=-1)
    similarity = (norm @ norm.T).detach().cpu().numpy()
    grid = similarity.reshape(7, 7, 7, 7).transpose(0, 2, 1, 3).reshape(49, 49)
    # Match the flattened patch order used by the original sequence.
    edges = []
    for r in range(7):
        for c in range(7):
            i = r * 7 + c
            if r < 7 - 1:
                edges.append((i, i + 7))
            if c < 7 - 1:
                edges.append((i, i + 1))
    adjacent = np.array([similarity[i, j] for i, j in edges])
    i, j = np.triu_indices(49, k=1)
    distance = np.abs(i // 7 - j // 7) + np.abs(i % 7 - j % 7)
    far = similarity[i[distance >= 6], j[distance >= 6]]
    stats = {
        "adjacent_grid_edges": len(adjacent),
        "mean_cosine_adjacent": float(adjacent.mean()),
        "mean_cosine_far_manhattan_ge_6": float(far.mean()),
        "cosine_difference_adjacent_minus_far": float(adjacent.mean() - far.mean()),
        "min_cosine": float(similarity.min()),
        "max_cosine": float(similarity.max()),
    }
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 6.2), layout="constrained")
    im = ax.imshow(similarity, cmap="coolwarm", vmin=-0.5, vmax=1)
    ax.set(xlabel="Patch index", ylabel="Patch index",
           title="ViT-B/32 pretrained position-embedding similarity")
    fig.colorbar(im, ax=ax, label="Cosine similarity")
    fig.savefig(FIGURES / "position_similarity.png", dpi=170)
    plt.close(fig)
    (FIGURES / "position_similarity.json").write_text(
        json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2), flush=True)


def confusion_and_errors(run):
    prediction_path = (ROOT / "results/linear_probe_predictions.npz" if run == "linear_probe"
                       else ROOT / "results" / run / "predictions.npz")
    result = np.load(prediction_path)
    y, pred = result["labels"], result["predictions"]
    cm = np.zeros((10, 10), dtype=np.int64)
    np.add.at(cm, (y, pred), 1)
    row_sums = np.maximum(cm.sum(axis=1, keepdims=True), 1)
    normalized = cm / row_sums
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 7), layout="constrained")
    im = ax.imshow(normalized, cmap="Blues", vmin=0, vmax=1)
    ax.set(xticks=range(10), yticks=range(10), xticklabels=CLASSES,
           yticklabels=CLASSES, xlabel="Predicted class", ylabel="True class",
           title=f"{run}: normalized CIFAR-10 confusion matrix")
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right", rotation_mode="anchor")
    fig.colorbar(im, ax=ax, label="Fraction per true class")
    fig.savefig(FIGURES / f"{run}_confusion_matrix.png", dpi=170)
    plt.close(fig)
    per_class = {
        name: float(normalized[i, i]) for i, name in enumerate(CLASSES)
    }
    ranked = np.argsort(result["probabilities"].max(axis=1))
    wrong = ranked[y[ranked] != pred[ranked]][:12]
    ds = CIFAR10(ROOT / "data", train=False, download=False)
    fig, axes = plt.subplots(3, 4, figsize=(10, 7), layout="constrained")
    for ax, index in zip(axes.flat, wrong):
        image, _ = ds[int(index)]
        ax.imshow(image)
        confidence = float(result["probabilities"][index, pred[index]])
        ax.set_title(f"true {CLASSES[y[index]]}\npred {CLASSES[pred[index]]} ({confidence:.2f})",
                     fontsize=8)
        ax.axis("off")
    for ax in axes.flat[len(wrong):]:
        ax.axis("off")
    fig.suptitle(f"{run}: uncertain misclassified test images")
    fig.savefig(FIGURES / f"{run}_errors.png", dpi=170)
    plt.close(fig)
    metrics_path = (ROOT / "results/linear_probe.json" if run == "linear_probe"
                    else ROOT / "results" / run / "metrics.json")
    metrics = json.loads(metrics_path.read_text())
    metrics["per_class_accuracy"] = per_class
    metrics["confusion_matrix"] = cm.tolist()
    metrics_path.write_text(
        json.dumps(metrics, indent=2) + "\n")


def attention_plot(run):
    model = load_model(run)
    pretrained_model = timm.create_model(MODEL)
    pretrained_model.load_pretrained(str(CHECKPOINT))
    pretrained_model = pretrained_model.to(model_device()).eval()
    ds = CIFAR10(ROOT / "data", train=False, transform=transforms.Compose([
        transforms.Resize((224, 224)), transforms.ToTensor(),
        transforms.Normalize((0.5,) * 3, (0.5,) * 3),
    ]))
    image, label = ds[0]
    def cls_attention(current_model):
        captured = {}
        attention = current_model.blocks[-1].attn

        def capture_qkv(_module, _inputs, output):
            captured["qkv"] = output.detach()

        hook = attention.qkv.register_forward_hook(capture_qkv)
        with torch.inference_mode():
            logits = current_model(image.unsqueeze(0).to(model_device()))
        hook.remove()
        qkv = captured["qkv"].reshape(1, 50, 3, 12, 64).permute(2, 0, 3, 1, 4)
        q, k = qkv[0], qkv[1]
        if not isinstance(attention.q_norm, torch.nn.Identity):
            q = attention.q_norm(q)
        if not isinstance(attention.k_norm, torch.nn.Identity):
            k = attention.k_norm(k)
        weights = ((q * attention.scale) @ k.transpose(-2, -1)).softmax(dim=-1)
        heatmap = weights[0, :, 0, 1:].mean(dim=0).reshape(7, 7).cpu().numpy()
        return heatmap, logits

    pretrained_attention, _ = cls_attention(pretrained_model)
    finetuned_attention, logits = cls_attention(model)
    original = np.asarray(Image.fromarray(ds.data[0]).resize((224, 224)))
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8), layout="constrained")
    axes[0].imshow(original)
    axes[0].set_title("CIFAR-10 test image")
    shared_max = max(float(pretrained_attention.max()), float(finetuned_attention.max()))
    for ax, heatmap, title in ((axes[1], pretrained_attention, "Pretrained"),
                               (axes[2], finetuned_attention, "Fine-tuned")):
        overlay = ax.imshow(heatmap, cmap="magma", vmin=0, vmax=shared_max, interpolation="nearest")
        ax.set_title(f"{title} last-block\nmean CLS attention")
        ax.set_xlabel("Patch column")
        ax.set_ylabel("Patch row")
        ax.set_xticks(range(7))
        ax.set_yticks(range(7))
    fig.suptitle(f"ViT-B/32 attention, true {CLASSES[label]}, pred {CLASSES[logits.argmax(-1).item()]}")
    fig.colorbar(overlay, ax=axes[1:], fraction=0.046, label="Attention weight")
    axes[0].axis("off")
    fig.savefig(FIGURES / f"{run}_attention.png", dpi=180)
    plt.close(fig)


def compare_runs():
    names = (
        "linear_probe", "head_only", "last_block",
        "last_block_3000", "full_finetune",
        "full_finetune_lr_scaled_1000",
        "full_finetune_paper_lr_1000",
    )
    rows = []
    for name in names:
        path = (ROOT / "results/linear_probe.json" if name == "linear_probe"
                else ROOT / "results" / name / "metrics.json")
        if path.exists():
            data = json.loads(path.read_text())
            rows.append({"experiment": name, "test_accuracy": data["test_accuracy"],
                         "trainable_parameters": (data.get("backbone_trainable_parameters", 0) + data.get("head_parameters", 0))
                                                 if name == "linear_probe" else data["trainable_parameters"],
                         "steps": data.get("steps"),
                         "selected_step": data.get("selected_step"),
                         "validation_accuracy": (max(x["validation_accuracy"] for x in data["validation_candidates"])
                                                   if name == "linear_probe"
                                                   else data["best_validation_accuracy"]),
                         "paper_reference_accuracy": 0.9879,
                         "difference_percentage_points": 100 * (data["test_accuracy"] - 0.9879),
                         "seconds": data.get("search_and_fit_seconds", data.get("train_seconds_including_validation"))})
    if rows:
        (ROOT / "results/comparison.json").write_text(json.dumps(rows, indent=2) + "\n")
        fig, ax = plt.subplots(figsize=(11, 6.2), layout="constrained")
        label_map = {
            "linear_probe": "Frozen features + linear probe",
            "head_only": "Head only, 500 steps",
            "last_block": "Last block, 300 steps",
            "last_block_3000": "Last block, 3,000 steps",
            "full_finetune": "Full fine-tuning, 300 steps",
            "full_finetune_lr_scaled_1000": "Full fine-tuning, 1,000 steps",
            "full_finetune_paper_lr_1000": "Full fine-tuning, LR 0.003",
        }
        labels = [label_map.get(row["experiment"], row["experiment"].replace("_", " ")) for row in rows]
        values = [100 * row["test_accuracy"] for row in rows]
        colors = ["#6b7280" if row["experiment"].startswith("last_block")
                  else "#1877b9" if row["experiment"] in ("linear_probe", "full_finetune_lr_scaled_1000", "full_finetune_paper_lr_1000")
                  else "#9ca3af" for row in rows]
        ax.barh(labels, values, color=colors)
        ax.axvline(98.79, color="#bd3d3a", linestyle="--")
        ax.set(xlim=(90, 100), xlabel="CIFAR-10 test accuracy (%)",
               title="ViT-B/32 accuracy comparison (axis starts at 90%)")
        for bar, value in zip(ax.patches, values):
            ax.text(value - 0.5, bar.get_y() + bar.get_height() / 2, f"{value:.2f}%",
                    ha="right", va="center", fontsize=8,
                    color="white" if value > 95 else "#172B4D")
        FIGURES.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES / "test_accuracy_comparison.png", dpi=180)
        plt.close(fig)
        print(json.dumps(rows, indent=2), flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="full_finetune")
    parser.add_argument("--analysis", choices=("position", "predictions", "attention", "all"), default="all")
    args = parser.parse_args()
    if args.analysis in ("position", "all"):
        position_plot()
    if args.analysis in ("predictions", "all"):
        confusion_and_errors(args.run)
    if args.analysis in ("attention", "all"):
        attention_plot(args.run)
    if args.analysis == "all":
        compare_runs()
