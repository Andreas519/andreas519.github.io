# ESP32-CAM CameraWebServer 0.8.0

## Überblick

Das Projekt erweitert den ursprünglichen `CameraWebServer` der Arduino-ESP32-
Bibliothek um eine dauerhafte WLAN-Verwaltung, einen BLE-Konfigurationsdialog,
zeitgesteuerte Fotos und einen Fotoabruf für Windows-PCs.

Die aktuelle Firmware-Version ist **0.8.0**.

## Funktionsumfang

- mehrere WLAN-Zugänge dauerhaft im Flash-Speicher verwalten
- gewünschtes WLAN vor dem Wechsel in den Webserver-Modus auswählen
- WLAN-Konfiguration über Bluetooth Low Energy
- Kamera-Livebild und Kamerasteuerung im Webbrowser
- einzelne Fotos über den Browser aufnehmen
- Auflösung und Intervall zeitgesteuerter Fotos konfigurieren
- letztes zeitgesteuertes Foto anzeigen und herunterladen
- Systemzeit über das Netzwerk aktualisieren
- Datums- und Zeitstempel in Foto-Dateinamen verwenden
- neue Kameraaufnahme per PC-Programm anfordern
- empfangenes JPEG auf dem PC anzeigen und lokal speichern
- unterschiedliche BLE-Namen mehrerer ESP32-CAM-Module im Windows-Dialog
  verwalten

## Hardware

Das Projekt wurde für ein ESP32-CAM-Modul mit AI-Thinker-Pinbelegung
entwickelt und getestet.

Benötigt werden:

- ESP32-CAM
- USB-Seriell-Adapter, im Test ein CH340 an COM6
- stabile 5-Volt-Stromversorgung
- WLAN mit 2,4 GHz
- optional ein Taster an GPIO 13 gegen GND

Die SD-Karte wird nicht verwendet. Dadurch steht GPIO 13 für den Taster zur
Verfügung.

## Betriebsarten

Wegen des begrenzten internen Arbeitsspeichers laufen BLE-Konfiguration und
Kamera-Webserver nicht gleichzeitig.

### BLE-Konfigurationsmodus

In diesem Modus:

- meldet sich das Modul standardmäßig als `ESP32-CAM-Setup`
- können WLAN-Zugänge aufgelistet, ergänzt und gelöscht werden
- kann das WLAN für den folgenden Neustart ausgewählt werden
- blinkt die weiße Blitz-LED als Statusanzeige

Beim ersten Start wird dieser Modus automatisch aktiviert. Später kann er
durch einen beim Neustart gedrückten Taster an GPIO 13 geöffnet werden.

### WLAN- und Webserver-Modus

Nach der WLAN-Auswahl speichert das Modul die gewünschte SSID und startet neu.
Erst nach dem Neustart wird die WLAN-Verbindung aufgebaut. Dadurch konkurrieren
BLE und WLAN nicht gleichzeitig um den knappen Speicher.

Bei erfolgreicher Verbindung startet das Modul Kamera, Webserver,
Zeitsynchronisierung und zeitgesteuerte Aufnahmen. Scheitert die Verbindung,
wird wieder der BLE-Konfigurationsmodus bereitgestellt.

## Serielle Startmeldung

Der serielle Monitor verwendet **115200 Baud**. Eine erfolgreiche Startmeldung
sieht beispielsweise so aus:

```text
ESP32 Cam 01
CameraWebServer.ino
Version 0.8.0
Saved WiFi networks: WLAN-1,WLAN-2
Connecting to WiFi: WLAN-1
WiFi connected, IP: 192.168.x.x
System time synchronized: TT.MM.JJJJ hh:mm:ss
HTTP camera server started
Camera Ready! Use 'http://192.168.x.x' to connect
```

Die IP-Adresse wird vom jeweiligen WLAN vergeben und kann sich ändern.

## WLAN-Daten

Bis zu acht WLAN-Zugänge können gespeichert werden. Die Daten liegen dauerhaft
im NVS-Flash des ESP32.

Zusätzliche Startdaten können lokal in `wifi_secrets.h` eingetragen werden. Als
Vorlage dient `wifi_secrets.example.h`.

```cpp
#define INITIAL_WIFI_NETWORKS \
  { "WLAN-1", "Passwort-1" }, \
  { "Offenes-WLAN", "" }
```

`wifi_secrets.h` wird nicht in Git gespeichert und ist nicht im öffentlichen
ZIP-Archiv enthalten. Die NVS-Daten sind dauerhaft, jedoch nicht verschlüsselt.

## BLE-Schnittstelle

Die Firmware verwendet den Nordic-UART-Dienst.

| Funktion | UUID |
|---|---|
| Dienst | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` |
| Befehle zum ESP32-CAM | `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` |
| Antworten vom ESP32-CAM | `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` |

Jeder Textbefehl endet mit einem Zeilenumbruch.

### BLE-Befehle

```text
HILFE
STATUS
WLAN LISTE
WLAN HINZUFUEGEN <SSID>|<PASSWORT>
WLAN LOESCHEN <SSID>
WLAN VERBINDEN <SSID>
```

Beim erneuten Speichern einer vorhandenen SSID wird deren Passwort
aktualisiert. Passwörter werden in Listen und Protokollen nicht ausgegeben.

## Windows-BLE-Dialog

Der Ordner `WindowsBLEDialog` enthält die grafische WLAN-Verwaltung.

Start:

```text
ESP32-CAM-BLE-Dialog starten.bat
```

Der Dialog:

- sucht nach einem einstellbaren BLE-Modulnamen
- merkt sich erfolgreich gefundene Modulnamen
- fügt Zeilenumbrüche automatisch an Befehle an
- setzt aufgeteilte BLE-Antworten wieder zusammen
- zeigt gespeicherte WLANs in einem Auswahlfeld
- verdeckt eingegebene WLAN-Passwörter
- startet das Modul mit dem ausgewählten WLAN neu

Voraussetzungen sind Python 3, Tkinter und das Paket `bleak`.

## Weboberfläche

Nach erfolgreicher WLAN-Verbindung wird die im seriellen Monitor ausgegebene
Adresse im Browser geöffnet:

```text
http://192.168.x.x/
```

### Wichtige Web-Endpunkte

| Adresse | Funktion |
|---|---|
| `/` | Kamerasteuerung |
| `/stream` | MJPEG-Livebild |
| `/capture` | einzelne Aufnahme für die Browsersteuerung |
| `/photo-settings` | Auflösung und Aufnahmeintervall einstellen |
| `/scheduled-photo` | letztes zeitgesteuertes Foto abrufen |
| `/photo-capture` | neue Aufnahme für das PC-Programm erzeugen |
| `/status` | aktuelle Kameraeinstellungen als JSON |
| `/control` | Kameraeinstellungen ändern |

## Zeitgesteuerte Fotos

Unter `/photo-settings` werden Auflösung und Aufnahmeintervall eingestellt.
Der Wert `0` deaktiviert automatische Aufnahmen.

Unterstützte Auflösungen:

- QVGA: 320 × 240
- VGA: 640 × 480
- SVGA: 800 × 600
- XGA: 1024 × 768
- SXGA: 1280 × 1024
- UXGA: 1600 × 1200

Nur das jeweils letzte zeitgesteuerte Foto liegt im Arbeitsspeicher. Die nächste
Aufnahme ersetzt das vorherige Bild. Nach einem Neustart ist das Bild verloren.
Es werden keine Fotos auf einer SD-Karte oder dauerhaft im Programm-Flash
gesammelt.

## Systemzeit und Dateinamen

Nach einer WLAN-Verbindung aktualisiert das Modul seine Uhr über einen externen
Zeitdienst. Eine erneute Synchronisierung erfolgt regelmäßig. Deutsche Winter-
und Sommerzeit werden berücksichtigt.

Beispiel für einen Dateinamen:

```text
esp32-cam-20260805-211025.jpg
```

## WindowsPhotoClient

Der Ordner `WindowsPhotoClient` enthält das PC-Programm für Einzelaufnahmen.

Start:

```text
ESP32-CAM-Fotoabruf starten.bat
```

Bedienung:

1. IP-Adresse oder Netzwerkname des Moduls eintragen.
2. **Neues Foto aufnehmen** auswählen.
3. Das Modul erzeugt über `/photo-capture` ein neues JPEG.
4. Das Programm zeigt das empfangene Bild an.
5. Das Bild kann mit **Foto speichern unter ...** lokal gespeichert werden.

Erfolgreich verwendete Moduladressen werden dauerhaft gemerkt. Voraussetzungen
sind Python 3, Tkinter und das Paket `Pillow`.

Der praktische Test von Version 0.8.0 übertrug erfolgreich ein JPEG mit
640 × 480 Pixeln vom ESP32-CAM zum PC.

## Arduino-Konfiguration

Verwendete Board-Einstellung:

```text
AI Thinker ESP32-CAM
FQBN: esp32:esp32:esp32cam
Partitionierung: Huge APP (3 MB No OTA / 1 MB SPIFFS)
```

Die Firmware belegte beim Test ungefähr:

- 58 Prozent des Programmspeichers
- 26 Prozent des dynamischen Speichers für globale Variablen

Bei knappem PC-Arbeitsspeicher kann der Build auf einen Auftrag begrenzt
werden:

```powershell
arduino-cli compile --clean --jobs 1 --fqbn esp32:esp32:esp32cam CameraWebServer
```

Für den verwendeten CH340-Adapter war die Übertragung mit 115200 Baud
zuverlässiger als mit 460800 Baud. Der serielle Monitor muss vor dem Flashen
geschlossen werden, damit der COM-Anschluss frei ist.

## Dateien und Verzeichnisse

| Pfad | Inhalt |
|---|---|
| `CameraWebServer/` | Arduino-Firmware 0.8.0 |
| `WindowsBLEDialog/` | BLE- und WLAN-Konfiguration für Windows |
| `WindowsPhotoClient/` | Fotoabruf, Anzeige und Speicherung auf dem PC |
| `dateien/CameraWebServer-v0.8.0.zip` | Firmware-Quellcode ohne private WLAN-Daten |
| `dateien/Probleme-und-Loesungen.md` | Entwicklungsprobleme und Lösungen |

## Bekannte Einschränkungen

- BLE-Konfiguration und Kamera-Webserver laufen nur in getrennten Modi.
- Die SD-Karte wird nicht verwendet.
- Bilder werden auf dem Modul nicht dauerhaft gesammelt.
- Die Blitz-LED ist im BLE-Modus trotz PWM noch sehr hell. Eine kürzere
  Einschaltzeit und ein niedrigerer PWM-Wert sind für eine spätere Version
  vorgesehen.
- Der Webserver besitzt derzeit keine Benutzeranmeldung. Er sollte nur in
  vertrauenswürdigen lokalen Netzwerken verwendet werden.

## Teststatus der Version 0.8.0

Folgende Funktionen wurden praktisch geprüft:

- Firmware kompiliert und auf das ESP32-CAM übertragen
- Version 0.8.0 im seriellen Monitor bestätigt
- Verbindung mit dem ausgewählten WLAN hergestellt
- Kamerasteuerung und Livebild geöffnet
- zeitgesteuerte Fotos erzeugt und heruntergeladen
- Datums- und Zeitstempel in Foto-Dateinamen geprüft
- Foto über `/photo-capture` vom PC angefordert
- empfangenes JPEG im WindowsPhotoClient verarbeitet
- BLE-Modulnamen im Windows-Dialog bearbeitbar und dauerhaft speicherbar

## Download

Der aktuelle Firmware-Quellcode steht als
`dateien/CameraWebServer-v0.8.0.zip` bereit. Vor der Veröffentlichung wurde
geprüft, dass die private Datei `wifi_secrets.h` nicht enthalten ist.
