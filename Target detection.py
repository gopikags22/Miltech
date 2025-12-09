from flask import Flask, Response
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# Load the YOLOv8 model
model = YOLO("yolov8x.pt")

# Open webcam
camera = cv2.VideoCapture(0)

def detect_objects():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Perform YOLOv8 object detection
        results = model(frame)

        # Loop through detections
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                conf = float(box.conf[0])  # Confidence score
                cls = int(box.cls[0])  # Object class ID
                label = model.names[cls]  # Get object name

                if conf > 0.5:  # Confidence threshold
                    # Draw bounding box and label
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
