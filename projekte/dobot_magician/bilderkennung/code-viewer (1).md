# Code Viewer

## Problem
Die `code-viewer.html` war an einen festen Ort gebunden. Ruft man sie aus verschiedenen Unterordnern auf, konnte sie Datei-Links nicht relativ zum Aufrufer auflösen.

**Beispiel (vorher):**
```
http://localhost:8080/tools/code-viewer.html?file=bild-auswerten.py
```
- Aus `/projekte/dobot_magician/bilderkennung/arbeitsplatte/` aufgerufen
- Sucht die Datei aber immer im gleichen Verzeichnis wie `code-viewer.html`

## Lösung
Der Code nutzt `document.referrer`, um das Verzeichnis der aufrufenden Seite zu ermitteln und die Datei relativ dazu zu laden.

### Ablauf
1. **Parameter lesen**: `file`, `lang`, `title` aus URL-Query
2. **Prüfen, ob relativ**: Wenn der Pfad nicht mit `/` beginnt → relativ
3. **Referrer-Verzeichnis extrahieren**: Aus `document.referrer` das Verzeichnis des Aufrufers ermitteln
4. **Absolute URL bilden**: `referrer_dir + file`
5. **Laden & Anzeigen**: Mit Prism.js syntaxhighlighting

### Absolute Pfade
Pfade, die mit `/` beginnen, werden nicht verändert:
```
?file=/projekte/dobot_magician/bilderkennung/arbeitsplatte/bild-auswerten.py
```

## Anwendungsbeispiele

### 1. Aus einem Projekt heraus (relativ)
Datei: `/projekte/dobot_magician/bilderkennung/arbeitsplatte/index.html`

```html
<a href="../../../../tools/code-viewer.html?file=bild-auswerten.py&lang=python&title=bild-auswerten.py">
  Code ansehen
</a>
```
→ Lädt: `/projekte/dobot_magician/bilderkennung/arbeitsplatte/bild-auswerten.py`

### 2. Aus verschiedenen Ebenen (alle relativ)
```html
<!-- Ebene 1: /projekte/dobot_magician/bilderkennung/arbeitsplatte/index.html -->
<a href="../../../../tools/code-viewer.html?file=bild-auswerten.py">...</a>

<!-- Ebene 2: /projekte/dobot_magician/beispiele.html -->
<a href="../../tools/code-viewer.html?file=bild-auswerten.py">...</a>

<!-- Ebene 3: /projekte/index.html -->
<a href="../../tools/code-viewer.html?file=bild-auswerten.py">...</a>
```

### 3. Mit absoluten Pfaden (funktioniert überall)
```html
<!-- Von überall aus -->
<a href="../../../../tools/code-viewer.html?file=/projekte/dobot_magician/beispiele.py">...</a>
```

## Technische Details

### Referrer-Auflösung
```javascript
const referrerUrl = new URL(document.referrer);
const referrerPath = referrerUrl.pathname;
const referrerDir = referrerPath.substring(0, referrerPath.lastIndexOf('/') + 1);
// Beispiel: "/projekte/dobot_magician/bilderkennung/arbeitsplatte/"
```

### Download-Link
Der Download-Link wird ebenfalls mit der vollständigen URL gesetzt, damit der Browser die richtige Datei herunterlädt.

## Browser-Kompatibilität
- `document.referrer`: Standard-Browser (IE9+)
- `URL()` API: Moderne Browser (IE nicht)
- Fallback: Wenn kein Referrer vorhanden, wird nur der `file`-Parameter verwendet

## Wichtig
- **Sicherheit**: Da nur relative Pfade erlaubt sind, können keine beliebigen Dateien außerhalb des Repositorys geladen werden
- **Dateiformat**: Die Sprache wird automatisch erkannt (Python, JavaScript, etc.) oder mit `?lang=...` gesetzt
- **Link-Zugriff**: Der `code-viewer.html` muss immer über einen HTML-Link aufgerufen werden (mit Referrer)
