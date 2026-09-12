# Training SONARIS models

SONARIS has separate models because the source annotations represent different tasks:

| Source | Task | Integration state |
| --- | --- | --- |
| AI4Shipwrecks | Binary shipwreck segmentation | Raw masks are present. Preserve the supplied site-level train/test split. |
| Marine_PULSE | Four-class target-crop classification | Ready for local training. These are not full-scene detection labels. |
| Ghost Pot | Full-scene crab-pot bounding-box detection | Gated dataset; download required before conversion/training. |

## Marine-PULSE baseline

```powershell
backend\venv\Scripts\python ml\train.py marine-pulse --epochs 30 --imgsz 320
```

This CPU-only machine will train slowly. Read the held-out `test` metrics created in `ml/runs/`; do not promise a threshold until they are measured.

## Ghost Pot gated download

1. Sign into Hugging Face and accept the dataset's contact-sharing terms.
2. Install `datasets` and `huggingface_hub` in the training environment.
3. Authenticate with `huggingface-cli login`.
4. Download into `data/raw/ghost_pot`, then validate it:

```powershell
backend\venv\Scripts\python ml\train.py ghost-pot-check
```

The code snippet `load_dataset("PINGEcosystem/sss-crab-pot-detection-ds")` does not itself place data in this repository or grant access. It will prompt/fail until the gated terms have been accepted.
