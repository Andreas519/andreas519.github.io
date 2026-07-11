def warten_bis_fertig(api, dType, ziel_index):
    """Wartet, bis ein Queue-Befehl vollständig ausgeführt wurde."""

    while dType.GetQueuedCmdCurrentIndex(api)[0] < ziel_index:
        dType.dSleep(100)


def test(api, dType):
    """
    Erlaubt das Verändern der Z-Koordinate.

    Ausgangspunkt ist die aktuelle Position des Dobot.
    X, Y und R bleiben unverändert.
    """

    # Alte Queue-Befehle entfernen
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    # Queue starten
    dType.SetQueuedCmdStartExec(api)

    # Aktuelle Armposition bestimmen
    x, y, z, r = dType.GetPose(api)[:4]

#     pose = dType.GetPose(api)
#     x = pose[0]
#     y = pose[1]
#     z = pose[2]
#     r = pose[3]

    print("\nZ-Position testen")
    print("------------------")

    while True:
        print(
            f"\nAktuelle Position: "
            f"X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}"
        )

        eingabe = input(
            "Neue Z-Koordinate oder 'a' zum Abbrechen: "
        ).strip()

        if eingabe.lower() == "a":
            break

        try:
            neue_z = float(eingabe)

        except ValueError:
            print("Ungültige Eingabe!")
            continue

        # Fahrbefehl in die Queue eintragen
        index = dType.SetPTPCmd(
            api,
            dType.PTPMode.PTPMOVLXYZMode,
            x,
            y,
            neue_z,
            r,
            isQueued=1
        )[0]

        # Warten, bis die Bewegung beendet ist
        warten_bis_fertig( api, dType, index)

        # Tatsächliche Position erneut abfragen
        pose = dType.GetPose(api)

        x = pose[0]
        y = pose[1]
        z = pose[2]
        r = pose[3]

    # Queue stoppen
    dType.SetQueuedCmdStopExec(api)

    print("\nTest beendet.")


def main():
    print(
        "Die Funktionen dieses Programms "
        "werden von 'start.py' aufgerufen."
    )


if __name__ == "__main__":
    main()