# CameraWebServer

Aktuelle Version: **0.3.0**

## Lokale WLAN-Startdaten

`wifi_secrets.example.h` nach `wifi_secrets.h` kopieren und dort das erste
WLAN eintragen. Die lokale Datei `wifi_secrets.h` wird von Git ignoriert.
Nach dem ersten Start liegen die Zugangsdaten dauerhaft im NVS-Flash.

## BLE-Dialog

Das Modul meldet sich als `ESP32-CAM-Setup` und stellt einen Nordic-UART-
kompatiblen BLE-Dienst bereit. Jeder Befehl wird mit einem Zeilenumbruch
abgeschlossen.

```text
HILFE
STATUS
WLAN LISTE
WLAN HINZUFUEGEN <SSID>|<PASSWORT>
WLAN LOESCHEN <SSID>
WLAN VERBINDEN
```

Bis zu acht WLAN-Zugänge können gespeichert werden. Kennwörter werden im
Dialog nicht angezeigt. Der NVS-Speicher ist dauerhaft, aber nicht
verschlüsselt.
