"""Verständliche Dobot-Befehlsketten mit mehreren Steuerquellen.

Version 3.3 basiert auf Version 3.2.

Neu:
- gemeinsame Steuerbefehls-Queue für Tastatur und ESP32,
- Steuerquelle wird bei Pause, Weiter, Halt und Status angezeigt,
- lange Befehle wie PAUSE oder STATUS werden ebenfalls erkannt.

Passendes Testprogramm:
    befehlskette_beispiel_v3.3.py
"""

from pathlib import Path
import queue
import sys
import threading
import time


VERSION = "3.3"
VERSIONSDATUM = "21.07.2026"

ZUSTAND_LAEUFT = "läuft"
ZUSTAND_PAUSIERT = "pausiert"
ZUSTAND_HALT = "Halt"
ZUSTAND_BEENDET = "beendet"

# GetEndEffectorSuctionCup() ist kein Queue-Befehl.
# Für eine zeitlich zugeordnete Abfrage wird daher ein kurzer
# WAIT-Befehl als Markierung in die Queue eingefügt.
SAUGER_STATUS_MARKER_MS = 500


# Erwartete Struktur:
# Dobot-Python/
# ├── sdk64/
# └── projektordner/
#     ├── befehlskette_v3_3.py
#     ├── befehlskette_beispiel_v3.3.py
#     └── esp32_seriell_v1_0.py
HAUPTORDNER = Path(__file__).resolve().parent.parent

if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

from sdk64 import DobotDllType as dType


PTP_BEFEHLE = {
    "fahre_zu": dType.PTPMode.PTPMOVLXYZMode,
    "fahre_um": dType.PTPMode.PTPMOVLXYZINCMode,
    "springe_auf": dType.PTPMode.PTPJUMPXYZMode,
}

SAUGER_BEFEHLE = {
    "sauger_ein",
    "sauger_aus",
    "sauger_status",
}


STEUERBEFEHLE = {
    "p": "p",
    "pause": "p",
    "w": "w",
    "weiter": "w",
    "h": "h",
    "halt": "h",
    "?": "?",
    "status": "?",
}

STEUERBEFEHL_NAMEN = {
    "p": "PAUSE",
    "w": "WEITER",
    "h": "HALT",
    "?": "STATUS",
}


def version():
    """Gibt die Versionsinformation des Moduls zurück."""

    return (
        f"befehlskette_v3_3.py Version {VERSION} "
        f"vom {VERSIONSDATUM}"
    )


def _pause_pruefen(pause_ms, befehlsnummer):
    """Prüft und normalisiert eine Pausenangabe."""

    if not isinstance(pause_ms, (int, float)) or pause_ms < 0:
        raise ValueError(
            f"Die Pause in Befehl {befehlsnummer} muss eine "
            "nicht negative Zahl sein."
        )

    return int(pause_ms)


def _bewegungsbefehl_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Liest einen PTP-Befehl aus der Befehlsliste."""

    if len(befehl) == 6:
        befehlsname, x, y, z, r, text = befehl
        pause_ms = standard_pause_ms

    elif len(befehl) == 7:
        befehlsname, x, y, z, r, text, pause_ms = befehl

    else:
        raise ValueError(
            f"Bewegungsbefehl {befehlsnummer} benötigt "
            "6 oder 7 Einträge:\n"
            "(Name, X, Y, Z, R, Text[, Pause_ms])."
        )

    return {
        "befehl": befehlsname,
        "art": "bewegung",
        "position": (x, y, z, r),
        "text": str(text),
        "pause_ms": _pause_pruefen(
            pause_ms,
            befehlsnummer,
        ),
    }


def _saugerbefehl_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Liest einen Saugerbefehl aus der Befehlsliste.

    Erlaubte Formen:

        ("sauger_ein",)
        ("sauger_ein", "Text")
        ("sauger_ein", "Text", Pause_ms)

    Entsprechend auch für ``sauger_aus`` und
    ``sauger_status``.
    """

    befehlsname = str(befehl[0]).strip().lower()

    standardtexte = {
        "sauger_ein": "Sauger einschalten",
        "sauger_aus": "Sauger ausschalten",
        "sauger_status": "Saugerstatus anzeigen",
    }

    if len(befehl) == 1:
        text = standardtexte[befehlsname]
        pause_ms = standard_pause_ms

    elif len(befehl) == 2:
        _, text = befehl
        pause_ms = standard_pause_ms

    elif len(befehl) == 3:
        _, text, pause_ms = befehl

    else:
        raise ValueError(
            f"Saugerbefehl {befehlsnummer} benötigt "
            "1, 2 oder 3 Einträge:\n"
            "(Name[, Text[, Pause_ms]])."
        )

    return {
        "befehl": befehlsname,
        "art": befehlsname,
        "position": None,
        "text": str(text),
        "pause_ms": _pause_pruefen(
            pause_ms,
            befehlsnummer,
        ),
    }


def _befehl_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Prüft einen Listeneintrag und gibt seine Daten zurück."""

    if not isinstance(befehl, (list, tuple)) or not befehl:
        raise ValueError(
            f"Befehl {befehlsnummer} muss eine nicht leere "
            "Liste oder ein Tupel sein."
        )

    befehlsname = str(befehl[0]).strip().lower()

    if befehlsname in PTP_BEFEHLE:
        daten = _bewegungsbefehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

    elif befehlsname in SAUGER_BEFEHLE:
        daten = _saugerbefehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

    else:
        erlaubte_befehle = (
            list(PTP_BEFEHLE)
            + sorted(SAUGER_BEFEHLE)
        )

        raise ValueError(
            f"Unbekannter Befehl '{befehlsname}' in "
            f"Befehl {befehlsnummer}. Erlaubt: "
            f"{', '.join(erlaubte_befehle)}."
        )

    daten["befehl"] = befehlsname
    daten["nummer"] = befehlsnummer

    return daten


def _queue_befehl_eintragen(api, daten):
    """Trägt einen geprüften Befehl in die Dobot-Queue ein."""

    befehlsname = daten["befehl"]

    if daten["art"] == "bewegung":
        x, y, z, r = daten["position"]

        return dType.SetPTPCmd(
            api,
            PTP_BEFEHLE[befehlsname],
            x,
            y,
            z,
            r,
            isQueued=1,
        )[0]

    if befehlsname == "sauger_ein":
        return dType.SetEndEffectorSuctionCup(
            api,
            True,
            True,
            isQueued=1,
        )[0]

    if befehlsname == "sauger_aus":
        return dType.SetEndEffectorSuctionCup(
            api,
            True,
            False,
            isQueued=1,
        )[0]

    if befehlsname == "sauger_status":
        # Die Statusabfrage selbst ist nicht queuefähig.
        # Der WAIT-Befehl dient als zeitliche Markierung.
        return dType.SetWAITCmd(
            api,
            SAUGER_STATUS_MARKER_MS / 1000.0,
            isQueued=1,
        )[0]

    raise RuntimeError(
        f"Interner Fehler: Befehl '{befehlsname}' "
        "konnte nicht eingetragen werden."
    )


def befehlskette_erstellen(api, befehle, standard_pause_ms=0):
    """Trägt Bewegungs- und Saugerbefehle in die Queue ein.

    Bewegungsbefehle:

        ("fahre_zu", X, Y, Z, R, "Text")
        ("fahre_zu", X, Y, Z, R, "Text", Pause_ms)

    Saugerbefehle:

        ("sauger_ein",)
        ("sauger_ein", "Text")
        ("sauger_ein", "Text", Pause_ms)

        ("sauger_aus", ...)
        ("sauger_status", ...)

    Ohne eigene Pausenangabe wird ``standard_pause_ms``
    verwendet. Bei 0 wird kein zusätzlicher WAIT-Befehl erzeugt.
    """

    if (
        not isinstance(standard_pause_ms, (int, float))
        or standard_pause_ms < 0
    ):
        raise ValueError(
            "standard_pause_ms muss eine nicht negative Zahl sein."
        )

    queue_befehle = {}

    for befehlsnummer, befehl in enumerate(
        befehle,
        start=1,
    ):
        daten = _befehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

        befehlsindex = _queue_befehl_eintragen(
            api,
            daten,
        )

        warteindex = None
        pause_ms = daten["pause_ms"]

        if pause_ms > 0:
            # SetWAITCmd() erwartet in der verwendeten
            # DobotDllType.py Sekunden.
            warteindex = dType.SetWAITCmd(
                api,
                pause_ms / 1000.0,
                isQueued=1,
            )[0]

        daten["warteindex"] = warteindex

        queue_befehle[befehlsindex] = daten

    return queue_befehle


def _befehl_darstellen(daten):
    """Erzeugt die kurze Darstellung eines Befehls."""

    if daten["art"] == "bewegung":
        x, y, z, r = daten["position"]

        return (
            f'{daten["befehl"]}'
            f"({x}, {y}, {z}, {r})"
        )

    return f'{daten["befehl"]}()'


def befehlskette_anzeigen(queue_befehle):
    """Zeigt die eingetragene Queue vor dem Start an."""

    print("\nErstellte Befehlskette:")

    for befehlsindex, daten in queue_befehle.items():
        pause_ms = daten["pause_ms"]
        pause_text = (
            f" | Pause: {pause_ms} ms"
            if pause_ms
            else ""
        )

        status_text = ""

        if daten["art"] == "sauger_status":
            status_text = (
                f" | Statusmarke: "
                f"{SAUGER_STATUS_MARKER_MS} ms"
            )

        print(
            f'{daten["nummer"]:2d}. '
            f"Queue-Index {befehlsindex:3d}: "
            f'{_befehl_darstellen(daten)} – '
            f'{daten["text"]}'
            f'{status_text}{pause_text}'
        )


def _letzter_queue_index(queue_befehle):
    """Gibt den letzten Befehls- oder WAIT-Index zurück."""

    letzter_index = 0

    for befehlsindex, daten in queue_befehle.items():
        letzter_index = max(
            letzter_index,
            befehlsindex,
        )

        if daten["warteindex"] is not None:
            letzter_index = max(
                letzter_index,
                daten["warteindex"],
            )

    return letzter_index


def _befehl_vor_ausfuehrung_anzeigen(
    queue_befehle,
    befehlsindex,
):
    """Zeigt einen Befehl vor seiner Ausführung an."""

    daten = queue_befehle[befehlsindex]

    print(
        f'Befehl {daten["nummer"]} wird als Nächstes ausgeführt: '
        f'{daten["text"]} '
        f'[{_befehl_darstellen(daten)}, '
        f"Queue-Index {befehlsindex}]",
        flush=True,
    )


def _faellige_befehle_anzeigen(
    queue_befehle,
    befehlsindizes,
    naechste_position,
    aktueller_index,
):
    """Zeigt alle inzwischen fälligen nächsten Befehle an."""

    while naechste_position < len(befehlsindizes):
        vorheriger_index = befehlsindizes[
            naechste_position - 1
        ]

        if aktueller_index < vorheriger_index:
            break

        naechster_index = befehlsindizes[
            naechste_position
        ]

        _befehl_vor_ausfuehrung_anzeigen(
            queue_befehle,
            naechster_index,
        )

        naechste_position += 1

    return naechste_position


def _sauger_status_anzeigen(api, daten, befehlsindex):
    """Liest und zeigt den aktuellen Pumpenschaltzustand."""

    rueckgabe = dType.GetEndEffectorSuctionCup(api)
    sauger_ein = bool(rueckgabe[0])

    if sauger_ein:
        status_text = "EIN"
    else:
        status_text = "AUS"

    print(
        f'Saugerstatus bei Befehl {daten["nummer"]}: '
        f"{status_text} "
        f"(Queue-Index {befehlsindex})"
    )
    print(
        "Hinweis: Der Status bestätigt den Pumpenbefehl, "
        "nicht das sichere Ansaugen eines Werkstücks."
    )


def _faellige_statusbefehle_ausfuehren(
    api,
    queue_befehle,
    aktueller_index,
    ausgefuehrte_statusbefehle,
):
    """Führt erreichte sauger_status-Abfragen einmalig aus."""

    for befehlsindex in sorted(queue_befehle):
        daten = queue_befehle[befehlsindex]

        if daten["art"] != "sauger_status":
            continue

        if befehlsindex in ausgefuehrte_statusbefehle:
            continue

        if aktueller_index < befehlsindex:
            continue

        _sauger_status_anzeigen(
            api,
            daten,
            befehlsindex,
        )

        ausgefuehrte_statusbefehle.add(
            befehlsindex
        )


def steuerbefehl_normalisieren(eingabe):
    """Übersetzt kurze und lange Steuerbefehle.

    Beispiele:
        p, PAUSE   -> p
        w, WEITER  -> w
        h, HALT    -> h
        ?, STATUS  -> ?
    """

    text = str(eingabe).strip().lower()
    return STEUERBEFEHLE.get(text)


def steuerbefehl_einreihen(
    steuerbefehle,
    eingabe,
    quelle="extern",
):
    """Legt einen gültigen Steuerbefehl in der Queue ab.

    Der Queue-Eintrag enthält den normierten Befehl und die
    Bezeichnung seiner Quelle, zum Beispiel ``ESP32``.
    """

    steuerbefehl = steuerbefehl_normalisieren(eingabe)

    if steuerbefehl is None:
        return False

    steuerbefehle.put(
        (steuerbefehl, str(quelle))
    )

    return True


def _steuerbefehl_entpacken(eintrag):
    """Liest neue und ältere Queue-Einträge.

    Für die Abwärtskompatibilität werden auch einzelne Zeichen
    wie ``"p"`` ohne Quellenangabe akzeptiert.
    """

    if (
        isinstance(eintrag, (tuple, list))
        and len(eintrag) == 2
    ):
        eingabe, quelle = eintrag
    else:
        eingabe = eintrag
        quelle = "extern"

    steuerbefehl = steuerbefehl_normalisieren(eingabe)

    if steuerbefehl is None:
        return None, str(quelle)

    return steuerbefehl, str(quelle)


def _tastatur_einlesen(
    steuerbefehle,
    eingabe_beenden,
):
    """Liest Steuerbefehle und legt sie in einer Queue ab."""

    while not eingabe_beenden.is_set():
        try:
            eingabe = input("> ").strip()

        except EOFError:
            return

        if eingabe_beenden.is_set():
            return

        if eingabe and not steuerbefehl_einreihen(
            steuerbefehle,
            eingabe,
            quelle="Tastatur",
        ):
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


def _alarm_pruefen(api, aktueller_index):
    """Prüft den Dobot auf aktive Alarme."""

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


def befehlskette_ausfuehren(api, queue_befehle, timeout=30.0):
    """Startet die Queue ohne Tastatursteuerung."""

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return

    befehlsindizes = sorted(queue_befehle)
    letzter_queue_index = _letzter_queue_index(
        queue_befehle
    )
    startzeit = time.monotonic()
    ausgefuehrte_statusbefehle = set()

    _befehl_vor_ausfuehrung_anzeigen(
        queue_befehle,
        befehlsindizes[0],
    )

    naechste_position = 1

    dType.SetQueuedCmdStartExec(api)

    while True:
        aktueller_index = (
            dType.GetQueuedCmdCurrentIndex(api)[0]
        )

        _alarm_pruefen(api, aktueller_index)

        naechste_position = _faellige_befehle_anzeigen(
            queue_befehle,
            befehlsindizes,
            naechste_position,
            aktueller_index,
        )

        _faellige_statusbefehle_ausfuehren(
            api,
            queue_befehle,
            aktueller_index,
            ausgefuehrte_statusbefehle,
        )

        if aktueller_index >= letzter_queue_index:
            print("Befehlskette vollständig ausgeführt.")
            return ZUSTAND_BEENDET

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
    """Führt die Befehlskette mit mehreren Steuerquellen aus.

    Tastatur oder ESP32:
        p / PAUSE   Pause
        w / WEITER  Weiter
        h / HALT    Halt
        ? / STATUS  Status der Befehlskette

    Alle Quellen schreiben ausschließlich in ``steuerbefehle``.
    Nur diese Hauptschleife ruft die Dobot-API auf.
    """

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return "leer"

    if timeout <= 0:
        raise ValueError("timeout muss größer als 0 sein.")

    if steuerbefehle is None:
        steuerbefehle = queue.Queue()

    eingabe_beenden = threading.Event()

    befehlsindizes = sorted(queue_befehle)
    letzter_queue_index = _letzter_queue_index(
        queue_befehle
    )
    naechste_position = 1
    ausgefuehrte_statusbefehle = set()

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
        befehlsindizes[0],
    )

    dType.SetQueuedCmdStartExec(api)

    try:
        while True:
            aktueller_index = (
                dType.GetQueuedCmdCurrentIndex(api)[0]
            )

            while True:
                try:
                    eintrag = steuerbefehle.get_nowait()

                except queue.Empty:
                    break

                steuerbefehl, steuerquelle = (
                    _steuerbefehl_entpacken(eintrag)
                )

                if steuerbefehl is None:
                    print(
                        f"Unbekannter Steuerbefehl von "
                        f"{steuerquelle}: {eintrag!r}"
                    )
                    continue

                print()
                print(
                    f"Steuerbefehl von {steuerquelle}: "
                    f"{STEUERBEFEHL_NAMEN[steuerbefehl]}"
                )

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

                        naechste_position = (
                            _faellige_befehle_anzeigen(
                                queue_befehle,
                                befehlsindizes,
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

            _alarm_pruefen(api, aktueller_index)

            _faellige_statusbefehle_ausfuehren(
                api,
                queue_befehle,
                aktueller_index,
                ausgefuehrte_statusbefehle,
            )

            if zustand == ZUSTAND_LAEUFT:
                naechste_position = (
                    _faellige_befehle_anzeigen(
                        queue_befehle,
                        befehlsindizes,
                        naechste_position,
                        aktueller_index,
                    )
                )

            if aktueller_index >= letzter_queue_index:
                print("Befehlskette vollständig ausgeführt.")
                return ZUSTAND_BEENDET

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
