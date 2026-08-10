# Prompt 06 – Fehler bei `rpicam-still`

## Prompt

`rpicam-still -o test.jpg` endet mit:

```text
failed to import fd 20
Aborted
```

## Antwort

Die Kamera selbst wurde korrekt erkannt. Der Fehler wurde der GPU-Vorschau in der RDP-Sitzung zugeordnet.

Lösung:

```bash
rpicam-still --nopreview -o test.jpg
```

Kurzform:

```bash
rpicam-still -n -o test.jpg
```

Empfohlener Test:

```bash
rpicam-still --nopreview --timeout 2000 --width 1296 --height 972 -o test.jpg
```
