# Mein Prompt

Es soll ein DHT11-Sensor an den ESP angeschlossen werden.

## Antwort

Gut. Wir erweitern die vorhandene ESP32-Datei, ohne ihren Dateinamen zu ändern, und erhöhen intern die Version.

Mein Vorschlag:

DHT11 wird nur auf Anforderung gemessen.

Neuer Befehl:

```text
DHT11_MESSEN
```

Beispielantwort:

```text
WERT;TEMPERATUR;23
WERT;LUFTFEUCHTIGKEIT;51
BEFEHL_AUSGEFUEHRT;DHT11_MESSEN
```

Bei einem Messfehler beispielsweise:

```text
BEFEHL_FEHLER;DHT11_MESSEN;Keine gültigen Sensordaten
```

- `ESP32_STATUS` könnte zusätzlich die zuletzt gemessenen Werte enthalten.
- `HILFE` wird um den neuen Befehl ergänzt.
- Die Messung erfolgt nicht in jedem 5-ms-Schleifendurchlauf, weil der DHT11 nur langsam abgefragt werden darf.

Vor der Implementierung benötige ich eine Hardwareangabe:

An welchem GPIO soll die Datenleitung des DHT11 angeschlossen werden?

Ein derzeit noch freier und meist geeigneter Anschluss wäre beispielsweise GPIO 4.

Vorgesehene Beschaltung:

```text
DHT11 VCC   → ESP32 3,3 V
DHT11 DATA  → gewählter GPIO
DHT11 GND   → ESP32 GND
```

Bei einem nackten DHT11-Sensor benötigt DATA üblicherweise einen Pull-up-Widerstand von etwa 4,7–10 kΩ gegen 3,3 V. Viele fertige DHT11-Module haben diesen Widerstand bereits eingebaut.
