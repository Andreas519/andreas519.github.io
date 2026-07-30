# Git-Spickzettel

## Der wichtigste Merksatz

> **Stagen = auswählen, committen = lokal speichern, pushen = zu GitHub hochladen.**

Kurz:

> **Auswählen → Speichern → Hochladen**

---

## 1. Änderungen ansehen

```powershell
git status
```

Zeigt unter anderem:

- geänderte Dateien,
- neue Dateien,
- gelöschte Dateien,
- bereits für den nächsten Commit ausgewählte Dateien.

**Merkhilfe:** Erst ansehen, dann auswählen.

---

## 2. Stagen: Änderungen auswählen

Eine bestimmte Datei auswählen:

```powershell
git add pfad/datei.html
```

Einen ganzen Ordner auswählen:

```powershell
git add pfad/ordner
```

Alle Änderungen auswählen:

```powershell
git add .
```

> `git add .` nur verwenden, wenn wirklich **alle** angezeigten Änderungen in den Commit gehören.

Auswahl kontrollieren:

```powershell
git diff --staged
```

**Merkhilfe:** Ich lege die gewünschten Änderungen auf den **Stapel**.

---

## 3. Committen: Zwischenstand lokal speichern

```powershell
git commit -m "Kurze Beschreibung der Änderung"
```

Beispiel:

```powershell
git commit -m "Vision-System-Dokumentation ergänzen"
```

Der Commit ist zunächst nur auf dem eigenen Computer gespeichert.

**Merkhilfe:** Ich verschließe und beschrifte das Paket.

---

## 4. Pushen: Commit zu GitHub hochladen

```powershell
git push
```

Danach prüfen:

```powershell
git status
```

Steht dort beispielsweise

```text
Your branch is up to date with 'origin/main'.
```

sind der lokale Branch und GitHub auf demselben Stand.

**Merkhilfe:** Ich schiebe das fertige Paket zu GitHub.

---

## Die normale Reihenfolge

```powershell
git status
git add pfad/datei.html
git diff --staged
git commit -m "Beschreibung"
git push
git status
```

Als Ablauf:

```text
Datei ändern
    ↓
Änderungen ansehen
    ↓
Stagen: auswählen
    ↓
Committen: lokal speichern
    ↓
Pushen: zu GitHub hochladen
```

---

## Nur eine Datei übertragen

```powershell
git status
git add projekte/mein-projekt/index.html
git diff --staged
git commit -m "Projektseite aktualisieren"
git push
```

Andere geänderte Dateien werden dabei nicht übertragen, solange sie nicht ebenfalls gestaged und committet wurden.

---

## Häufige Begriffe

| Git-Begriff | Einfache Bedeutung |
|---|---|
| Repository | Projektordner mit Git-Versionsgeschichte |
| Working Tree | aktueller Arbeitsordner auf dem Computer |
| Stage / Index | Auswahl für den nächsten Commit |
| Commit | gespeicherter Zwischenstand mit Beschreibung |
| Branch | Entwicklungszweig, meistens `main` |
| Remote | entferntes Repository, beispielsweise GitHub |
| `origin` | üblicher Kurzname für das GitHub-Repository |
| Push | lokale Commits hochladen |
| Pull | Änderungen von GitHub herunterladen |
| Clone | vollständige Arbeitskopie herunterladen |

---

## Wichtig

- GitHub kennt nur Änderungen, die **committet und gepusht** wurden.
- Ein Commit bleibt in der Versionsgeschichte nachvollziehbar.
- Auch gelöschte Dateien können aus einem älteren Commit wiederhergestellt werden.
- Vor `git add .` immer zuerst `git status` prüfen.
- Eine klare Commit-Beschreibung erklärt kurz, **was** geändert wurde.

---

Erstellt mit GitHub Copilot für Andreas Sigismund · AG Young Engineers
