from flask import Flask, request, jsonify, Response
import mysql.connector
from mysql.connector import Error
import hashlib
import cv2
import numpy as np
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS if needed for cross-origin requests

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'miltech_auth',
    'user': 'miltech_user',
    'password': 'your_password'  # Set this to match the MySQL user password
}
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        cursor.execute(check_query, (data['username'], data['email']))
        if cursor.fetchone():
            return jsonify({"error": "Username or email already exists"}), 400

        hashed_password = hash_password(data['password'])
        insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (data['username'], data['email'], hashed_password))
        connection.commit()
        return jsonify({"message": "Signup successful"})
    except Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        hashed_password = hash_password(data['password'])
        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (data['username'], hashed_password))
        user = cursor.fetchone()
        if user:
            return jsonify({"message": "Successfully logged in"})
        return jsonify({"error": "Invalid username or password"}), 401
    except Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

# Placeholder for video feed (for target detection and semaphore)
def gen_frames():
    camera = cv2.VideoCapture(0)  # Use webcam
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Placeholder for voice translation (basic implementation)
@app.route('/detect-translate', methods=['POST'])
def detect_translate():
    data = request.get_json()
    target_lang = data.get('target_lang', 'en')
    # This is a placeholder - real implementation would use speech recognition and translation APIs
    return jsonify({
        "spoken_text": "Hello (placeholder)",
        "detected_language": "en",
        "translated_text": "Hola" if target_lang == "es" else "Hello"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)