"""Reproducible training entry points for the datasets currently in SONARIS.

The tasks deliberately remain separate: Marine-PULSE is image classification,
while AI4Shipwrecks is binary semantic segmentation.  A gated Ghost Pot source
is supported only after its files are present locally.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RUNS = ROOT / "ml" / "runs"
# Keep Ultralytics' cache/settings inside the project so training also works
# under a restricted desktop account.
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "ml" / ".ultralytics"))


def require(path: Path, message: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{message}\nExpected: {path}")


def write_run_card(task: str, source: str, notes: str) -> Path:
    directory = RUNS / f"{task}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "run_card.json").write_text(json.dumps({
        "task": task,
        "source": source,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "started",
        "notes": notes,
        "warning": "Metrics must be read from the held-out evaluation output; do not claim target accuracy in advance.",
    }, indent=2), encoding="utf-8")
    return directory


def train_marine_pulse(epochs: int, image_size: int) -> None:
    """Train a four-class crop classifier on the source-provided split."""
    data = RAW / "Marine_PULSE"
    require(data / "train", "Marine_PULSE training split was not found.")
    require(data / "test", "Marine_PULSE test split was not found.")
    from ultralytics import YOLO
    run = write_run_card("marine-pulse-classification", "Marine_PULSE", "Source-provided train/test folders; classes must not be treated as full-scene detector labels.")
    model = YOLO("yolo11n-cls.pt")
    model.train(data=str(data), epochs=epochs, imgsz=image_size, device="cpu", workers=0, project=str(run), name="train", exist_ok=True, patience=max(5, epochs // 5), seed=42)
    model.val(data=str(data), split="test", device="cpu", workers=0, project=str(run), name="test", exist_ok=True)


def prepare_ghost_pot() -> None:
    """Validate a local Ghost Pot checkout without attempting a network login."""
    candidates = [RAW / "ghost_pot", RAW / "sss-crab-pot-detection-ds", RAW / "sss-crab-pot-detection"]
    root = next((item for item in candidates if item.exists()), None)
    if root is None:
        raise FileNotFoundError("Ghost Pot files are not local. Accept the Hugging Face gated terms, clone/download the dataset, then place it under data/raw/ghost_pot.")
    metadata = list(root.rglob("metadata.jsonl"))
    if not metadata:
        raise FileNotFoundError(f"No metadata.jsonl found under {root}. The Ghost Pot dataset download appears incomplete.")
    run = write_run_card("ghost-pot-detection", "PINGEcosystem/sss-crab-pot-detection-ds", "Validated JSONL annotations; conversion to YOLO is the next explicit pipeline stage.")
    (run / "sources.json").write_text(json.dumps({"root": str(root), "metadata_files": [str(p) for p in metadata]}, indent=2), encoding="utf-8")
    print(f"Ghost Pot annotations found: {len(metadata)} metadata files. Run card: {run}")


def train_ghost_pot(epochs: int, image_size: int) -> None:
    """Train a bounding-box detection model on the Ghost Pot dataset."""
    data = RAW / "ghost_pot"
    require(data / "data.yaml", "Ghost pot data.yaml was not found. Run prep_ghost_pot.py first.")
    from ultralytics import YOLO
    run = write_run_card("ghost-pot-detection", "PINGEcosystem/sss-crab-pot-detection", "Training YOLOv8 on Ghost Pot boxes.")
    model = YOLO("yolov8n.pt")
    model.train(data=str(data / "data.yaml"), epochs=epochs, imgsz=image_size, device="cpu", workers=0, project=str(run), name="train", exist_ok=True, patience=max(10, epochs // 4), seed=42)
    try:
        model.val(device="cpu", workers=0, project=str(run), name="test", exist_ok=True)
    except Exception:
        pass

def train_ai4shipwrecks(epochs: int, image_size: int) -> None:
    """Train a segmentation model on AI4Shipwrecks."""
    data = RAW / "ai4shipwrecks"
    require(data / "data.yaml", "ai4shipwrecks data.yaml was not found. Run prep_ai4shipwrecks.py first.")
    from ultralytics import YOLO
    run = write_run_card("ai4shipwrecks-segmentation", "AI4Shipwrecks", "Training YOLOv8-seg on AI4Shipwrecks dataset.")
    model = YOLO("yolov8n-seg.pt") 
    model.train(data=str(data / "data.yaml"), epochs=epochs, imgsz=image_size, device="cpu", workers=0, project=str(run), name="train", exist_ok=True, patience=max(10, epochs // 4), seed=42)
    try:
        model.val(device="cpu", workers=0, project=str(run), name="test", exist_ok=True)
    except Exception:
        pass

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["marine-pulse", "ghost-pot-check", "ghost-pot-train", "ai4shipwrecks"])
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=320)
    args = parser.parse_args()
    if args.task == "marine-pulse": train_marine_pulse(args.epochs, args.imgsz)
    elif args.task == "ai4shipwrecks": train_ai4shipwrecks(args.epochs, args.imgsz)
    elif args.task == "ghost-pot-train": train_ghost_pot(args.epochs, args.imgsz)
    else: prepare_ghost_pot()

if __name__ == "__main__":
    main()
