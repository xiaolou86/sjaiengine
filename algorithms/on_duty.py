# algorithms/yolo.py
from .base import BaseAlgorithm

class OnDutyAlgorithm(BaseAlgorithm):
    """Handler for YOLO-based models."""
    
    def process_frame(self, frame):
        # Implement YOLO processing logic here
        return self.model(frame)  # Replace with actual logic

