from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import time
from collections import deque

app = Flask(__name__)

# Load the trained YOLO model
try:
    model = YOLO("semaphore.pt")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Semaphore signal mapping (angles in degrees, left and right flag positions)
semaphore_map = {
    (0, 180): "A",   (45, 135): "B",   (90, 90): "C",
    (135, 45): "D",  (180, 0): "E",    (225, 315): "F",
    (270, 270): "G", (315, 225): "H",  (0, 45): "I",
    (45, 0): "J",    (90, 315): "K",   (135, 270): "L",
    (180, 225): "M", (225, 180): "N",  (270, 135): "O",
    (315, 90): "P",  (0, 135): "Q",    (45, 90): "R",
    (90, 45): "S",   (135, 0): "T",    (180, 315): "U",
    (225, 270): "V", (270, 225): "W",  (315, 180): "X",
    (0, 270): "Y",   (45, 225): "Z"
}

# Initialize webcam for Semaphore (Camera 1, fallback to Camera 0 if unavailable)
camera = cv2.VideoCapture(1)
if not camera.isOpened():
    print("Warning: Could not open second webcam for Semaphore. Falling back to Camera 0.")
    camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("Error: Could not open any webcam for Semaphore.")
    exit(1)

# Store recent decoded messages (max 10 for history)
message_history = deque(maxlen=10)
last_message_time = 0
MIN_MESSAGE_INTERVAL = 1.0  # Minimum time between new messages (in seconds)

def calculate_semaphore_angle(center_x, center_y, frame_shape):
    """Calculate semaphore angle based on flag position relative to image center."""
    img_center_x, img_center_y = frame_shape[1] // 2, frame_shape[0] // 2
    angle = int(np.arctan2(center_y - img_center_y, center_x - img_center_x) * 180 / np.pi) % 360
    semaphore_angle = (360 - angle) % 360
    return round(semaphore_angle / 45) * 45

def detect_semaphore(frame):
    """Detect flags and decode semaphore signal."""
    global last_message_time
    current_time = time.time()

    # Perform detection
    results = model(frame)
    decoded_message = "No message detected"
    flag_positions = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            if conf > 0.6:
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                semaphore_angle = calculate_semaphore_angle(center_x, center_y, frame.shape)
                flag_positions.append((center_x, semaphore_angle))

                # Draw bounding box and angle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Angle: {semaphore_angle}°", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Decode if two flags are detected
    if len(flag_positions) >= 2:
        flag_positions.sort(key=lambda x: x[0])
        left_angle = flag_positions[0][1]
        right_angle = flag_positions[1][1]

        if current_time - last_message_time >= MIN_MESSAGE_INTERVAL:
            decoded_message = semaphore_map.get((left_angle, right_angle), "?")
            if decoded_message != "No message detected" and (not message_history or decoded_message != message_history[-1]):
                message_history.append(decoded_message)
                last_message_time = current_time

        cv2.putText(frame, f"Letter: {decoded_message}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

    return frame, decoded_message

def generate_frames():
    """Generator function for video streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame, _ = detect_semaphore(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/decoded_message')
def get_decoded_message():
    success, frame = camera.read()
    if success:
        _, message = detect_semaphore(frame)
        return jsonify({
            "message": message,
            "history": list(message_history)
        })
    return jsonify({"message": "No message detected", "history": list(message_history)})

@app.route('/')
def index():
    return render_template('semaphore-flag-signaling.html')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
    finally:
        camera.release()
        cv2.destroyAllWindows()