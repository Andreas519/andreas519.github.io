ESP32 WLAN-Speicheroszilloskop - 2 Kanal
========================================

Funktionen:
- zwei analoge Eingänge: GPIO34 und GPIO35
- Trigger auf Kanal 1 oder Kanal 2
- steigende / fallende Flanke
- grafische Darstellung im Browser
- WLAN Access Point des ESP32
- Buttonanzeige: Messung läuft ...
- Onboard-LED:
  - bereit: 0,25 Hz, also 2 s EIN / 2 s AUS
  - Messung läuft: dauerhaft EIN
- Verbindungsanzeige im Browser über /ping

WLAN:
SSID: ESP32-Oszilloskop
Passwort: 12345678
Adresse: http://192.168.4.1

Hinweise:
- Für WLAN-Projekte beim klassischen ESP32 ADC1-Pins verwenden.
- GPIO34 und GPIO35 sind reine Eingänge und daher gut geeignet.
- Keine unbekannten oder höheren Spannungen direkt an den ADC anschließen.
- Eingangsspannung max. ca. 0...3,3 V.
- Für praktische Messungen Eingangsschutz verwenden.

Arduino IDE:
- Board: passendes ESP32 Dev Module auswählen
- Bibliotheken: WiFi.h und WebServer.h sind beim ESP32 Arduino Core enthalten
