from pathlib import Path
import os
import sys

# diese Zeilen anpassen

PORT = "COM10"
BAUDRATE = 115200
STANDARD_PAUSE_MS = 1000


befehle = [
    # Verwendet die Standardpause von 1000 ms.
    ("fahre_zu", 180, 160, 50, 0, "Fahre zu Punkt 1"),

    # Überschreibt die Standardpause: 2500 ms.
    ("fahre_zu", 240, 140, 70, 0, "Fahre zu Punkt 2", 2500),

    # Keine Pause nach diesem letzten Befehl.
    ("fahre_zu", 200, 180, 50, 0, "Fahre zu Punkt 3", 0),
]

# ab hier nichts mehr ändern

PROJEKTORDNER = Path(__file__).resolve().parent
HAUPTORDNER = PROJEKTORDNER.parent
SDK_ORDNER = HAUPTORDNER / "sdk64"
DLL_DATEI = SDK_ORDNER / "DobotDll.dll"


if not SDK_ORDNER.exists():
    raise FileNotFoundError(
        f"Der SDK-Ordner wurde nicht gefunden:\n{SDK_ORDNER}"
    )

if not DLL_DATEI.exists():
    raise FileNotFoundError(
        f"Die Dobot-DLL wurde nicht gefunden:\n{DLL_DATEI}"
    )


# Zuerst den richtigen Hauptordner eintragen.
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))


# Unter Windows den DLL-Ordner ausdrücklich bekannt machen.

dll_verzeichnis_handle = None

if os.name == "nt":
    dll_verzeichnis_handle = os.add_dll_directory(
        str(SDK_ORDNER)
    )
    
from ctypes import CDLL
from sdk64 import DobotDllType as dType
from befehlskette import (
    VERSION,
    befehlskette_erstellen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren,
)


print("Programmordner:", PROJEKTORDNER)
print("Hauptordner:   ", HAUPTORDNER)
print("SDK-Ordner:    ", SDK_ORDNER)
print("DobotDllType:  ", Path(dType.__file__).resolve())
print("DLL-Datei:     ", DLL_DATEI)

print("... lade api ...!")
# api = dType.load()
print()
print(f"DLL wird geladen: {DLL_DATEI}", flush=True)

api = CDLL(str(DLL_DATEI))

print("DobotDll.dll wurde erfolgreich geladen.", flush=True)



# Verbindung hier wie bisher herstellen.
# Vor dem Erstellen einer neuen Queue sollte sie angehalten und geleert werden.

dType.SetQueuedCmdStopExec(api)
dType.SetQueuedCmdClear(api)


befehle = [
    # Verwendet die Standardpause von 1000 ms.
    ("fahre_zu", 180, 160, 50, 0, "Fahre zu Punkt 1"),

    # Überschreibt die Standardpause: 2500 ms.
    ("fahre_zu", 240, 140, 70, 0, "Fahre zu Punkt 2", 2500),

    # Keine Pause nach diesem letzten Befehl.
    ("fahre_zu", 200, 180, 50, 0, "Fahre zu Punkt 3", 0),
]


queue_befehle = befehlskette_erstellen(api, befehle)

befehlskette_anzeigen(queue_befehle)

input("\nZum Starten der Befehlskette Enter drücken ...")

befehlskette_ausfuehren(api, queue_befehle)
