from pathlib import Path
import os
import platform
import sys
import time


# ============================================================
# KONFIGURATION
# ============================================================

COMPORT = "COM10"
BAUDRATE = 115200

ZIEL_X = 600.0
ZIEL_Y = 100.0
ZIEL_Z = 50.0
ZIEL_R = 0.0

BEWEGUNGS_TIMEOUT = 20.0


# ============================================================
# PROJEKT- UND SDK-PFADE
# ============================================================

PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

sdk_verzeichnis = PROJEKTORDNER / "sdk64"
dll_datei = sdk_verzeichnis / "DobotDll.dll"


# ============================================================
# HILFSFUNKTION: ALARM-IDs LESEN
# ============================================================

def alarm_ids_lesen(api, dType):
    """
    Liest den Alarmstatus des Dobot und gibt
    eine Liste der aktiven Alarm-IDs zurück.
    """

    alarm_result = dType.GetAlarmsState(api)

    alarm_bytes = alarm_result[0]
    alarm_laenge = alarm_result[1]

    alarm_ids = []

    for byte_index, byte_wert in enumerate(
        alarm_bytes[:alarm_laenge]
    ):
        for bit_index in range(8):

            if byte_wert & (1 << bit_index):

                alarm_id = (
                    byte_index * 8
                    + bit_index
                )

                alarm_ids.append(alarm_id)

    return alarm_ids


# ============================================================
# HILFSFUNKTION: ALARME AUSGEBEN
# ============================================================

def alarme_ausgeben(alarm_ids):

    if not alarm_ids:
        print("  Keine Alarme aktiv.")
        return

    for alarm_id in alarm_ids:

        print(
            f"  Alarm-ID {alarm_id} "
            f"(0x{alarm_id:02X})"
        )


# ============================================================
# PYTHON- UND DLL-INFORMATIONEN
# ============================================================

print("=" * 60)
print("DOBOT MAGICIAN - STATUS- UND RETTUNGSTEST")
print("=" * 60)

print()

print(
    "Python-Version:    ",
    platform.python_version()
)

print(
    "Python-Architektur:",
    platform.architecture()[0]
)

print(
    "SDK-Verzeichnis:   ",
    sdk_verzeichnis
)

print(
    "DLL-Datei:         ",
    dll_datei
)

print(
    "DLL vorhanden:     ",
    dll_datei.exists()
)


# ============================================================
# PRÜFEN, OB DIE DLL VORHANDEN IST
# ============================================================

if not dll_datei.exists():

    print()
    print("FEHLER:")
    print("Die Datei DobotDll.dll wurde nicht gefunden.")

    sys.exit(1)


# ============================================================
# DobotDllType.py IMPORTIEREN
# ============================================================

print()
print("DobotDllType.py wird importiert ...")

from sdk64 import DobotDllType as dType

print(
    "DobotDllType.py:   ",
    dType.__file__
)


# ============================================================
# DLL-VERZEICHNIS REGISTRIEREN
# ============================================================

print()
print(
    "SDK-Verzeichnis wird zum "
    "Windows-DLL-Suchpfad hinzugefügt ..."
)

dll_verzeichnis_handle = os.add_dll_directory(
    str(sdk_verzeichnis)
)

print("DLL-Verzeichnis registriert.")


# ============================================================
# DLL LADEN
# ============================================================

print()
print("DobotDll.dll wird geladen ...")

try:

    api = dType.load()

except Exception as fehler:

    print()
    print("FEHLER beim Laden der DobotDll.dll:")

    print(
        type(fehler).__name__
        + ": "
        + str(fehler)
    )

    sys.exit(1)


print("DobotDll.dll wurde erfolgreich geladen.")


# ============================================================
# VERBINDUNG HERSTELLEN
# ============================================================

print()
print(
    f"Verbindung zum Dobot über "
    f"{COMPORT} wird hergestellt ..."
)

verbindung = dType.ConnectDobot(
    api,
    COMPORT,
    BAUDRATE
)
print(" - verbindung = ",verbindung)
verbindungsstatus = verbindung[0]


if (
    verbindungsstatus
    == dType.DobotConnect.DobotConnect_NoError
):

    print("Dobot erfolgreich verbunden.")


elif (
    verbindungsstatus
    == dType.DobotConnect.DobotConnect_NotFound
):

    print()
    print("FEHLER:")
    print("Der Dobot wurde nicht gefunden.")

    sys.exit(1)


elif (
    verbindungsstatus
    == dType.DobotConnect.DobotConnect_Occupied
):

    print()
    print("FEHLER:")
    print(
        "Die serielle Schnittstelle ist "
        "belegt oder nicht verfügbar."
    )

    sys.exit(1)


else:

    print()
    print(
        "FEHLER: Unbekannter "
        "Verbindungsstatus:",
        verbindungsstatus
    )

    sys.exit(1)


# ============================================================
# DOBOT-TEST
# ============================================================

try:

    # --------------------------------------------------------
    # AKTUELLE POSITION LESEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("AKTUELLER ZUSTAND")
    print("=" * 60)

    pose = dType.GetPose(api)

    print()
    print("Aktuelle Position:")

    print(f"  x = {pose[0]:8.3f} mm")
    print(f"  y = {pose[1]:8.3f} mm")
    print(f"  z = {pose[2]:8.3f} mm")
    print(f"  r = {pose[3]:8.3f} °")

    print()
    print("Gelenkwinkel:")

    print(f"  J1 = {pose[4]:8.3f} °")
    print(f"  J2 = {pose[5]:8.3f} °")
    print(f"  J3 = {pose[6]:8.3f} °")
    print(f"  J4 = {pose[7]:8.3f} °")


    # --------------------------------------------------------
    # LAUFENDE QUEUE ZWANGSWEISE STOPPEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BEFEHLSAUSFÜHRUNG STOPPEN")
    print("=" * 60)

    print()
    print(
        "Eine eventuell laufende Bewegung "
        "wird zwangsweise gestoppt ..."
    )

    dType.SetQueuedCmdForceStopExec(api)

    dType.dSleep(300)

    print("Laufende Befehlsausführung gestoppt.")


    # --------------------------------------------------------
    # QUEUE LÖSCHEN
    # --------------------------------------------------------

    print()
    print(
        "Befehlswarteschlange wird gelöscht ..."
    )

    dType.SetQueuedCmdClear(api)

    dType.dSleep(300)

    print("Befehlswarteschlange gelöscht.")


    # --------------------------------------------------------
    # ALARMSTATUS VOR DEM LÖSCHEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ALARMSTATUS VOR DEM LÖSCHEN")
    print("=" * 60)

    alarme_vorher = alarm_ids_lesen(
        api,
        dType
    )

    print()

    alarme_ausgeben(
        alarme_vorher
    )


    # --------------------------------------------------------
    # ALLE ALARME LÖSCHEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ALARME LÖSCHEN")
    print("=" * 60)

    print()
    print(
        "Alle gespeicherten Alarmzustände "
        "werden gelöscht ..."
    )

    dType.ClearAllAlarmsState(api)

    dType.dSleep(500)


    # --------------------------------------------------------
    # ALARMSTATUS NACH DEM LÖSCHEN
    # --------------------------------------------------------

    alarme_nachher = alarm_ids_lesen(
        api,
        dType
    )

    print()
    print("Alarmstatus nach dem Löschen:")

    alarme_ausgeben(
        alarme_nachher
    )


    # --------------------------------------------------------
    # NUR BEWEGEN, WENN ALARM GELÖSCHT IST
    # --------------------------------------------------------

    if alarme_nachher:

        print()
        print("=" * 60)
        print("ABBRUCH")
        print("=" * 60)

        print()
        print(
            "Der Alarm ist weiterhin aktiv."
        )

        print(
            "Es wird kein Bewegungsbefehl "
            "gesendet."
        )

        print()
        print(
            "Die aktive Alarm-ID muss zuerst "
            "ausgewertet werden."
        )

        sys.exit(1)


    # --------------------------------------------------------
    # PTP-PARAMETER SETZEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PTP-PARAMETER SETZEN")
    print("=" * 60)

    print()

    dType.SetPTPCommonParams(
        api,
        20,
        20,
        isQueued=0
    )

    print(
        "PTP-Geschwindigkeit:   20 %"
    )

    print(
        "PTP-Beschleunigung:    20 %"
    )


    dType.SetPTPJointParams(
        api,

        200,
        200,
        200,
        200,

        200,
        200,
        200,
        200,

        isQueued=0
    )


    dType.SetPTPCoordinateParams(
        api,

        200,
        100,

        200,
        100,

        isQueued=0
    )


    # --------------------------------------------------------
    # RETTUNGSPOSITION IN DIE QUEUE EINTRAGEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ZIELPOSITION")
    print("=" * 60)

    print()

    print(
        f"  x = {ZIEL_X:.1f} mm"
    )

    print(
        f"  y = {ZIEL_Y:.1f} mm"
    )

    print(
        f"  z = {ZIEL_Z:.1f} mm"
    )

    print(
        f"  r = {ZIEL_R:.1f} °"
    )


    print()
    print(
        "Bewegungsbefehl wird "
        "in die Queue eingetragen ..."
    )


    ziel_index = dType.SetPTPCmd(
        api,

        dType.PTPMode.PTPMOVJXYZMode,

        ZIEL_X,
        ZIEL_Y,
        ZIEL_Z,
        ZIEL_R,

        isQueued=1
    )[0]


    print(
        "Queue-Index des Zielbefehls:",
        ziel_index
    )


    # --------------------------------------------------------
    # QUEUE STARTEN
    # --------------------------------------------------------

    print()
    print(
        "Befehlswarteschlange wird gestartet ..."
    )

    dType.SetQueuedCmdStartExec(api)

    print()
    print(
        "Der Dobot sollte sich jetzt bewegen."
    )


    # --------------------------------------------------------
    # BEWEGUNG ÜBERWACHEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BEWEGUNG WIRD ÜBERWACHT")
    print("=" * 60)

    startzeit = time.monotonic()

    bewegung_erfolgreich = False


    while True:

        # ----------------------------------------------------
        # ALARMSTATUS WÄHREND DER BEWEGUNG
        # ----------------------------------------------------

        aktuelle_alarme = alarm_ids_lesen(
            api,
            dType
        )


        if aktuelle_alarme:

            print()
            print(
                "ALARM WÄHREND DER BEWEGUNG:"
            )

            alarme_ausgeben(
                aktuelle_alarme
            )

            print()
            print(
                "Die Bewegung wird "
                "zwangsweise gestoppt."
            )

            dType.SetQueuedCmdForceStopExec(
                api
            )

            break


        # ----------------------------------------------------
        # QUEUE-INDEX PRÜFEN
        # ----------------------------------------------------

        aktueller_index = (
            dType.GetQueuedCmdCurrentIndex(api)[0]
        )


        if aktueller_index >= ziel_index:

            bewegung_erfolgreich = True

            print()
            print(
                "Der Zielbefehl wurde ausgeführt."
            )

            break


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        vergangene_zeit = (
            time.monotonic()
            - startzeit
        )


        if (
            vergangene_zeit
            > BEWEGUNGS_TIMEOUT
        ):

            print()
            print(
                "TIMEOUT:"
            )

            print(
                "Die Bewegung wurde nicht "
                "innerhalb von "
                f"{BEWEGUNGS_TIMEOUT:.1f} Sekunden "
                "abgeschlossen."
            )

            dType.SetQueuedCmdForceStopExec(
                api
            )

            break


        dType.dSleep(100)


    # --------------------------------------------------------
    # QUEUE STOPPEN
    # --------------------------------------------------------

    dType.SetQueuedCmdStopExec(api)


    # --------------------------------------------------------
    # ENDSTATUS LESEN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ENDSTATUS")
    print("=" * 60)

    pose = dType.GetPose(api)

    print()
    print("Aktuelle Position:")

    print(f"  x = {pose[0]:8.3f} mm")
    print(f"  y = {pose[1]:8.3f} mm")
    print(f"  z = {pose[2]:8.3f} mm")
    print(f"  r = {pose[3]:8.3f} °")


    # --------------------------------------------------------
    # ABWEICHUNG VON DER ZIELPOSITION
    # --------------------------------------------------------

    dx = abs(
        pose[0]
        - ZIEL_X
    )

    dy = abs(
        pose[1]
        - ZIEL_Y
    )

    dz = abs(
        pose[2]
        - ZIEL_Z
    )


    print()
    print("Abweichung vom Ziel:")

    print(f"  Δx = {dx:.3f} mm")
    print(f"  Δy = {dy:.3f} mm")
    print(f"  Δz = {dz:.3f} mm")


    # --------------------------------------------------------
    # ABSCHLIESSENDER ALARMSTATUS
    # --------------------------------------------------------

    letzte_alarme = alarm_ids_lesen(
        api,
        dType
    )

    print()
    print("Abschließender Alarmstatus:")

    alarme_ausgeben(
        letzte_alarme
    )


    # --------------------------------------------------------
    # ERGEBNIS
    # --------------------------------------------------------

    print()
    print("=" * 60)

    if (
        bewegung_erfolgreich
        and not letzte_alarme
    ):

        print(
            "TEST ERFOLGREICH ABGESCHLOSSEN"
        )

    else:

        print(
            "TEST NICHT ERFOLGREICH ABGESCHLOSSEN"
        )

    print("=" * 60)


# ============================================================
# VERBINDUNG IMMER SAUBER TRENNEN
# ============================================================

finally:

    print()
    print(
        "Verbindung zum Dobot "
        "wird getrennt ..."
    )

    try:

        dType.SetQueuedCmdStopExec(api)

    except Exception:

        pass


    dType.DisconnectDobot(api)

    print(
        "Verbindung zum Dobot getrennt."
    )