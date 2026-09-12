import json
import cv2
from pathlib import Path

def process_split(split_path: Path):
    if not split_path.exists(): return
    metadata_file = split_path / "metadata.jsonl"
    if not metadata_file.exists(): return
    
    print(f"Processing {split_path.name}...")
    with open(metadata_file, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        record = json.loads(line)
        filename = record["file_name"]
        img_path = split_path / filename
        
        if not img_path.exists():
            continue
            
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        h, w = img.shape[:2]
        
        txt_path = split_path / f"{Path(filename).stem}.txt"
        with open(txt_path, "w") as out:
            bboxes = record.get("objects", {}).get("bbox", [])
            for bbox in bboxes:
                bx, by, bw, bh = bbox
                x_c = (bx + bw / 2) / w
                y_c = (by + bh / 2) / h
                nw = bw / w
                nh = bh / h
                out.write(f"0 {x_c:.6f} {y_c:.6f} {nw:.6f} {nh:.6f}\n")

if __name__ == "__main__":
    root = Path(__file__).parents[1] / "data" / "raw" / "ghost_pot"
    for split in ["train", "valid", "test"]:
        process_split(root / split)
        
    yaml_content = f"""
path: {root.absolute()}
train: train
val: valid
test: test

names:
  0: crab-pot
"""
    with open(root / "data.yaml", "w") as f:
        f.write(yaml_content)
    print("Ghost pot dataset prepared for YOLO format.")
