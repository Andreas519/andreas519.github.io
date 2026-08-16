# Orion-Steuerung

Arduino-Programm für den Makeblock Starter mit Me-Orion-Board. Es verarbeitet
Fahrbefehle, stoppt die Motoren bei einem Kommunikationsausfall und sendet
konfigurierbare Sensormesswerte an das Steuerprogramm auf dem PC.

## Aktuelle Version

- Programm: `orion-steuerung`
- Version: `1.3.0`
- Protokollversion: `1`
- Boardprofil: `arduino:avr:uno`
- Abhängigkeit: MakeBlockDrive `3.27`
- Baudrate: `115200`

Das Programm verwendet [Semantic Versioning](https://semver.org/lang/de/):

- **MAJOR** für inkompatible Änderungen am seriellen Protokoll,
- **MINOR** für abwärtskompatible Funktionen und Sensoren,
- **PATCH** für abwärtskompatible Korrekturen.

Die Protokollversion wird getrennt geführt. Sie ändert sich nur, wenn das
PC-Steuerprogramm Nachrichten anders senden oder auswerten muss.

## Identifikation

Der mit einem Zeilenende gesendete Befehl `i` liefert beispielsweise:

```text
ID,programm=orion-steuerung,version=1.3.0,protokoll=1
ID,board=Me Orion,mcu=ATmega328P,profil=arduino:avr:uno,makeblockdrive=3.27
ID,build=Aug 16 2026 12:34:56
ID,ports=motor_links@M1;motor_rechts@M2;servo@PORT_3/SLOT1/D12;status_led@D13;usb_uart@D0_RX+D1_TX;
ID,sensoren=
```

`build` stammt aus den Compilerwerten `__DATE__` und `__TIME__`. Die
Sensorzeile beschreibt die beim Kompilieren aktivierte Konfiguration, nicht
eine automatische Hardwareerkennung. Die Zeile `ID,ports` nennt die vom
Programm erwartete Belegung. Aktivierte Sensoren werden dort zusätzlich
angehängt.

## Serielles Protokoll

Jeder Befehl endet mit `\n` oder `\r`. Motorwerte liegen zwischen `-255` und
`255`.

| Befehl | Funktion |
|---|---|
| `i` | Software, Build und Sensorkonfiguration identifizieren |
| `h` oder `0` | beide Motoren stoppen |
| `f 150` | beide Motoren mit Wert 150 fahren |
| `f 150 100` | linken und rechten Motor getrennt ansteuern |
| `l 120` | nur den linken Motor ansteuern |
| `r 120` | nur den rechten Motor ansteuern |
| `s 90` | Servo auf 90 Grad stellen |

Ausgabepräfixe:

| Präfix | Bedeutung |
|---|---|
| `READY` | Programmstart mit Name und Version |
| `ID` | Antwort auf den Befehl `i` |
| `OK` | gültiger Befehl wurde übernommen |
| `ERR` | ungültiger Befehl oder Sensorfehler |
| `SAFE` | sicherheitsbedingter Motorstopp |
| `TEL` | periodische Sensortelemetrie |

## Sensorkonfiguration

Sensoren werden über die `SENSOR_...`-Definitionen am Anfang des Sketches
aktiviert. Nur tatsächlich angeschlossene Module dürfen aktiviert werden.
Gyro und Kompass verwenden den gemeinsamen I2C-Bus und benötigen `Wire`.

In Version 1.1.0 sind für den Fahrtest alle Sensoren deaktiviert. Die
eingebaute LED blinkt nach dem Reset schnell mit 5 Hz. Sobald das
PC-Steuerprogramm oder der serielle Monitor den Befehl `i` mit Zeilenende
gesendet hat, blinkt sie dauerhaft langsam mit 0,5 Hz. Beim ATmega328P kann die
Software nicht erkennen, ob ein serielles Terminal geschlossen wurde. Der
Zustand wird deshalb erst beim nächsten Reset wieder auf "nicht verbunden"
gesetzt.

## Servo

Ein kleiner Servo wird über einen Me RJ25 Adapter an `PORT_3`, `SLOT1`
angeschlossen. Das Signal liegt damit auf Orion-Pin `D12`. `SLOT2` wird nicht
verwendet, weil dessen Pin `D13` bereits die eingebaute Status-LED ansteuert.

Der Befehl `s <winkel>` akzeptiert Winkel von 0 bis 180 Grad. Der Servoausgang
wird erst beim ersten gültigen Servobefehl aktiviert. Vor dem Anschließen sind
Signal, 5 V und GND am Adapter zu prüfen. Bei Servos mit höherem Strombedarf ist
eine separate 5-V-Versorgung mit gemeinsamer Masse zu verwenden.

## Versionshistorie

### 1.3.0 - 2026-08-16

- Identifikationsbefehl `i` um die erwartete Portbelegung erweitert
- Motoren, Servo, Status-LED, USB-UART und aktivierte Sensorports werden gemeldet

### 1.2.0 - 2026-08-16

- Servosteuerung an `PORT_3`, `SLOT1` ergänzt
- neuer Befehl `s <winkel>` für 0 bis 180 Grad
- Servoausgang wird erst beim ersten gültigen Befehl aktiviert

### 1.1.1 - 2026-08-16

- langsames Blinken nach `i` bleibt bis zum nächsten Reset aktiv
- Blinkfrequenzen deutlich auf 5 Hz und 0,5 Hz getrennt

### 1.1.0 - 2026-08-16

- alle Sensoren für den reinen Fahrtest deaktiviert
- Befehl `i` als dauerhaften Verbindungs-Handshake festgelegt
- schnelles Blinken mit 5 Hz ohne Handshake, langsames Blinken mit 0,5 Hz nach Handshake

### 1.0.0 - 2026-08-16

- Fahrbefehle für die Motoren M1 und M2
- automatischer Stopp bei Kommunikationsausfall
- periodische Telemetrie für konfigurierbare Makeblock-Sensoren
- Unterstützung für Me Gyro und Me Compass
- Identifikationsbefehl `i`
- versionierte, maschinenlesbare Start- und Identifikationsmeldungen