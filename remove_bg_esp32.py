from PIL import Image
import math

path = r'themen\esp32\bilder\esp32-30-vs-38-pin.png'
img = Image.open(path).convert('RGBA')
w, h = img.size
bg = img.getpixel((0, 0))

# Define similarity threshold for background color

def close(c1, c2, t=60):
    return math.dist(c1[:3], c2[:3]) < t

new = Image.new('RGBA', (w, h))
pixels = img.load()
newpix = new.load()
for y in range(h):
    for x in range(w):
        rgba = pixels[x, y]
        newpix[x, y] = (255, 255, 255, 0) if close(rgba, bg) else rgba

new.save(r'themen\esp32\bilder\esp32-30-vs-38-pin-neu.png')
print('saved esp32-30-vs-38-pin-neu.png')
