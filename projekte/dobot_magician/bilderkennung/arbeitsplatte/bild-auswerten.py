from pathlib import Path
import math
import cv2


ordner = Path(__file__).resolve().parent
bildpfad = ordner / "arbeitsplatte_leer-663x662.png"

bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(f"Bild nicht gefunden: {bildpfad}")

ergebnis = bild.copy()

# Graustufenbild erzeugen
grau = cv2.cvtColor(bild, cv2.COLOR_BGR2GRAY)

# Alles, was nicht nahezu weiß ist, wird zum Objekt
_, maske = cv2.threshold(
    grau,
    245,
    255,
    cv2.THRESH_BINARY_INV
)

# Äußere Umrisse bestimmen
konturen, _ = cv2.findContours(
    maske,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

objekte = []

for kontur in konturen:
    flaeche = cv2.contourArea(kontur)

    # Kleine Bildstörungen ignorieren
    if flaeche < 1000:
        continue

    umfang = cv2.arcLength(kontur, True)

    # Kontur vereinfachen und Eckenzahl ermitteln
    naeherung = cv2.approxPolyDP(
        kontur,
        0.02 * umfang,
        True
    )

    anzahl_ecken = len(naeherung)

    # Nicht gedrehtes Begrenzungsrechteck
    x, y, breite, hoehe = cv2.boundingRect(kontur)

    # Mittelpunkt über Bildmomente bestimmen
    momente = cv2.moments(kontur)

    if momente["m00"] != 0:
        mittelpunkt_x = int(momente["m10"] / momente["m00"])
        mittelpunkt_y = int(momente["m01"] / momente["m00"])
    else:
        mittelpunkt_x = x + breite // 2
        mittelpunkt_y = y + hoehe // 2

    # Kreisähnlichkeit
    if umfang > 0:
        kreisfoermigkeit = (
            4 * math.pi * flaeche / (umfang * umfang)
        )
    else:
        kreisfoermigkeit = 0

    # Form bestimmen
    if anzahl_ecken == 3:
        form = "Dreieck"

    elif anzahl_ecken == 4:
        seitenverhaeltnis = breite / float(hoehe)

        if 0.90 <= seitenverhaeltnis <= 1.10:
            form = "Quadrat"
        else:
            form = "Rechteck"

    elif kreisfoermigkeit > 0.80:
        form = "Kreis"

    else:
        form = "unbekannte Form"

    objekt = {
        "form": form,
        "x": x,
        "y": y,
        "mittelpunkt_x": mittelpunkt_x,
        "mittelpunkt_y": mittelpunkt_y,
        "breite": breite,
        "hoehe": hoehe,
        "laenge": max(breite, hoehe),
        "flaeche": round(flaeche, 1),
        "umfang": round(umfang, 1),
        "ecken": anzahl_ecken,
    }

    objekte.append(objekt)

# Objekte von oben nach unten und links nach rechts sortieren
objekte.sort(
    key=lambda objekt: (
        objekt["mittelpunkt_y"],
        objekt["mittelpunkt_x"]
    )
)

# Nummern nach der Sortierung vergeben
for nummer, objekt in enumerate(objekte, start=1):
    objekt["nummer"] = nummer

    beschriftung = f'{nummer}: {objekt["form"]}'

    cv2.drawContours(
        ergebnis,
        [konturen[0]],
        -1,
        (0, 0, 0),
        2
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
            objekt["mittelpunkt_x"],
            objekt["mittelpunkt_y"]
        ),
        6,
        (0, 0, 0),
        -1
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

# Tabelle ausgeben
print()
print("Erkannte Objekte:")
print("-" * 100)
print(
    f'{"Nr.":>3} '
    f'{"Form":<12} '
    f'{"x":>5} {"y":>5} '
    f'{"Mitte x":>8} {"Mitte y":>8} '
    f'{"Breite":>8} {"Höhe":>8} '
    f'{"Fläche":>10} {"Umfang":>10}'
)
print("-" * 100)

for objekt in objekte:
    print(
        f'{objekt["nummer"]:>3} '
        f'{objekt["form"]:<12} '
        f'{objekt["x"]:>5} '
        f'{objekt["y"]:>5} '
        f'{objekt["mittelpunkt_x"]:>8} '
        f'{objekt["mittelpunkt_y"]:>8} '
        f'{objekt["breite"]:>8} '
        f'{objekt["hoehe"]:>8} '
        f'{objekt["flaeche"]:>10.1f} '
        f'{objekt["umfang"]:>10.1f}'
    )

print("-" * 100)
print(f"Anzahl erkannter Objekte: {len(objekte)}")

cv2.imshow("Maske", maske)
cv2.imshow("Auswertung", ergebnis)

cv2.imwrite(
    str(ordner / "testbild_ausgewertet.png"),
    ergebnis
)

cv2.waitKey(0)
cv2.destroyAllWindows()