

PUNKTE = [
    (200.0,   0.0, 20.0, 0.0),
    (200.0,  50.0, 20.0, 0.0),
    (200.0, -50.0, 20.0, 0.0),
]


    print("Queue stoppen.")
    dType.SetQueuedCmdStopExec(api)
    dType.dSleep(200)
    
    print("# Alte Queue-Befehle entfernen")
    dType.SetQueuedCmdClear(api)
    dType.dSleep(200)
    print("# Bewegungsparameter:")
    # Geschwindigkeit und Beschleunigung jeweils in Prozent
    dType.SetPTPCommonParams(api, 50, 50, isQueued=1)

    letzter_index = 0

    print("# Drei Punkte in die Befehlswarteschlange eintragen")
    for nummer, punkt in enumerate(PUNKTE, start=1):
        x, y, z, r = punkt

        print(
            f"Punkt {nummer}: "
            f"X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}"
        )

        letzter_index = dType.SetPTPCmd(api, dType.PTPMode.PTPMOVJXYZMode, x, y, z, r, isQueued=1)[0]

    print("# Befehlswarteschlange starten")
    dType.SetQueuedCmdStartExec(api)

    # Warten, bis der letzte Fahrbefehl ausgeführt wurde
    while dType.GetQueuedCmdCurrentIndex(api)[0] < letzter_index:
        dType.dSleep(100)

    print("Alle drei Punkte wurden angefahren.")


