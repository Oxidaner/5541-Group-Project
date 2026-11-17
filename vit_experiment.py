"""ViT-B/32 transfer to CIFAR-10, with reproducible logs and held-out validation."""

import argparse
import concurrent.futures
import hashlib
import importlib.metadata
import json
import math
import platform
import random
import time
from pathlib import Path

import numpy as np
import requests
import timm
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from torchvision.datasets import CIFAR10

ROOT = Path(__file__).resolve().parent
MODEL = "vit_base_patch32_224.orig_in21k"
REPO = "timm/vit_base_patch32_224.orig_in21k"
REVISION = "4bfd55b246f2c4e4ae72d65fcaf84b6faca1cd90"
SEED = 5541
PRETRAINED = ROOT / "artifacts/pretrained"
CACHE = ROOT / "artifacts/features"
RESULTS = ROOT / "results"
WEIGHT_URL = "https://storage.googleapis.com/vit_models/imagenet21k/ViT-B_32.npz"
CIFAR_URL = "https://cave.cs.toronto.edu/kriz/cifar-10-python.tar.gz"
WEIGHT_SHA256 = "c0483c8051e6c5da8b644ccc85a586281e9cf32227d793074279e3f130db19d3"
CIFAR_SHA256 = "6d958be074577803d12ecdefd02955f39262c83c16fe9348329d7fe0b5c001ce"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def log(**data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def synchronize(dev):
    if dev.type == "mps":
        torch.mps.synchronize()
    elif dev.type == "cuda":
        torch.cuda.synchronize()


def seed_everything():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(6)


def transform(train=False):
    # The authors resize the whole evaluation image, rather than center-crop it.
    spatial = (
        [transforms.RandomResizedCrop(224, scale=(0.05, 1.0)),
         transforms.RandomHorizontalFlip()]
        if train else [transforms.Resize((224, 224))]
    )
    return transforms.Compose(spatial + [
        transforms.ToTensor(), transforms.Normalize((0.5,) * 3, (0.5,) * 3)
    ])


def dataset(train, augment=False):
    return CIFAR10(ROOT / "data", train=train, transform=transform(augment))


def split_indices(labels):
    train, val = train_test_split(
        np.arange(len(labels)), test_size=0.02, random_state=SEED,
        stratify=labels,
    )
    assert not np.intersect1d(train, val).size
    assert len(train) + len(val) == len(labels)
    return train, val


def backbone():
    model = timm.create_model(MODEL)
    model.load_pretrained(str(PRETRAINED / "ViT-B_32_imagenet21k.npz"))
    return model


def environment():
    return {
        "python": platform.python_version(), "platform": platform.platform(),
        "device": str(device()), "seed": SEED, "model": MODEL,
        "pretrained_revision": REVISION,
        "packages": {p: importlib.metadata.version(p) for p in (
            "torch", "torchvision", "timm", "numpy", "scikit-learn",
            "matplotlib", "requests",
        )},
    }


def prepare(_):
    PRETRAINED.mkdir(parents=True, exist_ok=True)
    weight = PRETRAINED / "ViT-B_32_imagenet21k.npz"
    resumable_download(WEIGHT_URL, weight, 419_441_810, WEIGHT_SHA256)
    write_json(PRETRAINED / "provenance.json", {
        "model_config": REPO, "repository_revision": REVISION,
        "weight_source": WEIGHT_URL,
        "weight_size_bytes": weight.stat().st_size,
        "weight_sha256": hashlib.file_digest(weight.open("rb"), "sha256").hexdigest(),
    })
    for train in (True, False):
        ds = CIFAR10(ROOT / "data", train=train, download=False)
        log(split="train" if train else "test", size=len(ds))
    write_json(RESULTS / "environment.json", environment())


def resumable_download(url, path, total, expected_sha256, chunks=8):
    path.parent.mkdir(parents=True, exist_ok=True)
    def verified():
        if not path.exists() or path.stat().st_size != total:
            return False
        with path.open("rb") as source:
            return hashlib.file_digest(source, "sha256").hexdigest() == expected_sha256
    if verified():
        log(event="download_verified", filename=path.name, size_bytes=total)
        return
    part_size = (total + chunks - 1) // chunks

    def fetch(i):
        start = i * part_size
        end = min(total, start + part_size) - 1
        part = path.with_name(path.name + f".part{i:02d}")
        current = part.stat().st_size if part.exists() else 0
        if current > end - start + 1:
            part.unlink()
            current = 0
        cursor = start + current
        while cursor <= end:
            headers = {"Range": f"bytes={cursor}-{end}"}
            with requests.get(url, headers=headers, stream=True, timeout=(30, 90)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError(f"Server ignored byte range: HTTP {response.status_code}")
                actual_range = response.headers.get("Content-Range", "")
                if not actual_range.startswith(f"bytes {cursor}-{end}/"):
                    raise RuntimeError(f"Unexpected Content-Range: {actual_range}")
                with part.open("ab") as output:
                    for block in response.iter_content(chunk_size=2**20):
                        if block:
                            output.write(block)
                            cursor += len(block)
        if part.stat().st_size != end - start + 1:
            raise RuntimeError(f"Incorrect download part size: {part}")
        log(event="download_part", filename=part.name, size_bytes=part.stat().st_size)
        return part

    with concurrent.futures.ThreadPoolExecutor(max_workers=chunks) as pool:
        parts = list(pool.map(fetch, range(chunks)))
    with path.open("wb") as output:
        for part in parts:
            with part.open("rb") as source:
                while block := source.read(2**20):
                    output.write(block)
    if not verified():
        raise RuntimeError(f"Downloaded file size or SHA-256 mismatch: {path}")
    for part in parts:
        part.unlink()


def benchmark(_):
    dev = device()
    model = backbone().to(dev).eval()
    assert len(model.blocks) == 12
    assert model.patch_embed.patch_size == (32, 32)
    assert model.pos_embed.shape == (1, 50, 768)
    assert isinstance(model.head, torch.nn.Identity)
    rows = []
    for n in (16, 32, 64):
        x = torch.randn(n, 3, 224, 224, device=dev)
        with torch.inference_mode():
            for _ in range(2):
                output = model(x)
            synchronize(dev)
            start = time.perf_counter()
            for _ in range(5):
                model(x)
            synchronize(dev)
        seconds = (time.perf_counter() - start) / 5
        row = {"batch_size": n, "seconds": seconds, "images_per_second": n / seconds}
        rows.append(row)
        log(**row)
        assert output.shape == (n, 768) and torch.isfinite(output).all()
    model.reset_classifier(10)
    model = model.to(dev)
    torch.nn.init.zeros_(model.head.weight)
    torch.nn.init.zeros_(model.head.bias)
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.003, momentum=0.9)
    x = torch.randn(32, 3, 224, 224, device=dev)
    y = torch.arange(32, device=dev) % 10
    train_rows = []
    for step in range(4):
        synchronize(dev)
        start = time.perf_counter()
        optimizer.zero_grad()
        loss = torch.nn.functional.cross_entropy(model(x), y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        synchronize(dev)
        row = {"training_step": step, "batch_size": 32,
               "seconds": time.perf_counter() - start, "loss": loss.item()}
        train_rows.append(row)
        log(**row)
    write_json(RESULTS / "benchmark.json", {"inference": rows, "training": train_rows})


def extract(args):
    CACHE.mkdir(parents=True, exist_ok=True)
    dev = device()
    model = backbone().to(dev).eval()
    write_json(RESULTS / "environment.json", environment())
    for train in (True, False):
        split = "train" if train else "test"
        ds = dataset(train)
        path = CACHE / f"{split}.npy"
        meta_path = CACHE / f"{split}.json"
        if meta_path.exists():
            log(event="cache_exists", split=split)
            continue
        loader = DataLoader(ds, batch_size=args.batch_size, num_workers=2)
        features = np.lib.format.open_memmap(path, mode="w+", shape=(len(ds), 768), dtype="float32")
        synchronize(dev)
        start = time.perf_counter()
        offset = 0
        with torch.inference_mode():
            for images, _ in loader:
                z = model(images.to(dev)).cpu().numpy()
                features[offset:offset + len(z)] = z
                offset += len(z)
                if offset % (args.batch_size * 20) == 0:
                    log(event="extract", split=split, completed=offset, total=len(ds),
                        seconds=round(time.perf_counter() - start, 2))
        features.flush()
        assert offset == len(ds) and np.isfinite(features).all()
        np.save(CACHE / f"{split}_labels.npy", ds.targets)
        seconds = time.perf_counter() - start
        meta = {"split": split, "size": len(ds), "seconds": seconds,
                "images_per_second": len(ds) / seconds, "revision": REVISION,
                "dtype": "float32", "preprocess": "resize_224_bilinear_normalize_minus1_plus1"}
        write_json(meta_path, meta)
        log(event="extract_complete", **meta)


def probe(_):
    import joblib
    from threadpoolctl import threadpool_limits

    x = np.load(CACHE / "train.npy", mmap_mode="r")
    y = np.load(CACHE / "train_labels.npy")
    train, val = split_indices(y)
    np.savez(RESULTS / "split_indices.npz", train=train, val=val)
    candidates = []
    start = time.perf_counter()
    # Test features are intentionally not loaded until validation selection ends.
    with threadpool_limits(limits=6):
        for c in (0.001, 0.01, 0.1, 1.0):
            clf = make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=400))
            fit_start = time.perf_counter()
            clf.fit(x[train], y[train])
            score = accuracy_score(y[val], clf.predict(x[val]))
            row = {"C": c, "validation_accuracy": score,
                   "fit_seconds": time.perf_counter() - fit_start}
            candidates.append(row)
            log(event="probe_validation", **row)
        best = max(candidates, key=lambda row: row["validation_accuracy"])
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=best["C"], max_iter=400))
        fit_start = time.perf_counter()
        clf.fit(x, y)
    fit_seconds = time.perf_counter() - fit_start
    joblib.dump(clf, RESULTS / "linear_probe.joblib")
    test_x = np.load(CACHE / "test.npy", mmap_mode="r")
    test_y = np.load(CACHE / "test_labels.npy")
    predict_start = time.perf_counter()
    predictions = clf.predict(test_x)
    prediction_seconds = time.perf_counter() - predict_start
    np.savez(RESULTS / "linear_probe_predictions.npz", labels=test_y, predictions=predictions,
             probabilities=clf.predict_proba(test_x))
    result = {"method": "frozen_backbone_linear_probe", "validation_candidates": candidates,
              "selected_C": best["C"], "test_accuracy": accuracy_score(test_y, predictions),
              "train_size": len(y), "validation_size": len(val), "test_size": len(test_y),
              "final_fit_seconds": fit_seconds, "test_head_seconds": prediction_seconds,
              "search_and_fit_seconds": time.perf_counter() - start,
              "backbone_trainable_parameters": 0, "head_parameters": 769 * 10,
              "protocol": "extension: standardized frozen features with logistic regression"}
    write_json(RESULTS / "linear_probe.json", result)
    log(event="probe_complete", **result)


@torch.inference_mode()
def evaluate(model, loader, dev):
    model.eval()
    labels, predictions, probabilities = [], [], []
    for images, targets in loader:
        scores = model(images.to(dev)).softmax(dim=-1).cpu()
        labels.append(targets.numpy())
        predictions.append(scores.argmax(dim=-1).numpy())
        probabilities.append(scores.numpy())
    return {"labels": np.concatenate(labels), "predictions": np.concatenate(predictions),
            "probabilities": np.concatenate(probabilities)}


def finetune(args):
    dev = device()
    run_dir = RESULTS / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
    model = backbone()
    model.reset_classifier(10)
    model = model.to(dev)
    torch.nn.init.zeros_(model.head.weight)
    torch.nn.init.zeros_(model.head.bias)
    if args.mode in ("head", "last_block"):
        model.requires_grad_(False)
        if args.mode == "last_block":
            model.blocks[-1].requires_grad_(True)
            model.norm.requires_grad_(True)
        model.head.requires_grad_(True)
    params = [p for p in model.parameters() if p.requires_grad]
    ds = dataset(True, augment=True)
    train_idx, val_idx = split_indices(ds.targets)
    train_ds = Subset(ds, train_idx)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(Subset(dataset(True), val_idx), batch_size=args.batch_size, num_workers=2)
    optimizer = torch.optim.SGD(params, lr=args.lr, momentum=0.9)
    config = {**vars(args), **environment(), "train_size": len(train_ds),
              "validation_size": len(val_idx), "input_size": 224,
              "trainable_parameters": sum(p.numel() for p in params),
              "total_parameters": sum(p.numel() for p in model.parameters()),
              "warmup_steps": max(1, args.steps // 10),
              "paper_reference_accuracy": 0.9879,
              "protocol": "resource-scaled fine-tuning; differs from paper resolution and budget"}
    write_json(run_dir / "config.json", config)
    log(event="finetune_start", **config)
    step = 0
    start = time.perf_counter()
    best_val = -1
    with (run_dir / "history.jsonl").open("w") as history:
        while step < args.steps:
            model.train()
            for images, targets in train_loader:
                step += 1
                warmup = config["warmup_steps"]
                progress = max(0, step - warmup) / max(1, args.steps - warmup)
                factor = step / warmup if step <= warmup else 0.5 * (1 + math.cos(math.pi * progress))
                for group in optimizer.param_groups:
                    group["lr"] = args.lr * factor
                optimizer.zero_grad()
                loss = torch.nn.functional.cross_entropy(model(images.to(dev)), targets.to(dev))
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                optimizer.step()
                if step % 20 == 0 or step == 1:
                    row = {"step": step, "loss": loss.item(), "lr": optimizer.param_groups[0]["lr"],
                           "elapsed_seconds": time.perf_counter() - start}
                    history.write(json.dumps(row) + "\n")
                    history.flush()
                    log(event="train", **row)
                if step % args.eval_every == 0 or step == args.steps:
                    pred = evaluate(model, val_loader, dev)
                    score = accuracy_score(pred["labels"], pred["predictions"])
                    row = {"step": step, "validation_accuracy": score,
                           "elapsed_seconds": time.perf_counter() - start}
                    history.write(json.dumps(row) + "\n")
                    history.flush()
                    log(event="validation", **row)
                    if score > best_val:
                        best_val = score
                        torch.save({"state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
                                    "step": step, "validation_accuracy": score}, run_dir / "best.pt")
                    model.train()
                if step >= args.steps:
                    break
    train_seconds = time.perf_counter() - start
    checkpoint = torch.load(run_dir / "best.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["state_dict"])
    test_loader = DataLoader(dataset(False), batch_size=args.batch_size, num_workers=2)
    synchronize(dev)
    test_start = time.perf_counter()
    pred = evaluate(model, test_loader, dev)
    synchronize(dev)
    test_seconds = time.perf_counter() - test_start
    np.savez(run_dir / "predictions.npz", **pred)
    result = {"method": args.mode, "name": args.name,
              "test_accuracy": accuracy_score(pred["labels"], pred["predictions"]),
              "test_size": len(pred["labels"]), "best_validation_accuracy": best_val,
              "selected_step": checkpoint["step"], "steps": args.steps,
              "train_seconds_including_validation": train_seconds,
              "test_seconds": test_seconds,
              "trainable_parameters": config["trainable_parameters"],
              "paper_reference_accuracy": 0.9879,
              "difference_percentage_points": 100 * (accuracy_score(pred["labels"], pred["predictions"]) - 0.9879)}
    write_json(run_dir / "metrics.json", result)
    log(event="finetune_complete", **result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "benchmark", "extract", "probe", "finetune"))
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--lr", type=float, default=0.003)
    parser.add_argument("--eval-every", type=int, default=100)
    parser.add_argument("--mode", choices=("head", "last_block", "full"), default="head")
    parser.add_argument("--name", default="head_only")
    args = parser.parse_args()
    seed_everything()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.command == "prepare":
        resumable_download(CIFAR_URL, ROOT / "data/cifar-10-python.tar.gz", 170_498_071, CIFAR_SHA256)
        # torchvision extracts the official archive when the dataset is initialized.
        CIFAR10(ROOT / "data", train=True, download=True)
    globals()[args.command](args)


if __name__ == "__main__":
    main()
