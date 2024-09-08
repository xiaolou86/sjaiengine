# algorithms/base.py

import logging
import requests
from abc import ABC, abstractmethod

from config.config import API_URL

logger = logging.getLogger(__name__)

class BaseAlgorithm(ABC):
    """Abstract base class for all algorithm handlers."""
    
    def __init__(self, model_config):
        self.model_config = model_config
        self.api_url = API_URL

        logger.info(f"Initialized {self.__class__.__name__} with model: {model_config}")

    @abstractmethod
    def detect(self):
        pass

    def process_results(self, alarm_data):
        """
        Send a notification to the platform with detection details.
        Args:
            camera_id (str): Identifier of the camera.
            model_name (str): Model that detected the object.
            detection (object): Detected object details.
        """
        alarm_data["id"] = 1
        alarm_data["terminalId"] = 1
        alarm_data["cameraIp"] = "1.1.1.1"
        alarm_data["cameraName"] = "cameraName"
        payload = alarm_data
        logger.info(f"send results {payload}")
        try:
            response = requests.post(f"{self.api_url}/notify", json=payload)
            logger.info(response.status_code)
            if response.status_code == 200:
                response_data = response.json()
                logger.info(response_data)
            else:
                logger.error(f"Failed to send notification for camera")
        except requests.RequestException as e:
            logger.error(e)

