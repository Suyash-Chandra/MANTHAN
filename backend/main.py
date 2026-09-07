"""Local API for the SONARIS sonar-analysis MVP."""
from __future__ import annotations
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.inference import SonarDetector
from ml.preprocessing import SonarPreprocessor

app = FastAPI(title="SONARIS API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/tiff", "image/x-tiff"}
detector, preprocessor = SonarDetector(demo_mode=True), SonarPreprocessor()
DETECTIONS: dict[str, dict] = {}

class FeedbackRequest(BaseModel):
    action: Literal["CONFIRM", "REJECT", "RECOVERY_QUEUE", "RECLASSIFY"]
    new_class: str | None = None

def demo_detection(image_id: str, width: int, height: int) -> dict:
    result = detector.predict(image_id, image_size=(width, height))[0]
    result.update({"image_id": image_id, "status": "NEW", "inference_mode": "DEMO_SYNTHETIC", "model_version": "Sonaris Demo Detector 0.2", "geolocation_status": "unavailable — no positional metadata supplied", "latitude": None, "longitude": None, "timestamp": datetime.now(timezone.utc).isoformat()})
    return result

@app.get("/")
def root() -> dict:
    return {"name": "SONARIS", "mode": "demo", "message": "Local sonar intelligence API"}

@app.get("/api/survey")
def survey() -> dict:
    return {"name": "THUNDER BAY — DEMO SURVEY", "status": "DEMO DATA — NOT OPERATIONAL METRICS", "is_demo": True, "images_processed": 0, "detections": len(DETECTIONS), "message": "Upload sonar imagery to begin a local demo analysis."}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Supported formats: PNG, JPEG, TIFF.")
    blob = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(blob) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Upload exceeds 25 MB limit.")
    image = cv2.imdecode(np.frombuffer(blob, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(422, "The uploaded file is not a readable image.")
    height, width = image.shape[:2]
    image_id = hashlib.sha256(blob).hexdigest()[:12]
    processed = preprocessor.preprocess(image)
    detection = demo_detection(image_id, width, height)
    detection.update({"preprocessing": preprocessor.describe(), "processed_shape": list(processed.shape[:2])})
    DETECTIONS[detection["detection_id"]] = detection
    return {"status": "success", "mode": "DEMO_SYNTHETIC", "disclaimer": "Synthetic demo result, not a scientific prediction or trained-model inference.", "processing_time_ms": 0, "detections": [detection]}

@app.get("/api/detections")
def list_detections() -> list[dict]: return list(DETECTIONS.values())

@app.get("/api/detections/{detection_id}")
def get_detection(detection_id: str) -> dict:
    if detection_id not in DETECTIONS: raise HTTPException(404, "Detection not found")
    return DETECTIONS[detection_id]

@app.post("/api/detections/{detection_id}/feedback")
def feedback(detection_id: str, request: FeedbackRequest) -> dict:
    item = get_detection(detection_id)
    if request.action == "RECLASSIFY":
        if not request.new_class or len(request.new_class) > 64: raise HTTPException(422, "A short replacement class is required.")
        item.update({"class_name": request.new_class.upper(), "status": "REVIEWED"})
    else: item["status"] = {"CONFIRM": "CONFIRMED", "REJECT": "REJECTED", "RECOVERY_QUEUE": "RECOVERY QUEUE"}[request.action]
    item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return item

@app.get("/api/report/json")
def report_json() -> StreamingResponse:
    return StreamingResponse(io.BytesIO(json.dumps(list(DETECTIONS.values()), indent=2).encode()), media_type="application/json", headers={"Content-Disposition": "attachment; filename=sonaris-report.json"})

@app.get("/api/report/csv")
def report_csv() -> StreamingResponse:
    output = io.StringIO(); fields = ["detection_id", "class_name", "confidence", "anomaly_score", "priority", "status", "image_id", "inference_mode", "geolocation_status", "estimated_dimensions", "shadow_length_px"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(DETECTIONS.values())
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sonaris-report.csv"})

@app.get("/api/model")
def model() -> dict:
    return {"name": "Sonaris Demo Detector", "version": "0.2", "mode": "DEMO_SYNTHETIC", "evaluation": "Not evaluated yet", "supported_classes": ["Unknown Anomaly (demo only)"], "note": "A YOLO adapter will replace this only when validated local weights are supplied."}
