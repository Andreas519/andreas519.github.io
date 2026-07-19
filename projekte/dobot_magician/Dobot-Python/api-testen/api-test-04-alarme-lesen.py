"""
test-04-alarme-lesen.py

Verbindet den Dobot Magician, liest den Alarmstatus und zeigt
die Nummern aller aktiven Alarme an.
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

    alarmdaten, laenge = dType.GetAlarmsState(api)

    print("Rückgabe von GetAlarmsState():")
    print("Alarmdaten:", alarmdaten)
    print("Länge:     ", laenge)
    print()

    aktive_alarme = []

    for byte_index, byte_wert in enumerate(alarmdaten[:laenge]):
        for bit_index in range(8):
            if byte_wert & (1 << bit_index):
                alarmnummer = byte_index * 8 + bit_index
                aktive_alarme.append(alarmnummer)

    if not aktive_alarme:
        print("Keine Alarme aktiv.")
    else:
        print(f"{len(aktive_alarme)} Alarm(e) aktiv:")

        for alarmnummer in aktive_alarme:
            print(
                f"  Alarm {alarmnummer:3d} "
                f"(0x{alarmnummer:02X})"
            )

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")
