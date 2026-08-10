# CameraWebServer

Aktuelle Version: **0.9.3**

## Wechsel von BLE zum Access Point

Im BLE-Modus kann eine private AP-IP-Adresse gewählt und der Access Point
direkt gestartet werden:

```text
MODUS AP 192.168.41.1
```

`MODUS AP` ohne Adresse verwendet die zuletzt gespeicherte AP-IP. Erlaubt sind
private IPv4-Bereiche mit einer Hostnummer von 1 bis 254. Der Windows-BLE-
Dialog stellt dafür ein eigenes Eingabefeld bereit.

## Systemseite und Betriebsarten

Unter `/system` zeigt die Firmware Programmversion, aktive Betriebsart,
Gerätenamen, WLAN und IP-Adresse an. Von dort kann das Modul per Schaltfläche
für den nächsten Neustart in den Station-, Access-Point- oder BLE-Modus
versetzt werden. `/device-info` stellt dieselben Geräteinformationen als JSON
bereit.

Die Umschalt-Endpunkte akzeptieren ausschließlich POST-Anfragen:

```text
POST /station-mode
POST /ap-mode
POST /ble-mode
```

## Automatischer Access-Point-Fallback

Beim Start versucht das Modul zuerst, ein gespeichertes 2,4-GHz-WLAN zu
erreichen. Gelingt das nicht, öffnet es automatisch ein eigenes WLAN:

```text
Name:     ESP32-CAM-Setup-XXXXXX
Passwort: esp32cam
Adresse:  http://<konfigurierte-AP-IP>/
WLAN:     http://<konfigurierte-AP-IP>/wifi-settings
```

Die sechs Zeichen am Ende des WLAN-Namens stammen aus der Geräte-ID. Dadurch
lassen sich mehrere Module unterscheiden. Im eigenen WLAN stehen Kamera,
Livebild, Einzelaufnahme, Fotoeinstellungen und WLAN-Konfiguration gemeinsam
zur Verfügung. Nach dem Speichern eines WLANs startet das Modul neu. Scheitert
auch dieser Verbindungsversuch, öffnet es wieder seinen Access Point.

Bricht eine bestehende WLAN-Verbindung ab, wartet das Modul 30 Sekunden auf
die automatische Wiederverbindung. Bleibt das WLAN unerreichbar, startet es
neu und verwendet anschließend den Access-Point-Fallback.

## LED-Signale der Betriebsarten

- Station-Modus: Nach erfolgreicher Verbindung leuchtet die Blitz-LED einmal
  kurz und schwach; danach bleibt sie aus.
- Access-Point-Modus: Die LED blinkt schwach zweimal kurz und legt danach eine
  längere Pause ein.
- BLE-Modus: Die LED leuchtet schwach für 20 ms und bleibt danach 2000 ms aus
  (Zeitverhältnis 1:100). Alle Statussignale verwenden den stark reduzierten
  PWM-Wert 2.

## Erprobte und geplante Anwendungen

- Frontkamera an einem RoboCar
- Kamera über der Arbeitsplatte eines Dobot Magician
- weitere mobile oder stationäre Kameraanwendungen

Für mehrere Module sind die gerätespezifischen AP-Namen und frei wählbaren
privaten AP-IP-Adressen vorgesehen. Dadurch lassen sich die Kameras auch ohne
vorhandenes WLAN einzeln konfigurieren und testen.

## Lokale WLAN-Startdaten

`wifi_secrets.example.h` nach `wifi_secrets.h` kopieren und dort bis zu acht
WLANs eintragen. Die lokale Datei `wifi_secrets.h` wird von Git ignoriert.
Noch nicht gespeicherte Einträge werden beim Start in den NVS-Flash übernommen.
Bereits gespeicherte Einträge werden dabei nicht überschrieben. Ein leeres
Passwort kennzeichnet ein offenes WLAN.

## BLE-Notbetrieb

Das Modul meldet sich als `ESP32-CAM-Setup` und stellt einen Nordic-UART-
kompatiblen BLE-Dienst bereit. Jeder Befehl wird mit einem Zeilenumbruch
abgeschlossen.

Für den BLE-Konfigurationsmodus GPIO 13 beim Neustart gedrückt halten. Kamera-
Webserver und BLE laufen wegen des begrenzten internen RAMs des ESP32-CAM in
getrennten Betriebsarten. Nach `WLAN VERBINDEN` startet das Modul automatisch
in den Webserver-Modus neu.

BLE dient ab Version 0.9.0 nur noch als Notzugang. Es wird über GPIO 13 oder
über `POST /ble-mode` für den nächsten Neustart aktiviert.

```text
HILFE
STATUS
WLAN LISTE
WLAN HINZUFUEGEN <SSID>|<PASSWORT>
WLAN LOESCHEN <SSID>
WLAN VERBINDEN <SSID>
```

Bis zu acht WLAN-Zugänge können gespeichert werden. Kennwörter werden im
Dialog nicht angezeigt. Der NVS-Speicher ist dauerhaft, aber nicht
verschlüsselt.

## Zeitgesteuerte Fotos

Unter `/photo-settings` lassen sich Auflösung und Aufnahmeintervall einstellen.
Der Wert `0` deaktiviert automatische Aufnahmen. Das jeweils letzte Foto steht
unter `/scheduled-photo` für den Browser oder ein PC-Programm bereit. Die
Einstellungen bleiben im NVS-Flash gespeichert.

Nach einer WLAN-Verbindung aktualisiert das Modul seine Uhr über einen externen
Zeitdienst. Eine erneute Aktualisierung erfolgt alle sechs Stunden. Anzeige und
Foto-Dateinamen verwenden die deutsche Winter- beziehungsweise Sommerzeit.

## Fotoabruf vom PC

Eine neue Einzelaufnahme kann per `GET /photo-capture` angefordert werden. Das
Windows-Programm im Ordner `WindowsPhotoClient` zeigt das empfangene JPEG an
und kann es mit Datums- und Zeitstempel im Dateinamen speichern.

## Wechsel in den BLE-Modus per HTTP

Im Webserver-Modus merkt `POST /ble-mode` den BLE-Modus vor und startet das
Modul neu. Nach dem Neustart ist der Webserver nicht mehr erreichbar und das
Modul kann per BLE konfiguriert werden.

```powershell
Invoke-RestMethod -Method Post -Uri http://192.168.x.x/ble-mode
```

Der Endpunkt besitzt keine Anmeldung und darf deshalb nur in einem
vertrauenswürdigen lokalen Netzwerk verwendet werden.
