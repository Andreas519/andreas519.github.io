## interne Versionsführung
```VERSION = "1.3.1"
VERSIONSDATUM = "25.07.2026"

# Änderungen:
# 1.3.1:
# - Eingabe q beendet das Programm kontrolliert.
# - Beide LEDs werden beim Beenden ausgeschaltet.
# - Die LED-Simulation wird beendet.
```

```## esp32_dobot_steuerung_v1_3.py

### Version 1.3.1 – 25.07.2026

- Befehl `q` ergänzt.
- Ausgabe `PROGRAMM_BEENDET` ergänzt.
- Kontrolliertes Aufräumen beim Programmende.
- Syntaxprüfung erfolgreich.
- Funktionstest auf dem ESP32 erfolgreich.

## esp32_kommunikation_v1_4.py

### Version 1.4.1 – 25.07.2026

- Automatische `EMPFANGEN ...`-Antworten entfernt.
- Rückkopplung mit dem ESP-Simulator verhindert.
- Bidirektionaler TCP-Test erfolgreich.

## esp-simulator.py

### Version 1.3.1 – 25.07.2026

- `EMPFANGEN ...` und `UNBEKANNT ...` werden als abschließende
  Protokollmeldungen behandelt.
- Endlose Antwortschleife verhindert.
- Bidirektionaler TCP-Test erfolgreich.
```