""" befehlskette_beispiel.py
Verbindet den Dobot Magician, importiert das Modul 'befehlskette.py'
und startet
"""

from pathlib import Path
import os
import sys

COM_PORT = "COM10"
BAUDRATE = 115200

PROGRAMMORDNER = Path(__file__).resolve().parent
DOBOT_ORDNER = PROGRAMMORDNER.parent
SDK_ORDNER = DOBOT_ORDNER / "sdk64"

sys.path.insert(0, str(SDK_ORDNER))

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

    from befehlskette import (
        befehlskette_erstellen,
        befehlskette_anzeigen,
        befehlskette_ausfuehren,
    )

    # Verbindung hier wie bisher herstellen.
    # Vor dem Erstellen einer neuen Queue sollte sie angehalten und geleert werden.
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)


    befehle = [
        ("fahre_zu",   200, 125,  20, 79, "Fahre zum Startpunkt"),
        ("fahre_um",    20,  14,   0,  0, "Kleine Verschiebung"),
        ("springe_auf", 200, 140, -40,  0, "Sprung über den Kasten"),
    ]

    queue_befehle = befehlskette_erstellen(
        api,
        befehle,
        standard_pause_ms=5000,
    )
    befehlskette_anzeigen(queue_befehle)

    input("\nZum Starten der Befehlskette Enter drücken ...")

    befehlskette_ausfuehren(api, queue_befehle)




# ... endet hier

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")
