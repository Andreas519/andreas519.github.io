"""Test der Hilfsfunktionen aus dobot.py.

Ablauf:
1. Verbindung zum Dobot herstellen
2. HOME-Fahrt ausführen
3. Aktuelle HOME-Position auslesen
4. X, Y und R beibehalten
5. Linear auf Z = 0 mm fahren
"""

from pathlib import Path
import sys


# Hauptordner "Dobot-Python" in den Python-Suchpfad aufnehmen.
DOBOT_PYTHON = Path(__file__).resolve().parent.parent

if str(DOBOT_PYTHON) not in sys.path:
    sys.path.insert(0, str(DOBOT_PYTHON))


import dobot


def main():
    api = None

    try:
        # Verbindung über COM10 herstellen.
        api = dobot.init(comport="COM10")

        # Befehlswarteschlange leeren und starten.
        dobot.queue_starten(api)

        print()
        print("Position vor der HOME-Fahrt:")
        dobot.position_anzeigen(api)

        # HOME-Fahrt durchführen.
        dobot.home(api)

        print()
        print("Erreichte HOME-Position:")
        x, y, z, r = dobot.position_lesen(api)
        dobot.position_anzeigen(api)

        print()
        print(
            f"Lineare Fahrt von Z={z:.1f} mm "
            f"auf Z=0.0 mm."
        )

        # Nur Z verändern.
        # X, Y und R bleiben auf den Werten der HOME-Position.
        dobot.fahre_zu(
            api,
            x,
            y,
            0.0,
            r,
            dobot.dType.PTPMode.PTPMOVLXYZMode,
        )

        print()
        print("Zielposition erreicht:")
        dobot.position_anzeigen(api)

    except KeyboardInterrupt:
        print()
        print("Programm durch den Benutzer abgebrochen.")

    except Exception as fehler:
        print()
        print("FEHLER:")
        print(fehler)

    finally:
        if api is not None:
            dobot.queue_stoppen(api)
            dobot.dType.DisconnectDobot(api)
            print()
            print("Verbindung zum Dobot getrennt.")


if __name__ == "__main__":
    main()