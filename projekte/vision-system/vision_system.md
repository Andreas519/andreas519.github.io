# Vision-System

## Projektbeschreibung

**Vision-System** ist ein praxisorientiertes Projekt zur Entwicklung eines modularen Kamera- und Bildverarbeitungssystems für Unterricht, Robotik und Automatisierung. Dokumentiert wird der gesamte Entwicklungsweg – von der Installation des Betriebssystems über die Bildaufnahme und Bildübertragung bis zu OpenCV, künstlicher Intelligenz und der Anbindung an ESP32 und Dobot Magician.

## Inhalt

1. [Einführung](kapitel/01_einfuehrung.md)
2. [Hardware](kapitel/02_hardware.md)
3. [Betriebssystem](kapitel/03_betriebssystem.md)
4. [Kamera](kapitel/04_kamera.md)
5. [Python](kapitel/05_python.md)
6. [OpenCV](kapitel/06_open_cv.md)
7. [Künstliche Intelligenz](kapitel/07_ki.md)
8. [Bildübertragung](kapitel/08_bilduebertragung.md)
9. [Kommunikation](kapitel/09_kommunikation.md)
10. [Projekte](kapitel/10_projekte.md)

## Projektstruktur

```text
vision-system/
├── README.md
├── index.html
├── vision_system.md
├── kapitel/
├── python/
│   └── beispiele/
├── bilder/
├── downloads/
└── dokumentation/
```

## Praktisch bestätigter Stand

```text
Betriebssystem: Raspbian GNU/Linux 13 (Trixie)
Kamera:         OV5647
Max. Auflösung: 2592 × 1944 Pixel
Fernzugriff:    SSH und RDP
Testaufnahme:   erfolgreich mit --nopreview
```

## Nächster Arbeitsschwerpunkt

Kapitel 8 wird zuerst praktisch nachvollzogen. Zunächst holt der Windows-PC ein aufgenommenes Bild per SCP vom Raspberry Pi ab. Anschließend folgen Automatisierung per PowerShell und Python.
