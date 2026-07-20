"""
test-08-queue-fahren.py

Fährt den Dobot über die Queue um 10 mm nach oben.
Während des Wartens werden Alarme und ein Zeitlimit überwacht.
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
    pose = dType.GetPose(api)
    ziel_x = pose[0]
    ziel_y = pose[1]
    ziel_z = pose[2] + 10.0
    ziel_r = pose[3]

    print("Aktuelle Position:")
    print(
        f"X={pose[0]:.2f}, Y={pose[1]:.2f}, "
        f"Z={pose[2]:.2f}, R={pose[3]:.2f}"
    )
    print()
    print("Queue-Ziel: 10 mm nach oben")
    print(
        f"X={ziel_x:.2f}, Y={ziel_y:.2f}, "
        f"Z={ziel_z:.2f}, R={ziel_r:.2f}"
    )

    bestaetigung = input(
        "Fahrt über die Queue starten? (j/n): "
    ).strip().lower()

    if bestaetigung != "j":
        print("Die Fahrt wurde nicht ausgeführt.")
    else:
        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdClear(api)
        dType.SetQueuedCmdStartExec(api)
        print(" - Queue-Index nach Neustart: ", dType.GetQueuedCmdCurrentIndex(api))

        ziel_index = dType.SetPTPCmd(
            api,
            dType.PTPMode.PTPMOVLXYZMode,
            ziel_x,
            ziel_y,
            ziel_z,
            ziel_r,
            isQueued=1,
        )[0]

        print("Queue-Index:", ziel_index)

        warten_bis_fertig(
            api,
            ziel_index,
            timeout=30.0,
        )

        neue_pose = dType.GetPose(api)

        print()
        print("Fahrt abgeschlossen.")
        print(
            f"X={neue_pose[0]:.2f}, Y={neue_pose[1]:.2f}, "
            f"Z={neue_pose[2]:.2f}, R={neue_pose[3]:.2f}"
        )

finally:
    if verbunden:
        dType.SetQueuedCmdStopExec(api)
        dType.DisconnectDobot(api)

        print()
        print("Queue gestoppt.")
        print("Verbindung zum Dobot getrennt.")
