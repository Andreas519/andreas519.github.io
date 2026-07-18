from pathlib import Path
import cv2

ordner = Path(__file__).resolve().parent
bildpfad = ordner / "testbild-01.png"

bild = cv2.imread(str(bildpfad))

if bild is None:
    raise FileNotFoundError(f"Bild nicht gefunden: {bildpfad}")

print(type(bild))
print()
print(bild[11])

cv2.imshow("Testbild", bild)
cv2.waitKey(0)
cv2.destroyAllWindows()