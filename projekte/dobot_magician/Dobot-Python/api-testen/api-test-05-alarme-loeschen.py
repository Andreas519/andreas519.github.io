"""
test-05-alarme-loeschen.py

Verbindet den Dobot Magician, zeigt die aktiven Alarme,
löscht sie und prüft den Alarmstatus erneut.
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


def alarmnummern_lesen():
    """Liest die Nummern aller aktiven Alarme."""

    alarmdaten, laenge = dType.GetAlarmsState(api)
    alarmnummern = []

    for byte_index, byte_wert in enumerate(alarmdaten[:laenge]):
        for bit_index in range(8):
            if byte_wert & (1 << bit_index):
                alarmnummern.append(
                    byte_index * 8 + bit_index
                )

    return alarmnummern


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

    alarme_vorher = alarmnummern_lesen()

    print("Alarme vor dem Löschen:", alarme_vorher)

    dType.ClearAllAlarmsState(api)
    dType.dSleep(300)

    alarme_nachher = alarmnummern_lesen()

    print("Alarme nach dem Löschen:", alarme_nachher)
    print()

    if not alarme_nachher:
        print("Alle Alarme wurden gelöscht.")
    else:
        print(
            "Mindestens ein Alarm ist weiterhin aktiv. "
            "Die Alarmursache besteht noch."
        )

finally:
    if verbunden:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot getrennt.")
