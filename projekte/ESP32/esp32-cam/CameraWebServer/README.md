# CameraWebServer

Aktuelle Version: **0.4.0**

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
