"""Inference engine — loads all available YOLO models and falls back to
enhanced OpenCV heuristics when no weights are present."""
from __future__ import annotations
import hashlib
from typing import Any
from pathlib import Path
import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "ml" / "runs"


def _find_all_weights() -> list[Path]:
    """Return every best.pt under ml/runs, sorted newest-first."""
    if not RUNS_DIR.exists():
        return []
    found = list(RUNS_DIR.rglob("best.pt"))
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


class SonarDetector:
    def __init__(self, model_path: str | None = None, demo_mode: bool = True):
        self.model_path = model_path
        self.demo_mode = demo_mode
        self.yolo_models: list[tuple[str, Any]] = []   # (label, model)
        self.model_name = "MANTHAN Heuristic Engine 0.3"
        self.inference_mode = "DEMO_SYNTHETIC"

        weights = _find_all_weights()
        if weights:
            try:
                from ultralytics import YOLO
                for w in weights:
                    tag = w.parent.parent.parent.name  # e.g. "ai4shipwrecks-seg…"
                    model = YOLO(str(w))
                    self.yolo_models.append((tag, model))
                    print(f"[MANTHAN] Loaded: {tag}  →  {w}")
                if self.yolo_models:
                    self.model_name = f"YOLOv8 Multi-Model ({len(self.yolo_models)} models)"
                    self.inference_mode = "YOLOv8_AI"
            except Exception as exc:
                print(f"[MANTHAN] YOLO load failed: {exc}")

    # ------------------------------------------------------------------ #
    #  Main entry point                                                    #
    # ------------------------------------------------------------------ #
    def predict(self, image: np.ndarray, image_identity: str) -> list[dict[str, Any]]:
        detections: list[dict[str, Any]] = []

        # ---------- YOLO pass (run EVERY loaded model) ----------
        if self.yolo_models:
            det_idx = 0
            for tag, model in self.yolo_models:
                try:
                    results = model(image, conf=0.15, iou=0.4, verbose=False)[0]

                    for box in results.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls_idx = int(box.cls[0].cpu().numpy())
                        cls_name = results.names[cls_idx].upper()

                        w_px = x2 - x1
                        h_px = y2 - y1

                        detections.append({
                            "detection_id": f"YOLO-{image_identity[:4]}-{det_idx}",
                            "class_name": cls_name,
                            "confidence": round(conf, 4),
                            "anomaly_score": int(conf * 100),
                            "priority": "CRITICAL" if conf > 0.5 else ("HIGH" if conf > 0.3 else "MEDIUM"),
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "estimated_dimensions": f"{w_px * 0.1:.1f}m × {h_px * 0.1:.1f}m",
                            "shadow_length_px": int(h_px * 0.8),
                            "shadow_direction": "SW",
                            "_inference_meta": {
                                "mode": "YOLOv8_AI",
                                "version": f"YOLOv8 ({tag})",
                            },
                        })
                        det_idx += 1
                except Exception as exc:
                    print(f"[MANTHAN] Model '{tag}' inference error: {exc}")

        if detections:
            return detections

        # ---------- Enhanced OpenCV heuristic fallback ----------
        return self._heuristic_detect(image, image_identity)

    # ------------------------------------------------------------------ #
    #  Enhanced heuristic detector (OpenCV)                                #
    # ------------------------------------------------------------------ #
    def _heuristic_detect(self, image: np.ndarray, image_identity: str) -> list[dict[str, Any]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        h_img, w_img = gray.shape[:2]
        img_area = h_img * w_img

        # --- Multi-scale preprocessing for better anomaly isolation ---
        # 1. CLAHE to enhance local contrast in sonar imagery
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 2. Adaptive threshold — captures anomalies across varying backgrounds
        thresh = cv2.adaptiveThreshold(
            cv2.medianBlur(enhanced, 7),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31,
            C=-8,
        )

        # 3. Morphological operations to group nearby blobs
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close, iterations=2)
        morphed = cv2.morphologyEx(morphed, cv2.MORPH_OPEN, kernel_open, iterations=1)

        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # --- Filter: ignore too-small noise and too-large border junk ---
        min_area = max(200, img_area * 0.002)
        max_area = img_area * 0.55
        good = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
        good.sort(key=cv2.contourArea, reverse=True)

        detections: list[dict[str, Any]] = []
        for idx, contour in enumerate(good[:5]):     # top-5 anomalies
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            # Pad bounding box slightly for better visual fit
            pad_x = int(w * 0.08)
            pad_y = int(h * 0.08)
            x = max(0, x - pad_x)
            y = max(0, y - pad_y)
            w = min(w_img - x, w + 2 * pad_x)
            h = min(h_img - y, h + 2 * pad_y)

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull) or 1
            solidity = area / hull_area
            aspect = max(w, h) / max(min(w, h), 1)

            # Classification heuristics
            if aspect > 5.0:
                cls_name, priority = "SUBSEA CABLE / PIPE", "HIGH"
            elif area > (img_area * 0.08) and solidity > 0.85:
                cls_name, priority = "SHIPWRECK", "CRITICAL"
            elif area > (img_area * 0.03):
                cls_name, priority = "SHIPWRECK", "CRITICAL"
            elif solidity > 0.90 and aspect < 1.6 and area < (img_area * 0.02):
                cls_name, priority = "CRAB POT / DEBRIS", "MEDIUM"
            else:
                cls_name, priority = "MARINE DEBRIS", "MEDIUM"

            conf = min(0.95, 0.55 + (area / img_area) * 3)
            detections.append({
                "detection_id": f"DEMO-{image_identity[:4]}-{idx}",
                "class_name": cls_name,
                "confidence": round(conf, 4),
                "anomaly_score": min(100, int(55 + solidity * 35)),
                "priority": priority,
                "bbox": [x, y, x + w, y + h],
                "estimated_dimensions": f"{w * 0.1:.1f}m × {h * 0.1:.1f}m",
                "shadow_length_px": int(h * 0.8),
                "shadow_direction": "SW",
                "_inference_meta": {
                    "mode": "DEMO_ENHANCED",
                    "version": self.model_name,
                },
            })

        # Ultimate fallback — scan centre
        if not detections:
            bw = max(60, w_img // 4)
            bh = max(50, h_img // 5)
            cx, cy = w_img // 2 - bw // 2, h_img // 2 - bh // 2
            detections.append({
                "detection_id": f"DEMO-{image_identity[:6]}",
                "class_name": "UNIDENTIFIED ANOMALY",
                "confidence": 0.40,
                "anomaly_score": 40,
                "priority": "LOW",
                "bbox": [cx, cy, cx + bw, cy + bh],
                "estimated_dimensions": "Unknown",
                "shadow_length_px": 0,
                "shadow_direction": "None",
                "_inference_meta": {
                    "mode": "DEMO_SYNTHETIC",
                    "version": self.model_name,
                },
            })

        return detections
