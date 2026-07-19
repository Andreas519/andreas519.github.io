"""
test-10-sauger-status.py

Liest den aktuellen Schaltzustand des Saugers.
Der Wert zeigt den Pumpenbefehl, nicht einen gemessenen Unterdruck.
"""

from pathlib import Path
import os
import sys
import time


COM_PORT = "COM10"
BAUDRATE = 115200

PROGRAMMORDNER = Path(__file__).resolve().parent
DOBOT_ORDNER = PROGRAMMORDNER.parent
SDK_ORDNER = DOBOT_ORDNER / "sdk64"

# DobotDllType.py für Python auffindbar machen.
sys.path.insert(0, str(SDK_ORDNER))

# DobotDll.dll für Windows auffindbar machen.
_dll_verzeichnis = None
if hasattr(os, "add_dll_directory"):
    _dll_verzeichnis = os.add_dll_directory(str(SDK_ORDNER))

import DobotDllType as dType


def alarme_lesen(api):
    """Liest die Nummern aller aktiven Alarme."""

    alarmdaten, laenge = dType.GetAlarmsState(api)
    aktive_alarme = []

    for byte_index, byte_wert in enumerate(alarmdaten[:laenge]):
        for bit_index in range(8):
            if byte_wert & (1 << bit_index):
                aktive_alarme.append(
                    byte_index * 8 + bit_index
                )

    return aktive_alarme


def warten_bis_fertig(api, ziel_index, timeout=30.0):
    """Wartet mit Alarmprüfung und Zeitbegrenzung."""

    startzeit = time.monotonic()

    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

        if aktueller_index >= ziel_index:
            return

        aktive_alarme = alarme_lesen(api)

        if aktive_alarme:
            alarmcodes = ", ".join(
                f"0x{alarmnummer:02X}"
                for alarmnummer in aktive_alarme
            )

            raise RuntimeError(
                "Befehl wegen eines Alarms nicht beendet: "
                f"{alarmcodes}"
            )

        if time.monotonic() - startzeit > timeout:
            raise TimeoutError(
                f"Queue-Befehl {ziel_index} wurde nicht "
                f"innerhalb von {timeout:.1f} Sekunden beendet."
            )

        dType.dSleep(100)


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

    rueckgabe = dType.GetEndEffectorSuctionCup(api)
    sauger_ein = bool(rueckgabe[0])

    print("Rückgabe von GetEndEffectorSuctionCup():")
    print(rueckgabe)
    print()

    if sauger_ein:
        print("Der Sauger ist eingeschaltet.")
    else:
        print("Der Sauger ist ausgeschaltet.")

    print()
    print(
        "Hinweis: Der Wert bestätigt nur den Schaltzustand "
        "der Pumpe, nicht das sichere Ansaugen eines Werkstücks."
    )

finally:
    if verbunden:
        dType.DisconnectDobot(api)

        print()
        print("Verbindung zum Dobot getrennt.")
