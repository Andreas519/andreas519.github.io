# 4. Kamera

## Kamera erkennen

```bash
rpicam-hello --list-cameras
```

Praktisch erkannte Kamera:

```text
0 : ov5647 [2592x1944 10-bit GBRG]
```

Verfügbare Sensormodi:

| Auflösung | maximale Bildrate |
|---:|---:|
| 640 × 480 | 62,50 fps |
| 1296 × 972 | 46,34 fps |
| 1920 × 1080 | 32,81 fps |
| 2592 × 1944 | 15,63 fps |

## Testaufnahme

Bei lokaler Bedienung kann zunächst versucht werden:

```bash
rpicam-still -o test.jpg
```

Über RDP kann das EGL-Vorschaufenster fehlschlagen. Die praktisch funktionierende Aufnahme lautet daher:

```bash
rpicam-still --nopreview -o test.jpg
```

Erfolgsmeldung:

```text
Still capture image received
```

## Datei prüfen

```bash
ls -lh test.jpg
file test.jpg
```

## Auflösung einstellen

```bash
rpicam-still --nopreview --width 640 --height 480 -o bild_vga.jpg
rpicam-still --nopreview --width 1280 --height 720 -o bild_hd.jpg
rpicam-still --nopreview --width 1920 --height 1080 -o bild_fullhd.jpg
rpicam-still --nopreview --width 2592 --height 1944 -o bild_max.jpg
```

## Typischer RDP-Fehler

```text
failed to import fd 20
```

Dieser Fehler trat beim Erzeugen des Vorschaufensters auf. Die Aufnahme ohne Vorschau mit `--nopreview` funktionierte.
