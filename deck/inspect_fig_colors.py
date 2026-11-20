from PIL import Image
import pathlib, collections
D = pathlib.Path("results/figures")
for name in ["full_finetune_paper_lr_1000_attention.png","full_finetune_paper_lr_1000_confusion_matrix.png","position_similarity.png","efficiency_tradeoff.png","efficiency_validation_curves.png","test_accuracy_comparison.png"]:
    im = Image.open(D/name).convert("RGB")
    w,h = im.size
    im2 = im.resize((400, max(1,int(400*h/w))))
    small = im2.resize((160,160))
    cnt = collections.Counter(small.getdata())
    top = cnt.most_common(12)
    print(name, (w,h))
    for c,n in top:
        print("   ", c, n)
