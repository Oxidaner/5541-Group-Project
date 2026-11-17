#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
.venv/bin/python vit_experiment.py prepare
.venv/bin/python vit_experiment.py extract --batch-size 64
.venv/bin/python vit_experiment.py probe
.venv/bin/python vit_experiment.py finetune --mode head --name head_only --steps 500 --batch-size 64 --eval-every 100 --lr 0.003
.venv/bin/python vit_experiment.py finetune --mode last_block --name last_block --steps 300 --batch-size 32 --eval-every 100 --lr 0.001
.venv/bin/python vit_experiment.py finetune --mode last_block --name last_block_3000 --steps 3000 --batch-size 64 --eval-every 1000 --lr 0.0001
.venv/bin/python vit_experiment.py finetune --mode full --name full_finetune --steps 300 --batch-size 32 --eval-every 100 --lr 0.0001
.venv/bin/python vit_experiment.py finetune --mode full --name full_finetune_lr_scaled_1000 --steps 1000 --batch-size 64 --eval-every 200 --lr 0.000375
.venv/bin/python vit_experiment.py finetune --mode full --name full_finetune_paper_lr_1000 --steps 1000 --batch-size 64 --eval-every 200 --lr 0.003
.venv/bin/python analyze_results.py --run full_finetune_paper_lr_1000 --analysis all
