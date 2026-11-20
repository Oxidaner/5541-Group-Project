# COMP5541 ViT Project Handoff

## Selection and result

The selected paper is the instructor-listed ViT paper, *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale* (ICLR 2021).

The best local full fine-tuning run reached 97.57% CIFAR-10 test accuracy. The paper reference is 98.79%, a gap of 1.22 percentage points. The local run uses 224 px inputs, batch size 64 and 1,000 steps, whereas the paper reports 384 px and 10,000 steps. Treat this as a partial, resource-scaled reproduction, not an exact reproduction of the paper's full protocol.

The LR=0.003 run was selected after test scores from earlier exploratory runs had been inspected. The cross-run test comparison is exploratory and does not support a confirmatory claim. A future confirmatory comparison should use a fresh, untouched test split.

## New efficiency experiment (2026-11-17)

The project applies the existing [PatchDropout method](https://arxiv.org/abs/2208.07220) through timm 1.0.22. During training, 36 of 49 image patches are retained, plus CLS (37 tokens instead of 50); evaluation uses all 50 tokens. This is a ViT efficiency extension, not a change of the selected reproduction paper or a claim of an original algorithm.

| New paired run | Best validation | Test accuracy | Training time | Selected step |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 97.90% | 97.57% | 747.27 s | 600 |
| PatchDropout 25% | 97.90% | 97.47% | 630.01 s | 800 |

Training time falls by 15.7% (117.26 s), with a 0.10 percentage-point test decrease. Both use 1,000 steps, batch 64, LR 0.003 and seed 5541. Time includes loading, validation and checkpoint I/O, but excludes initialization and final testing. The new baseline reproduces every logged loss/validation score and all test predictions of the historical baseline. Both validation-selected checkpoints were fixed before the new test evaluations.

`bash scripts/reproduce_efficiency.sh` reruns the two conditions, deferred tests and analysis. It overwrites the named runs, so back up results first. `python -m scripts.analyze_efficiency` validates the comparison and rebuilds figures without training. The pre-specified plan is in `docs/efficiency_plan.md`; compact evidence is in `results/efficiency_comparison.json` and the two run directories. Checkpoints remain local and are excluded from the ZIP.

The synthetic-batch synchronized update benchmark shows a 22.2% median reduction, from 0.566 to 0.441 s (three alternating rounds, 45 timed updates per condition). It excludes data and validation overhead. Parameter count and evaluation token count remain unchanged. Peak memory was not measured; no inference speedup is claimed. There is only one seed and one full run per condition, and the official test set was inspected during earlier exploration.

## Run the experiment

See `README.md` and `scripts/reproduce_experiments.sh`. The script reruns training and overwrites each named run directory. The local environment was tested with Python 3.12.13, torch 2.8.0, torchvision 0.23.0, timm 1.0.22, scikit-learn 1.7.2, matplotlib 3.10.7 and requests 2.32.5.

`requirements-lock.txt` is the exact package snapshot from the validated local environment. It was not regenerated for a clean host because the required registry metadata was not cached offline. If installation fails on a new host, use `requirements.txt` with a compatible Python 3.12 PyTorch build for that operating system, then record the installed versions.

Official model weights and CIFAR-10 data download through `vit_experiment.py prepare`. The model checkpoint SHA-256 is stored in `artifacts/pretrained/provenance.json`. Feature and dataset caches are generated under `data/` and `artifacts/features/`.

## Results

- `results/comparison.json`: test accuracy, selected validation checkpoint, parameter count and training time for each completed run.
- `results/*/metrics.json` and `results/*/history.jsonl`: per-run metrics and training history.
- `results/efficiency_comparison.json`: controlled-configuration audit, paired test outcomes and training-time tradeoff.
- `results/patch_dropout_benchmark.json`: synchronized update timings and correctness checks.
- `results/figures/`: accuracy comparison, positional-embedding similarity, attention comparison, confusion matrices and error samples.
- `MANIFEST.sha256` at the ZIP root: verified SHA-256 hashes for every packaged file.
- `output/pdf/ViT_B32_CIFAR10_Reproduction_Draft.pdf`: four-page report draft with blank member and contribution rows.

The trained model checkpoint remains at `results/full_finetune_paper_lr_1000/best.pt` for a demonstration. It is about 334 MiB and is excluded from this archive. The CIFAR-10 dataset and pretrained weights are also excluded.

## Still needed for course submission

- Record a successful end-to-end code run.
- Produce a presentation video no longer than four minutes.
- Fill in group members' names, student IDs and actual contributions in the report.
- Convert the final report and any other documents to PDF.
- Confirm that the complete submission package stays below 50 MB.

The name, student ID and contribution table is intentionally blank.
