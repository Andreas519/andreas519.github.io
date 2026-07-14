from pathlib import Path
import os
import platform
import sys


# ============================================================
# KONFIGURATION
# ============================================================

COMPORT = "COM10"
BAUDRATE = 115200


# ============================================================
# PROJEKT- UND SDK-PFADE
# ============================================================

PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

sdk_verzeichnis = PROJEKTORDNER / "sdk64"
dll_datei = sdk_verzeichnis / "DobotDll.dll"

module.systeminfo()

#module.alarme_ausgeben(api,dType)


# ============================================================
# DLL VORHANDEN?
# ============================================================

if not dll_datei.exists():

    print()
    print("FEHLER:")
    print("DobotDll.dll wurde nicht gefunden.")

    sys.exit(1)


# ============================================================
# DOBOT-API IMPORTIEREN
# ============================================================

print()
print("DobotDllType.py wird importiert ...")

from sdk64 import DobotDllType as dType

print(
    "DobotDllType.py:   ",
    dType.__file__
)


# ============================================================
# DLL-SUCHPFAD REGISTRIEREN
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
# DOBOT STARTEN
# ============================================================

try:
    x, y, z, r = dType.GetPose(api)[:4]

    
    print("Startposition")
    print(f"x = {x:8.3f} mm     y = {y:8.3f} mm   z = {z:8.3f} mm")



    # --------------------------------------------------------
    # 1. Eventuell laufende Bewegung sofort stoppen
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BEFEHLSAUSFÜHRUNG STOPPEN")
    print("=" * 60)

    print()
    print(
        "Eventuell laufende Bewegung "
        "wird zwangsweise gestoppt ..."
    )

    dType.SetQueuedCmdForceStopExec(api)

    dType.dSleep(300)

    print("Befehlsausführung gestoppt.")


    # --------------------------------------------------------
    # 2. Alte Queue löschen
    # --------------------------------------------------------

    print()
    print("Befehlswarteschlange wird gelöscht ...")

    dType.SetQueuedCmdClear(api)

    dType.dSleep(300)

    print("Befehlswarteschlange gelöscht.")


    # --------------------------------------------------------
    # 3. Alarmstatus vor dem Löschen
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
    # 4. Alle Alarme löschen
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ALARME LÖSCHEN")
    print("=" * 60)

    print()
    print("Alle Alarme werden gelöscht ...")

    dType.ClearAllAlarmsState(api)

    dType.dSleep(500)


    # --------------------------------------------------------
    # 5. Alarmstatus erneut prüfen
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
    # 6. Abbrechen, wenn weiterhin Alarm aktiv
    # --------------------------------------------------------

    if alarme_nachher:

        print()
        print("=" * 60)
        print("HOME-FAHRT NICHT MÖGLICH")
        print("=" * 60)

        print()
        print(
            "Der Alarm ist weiterhin aktiv."
        )

        print(
            "Die HOME-Fahrt wird aus "
            "Sicherheitsgründen nicht gestartet."
        )

        sys.exit(1)


    # --------------------------------------------------------
    # 7. HOME-Fahrt vorbereiten
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("HOME-FAHRT")
    print("=" * 60)

    print()
    print(
        "Keine Alarme aktiv."
    )

    print(
        "HOME-Befehl wird in die "
        "Befehlswarteschlange eingetragen ..."
    )


    home_index = dType.SetHOMECmd(
        api,
        0,
        isQueued=1
    )[0]


    print(
        "Queue-Index des HOME-Befehls:",
        home_index
    )
    
    # --------------------------------------------------------
    # Aktuelle Position nach der HOME-Fahrt ermitteln
    # --------------------------------------------------------

    pose = dType.GetPose(api)

    x = pose[0]
    y = pose[1]
    z = pose[2]
    r = pose[3]

    print()
    print("=" * 60)
    print("AKTUELLE POSITION")
    print("=" * 60)

    print(f"x = {x:8.3f} mm")
    print(f"y = {y:8.3f} mm")
    print(f"z = {z:8.3f} mm")
    print(f"r = {r:8.3f} °")


    # --------------------------------------------------------
    # 8. Queue starten
    # --------------------------------------------------------

    print()
    print("HOME-Fahrt wird gestartet ...")

    dType.SetQueuedCmdStartExec(api)


    # --------------------------------------------------------
    # 9. Auf Abschluss der HOME-Fahrt warten
    # --------------------------------------------------------

    while True:

        # Alarmstatus während der HOME-Fahrt prüfen
        aktuelle_alarme = alarm_ids_lesen(
            api,
            dType
        )

        if aktuelle_alarme:

            print()
            print(
                "ALARM WÄHREND DER HOME-FAHRT:"
            )

            alarme_ausgeben(
                aktuelle_alarme
            )

            print()
            print(
                "HOME-Fahrt wird "
                "zwangsweise gestoppt."
            )

            dType.SetQueuedCmdForceStopExec(
                api
            )

            break


        # Aktuellen Queue-Index lesen
        aktueller_index = (
            dType.GetQueuedCmdCurrentIndex(api)[0]
        )


        if aktueller_index >= home_index:

            print()
            print(
                "HOME-Befehl wurde ausgeführt."
            )

            break


        dType.dSleep(100)


    # --------------------------------------------------------
    # 10. Queue stoppen
    # --------------------------------------------------------

    dType.SetQueuedCmdStopExec(api)


    # --------------------------------------------------------
    # 11. Aktuelle Position nach HOME lesen
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("POSITION NACH DER HOME-FAHRT")
    print("=" * 60)

    pose = dType.GetPose(api)

    print()

    print(
        f"  x = {pose[0]:8.3f} mm"
    )

    print(
        f"  y = {pose[1]:8.3f} mm"
    )

    print(
        f"  z = {pose[2]:8.3f} mm"
    )

    print(
        f"  r = {pose[3]:8.3f} °"
    )


    print()
    print("Gelenkwinkel:")

    print(
        f"  J1 = {pose[4]:8.3f} °"
    )

    print(
        f"  J2 = {pose[5]:8.3f} °"
    )

    print(
        f"  J3 = {pose[6]:8.3f} °"
    )

    print(
        f"  J4 = {pose[7]:8.3f} °"
    )


    # --------------------------------------------------------
    # 12. Abschließender Alarmstatus
    # --------------------------------------------------------

    letzte_alarme = alarm_ids_lesen(
        api,
        dType
    )

    print()
    print("=" * 60)
    print("ABSCHLIESSENDER ALARMSTATUS")
    print("=" * 60)

    print()

    alarme_ausgeben(
        letzte_alarme
    )


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