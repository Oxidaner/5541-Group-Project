# Vision Transformer: Reproduction and Experimental Analysis

> 实验报告草稿。成员信息及贡献留空待补。定稿时压缩至最多 4 页 PDF。

| Name | Student ID | Contribution |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |

## 1. Background and Method

Vision Transformer（ViT）将图像划分为固定大小的 patch，将每个 patch 投影为向量，加入位置编码后输入 Transformer encoder，并以 class token 表示完成分类。原论文先在大型 ImageNet-21k 数据集上预训练模型，再迁移到 CIFAR-10。本实验以作者公开的 ViT-B/32 ImageNet-21k 权重为初始化，复现 CIFAR-10 迁移分类，并分析位置编码和注意力。作者原始 JAX 权重来源、精确文件哈希与运行配置记录在项目代码中。

## 2. Experimental Setup

使用官方 CIFAR-10 训练集的 49,000 张训练图和分层抽取的 1,000 张验证图，另用官方 10,000 张测试图做最终评估。模型使用 ImageNet-21k 预训练 ViT-B/32，输入分辨率为 224 × 224。原论文 Table 5 的 CIFAR-10 全量微调为 384 × 384、10,000 步和 batch size 512，参考准确率 98.79%。本地主全量微调设置为 1,000 步、batch size 64、学习率 0.003；按验证准确率选择检查点，最佳点在第 600 步。固定测试集不参与调参。设备是 Apple M4 Pro MPS，PyTorch 2.8.0、timm 1.0.22。完整参数和偏差见 docs/protocol.md。

## 3. Reproduction Results

结果如下。全部测试准确率来自 CIFAR-10 官方 10,000 张测试图。线性探测与其他微调方案作为课程扩展对照，不等同于论文 Table 5 的全量微调。

| Experiment | Model / Protocol | Paper Reference | Our Result | Difference |
| --- | --- | --- | --- | --- |
| Linear probe (extension) | Frozen ViT-B/32 features, validation-selected logistic regression | Not the Table 5 protocol | **96.13%** test accuracy | 1.44 percentage points below our best fine-tune |
| Full fine-tuning | ViT-B/32, 224 resolution, batch 64, LR 0.003, 1,000 steps | ViT-B/32, CIFAR-10, 384 resolution, 10,000 steps: 98.79% | **97.57%** test accuracy; 97.90% validation; best checkpoint step 600 | **1.22 percentage points below paper reference** |

Full fine-tuning at LR 0.003 reached 97.57% test accuracy. The same-seed LR 0.000375 run reached 95.63%; frozen-feature linear probing reached 96.13%. The best full fine-tuning checkpoint reduced the error rate to 2.43%, versus 4.37% for the lower-LR run. In the best run, cat accuracy was 95.0%; 33 cats were predicted as dogs and 40 dogs as cats.

## 4. Modification and Analysis

The code applies the existing PatchDropout method (Liu et al., WACV 2023) through timm 1.0.22. After adding positional embeddings, each training image keeps 36 of its 49 patches plus CLS: 37 tokens rather than 50. Validation and testing keep all 50 tokens. This is an efficiency extension to the ViT reproduction, not an original algorithm.

Two fresh runs use identical pretrained initialization, 49,000/1,000 split, seed 5541, batch 64, LR 0.003 and 1,000 steps. Their best validation accuracies are both 97.90%; selected steps are 600 (baseline) and 800 (PatchDropout). Both checkpoints were fixed before their test evaluations. Baseline test accuracy is 97.57% in 747.27 s; PatchDropout is 97.47% in 630.01 s. Training time, including loading, validation and checkpoint I/O, falls by **15.7%**, while test accuracy falls by **0.10 percentage points**. Initialization and final testing are excluded. The fresh baseline's logged losses, validation scores and all 10,000 test predictions match the historical baseline exactly.

The device-synchronized synthetic-batch benchmark (three alternating rounds; five warmup and 15 timed steps per condition per round) reduces median forward/backward/clip/SGD update time from 0.566 to 0.441 s, or 22.2%. This excludes data and validation overhead. Evaluation output with identical weights matches exactly in the CPU correctness check. Parameter count and inference token count remain unchanged; peak memory was not measured. Each condition has only one seed and one full training run. The official test set was previously inspected, so comparisons remain exploratory.

Figures: `results/figures/efficiency_tradeoff.png` and `results/figures/efficiency_validation_curves.png`. Evidence and pre-specified protocol: `results/efficiency_comparison.json`, `docs/efficiency_plan.md`.

The project compares frozen features, head-only training, final-block fine-tuning and full fine-tuning. A 3,000-step last-block run selected its 1,000-step validation checkpoint at 92.56%. Two 1,000-step full fine-tuning runs used the same seed, batch size, resolution and validation protocol; LR 0.003 reached 97.57% test accuracy versus 95.63% at LR 0.000375. The lower-LR test score had already been viewed before selecting the LR 0.003 follow-up. Treat this as an exploratory single-seed comparison, not confirmatory evidence.

On Apple M4 Pro MPS, batch-size-64 inference throughput was about 416 images/s after warmup. The pretrained position vectors had mean cosine similarity 0.644 between adjacent patch positions and -0.157 between positions at Manhattan distance at least six. The attention visualization compares the pretrained and fine-tuned last-block mean CLS attention for a correctly classified cat. The pretrained map emphasizes the upper-left patch; the final fine-tuned map emphasizes both upper corners, covering background rather than the cat body. This single example does not show that attention localizes the cat; the pattern could reflect position bias or the image layout. Attention weights are a diagnostic visualization, not an explanation or object detector.

The best full fine-tuning result is 1.22 percentage points below the paper reference. Remaining differences include the 224 rather than 384 resolution, 1,000 rather than 10,000 steps, one random seed, and a different resize implementation. A confirmatory comparison should use a fresh, untouched test split; a closer reproduction should also match the paper resolution and schedule.

| Experiment | Change | Quality Metric | Time / Memory | Observation |
| --- | --- | --- | --- | --- |
| LR comparison | Full fine-tune, LR 0.000375 vs 0.003 | 95.63% vs 97.57% test | 656 s vs 672 s | Same seed, batch, steps and validation protocol |
| PatchDropout extension | Training tokens 50 → 37; evaluation tokens 50 | 97.57% vs 97.47% test; validation both 97.90% | Fresh pair: 747.27 s vs 630.01 s; peak memory not measured | Training time -15.7%; test accuracy -0.10 pp; one seed |

## 5. Conclusion and References

ViT-B/32 的 ImageNet-21k 预训练模型迁移到 CIFAR-10 后，学习率 0.003 的 1,000 步全量微调取得 97.57% 测试准确率，比原论文 98.79% 低 1.22 个百分点。实验复用了作者初始化权重和 CIFAR-10 迁移任务，但分辨率和训练预算较小，属于部分复现。新增 PatchDropout 对照在验证准确率相同的情况下，将完整训练耗时降低 15.7%，测试准确率为 97.47%。未来可重复多个随机种子，并进一步对齐论文分辨率及日程。

References

1. Dosovitskiy et al., “An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale,” ICLR 2021, arXiv:2010.11929.
2. Google Research, `google-research/vision_transformer`, reference code and ImageNet-21k checkpoints.
3. Yue Liu et al., “PatchDropout: Economizing Vision Transformers Using Patch Dropout,” WACV 2023, [arXiv:2208.07220](https://arxiv.org/abs/2208.07220).

## 配套实验素材

配套交付需提供可复现代码与命令、配置、日志、结果图、运行录屏及不超过四分钟的讲解视频，完整材料小于 50M。预训练权重、完整数据集、特征缓存和大型 checkpoint 不应打包进最终提交。
