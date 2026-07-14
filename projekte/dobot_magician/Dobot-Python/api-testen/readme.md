### Testen von 'Dobot-Python-API'
#### Dobot-Python-API-Dokumentationen
1. gruppierte Variante: [Dobot-Python-API-Dokumentation.html](https://andreas519.github.io/projekte/dobot_magician/Dobot-Python-API-Dokumentation.html)
2. alphabetische Variante: [Dobot-Magician-Deutsche-Python-API-Dokumentation.html](https://andreas519.github.io/projekte/dobot_magician/Dobot-Python/Dobot-Magician-Deutsche-Python-API-Dokumentation.html)

#### `DobotDllType` importieren
##### eigentlich sollte das funktionieren
in der Befehlszeile

```
>>> %cd 'D:\Github\andreas519.github.io\projekte\dobot_magician\Dobot-Python\sdk64'
>>> import DobotDllType
>>> api = DobotDllType.load()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "D:\Github\andreas519.github.io\projekte\dobot_magician\Dobot-Python\sdk64\DobotDllType.py", line 460, in load
    return CDLL("DobotDll.dll",  RTLD_GLOBAL)
  File "D:\Program Files\Python314\Lib\ctypes\__init__.py", line 433, in __init__
    self._handle = self._load_library(name, mode, handle, winmode)
  File "D:\Program Files\Python314\Lib\ctypes\__init__.py", line 451, in _load_library
    return _LoadLibrary(self._name, winmode)
FileNotFoundError: Could not find module 'DobotDll.dll' (or one of its dependencies).
  Try using the full path with constructor syntax.
```
##### So funktioniert es aus dem Programm  
```Python
from pathlib import Path
import sys

# Übergeordneten Ordner "projekte" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

from sdk64 import DobotDllType as dType

api = dType.init()

```
in der Kommandozeiel erscheint:
```
>>> %Run test.py
Python-Version:     3.14.5
Python-Architektur: 64bit
SDK-Verzeichnis:    D:\Github\andreas519.github.io\projekte\dobot_magician\Dobot-Python\sdk64
DLL-Datei:          D:\Github\andreas519.github.io\projekte\dobot_magician\Dobot-Python\sdk64\DobotDll.dll
DLL vorhanden:      True

FEHLER: Die serielle Schnittstelle COM10 ist nicht verfügbar.

Es wurden keine seriellen Schnittstellen gefunden.

Das Programm wird beendet.

Process ended with exit code 1.
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Python 3.14.5 (D:\Program Files\Python314\python.exe)
```
#### Grundfunktionen des Magician

##### Verhalten beim Einschalten

1. kurzer Peep
2. Status-LED blinkt rot, danach dauerhaft rot
3. Arm wird nicht bewegt

### Verbindung zum Dobot herstellen

```python
import DobotDllType as dType

```


PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

import dobot
from sdk64 import DobotDllType as dType

api = dobot.init()

```

### Übergeordneten Ordner "projekte" in den Python-Suchpfad aufnehmen

```python


PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

import dobot
from sdk64 import DobotDllType as dType

api = dobot.init()

```