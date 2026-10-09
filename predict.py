"""Standalone CLI using the same repaired model loader as the dashboard."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageOps
from model_service import service

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('image',type=Path)
    parser.add_argument('--output',type=Path,default=Path('prediction'))
    args=parser.parse_args()
    if not args.image.is_file():
        parser.error('Image file does not exist')
    with Image.open(args.image) as im:
        image=ImageOps.exif_transpose(im).convert('RGB')
    result,overlay,heat=service.predict(image)
    args.output.mkdir(parents=True,exist_ok=True)
    overlay.save(args.output/'heatmap_overlay.png')
    import numpy as np
    np.save(args.output/'anomaly_map.npy',heat,allow_pickle=False)
    (args.output/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
