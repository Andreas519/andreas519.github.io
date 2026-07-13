from pathlib import Path
import os
import platform
import ctypes

import DobotDllType as dType


# Verzeichnis, in dem dieses Python-Programm liegt
dll_verzeichnis = Path(__file__).resolve().parent
dll_datei = dll_verzeichnis / "DobotDll.dll"

print("Python-Version:", platform.python_version())
print("Python-Architektur:", platform.architecture())
print("DLL-Verzeichnis:", dll_verzeichnis)
print("DLL-Datei:", dll_datei)
print("DLL vorhanden:", dll_datei.exists())

# Wichtig: Suchverzeichnis für weitere abhängige DLLs eintragen
dll_suchpfad = os.add_dll_directory(str(dll_verzeichnis))

# DobotDll.dll über den vollständigen Pfad laden
api = ctypes.CDLL(str(dll_datei))

print("DobotDll.dll wurde erfolgreich geladen.")

result = dType.ConnectDobot(api, "COM10", 115200)
print("ConnectDobot-Ergebnis:", result)