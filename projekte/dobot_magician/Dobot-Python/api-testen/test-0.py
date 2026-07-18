from pathlib import Path
import os
import platform
import sys

# Übergeordneten Ordner "Dobot-Python" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

sdk_verzeichnis = PROJEKTORDNER / "sdk64"
dll_datei = sdk_verzeichnis / "DobotDll.dll"

print("Python-Version:    ", platform.python_version())
print("Python-Architektur:", platform.architecture()[0])
print("SDK-Verzeichnis:   ", sdk_verzeichnis)
print("DLL-Datei:         ", dll_datei)
print("DLL vorhanden:     ", dll_datei.exists())

print()

# DobotDllType.py importieren
from sdk64 import DobotDllType as dType

print("DobotDllType.py:   ", dType.__file__)

print()
print("DLL-Verzeichnis wird zum Windows-DLL-Suchpfad hinzugefügt ...")

# Das Verzeichnis sdk64 für die DLL-Suche registrieren.
# Das Handle muss während des Ladens der DLL erhalten bleiben.
dll_verzeichnis_handle = os.add_dll_directory(str(sdk_verzeichnis))

print("DLL-Verzeichnis registriert.")
print()
print("DobotDll.dll wird geladen ...")

try:
    api = dType.load()

    print("DobotDll.dll wurde erfolgreich geladen.")
    print("API-Objekt:", api)

except Exception as fehler:
    print()
    print("FEHLER beim Laden der DobotDll.dll:")
    print(type(fehler).__name__ + ":", fehler)

    sys.exit(1)

print()
print("Test erfolgreich beendet.")

sys.exit()