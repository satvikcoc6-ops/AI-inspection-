"""Usage: python predict.py path/to/metal_nut_photo.png"""
from pathlib import Path
import argparse, json
import numpy as np
import torch
from PIL import Image
from anomalib.models import Patchcore
from anomalib.engine import Engine

parser=argparse.ArgumentParser()
parser.add_argument('image', type=Path)
parser.add_argument('--output', type=Path, default=Path('prediction'))
args=parser.parse_args()
if not args.image.is_file(): parser.error('Image file does not exist')
args.output.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(4)
root=Path(__file__).resolve().parent
model=Patchcore.load_from_checkpoint(root/'metal_nut_patchcore.ckpt',pre_trained=False,weights_only=False)
engine=Engine(accelerator='cpu',devices=1,logger=False,enable_progress_bar=False)
batch=engine.predict(model=model,data_path=args.image,return_predictions=True)[0]
score=float(batch.pred_score.reshape(-1)[0])
label=bool(batch.pred_label.reshape(-1)[0])
heat=batch.anomaly_map[0].detach().cpu().numpy().squeeze()
heat=np.clip(heat,0,1)
rgb=np.stack([heat,0.15*np.ones_like(heat),1-heat],axis=-1)
original=Image.open(args.image).convert('RGB')
overlay=Image.fromarray(np.uint8(rgb*255)).resize(original.size)
Image.blend(original,overlay,0.4).save(args.output/'heatmap_overlay.png')
result={'image':str(args.image),'status':'Anomaly detected—review required' if label else 'No anomaly detected',
 'normalized_anomaly_score':score,'score_is_probability':False,
 'defect_type':'Not classified','scope':'MVTec-style metal-nut images only',
 'note':'Experimental baseline; not validated for automotive acceptance decisions.'}
(args.output/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
