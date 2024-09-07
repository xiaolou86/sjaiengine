# algorithms/base.py

import logging
import aiohttp
from abc import ABC, abstractmethod

from config.config import API_URL

logger = logging.getLogger(__name__)

class BaseAlgorithm(ABC):
    """Abstract base class for all algorithm handlers."""
    
    def __init__(self, model_config):
        self.model_config = model_config
        logger.info(f"Initialized {self.__class__.__name__} with model: {model_config}")

    @abstractmethod
    def detect(self):
        pass

    async def process_results(self):
        """
        Send a notification to the platform with detection details.
        Args:
            camera_id (str): Identifier of the camera.
            model_name (str): Model that detected the object.
            detection (object): Detected object details.
        """
        payload = {
            "camera_id": camera_id,
            "model": model_name,
            "object": detection,  # Serialize detection data as needed
            "timestamp": detection.timestamp
        }
        logger.info(f"send results {payload}")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/notify", json=payload) as response:
                if response.status == 200:
                    print(f"Notification sent for camera {camera_id} using model {model_name}")
                else:
                    print(f"Failed to send notification for camera {camera_id} using model {model_name}")

