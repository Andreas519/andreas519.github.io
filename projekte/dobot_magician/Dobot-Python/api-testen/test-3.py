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
    # ------------------------------------------------------------
    # Alarm-IDs ermitteln
    # ------------------------------------------------------------

    def alarm_ids_lesen(api):
        alarm_result = dType.GetAlarmsState(api)

        alarm_bytes = alarm_result[0]
        alarm_laenge = alarm_result[1]

        alarm_ids = []

        for byte_index, byte_wert in enumerate(
            alarm_bytes[:alarm_laenge]
        ):
            for bit_index in range(8):
                if byte_wert & (1 << bit_index):
                    alarm_id = byte_index * 8 + bit_index
                    alarm_ids.append(alarm_id)

        return alarm_ids


    # ------------------------------------------------------------
    # 1. Alle laufenden und gespeicherten Befehle stoppen
    # ------------------------------------------------------------

    print()
    print("Laufende Befehle werden zwangsweise gestoppt ...")

    dType.SetQueuedCmdForceStopExec(api)
    dType.dSleep(200)

    print("Befehlswarteschlange wird gelöscht ...")

    dType.SetQueuedCmdClear(api)
    dType.dSleep(200)


    # ------------------------------------------------------------
    # 2. Alarmstatus vor dem Löschen anzeigen
    # ------------------------------------------------------------

    alarme_vorher = alarm_ids_lesen(api)

    print()
    print("Alarme vor dem Löschen:")

    if alarme_vorher:
        for alarm_id in alarme_vorher:
            print(
                f"  Alarm-ID {alarm_id} "
                f"(0x{alarm_id:02X})"
            )
    else:
        print("  Keine Alarme aktiv.")


    # ------------------------------------------------------------
    # 3. Alle Alarme löschen
    # ------------------------------------------------------------

    print()
    print("Alle Alarme werden gelöscht ...")

    dType.ClearAllAlarmsState(api)
    dType.dSleep(500)


    # ------------------------------------------------------------
    # 4. Prüfen, ob der Alarm wirklich gelöscht wurde
    # ------------------------------------------------------------

    alarme_nachher = alarm_ids_lesen(api)

    print()
    print("Alarme nach dem Löschen:")

    if alarme_nachher:

        for alarm_id in alarme_nachher:
            print(
                f"  Alarm-ID {alarm_id} "
                f"(0x{alarm_id:02X})"
            )

        print()
        print("ABBRUCH:")
        print("Der Alarm konnte nicht gelöscht werden.")
        print("Es wird KEIN Bewegungsbefehl gesendet.")

        dType.DisconnectDobot(api)
        sys.exit(1)

    else:
        print("  Keine Alarme aktiv.")


    # ------------------------------------------------------------
    # 5. PTP-Parameter setzen
    # ------------------------------------------------------------

    dType.SetPTPCommonParams(
        api,
        20,
        20,
        isQueued=0
    )

    dType.SetPTPJointParams(
        api,
        200, 200, 200, 200,
        200, 200, 200, 200,
        isQueued=0
    )

    dType.SetPTPCoordinateParams(
        api,
        200, 100,
        200, 100,
        isQueued=0
    )


    # ------------------------------------------------------------
    # 6. Sichere Zielposition in die Queue eintragen
    # ------------------------------------------------------------

    ZIEL_X = 200.0
    ZIEL_Y = 100.0
    ZIEL_Z = 50.0
    ZIEL_R = 0.0

    print()
    print(
        f"Zielposition: "
        f"x={ZIEL_X}, "
        f"y={ZIEL_Y}, "
        f"z={ZIEL_Z}, "
        f"r={ZIEL_R}"
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

    print("Queue-Index des Bewegungsbefehls:", ziel_index)


    # ------------------------------------------------------------
    # 7. Queue starten
    # ------------------------------------------------------------

    print()
    print("Bewegung wird gestartet ...")

    dType.SetQueuedCmdStartExec(api)


    # ------------------------------------------------------------
    # 8. Bewegung überwachen
    # ------------------------------------------------------------

    while True:

        aktuelle_alarme = alarm_ids_lesen(api)

        if aktuelle_alarme:

            print()
            print("ALARM WÄHREND DER BEWEGUNG:")

            for alarm_id in aktuelle_alarme:
                print(
                    f"  Alarm-ID {alarm_id} "
                    f"(0x{alarm_id:02X})"
                )

            dType.SetQueuedCmdForceStopExec(api)

            print("Bewegung wurde zwangsweise gestoppt.")
            break

        aktueller_index = (
            dType.GetQueuedCmdCurrentIndex(api)[0]
        )

        if aktueller_index >= ziel_index:
            print()
            print("Zielbefehl wurde ausgeführt.")
            break

        dType.dSleep(100)


    # ------------------------------------------------------------
    # 9. Queue stoppen und Endposition lesen
    # ------------------------------------------------------------

    dType.SetQueuedCmdStopExec(api)

    pose = dType.GetPose(api)

    print()
    print("Aktuelle Position nach dem Versuch:")

    print(f"  x = {pose[0]:.3f}")
    print(f"  y = {pose[1]:.3f}")
    print(f"  z = {pose[2]:.3f}")
    print(f"  r = {pose[3]:.3f}")

# ------------------------------------------------------------
# Verbindung immer sauber trennen
# ------------------------------------------------------------
finally:

    print()
    print("Verbindung zum Dobot wird getrennt ...")

    dType.DisconnectDobot(api)

    print("Verbindung getrennt.")


