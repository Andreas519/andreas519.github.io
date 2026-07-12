from pathlib import Path
import sys

# Übergeordneten Ordner "projekte" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

import dobot
from sdk64 import DobotDllType as dType

dobot.init()