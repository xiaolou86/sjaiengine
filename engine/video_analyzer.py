# engine/video_analyzer.py
import cv2
import asyncio
import aiohttp
from ultralytics import YOLO
from config.config import API_URL
from algorithms.algorithm_factory import algorithm_factory

class VideoAnalyzerEngine:
    def __init__(self):
        self.api_url = API_URL
        self.camera_configs = {}  # Store configurations of each camera
        self.models = {}  # Store loaded models and their associated handlers

    async def fetch_camera_model_mapping(self):
        """
        Fetch the mapping of cameras to their respective models and stream URLs.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/camera-models") as response:
                self.camera_configs = await response.json()

    def load_models(self):
        """
        Load models and create associated handler instances based on the configurations fetched from the API.
        """
        for config in self.camera_configs.values():
            for model_config in config['models']:
                model_name = model_config['name']
                algorithm = model_config['algorithm']
                
                if model_name not in self.models:
                    # Load the model dynamically
                    model = YOLO(f'/path/to/{model_name}.pt')
                    # Create the appropriate handler instance using the algorithm name
                    self.models[model_name] = algorithm_factory(algorithm, model)

    async def process_stream(self, camera_id, model_name, stream_url):
        """
        Process the video stream for a given camera using the specified model and handler.
        Args:
            camera_id (str): Identifier of the camera.
            model_name (str): Model to be used for detection.
            stream_url (str): URL of the camera stream.
        """
        print(f"Starting stream processing for camera {camera_id} using model {model_name}")
        
        cap = cv2.VideoCapture(stream_url)

        if not cap.isOpened():
            print(f"Failed to open stream for camera {camera_id}")
            return

        handler = self.models.get(model_name)

        if not handler:
            print(f"No handler found for model name {model_name}")
            cap.release()
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Use the handler to process the frame with the model
            results = handler.process_frame(frame)
            await self.process_results(camera_id, model_name, results)

        cap.release()
        print(f"Stopped stream processing for camera {camera_id} using model {model_name}")

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
        Start processing streams for all configured cameras and models concurrently.
        """
        await self.fetch_camera_model_mapping()
        self.load_models()

        tasks = []
        for camera_id, config in self.camera_configs.items():
            stream_url = config['stream_url']
            for model_config in config['models']:
                model_name = model_config['name']
                tasks.append(self.process_stream(camera_id, model_name, stream_url))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    engine = VideoAnalyzerEngine()
    asyncio.run(engine.run_all_cameras())
