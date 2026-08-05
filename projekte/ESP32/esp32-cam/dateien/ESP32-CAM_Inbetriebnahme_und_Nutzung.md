# ESP32-CAM-Modul – Inbetriebnahme und Nutzung

## 1. Ziel

Diese Anleitung beschreibt die Inbetriebnahme eines ESP32-CAM-Moduls mit
OV2640-Kamera und einem ESP32-CAM-MB-Programmieradapter. Als erstes Projekt wird
der in der Arduino IDE enthaltene Kamerawebserver verwendet.

Nach erfolgreicher Einrichtung stellt das Modul über WLAN eine Webseite bereit.
Darüber können ein einzelnes Kamerabild und ein fortlaufender Videostream
angezeigt und verschiedene Kameraeinstellungen verändert werden.

Die beschriebene Kombination wurde praktisch erfolgreich getestet.

---

## 2. Verwendete Hardware

- ESP32-CAM-Modul
- OV2640-Kameramodul
- ESP32-CAM-MB-Programmieradapter mit CH340-Chip
- Micro-USB-Datenkabel
- Windows-PC
- WLAN mit 2,4 GHz

> **Wichtig:** Ein reines USB-Ladekabel reicht nicht aus. Das Kabel muss auch
> Daten übertragen können.

### Bestandteile des ESP32-CAM-Moduls

- ESP32-Mikrocontroller mit WLAN und Bluetooth
- Anschluss für das Kameramodul
- OV2640-Kamera, üblicherweise mit 2 Megapixeln
- helle Blitz-LED an GPIO 4
- Steckplatz für eine microSD-Karte
- kein eigener USB-Anschluss

Der ESP32-CAM-MB-Adapter ergänzt den fehlenden USB-Anschluss und übernimmt die
serielle Verbindung zum Computer.

---

## 3. Modul und Programmieradapter zusammensetzen

Das ESP32-CAM-Modul wird in die beiden Buchsenleisten des
ESP32-CAM-MB-Programmieradapters gesteckt.

Dabei gilt:

- Die Kamera zeigt nach oben.
- Das Kameraende liegt dem Micro-USB-Anschluss gegenüber.
- Beide Stiftleisten müssen gerade und vollständig in den Buchsen sitzen.
- Das Modul darf nicht seitlich versetzt eingesteckt werden.
- Das USB-Kabel wird erst nach der Kontrolle des Aufbaus angeschlossen.

Vereinfachte Anordnung:

```text
        Kameramodul
             ↓
         ESP32-CAM
             ↓
   ESP32-CAM-MB-Adapter
             ↓
       Micro-USB-Kabel
```

Der Adapter besitzt gewöhnlich zwei Tasten:

- `IO0`: versetzt den ESP32 in den Programmiermodus
- `RST`: startet den ESP32 neu

---

## 4. Arduino IDE vorbereiten

### 4.1 ESP32-Paket kontrollieren

In der Arduino IDE wird der Boardverwalter geöffnet:

```text
Werkzeuge → Board → Boardverwalter
```

Nach `esp32` suchen und das Paket **esp32 von Espressif Systems** installieren.
Ist es bereits vorhanden, muss es für den ersten Test nicht zwangsläufig
aktualisiert werden. Eine funktionierende Umgebung sollte nicht ohne Grund
verändert werden.

### 4.2 Board auswählen

```text
Werkzeuge → Board → esp32 → AI Thinker ESP32-CAM
```

Dieses Boardprofil enthält die passende Pinbelegung für das verwendete
ESP32-CAM-Modul.

### 4.3 Seriellen Port auswählen

Nach dem Verbinden des Programmieradapters erscheint unter Windows ein
COM-Anschluss:

```text
Werkzeuge → Port → COM6
```

Im erfolgreichen Test wurde `COM6` verwendet. Auf einem anderen Computer kann
die Nummer abweichen.

Falls kein Port erscheint:

1. ein anderes Micro-USB-Datenkabel testen,
2. einen anderen USB-Anschluss verwenden,
3. den Windows-Geräte-Manager öffnen,
4. unter **Anschlüsse (COM & LPT)** nach einem CH340-Gerät suchen,
5. gegebenenfalls den CH340-Treiber installieren.

---

## 5. Beispielprogramm `CameraWebServer` öffnen

Das Beispiel ist in der Arduino IDE zu finden:

```text
Datei → Beispiele → ESP32 → Camera → CameraWebServer
```

Je nach Version des ESP32-Pakets besteht das Beispiel aus mehreren Dateien bzw.
Reitern.

Wichtige Dateien:

- `CameraWebServer.ino`: Hauptprogramm und WLAN-Zugangsdaten
- `board_config.h`: Auswahl des Kameramodells bei neueren Versionen
- `camera_pins.h`: Pinbelegungen der unterstützten Kameraplatinen
- weitere Dateien für den Webserver und die Benutzeroberfläche

Bei älteren Versionen kann die Auswahl des Kameramodells direkt in
`CameraWebServer.ino` stehen.

---

## 6. Kameramodell einstellen

Für das verwendete Modul muss genau diese Definition aktiv sein:

```cpp
#define CAMERA_MODEL_AI_THINKER
```

Alle anderen Kameramodelle müssen mit `//` auskommentiert sein:

```cpp
//#define CAMERA_MODEL_ESP_EYE
//#define CAMERA_MODEL_M5STACK_PSRAM
#define CAMERA_MODEL_AI_THINKER
```

Es darf nur **ein** Kameramodell gleichzeitig aktiviert sein.

---

## 7. WLAN-Zugangsdaten eintragen

In `CameraWebServer.ino` stehen die folgenden Zeilen:

```cpp
const char *ssid = "**********";
const char *password = "**********";
```

Die Platzhalter werden durch die eigenen WLAN-Daten ersetzt:

```cpp
const char *ssid = "Name_des_WLANs";
const char *password = "WLAN-Passwort";
```

Hinweise:

- Das klassische ESP32-CAM-Modul unterstützt WLAN mit **2,4 GHz**.
- Groß- und Kleinschreibung müssen stimmen.
- Leerzeichen im WLAN-Namen sind erlaubt.
- WLAN-Passwörter gehören nicht in öffentlich zugängliche Dokumentationen oder
  GitHub-Repositories.

---

## 8. Programm hochladen

Vor dem Hochladen noch einmal kontrollieren:

```text
Board: AI Thinker ESP32-CAM
Port:  COM6 bzw. der aktuell erkannte COM-Port
```

Danach in der Arduino IDE auf **Hochladen** klicken.

Beim Hochladen kompiliert die Arduino IDE das Programm automatisch. Ein
vorheriges separates Kompilieren ist nicht erforderlich.

### Falls die Verbindung bei `Connecting...` stehen bleibt

1. Taste `IO0` gedrückt halten.
2. Taste `RST` kurz drücken.
3. Taste `IO0` loslassen.
4. Den Hochladevorgang gegebenenfalls erneut starten.

Eine erfolgreiche Übertragung endet typischerweise mit einer Meldung wie:

```text
Leaving...
Hard resetting via RTS pin...
```

Je nach Programmieradapter kann der Wechsel in den Programmiermodus automatisch
erfolgen.

---

## 9. Kameraserver starten

Nach dem Hochladen:

1. seriellen Monitor der Arduino IDE öffnen,
2. `115200 Baud` einstellen,
3. gegebenenfalls die Taste `RST` kurz drücken.

Im seriellen Monitor erscheinen Startmeldungen und nach erfolgreicher
WLAN-Verbindung eine IP-Adresse:

```text
WiFi connected
Camera Ready!
Use 'http://192.168.x.x' to connect
```

Die angezeigte Adresse wird in einem Browser geöffnet:

```text
http://192.168.x.x
```

Computer bzw. Mobilgerät und ESP32-CAM müssen sich dabei normalerweise im
gleichen lokalen Netzwerk befinden.

---

## 10. Webseite und Kamerabild verwenden

Die Webseite bietet – abhängig von der installierten Beispielversion – unter
anderem:

- Einzelbild aufnehmen
- Videostream starten und anhalten
- Auflösung auswählen
- Bildqualität verändern
- Helligkeit, Kontrast und Sättigung einstellen
- Bild spiegeln oder vertikal drehen
- automatische Belichtung und Weißabgleich beeinflussen
- Blitz-LED schalten

Für die ersten Tests empfiehlt sich eine kleinere Auflösung. Sie benötigt
weniger Speicher und führt meist zu einem flüssigeren Stream.

Die konkret verfügbaren Schalter hängen von der verwendeten Version des
`CameraWebServer`-Beispiels ab.

---

## 11. Blitz-LED

Die helle LED neben dem Kameraanschluss ist beim verbreiteten
AI-Thinker-kompatiblen ESP32-CAM-Modul mit **GPIO 4** verbunden.

Ein einfacher Blinktest:

```cpp
const int LED = 4;

void setup() {
    pinMode(LED, OUTPUT);
}

void loop() {
    digitalWrite(LED, HIGH);
    delay(500);
    digitalWrite(LED, LOW);
    delay(500);
}
```

> **Achtung:** GPIO 4 wird auch von der microSD-Schnittstelle verwendet. Beim
> gleichzeitigen Einsatz der Blitz-LED und einer microSD-Karte kann deshalb ein
> Konflikt entstehen.

Die kleine Betriebsanzeige ist nicht mit der frei programmierbaren Blitz-LED zu
verwechseln. `LED_BUILTIN` zeigt bei unterschiedlichen ESP32-Platinen nicht
immer auf denselben GPIO.

---

## 12. Häufige Fehler und Ursachen

### Kein COM-Port sichtbar

Mögliche Ursachen:

- USB-Kabel kann nur laden,
- CH340-Treiber fehlt,
- USB-Anschluss oder Kabel ist fehlerhaft,
- Modul bzw. Adapter ist nicht richtig eingesteckt.

### Hochladen bleibt bei `Connecting...` stehen

Der ESP32 befindet sich nicht im Programmiermodus. Die Tastenfolge mit `IO0`
und `RST` aus Abschnitt 8 verwenden.

### `Camera probe failed`

Mögliche Ursachen:

- falsches Kameramodell im Programm aktiviert,
- Kameraflachbandkabel locker oder verdreht,
- Kamera bei eingeschalteter Versorgung umgesteckt,
- unzureichende Stromversorgung,
- defektes Kameramodul.

Zuerst prüfen:

```cpp
#define CAMERA_MODEL_AI_THINKER
```

### Ständige Neustarts oder `Brownout detector was triggered`

Die Versorgungsspannung bricht ein.

Mögliche Abhilfen:

- kurzes, hochwertiges USB-Kabel verwenden,
- anderen USB-Anschluss testen,
- stabile 5-V-Versorgung einsetzen,
- nicht aus einem schwachen 3,3-V-Ausgang versorgen.

### WLAN-Verbindung gelingt nicht

Prüfen:

- WLAN-Name und Passwort,
- Groß- und Kleinschreibung,
- Verfügbarkeit eines 2,4-GHz-WLANs,
- ausreichende Entfernung zum Router,
- Sonderzeichen im Passwort.

### Webseite ist erreichbar, aber der Stream startet nicht

Mögliche Maßnahmen:

- kleinere Auflösung auswählen,
- Webseite neu laden,
- nur einen Stream gleichzeitig öffnen,
- ESP32 mit `RST` neu starten,
- Stromversorgung prüfen.

### Die Arduino IDE startet scheinbar nicht

Unter Windows kann eine Firewall-Abfrage für `mdns-discovery.exe` im Hintergrund
auf eine Antwort warten. Für ein vertrauenswürdiges Heim- oder Schulnetz genügt:

```text
Private Netzwerke:    zulassen
Öffentliche Netzwerke: nicht zulassen
```

`mdns-discovery.exe` dient der Erkennung von Geräten im lokalen Netzwerk. Für
das reine Hochladen über einen COM-Port ist diese Freigabe nicht zwingend
erforderlich.

---

## 13. Sicherheit und sorgfältiger Umgang

- Kamera oder Flachbandkabel nur bei ausgeschalteter Versorgung umstecken.
- Platinen nicht auf leitende Metallflächen legen.
- WLAN-Passwort nicht veröffentlichen.
- Den Kameraserver nicht ohne zusätzliche Sicherheitsmaßnahmen aus dem Internet
  erreichbar machen.
- Die Kamera nur dort einsetzen, wo keine Persönlichkeits- oder
  Datenschutzrechte verletzt werden.
- Vor längerer unbeaufsichtigter Nutzung für eine zuverlässige Stromversorgung
  und eine sichere mechanische Befestigung sorgen.

---

## 14. Möglichkeiten für weitere Projekte

Nach der erfolgreichen Inbetriebnahme kann die ESP32-CAM beispielsweise
verwendet werden für:

- Überwachung eines 3D-Druckers,
- Aufnahme einzelner Bilder in festen Zeitabständen,
- Bewegungserkennung,
- Dokumentation technischer Versuche,
- Beobachtung eines Roboters oder einer Modellanlage,
- Übertragung des Kamerabildes an ein Python-Programm,
- Auswertung des Bildes mit OpenCV auf einem PC oder Raspberry Pi,
- einfache Erkennung von Farben, Formen oder Markierungen.

Die ESP32-CAM eignet sich gut als kompakte WLAN-Kamera. Aufwendige
Bildverarbeitung wird jedoch meist besser auf einem leistungsfähigeren Computer
ausgeführt. Dabei liefert die ESP32-CAM nur die Bilder, während beispielsweise
ein Raspberry Pi oder PC die eigentliche OpenCV-Auswertung übernimmt.

---

## 15. Erfolgreich getesteter Zustand

Bei der beschriebenen Inbetriebnahme wurde folgender Zustand erreicht:

- ESP32-CAM korrekt auf ESP32-CAM-MB gesteckt,
- OV2640-Kamera erkannt,
- Programmieradapter unter Windows als `COM6` erkannt,
- Boardprofil `AI Thinker ESP32-CAM` verwendet,
- Beispiel `CameraWebServer` erfolgreich übertragen,
- ESP32-CAM mit dem 2,4-GHz-WLAN verbunden,
- Webseite im Browser geöffnet,
- Kamerabild und Videostream erfolgreich angezeigt.

Damit sind Hardware, USB-Verbindung, Programmübertragung, WLAN und Kamera
funktionsfähig.
