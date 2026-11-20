# Gesture Car

Hand-gesture controlled car. A Raspberry Pi 5 reads the camera, classifies the hand gesture with MediaPipe + a scikit-learn model, and sends a number over USB serial to an Arduino that drives the motors.

## Gestures

| Gesture | Number | Action |
|---|---|---|
| thumbs_up | 5 | Unlock |
| fist | 2 | Lock and stop |
| palm | 1 | Forward |
| point_left | 3 | Spin left |
| point_right | 4 | Spin right |
| none | 0 | Stop (stays unlocked) |

The car ignores everything until a thumbs-up. After that, any movement works until a fist. If the Pi stops sending for 500 ms, the Arduino stops and locks.

## Wiring (Arduino Uno to HW-094 / L298N)

| Arduino | Driver |
|---|---|
| 2 | IN1 |
| 3 | IN2 |
| 4 | IN3 |
| 7 | IN4 |
| 5 (PWM) | ENA |
| 6 (PWM) | ENB |
| 8 | Start/enable line (HIGH while unlocked) |
| GND | GND (shared with battery) |

Left two motors in parallel on OUT1/OUT2, right two in parallel on OUT3/OUT4. Remove the ENA/ENB jumpers.

## Setup

Raspberry Pi (64-bit OS):

```bash
python3 -m venv --system-site-packages ~/gesture-env
source ~/gesture-env/bin/activate

pip install mediapipe joblib scikit-learn pyserial opencv-python-headless
python live2.py
```

Needs `gesture_model.pkl` and `hand_landmarker.task` in the same folder as `live.py`.

Arduino: open `arduino/gesture_car/gesture_car.ino` in the Arduino IDE and upload.

## Tuning

- `SPEED` in the sketch: 0 to 255.
- Turns swapped: swap the `g == 3` and `g == 4` lines.
- Softer turns: use `drive(0, 0, 1, 0, SPEED)` for left and `drive(1, 0, 0, 0, SPEED)` for right (pivot instead of spin).
