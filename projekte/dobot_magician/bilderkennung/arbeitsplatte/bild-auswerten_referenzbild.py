import cv2
import numpy as np

hintergrund = cv2.imread(
    "arbeitsplatte_leer-663x662.png"
)

bild = cv2.imread(
    "arbeitsplatte_mit_objekten-663x662.png"
)

if hintergrund is None or bild is None:
    raise FileNotFoundError(
        "Ein Bild konnte nicht geladen werden."
    )

if hintergrund.shape != bild.shape:
    raise ValueError(
        "Beide Bilder müssen gleich groß sein."
    )

# Unterschied zwischen leerer und belegter Platte
differenz = cv2.absdiff(
    bild,
    hintergrund
)

# Differenz in Graustufen umwandeln
grau = cv2.cvtColor(
    differenz,
    cv2.COLOR_BGR2GRAY
)

# Nur deutliche Unterschiede übernehmen
_, maske = cv2.threshold(
    grau,
    30,
    255,
    cv2.THRESH_BINARY
)

kernel = np.ones((5, 5), dtype=np.uint8)

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

vordergrund = cv2.bitwise_and(
    bild,
    bild,
    mask=maske
)

cv2.imshow("Unterschied", differenz)
cv2.imshow("Objektmaske", maske)
cv2.imshow("Erkannte Objekte", vordergrund)

cv2.waitKey(0)
cv2.destroyAllWindows()