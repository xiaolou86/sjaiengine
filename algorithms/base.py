# algorithms/base.py
from abc import ABC, abstractmethod

class BaseAlgorithm(ABC):
    """Abstract base class for all algorithm handlers."""
    
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def process_frame(self, frame):
        """Process a single video frame."""
        pass

