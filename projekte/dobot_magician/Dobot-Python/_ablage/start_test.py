from pathlib import Path
import struct

# dll = Path(r"D:\Programme\DobotStudio\DobotDll.dll")
# dll = Path(r".\sdk-64\DobotDll.dll")
dll = Path(r".\sdk-32\DobotDll.dll")

with dll.open("rb") as datei:
    datei.seek(0x3C)
    pe_offset = struct.unpack("<I", datei.read(4))[0]

    datei.seek(pe_offset + 4)
    machine = struct.unpack("<H", datei.read(2))[0]

typen = {
    0x014C: "32-Bit (x86)",
    0x8664: "64-Bit (x64)",
    0xAA64: "64-Bit ARM",
}

print("Datei:", dll)
print("Typ:", typen.get(machine, f"Unbekannt: 0x{machine:04X}"))