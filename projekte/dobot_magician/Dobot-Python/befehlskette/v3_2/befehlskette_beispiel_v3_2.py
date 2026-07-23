"""Testprogramm für befehlskette_v3_2.py.

Programmversion 3.2

Neu:
    sauger_ein
    sauger_aus
    sauger_status

Tastatur:
    p + Enter = Pause
    w + Enter = Weiter
    h + Enter = Halt
    ? + Enter = Status der Befehlskette
"""

from pathlib import Path
import os
import sys


# ------------------------------------------------------------
# Diese Zeilen anpassen
# ------------------------------------------------------------

PORT = "COM10"
BAUDRATE = 115200

STANDARD_PAUSE_MS = 1000
TIMEOUT_SEKUNDEN = 90.0

PROGRAMM_VERSION = "3.2"
ERWARTETE_MODULVERSION = "3.2"


befehle = [
    (
        "fahre_zu",
        180,
        160,
        50,
        0,
        "Fahre zu Punkt 1",
    ),

    (
        "sauger_ein",
        "Sauger einschalten",
        1000,
    ),

    (
        "sauger_status",
        "Status nach dem Einschalten anzeigen",
        0,
    ),

    (
        "fahre_zu",
        240,
        140,
        70,
        0,
        "Fahre zu Punkt 2",
        2500,
    ),

    (
        "sauger_aus",
        "Sauger ausschalten",
        500,
    ),

    (
        "sauger_status",
        "Status nach dem Ausschalten anzeigen",
        0,
    ),

    (
        "fahre_zu",
        200,
        180,
        50,
        0,
        "Fahre zu Punkt 3",
        0,
    ),
]


# ------------------------------------------------------------
# Ab hier nichts mehr ändern
# ------------------------------------------------------------

PROJEKTORDNER = Path(__file__).resolve().parent
HAUPTORDNER = PROJEKTORDNER.parent
SDK_ORDNER = HAUPTORDNER / "sdk64"
DLL_DATEI = SDK_ORDNER / "DobotDll.dll"


if not SDK_ORDNER.exists():
    raise FileNotFoundError(
        f"Der SDK-Ordner wurde nicht gefunden:\n"
        f"{SDK_ORDNER}"
    )

if not DLL_DATEI.exists():
    raise FileNotFoundError(
        f"Die Dobot-DLL wurde nicht gefunden:\n"
        f"{DLL_DATEI}"
    )


if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))


if os.name == "nt":
    os.add_dll_directory(str(SDK_ORDNER))


from sdk64 import DobotDllType as dType
from befehlskette_v3_2 import (
    VERSION,
    VERSIONSDATUM,
    ZUSTAND_HALT,
    befehlskette_erstellen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren_steuerbar,
)


print(
    f"Testprogramm Version {PROGRAMM_VERSION}"
)
print("Programmordner:", PROJEKTORDNER)
print("Hauptordner:   ", HAUPTORDNER)
print("SDK-Ordner:    ", SDK_ORDNER)
print("DobotDllType:  ", Path(dType.__file__).resolve())
print("DLL-Datei:     ", DLL_DATEI)


if ERWARTETE_MODULVERSION == VERSION:
    print(
        f"Korrekte Modulversion {VERSION} "
        f"vom {VERSIONSDATUM} wird verwendet."
    )
else:
    print(
        f"Versionskonflikt: erwartet "
        f"{ERWARTETE_MODULVERSION}, geladen {VERSION}."
    )
    sys.exit()


api = dType.load()

verbindung = dType.ConnectDobot(
    api,
    PORT,
    BAUDRATE,
)

print(f"Verbindungsrückgabe: {verbindung}")

if (
    verbindung[0]
    != dType.DobotConnect.DobotConnect_NoError
):
    raise ConnectionError(
        "Der Dobot konnte nicht verbunden werden."
    )

print("Dobot erfolgreich verbunden.")
print(f"Befehlskettenmodul Version {VERSION}")


try:
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    queue_befehle = befehlskette_erstellen(
        api,
        befehle,
        standard_pause_ms=STANDARD_PAUSE_MS,
    )

    befehlskette_anzeigen(queue_befehle)

    input(
        "\nZum Starten der Befehlskette "
        "Enter drücken ..."
    )

    ergebnis = befehlskette_ausfuehren_steuerbar(
        api,
        queue_befehle,
        timeout=TIMEOUT_SEKUNDEN,
    )

    print(f"\nErgebnis der Ausführung: {ergebnis}")

    if ergebnis == ZUSTAND_HALT:
        print()
        print(
            "Vor einem Neustart müssen Arbeitsplatte "
            "und Dobot kontrolliert werden."
        )
        print(
            "Danach ist eine sichere Ausgangsstellung "
            "herzustellen."
        )


except KeyboardInterrupt:
    print("\nProgrammabbruch über die Tastatur.")

    if hasattr(
        dType,
        "SetQueuedCmdForceStopExec",
    ):
        dType.SetQueuedCmdForceStopExec(api)
    else:
        dType.SetQueuedCmdStopExec(api)


finally:
    dType.SetQueuedCmdStopExec(api)
    dType.DisconnectDobot(api)
    print("\nVerbindung zum Dobot getrennt.")
