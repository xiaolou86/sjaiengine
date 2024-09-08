# algorithms/yolo.py
from .base import BaseAlgorithm
import cv2
import time
import logging
from pathlib import Path

from ultralytics import YOLO
from ultralytics.utils.files import increment_path

logger = logging.getLogger(__name__)

class OnDutyAlgorithm(BaseAlgorithm):
    """Handler for YOLO-based models."""

    def __init__(self, model_config):
        super().__init__(model_config)

        self.model = YOLO(model_config["model"])
        self.class_id = list(self.model.names.values()).index('person')  # Assuming 'person' is the class name for people

        self.no_move = False
        self.no_person = False
        self.last_time_no_move = 0
        self.last_time_no_person = 0
        self.persons = {}
        self.keypoints = None
    
    def detect(self):
        # Video setup
        source = self.model_config["stream_url"]
        #source = "人员在岗.mp4"
        #source = "人员脱岗.mp4"
        #source = "人员跌倒.mkv"
        videocapture = cv2.VideoCapture(source)
        frame_width, frame_height = int(videocapture.get(3)), int(videocapture.get(4))
        fps, fourcc = int(videocapture.get(5)), cv2.VideoWriter_fourcc(*"mp4v")

        # Output setup
        save_dir = increment_path(Path("outputs") / "exp", mkdir=True)
        save_dir.mkdir(parents=True, exist_ok=True)
        video_writer = cv2.VideoWriter(str(save_dir / f"{Path(source).stem}.mp4"), fourcc, fps, (frame_width, frame_height))
    
        # Iterate over video frames
        while videocapture.isOpened():
            success, frame = videocapture.read()
            if not success:
                break
    
            # TODO: add logic
            results = self.model.track(frame, persist=True)
            if len(results) <= 0:
                continue

            filter_boxes = results[0].boxes[results[0].boxes.cls == self.class_id]

            current_time = time.time()
            if len(filter_boxes) == 0:
                if self.no_person == True:
                    #if current_time - self.last_time_no_person > 60*5: # 300 seconds threshold
                    if current_time - self.last_time_no_person > 1: # 300 seconds threshold
                        # TODO: generate an alert
                        logger.info("no person, generate an alert")
                        self.last_time_no_person = current_time
                        alert_data = {
                            "file": "f",
                            "video": "v",
                            "alarmMsg": "a",
                            "alarmTime": current_time,
                            "name": "n",
                            "code": "c",
                            "alarmLevelCode": "a",
                            "alarmLevelName": "a"
                        }
                        self.process_results(alert_data)
                else:
                    self.no_person = True
                    self.last_time_no_person = current_time
                continue
            self.no_person = False

            boxes = filter_boxes.xyxy.cpu()
            logger.info(boxes)
            logger.info(filter_boxes.id)
            track_ids = filter_boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                # TODO: add logic for move; clearup self.persions
                if track_id not in self.persons:
                    self.persons[track_id] = box
                    self.no_move = False
                    continue
                else:
                    old_box = self.persons[track_id]

                    self.persons[track_id] = box



            video_writer.write(frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

