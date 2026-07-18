from pathlib import Path
import sys

# Übergeordneten Ordner "Dobot-Python" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

from sdk64 import DobotDllType as dType

# 
# if result[0] != dType.DobotConnect.DobotConnect_NoError:
#     print("Verbindung fehlgeschlagen.")
#     raise SystemExit
# 
# try:
#     dType.SetQueuedCmdStopExec(api)
#     dType.SetQueuedCmdClear(api)
#     dType.SetPTPCommonParams( api, 20, 20, 0)
#     pose = dType.GetPose(api)
#     x, y, z, r = pose[:4]
#     
#     print(f"Position: "f"X={x:.1f}, "f"Y={y:.1f}, "f"Z={z:.1f}, "f"R={r:.1f}")
#     
#     ziel_index = dType.SetPTPCmd(api,dType.PTPMode.PTPMOVLXYZMode, x+50, y+50, z + 20,r, isQueued=1)[0]
# 
#     dType.SetQueuedCmdStartExec(api)
#     while dType.GetQueuedCmdCurrentIndex(api)[0] < ziel_index:
#         dType.dSleep(100)
# 
# finally:
#     dType.SetQueuedCmdStopExec(api)
#     dType.DisconnectDobot(api)
# 