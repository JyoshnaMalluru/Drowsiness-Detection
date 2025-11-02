# backend/app.py
import base64
import os
import io
import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
import cv2
import dlib
from imutils import face_utils
from scipy.spatial import distance

# --- Config ---
EAR_THRESH = 0.25
FRAME_CHECK = 5   # trigger alert when eyes closed for 5 frames
MODEL_PATH = os.path.join("models", "shape_predictor_68_face_landmarks.dat")
# ----------------

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# dlib setup
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C) if C != 0 else 0

# state per-client
client_state = {}

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    client_state[sid] = {"flag": 0}
    print(f"Client connected: {sid}")
    emit("connected", {"message": "connected to drowsiness backend"})

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    client_state.pop(sid, None)

@socketio.on("frame")
def handle_frame(data):
    sid = request.sid
    try:
        # Decode frame (support base64 string or raw bytes)
        if isinstance(data, str):
            header, b64 = (data.split(",", 1) if "," in data else ("", data))
            frame_bytes = base64.b64decode(b64)
        else:
            frame_bytes = data

        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return

        frame = cv2.resize(frame, (450, int(frame.shape[0] * 450 / frame.shape[1])))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detector(gray, 0)

        ear_value = None
        drowsy = False

        for subject in subjects:
            shape = predictor(gray, subject)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear_value = (leftEAR + rightEAR) / 2.0

            state = client_state.setdefault(sid, {"flag": 0})
            if ear_value < EAR_THRESH:
                state["flag"] += 1
                if state["flag"] >= FRAME_CHECK:
                    drowsy = True
                    # Draw alert on frame
                    cv2.putText(frame, "!!! ALERT: DROWSY !!!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                state["flag"] = 0

            # Draw eyes for visualization
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            break  # only first face

        # Encode frame back to base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')

        # Send annotated frame + status to frontend
        emit("status", {
            "drowsy": drowsy,
            "ear": float(ear_value) if ear_value is not None else None,
            "flag": client_state.get(sid, {}).get("flag", 0),
            "frame": "data:image/jpeg;base64," + frame_b64
        })

    except Exception as e:
        print("Error processing frame:", e)

if __name__ == "__main__":
    print("Starting drowsiness detection server...")
    socketio.run(app, host="0.0.0.0", port=5000)
