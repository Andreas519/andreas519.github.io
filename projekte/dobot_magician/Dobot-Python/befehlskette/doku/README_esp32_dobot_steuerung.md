# ESP32-Dobot-Steuerung – Versionsdokumentation

## Zweck

Das MicroPython-Programm läuft auf einem ESP32 und kommuniziert über USB-COM mit der Dobot-Befehlskette auf dem PC.

Es verarbeitet:

- sechs Taster,
- eine blaue Online-LED,
- eine gelbe Simulations-LED,
- Meldungen vom PC,
- Zustandsmeldungen an den PC.

## Anschlussbelegung

| GPIO | Signal | Nachricht/Funktion |
|---:|---|---|
| 25 | Pause | `PAUSE` |
| 26 | Weiter | `WEITER` |
| 27 | Halt | `HALT` |
| 33 | Status | `STATUS` |
| 18 | Frei 1 | `FREI_1` |
| 32 | Frei 2 | `FREI_2` |
| 2 | Blaue LED | leuchtet nach `PC_BEREIT` |
| 19 | Gelbe LED | überwachter Simulationsausgang |

## Version 1.0

Erste Erweiterung um `ueberwache()` und eine zufällige LED-Simulation.

Probleme:

- fehlende Initialisierung der Überwachungs-Dictionaries,
- `KeyError: LED_gelb`,
- falscher Funktionsname `sende_zeile()` statt `zeile_senden()`,
- doppelte Meldungserzeugung,
- doppelte Imports.

## Version 1.1

Korrekturen:

- `ueberwachung_initialisieren()` ergänzt,
- Initialisierung vor der Hauptschleife,
- Funktionsname korrigiert,
- Meldung ausschließlich über `ueberwache()`,
- doppelte Imports entfernt.

Verbleibendes Problem:

- Die LED-Simulation über `_thread` arbeitete im Test nicht zuverlässig.

## Version 1.2

Die LED-Simulation arbeitet ohne zusätzlichen Thread.

Neue Struktur:

```python
while True:
    tasten_pruefen()
    simulation_led_pruefen()
    ueberwache()
    pc_nachrichten_lesen()
    time.sleep_ms(SCHLEIFENPAUSE_MS)
```

Signalweg:

1. `simulation_led_pruefen()` ändert `led_gelb`.
2. `ueberwache()` erkennt die Änderung.
3. `zeile_senden()` sendet `WERT;LED_gelb;0` oder `WERT;LED_gelb;1`.

## Noch offen

`pc_nachrichten_lesen()` verarbeitet derzeit nur:

```python
if nachricht == "PC_BEREIT":
    led.on()
```

Geplant sind:

- `LED_GELB_EIN`
- `LED_GELB_AUS`
- `LED_GELB_UMSCHALTEN`
- Rückmeldung bei unbekannten Befehlen

Diese Erweiterung wäre sinnvoll für Version 1.3.
