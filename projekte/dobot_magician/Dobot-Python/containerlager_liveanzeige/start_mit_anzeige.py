"""Containerlager mit paralleler Live-Anzeige der Lochplatte.

Ordnerstruktur:

Dobot-Python/
├── dobot.py
├── containerlager.py
├── lochplattenanzeige.py
├── sdk64/
└── containerlager_projekt/
    └── start.py

Diese Datei kann als neue start.py in containerlager_projekt gespeichert werden.
"""

from pathlib import Path
import sys
import threading
import traceback


HAUPTORDNER = Path(__file__).resolve().parent.parent

if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

import dobot
import containerlager as lager
from lochplattenanzeige import LochplattenAnzeige


VERSION = "1.0-mit-anzeige"
COMPORT = "COM10"
SICHERE_HOEHE = 50.0

# Hier die eigenen, bereits ermittelten Kalibrierwerte eintragen bzw.
# aus der bisherigen start.py übernehmen.
REFERENZLOCH_1 = (2, 1, -73.8, -311.1)
REFERENZLOCH_2 = (39, 1, None, None)
REFERENZLOCH_3 = (2, 26, None, None)

PLATTEN_Z = -35.0
STANDARD_R = 0.0


def lagerplaetze_anlegen():
    """Legt frei benannte Lagerplätze über ihre Mittellöcher an."""

    lager.LAGERPLAETZE.clear()

    lager.lagerplatz_hinzufuegen("Wareneingang", 5, 4)
    lager.lagerplatz_hinzufuegen("Lagerplatz links", 8, 4)
    lager.lagerplatz_hinzufuegen("Lagerplatz rechts", 11, 4)
    lager.lagerplatz_hinzufuegen("Warenausgang", 14, 4)


def kalibrierung_pruefen():
    """Verhindert Bewegungen mit unvollständigen Kalibrierwerten."""

    referenzloecher = (
        REFERENZLOCH_1,
        REFERENZLOCH_2,
        REFERENZLOCH_3,
    )

    if any(wert is None for referenz in referenzloecher for wert in referenz):
        raise RuntimeError(
            "Die Dobot-Koordinaten der drei Referenzlöcher müssen "
            "vollständig eingetragen werden."
        )


def fahre_zu_lagerplatz(
    api,
    anzeige,
    lagerplatz_name,
    hoehe=SICHERE_HOEHE,
):
    """Markiert das Ziel und fährt über das Mittelloch des Lagerplatzes."""

    spalte, zeile = lager.lochkoordinate(lagerplatz_name)

    anzeige.ziel_setzen(spalte, zeile, lagerplatz_name)
    anzeige.status_setzen(
        f"Fahre zu {lagerplatz_name}: Mittelloch ({spalte}, {zeile}), "
        f"Höhe {hoehe:.1f} mm"
    )

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

    # Der orange Marker zeigt die zuletzt angefahrene bzw. beauftragte
    # Lochposition. Ob fahre_zu_loch() bis zum Bewegungsende wartet, hängt
    # von der Implementierung in dobot.py ab.
    anzeige.roboterposition_setzen(spalte, zeile)


def container_umlagern_datenmodell(
    anzeige,
    container_id,
    von_lagerplatz,
    nach_lagerplatz,
):
    """Aktualisiert nur die virtuelle Lagerbelegung nach dem Abstellen."""

    ausgelagert, _ebene = lager.auslagern(von_lagerplatz)

    if ausgelagert != container_id:
        raise RuntimeError(
            f"Erwartet wurde {container_id!r}, entnommen wurde "
            f"aber {ausgelagert!r}."
        )

    neue_ebene = lager.einlagern(container_id, nach_lagerplatz)
    anzeige.lager_aktualisieren()
    anzeige.status_setzen(
        f"{container_id} ist im Datenmodell auf "
        f"{nach_lagerplatz}, Ebene {neue_ebene + 1}, eingelagert."
    )


def roboterprogramm(api, anzeige):
    """Beispielablauf mit synchronen Meldungen an die Live-Anzeige."""

    dobot.queue_starten(api)

    try:
        # Anfangszustand: W01 steht am Wareneingang.
        lager.einlagern("W01", "Wareneingang")
        anzeige.lager_aktualisieren()
        anzeige.status_setzen("W01 steht am Wareneingang.")

        fahre_zu_lagerplatz(api, anzeige, "Wareneingang")

        # Hier später ergänzen:
        #   - absenken
        #   - Sauger einschalten
        #   - anheben

        fahre_zu_lagerplatz(api, anzeige, "Lagerplatz links")

        # Hier später ergänzen:
        #   - absenken
        #   - Sauger ausschalten
        #   - anheben

        container_umlagern_datenmodell(
            anzeige,
            container_id="W01",
            von_lagerplatz="Wareneingang",
            nach_lagerplatz="Lagerplatz links",
        )

        fahre_zu_lagerplatz(api, anzeige, "Warenausgang")
        anzeige.status_setzen("Roboterprogramm erfolgreich beendet.")

    finally:
        dobot.queue_stoppen(api)
        anzeige.ziel_loeschen()
        print()
        print("Roboterprogramm beendet.")


def roboterthread(anzeige):
    """Verbindet und steuert den Dobot außerhalb des GUI-Hauptthreads."""

    anzeige.programm_laeuft_setzen(True)

    try:
        anzeige.status_setzen("Prüfe Plattenkalibrierung …")
        kalibrierung_pruefen()

        anzeige.status_setzen(f"Verbinde Dobot über {COMPORT} …")
        api = dobot.init(COMPORT)

        dobot.plattenkalibrierung_setzen(
            referenzloch_1=REFERENZLOCH_1,
            referenzloch_2=REFERENZLOCH_2,
            referenzloch_3=REFERENZLOCH_3,
            platten_z=PLATTEN_Z,
            standard_r=STANDARD_R,
        )

        dobot.plattenkalibrierung_anzeigen()
        anzeige.status_setzen("Dobot verbunden; Roboterprogramm startet.")
        roboterprogramm(api, anzeige)

    except Exception as exc:
        traceback.print_exc()
        anzeige.fehler_anzeigen(f"{type(exc).__name__}: {exc}")

    finally:
        anzeige.programm_laeuft_setzen(False)


def main():
    """Startet Anzeige und Robotersteuerung parallel."""

    lagerplaetze_anlegen()

    anzeige = LochplattenAnzeige(
        lager,
        titel=f"Dobot-Containerlager · start.py {VERSION}",
    )
    anzeige.lager_aktualisieren()

    thread = threading.Thread(
        target=roboterthread,
        args=(anzeige,),
        name="Dobot-Roboterprogramm",
        daemon=False,
    )
    thread.start()

    # tkinter muss im Hauptthread laufen.
    anzeige.start()

    # Das Fenster kann erst geschlossen werden, wenn der Thread beendet ist.
    thread.join()


if __name__ == "__main__":
    main()
