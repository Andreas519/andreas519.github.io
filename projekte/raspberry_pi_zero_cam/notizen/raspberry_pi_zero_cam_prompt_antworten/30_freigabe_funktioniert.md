# Prompt 30 – Lesen und Schreiben funktionieren

## Prompt

Die Windows-Freigabe kann vom Raspberry Pi gelesen und beschrieben werden.

## Antwort

Variante 3 wurde damit als erfolgreich eingerichtet bewertet.

Direkte Kameraaufnahme in die Freigabe:

```bash
rpicam-still --nopreview -o /mnt/windows/test.jpg
```

Damit erscheint das Bild unmittelbar auf dem Windows-PC.
