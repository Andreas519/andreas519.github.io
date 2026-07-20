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
    
    dType.ClearAllAlarmsState(api)
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)
# Bereich für deinen Programmcode ...

    befehle = {}       # Dictionary
    
    pos = [180, 160, 50, 0]
    i = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3], isQueued=1, )[0]
    befehle[i] = f"Fahre zu Punkt 1: X={pos[0]}, Y={pos[1]}, Z={pos[2]}"    
    
    pos = [240, 140, 70, 0]
    i = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3], isQueued=1, )[0]
    befehle[i] = f"Fahre zu Punkt 2: X={pos[0]}, Y={pos[1]}, Z={pos[2]}" 

    pos = [240, 140, 70, 0]
    i = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, pos[0], pos[1], pos[2], pos[3], isQueued=1, )[0]
    befehle[i] = f"Fahre zu Punkt 3: X={pos[0]}, Y={pos[1]}, Z={pos[2]}" 

    print("Eingereihte Befehle:")
    for i, beschreibung in befehle.items():
        print(i, beschreibung)

    vorheriger_index = -1

    dType.SetQueuedCmdStartExec(api)
    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

        if aktueller_index != vorheriger_index:
            print()
            print("Queue-Index:", aktueller_index)

            if aktueller_index in befehle:
                print("Befehl abgeschlossen:", befehle[aktueller_index])

            vorheriger_index = aktueller_index

        if aktueller_index >= index_3:
            break

        dType.dSleep(100)

    print()
    print("Alle Fahrbefehle wurden abgearbeitet.")

# ... endet hier




# ... endet hier

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")

