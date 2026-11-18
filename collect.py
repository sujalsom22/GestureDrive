import sys, time, csv, os, cv2, mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
from picamera2 import Picamera2

label, person = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 200
det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
    base_options=mpp.BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_hands=1))
cam = Picamera2()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()
print(f"Get ready: {label} ({person}). Starting in 3 s")
time.sleep(3)
print("RECORDING - move the hand a little (distance, angle)")
os.makedirs("data", exist_ok=True)
t0 = time.time(); saved = 0
with open("data/samples.csv", "a", newline="") as f:
    w = csv.writer(f)
    while saved < N:
        rgb = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
        res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int((time.time() - t0) * 1000))
        if not res.hand_landmarks:
            continue
        pts = res.hand_landmarks[0]
        wx, wy, wz = pts[0].x, pts[0].y, pts[0].z
        size = ((pts[9].x - wx) ** 2 + (pts[9].y - wy) ** 2) ** 0.5 or 1e-6
        row = []
        for p in pts:
            row += [(p.x - wx) / size, (p.y - wy) / size, (p.z - wz) / size]
        w.writerow([label, person] + row)
        saved += 1
print(f"saved {saved} samples")
