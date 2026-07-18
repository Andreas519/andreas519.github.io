from pathlib import Path
import sys

HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

import dobot

print(dobot.version())

api = dobot.init("COM10")

# Alarmzustand prüfen, bevor eine Bewegung gestartet wird.
dobot.alarme_anzeigen(api)

# Queue für HOME-, Fahr- und eingereihte Saugerbefehle starten.
dobot.queue_starten(api)

try:
    dobot.home(api)
    dobot.position_anzeigen(api)
    dobot.lochposition_anzeigen(api)

    dobot.fahre_zu_loch(
        api,
        spalte=20,
        zeile=20,
        hoehe=30.0,
    )

    dobot.sauger_aktivieren(api)
finally:
    dobot.queue_stoppen(api)
