from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics

from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/ViT_B32_CIFAR10_Reproduction_Draft.pdf'
FIG = ROOT / 'results/figures'
main_result = json.loads((ROOT / 'results/full_finetune_paper_lr_1000/metrics.json').read_text())
scaled_result = json.loads((ROOT / 'results/full_finetune_lr_scaled_1000/metrics.json').read_text())
probe_result = json.loads((ROOT / 'results/linear_probe.json').read_text())
head_result = json.loads((ROOT / 'results/head_only/metrics.json').read_text())
last_result = json.loads((ROOT / 'results/last_block_3000/metrics.json').read_text())
short_full_result = json.loads((ROOT / 'results/full_finetune/metrics.json').read_text())
efficiency = json.loads((ROOT / 'results/efficiency_comparison.json').read_text())
eff_base, eff_drop = efficiency['conditions']
micro = json.loads((ROOT / 'results/patch_dropout_benchmark.json').read_text())
paper_accuracy = main_result['paper_reference_accuracy'] * 100
main_test = main_result['test_accuracy'] * 100
main_val = main_result['best_validation_accuracy'] * 100
main_step = main_result['selected_step']
main_gap = paper_accuracy - main_test
scaled_test = scaled_result['test_accuracy'] * 100
probe_test = probe_result['test_accuracy'] * 100
cat_acc = main_result['per_class_accuracy']['cat'] * 100
cat_to_dog = main_result['confusion_matrix'][3][5]
W, H = A4
NAVY = colors.HexColor('#172B4D')
BLUE = colors.HexColor('#1877B9')
MUTED = colors.HexColor('#58677C')
PALE = colors.HexColor('#EEF4F8')
RULE = colors.HexColor('#D7E0E8')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCN', fontName='Times-Roman', fontSize=21, leading=27, textColor=NAVY, spaceAfter=2*mm))
styles.add(ParagraphStyle(name='DeckCN', fontName='Times-Roman', fontSize=9.2, leading=13, textColor=MUTED, spaceAfter=4*mm))
styles.add(ParagraphStyle(name='H1CN', fontName='Times-Roman', fontSize=12.2, leading=16, textColor=NAVY, spaceBefore=1.5*mm, spaceAfter=2*mm))
styles.add(ParagraphStyle(name='BodyCN', fontName='Times-Roman', fontSize=10, leading=13.6, textColor=colors.HexColor('#263238'), spaceAfter=1.7*mm))
styles.add(ParagraphStyle(name='SmallCN', fontName='Times-Roman', fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=0.7*mm))
styles.add(ParagraphStyle(name='Metric', fontName='Helvetica-Bold', fontSize=21, leading=24, textColor=BLUE, alignment=1))
styles.add(ParagraphStyle(name='MetricLabel', fontName='Times-Roman', fontSize=7, leading=9, textColor=MUTED, alignment=1))
styles.add(ParagraphStyle(name='CellCN', fontName='Times-Roman', fontSize=8, leading=10, textColor=colors.HexColor('#263238')))
styles.add(ParagraphStyle(name='CellHeadCN', fontName='Times-Roman', fontSize=8, leading=10, textColor=colors.white))
styles.add(ParagraphStyle(name='CaptionCN', fontName='Times-Roman', fontSize=8, leading=10.5, textColor=MUTED, spaceBefore=0.5*mm, spaceAfter=1.2*mm))
styles.add(ParagraphStyle(name='RefCN', fontName='Times-Roman', fontSize=8, leading=10, textColor=colors.HexColor('#263238'), spaceAfter=1*mm))
P = lambda text, style='BodyCN': Paragraph(text, styles[style])

def fitted(path, max_w, max_h):
    image = Image(str(path))
    scale = min(max_w / image.imageWidth, max_h / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image

def make_table(data, widths, padding=3):
    obj = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    commands = [
        ('GRID', (0, 0), (-1, -1), 0.3, RULE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), padding), ('RIGHTPADDING', (0, 0), (-1, -1), padding),
        ('TOPPADDING', (0, 0), (-1, -1), padding), ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
    ]
    for row in range(1, len(data)):
        if row % 2 == 0:
            commands.append(('BACKGROUND', (0, row), (-1, row), PALE))
    obj.setStyle(TableStyle(commands))
    return obj

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(17*mm, 14*mm, W-17*mm, 14*mm)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(17*mm, 9.5*mm, 'COMP5541 | ViT-B/32 CIFAR-10 transfer study')
    canvas.drawRightString(W-17*mm, 9.5*mm, str(doc.page))
    canvas.restoreState()

story = []

story += [P('Vision Transformer on CIFAR-10', 'TitleCN'),
          P('ImageNet-21k pretrained ViT-B/32 | Resource-scaled reproduction and controlled comparisons', 'DeckCN')]
metric_w = (W - 34*mm) / 3
m = Table([[P(f'{main_test:.2f}%', 'Metric'), P(f'{paper_accuracy:.2f}%', 'Metric'), P(f'-{main_gap:.2f} pp', 'Metric')],
           [P('Best full fine-tune test accuracy', 'MetricLabel'), P('Paper Table 5 reference', 'MetricLabel'), P('Gap to reference', 'MetricLabel')]],
          colWidths=[metric_w]*3, rowHeights=[10*mm, 7.5*mm])
m.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),0.6,RULE),
                       ('INNERGRID',(0,0),(-1,-1),0.35,RULE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                       ('TOPPADDING',(0,0),(-1,-1),1.5*mm),('BOTTOMPADDING',(0,0),(-1,-1),1*mm)]))
story += [m, Spacer(1,3*mm), P('Team members and contributions','H1CN')]
story.append(make_table([[P('Name','CellHeadCN'),P('Student ID','CellHeadCN'),P('Contribution','CellHeadCN')],
                         [P('','CellCN'),P('','CellCN'),P('','CellCN')],
                         [P('','CellCN'),P('','CellCN'),P('','CellCN')],
                         [P('','CellCN'),P('','CellCN'),P('','CellCN')]],
                        [38*mm,38*mm,W-34*mm-76*mm],padding=4))
story += [Spacer(1,3*mm), P('Background and method','H1CN'),
          P('Vision Transformer (ViT) splits an image into patches, projects each patch into a token, adds positional embeddings, and processes the sequence with a Transformer encoder. A class token supplies the image representation for classification. The paper studies large-scale pretraining followed by transfer to smaller image-classification benchmarks.'),
          P('This project loads the authors’ ImageNet-21k pretrained ViT-B/32 checkpoint and adapts its classifier to CIFAR-10. The main target is the paper’s CIFAR-10 transfer experiment. Frozen-feature logistic regression and restricted fine-tuning runs are labeled extension experiments.'),
          P('Data and implementation','H1CN'),
          P(f'CIFAR-10 uses its official 50,000-image training split and 10,000-image test split. A stratified 1,000-image validation subset is held out from training. The model receives bilinear-resized 224 × 224 images normalized to [-1, 1]. The best full fine-tuning run uses batch size 64, 1,000 steps and LR 0.003; the selected validation checkpoint is step {main_step}. Device: Apple M4 Pro MPS; PyTorch 2.8.0 and timm 1.0.22.'),
          P('The reference ViT-B/32 checkpoint is the authors’ ImageNet-21k JAX weight file loaded with timm. Its source, model configuration revision and SHA-256 are recorded in the project provenance file. No CIFAR-10-finetuned checkpoint was used as the initial result. The downloaded pretraining source was not re-audited for downstream image overlap.')]
story.append(PageBreak())

story += [P('Reproduction results','H1CN'),
          P('The paper reports 98.79% top-1 accuracy for ImageNet-21k pretrained ViT-B/32 fine-tuned on CIFAR-10 using 384 × 384 inputs, batch size 512 and 10,000 steps. The best local full fine-tuning run uses 224 × 224 inputs and 1,000 steps. It is therefore a resource-scaled partial reproduction, not a full replication of the paper schedule.'),
          fitted(FIG/'test_accuracy_comparison.png',W-34*mm,78*mm),
          P('Figure 1. CIFAR-10 test accuracy for all local experiments. The x-axis starts at 90%. The dashed line marks the paper’s 98.79% reference. Frozen-feature linear probing is an extension, not the paper’s Table 5 result.','CaptionCN')]
rows = [
 [P('Experiment','CellHeadCN'),P('Trainable parameters','CellHeadCN'),P('Budget; best step','CellHeadCN'),P('Val.','CellHeadCN'),P('Test','CellHeadCN')],
 [P('Frozen features + logistic regression (extension)','CellCN'),P('7,690','CellCN'),P('5.16 s search and fit','CellCN'),P('97.50%','CellCN'),P('96.13%','CellCN')],
 [P('Head only (extension)','CellCN'),P('7,690','CellCN'),P('500; 400','CellCN'),P(f'{head_result["best_validation_accuracy"]*100:.2f}%','CellCN'),P(f'{head_result["test_accuracy"]*100:.2f}%','CellCN')],
 [P('Last block (extension)','CellCN'),P('7,097,098','CellCN'),P(f'{last_result["steps"]:,}; {last_result["selected_step"]:,}','CellCN'),P(f'{last_result["best_validation_accuracy"]*100:.2f}%','CellCN'),P(f'{last_result["test_accuracy"]*100:.2f}%','CellCN')],
 [P('Full fine-tune, short LR','CellCN'),P('87,462,922','CellCN'),P(f'{short_full_result["steps"]}; {short_full_result["selected_step"]}','CellCN'),P(f'{short_full_result["best_validation_accuracy"]*100:.2f}%','CellCN'),P(f'{short_full_result["test_accuracy"]*100:.2f}%','CellCN')],
 [P('Full fine-tune, scaled LR','CellCN'),P('87,462,922','CellCN'),P('1,000; 800','CellCN'),P(f'{scaled_result["best_validation_accuracy"]*100:.2f}%','CellCN'),P(f'{scaled_test:.2f}%','CellCN')],
 [P('Full fine-tune, LR 0.003','CellCN'),P('87,462,922','CellCN'),P(f'1,000; {main_step}','CellCN'),P(f'{main_val:.2f}%','CellCN'),P(f'{main_test:.2f}%','CellCN')],
]
story += [make_table(rows,[47*mm,29*mm,38*mm,22*mm,W-34*mm-136*mm],padding=3),Spacer(1,2*mm),
          P(f'The best full fine-tuning result is {main_gap:.2f} percentage points below the paper. Frozen-feature probing is a labeled extension. Training experiments use one random seed, so run-to-run variance is not estimated.','SmallCN'),PageBreak()]

story += [P('Representation and error analysis','H1CN'),
          P('The 49 pretrained positional vectors have mean cosine similarity 0.644 for adjacent patch positions and -0.157 for pairs separated by Manhattan distance at least six. This follows the analysis in the paper’s Figure 7, using ViT-B/32 rather than ViT-L/32.'),
          fitted(FIG/'position_similarity.png',W-34*mm,82*mm),
          P('Figure 2. Pairwise cosine similarity of the 49 pretrained positional vectors. Neighboring positions are more similar on average than distant positions.','CaptionCN'),
          fitted(FIG/'full_finetune_paper_lr_1000_attention.png',W-34*mm,56*mm),
          P('Figure 3. Last-block mean CLS-to-patch attention for one correctly classified cat. The pretrained map emphasizes the upper-left patch; after fine-tuning, both upper corners gain weight. These patches cover background and cushion rather than the cat. This example does not demonstrate object localization.','CaptionCN'),
          P(f'In the best full fine-tuning run, cat accuracy is {cat_acc:.1f}%; {cat_to_dog} of 1,000 true cats are predicted as dogs, while 40 dogs are predicted as cats. Cat/dog discrimination remains a prominent source of error.')]
story.append(PageBreak())

story += [P('Code modification: training with fewer patch tokens','H1CN'),
          P('We apply PatchDropout [3] through timm 1.0.22: after adding position embeddings, randomly retain 36 of 49 image patches per training image and preserve CLS (37 tokens versus 50). Validation and testing use all 50 tokens. This is an application of an existing method, not a new algorithm. The pretrained initialization, split, seed, batch, LR and 1,000-step budget are held fixed.'),
          fitted(FIG/'efficiency_tradeoff.png',W-34*mm,64*mm),
          P(f'Figure 4. Fresh paired runs: baseline {eff_base["test_accuracy"]*100:.2f}% test in {eff_base["train_seconds_including_validation"]:.1f} s; PatchDropout {eff_drop["test_accuracy"]*100:.2f}% in {eff_drop["train_seconds_including_validation"]:.1f} s. Timing includes data loading, validation and checkpoint I/O, excluding initialization and final test.','CaptionCN'),
          P(f'Training time falls by {efficiency["train_time_reduction_fraction"]*100:.1f}%; the test difference is {efficiency["test_difference_percentage_points"]:+.2f} percentage points. Best validation scores are {eff_base["best_validation_accuracy"]*100:.2f}% and {eff_drop["best_validation_accuracy"]*100:.2f}%, selecting steps {eff_base["selected_step"]} and {eff_drop["selected_step"]}. Both checkpoints were fixed before the new test evaluations. No dropout-rate search used test results.'),
          fitted(FIG/'efficiency_validation_curves.png',W-34*mm,58*mm),
          P('Figure 5. Validation accuracy versus equal training steps and wall-clock time. Each point evaluates 1,000 held-out training images.','CaptionCN'),
          P(f'A synchronized synthetic-batch benchmark (batch 64; three alternating rounds, five warmup and 15 timed updates per condition per round) reduced median forward/backward/clip/SGD time from {micro["summary"][0]["median_seconds"]:.3f} to {micro["summary"][1]["median_seconds"]:.3f} s ({micro["median_update_time_reduction"]*100:.1f}%). Evaluation outputs with identical weights match exactly in the CPU check. Parameter count and inference token count are unchanged. Peak memory was not measured.','SmallCN'),
          P('Limits: one seed and one full run per condition; timing can vary with device load. Earlier test scores influenced a follow-up LR choice, and the same official test set is reused here. Comparisons remain exploratory, with no claim of statistical significance. Frozen probing’s 5.16 s excludes feature extraction.','SmallCN'),
          P('References','H1CN'),
          P('[1] A. Dosovitskiy et al., “An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale,” ICLR 2021. <link href="https://arxiv.org/abs/2010.11929" color="#1877B9">arXiv:2010.11929</link>.','RefCN'),
          P('[2] Google Research, <link href="https://github.com/google-research/vision_transformer" color="#1877B9">vision_transformer</link>, reference implementation and pretrained ViT models.','RefCN'),
          P('[3] Y. Liu et al., “PatchDropout: Economizing Vision Transformers Using Patch Dropout,” WACV 2023. <link href="https://arxiv.org/abs/2208.07220" color="#1877B9">arXiv:2208.07220</link>.','RefCN'),
          P('Submission note: keep code and compact results; exclude downloaded weights, dataset, feature cache and large checkpoints. Final package must be below 50 MB and include the required run recording and short presentation.','SmallCN')]

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=12*mm,bottomMargin=18*mm,title='ViT-B/32 Reproduction on CIFAR-10',author='COMP5541 Group Project')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
