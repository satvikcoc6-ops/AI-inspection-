"""Check imports and execute a real trained-model prediction."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
from model_service import service, ROOT, CHECKPOINT

if __name__ == '__main__':
    import importlib.metadata as metadata
    print('Python:',sys.version)
    for name in ('torch','torchvision','anomalib','fastapi','reportlab'):
        print(name,metadata.version(name))
    print('Checkpoint:',CHECKPOINT, CHECKPOINT.is_file())
    for sample in ('good','bent','scratch'):
        result,_,_=service.predict(Image.open(ROOT/'references'/'examples'/f'{sample}.png').convert('RGB'))
        print(sample,result)
