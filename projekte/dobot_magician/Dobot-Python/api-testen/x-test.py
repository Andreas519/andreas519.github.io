from pathlib import Path
import os
import platform
import sys

PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

sdk_verzeichnis = PROJEKTORDNER / "sdk64"
dll_datei = sdk_verzeichnis / "DobotDll.dll"

from sdk64 import DobotDllType as dType

dll_verzeichnis_handle = os.add_dll_directory(str(sdk_verzeichnis))

COM_PORT = "COM10"

try:
    api = dType.load()
    zustand = dType.ConnectDobot(api, COM_PORT, 115200)
    if zustand[0] != dType.DobotConnect.DobotConnect_NoError:
        print("Verbindung fehlgeschlagen:", zustand)
        sys.exit()

except Exception as fehler:
    print("FEHLER beim Laden der DobotDll.dll:")
    print(type(fehler).__name__ + ":", fehler)
    sys.exit(1)


print("Dobot verbunden")
print(" - Seriennummer:     ",dType.GetDeviceSN(api))
print(" - Positionsangaben: ",dType.GetPose(api))

dType.DisconnectDobot(api)