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

import random

def get_demo_detections(image: np.ndarray, image_id: str) -> list[dict]:
    results = detector.predict(image, image_id)
    
    # Deterministic base coordinate for this specific sonar image
    import struct
    hash_val = int(hashlib.md5(image_id.encode()).hexdigest()[:8], 16)
    
    # Base location in Thunder Bay: 45.0 N, -83.0 W
    base_lat = 45.0 + ((hash_val % 1000) / 10000.0) - 0.05
    base_lon = -83.0 + (((hash_val // 1000) % 1000) / 10000.0) - 0.05
    
    h_img, w_img = image.shape[:2]
    
    for i, res in enumerate(results):
        # Extract pixel center of the anomaly
        bbox = res.get("bbox", [0, 0, 0, 0])
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        
        # Offset lat/lon based on pixel position (assuming 1 pixel = ~5cm)
        # 1 degree lat = ~111,000 meters
        lat_offset = -((cy - h_img/2) * 0.0000005)
        lon_offset = ((cx - w_img/2) * 0.0000005)
        
        lat = base_lat + lat_offset
        lon = base_lon + lon_offset
        
        meta = res.pop("_inference_meta", {})
        
        res.update({
            "image_id": image_id, 
            "status": "NEW", 
            "inference_mode": meta.get("mode", "DEMO_SYNTHETIC"), 
            "model_version": meta.get("version", "Sonaris Demo Detector 0.2"), 
            "geolocation_status": "Simulated Demo Coordinate", 
            "latitude": round(lat, 6), 
            "longitude": round(lon, 6), 
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    return results

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
    
    import numpy as np
    image = cv2.imdecode(np.frombuffer(blob, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(422, "The uploaded file is not a readable image.")
    
    height, width = image.shape[:2]
    image_id = hashlib.sha256(blob).hexdigest()[:12]
    processed = preprocessor.preprocess(image)
    
    detections = get_demo_detections(processed, image_id)
    for d in detections:
        d.update({"preprocessing": preprocessor.describe(), "processed_shape": list(processed.shape[:2])})
        DETECTIONS[d["detection_id"]] = d
        
    return {"status": "success", "mode": "DEMO_SYNTHETIC", "disclaimer": "Synthetic demo result", "processing_time_ms": 0, "detections": detections}

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
    return {"name": detector.model_name, "version": "1.0", "mode": detector.inference_mode, "models_loaded": len(detector.yolo_models), "supported_classes": ["Shipwreck", "Crab-Pot", "Marine Debris", "Subsea Cable / Pipe"], "note": f"Running {len(detector.yolo_models)} YOLO model(s)" if detector.yolo_models else "Heuristic fallback mode"}
