from pathlib import Path
import cv2

# Ordner des Python-Programms
ordner = Path(__file__).resolve().parent
bildpfad = ordner / "testbild-01.png"

# Bild laden
bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(f"Bild nicht gefunden: {bildpfad}")

# Arbeitskopie für die Beschriftungen
ergebnis = bild.copy()

# Graustufenbild erzeugen
grau = cv2.cvtColor(bild, cv2.COLOR_BGR2GRAY)

# Leicht glätten
grau = cv2.GaussianBlur(grau, (5, 5), 0)

# Kanten erkennen
kanten = cv2.Canny(grau, 50, 150)

# Äußere Konturen suchen
konturen, _ = cv2.findContours(
    kanten,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

for kontur in konturen:
    flaeche = cv2.contourArea(kontur)

    # Kleine Störungen ignorieren
    if flaeche < 1000:
        continue

    # Kontur vereinfachen
    umfang = cv2.arcLength(kontur, True)
    ecken = cv2.approxPolyDP(kontur, 0.03 * umfang, True)

    # Begrenzungsrechteck
    x, y, breite, hoehe = cv2.boundingRect(ecken)

    anzahl_ecken = len(ecken)

    if anzahl_ecken == 3:
        form = "Dreieck"

    elif anzahl_ecken == 4:
        seitenverhaeltnis = breite / float(hoehe)

        if 0.90 <= seitenverhaeltnis <= 1.10:
            form = "Quadrat"
        else:
            form = "Rechteck"

    elif anzahl_ecken >= 8:
        form = "Kreis"

    else:
        form = f"Form mit {anzahl_ecken} Ecken"

    # Kontur einzeichnen
    cv2.drawContours(ergebnis, [ecken], -1, (0, 0, 0), 3)

    # Beschriftung oberhalb der Form
    cv2.putText(
        ergebnis,
        form,
        (x, max(y - 10, 25)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        2
    )

    print(
        f"{form}: Position=({x}, {y}), "
        f"Groesse={breite} x {hoehe}, "
        f"Flaeche={flaeche:.0f}"
    )

# Ergebnis speichern
ausgabepfad = ordner / "testbild_ausgewertet.png"
cv2.imwrite(str(ausgabepfad), ergebnis)

# Bilder anzeigen
cv2.imshow("Original", bild)
cv2.imshow("Erkannte Kanten", kanten)
cv2.imshow("Erkannte Formen", ergebnis)

print()
print(f"Das Ergebnis wurde gespeichert unter:")
print(ausgabepfad)
print("Zum Beenden eine beliebige Taste druecken.")

cv2.waitKey(0)
cv2.destroyAllWindows()