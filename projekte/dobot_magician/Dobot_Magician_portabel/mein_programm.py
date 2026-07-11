"""Eigentliches Roboterprogramm für den Dobot Magician.

Diese Datei wird von start.py importiert.

start.py übernimmt:
    - Laden der Dobot-DLL
    - Verbindung zum Dobot
    - Grundeinstellungen
    - Trennen der Verbindung

Diese Datei enthält:
    - kleine Hilfsfunktionen
    - die eigentliche Ablaufsteuerung in ausfuehren(api, dType)
"""


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------

def warten_bis_fertig(api, dType, ziel_index):
    """Wartet, bis ein Queue-Befehl vollständig ausgeführt wurde."""

    while dType.GetQueuedCmdCurrentIndex(api)[0] < ziel_index:
        dType.dSleep(100)


def queue_starten(api, dType):
    """Stoppt eine laufende Queue, löscht sie und startet sie neu."""

    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)
    dType.SetQueuedCmdStartExec(api)


def queue_stoppen(api, dType):
    """Stoppt die Ausführung der Queue."""

    dType.SetQueuedCmdStopExec(api)


def position_lesen(api, dType):
    """Liest die kartesische Position X, Y, Z und R."""

    return dType.GetPose(api)[:4]


def position_anzeigen(api, dType):
    """Liest und zeigt die aktuelle kartesische Position an."""

    x, y, z, r = position_lesen(api, dType)

    print(
        f"X={x:.1f} mm, "
        f"Y={y:.1f} mm, "
        f"Z={z:.1f} mm, "
        f"R={r:.1f}°"
    )


def fahre_zu(api, dType, x, y, z, r, modus=None):
    """Fährt zu einer Zielposition und wartet auf das Ende der Bewegung."""

    if modus is None:
        modus = dType.PTPMode.PTPMOVJXYZMode

    ziel_index = dType.SetPTPCmd(
        api,
        modus,
        x,
        y,
        z,
        r,
        isQueued=1
    )[0]

    warten_bis_fertig(api, dType, ziel_index)


def home(api, dType):
    """Führt eine HOME-Fahrt aus und wartet auf deren Abschluss."""

    print("HOME-Fahrt wird gestartet.")

    ziel_index = dType.SetHOMECmd(
        api,
        0,
        1
    )[0]

    warten_bis_fertig(api, dType, ziel_index)

    print("HOME-Fahrt abgeschlossen.")


# ------------------------------------------------------------
# Testfunktion
# ------------------------------------------------------------

def test_z(api, dType):
    """Verändert nur die Z-Koordinate der aktuellen Armposition."""

    # Ausgangsposition einmalig lesen.
    # X, Y und R bleiben während dieses Tests unverändert.
    x, y, z, r = position_lesen(api, dType)

    print()
    print("Z-Koordinate testen")
    print("-------------------")

    while True:
        print(
            f"Position: "
            f"X={x:.1f}, "
            f"Y={y:.1f}, "
            f"Z={z:.1f}, "
            f"R={r:.1f}"
        )

        eingabe = input(
            "Neue Z-Koordinate oder 'a' zum Abbrechen: "
        ).strip()

        if eingabe.lower() == "a":
            break

        try:
            neue_z = float(eingabe)

        except ValueError:
            print("Ungültige Eingabe.")
            continue

        # Nur Z wird verändert.
        # MOVL sorgt für eine lineare Bewegung.
        fahre_zu(
            api,
            dType,
            x,
            y,
            neue_z,
            r,
            dType.PTPMode.PTPMOVLXYZMode
        )

        # Tatsächliche Position nach der Bewegung erneut lesen.
        x, y, z, r = position_lesen(api, dType)

        print("Neue Position erreicht.")

    print("Z-Test beendet.")


# ------------------------------------------------------------
# Eigentliches Roboterprogramm
# ------------------------------------------------------------

def ausfuehren(api, dType):
    """Wird von start.py aufgerufen."""

    print()
    print("Roboterprogramm wird gestartet.")
    print("--------------------------------")

    queue_starten(api, dType)

    try:
        print("Aktuelle Position:")
        position_anzeigen(api, dType)

        # ----------------------------------------------------
        # Hier steht der eigentliche Programmablauf.
        # ----------------------------------------------------

        test_z(api, dType)

        # Spätere Beispiele:
        #
        # home(api, dType)
        #
        # x, y, z, r = position_lesen(api, dType)
        # fahre_zu(
        #     api,
        #     dType,
        #     x,
        #     y,
        #     z + 20,
        #     r,
        #     dType.PTPMode.PTPMOVLXYZMode
        # )

    finally:
        queue_stoppen(api, dType)

        print()
        print("Roboterprogramm beendet.")


# ------------------------------------------------------------
# Direkter Aufruf dieser Datei
# ------------------------------------------------------------

def main():
    print(
        "Diese Datei wird normalerweise nicht direkt gestartet.\n"
        "Bitte 'start.py' ausführen."
    )


if __name__ == "__main__":
    main()
