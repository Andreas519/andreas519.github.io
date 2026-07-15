from pathlib import Path
import sys

HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

import dobot

print(dobot.version())

api = dobot.init("COM10")
dobot.alarme_loeschen(api)
dobot.queue_starten(api)

try:
    # dobot.home(api)
    dobot.position_anzeigen(api)

    # Optional: Lochrasterplatte kalibrieren
    # dobot.plattenkalibrierung_setzen(...)
finally:
    dobot.queue_stoppen(api)
