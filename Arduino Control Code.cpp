// ===== Arduino final control sketch =====
// Function:
// 1. Receive level value from serial port
// 2. Control fan speed by PWM
// 3. Control LED / relay state
//
// Suggested serial format from Python:
// send "0\n", "1\n", "2\n", "3\n"

const int FAN_PWM_PIN = 5;      // MOS control pin for fan
const int LED_PIN = 6;          // LED light / indicator
const int RELAY_PIN = 7;        // Relay control pin

int currentLevel = 0;
String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);

  pinMode(FAN_PWM_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  analogWrite(FAN_PWM_PIN, 0);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);

  inputString.reserve(20);

  Serial.println("System ready.");
}

void loop() {
  if (stringComplete) {
    inputString.trim();

    if (inputString.length() > 0) {
      int level = inputString.toInt();

      // Limit level range
      if (level < 0) level = 0;
      if (level > 3) level = 3;

      currentLevel = level;
      applyControl(currentLevel);

      Serial.print("Received level: ");
      Serial.println(currentLevel);
    }

    inputString = "";
    stringComplete = false;
  }
}

void applyControl(int level) {
  switch (level) {
    case 0:
      // No person
      analogWrite(FAN_PWM_PIN, 0);
      digitalWrite(LED_PIN, LOW);
      digitalWrite(RELAY_PIN, LOW);
      break;

    case 1:
      // Low occupancy
      analogWrite(FAN_PWM_PIN, 80);
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, LOW);
      break;

    case 2:
      // Medium occupancy
      analogWrite(FAN_PWM_PIN, 160);
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, HIGH);
      break;

    case 3:
      // High occupancy
      analogWrite(FAN_PWM_PIN, 255);
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(RELAY_PIN, HIGH);
      break;
  }
}

// Serial event callback
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}