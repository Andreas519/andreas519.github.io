Mein Prompt im Dialog mit Codex:

```
Ich teste das ESP32-Programm zusammen mit dem Dobot-Steuerungsprogramm auf dem PC.

Dazu übertrage ich das ESP32-Programm aus deiner Arbeitsumgebung auf den ESP32 und
richte den Autostart beim Einschalten beziehungsweise nach einem Reset ein.

Anschließend gebe ich in Thonny den COM-Port frei, indem ich auf WebREPL umstelle
oder zu einem anderen freien COM-Port wechsle. Danach starte ich den ESP32 neu.
Ist dieser Ablauf korrekt?
```

Ja, der Ablauf ist korrekt.

Empfohlene Reihenfolge:

1. Die aktuelle Datei aus unserer Arbeitsumgebung auf den ESP32 übertragen:

   [esp32_dobot_steuerung_v1_3.py](C:\Users\nutzer\Documents\Codex\2026-07-25\erkunden\work\befehlskette_v3_3_5\esp32_dobot_steuerung_v1_3.py)

2. Auf dem ESP32 unter diesem Namen speichern:

   ```text
   main.py
   ```

   MicroPython führt `main.py` nach dem Einschalten und nach einem Reset automatisch aus.

3. In Thonny den tatsächlichen ESP32-COM-Port freigeben, beispielsweise durch:

   - Wechsel auf WebREPL,
   - Wechsel auf einen anderen freien COM-Port,
   - Wechsel auf „Lokales Python“,
   - oder vollständiges Schließen von Thonny.

4. Den ESP32 über die Reset-Taste neu starten.

5. Das PC-Programm mit serieller Kommunikation starten:

   ```python
   COM_MODUS = "serial"
   ```

6. Dort muss der richtige ESP32-Port eingetragen sein:

   ```python
   ESP32_COM_PORT = "COM..."
   ESP32_COM_BAUDRATE = 115200
   ```

Nach dem Reset läuft auf dem ESP32:

```text
main.py
ESP32_BEREIT
```

Das PC-Programm öffnet anschließend den COM-Port und sendet:

```text
PC_BEREIT
```

Der ESP32 schaltet daraufhin die blaue LED ein und antwortet:

```text
PC_BEREIT_BESTAETIGT
```

Wichtig ist nur:

> Thonny und das Dobot-Steuerungsprogramm dürfen den ESP32-COM-Port 
  nicht gleichzeitig geöffnet haben.

Falls das PC-Programm keine Verbindung erhält, zuerst kontrollieren:

- Ist Thonny wirklich auf einen anderen Anschluss gewechselt?
- Hat der ESP32 nach dem Wechsel einen Reset erhalten?
- Ist die Datei auf dem ESP32 tatsächlich als `main.py` gespeichert?
- Stimmt die COM-Portnummer im PC-Programm?
- Wird der Port im Windows-Geräte-Manager angezeigt?

Dein geplanter Testablauf ist damit richtig.