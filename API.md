# API

`POST /api/analyze` accepts an image up to 25 MB and returns a `DEMO_SYNTHETIC` candidate. `GET /api/detections` lists the local session. `POST /api/detections/{id}/feedback` accepts `CONFIRM`, `REJECT`, `RECOVERY_QUEUE`, or `RECLASSIFY`. `GET /api/report/csv` and `/api/report/json` export the session. `GET /api/model` reports the demo detector's unevaluated state.
