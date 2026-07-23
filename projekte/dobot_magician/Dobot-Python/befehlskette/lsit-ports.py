from serial.tools import list_ports

print("Vorhandene COM-Ports:")

ports = list_ports.comports()

if not ports:
    print("Keine COM-Ports gefunden.")
else:
    for port in ports:
        print(
            f"{port.device}: "
            f"{port.description}"
        )