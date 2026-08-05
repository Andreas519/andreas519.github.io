# ESP32-CAM BLE-Dialog für Windows

Das Programm verbindet sich mit `ESP32-CAM-Setup` und stellt die WLAN-Befehle
in einer einfachen Windows-Oberfläche bereit. Zeilenumbrüche werden automatisch
gesendet und Antworten als Text angezeigt.

## Start

`ESP32-CAM-BLE-Dialog starten.bat` doppelt anklicken.

Voraussetzungen:

- Windows mit aktiviertem Bluetooth LE
- Python 3 mit Tkinter
- Python-Paket `bleak`
- ESP32-CAM im BLE-Konfigurationsmodus

Das Modul muss nicht über die Windows-Bluetooth-Einstellungen gekoppelt werden.
Das Programm sucht und verbindet es direkt über den BLE-GATT-Dienst.
