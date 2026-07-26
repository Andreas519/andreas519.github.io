# Entwurf einer Aufgabenstellung für Morten

## Projekt: Ein Befehlsinterpreter für den Dobot Magician

> **Status:** Entwurf zur gemeinsamen Begutachtung
>
> **Arbeitsbereich:** `befehlskette/befehlsinterpreter/`
>
> **Mortens Arbeitsplattform:** Codeberg
>
> **Erste Projektphase:** Entwicklung ohne automatische Roboterbewegung

## 1. Ausgangssituation

Für den Dobot Magician existiert bereits ein Python-Programm, das eine
Befehlskette ausführt. Diese Befehlskette wird bisher direkt als Python-Liste
geschrieben:

```python
befehle = [
    ("home",),
    ("fahre_zu", 100, 100, 0, 0),
    ("warte_bis", "FREIGABE"),
    ("fahre_zu", 200, 120, 10, 0),
]
```

Für Personen ohne Python-Kenntnisse ist diese Schreibweise wenig anschaulich.

Du sollst deshalb eine kleine Sprache entwickeln, mit der ein Roboterablauf
einfacher beschrieben werden kann:

```text
Home

A = (100, 100, 0)
B = (200, 120, 10)

Fahre zu A
Warte auf "FREIGABE"
Fahre zu B

Ende
```

Dein Programm übersetzt diesen Text in die vorhandene Python-Befehlskette.

## 2. Verbindung zu deinem Minecraft-Projekt

Das Prinzip ähnelt deinem Compiler für Minecraft-Mods:

```text
Quelltext
   ↓
Lexer und Parser
   ↓
interne Darstellung
   ↓
Prüfung
   ↓
Ausgabe für das Zielsystem
```

Beim Dobot-Projekt sieht der Weg so aus:

```text
Dobot-Textdatei
   ↓
Befehlsinterpreter
   ↓
Python-Befehlsliste
   ↓
befehlskette_pruefen()
   ↓
später: kontrollierte Dobot-Ausführung
```

Der wichtigste Unterschied: Ein Fehler in einem Minecraft-Mod führt meistens
zu einer Fehlermeldung oder einem fehlerhaften Spielablauf. Ein fehlerhafter
Roboterbefehl kann eine reale Kollision verursachen.

Deshalb gilt:

> Erst übersetzen, dann prüfen, dann anzeigen – und erst nach ausdrücklicher
> Freigabe ausführen.

## 3. Dein Arbeitsbereich

Du entwickelst das Teilprojekt selbstständig in einem eigenen Repository auf
Codeberg. Der Inhalt dieses Repositorys ist für folgenden Ordner des
Dobot-Gesamtprojekts bestimmt:

```text
befehlskette/
└── befehlsinterpreter/
```

In diesem Ordner darfst du:

- eigene Python-Dateien anlegen und bearbeiten,
- Beispielprogramme erstellen,
- automatische Tests entwickeln,
- deine Sprachdefinition und Entscheidungen dokumentieren,
- Unterordner für Tests, Beispiele und Dokumentation anlegen.

Das Codeberg-Repository enthält nur das Teilprojekt. Dateien außerhalb dieses
Ordners gehören zum bestehenden Dobot-Projekt. Sie werden zunächst nur als
Referenz gelesen und nicht von dir geändert.

Wenn du später eine Änderung außerhalb deines Arbeitsbereichs benötigst:

1. Beschreibe die gewünschte Änderung.
2. Begründe, warum die vorhandene Schnittstelle nicht ausreicht.
3. Besprich die Änderung vor der Umsetzung mit dem Projektverantwortlichen.

## 4. Ziel der ersten Projektphase

Entwickle einen Befehlsinterpreter, der:

1. eine Textdatei mit Dobot-Befehlen einliest,
2. Positionsdefinitionen erkennt und speichert,
3. Anweisungen in Python-Befehle übersetzt,
4. verständliche Fehlermeldungen erzeugt,
5. die übersetzte Befehlskette zur Kontrolle anzeigt,
6. die vorhandene Prüffunktion des Dobot-Projekts verwenden kann.

Der Interpreter steuert den Dobot in dieser Phase noch nicht selbst.

## 5. Erste Version der Sprache

Die erste Version unterstützt bewusst nur wenige Anweisungen.

### 5.1 HOME-Fahrt

```text
Home
```

Übersetzung:

```python
("home",)
```

### 5.2 Position definieren

```text
A = (100, 100, 0)
```

Die drei Zahlen stehen für:

```text
X, Y, Z
```

Die Werkzeugdrehung `R` erhält zunächst automatisch den Wert `0`.

Optional darf später eine vierte Zahl erlaubt werden:

```text
A = (100, 100, 0, 45)
```

### 5.3 Position anfahren

```text
Fahre zu A
```

Übersetzung:

```python
("fahre_zu", 100, 100, 0, 0, "Fahre zu A", 500)
```

### 5.4 Auf eine Meldung warten

```text
Warte auf "FREIGABE"
```

Übersetzung:

```python
(
    "warte_bis",
    "FREIGABE",
    "Warte auf FREIGABE",
    None,
)
```

### 5.5 Programmende

```text
Ende
```

`Ende` erzeugt keinen Roboterbefehl. Es beendet das Einlesen des Programms.

Text nach `Ende` soll entweder ignoriert oder als Fehler gemeldet werden.
Entscheide dich für eine Variante und dokumentiere deine Entscheidung.

### 5.6 Kommentare

Kommentare beginnen mit `#`:

```text
# Ausgangsposition anfahren
Fahre zu A
```

Leerzeilen und Kommentarzeilen werden ignoriert.

## 6. Beispielprogramm

Dateiname:

```text
programme/erster_ablauf.dobot
```

Inhalt:

```text
# Einfacher Dobot-Ablauf

Home

A = (100, 100, 0)
B = (200, 120, 10)

Fahre zu A
Warte auf "FREIGABE"
Fahre zu B

Ende
```

Erwartete Übersetzung:

```python
[
    ("home",),
    (
        "fahre_zu",
        100,
        100,
        0,
        0,
        "Fahre zu A",
        500,
    ),
    (
        "warte_bis",
        "FREIGABE",
        "Warte auf FREIGABE",
        None,
    ),
    (
        "fahre_zu",
        200,
        120,
        10,
        0,
        "Fahre zu B",
        500,
    ),
]
```

## 7. Technische Anforderungen

Das Hauptprogramm soll zunächst als eigene Datei entwickelt werden:

```text
befehlsinterpreter.py
```

Eine mögliche Aufteilung ist:

```python
def programmdatei_lesen(dateiname):
    pass


def zeile_analysieren(zeile, zeilennummer, positionen):
    pass


def position_lesen(zeile, zeilennummer):
    pass


def anweisung_lesen(zeile, zeilennummer, positionen):
    pass


def programm_uebersetzen(text):
    pass


def befehlsliste_anzeigen(befehle):
    pass
```

Diese Aufteilung ist nur ein Vorschlag. Du darfst eine andere Struktur wählen,
wenn du sie erklären und begründen kannst.

## 8. Interne Daten

Benannte Positionen können zunächst in einem Dictionary gespeichert werden:

```python
positionen = {
    "A": (100, 100, 0, 0),
    "B": (200, 120, 10, 0),
}
```

Entscheide, ob Namen unabhängig von Groß- und Kleinschreibung sein sollen:

```text
A = (100, 100, 0)
Fahre zu a
```

Dokumentiere deine Entscheidung und verwende intern eine einheitliche
Schreibweise.

## 9. Fehlerbehandlung

Fehlermeldungen müssen mindestens enthalten:

- die Zeilennummer,
- die fehlerhafte Zeile,
- eine verständliche Fehlerursache.

Schlecht:

```text
ValueError
```

Besser:

```text
Fehler in Zeile 7:
Fahre zu C

Die Position "C" wurde noch nicht definiert.
```

Mindestens folgende Fehler sollen erkannt werden:

### 9.1 Unbekannter Befehl

```text
Fliege zu A
```

### 9.2 Unbekannte Position

```text
Fahre zu C
```

### 9.3 Fehlerhafte Koordinaten

```text
A = (100, links, 20)
```

### 9.4 Falsche Anzahl von Koordinaten

```text
A = (100, 20)
```

### 9.5 Doppelte Position

```text
A = (100, 100, 0)
A = (200, 120, 10)
```

Für die sichere Roboternutzung sollte eine doppelte Definition zunächst als
Fehler behandelt werden.

### 9.6 Fehlende Anführungszeichen

```text
Warte auf FREIGABE
```

Für die erste Version darf verlangt werden:

```text
Warte auf "FREIGABE"
```

### 9.7 Befehl nach Programmende

```text
Ende
Fahre zu A
```

## 10. Sicherheitsanforderungen

Der Interpreter darf den Dobot in der ersten Entwicklungsphase nicht bewegen.

Die Ausgabe erfolgt zunächst nur als Vorschau:

```text
Übersetzung erfolgreich.

1: home()
2: fahre_zu(100, 100, 0, 0)
3: warte_bis("FREIGABE")
4: fahre_zu(200, 120, 10, 0)
```

Anschließend kann die vorhandene Prüfung aufgerufen werden:

```python
programm = befehlskette_pruefen(befehle)
```

Erst in einer späteren, gemeinsam freigegebenen Projektphase darf die
Ausführung ergänzt werden.

Vor jeder späteren Roboter-Ausführung müssen mindestens gelten:

- Übersetzung ohne Fehler,
- Befehlskettenprüfung ohne Fehler,
- Anzeige aller erzeugten Befehle,
- ausdrückliche Bestätigung durch einen Menschen,
- freier Arbeitsbereich,
- funktionsfähiger Halt-Taster,
- Sicherheitshub vor einer HOME-Fahrt.

## 11. Empfohlene Arbeitsschritte

### Stufe 1: Text einlesen

- Textdatei öffnen.
- Zeilen nummerieren.
- Leerzeilen und Kommentare ignorieren.
- verarbeitete Zeilen zur Kontrolle ausgeben.

### Stufe 2: Positionsdefinitionen

- Definitionen wie `A = (100, 100, 0)` erkennen.
- Zahlen umwandeln.
- Positionen im Dictionary speichern.
- fehlerhafte Definitionen melden.

### Stufe 3: Einfache Anweisungen

Zunächst nur:

```text
Home
Fahre zu A
Ende
```

### Stufe 4: Warten auf Meldungen

Unterstützung ergänzen für:

```text
Warte auf "FREIGABE"
```

### Stufe 5: Fehlerdiagnose

Für jede fehlerhafte Eingabe eine verständliche Meldung mit Zeilennummer
erzeugen.

### Stufe 6: Vorschau

Die erzeugte Python-Befehlsliste lesbar anzeigen.

### Stufe 7: Vorhandene Prüfung anbinden

Die fertige Liste an `befehlskette_pruefen()` übergeben.

### Stufe 8: Automatische Tests

Gültige und ungültige Beispielprogramme automatisch prüfen.

### Stufe 9: Optionale Dobot-Ausführung

Erst nach gemeinsamer Begutachtung und praktischer Sicherheitsprüfung.

## 12. Mindestanforderungen

Die erste Version ist fertig, wenn:

- Positionsdefinitionen mit drei Zahlen funktionieren,
- `Home` erkannt wird,
- `Fahre zu Name` funktioniert,
- `Warte auf "Meldung"` funktioniert,
- `Ende` erkannt wird,
- Kommentare und Leerzeilen ignoriert werden,
- unbekannte Positionen verständlich gemeldet werden,
- jede Fehlermeldung eine Zeilennummer enthält,
- die erzeugte Befehlsliste angezeigt wird,
- der Dobot nicht automatisch gestartet wird.

## 13. Testfälle

### 13.1 Gültiges Programm

```text
Home
A = (100, 100, 20)
Fahre zu A
Ende
```

Erwartung: erfolgreiche Übersetzung.

### 13.2 Unbekannte Position

```text
Home
Fahre zu A
Ende
```

Erwartung: Fehler bei `Fahre zu A`.

### 13.3 Fehlerhafte Zahl

```text
A = (100, vorne, 20)
Ende
```

Erwartung: verständliche Fehlermeldung für `vorne`.

### 13.4 Falsche Koordinatenanzahl

```text
A = (100, 20)
Ende
```

Erwartung: Hinweis, dass drei oder vier Koordinaten notwendig sind.

### 13.5 Unbekannter Befehl

```text
Teleportiere zu A
```

Erwartung: unbekannter Befehl mit Zeilennummer.

### 13.6 Kommentare und Leerzeilen

```text
# Testprogramm

Home

# Zielposition
A = (100, 100, 20)
Fahre zu A
Ende
```

Erwartung: Kommentare und Leerzeilen werden ignoriert.

## 14. Mögliche Erweiterungen

Erst nach Abschluss der Grundversion:

```text
Geschwindigkeit 20
Sauger ein
Sauger aus
Warte 1000
Fahre um (0, 0, 30)
Marke Anfang
Gehe zu Anfang
```

Später wären auch Bedingungen denkbar:

```text
Wenn TEMPERATUR >= 30 dann Gehe zu Warnung
```

Diese Erweiterungen gehören ausdrücklich nicht zur ersten Aufgabe.

## 15. Zusammenarbeit und Versionsverwaltung

### 15.1 Eigenständiges Teilprojekt auf Codeberg

Codeberg bleibt deine Arbeitsplattform. Dort verwaltest du das eigenständige
Repository für den Dobot-Befehlsinterpreter.

Ein möglicher Repositoryname ist:

```text
dobot-befehlsinterpreter
```

Den endgültigen Namen und die Sichtbarkeit des Repositorys legst du gemeinsam
mit dem Projektverantwortlichen fest.

Das Codeberg-Repository ist die Arbeitsquelle für den Interpreter. Das
GitHub-Repository des Dobot-Gesamtprojekts bleibt davon getrennt und wird nicht
automatisch durch deine Arbeit verändert.

### 15.2 Selbstständige Arbeit

Du planst und implementierst deine Lösung selbstständig. Offene Fragen,
Entscheidungen und Probleme hältst du in deiner Dokumentation fest.

### 15.3 Branches und kleine, nachvollziehbare Schritte

Für eine neue, zusammenhängende Aufgabe kannst du auf Codeberg einen eigenen
Branch verwenden. Beispiele:

```text
positionsdefinitionen
fehlerbehandlung
warte-auf-befehl
```

Änderungen sollen in kleinen Arbeitsschritten gespeichert werden. Eine
Commit-Nachricht beschreibt, was erreicht wurde, zum Beispiel:

```text
Positionsdefinitionen einlesen
Fehler für unbekannte Position ergänzen
Warte-auf-Befehl übersetzen
```

### 15.4 Begutachtung auf Codeberg

Ein begutachtbarer Arbeitsstand wird auf Codeberg als Pull Request oder als
klar gekennzeichneter Branch bereitgestellt.

Für eine Begutachtung werden mindestens angegeben:

- kurze Beschreibung des erreichten Stands,
- betroffene Dateien,
- ausgeführte Tests,
- bekannte Einschränkungen,
- offene Fragen.

### 15.5 Übernahme in das Dobot-Gesamtprojekt

Nach der Begutachtung wird ein freigegebener Stand bewusst in folgenden Ordner
des GitHub-Projekts übernommen:

```text
projekte/dobot_magician/Dobot-Python/befehlskette/befehlsinterpreter/
```

Die Übernahme erfolgt nicht automatisch. Dadurch bleiben die veröffentlichte
Projektseite und die bestehende Dobot-Steuerung geschützt.

Bei der Übernahme werden festgehalten:

- Codeberg-Repository,
- Branch oder Versionskennzeichnung,
- übernommener Commit,
- ausgeführte Tests,
- Datum der Übernahme.

Die genaue technische Übernahme – beispielsweise über ein zusätzliches
Git-Remote – wird später gemeinsam eingerichtet.

### 15.6 Änderungen außerhalb des Arbeitsbereichs

Änderungen außerhalb von `befehlsinterpreter/` werden nicht selbstständig
vorgenommen. Wenn eine Schnittstelle fehlt, wird zunächst ein Vorschlag
erstellt.

## 16. Arbeiten ohne und mit KI

### Phase A: zunächst ohne KI-Unterstützung

In der ersten Phase entwickelst du selbst:

- die Grundidee deiner Grammatik,
- das Einlesen der Datei,
- Positionsdefinitionen,
- mindestens einen ausführbaren Parser-Entwurf,
- erste gültige und ungültige Testfälle.

Du darfst vorhandene Python-Dokumentation und die bestehende
Dobot-Befehlskette lesen.

Ziel dieser Phase ist nicht, sofort die perfekte Lösung zu erstellen. Ziel ist,
dass dein eigener Lösungsansatz sichtbar und erklärbar wird.

### Phase B: später mit KI-Unterstützung

Nach der ersten gemeinsamen Begutachtung darf KI gezielt eingesetzt werden,
zum Beispiel für:

- Rückfragen zu Python,
- Hinweise auf übersehene Testfälle,
- Verbesserung von Fehlermeldungen,
- Code-Review,
- Vorschläge zur Strukturierung,
- Erklärung unbekannter vorhandener Projektteile.

Die KI soll nicht unkontrolliert das gesamte Projekt erzeugen.

Für jede wesentliche KI-Unterstützung wird kurz dokumentiert:

```text
Meine Frage:

Vorschlag der KI:

Was ich übernommen oder verändert habe:

Wie ich das Ergebnis geprüft habe:
```

Du bleibst für jede übernommene Änderung verantwortlich und musst sie erklären
können.

## 17. Abgabe

Abzugeben sind:

- `befehlsinterpreter.py`,
- mindestens drei gültige `.dobot`-Programme,
- mindestens fünf absichtlich fehlerhafte Testprogramme,
- eine kurze `README.md`,
- eine Liste der unterstützten Sprachbefehle,
- Beispiele der wichtigsten Fehlermeldungen,
- automatische Tests,
- eine kurze Beschreibung, wie aus dem Text die Python-Befehlsliste entsteht,
- später gegebenenfalls die Dokumentation der KI-Unterstützung.

Eine mögliche Ordnerstruktur:

```text
befehlsinterpreter/
├── AUFGABENSTELLUNG_MORTEN.md
├── README.md
├── befehlsinterpreter.py
├── programme/
│   ├── erster_ablauf.dobot
│   └── ...
├── tests/
│   ├── test_befehlsinterpreter.py
│   └── testprogramme/
└── dokumentation/
    └── ...
```

## 18. Leitfragen für die Dokumentation

1. Wo liegt in deinem Programm die Grenze zwischen Lexer, Parser, semantischer
   Prüfung und Codeerzeugung?
2. Welche Fehler erkennt dein Parser, welche erst die semantische Prüfung?
3. Wie stellst du sicher, dass unbekannte Positionen nicht ausgeführt werden?
4. Welche Entscheidungen hast du bei Groß- und Kleinschreibung getroffen?
5. Wie verhinderst du, dass ein ungeprüftes Programm den Dobot bewegt?
6. Welche Teile hast du selbst entwickelt?
7. Wo hat später eine KI geholfen, und wie hast du deren Vorschläge geprüft?

## 19. Vor dem Arbeitsbeginn noch gemeinsam festzulegen

Codeberg ist als Arbeitsplattform festgelegt. Offen sind noch:

- Wie heißt das Codeberg-Repository?
- Ist es öffentlich oder privat?
- Wer erhält auf Codeberg welche Rolle?
- Welche Branch- und Review-Regeln werden verwendet?
- Wie wird das vorhandene Befehlskettenmodul zunächst nur lesend bereitgestellt?
- Wie wird ein freigegebener Commit in das GitHub-Projekt übernommen?
- Wann beginnt Phase B mit KI-Unterstützung?
- Wer gibt die erste reale Dobot-Ausführung frei?
