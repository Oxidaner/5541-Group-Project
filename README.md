# COMP5541: Vision Transformer 实验

论文：[*An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale*](https://arxiv.org/abs/2010.11929)，ICLR 2021，老师名单第 3 篇。

本项目使用作者在 ImageNet-21k 上预训练的 ViT-B/32，在 CIFAR-10 上比较冻结特征探测、分类头微调、末层微调和全量微调，并分析位置编码及注意力。

原论文报告 ViT-B/32 在 CIFAR-10 上达到 98.79%，使用 384 分辨率和 10,000 步。本机最佳全量微调使用 224 分辨率、batch size 64、LR 0.003 和 1,000 步，测试准确率为 97.57%，低于参考值 1.22 个百分点。 跨 run 探索曾查看先前测试分数，并据此选择后续 LR 条件；跨设置比较属于探索性结果，确认性比较应使用未查看的新测试划分。

## 环境与运行

已固定直接依赖；`requirements-lock.txt` 记录本次安装的全部版本。Mac 自动使用 MPS，有 NVIDIA GPU 的设备自动使用 CUDA，否则使用 CPU。

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt
.venv/bin/python vit_experiment.py prepare
.venv/bin/python vit_experiment.py benchmark
.venv/bin/python vit_experiment.py extract
.venv/bin/python vit_experiment.py probe
.venv/bin/python vit_experiment.py finetune --mode head --name head_only --steps 500 --batch-size 64 --eval-every 100 --lr 0.003
.venv/bin/python vit_experiment.py finetune --mode last_block --name last_block --steps 300 --batch-size 32 --eval-every 100 --lr 0.001
.venv/bin/python vit_experiment.py finetune --mode full --name full_finetune_paper_lr_1000 --steps 1000 --batch-size 64 --eval-every 200 --lr 0.003
.venv/bin/python analyze_results.py --run full_finetune_paper_lr_1000 --analysis all
```

`prepare` 使用可续传的并行分块下载，获取约 400 MiB 的 Google Research 原始 ImageNet-21k 权重和约 163 MiB 的 CIFAR-10 官方压缩包。timm 1.0.22 将作者 JAX checkpoint 直接装入相同结构的 PyTorch 模型。权重 URL、模型配置 revision、文件大小和 SHA-256 写入 provenance。权重未在 CIFAR-10 上微调，分类头由本实验训练，避免直接拿下游分类权重冒充复现。

`probe` 只使用训练集划出的验证集选择正则化强度，然后用完整训练集拟合，并评价固定测试集。只训练分类头、微调最后一个 Transformer block 和全量微调使用同一训练/验证拆分，按验证准确率选择检查点，最后评价完整测试集。测试标签不用于调参。

## 已完成的实验

原论文的 CIFAR-10 参考准确率为 98.79%。本机全量微调在 batch size 64 下训练 1,000 步，使用论文搜索候选 LR 0.003，最佳验证 checkpoint 为第 600 步，独立测试准确率为 97.57%。224 分辨率和较短训练预算仍低于原论文设置。

冻结特征线性探测为 96.13%，batch-scaled LR 全量微调为 95.63%，分类头微调为 94.70%，末层 3,000 步微调为 92.56%。交叉 run 的分数用于探索性分析；确认性比较仍需未查看过的新测试划分。完整配置和日志位于 `results/`。

## 新增效率改动：PatchDropout

2026-11-17 完成两组新的 1,000 步对照。训练时随机保留 49 个图像 patch 中的 36 个，加 CLS 共 37 tokens；验证和测试恢复全部 50 tokens。使用 [PatchDropout](https://arxiv.org/abs/2208.07220) 的已有方法及 timm 公共实现，作为 ViT 复现后的效率扩展。原来的最优准确率模型继续保留。

| 条件 | 最佳验证准确率 | 测试准确率 | 完整训练耗时 | 验证选中步数 |
| --- | ---: | ---: | ---: | ---: |
| 新跑基线，50 tokens | 97.90% | 97.57% | 747.27 秒 | 600 |
| PatchDropout 25%，37 tokens | 97.90% | 97.47% | 630.01 秒 | 800 |

**训练耗时减少 15.7%（117.26 秒），测试准确率下降 0.10 个百分点。**时间包括数据加载、五次验证和保存检查点，不包括初始化和最终测试。两组均为 batch 64、LR 0.003、seed 5541，训练样本预算和其他配置相同。新基线的完整损失/验证日志与旧基线一致，10,000 条测试预测也完全相同。验证选出的两个检查点在新一轮测试前固定，不根据测试分数搜索 dropout 比例。

设备同步的合成 batch 微基准中，单步 forward/backward/clip/SGD 中位数从 0.566 秒降至 0.441 秒，减少 22.2%。这不包括数据与验证开销，不能替代上表完整训练耗时。参数量和测试时 token 数未减少，未测峰值内存，也不声称推理加速。每条件仅一个 seed、一次完整训练；测试集此前已查看，结果为探索性对照。

```bash
# 重跑会覆盖这两个命名 run；原始权重和数据需要已 prepare。
bash scripts/reproduce_efficiency.sh
# 只重建对照图和审计结果，不训练：
.venv/bin/python -m scripts.analyze_efficiency
```

训练前写定的方案见 `docs/efficiency_plan.md`；原始证据见 `results/efficiency_comparison.json`、两个 run 的配置/日志/预测以及 `results/patch_dropout_benchmark.json`。图表为 `results/figures/efficiency_tradeoff.png` 和 `efficiency_validation_curves.png`。

## 文件说明

- `vit_experiment.py`：准备数据、设备实测、提取特征、线性分类和微调。
- `analyze_results.py`：位置编码、注意力、混淆矩阵和误分类样例。
- `docs/protocol.md`：与论文的对应关系、实验差异和参数默认值核对。
- `results/`：环境、划分索引、模型结果、逐步训练日志和图表。
- `artifacts/`：预训练权重、特征缓存等大文件，不放入课程提交包。
- `data/`：公开数据集，不放入课程提交包。

大模型检查点同样不适合放入小于 50M 的课程提交包。最终交付应保留可复现代码、权重来源、必要结果和视频，按实际打包体积检查。当前文档是实验工作文件，正式提交时文档需要转 PDF，并附运行录屏及不超过四分钟的讲解视频。

## 成员与分工

| 姓名 | 学号 | 实际贡献 |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |

## 实验交接

英文四页报告草稿位于 output/pdf/ViT_B32_CIFAR10_Reproduction_Draft.pdf。姓名、学号及贡献均留空。scripts/build_report.py 可从结果 JSON 重建报告；安装 requirements-report.txt 即可使用。

最终模型保留在 `results/full_finetune_paper_lr_1000/best.pt`，供本机演示，不放入压缩包。交接包包含代码、配置、预测、图表和报告。运行录屏及不超过四分钟的讲解视频尚未制作，因此交接包不是可直接提交的完整材料。

scripts/reproduce_experiments.sh 记录七组实验的精确命令。执行时会重跑训练并覆盖对应 run 结果，应先备份；已经校验的原始权重和特征缓存可以复用。

scripts/reproduce_efficiency.sh 另记录新增两组效率实验。新增模型分别保留于 `results/efficiency_baseline_1000/best.pt` 和 `results/efficiency_patchdrop25_1000/best.pt`，仅供本机演示，不进入交接包。
