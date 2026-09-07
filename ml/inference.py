"""Inference contracts; demo mode never presents output as model inference."""
from __future__ import annotations
import hashlib
from typing import Any

class SonarDetector:
    def __init__(self, model_path: str | None = None, demo_mode: bool = True):
        self.model_path, self.demo_mode = model_path, demo_mode
        if not demo_mode: raise RuntimeError("Real model loading is not configured. Supply validated local weights first.")

    def predict(self, image_identity: str, image_size: tuple[int, int]) -> list[dict[str, Any]]:
        width, height = image_size; digest = int(hashlib.sha256(image_identity.encode()).hexdigest()[:8], 16)
        bw, bh = max(40, width // 5), max(30, height // 7)
        x = min(max(0, (digest % max(width, 1)) - bw // 2), max(0, width - bw)); y = min(max(0, ((digest >> 8) % max(height, 1)) - bh // 2), max(0, height - bh))
        return [{"detection_id": f"DEMO-{hashlib.sha256(image_identity.encode()).hexdigest()[:6].upper()}", "class_name": "UNKNOWN ANOMALY", "confidence": 0.0, "anomaly_score": 0, "priority": "UNASSESSED", "bbox": [x, y, x + bw, y + bh], "estimated_dimensions": "Unavailable — pixel scale not supplied", "shadow_length_px": None, "shadow_direction": "Not assessed in demo mode"}]
