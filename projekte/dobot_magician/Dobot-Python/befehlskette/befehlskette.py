"""Verständliche Dobot-Befehlsketten mit optionalen Queue-Pausen."""

from pathlib import Path
import sys
import time

VERSION = "3.0"

# # Erwartete Struktur:
# # Dobot-Python/
# # ├── sdk64/
# # └── projektordner/
# #     ├── befehlskette.py
# #     └── befehlskette_beispiel.py
# 
# HAUPTORDNER = Path(__file__).resolve().parent.parent
# if str(HAUPTORDNER) not in sys.path:
#     sys.path.insert(0, str(HAUPTORDNER))
# 
# from sdk64 import DobotDllType as dType
# 
# 
# # Zuordnung unserer verständlichen Befehlsnamen zu den PTP-Modi.
# PTP_BEFEHLE = {
#     "fahre_zu": dType.PTPMode.PTPMOVLXYZMode,
#     "fahre_um": dType.PTPMode.PTPMOVLXYZINCMode,
#     "springe_auf": dType.PTPMode.PTPJUMPXYZMode,
# }
# 

def befehlskette_erstellen(api, befehle):
    """
    Schreibt alle Einträge aus 'befehle' in die Dobot-Queue.

    Aufbau eines Befehls:
        ("befehlsname", x, y, z, r, "Beschreibung")

    Rückgabe:
        Dictionary:
        Queue-Index -> Befehlsnummer, Befehlsname, Koordinaten und Text
    """

    queue_befehle = {}

    for befehlsnummer, befehl in enumerate(befehle, start=1):
        if len(befehl) != 6:
            raise ValueError(
                f"Befehl {befehlsnummer} benötigt genau 6 Einträge: "
                "(Name, X, Y, Z, R, Text)."
            )

        befehlsname, x, y, z, r, text = befehl
        befehlsname = str(befehlsname).lower()

        if befehlsname not in PTP_BEFEHLE:
            erlaubte_befehle = ", ".join(PTP_BEFEHLE)
            raise ValueError(
                f"Unbekannter Befehl '{befehlsname}' in Befehl "
                f"{befehlsnummer}. Erlaubt sind: {erlaubte_befehle}."
            )

        modus = PTP_BEFEHLE[befehlsname]

        queue_index = dType.SetPTPCmd(
            api,
            modus,
            x,
            y,
            z,
            r,
            isQueued=1,
        )[0]

        queue_befehle[queue_index] = {
            "nummer": befehlsnummer,
            "befehl": befehlsname,
            "position": (x, y, z, r),
            "text": text,
        }

    return queue_befehle


def befehlskette_anzeigen(queue_befehle):
    """Zeigt die erstellte Befehlskette vor dem Start vollständig an."""

    print("\nErstellte Befehlskette:")

    for queue_index, daten in queue_befehle.items():
        x, y, z, r = daten["position"]

        print(
            f'{daten["nummer"]:2d}. Queue-Index {queue_index:3d}: '
            f'{daten["befehl"]}({x}, {y}, {z}, {r})'
            f' – {daten["text"]}'
        )


def befehlskette_ausfuehren(api, queue_befehle, timeout=30.0):
    """
    Startet die Queue und zeigt jeden erreichten Befehl in Thonny an.

    Hinweis:
    Die Anzeige erfolgt, sobald der Queue-Index erreicht wurde.
    """

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return

    letzter_queue_index = max(queue_befehle)
    letzter_angezeigter_index = -1
    startzeit = time.monotonic()

    dType.SetQueuedCmdStartExec(api)

    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

        for queue_index in sorted(queue_befehle):
            if letzter_angezeigter_index < queue_index <= aktueller_index:
                daten = queue_befehle[queue_index]

                print(
                    f'Befehl {daten["nummer"]}: '
                    f'{daten["text"]} '
                    f'(Queue-Index {queue_index})'
                )

        letzter_angezeigter_index = max(
            letzter_angezeigter_index,
            aktueller_index,
        )

        if aktueller_index >= letzter_queue_index:
            print("Befehlskette vollständig ausgeführt.")
            return

        if time.monotonic() - startzeit > timeout:
            dType.SetQueuedCmdStopExec(api)
            raise TimeoutError(
                f"Die Befehlskette wurde nicht innerhalb von "
                f"{timeout:.1f} Sekunden beendet."
            )

        dType.dSleep(100)
