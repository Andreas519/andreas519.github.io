# Dobot Magician – Türme von Hanoi

Ein Python-Programm, das das klassische Türme-von-Hanoi-Rätsel mit dem
[Dobot Magician](https://www.dobot-robots.com/products/education/magician.html)
Roboterarm physisch löst. Ursprünglich in ca. 4 Stunden für einen Messeauftritt
entwickelt – diese Version ist die dokumentierte, wieder aufgebaute Fassung.

## Was macht das Programm?

1. Berechnet die optimale Zugfolge für **n Scheiben** (klassischer rekursiver
   Hanoi-Algorithmus, 2ⁿ − 1 Züge).
2. Steuert den Dobot Magician mit Saugnapf-Endeffektor an, um die Scheiben
   physisch zwischen drei Türmen (A, B, C) umzustapeln.
3. Führt bei jedem Zug automatisch die korrekte Höhe (Z-Koordinate) mit, je
   nachdem wie hoch der jeweilige Stapel gerade ist.

## Voraussetzungen

- Dobot Magician mit Saugnapf-Kit
- Python 3.8+
- Pakete:
  ```bash
  pip install pydobotplus pyserial
  ```

## Hardware-Setup

- 3 Türme (Stifte/Dübel oder markierte Positionen auf einer Platte)
- Scheiben mit glatter Oberseite (damit der Saugnapf greifen kann)

## Konfiguration

Vor dem ersten Einsatz **unbedingt anpassen** (im Kopf der Datei
`dobot_hanoi.py`):

| Variable         | Bedeutung                                          |
|------------------|-----------------------------------------------------|
| `PEG_POSITIONS`  | X/Y-Koordinaten der drei Türme                      |
| `BASE_Z`         | Z-Höhe der Turmbasis / Tischoberfläche              |
| `DISC_HEIGHT`    | Dicke einer einzelnen Scheibe                       |
| `SAFE_Z`         | Sichere Transporthöhe zwischen den Türmen           |

**Tipp:** Am einfachsten lassen sich die Koordinaten über den
"Teach & Playback"-Modus in DobotStudio/DobotLab ermitteln – Arm manuell auf
jeden Turm fahren und die angezeigte Position übernehmen.

## Verwendung

```bash
# Standard: 3 Scheiben
python dobot_hanoi.py

# 5 Scheiben
python dobot_hanoi.py -n 5

# Bestimmten Port erzwingen (z.B. wenn mehrere Geräte angeschlossen sind)
python dobot_hanoi.py -n 5 -p COM4

# Nur die Zugfolge berechnen und anzeigen, OHNE den Roboter anzusteuern
# (praktisch zum schnellen Testen am Messestand ohne Hardware)
python dobot_hanoi.py --dry-run -n 7
```

## Bekannte Stolperfallen

- **Saugnapf-Timing:** Falls Scheiben gelegentlich fallen gelassen werden,
  `SUCTION_DELAY` erhöhen.
- **USB-Verbindungsprobleme auf Messen:** Das Programm versucht bei
  Verbindungsproblemen automatisch mehrfach neu und gibt eine Checkliste aus
  (Kabel, Treiber, DobotStudio geschlossen?).
- **Scheibenanzahl:** Die Zugzahl wächst exponentiell (2ⁿ − 1). Bei 10
  Scheiben sind das bereits 1023 Züge – für eine Live-Vorführung ggf. bei
  5–7 Scheiben bleiben.

## Lizenz

Nutzung frei für AG-/Schul-/Bildungszwecke.
