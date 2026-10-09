"""Cached, CPU-only inference with the original trained PatchCore checkpoint."""
from pathlib import Path
from threading import Lock
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
CHECKPOINT = ROOT / 'references' / 'metal_nut_patchcore.ckpt'


class PatchCoreService:
    name = 'PatchCore / ResNet18'
    def __init__(self):
        self.model = None
        self.lock = Lock()

    def load(self):
        if self.model is None:
            import torch
            from anomalib.models import Patchcore
            torch.set_num_threads(4)
            self.model = Patchcore.load_from_checkpoint(
                str(CHECKPOINT), map_location='cpu', pre_trained=False, weights_only=False
            ).eval().cpu()
            # Newer torchvision checkpoints serialize interpolation as a string.
            # torchvision 0.21 needs the equivalent enum at execution time.
            from torchvision.transforms import InterpolationMode
            pending = list(self.model.pre_processor.modules())
            while pending:
                module = pending.pop()
                pending.extend(getattr(module, 'transforms', []))
                if isinstance(getattr(module, 'interpolation', None), str):
                    module.interpolation = InterpolationMode(module.interpolation)
        return self.model

    def predict(self, image: Image.Image):
        import torch
        from torchvision.transforms.functional import to_tensor
        with self.lock, torch.inference_mode():
            model = self.load()
            # Match Engine.predict's callback path, including antialiasing.
            batch = model.pre_processor.transform(to_tensor(image).unsqueeze(0))
            prediction = model.model(batch)
            prediction = model.post_processor(prediction)
            score = float(prediction.pred_score.reshape(-1)[0])
            anomaly = bool(prediction.pred_label.reshape(-1)[0])
            heat = prediction.anomaly_map[0].cpu().numpy().squeeze()
        heat = np.clip(heat, 0, 1)
        # Fixed color scale across inspections; low scores remain transparent.
        colors = np.stack([np.clip(1.5-abs(4*heat-3),0,1),
                           np.clip(1.5-abs(4*heat-2),0,1),
                           np.clip(1.5-abs(4*heat-1),0,1)], axis=-1)
        color = Image.fromarray((colors*255).astype('uint8')).resize(image.size)
        alpha = Image.fromarray((heat*150).astype('uint8')).resize(image.size)
        overlay = Image.composite(color, image, alpha)
        return {'normalized_anomaly_score': score, 'is_anomaly': anomaly,
                'decision': 'REVIEW' if anomaly else 'NORMAL',
                'status': 'Anomaly detected - review required' if anomaly else 'No anomaly detected',
                'threshold': 0.5, 'score_is_probability': False,
                'model': self.name, 'scope': 'MVTec-style metal-nut images only',
                'defect_type': 'Not classified'}, overlay, heat


service = PatchCoreService()
