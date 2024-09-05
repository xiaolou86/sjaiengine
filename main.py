import cv2
import asyncio
import aiohttp
from ultralytics import YOLO
from config import API_URL

class VideoAnalyzerEngine:
    def __init__(self):
        self.api_url = API_URL
        self.camera_configs = {}  # Store configurations of each camera
        self.models = {}  # Store loaded models

    async def fetch_camera_model_mapping(self):
        """
        Fetch the mapping of cameras to their respective models and stream URLs.
        Example response:
        {
            "camera1": {
                "stream_url": "rtsp://camera1/stream",
                "models": ["model1", "model2"]
            },
            "camera2": {
                "stream_url": "rtsp://camera2/stream",
                "models": ["model2"]
            }
        }
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/camera-models") as response:
                self.camera_configs = await response.json()

    def load_models(self):
        """
        Load models based on the configurations fetched from the API.
        Models are loaded once and reused across cameras.
        """
        model_names = set(
            model_name for config in self.camera_configs.values() for model_name in config['models']
        )
        for model_name in model_names:
            # Load each model dynamically
            self.models[model_name] = YOLO(f'/path/to/{model_name}.pt')

    async def process_stream(self, camera_id, config):
        """
        Process the video stream for a given camera using the associated models.
        Args:
            camera_id (str): Identifier of the camera.
            config (dict): Configuration containing stream URL and associated models.
        """
        stream_url = config['stream_url']
        model_names = config['models']
        
        print(f"Starting stream processing for camera {camera_id} using models {model_names}")
        
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            print(f"Failed to open stream for camera {camera_id}")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame with each associated model
            for model_name in model_names:
                model = self.models.get(model_name)
                if model:
                    results = model(frame)
                    await self.process_results(camera_id, model_name, results)

        cap.release()
        print(f"Stopped stream processing for camera {camera_id}")

    async def process_results(self, camera_id, model_name, results):
        """
        Process detection results and notify the platform if necessary.
        Args:
            camera_id (str): Identifier of the camera.
            model_name (str): Model that was used for detection.
            results (list): List of detection results.
        """
        for result in results:
            if self.is_object_of_interest(result):
                await self.notify_platform(camera_id, model_name, result)

    def is_object_of_interest(self, result):
        """
        Determine if the detected object is of interest.
        This function should contain logic to filter detections.
        """
        # Implement filtering logic here
        return True

    async def notify_platform(self, camera_id, model_name, detection):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_url}/notify", json=payload) as response:
                if response.status == 200:
                    print(f"Notification sent for camera {camera_id} using model {model_name}")
                else:
                    print(f"Failed to send notification for camera {camera_id} using model {model_name}")

    async def run_all_cameras(self):
        """
        Start processing streams for all configured cameras concurrently.
        """
        await self.fetch_camera_model_mapping()
        self.load_models()

        tasks = [
            self.process_stream(camera_id, config)
            for camera_id, config in self.camera_configs.items()
        ]

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    engine = VideoAnalyzerEngine()
    asyncio.run(engine.run_all_cameras())
