# dobot-test-1.py
from pathlib import Path
import sys

# Übergeordneten Ordner "Dobot-Python" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

from sdk64 import DobotDllType as dType

xxxx

import dobot

api = dobot.init("COM13")
dobot.alarme_anzeigen(api)
dobot.position_anzeigen(api)

#bisher keine Aktionen des Dobot

dobot.queue_starten(api)
dobot.test_z(api)