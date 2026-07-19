"""
test-5-alarme-beseitigen.py

Kleines interaktives Testprogramm zum Anzeigen und Beseitigen
von Alarmzuständen des Dobot Magician.

Das Programm:
1. verbindet den Dobot,
2. stoppt und leert die Queue,
3. zeigt Position und Alarme,
4. versucht, die Alarme zu löschen,
5. fordert bei Grenzalarmen zum vorsichtigen manuellen
   Verlassen der Grenzstellung auf,
6. prüft anschließend erneut.

Wichtig:
Das Programm führt keine automatische Ausweichbewegung aus.
"""

from pathlib import Path
import sys

HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

import dobot
from sdk64 import DobotDllType as dType


COMPORT = "COM10"

# Gelenk- und Parallelogramm-Grenzalarme:
GRENZALARME = set(range(0x40, 0x4A))


def queue_sicher_anhalten(api):
    """Stoppt die Queue und entfernt noch nicht ausgeführte Befehle."""

    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)


def alarmcodes_anzeigen(alarme):
    """Gibt Alarmcodes kompakt aus."""

    if not alarme:
        return

    codes = ", ".join(
        f"{alarmnummer} (0x{alarmnummer:02X})"
        for alarmnummer in alarme
    )
    print(f"Aktive Alarmcodes: {codes}")


def main():
    api = None

    try:
        print(dobot.version())
        api = dobot.init(COMPORT)

        print()
        print("Alarmbeseitigung")
        print("=================")

        queue_sicher_anhalten(api)

        while True:
            print()
            print("Aktueller Zustand")
            print("-----------------")

            dobot.position_anzeigen(api)
            alarme = dobot.alarme_lesen(api)
            dobot.alarme_anzeigen(api)

            if not alarme:
                print()
                print("Der Dobot ist alarmfrei.")
                break

            alarmcodes_anzeigen(alarme)

            print()
            print("Alarme werden gelöscht ...")
            dobot.alarme_loeschen(api)
            dType.dSleep(300)

            alarme = dobot.alarme_lesen(api)

            if not alarme:
                print("Die Alarme wurden erfolgreich gelöscht.")
                break

            print("Mindestens ein Alarm ist weiterhin aktiv.")
            dobot.alarme_anzeigen(api)

            grenzalarme = set(alarme) & GRENZALARME

            if not grenzalarme:
                print()
                print(
                    "Es liegt kein einfacher Grenzalarm vor. "
                    "Der Roboterarm wird nicht manuell bewegt."
                )
                print(
                    "Die konkrete Alarmursache muss zuerst "
                    "untersucht werden."
                )
                break

            print()
            print("Grenzstellung erkannt.")
            print(
                "Halte die Entriegelungstaste am Roboterarm gedrückt "
                "und bewege den Arm vorsichtig ein kleines Stück "
                "aus der Grenzstellung heraus."
            )
            print(
                "Keine Gewalt anwenden und den Arm nicht gegen "
                "einen mechanischen Anschlag drücken."
            )

            eingabe = input(
                "Danach Enter drücken; 'a' bricht den Test ab: "
            ).strip().lower()

            if eingabe == "a":
                print("Test abgebrochen.")
                break

            queue_sicher_anhalten(api)

    except KeyboardInterrupt:
        print("\nTest mit Strg+C abgebrochen.")

    finally:
        if api is not None:
            try:
                queue_sicher_anhalten(api)
            except Exception:
                pass

            try:
                dType.DisconnectDobot(api)
                print("Verbindung zum Dobot getrennt.")
            except Exception as exc:
                print(f"Fehler beim Trennen: {exc}")


if __name__ == "__main__":
    main()
