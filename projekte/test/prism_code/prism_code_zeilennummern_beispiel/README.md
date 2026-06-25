# Prism Code-Beispiel

Dieses Beispiel zeigt eine externe Python-Datei auf einer HTML-Seite an.

Enthaltene Dateien:

- index.html
- style.css
- script.js
- main.py

Wichtig:
Die Seite darf lokal nicht per Doppelklick als file:// geöffnet werden,
weil fetch() dann oft blockiert wird.

Lokal testen:

```bash
python -m http.server 8000
```

Dann im Browser öffnen:

```text
http://localhost:8000/
```

Auf GitHub Pages funktioniert es direkt, wenn alle Dateien im gleichen Ordner liegen.
