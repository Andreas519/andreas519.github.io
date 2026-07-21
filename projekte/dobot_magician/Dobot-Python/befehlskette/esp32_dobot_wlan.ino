/*
  ESP32-WLAN-Steuerung für die Dobot-Befehlskette

  Der ESP32 verbindet sich mit dem WLAN und anschließend
  als TCP-Client mit dem Python-Programm auf dem PC.

  Vier Taster:
    GPIO 25 -> PAUSE
    GPIO 26 -> WEITER
    GPIO 27 -> HALT
    GPIO 33 -> STATUS

  Jeder Taster wird zwischen GPIO und GND angeschlossen.
  INPUT_PULLUP aktiviert den internen Pull-up-Widerstand.
*/

#include <WiFi.h>


// ------------------------------------------------------------
// Diese Angaben anpassen
// ------------------------------------------------------------

const char* WLAN_NAME = "MEIN-WLAN";
const char* WLAN_PASSWORT = "MEIN-PASSWORT";

// IPv4-Adresse des PCs, angezeigt von esp32_wlan_test.py
IPAddress PC_IP(192, 168, 1, 100);

const uint16_t PC_PORT = 8765;


// ------------------------------------------------------------
// Ab hier normalerweise nichts mehr ändern
// ------------------------------------------------------------

const int PIN_PAUSE  = 25;
const int PIN_WEITER = 26;
const int PIN_HALT   = 27;
const int PIN_STATUS = 33;

const int PIN_LED = 2;

const unsigned long ENTPRELLZEIT_MS = 50;
const unsigned long WLAN_WIEDERHOLZEIT_MS = 5000;
const unsigned long TCP_WIEDERHOLZEIT_MS = 2000;
const unsigned long PING_INTERVALL_MS = 10000;

WiFiClient client;

unsigned long letzterWLANVersuch = 0;
unsigned long letzterTCPVersuch = 0;
unsigned long letzterPing = 0;

String empfangszeile = "";


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

const int ANZAHL_TASTEN =
  sizeof(tasten) / sizeof(tasten[0]);


void wlanVerbinden() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  unsigned long jetzt = millis();

  if (
    letzterWLANVersuch != 0
    && jetzt - letzterWLANVersuch < WLAN_WIEDERHOLZEIT_MS
  ) {
    return;
  }

  letzterWLANVersuch = jetzt;

  Serial.println("WLAN-Verbindung wird aufgebaut ...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WLAN_NAME, WLAN_PASSWORT);
}


void tcpVerbinden() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  if (client.connected()) {
    return;
  }

  unsigned long jetzt = millis();

  if (
    letzterTCPVersuch != 0
    && jetzt - letzterTCPVersuch < TCP_WIEDERHOLZEIT_MS
  ) {
    return;
  }

  letzterTCPVersuch = jetzt;

  Serial.print("TCP-Verbindung zum PC ");
  Serial.print(PC_IP);
  Serial.print(":");
  Serial.print(PC_PORT);
  Serial.println(" ...");

  client.stop();

  if (client.connect(PC_IP, PC_PORT)) {
    Serial.println("TCP-Verbindung hergestellt.");
    client.println("ESP32_BEREIT");
    letzterPing = millis();
  }
  else {
    Serial.println("TCP-Verbindung fehlgeschlagen.");
  }
}


void befehlSenden(const char* befehl) {
  if (!client.connected()) {
    Serial.print("Nicht gesendet, keine TCP-Verbindung: ");
    Serial.println(befehl);
    return;
  }

  client.println(befehl);

  Serial.print("Gesendet: ");
  Serial.println(befehl);
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
        befehlSenden(tasten[i].befehl);
      }
    }
  }
}


void pcNachrichtenLesen() {
  while (client.connected() && client.available() > 0) {
    char zeichen = client.read();

    if (zeichen == '\n') {
      empfangszeile.trim();

      if (empfangszeile.length() > 0) {
        Serial.print("PC: ");
        Serial.println(empfangszeile);

        if (empfangszeile == "PC_BEREIT") {
          digitalWrite(PIN_LED, HIGH);
        }
      }

      empfangszeile = "";
    }
    else if (zeichen != '\r') {
      empfangszeile += zeichen;
    }
  }
}


void verbindungUeberwachen() {
  wlanVerbinden();

  if (WiFi.status() == WL_CONNECTED) {
    tcpVerbinden();
  }

  digitalWrite(
    PIN_LED,
    client.connected() ? HIGH : LOW
  );
}


void pingSenden() {
  if (!client.connected()) {
    return;
  }

  unsigned long jetzt = millis();

  if (jetzt - letzterPing >= PING_INTERVALL_MS) {
    client.println("PING");
    letzterPing = jetzt;
  }
}


void setup() {
  Serial.begin(115200);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  for (int i = 0; i < ANZAHL_TASTEN; i++) {
    pinMode(tasten[i].pin, INPUT_PULLUP);
  }

  delay(500);

  wlanVerbinden();
}


void loop() {
  verbindungUeberwachen();
  pcNachrichtenLesen();
  tastenPruefen();
  pingSenden();

  delay(5);
}
