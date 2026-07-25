# Dialog zur Erweiterung um einen DHT11-Sensor

**Projekt:** `befehlskette_v3_3_5`  
**Datum:** 25.07.2026  
**Unterstützung:** OpenAI Codex

## Ausgangspunkt

**Nutzer:**

> Es soll ein DHT11-Sensor an den ESP angeschlossen werden.

**Codex:**

Als erste Lösung wurde eine optionale Einbindung vorgeschlagen:

- Datenleitung des DHT11 an GPIO 4
- Messung auf Anforderung
- neuer Befehl `DHT11_MESSEN`
- Ausgabe von Temperatur und Luftfeuchtigkeit als `WERT`-Meldungen
- strukturierte Fehlermeldung bei einem Messfehler

Vorgesehene Beschaltung:

```text
DHT11 VCC   → ESP32 3,3 V
DHT11 DATA  → ESP32 GPIO 4
DHT11 GND   → ESP32 GND
```

Bei einem nackten DHT11-Sensor wird üblicherweise ein Pull-up-Widerstand
von etwa 4,7–10 kΩ zwischen DATA und 3,3 V benötigt. Viele fertige
DHT11-Module enthalten diesen Widerstand bereits.

---

## Minimales Testprogramm

**Nutzer:**

> Stelle ein minimales Testprogramm für den DHT11 bereit.

**Codex:**

Es wurde die eigenständige Datei `dht11_test.py` erstellt. Das Programm
verwendet GPIO 4 und misst alle zwei Sekunden:

```python
"""Minimaler DHT11-Test für MicroPython auf dem ESP32."""

from machine import Pin
import dht
import time


PIN_DHT11 = 4

sensor = dht.DHT11(Pin(PIN_DHT11))

print("DHT11-Test gestartet")
print("Datenleitung: GPIO", PIN_DHT11)

try:
    while True:
        try:
            sensor.measure()

            print(
                "Temperatur:",
                sensor.temperature(),
                "°C | Luftfeuchtigkeit:",
                sensor.humidity(),
                "%",
            )

        except OSError as fehler:
            print("DHT11-Messfehler:", fehler)

        time.sleep(2)

except KeyboardInterrupt:
    print("DHT11-Test beendet")
```

Erwartete Ausgabe:

```text
DHT11-Test gestartet
Datenleitung: GPIO 4
Temperatur: 23 °C | Luftfeuchtigkeit: 51 %
```

Mögliche Fehlermeldung:

```text
DHT11-Messfehler: [Errno 116] ETIMEDOUT
```

---

## Integration in das ESP32-Steuerungsprogramm

**Nutzer:**

> Erweitere `esp32-dobot-steuerung.py` bezüglich eines DHT11-Sensor am
> Pin 4. Der Sensor sollte optional verfügbar sein. Für mich bedeutet
> das, das wir im Programm über eine Konstante entscheiden, ob der
> Sensor angeschlossen ist. Wenn der Sensor aktiviert ist und die
> Fehlermeldung `DHT11-Messfehler: [Errno 116] ETIMEDOUT` produziert,
> sollten beide Programme darauf reagieren. Füge noch einen analogen
> Eingang für einen Fotowiderstand zur Helligkeitsmessung hinzu.

**Codex:**

Die Erweiterung wurde in den vorhandenen Dateien umgesetzt. Die
Dateinamen wurden nicht verändert.

### Interne Version des ESP32-Programms

```python
VERSION = "1.4"
VERSIONSDATUM = "25.07.2026"
```

### Konfiguration der optionalen Sensoren

```python
PIN_DHT11 = 4
PIN_FOTOWIDERSTAND = 34

DHT11_AKTIV = False
FOTOWIDERSTAND_AKTIV = False
```

Für einen angeschlossenen DHT11 wird eingestellt:

```python
DHT11_AKTIV = True
```

Ist der Sensor nicht angeschlossen, bleibt die Konstante auf `False`.
Das übrige ESP32-Programm arbeitet dann weiterhin ohne DHT11.

### DHT11 messen

Neuer Befehl:

```text
DHT11_MESSEN
```

Erfolgreiche Antwort:

```text
WERT;TEMPERATUR;23
WERT;LUFTFEUCHTIGKEIT;51
BEFEHL_AUSGEFUEHRT;DHT11_MESSEN
```

Bei einem Timeout sendet der ESP32 eine strukturierte Fehlermeldung:

```text
SENSOR_FEHLER;DHT11;DHT11-Messfehler: [Errno 116] ETIMEDOUT
```

Ist der Sensor in der Konfiguration deaktiviert, lautet die Antwort:

```text
BEFEHL_FEHLER;DHT11_MESSEN;DHT11 ist nicht aktiviert
```

---

## Reaktion des PC-Programms

Das Kommunikationsmodul besitzt jetzt intern die Version:

```python
VERSION = "1.4.1"
VERSIONSDATUM = "25.07.2026"
```

Eine Meldung der Form

```text
SENSOR_FEHLER;DHT11;Fehlertext
```

wird vom PC-Programm:

- ausdrücklich als Sensorfehler erkannt,
- deutlich in der Kommandozeile ausgegeben,
- in die Meldungswarteschlange eingetragen,
- dauerhaft im ESP-Wertespeicher abgelegt,
- nicht beantwortet, damit keine Kommunikationsschleife entsteht.

Beispielausgabe:

```text
Sensorfehler von ESP32-COM: DHT11 – DHT11-Messfehler: [Errno 116] ETIMEDOUT
```

Der Fehlertext ist unter diesem Namen im Wertespeicher verfügbar:

```text
SENSOR_FEHLER_DHT11
```

---

## Ergänzung: Fotowiderstand

Für die Helligkeitsmessung wurde GPIO 34 als analoger Eingang
vorgesehen:

```python
PIN_FOTOWIDERSTAND = 34
FOTOWIDERSTAND_AKTIV = False
```

Aktivierung:

```python
FOTOWIDERSTAND_AKTIV = True
```

Neuer Befehl:

```text
HELLIGKEIT_MESSEN
```

Beispielantwort:

```text
WERT;HELLIGKEIT;2748
BEFEHL_AUSGEFUEHRT;HELLIGKEIT_MESSEN
```

Der ADC-Rohwert liegt grundsätzlich zwischen 0 und 4095. Ob ein
größerer Wert eine höhere oder niedrigere Helligkeit bezeichnet, hängt
von der Anordnung des Fotowiderstands im Spannungsteiler ab.

GPIO 34 darf höchstens mit 3,3 V belastet werden. Der Fotowiderstand
wird deshalb zusammen mit einem Festwiderstand als Spannungsteiler
angeschlossen.

---

## Geänderte Dateien

- `esp32_dobot_steuerung_v1_3.py`
- `esp32_kommunikation_v1_4.py`
- `befehlskette_beispiel_v3_3_5.py`
- `AENDERUNGSPROTOKOLL.md`

Zusätzlich wurde das eigenständige Testprogramm `dht11_test.py`
erstellt.

## Prüfstand

Erfolgreich geprüft wurden:

- Syntax der geänderten Python-Dateien
- Erkennung einer simulierten DHT11-Timeoutmeldung
- Speicherung des Sensorfehlers
- Übergabe an die Meldungswarteschlange
- Vermeidung einer Rückantwort auf den Sensorfehler

Noch ausstehend:

- Test des DHT11 an der realen ESP32-Hardware
- Test des Fotowiderstands und Feststellung der Messrichtung
