import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from sklearn.cluster import DBSCAN

class CrowdAnalytics:
    def __init__(self):
        self.previous_positions = None
        self.heatmap = None
        
    def analyze(self, frame, detections):
        results = {
            'count': len(detections.boxes),
            'density': self._calculate_density(detections),
            'movement': self._track_movement(detections),
            'anomalies': self._detect_anomalies(detections)
        }
        return results
    
    def _calculate_density(self, detections):
        if len(detections.boxes) == 0:
            return 0.0
            
        positions = detections.boxes.xyxy.cpu().numpy()
        kernel = gaussian_filter(positions, sigma=5)
        return np.max(kernel)
    
    def _track_movement(self, detections):
        current_positions = detections.boxes.xyxy.cpu().numpy()
        
        if self.previous_positions is None:
            self.previous_positions = current_positions
            return []
            
        movement_vectors = []
        for curr in current_positions:
            if len(self.previous_positions) > 0:
                # Find closest previous position
                distances = np.linalg.norm(
                    self.previous_positions[:, :2] - curr[:2], axis=1)
                min_idx = np.argmin(distances)
                if distances[min_idx] < 50:  # threshold for matching
                    vector = curr[:2] - self.previous_positions[min_idx, :2]
                    movement_vectors.append(vector)
                    
        self.previous_positions = current_positions
        return movement_vectors
    
    def _detect_anomalies(self, detections):
        positions = detections.boxes.xyxy.cpu().numpy()
        
        if len(positions) < 5:  # Need minimum points for clustering
            return []
            
        clustering = DBSCAN(eps=50, min_samples=3).fit(positions[:, :2])
        labels = clustering.labels_
        
        # Points labeled as -1 are anomalies
        anomalies = positions[labels == -1]
        return anomalies.tolist()
    
    def draw_heatmap(self, frame, results):
        if not results.get('density'):
            return frame
            
        if self.heatmap is None:
            self.heatmap = np.zeros(frame.shape[:2])
            
        # Update heatmap based on detections
        positions = results['boxes']
        for pos in positions:
            x, y = int(pos[0]), int(pos[1])
            cv2.circle(self.heatmap, (x, y), 20, 1, -1)
            
        # Apply colormap
        heatmap = cv2.applyColorMap(
            (self.heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)
        
        # Blend with original frame
        return cv2.addWeighted(frame, 0.7, heatmap, 0.3, 0)