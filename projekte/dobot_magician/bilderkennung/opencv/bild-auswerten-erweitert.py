from pathlib import Path
import math
import cv2


# --------------------------------------------------
# Bild laden
# --------------------------------------------------

ordner = Path(__file__).resolve().parent
bildpfad = ordner / "testbild-01.png"

bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(
        f"Das Bild wurde nicht gefunden: {bildpfad}"
    )

ergebnis = bild.copy()


# --------------------------------------------------
# Farbige Flächen auswählen
# --------------------------------------------------

# Umwandlung in den HSV-Farbraum
hsv = cv2.cvtColor(bild, cv2.COLOR_BGR2HSV)

# Nur deutlich farbige Bereiche auswählen.
# Der weiße Hintergrund und die schwarzen Umrandungen
# haben eine geringe Farbsättigung und werden ausgeblendet.
maske = cv2.inRange(
    hsv,
    (0, 80, 40),
    (179, 255, 255)
)

# Kleine Lücken und Störungen beseitigen
kernel = cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE,
    (5, 5)
)

maske = cv2.morphologyEx(
    maske,
    cv2.MORPH_CLOSE,
    kernel,
    iterations=2
)

maske = cv2.morphologyEx(
    maske,
    cv2.MORPH_OPEN,
    kernel,
    iterations=1
)


# --------------------------------------------------
# Konturen suchen
# --------------------------------------------------

konturen, _ = cv2.findContours(
    maske,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

objekte = []


# --------------------------------------------------
# Konturen auswerten
# --------------------------------------------------

for kontur in konturen:

    flaeche = cv2.contourArea(kontur)

    # Kleine Störungen ignorieren
    if flaeche < 2000:
        continue

    umfang = cv2.arcLength(kontur, True)

    if umfang == 0:
        continue

    # Kontur vereinfachen
    naeherung = cv2.approxPolyDP(
        kontur,
        0.02 * umfang,
        True
    )

    anzahl_ecken = len(naeherung)

    # Begrenzungsrechteck
    x, y, breite, hoehe = cv2.boundingRect(kontur)

    # Mittelpunkt über Bildmomente
    momente = cv2.moments(kontur)

    if momente["m00"] != 0:
        mitte_x = int(momente["m10"] / momente["m00"])
        mitte_y = int(momente["m01"] / momente["m00"])
    else:
        mitte_x = x + breite // 2
        mitte_y = y + hoehe // 2

    # Kreisförmigkeit:
    # Kreis ungefähr 1,0
    # Quadrat ungefähr 0,79
    # Rechteck meist kleiner
    kreisfoermigkeit = (
        4 * math.pi * flaeche / (umfang * umfang)
    )

    # --------------------------------------------------
    # Form bestimmen
    # --------------------------------------------------

    # Kreis zuerst prüfen
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
        form = f"unbekannt ({anzahl_ecken} Ecken)"

    objekt = {
        "kontur": kontur,
        "form": form,
        "x": x,
        "y": y,
        "mitte_x": mitte_x,
        "mitte_y": mitte_y,
        "breite": breite,
        "hoehe": hoehe,
        "laenge": max(breite, hoehe),
        "flaeche": flaeche,
        "umfang": umfang,
        "ecken": anzahl_ecken,
        "kreisfoermigkeit": kreisfoermigkeit,
    }

    objekte.append(objekt)


# --------------------------------------------------
# Objekte sortieren
# --------------------------------------------------

# Zuerst von oben nach unten,
# innerhalb einer Zeile von links nach rechts
objekte.sort(
    key=lambda objekt: (
        objekt["mitte_y"],
        objekt["mitte_x"]
    )
)


# --------------------------------------------------
# Ergebnisbild beschriften
# --------------------------------------------------

for nummer, objekt in enumerate(objekte, start=1):

    objekt["nummer"] = nummer

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
        6,
        (0, 0, 0),
        -1
    )

    beschriftung = (
        f'{nummer}: {objekt["form"]}'
    )

    cv2.putText(
        ergebnis,
        beschriftung,
        (
            objekt["x"],
            max(objekt["y"] - 10, 25)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2
    )


# --------------------------------------------------
# Tabelle ausgeben
# --------------------------------------------------

print()
print("Erkannte Objekte")
print("-" * 115)

print(
    f'{"Nr.":>3} '
    f'{"Form":<12} '
    f'{"x":>5} '
    f'{"y":>5} '
    f'{"Mitte x":>8} '
    f'{"Mitte y":>8} '
    f'{"Breite":>8} '
    f'{"Hoehe":>8} '
    f'{"Laenge":>8} '
    f'{"Flaeche":>10} '
    f'{"Umfang":>10}'
)

print("-" * 115)

for objekt in objekte:
    print(
        f'{objekt["nummer"]:>3} '
        f'{objekt["form"]:<12} '
        f'{objekt["x"]:>5} '
        f'{objekt["y"]:>5} '
        f'{objekt["mitte_x"]:>8} '
        f'{objekt["mitte_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["laenge"]:>8} '
        f'{objekt["flaeche"]:>10.1f} '
        f'{objekt["umfang"]:>10.1f}'
    )

print("-" * 115)
print(f"Anzahl erkannter Objekte: {len(objekte)}")


# --------------------------------------------------
# Ergebnis speichern und anzeigen
# --------------------------------------------------

ausgabepfad = ordner / "testbild_ausgewertet.png"

cv2.imwrite(
    str(ausgabepfad),
    ergebnis
)

cv2.imshow("Farbmaske", maske)
cv2.imshow("Erkannte Objekte", ergebnis)

print()
print(f"Ergebnis gespeichert: {ausgabepfad}")
print("Zum Beenden eine Taste drücken.")

cv2.waitKey(0)
cv2.destroyAllWindows()