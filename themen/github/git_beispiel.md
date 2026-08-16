# Einführung in Git an einem konkreten Beispiel

## 1. Grundidee

Git ist ein Versionsverwaltungssystem.

Das bedeutet:

> Git merkt sich ausgewählte Zustände eines Projektes.

Ein Projekt kann zum Beispiel sein:

* eine Webseite,
* ein Python-Programm,
* ein MicroPython-Projekt für den ESP32,
* eine Dokumentation,
* ein Unterrichtsmaterial.

Git speichert nicht einfach nur „Dateien“, sondern Änderungen an Dateien.

Man kann sich Git wie ein Projekttagebuch vorstellen:

```text
Heute habe ich eine Überschrift eingefügt.
Heute habe ich eine CSS-Datei ergänzt.
Heute habe ich einen Fehler behoben.
```

Jeder gespeicherte Stand heißt **Commit**.

---

## 2. Unser Beispielprojekt

Wir erstellen eine kleine Webseite.

Ordner:

```text
git-test/
```

Datei:

```text
index.html
```

Inhalt von `index.html`:

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Mein erstes Git-Projekt</title>
</head>
<body>
  <h1>Mein erstes Git-Projekt</h1>
  <p>Diese Webseite wird mit Git verwaltet.</p>
</body>
</html>
```

Jetzt haben wir ein kleines Projekt.

Aber Git weiß davon noch nichts.

---

## 3. Git im Projektordner starten

Im Terminal wechseln wir in den Projektordner:

```powershell
cd git-test
```

Dann starten wir Git:

```powershell
git init
```

Damit entsteht im Ordner ein versteckter Unterordner:

```text
.git/
```

Dieser Ordner ist das Gedächtnis von Git.

Wichtig:

> Ohne `.git` ist es nur ein normaler Ordner.
> Mit `.git` ist es ein Git-Repository.

---

## 4. Zustand prüfen

Der wichtigste Git-Befehl für Anfänger ist:

```powershell
git status
```

Git meldet jetzt sinngemäß:

```text
Untracked files:
  index.html
```

Das bedeutet:

> Die Datei existiert, aber Git beobachtet sie noch nicht.

Git speichert nicht automatisch jede Datei.
Man muss Git sagen, welche Dateien zum nächsten gespeicherten Stand gehören sollen.

---

## 5. Datei vormerken

Wir merken die Datei für den nächsten Commit vor:

```powershell
git add index.html
```

Danach wieder:

```powershell
git status
```

Jetzt meldet Git sinngemäß:

```text
Changes to be committed:
  new file: index.html
```

Das bedeutet:

> Die Datei liegt jetzt im Wartebereich für den nächsten Commit.

Dieser Wartebereich heißt **Staging Area**.

---

## 6. Ersten Commit erstellen

Jetzt speichern wir den ersten Projektstand:

```powershell
git commit -m "Erste Version der Webseite"
```

Damit entsteht ein Commit.

Ein Commit enthält:

* die vorgemerkten Änderungen,
* den Autor,
* Datum und Uhrzeit,
* eine Commit-Nachricht,
* eine eindeutige Kennung.

Die Commit-Nachricht soll kurz sagen, was geändert wurde.

Gute Nachricht:

```text
Erste Version der Webseite
```

Schlechte Nachricht:

```text
Update
```

---

## 7. Verlauf anzeigen

Mit folgendem Befehl sehen wir den Verlauf:

```powershell
git log
```

Etwas kürzer:

```powershell
git log --oneline
```

Beispiel:

```text
a3f5c9e Erste Version der Webseite
```

Jetzt hat unser Projekt einen gespeicherten Zustand.

---

## 8. Datei ändern

Wir erweitern `index.html`:

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Mein erstes Git-Projekt</title>
</head>
<body>
  <h1>Mein erstes Git-Projekt</h1>
  <p>Diese Webseite wird mit Git verwaltet.</p>

  <h2>Was ist Git?</h2>
  <p>Git speichert verschiedene Versionen eines Projektes.</p>
</body>
</html>
```

Jetzt fragen wir Git wieder:

```powershell
git status
```

Git erkennt:

```text
modified: index.html
```

Das bedeutet:

> Die Datei wurde geändert.

---

## 9. Änderungen ansehen

Mit diesem Befehl sehen wir die Unterschiede:

```powershell
git diff
```

Git zeigt, welche Zeilen neu hinzugekommen sind.

Das ist besonders nützlich, wenn man wissen möchte:

> Was habe ich seit dem letzten Commit verändert?

---

## 10. Zweiten Commit erstellen

Die Änderung wird wieder vorgemerkt:

```powershell
git add index.html
```

Dann wird ein neuer Commit erstellt:

```powershell
git commit -m "Abschnitt über Git ergänzt"
```

Jetzt gibt es zwei gespeicherte Projektstände.

Verlauf anzeigen:

```powershell
git log --oneline
```

Beispiel:

```text
b81d2a1 Abschnitt über Git ergänzt
a3f5c9e Erste Version der Webseite
```

---

## 11. Git-Arbeitsablauf

Der typische Ablauf ist immer ähnlich:

```text
Datei ändern
git status
git diff
git add datei
git commit -m "Nachricht"
git log --oneline
```

Kurzform:

```text
ändern → prüfen → vormerken → speichern
```

Oder als Git-Befehle:

```powershell
git status
git diff
git add index.html
git commit -m "Sinnvolle Nachricht"
```

---

## 12. Wichtige Begriffe

### Repository

Ein Projektordner, der von Git verwaltet wird.

```text
git-test/
└── .git/
```

### Commit

Ein gespeicherter Projektstand.

### Staging Area

Der Wartebereich für den nächsten Commit.

### Branch

Ein Entwicklungszweig.

Der Hauptzweig heißt heute meistens:

```text
main
```

Früher hieß er oft:

```text
master
```

Technisch sind beide Namen gleichwertig.

### Working Directory

Der aktuelle Projektordner, in dem man Dateien bearbeitet.

---

## 13. Bildhafte Erklärung

Man kann sich Git so vorstellen:

```text
Arbeitsordner
    ↓ git add
Wartebereich
    ↓ git commit
Projektgeschichte
```

Oder:

```text
Working Directory → Staging Area → Repository
```

---

## 14. Warum ist Git nützlich?

Git hilft bei Fragen wie:

* Was habe ich geändert?
* Wann habe ich etwas geändert?
* Warum habe ich etwas geändert?
* Welche Version hat noch funktioniert?
* Wie kann ich einen alten Stand ansehen?
* Wie können mehrere Personen an einem Projekt arbeiten?

Für Programmierprojekte ist Git deshalb fast unverzichtbar.

---

## 15. Mini-Übung

Aufgabe:

1. Erstelle einen Ordner `git-test`.
2. Erstelle darin eine Datei `index.html`.
3. Starte Git mit `git init`.
4. Prüfe den Zustand mit `git status`.
5. Speichere die erste Version mit `git add` und `git commit`.
6. Ändere die Webseite.
7. Sieh dir die Änderung mit `git diff` an.
8. Speichere die zweite Version.
9. Zeige den Verlauf mit `git log --oneline`.

---

## 16. Merksätze

```text
Git speichert Projektstände.
```

```text
Ein Commit ist ein gespeicherter Zustand.
```

```text
git status sagt: Was ist los?
```

```text
git add merkt Änderungen vor.
```

```text
git commit speichert vorgemerkte Änderungen dauerhaft.
```

```text
git log zeigt die Geschichte des Projektes.
```

```text
GitHub und Codeberg sind Plattformen.
Git ist das eigentliche Versionsverwaltungssystem.
```
