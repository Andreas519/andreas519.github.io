from pathlib import Path
import math

import cv2
import numpy as np


def farbe_bestimmen(farbton):
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


bild = cv2.resize(cv2.imread("bilder/arbeitsplatte.png"), None, fx=0.15, fy=0.15, interpolation=cv2.INTER_AREA )

if bild is None:
    raise FileNotFoundError(f"Bild nicht gefunden: {bildpfad}")

ergebnis = bild.copy()
hsv = cv2.cvtColor(bild, cv2.COLOR_BGR2HSV)

farbmaske = cv2.inRange(
    hsv,
    np.array([0, 80, 50]),
    np.array([179, 255, 255])
)

hoehe, breite = bild.shape[:2]

bereichsmaske = np.full(
    (hoehe, breite),
    255,
    dtype=np.uint8
)

# Beispiel: Dobot-Standplatz ausschließen
cv2.rectangle(
    bereichsmaske,
    (25, 100),
    (375, 270),
    0,
    -1
)

ueberlagerung = bild.copy()
ausgeschlossen = bereichsmaske == 0

ueberlagerung[ausgeschlossen] = [0, 0, 255]
anzeige = cv2.addWeighted(
    bild,
    0.85,
    ueberlagerung,
    0.15,
    0
)



maske = cv2.bitwise_and(
    farbmaske,
    bereichsmaske
)

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

konturen, _ = cv2.findContours(
    maske,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

objekte = []

for kontur in konturen:
    flaeche = cv2.contourArea(kontur)

    if flaeche < 2000:
        continue

    umfang = cv2.arcLength(kontur, True)

    if umfang == 0:
        continue

    naeherung = cv2.approxPolyDP(
        kontur,
        0.02 * umfang,
        True
    )

    ecken = len(naeherung)
    x, y, w, h = cv2.boundingRect(kontur)

    momente = cv2.moments(kontur)

    if momente["m00"] != 0:
        mitte_x = int(momente["m10"] / momente["m00"])
        mitte_y = int(momente["m01"] / momente["m00"])
    else:
        mitte_x = x + w // 2
        mitte_y = y + h // 2

    kreisfoermigkeit = (
        4 * math.pi * flaeche / (umfang * umfang)
    )

    if kreisfoermigkeit > 0.84:
        form = "Kreis"
    elif ecken == 3:
        form = "Dreieck"
    elif ecken == 4:
        verhaeltnis = w / float(h)
        form = (
            "Quadrat"
            if 0.90 <= verhaeltnis <= 1.10
            else "Rechteck"
        )
    else:
        form = "Unbekannt"

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

    farbe = farbe_bestimmen(
        mittlere_hsv_farbe[0]
    )

    objekte.append({
        "kontur": kontur,
        "farbe": farbe,
        "form": form,
        "mitte_x": mitte_x,
        "mitte_y": mitte_y,
        "breite": w,
        "hoehe": h,
        "flaeche": flaeche,
        "umfang": umfang
    })

objekte.sort(
    key=lambda objekt: objekt["mitte_x"]
)

print()
print("AUSWERTUNG DER ARBEITSPLATTE")
print("=" * 92)
print(
    f'{"Nr.":>3} '
    f'{"Farbe":<10} '
    f'{"Form":<12} '
    f'{"Mitte x":>8} '
    f'{"Mitte y":>8} '
    f'{"Breite":>8} '
    f'{"Hoehe":>8} '
    f'{"Flaeche":>10}'
)
print("-" * 92)

for nummer, objekt in enumerate(objekte, start=1):
    print(
        f'{nummer:>3} '
        f'{objekt["farbe"]:<10} '
        f'{objekt["form"]:<12} '
        f'{objekt["mitte_x"]:>8} '
        f'{objekt["mitte_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["flaeche"]:>10.1f}'
    )

print("-" * 92)
print(f"Anzahl erkannter Objekte: {len(objekte)}")

cv2.imshow("Maske", maske)
#cv2.imshow("Original", bild)
cv2.imshow("Original", anzeige)
cv2.waitKey(0)
cv2.destroyAllWindows()