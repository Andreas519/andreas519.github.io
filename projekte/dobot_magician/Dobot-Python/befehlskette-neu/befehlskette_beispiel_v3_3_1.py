"""Testprogramm für Dobot und ESP32.

Programmversion 3.3.1

Die ESP32-Kommunikation wird mit ``COM_MODUS`` ausgewählt:

    COM_MODUS = "serial"   USB-COM-Verbindung zum ESP32
    COM_MODUS = "tcp"      TCP-Verbindung zum ESP-Simulator

Tastatur und ESP32 schreiben in dieselbe Steuerbefehls-Queue:

    p / PAUSE   Pause
    w / WEITER  Weiter
    h / HALT    Halt
    ? / STATUS  Status
"""

from pathlib import Path
import os
import queue
import sys


# ------------------------------------------------------------
# Diese Zeilen anpassen
# ------------------------------------------------------------

COM_MODUS = "tcp"  # "serial" oder "tcp"

DOBOT_PORT = "COM10"
DOBOT_BAUDRATE = 115200

# Beide Schalter werden zuerst definiert. Dadurch sind sie auch
# im jeweils anderen Kommunikationsmodus sicher vorhanden.
ESP32_COM_AKTIV = False
ESP32_TCP_AKTIV = False

if COM_MODUS == "serial":
    ESP32_COM_AKTIV = True
    ESP32_COM_PORT = "COM26"
    ESP32_COM_BAUDRATE = 115200
    ESP32_COM_VERBINDUNGS_TIMEOUT = 5.0

elif COM_MODUS == "tcp":
    ESP32_TCP_AKTIV = True
    ESP32_TCP_HOST = "127.0.0.1"
    ESP32_TCP_PORT = 5000
    ESP32_TCP_VERBINDUNGS_TIMEOUT = 5.0

else:
    raise ValueError(
        "COM_MODUS muss 'serial' oder 'tcp' sein."
    )

STANDARD_PAUSE_MS = 1000
TIMEOUT_SEKUNDEN = 90.0

PROGRAMM_VERSION = "3.3.1"
ERWARTETE_BEFEHLSKETTENVERSION = "3.3"
ERWARTETE_ESP32_MODULVERSION = "1.1"


befehle = [
    ("fahre_zu", 180, 160, 50, 0, "Fahre zu Punkt 1"),
    ("sauger_ein", "Sauger einschalten", 1000),
    ("sauger_status","Status nach dem Einschalten anzeigen",100,),
    ("sauger_aus", "Sauger schnell wieder AUS - wegen Lautstärke", 1000),
    ("fahre_zu", 240, 140, 70,  0, "Fahre zu Punkt 2", 2500, ),
    ("sauger_aus", "Sauger ausschalten", 500),
    ("sauger_status", "Status nach dem Ausschalten anzeigen", 0,),
    ("fahre_zu", 200, 180, 50, 0, "Fahre zu Punkt 3", 0),
]


# ------------------------------------------------------------
# Ab hier nichts mehr ändern
# ------------------------------------------------------------

PROJEKTORDNER = Path(__file__).resolve().parent
HAUPTORDNER = PROJEKTORDNER.parent
SDK_ORDNER = HAUPTORDNER / "sdk64"
DLL_DATEI = SDK_ORDNER / "DobotDll.dll"


if (
    ESP32_COM_AKTIV
    and DOBOT_PORT.upper() == ESP32_COM_PORT.upper()
):
    raise ValueError(
        "Dobot und ESP32 benötigen verschiedene COM-Ports."
    )

if not SDK_ORDNER.exists():
    raise FileNotFoundError(
        f"Der SDK-Ordner wurde nicht gefunden:\n"
        f"{SDK_ORDNER}"
    )

if not DLL_DATEI.exists():
    raise FileNotFoundError(
        f"Die Dobot-DLL wurde nicht gefunden:\n"
        f"{DLL_DATEI}"
    )

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(1, str(HAUPTORDNER))


dll_verzeichnis_handle = None

if os.name == "nt":
    dll_verzeichnis_handle = os.add_dll_directory(
        str(SDK_ORDNER)
    )


from sdk64 import DobotDllType as dType

from befehlskette_v3_3 import (
    VERSION as BEFEHLSKETTENVERSION,
    VERSIONSDATUM as BEFEHLSKETTENDATUM,
    ZUSTAND_HALT,
    befehlskette_erstellen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren_steuerbar,
)

from esp32_kommunikation_v1_1 import (
    VERSION as ESP32_MODULVERSION,
    ESP32SerielleSteuerung,
    ESP32TCPSteuerung,
    serielle_ports_auflisten,
)


if (
    BEFEHLSKETTENVERSION
    != ERWARTETE_BEFEHLSKETTENVERSION
):
    raise RuntimeError(
        "Versionskonflikt beim Befehlskettenmodul: "
        f"erwartet {ERWARTETE_BEFEHLSKETTENVERSION}, "
        f"geladen {BEFEHLSKETTENVERSION}."
    )

if (
    ESP32_MODULVERSION
    != ERWARTETE_ESP32_MODULVERSION
):
    raise RuntimeError(
        "Versionskonflikt beim ESP32-Kommunikationsmodul: "
        f"erwartet {ERWARTETE_ESP32_MODULVERSION}, "
        f"geladen {ESP32_MODULVERSION}."
    )


print(f"Testprogramm Version {PROGRAMM_VERSION}")
print(f"Kommunikationsmodus: {COM_MODUS}")
print(
    f"Befehlskettenmodul Version "
    f"{BEFEHLSKETTENVERSION} vom {BEFEHLSKETTENDATUM}"
)
print(f"ESP32-Kommunikationsmodul Version {ESP32_MODULVERSION}")
print("Programmordner:", PROJEKTORDNER)
print("Hauptordner:   ", HAUPTORDNER)
print("SDK-Ordner:    ", SDK_ORDNER)
print("DobotDllType:  ", Path(dType.__file__).resolve())
print("DLL-Datei:     ", DLL_DATEI)


steuerbefehle = queue.Queue()
esp32 = None
api = None
dobot_verbunden = False


try:
    if ESP32_COM_AKTIV:
        print("\nVon pySerial gefundene COM-Ports:")

        for port in serielle_ports_auflisten():
            print(
                f'  {port["geraet"]}: '
                f'{port["beschreibung"]}'
            )

        esp32 = ESP32SerielleSteuerung(
            steuerbefehle=steuerbefehle,
            port=ESP32_COM_PORT,
            baudrate=ESP32_COM_BAUDRATE,
        )

        esp32.starten()

        if not esp32.auf_verbindung_warten(
            ESP32_COM_VERBINDUNGS_TIMEOUT
        ):
            print(
                f"\nWARNUNG: Der ESP32 wurde über "
                f"{ESP32_COM_PORT} noch nicht verbunden."
            )
            print(
                "Die Tastatursteuerung bleibt verfügbar; "
                "der ESP32-Thread versucht die Verbindung weiter."
            )

    elif ESP32_TCP_AKTIV:
        print(
            f"\nTCP-Verbindung zum ESP-Simulator: "
            f"{ESP32_TCP_HOST}:{ESP32_TCP_PORT}"
        )

        esp32 = ESP32TCPSteuerung(
            steuerbefehle=steuerbefehle,
            host=ESP32_TCP_HOST,
            port=ESP32_TCP_PORT,
        )

        esp32.starten()

        if not esp32.auf_verbindung_warten(
            ESP32_TCP_VERBINDUNGS_TIMEOUT
        ):
            print(
                f"\nWARNUNG: Der TCP-Server unter "
                f"{ESP32_TCP_HOST}:{ESP32_TCP_PORT} "
                "ist noch nicht verbunden."
            )
            print(
                "Starte esp-simulator.py. "
                "Der TCP-Thread versucht die Verbindung weiter."
            )

    api = dType.load()

    verbindung = dType.ConnectDobot(
        api,
        DOBOT_PORT,
        DOBOT_BAUDRATE,
    )

    print(f"\nVerbindungsrückgabe Dobot: {verbindung}")

    if (
        verbindung[0]
        != dType.DobotConnect.DobotConnect_NoError
    ):
        raise ConnectionError(
            "Der Dobot konnte nicht verbunden werden."
        )

    dobot_verbunden = True
    print("Dobot erfolgreich verbunden.")

    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    queue_befehle = befehlskette_erstellen(
        api,
        befehle,
        standard_pause_ms=STANDARD_PAUSE_MS,
    )

    befehlskette_anzeigen(queue_befehle)

    input(
        "\nZum Starten der Befehlskette "
        "Enter drücken ..."
    )

    ergebnis = befehlskette_ausfuehren_steuerbar(
        api,
        queue_befehle,
        timeout=TIMEOUT_SEKUNDEN,
        steuerbefehle=steuerbefehle,
        tastatur=True,
    )

    print(f"\nErgebnis der Ausführung: {ergebnis}")

    if ergebnis == ZUSTAND_HALT:
        print()
        print(
            "Vor einem Neustart müssen Arbeitsplatte "
            "und Dobot kontrolliert werden."
        )
        print(
            "Danach ist eine sichere Ausgangsstellung "
            "herzustellen."
        )


except KeyboardInterrupt:
    print("\nProgrammabbruch über die Tastatur.")

    if api is not None and dobot_verbunden:
        if hasattr(dType, "SetQueuedCmdForceStopExec"):
            dType.SetQueuedCmdForceStopExec(api)
        else:
            dType.SetQueuedCmdStopExec(api)


finally:
    if esp32 is not None:
        esp32.beenden()
        print(f"ESP32-{COM_MODUS}-Thread beendet.")

    if api is not None and dobot_verbunden:
        dType.SetQueuedCmdStopExec(api)
        dType.DisconnectDobot(api)
        print("Verbindung zum Dobot getrennt.")
