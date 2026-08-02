from pathlib import Path
import cv2

ordner = Path(__file__).resolve().parent
#bildpfad = ordner / "bilder/testbild-01.png"
bildpfad = ordner / "bilder/Dobot-Arbeitsplatte.png"    # .SVG-Dateien werden nicht  erkannt.

bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(f"Bild nicht gefunden: {bildpfad}")

cv2.imshow("Testbild", bild)
cv2.waitKey(0)
cv2.destroyAllWindows()