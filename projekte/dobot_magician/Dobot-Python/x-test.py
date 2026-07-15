from pathlib import Path
import os
from sdk64 import DobotDllType as dType

sdk_verzeichnis = Path(__file__).resolve().parent / "sdk64"
os.add_dll_directory(str(sdk_verzeichnis))

api = dType.load()
COM_PORT = "COM10"

zustand = dType.ConnectDobot(api, COM_PORT, 115200)

if zustand[0] == dType.DobotConnect.DobotConnect_NoError:
    print("Dobot verbunden")
    print(" - Seriennummer:     ",dType.GetDeviceSN(api))
    print(" - Positionsangaben: ",dType.GetPose(api))
else:
    print("Verbindung fehlgeschlagen:", zustand)

dType.DisconnectDobot(api)