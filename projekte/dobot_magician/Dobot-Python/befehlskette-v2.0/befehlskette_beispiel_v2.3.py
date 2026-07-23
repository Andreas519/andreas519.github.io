from pathlib import Path
import os
import sys

# diese Zeilen anpassen

PORT = "COM10"
BAUDRATE = 115200
STANDARD_PAUSE_MS = 1000
version = "2.3" 

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
if os.name == "nt":
    os.add_dll_directory(str(SDK_ORDNER))


from sdk64 import DobotDllType as dType
from befehlskette_v2_3 import (
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

if version==VERSION:
    print(f"korrekte Version {VERSION} wird verwendet")
else:
    print(f" Versionskonflikt {version} - {VERSION}")
    sys.exit()

api = dType.load()


verbindung = dType.ConnectDobot(api, PORT, BAUDRATE)
print(f"Verbindungsrückgabe: {verbindung}")

if verbindung[0] != dType.DobotConnect.DobotConnect_NoError:
    raise ConnectionError("Der Dobot konnte nicht verbunden werden.")

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
    input("\nZum Starten der Befehlskette Enter drücken ...")
    befehlskette_ausfuehren(api, queue_befehle, timeout=60.0)

finally:
    dType.SetQueuedCmdStopExec(api)
    dType.DisconnectDobot(api)
    print("\nVerbindung zum Dobot getrennt.")
