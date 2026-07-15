from pathlib import Path
import sys

# Übergeordneten Ordner "Dobot-Python" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

from sdk64 import DobotDllType as dType
import dobot

api = dobot.init()

dobot.position_anzeigen(api)


# dobot.plattenkalibrierung_anzeigen()
# dType.ClearAllAlarmsState(api)
# dobot.home(api)
