import cv2
import numpy as np
from pathlib import Path

def process_split(split_dir: Path):
    if not split_dir.exists(): return
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"
    if not images_dir.exists() or not labels_dir.exists(): return
    
    print(f"Processing {split_dir.name}...")
    for mask_path in labels_dir.glob("*.png"):
        img_path = images_dir / mask_path.name
        if not img_path.exists():
            img_path = images_dir / mask_path.with_suffix('.jpg').name
            if not img_path.exists(): continue
            
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        img = cv2.imread(str(img_path))
        if mask is None or img is None: continue
        
        h, w = img.shape[:2]
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        txt_path = labels_dir / f"{mask_path.stem}.txt"
        with open(txt_path, "w") as out:
            for contour in contours:
                if cv2.contourArea(contour) < 20: continue
                poly = contour.flatten().astype(float)
                poly[0::2] /= w
                poly[1::2] /= h
                
                poly_str = " ".join([f"{val:.6f}" for val in poly])
                out.write(f"0 {poly_str}\n")

if __name__ == "__main__":
    root = Path(__file__).parents[1] / "data" / "raw" / "ai4shipwrecks"
    for split in ["train", "test"]:
        process_split(root / split)
        
    yaml_content = f"""
path: {root.absolute()}
train: train/images
val: test/images
test: test/images

names:
  0: shipwreck
"""
    with open(root / "data.yaml", "w") as f:
        f.write(yaml_content)
    print("ai4shipwrecks prepared for YOLO segmentation format.")
