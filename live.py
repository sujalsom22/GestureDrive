import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TARGET = ("127.0.0.1", 4210)   # later: the ESP32's IP
import time, joblib, numpy as np, cv2, mediapipe as mp
from collections import deque, Counter
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

CMD = {"palm": "F", "point_left": "L", "point_right": "R"}
votes = deque(maxlen=5)
armed, thumb_start, last_hand, last_send = False, None, time.time(), 0
t0 = time.time()
print("Thumbs-up 1 s = ARM, fist = DISARM. Ctrl+C to quit.")
while True:
    rgb = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
    res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.time() - t0) * 1000))
    now = time.time()
    if res.hand_landmarks:
        pts = res.hand_landmarks[0]
        wx, wy, wz = pts[0].x, pts[0].y, pts[0].z
        size = ((pts[9].x - wx) ** 2 + (pts[9].y - wy) ** 2) ** 0.5 or 1e-6
        feat = [v for p in pts for v in ((p.x - wx) / size, (p.y - wy) / size, (p.z - wz) / size)]
        votes.append(model.predict([feat])[0])
        last_hand = now
    else:
        votes.append("none")
    g, c = Counter(votes).most_common(1)[0]
    g = g if c >= 3 else "none"

    if g == "thumbs_up" and not armed:
        thumb_start = thumb_start or now
        if now - thumb_start >= 1.0:
            armed = True
    else:
        thumb_start = None
    if g == "fist" or now - last_hand > 2:
        armed = False

    letter = CMD.get(g, "S") if armed else "S"
    if now - last_send >= 0.1:
        print(f"\r{'ARMED   ' if armed else 'DISARMED'}  raw={votes[-1]:<12} gesture={g:<12} send={letter}   ", end="", flush=True)
        sock.sendto((letter + "\n").encode(), TARGET)
        last_send = now
