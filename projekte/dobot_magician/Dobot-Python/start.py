from pathlib import Path
import os
import struct
import sys


# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

COM_PORT = "COM10"
BAUDRATE = 115200

# Allgemeine PTP-Geschwindigkeit und -Beschleunigung in Prozent
PTP_GESCHWINDIGKEIT = 20
PTP_BESCHLEUNIGUNG = 20


# ------------------------------------------------------------
# Pfade vorbereiten
# ------------------------------------------------------------

# Ordner, in dem diese start.py liegt
BASE_DIR = Path(__file__).resolve().parent

# In diesem Ordner liegen DobotDll.dll und die abhängigen DLLs
DLL_DIR = BASE_DIR

# Windows-DLL-Suchpfad ergänzen
_dll_dir_handle = os.add_dll_directory(str(DLL_DIR))

# Python soll auch Module aus dem Programmordner finden
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ------------------------------------------------------------
# Dobot-API laden
# ------------------------------------------------------------

import DobotDllType as dType


def main():
    print("Dobot Magician – Python-Startprogramm")
    print("------------------------------------")
    print("Python:", struct.calcsize("P") * 8, "Bit")
    print("Programmordner:", BASE_DIR)
    print("COM-Port:", COM_PORT)

    dll_datei = DLL_DIR / "DobotDll.dll"

    if not dll_datei.exists():
        print()
        print("FEHLER: DobotDll.dll wurde nicht gefunden.")
        print("Erwarteter Pfad:", dll_datei)
        return

    api = dType.load()
    print("DobotDll.dll wurde geladen.")

    verbindung = dType.ConnectDobot(
        api,
        COM_PORT,
        BAUDRATE
    )

    status = verbindung[0]

    if status != dType.DobotConnect.DobotConnect_NoError:
        print()
        print("Verbindung fehlgeschlagen.")

        if status == dType.DobotConnect.DobotConnect_NotFound:
            print("Der Dobot wurde an", COM_PORT, "nicht gefunden.")

        elif status == dType.DobotConnect.DobotConnect_Occupied:
            print(COM_PORT, "ist belegt oder nicht verfügbar.")
            print("Bitte DobotStudio schließen.")

        else:
            print("Unbekannter Statuscode:", status)

        return

    print("Dobot erfolgreich verbunden.")
    print("Verbindungsdaten:", verbindung)

    try:
        # Aktuelle Position lesen
        pose = dType.GetPose(api)

        print()
        print("Aktuelle Position:")
        print("X  = {:.2f} mm".format(pose[0]))
        print("Y  = {:.2f} mm".format(pose[1]))
        print("Z  = {:.2f} mm".format(pose[2]))
        print("R  = {:.2f} °".format(pose[3]))
        print("J1 = {:.2f} °".format(pose[4]))
        print("J2 = {:.2f} °".format(pose[5]))
        print("J3 = {:.2f} °".format(pose[6]))
        print("J4 = {:.2f} °".format(pose[7]))

        # PTP-Geschwindigkeit reduzieren
        dType.SetPTPCommonParams(
            api,
            PTP_GESCHWINDIGKEIT,
            PTP_BESCHLEUNIGUNG,
            0
        )

        print()
        print(
            "PTP-Geschwindigkeit:",
            PTP_GESCHWINDIGKEIT,
            "%"
        )
        print(
            "PTP-Beschleunigung:",
            PTP_BESCHLEUNIGUNG,
            "%"
        )

        # Hier kann später das eigentliche Programm stehen
        print()

        print("Dobot ist bereit.")

    finally:
        dType.DisconnectDobot(api)
        print()
        print("Verbindung zum Dobot wurde getrennt.")


if __name__ == "__main__":
    main()
