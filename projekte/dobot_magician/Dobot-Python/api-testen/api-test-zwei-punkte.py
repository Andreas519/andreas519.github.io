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
    print("Dobot erfolgreich verbunden.\n")

    pose = dType.GetPose(api)
    print("GetPose() : ", pose[:3])
    dType.ClearAllAlarmsState(api)
    dType.dSleep(300)
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)
#    dType.SetQueuedCmdStartExec(api)
    print(" - Queue-Index nach Neustart: ", dType.GetQueuedCmdCurrentIndex(api))
    
#
    ziel_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,
            210, 160, 50, 0, isQueued=1, )[0]
    dType.dSleep(00)
    ziel_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,
            190, 140, 90, 0, isQueued=1, )[0]
    dType.dSleep(00)
    ziel_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode,
            230, 200, 0, 0, isQueued=1, )[0]
    dType.dSleep(00)
    print("Start die Queue")
    dType.SetQueuedCmdStartExec(api)
#
    

finally:
    print("Weiter in der Befehlszeile")
#     if verbunden:
#         dType.DisconnectDobot(api)
#         print()
#         print("Verbindung zum Dobot getrennt.")
