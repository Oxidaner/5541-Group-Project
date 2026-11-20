"""Real inference demo for screen recording; preserves original experiment files."""

import io
import base64
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

from vit_experiment import ROOT, backbone, dataset, device, seed_everything, synchronize, write_json

OUT = ROOT / "output/recording"
RUNS = (("efficiency_baseline_1000", "ViT-B/32 baseline"),
        ("efficiency_patchdrop25_1000", "PatchDropout 25%"))
CLASSES = ("airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck")


def emit(event, **data):
    # Human-readable process output is captured verbatim beside structured UI events.
    if event == "environment":
        print(f"$ {sys.executable} -m scripts.recording_run\n"
              f"Working directory: {ROOT}\n"
              f"Process PID: {os.getpid()}\n"
              f"Python {data['python']} | PyTorch {data['torch']}\n"
              f"Platform: {platform.system()} {platform.machine()}\n"
              f"Device: {data['device'].upper()} | Model: {data['model']}\n"
              "CIFAR-10: 10,000 test images per model", flush=True)
    elif event == "message":
        print(data["text"], flush=True)
    elif event == "start":
        print(f"\n[{data['index'] + 1}/2] {data['label']} | checkpoint step {data['step']}", flush=True)
    elif event == "progress":
        print(f"  {data['done']:5,} / {data['total']:,} images | {data['seconds']:.1f} s", flush=True)
    elif event == "result":
        print(f"PASS: {data['correct']:,}/{data['total']:,} correct | {data['accuracy']:.2%}\n"
              f"Saved experiment prediction differences: {data['historical_prediction_disagreements']}", flush=True)
    elif event == "complete":
        print("\nSaved: output/recording/live_verification.json\n"
              "Both full test evaluations completed.", flush=True)
    print(json.dumps({"event": event, **data}), flush=True)


@torch.inference_mode()
def evaluate_live(model, loader, dev, label):
    model.eval()
    all_labels, all_predictions = [], []
    synchronize(dev)
    started = time.perf_counter()
    for images, targets in loader:
        logits = model(images.to(dev))
        predictions = logits.argmax(dim=1).cpu().numpy()
        all_labels.extend(targets.numpy().tolist())
        all_predictions.extend(predictions.tolist())
        done = len(all_labels)
        if done % 1024 == 0 or done == len(loader.dataset):
            emit("progress", label=label, done=done, total=len(loader.dataset),
                 seconds=round(time.perf_counter() - started, 1))
    synchronize(dev)
    seconds = time.perf_counter() - started
    y, pred = np.asarray(all_labels), np.asarray(all_predictions)
    return y, pred, seconds


def main():
    seed_everything()
    OUT.mkdir(parents=True, exist_ok=True)
    dev = device()
    emit("environment", device=str(dev), python=platform.python_version(),
         torch=torch.__version__, model="ViT-B/32", dataset="Official CIFAR-10 test split", size=10000)
    emit("message", text="Loading local ImageNet-21k ViT-B/32 architecture and trained checkpoint...")
    model = backbone()
    model.reset_classifier(10)
    model.to(dev)
    ds = dataset(False)
    assert len(ds) == 10000
    loader = DataLoader(ds, batch_size=64, num_workers=2)
    rows = []
    for index, (run, label) in enumerate(RUNS):
        checkpoint = torch.load(ROOT / "results" / run / "best.pt", map_location="cpu", weights_only=True)
        model.load_state_dict(checkpoint["state_dict"])
        emit("start", index=index, label=label, step=checkpoint["step"],
             text=f"Loaded validation-selected step {checkpoint['step']}. Evaluating all 10,000 test images.")
        y, pred, seconds = evaluate_live(model, loader, dev, label)
        previous = np.load(ROOT / "results" / run / "predictions.npz")
        np.testing.assert_array_equal(y, previous["labels"])
        disagreements = int(np.count_nonzero(pred != previous["predictions"]))
        accuracy = float((y == pred).mean())
        np.savez(OUT / f"{run}_live_predictions.npz", labels=y, predictions=pred)
        row = {"label": label, "correct": int(np.sum(y == pred)), "total": len(y),
               "accuracy": accuracy, "seconds": seconds, "selected_step": checkpoint["step"],
               "historical_prediction_disagreements": disagreements}
        rows.append(row)
        emit("result", index=index, **row)
        if index == 0:
            raw = __import__("torchvision").datasets.CIFAR10(ROOT / "data", train=False)
            examples = []
            for i in (0, 1, 2, 3, 4, 5):
                image, target = raw[i]
                buffer = io.BytesIO()
                image.resize((128, 128), Image.Resampling.NEAREST).save(buffer, format="PNG")
                examples.append({"image": base64.b64encode(buffer.getvalue()).decode(),
                                 "truth": CLASSES[target], "prediction": CLASSES[pred[i]]})
            emit("examples", items=examples)
        del checkpoint
    efficiency = json.loads((ROOT / "results/efficiency_comparison.json").read_text())
    result = {"live_evaluation": rows,
              "historical_training_seconds": [r["train_seconds_including_validation"] for r in efficiency["conditions"]],
              "historical_training_time_reduction": efficiency["train_time_reduction_fraction"],
              "scope": "Live inference of retained checkpoints, not retraining; train times are from previous recorded experiments."}
    write_json(OUT / "live_verification.json", result)
    emit("complete", **result)


if __name__ == "__main__":
    main()
