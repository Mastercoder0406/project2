from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import threading
import queue
import os
from werkzeug.utils import secure_filename
from utils.detection import CrowdDetector
from utils.analytics import CrowdAnalytics
from utils.notifications import NotificationManager
from utils.database import DatabaseManager
from utils.report_generator import ReportGenerator

app = Flask(__name__)
app.config.from_object('config.Config')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize components
detector = CrowdDetector()
analytics = CrowdAnalytics()
# notification_manager = NotificationManager()
# db_manager = DatabaseManager()
report_generator = ReportGenerator()

# Global variables
frame_queue = queue.Queue(maxsize=10)
analysis_results = {}
video_source = None
video_path = None

def process_frames():
    global video_source, video_path
    
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            
            # Perform detection
            detections = detector.detect(frame)
            
            # Analyze crowd
            analysis = analytics.analyze(frame, detections)
            
            # Convert numpy types to Python native types for JSON serialization
            analysis_results.update({
                'timestamp': datetime.now().isoformat(),
                'count': int(analysis['count']),
                'density': float(analysis['density']),
                'movement': [float(x) for x in analysis['movement']] if analysis['movement'] else [],
                'anomalies': [[float(x) for x in anomaly] for anomaly in analysis['anomalies']]
            })
            
            # Check thresholds and send alerts if needed
            if analysis_results['count'] > app.config['CROWD_THRESHOLD'] or \
               analysis_results['density'] > app.config['DENSITY_THRESHOLD']:
                # notification_manager.send_alert(analysis_results)
                print('sent msg')
            
            # Store in database
            # db_manager.store_analysis(analysis_results)

# Start processing thread
processing_thread = threading.Thread(target=process_frames, daemon=True)
processing_thread.start()

def get_video_capture():
    global video_source, video_path
    
    if video_source == 'rtsp':
        return cv2.VideoCapture(video_path)
    elif video_source == 'recorded' and video_path:
        return cv2.VideoCapture(video_path)
    else:
        return cv2.VideoCapture(0)  # Default to webcam

def gen_frames():
    while True:
        cap = get_video_capture()
        while True:
            success, frame = cap.read()
            if not success:
                if video_source == 'recorded':
                    # Reset video to beginning for recorded videos
                    cap = get_video_capture()
                    continue
                break
            
            # Add frame to processing queue
            if not frame_queue.full():
                frame_queue.put(frame)
            
            # Draw analytics on frame
            if analysis_results:
                frame = detector.draw_detections(frame, analysis_results)
                frame = analytics.draw_heatmap(frame, analysis_results)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_input_source', methods=['POST'])
def set_input_source():
    global video_source, video_path
    
    try:
        input_type = request.form['input_type']
        
        if input_type == 'recorded':
            if 'video_file' not in request.files:
                return jsonify({'success': False, 'error': 'No video file provided'})
                
            file = request.files['video_file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'})
                
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            video_source = 'recorded'
            video_path = filepath
            
        elif input_type == 'rtsp':
            rtsp_url = request.form['rtsp_url']
            if not rtsp_url:
                return jsonify({'success': False, 'error': 'No RTSP URL provided'})
                
            video_source = 'rtsp'
            video_path = rtsp_url
            
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analytics')
def get_analytics():
    return jsonify(analysis_results)

# @app.route('/api/report/<report_type>')
# def generate_report(report_type):
#     data = db_manager.get_historical_data()
#     report_path = report_generator.generate(data, report_type)
#     return jsonify({'report_url': report_path})

if __name__ == '__main__':
    app.run(debug=True)