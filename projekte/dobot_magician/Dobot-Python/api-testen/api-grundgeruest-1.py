"""
api-grundgeruest-1.py
Verbindet den Dobot Magician 
"""

from pathlib import Path
import os
import sys


COM_PORT = "COM10"
BAUDRATE = 115200

PROGRAMMORDNER = Path(__file__).resolve().parent
DOBOT_ORDNER = PROGRAMMORDNER.parent
SDK_ORDNER = DOBOT_ORDNER / "sdk64"

# DobotDllType.py für Python auffindbar machen.
sys.path.insert(0, str(SDK_ORDNER))

# DobotDll.dll für Windows auffindbar machen.
_dll_verzeichnis = os.add_dll_directory(str(SDK_ORDNER))

import DobotDllType as dType

api = dType.load()
verbunden = False

try:
    verbindung = dType.ConnectDobot(api, COM_PORT, BAUDRATE, )

    print("Verbindungsrückgabe:", verbindung)

    if verbindung[0] != 0:
        raise ConnectionError(
            f"Verbindung über {COM_PORT} fehlgeschlagen "
            f"(Fehlercode {verbindung[0]})."
        )

    verbunden = True
    print("Dobot erfolgreich verbunden.\n")

# Bereich für deinen Programmcode ...

# ... endet hier

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")

