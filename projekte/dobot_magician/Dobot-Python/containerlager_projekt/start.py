"""Beispielprogramm für das Containerlager mit dem Dobot Magician.

Ordnerstruktur:

Dobot_Python/
├── dobot.py
├── containerlager.py
├── sdk64/
└── containerlager_projekt/
    └── start.py
"""

from pathlib import Path
import sys


# Den Hauptordner in den Python-Suchpfad aufnehmen.
HAUPTORDNER = Path(__file__).resolve().parent.parent

if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

import dobot
import containerlager as lager


COMPORT = "COM10"
SICHERE_HOEHE = 50.0

# Bereits gemessener Referenzpunkt:
REFERENZLOCH_1 = (40, 3, -54.3, -312.0)

# Diese Werte noch durch die tatsächlich gemessenen Dobot-Koordinaten
# ersetzen. None verhindert, dass der Dobot versehentlich mit falschen
# Kalibrierwerten bewegt wird.
REFERENZLOCH_2 = (1, 3, -56.1, 312.2)
REFERENZLOCH_3 = (22, 26, 310.5, -18.5)

PLATTEN_Z = -67.2
STANDARD_R = 0.0


    
def lagerplaetze_anlegen():
    """Legt die vom Anwender benannten Lagerplätze an."""

    # Beim erneuten Start in derselben Python-Sitzung alte Einträge löschen.
    lager.LAGERPLAETZE.clear()

    # Name, Mittelspalte und Mittelzeile des jeweiligen Würfels.
    lager.lagerplatz_hinzufuegen("Wareneingang", 5, 4)
    lager.lagerplatz_hinzufuegen("Lagerplatz links", 8, 4)
    lager.lagerplatz_hinzufuegen("Lagerplatz rechts", 11, 4)
    lager.lagerplatz_hinzufuegen("Warenausgang", 14, 4)


def kalibrierung_pruefen():
    """Bricht ab, solange noch Kalibrierwerte fehlen."""

    referenzloecher = (
        REFERENZLOCH_1,
        REFERENZLOCH_2,
        REFERENZLOCH_3,
    )

    if any(wert is None for referenz in referenzloecher for wert in referenz):
        raise RuntimeError(
            "Die Dobot-Koordinaten für REFERENZLOCH_2 und "
            "REFERENZLOCH_3 müssen zuerst eingetragen werden."
        )


def fahre_zu_lagerplatz(api, lagerplatz_name, hoehe=SICHERE_HOEHE):
    """Fährt über das Mittelloch eines benannten Lagerplatzes."""

    spalte, zeile = lager.lochkoordinate(lagerplatz_name)

    print()
    print(
        f"Fahre zu {lagerplatz_name!r}: "
        f"Mittelloch ({spalte}, {zeile}), Höhe {hoehe:.1f} mm"
    )

    dobot.fahre_zu_loch(
        api,
        spalte=spalte,
        zeile=zeile,
        hoehe=hoehe,
    )


def roboterprogramm(api):
    """Beispielhafter Ablauf des Containerlagerprogramms."""

    dobot.queue_starten(api)

    try:
        lager.belegung_anzeigen()

        # Beispiel: Einen Container in der Datenstruktur eintragen.
        lager.einlagern("W01", "Lagerplatz links")

        print()
        print("Belegung nach dem Einlagern von W01:")
        lager.belegung_anzeigen()

        # Zunächst nur sicher oberhalb der Lagerplätze fahren.
        fahre_zu_lagerplatz(api, "Wareneingang")
        fahre_zu_lagerplatz(api, "Lagerplatz links")
        fahre_zu_lagerplatz(api, "Warenausgang")

    finally:
        dobot.queue_stoppen(api)
        print()
        print("Roboterprogramm beendet.")


def main():
    """Verbindet den Dobot und startet das Containerlagerprogramm."""

    lagerplaetze_anlegen()
    kalibrierung_pruefen()

    api = dobot.init(COMPORT)

    dobot.plattenkalibrierung_setzen(
        referenzloch_1=REFERENZLOCH_1,
        referenzloch_2=REFERENZLOCH_2,
        referenzloch_3=REFERENZLOCH_3,
        platten_z=PLATTEN_Z,
        standard_r=STANDARD_R,
    )

    dobot.plattenkalibrierung_anzeigen()
    roboterprogramm(api)


if __name__ == "__main__":
    main()