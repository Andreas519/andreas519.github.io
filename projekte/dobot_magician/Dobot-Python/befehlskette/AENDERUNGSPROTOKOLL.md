# Änderungsprotokoll

Dieses Protokoll dokumentiert die Weiterentwicklung des Projekts
**Dobot Befehlskette** ab Version 3.3.5.

## 26.07.2026, 21:30 Uhr – Bedeutung von Pause und Halt verdeutlicht

- `PAUSE` beendet den aktuell laufenden Roboterbefehl kontrolliert und wartet
  vor dem nächsten Befehl auf `WEITER`.
- `HALT` bleibt dem kritischen Ereignis vorbehalten: Die aktuelle Bewegung wird
  zwangsweise gestoppt und die Befehlskette abgebrochen.
- Die Konsolenmeldung beschreibt das Verhalten von `PAUSE` nun ausdrücklich.
- Für den praktischen Test folgt auf Position B eine Fahrt zu Position A. Nach
  einer während der Fahrt zu B angeforderten Pause darf A erst nach `WEITER`
  angefahren werden.
- Das Befehlskettenmodul wurde auf Version `3.3.5.3`, das Startprogramm auf
  Version `3.3.5.9` erhöht.

## 26.07.2026, 21:20 Uhr – Befehlskette für Pause-Test verlangsamt

- Geschwindigkeit und Beschleunigung wurden für den praktischen Pause-/Weiter-
  Test von 40 auf 15 Prozent reduziert.
- Sicherheitshub, HOME, Freigabe und die bereits bestätigte Position B bleiben
  unverändert.
- Die langsamere Fahrt zu Position B schafft ausreichend Zeit, während der
  Bewegung den Pause-Taster zu betätigen.
- Das Startprogramm wurde auf Version `3.3.5.8` erhöht.

## 26.07.2026, 21:16 Uhr – Vereinfachten Hardwareablauf bestätigt

- Die fünf Befehle Geschwindigkeit, Sicherheitshub, HOME, Warten auf
  `FREIGABE` und Fahrt zu Position B wurden vollständig ausgeführt.
- Der Taster an GPIO 18 setzte die wartende Befehlskette mit `FREIGABE` fort.
- Die Befehlskette endete normal; ESP32-Thread und Dobot-Verbindung wurden
  sauber beendet.
- Die zuvor unter hoher Nachrichtenlast beobachteten beschädigten
  `UNBEKANNTER_BEFEHL`-Meldungen traten nicht erneut auf.

## 26.07.2026, 20:58 Uhr – Aktive Beispielkette vereinfacht

- Der praktische Test erzeugte durch die Endlosschleife und die noch nicht
  vorhandenen Werte `TEMPERATUR` und `POSITION` unnötig viele Meldungen.
- Die aktive Beispielkette führt nun genau einmal Geschwindigkeit,
  Sicherheitshub, HOME, Warten auf `FREIGABE` und Fahrt zu Position B aus.
- Anschließend endet das Programm kontrolliert.
- Sensorwert-, Marken- und Sprungbefehle bleiben verfügbar, sind aber nur noch
  als weitere mögliche Befehle aufgeführt.
- Das Startprogramm wurde auf Version `3.3.5.7` erhöht.

## 26.07.2026, 20:49 Uhr – Taster für FREIGABE zugeordnet

- Die Befehlskette wartet nach HOME auf die ESP-Meldung `FREIGABE`, aber bisher
  sendete keiner der sechs Taster diese Meldung.
- Der Taster an GPIO 18 sendet nun `FREIGABE` statt `FREI_1`.
- GPIO 32 bleibt mit `FREI_2` für eine spätere Funktion verfügbar.
- Das ESP32-Programm wurde auf Version `1.3.8` erhöht.

## 26.07.2026, 20:40 Uhr – ESP32-Versionsdokumentation aktualisiert

- Die Versionsdokumentation der ESP32-Dobot-Steuerung wurde vom bisherigen
  Stand 1.2 bis zum praktisch getesteten Stand 1.3.7 ergänzt.
- Unterstützte PC-Befehle, Autostart über `main.py`, serielle Kommunikation,
  blaue Empfangsanzeige und bestätigte Hardwaretests sind dokumentiert.
- Die Dokumentation ist nun auf der aktuellen Projektseite und der parallel
  gepflegten Version-1-Seite direkt verlinkt.

## 26.07.2026, 20:10 Uhr – Wertmeldungen nicht doppelt puffern

- Der HOME-Test zeigte, dass `WERT;...`-Nachrichten nach der korrekten
  Aktualisierung des ESP-Werts zusätzlich als allgemeine Meldungen gepuffert
  wurden.
- Nach der Wertaktualisierung beendet das Kommunikationsmodul die Verarbeitung
  nun unmittelbar.
- Zwei nicht mehr benötigte, auskommentierte Rückbestätigungen wurden entfernt.
- Das Kommunikationsmodul wurde auf Version `1.4.5`, das angepasste
  Startprogramm auf Version `3.3.5.6` erhöht.

## 26.07.2026, 20:05 Uhr – Sicherheitshub vor der HOME-Fahrt

- Der praktische Test zeigte eine ruppige HOME-Fahrt, weil der Sauger auf der
  Arbeitsplatte stand und HOME in der aktuellen Höhe begann.
- Die Beispiel-Befehlskette hebt den Arm deshalb vor HOME zunächst linear und
  relativ um 30 mm in positiver Z-Richtung an.
- Der Halt-Taster stoppte die problematische Bewegung im Test sofort.
- Das angepasste Startprogramm wurde auf Version `3.3.5.5` erhöht.

## 26.07.2026, 13:00 Uhr – Abschließendes Semikolon bei ESP-Befehlen

- Abschließende leere Parameter werden bei vom PC empfangenen ESP-Befehlen
  ignoriert.
- `SIMULATION_LED_START;2;5` und `SIMULATION_LED_START;2;5;` werden dadurch
  gleich behandelt.
- Das ESP32-Programm wurde auf Version `1.3.7` erhöht.

## 26.07.2026, 12:43 Uhr – Autostart als main.py

- Die REPL-Fehlermeldungen zeigen, dass das ESP32-Steuerprogramm während des
  PC-Tests nicht lief und die Befehle deshalb als Python-Code ausgewertet wurden.
- Das ESP32-Programm muss auf dem Gerät als `main.py` gespeichert sein, damit
  MicroPython es nach dem Neustart automatisch ausführt.
- Der vorübergehende direkte Zugriff auf `UART(0)` wurde zurückgenommen.
  Ein laufendes `main.py` liest den dem REPL zugeordneten Eingang über
  `sys.stdin`.
- Die blaue Empfangsanzeige bleibt erhalten.
- Das ESP32-Programm wurde auf Version `1.3.6` erhöht.

## 26.07.2026, 11:20 Uhr – Empfangsanzeige über die blaue LED

- Jede vollständig empfangene PC-Nachricht wird für 200 ms über die blaue LED
  angezeigt.
- Die LED wechselt dafür kurz in den entgegengesetzten Zustand und kehrt
  anschließend zu ihrem vorherigen Zustand zurück.
- Dadurch bleibt die bisherige Verbindungsanzeige erhalten: Eine leuchtende
  blaue LED erlischt beim Nachrichtenempfang kurz.
- Das ESP32-Programm wurde auf Version `1.3.5` erhöht.

## 26.07.2026, 11:15 Uhr – Direkter Empfang über UART0

- Nachdem der ESP32 auch korrekt mit `CR/LF` gesendete PC-Befehle nicht über
  `sys.stdin` empfangen hat, wurde diese firmwareabhängige REPL-Schicht
  umgangen.
- Das ESP32-Programm liest die Zeichen des USB-Seriell-Wandlers nun direkt und
  nicht blockierend über `UART(0)`.
- Das ESP32-Programm wurde auf Version `1.3.4` erhöht.

## 26.07.2026, 11:04 Uhr – Zeilenende der seriellen PC-Befehle

- Das serielle Kommunikationsmodul sendet Befehle an die MicroPython-Konsole
  jetzt mit `CR/LF` statt nur mit `LF`.
- Fehler beim seriellen Senden werden mit ihrer konkreten Ursache ausgegeben
  und nicht mehr still unterdrückt.
- Das Kommunikationsmodul wurde auf Version `1.4.4`, das angepasste
  Startprogramm auf Version `3.3.5.4` erhöht.

## 26.07.2026, 10:52 Uhr – Serieller Befehlsempfang am ESP32

- Das ESP32-Programm liest PC-Befehle jetzt zeichenweise und nicht blockierend
  in einen eigenen Eingabepuffer ein.
- Sowohl `LF` als auch `CR/LF` werden als Zeilenende erkannt.
- Dadurch können Befehle wie `LED_GELB_STATUS`, `PING` und `ESP32_STATUS`
  zuverlässig verarbeitet werden.
- Das ESP32-Programm wurde auf Version `1.3.3` erhöht.

## 26.07.2026, 10:42 Uhr – Einleitungskommentare entfernt

- Die vollständigen einleitenden Mehrzeilenkommentare wurden aus den fünf
  aktiven Programmdateien entfernt.
- Versionsnummer und Versionszeitpunkt bleiben als eindeutige Konstanten erhalten.
- Der lokale Simulatorbefehl `gs` bleibt unverändert: Er wird im Simulator
  verarbeitet; nur die erzeugte Statusmeldung wird an den PC gesendet.

## 26.07.2026, 10:32 Uhr – Versionsangaben vereinheitlicht

- Doppelte Versionsangaben wurden aus den einleitenden Kommentaren der fünf
  aktiven Programmdateien entfernt.
- Die Kommentare enthalten nur noch dauerhaft gültige Funktionsbeschreibungen.
- Versionsnummer und Versionszeitpunkt stehen jeweils ausschließlich in den
  dafür vorgesehenen Konstanten.
- Die internen Patch-Versionen wurden wegen der Änderungen an allen fünf
  Dateien erhöht.

## 26.07.2026, 10:13 Uhr – Einheitliche Versionszeitpunkte

- `VERSIONSDATUM` enthält bei neuen Änderungen neben dem Datum künftig auch
  die Uhrzeit.
- Das geänderte Startprogramm erhielt nachträglich die interne Version
  `3.3.5.1` und ein eigenes `PROGRAMM_VERSIONSDATUM`.
- Das Befehlskettenmodul bleibt unverändert auf Version `3.3.5`.

## 26.07.2026 – ESP-Simulator 1.3.1

- Eingaben, die nach dem Ende der PC-Verbindung noch im Simulatorfenster
  bestätigt werden, werden nicht mehr an den geschlossenen Socket gesendet.
- Statt des Windows-Socketfehlers `WinError 10053` erscheint eine verständliche
  Meldung, und der Simulator wird kontrolliert beendet.

## 26.07.2026 – Kommunikationsmodul 1.4.1

- Eine noch aktive pauschale Rückbestätigung allgemeiner ESP32-Nachrichten
  wurde aus `esp32_kommunikation_v1_4.py` entfernt.
- Diese Rückbestätigung erzeugte zusammen mit der Antwort
  `UNBEKANNTER_BEFEHL` eine Endloskommunikation zwischen PC und Simulator.
- Die erwartete Kommunikationsmodulversion im Startprogramm wurde auf
  `1.4.1` erhöht.

## 25.07.2026, 23:40 Uhr – Aktueller Download

- Die neuesten vorhandenen v3.3.5-Programmdateien wurden in den aktiven
  Projektordner `befehlskette` übernommen.
- Das Downloadpaket `befehlskette-aktuell.zip` wurde erstellt.
- Die Projektseite unterscheidet nun zwischen dem aktuellen Download und
  der unveränderten Ausgangsversion.

## 25.07.2026 – DHT11-Integration

### Geänderte Komponenten

- `esp32_dobot_steuerung_v1_3.py`
  - DHT11-Sensor in die ESP32-Steuerung aufgenommen.
  - Sensormessungen und Fehlermeldungen für die Übertragung an den PC vorbereitet.
- `esp32_kommunikation_v1_4.py`
  - Verarbeitung der vom ESP32 übertragenen Sensorwerte und Sensorfehler ergänzt.
  - Rückantworten auf Sensorfehlermeldungen vermieden.
- `befehlskette_beispiel_v3_3_5.py`
  - Beispielablauf um die Verarbeitung der neuen Sensordaten erweitert.
- `dht11_test.py`
  - Eigenständiges Testprogramm für den DHT11-Sensor erstellt.

### Prüfungen

- Syntax der geänderten Python-Dateien geprüft.
- Simulierte DHT11-Timeoutmeldung erkannt.
- Sensorfehler gespeichert und an die Meldungswarteschlange übergeben.
- Unbeabsichtigte Rückantwort auf Sensorfehlermeldungen verhindert.

### Noch praktisch zu prüfen

- Programm auf den ESP32 übertragen.
- DHT11 am vorgesehenen GPIO anschließen.
- Kommunikation zwischen ESP32 und PC-Steuerungsprogramm am realen Aufbau testen.

## 25.07.2026 – Projektstand 3.3.5

- Stabilen Projektstand als `befehlskette-v3_3_5-komplett.zip` bereitgestellt.
- Projektdokumentation und schrittweisen Einstieg ergänzt.
- Versionsbezogene Entwicklungsdokumentation unter `doku` gesammelt.
