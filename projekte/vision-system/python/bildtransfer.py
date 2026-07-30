"""Bildübertragung vom Raspberry Pi auf einen Windows-PC per SCP."""

from __future__ import annotations

import subprocess
from pathlib import Path


def hole_bild(
    host: str = "raspi-zero-xx",
    benutzer: str = "pi",
    entfernte_datei: str = "/home/pi/test.jpg",
    zielordner: str | Path = r"D:\Kamera\Bilder",
) -> Path:
    """Holt eine Bilddatei per SCP und gibt ihren lokalen Pfad zurück."""
    ziel = Path(zielordner)
    ziel.mkdir(parents=True, exist_ok=True)
    lokale_datei = ziel / Path(entfernte_datei).name
    quelle = f"{benutzer}@{host}:{entfernte_datei}"

    try:
        subprocess.run(["scp", quelle, str(lokale_datei)], check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Der Befehl 'scp' wurde auf diesem PC nicht gefunden.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"SCP-Übertragung fehlgeschlagen: {quelle}") from exc

    return lokale_datei


if __name__ == "__main__":
    datei = hole_bild()
    print(f"Bild gespeichert: {datei}")
