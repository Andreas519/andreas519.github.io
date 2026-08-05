# Änderungsprotokoll

## 0.8.1 – 2026-08-05

- Wechsel vom Webserver-Modus in den BLE-Konfigurationsmodus über
  `POST /ble-mode` ermöglichen.
- BLE-Modus vor dem Neustart im NVS vormerken und beim Start einmalig
  aktivieren.
- HTTP-Anfrage vor dem Neustart als JSON bestätigen.

## 0.8.0 – 2026-08-05

- Neue Einzelaufnahme über den PC-Endpunkt `/photo-capture` bereitstellen.
- Windows-Programm zum Anfordern, Anzeigen und Speichern eines Fotos ergänzen.
- Den gesuchten BLE-Modulnamen im Windows-Dialog bearbeitbar machen.
- Erfolgreich gefundene BLE-Modulnamen dauerhaft als Auswahlliste speichern.

## 0.7.1 – 2026-08-05

- Das ausgewählte WLAN vor dem Verlassen des BLE-Modus vormerken.
- Vor dem WLAN-Verbindungsversuch neu starten, damit BLE und WLAN nicht
  gleichzeitig um den knappen internen Speicher konkurrieren.
- Bei einer fehlgeschlagenen WLAN-Verbindung automatisch wieder den BLE-Modus
  bereitstellen.

## 0.7.0 – 2026-08-05

- Das im Windows-Dialog ausgewählte gespeicherte WLAN gezielt verbinden.
- Alle im Flash gespeicherten WLAN-Namen beim Start seriell ausgeben.
- Gespeicherte WLANs im Windows-Dialog automatisch als Auswahlliste laden.
- Eine erneute BLE-Verbindung ohne Neustart des Windows-Dialogs ermöglichen.

## Vorgemerkt für 0.6.1

- Helligkeit der Blitz-LED im BLE-Modus deutlich reduzieren.
- Kurze AN-Zeit und niedrigeren PWM-Wert praktisch vergleichen.

## 0.6.0 – 2026-08-05

- Nach Einführung dieser Version einmalig automatisch im BLE-Modus starten.
- Erststart erst nach erfolgreichem `WLAN VERBINDEN` als abgeschlossen speichern.
- Blitz-LED im BLE-Konfigurationsmodus schwach blinken lassen.
- GPIO 13 weiterhin als manuellen Zugang zum BLE-Modus unterstützen.

## 0.5.0 – 2026-08-04

- Gespeicherte WLAN-Namen statt ihrer Anzahl beim Start ausgeben.
- Browserseite `/photo-settings` für Auflösung und Aufnahmeintervall ergänzen.
- Letztes zeitgesteuertes Foto unter `/scheduled-photo` bereitstellen.
- Fotoeinstellungen dauerhaft im NVS-Flash speichern.
- Systemzeit beim Start und anschließend alle sechs Stunden über einen
  externen Zeitdienst aktualisieren.
- Deutsche Winter- und Sommerzeit für Anzeige und Dateinamen berücksichtigen.
- Kamera-Webserver und BLE-Konfiguration in getrennten, über GPIO 13
  auswählbaren Betriebsarten stabil betreiben.
- Videostream und Steuerung gemeinsam auf Port 80 bereitstellen.

## 0.4.0 – 2026-08-04

- Mehrere lokale Start-WLANs in `wifi_secrets.h` unterstützen.
- Noch nicht im NVS vorhandene lokale WLANs bei jedem Start sicher ergänzen.
- Bereits gespeicherte WLAN-Zugänge und Passwörter nicht überschreiben.
- Offene WLANs durch ein leeres Passwort unterstützen.

## 0.3.0 – 2026-08-04

- Bis zu acht WLAN-Zugänge dauerhaft im NVS-Flash speichern.
- Automatisch das stärkste bekannte WLAN auswählen.
- WLAN-Zugänge über einen BLE-UART-Dialog verwalten.
- BLE-Gerätename `ESP32-CAM-Setup` verwenden.
- WLAN-Kennwörter nicht mehr über die serielle Schnittstelle ausgeben.
- Lokale WLAN-Startdaten aus der Versionsverwaltung ausschließen.
- Tastereingang an GPIO 13 beibehalten.

## Frühere Entwicklungsstände

- **0.2.0:** Tastereingang von GPIO 16 auf GPIO 13 verlegt.
- **0.1.0:** CameraWebServer für das AI-Thinker ESP32-CAM eingerichtet.

Die Stände 0.1.0 und 0.2.0 wurden vor Einführung der lokalen
Versionsverwaltung erstellt und sind daher nur dokumentiert, nicht als
separate Git-Commits vorhanden.
