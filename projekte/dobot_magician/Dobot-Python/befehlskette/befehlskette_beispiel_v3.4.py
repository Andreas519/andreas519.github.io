"""Testprogramm für Dobot, ESP32-COM und ESP32-WLAN.

Programmversion 3.4

Alle Steuerquellen schreiben in dieselbe Queue:

    Tastatur
    ESP32 über COM
    ESP32 über WLAN

Erlaubte Befehle:
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

DOBOT_PORT = "COM10"
DOBOT_BAUDRATE = 115200

ESP32_COM_AKTIV = True
ESP32_COM_PORT = "COM11"
ESP32_COM_BAUDRATE = 115200
ESP32_COM_TIMEOUT = 5.0

ESP32_WLAN_AKTIV = True
ESP32_WLAN_HOST = "0.0.0.0"
ESP32_WLAN_PORT = 8765
ESP32_WLAN_CLIENT_TIMEOUT = 10.0

STANDARD_PAUSE_MS = 1000
TIMEOUT_SEKUNDEN = 90.0

PROGRAMM_VERSION = "3.4"
ERWARTETE_BEFEHLSKETTENVERSION = "3.3"
ERWARTETE_COM_MODULVERSION = "1.0"
ERWARTETE_WLAN_MODULVERSION = "1.0"


befehle = [
    ("fahre_zu", 180, 160, 50, 0, "Fahre zu Punkt 1"),
    ("sauger_ein", "Sauger einschalten", 1000),
    ("sauger_status", "Status nach dem Einschalten anzeigen", 0),
    ("fahre_zu", 240, 140, 70, 0, "Fahre zu Punkt 2", 2500),
    ("sauger_aus", "Sauger ausschalten", 500),
    ("sauger_status", "Status nach dem Ausschalten anzeigen", 0),
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
        "Dobot und ESP32-COM benötigen verschiedene COM-Ports."
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
    ZUSTAND_HALT,
    befehlskette_erstellen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren_steuerbar,
)

from esp32_seriell_v1_0 import (
    VERSION as COM_MODULVERSION,
    ESP32SerielleSteuerung,
    serielle_ports_auflisten,
)

from esp32_wlan_v1_0 import (
    VERSION as WLAN_MODULVERSION,
    ESP32WLANSteuerung,
    lokale_ipv4_adressen,
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
    ESP32_COM_AKTIV
    and COM_MODULVERSION
    != ERWARTETE_COM_MODULVERSION
):
    raise RuntimeError(
        "Versionskonflikt beim COM-Modul: "
        f"erwartet {ERWARTETE_COM_MODULVERSION}, "
        f"geladen {COM_MODULVERSION}."
    )

if (
    ESP32_WLAN_AKTIV
    and WLAN_MODULVERSION
    != ERWARTETE_WLAN_MODULVERSION
):
    raise RuntimeError(
        "Versionskonflikt beim WLAN-Modul: "
        f"erwartet {ERWARTETE_WLAN_MODULVERSION}, "
        f"geladen {WLAN_MODULVERSION}."
    )


print(f"Testprogramm Version {PROGRAMM_VERSION}")
print(
    f"Befehlskettenmodul Version "
    f"{BEFEHLSKETTENVERSION}"
)
print("Programmordner:", PROJEKTORDNER)
print("Hauptordner:   ", HAUPTORDNER)
print("SDK-Ordner:    ", SDK_ORDNER)
print("DLL-Datei:     ", DLL_DATEI)


steuerbefehle = queue.Queue()

esp32_com = None
esp32_wlan = None

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

        esp32_com = ESP32SerielleSteuerung(
            steuerbefehle=steuerbefehle,
            port=ESP32_COM_PORT,
            baudrate=ESP32_COM_BAUDRATE,
        )

        esp32_com.starten()

        if not esp32_com.auf_verbindung_warten(
            ESP32_COM_TIMEOUT
        ):
            print(
                f"WARNUNG: ESP32-COM wurde über "
                f"{ESP32_COM_PORT} noch nicht verbunden."
            )

    if ESP32_WLAN_AKTIV:
        print("\nLokale IPv4-Adressen des PCs:")

        for adresse in lokale_ipv4_adressen():
            print(f"  {adresse}")

        print(
            f"WLAN-Port für den ESP32: "
            f"{ESP32_WLAN_PORT}"
        )

        esp32_wlan = ESP32WLANSteuerung(
            steuerbefehle=steuerbefehle,
            host=ESP32_WLAN_HOST,
            port=ESP32_WLAN_PORT,
            name="ESP32-WLAN",
        )

        esp32_wlan.starten()

        if not esp32_wlan.auf_server_warten(5.0):
            raise RuntimeError(
                "Der ESP32-WLAN-Server konnte "
                "nicht gestartet werden."
            )

        if not esp32_wlan.auf_client_warten(
            ESP32_WLAN_CLIENT_TIMEOUT
        ):
            print(
                "WARNUNG: Noch kein ESP32 über WLAN "
                "verbunden. Der Server wartet weiter."
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


except KeyboardInterrupt:
    print("\nProgrammabbruch über die Tastatur.")

    if api is not None and dobot_verbunden:
        if hasattr(
            dType,
            "SetQueuedCmdForceStopExec",
        ):
            dType.SetQueuedCmdForceStopExec(api)
        else:
            dType.SetQueuedCmdStopExec(api)


finally:
    if esp32_com is not None:
        esp32_com.beenden()
        print("ESP32-COM-Thread beendet.")

    if esp32_wlan is not None:
        esp32_wlan.beenden()
        print("ESP32-WLAN-Thread beendet.")

    if api is not None and dobot_verbunden:
        dType.SetQueuedCmdStopExec(api)
        dType.DisconnectDobot(api)
        print("Verbindung zum Dobot getrennt.")
