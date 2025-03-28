import cv2
import numpy as np
from ultralytics import YOLO
import torch.serialization

class CrowdDetector:
    def __init__(self):
        # Add YOLOv8 model class to safe globals
        torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
        
        try:
            # First attempt with weights_only=True (safer)
            self.model = YOLO('yolov8x.pt')
        except Exception as e:
            # If that fails, try with weights_only=False
            torch.serialization._weights_only = False
            self.model = YOLO('yolov8x.pt')
            torch.serialization._weights_only = True  # Reset to default
        
    def detect(self, frame):
        results = self.model(frame, classes=[0])  # 0 is person class
        return results[0]
    
    def draw_detections(self, frame, results):
        for box in results.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add count overlay
        cv2.putText(frame, f"Count: {len(results.boxes)}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame