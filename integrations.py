"""Provider contracts for future integrations. No unconfigured provider is invoked."""
from typing import Protocol, TypedDict
from PIL import Image


class Detection(TypedDict):
    label: str
    confidence: float
    box_xyxy: tuple[float, float, float, float]


class DefectDetector(Protocol):
    def detect(self, image: Image.Image) -> list[Detection]: ...


class ExplanationProvider(Protocol):
    def explain(self, inspection: dict, detections: list[Detection]) -> str: ...
