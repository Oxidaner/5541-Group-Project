# Patch Dropout 效率实验预设方案

方案在新对照训练前写定（2026-11-17）。此前已查看旧实验的测试分数，沿用 CIFAR-10 官方测试集的比较仍属于探索性结果。

- 基线：全量微调，224 输入、batch 64、SGD momentum 0.9、LR 0.003、1,000 步、100 步 warmup、cosine 衰减、梯度裁剪 1，每 200 步验证，seed 5541。
- 唯一方法改动：timm 1.0.22 的 `patch_drop_rate=0.25`。49 个 patch 保留 `floor(49 × 0.75) = 36` 个，加 CLS 共 37 tokens；基线 50 tokens。先加位置编码，再按每张图随机抽取 patch，始终保留 CLS。验证和测试恢复全部 50 tokens。
- 同一预训练权重、零初始化分类头、49,000/1,000 分层拆分、数据增强、优化器、训练样本预算和选 checkpoint 规则。不能把旧 run 第 600 步作为预先确定的 early stopping。
- 先用设备同步的合成 batch 更新基准测计算收益：3 轮交替顺序，每条件每轮 5 步 warmup + 15 步计时；不含加载、验证和保存。检查启用改动后 eval 输出与基线完全一致、训练 token 数正确、梯度有限。
- 新跑基线 `efficiency_baseline_1000` 和改动 `efficiency_patchdrop25_1000`。总训练计时包含数据加载、验证和保存，不含模型初始化及最终测试；使用相同计时范围。
- 按各 run 验证最高准确率选 checkpoint，平分保留较早者。先记录两组验证结果，再统一评价固定 checkpoint 的测试集。
- 主要指标：完整 1,000 步训练耗时、测试准确率、验证准确率；合成 batch 更新中位数作为辅助。预设实用目标为训练耗时下降至少 10%，验证准确率下降不超过 0.3 个百分点。未达到也如实保留，不根据测试分数调 dropout。
- 只做一个 seed、每个条件一次完整训练，不能声称显著性或普遍加速。三轮微基准仅估计设备更新时间波动，不代表训练准确率方差。不声称降低推理 token 数、实测峰值内存或原创方法。

方法来源：Liu et al., *PatchDropout: Economizing Vision Transformers Using Patch Dropout*（https://arxiv.org/abs/2208.07220），以及 timm 1.0.22 的 `PatchDropout` 公共实现。ViT 构造参数 `patch_drop_rate` 默认 0，扩展条件显式改为 0.25，基线使用库默认值；未增加其他配置。
