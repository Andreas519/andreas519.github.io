from pathlib import Path
import os
import platform
import sys


# ------------------------------------------------------------
# Projekt- und SDK-Pfade
# ------------------------------------------------------------

PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

sdk_verzeichnis = PROJEKTORDNER / "sdk64"
dll_datei = sdk_verzeichnis / "DobotDll.dll"


# ------------------------------------------------------------
# Python- und DLL-Informationen
# ------------------------------------------------------------

print("Python-Version:    ", platform.python_version())
print("Python-Architektur:", platform.architecture()[0])
print("SDK-Verzeichnis:   ", sdk_verzeichnis)
print("DLL-Datei:         ", dll_datei)
print("DLL vorhanden:     ", dll_datei.exists())

print()


# ------------------------------------------------------------
# DobotDllType.py importieren
# ------------------------------------------------------------

from sdk64 import DobotDllType as dType

print("DobotDllType.py:   ", dType.__file__)


# ------------------------------------------------------------
# DLL-Verzeichnis registrieren
# ------------------------------------------------------------

print()
print("DLL-Verzeichnis wird zum Windows-DLL-Suchpfad hinzugefügt ...")

dll_verzeichnis_handle = os.add_dll_directory(str(sdk_verzeichnis))

print("DLL-Verzeichnis registriert.")


# ------------------------------------------------------------
# DobotDll.dll laden
# ------------------------------------------------------------

print()
print("DobotDll.dll wird geladen ...")

try:
    api = dType.load()

    print("DobotDll.dll wurde erfolgreich geladen.")

except Exception as fehler:
    print()
    print("FEHLER beim Laden der DobotDll.dll:")
    print(type(fehler).__name__ + ":", fehler)

    sys.exit(1)


# ------------------------------------------------------------
# Verbindung zum Dobot herstellen
# ------------------------------------------------------------

COMPORT = "COM10"
BAUDRATE = 115200

print()
print(f"Verbindung zum Dobot über {COMPORT} wird hergestellt ...")

verbindung = dType.ConnectDobot(api, COMPORT, BAUDRATE)

verbindungsstatus = verbindung[0]

if verbindungsstatus == dType.DobotConnect.DobotConnect_NoError:
    print("Dobot erfolgreich verbunden.")

elif verbindungsstatus == dType.DobotConnect.DobotConnect_NotFound:
    print("FEHLER: Dobot wurde nicht gefunden.")
    sys.exit(1)

elif verbindungsstatus == dType.DobotConnect.DobotConnect_Occupied:
    print("FEHLER: Die Schnittstelle ist belegt oder nicht verfügbar.")
    sys.exit(1)

else:
    print("FEHLER: Unbekannter Verbindungsstatus:", verbindungsstatus)
    sys.exit(1)


# ------------------------------------------------------------
# Statusinformationen abfragen
# ------------------------------------------------------------

try:
    print()
    print("=" * 60)
    print("AKTUELLER DOBOT-STATUS")
    print("=" * 60)

    # --------------------------------------------------------
    # Verbindungsinformationen
    # --------------------------------------------------------

    print()
    print("Verbindung:")
    print("  COM-Port:       ", COMPORT)
    print("  Baudrate:       ", BAUDRATE)
    print("  Statuscode:     ", verbindungsstatus)

    if len(verbindung) > 1:
        print("  Firmware-Typ:   ", verbindung[1])

    if len(verbindung) > 2:
        print("  Firmware-Version:", verbindung[2])


    # --------------------------------------------------------
    # Geräteinformationen
    # --------------------------------------------------------

    print()
    print("Geräteinformationen:")

    seriennummer = dType.GetDeviceSN(api)
    geraetename = dType.GetDeviceName(api)
    version = dType.GetDeviceVersion(api)

    print("  Seriennummer:", seriennummer)
    print("  Gerätename:  ", geraetename)
    print(
        "  Version:     ",
        f"{version[0]}.{version[1]}.{version[2]}"
    )


    # --------------------------------------------------------
    # Aktuelle Position
    # --------------------------------------------------------

    pose = dType.GetPose(api)

    print()
    print("Aktuelle Position:")

    print(f"  x:      {pose[0]:8.3f} mm")
    print(f"  y:      {pose[1]:8.3f} mm")
    print(f"  z:      {pose[2]:8.3f} mm")
    print(f"  r:      {pose[3]:8.3f} °")

    print()
    print("Gelenkwinkel:")

    print(f"  Joint 1: {pose[4]:8.3f} °")
    print(f"  Joint 2: {pose[5]:8.3f} °")
    print(f"  Joint 3: {pose[6]:8.3f} °")
    print(f"  Joint 4: {pose[7]:8.3f} °")


    # --------------------------------------------------------
    # Alarmstatus
    # --------------------------------------------------------

    alarmdaten = dType.GetAlarmsState(api)

    alarm_bytes = alarmdaten[0]
    alarm_laenge = alarmdaten[1]

    print()
    print("Alarmstatus:")
    print("  Anzahl Alarm-Bytes:", alarm_laenge)

    aktive_alarme = []

    for byte_index, byte_wert in enumerate(alarm_bytes[:alarm_laenge]):

        for bit_index in range(8):

            if byte_wert & (1 << bit_index):

                alarm_id = byte_index * 8 + bit_index
                aktive_alarme.append(alarm_id)

    if aktive_alarme:
        print("  Aktive Alarm-IDs:", aktive_alarme)
        print("  Status:           ALARM")
    else:
        print("  Aktive Alarm-IDs: keine")
        print("  Status:           OK")


    print()
    print("=" * 60)
    print("STATUSABFRAGE ERFOLGREICH")
    print("=" * 60)


# ------------------------------------------------------------
# Verbindung immer sauber trennen
# ------------------------------------------------------------

finally:

    print()
    print("Verbindung zum Dobot wird getrennt ...")

    dType.DisconnectDobot(api)

    print("Verbindung getrennt.")