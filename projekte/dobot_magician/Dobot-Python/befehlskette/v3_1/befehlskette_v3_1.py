"""Verständliche Dobot-Befehlsketten mit Tastatursteuerung.

Version 3.1 basiert auf Version 2.4.

Enthalten sind:
- Anzeige des jeweils nächsten Bewegungsbefehls vor der Ausführung,
- optionale Queue-Pausen nach Bewegungsbefehlen,
- Pause, Weiter, Halt und Status per Tastatur,
- endgültiger Abbruch der Befehlskette nach einem Halt.

Passendes Testprogramm:
    befehlskette_beispiel_v3.1.py
"""

from pathlib import Path
import queue
import sys
import threading
import time


VERSION = "3.1"
VERSIONSDATUM = "21.07.2026"

ZUSTAND_LAEUFT = "läuft"
ZUSTAND_PAUSIERT = "pausiert"
ZUSTAND_HALT = "Halt"
ZUSTAND_BEENDET = "beendet"


# Erwartete Struktur:
# Dobot-Python/
# ├── sdk64/
# └── projektordner/
#     ├── befehlskette_v3_1.py
#     └── befehlskette_beispiel_v3.1.py
HAUPTORDNER = Path(__file__).resolve().parent.parent

if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

from sdk64 import DobotDllType as dType


PTP_BEFEHLE = {
    "fahre_zu": dType.PTPMode.PTPMOVLXYZMode,
    "fahre_um": dType.PTPMode.PTPMOVLXYZINCMode,
    "springe_auf": dType.PTPMode.PTPJUMPXYZMode,
}


def version():
    """Gibt die Versionsinformation des Moduls zurück."""

    return (
        f"befehlskette_v3_1.py Version {VERSION} "
        f"vom {VERSIONSDATUM}"
    )


def befehlskette_erstellen(api, befehle, standard_pause_ms=0):
    """Trägt Bewegungen und optionale Pausen in die Dobot-Queue ein.

    Ein Befehl kann sechs oder sieben Einträge besitzen:

        (Name, X, Y, Z, R, Text)
        (Name, X, Y, Z, R, Text, Pause_ms)

    Ohne siebten Eintrag wird ``standard_pause_ms`` verwendet.
    Bei einer Pause von 0 wird kein WAIT-Befehl erzeugt.
    """

    if (
        not isinstance(standard_pause_ms, (int, float))
        or standard_pause_ms < 0
    ):
        raise ValueError(
            "standard_pause_ms muss eine nicht negative Zahl sein."
        )

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
                f"{befehlsnummer}. Erlaubt: "
                f"{', '.join(PTP_BEFEHLE)}."
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
            # SetWAITCmd() erwartet in der verwendeten
            # DobotDllType.py Sekunden.
            warteindex = dType.SetWAITCmd(
                api,
                pause_ms / 1000.0,
                isQueued=1,
            )[0]

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
            f'{daten["nummer"]:2d}. '
            f"Queue-Index {bewegungsindex:3d}: "
            f'{daten["befehl"]}({x}, {y}, {z}, {r}) – '
            f'{daten["text"]}{pause_text}'
        )


def _letzter_queue_index(queue_befehle):
    """Gibt den letzten Bewegungs- oder WAIT-Index zurück."""

    letzter_index = 0

    for bewegungsindex, daten in queue_befehle.items():
        letzter_index = max(letzter_index, bewegungsindex)

        if daten["warteindex"] is not None:
            letzter_index = max(
                letzter_index,
                daten["warteindex"],
            )

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


def _faellige_befehle_anzeigen(
    queue_befehle,
    bewegungsindizes,
    naechste_position,
    aktueller_index,
):
    """Zeigt alle inzwischen fälligen nächsten Bewegungsbefehle an."""

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

    return naechste_position


def _tastatur_einlesen(
    steuerbefehle,
    eingabe_beenden,
):
    """Liest Steuerbefehle und legt sie in einer Queue ab.

    Dieser Thread ruft keine Funktion aus DobotDllType.py auf.
    """

    while not eingabe_beenden.is_set():
        try:
            eingabe = input("> ").strip().lower()

        except EOFError:
            return

        if eingabe_beenden.is_set():
            return

        if eingabe in ("p", "w", "h", "?"):
            steuerbefehle.put(eingabe)

        elif eingabe:
            print(
                "Unbekannter Steuerbefehl. "
                "Erlaubt sind p, w, h und ?."
            )


def tastatursteuerung_starten(
    steuerbefehle,
    eingabe_beenden,
):
    """Startet die Tastaturabfrage als Daemon-Thread."""

    print("\nSteuerung während der Ausführung:")
    print("  p + Enter = Pause")
    print("  w + Enter = Weiter")
    print("  h + Enter = Halt")
    print("  ? + Enter = Status")

    thread = threading.Thread(
        target=_tastatur_einlesen,
        args=(steuerbefehle, eingabe_beenden),
        daemon=True,
        name="Dobot-Tastatursteuerung",
    )

    thread.start()

    return thread


def _halt_ausfuehren(api):
    """Stoppt auch einen aktuell ausgeführten Queue-Befehl."""

    if not hasattr(dType, "SetQueuedCmdForceStopExec"):
        raise RuntimeError(
            "Die verwendete DobotDllType.py enthält "
            "SetQueuedCmdForceStopExec() nicht."
        )

    dType.SetQueuedCmdForceStopExec(api)


def befehlskette_ausfuehren(api, queue_befehle, timeout=30.0):
    """Startet die Queue ohne Tastatursteuerung.

    Diese Funktion entspricht weiterhin dem Verhalten von Version 2.4.
    Der jeweils nächste Bewegungsbefehl wird vor seiner Ausführung
    angezeigt.
    """

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return

    bewegungsindizes = sorted(queue_befehle)
    letzter_queue_index = _letzter_queue_index(queue_befehle)
    startzeit = time.monotonic()

    _befehl_vor_ausfuehrung_anzeigen(
        queue_befehle,
        bewegungsindizes[0],
    )

    naechste_position = 1

    dType.SetQueuedCmdStartExec(api)

    while True:
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]

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

        naechste_position = _faellige_befehle_anzeigen(
            queue_befehle,
            bewegungsindizes,
            naechste_position,
            aktueller_index,
        )

        if aktueller_index >= letzter_queue_index:
            print("Befehlskette vollständig ausgeführt.")
            return

        if time.monotonic() - startzeit > timeout:
            dType.SetQueuedCmdStopExec(api)

            raise TimeoutError(
                f"Die Befehlskette wurde nicht innerhalb von "
                f"{timeout:.1f} Sekunden beendet. "
                f"Aktueller Queue-Index: {aktueller_index}, "
                f"erwarteter letzter Index: "
                f"{letzter_queue_index}."
            )

        dType.dSleep(100)


def befehlskette_ausfuehren_steuerbar(
    api,
    queue_befehle,
    timeout=30.0,
    steuerbefehle=None,
    tastatur=True,
):
    """Führt die Befehlskette mit Tastatursteuerung aus.

    Befehle:
        p + Enter  Pause
        w + Enter  Weiter
        h + Enter  Halt
        ? + Enter  Status

    Pause:
        SetQueuedCmdStopExec() lässt den aktuellen Queue-Befehl
        noch enden und stoppt danach die weitere Abarbeitung.
        Mit Weiter kann die Queue fortgesetzt werden.

    Halt:
        SetQueuedCmdForceStopExec() bricht auch den aktuell
        ausgeführten Queue-Befehl ab. Danach wird diese
        Befehlskette nicht fortgesetzt.

    Über ``steuerbefehle`` können später auch andere Signalquellen
    dieselben Steuerzeichen bereitstellen.
    """

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return "leer"

    if timeout <= 0:
        raise ValueError("timeout muss größer als 0 sein.")

    if steuerbefehle is None:
        steuerbefehle = queue.Queue()

    eingabe_beenden = threading.Event()

    bewegungsindizes = sorted(queue_befehle)
    letzter_queue_index = _letzter_queue_index(queue_befehle)
    naechste_position = 1

    zustand = ZUSTAND_LAEUFT
    startzeit = time.monotonic()
    pausenbeginn = None
    gesamte_pausendauer = 0.0

    if tastatur:
        tastatursteuerung_starten(
            steuerbefehle,
            eingabe_beenden,
        )

    _befehl_vor_ausfuehrung_anzeigen(
        queue_befehle,
        bewegungsindizes[0],
    )

    dType.SetQueuedCmdStartExec(api)

    try:
        while True:
            aktueller_index = (
                dType.GetQueuedCmdCurrentIndex(api)[0]
            )

            # Alle inzwischen eingegangenen Steuerbefehle bearbeiten.
            while True:
                try:
                    steuerbefehl = steuerbefehle.get_nowait()

                except queue.Empty:
                    break

                if steuerbefehl == "p":
                    if zustand == ZUSTAND_LAEUFT:
                        dType.SetQueuedCmdStopExec(api)
                        zustand = ZUSTAND_PAUSIERT
                        pausenbeginn = time.monotonic()

                        print()
                        print("PAUSE angefordert.")
                        print(
                            "Der aktuelle Queue-Befehl wird noch "
                            "beendet."
                        )
                        print(
                            "Mit 'w' + Enter wird die "
                            "Befehlskette fortgesetzt."
                        )

                    else:
                        print()
                        print(
                            "Pause nicht ausgeführt: "
                            f"Zustand ist '{zustand}'."
                        )

                elif steuerbefehl == "w":
                    if zustand == ZUSTAND_PAUSIERT:
                        if pausenbeginn is not None:
                            gesamte_pausendauer += (
                                time.monotonic()
                                - pausenbeginn
                            )
                            pausenbeginn = None

                        # Falls der vorige Befehl während der Pause
                        # beendet wurde, den nächsten Befehl vor dem
                        # Wiederanlauf anzeigen.
                        naechste_position = (
                            _faellige_befehle_anzeigen(
                                queue_befehle,
                                bewegungsindizes,
                                naechste_position,
                                aktueller_index,
                            )
                        )

                        dType.SetQueuedCmdStartExec(api)
                        zustand = ZUSTAND_LAEUFT

                        print()
                        print(
                            "WEITER: Die Befehlskette läuft weiter."
                        )

                    else:
                        print()
                        print(
                            "Weiter nicht ausgeführt: "
                            f"Zustand ist '{zustand}'."
                        )

                elif steuerbefehl == "h":
                    _halt_ausfuehren(api)
                    zustand = ZUSTAND_HALT

                    print()
                    print("HALT!")
                    print(
                        "Die aktuelle Bewegung und die "
                        "Befehlskette wurden abgebrochen."
                    )
                    print(
                        "Die Befehlskette kann nicht "
                        "fortgesetzt werden."
                    )

                    return ZUSTAND_HALT

                elif steuerbefehl == "?":
                    print()
                    print(f"Zustand: {zustand}")
                    print(
                        f"Aktueller Queue-Index: "
                        f"{aktueller_index}"
                    )
                    print(
                        f"Letzter Queue-Index: "
                        f"{letzter_queue_index}"
                    )

            alarmdaten = dType.GetAlarmsState(api)
            alarmbytes = alarmdaten[0] if alarmdaten else []

            if any(alarmbytes):
                dType.SetQueuedCmdStopExec(api)

                print()
                print("Alarmdaten:", list(alarmbytes))

                raise RuntimeError(
                    f"Die Ausführung wurde bei Queue-Index "
                    f"{aktueller_index} durch einen Alarm "
                    "gestoppt."
                )

            # Während einer Pause wird kein neuer Befehl angekündigt.
            # Er wird unmittelbar vor dem Wiederanlauf angezeigt.
            if zustand == ZUSTAND_LAEUFT:
                naechste_position = (
                    _faellige_befehle_anzeigen(
                        queue_befehle,
                        bewegungsindizes,
                        naechste_position,
                        aktueller_index,
                    )
                )

            if aktueller_index >= letzter_queue_index:
                print("Befehlskette vollständig ausgeführt.")
                return ZUSTAND_BEENDET

            # Die Bedienpause wird nicht auf den Timeout angerechnet.
            if zustand == ZUSTAND_LAEUFT:
                laufzeit_ohne_pause = (
                    time.monotonic()
                    - startzeit
                    - gesamte_pausendauer
                )

                if laufzeit_ohne_pause > timeout:
                    dType.SetQueuedCmdStopExec(api)

                    raise TimeoutError(
                        f"Die Befehlskette wurde nicht innerhalb "
                        f"von {timeout:.1f} Sekunden beendet. "
                        f"Aktueller Queue-Index: "
                        f"{aktueller_index}, "
                        f"erwarteter letzter Index: "
                        f"{letzter_queue_index}."
                    )

            dType.dSleep(100)

    finally:
        eingabe_beenden.set()
