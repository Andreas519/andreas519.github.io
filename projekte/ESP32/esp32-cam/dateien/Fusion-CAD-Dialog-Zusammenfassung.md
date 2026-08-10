# Zusammenfassung: Autodesk Fusion und Projekt `fusion-cad`

## Ausgangspunkt

Nach dem vorläufigen Abschluss der Arbeiten an der ESP32-CAM entstand die
Frage, in welchem Umfang Codex technische Bauteile für Autodesk Fusion
konstruieren kann.

Codex kann insbesondere bei folgenden Aufgaben unterstützen:

- parametrische Halterungen, Gehäuse und Adapterplatten konstruieren
- Aufnahmen für ESP32-CAM, Sensoren, Akkus und andere Baugruppen entwickeln
- Befestigungen für RoboCar und Dobot Magician planen
- Schrauben, Muttern, Gewindeeinsätze, Kabeldurchführungen und Drucktoleranzen
  berücksichtigen
- Python-Skripte für die Autodesk-Fusion-API erstellen
- vorhandene Skripte, CAD-Exporte, Fotos und Maßskizzen auswerten
- STEP-, STL- und 3MF-Exporte sowie Zeichnungen und Dokumentationen vorbereiten

Die direkte und präzise Bedienung der nativen Fusion-Oberfläche ist nicht als
spezielle Autodesk-Integration verfügbar. Als reproduzierbare Verbindung
zwischen Codex und Fusion sollen deshalb bevorzugt parametrische
Fusion-Python-Skripte verwendet werden.

## Vorgesehener Konstruktionsablauf

1. Fotos und Hauptmaße des Einsatzortes erfassen.
2. Befestigung, Bewegungsraum, Kamerahöhe und Neigungsbereich festlegen.
3. Ein parametrisches Fusion-Python-Skript erstellen.
4. Das Skript in Autodesk Fusion ausführen und das Modell erzeugen.
5. Modell und Exportdateien prüfen.
6. Einen Probedruck anfertigen und montieren.
7. Passung, Stabilität und Kamerablickwinkel bewerten.
8. Parameter und Konstruktion iterativ verbessern.

Als erstes mögliches Projekt wurde ein schwenkbarer ESP32-CAM-Halter als
Frontkamera für ein RoboCar vorgeschlagen. Danach soll eine Halterung für eine
ESP32-CAM über der Arbeitsplatte eines Dobot Magician entstehen.

## Neue Codex-Aufgabe

Für die CAD-Arbeiten wurde eine eigene Codex-Aufgabe mit dem Namen
**Autodesk Fusion – CAD-Konstruktionen** angelegt. Der bisherige Dialog konnte
nicht nachträglich aus dem ESP32-Chat entfernt werden. Stattdessen wurde der
gesamte Fusion-CAD-Kontext als strukturierte Übergabe in die neue Aufgabe
gesendet.

## Zusammenarbeit auf zwei Rechnern

Für die Arbeit stehen ein Windows-PC und ein leistungsfähigerer iMac mit
Autodesk Fusion und Codex zur Verfügung.

Die vorgesehene Aufgabenteilung lautet:

- **iMac:** Autodesk Fusion, Ausführung der Fusion-Skripte, Modellkontrolle und
  CAD-Exporte
- **Windows-PC:** Elektronik, ESP32-Firmware, Website und Dokumentation
- **GitHub:** gemeinsame und verbindliche Projektablage

Auf beiden Rechnern wird dasselbe GitHub-Repository verwendet. Vor Beginn
eines Arbeitsschritts wird der aktuelle Stand abgerufen. Abgeschlossene
Änderungen werden gezielt committed und anschließend zu GitHub übertragen.

Der iMac ist derzeit nicht als entfernter Codex-Host des Windows-PCs
registriert. Die geräteübergreifende Zusammenarbeit erfolgt deshalb zunächst
über Git und GitHub.

## Umgang mit CAD-Dateien in Git

Textbasierte Dateien eignen sich besonders gut für die Zusammenarbeit:

- Fusion-Python-Skripte
- JSON-Parameterdateien
- Markdown-Dokumentationen
- HTML-Projektseiten

Native Fusion-Dateien und CAD-Exporte sind Binärdateien. Sie lassen sich nicht
sinnvoll zusammenführen und sollen daher immer nur auf einem Rechner
gleichzeitig bearbeitet werden. Für größere F3D-, STEP-, STL- oder
3MF-Dateien kann später Git LFS eingesetzt werden.

## Geplanter Projektbereich

Die CAD-Projekte sollen nicht innerhalb eines einzelnen Elektronikprojekts,
sondern in einem eigenen Sammelbereich des bestehenden Repositorys
`Andreas519/andreas519.github.io` abgelegt werden:

```text
projekte/
└── fusion-cad/
    ├── README.md
    ├── index.html
    ├── gemeinsame-teile/
    │   ├── fusion/
    │   └── exports/
    ├── esp32-cam-robocar/
    │   ├── README.md
    │   ├── fusion/
    │   │   ├── kamerahalter.py
    │   │   └── parameter.json
    │   ├── models/
    │   ├── exports/
    │   └── bilder/
    ├── esp32-cam-dobot/
    │   ├── README.md
    │   ├── fusion/
    │   ├── models/
    │   ├── exports/
    │   └── bilder/
    └── vorlagen/
        ├── projekt-readme.md
        └── parameter-beispiel.json
```

Die Verzeichnisse haben folgende Aufgaben:

- `fusion/`: parametrische Skripte und Parameter
- `models/`: native Fusion-Dateien
- `exports/`: STEP-, STL- und 3MF-Dateien
- `bilder/`: Fotos, Maßskizzen und gerenderte Ansichten
- `gemeinsame-teile/`: wiederverwendbare Modelle und Komponenten
- `vorlagen/`: einheitlicher Ausgangspunkt für neue Konstruktionen

## Späterer Themenbereich

Zusätzlich zum praktischen Projektbereich soll später ein allgemeiner
Themenbereich entstehen:

```text
themen/fusion-cad/
├── index.html
├── grundlagen.md
├── parametrisches-konstruieren.md
├── fusion-python-api.md
├── zusammenarbeit-mit-codex.md
├── git-arbeitsablauf.md
└── druck-und-toleranzen.md
```

Die Bereiche werden klar getrennt:

- `projekte/fusion-cad/` enthält konkrete Konstruktionen, Skripte, Modelle,
  Exporte und Probedrucke.
- `themen/fusion-cad/` erklärt die allgemeine Methode und die technischen
  Grundlagen.

Beide Bereiche sollen sich gegenseitig verlinken. Die realen Konstruktionen
dienen dabei als nachvollziehbare Beispiele für die allgemeinen Anleitungen.

## Selbstständig durch Codex realisierbar

Nach dem Öffnen des Repository-Roots als beschreibbarer Workspace kann Codex
selbstständig:

- die gesamte Ordnerstruktur anlegen
- README- und HTML-Projektseiten erstellen
- Projektvorlagen und Parameterdateien vorbereiten
- den neuen Bereich in die bestehende Website integrieren
- Fusion-Python-Skripte entwickeln
- Git-Regeln, `.gitignore` und bei Bedarf Git LFS vorbereiten
- Links, Dateien und Versionsstände prüfen
- nach ausdrücklichem Auftrag gezielte Git-Commits und Pushes ausführen

Für endgültige mechanische Konstruktionen bleiben reale Maße, Montageort,
Kabelweg, Bewegungsfreiheit, Materialwahl, Probedruck und Passungsprüfung durch
den Nutzer erforderlich.

## Workspace und Repository

Das Repository-Root lautet:

```text
D:\Github\andreas519.github.io
```

Es ist in Codex bereits als lokales Projekt registriert, wird in der
Projektauswahl momentan jedoch unter dem Namen **Dobot-Befehlskette** angezeigt.
Für die Anlage von `projekte/fusion-cad/` soll eine neue Aufgabe mit diesem
Root-Projekt und einer lokalen Umgebung gestartet werden.

Im Repository liegen derzeit zahlreiche ungesicherte Änderungen. Vor der
Zusammenarbeit auf zwei Rechnern müssen die beabsichtigten Änderungen gezielt
gesichtet und committed werden. Unabhängige oder fremde Änderungen dürfen
nicht unbeabsichtigt in einen Commit aufgenommen werden.

## Vorgeschlagener erster Arbeitsauftrag

```text
Lege im bestehenden Repository unter projekte/fusion-cad/ das neue
Sammelprojekt für Autodesk-Fusion-Konstruktionen an. Erstelle zunächst
Struktur, README.md, index.html und eine Vorlage für kommende CAD-Projekte.
Berücksichtige die vorhandene Website-Gestaltung und verändere keine
bestehenden Projekte.
```

Nach dem Aufbau des Sammelprojekts soll als erstes konkretes Vorhaben der
parametrische ESP32-CAM-Halter für das RoboCar begonnen werden.
