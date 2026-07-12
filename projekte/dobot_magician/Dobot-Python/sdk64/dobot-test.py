import DobotDllType as dType

api = dType.load()
print("DobotDll.dll wurde erfolgreich geladen.")

result = dType.ConnectDobot(api, "COM10", 115200)