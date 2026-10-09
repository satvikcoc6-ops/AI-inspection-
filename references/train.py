"""Train a CPU-friendly PatchCore baseline; validation is separate from testing."""
from pathlib import Path
import json, os, platform
import torch
from lightning.pytorch import seed_everything
from anomalib.data import MVTecAD
from anomalib.data.utils import ValSplitMode
from anomalib.models import Patchcore
from anomalib.engine import Engine

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
torch.set_num_threads(4)
seed_everything(42, workers=True)
data = MVTecAD(root=ROOT/'data', category='metal_nut', train_batch_size=8,
    eval_batch_size=8, num_workers=0, val_split_mode=ValSplitMode.FROM_TEST,
    val_split_ratio=0.25, seed=42)
model = Patchcore(backbone='resnet18', layers=['layer2','layer3'],
    coreset_sampling_ratio=0.01, num_neighbors=3,
    pre_processor=Patchcore.configure_pre_processor(image_size=(256,256)))
engine = Engine(default_root_dir=str(ROOT/'runs'), accelerator='cpu', devices=1,
    max_epochs=1, logger=False, enable_progress_bar=False)
engine.fit(model=model, datamodule=data)
engine.trainer.save_checkpoint(str(ROOT/'metal_nut_patchcore.ckpt'))
results = engine.test(model=model, datamodule=data)
metadata={'dataset':'MVTec AD metal_nut', 'license':'CC BY-NC-SA 4.0',
    'method':'PatchCore, pretrained ResNet18, layer2+layer3, 1% coreset',
    'seed':42,'validation':'25% of original test split; remaining 75% held out',
    'benchmark_note':'Custom validation/test split, not the full official benchmark',
    'task':'normal versus anomaly with heatmap; no defect-type classifier',
    'automotive_validation':False,'test_results':results,
    'torch':torch.__version__, 'python':platform.python_version()}
for name, loader in [('train',data.train_dataloader()),('validation',data.val_dataloader()),('test',data.test_dataloader())]:
    metadata[name+'_images']=len(loader.dataset)
    frame=loader.dataset.samples
    frame.to_csv(ROOT/(name+'_manifest.csv'),index=False)
(ROOT/'evaluation.json').write_text(json.dumps(metadata,indent=2,default=str))
print(json.dumps(metadata,indent=2,default=str),flush=True)
