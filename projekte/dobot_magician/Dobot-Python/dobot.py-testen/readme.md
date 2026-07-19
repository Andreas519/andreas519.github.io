# Testen von 'dobot-.py'


## Unsere Dobot-Python-API-Dokumentationen:
1. gruppierte Variante: [Dobot-Python-API-Dokumentation.html](https://andreas519.github.io/projekte/dobot_magician/Dobot-Python-API-Dokumentation.html)
2. alphabetische Variante: [Dobot-Magician-Deutsche-Python-API-Dokumentation.html](https://andreas519.github.io/projekte/dobot_magician/Dobot-Python/Dobot-Magician-Deutsche-Python-API-Dokumentation.html)
## Aufgaben



## Roboter testen
##### eigentlich sollte das funktionieren
```python
from pathlib import Path
import sys

# Übergeordneten Ordner "projekte" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

import dobot
from sdk64 import DobotDllType as dType

api = dobot.init()

dType.ClearAllAlarmsState(api)
dobot.home(api)

dobot.position_anzeigen(api)

# ...

dobot.queue_stoppen(api)
dobot.dType.DisconnectDobot(api)
print("\nVerbindung zum Dobot getrennt.")
```

