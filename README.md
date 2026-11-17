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
