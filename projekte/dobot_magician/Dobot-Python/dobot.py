from pathlib import Path
import os
import platform
import ctypes

from sdk64 import DobotDllType as dType

def init():

    # Verzeichnis, in dem dieses Python-Programm liegt
    dll_verzeichnis = Path(__file__).resolve().parent
    dll_datei = dll_verzeichnis / "sdk64\\DobotDll.dll"

    print("Python-Version:", platform.python_version())
    print("Python-Architektur:", platform.architecture())
    print("DLL-Verzeichnis:", dll_verzeichnis)
    print("DLL-Datei:", dll_datei)
    print("DLL vorhanden:", dll_datei.exists())

    # Wichtig: Suchverzeichnis für weitere abhängige DLLs eintragen
    dll_suchpfad = os.add_dll_directory(str(dll_verzeichnis))
     
    # DobotDll.dll über den vollständigen Pfad laden
    api = ctypes.CDLL(str(dll_datei))

    # mit Dobot verbinden 
    result = dType.ConnectDobot(api, "COM10", 115200)
    print("ConnectDobot-Ergebnis:", result)

    dType.SetDeviceName(api, "Dobot Magician - AG Young Engineers - Martin-Rinckart-Gymnasium")

    name = dType.GetDeviceName(api)
    seriennummer = dType.GetDeviceSN(api)

    print("Gerätename:   ", name)
    print("Seriennummer: ", seriennummer)
