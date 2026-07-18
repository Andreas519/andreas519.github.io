from pathlib import Path
import math

import cv2
import numpy as np


# ------------------------------------------------------------
# Farbe anhand des HSV-Farbtons bestimmen
# ------------------------------------------------------------

def farbe_bestimmen(farbton):
    """
    Bestimmt den Farbnamen anhand des mittleren HSV-Farbtons.

    OpenCV verwendet für den Farbton Werte von 0 bis 179.
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
        return "Unbekannt", 0, 0

    # Kontur auf wenige Eckpunkte vereinfachen
    naeherung = cv2.approxPolyDP(
        kontur,
        0.02 * umfang,
        True
    )

    anzahl_ecken = len(naeherung)

    x, y, breite, hoehe = cv2.boundingRect(kontur)

    # Kreisförmigkeit:
    # Ein idealer Kreis hat den Wert 1.
    kreisfoermigkeit = (
        4 * math.pi * flaeche / (umfang * umfang)
    )

    # Kreis zuerst prüfen
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
#bildpfad = ordner / "Dobot-Arbeitsplatte.png"
bildpfad = ordner / "testbild-01.png"

bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(
        f"Das Bild wurde nicht gefunden:\n{bildpfad}"
    )

ergebnis = bild.copy()


# ------------------------------------------------------------
# Farbige Flächen auswählen
# ------------------------------------------------------------

# BGR-Bild in den HSV-Farbraum umwandeln
hsv = cv2.cvtColor(bild, cv2.COLOR_BGR2HSV)

# Auswahl deutlich gesättigter Farben:
# - weißer Hintergrund wird ausgeschlossen
# - schwarze Löcher und Linien werden ausgeschlossen
maske = cv2.inRange(
    hsv,
    np.array([0, 80, 60]),
    np.array([179, 255, 255])
)

# Kleine Störungen entfernen
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

    # Kleine rote Striche des Arbeitsbereiches und andere
    # kleine Bildbestandteile ignorieren
    if flaeche < 2000:
        continue

    umfang = cv2.arcLength(kontur, True)

    x, y, breite, hoehe = cv2.boundingRect(kontur)

    # Mittelpunkt über die Bildmomente bestimmen
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

    # --------------------------------------------------------
    # Form erkennen
    # --------------------------------------------------------

    form, ecken, kreisfoermigkeit = form_bestimmen(
        kontur
    )

    # --------------------------------------------------------
    # Mittlere Farbe innerhalb der Kontur bestimmen
    # --------------------------------------------------------

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

    mittlere_hsv_farbe = cv2.mean(
        hsv,
        mask=objektmaske
    )

    farbton = mittlere_hsv_farbe[0]
    farbe = farbe_bestimmen(farbton)

    objekt = {
        "kontur": kontur,
        "form": form,
        "farbe": farbe,
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
# Objekte sortieren
# ------------------------------------------------------------

# Sortierung von links nach rechts
objekte.sort(
    key=lambda objekt: objekt["mitte_x"]
)


# ------------------------------------------------------------
# Ergebnisbild erzeugen
# ------------------------------------------------------------

for nummer, objekt in enumerate(objekte, start=1):
    objekt["nummer"] = nummer

    # Kontur zeichnen
    cv2.drawContours(
        ergebnis,
        [objekt["kontur"]],
        -1,
        (0, 0, 0),
        3
    )

    # Begrenzungsrechteck zeichnen
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

    # Mittelpunkt markieren
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
        f'{nummer}: {objekt["farbe"]} '
        f'{objekt["form"]}'
    )

    cv2.putText(
        ergebnis,
        beschriftung,
        (
            objekt["x"],
            max(objekt["y"] - 10, 20)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        2
    )


# ------------------------------------------------------------
# Liste in der Befehlszeile ausgeben
# ------------------------------------------------------------

print()
print("Erkannte Objekte")
print("-" * 110)

print(
    f'{"Nr.":>3} '
    f'{"Farbe":<10} '
    f'{"Form":<12} '
    f'{"Mitte x":>8} '
    f'{"Mitte y":>8} '
    f'{"Breite":>8} '
    f'{"Hoehe":>8} '
    f'{"Flaeche":>10} '
    f'{"Umfang":>10}'
)

print("-" * 110)

for objekt in objekte:
    print(
        f'{objekt["nummer"]:>3} '
        f'{objekt["farbe"]:<10} '
        f'{objekt["form"]:<12} '
        f'{objekt["mitte_x"]:>8} '
        f'{objekt["mitte_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["flaeche"]:>10.1f} '
        f'{objekt["umfang"]:>10.1f}'
    )

print("-" * 110)
print(f"Anzahl erkannter Objekte: {len(objekte)}")


# ------------------------------------------------------------
# Ergebnis speichern und anzeigen
# ------------------------------------------------------------

ausgabepfad = (
    ordner / "Dobot-Arbeitsplatte-ausgewertet.png"
)

cv2.imwrite(
    str(ausgabepfad),
    ergebnis
)

cv2.imshow("Farbmaske", maske)
cv2.imshow("Formen und Farben", ergebnis)

print()
print(f"Ergebnis gespeichert unter:")
print(ausgabepfad)
print()
print("Zum Beenden eine Taste druecken.")

cv2.waitKey(0)
cv2.destroyAllWindows()