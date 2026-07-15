"""
Hilfsfunktionen zur Steuerung eines Dobot Magician auf Basis von DobotDllType.py.

Version: 1.2.0
Stand: 15.07.2026 - 23:40

Die Datei liegt im Hauptordner ``Dobot_Python``. Die 64-Bit-Version des
Dobot-SDK wird aus dem Unterordner ``sdk64`` geladen.
"""

from pathlib import Path
import ctypes
import os
import platform
import sys

from sdk64 import DobotDllType as dType


VERSION = "1.2.0"
VERSIONSDATUM = "15.07.2026"


def version():
    """Gibt die Versionsinformation dieser Hilfsbibliothek zurück."""

    return f"dobot.py Version {VERSION} - Stand {VERSIONSDATUM}"


def com_ports_ermitteln():
    """Gibt die vom Betriebssystem erkannten seriellen Schnittstellen zurück.

    Das Ergebnis ist eine Liste aus Paaren:
    ``[(Portname, Beschreibung), ...]``.

    Wenn PySerial installiert ist, werden dessen ausführliche Angaben
    verwendet. Unter Windows dient andernfalls die Registrierungsdatenbank
    als Fallback.
    """

    try:
        from serial.tools import list_ports
    except ImportError:
        list_ports = None

    if list_ports is not None:
        ports = [
            (port.device, port.description or "Keine Beschreibung")
            for port in list_ports.comports()
        ]
        return sorted(ports, key=lambda eintrag: eintrag[0].upper())

    # Fallback ohne PySerial für Windows.
    if os.name == "nt":
        try:
            import winreg

            schluessel = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DEVICEMAP\SERIALCOMM",
            )

            ports = []
            index = 0

            while True:
                try:
                    _, portname, _ = winreg.EnumValue(schluessel, index)
                    ports.append((portname, "Serielle Schnittstelle"))
                    index += 1
                except OSError:
                    break

            winreg.CloseKey(schluessel)
            return sorted(
                set(ports),
                key=lambda eintrag: eintrag[0].upper(),
            )

        except OSError:
            return []

    return []


def comport_pruefen(comport):
    """Prüft, ob der gewünschte COM-Port vom Betriebssystem erkannt wird.

    Ist der Port nicht vorhanden, werden alle erkannten seriellen
    Schnittstellen ausgegeben und das Programm mit Fehlercode 1 beendet.
    """

    ports = com_ports_ermitteln()
    vorhandene_portnamen = {
        portname.upper()
        for portname, _ in ports
    }

    if comport.upper() in vorhandene_portnamen:
        print(f"Serielle Schnittstelle: {comport} ist vorhanden.")
        return

    print()
    print(f"FEHLER: Die serielle Schnittstelle {comport} ist nicht verfügbar.")
    print()

    if ports:
        print("Vom Betriebssystem erkannte COM-Ports:")

        for portname, beschreibung in ports:
            print(f"  {portname:<8} {beschreibung}")
    else:
        print("Es wurden keine seriellen Schnittstellen gefunden.")

    print()
    print("Das Programm wird beendet.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Lochrasterplatte
# ---------------------------------------------------------------------------

PLATTE_SPALTEN = 40
PLATTE_ZEILEN = 27
PLATTE_RASTER_MM = 16.0

# Die Kalibrierung wird mit plattenkalibrierung_setzen(...) eingetragen.
# Verwendet werden drei beliebige erreichbare Referenzlöcher, deren
# Rasterpositionen nicht auf einer gemeinsamen Geraden liegen dürfen.
_plattenkalibrierung = None


def _referenzloch_lesen(referenz, bezeichnung):
    """Prüft und zerlegt ein Referenzloch.

    Neue Schreibweise:
        ``(spalte, zeile, x, y)``

    Für die bisherige Eckpunktkalibrierung wird zusätzlich die alte
    Schreibweise ``(x, y)`` unterstützt.
    """

    try:
        werte = tuple(referenz)
    except TypeError as exc:
        raise TypeError(
            f"{bezeichnung} muss ein Tupel oder eine Liste sein."
        ) from exc

    if len(werte) != 4:
        raise ValueError(
            f"{bezeichnung} muss als "
            "(spalte, zeile, x, y) angegeben werden."
        )

    spalte, zeile, x, y = map(float, werte)
    _plattenkoordinate_pruefen(spalte, zeile)

    return spalte, zeile, x, y


def plattenkalibrierung_setzen(
    referenzloch_1,
    referenzloch_2,
    referenzloch_3,
    platten_z,
    standard_r=0.0,
):
    """Kalibriert die Platte mit drei beliebigen erreichbaren Löchern.

    Neue Schreibweise der Referenzpunkte:
        ``(spalte, zeile, x, y)``

    Beispiel:
        ``referenzloch_1=(2, 1, -73.8, -311.1)``

    Die drei Rasterpositionen dürfen nicht auf einer gemeinsamen Geraden
    liegen. Günstig sind zwei weit auseinanderliegende Löcher einer Zeile
    und ein drittes Loch in einer möglichst weit entfernten Zeile.

    Aus Gründen der Abwärtskompatibilität wird auch die bisherige
    Eckpunkt-Schreibweise mit drei XY-Tupeln unterstützt:

        ``loch_1_1=(x, y)``
        ``loch_40_1=(x, y)``
        ``loch_1_27=(x, y)``
    """

    global _plattenkalibrierung

    # Alte Schreibweise erkennen:
    # (x, y), (x, y), (x, y)
    alte_schreibweise = all(
        hasattr(ref, "__len__") and len(ref) == 2
        for ref in (
            referenzloch_1,
            referenzloch_2,
            referenzloch_3,
        )
    )

    if alte_schreibweise:
        referenzloch_1 = (
            1,
            1,
            referenzloch_1[0],
            referenzloch_1[1],
        )
        referenzloch_2 = (
            PLATTE_SPALTEN,
            1,
            referenzloch_2[0],
            referenzloch_2[1],
        )
        referenzloch_3 = (
            1,
            PLATTE_ZEILEN,
            referenzloch_3[0],
            referenzloch_3[1],
        )

    a = _referenzloch_lesen(referenzloch_1, "referenzloch_1")
    b = _referenzloch_lesen(referenzloch_2, "referenzloch_2")
    c = _referenzloch_lesen(referenzloch_3, "referenzloch_3")

    spalte_a, zeile_a, x_a, y_a = a
    spalte_b, zeile_b, x_b, y_b = b
    spalte_c, zeile_c, x_c, y_c = c

    ds_b = spalte_b - spalte_a
    dz_b = zeile_b - zeile_a
    ds_c = spalte_c - spalte_a
    dz_c = zeile_c - zeile_a

    determinante = ds_b * dz_c - ds_c * dz_b

    if abs(determinante) < 1e-9:
        raise ValueError(
            "Die drei Referenzlöcher sind für eine Kalibrierung "
            "ungeeignet: Ihre Rasterpositionen liegen auf einer Geraden."
        )

    dx_b = x_b - x_a
    dx_c = x_c - x_a
    dy_b = y_b - y_a
    dy_c = y_c - y_a

    # Dobot-Vektor für einen Schritt in Spaltenrichtung.
    sx = (dx_b * dz_c - dx_c * dz_b) / determinante
    sy = (dy_b * dz_c - dy_c * dz_b) / determinante

    # Dobot-Vektor für einen Schritt in Zeilenrichtung.
    zx = (ds_b * dx_c - ds_c * dx_b) / determinante
    zy = (ds_b * dy_c - ds_c * dy_b) / determinante

    # Aus dem erreichbaren Referenzloch A wird rechnerisch die Position
    # des möglicherweise nicht erreichbaren Lochs (1, 1) bestimmt.
    x_1_1 = (
        x_a
        - (spalte_a - 1.0) * sx
        - (zeile_a - 1.0) * zx
    )
    y_1_1 = (
        y_a
        - (spalte_a - 1.0) * sy
        - (zeile_a - 1.0) * zy
    )

    _plattenkalibrierung = {
        "loch_1_1": (x_1_1, y_1_1),
        "spaltenvektor": (sx, sy),
        "zeilenvektor": (zx, zy),
        "referenzloecher": (a, b, c),
        "platten_z": float(platten_z),
        "standard_r": float(standard_r),
    }



def _plattenkalibrierung_holen():
    """Liefert die Kalibrierung oder erzeugt eine verständliche Meldung."""

    if _plattenkalibrierung is None:
        raise RuntimeError(
            "Die Lochrasterplatte ist noch nicht kalibriert.\n"
            "Bitte zuerst plattenkalibrierung_setzen(...) aufrufen."
        )

    return _plattenkalibrierung


def _plattenkoordinate_pruefen(spalte, zeile):
    """Prüft, ob die angegebene Position innerhalb des Lochfeldes liegt."""

    if not 1 <= spalte <= PLATTE_SPALTEN:
        raise ValueError(
            f"Spalte {spalte} liegt außerhalb der Platte. "
            f"Erlaubt sind Werte von 1 bis {PLATTE_SPALTEN}."
        )

    if not 1 <= zeile <= PLATTE_ZEILEN:
        raise ValueError(
            f"Zeile {zeile} liegt außerhalb der Platte. "
            f"Erlaubt sind Werte von 1 bis {PLATTE_ZEILEN}."
        )


def _platten_rastervektoren():
    """Liefert die kalibrierten Dobot-XY-Vektoren eines Rasterabstands."""

    k = _plattenkalibrierung_holen()
    return k["spaltenvektor"], k["zeilenvektor"]


def _loch_zu_dobot(spalte, zeile, hoehe=30.0, r=None):
    """Rechnet Lochrasterkoordinaten in Dobot-Koordinaten um."""

    spalte = float(spalte)
    zeile = float(zeile)
    hoehe = float(hoehe)

    _plattenkoordinate_pruefen(spalte, zeile)

    k = _plattenkalibrierung_holen()
    spaltenvektor, zeilenvektor = _platten_rastervektoren()

    x11, y11 = k["loch_1_1"]

    spaltenschritte = spalte - 1.0
    zeilenschritte = zeile - 1.0

    x = (
        x11
        + spaltenschritte * spaltenvektor[0]
        + zeilenschritte * zeilenvektor[0]
    )

    y = (
        y11
        + spaltenschritte * spaltenvektor[1]
        + zeilenschritte * zeilenvektor[1]
    )

    z = k["platten_z"] + hoehe
    rotation = k["standard_r"] if r is None else float(r)

    return x, y, z, rotation


def _dobot_zu_platte(x, y, z):
    """Rechnet Dobot-Koordinaten in Lochrasterkoordinaten zurück."""

    k = _plattenkalibrierung_holen()
    spaltenvektor, zeilenvektor = _platten_rastervektoren()

    x11, y11 = k["loch_1_1"]

    px = float(x) - x11
    py = float(y) - y11

    sx, sy = spaltenvektor
    zx, zy = zeilenvektor

    determinante = sx * zy - sy * zx

    if abs(determinante) < 1e-9:
        raise RuntimeError(
            "Die Plattenkalibrierung ist ungültig. "
            "Die beiden Rasterrichtungen sind nicht unabhängig."
        )

    # Lösung des linearen Gleichungssystems:
    #
    # [sx  zx] [a] = [px]
    # [sy  zy] [b]   [py]
    #
    # a und b sind die Rasterabstände vom Loch (1, 1).
    a = (px * zy - py * zx) / determinante
    b = (sx * py - sy * px) / determinante

    spalte = a + 1.0
    zeile = b + 1.0
    hoehe = float(z) - k["platten_z"]

    return spalte, zeile, hoehe


def plattenkalibrierung_anzeigen():
    """Zeigt Referenzlöcher, Ursprung und Rastervektoren an."""

    k = _plattenkalibrierung_holen()
    spaltenvektor, zeilenvektor = _platten_rastervektoren()

    print("Kalibrierung der Lochrasterplatte")
    print("---------------------------------")

    for nummer, referenz in enumerate(k["referenzloecher"], start=1):
        spalte, zeile, x, y = referenz
        print(
            f"Referenz {nummer}: "
            f"Loch ({spalte:g}, {zeile:g}) -> "
            f"X={x:.2f}, Y={y:.2f}"
        )

    x11, y11 = k["loch_1_1"]

    print()
    print(
        "Rechnerisches Loch (1, 1): "
        f"X={x11:.2f}, Y={y11:.2f}"
    )
    print(f"Platten-Z:   {k['platten_z']:.2f} mm")
    print(f"Standard-R:  {k['standard_r']:.2f}°")
    print()
    print(
        "Rastervektor Spalte: "
        f"dx={spaltenvektor[0]:.4f}, "
        f"dy={spaltenvektor[1]:.4f}"
    )
    print(
        "Rastervektor Zeile:  "
        f"dx={zeilenvektor[0]:.4f}, "
        f"dy={zeilenvektor[1]:.4f}"
    )




# Das von os.add_dll_directory() gelieferte Objekt muss erhalten bleiben,
# solange die DLL verwendet wird.
_dll_suchpfad = None


def init(
    comport="COM10",
    device_name=(
        "Dobot Magician - AG Young Engineers - "
        "Martin-Rinckart-Gymnasium"
    ),
):
    """Lädt die 64-Bit-DLL, verbindet den Dobot und gibt ``api`` zurück."""

    global _dll_suchpfad

    hauptverzeichnis = Path(__file__).resolve().parent
    sdk_verzeichnis = hauptverzeichnis / "sdk64"
    dll_datei = sdk_verzeichnis / "DobotDll.dll"

    print("Python-Version:    ", platform.python_version())
    print("Python-Architektur:", platform.architecture()[0])
    print("SDK-Verzeichnis:   ", sdk_verzeichnis)
    print("DLL-Datei:         ", dll_datei)
    print("DLL vorhanden:     ", dll_datei.exists())

    # Vor dem Laden der DLL prüfen, ob der gewünschte COM-Port existiert.
    comport_pruefen(comport)

    if not dll_datei.exists():
        raise FileNotFoundError(
            "Die Dobot-DLL wurde nicht gefunden:\n"
            f"{dll_datei}\n\n"
            "Erwartete Ordnerstruktur:\n"
            "Dobot_Python\\\n"
            "├── dobot.py\n"
            "├── sdk64\\\n"
            "│   ├── DobotDll.dll\n"
            "│   └── DobotDllType.py\n"
            "└── projekt01\\\n"
            "    └── start.py"
        )

    # Unter Windows können sich in sdk64 weitere benötigte DLLs befinden.
    if hasattr(os, "add_dll_directory"):
        _dll_suchpfad = os.add_dll_directory(str(sdk_verzeichnis))

    # DobotDll.dll über ihren vollständigen Pfad laden.
    api = ctypes.CDLL(str(dll_datei))

    result = dType.ConnectDobot(api, comport, 115200)
    print("ConnectDobot-Ergebnis:", result)

    # 0 bedeutet bei der Dobot-API: Verbindung erfolgreich.
    if result[0] != 0:
        meldungen = {
            1: "Dobot wurde nicht gefunden.",
            2: "Der COM-Port ist bereits belegt.",
        }
        meldung = meldungen.get(result[0], "Unbekannter Verbindungsfehler.")
        raise ConnectionError(
            f"Verbindung über {comport} fehlgeschlagen: {meldung} "
            f"(Fehlercode {result[0]})"
        )

    if device_name:
        dType.SetDeviceName(api, device_name)

    name = dType.GetDeviceName(api)
    seriennummer = dType.GetDeviceSN(api)

    print("Gerätename:   ", name)
    print("Seriennummer: ", seriennummer)

    return api


def warten_bis_fertig(api, ziel_index):
    """Wartet, bis ein Queue-Befehl vollständig ausgeführt wurde."""

    while dType.GetQueuedCmdCurrentIndex(api)[0] < ziel_index:
        dType.dSleep(100)


def queue_starten(api):
    """Stoppt eine laufende Queue, löscht sie und startet sie neu."""

    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)
    dType.SetQueuedCmdStartExec(api)


def queue_stoppen(api):
    """Stoppt die Ausführung der Queue."""

    dType.SetQueuedCmdStopExec(api)


def position_lesen(api):
    """Liest die kartesische Position X, Y, Z und R."""

    return dType.GetPose(api)[:4]


def position_anzeigen(api):
    """Liest und zeigt die aktuelle kartesische Position an."""

    x, y, z, r = position_lesen(api)

    print(
        f"X={x:.1f} mm, "
        f"Y={y:.1f} mm, "
        f"Z={z:.1f} mm, "
        f"R={r:.1f}°"
    )


def fahre_zu(api, x, y, z, r, modus=None):
    """Fährt zu einer Zielposition und wartet auf das Bewegungsende."""

    if modus is None:
        modus = dType.PTPMode.PTPMOVJXYZMode

    ziel_index = dType.SetPTPCmd(
        api,
        modus,
        x,
        y,
        z,
        r,
        isQueued=1,
    )[0]

    warten_bis_fertig(api, ziel_index)


def fahre_zu_loch(
    api,
    spalte,
    zeile,
    hoehe=30.0,
    r=None,
):
    """Fährt gelenkoptimiert zu einer Position im Lochraster.

    ``spalte`` und ``zeile`` beginnen bei 1.

    ``hoehe`` ist die Höhe in Millimetern über der Plattenoberfläche.
    Der sichere Standardwert beträgt 30 mm.

    Beispiel:
        ``fahre_zu_loch(api, 10, 8, hoehe=30)``
    """

    x, y, z, rotation = _loch_zu_dobot(
        spalte=spalte,
        zeile=zeile,
        hoehe=hoehe,
        r=r,
    )

    fahre_zu(
        api,
        x,
        y,
        z,
        rotation,
        dType.PTPMode.PTPMOVJXYZMode,
    )

    return x, y, z, rotation


def fahre_zu_loch_linear(
    api,
    spalte,
    zeile,
    hoehe=30.0,
    r=None,
):
    """Fährt auf einer geraden Bahn zu einer Position im Lochraster.

    Der gesamte Weg wird linear ausgeführt. Vor allem bei niedriger Höhe
    muss deshalb geprüft werden, ob der Fahrweg frei ist.

    Beispiel:
        ``fahre_zu_loch_linear(api, 10, 8, hoehe=5)``
    """

    x, y, z, rotation = _loch_zu_dobot(
        spalte=spalte,
        zeile=zeile,
        hoehe=hoehe,
        r=r,
    )

    fahre_zu(
        api,
        x,
        y,
        z,
        rotation,
        dType.PTPMode.PTPMOVLXYZMode,
    )

    return x, y, z, rotation


def lochposition_lesen(api):
    """Liest die aktuelle Position im Koordinatensystem der Lochrasterplatte.

    Rückgabe:
        ``(spalte, zeile, hoehe)``

    ``spalte`` und ``zeile`` können Dezimalstellen enthalten. Ganzzahlige
    Werte entsprechen den Mittelpunkten der Rasterlöcher. ``hoehe`` ist die
    Höhe in Millimetern über der kalibrierten Plattenoberfläche.
    """

    x, y, z, _r = position_lesen(api)
    return _dobot_zu_platte(x, y, z)


def lochposition_anzeigen(api):
    """Liest und zeigt die aktuelle Position auf der Lochrasterplatte an.

    Zusätzlich zur genauen Rasterposition wird das nächstgelegene Loch
    ausgegeben. Die gelesenen Werte werden auch als Tupel zurückgegeben.
    """

    spalte, zeile, hoehe = lochposition_lesen(api)
    naechste_spalte = round(spalte)
    naechste_zeile = round(zeile)

    print("Aktuelle Lochposition:")
    print(f"  Spalte: {spalte:.3f}")
    print(f"  Zeile:  {zeile:.3f}")
    print(f"  Höhe:   {hoehe:.2f} mm")
    print(
        "  Nächstes Loch: "
        f"({naechste_spalte}, {naechste_zeile})"
    )

    return spalte, zeile, hoehe


def aktuelle_plattenposition(api, anzeigen=True):
    """Kompatibler Alias für die Lochpositionsfunktionen.

    Mit ``anzeigen=True`` wird ``lochposition_anzeigen(api)`` verwendet.
    Mit ``anzeigen=False`` wird ``lochposition_lesen(api)`` verwendet.

    Rückgabe:
        ``(spalte, zeile, hoehe)``
    """

    if anzeigen:
        return lochposition_anzeigen(api)

    return lochposition_lesen(api)


def home(api):
    """Führt eine HOME-Fahrt aus und wartet auf deren Abschluss."""

    print("HOME-Fahrt wird gestartet.")

    ziel_index = dType.SetHOMECmd(
        api,
        0,
        isQueued=1,
    )[0]

    warten_bis_fertig(api, ziel_index)

    print("HOME-Fahrt abgeschlossen.")


def test_z(api):
    """Erlaubt das interaktive Verändern der aktuellen Z-Koordinate."""

    print()
    print("Interaktiver Test der Z-Koordinate")
    print("----------------------------------")

    while True:
        x, y, z, r = position_lesen(api)

        print(
            f"Position: X={x:.1f}, Y={y:.1f}, "
            f"Z={z:.1f}, R={r:.1f}"
        )

        eingabe = input(
            "Neue Z-Koordinate oder 'a' zum Abbrechen: "
        ).strip()

        if eingabe.lower() == "a":
            break

        # Auch eine Eingabe mit deutschem Dezimalkomma wird akzeptiert.
        try:
            neue_z = float(eingabe.replace(",", "."))
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl oder 'a' eingeben.")
            continue

        fahre_zu(
            api,
            x,
            y,
            neue_z,
            r,
            dType.PTPMode.PTPMOVLXYZMode,
        )

        print("Erreichte Position:")
        position_anzeigen(api)

    print("Z-Test beendet.")

def fahre_sofort_zu(api, x, y, z):
    """Sendet eine Bewegung sofort, ohne sie in die Queue einzureihen.

    Die aktuelle Werkzeugrotation R wird beibehalten.
    Als Bewegungsart wird PTPMOVJXYZMode verwendet.
    """

    if api is None:
        raise RuntimeError("Der Dobot ist nicht verbunden.")

    # Aktuelle Werkzeugrotation beibehalten.
    _, _, _, r = position_lesen(api)

    return dType.SetPTPCmd(
        api,
        dType.PTPMode.PTPMOVJXYZMode,
        x,
        y,
        z,
        r,
        isQueued=0,
    )

def sauger_status(api):
    """Gibt True zurück, wenn der Sauger eingeschaltet ist."""
    return bool(dType.GetEndEffectorSuctionCup(api)[0])

def sauger_aktivieren(api, isQueued=1):
    """Aktiviert den Sauger."""
    return dType.SetEndEffectorSuctionCup(
        api,
        True,
        True,
        isQueued=isQueued,
    )

def sauger_deaktivieren(api, isQueued=1):
    """Deaktiviert den Sauger."""
    return dType.SetEndEffectorSuctionCup(
        api,
        True,
        False,
        isQueued=isQueued,
    )

def ausfuehren(api):
    """Startet den auf der Webseite beschriebenen Beispielablauf."""

    print()
    print("Roboterprogramm wird gestartet.")
    print("--------------------------------")

    queue_starten(api)

    try:
        print("Aktuelle Position:")
        position_anzeigen(api)

        test_z(api)
    finally:
        queue_stoppen(api)

        print()
        print("Roboterprogramm beendet.")
# ---------------------------------------------------------------------------
# Alarmfunktionen
# ---------------------------------------------------------------------------

ALARM_MELDUNGEN = {
    # Allgemeine Fehler
    0x00: "Reset-Alarm",
    0x01: "Unbekannter oder ungültiger Befehl",
    0x02: "Dateisystemfehler",
    0x03: "Kommunikationsfehler zwischen MCU und FPGA",
    0x04: "Fehler des Winkelsensors",

    # Planungsfehler
    0x10: "Zielposition liegt in einer Singularität",
    0x11: "Zielposition liegt außerhalb des Arbeitsbereichs",
    0x12: "Zielposition überschreitet einen Gelenkgrenzwert",
    0x13: "Doppelte oder ungeeignete Punkte bei ARC/JUMP",
    0x14: "Ungültige Eingabeparameter für ARC",
    0x15: "Ungültige JUMP-Parameter",

    # Bewegungsfehler
    0x20: "Bewegungsbahn führt durch eine Singularität",
    0x21: "Bewegungsbahn liegt außerhalb des Arbeitsbereichs",
    0x22: "Bewegung überschreitet einen Gelenkgrenzwert",

    # Geschwindigkeitsfehler
    0x30: "Gelenk 1: Geschwindigkeit zu hoch",
    0x31: "Gelenk 2: Geschwindigkeit zu hoch",
    0x32: "Gelenk 3: Geschwindigkeit zu hoch",
    0x33: "Gelenk 4: Geschwindigkeit zu hoch",

    # Grenzwertfehler
    0x40: "Gelenk 1: positiver Grenzwert erreicht",
    0x41: "Gelenk 1: negativer Grenzwert erreicht",
    0x42: "Gelenk 2: positiver Grenzwert erreicht",
    0x43: "Gelenk 2: negativer Grenzwert erreicht",
    0x44: "Gelenk 3: positiver Grenzwert erreicht",
    0x45: "Gelenk 3: negativer Grenzwert erreicht",
    0x46: "Gelenk 4: positiver Grenzwert erreicht",
    0x47: "Gelenk 4: negativer Grenzwert erreicht",
    0x48: "Parallelogramm: positiver Grenzwert erreicht",
    0x49: "Parallelogramm: negativer Grenzwert erreicht",

    # Schrittverluste
    0x50: "Gelenk 1: Schrittverlust erkannt",
    0x51: "Gelenk 2: Schrittverlust erkannt",
    0x52: "Gelenk 3: Schrittverlust erkannt",
    0x53: "Gelenk 4: Schrittverlust erkannt",
}

def alarme_loeschen(api):
    """Löscht alle gespeicherten Alarmzustände des Dobot.

    Achtung:
        Besteht die Ursache weiterhin, wird der Alarm erneut ausgelöst.
    """

    if api is None:
        raise RuntimeError("Der Dobot ist nicht verbunden.")

    dType.ClearAllAlarmsState(api)

def alarme_lesen(api):
    """Liest die aktuell gesetzten Alarmnummern des Dobot."""

    alarmdaten, laenge = dType.GetAlarmsState(api)

    aktive_alarme = []

    for byte_index, wert in enumerate(alarmdaten[:laenge]):
        for bit_index in range(8):
            if wert & (1 << bit_index):
                alarmnummer = byte_index * 8 + bit_index
                aktive_alarme.append(alarmnummer)

    return aktive_alarme


def alarme_anzeigen(api):
    """Liest die aktiven Alarme und zeigt Nummer und Fehlermeldung an."""

    aktive_alarme = alarme_lesen(api)

    if not aktive_alarme:
        print("Keine Alarme aktiv.")
        return

    print(f"{len(aktive_alarme)} Alarm(e) aktiv:")
    print()

    for alarmnummer in aktive_alarme:
        meldung = ALARM_MELDUNGEN.get(
            alarmnummer,
            "Unbekannter Alarm"
        )

        print(
            f"  Alarm {alarmnummer:3d} "
            f"(0x{alarmnummer:02X}): "
            f"{meldung}"
        )

def main():
    """Hinweis beim direkten Start dieser Bibliotheksdatei."""

    print(
        "Diese Datei wird normalerweise nicht direkt gestartet.\n"
        "Bitte 'start.py' ausführen."
    )


if __name__ == "__main__":
    main()