from pathlib import Path
import math

import cv2
import numpy as np


# ------------------------------------------------------------
# Farbe bestimmen
# ------------------------------------------------------------

def farbe_bestimmen(farbton):
    """
    Ermittelt einen Farbnamen aus dem HSV-Farbton.
    OpenCV verwendet für H Werte von 0 bis 179.
    """

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

    if kreisfoermigkeit > 0.84:
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
# Bild laden
# ------------------------------------------------------------

ordner = Path(__file__).resolve().parent
bildpfad = ordner / "bilder/arbeitsplatte.png"

orginal_bild = cv2.imread(str(bildpfad))

if orginal_bild is None:
    raise FileNotFoundError(
        f"Das Bild wurde nicht gefunden:\n{bildpfad}"
    )

bild = cv2.resize(
    orginal_bild,
    None,
    fx=0.15,
    fy=0.15,                 # Breite, Höhe
    interpolation=cv2.INTER_AREA
)

ergebnis = bild.copy()


# ------------------------------------------------------------
# Farbige Flächen auswählen
# ------------------------------------------------------------

hsv = cv2.cvtColor(
    bild,
    cv2.COLOR_BGR2HSV
)

maske = cv2.inRange(
    hsv,
    np.array([0, 80, 50]),
    np.array([179, 255, 255])
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
    kernel
)


# ------------------------------------------------------------
# Konturen suchen
# ------------------------------------------------------------

konturen, _ = cv2.findContours(
    maske,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

objekte = []


# ------------------------------------------------------------
# Konturen auswerten
# ------------------------------------------------------------

for kontur in konturen:
    flaeche = cv2.contourArea(kontur)

    # Kleine rote Striche, Rasterpunkte und Störungen
    # nicht als Objekte übernehmen
    if flaeche < 2000:
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

    # Form ermitteln
    form, ecken, kreisfoermigkeit = form_bestimmen(
        kontur
    )

    # Maske nur für dieses Objekt erzeugen
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

    # Mittlere HSV-Farbe innerhalb des Objektes
    mittlere_farbe = cv2.mean(
        hsv,
        mask=objektmaske
    )

    farbton = mittlere_farbe[0]
    farbe = farbe_bestimmen(farbton)

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
        "kreisfoermigkeit": kreisfoermigkeit,
        "farbton": farbton,
    }

    objekte.append(objekt)


# ------------------------------------------------------------
# Objekte von links nach rechts sortieren
# ------------------------------------------------------------

objekte.sort(
    key=lambda objekt: objekt["mitte_x"]
)


# ------------------------------------------------------------
# Textausgabe in der Thonny-Shell
# ------------------------------------------------------------

print()
print("AUSWERTUNG DER ARBEITSPLATTE")
print("=" * 113)

print(
    f'{"Nr.":>3} '
    f'{"Farbe":<10} '
    f'{"Form":<13} '
    f'{"Mitte x":>8} '
    f'{"Mitte y":>8} '
    f'{"Breite":>8} '
    f'{"Hoehe":>8} '
    f'{"Flaeche":>10} '
    f'{"Umfang":>10} '
    f'{"Ecken":>6}'
)

print("-" * 113)

for nummer, objekt in enumerate(objekte, start=1):
    objekt["nummer"] = nummer

    print(
        f'{nummer:>3} '
        f'{objekt["farbe"]:<10} '
        f'{objekt["form"]:<13} '
        f'{objekt["mitte_x"]:>8} '
        f'{objekt["mitte_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["flaeche"]:>10.1f} '
        f'{objekt["umfang"]:>10.1f} '
        f'{objekt["ecken"]:>6}'
    )

print("-" * 113)

print(
    f"Anzahl erkannter Objekte: {len(objekte)}"
)

print()

for objekt in objekte:
    print(
        f'Objekt {objekt["nummer"]}: '
        f'{objekt["farbe"]}es '
        f'{objekt["form"]}, '
        f'Mittelpunkt=({objekt["mitte_x"]}, '
        f'{objekt["mitte_y"]}), '
        f'Groesse={objekt["breite"]} x '
        f'{objekt["hoehe"]} Pixel, '
        f'Flaeche={objekt["flaeche"]:.1f} Pixel²'
    )


# ------------------------------------------------------------
# Ergebnis im Bild markieren
# ------------------------------------------------------------

for objekt in objekte:
    cv2.drawContours(
        ergebnis,
        [objekt["kontur"]],
        -1,
        (0, 0, 0),
        3
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

    beschriftung = (
        f'{objekt["nummer"]}: '
        f'{objekt["farbe"]} '
        f'{objekt["form"]}'
    )

    cv2.putText(
        ergebnis,
        beschriftung,
        (
            objekt["x"],
            max(objekt["y"] - 8, 20)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        2
    )


# ------------------------------------------------------------
# Bilder anzeigen
# ------------------------------------------------------------

cv2.imshow(
    "Maske - Arbeitsplatte ausgeblendet",
    maske
)

cv2.imshow(
    "Erkannte Formen und Farben",
    ergebnis
)

cv2.waitKey(0)
cv2.destroyAllWindows()