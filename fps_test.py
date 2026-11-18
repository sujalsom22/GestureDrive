import time, cv2, mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from picamera2 import Picamera2

det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_hands=1))
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()
time.sleep(2)
print("5 seconds, get your palm ready")
time.sleep(5)
print("Hold your palm still NOW")
n = found = 0
t0 = time.time()
while n < 100:
    rgb = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
    res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.time() - t0) * 1000))
    found += len(res.hand_landmarks) > 0
    n += 1
print(f"FPS: {n / (time.time() - t0):.1f}, hand found in {found}/{n} frames")
