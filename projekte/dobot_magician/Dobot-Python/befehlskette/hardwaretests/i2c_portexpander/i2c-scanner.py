from machine import Pin, I2C
import time

# Diesen Scanner vor jedem modulspezifischen I2C-Test zuerst ausführen.
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün

i2c = I2C(
    0,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=100_000,
)

while True:
    print([hex(adresse) for adresse in i2c.scan()], end=", ")
    time.sleep(1)
# Bei A0 = A1 = A2 = GND muss 0x20 erscheinen.
