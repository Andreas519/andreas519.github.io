"""Datenstruktur für ein Würfelcontainerlager auf einer Lochrasterplatte.

Ein Würfelcontainer belegt eine Fläche von 3 x 3 Löchern. Das mittlere
Loch ist die Lochkoordinate des Lagerplatzes. Gespeichert werden nur das
Mittelloch und die Stapelbelegung. Alle weiteren Lochpositionen werden
bei Bedarf aus dem Mittelloch abgeleitet.
"""

VERSION = "3x3-mittelloch-1.1"

PLATTE_SPALTEN = 40
PLATTE_ZEILEN = 27
MAX_STAPELHOEHE = 3

LAGERPLAETZE = {}


# Alle Mittellöcher, an denen eine vollständige 3-x-3-Fläche auf die Platte passt.
MOEGLICHE_POSITIONEN = tuple(
    (spalte, zeile)
    for zeile in range(2, PLATTE_ZEILEN)
    for spalte in range(2, PLATTE_SPALTEN)
)


def _ganzzahlige_lochkoordinate(wert, bezeichnung):
    """Prüft eine ganzzahlige Lochkoordinate."""

    if isinstance(wert, bool):
        raise TypeError(f"{bezeichnung} muss eine ganze Zahl sein.")

    try:
        zahl = int(wert)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{bezeichnung} muss eine ganze Zahl sein.") from exc

    if zahl != wert:
        raise ValueError(f"{bezeichnung} muss eine ganze Zahl sein.")

    return zahl


def _mittelloch_pruefen(mittelspalte, mittelzeile):
    """Prüft, ob rund um das Mittelloch eine 3-x-3-Fläche Platz hat."""

    mittelspalte = _ganzzahlige_lochkoordinate(
        mittelspalte, "Die Mittelspalte"
    )
    mittelzeile = _ganzzahlige_lochkoordinate(
        mittelzeile, "Die Mittelzeile"
    )

    if not 2 <= mittelspalte <= PLATTE_SPALTEN - 1:
        raise ValueError(
            f"Die Mittelspalte muss zwischen 2 und {PLATTE_SPALTEN - 1} liegen."
        )

    if not 2 <= mittelzeile <= PLATTE_ZEILEN - 1:
        raise ValueError(
            f"Die Mittelzeile muss zwischen 2 und {PLATTE_ZEILEN - 1} liegen."
        )

    return mittelspalte, mittelzeile


def flaechenloecher(mittelloch):
    """Leitet die neun Löcher der 3-x-3-Fläche vom Mittelloch ab."""

    mittelspalte, mittelzeile = _mittelloch_pruefen(*mittelloch)

    return tuple(
        (mittelspalte + dx, mittelzeile + dy)
        for dy in (-1, 0, 1)
        for dx in (-1, 0, 1)
    )


def zapfenloecher(mittelloch):
    """Leitet die acht äußeren Zapfen- bzw. Stapellöcher ab."""

    return tuple(
        loch for loch in flaechenloecher(mittelloch)
        if loch != tuple(mittelloch)
    )


def containerposition_erzeugen(mittelspalte, mittelzeile):
    """Erzeugt den minimalen Datensatz eines Lagerplatzes."""

    mittelloch = _mittelloch_pruefen(mittelspalte, mittelzeile)

    return {
        "mittelloch": mittelloch,
        "stapel": [None] * MAX_STAPELHOEHE,
    }


def position_moeglich(mittelspalte, mittelzeile):
    """Liefert True, wenn die 3-x-3-Fläche vollständig auf die Platte passt."""

    try:
        _mittelloch_pruefen(mittelspalte, mittelzeile)
    except (TypeError, ValueError):
        return False

    return True


def lagerplatz_hinzufuegen(name, mittelspalte, mittelzeile):
    """Fügt einen frei benannten Lagerplatz hinzu."""

    name = str(name).strip()

    if not name:
        raise ValueError("Der Lagerplatz benötigt einen Namen.")

    if name in LAGERPLAETZE:
        raise ValueError(f"Der Lagerplatz {name!r} existiert bereits.")

    neuer_platz = containerposition_erzeugen(mittelspalte, mittelzeile)
    neue_flaeche = set(flaechenloecher(neuer_platz["mittelloch"]))

    for vorhandener_name, vorhandener_platz in LAGERPLAETZE.items():
        vorhandene_flaeche = set(
            flaechenloecher(vorhandener_platz["mittelloch"])
        )

        if neue_flaeche & vorhandene_flaeche:
            raise ValueError(
                f"Der Lagerplatz {name!r} überschneidet sich mit "
                f"{vorhandener_name!r}."
            )

    LAGERPLAETZE[name] = neuer_platz
    return neuer_platz


def lagerplatz_holen(name):
    """Liefert den Datensatz eines benannten Lagerplatzes."""

    try:
        return LAGERPLAETZE[name]
    except KeyError as exc:
        raise KeyError(f"Unbekannter Lagerplatz: {name!r}") from exc


def lagerplatz_entfernen(name):
    """Entfernt einen leeren Lagerplatz."""

    platz = lagerplatz_holen(name)

    if any(container is not None for container in platz["stapel"]):
        raise ValueError(f"Der Lagerplatz {name!r} ist nicht leer.")

    del LAGERPLAETZE[name]


def lochkoordinate(lagerplatz_name):
    """Liefert das Mittelloch als (Spalte, Zeile)."""

    return lagerplatz_holen(lagerplatz_name)["mittelloch"]


def greifposition(lagerplatz_name):
    """Liefert die Greifposition; sie entspricht dem Mittelloch."""

    return lochkoordinate(lagerplatz_name)


def lagerplatz_flaechenloecher(lagerplatz_name):
    """Liefert die neun belegten Löcher eines Lagerplatzes."""

    return flaechenloecher(lochkoordinate(lagerplatz_name))


def lagerplatz_zapfenloecher(lagerplatz_name):
    """Liefert die acht äußeren Zapfenlöcher eines Lagerplatzes."""

    return zapfenloecher(lochkoordinate(lagerplatz_name))


def finde_container(container_id):
    """Sucht einen Container und liefert (Lagerplatzname, Ebene) oder None."""

    for name, platz in LAGERPLAETZE.items():
        for ebene, inhalt in enumerate(platz["stapel"]):
            if inhalt == container_id:
                return name, ebene

    return None


def naechste_freie_ebene(lagerplatz_name):
    """Liefert die nächste freie Ebene oder None bei vollem Stapel."""

    platz = lagerplatz_holen(lagerplatz_name)

    for ebene, inhalt in enumerate(platz["stapel"]):
        if inhalt is None:
            return ebene

    return None


def einlagern(container_id, lagerplatz_name):
    """Trägt einen Container auf der niedrigsten freien Ebene ein."""

    if finde_container(container_id) is not None:
        raise ValueError(
            f"Der Container {container_id!r} ist bereits eingelagert."
        )

    platz = lagerplatz_holen(lagerplatz_name)

    for ebene, inhalt in enumerate(platz["stapel"]):
        if inhalt is None:
            platz["stapel"][ebene] = container_id
            return ebene

    raise ValueError(f"Der Lagerplatz {lagerplatz_name!r} ist voll.")


def auslagern(lagerplatz_name):
    """Entnimmt den obersten Container und liefert (Container-ID, Ebene)."""

    platz = lagerplatz_holen(lagerplatz_name)

    for ebene in range(MAX_STAPELHOEHE - 1, -1, -1):
        container_id = platz["stapel"][ebene]

        if container_id is not None:
            platz["stapel"][ebene] = None
            return container_id, ebene

    raise ValueError(f"Der Lagerplatz {lagerplatz_name!r} ist leer.")


def belegung_anzeigen():
    """Gibt alle Lagerplätze und deren Stapelbelegung aus."""

    if not LAGERPLAETZE:
        print("Es wurden noch keine Lagerplätze angelegt.")
        return

    print("Containerlager")
    print("---------------")

    for name, platz in LAGERPLAETZE.items():
        spalte, zeile = platz["mittelloch"]
        stapel_text = ", ".join(
            "frei" if container is None else str(container)
            for container in platz["stapel"]
        )

        print(
            f"{name}: Mittelloch ({spalte}, {zeile}), "
            f"Stapel unten→oben: [{stapel_text}]"
        )
