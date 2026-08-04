# Änderungsprotokoll

## 0.3.0 – 2026-08-04

- Bis zu acht WLAN-Zugänge dauerhaft im NVS-Flash speichern.
- Automatisch das stärkste bekannte WLAN auswählen.
- WLAN-Zugänge über einen BLE-UART-Dialog verwalten.
- BLE-Gerätename `ESP32-CAM-Setup` verwenden.
- WLAN-Kennwörter nicht mehr über die serielle Schnittstelle ausgeben.
- Lokale WLAN-Startdaten aus der Versionsverwaltung ausschließen.
- Tastereingang an GPIO 13 beibehalten.

## Frühere Entwicklungsstände

- **0.2.0:** Tastereingang von GPIO 16 auf GPIO 13 verlegt.
- **0.1.0:** CameraWebServer für das AI-Thinker ESP32-CAM eingerichtet.

Die Stände 0.1.0 und 0.2.0 wurden vor Einführung der lokalen
Versionsverwaltung erstellt und sind daher nur dokumentiert, nicht als
separate Git-Commits vorhanden.
