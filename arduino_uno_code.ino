const int IN1 = 2, IN2 = 3, IN3 = 4, IN4 = 7;
const int ENA = 5, ENB = 6;
const int START = 8;
const int SPEED = 200;                 // 0-255

bool unlocked = false;
unsigned long lastRx = 0;

void drive(int a1, int a2, int b1, int b2, int spd) {
  digitalWrite(IN1, a1); digitalWrite(IN2, a2);
  digitalWrite(IN3, b1); digitalWrite(IN4, b2);
  analogWrite(ENA, spd);
  analogWrite(ENB, spd);
}

void lockAll() {
  unlocked = false;
  drive(0, 0, 0, 0, 0);
  digitalWrite(START, LOW);
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(20);
  int outs[] = {IN1, IN2, IN3, IN4, ENA, ENB, START};
  for (int p : outs) pinMode(p, OUTPUT);
  lockAll();
}

void loop() {
  if (Serial.available()) {
    int g = Serial.readStringUntil('\n').toInt();
    lastRx = millis();

    if (g == 2) {                          // fist -> LOCK
      lockAll();
    }
    else if (!unlocked) {                  // locked: only thumbs_up does anything
      if (g == 5) {
        unlocked = true;
        digitalWrite(START, HIGH);
      }
    }
    else {                                 // unlocked: gestures drive the car
      if      (g == 1) drive(1, 0, 1, 0, SPEED);   // palm        -> forward
      else if (g == 3) drive(0, 1, 1, 0, SPEED);   // point_left  -> turn left
      else if (g == 4) drive(1, 0, 0, 1, SPEED);   // point_right -> turn right
      else             drive(0, 0, 0, 0, 0);       // 0 / thumbs_up -> stop, stay unlocked
    }
  }

  // failsafe: Pi went silent -> stop and lock
  if (millis() - lastRx > 500) lockAll();
}