"""Testprogramm für befehlskette_v2.py."""

from pathlib import Path
import sys

# Erwartete Struktur:
# Dobot-Python/
# ├── sdk64/
# └── befehlskette-1/
#     ├── befehlskette_v2.py
#     └── befehlskette_beispiel_v2.py
HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

from sdk64 import DobotDllType as dType
from befehlskette_v2 import (
    VERSION,
    befehlskette_erstellen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren,
)

PORT = "COM13"       # Bei Bedarf anpassen oder "" für automatische Suche.
BAUDRATE = 115200
STANDARD_PAUSE_MS = 1000


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

    befehle = [
        # Verwendet die Standardpause von 1000 ms.
        ("fahre_zu", 180, 160, 50, 0, "Fahre zu Punkt 1"),

        # Überschreibt die Standardpause: 2500 ms.
        ("fahre_zu", 240, 140, 70, 0, "Fahre zu Punkt 2", 2500),

        # Keine Pause nach diesem letzten Befehl.
        ("fahre_zu", 200, 180, 50, 0, "Fahre zu Punkt 3", 0),
    ]

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
