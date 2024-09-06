# engine/video_analyzer.py
import cv2
import asyncio
import aiohttp
from ultralytics import YOLO
from config.config import API_URL
from algorithms.algorithm_factory import algorithm_factory

"""
[
    {
        "cameraIp": "1.1.1.1",
        "cameraName": "camera1",
        "stream_url": "rtsp://camera1/stream",
        "taskId": "id001",
        "model": "yolov8.pt",
        "algorithm": "yolo_handler"
    },
    {
        "cameraIp": "1.1.1.1",
        "cameraName": "camera1",
        "stream_url": "rtsp://camera1/stream",
        "taskId": "id002",
        "model": "yolov8.pt",
        "algorithm": "custom_handler"
    }
]
"""

class VideoAnalyzerEngine:
    def __init__(self):
        self.api_url = API_URL
        self.camera_configs = {}  # Store configurations of each camera
        self.tasks = {}

    async def fetch_camera_model_mapping(self):
        """
        Fetch the mapping of cameras to their respective tasks and stream URLs.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/tasks") as response:
                self.camera_configs = await response.json()

    def load_tasks(self):
        """
        Load tasks and create associated handler instances based on the configurations fetched from the API.
        """
        for model_config in self.camera_configs:
            task_id = model_config['taskId']
            algorithm = model_config['algorithm']
                
            if task_id not in self.tasks:
                # Create the appropriate handler instance using the algorithm name
                self.tasks[task_id] = algorithm_factory(algorithm, model_config)

    async def process(self, task_id, algorithm):
        """
        Process the video stream for a given camera using the specified model and handler.
        """
        algorithm.detect()
        
        print(f"Stopped stream processing for camera")

    async def run_all_cameras(self):
        """
        Start processing streams for all configured cameras and tasks concurrently.
        """
        await self.fetch_camera_model_mapping()
        self.load_tasks()

        workers = []
        for task_id, algorithm in self.tasks.items():
            workers.append(self.process(task_id, algorithm))

        await asyncio.gather(*workers)

if __name__ == "__main__":
    engine = VideoAnalyzerEngine()
    asyncio.run(engine.run_all_cameras())
