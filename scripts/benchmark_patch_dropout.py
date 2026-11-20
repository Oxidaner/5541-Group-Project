"""Paired MPS/CUDA-synchronized update timing through timm's public model API.

Run from the project root: python -m scripts.benchmark_patch_dropout
Input tensors are resident on the device; data loading, validation, checkpoint
I/O and model construction are excluded. Full experiments measure those costs.
"""

import gc
import time

import numpy as np
import torch

from vit_experiment import (
    RESULTS, backbone, device, environment, log, seed_everything, synchronize,
    write_json,
)


def main():
    seed_everything()
    dev = device()
    base = backbone().eval()
    modified = backbone(0.25).eval()
    # Patch dropout has no parameters: the exact pretrained state is compatible.
    modified.load_state_dict(base.state_dict())
    x_cpu = torch.randn(2, 3, 224, 224)
    with torch.inference_mode():
        torch.testing.assert_close(base(x_cpu), modified(x_cpu), rtol=0, atol=0)
    tokens = {}
    for label, model in (("baseline", base), ("drop_25", modified)):
        handle = model.blocks[0].register_forward_pre_hook(
            lambda _, inputs, label=label: tokens.update({label: inputs[0].shape[1]})
        )
        model.train()
        with torch.no_grad():
            model(x_cpu)
        handle.remove()
    assert tokens == {"baseline": 50, "drop_25": 37}, tokens
    del base, modified
    gc.collect()

    # Alternate order over three paired rounds to reduce order/thermal bias.
    rounds = []
    for repeat in range(3):
        for rate in ((0.0, 0.25) if repeat % 2 == 0 else (0.25, 0.0)):
            seed_everything()
            model = backbone(rate)
            model.reset_classifier(10)
            torch.nn.init.zeros_(model.head.weight)
            torch.nn.init.zeros_(model.head.bias)
            model = model.to(dev).train()
            optimizer = torch.optim.SGD(model.parameters(), lr=0.003, momentum=0.9)
            x = torch.randn(64, 3, 224, 224, device=dev)
            y = torch.arange(64, device=dev) % 10
            samples = []
            for step in range(20):
                synchronize(dev)
                start = time.perf_counter()
                optimizer.zero_grad()
                loss = torch.nn.functional.cross_entropy(model(x), y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                synchronize(dev)
                seconds = time.perf_counter() - start
                assert torch.isfinite(loss).item()
                if step >= 5:
                    samples.append(seconds)
            assert torch.isfinite(model.blocks[0].attn.qkv.weight.grad).all().item()
            row = {"repeat": repeat, "patch_drop_rate": rate,
                   "step_seconds": samples, "median_seconds": float(np.median(samples))}
            rounds.append(row)
            log(**row)
            del model, optimizer, x, y, loss
            gc.collect()
            if dev.type == "mps":
                torch.mps.empty_cache()
    summary = []
    for rate in (0.0, 0.25):
        values = [s for row in rounds if row["patch_drop_rate"] == rate
                  for s in row["step_seconds"]]
        summary.append({"patch_drop_rate": rate, "timed_steps": len(values),
                        "median_seconds": float(np.median(values)),
                        "q25_seconds": float(np.quantile(values, 0.25)),
                        "q75_seconds": float(np.quantile(values, 0.75))})
    result = {"environment": environment(), "batch_size": 64,
              "warmup_steps_per_round": 5, "timing_scope": "resident synthetic batch: forward/backward/clip/SGD; synchronized each step",
              "eval_output_exact_equality_cpu": True, "training_tokens": tokens,
              "rounds": rounds, "summary": summary,
              "median_update_time_reduction": 1 - summary[1]["median_seconds"] / summary[0]["median_seconds"]}
    write_json(RESULTS / "patch_dropout_benchmark.json", result)
    log(event="benchmark_complete", **{k: v for k, v in result.items() if k != "rounds"})


if __name__ == "__main__":
    main()
