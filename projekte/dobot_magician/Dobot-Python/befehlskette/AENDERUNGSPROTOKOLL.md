# Änderungsprotokoll

Dieses Protokoll dokumentiert die Weiterentwicklung des Projekts
**Dobot Befehlskette** ab Version 3.3.5.

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
