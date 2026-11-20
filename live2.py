import time, joblib, numpy as np, cv2, serial
import mediapipe as mp
from collections import deque, Counter
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from picamera2 import Picamera2

# ---------- config ----------
GESTURE_ID = {
    "none": 0,
    "palm": 1,
    "fist": 2,
    "point_left": 3,
    "point_right": 4,
    "thumbs_up": 5,
}
ARM_REQUIRED = False   # True = keep the thumbs-up arm / fist disarm logic, sends 0 until armed
SEND_EVERY = 0.1       # seconds

# ---------- setup ----------
model = joblib.load("gesture_model.pkl")
det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_hands=1))

cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()

arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=0.1)
time.sleep(2)  # Arduino resets when serial opens

votes = deque(maxlen=5)
armed, thumb_start, last_hand, last_send = False, None, time.time(), 0
t0 = time.time()
print("Ctrl+C to quit." + (" Thumbs-up 1 s = ARM, fist = DISARM." if ARM_REQUIRED else ""))

try:
    while True:
        rgb = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
        res = det.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
            int((time.time() - t0) * 1000))
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

        # optional arming logic
        if ARM_REQUIRED:
            if g == "thumbs_up" and not armed:
                thumb_start = thumb_start or now
                if now - thumb_start >= 1.0:
                    armed = True
            else:
                thumb_start = None
            if g == "fist" or now - last_hand > 2:
                armed = False
            num = GESTURE_ID.get(g, 0) if armed else 0
        else:
            num = GESTURE_ID.get(g, 0)

        if now - last_send >= SEND_EVERY:
            arduino.write(f"{num}\n".encode())
            print(f"\rraw={votes[-1]:<12} gesture={g:<12} send={num}   ", end="", flush=True)
            last_send = now

except KeyboardInterrupt:
    arduino.write(b"0\n")   # stop on exit
    arduino.close()
    cam.stop()
