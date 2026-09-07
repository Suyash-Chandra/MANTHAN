import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SonarDatasetAdapter:
    """Base adapter for loading various side-scan sonar datasets."""
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement load()")
        
class AI4ShipwrecksAdapter(SonarDatasetAdapter):
    def load(self) -> List[Dict[str, Any]]:
        # Implementation of loading AI4Shipwrecks format
        # Normalizes to an internal format
        logger.info(f"Loading AI4Shipwrecks dataset from {self.data_dir}")
        samples = []
        # In a real scenario, this parses the XML/JSON from AI4Shipwrecks
        return samples

class YOLOAdapter(SonarDatasetAdapter):
    def load(self) -> List[Dict[str, Any]]:
        # Implementation of loading YOLO format annotations
        logger.info(f"Loading YOLO dataset from {self.data_dir}")
        samples = []
        # In a real scenario, this parses the YOLO txt files
        return samples

def normalize_dataset(adapter: SonarDatasetAdapter) -> List[Dict[str, Any]]:
    """Loads and normalizes the dataset using the provided adapter."""
    return adapter.load()
