"""Verständliche Dobot-Befehlsketten mit optionalen Queue-Pausen.

Version 2.4:
Der jeweils nächste Bewegungsbefehl wird vor seiner Ausführung
in der Kommandozeile angezeigt.
"""

from pathlib import Path
import sys
import time

VERSION = "2.4"

# Erwartete Struktur:
# Dobot-Python/
# ├── sdk64/
# └── projektordner/
#     ├── befehlskette_v2_4.py
#     └── befehlskette_beispiel_v2.4.py
HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

from sdk64 import DobotDllType as dType


PTP_BEFEHLE = {
    "fahre_zu": dType.PTPMode.PTPMOVLXYZMode,
    "fahre_um": dType.PTPMode.PTPMOVLXYZINCMode,
    "springe_auf": dType.PTPMode.PTPJUMPXYZMode,
}


def befehlskette_erstellen(api, befehle, standard_pause_ms=0):
    """Trägt Bewegungen und optionale Pausen in die Dobot-Queue ein.

    Ein Befehl kann sechs oder sieben Einträge besitzen:

        (Name, X, Y, Z, R, Text)
        (Name, X, Y, Z, R, Text, Pause_ms)

    Ohne siebten Eintrag wird ``standard_pause_ms`` verwendet.
    Bei einer Pause von 0 wird kein WAIT-Befehl erzeugt.
    """

    if not isinstance(standard_pause_ms, (int, float)) or standard_pause_ms < 0:
        raise ValueError("standard_pause_ms muss eine nicht negative Zahl sein.")

    queue_befehle = {}

    for befehlsnummer, befehl in enumerate(befehle, start=1):
        if len(befehl) == 6:
            befehlsname, x, y, z, r, text = befehl
            pause_ms = standard_pause_ms
        elif len(befehl) == 7:
            befehlsname, x, y, z, r, text, pause_ms = befehl
        else:
            raise ValueError(
                f"Befehl {befehlsnummer} benötigt 6 oder 7 Einträge: "
                "(Name, X, Y, Z, R, Text[, Pause_ms])."
            )

        befehlsname = str(befehlsname).strip().lower()

        if befehlsname not in PTP_BEFEHLE:
            raise ValueError(
                f"Unbekannter Befehl '{befehlsname}' in Befehl "
                f"{befehlsnummer}. Erlaubt: {', '.join(PTP_BEFEHLE)}."
            )

        if not isinstance(pause_ms, (int, float)) or pause_ms < 0:
            raise ValueError(
                f"Die Pause in Befehl {befehlsnummer} muss eine "
                "nicht negative Zahl sein."
            )

        pause_ms = int(pause_ms)

        bewegungsindex = dType.SetPTPCmd(
            api,
            PTP_BEFEHLE[befehlsname],
            x,
            y,
            z,
            r,
            isQueued=1,
        )[0]

        warteindex = None
        if pause_ms > 0:
            warteindex = dType.SetWAITCmd(api, pause_ms / 1000.0, isQueued=1)[0]

        queue_befehle[bewegungsindex] = {
            "nummer": befehlsnummer,
            "befehl": befehlsname,
            "position": (x, y, z, r),
            "text": str(text),
            "pause_ms": pause_ms,
            "warteindex": warteindex,
        }

    return queue_befehle


def befehlskette_anzeigen(queue_befehle):
    """Zeigt die eingetragene Queue vor dem Start an."""

    print("\nErstellte Befehlskette:")

    for bewegungsindex, daten in queue_befehle.items():
        x, y, z, r = daten["position"]
        pause = daten["pause_ms"]
        pause_text = f" | Pause: {pause} ms" if pause else ""

        print(
            f'{daten["nummer"]:2d}. Queue-Index {bewegungsindex:3d}: '
            f'{daten["befehl"]}({x}, {y}, {z}, {r}) – '
            f'{daten["text"]}{pause_text}'
        )


def _letzter_queue_index(queue_befehle):
    """Gibt den letzten Bewegungs- oder WAIT-Index zurück."""

    letzter_index = 0

    for bewegungsindex, daten in queue_befehle.items():
        letzter_index = max(letzter_index, bewegungsindex)
        if daten["warteindex"] is not None:
            letzter_index = max(letzter_index, daten["warteindex"])

    return letzter_index


def _befehl_vor_ausfuehrung_anzeigen(
    queue_befehle,
    bewegungsindex,
):
    """Zeigt einen Bewegungsbefehl vor seiner Ausführung an."""

    daten = queue_befehle[bewegungsindex]

    print(
        f'Befehl {daten["nummer"]} wird als Nächstes ausgeführt: '
        f'{daten["text"]} '
        f'(Queue-Index {bewegungsindex})',
        flush=True,
    )


def befehlskette_ausfuehren(api, queue_befehle, timeout=30.0):
    """Startet die Queue und zeigt jeden Befehl vorher an.

    Der erste Bewegungsbefehl wird unmittelbar vor dem Start der
    Queue angezeigt.

    Jeder weitere Bewegungsbefehl wird angezeigt, sobald der
    vorherige Bewegungsbefehl beendet ist. Liegt nach dem vorherigen
    Befehl eine Queue-Pause, erfolgt die Anzeige während dieser Pause
    und damit eindeutig vor der nächsten Bewegung.
    """

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return

    bewegungsindizes = sorted(queue_befehle)
    letzter_queue_index = _letzter_queue_index(queue_befehle)
    startzeit = time.monotonic()

    # Der erste Befehl wird sicher vor dem Start der Queue angezeigt.
    _befehl_vor_ausfuehrung_anzeigen(
        queue_befehle,
        bewegungsindizes[0],
    )

    naechste_position = 1

    dType.SetQueuedCmdStartExec(api)

    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

        # Alarmzustand genau einmal pro Schleifendurchlauf prüfen.
        alarmdaten = dType.GetAlarmsState(api)
        alarmbytes = alarmdaten[0] if alarmdaten else []

        if any(alarmbytes):
            dType.SetQueuedCmdStopExec(api)

            print()
            print("Alarmdaten:", list(alarmbytes))

            raise RuntimeError(
                f"Die Ausführung wurde bei Queue-Index "
                f"{aktueller_index} durch einen Alarm gestoppt."
            )

        # Der nächste Befehl wird angekündigt, sobald die vorherige
        # Bewegung beendet ist. Eine nachfolgende Queue-Pause dient
        # dabei als Vorlauf vor der nächsten Bewegung.
        while naechste_position < len(bewegungsindizes):
            vorheriger_index = bewegungsindizes[
                naechste_position - 1
            ]

            if aktueller_index < vorheriger_index:
                break

            naechster_index = bewegungsindizes[
                naechste_position
            ]

            _befehl_vor_ausfuehrung_anzeigen(
                queue_befehle,
                naechster_index,
            )

            naechste_position += 1

        if aktueller_index >= letzter_queue_index:
            print("Befehlskette vollständig ausgeführt.")
            return

        if time.monotonic() - startzeit > timeout:
            dType.SetQueuedCmdStopExec(api)

            raise TimeoutError(
                f"Die Befehlskette wurde nicht innerhalb von "
                f"{timeout:.1f} Sekunden beendet. "
                f"Aktueller Queue-Index: {aktueller_index}, "
                f"erwarteter letzter Index: {letzter_queue_index}."
            )

        dType.dSleep(100)
