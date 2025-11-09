# diagnosis/ai_engine/model_loader.py
"""Singleton pattern for model loading"""
from .detect_stuttering import StutterDetector

_detector_instance = None

def get_stutter_detector():
    """Get or create singleton StutterDetector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = StutterDetector()
    return _detector_instance
