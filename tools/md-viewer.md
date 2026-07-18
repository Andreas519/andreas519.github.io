# Markdown Viewer (`md-viewer.html`)

## Zweck

Lädt eine beliebige Markdown-Datei (`.md`) per URL-Parameter und zeigt sie als
formatiertes HTML an. Syntax-Highlighting für Code-Blöcke ist eingebaut.

## Parameter

| Parameter | Pflicht | Beschreibung                  | Beispiel              |
|-----------|---------|-------------------------------|-----------------------|
| `file`    | ja      | Dateiname oder Pfad           | `inhalt.md`           |
| `title`   | nein    | Titel in Kopfzeile und Tab    | `Meine Dokumentation` |

## Verwendung

### Relativer Pfad (aus einem Unterordner)

```html
<a href="../../tools/md-viewer.html?file=inhalt.md&title=Inhaltsübersicht">
  Dokumentation ansehen
</a>
```

→ Lädt die Datei `inhalt.md` relativ zum Verzeichnis der aufrufenden Seite.

### Absoluter Pfad (von überall)

```html
<a href="/tools/md-viewer.html?file=/projekte/dobot_magician/README.md&title=Dobot%20Readme">
  Dokumentation ansehen
</a>
```

→ Lädt die Datei `/projekte/dobot_magician/README.md`.

## Pfadauflösung

- **Relative Pfade** (ohne führendes `/`): Das Verzeichnis der aufrufenden Seite
  wird aus `document.referrer` extrahiert. Die Datei wird relativ dazu geladen.
- **Absolute Pfade** (mit führendem `/`): Werden direkt geladen, unabhängig vom
  Aufrufer.
- **Kein Referrer**: Wenn `document.referrer` nicht gesetzt ist (z. B. bei
  direktem Aufruf), wird der `file`-Parameter unverändert als URL verwendet.

## Darstellung

Unterstützte Markdown-Elemente:

| Element          | Darstellung                                          |
|------------------|------------------------------------------------------|
| Überschriften    | `h1`–`h6`, `h1` mit Trennlinie                       |
| Fließtext        | Zeilenabstand 1,6                                    |
| Listen           | `ul` / `ol`, eingerückt                              |
| Code (inline)    | Grauer Hintergrund, Monospace-Schrift                |
| Code-Blöcke      | Grauer Hintergrund, Syntax-Highlighting via Prism.js |
| Blockquotes      | Linker Balken in Akzentfarbe                         |
| Tabellen         | Rahmen, Kopfzeile mit Hintergrund                    |
| Links            | Akzentfarbe, Unterstreichung beim Hover              |

### Syntax-Highlighting in Code-Blöcken

Prism.js erkennt die Sprache anhand der Info-Zeichenkette im Fenced-Code-Block:

````markdown
```python
def hallo():
    print("Hallo Welt")
```
````

Unterstützte Sprachen: **Python, JavaScript, HTML, CSS**.

## Download

Sobald die Datei erfolgreich geladen wurde, zeigt der „Datei herunterladen"-Button
die Original-Markdown-Datei zum Download an (als Blob mit MIME-Typ `text/markdown`).

## Abhängigkeiten

| Bibliothek  | Quelle (CDN)                                                   |
|-------------|----------------------------------------------------------------|
| marked.js   | `cdn.jsdelivr.net/npm/marked/lib/marked.umd.min.js`            |
| Prism.js    | `cdn.jsdelivr.net/npm/prismjs/`                                |
| my.css      | `../../../../css/my.css` (lokal, relativ zu `tools/`)          |

## Bekannte Einschränkungen

- Benötigt einen HTTP-Server (kein `file://`-Protokoll), da `fetch()` verwendet wird.
- Relative Pfade funktionieren nur, wenn der Viewer über einen Link aufgerufen wird
  (nicht bei direktem Aufruf im Browser, da `document.referrer` dann leer ist).
- Bilder in der Markdown-Datei werden relativ zur Viewer-URL aufgelöst,
  nicht relativ zur Markdown-Datei selbst.
