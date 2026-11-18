import time
from picamera2 import Picamera2
cam = Picamera2()
cam.configure(cam.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)},
    controls={"FrameDurationLimits": (33333, 33333)}))
cam.start()
time.sleep(2)
t0 = time.time()
for _ in range(100):
    cam.capture_array()
print(f"camera-only FPS: {100 / (time.time() - t0):.1f}")
