# Codex und ESP32: Code ausführen und testen

**Ja – allerdings mit einer wichtigen Einschränkung:** Codex führt nicht selbst ESP32-Maschinencode auf deinem Computer aus. Es kann aber die auf deinem Rechner installierten Entwicklungswerkzeuge bedienen, den Code kompilieren, Tests starten, die Firmware auf einen angeschlossenen ESP32 übertragen und dessen serielle Ausgabe auswerten.

Codex kann lokale Terminalbefehle ausführen und deren Ergebnisse analysieren.

## Was möglich ist

| Aufgabe | Mit Codex möglich? | Voraussetzung |
|---|---:|---|
| Quellcode prüfen | ✅ | keine Hardware nötig |
| Compilerfehler finden | ✅ | ESP-IDF oder PlatformIO installiert |
| Firmware kompilieren | ✅ | passende Toolchain installiert |
| Unit-Tests auf dem PC | ✅ | testbare Programmlogik, gegebenenfalls Mocks |
| Firmware auf ESP32 übertragen | ✅ | ESP32 per USB angeschlossen |
| Seriellen Monitor auslesen | ✅ | Zugriff auf den COM-/USB-Port |
| Tests direkt auf dem ESP32 | ✅ | Board angeschlossen und Testsystem eingerichtet |
| LED, Sensoren oder Motoren beurteilen | ⚠️ teilweise | Messwerte oder Rückmeldungen müssen maschinell erfassbar sein |
| Hardware ohne angeschlossenes Board vollständig simulieren | ❌ nicht automatisch | zusätzliche Simulationssoftware erforderlich |

## 1. Nur kompilieren

Bei einem **ESP-IDF-Projekt** kann Codex beispielsweise ausführen:

```bash
idf.py build
```

Dabei werden Anwendung, ESP-IDF-Komponenten, Bootloader und Partitionstabelle kompiliert. Fehler und Warnungen kann Codex anschließend untersuchen und den Code korrigieren.

Ein geeigneter Auftrag wäre:

```text
Kompiliere dieses ESP-IDF-Projekt mit `idf.py build`.

Behebe nur eindeutig erkennbare Compilerfehler.
Ändere keine Pinbelegungen und keine Hardwarekonfiguration.

Zeige mir anschließend:
1. die gefundenen Fehler,
2. die vorgenommenen Änderungen,
3. das Ergebnis des erneuten Builds.
```

## 2. Firmware auf einen echten ESP32 übertragen

Ist das Board über USB angeschlossen, kann Codex beispielsweise diesen Befehl ausführen:

```bash
idf.py -p COM5 flash monitor
```

Unter Linux könnte der Port beispielsweise so heißen:

```bash
idf.py -p /dev/ttyUSB0 flash monitor
```

ESP-IDF kann damit das Projekt bauen, auf den ESP32 übertragen und anschließend die serielle Ausgabe anzeigen. Der konkrete Port muss zum angeschlossenen Gerät passen.

Auftrag an Codex:

```text
Ermittle zunächst den seriellen Port des angeschlossenen ESP32.

Kompiliere danach das Projekt und übertrage es auf das Board.
Starte anschließend den seriellen Monitor für 20 Sekunden.

Prüfe, ob:
- der ESP32 ohne Neustartschleife startet,
- die Meldung "System bereit" erscheint,
- Fehlermeldungen ausgegeben werden.

Frage vor dem Flashen nach meiner Freigabe.
```

Codex könnte wegen des Zugriffs auf den seriellen Port oder wegen seiner Sicherheitsbeschränkungen eine Genehmigung verlangen.

## 3. Tests mit PlatformIO

Für Arduino-basierte ESP32-Projekte ist **PlatformIO** häufig besonders bequem.

Codex kann dort unter anderem ausführen:

```bash
pio run
```

Firmware übertragen:

```bash
pio run --target upload
```

Seriellen Monitor öffnen:

```bash
pio device monitor
```

Tests starten:

```bash
pio test
```

PlatformIO kann Tests sowohl auf dem lokalen Computer als auch auf einem angeschlossenen Mikrocontroller ausführen. Bei Tests auf dem Board kompiliert PlatformIO die Testfirmware, lädt sie auf das Gerät und sammelt die Testergebnisse über die serielle Verbindung ein.

Ein guter Auftrag wäre:

```text
Untersuche dieses PlatformIO-Projekt.

1. Führe `pio run` aus.
2. Behebe mögliche Compilerfehler.
3. Erstelle Unit-Tests für die hardwareunabhängigen Funktionen.
4. Führe `pio test` aus.
5. Übertrage die Firmware noch nicht auf das Board.
6. Berichte getrennt über Build- und Testergebnisse.
```

## 4. Tests ohne angeschlossenen ESP32

Reine Programmlogik kann auf dem Computer getestet werden, zum Beispiel:

- Berechnungen
- Zustandsautomaten
- Messwertumrechnungen
- Grenzwertprüfungen
- Datenfilter
- Protokollauswertung
- Prüfsummen
- Zeichenkettenverarbeitung

Hardwarezugriffe wie GPIO, ADC, I²C oder SPI müssen dabei durch **Mocks** oder Ersatzfunktionen nachgebildet werden.

Beispiel:

```cpp
float spannungZuTemperatur(float spannung) {
    return spannung * 100.0f;
}
```

Diese Funktion kann Codex problemlos auf dem PC testen.

Dagegen benötigt diese Funktion normalerweise Hardware oder eine Simulation:

```cpp
int messwert = analogRead(34);
```

Codex kann zwar prüfen, ob der Aufruf syntaktisch richtig ist. Ob am Pin tatsächlich die erwartete Spannung anliegt, kann es ohne angeschlossene und entsprechend instrumentierte Hardware nicht feststellen.

## 5. Automatisierte Tests auf dem echten Board

ESP-IDF stellt dafür unter anderem das Testframework **Unity** bereit. Tests können in Testanwendungen kompiliert, auf den ESP32 übertragen und dort ausgeführt werden. Testabläufe können außerdem mit `pytest` vom Computer aus gesteuert werden.

Codex kann dabei:

1. Testfälle erstellen,
2. die Testfirmware kompilieren,
3. sie flashen,
4. Tests starten,
5. die serielle Ausgabe lesen,
6. fehlgeschlagene Tests analysieren,
7. nach Änderungen erneut testen.

## Was Codex nicht zuverlässig allein beurteilen kann

Eine Ausgabe wie

```text
LED eingeschaltet
```

beweist nur, dass das Programm diese Meldung ausgegeben hat. Sie beweist nicht, dass die LED tatsächlich leuchtet.

Für echte Hardwareprüfungen braucht Codex messbare Rückmeldungen, beispielsweise:

- einen zweiten GPIO als Rücklesesignal,
- einen Sensorwert,
- eine Antwort eines I²C-Geräts,
- eine Netzwerkantwort,
- einen Strom- oder Spannungsmesswert,
- eine Kamera oder zusätzliche Testhardware.

## Empfehlung für den Einstieg

Für den Einstieg eignet sich:

```text
PlatformIO + Codex + ein per USB angeschlossener ESP32
```

Codex kann dann den Ablauf weitgehend begleiten:

```text
Code prüfen
→ kompilieren
→ Tests ausführen
→ nach Freigabe flashen
→ seriellen Monitor lesen
→ Fehler analysieren
```

Lass Codex zunächst immer **nur kompilieren und berichten**. Das Flashen und mögliche Änderungen an Pinbelegungen solltest du ausdrücklich freigeben. So behältst du die Kontrolle über das Board und die angeschlossene Schaltung.

## Quellen

- [OpenAI Codex CLI](https://developers.openai.com/codex/cli)
- [OpenAI: Agent Approvals and Security](https://developers.openai.com/codex/agent-approvals-security)
- [ESP-IDF: Start a Project](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/start-project.html)
- [ESP-IDF: Host-based Testing](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32/api-guides/linux-host-testing.html)
- [ESP-IDF: Unit Testing](https://docs.espressif.com/projects/esp-idf/en/v5.0.5/esp32/api-guides/unit-tests.html)
- [PlatformIO: `pio test`](https://docs.platformio.org/en/latest/core/userguide/cmd_test.html)
