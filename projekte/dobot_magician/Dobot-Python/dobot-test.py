import DobotDllType as dType

#print("Python:", struct.calcsize("P") * 8, "Bit")

api = dType.load()
print("DobotDll.dll wurde erfolgreich geladen.")

result = dType.ConnectDobot(api, "COM10", 115200)