# SONARIS

AI-powered automated underwater marine-debris and anomaly detection using side-scan sonar imagery.

This local workstation MVP currently uses deterministic demo logic—not a trained or evaluated model.

Run the API with `backend\\venv\\Scripts\\python -m uvicorn backend.main:app --reload --port 8000`, then run `npm run dev` from `frontend`. Upload PNG, JPEG or TIFF in **Analyze** to create a clearly marked synthetic demo candidate, review it, and export JSON/CSV.

See [ARCHITECTURE.md](ARCHITECTURE.md), [DATASETS.md](DATASETS.md), [MODEL_CARD.md](MODEL_CARD.md), and [API.md](API.md).
