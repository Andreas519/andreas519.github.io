from pathlib import Path
import sys

# Übergeordneten Ordner "projekte" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

import dobot
from sdk64 import DobotDllType as dType

api = dobot.init()


dobot.plattenkalibrierung_setzen(
    referenzloch_1=(40, 3, -54.3, -312.0),
    referenzloch_2=(1, 3, -56.1, 312.2),
    referenzloch_3=(22, 26, 310.5, -18.5),
    platten_z=-67.2,
)

dobot.plattenkalibrierung_anzeigen()

dType.ClearAllAlarmsState(api)

dobot.home(api)

dobot.position_anzeigen(api)