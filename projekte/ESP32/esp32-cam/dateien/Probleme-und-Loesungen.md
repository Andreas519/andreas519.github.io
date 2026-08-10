# ESP32-CAM: Probleme und Lösungen bei der Projektentwicklung

Diese Dokumentation beschreibt wichtige Probleme, die während der Entwicklung
des Projektes bis zur Version 0.8.0 aufgetreten sind. Zu jedem Problem werden
die Ursache und die umgesetzte beziehungsweise vorgesehene Lösung genannt.

## 1. Zu wenige frei verfügbare Anschlüsse

### Problem

Für einen Taster wurde ein freier GPIO benötigt. Viele Anschlüsse des
ESP32-CAM sind bereits durch Kamera und SD-Kartenschnittstelle belegt.

### Lösung

Da die SD-Karte vorerst nicht verwendet wird, konnte GPIO 13 für den Taster
genutzt werden. Der Taster schaltet beim Neustart in den BLE-Konfigurationsmodus.

## 2. BLE, WLAN und Kamera benötigen gemeinsam zu viel Speicher

### Problem

Der gleichzeitige Betrieb von Bluetooth LE, WLAN, Kamera und Webserver führte
wegen des knappen internen Arbeitsspeichers des ESP32-CAM zu instabilem
Verhalten.

### Lösung

Das Programm verwendet getrennte Betriebsarten:

- BLE-Modus zum Verwalten der WLAN-Zugänge
- WLAN-Modus für Kamera, Webserver und Fotoübertragung

Zwischen beiden Betriebsarten wird das Modul neu gestartet. Dadurch müssen BLE
und Kamera-Webserver nicht gleichzeitig im Speicher liegen.

## 3. Konfiguration ohne Zugriff auf den eingebauten Taster

### Problem

Das Modul befindet sich in einem Gehäuse. Der Taster ist deshalb nicht immer
leicht erreichbar.

### Lösung

Findet Version 0.9.0 kein bekanntes WLAN, startet sie automatisch den eigenen
Access Point `ESP32-CAM-Setup-XXXXXX`. Kamera und WLAN-Konfiguration sind dann
unter `http://192.168.4.1/` erreichbar. GPIO 13 bleibt als manueller Zugang zum
BLE-Notbetrieb erhalten.

## 4. Die Blitz-LED ist im BLE-Modus zu hell

### Problem

Die weiße Blitz-LED zeigt den BLE-Modus durch Blinken an, ist dabei aber selbst
mit reduziertem PWM-Wert noch sehr hell.

### Vorgesehene Lösung

Für eine spätere Version sind ein niedrigerer PWM-Wert und eine deutlich
kürzere Einschaltzeit vorgesehen. Die endgültigen Werte müssen praktisch am
eingebauten Modul verglichen werden.

## 5. BLE-Apps sind für Textdialoge umständlich

### Problem

Apps wie LightBlue oder nRF Connect zeigen einzelne Characteristics und
BLE-Pakete an. Befehle mussten teilweise zusammen mit dem Zeilenende `0A`
manuell gesendet werden. Antworten erschienen außerdem in mehrere Pakete
zerlegt.

### Lösung

Der eigene Windows-Dialog `esp32_cam_ble_dialog.py` übernimmt:

- Suche nach dem ESP32-CAM-Modul
- Verbindung mit dem Nordic-UART-Dienst
- automatisches Anhängen des Zeilenendes
- Zusammensetzen aufgeteilter Antworten
- Schaltflächen für die wichtigsten WLAN-Befehle
- verdeckte Anzeige von WLAN-Passwörtern

## 6. Erneute BLE-Verbindung erforderte einen Programmneustart

### Problem

Nach einer Trennung konnte der Windows-Dialog das Modul zunächst erst wieder
finden, nachdem das Dialogprogramm geschlossen und neu gestartet worden war.

### Lösung

Beim Trennen wird das alte BLE-Clientobjekt vollständig verworfen. Eine neue
Suche erstellt anschließend eine frische Verbindung, ohne dass das
Windows-Programm neu gestartet werden muss.

## 7. Unterschiedliche Namen mehrerer ESP32-CAM-Module

### Problem

Der ursprünglich fest eingebaute Gerätename `ESP32-CAM-Setup` eignete sich
nicht für mehrere Module mit unterschiedlichen Namen.

### Lösung

Der Modulname ist im Windows-Dialog bearbeitbar. Erfolgreich gefundene Namen
werden dauerhaft gespeichert und stehen beim nächsten Start in einer
Auswahlliste bereit.

## 8. Gespeicherte WLANs wurden unvollständig ausgegeben

### Problem

Die serielle Startmeldung zeigte zeitweise nur die WLANs aus
`wifi_secrets.h`, nicht aber alle zusätzlich im Flash gespeicherten Zugänge.

### Lösung

Nach dem Laden des Flash-Speichers wird die vollständige interne WLAN-Liste
ausgegeben. Passwörter erscheinen weder im seriellen Monitor noch in der
WLAN-Liste des Dialogprogramms.

## 9. Das leistungsstärkste WLAN war nicht immer das gewünschte WLAN

### Problem

Das Modul wählte ursprünglich automatisch das gespeicherte WLAN mit dem
stärksten Signal. Der Benutzer konnte nicht festlegen, welches WLAN nach der
Konfiguration verwendet werden sollte.

### Lösung

Der Windows-Dialog lädt alle gespeicherten WLAN-Namen in ein Auswahlfeld. Der
Befehl `WLAN VERBINDEN <SSID>` übergibt das ausdrücklich ausgewählte WLAN an
das Modul.

## 10. BLE brach während des WLAN-Verbindungsversuchs ab

### Problem

Version 0.7.0 versuchte, das ausgewählte WLAN noch während der aktiven
BLE-Verbindung aufzubauen. Dabei wurde BLE getrennt, bevor das Ergebnis an den
PC gesendet werden konnte. Das Modul blieb anschließend im blinkenden
Konfigurationsmodus.

### Lösung

Seit Version 0.7.1 wird die ausgewählte SSID zunächst im Flash vorgemerkt.
Danach wird das Modul neu gestartet. Erst nach dem Neustart beginnt der
WLAN-Verbindungsversuch ohne aktives BLE. Schlägt er fehl, stellt das Modul den
BLE-Modus wieder bereit.

## 11. WLAN-Passwörter müssen aktualisiert werden können

### Problem

Im Dialog wird ein gespeichertes Passwort aus Sicherheitsgründen nicht
angezeigt. Dadurch war nicht sofort erkennbar, ob ein leeres oder falsches
Passwort hinterlegt war.

### Lösung

Wird eine bereits vorhandene SSID erneut mit `WLAN speichern` übertragen,
überschreibt das neue Passwort den alten Eintrag. Die Anzeige verwendet dabei
nur `********`; das tatsächliche Passwort wird nicht im Dialogprotokoll
ausgegeben.

## 12. Fotos sollen ohne SD-Karte bereitgestellt werden

### Problem

Das Projekt soll vorerst keine SD-Karte verwenden. Eine dauerhafte Sammlung
vieler Bilder im internen Flash wäre wegen Speicherplatz und Verschleiß
ebenfalls ungeeignet.

### Lösung

Zeitgesteuerte Aufnahmen halten nur das jeweils letzte Bild im Arbeitsspeicher.
Die nächste Aufnahme ersetzt das vorherige Bild. Manuell angeforderte Bilder
werden direkt an den PC übertragen und dort gespeichert.

## 13. Fotoabruf und lokale Speicherung auf dem PC

### Problem

Für den automatisierten Einsatz wurde ein einfaches PC-Programm benötigt, das
nicht die vollständige Browser-Kamerasteuerung voraussetzt.

### Lösung

Version 0.8.0 stellt den Endpunkt `/photo-capture` bereit. Der
`WindowsPhotoClient` kann:

- eine neue Aufnahme anfordern
- das empfangene JPEG prüfen
- das Bild direkt anzeigen
- die Datei mit Datums- und Zeitstempel lokal speichern
- erfolgreich verwendete Moduladressen dauerhaft merken

Der praktische Test übertrug erfolgreich ein JPEG mit 640 × 480 Pixeln.

## 14. Systemzeit und aussagekräftige Dateinamen

### Problem

Nach einem Neustart besitzt der ESP32-CAM zunächst keine zuverlässige Uhrzeit.
Ohne Systemzeit können Fotos nicht eindeutig benannt werden.

### Lösung

Nach der WLAN-Verbindung wird die Uhrzeit über einen externen Zeitdienst
aktualisiert und anschließend regelmäßig nachgeführt. Winter- und Sommerzeit
werden berücksichtigt. Fotodateien erhalten dadurch einen Datums- und
Zeitstempel.

## 15. Serielle Schnittstelle beim Übertragen blockiert

### Problem

War der serielle Monitor geöffnet, konnte das Übertragungsprogramm COM6 nicht
verwenden und meldete `Access denied` beziehungsweise einen belegten Anschluss.

### Lösung

Vor dem Flashen wird der serielle Monitor geschlossen. Nach abgeschlossener
Übertragung kann er wieder mit 115200 Baud geöffnet werden.

## 16. Unzuverlässige Übertragung mit hoher Baudrate

### Problem

Der CH340-Adapter verlor beim Umschalten auf 460800 Baud die Verbindung zum
ESP32. Das Schreiben begann dadurch nicht zuverlässig.

### Lösung

Die Firmware wird mit 115200 Baud übertragen. Das dauert länger, arbeitete bei
den folgenden Versionen aber stabil. Die geschriebenen Bereiche werden danach
durch Prüfsummen verifiziert.

## 17. Zu wenig Arbeitsspeicher beim Kompilieren auf dem PC

### Problem

Mehrere parallele Compilerprozesse konnten auf dem Windows-PC nicht genügend
Arbeitsspeicher reservieren. Der Build endete mit `out of memory`.

### Lösung

Die Arduino-Kompilierung wird bei Bedarf mit nur einem Auftrag ausgeführt:

```powershell
arduino-cli compile --clean --jobs 1 --fqbn esp32:esp32:esp32cam CameraWebServer
```

Der speicherschonende Build dauert länger, kompiliert das Projekt aber
zuverlässig.

## 18. Private WLAN-Daten dürfen nicht veröffentlicht werden

### Problem

`wifi_secrets.h` enthält persönliche WLAN-Namen und Passwörter. Diese Daten
dürfen weder in Git noch in einem Download-Archiv landen.

### Lösung

Die Datei wird durch `.gitignore` ausgeschlossen. Veröffentlichte ZIP-Dateien
enthalten nur `wifi_secrets.example.h` als ausfüllbare Vorlage. Der ZIP-Inhalt
wird vor der Bereitstellung ausdrücklich auf das Fehlen von
`wifi_secrets.h` geprüft.

## 19. Das Modul ist in einer unbekannten WLAN-Umgebung nicht erreichbar

### Problem

Keines der gespeicherten WLANs ist erreichbar. Eine Konfiguration nur über BLE
setzt ein geeignetes Programm voraus und ist deshalb als normaler Zugangsweg
zu umständlich.

### Lösung

Version 0.9.0 startet nach den fehlgeschlagenen WLAN-Versuchen automatisch
einen passwortgeschützten Access Point. Der vorhandene Kamera-Webserver läuft
auch dort. Unter `/wifi-settings` lassen sich WLANs suchen, speichern und
löschen. Nach einer neuen Auswahl startet das Modul neu; schlägt auch diese
Verbindung fehl, kehrt es wieder zum Access Point zurück. BLE wird nur noch
gezielt per GPIO 13 oder HTTP-Anforderung aktiviert.

### Teststand

Die Firmware wurde kompiliert und auf das ESP32-CAM-Modul übertragen. Der
Station-Modus mit Kamera, Livebild, Foto-Endpunkten und WLAN-Webseite ist
praktisch bestätigt. Access-Point- und BLE-Modus stehen noch aus.

## Ergebnis

Mit Version 0.9.0 sind folgende Abläufe implementiert:

1. Ein bekanntes WLAN automatisch verwenden.
2. Ohne bekanntes WLAN einen eigenen Access Point bereitstellen.
3. Kamera und WLAN-Konfiguration in diesem Access Point gemeinsam betreiben.
4. WLAN-Zugänge im Browser verwalten.
5. BLE getrennt als Notbetrieb starten.
6. Zeitgesteuerte Fotos und Einzelbilder weiterhin bereitstellen.
