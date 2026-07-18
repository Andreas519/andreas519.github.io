import cv2

bild = cv2.imread("bilder/arbeitsplatte.png")

kleines_bild = cv2.resize(
    bild,
    None,
    fx=0.25,
    fy=0.25,                 # Breite, Höhe
    interpolation=cv2.INTER_AREA
)

cv2.imshow("Original", bild)
cv2.imshow("Verkleinert", kleines_bild)

cv2.waitKey(0)
cv2.destroyAllWindows()