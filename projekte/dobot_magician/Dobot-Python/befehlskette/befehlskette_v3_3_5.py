from pathlib import Path
import queue
import sys
import threading
import time


VERSION = "3.3.5.3"
VERSIONSDATUM = "26.07.2026, 21:30 Uhr"

ZUSTAND_LAEUFT = "läuft"
ZUSTAND_PAUSIERT = "pausiert"
ZUSTAND_HALT = "Halt"
ZUSTAND_BEENDET = "beendet"


# Erwartete Struktur:
# Dobot-Python/
# ├── sdk64/
# └── befehlskette-v3_3_5/
#     ├── befehlskette_v3_3_5.py
#     └── befehlskette_beispiel_v3_3_5.py
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


VERGLEICHSOPERATOREN = {"==", "!=", "<", "<=", ">", ">="}


def _vergleichsoperator_normalisieren(operator, befehlsnummer):
    """Prüft und normalisiert einen Vergleichsoperator."""

    operator = str(operator).strip()
    alias = {"=": "==", "<>": "!="}
    operator = alias.get(operator, operator)

    if operator not in VERGLEICHSOPERATOREN:
        erlaubt = ", ".join(sorted(VERGLEICHSOPERATOREN))
        raise ValueError(
            f"Ungültiger Vergleichsoperator {operator!r} in "
            f"Befehl {befehlsnummer}. Erlaubt: {erlaubt}."
        )

    return operator


def _statusfeld(text):
    """Bereitet ein Feld für eine semikolongetrennte Statusmeldung vor."""

    return str(text).replace(";", ",").replace("\r", " ").replace("\n", " ")


def _status_senden(senden, *felder):
    """Sendet eine Statusmeldung, sofern eine Sendefunktion vorhanden ist."""

    if senden is None:
        return False

    nachricht = ";".join(_statusfeld(feld) for feld in felder)

    try:
        return bool(senden(nachricht))
    except Exception as fehler:
        print(f"Statusmeldung konnte nicht gesendet werden: {fehler}")
        return False


def version():
    """Gibt die Versionsinformation des Moduls zurück."""

    return (
        f"befehlskette_v3_3_5.py Version {VERSION} "
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


def _prozent_pruefen(wert, bezeichnung, befehlsnummer):
    """Prüft eine Prozentangabe für PTP-Parameter."""

    if not isinstance(wert, (int, float)):
        raise ValueError(
            f"{bezeichnung} in Befehl {befehlsnummer} "
            "muss eine Zahl sein."
        )

    wert = float(wert)

    if not 1 <= wert <= 100:
        raise ValueError(
            f"{bezeichnung} in Befehl {befehlsnummer} "
            "muss zwischen 1 und 100 Prozent liegen."
        )

    return wert


def _name_normalisieren(name, bezeichnung, befehlsnummer):
    """Prüft und normalisiert Marken- und Meldungsnamen."""

    name = str(name).strip()

    if not name:
        raise ValueError(
            f"{bezeichnung} in Befehl {befehlsnummer} "
            "darf nicht leer sein."
        )

    return name.casefold()


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

    koordinaten = (x, y, z, r)

    if not all(isinstance(wert, (int, float)) for wert in koordinaten):
        raise ValueError(
            f"Die Koordinaten in Befehl {befehlsnummer} "
            "müssen Zahlen sein."
        )

    return {
        "befehl": str(befehlsname).strip().lower(),
        "art": "roboter",
        "position": koordinaten,
        "text": str(text),
        "pause_ms": _pause_pruefen(pause_ms, befehlsnummer),
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

    art = "status" if befehlsname == "sauger_status" else "roboter"

    return {
        "befehl": befehlsname,
        "art": art,
        "position": None,
        "text": str(text),
        "pause_ms": _pause_pruefen(pause_ms, befehlsnummer),
    }


def _homebefehl_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Liest einen HOME-Befehl."""

    if len(befehl) == 1:
        text = "HOME-Fahrt ausführen"
        pause_ms = standard_pause_ms

    elif len(befehl) == 2:
        _, text = befehl
        pause_ms = standard_pause_ms

    elif len(befehl) == 3:
        _, text, pause_ms = befehl

    else:
        raise ValueError(
            f"HOME-Befehl {befehlsnummer} benötigt "
            "1, 2 oder 3 Einträge:\n"
            "('home'[, Text[, Pause_ms]])."
        )

    return {
        "befehl": "home",
        "art": "roboter",
        "position": None,
        "text": str(text),
        "pause_ms": _pause_pruefen(pause_ms, befehlsnummer),
    }


def _geschwindigkeitsbefehl_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Liest Geschwindigkeit und Beschleunigung.

    Unterstützte Formen:

        ("geschwindigkeit", 50)
        ("geschwindigkeit", 50, "Text")
        ("geschwindigkeit", 50, "Text", Pause_ms)
        ("geschwindigkeit", 50, 40, "Text")
        ("geschwindigkeit", 50, 40, "Text", Pause_ms)

    Bei nur einem Prozentwert wird dieser für Geschwindigkeit und
    Beschleunigung verwendet.
    """

    if len(befehl) == 2:
        _, geschwindigkeit = befehl
        beschleunigung = geschwindigkeit
        text = (
            f"Geschwindigkeit und Beschleunigung "
            f"auf {geschwindigkeit} % setzen"
        )
        pause_ms = standard_pause_ms

    elif len(befehl) == 3:
        _, geschwindigkeit, text = befehl
        beschleunigung = geschwindigkeit
        pause_ms = standard_pause_ms

    elif len(befehl) == 4:
        if isinstance(befehl[2], str):
            _, geschwindigkeit, text, pause_ms = befehl
            beschleunigung = geschwindigkeit
        else:
            _, geschwindigkeit, beschleunigung, text = befehl
            pause_ms = standard_pause_ms

    elif len(befehl) == 5:
        (
            _,
            geschwindigkeit,
            beschleunigung,
            text,
            pause_ms,
        ) = befehl

    else:
        raise ValueError(
            f"Geschwindigkeitsbefehl {befehlsnummer} hat "
            "eine ungültige Anzahl von Einträgen."
        )

    geschwindigkeit = _prozent_pruefen(
        geschwindigkeit,
        "Geschwindigkeit",
        befehlsnummer,
    )
    beschleunigung = _prozent_pruefen(
        beschleunigung,
        "Beschleunigung",
        befehlsnummer,
    )

    return {
        "befehl": "geschwindigkeit",
        "art": "roboter",
        "geschwindigkeit": geschwindigkeit,
        "beschleunigung": beschleunigung,
        "position": None,
        "text": str(text),
        "pause_ms": _pause_pruefen(pause_ms, befehlsnummer),
    }


def _wartebefehl_lesen(befehl, befehlsnummer):
    """Liest einen ``warte_bis``-Befehl.

    Formen:

        ("warte_bis", "FREIGABE")
        ("warte_bis", "FREIGABE", "Text")
        ("warte_bis", "FREIGABE", "Text", Timeout_s)

    ``None`` als Timeout bedeutet unbegrenztes Warten.
    """

    if len(befehl) == 2:
        _, meldung = befehl
        text = f"Warte auf Meldung {meldung!r}"
        timeout_s = None

    elif len(befehl) == 3:
        _, meldung, text = befehl
        timeout_s = None

    elif len(befehl) == 4:
        _, meldung, text, timeout_s = befehl

    else:
        raise ValueError(
            f"warte_bis in Befehl {befehlsnummer} benötigt "
            "2, 3 oder 4 Einträge:\n"
            "('warte_bis', Meldung[, Text[, Timeout_s]])."
        )

    meldung_original = str(meldung).strip()
    meldung_norm = _name_normalisieren(
        meldung_original,
        "Meldung",
        befehlsnummer,
    )

    if timeout_s is not None:
        if not isinstance(timeout_s, (int, float)) or timeout_s <= 0:
            raise ValueError(
                f"Timeout in Befehl {befehlsnummer} muss "
                "größer als 0 oder None sein."
            )
        timeout_s = float(timeout_s)

    return {
        "befehl": "warte_bis",
        "art": "warten",
        "meldung": meldung_original,
        "meldung_norm": meldung_norm,
        "timeout_s": timeout_s,
        "position": None,
        "text": str(text),
        "pause_ms": 0,
    }



def _timeout_pruefen(timeout_s, befehlsnummer):
    """Prüft einen optionalen Timeout in Sekunden."""

    if timeout_s is None:
        return None

    if not isinstance(timeout_s, (int, float)) or timeout_s <= 0:
        raise ValueError(
            f"Timeout in Befehl {befehlsnummer} muss "
            "größer als 0 oder None sein."
        )

    return float(timeout_s)


def _warte_bis_wert_lesen(befehl, befehlsnummer):
    """Liest einen Befehl zum Warten auf einen ESP-Wert.

    Alte Form mit Gleichheitsvergleich:
        ("warte_bis_wert", Name, Sollwert[, Text[, Timeout_s]])

    Neue Form mit Vergleichsoperator:
        ("warte_bis_wert", Name, Operator, Sollwert[, Text[, Timeout_s]])
    """

    if len(befehl) < 3 or len(befehl) > 6:
        raise ValueError(
            f"warte_bis_wert in Befehl {befehlsnummer} hat "
            "eine ungültige Anzahl von Einträgen."
        )

    _, name, *rest = befehl

    if rest and str(rest[0]).strip() in (VERGLEICHSOPERATOREN | {"=", "<>"}):
        operator = _vergleichsoperator_normalisieren(rest.pop(0), befehlsnummer)
    else:
        operator = "=="

    if not rest:
        raise ValueError(
            f"warte_bis_wert in Befehl {befehlsnummer} benötigt einen Sollwert."
        )

    sollwert = rest.pop(0)
    text = f"Warte auf {name} {operator} {sollwert!r}"
    timeout_s = None

    if rest:
        text = rest.pop(0)
    if rest:
        timeout_s = rest.pop(0)
    if rest:
        raise ValueError(
            f"warte_bis_wert in Befehl {befehlsnummer} enthält zu viele Einträge."
        )

    name_original = str(name).strip()

    return {
        "befehl": "warte_bis_wert",
        "art": "wert_warten",
        "wertname": name_original,
        "wertname_norm": _name_normalisieren(name_original, "Wertname", befehlsnummer),
        "operator": operator,
        "sollwert": sollwert,
        "timeout_s": _timeout_pruefen(timeout_s, befehlsnummer),
        "position": None,
        "text": str(text),
        "pause_ms": 0,
    }

def _wert_anzeigen_lesen(befehl, befehlsnummer):
    """Liest einen Befehl zum Anzeigen eines ESP-Wertes."""

    if len(befehl) == 2:
        _, name = befehl
        text = f"ESP-Wert {name} anzeigen"

    elif len(befehl) == 3:
        _, name, text = befehl

    else:
        raise ValueError(
            f"wert_anzeigen in Befehl {befehlsnummer} benötigt "
            "2 oder 3 Einträge:\n"
            "('wert_anzeigen', Name[, Text])."
        )

    name_original = str(name).strip()

    return {
        "befehl": "wert_anzeigen",
        "art": "wert_status",
        "wertname": name_original,
        "wertname_norm": _name_normalisieren(
            name_original,
            "Wertname",
            befehlsnummer,
        ),
        "position": None,
        "text": str(text),
        "pause_ms": 0,
    }


def _esp_senden_lesen(befehl, befehlsnummer):
    """Liest einen Befehl zum Senden eines Textes an den ESP32.

    Formen:

        ("esp_senden", "LED_GELB_EIN")
        ("esp_senden", "LED_GELB_EIN", "Gelbe LED einschalten")
    """

    if len(befehl) == 2:
        _, nachricht = befehl
        text = f"An ESP32 senden: {nachricht}"

    elif len(befehl) == 3:
        _, nachricht, text = befehl

    else:
        raise ValueError(
            f"esp_senden in Befehl {befehlsnummer} benötigt "
            "2 oder 3 Einträge:\n"
            "('esp_senden', Nachricht[, Text])."
        )

    nachricht = str(nachricht).strip()

    if not nachricht:
        raise ValueError(
            f"Die Nachricht in Befehl {befehlsnummer} "
            "darf nicht leer sein."
        )

    if "\n" in nachricht or "\r" in nachricht:
        raise ValueError(
            f"Die Nachricht in Befehl {befehlsnummer} "
            "darf keinen Zeilenumbruch enthalten."
        )

    return {
        "befehl": "esp_senden",
        "art": "esp_senden",
        "nachricht": nachricht,
        "position": None,
        "text": str(text),
        "pause_ms": 0,
    }


def _wenn_wert_lesen(
    befehl,
    befehlsnummer,
    standard_pause_ms,
):
    """Liest eine Verzweigung anhand eines gespeicherten ESP-Wertes.

    Alte Form:
        ("wenn_wert", Name, Sollwert, Wahr-Befehl, Falsch-Befehl)

    Neue Form:
        ("wenn_wert", Name, Operator, Sollwert, Wahr-Befehl, Falsch-Befehl)
    """

    if len(befehl) == 5:
        _, name, sollwert, wahr_befehl, falsch_befehl = befehl
        operator = "=="
    elif len(befehl) == 6:
        _, name, operator, sollwert, wahr_befehl, falsch_befehl = befehl
        operator = _vergleichsoperator_normalisieren(operator, befehlsnummer)
    else:
        raise ValueError(
            f"wenn_wert in Befehl {befehlsnummer} benötigt 5 oder 6 Einträge:\n"
            "('wenn_wert', Name[, Operator], Sollwert, Wahr-Befehl, Falsch-Befehl)."
        )

    name_original = str(name).strip()

    wahr_daten = _befehl_lesen(wahr_befehl, befehlsnummer, standard_pause_ms)
    falsch_daten = _befehl_lesen(falsch_befehl, befehlsnummer, standard_pause_ms)

    verbotene_arten = {"marke", "wert_bedingung"}

    for zweig_name, zweig in (("Wahr-Befehl", wahr_daten), ("Falsch-Befehl", falsch_daten)):
        if zweig["art"] in verbotene_arten:
            raise ValueError(
                f"{zweig_name} in Befehl {befehlsnummer} darf "
                "keine Marke und keine weitere wenn_wert-Bedingung sein."
            )

    return {
        "befehl": "wenn_wert",
        "art": "wert_bedingung",
        "wertname": name_original,
        "wertname_norm": _name_normalisieren(name_original, "Wertname", befehlsnummer),
        "operator": operator,
        "sollwert": sollwert,
        "wahr_befehl": wahr_daten,
        "falsch_befehl": falsch_daten,
        "position": None,
        "text": f"Wenn {name_original} {operator} {sollwert!r}",
        "pause_ms": 0,
    }

def _markenbefehl_lesen(befehl, befehlsnummer):
    """Liest eine Befehlsmarke."""

    if len(befehl) != 2:
        raise ValueError(
            f"Marke {befehlsnummer} benötigt genau zwei "
            "Einträge: ('marke', Name)."
        )

    _, name = befehl
    name_original = str(name).strip()

    return {
        "befehl": "marke",
        "art": "marke",
        "marke": name_original,
        "marke_norm": _name_normalisieren(
            name_original,
            "Markenname",
            befehlsnummer,
        ),
        "position": None,
        "text": f"Marke {name_original!r}",
        "pause_ms": 0,
    }


def _sprungbefehl_lesen(befehl, befehlsnummer):
    """Liest einen Sprung zu einer Befehlsmarke."""

    if len(befehl) != 2:
        raise ValueError(
            f"Sprungbefehl {befehlsnummer} benötigt genau "
            "zwei Einträge: ('gehe_zu_befehl', Markenname)."
        )

    _, ziel = befehl
    ziel_original = str(ziel).strip()

    return {
        "befehl": "gehe_zu_befehl",
        "art": "sprung",
        "ziel": ziel_original,
        "ziel_norm": _name_normalisieren(
            ziel_original,
            "Sprungziel",
            befehlsnummer,
        ),
        "position": None,
        "text": f"Springe zu Marke {ziel_original!r}",
        "pause_ms": 0,
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

    elif befehlsname == "home":
        daten = _homebefehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

    elif befehlsname == "geschwindigkeit":
        daten = _geschwindigkeitsbefehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

    elif befehlsname == "warte_bis":
        daten = _wartebefehl_lesen(
            befehl,
            befehlsnummer,
        )

    elif befehlsname == "warte_bis_wert":
        daten = _warte_bis_wert_lesen(
            befehl,
            befehlsnummer,
        )

    elif befehlsname == "wert_anzeigen":
        daten = _wert_anzeigen_lesen(
            befehl,
            befehlsnummer,
        )

    elif befehlsname == "wenn_wert":
        daten = _wenn_wert_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

    elif befehlsname == "esp_senden":
        daten = _esp_senden_lesen(
            befehl,
            befehlsnummer,
        )

    elif befehlsname == "marke":
        daten = _markenbefehl_lesen(
            befehl,
            befehlsnummer,
        )

    elif befehlsname == "gehe_zu_befehl":
        daten = _sprungbefehl_lesen(
            befehl,
            befehlsnummer,
        )

    else:
        erlaubte_befehle = (
            list(PTP_BEFEHLE)
            + sorted(SAUGER_BEFEHLE)
            + [
                "home",
                "geschwindigkeit",
                "warte_bis",
                "warte_bis_wert",
                "wert_anzeigen",
                "wenn_wert",
                "esp_senden",
                "marke",
                "gehe_zu_befehl",
            ]
        )

        raise ValueError(
            f"Unbekannter Befehl '{befehlsname}' in "
            f"Befehl {befehlsnummer}. Erlaubt: "
            f"{', '.join(erlaubte_befehle)}."
        )

    daten["nummer"] = befehlsnummer
    return daten


def befehlskette_pruefen(befehle, standard_pause_ms=0):
    """Prüft die Befehlsliste und erstellt ein Ablaufprogramm.

    Die Prüfung erfolgt vollständig ohne Verbindung zum Dobot.
    Fehlerhafte Befehle, Parameter, Marken und Sprünge werden dadurch
    erkannt, bevor sich der Roboter bewegen kann.
    """

    if (
        not isinstance(standard_pause_ms, (int, float))
        or standard_pause_ms < 0
    ):
        raise ValueError(
            "standard_pause_ms muss eine nicht negative Zahl sein."
        )

    if not isinstance(befehle, (list, tuple)):
        raise ValueError("befehle muss eine Liste oder ein Tupel sein.")

    programm_befehle = []
    marken = {}

    for befehlsnummer, befehl in enumerate(befehle, start=1):
        daten = _befehl_lesen(
            befehl,
            befehlsnummer,
            standard_pause_ms,
        )

        position = len(programm_befehle)
        programm_befehle.append(daten)

        if daten["art"] == "marke":
            marke = daten["marke_norm"]

            if marke in marken:
                alte_nummer = programm_befehle[
                    marken[marke]
                ]["nummer"]
                raise ValueError(
                    f"Die Marke {daten['marke']!r} ist doppelt "
                    f"vorhanden: Befehl {alte_nummer} und "
                    f"Befehl {befehlsnummer}."
                )

            marken[marke] = position

    def sprungbefehle(daten):
        if daten["art"] == "sprung":
            yield daten

        elif daten["art"] == "wert_bedingung":
            yield from sprungbefehle(daten["wahr_befehl"])
            yield from sprungbefehle(daten["falsch_befehl"])

    for daten in programm_befehle:
        for sprung in sprungbefehle(daten):
            if sprung["ziel_norm"] not in marken:
                raise ValueError(
                    f"Befehl {daten['nummer']} springt zur nicht "
                    f"vorhandenen Marke {sprung['ziel']!r}."
                )

    return {
        "befehle": programm_befehle,
        "marken": marken,
    }



def befehlskette_erstellen(api, befehle, standard_pause_ms=0):
    """Kompatibler Aufruf zum Prüfen und Erstellen der Befehlskette."""

    del api
    return befehlskette_pruefen(befehle, standard_pause_ms)

def _befehl_darstellen(daten):
    """Erzeugt die kurze Darstellung eines Befehls."""

    befehlsname = daten["befehl"]

    if befehlsname in PTP_BEFEHLE:
        x, y, z, r = daten["position"]
        return f"{befehlsname}({x}, {y}, {z}, {r})"

    if befehlsname == "geschwindigkeit":
        return (
            "geschwindigkeit("
            f"{daten['geschwindigkeit']:g}, "
            f"{daten['beschleunigung']:g})"
        )

    if befehlsname == "warte_bis":
        return f"warte_bis({daten['meldung']!r})"

    if befehlsname == "warte_bis_wert":
        return (
            f"warte_bis_wert({daten['wertname']!r}, "
            f"{daten['operator']!r}, {daten['sollwert']!r})"
        )

    if befehlsname == "wert_anzeigen":
        return f"wert_anzeigen({daten['wertname']!r})"

    if befehlsname == "wenn_wert":
        return (
            f"wenn_wert({daten['wertname']!r}, "
            f"{daten['operator']!r}, {daten['sollwert']!r}, "
            f"{_befehl_darstellen(daten['wahr_befehl'])}, "
            f"{_befehl_darstellen(daten['falsch_befehl'])})"
        )

    if befehlsname == "esp_senden":
        return f"esp_senden({daten['nachricht']!r})"

    if befehlsname == "marke":
        return f"marke({daten['marke']!r})"

    if befehlsname == "gehe_zu_befehl":
        return f"gehe_zu_befehl({daten['ziel']!r})"

    return f"{befehlsname}()"


def befehlskette_anzeigen(programm):
    """Zeigt das geprüfte Ablaufprogramm vor dem Start an."""

    print("\nErstellte Befehlskette:")

    for daten in programm["befehle"]:
        zusatz = ""

        if daten["pause_ms"]:
            zusatz += f" | Pause: {daten['pause_ms']} ms"

        if daten["art"] in {"warten", "wert_warten"}:
            if daten["timeout_s"] is None:
                zusatz += " | ohne Timeout"
            else:
                zusatz += f" | Timeout: {daten['timeout_s']:g} s"

        print(
            f"{daten['nummer']:2d}. "
            f"{_befehl_darstellen(daten)} – "
            f"{daten['text']}{zusatz}"
        )


def steuerbefehl_normalisieren(eingabe):
    """Übersetzt kurze und lange Steuerbefehle."""

    text = str(eingabe).strip().lower()
    return STEUERBEFEHLE.get(text)


def steuerbefehl_einreihen(
    steuerbefehle,
    eingabe,
    quelle="extern",
):
    """Legt einen gültigen Steuerbefehl in der Queue ab."""

    steuerbefehl = steuerbefehl_normalisieren(eingabe)

    if steuerbefehl is None:
        return False

    steuerbefehle.put((steuerbefehl, str(quelle)))
    return True


def _steuerbefehl_entpacken(eintrag):
    """Liest Queue-Einträge mit oder ohne Quellenangabe."""

    if isinstance(eintrag, (tuple, list)) and len(eintrag) == 2:
        eingabe, quelle = eintrag
    else:
        eingabe = eintrag
        quelle = "extern"

    steuerbefehl = steuerbefehl_normalisieren(eingabe)

    if steuerbefehl is None:
        return None, str(quelle)

    return steuerbefehl, str(quelle)


def _meldung_entpacken(eintrag):
    """Liest eine Kommunikationsmeldung samt Quelle."""

    if isinstance(eintrag, (tuple, list)) and len(eintrag) == 2:
        meldung, quelle = eintrag
    else:
        meldung = eintrag
        quelle = "extern"

    meldung = str(meldung).strip()
    return meldung, str(quelle)


def _tastatur_einlesen(steuerbefehle, eingabe_beenden):
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


def tastatursteuerung_starten(steuerbefehle, eingabe_beenden):
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

    if hasattr(dType, "SetQueuedCmdForceStopExec"):
        dType.SetQueuedCmdForceStopExec(api)
    else:
        dType.SetQueuedCmdStopExec(api)


def _alarm_pruefen(api, befehlsnummer):
    """Prüft den Dobot auf aktive Alarme."""

    alarmdaten = dType.GetAlarmsState(api)
    alarmbytes = alarmdaten[0] if alarmdaten else []

    if any(alarmbytes):
        dType.SetQueuedCmdStopExec(api)

        print()
        print("Alarmdaten:", list(alarmbytes))

        raise RuntimeError(
            f"Die Ausführung wurde bei Befehl {befehlsnummer} "
            "durch einen Alarm gestoppt."
        )


def _steuerbefehle_verarbeiten(
    api,
    steuerbefehle,
    zustand,
    roboter_aktiv,
    status_text,
):
    """Verarbeitet alle aktuell vorliegenden Steuerbefehle."""

    while True:
        try:
            eintrag = steuerbefehle.get_nowait()
        except queue.Empty:
            break

        steuerbefehl, steuerquelle = _steuerbefehl_entpacken(eintrag)

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
                if roboter_aktiv:
                    dType.SetQueuedCmdStopExec(api)
                zustand = ZUSTAND_PAUSIERT
                if roboter_aktiv:
                    print(
                        "PAUSE angefordert: Der aktuelle Roboterbefehl "
                        "wird kontrolliert beendet. Vor dem nächsten "
                        "Befehl wartet die Befehlskette."
                    )
                else:
                    print("PAUSE angefordert.")
            else:
                print(
                    "Pause nicht ausgeführt: "
                    f"Zustand ist '{zustand}'."
                )

        elif steuerbefehl == "w":
            if zustand == ZUSTAND_PAUSIERT:
                if roboter_aktiv:
                    dType.SetQueuedCmdStartExec(api)
                zustand = ZUSTAND_LAEUFT
                print("WEITER: Die Befehlskette läuft weiter.")
            else:
                print(
                    "Weiter nicht ausgeführt: "
                    f"Zustand ist '{zustand}'."
                )

        elif steuerbefehl == "h":
            _halt_ausfuehren(api)
            print("HALT! Die Befehlskette wurde abgebrochen.")
            return ZUSTAND_HALT, True

        elif steuerbefehl == "?":
            print(f"Zustand: {zustand}")
            print(status_text())

    return zustand, False


def _auf_weiter_warten(
    api,
    steuerbefehle,
    zustand,
    status_text,
):
    """Verhindert den Start eines neuen Befehls während einer Pause."""

    while zustand == ZUSTAND_PAUSIERT:
        zustand, halt = _steuerbefehle_verarbeiten(
            api,
            steuerbefehle,
            zustand,
            roboter_aktiv=False,
            status_text=status_text,
        )

        if halt:
            return zustand, True

        dType.dSleep(100)

    return zustand, False


def _roboterbefehl_einreihen(api, daten):
    """Leert die Hardware-Queue und reiht genau einen Befehl ein."""

    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    befehlsname = daten["befehl"]

    if befehlsname in PTP_BEFEHLE:
        x, y, z, r = daten["position"]
        zielindex = dType.SetPTPCmd(
            api,
            PTP_BEFEHLE[befehlsname],
            x,
            y,
            z,
            r,
            isQueued=1,
        )[0]

    elif befehlsname == "sauger_ein":
        zielindex = dType.SetEndEffectorSuctionCup(
            api,
            True,
            True,
            isQueued=1,
        )[0]

    elif befehlsname == "sauger_aus":
        zielindex = dType.SetEndEffectorSuctionCup(
            api,
            True,
            False,
            isQueued=1,
        )[0]

    elif befehlsname == "home":
        zielindex = dType.SetHOMECmd(
            api,
            temp=0,
            isQueued=1,
        )[0]

    elif befehlsname == "geschwindigkeit":
        zielindex = dType.SetPTPCommonParams(
            api,
            daten["geschwindigkeit"],
            daten["beschleunigung"],
            isQueued=1,
        )[0]

    else:
        raise RuntimeError(
            f"Interner Fehler: Roboterbefehl {befehlsname!r} "
            "ist nicht implementiert."
        )

    if daten["pause_ms"] > 0:
        zielindex = dType.SetWAITCmd(
            api,
            daten["pause_ms"] / 1000.0,
            isQueued=1,
        )[0]

    return zielindex


def _roboterbefehl_ausfuehren(
    api,
    daten,
    timeout,
    steuerbefehle,
    zustand,
):
    """Führt genau einen Queue-Befehl aus und wartet auf sein Ende."""

    zielindex = _roboterbefehl_einreihen(api, daten)
    dType.SetQueuedCmdStartExec(api)

    aktive_laufzeit = 0.0
    letzter_zeitpunkt = time.monotonic()

    def status_text():
        aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]
        return (
            f"Befehl {daten['nummer']}: {daten['text']}\n"
            f"Queue-Index: {aktueller_index} von {zielindex}"
        )

    try:
        while True:
            jetzt = time.monotonic()

            if zustand == ZUSTAND_LAEUFT:
                aktive_laufzeit += jetzt - letzter_zeitpunkt

            letzter_zeitpunkt = jetzt

            zustand, halt = _steuerbefehle_verarbeiten(
                api,
                steuerbefehle,
                zustand,
                roboter_aktiv=True,
                status_text=status_text,
            )

            if halt:
                return zustand, True

            aktueller_index = dType.GetQueuedCmdCurrentIndex(api)[0]
            _alarm_pruefen(api, daten["nummer"])

            if aktueller_index >= zielindex:
                return zustand, False

            if aktive_laufzeit > timeout:
                dType.SetQueuedCmdStopExec(api)
                raise TimeoutError(
                    f"Befehl {daten['nummer']} wurde nicht "
                    f"innerhalb von {timeout:.1f} Sekunden beendet. "
                    f"Queue-Index: {aktueller_index} von {zielindex}."
                )

            dType.dSleep(50)

    finally:
        dType.SetQueuedCmdStopExec(api)


def _zeitpause_ausfuehren(
    api,
    pause_ms,
    steuerbefehle,
    zustand,
    daten,
):
    """Wartet außerhalb der Dobot-Queue und bleibt steuerbar."""

    zielzeit = pause_ms / 1000.0
    aktive_laufzeit = 0.0
    letzter_zeitpunkt = time.monotonic()

    def status_text():
        return (
            f"Befehl {daten['nummer']}: {daten['text']}\n"
            f"Zeitpause: {aktive_laufzeit:.1f} von {zielzeit:.1f} s"
        )

    while aktive_laufzeit < zielzeit:
        jetzt = time.monotonic()

        if zustand == ZUSTAND_LAEUFT:
            aktive_laufzeit += jetzt - letzter_zeitpunkt

        letzter_zeitpunkt = jetzt

        zustand, halt = _steuerbefehle_verarbeiten(
            api,
            steuerbefehle,
            zustand,
            roboter_aktiv=False,
            status_text=status_text,
        )

        if halt:
            return zustand, True

        dType.dSleep(50)

    return zustand, False


def _sauger_status_anzeigen(api, daten):
    """Liest und zeigt den aktuellen Pumpenschaltzustand."""

    rueckgabe = dType.GetEndEffectorSuctionCup(api)
    sauger_ein = bool(rueckgabe[0])
    status_text = "EIN" if sauger_ein else "AUS"

    print(
        f"Saugerstatus bei Befehl {daten['nummer']}: "
        f"{status_text}"
    )
    print(
        "Hinweis: Der Status bestätigt den Pumpenbefehl, "
        "nicht das sichere Ansaugen eines Werkstücks."
    )


def _passende_gepufferte_meldung(
    meldungspuffer,
    erwartete_meldung_norm,
):
    """Entnimmt eine passende, früher empfangene Meldung."""

    for position, eintrag in enumerate(meldungspuffer):
        meldung, quelle = _meldung_entpacken(eintrag)

        if meldung.casefold() == erwartete_meldung_norm:
            del meldungspuffer[position]
            return meldung, quelle

    return None


def _auf_meldung_warten(
    api,
    daten,
    meldungen,
    meldungspuffer,
    steuerbefehle,
    zustand,
):
    """Wartet steuerbar auf eine bestimmte COM-/TCP-Meldung."""

    erwartete_meldung_norm = daten["meldung_norm"]
    timeout_s = daten["timeout_s"]

    gepuffert = _passende_gepufferte_meldung(
        meldungspuffer,
        erwartete_meldung_norm,
    )

    if gepuffert is not None:
        meldung, quelle = gepuffert
        print(
            f"Bereits gepufferte Meldung empfangen: "
            f"{meldung!r} von {quelle}."
        )
        return zustand, False

    aktive_wartezeit = 0.0
    letzter_zeitpunkt = time.monotonic()

    print(
        f"Warte auf Meldung {daten['meldung']!r} "
        "vom COM-/TCP-Client ..."
    )

    def status_text():
        timeout_text = (
            "ohne Timeout"
            if timeout_s is None
            else f"Timeout {timeout_s:g} s"
        )
        return (
            f"Befehl {daten['nummer']}: Warte auf "
            f"{daten['meldung']!r}\n"
            f"Aktive Wartezeit: {aktive_wartezeit:.1f} s, "
            f"{timeout_text}, gepuffert: {len(meldungspuffer)}"
        )

    while True:
        jetzt = time.monotonic()

        if zustand == ZUSTAND_LAEUFT:
            aktive_wartezeit += jetzt - letzter_zeitpunkt

        letzter_zeitpunkt = jetzt

        zustand, halt = _steuerbefehle_verarbeiten(
            api,
            steuerbefehle,
            zustand,
            roboter_aktiv=False,
            status_text=status_text,
        )

        if halt:
            return zustand, True

        if zustand == ZUSTAND_PAUSIERT:
            dType.dSleep(100)
            continue

        try:
            eintrag = meldungen.get(timeout=0.1)
        except queue.Empty:
            eintrag = None

        if eintrag is not None:
            meldung, quelle = _meldung_entpacken(eintrag)

            print(
                f"Kommunikationsmeldung: {meldung!r} "
                f"von {quelle}"
            )

            if meldung.casefold() == erwartete_meldung_norm:
                print(
                    f"Erwartete Meldung {daten['meldung']!r} "
                    "wurde empfangen."
                )
                return zustand, False

            meldungspuffer.append((meldung, quelle))
            print("Meldung wurde für einen späteren Befehl gepuffert.")

        if timeout_s is not None and aktive_wartezeit > timeout_s:
            raise TimeoutError(
                f"Befehl {daten['nummer']} hat die Meldung "
                f"{daten['meldung']!r} nicht innerhalb von "
                f"{timeout_s:g} Sekunden empfangen."
            )



_KEIN_WERT = object()


def _esp_wert_eintrag_lesen(esp_werte, name):
    """Liest einen ESP-Werteintrag aus Speicherobjekt oder Dictionary."""

    if esp_werte is None:
        return None

    if hasattr(esp_werte, "eintrag_lesen"):
        return esp_werte.eintrag_lesen(name)

    if isinstance(esp_werte, dict):
        name_norm = str(name).strip().casefold()

        for schluessel, wert in esp_werte.items():
            if str(schluessel).strip().casefold() == name_norm:
                if isinstance(wert, dict) and "wert" in wert:
                    return dict(wert)

                return {
                    "name": str(schluessel),
                    "wert": wert,
                    "quelle": "Dictionary",
                    "zeit": None,
                }

    return None


def _werte_sind_gleich(istwert, sollwert):
    """Vergleicht Texte ohne Beachtung der Groß-/Kleinschreibung."""

    if isinstance(istwert, str) and isinstance(sollwert, str):
        return istwert.strip().casefold() == sollwert.strip().casefold()

    return istwert == sollwert


def _werte_vergleichen(istwert, operator, sollwert):
    """Vergleicht zwei Werte mit einem freigegebenen Operator."""

    operator = _vergleichsoperator_normalisieren(operator, "intern")

    if operator == "==":
        return _werte_sind_gleich(istwert, sollwert)
    if operator == "!=":
        return not _werte_sind_gleich(istwert, sollwert)

    if isinstance(istwert, str) and isinstance(sollwert, str):
        links = istwert.strip().casefold()
        rechts = sollwert.strip().casefold()
    elif isinstance(istwert, (int, float)) and isinstance(sollwert, (int, float)):
        links = istwert
        rechts = sollwert
    else:
        raise TypeError(
            f"Die Werte {istwert!r} und {sollwert!r} können mit "
            f"dem Operator {operator!r} nicht verglichen werden."
        )

    if operator == "<":
        return links < rechts
    if operator == "<=":
        return links <= rechts
    if operator == ">":
        return links > rechts
    if operator == ">=":
        return links >= rechts

    raise RuntimeError(f"Interner Fehler beim Operator {operator!r}.")


def _esp_wert_anzeigen(daten, esp_werte):
    """Zeigt einen gespeicherten ESP-Wert samt Herkunft an."""

    eintrag = _esp_wert_eintrag_lesen(esp_werte, daten["wertname"])

    if eintrag is None:
        print(f"ESP-Wert {daten['wertname']!r} ist noch nicht vorhanden.")
        return

    print(
        f"ESP-Wert {eintrag.get('name', daten['wertname'])}: "
        f"{eintrag['wert']!r} "
        f"(Quelle: {eintrag.get('quelle', 'unbekannt')})"
    )


def _auf_esp_wert_warten(
    api,
    daten,
    esp_werte,
    steuerbefehle,
    zustand,
):
    """Wartet steuerbar, bis ein gespeicherter ESP-Wert passt."""

    timeout_s = daten["timeout_s"]
    aktive_wartezeit = 0.0
    letzter_zeitpunkt = time.monotonic()

    print(
        f"Warte auf ESP-Wert {daten['wertname']!r} "
        f"{daten['operator']} {daten['sollwert']!r} ..."
    )

    def status_text():
        eintrag = _esp_wert_eintrag_lesen(
            esp_werte,
            daten["wertname"],
        )
        istwert = "noch nicht vorhanden" if eintrag is None else repr(eintrag["wert"])
        timeout_text = (
            "ohne Timeout"
            if timeout_s is None
            else f"Timeout {timeout_s:g} s"
        )
        return (
            f"Befehl {daten['nummer']}: Warte auf "
            f"{daten['wertname']} {daten['operator']} {daten['sollwert']!r}\n"
            f"Aktueller Wert: {istwert}, "
            f"aktive Wartezeit: {aktive_wartezeit:.1f} s, "
            f"{timeout_text}"
        )

    while True:
        jetzt = time.monotonic()

        if zustand == ZUSTAND_LAEUFT:
            aktive_wartezeit += jetzt - letzter_zeitpunkt

        letzter_zeitpunkt = jetzt

        zustand, halt = _steuerbefehle_verarbeiten(
            api,
            steuerbefehle,
            zustand,
            roboter_aktiv=False,
            status_text=status_text,
        )

        if halt:
            return zustand, True

        if zustand == ZUSTAND_PAUSIERT:
            dType.dSleep(100)
            continue

        eintrag = _esp_wert_eintrag_lesen(
            esp_werte,
            daten["wertname"],
        )

        if (
            eintrag is not None
            and _werte_vergleichen(
                eintrag["wert"],
                daten["operator"],
                daten["sollwert"],
            )
        ):
            print(
                f"Erwarteter ESP-Wert empfangen: "
                f"{daten['wertname']} = {eintrag['wert']!r}; "
                f"Bedingung {daten['operator']} {daten['sollwert']!r} erfüllt."
            )
            return zustand, False

        if timeout_s is not None and aktive_wartezeit > timeout_s:
            raise TimeoutError(
                f"Befehl {daten['nummer']} hat den ESP-Wert "
                f"{daten['wertname']!r} {daten['operator']} {daten['sollwert']!r} "
                f"nicht innerhalb von {timeout_s:g} Sekunden empfangen."
            )

        dType.dSleep(100)


def befehlskette_ausfuehren_steuerbar(
    api,
    programm,
    timeout=30.0,
    steuerbefehle=None,
    meldungen=None,
    esp_werte=None,
    tastatur=True,
    max_schritte=1000,
    status_senden=None,
):
    """Führt das Ablaufprogramm mit Sprüngen und Meldungen aus.

    ``timeout`` gilt für jeden einzelnen Dobot-Queue-Befehl.
    ``max_schritte`` schützt vor unbeabsichtigten Endlosschleifen.
    Ein absichtlich dauerhaft laufendes Programm kann einen größeren
    Wert oder ``None`` verwenden.
    """

    if timeout <= 0:
        raise ValueError("timeout muss größer als 0 sein.")

    if max_schritte is not None:
        if not isinstance(max_schritte, int) or max_schritte <= 0:
            raise ValueError(
                "max_schritte muss eine positive ganze Zahl "
                "oder None sein."
            )

    if steuerbefehle is None:
        steuerbefehle = queue.Queue()

    if meldungen is None:
        meldungen = queue.Queue()

    befehle = programm["befehle"]
    marken = programm["marken"]

    if not befehle:
        print("Die Befehlskette ist leer.")
        return "leer"

    eingabe_beenden = threading.Event()
    meldungspuffer = []
    zustand = ZUSTAND_LAEUFT
    programmzeiger = 0
    schritte = 0

    _status_senden(status_senden, "PROGRAMM_GESTARTET", VERSION)

    if tastatur:
        tastatursteuerung_starten(
            steuerbefehle,
            eingabe_beenden,
        )

    try:
        while 0 <= programmzeiger < len(befehle):
            daten = befehle[programmzeiger]

            def status_text():
                return (
                    f"Nächster Befehl {daten['nummer']}: "
                    f"{daten['text']}\n"
                    f"Programmschritt: {schritte}, "
                    f"Programmposition: {programmzeiger + 1} "
                    f"von {len(befehle)}"
                )

            zustand, halt = _steuerbefehle_verarbeiten(
                api,
                steuerbefehle,
                zustand,
                roboter_aktiv=False,
                status_text=status_text,
            )

            if halt:
                _status_senden(status_senden, "BEFEHLSKETTE_BEENDET", "HALT")
                return ZUSTAND_HALT

            zustand, halt = _auf_weiter_warten(
                api,
                steuerbefehle,
                zustand,
                status_text,
            )

            if halt:
                _status_senden(status_senden, "BEFEHLSKETTE_BEENDET", "HALT")
                return ZUSTAND_HALT

            schritte += 1

            if max_schritte is not None and schritte > max_schritte:
                raise RuntimeError(
                    "Die maximale Anzahl von Programmschritten "
                    f"({max_schritte}) wurde überschritten. "
                    "Möglicherweise enthält die Befehlskette eine "
                    "unbeabsichtigte Endlosschleife."
                )

            _status_senden(
                status_senden,
                "BEFEHL_GESTARTET",
                daten["nummer"],
                daten["befehl"],
                daten["text"],
            )

            print()
            print(
                f"Befehl {daten['nummer']} wird ausgeführt: "
                f"{daten['text']} "
                f"[{_befehl_darstellen(daten)}]"
            )

            if daten["art"] == "marke":
                _status_senden(status_senden, "MARKE", daten["marke"])
                _status_senden(status_senden, "BEFEHL_FERTIG", daten["nummer"], daten["befehl"])
                programmzeiger += 1
                continue

            if daten["art"] == "sprung":
                zielposition = marken[daten["ziel_norm"]]
                print(
                    f"Sprung zu Befehl "
                    f"{befehle[zielposition]['nummer']} "
                    f"(Marke {daten['ziel']!r})."
                )
                _status_senden(status_senden, "SPRUNG", daten["ziel"], befehle[zielposition]["nummer"])
                _status_senden(status_senden, "BEFEHL_FERTIG", daten["nummer"], daten["befehl"])
                programmzeiger = zielposition
                continue

            auszufuehrende_daten = daten

            if daten["art"] == "wert_bedingung":
                eintrag = _esp_wert_eintrag_lesen(
                    esp_werte,
                    daten["wertname"],
                )
                istwert = _KEIN_WERT if eintrag is None else eintrag["wert"]
                bedingung_erfuellt = (
                    istwert is not _KEIN_WERT
                    and _werte_vergleichen(
                        istwert,
                        daten["operator"],
                        daten["sollwert"],
                    )
                )
                zweig_name = "WAHR" if bedingung_erfuellt else "FALSCH"
                auszufuehrende_daten = (
                    daten["wahr_befehl"]
                    if bedingung_erfuellt
                    else daten["falsch_befehl"]
                )

                if istwert is _KEIN_WERT:
                    print(
                        f"Bedingung FALSCH: ESP-Wert "
                        f"{daten['wertname']!r} ist nicht vorhanden."
                    )
                else:
                    print(
                        f"Bedingung {zweig_name}: "
                        f"{daten['wertname']} = {istwert!r}; "
                        f"geprüft: {daten['operator']} {daten['sollwert']!r}."
                    )

                print(
                    f"Ausgewählter Teilbefehl: "
                    f"{_befehl_darstellen(auszufuehrende_daten)}"
                )
                _status_senden(
                    status_senden,
                    "BEDINGUNG",
                    daten["wertname"],
                    "NICHT_VORHANDEN" if istwert is _KEIN_WERT else repr(istwert),
                    daten["operator"],
                    repr(daten["sollwert"]),
                    zweig_name,
                    _befehl_darstellen(auszufuehrende_daten),
                )

            if auszufuehrende_daten["art"] == "sprung":
                zielposition = marken[auszufuehrende_daten["ziel_norm"]]
                print(
                    f"Sprung zu Befehl "
                    f"{befehle[zielposition]['nummer']} "
                    f"(Marke {auszufuehrende_daten['ziel']!r})."
                )
                _status_senden(status_senden, "SPRUNG", auszufuehrende_daten["ziel"], befehle[zielposition]["nummer"])
                _status_senden(status_senden, "BEFEHL_FERTIG", daten["nummer"], daten["befehl"])
                programmzeiger = zielposition
                continue

            if auszufuehrende_daten["art"] == "warten":
                _status_senden(status_senden, "WARTE_AUF", "MELDUNG", auszufuehrende_daten["meldung"])
                zustand, halt = _auf_meldung_warten(
                    api,
                    auszufuehrende_daten,
                    meldungen,
                    meldungspuffer,
                    steuerbefehle,
                    zustand,
                )

            elif auszufuehrende_daten["art"] == "wert_warten":
                _status_senden(status_senden, "WARTE_AUF", "WERT", auszufuehrende_daten["wertname"], auszufuehrende_daten["operator"], repr(auszufuehrende_daten["sollwert"]))
                zustand, halt = _auf_esp_wert_warten(
                    api,
                    auszufuehrende_daten,
                    esp_werte,
                    steuerbefehle,
                    zustand,
                )

            elif auszufuehrende_daten["art"] == "wert_status":
                _esp_wert_anzeigen(
                    auszufuehrende_daten,
                    esp_werte,
                )
                halt = False

            elif auszufuehrende_daten["art"] == "esp_senden":
                if status_senden is None:
                    raise RuntimeError(
                        "Der Befehl esp_senden kann nicht ausgeführt "
                        "werden, weil keine ESP32-Verbindung vorhanden ist."
                    )

                nachricht = auszufuehrende_daten["nachricht"]

                try:
                    gesendet = bool(status_senden(nachricht))
                except Exception as fehler:
                    raise RuntimeError(
                        f"Die Nachricht {nachricht!r} konnte nicht "
                        "an den ESP32 gesendet werden: {fehler}"
                    ) from fehler

                if not gesendet:
                    raise RuntimeError(
                        f"Die Nachricht {nachricht!r} konnte nicht "
                        "an den ESP32 gesendet werden."
                    )

                print(f"An ESP32 gesendet: {nachricht!r}")
                halt = False

            elif auszufuehrende_daten["art"] == "status":
                _sauger_status_anzeigen(api, auszufuehrende_daten)
                halt = False

                if auszufuehrende_daten["pause_ms"] > 0:
                    zustand, halt = _zeitpause_ausfuehren(
                        api,
                        auszufuehrende_daten["pause_ms"],
                        steuerbefehle,
                        zustand,
                        auszufuehrende_daten,
                    )

            elif auszufuehrende_daten["art"] == "roboter":
                zustand, halt = _roboterbefehl_ausfuehren(
                    api,
                    auszufuehrende_daten,
                    float(timeout),
                    steuerbefehle,
                    zustand,
                )

            else:
                raise RuntimeError(
                    f"Interner Fehler: unbekannte Befehlsart "
                    f"{auszufuehrende_daten['art']!r}."
                )

            if halt:
                _status_senden(status_senden, "BEFEHLSKETTE_BEENDET", "HALT")
                return ZUSTAND_HALT

            _status_senden(status_senden, "BEFEHL_FERTIG", daten["nummer"], daten["befehl"])
            programmzeiger += 1

        print("Befehlskette vollständig ausgeführt.")
        _status_senden(status_senden, "BEFEHLSKETTE_BEENDET", "NORMAL")
        return ZUSTAND_BEENDET

    except Exception:
        _status_senden(status_senden, "BEFEHLSKETTE_BEENDET", "FEHLER")
        raise

    finally:
        eingabe_beenden.set()


def befehlskette_ausfuehren(
    api,
    programm,
    timeout=30.0,
    meldungen=None,
    esp_werte=None,
    max_schritte=1000,
    status_senden=None,
):
    """Führt das Programm ohne Tastatursteuerung aus."""

    return befehlskette_ausfuehren_steuerbar(
        api,
        programm,
        timeout=timeout,
        steuerbefehle=queue.Queue(),
        meldungen=meldungen,
        esp_werte=esp_werte,
        tastatur=False,
        max_schritte=max_schritte,
        status_senden=status_senden,
    )
