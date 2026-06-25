# Prism Code-Beispiel mit Scrollbereich

Dieses Beispiel zeigt eine externe Python-Datei auf einer HTML-Seite an.

Funktionen:

- externe Datei `main.py` wird geladen
- Syntaxhighlighting mit Prism.js
- Zeilennummern
- Codebereich mit ungefähr 10 sichtbaren Zeilen
- längere Dateien sind scrollbar

Enthaltene Dateien:

- index.html
- style.css
- script.js
- main.py
- README.md

Wichtig:
Die Seite darf lokal nicht per Doppelklick als `file://` geöffnet werden,
weil `fetch()` dann oft blockiert wird.

Lokal testen:

```bash
python -m http.server 8000
```

Falls dein Python über einen festen Pfad gestartet wird:

```bat
"D:\Program Files\Python314\python.exe" -m http.server 8000
```

Dann im Browser öffnen:

```text
http://localhost:8000/
```

Auf GitHub Pages funktioniert es direkt, wenn alle Dateien im gleichen Ordner liegen.
