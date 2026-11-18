import time, joblib, cv2, mediapipe as mp
from collections import deque, Counter
from flask import Flask, Response
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from picamera2 import Picamera2

model = joblib.load("gesture_model.pkl")
det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_hands=1))
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()
time.sleep(2)
app = Flask(__name__)

def frames():
    votes, t0, last = deque(maxlen=5), time.time(), time.time()
    while True:
        frame = cam.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.time() - t0) * 1000))
        if res.hand_landmarks:
            pts = res.hand_landmarks[0]
            wx, wy, wz = pts[0].x, pts[0].y, pts[0].z
            size = ((pts[9].x - wx) ** 2 + (pts[9].y - wy) ** 2) ** 0.5 or 1e-6
            feat = [v for p in pts for v in ((p.x - wx) / size, (p.y - wy) / size, (p.z - wz) / size)]
            votes.append(model.predict([feat])[0])
            for p in pts:
                cv2.circle(frame, (int(p.x * 640), int(p.y * 480)), 4, (0, 255, 0), -1)
        else:
            votes.append("none")
        g, c = Counter(votes).most_common(1)[0]
        g = g if c >= 3 else "none"
        now = time.time(); fps = 1 / (now - last); last = now
        cv2.putText(frame, f"{g}  {fps:.0f} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        yield b"--f\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n"

@app.route("/")
def video():
    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=f")

app.run(host="0.0.0.0", port=5000, threaded=True)
