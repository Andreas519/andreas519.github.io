# JSON Viewer (`json-viewer.html`)

Der JSON Viewer lädt eine JSON-Datei, prüft sie mit `JSON.parse`, formatiert gültige Daten mit zwei Leerzeichen und hebt die Syntax mit Prism hervor. Die Originaldatei kann über den Downloadknopf gespeichert werden.

## Parameter

- `file`: absoluter Pfad ab der Website-Wurzel oder relativer Pfad zum aufrufenden HTML-Dokument
- `title`: optionaler Seitentitel

## Beispiel mit absolutem Pfad

```html
<a href="/tools/json-viewer.html?file=/projekte/fusion-cad/esp32-cam-robocar/fusion/parameter.json&amp;title=ESP32-CAM%20Parameter">
  Parameter anzeigen
</a>
```

## Beispiel mit relativem Pfad

```html
<a href="../../tools/json-viewer.html?file=daten.json&amp;title=Messdaten">
  Messdaten anzeigen
</a>
```

Relative Pfade werden anhand des aufrufenden Dokuments (`document.referrer`) aufgelöst. Für direkt aufgerufene Viewer-Seiten sind absolute Pfade zuverlässiger.
