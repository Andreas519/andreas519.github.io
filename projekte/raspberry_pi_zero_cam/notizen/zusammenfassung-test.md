🔴 Bitte eine Zusammenfassung zu **„Kamera am Raspberry Pi Zero W“**.

# Kamera am Raspberry Pi Zero W – Zusammenfassung

## Projektziel

Der Raspberry Pi Zero W wird als **intelligentes Kamerasystem** eingesetzt. Er übernimmt die Bildaufnahme, später die Bildverarbeitung mit OpenCV sowie die Kommunikation mit einem Windows-PC, einem ESP32 oder dem Dobot Magician.

---

# Hardware

## Raspberry Pi

* Raspberry Pi Zero W Version 1.1
* WLAN integriert
* Bluetooth integriert
* 40-polige GPIO-Leiste
* Mini-HDMI
* 2 × Micro-USB
* CSI-Kameraanschluss

## Kamera

Verwendet wird eine **AZ-Delivery Kamera V1.3** mit dem Bildsensor

```
OV5647
```

Technische Daten

* 5 Megapixel
* maximale Auflösung 2592 × 1944 Pixel
* Anschluss über das CSI-Flachbandkabel

---

# Betriebssystem

Installiert wurde

```
Raspberry Pi OS
Version 13 (Trixie)
```

Prüfen

```bash
cat /etc/os-release
```

---

# System aktualisieren

Nach der Installation wurde das System aktualisiert.

```bash
sudo apt update
sudo apt upgrade
```

---

# Kamera erkannt

Die Kamera wurde erfolgreich erkannt.

```bash
rpicam-hello --list-cameras
```

Ausgabe

```text
0 : ov5647
```

Damit ist die Hardware korrekt installiert.

---

# Erstes Testbild

Standardbefehl

```bash
rpicam-still -o test.jpg
```

Dieser führte über die RDP-Verbindung zu einem Fehler.

Fehlermeldung

```text
failed to import fd 20
```

Ursache

Die GPU-Vorschau kann innerhalb einer RDP-Sitzung nicht korrekt dargestellt werden.

---

# Lösung

Die Vorschau wird abgeschaltet.

```bash
rpicam-still --nopreview -o test.jpg
```

Danach wurde das Bild erfolgreich aufgenommen.

Ausgabe

```text
Still capture image received
```

Die Datei

```
test.jpg
```

wurde korrekt gespeichert.

---

# Einstellbare Auflösungen

Beispiele

640 × 480

```bash
rpicam-still --nopreview --width 640 --height 480 -o bild.jpg
```

1920 × 1080

```bash
rpicam-still --nopreview --width 1920 --height 1080 -o bild.jpg
```

Maximale Auflösung

```bash
rpicam-still --nopreview --width 2592 --height 1944 -o bild.jpg
```

---

# Fernzugriff

Der Raspberry Pi ist vom Windows-PC erreichbar.

* SSH
* RDP

Damit kann vollständig ohne Monitor, Tastatur und Maus am Raspberry Pi gearbeitet werden.

---

# Bildübertragung

Es wurden drei Möglichkeiten untersucht.

## Variante 1 – Windows holt das Bild (SCP)

Windows kopiert das Bild vom Raspberry Pi.

Beispiel

```powershell
scp pi@raspi-zero:/home/pi/test.jpg D:\Kamera\
```

### Vorteile

* einfach
* sicher
* keine zusätzliche Software
* leicht automatisierbar

**Empfehlung für die erste Projektphase.**

---

## Variante 2 – Raspberry Pi sendet das Bild

Der Raspberry Pi kopiert das Bild selbst zum Windows-PC.

Vorteil

* vollständig automatisch

Nachteil

* Windows benötigt einen SSH-Server.

---

## Variante 3 – Gemeinsame Netzwerkfreigabe

Der Raspberry Pi schreibt die Bilder direkt in einen freigegebenen Windows-Ordner.

Vorteile

* sehr schnell
* ideal für viele Bilder
* auch für Videos geeignet

---

# Geplante Python-Module

```
kamera.py
```

* Kamera steuern
* Auflösung einstellen
* Bild aufnehmen

```
bildtransfer.py
```

* Bilder übertragen
* SCP kapseln

```
bildverarbeitung.py
```

* OpenCV
* Formerkennung
* Farberkennung
* Mittelpunkt berechnen

```
ki.py
```

* TensorFlow Lite
* spätere KI-Anwendungen

---

# Projekt "Vision-System"

Aus den bisherigen Arbeiten entsteht das eigenständige Projekt

```
Vision-System
```

Es soll den kompletten Entwicklungsweg dokumentieren – von der Installation des Raspberry Pi bis zur intelligenten Bildverarbeitung und der Anbindung an Robotiksysteme.

---

# Aktueller Entwicklungsstand

✅ Raspberry Pi Zero W eingerichtet

✅ Raspberry Pi OS 13 installiert

✅ Kamera erfolgreich erkannt

✅ Erstes Testbild aufgenommen

✅ SSH eingerichtet

✅ RDP eingerichtet

✅ Bildübertragung per SCP geplant

✅ Projektstruktur **Vision-System** festgelegt

---

# Nächste Schritte

1. Automatische Bildübertragung per SCP einrichten.
2. Python-Modul `kamera.py` entwickeln.
3. Python-Modul `bildtransfer.py` entwickeln.
4. OpenCV installieren und testen.
5. Erste Formerkennung (Kreis, Rechteck, Dreieck).
6. Kommunikation mit ESP32 und Dobot Magician aufbauen.

---

## Fazit

Die grundlegende Inbetriebnahme der Kamera am Raspberry Pi Zero W ist erfolgreich abgeschlossen. Die Hardware arbeitet zuverlässig, die Kamera wird korrekt erkannt und Testbilder können aufgenommen werden. Mit der festgelegten Projektstruktur **Vision-System** besteht nun eine solide Grundlage für die nächsten Entwicklungsschritte: automatisierte Bildübertragung, Bildverarbeitung mit OpenCV und später der Einsatz von Künstlicher Intelligenz in Verbindung mit Robotik und Mikrocontrollern. 🚀📷🤖
