# ESP32-CAM BLE-Dialog für Windows

Das Programm verbindet sich mit `ESP32-CAM-Setup` und stellt die WLAN-Befehle
in einer einfachen Windows-Oberfläche bereit. Zeilenumbrüche werden automatisch
gesendet und Antworten als Text angezeigt.

Nach dem Verbinden lädt das Programm die im Modul gespeicherten WLAN-Namen in
das Auswahlfeld. Beim Neustart wird ausschließlich das dort ausgewählte WLAN
verwendet. Nach einer BLE-Trennung kann das Modul ohne Neustart des Dialogs
erneut gesucht werden.

Über das Feld **AP-IP-Adresse** kann das Modul direkt aus dem BLE-Modus in den
Access-Point-Modus wechseln. Beispiel: `192.168.41.1`. Die Adresse muss aus
einem privaten IPv4-Bereich stammen und wird im Modul dauerhaft gespeichert.
Damit lassen sich in der AG unterschiedliche Adressbereiche für mehrere Module
festlegen.

Der zu suchende BLE-Modulname kann im Feld **Modulname** geändert werden.
Erfolgreich gefundene Namen bleiben dauerhaft gespeichert und können beim
nächsten Start aus der Liste ausgewählt werden.

## Start

`ESP32-CAM-BLE-Dialog starten.bat` doppelt anklicken.

Voraussetzungen:

- Windows mit aktiviertem Bluetooth LE
- Python 3 mit Tkinter
- Python-Paket `bleak`
- ESP32-CAM im BLE-Konfigurationsmodus

Das Modul muss nicht über die Windows-Bluetooth-Einstellungen gekoppelt werden.
Das Programm sucht und verbindet es direkt über den BLE-GATT-Dienst.
