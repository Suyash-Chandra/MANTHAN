# Architecture

`frontend/` is the React inspection workstation. `backend/` validates uploads, exposes the local API and exports reports. `ml/` owns preprocessing and inference contracts. A future SQLite repository replaces the in-memory MVP store.

Analysis: validated image → OpenCV decode → grayscale/median/CLAHE preprocessing → detector → review → report. The present detector returns one deterministic synthetic candidate and declares `DEMO_SYNTHETIC` on every response.
