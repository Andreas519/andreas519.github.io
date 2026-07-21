/*
  ESP32-Steuerung für die Dobot-Befehlskette

  Vier Taster senden über die USB-COM-Schnittstelle:
    GPIO 25 -> PAUSE
    GPIO 26 -> WEITER
    GPIO 27 -> HALT
    GPIO 33 -> STATUS

  Jeder Taster wird zwischen GPIO und GND angeschlossen.
  INPUT_PULLUP aktiviert den internen Pull-up-Widerstand.

  Achtung:
  HALT bricht die laufende Dobot-Aufgabe endgültig ab.
*/

const int PIN_PAUSE  = 25;
const int PIN_WEITER = 26;
const int PIN_HALT   = 27;
const int PIN_STATUS = 33;

const int PIN_LED = 2;

const unsigned long ENTPRELLZEIT_MS = 50;

struct Taste {
  int pin;
  const char* befehl;
  int letzterRohzustand;
  int stabilerZustand;
  unsigned long letzteAenderung;
};

Taste tasten[] = {
  {PIN_PAUSE,  "PAUSE",  HIGH, HIGH, 0},
  {PIN_WEITER, "WEITER", HIGH, HIGH, 0},
  {PIN_HALT,   "HALT",   HIGH, HIGH, 0},
  {PIN_STATUS, "STATUS", HIGH, HIGH, 0},
};

const int ANZAHL_TASTEN = sizeof(tasten) / sizeof(tasten[0]);

String empfangszeile = "";

void setup() {
  Serial.begin(115200);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  for (int i = 0; i < ANZAHL_TASTEN; i++) {
    pinMode(tasten[i].pin, INPUT_PULLUP);
  }

  delay(1000);
  Serial.println("ESP32_BEREIT");
}

void tastenPruefen() {
  unsigned long jetzt = millis();

  for (int i = 0; i < ANZAHL_TASTEN; i++) {
    int rohzustand = digitalRead(tasten[i].pin);

    if (rohzustand != tasten[i].letzterRohzustand) {
      tasten[i].letzteAenderung = jetzt;
      tasten[i].letzterRohzustand = rohzustand;
    }

    if (
      jetzt - tasten[i].letzteAenderung >= ENTPRELLZEIT_MS
      && rohzustand != tasten[i].stabilerZustand
    ) {
      tasten[i].stabilerZustand = rohzustand;

      if (rohzustand == LOW) {
        Serial.println(tasten[i].befehl);
      }
    }
  }
}

void pcNachrichtenLesen() {
  while (Serial.available() > 0) {
    char zeichen = Serial.read();

    if (zeichen == '\n') {
      empfangszeile.trim();

      if (empfangszeile == "PC_BEREIT") {
        digitalWrite(PIN_LED, HIGH);
      }

      empfangszeile = "";
    }
    else if (zeichen != '\r') {
      empfangszeile += zeichen;
    }
  }
}

void loop() {
  tastenPruefen();
  pcNachrichtenLesen();
  delay(5);
}
