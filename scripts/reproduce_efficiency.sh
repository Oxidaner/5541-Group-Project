#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
.venv/bin/python -m scripts.benchmark_patch_dropout
.venv/bin/python vit_experiment.py finetune --mode full --name efficiency_baseline_1000 --steps 1000 --batch-size 64 --eval-every 200 --lr 0.003 --defer-test
.venv/bin/python vit_experiment.py finetune --mode full --name efficiency_patchdrop25_1000 --steps 1000 --batch-size 64 --eval-every 200 --lr 0.003 --patch-drop-rate 0.25 --defer-test
.venv/bin/python vit_experiment.py test --name efficiency_baseline_1000
.venv/bin/python vit_experiment.py test --name efficiency_patchdrop25_1000
.venv/bin/python -m scripts.analyze_efficiency
