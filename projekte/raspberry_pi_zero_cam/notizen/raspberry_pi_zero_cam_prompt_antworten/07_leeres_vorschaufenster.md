# Prompt 07 – Leeres Vorschaufenster

## Prompt

Ein Fenster geht kurz auf und schließt sich wieder, ohne Inhalt.

## Antwort

Das leere Fenster ist die Kamera-Vorschau. In einer RDP-Sitzung kann diese Vorschau oft nicht korrekt angezeigt werden.

Daher sollte die Aufnahme ohne Vorschau erfolgen:

```bash
rpicam-still --nopreview -o test.jpg
```
