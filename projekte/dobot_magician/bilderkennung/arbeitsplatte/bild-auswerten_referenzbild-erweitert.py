from pathlib import Path
import math

import cv2
import numpy as np


# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

SCHWELLWERT = 30
MIN_FLAECHE = 1000


# ------------------------------------------------------------
# Farbe bestimmen
# ------------------------------------------------------------

def farbe_bestimmen(farbton, saettigung):
    """
    Bestimmt eine vereinfachte Farbbezeichnung
    aus Farbton und Sättigung.
    """

    if saettigung < 40:
        return "Grau/Weiss"

    if farbton < 10 or farbton >= 170:
        return "Rot"

    if farbton < 40:
        return "Gelb"

    if farbton < 85:
        return "Gruen"

    if farbton < 130:
        return "Blau"

    if farbton < 165:
        return "Violett"

    return "Unbekannt"


# ------------------------------------------------------------
# Form bestimmen
# ------------------------------------------------------------

def form_bestimmen(kontur):
    flaeche = cv2.contourArea(kontur)
    umfang = cv2.arcLength(kontur, True)

    if umfang == 0:
        return "Unbekannt", 0, 0.0

    naeherung = cv2.approxPolyDP(
        kontur,
        0.02 * umfang,
        True
    )

    anzahl_ecken = len(naeherung)

    x, y, breite, hoehe = cv2.boundingRect(kontur)

    kreisfoermigkeit = (
        4 * math.pi * flaeche
        / (umfang * umfang)
    )

    if kreisfoermigkeit > 0.82:
        form = "Kreis"

    elif anzahl_ecken == 3:
        form = "Dreieck"

    elif anzahl_ecken == 4:
        seitenverhaeltnis = breite / float(hoehe)

        if 0.90 <= seitenverhaeltnis <= 1.10:
            form = "Quadrat"
        else:
            form = "Rechteck"

    else:
        form = f"Unbekannt ({anzahl_ecken} Ecken)"

    return form, anzahl_ecken, kreisfoermigkeit

    
# ------------------------------------------------------------
# Bilder laden
# ------------------------------------------------------------

ordner = Path(__file__).resolve().parent

pfad_leer = ordner / "bilder/arbeitsplatte_leer.png"
pfad_objekte = ordner / "bilder/arbeitsplatte.png"

bild_leer_orginal = cv2.imread(str(pfad_leer))
bild_objekte_orginal = cv2.imread(str(pfad_objekte))


bild_leer = cv2.resize(bild_leer_orginal, None, fx=0.15, fy=0.15, interpolation=cv2.INTER_AREA )

bild_objekte = cv2.resize(bild_objekte_orginal, None, fx=0.15, fy=0.15, interpolation=cv2.INTER_AREA )

if bild_leer is None:
    raise FileNotFoundError(
        f"Referenzbild nicht gefunden:\n{pfad_leer}"
    )

if bild_objekte is None:
    raise FileNotFoundError(
        f"Objektbild nicht gefunden:\n{pfad_objekte}"
    )

if bild_leer.shape != bild_objekte.shape:
    raise ValueError(
        "Referenzbild und Objektbild müssen gleich groß sein."
    )

ergebnis = bild_objekte.copy()


# ------------------------------------------------------------
# Referenzbild vom Objektbild abziehen
# ------------------------------------------------------------

differenz = cv2.absdiff(
    bild_objekte,
    bild_leer
)

differenz_grau = cv2.cvtColor(
    differenz,
    cv2.COLOR_BGR2GRAY
)

_, maske = cv2.threshold(
    differenz_grau,
    SCHWELLWERT,
    255,
    cv2.THRESH_BINARY
)


# ------------------------------------------------------------
# Maske bereinigen
# ------------------------------------------------------------

kernel = cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE,
    (5, 5)
)

maske = cv2.morphologyEx(
    maske,
    cv2.MORPH_OPEN,
    kernel
)

maske = cv2.morphologyEx(
    maske,
    cv2.MORPH_CLOSE,
    kernel,
    iterations=2
)


# ------------------------------------------------------------
# Konturen suchen
# ------------------------------------------------------------

konturen, _ = cv2.findContours(
    maske,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

hsv = cv2.cvtColor(
    bild_objekte,
    cv2.COLOR_BGR2HSV
)

objekte = []


# ------------------------------------------------------------
# Konturen auswerten
# ------------------------------------------------------------

for kontur in konturen:
    flaeche = cv2.contourArea(kontur)

    if flaeche < MIN_FLAECHE:
        continue

    umfang = cv2.arcLength(kontur, True)

    x, y, breite, hoehe = cv2.boundingRect(kontur)

    # Mittelpunkt bestimmen
    momente = cv2.moments(kontur)

    if momente["m00"] != 0:
        mitte_x = int(
            momente["m10"] / momente["m00"]
        )

        mitte_y = int(
            momente["m01"] / momente["m00"]
        )

    else:
        mitte_x = x + breite // 2
        mitte_y = y + hoehe // 2

    # Form bestimmen
    form, ecken, kreisfoermigkeit = form_bestimmen(
        kontur
    )

    # Maske für genau dieses Objekt erzeugen
    objektmaske = np.zeros(
        maske.shape,
        dtype=np.uint8
    )

    cv2.drawContours(
        objektmaske,
        [kontur],
        -1,
        255,
        -1
    )

    # Mittlere Farbe innerhalb des Objektes
    mittlere_hsv_farbe = cv2.mean(
        hsv,
        mask=objektmaske
    )

    farbton = mittlere_hsv_farbe[0]
    saettigung = mittlere_hsv_farbe[1]

    farbe = farbe_bestimmen(
        farbton,
        saettigung
    )

    objekt = {
        "kontur": kontur,
        "farbe": farbe,
        "form": form,
        "x": x,
        "y": y,
        "mitte_x": mitte_x,
        "mitte_y": mitte_y,
        "breite": breite,
        "hoehe": hoehe,
        "flaeche": flaeche,
        "umfang": umfang,
        "ecken": ecken,
        "kreisfoermigkeit": kreisfoermigkeit
    }

    objekte.append(objekt)


# ------------------------------------------------------------
# Objekte sortieren
# ------------------------------------------------------------

objekte.sort(
    key=lambda objekt: (
        objekt["mitte_y"],
        objekt["mitte_x"]
    )
)


# ------------------------------------------------------------
# Textausgabe in Thonny
# ------------------------------------------------------------

print()
print("AUSWERTUNG MIT REFERENZBILD")
print("=" * 116)

print(
    f'{"Nr.":>3} '
    f'{"Farbe":<12} '
    f'{"Form":<16} '
    f'{"Mitte x":>8} '
    f'{"Mitte y":>8} '
    f'{"Breite":>8} '
    f'{"Hoehe":>8} '
    f'{"Flaeche":>10} '
    f'{"Umfang":>10} '
    f'{"Ecken":>6}'
)

print("-" * 116)

for nummer, objekt in enumerate(objekte, start=1):
    objekt["nummer"] = nummer

    print(
        f'{nummer:>3} '
        f'{objekt["farbe"]:<12} '
        f'{objekt["form"]:<16} '
        f'{objekt["mitte_x"]:>8} '
        f'{objekt["mitte_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["flaeche"]:>10.1f} '
        f'{objekt["umfang"]:>10.1f} '
        f'{objekt["ecken"]:>6}'
    )

print("-" * 116)
print(f"Anzahl erkannter Objekte: {len(objekte)}")

print()

for objekt in objekte:
    print(
        f'Objekt {objekt["nummer"]}: '
        f'{objekt["farbe"]}, '
        f'{objekt["form"]}, '
        f'Mittelpunkt=({objekt["mitte_x"]}, '
        f'{objekt["mitte_y"]}), '
        f'Groesse={objekt["breite"]} x '
        f'{objekt["hoehe"]} Pixel, '
        f'Flaeche={objekt["flaeche"]:.1f} Pixel²'
    )


# ------------------------------------------------------------
# Ergebnisbild beschriften
# ------------------------------------------------------------

for objekt in objekte:
    cv2.drawContours(
        ergebnis,
        [objekt["kontur"]],
        -1,
        (0, 0, 0),
        3
    )

    cv2.rectangle(
        ergebnis,
        (objekt["x"], objekt["y"]),
        (
            objekt["x"] + objekt["breite"],
            objekt["y"] + objekt["hoehe"]
        ),
        (0, 0, 0),
        2
    )

    cv2.circle(
        ergebnis,
        (
            objekt["mitte_x"],
            objekt["mitte_y"]
        ),
        5,
        (0, 0, 0),
        -1
    )

    text = (
        f'{objekt["nummer"]}: '
        f'{objekt["farbe"]} '
        f'{objekt["form"]}'
    )

    cv2.putText(
        ergebnis,
        text,
        (
            objekt["x"],
            max(objekt["y"] - 8, 20)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        2
    )


# ------------------------------------------------------------
# Ergebnis anzeigen
# ------------------------------------------------------------

cv2.imshow(
    "Differenz zum Referenzbild",
    differenz
)

cv2.imshow(
    "Objektmaske",
    maske
)

cv2.imshow(
    "Erkannte Objekte",
    ergebnis
)

cv2.waitKey(0)
cv2.destroyAllWindows()