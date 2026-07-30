# Vision-System

Praxisorientiertes Projekt zur Entwicklung eines modularen Kamera- und Bildverarbeitungssystems für Unterricht, Robotik und Automatisierung.

## Ziele

- Kamera am Raspberry Pi Zero W einrichten und testen
- Bilder in einstellbarer Auflösung aufnehmen
- Bilder zwischen Raspberry Pi und Windows-PC übertragen
- Bilder mit Python und OpenCV auswerten
- später ESP32 und Dobot Magician anbinden

## Einstieg

1. [`vision_system.md`](vision_system.md) – Gesamtdokumentation
2. [`kapitel/08_bilduebertragung.md`](kapitel/08_bilduebertragung.md) – sofort praktisch nutzbares Kapitel
3. [`python/beispiele/bild_aufnehmen.sh`](python/beispiele/bild_aufnehmen.sh) – Testaufnahme auf dem Raspberry Pi
4. [`python/beispiele/bild_holen.ps1`](python/beispiele/bild_holen.ps1) – Bild per SCP auf Windows abholen

## Aktueller Entwicklungsstand

- Raspberry Pi Zero W v1.1 eingerichtet
- Raspberry Pi OS 13 „Trixie“ installiert
- Zugriff per SSH und RDP möglich
- Kamera OV5647 wird erkannt
- Testaufnahme ohne Vorschau erfolgreich
- SCP-Bildübertragung wird praktisch erprobt

Stand: 30. Juli 2026
