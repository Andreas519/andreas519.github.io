# 5. Python

## Ziel

Die Kamerafunktionen sollen später in verständlichen Python-Modulen gekapselt werden.

Geplante Aufrufe:

```python
kamera.foto("HD")
kamera.foto("FULLHD", datei="werkstueck.jpg")
bildtransfer.hole_bild()
```

## Geplante Dateien

- `kamera.py` – Aufnahme, Auflösung, Dateiname
- `bildtransfer.py` – Übertragung zwischen Pi und PC
- `bildverarbeitung.py` – OpenCV-Auswertung
- `ki.py` – spätere KI-Verfahren
