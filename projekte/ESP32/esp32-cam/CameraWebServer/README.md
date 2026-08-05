# CameraWebServer

Aktuelle Version: **0.8.0**

## Lokale WLAN-Startdaten

`wifi_secrets.example.h` nach `wifi_secrets.h` kopieren und dort bis zu acht
WLANs eintragen. Die lokale Datei `wifi_secrets.h` wird von Git ignoriert.
Noch nicht gespeicherte Einträge werden beim Start in den NVS-Flash übernommen.
Bereits gespeicherte Einträge werden dabei nicht überschrieben. Ein leeres
Passwort kennzeichnet ein offenes WLAN.

## BLE-Dialog

Das Modul meldet sich als `ESP32-CAM-Setup` und stellt einen Nordic-UART-
kompatiblen BLE-Dienst bereit. Jeder Befehl wird mit einem Zeilenumbruch
abgeschlossen.

Für den BLE-Konfigurationsmodus GPIO 13 beim Neustart gedrückt halten. Kamera-
Webserver und BLE laufen wegen des begrenzten internen RAMs des ESP32-CAM in
getrennten Betriebsarten. Nach `WLAN VERBINDEN` startet das Modul automatisch
in den Webserver-Modus neu.

Beim ersten Start von Version 0.6.0 wird der BLE-Modus einmalig automatisch
aktiviert; ein Zugriff auf den Taster ist dafür nicht erforderlich. Die
Blitz-LED blinkt in diesem Modus schwach. Der automatische Erststart gilt nach
einem erfolgreichen `WLAN VERBINDEN` als abgeschlossen.

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
