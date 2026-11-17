# RSI 相关论文的课程复现选题

核对日期：2026-11-15。这里将 RSI 理解为 Recursive Self-Improvement，即递归自我改进。本文件保留早期选题调查；当前项目已选择老师名单中的 ViT，RSI 候选未进入实验。

## 推荐结论

如果优先考虑课程交付，推荐 **Reflexion**：有作者代码，能做客观的编程任务评价，也容易解释失败、反馈和下一次尝试之间的关系。

如果主题必须体现“改进器改进自己”，推荐 **STOP**：它修改调用语言模型的程序，再把改进后的程序用于后续改进。其工程和评价工作量高于 Self-Refine 与 Reflexion。STOP 作者也明确说明，这不等同于完整的模型层面 RSI，因为语言模型本身没有被修改。[STOP 论文](https://arxiv.org/abs/2310.02304)

四篇论文都不在老师给出的 15 篇名单内。课程允许选择名单外论文，但要求先联系老师并说明理由。具体规则见 [Group Project.pdf](<Group Project.pdf>) 第 1 页。选择方向、准备实验范围和理由可以先完成；不要把名单外选题写成已经得到老师认可。

## 候选比较

难度针对控制规模、使用模型 API 的课程实验，是本项目的判断，不是实测耗时或成本。

| 论文 | 改进什么 | 与 RSI 的关系 | 复现难度判断 | 作者代码 |
| --- | --- | --- | --- | --- |
| Self-Refine，NeurIPS 2023 | 对当前答案生成反馈，再修订答案 | 自我修正入门；没有修改自身改进机制 | 低 | [madaan/self-refine](https://github.com/madaan/self-refine) |
| Reflexion，NeurIPS 2023 | 根据反馈生成反思，用于后续尝试 | 通过文本经验改善行为；没有修改模型权重 | 低到中，课程首选 | [noahshinn/reflexion](https://github.com/noahshinn/reflexion) |
| STOP，2023 | 改进程序的程序，并继续使用新改进器 | 明确包含程序层面的递归自我改进 | 中到高，主题首选 | [microsoft/stop](https://github.com/microsoft/stop) |
| Darwin Gödel Machine，2025 | 编程 Agent 自身代码与工具，并维护候选档案 | Agent 系统层面的自我改进 | 高，不作为本次的首选 | [jennyzzt/dgm](https://github.com/jennyzzt/dgm) |

以上 API 路线不需要在本地训练大模型，但需要模型调用预算。嵌套搜索、失败重试和多轮评价都会增加调用量；选定后应先小规模测量，再估计正式实验预算。

## 1. Self-Refine：最容易理解和实现

完整题目：*Self-Refine: Iterative Refinement with Self-Feedback*。

[NeurIPS 论文页面](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html)说明，其方法用同一语言模型生成答案、提供反馈和修改答案，不需要额外训练。作者仓库提供 GSM-8k 的运行与评价入口，以及其他任务的提示词和代码。

建议选择论文已有的 GSM-8k 数学题任务，比较初次回答与多轮修订后的答案正确率，再增加等预算的独立重试对照。保留逐题答案、反馈、修订轨迹和调用量。

优点是流程短，适合在四分钟内讲清楚。限制是现代模型未必因自我反馈而改善，也可能把正确答案改错；结果下降同样需要如实报告。若把外部判题反馈加入循环，应单独标为扩展，不能与原始自我反馈方法混写。

## 2. Reflexion：最适合本次项目的折中

完整题目：*Reflexion: Language Agents with Verbal Reinforcement Learning*。

[论文](https://arxiv.org/abs/2303.11366)通过语言反馈和文本经验改善后续尝试，不更新模型权重。作者提供推理、环境交互和编程实验；[编程循环源码](https://github.com/noahshinn/reflexion/blob/main/programming_runs/reflexion.py)包含内部测试、反馈、反思、再次生成以及结果记录。

建议优先做编程任务，以 HumanEval 对应协议为起点，避免一开始搭建完整交互环境。正式实验比较三组：

1. 初次生成：建立基线。
2. 等预算独立重试：判断收益是否只是来自更多尝试。
3. 反思后重试：使用内部测试反馈和反思，评价增量收益。

公平比较需要明确总调用量、总 token 和重试次数。隐藏评价测试不用于生成反思或挑选候选；候选选择使用可见或模型生成的内部测试，最终再评价。报告区分单次提交指标与多轮累计成功率，不把多次尝试后的成功率直接当成一次生成的成功率。

可测指标包括最终通过率、每轮累计成功率、平均调用量、耗时，以及“修好错误”和“改坏正确答案”的数量。加分方向可考虑根据内部测试证据提前停止，衡量节省的调用量和质量变化。这是候选改动，是否有效需要实测。

作者 README 保留了原始实验日志，也提示完整重跑有 API 成本。课程实验应固定模型、任务、提示词和预算，而不是只演示一个成功样例。[官方 README](https://github.com/noahshinn/reflexion/blob/main/README.md)

## 3. STOP：更符合递归自我改进主题

完整题目：*Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation*。

可以把核心过程理解为：初始改进器修改程序，再把初始改进器本身当成待修改程序；新的改进器随后参与下一轮改进。关键是保存每一代改进器，并检查其能力是否能迁移到新的任务实例。[论文与作者说明](https://github.com/microsoft/stop/blob/main/README.md)

作者代码提供 [run_improver.py](https://github.com/microsoft/stop/blob/main/run_improver.py) 和迁移评价入口。当前公开配置默认使用 `parity_noise` 子任务，并设有语言模型调用预算及多轮迭代配置。[配置来源](https://github.com/microsoft/stop/blob/main/config.py)

建议先围绕作者提供的一类任务建立可运行基线，比较固定初始改进器与递归更新改进器。在相同预算下画出每代效用、调用量和失败率，并把最终改进器冻结后，在新的随机实例上评价。

前几轮开发实验可以缩小预算，但这属于缩小规模的方法检查。正式提交前仍需核对论文具体实验条件、评价单位和参考结果，才能判断是否满足“与原论文结果相近”。只在用于搜索的题目上变好，不足以证明获得了通用的改进能力。

## 4. Darwin Gödel Machine：贴题，但工作量大

完整题目：*Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*。

[论文](https://arxiv.org/abs/2505.22954)和[作者代码](https://github.com/jennyzzt/dgm)展示了自修改编程 Agent，并通过 SWE-bench、Polyglot 等编程基准评价。官方运行准备包含 Docker、基准环境以及模型 API，外层还要反复生成和评价候选 Agent。

它适合研究 Agent 如何修改自己的工具和实现，但相较前面三篇，需要处理更多环境、执行与评测工作。不建议把完整原论文复现作为这次短课程项目的第一目标。自己换成少量玩具题，只能称为缩小规模原型，不能声称复现了原论文基准结果。

## 复现边界与选题说明

这些论文使用的模型和提示词来自各自的实验时期。若换成不同模型，仍可复现方法和比较趋势，但不能预先保证达到论文报告的数值。报告需要明确模型替换、任务规模和协议差异，再与老师确认所选实验范围是否合适。

选择名单外论文时，可向老师说明：有公开论文和作者代码；使用明确的公开基准和客观指标；只复现一个可控制规模的实验；计划追加等预算比较及效率分析。当前没有替用户联系老师。

项目成员、学号和分工继续沿用[报告草稿](Report_结构草稿.md)中的空白表格。
