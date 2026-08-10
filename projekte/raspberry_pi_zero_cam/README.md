# Kamera-Projekte mit dem Raspberry Pi Zero W

## Aufgaben



## Einstieg

## Aktueller Entwicklungsstand

- Raspberry Pi Zero W v1.1 eingerichtet
- Raspberry Pi OS 13 „Trixie“ installiert
- Zugriff per SSH und RDP möglich
- Kamera OV5647 wird erkannt
- Testaufnahme ohne Vorschau erfolgreich
- SCP-Bildübertragung wird praktisch erprobt

Stand: 30. Juli 2026

## Test

### Gemeinsame Netzwerkfreigabe 

`D:\Daten\Github\andreas519.github.io\projekte\raspberry_pi_zero_cam\cam_bilder`

Dieser Ordner ist in `.gitignore` aufgenommen.

```Powershell
PS D:\downloads> scp pi@192.168.2.128:/home/pi/test*.jpg D:\Daten\Github\andreas519.github.io\projekte\raspberry_pi_zero_cam\cam_bilder
pi@192.168.2.128's password:
test-1.jpg                                                                            100%  111KB 805.6KB/s   00:00
test-x.jpg                                                                            100%  747KB   1.0MB/s   00:00
test.jpg                                                                              100%  114KB 590.2KB/s   00:00
PS D:\downloads>

PS D:\downloads> dir D:\Daten\Github\andreas519.github.io\projekte\raspberry_pi_zero_cam\cam_bilder


    Verzeichnis: D:\Daten\Github\andreas519.github.io\projekte\raspberry_pi_zero_cam\cam_bilder


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        01.08.2026     10:37         113840 test-1.jpg
-a----        01.08.2026     10:37         765265 test-x.jpg
-a----        01.08.2026     10:37         116644 test.jpg
```

