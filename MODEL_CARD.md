# Model card — Sonaris Demo Detector 0.2

**Status:** deterministic synthetic candidate generator. It is not trained, evaluated, or suitable for operational or safety decisions.

**Inputs:** PNG/JPEG/TIFF SSS-like imagery. **Preprocessing:** grayscale normalization, median filtering and CLAHE. **Outputs:** image-relative candidate box and explicitly unavailable confidence/anomaly values. No mAP, precision, recall, physical dimensions, shadow estimate, or geolocation is claimed.
