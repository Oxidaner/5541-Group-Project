# COMP5541 ViT Project Handoff

## Selection and result

The selected paper is the instructor-listed ViT paper, *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale* (ICLR 2021).

The best local full fine-tuning run reached 97.57% CIFAR-10 test accuracy. The paper reference is 98.79%, a gap of 1.22 percentage points. The local run uses 224 px inputs, batch size 64 and 1,000 steps, whereas the paper reports 384 px and 10,000 steps. Treat this as a partial, resource-scaled reproduction, not an exact reproduction of the paper's full protocol.

The LR=0.003 run was selected after test scores from earlier exploratory runs had been inspected. The cross-run test comparison is exploratory and does not support a confirmatory claim. A future confirmatory comparison should use a fresh, untouched test split.

## Run the experiment

See `README.md` and `scripts/reproduce_experiments.sh`. The script reruns training and overwrites each named run directory. The local environment was tested with Python 3.12.13, torch 2.8.0, torchvision 0.23.0, timm 1.0.22, scikit-learn 1.7.2, matplotlib 3.10.7 and requests 2.32.5.

`requirements-lock.txt` is the exact package snapshot from the validated local environment. It was not regenerated for a clean host because the required registry metadata was not cached offline. If installation fails on a new host, use `requirements.txt` with a compatible Python 3.12 PyTorch build for that operating system, then record the installed versions.

Official model weights and CIFAR-10 data download through `vit_experiment.py prepare`. The model checkpoint SHA-256 is stored in `artifacts/pretrained/provenance.json`. Feature and dataset caches are generated under `data/` and `artifacts/features/`.

## Results

- `results/comparison.json`: test accuracy, selected validation checkpoint, parameter count and training time for each completed run.
- `results/*/metrics.json` and `results/*/history.jsonl`: per-run metrics and training history.
- `results/figures/`: accuracy comparison, positional-embedding similarity, attention comparison, confusion matrices and error samples.
- `results/MANIFEST.sha256`: hashes for compact result artifacts.
- `output/pdf/ViT_B32_CIFAR10_Reproduction_Draft.pdf`: four-page report draft with blank member and contribution rows.

The trained model checkpoint remains at `results/full_finetune_paper_lr_1000/best.pt` for a demonstration. It is about 334 MiB and is excluded from this archive. The CIFAR-10 dataset and pretrained weights are also excluded.

## Still needed for course submission

- Record a successful end-to-end code run.
- Produce a presentation video no longer than four minutes.
- Fill in group members' names, student IDs and actual contributions in the report.
- Convert the final report and any other documents to PDF.
- Confirm that the complete submission package stays below 50 MB.

The name, student ID and contribution table is intentionally blank.
