# GestureDrive

A robot car driven by hand gestures. A Raspberry Pi 5 reads the hand with a camera, classifies the gesture, and sends one letter (F, L, R or S) over Wi-Fi (UDP) to an ESP32 on the car, which passes it to an Arduino that drives the motors.

**Team:** Md Kaif Raza (B24DS017), Kanishk Nandeshwar (B24DS010), Sujal Som (B24DS032)
**Course:** AI Lab, hardware + software project

## Gestures

| Gesture | Meaning | Letter |
|---|---|---|
| Thumbs-up held 1 s | Arm the car | S |
| Open palm | Forward | F |
| Point left / right | Turn | L / R |
| Fist | Stop and disarm | S |
| No hand / unsure | Stop (disarm after 2 s) | S |

A gesture counts only if it appears in 3 of the last 5 frames.

## Files

| File | Purpose |
|---|---|
| hand_test.py | Detect a hand in one frame |
| fps_test.py, cam_fps.py | Speed tests (tracker, camera only) |
| collect.py | Record landmark samples: `python -u collect.py LABEL PERSON [N]` |
| train.py | Train Random Forest and kNN, save the best to gesture_model.pkl |
| live.py | Live recognition, arming, sends letters over UDP |
| stream.py | Browser live view at http://PI_IP:5000 |
| listen.py | Fake car: prints letters received on UDP port 4210 |
| data/samples.csv | Landmark features only, no video stored |

## Setup (Raspberry Pi 5, Raspberry Pi OS 64-bit)

    sudo apt install -y python3-picamera2 python3-opencv
    python3 -m venv --system-site-packages venv
    source venv/bin/activate
    pip install mediapipe numpy scikit-learn flask pandas joblib
    wget -O hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

## Usage

    python -u collect.py palm yourname      # repeat for fist, point_left, point_right, thumbs_up, none
    python train.py
    python listen.py                        # second terminal, fake car
    python live.py 2>/dev/null              # live recognition
    python stream.py 2>/dev/null            # browser view

## Results so far

- Camera only: 30 FPS. With MediaPipe: about 15 FPS (Pi CPU limit, enough for 10 Hz commands).
- Gesture accuracy: to be measured (leave-one-person-out and outside volunteers).

## Privacy

Only landmark numbers are stored, never video. Volunteers give consent and are recorded by number.

## Status

Pi, camera, data collection, training, live recognition and UDP sending work. ESP32 bridge, Arduino code and the car are next.
