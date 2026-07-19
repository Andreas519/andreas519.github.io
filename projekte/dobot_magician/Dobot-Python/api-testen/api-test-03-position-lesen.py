"""
test-03-position-lesen.py

Verbindet den Dobot Magician und liest mit GetPose():
- kartesische Position X, Y, Z
- Werkzeugdrehung R
- Gelenkwinkel J1 bis J4
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
    verbindung = dType.ConnectDobot(
        api,
        COM_PORT,
        BAUDRATE,
    )

    print("Verbindungsrückgabe:", verbindung)

    if verbindung[0] != 0:
        raise ConnectionError(
            f"Verbindung über {COM_PORT} fehlgeschlagen "
            f"(Fehlercode {verbindung[0]})."
        )

    verbunden = True
    print("Dobot erfolgreich verbunden.")
    print()

    pose = dType.GetPose(api)

    print("Rückgabe von GetPose():")
    print(pose)
    print()

    print("Kartesische Position:")
    print(f"  X = {pose[0]:8.2f} mm")
    print(f"  Y = {pose[1]:8.2f} mm")
    print(f"  Z = {pose[2]:8.2f} mm")
    print(f"  R = {pose[3]:8.2f}°")
    print()

    print("Gelenkwinkel:")
    print(f"  J1 = {pose[4]:8.2f}°")
    print(f"  J2 = {pose[5]:8.2f}°")
    print(f"  J3 = {pose[6]:8.2f}°")
    print(f"  J4 = {pose[7]:8.2f}°")

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")