import time, cv2, mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from picamera2 import Picamera2

opts = vision.HandLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path="hand_landmarker.task"),
    num_hands=1)
det = vision.HandLandmarker.create_from_options(opts)

cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()
print("Show open palm NOW, 40 cm away")
time.sleep(5)

frame = cam.capture_array()
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
print("hand found:", len(res.hand_landmarks) > 0)

h, w = frame.shape[:2]
for hand in res.hand_landmarks:
    for p in hand:
        cv2.circle(frame, (int(p.x * w), int(p.y * h)), 4, (0, 255, 0), -1)
cv2.imwrite("hand.jpg", frame)
