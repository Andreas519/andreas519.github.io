import os
from pathlib import Path
import struct

BASE_DIR = Path(__file__).resolve().parent
DLL_PATH = BASE_DIR / "DobotDll.dll"

print("Python:", struct.calcsize("P") * 8, "Bit")
print("Programmordner:", BASE_DIR)
print("DLL:", DLL_PATH)
print("DLL vorhanden:", DLL_PATH.exists())

if not DLL_PATH.exists():
    raise FileNotFoundError(
        "DobotDll.dll wurde nicht gefunden:\n{}".format(DLL_PATH)
    )

# Der Ordner mit den DLL-Dateien ist hier direkt BASE_DIR
_dll_dir_handle = os.add_dll_directory(str(BASE_DIR))

import DobotDllType as dType

api = dType.load()

print("DobotDll.dll wurde erfolgreich geladen.")