"""Hier steht das eigentliche Dobot-Programm.

Die Funktion ausfuehren(api, dType) wird automatisch von start.py aufgerufen.
Das aktuelle Beispiel liest nur Werte und bewegt den Roboter noch nicht.
"""

def test(api, dType):
    # Aktuelle Armposition einmalig einlesen
    pose = dType.GetPose(api)

    x = pose[0]
    y = pose[1]
    z = pose[2]
    r = pose[3]

    while True:
        print(
            f"\nAktuelle Position: "
            f"X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}"
        )

        eingabe = input("Neue Z-Koordinate oder 'a' zum Abbrechen: ").strip()

        if eingabe.lower() == "a":
            break

        try:
            z = float(eingabe)
        except ValueError:
            print("Ungültige Eingabe!")
            continue

        index = dType.SetPTPCmd(
            api,
            dType.PTPMode.PTPMOVLXYZMode,
            x,
            y,
            z,
            r,
            isQueued=1
        )[0]

        warten_bis_fertig(api, index)

    print("Test beendet.")

def beispiel_01(api, dType):
    # Z-Koordinate der Arbeitsplatte
    # Diesen Wert müssen wir noch an deinem Aufbau bestimmen.
    ARBEITSPLATTE_Z = -50

    def warten_bis_fertig(api, ziel_index):
        """Wartet, bis ein Queue-Befehl vollständig ausgeführt wurde."""
        while dType.GetQueuedCmdCurrentIndex(api)[0] < ziel_index:
            dType.dSleep(100)

#     dType.SetQueuedCmdClear(api)
#     dType.SetQueuedCmdStartExec(api)
# 
#     print("Fahre in die Home-Position ...")
# 
#     home_index = dType.SetHOMECmd(
#         api,
#         temp=0,
#         isQueued=1
#     )[0]
# 
#     warten_bis_fertig(api, home_index)
# 
#     print("Home-Position erreicht.")
    
####################
    
eingabe = ""

while True:
    pose = dType.GetPose(api)

    x = pose[0]
    y = pose[1]
    z = pose[2]
    r = pose[3]

    print(f"\nAktuelle Position: X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}")

    eingabe = input("Neue Z-Koordinate oder 'a' zum Abbrechen: ").strip()

    if eingabe.lower() == "a":
        break

    try:
        neue_z = float(eingabe)
    except ValueError:
        print("Ungültige Eingabe!")
        continue

    absenk_index = dType.SetPTPCmd(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        x,
        y,
        neue_z,
        r,
        isQueued=1
    )[0]

    warten_bis_fertig(api, absenk_index)


    # ------------------------------------------------------------
    # Aktuelle Position nach dem Homing ermitteln
    # ------------------------------------------------------------

    #pose = dType.GetPose(api)
    (x,y,z,r)  = dType.GetPose(api)

    print(f"Aktuelle Position: X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}")


    # ------------------------------------------------------------
    # 2. Saugnapf senkrecht auf die Arbeitsplatte absenken
    # ------------------------------------------------------------

    print("Senke Saugnapf ab ...")

    absenk_index = dType.SetPTPCmd(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        x,
        y,
        ARBEITSPLATTE_Z,
        r,
        isQueued=1
    )[0]

    warten_bis_fertig(api, absenk_index)

    print("Arbeitsplatte erreicht.")


    # ------------------------------------------------------------
    # Ende
    # ------------------------------------------------------------

#     dType.SetQueuedCmdStopExec(api)
#     dType.DisconnectDobot(api)
# 
#     print("Verbindung getrennt.")

    

def SetHOMECmd(api, dType):
    print("HOME-Fahrt wird vorbereitet.")

    # Laufende Queue stoppen und alte Befehle löschen
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    # Vorhandene Alarme löschen
    dType.ClearAllAlarmsState(api)
    dType.dSleep(300)

    # Prüfen, ob weiterhin ein Alarm aktiv ist
    alarm_result = dType.GetAlarmsState(api)
    alarm_bytes = alarm_result[0]

    if any(alarm_bytes):
        print("Abbruch: Es ist weiterhin ein Alarm aktiv.")
        print("Alarmstatus:", alarm_result)
        return

    print("Kein Alarm aktiv.")


    dType.SetHOMEParams(
        api,
        200,   # X
        0,     # Y
        80,    # Z, zunächst sicher hoch
        0,     # R
        0      # sofort setzen, nicht in die Queue
    )
    # HOME-Befehl in die Warteschlange eintragen
    home_index = dType.SetHOMECmd(
        api,
        0,  # reservierter Parameter
        1   # als Queue-Befehl
    )[0]

    print("HOME-Befehl eingereiht, Index:", home_index)

    # Warteschlange starten
    dType.SetQueuedCmdStartExec(api)

    # Warten, bis der HOME-Befehl abgearbeitet wurde
    while dType.GetQueuedCmdCurrentIndex(api)[0] < home_index:
        dType.dSleep(100)

    # Warteschlange wieder stoppen
    dType.SetQueuedCmdStopExec(api)

    print("HOME-Fahrt abgeschlossen.")

    # Position nach der HOME-Fahrt anzeigen
    pose = dType.GetPose(api)

    print("Position nach HOME:")
    print("X  = {:.2f} mm".format(pose[0]))
    print("Y  = {:.2f} mm".format(pose[1]))
    print("Z  = {:.2f} mm".format(pose[2]))
    print("R  = {:.2f}°".format(pose[3]))
    print("J1 = {:.2f}°".format(pose[4]))
    print("J2 = {:.2f}°".format(pose[5]))
    print("J3 = {:.2f}°".format(pose[6]))
    print("J4 = {:.2f}°".format(pose[7]))


def info(api, dType):
    # Aktuelle Position erneut abfragen
    pose = dType.GetPose(api)
    print("Position als Liste:", pose)
    print("\nPoint to Point - Parameter anzeigen:")
    
    print(" - PTP Joint:     ", dType.GetPTPJointParams(api))
    print(" - PTP Coordinate:", dType.GetPTPCoordinateParams(api))
    print(" - PTP Common:    ", dType.GetPTPCommonParams(api))

    print("\nDer Dobot wurde in diesem Beispiel nicht bewegt.")

    # --------------------------------------------------------
    # Später können hier eigene Befehle eingefügt werden.
    # Beispiel HOME – zunächst bewusst auskommentiert:
    # home_index = dType.SetHOMECmd(api, 0, 1)[0]

    # dType.SetQueuedCmdClear(api)
    # home_index = dType.SetHOMECmd(api, 0, 1)[0]
    # dType.SetQueuedCmdStartExec(api)
    # while dType.GetQueuedCmdCurrentIndex(api)[0] < home_index:
    #     dType.dSleep(100)
    # dType.SetQueuedCmdStopExec(api)
    # --------------------------------------------------------
def ausfuehren(api, dType):
    # Aktuelle Position erneut abfragen
    pose = dType.GetPose(api)
    print("\nDer Dobot wird bewegt.")

    # --------------------------------------------------------
    # Später können hier eigene Befehle eingefügt werden.
    # Beispiel HOME – zunächst bewusst auskommentiert:
    # home_index = dType.SetHOMECmd(api, 0, 1)[0]

    dType.SetQueuedCmdClear(api)
    home_index = dType.SetHOMECmd(api, 0, 1)[0]
    print(home_index)
    dType.SetQueuedCmdStartExec(api)
    while dType.GetQueuedCmdCurrentIndex(api)[0] < home_index:
        dType.dSleep(100)
    dType.SetQueuedCmdStopExec(api)

    
def main():
    print("Die Funktionen dieses Programmes wird von 'start.py' aufgerufen!")
    info="""In 'start.py' ab
 Zeile:
    130  # ----------------------------------------------
    131         # Eigenes Roboterprogramm laden
    132         import mein_programm
    133    
    134         # Eigenes Roboterprogramm ausführen
    135         mein_programm.ausfuehren(api, dType)
    136  #----------------------------------------------"""
    print(info)
   
if __name__ == "__main__":
    main()
