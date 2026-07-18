import cv2
import numpy as np

bild = cv2.resize(cv2.imread("bilder/arbeitsplatte.png"), None, fx=0.15, fy=0.15, interpolation=cv2.INTER_AREA )

if bild is None:
    raise FileNotFoundError(
        "Das Bild konnte nicht geladen werden."
    )

hoehe, breite = bild.shape[:2]

print("Höhe: ",hoehe, "Breite: ",breite)

# Gesamtes Bild zunächst freigeben
bereichsmaske = np.full((hoehe, breite), 0, dtype=np.uint8)

# Dobot-Standplatz ausschließen
cv2.rectangle( bereichsmaske, ( 10, 10), (385, 150), 255, -1 )
cv2.rectangle( bereichsmaske, ( 10, 10), (100, 270), 255, -1 )
cv2.rectangle( bereichsmaske, (385, 10), (285, 270), 255, -1 )

# Nur freigegebenen Bildbereich erzeugen
bild_mit_maske = cv2.bitwise_and(
    bild,
    bild,
    mask=bereichsmaske
)

# Ausgeschlossene Bereiche rot überlagern
ueberlagerung = bild.copy()
ausgeschlossen = bereichsmaske == 0

ueberlagerung[ausgeschlossen] = [0, 0, 255]

anzeige = cv2.addWeighted(bild, 0.75, ueberlagerung, 0.15, 0)

cv2.imshow("Originalbild", bild)
cv2.imshow("Bereichsmaske", bereichsmaske)
cv2.imshow("Nur erlaubter Bereich", bild_mit_maske)
cv2.imshow("Maske im Bild markiert", anzeige)

cv2.waitKey(0)
cv2.destroyAllWindows()