# ESP32-CAM CameraWebServer 0.9.1

## Überblick

Version 0.9.1 baut auf dem automatischen Access-Point-Fallback von Version
0.9.0 auf. Neu sind eine Systemseite, Geräteinformationen als JSON und die
gezielte Auswahl aller drei Betriebsarten über den Webbrowser.

## Betriebsarten

### Station-Modus

Das Modul verbindet sich mit einem gespeicherten 2,4-GHz-WLAN und stellt dort
Kamera, Livebild, Fotos, WLAN-Konfiguration und Systemseite bereit.

### Access-Point-Modus

Das Modul öffnet sein eigenes WLAN:

```text
WLAN-Name: ESP32-CAM-Setup-XXXXXX
Passwort:  esp32cam
Adresse:   http://192.168.4.1/
```

Der Access Point startet automatisch, wenn kein bekanntes WLAN erreichbar ist,
oder gezielt über die Systemseite. Die bekannten Kamera- und Webfunktionen
bleiben verfügbar.

### BLE-Notbetrieb

BLE läuft getrennt von Kamera und Webserver. Der Modus wird über GPIO 13 oder
die Systemseite aktiviert. Das Modul meldet sich als `ESP32-CAM-Setup`.

## Systemseite

Die Seite ist in Station- und Access-Point-Modus verfügbar:

```text
http://<IP-Adresse>/system
```

Sie zeigt:

- Programmname und Version
- aktive Betriebsart
- Gerätename
- WLAN-Name
- IP-Adresse

Außerdem enthält sie Schaltflächen für:

- Station-Modus starten
- Access-Point-Modus starten
- BLE-Notbetrieb starten

Die Schaltfläche der bereits aktiven Betriebsart ist deaktiviert. Nach einer
Auswahl wird die aktuelle HTTP-Antwort noch bestätigt und das Modul startet
anschließend neu. Dadurch wird die bisherige Netzwerkverbindung unterbrochen.

## Geräteinformationen als JSON

```text
GET /device-info
```

Beispiel im Station-Modus:

```json
{
  "program": "CameraWebServer",
  "version": "0.9.1",
  "mode": "station",
  "ssid": "WLAN-QE6FWC",
  "ip": "192.168.2.138",
  "device": "esp32-9A3060"
}
```

Im Access-Point-Modus lautet `mode` entsprechend `access-point`; SSID und IP
beziehen sich dann auf das eigene WLAN des Moduls.

## Endpunkte für den Moduswechsel

Die Umschaltbefehle akzeptieren nur POST-Anfragen:

| Endpunkt | Folgender Startmodus |
|---|---|
| `POST /station-mode` | gespeichertes WLAN suchen und verbinden |
| `POST /ap-mode` | eigenen Access Point sofort starten |
| `POST /ble-mode` | BLE-Notbetrieb starten |

Beispiele für PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://192.168.2.138/ap-mode
Invoke-RestMethod -Method Post -Uri http://192.168.4.1/station-mode
Invoke-RestMethod -Method Post -Uri http://192.168.2.138/ble-mode
```

Die gewünschte Betriebsart wird nur für den unmittelbar folgenden Neustart im
NVS vorgemerkt. Dadurch bleibt das Modul nach einem weiteren normalen Neustart
nicht dauerhaft in einem erzwungenen Modus.

## Weitere Web-Endpunkte

| Adresse | Funktion |
|---|---|
| `/` | Kamerasteuerung und Livebild |
| `/status` | Kameraeinstellungen als JSON |
| `/capture` | Browser-Einzelaufnahme |
| `/photo-capture` | Einzelaufnahme für den WindowsPhotoClient |
| `/photo-settings` | zeitgesteuerte Fotos konfigurieren |
| `/scheduled-photo` | letztes zeitgesteuertes Foto abrufen |
| `/wifi-settings` | WLANs suchen, speichern und löschen |
| `/system` | Systeminformationen und Betriebsart wählen |
| `/device-info` | Geräteinformationen als JSON |

## Sicherheit

Die Weboberfläche und die Umschalt-Endpunkte besitzen keine Anmeldung. Sie
sollten nur in einem vertrauenswürdigen lokalen Netzwerk verwendet werden. Der
eigene Access Point ist mit `esp32cam` geschützt.

## Speicher und Build

Die Zielkonfiguration lautet `esp32:esp32:esp32cam` mit `huge_app`.

```text
Programmspeicher: 1.859.448 von 3.145.728 Byte (59 %)
Globale Variablen: 86.760 von 327.680 Byte (26 %)
```

Die Firmware wurde vollständig kompiliert und mit 115200 Baud auf das Modul
mit der MAC-Adresse `58:BF:25:9A:30:60` übertragen. Alle geschriebenen
Flashbereiche wurden per Hash verifiziert.

## Praktischer Teststand

Im Station-Modus sind bestätigt:

- Start und Versionsmeldung 0.9.1
- WLAN-Verbindung und Zeitsynchronisierung
- Kamera-Webserver, Livebild und Foto-Endpunkte
- `/device-info` mit gültigen Geräteinformationen
- `/system` mit allen drei Betriebsart-Schaltflächen
- deaktivierte Station-Schaltfläche bei aktivem Station-Modus

Die tatsächlichen Neustarts in Access-Point- und BLE-Modus sowie die Rückkehr
zum Station-Modus werden anschließend gemeinsam praktisch geprüft.

