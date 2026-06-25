# Modernisierte MicroPython-ESP32-Seite

Diese ZIP enthält eine modernisierte Fassung der hochgeladenen `micropython.html`.

## Dateien

- `index.html` – modernisierte HTML-Seite
- `style.css` – neues Layout, Karten, responsive Darstellung, Code-Scrollbereiche
- `script.js` – lädt externe Code-Dateien über `data-src`
- `original/` – deine hochgeladenen Ausgangsdateien zum Vergleich

## Wichtig zum lokalen Testen

Die Seite darf nicht per Doppelklick als `file://` geöffnet werden, wenn externe Code-Dateien per `fetch()` geladen werden sollen.

Im Ordner starten:

```bat
python -m http.server 8000
```

Oder bei dir mit vollständigem Pfad:

```bat
"D:\Program Files\Python314\python.exe" -m http.server 8000
```

Dann öffnen:

```text
http://localhost:8000/
```

## Hinweis

Die ursprüngliche Seite verweist auf viele externe `.py.txt`-Dateien wie `blink.py.txt`, `pwm.py.txt` usw. Diese Dateien waren nicht Teil des Uploads und sind deshalb nicht in der ZIP enthalten. Auf deinem Server funktionieren die Verweise weiter, wenn die Dateien im gleichen Ordner wie bisher liegen.
