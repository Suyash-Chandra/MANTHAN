import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SonarPreprocessor:
    """
    Handles preprocessing of side-scan sonar imagery to improve detection
    and handle sonar-specific artifacts (speckle, contrast).
    """
    def __init__(self, config: dict = None):
        self.config = config or {
            "clahe_clip_limit": 2.0,
            "clahe_tile_grid": (8, 8),
            "median_blur_ksize": 5
        }
        
    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(
            clipLimit=self.config["clahe_clip_limit"],
            tileGridSize=self.config["clahe_tile_grid"]
        )
        return clahe.apply(image)
        
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        # 1. Grayscale normalization
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # 2. Denoising (Median filter for speckle reduction)
        denoised = cv2.medianBlur(gray, self.config["median_blur_ksize"])
        
        # 3. Contrast enhancement (CLAHE)
        enhanced = self.apply_clahe(denoised)
        
        return enhanced

    def describe(self) -> list[str]:
        return ["grayscale normalization", "median speckle reduction", "CLAHE contrast enhancement"]
