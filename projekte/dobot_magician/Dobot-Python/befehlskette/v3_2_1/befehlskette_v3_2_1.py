"""Verständliche Dobot-Befehlsketten mit kontrolliertem Fehlerbetrieb.

Version 3.2.1 basiert auf Version 3.2.

Neu:
- Ein Dobot-Alarm führt nicht mehr zum Programmabsturz.
- Die laufende Queue wird endgültig gestoppt und gelöscht.
- Ein interaktiver Fehlerbetrieb ermöglicht anschließend Sofortbefehle:
    1  Fahrt zu frei gewählten Koordinaten
    2  Fahrt zu einer vorgegebenen Ausgangsposition
    3  Saugerstatus
    4  Sauger ausschalten
    5  Programmende bei ausgeschaltetem Sauger
    9  Programmende erzwingen
- Die alte Befehlskette kann nach einem Alarm nicht fortgesetzt werden.

Passendes Testprogramm:
    befehlskette_beispiel_v3.2.1.py
"""

from pathlib import Path
import queue
import sys
import threading
import time


VERSION = "3.2.1"
VERSIONSDATUM = "22.07.2026"

ZUSTAND_LAEUFT = "läuft"
ZUSTAND_PAUSIERT = "pausiert"
ZUSTAND_HALT = "Halt"
ZUSTAND_FEHLERBETRIEB = "Fehlerbetrieb"
ZUSTAND_BEENDET = "beendet"
ZUSTAND_FEHLER_BEENDET = "nach Fehler beendet"

SAUGER_STATUS_MARKER_MS = 500
SOFORTFAHRT_TIMEOUT = 30.0
POSITIONSTOLERANZ_MM = 1.0
ROTATIONSTOLERANZ_GRAD = 2.0


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


def version():
    """Gibt die Versionsinformation des Moduls zurück."""

    return (
        f"befehlskette_v3_2_1.py Version {VERSION} "
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
    """Liest einen Saugerbefehl aus der Befehlsliste."""

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
    """Trägt Bewegungs- und Saugerbefehle in die Queue ein."""

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


def _sauger_eingeschaltet(api):
    """Liest den aktuellen Pumpenschaltzustand."""

    rueckgabe = dType.GetEndEffectorSuctionCup(api)
    return bool(rueckgabe[0])


def sauger_status_sofort_anzeigen(api):
    """Zeigt den Saugerstatus als Sofortabfrage an."""

    eingeschaltet = _sauger_eingeschaltet(api)
    status_text = "EIN" if eingeschaltet else "AUS"

    print(f"Saugerstatus: {status_text}")
    print(
        "Hinweis: Der Status bestätigt den Pumpenbefehl, "
        "nicht das sichere Ansaugen eines Werkstücks."
    )

    return eingeschaltet


def _sauger_status_anzeigen(api, daten, befehlsindex):
    """Liest und zeigt den Pumpenschaltzustand in der Queue."""

    eingeschaltet = _sauger_eingeschaltet(api)
    status_text = "EIN" if eingeschaltet else "AUS"

    print(
        f'Saugerstatus bei Befehl {daten["nummer"]}: '
        f"{status_text} "
        f"(Queue-Index {befehlsindex})"
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


def _tastatur_einlesen(
    eingaben,
    eingabe_beenden,
):
    """Liest sämtliche Texteingaben in einem eigenen Thread."""

    while not eingabe_beenden.is_set():
        try:
            eingabe = input("> ").strip()

        except EOFError:
            return

        if eingabe_beenden.is_set():
            return

        if eingabe:
            eingaben.put(eingabe)


def tastatursteuerung_starten(
    eingaben,
    eingabe_beenden,
):
    """Startet die Tastaturabfrage als Daemon-Thread."""

    print("\nSteuerung während der Ausführung:")
    print("  p + Enter = Pause")
    print("  w + Enter = Weiter")
    print("  h + Enter = Halt / Fehlerbetrieb")
    print("  ? + Enter = Status")

    thread = threading.Thread(
        target=_tastatur_einlesen,
        args=(eingaben, eingabe_beenden),
        daemon=True,
        name="Dobot-Tastatursteuerung",
    )

    thread.start()

    return thread


def _halt_ausfuehren(api):
    """Stoppt auch einen aktuell ausgeführten Queue-Befehl."""

    if hasattr(dType, "SetQueuedCmdForceStopExec"):
        dType.SetQueuedCmdForceStopExec(api)
    else:
        dType.SetQueuedCmdStopExec(api)


def _queue_endgueltig_verwerfen(api):
    """Stoppt und löscht die alte Befehlskette."""

    _halt_ausfuehren(api)
    dType.dSleep(100)
    dType.SetQueuedCmdClear(api)


def _aktive_alarme_lesen(api):
    """Liest die aktiven Alarmnummern."""

    alarmdaten = dType.GetAlarmsState(api)

    if not alarmdaten:
        return []

    alarmbytes = alarmdaten[0]
    laenge = alarmdaten[1] if len(alarmdaten) > 1 else len(alarmbytes)

    aktive_alarme = []

    for byte_index, wert in enumerate(alarmbytes[:laenge]):
        for bit_index in range(8):
            if wert & (1 << bit_index):
                aktive_alarme.append(
                    byte_index * 8 + bit_index
                )

    return aktive_alarme


def _alarme_anzeigen(aktive_alarme):
    """Zeigt Alarmnummern dezimal und hexadezimal."""

    if not aktive_alarme:
        print("Keine Alarme aktiv.")
        return

    print(
        f"{len(aktive_alarme)} Alarm(e) aktiv:",
        file=sys.stderr,
    )

    for alarmnummer in aktive_alarme:
        print(
            f"  Alarm {alarmnummer} "
            f"(0x{alarmnummer:02X})",
            file=sys.stderr,
        )


def _alarme_loeschen(api):
    """Löscht Alarme und prüft den verbleibenden Zustand."""

    dType.ClearAllAlarmsState(api)
    dType.dSleep(300)

    verbleibende_alarme = _aktive_alarme_lesen(api)

    if verbleibende_alarme:
        print(
            "Die Alarmursache besteht weiterhin.",
            file=sys.stderr,
        )
        _alarme_anzeigen(verbleibende_alarme)
        return False

    print("Alarmzustände wurden gelöscht.")
    return True


def _position_anzeigen(api):
    """Zeigt die aktuelle kartesische Position."""

    pose = dType.GetPose(api)
    x, y, z, r = pose[:4]

    print(
        f"Aktuelle Position: "
        f"X={x:.1f}, Y={y:.1f}, "
        f"Z={z:.1f}, R={r:.1f}"
    )

    return x, y, z, r


def _ziel_erreicht(pose, ziel):
    """Prüft, ob die Zielposition innerhalb der Toleranz liegt."""

    x, y, z, r = pose[:4]
    ziel_x, ziel_y, ziel_z, ziel_r = ziel

    return (
        abs(x - ziel_x) <= POSITIONSTOLERANZ_MM
        and abs(y - ziel_y) <= POSITIONSTOLERANZ_MM
        and abs(z - ziel_z) <= POSITIONSTOLERANZ_MM
        and abs(r - ziel_r) <= ROTATIONSTOLERANZ_GRAD
    )


def sofort_fahren(
    api,
    x,
    y,
    z,
    r,
    timeout=SOFORTFAHRT_TIMEOUT,
):
    """Fährt ohne Queue zu einer Zielposition.

    Vor der Fahrt werden bestehende Alarmzustände gelöscht.
    Die Funktion wartet, bis das Ziel erreicht wurde, ein neuer
    Alarm auftritt oder der Timeout abläuft.
    """

    ziel = (
        float(x),
        float(y),
        float(z),
        float(r),
    )

    if not _alarme_loeschen(api):
        print(
            "Sofortfahrt nicht möglich.",
            file=sys.stderr,
        )
        return False

    print(
        f"Sofortfahrt zu "
        f"X={ziel[0]:.1f}, Y={ziel[1]:.1f}, "
        f"Z={ziel[2]:.1f}, R={ziel[3]:.1f}"
    )

    dType.SetPTPCmd(
        api,
        dType.PTPMode.PTPMOVJXYZMode,
        ziel[0],
        ziel[1],
        ziel[2],
        ziel[3],
        isQueued=0,
    )

    startzeit = time.monotonic()

    while True:
        aktive_alarme = _aktive_alarme_lesen(api)

        if aktive_alarme:
            _halt_ausfuehren(api)
            print(
                "Sofortfahrt durch Alarm abgebrochen.",
                file=sys.stderr,
            )
            _alarme_anzeigen(aktive_alarme)
            return False

        pose = dType.GetPose(api)

        if _ziel_erreicht(pose, ziel):
            print("Zielposition erreicht.")
            _position_anzeigen(api)
            return True

        if time.monotonic() - startzeit > timeout:
            _halt_ausfuehren(api)
            print(
                f"Sofortfahrt nach {timeout:.1f} Sekunden "
                "abgebrochen.",
                file=sys.stderr,
            )
            return False

        dType.dSleep(100)


def _koordinaten_lesen(text):
    """Liest X Y Z R aus einer Leerzeichen- oder Semikolonfolge."""

    teile = text.replace(";", " ").split()

    if len(teile) != 4:
        raise ValueError(
            "Es werden genau vier Werte benötigt: X Y Z R"
        )

    return tuple(
        float(teil.replace(",", "."))
        for teil in teile
    )


def _eingabequeue_leeren(eingaben):
    """Verwirft alte Tastaturbefehle vor dem Fehlerbetrieb."""

    while True:
        try:
            eingaben.get_nowait()
        except queue.Empty:
            return


def _fehlerbetriebsmenue_anzeigen(ausgangsposition):
    """Zeigt die verfügbaren Sofortbefehle."""

    x, y, z, r = ausgangsposition

    print()
    print("FEHLERBETRIEB")
    print("-------------")
    print("Die alte Befehlskette wurde endgültig verworfen.")
    print("  1 = Zu frei gewählten Koordinaten fahren")
    print(
        f"  2 = Zur Ausgangsposition fahren "
        f"({x}, {y}, {z}, {r})"
    )
    print("  3 = Saugerstatus anzeigen")
    print("  4 = Sauger sofort ausschalten")
    print("  5 = Programmende, wenn der Sauger AUS ist")
    print("  9 = Programmende trotz aktivem Sauger erzwingen")
    print("  ? = Menü erneut anzeigen")


def fehlerbetrieb_starten(
    api,
    eingaben,
    ausgangsposition,
    grund,
):
    """Startet nach Alarm oder Halt den kontrollierten Fehlerbetrieb."""

    ausgangsposition = tuple(
        float(wert)
        for wert in ausgangsposition
    )

    if len(ausgangsposition) != 4:
        raise ValueError(
            "ausgangsposition muss aus X, Y, Z und R bestehen."
        )

    _queue_endgueltig_verwerfen(api)
    _eingabequeue_leeren(eingaben)

    print()
    print(
        f"PROGRAMMUNTERBRECHUNG: {grund}",
        file=sys.stderr,
    )

    aktive_alarme = _aktive_alarme_lesen(api)
    _alarme_anzeigen(aktive_alarme)
    _position_anzeigen(api)
    sauger_status_sofort_anzeigen(api)
    _fehlerbetriebsmenue_anzeigen(ausgangsposition)

    wartet_auf_koordinaten = False

    while True:
        try:
            eingabe = eingaben.get(timeout=0.1).strip()

        except queue.Empty:
            continue

        if wartet_auf_koordinaten:
            if eingabe.lower() == "a":
                wartet_auf_koordinaten = False
                _fehlerbetriebsmenue_anzeigen(
                    ausgangsposition
                )
                continue

            try:
                ziel = _koordinaten_lesen(eingabe)

            except ValueError as fehler:
                print(
                    f"Ungültige Koordinaten: {fehler}",
                    file=sys.stderr,
                )
                print(
                    "Bitte erneut X Y Z R eingeben "
                    "oder 'a' zum Abbrechen."
                )
                continue

            sofort_fahren(api, *ziel)
            wartet_auf_koordinaten = False
            _fehlerbetriebsmenue_anzeigen(
                ausgangsposition
            )
            continue

        befehl = eingabe.lower()

        if befehl == "1":
            print(
                "Koordinaten als X Y Z R eingeben, "
                "zum Beispiel: 200 0 50 0"
            )
            print(
                "Dezimalzahlen dürfen ein Komma enthalten. "
                "'a' bricht die Eingabe ab."
            )
            wartet_auf_koordinaten = True

        elif befehl == "2":
            sofort_fahren(
                api,
                *ausgangsposition,
            )
            _fehlerbetriebsmenue_anzeigen(
                ausgangsposition
            )

        elif befehl == "3":
            sauger_status_sofort_anzeigen(api)

        elif befehl == "4":
            dType.SetEndEffectorSuctionCup(
                api,
                True,
                False,
                isQueued=0,
            )
            dType.dSleep(300)
            sauger_status_sofort_anzeigen(api)

        elif befehl == "5":
            if _sauger_eingeschaltet(api):
                print(
                    "Programmende abgelehnt: "
                    "Der Sauger ist noch EIN.",
                    file=sys.stderr,
                )
                print(
                    "Zuerst 4 zum Ausschalten oder "
                    "9 zum erzwungenen Programmende wählen."
                )
            else:
                print("Fehlerbetrieb wird beendet.")
                return ZUSTAND_FEHLER_BEENDET

        elif befehl == "9":
            print(
                "WARNUNG: Programmende wurde trotz "
                "möglicherweise aktivem Sauger erzwungen.",
                file=sys.stderr,
            )
            return ZUSTAND_FEHLER_BEENDET

        elif befehl == "?":
            _fehlerbetriebsmenue_anzeigen(
                ausgangsposition
            )

        else:
            print(
                "Unbekannte Eingabe. "
                "Erlaubt sind 1, 2, 3, 4, 5, 9 und ?."
            )


def befehlskette_ausfuehren_steuerbar(
    api,
    queue_befehle,
    timeout=30.0,
    eingaben=None,
    tastatur=True,
    ausgangsposition=(200, 0, 50, 0),
):
    """Führt die Befehlskette mit Tastatur- und Fehlersteuerung aus."""

    if not queue_befehle:
        print("Die Befehlskette ist leer.")
        return "leer"

    if timeout <= 0:
        raise ValueError("timeout muss größer als 0 sein.")

    if eingaben is None:
        eingaben = queue.Queue()

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
            eingaben,
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
                    steuerbefehl = (
                        eingaben.get_nowait()
                    ).strip().lower()

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
                            "Mit 'w' + Enter wird die "
                            "Befehlskette fortgesetzt."
                        )

                elif steuerbefehl == "w":
                    if zustand == ZUSTAND_PAUSIERT:
                        if pausenbeginn is not None:
                            gesamte_pausendauer += (
                                time.monotonic()
                                - pausenbeginn
                            )
                            pausenbeginn = None

                        dType.SetQueuedCmdStartExec(api)
                        zustand = ZUSTAND_LAEUFT
                        print("WEITER: Befehlskette läuft.")

                elif steuerbefehl == "h":
                    return fehlerbetrieb_starten(
                        api,
                        eingaben,
                        ausgangsposition,
                        grund="HALT durch den Nutzer",
                    )

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

                else:
                    print(
                        "Unbekannter Steuerbefehl. "
                        "Erlaubt sind p, w, h und ?."
                    )

            aktive_alarme = _aktive_alarme_lesen(api)

            if aktive_alarme:
                return fehlerbetrieb_starten(
                    api,
                    eingaben,
                    ausgangsposition,
                    grund=(
                        f"Dobot-Alarm bei Queue-Index "
                        f"{aktueller_index}"
                    ),
                )

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
                    return fehlerbetrieb_starten(
                        api,
                        eingaben,
                        ausgangsposition,
                        grund=(
                            f"Timeout nach {timeout:.1f} Sekunden"
                        ),
                    )

            dType.dSleep(100)

    finally:
        eingabe_beenden.set()
