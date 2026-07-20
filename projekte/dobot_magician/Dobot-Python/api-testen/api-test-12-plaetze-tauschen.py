"""
test-10-plaetze-tauschen.py

Tauscht zwei Würfel mithilfe einer freien Zwischenablage.

Ablauf:
    1. Würfel A -> freier Platz
    2. Würfel B -> Platz A
    3. Würfel vom freien Platz -> Platz B

Es werden ausschließlich Roboterfunktionen aus DobotDllType.py verwendet.
Die kleinen Python-Hilfsfunktionen in dieser Datei dienen nur der
Übersichtlichkeit, Alarmüberwachung und Queue-Steuerung.
"""

from pathlib import Path
import math
import os
import sys
import time


COM_PORT = "COM10"
BAUDRATE = 115200

# Angegebene direkte Dobot-Koordinaten in Millimetern.
PLATZ_A = (180.0, 100.0)
PLATZ_B = (200.0, 100.0)
FREIER_PLATZ = (220.0, 100.0)



# Die Platte liegt bei Z = -72 mm.
# Der Würfel ist 62 mm hoch:
# -72 mm + 62 mm = -10 mm Würfeloberfläche.
PLATTEN_Z = -72.0
WUERFEL_HOEHE = 62.0
GREIF_Z = PLATTEN_Z + WUERFEL_HOEHE

# 40 mm oberhalb der Würfeloberfläche.
ANFAHR_Z = 30.0

# Zeit zum Ansaugen und Loslassen.
SAUGER_WARTEZEIT_MS = 700

# Nominelle maximale Reichweite des Dobot Magician.
MAX_REICHWEITE_MM = 320.0

PROGRAMMORDNER = Path(__file__).resolve().parent
DOBOT_ORDNER = PROGRAMMORDNER.parent
SDK_ORDNER = DOBOT_ORDNER / "sdk64"

sys.path.insert(0, str(SDK_ORDNER))

_dll_verzeichnis = None
if hasattr(os, "add_dll_directory"):
    _dll_verzeichnis = os.add_dll_directory(str(SDK_ORDNER))

import DobotDllType as dType


def alarme_lesen(api):
    """Liest die Nummern aller aktiven Alarme."""

    alarmdaten, laenge = dType.GetAlarmsState(api)
    aktive_alarme = []

    for byte_index, byte_wert in enumerate(alarmdaten[:laenge]):
        for bit_index in range(8):
            if byte_wert & (1 << bit_index):
                aktive_alarme.append(
                    byte_index * 8 + bit_index
                )

    return aktive_alarme


def warten_bis_fertig(api, ziel_index, timeout=90.0):
    """Wartet auf den letzten Queue-Befehl und überwacht Alarme."""

    startzeit = time.monotonic()

    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

        if aktueller_index >= ziel_index:
            return

        aktive_alarme = alarme_lesen(api)

        if aktive_alarme:
            dType.SetQueuedCmdStopExec(api)

            alarmcodes = ", ".join(
                f"0x{alarmnummer:02X}"
                for alarmnummer in aktive_alarme
            )

            raise RuntimeError(
                "Der Ablauf wurde wegen eines Alarms gestoppt: "
                f"{alarmcodes}"
            )

        if time.monotonic() - startzeit > timeout:
            dType.SetQueuedCmdStopExec(api)

            raise TimeoutError(
                "Der Tauschvorgang wurde nicht innerhalb von "
                f"{timeout:.1f} Sekunden beendet."
            )

        dType.dSleep(100)


def positionen_pruefen():
    """Prüft die horizontale Entfernung aller drei Plätze."""

    fehler = []

    for name, position in (
        ("Platz A", PLATZ_A),
        ("Platz B", PLATZ_B),
        ("Freier Platz", FREIER_PLATZ),
    ):
        x, y = position
        entfernung = math.hypot(x, y)

        print(
            f"{name:13}: X={x:7.1f}, Y={y:7.1f}, "
            f"Abstand={entfernung:7.1f} mm"
        )

        if entfernung > MAX_REICHWEITE_MM:
            fehler.append(
                f"{name} liegt mit {entfernung:.1f} mm "
                f"außerhalb der nominalen Reichweite "
                f"von {MAX_REICHWEITE_MM:.1f} mm."
            )

    return fehler


def ptp_einreihen(api, modus, x, y, z, r):
    """Reiht einen PTP-Fahrbefehl ein und gibt den Queue-Index zurück."""

    return dType.SetPTPCmd(
        api,
        modus,
        x,
        y,
        z,
        r,
        isQueued=1,
    )[0]


def sauger_einreihen(api, eingeschaltet):
    """Reiht einen Saugerbefehl ein und gibt den Queue-Index zurück."""

    return dType.SetEndEffectorSuctionCup(
        api,
        True,
        eingeschaltet,
        isQueued=1,
    )[0]


def warten_einreihen(api, dauer_ms):
    """Reiht eine Wartezeit ein und gibt den Queue-Index zurück."""

    return dType.SetWAITCmd(
        api,
        dauer_ms,
        1,
    )[0]


def wuerfel_verschieben(api, quelle, ziel, r):
    """Reiht das Aufnehmen und Absetzen eines Würfels ein."""

    qx, qy = quelle
    zx, zy = ziel

    # Über den Würfel fahren.
    ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVJXYZMode,
        qx,
        qy,
        ANFAHR_Z,
        r,
    )

    # Senkrecht auf die Würfeloberfläche absenken.
    ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        qx,
        qy,
        GREIF_Z,
        r,
    )

    # Würfel ansaugen.
    sauger_einreihen(api, True)
    warten_einreihen(api, SAUGER_WARTEZEIT_MS)

    # Würfel senkrecht anheben.
    ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        qx,
        qy,
        ANFAHR_Z,
        r,
    )

    # Über den Zielplatz fahren.
    ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVJXYZMode,
        zx,
        zy,
        ANFAHR_Z,
        r,
    )

    # Würfel senkrecht absetzen.
    ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        zx,
        zy,
        GREIF_Z,
        r,
    )

    # Würfel loslassen.
    sauger_einreihen(api, False)
    warten_einreihen(api, SAUGER_WARTEZEIT_MS)

    # Sauger wieder anheben.
    return ptp_einreihen(
        api,
        dType.PTPMode.PTPMOVLXYZMode,
        zx,
        zy,
        ANFAHR_Z,
        r,
    )


def main():
    print("Koordinatenprüfung")
    print("==================")

    fehler = positionen_pruefen()

    if fehler:
        print()
        print("Der Tauschvorgang wird nicht gestartet:")

        for meldung in fehler:
            print("  -", meldung)

        print()
        print(
            "Die Werte müssen direkte, erreichbare "
            "Dobot-Koordinaten sein."
        )
        return

    api = dType.load()
    verbunden = False

    try:
        verbindung = dType.ConnectDobot(
            api,
            COM_PORT,
            BAUDRATE,
        )

        print()
        print("Verbindungsrückgabe:", verbindung)

        if verbindung[0] != 0:
            raise ConnectionError(
                f"Verbindung über {COM_PORT} fehlgeschlagen "
                f"(Fehlercode {verbindung[0]})."
            )

        verbunden = True
        print("Dobot erfolgreich verbunden.")

        aktive_alarme = alarme_lesen(api)

        if aktive_alarme:
            alarmcodes = ", ".join(
                f"0x{nummer:02X}"
                for nummer in aktive_alarme
            )

            raise RuntimeError(
                "Der Ablauf wird wegen bereits aktiver Alarme "
                f"nicht gestartet: {alarmcodes}"
            )

        aktuelle_pose = dType.GetPose(api)
        r = aktuelle_pose[3]

        print()
        print(f"Greifhöhe:    Z={GREIF_Z:.1f} mm")
        print(f"Anfahrhöhe:   Z={ANFAHR_Z:.1f} mm")
        print(f"Werkzeug-R:   R={r:.1f}°")
        print()
        print("Geplanter Ablauf:")
        print("  1. Würfel A -> freier Platz")
        print("  2. Würfel B -> Platz A")
        print("  3. freier Platz -> Platz B")

        bestaetigung = input(
            "Arbeitsraum frei und Sauger montiert? Starten? (j/n): "
        ).strip().lower()

        if bestaetigung != "j":
            print("Der Tauschvorgang wurde nicht gestartet.")
            return

        # Sauger zunächst sicher ausschalten.
        dType.SetEndEffectorSuctionCup(
            api,
            True,
            False,
            isQueued=0,
        )

        # Queue vorbereiten.
        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdClear(api)

        # 1. A auf den freien Platz.
        wuerfel_verschieben(
            api,
            PLATZ_A,
            FREIER_PLATZ,
            r,
        )

        # 2. B auf den jetzt freien Platz A.
        wuerfel_verschieben(
            api,
            PLATZ_B,
            PLATZ_A,
            r,
        )

        # 3. Würfel vom Zwischenplatz auf Platz B.
        letzter_index = wuerfel_verschieben(
            api,
            FREIER_PLATZ,
            PLATZ_B,
            r,
        )

        print()
        print("Alle Befehle wurden in die Queue eingereiht.")
        print("Letzter Queue-Index:", letzter_index)
        print("Tauschvorgang wird gestartet.")

        dType.SetQueuedCmdStartExec(api)

        warten_bis_fertig(
            api,
            letzter_index,
            timeout=90.0,
        )

        print()
        print("Die Würfel wurden erfolgreich getauscht.")

    finally:
        if verbunden:
            # Sauger und Queue in einen sicheren Zustand bringen.
            try:
                dType.SetEndEffectorSuctionCup(
                    api,
                    True,
                    False,
                    isQueued=0,
                )
            except Exception:
                pass

            try:
                dType.SetQueuedCmdStopExec(api)
            except Exception:
                pass

            dType.DisconnectDobot(api)

            print()
            print("Sauger ausgeschaltet.")
            print("Queue gestoppt.")
            print("Verbindung zum Dobot getrennt.")


if __name__ == "__main__":
    main()
