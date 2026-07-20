import DobotDllType as dType


# --------------------------------------------------
# Einstellungen
# --------------------------------------------------

PORT = "COM13"

PUNKTE = [
    (200.0,   0.0, 20.0, 0.0),
    (200.0,  50.0, 20.0, 0.0),
    (200.0, -50.0, 20.0, 0.0),
]


# --------------------------------------------------
# Dobot-API laden und Verbindung herstellen
# --------------------------------------------------

api = dType.load()

verbindung = dType.ConnectDobot(api, PORT, 115200)[0]

if verbindung != dType.DobotConnect.DobotConnect_NoError:
    raise RuntimeError(
        f"Verbindung zum Dobot über {PORT} fehlgeschlagen. "
        f"Fehlercode: {verbindung}"
    )

print(f"Dobot über {PORT} verbunden.")


try:
    # Alte Queue-Befehle entfernen
    dType.SetQueuedCmdClear(api)

    # Bewegungsparameter:
    # Geschwindigkeit und Beschleunigung jeweils in Prozent
    dType.SetPTPCommonParams(
        api,
        50,
        50,
        isQueued=1
    )

    letzter_index = 0

    # Drei Punkte in die Befehlswarteschlange eintragen
    for nummer, punkt in enumerate(PUNKTE, start=1):
        x, y, z, r = punkt

        print(
            f"Punkt {nummer}: "
            f"X={x:.1f}, Y={y:.1f}, Z={z:.1f}, R={r:.1f}"
        )

        letzter_index = dType.SetPTPCmd(
            api,
            dType.PTPMode.PTPMOVJXYZMode,
            x,
            y,
            z,
            r,
            isQueued=1
        )[0]

    # Befehlswarteschlange starten
    dType.SetQueuedCmdStartExec(api)

    # Warten, bis der letzte Fahrbefehl ausgeführt wurde
    while dType.GetQueuedCmdCurrentIndex(api)[0] < letzter_index:
        dType.dSleep(100)

    print("Alle drei Punkte wurden angefahren.")

finally:
    dType.SetQueuedCmdStopExec(api)
    dType.DisconnectDobot(api)

    print("Verbindung zum Dobot getrennt.")