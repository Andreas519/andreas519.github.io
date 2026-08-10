# Prompt 09 – Bildtransfer und einstellbare Auflösung

## Prompt

Das Bild soll auf den PC übertragen werden. Die Auflösung soll einstellbar sein.

## Antwort

Es wurden vier Wege vorgeschlagen:

1. Windows holt das Bild per SCP.
2. Raspberry Pi sendet das Bild per SCP.
3. Gemeinsamer Windows-Netzwerkordner.
4. Eigener Python-TCP-Server.

Für die Auflösung wurde eine verständliche Auswahl über Namen vorgeschlagen:

```python
AUFLOESUNGEN = {
    "VGA": (640, 480),
    "HD": (1280, 720),
    "FULLHD": (1920, 1080),
    "MAX": (2592, 1944),
}
```

Später könnte der Aufruf so aussehen:

```python
kamera.foto("FULLHD")
```
