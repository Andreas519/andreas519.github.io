# Prompt 08 – Erfolgreiche Aufnahme

## Prompt

Die Aufnahme mit `--nopreview` endet mit:

```text
Still capture image received
```

und `test.jpg` wurde erzeugt.

## Antwort

Die Aufnahme war erfolgreich. Die Datei liegt standardmäßig unter:

```text
/home/pi/test.jpg
```

Öffnen:

```bash
xdg-open test.jpg
```

Datei prüfen:

```bash
ls -lh test.jpg
file test.jpg
```

Auf den Windows-PC kopieren:

```powershell
scp pi@IP-ADRESSE:/home/pi/test.jpg .
```
