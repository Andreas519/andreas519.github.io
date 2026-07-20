"""
hanoi_dobot.py

Turm von Hanoi mit drei Scheiben und einem Dobot Magician.
Verwendet das Modul dobot.py.

Vor dem ersten Roboterlauf:
1. POSITIONEN A, B und C einmessen.
2. BASIS_Z, SCHEIBENHOEHE und SICHERE_Z prüfen.
3. Zunächst mit NUR_ANZEIGEN = True testen.
"""

from pathlib import Path
import sys

# dobot.py liegt im übergeordneten Ordner.
PROGRAMMORDNER = Path(__file__).resolve().parent
DOBOT_ORDNER = PROGRAMMORDNER.parent
sys.path.insert(0, str(DOBOT_ORDNER))

import dobot
from sdk64 import DobotDllType as dType


# ---------------------------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------------------------

COM_PORT = "COM10"

ANZAHL_SCHEIBEN = 3
STARTPOSITION = "A"
HILFSPOSITION = "B"
ENDPOSITION = "C"

# Mittelpunkt der drei Stapel: X, Y, R
# Diese Beispielwerte müssen am realen Aufbau geprüft und angepasst werden.
POSITIONEN = {
    "A": (180.0, 160.0, 0.0),
    "B": (240.0, 140.0, 0.0),
    "C": (200.0, 180.0, 0.0),
}

# Z-Höhe, bei der eine einzelne Scheibe aufgenommen oder abgelegt wird.
BASIS_Z = 50.0

# Dicke einer Scheibe einschließlich eines kleinen Höhenzuschlags.
SCHEIBENHOEHE = 10.0

# Sichere Fahrhöhe über allen drei Stapeln.
SICHERE_Z = 100.0

# Zeit zum Ansaugen und Loslassen in Millisekunden.
SAUGPAUSE_MS = 700

# True: nur Zugfolge und Höhen anzeigen, der Dobot bewegt sich nicht.
# False: Verbindung aufbauen und die Bewegungen ausführen.
NUR_ANZEIGEN = True


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def eingaben_pruefen():
    """Prüft die grundlegenden Programmeinstellungen."""

    namen = {STARTPOSITION, HILFSPOSITION, ENDPOSITION}

    if namen != {"A", "B", "C"}:
        raise ValueError("Start-, Hilfs- und Endposition müssen A, B und C jeweils genau einmal enthalten.")

    if ANZAHL_SCHEIBEN != 3:
        raise ValueError("Dieser erste Entwurf ist für genau drei Scheiben vorgesehen.")

    if SICHERE_Z <= BASIS_Z + ANZAHL_SCHEIBEN * SCHEIBENHOEHE:
        raise ValueError("SICHERE_Z muss über dem höchsten möglichen Stapel liegen.")


def warte(api, dauer_ms):
    """Fügt eine Wartezeit in die laufende Queue ein und wartet auf ihr Ende."""

    index = dType.SetWAITCmd(api, dauer_ms, isQueued=1)[0]
    dobot.warten_bis_fertig(api, index)


def fahre(api, position, z, linear=False):
    """Fährt zum Mittelpunkt einer Hanoi-Position auf die angegebene Höhe."""

    x, y, r = POSITIONEN[position]
    modus = dType.PTPMode.PTPMOVLXYZMode if linear else dType.PTPMode.PTPMOVJXYZMode
    dobot.fahre_zu(api, x, y, z, r, modus)


def scheibe_umsetzen(api, staebe, von, nach):
    """Setzt die oberste Scheibe von einem Stapel auf einen anderen."""

    if not staebe[von]:
        raise RuntimeError(f"Position {von} enthält keine Scheibe.")

    scheibe = staebe[von][-1]

    if staebe[nach] and staebe[nach][-1] < scheibe:
        raise RuntimeError(f"Scheibe {scheibe} darf nicht auf Scheibe {staebe[nach][-1]} gelegt werden.")

    quellhoehe = BASIS_Z + (len(staebe[von]) - 1) * SCHEIBENHOEHE
    zielhoehe = BASIS_Z + len(staebe[nach]) * SCHEIBENHOEHE

    print(f"Scheibe {scheibe}: {von} -> {nach} | Aufnahme Z={quellhoehe:.1f}, Ablage Z={zielhoehe:.1f}")

    if api is not None:
        fahre(api, von, SICHERE_Z)
        fahre(api, von, quellhoehe, linear=True)
        index = dobot.sauger_aktivieren(api, isQueued=1)[0]
        dobot.warten_bis_fertig(api, index)
        warte(api, SAUGPAUSE_MS)
        fahre(api, von, SICHERE_Z, linear=True)

        fahre(api, nach, SICHERE_Z)
        fahre(api, nach, zielhoehe, linear=True)
        index = dobot.sauger_deaktivieren(api, isQueued=1)[0]
        dobot.warten_bis_fertig(api, index)
        warte(api, SAUGPAUSE_MS)
        fahre(api, nach, SICHERE_Z, linear=True)

    staebe[von].pop()
    staebe[nach].append(scheibe)
    print(f"A={staebe['A']}  B={staebe['B']}  C={staebe['C']}")


def hanoi(api, anzahl, start, hilf, ziel, staebe):
    """Löst den Turm von Hanoi rekursiv."""

    if anzahl == 1:
        scheibe_umsetzen(api, staebe, start, ziel)
        return

    hanoi(api, anzahl - 1, start, ziel, hilf, staebe)
    scheibe_umsetzen(api, staebe, start, ziel)
    hanoi(api, anzahl - 1, hilf, start, ziel, staebe)


def startzustand_erzeugen():
    """Erzeugt den Anfangszustand passend zur gewählten Startposition."""

    staebe = {"A": [], "B": [], "C": []}
    staebe[STARTPOSITION] = list(range(ANZAHL_SCHEIBEN, 0, -1))
    return staebe


def main():
    eingaben_pruefen()
    staebe = startzustand_erzeugen()
    api = None

    print("Turm von Hanoi")
    print("---------------")
    print(f"Start: {STARTPOSITION}, Hilfe: {HILFSPOSITION}, Ziel: {ENDPOSITION}")
    print(f"Anfangszustand: A={staebe['A']}  B={staebe['B']}  C={staebe['C']}")
    print()

    if NUR_ANZEIGEN:
        print("Testmodus: Es werden keine Roboterbefehle ausgeführt.\n")
        hanoi(None, ANZAHL_SCHEIBEN, STARTPOSITION, HILFSPOSITION, ENDPOSITION, staebe)
        return

    try:
        api = dobot.init(COM_PORT)
        print(dobot.version())
        dobot.alarme_loeschen(api)
        dobot.queue_starten(api)
        hanoi(api, ANZAHL_SCHEIBEN, STARTPOSITION, HILFSPOSITION, ENDPOSITION, staebe)
        print("\nTurm vollständig umgesetzt.")

    finally:
        if api is not None:
            dobot.sauger_deaktivieren(api, isQueued=0)
            dobot.queue_stoppen(api)
            dType.DisconnectDobot(api)
            print("Verbindung zum Dobot getrennt.")


if __name__ == "__main__":
    main()
