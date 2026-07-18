import cv2
import numpy as np


bild = cv2.resize(cv2.imread("bilder/arbeitsplatte.png"), None, fx=0.15, fy=0.15, interpolation=cv2.INTER_AREA )
hoehe, breite = bild.shape[:2]

# Zunächst ist das gesamte Bild erlaubt
bereichsmaske = np.full(
    (hoehe, breite),
    255,
    dtype=np.uint8
)

# Rechteck ausschließen
# linke obere Ecke: (x1, y1)
# rechte untere Ecke: (x2, y2)
cv2.rectangle(
    bereichsmaske,
    (245, 265),
    (415, 435),
    0,
    -1
)

cv2.imshow("Bereichsmaske", bereichsmaske)

cv2.imshow("Bereichsmaske", bereichsmaske)



cv2.waitKey(0)
cv2.destroyAllWindows()