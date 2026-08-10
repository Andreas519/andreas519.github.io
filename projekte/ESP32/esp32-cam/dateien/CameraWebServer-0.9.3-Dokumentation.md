# ESP32-CAM CameraWebServer 0.9.3

## Überblick

Version 0.9.3 ergänzt die automatische Wiederherstellung nach einem
WLAN-Abbruch und unterscheidbare, stark gedimmte LED-Signale für alle drei
Betriebsarten. Die wählbare AP-IP aus Version 0.9.2 bleibt erhalten. Dadurch
können in der AG mehrere Module mit getrennten Adressbereichen betrieben und
in wechselnden WLAN-Umgebungen wieder erreicht werden.

## Betriebsarten

| Betriebsart | Aufgabe | Typischer Zugriff |
|---|---|---|
| Station | Kamera im vorhandenen WLAN | vom Router vergebene IP |
| Access Point | eigenes WLAN mit Kamera und Konfiguration | wählbare private IP |
| BLE | WLAN- und AP-Konfiguration als Notzugang | `ESP32-CAM-Setup` |

## BLE-Befehl für den Access Point

```text
MODUS AP [PRIVATE-IP]
```

Beispiele:

```text
MODUS AP 192.168.41.1
MODUS AP 192.168.42.1
MODUS AP 10.20.3.1
MODUS AP
```

Mit angegebener Adresse wird diese geprüft, gespeichert und für den folgenden
AP-Start verwendet. Ohne Parameter verwendet das Modul die zuletzt
gespeicherte Adresse. Beim ersten Einsatz ist `192.168.4.1` voreingestellt.

Zulässig sind:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`
- Hostnummern von 1 bis 254 im letzten Oktett

Das Modul verwendet ein `/24`-Netz mit der Maske `255.255.255.0`. Die gewählte
Adresse ist gleichzeitig IP-Adresse und Gateway des Access Points.

Beispielantwort:

```text
Neustart in AP-Modus mit IP 192.168.41.1 ...
```

## Mehrere Module in der AG

Eine mögliche Zuordnung lautet:

| Modul | WLAN-Name | AP-IP |
|---|---|---|
| 1 | `ESP32-CAM-Setup-9A3060` | `192.168.41.1` |
| 2 | `ESP32-CAM-Setup-XXXXXX` | `192.168.42.1` |
| 3 | `ESP32-CAM-Setup-YYYYYY` | `192.168.43.1` |

Die Kennung im WLAN-Namen wird ab Version 0.9.2 aus den letzten drei Bytes der
MAC-Adresse gebildet. Für das getestete Modul mit
`58:BF:25:9A:30:60` lautet sie deshalb `9A3060`.

Hinweis: Jedes Modul bildet weiterhin sein eigenes WLAN. Unterschiedliche
IP-Netze erleichtern Dokumentation und späteres Umschalten, ermöglichen einem
einzelnen WLAN-Adapter aber nicht die gleichzeitige Verbindung mit mehreren
Access Points.

## Windows-BLE-Dialog

Der Dialog besitzt das Feld **AP-IP-Adresse** und die Schaltfläche
**Access Point starten und neu starten**. Die Eingabe wird bereits unter
Windows geprüft und anschließend als `MODUS AP <IP>` übertragen. Die Firmware
prüft die Adresse ein zweites Mal.

Auf dem iPhone wurde `BLESerial nRF` erfolgreich getestet. Die App ist der
Favorit für den direkten Textdialog mit dem Modul. Alternativ kann derselbe
Befehl mit nRF Connect über die Nordic-UART-Characteristics gesendet werden;
dort bleibt das Zeilenende `0A` erforderlich.

## Systemseite

```text
http://<aktuelle-IP>/system
```

Die Systemseite zeigt neben Version, Betriebsart, WLAN und aktueller IP nun
auch die gespeicherte AP-IP. Die Browser-Schaltflächen für Station, Access
Point und BLE bleiben erhalten.

## WLAN-Wiederherstellung und LED-Signale

Bricht die WLAN-Verbindung im Station-Modus ab, wartet das Modul 30 Sekunden
auf die automatische Wiederverbindung. Bleibt das WLAN unerreichbar, startet
es neu. Beim folgenden Start sucht es die gespeicherten WLANs und öffnet als
Rückfallebene den eigenen Access Point.

Die weiße Blitz-LED verwendet für Statussignale den stark reduzierten
PWM-Wert 2:

- Station: einmaliges kurzes Bestätigungssignal, danach aus
- Access Point: zwei kurze Impulse und eine lange Pause
- BLE: 20 ms an, 2000 ms aus (Zeitverhältnis 1:100)

## Geplante Praxiseinsätze

1. Frontkamera an einem RoboCar
2. Kamera über der Arbeitsplatte eines Dobot Magician
3. weitere mobile oder stationäre Kameraanwendungen

## Wichtige Endpunkte

| Adresse | Funktion |
|---|---|
| `/` | Kamerasteuerung und Livebild |
| `/device-info` | Version und aktuelle Geräteinformationen als JSON |
| `/system` | Systeminformationen und Moduswahl |
| `/wifi-settings` | WLAN-Konfiguration |
| `POST /station-mode` | Station-Modus für Neustart auswählen |
| `POST /ap-mode` | AP-Modus für Neustart auswählen |
| `POST /ble-mode` | BLE-Modus für Neustart auswählen |

## Build und Test

```text
Version:           0.9.3
Programmspeicher:  1.862.108 von 3.145.728 Byte (59 %)
Globale Variablen: 86.792 von 327.680 Byte (26 %)
```

Praktisch bestätigt wurden:

- vollständiger Build und Flash-Hashprüfung
- erfolgreicher Upload von Version 0.9.3 über COM6 mit 115200 Baud
- Start von Version 0.9.2 im Station-Modus
- Wechsel vom Station- in den BLE-Modus
- BLE-Befehl `MODUS AP 192.168.41.1`
- Bestätigung und Neustart in den AP-Modus
- dauerhafte Speicherung von `192.168.41.1`
- Rückkehr zum Station-Modus nach einem normalen weiteren Neustart
- sichtbarer AP-Name `ESP32-CAM-Setup-9A3060`
- WPA2-Verbindung mit `esp32cam`
- Geräteinfo im AP-Modus unter `http://192.168.41.1/device-info`
- vollständiger Wechsel Station → Access Point → Station
- BLE-Start mit GPIO 13 und funktionierender Windows-BLE-Dialog
- Statusausgabe der gespeicherten AP-IP `192.168.41.1`

Die reduzierte LED-Helligkeit, der automatische Neustart nach einem längeren
WLAN-Ausfall sowie die geplanten Anwendungsszenarien werden mit den einzelnen
Modulen praktisch weiter erprobt.
