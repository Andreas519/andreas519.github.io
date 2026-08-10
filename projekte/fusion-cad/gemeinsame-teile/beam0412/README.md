# Parametrischer Beam-0412-Generator

Das Fusion-Python-Skript erzeugt ein eigenständiges, Makeblock-kompatibles Referenzmodell der Beam-0412-Baureihe. Voreingestellt ist der `Beam0412-140`.

## Bestätigte Grundmaße

- Querschnitt: 4 × 12 mm
- Gesamtlänge: 140 mm
- Endradius: 6 mm
- neun Durchgangsbohrungen Ø 4,1 mm
- Lochraster: 16 mm
- erste und letzte Lochmitte: jeweils 6 mm vom Stirnende

Diese Werte wurden mit der technischen Zeichnung und der bereitgestellten STEP-Datei abgeglichen. Die STEP-Datei selbst wird nicht benötigt und ist nicht Bestandteil dieses Verzeichnisses.

## Installation und Ausführung

1. Den Ordner `beam0412` auf den iMac übertragen beziehungsweise per Git abrufen.
2. In Autodesk Fusion **Dienstprogramme → Skripte und Add-Ins** öffnen.
3. Über das grüne Plus den Ordner mit `beam0412_generator.py` hinzufügen.
4. `parameter.json` und das Python-Skript im selben Ordner belassen.
5. Das Skript ausführen.

Das Skript verwendet ein vorhandenes Fusion-Design oder legt ein neues Design an. Es erzeugt eine eigene Komponente, einen benannten Körper, Benutzerparameter, das Lochmuster und optional die Längsnuten.

## Praktische Prüfung

Getestet am 9. August 2026 mit Autodesk Fusion 2704.1.36 unter macOS 26.5 (25F71) auf einem iMac21,1.

- `Beam0412-140`: erfolgreich mit 140 mm Gesamtlänge, neun Bohrungen Ø 4,1 mm, 16 mm Lochraster und beidseitigen Längsnuten erzeugt
- Benutzerparameter: alle neun Werte aus `parameter.json` korrekt in Fusion angelegt
- `Beam0412-060`: erfolgreich mit 60 mm Gesamtlänge und vier Bohrungen erzeugt
- `create_grooves: false`: erfolgreich ohne Längsnuten erzeugt
- ungültige Länge 61 mm: erwartungsgemäß mit einem Hinweis auf das unvollständige Lochraster abgewiesen
- STEP-Export `exports/Beam0412-140.step`: erfolgreich wieder in Fusion geöffnet und mit 128 mm Abstand der äußeren Lochmittelpunkte, Ø 4,1 mm Bohrungsdurchmesser, 12 mm Gesamtbreite und 4 mm Gesamtdicke geprüft

Nach den Tests wurde `parameter.json` wieder auf `Beam0412-140` mit aktivierten Längsnuten zurückgesetzt.

## Varianten erzeugen

In `parameter.json` werden `length` und `component_name` geändert. Eine gültige Länge muss zum Raster passen:

```text
length = 2 × first_hole_offset + (hole_count - 1) × hole_pitch
```

Bei den Standardwerten ergibt sich:

```text
length = 12 + (hole_count - 1) × 16
```

Beispiele:

| Variante | Länge | Lochanzahl |
| --- | ---: | ---: |
| Beam0412-060 | 60 mm | 4 |
| Beam0412-076 | 76 mm | 5 |
| Beam0412-092 | 92 mm | 6 |
| Beam0412-108 | 108 mm | 7 |
| Beam0412-140 | 140 mm | 9 |

## Hinweise zur Geometrie

Der Generator bildet Außenkontur, Lochraster und den funktionalen Nutquerschnitt parametrisch ab. Kleine Radien und herstellungsbedingte Details des stranggepressten Originalprofils sind bewusst nicht nachgebildet. Für reine Einbau- oder Kollisionsmodelle können die Nuten mit `create_grooves: false` deaktiviert werden.

Das Modell ist eine eigenständige Rekonstruktion für Konstruktion und Unterricht, kein offizielles Hersteller-CAD-Modell.
