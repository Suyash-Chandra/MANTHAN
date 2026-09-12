# 🌊 MANTHAN
**M**arine **A**nomaly **N**avigation, **T**racking & **H**azard **A**nalysis **N**etwork

![MANTHAN Tech Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20YOLOv8-06b6d4?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20%2F%20MVP-success?style=for-the-badge)

MANTHAN is an advanced, AI-powered underwater telemetry dashboard built to automatically detect marine debris, shipwrecks, subsea cables, and ghost pots using raw side-scan sonar imagery. Designed for speed and accuracy, the system acts as a "smart radar," processing underwater acoustic data in real time and providing precise geospatial metadata for human-in-the-loop review workflows.

---

### 🚀 Key Features

*   **Multi-Model Neural Network Inference:** Instead of relying on a single detection algorithm, MANTHAN simultaneously feeds data through **4 concurrent YOLOv8 Neural Networks** to accurately classify Shipwrecks (Segmentation), Marine Debris, and Ghost Pots (Bounding Box Detection) in a single pass.
*   **Acoustic Signal Pre-Processing:** Uses OpenCV to algorithmically clean raw sonar imagery before AI ingestion. It applies **CLAHE** (Contrast Limited Adaptive Histogram Equalization) and Median Blurring to eliminate speckle noise caused by suspended sea sand.
*   **Dynamic GIS Clustering:** Anomalies are mapped with extreme precision. The system deterministically anchors each sonar scan and calculates micro-degree Latitude/Longitude offsets for every detected target based on its internal pixel geometry. 
*   **Human-In-The-Loop (HITL):** A premium Glassmorphism UI allows sonar operators to review the neural network's findings, visually confirm/reject anomalies, and immediately export fully structured JSON/CSV evidence reports for dive teams.

---

### 🛠️ Technology Stack
*   **Frontend User Interface:** React, TypeScript, Vite, CSS (Custom Glassmorphism UI), OpenStreetMap.
*   **Backend & File Handling:** FastAPI (Python), Uvicorn, Pydantic.
*   **AI / Machine Learning:** Ultralytics YOLOv8, OpenCV, NumPy.

---

### ⚙️ How to Run Locally

Because MANTHAN handles heavy image processing and AI execution, it is split into two connected local servers.

#### 1. Start the API & AI Engine (Backend)
Open a terminal in the `backend` directory and activate the environment:
```bash
# Windows
.\venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Mac/Linux
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

#### 2. Start the Mission Dashboard (Frontend)
Open a new terminal in the `frontend` directory:
```bash
npm install
npm run dev
```

Navigate to `http://localhost:5173` in your browser. Upload a standard PNG/TIFF side-scan sonar image in the **Analyze Workspace** to trigger the AI inference pipeline!

---
*Powered by Team TATSARVA*
