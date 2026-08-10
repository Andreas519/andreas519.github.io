# Änderungsprotokoll

## Vorgemerkt für die nächste Version

- Einsatz im Schulnetz mit der Subnetzmaske `255.255.0.0` (`/16`) praktisch
  prüfen. Im Station-Modus soll das Modul IP-Adresse, Subnetzmaske und Gateway
  per DHCP übernehmen.
- Verbindung mit dem offenen WLAN `mrge-ap-bu46` aus dem Computerkabinett
  testen; für dieses WLAN wird ein leerer Passwortwert gespeichert.
- Subnetzmaske und Gateway auf `/system` sowie unter `/device-info` anzeigen,
  damit die Netzwerkkonfiguration im Schulnetz kontrolliert werden kann.
- Die `/16`-Maske des Schulnetzes von der weiterhin separat konfigurierten
  Maske des eigenen ESP32-CAM-Access-Points unterscheiden.

## 0.9.3 – 2026-08-08

- Die drei Betriebsarten über unterscheidbare LED-Signale anzeigen:
  einmaliges kurzes Leuchten im Station-Modus, Doppelblinken im
  Access-Point-Modus und ein schwacher 20-ms-Impuls mit 2000 ms Pause im
  BLE-Notbetrieb.
- Eine verlorene WLAN-Verbindung 30 Sekunden lang wiederherzustellen versuchen
  und danach neu starten, damit der Access-Point-Fallback greift.
- Die Status-LED-Helligkeit nach dem praktischen BLE-Test von PWM 24 auf PWM 2
  reduzieren.
- BLE-Start über GPIO 13, BLE-Dialog, gespeicherte AP-IP `192.168.41.1` und
  anschließende Rückkehr in den Station-Modus praktisch bestätigen.
- Geplante Tests als Frontkamera eines RoboCars und als Kamera über der
  Arbeitsplatte eines Dobot Magician dokumentieren.
- Version 0.9.3 erfolgreich kompiliert und über COM6 mit 115200 Baud
  übertragen; Flash-Hash vollständig verifiziert.

## 0.9.1 – 2026-08-07

- Programmversion, Betriebsart, Gerätename, WLAN und IP-Adresse unter
  `/device-info` als JSON bereitstellen.
- Systemübersicht unter `/system` ergänzen.
- Station-, Access-Point- und BLE-Modus über Schaltflächen auswählen.
- Neue POST-Endpunkte `/station-mode` und `/ap-mode` ergänzen.
- Betriebsart nur für den unmittelbar folgenden Neustart im NVS vormerken.
- Version 0.9.1 erfolgreich kompiliert, mit 115200 Baud übertragen und
  Geräteinfo sowie Systemseite im Station-Modus praktisch geprüft.

## 0.9.2 – 2026-08-07

- Direkten Wechsel vom BLE- in den Access-Point-Modus über `MODUS AP`
  ermöglichen.
- Optionale private AP-IP als Befehlsparameter unterstützen und dauerhaft im
  NVS speichern.
- Private IPv4-Bereiche und Hostnummern von 1 bis 254 validieren.
- Gespeicherte AP-IP in BLE-Status und Systemseite anzeigen.
- Windows-BLE-Dialog um AP-IP-Feld und AP-Neustart-Schaltfläche erweitern.
- AP-Kennung aus den letzten drei MAC-Bytes ableiten, sodass das getestete
  Modul künftig `ESP32-CAM-Setup-9A3060` verwendet.
- BLE-zu-AP-Wechsel mit `192.168.41.1` sowie anschließende Rückkehr zum
  Station-Modus praktisch geprüft.
- Korrigierten AP-Namen `ESP32-CAM-Setup-9A3060`, WPA2-Verbindung,
  `/device-info` unter `192.168.41.1` und den vollständigen Zyklus
  Station → Access Point → Station praktisch bestätigt.

## 0.9.0 – 2026-08-07

- Bei nicht erreichbarem bekanntem WLAN automatisch einen eigenen Access Point
  `ESP32-CAM-Setup-XXXXXX` starten.
- Kamera-Webserver und alle bekannten HTTP-Zugriffe auch im Access-Point-Modus
  unter `http://192.168.4.1/` bereitstellen.
- WLANs unter `/wifi-settings` suchen, speichern, aktualisieren, auswählen und
  löschen.
- Nach der WLAN-Auswahl neu starten und bei einem Verbindungsfehler erneut in
  den Access-Point-Modus zurückfallen.
- BLE nur noch per GPIO 13 oder `POST /ble-mode` als Notzugang aktivieren.
- Access Point mit dem Passwort `esp32cam` schützen und über eine gerätespezifische
  Endung im WLAN-Namen unterscheidbar machen.
- Firmware mit 115200 Baud erfolgreich auf das ESP32-CAM-Modul übertragen.
- Station-Modus, Zeitsynchronisierung, Kamera-Webserver, MJPEG-Livebild,
  Einzelaufnahme, zeitgesteuertes Foto und WLAN-Webseite praktisch geprüft.
- Praktische Tests des Access-Point- und BLE-Modus stehen noch aus.

## 0.8.1 – 2026-08-05

- Wechsel vom Webserver-Modus in den BLE-Konfigurationsmodus über
  `POST /ble-mode` ermöglichen.
- BLE-Modus vor dem Neustart im NVS vormerken und beim Start einmalig
  aktivieren.
- HTTP-Anfrage vor dem Neustart als JSON bestätigen.

## 0.8.0 – 2026-08-05

- Neue Einzelaufnahme über den PC-Endpunkt `/photo-capture` bereitstellen.
- Windows-Programm zum Anfordern, Anzeigen und Speichern eines Fotos ergänzen.
- Den gesuchten BLE-Modulnamen im Windows-Dialog bearbeitbar machen.
- Erfolgreich gefundene BLE-Modulnamen dauerhaft als Auswahlliste speichern.

## 0.7.1 – 2026-08-05

- Das ausgewählte WLAN vor dem Verlassen des BLE-Modus vormerken.
- Vor dem WLAN-Verbindungsversuch neu starten, damit BLE und WLAN nicht
  gleichzeitig um den knappen internen Speicher konkurrieren.
- Bei einer fehlgeschlagenen WLAN-Verbindung automatisch wieder den BLE-Modus
  bereitstellen.

## 0.7.0 – 2026-08-05

- Das im Windows-Dialog ausgewählte gespeicherte WLAN gezielt verbinden.
- Alle im Flash gespeicherten WLAN-Namen beim Start seriell ausgeben.
- Gespeicherte WLANs im Windows-Dialog automatisch als Auswahlliste laden.
- Eine erneute BLE-Verbindung ohne Neustart des Windows-Dialogs ermöglichen.

## Vorgemerkt für 0.6.1

- Helligkeit der Blitz-LED im BLE-Modus deutlich reduzieren.
- Kurze AN-Zeit und niedrigeren PWM-Wert praktisch vergleichen.

## 0.6.0 – 2026-08-05

- Nach Einführung dieser Version einmalig automatisch im BLE-Modus starten.
- Erststart erst nach erfolgreichem `WLAN VERBINDEN` als abgeschlossen speichern.
- Blitz-LED im BLE-Konfigurationsmodus schwach blinken lassen.
- GPIO 13 weiterhin als manuellen Zugang zum BLE-Modus unterstützen.

## 0.5.0 – 2026-08-04

- Gespeicherte WLAN-Namen statt ihrer Anzahl beim Start ausgeben.
- Browserseite `/photo-settings` für Auflösung und Aufnahmeintervall ergänzen.
- Letztes zeitgesteuertes Foto unter `/scheduled-photo` bereitstellen.
- Fotoeinstellungen dauerhaft im NVS-Flash speichern.
- Systemzeit beim Start und anschließend alle sechs Stunden über einen
  externen Zeitdienst aktualisieren.
- Deutsche Winter- und Sommerzeit für Anzeige und Dateinamen berücksichtigen.
- Kamera-Webserver und BLE-Konfiguration in getrennten, über GPIO 13
  auswählbaren Betriebsarten stabil betreiben.
- Videostream und Steuerung gemeinsam auf Port 80 bereitstellen.

## 0.4.0 – 2026-08-04

- Mehrere lokale Start-WLANs in `wifi_secrets.h` unterstützen.
- Noch nicht im NVS vorhandene lokale WLANs bei jedem Start sicher ergänzen.
- Bereits gespeicherte WLAN-Zugänge und Passwörter nicht überschreiben.
- Offene WLANs durch ein leeres Passwort unterstützen.

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
