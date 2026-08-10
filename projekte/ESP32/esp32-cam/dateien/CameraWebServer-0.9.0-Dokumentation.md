# ESP32-CAM CameraWebServer 0.9.0

## Überblick

Version 0.9.0 ergänzt den Kamera-Webserver um einen automatischen
Access-Point-Fallback. Das Modul bleibt dadurch auch erreichbar, wenn es in
einer unbekannten Umgebung kein gespeichertes WLAN findet. BLE bleibt als
getrennter Notzugang erhalten.

## Startverhalten

1. Beim Einschalten lädt das Modul bis zu acht gespeicherte WLAN-Zugänge.
2. Es sucht nach erreichbaren bekannten WLANs und versucht die Verbindung.
3. Bei Erfolg startet es Kamera, Webserver und – soweit ein Internetzugang
   besteht – die Zeitsynchronisierung.
4. Ist kein bekanntes WLAN erreichbar oder schlägt die Verbindung fehl,
   startet es einen eigenen Access Point mit Kamera- und Konfigurationsserver.
5. Wird GPIO 13 beim Neustart gedrückt gehalten oder vorher `POST /ble-mode`
   aufgerufen, startet stattdessen der BLE-Notbetrieb.

Eine fehlgeschlagene WLAN-Verbindung führt nicht zu einer Neustartschleife.
Das Modul bleibt im Access-Point-Modus erreichbar.

## Eigenes WLAN der ESP32-CAM

```text
WLAN-Name: ESP32-CAM-Setup-XXXXXX
Passwort:  esp32cam
Kamera:    http://192.168.4.1/
WLAN:      http://192.168.4.1/wifi-settings
```

`XXXXXX` ist eine gerätespezifische Endung. Sie hilft dabei, mehrere
ESP32-CAM-Module auseinanderzuhalten.

Nach der Verbindung mit diesem WLAN stehen die bekannten Webfunktionen bereit:

- Kamerasteuerung und MJPEG-Livebild
- Einzelaufnahme im Browser
- Einzelaufnahme für den WindowsPhotoClient
- zeitgesteuerte Aufnahmen und deren Einstellungen
- Abruf des zuletzt gespeicherten Fotos
- Wechsel in den BLE-Notbetrieb
- WLAN-Konfiguration

Im reinen Access-Point-Modus besteht normalerweise kein Internetzugang. Die
Systemzeit kann deshalb dort nicht neu synchronisiert werden. Aufnahmen sind
trotzdem möglich; ohne gültige synchronisierte Zeit wird kein verlässlicher
Zeitstempel verwendet.

## WLAN im Browser konfigurieren

Unter `/wifi-settings` führt das Modul einen WLAN-Scan aus. Die Seite kann:

- gefundene WLANs auswählen
- eine versteckte SSID manuell erfassen
- neue Zugangsdaten speichern
- das Passwort eines bekannten WLANs aktualisieren
- gespeicherte WLANs auflisten und löschen
- das ausgewählte WLAN für den folgenden Neustart vormerken

Nach `Speichern, verbinden und neu starten` wird die neue Konfiguration im
NVS-Flash abgelegt. Gelingt die Verbindung nach dem Neustart nicht, erscheint
der Access Point erneut. Bei einem bereits gespeicherten WLAN behält ein leeres
Passwortfeld das vorhandene Passwort bei. Für ein neues offenes WLAN bleibt das
Feld ebenfalls leer.

## Wichtige Web-Endpunkte

| Adresse | Funktion |
|---|---|
| `/` | Kamerasteuerung |
| `/stream` | MJPEG-Livebild |
| `/capture` | einzelne Browser-Aufnahme |
| `/photo-capture` | neue Aufnahme für den WindowsPhotoClient |
| `/photo-settings` | Auflösung und Aufnahmeintervall einstellen |
| `/scheduled-photo` | letztes zeitgesteuertes Foto abrufen |
| `/wifi-settings` | WLAN suchen, speichern und löschen |
| `/wifi-save` | WLAN-Daten per POST speichern |
| `/wifi-delete` | gespeichertes WLAN per POST löschen |
| `/ble-mode` | per POST in den BLE-Notbetrieb wechseln |
| `/status` | Kameraeinstellungen als JSON |
| `/control` | Kameraeinstellungen ändern |

Im vorhandenen WLAN wird die vom Router vergebene IP-Adresse verwendet. Im
eigenen WLAN ist die Adresse immer `192.168.4.1`.

## BLE-Notbetrieb

BLE und Kamera-Webserver laufen wegen des begrenzten internen Arbeitsspeichers
nicht gleichzeitig. Der BLE-Modus wird auf einem der folgenden Wege gestartet:

- GPIO 13 beim Neustart gegen GND halten
- im Webserver-Modus `POST /ble-mode` aufrufen

Das Modul meldet sich als `ESP32-CAM-Setup` und unterstützt weiterhin:

```text
HILFE
STATUS
WLAN LISTE
WLAN HINZUFUEGEN <SSID>|<PASSWORT>
WLAN LOESCHEN <SSID>
WLAN VERBINDEN <SSID>
```

## Lokale WLAN-Startdaten

Zusätzliche WLANs können weiterhin in einer privaten `wifi_secrets.h` stehen.
Als Vorlage dient `wifi_secrets.example.h`. Noch nicht vorhandene Einträge
werden in den NVS-Flash übernommen, bestehende Passwörter aber nicht
überschrieben. Die private Datei ist von Git und vom Download-Archiv
ausgeschlossen.

## Kompilieren

Getestete Zielkonfiguration:

```text
Board: esp32:esp32:esp32cam
Partition: huge_app
```

Beispiel mit Arduino CLI:

```text
arduino-cli compile --clean --jobs 1 --fqbn esp32:esp32:esp32cam CameraWebServer
```

## Teststand

Die Firmware wurde statisch geprüft, vollständig kompiliert und mit 115200 Baud
erfolgreich auf das ESP32-CAM-Modul übertragen. Folgende Funktionen wurden im
Station-Modus praktisch bestätigt:

- Start von Version 0.9.0 und Verbindung mit einem gespeicherten WLAN
- Zeitsynchronisierung
- Kamera-Webseite und Statusabfrage
- MJPEG-Livebild
- Browser- und PC-Einzelaufnahme
- zeitgesteuerte Aufnahme und Fotoabruf
- WLAN-Konfigurationsseite mit Scan, Speichern- und Löschen-Funktion

Der Access-Point-Fallback und der BLE-Notbetrieb sind noch praktisch zu testen.

Beim späteren Hardwaretest sollten mindestens diese Fälle geprüft werden:

1. Start ohne bekanntes WLAN und Zugriff über `192.168.4.1`
2. Kamera, Livebild und Foto-Endpunkte im eigenen WLAN
3. Speichern eines gültigen neuen WLANs und erfolgreicher Neustart
4. falsches Passwort und Rückkehr zum Access Point
5. Löschen eines gespeicherten WLANs
6. BLE-Start über GPIO 13 und über `POST /ble-mode`
