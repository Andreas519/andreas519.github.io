from pathlib import Path
import os
import struct
import sys


# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

COM_PORT = "COM10"
BAUDRATE = 115200

PTP_GESCHWINDIGKEIT = 20
PTP_BESCHLEUNIGUNG = 20


# ------------------------------------------------------------
# Ordner bestimmen
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SDK_DIR = BASE_DIR / "dobot_sdk"


# ------------------------------------------------------------
# Dateien prüfen
# ------------------------------------------------------------

if not SDK_DIR.exists():
    raise FileNotFoundError(
        "Der Ordner 'dobot_sdk' wurde nicht gefunden:\n{}".format(SDK_DIR)
    )

dll_datei = SDK_DIR / "DobotDll.dll"
api_datei = SDK_DIR / "DobotDllType.py"

if not dll_datei.exists():
    raise FileNotFoundError(
        "DobotDll.dll wurde nicht gefunden:\n{}".format(dll_datei)
    )

if not api_datei.exists():
    raise FileNotFoundError(
        "DobotDllType.py wurde nicht gefunden:\n{}".format(api_datei)
    )


# ------------------------------------------------------------
# Suchpfade einrichten
# ------------------------------------------------------------

sys.path.insert(0, str(SDK_DIR))
_dll_dir_handle = os.add_dll_directory(str(SDK_DIR))

import DobotDllType as dType


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------

def main():
    print("Dobot Magician – Startprogramm")
    print("--------------------------------")
    print("Python:", struct.calcsize("P") * 8, "Bit")
    print("Programmordner:", BASE_DIR)
    print("SDK-Ordner:", SDK_DIR)
    print("COM-Port:", COM_PORT)

    if struct.calcsize("P") * 8 != 32:
        print()
        print("FEHLER: Für diese DobotDll.dll wird 32-Bit-Python benötigt.")
        return

    api = dType.load()
    print("DobotDll.dll wurde erfolgreich geladen.")

    verbindung = dType.ConnectDobot(api, COM_PORT, BAUDRATE)
    print("Rückgabe:", verbindung)

    status = verbindung[0]

    if status != dType.DobotConnect.DobotConnect_NoError:
        print()

        if status == dType.DobotConnect.DobotConnect_NotFound:
            print("Der Dobot wurde an {} nicht gefunden.".format(COM_PORT))

        elif status == dType.DobotConnect.DobotConnect_Occupied:
            print("{} ist belegt oder nicht verfügbar.".format(COM_PORT))
            print("Bitte DobotStudio schließen.")

        else:
            print("Unbekannter Verbindungsstatus:", status)

        return

    print("Dobot erfolgreich verbunden.")

    try:
        dType.SetPTPCommonParams(
            api,
            PTP_GESCHWINDIGKEIT,
            PTP_BESCHLEUNIGUNG,
            0
        )

        print(
            "PTP-Einstellungen: {} % Geschwindigkeit, "
            "{} % Beschleunigung".format(
                PTP_GESCHWINDIGKEIT,
                PTP_BESCHLEUNIGUNG
            )
        )

        # Eigenes Roboterprogramm laden und ausführen
        import mein_programm
        mein_programm.ausfuehren(api, dType)

    except Exception as fehler:
        print()
        print("FEHLER im Roboterprogramm:")
        print(fehler)

    finally:
        # Sicherheitshalber Queue stoppen
        dType.SetQueuedCmdStopExec(api)

        # Verbindung trennen
        dType.DisconnectDobot(api)

        print()
        print("Das Programm 'start.py' wurde beendet.")
        print("Verbindung zum Dobot wurde getrennt.")


if __name__ == "__main__":
    main()
