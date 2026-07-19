"""
test-06-sofort-fahren.py

Verbindet den Dobot Magician und sendet genau einen
PTP-Fahrbefehl sofort, also ohne Queue.
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

    print("Aktuelle Position:")
    print(f"  X = {pose[0]:8.2f} mm")
    print(f"  Y = {pose[1]:8.2f} mm")
    print(f"  Z = {pose[2]:8.2f} mm")
    print(f"  R = {pose[3]:8.2f}°")
    print()

    ziel_x = float(
        input("Ziel X in mm: ").replace(",", ".")
    )
    ziel_y = float(
        input("Ziel Y in mm: ").replace(",", ".")
    )
    ziel_z = float(
        input("Ziel Z in mm: ").replace(",", ".")
    )

    bestaetigung = input(
        "Fahrt sofort starten? (j/n): "
    ).strip().lower()

    if bestaetigung == "j":
        # Laufende Queue-Befehle dürfen den Test nicht überlagern.
        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdClear(api)

        rueckgabe = dType.SetPTPCmd(
            api,
            dType.PTPMode.PTPMOVJXYZMode,
            ziel_x,
            ziel_y,
            ziel_z,
            pose[3],
            isQueued=0,
        )

        print()
        print("Rückgabe von SetPTPCmd():", rueckgabe)
        print("Der Fahrbefehl wurde sofort gesendet.")

        input(
            "Nach Abschluss der Bewegung Enter drücken: "
        )

        neue_pose = dType.GetPose(api)

        print()
        print("Position nach der Bewegung:")
        print(f"  X = {neue_pose[0]:8.2f} mm")
        print(f"  Y = {neue_pose[1]:8.2f} mm")
        print(f"  Z = {neue_pose[2]:8.2f} mm")
        print(f"  R = {neue_pose[3]:8.2f}°")
    else:
        print("Die Fahrt wurde nicht ausgeführt.")

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")
