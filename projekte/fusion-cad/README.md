# Autodesk-Fusion-Konstruktionen

Dieser Bereich bündelt parametrische CAD-Projekte für Autodesk Fusion. Dazu gehören Halterungen, Gehäuse, Adapterplatten und weitere Bauteile für Robotik, Elektronik und 3D-Druck.

## Arbeitsweise

1. Anforderungen, Fotos und Einbauraum erfassen.
2. Maße, Toleranzen und veränderliche Werte in `fusion/parameter.json` festhalten.
3. Das Modell möglichst parametrisch mit einem Python-Skript für die Autodesk-Fusion-API erzeugen.
4. Das Ergebnis in Fusion prüfen und bei Bedarf als native Fusion-Datei sichern.
5. Fertigungsdateien nach `exports/` ausgeben und einen Probedruck anfertigen.
6. Änderungen, Prüfergebnisse und bekannte Abweichungen im Projekt-README dokumentieren.

## Verzeichnisstruktur

- `gemeinsame-teile/`: wiederverwendbare Modelle, Parameter und Exporte
- `vorlagen/`: Vorlage für neue CAD-Projekte und eine Parameterdatei als Beispiel
- `esp32-cam-robocar/`: schwenkbarer Frontkamera-Halter für ein RoboCar
- `esp32-cam-dobot/`: späterer Kamera-Halter über der Arbeitsplatte eines Dobot Magician

Ein einzelnes Projekt verwendet normalerweise:

- `fusion/` für Python-Skripte, Parameter und Hinweise zur Fusion-Datei
- `models/` für weitere Modellquellen und Referenzgeometrie
- `exports/` für STEP, STL und 3MF
- `bilder/` für Fotos, Maßskizzen, Renderings und Probedrucke

## Autodesk Fusion

Die beim Erzeugen oder Prüfen eines Modells verwendete Fusion-Version wird im jeweiligen Projekt-README dokumentiert. API-Skripte sollen ihre Eingabeparameter aus einer gut lesbaren JSON-Datei beziehen und die erzeugten Komponenten eindeutig benennen.

## Git-Regeln für CAD

- Vor Arbeitsbeginn `git pull` ausführen.
- Textquellen, Skripte und Parameter bevorzugen; sie lassen sich gut vergleichen.
- Native Fusion-Dateien nie gleichzeitig auf mehreren Rechnern bearbeiten, da sie nicht sinnvoll zusammengeführt werden können.
- Exporte nur gezielt aktualisieren und mit dem zugehörigen Modellstand committen.
- Große Binärdateien bei Bedarf über Git LFS verwalten.
- Pro Projekt einen klar abgegrenzten Commit erstellen und keine unabhängigen Änderungen einbeziehen.

## Rechnerübergreifende Zusammenarbeit

- **iMac:** Autodesk Fusion ausführen, CAD-Skripte testen, Modelle und Exporte prüfen.
- **Windows-PC:** Elektronik, Firmware, Dokumentation, Parameterpflege und Website bearbeiten.
- **GitHub:** gemeinsame Quelle für den abgestimmten Projektstand.

## Projektübersicht

| Projekt | Ziel | Status |
| --- | --- | --- |
| `esp32-cam-robocar` | Schwenkbarer ESP32-CAM-Halter als Frontkamera | Anforderungen und Maße ausstehend |
| `esp32-cam-dobot` | ESP32-CAM über der Arbeitsplatte eines Dobot Magician | Vorgemerkt |

Die zugehörige [Projektseite](index.html) fasst den Bereich für GitHub Pages zusammen. Ein allgemeiner Themenbereich `themen/fusion-cad/` soll später die Methode hinter den Konstruktionen erklären.
