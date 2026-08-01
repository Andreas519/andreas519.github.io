"""Einfacher Hardwaretest für ein PCF8574-Modul am ESP32."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
I2C_ID = 0
I2C_FREQUENZ = 100_000
ADRESSE = 0x20  # PCF8574 häufig 0x20 bis 0x27; PCF8574A: 0x38 bis 0x3F


def adressen_anzeigen(i2c):
    adressen = i2c.scan()
    print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])
    return adressen


class PCF8574:
    """Minimale PCF8574-Ansteuerung für den Hardwaretest."""

    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.adresse = adresse
        self.ausgabewert = 0xFF
        self.schreiben(self.ausgabewert)

    def schreiben(self, wert):
        self.ausgabewert = wert & 0xFF
        self.i2c.writeto(self.adresse, bytes((self.ausgabewert,)))

    def lesen(self):
        return self.i2c.readfrom(self.adresse, 1)[0]

    def pin_schreiben(self, pin, wert):
        if not 0 <= pin <= 7:
            raise ValueError("Der Pin muss zwischen 0 und 7 liegen.")

        if wert:
            self.schreiben(self.ausgabewert | (1 << pin))
        else:
            self.schreiben(self.ausgabewert & ~(1 << pin))


i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=I2C_FREQUENZ,
)

print("PCF8574-Test")
if ADRESSE not in adressen_anzeigen(i2c):
    raise OSError(
        "PCF8574 nicht unter {} gefunden. ADRESSE prüfen.".format(hex(ADRESSE))
    )

pcf = PCF8574(i2c, ADRESSE)

try:
    while True:
        for pin in range(8):
            # Alle Pins HIGH/freigegeben, genau ein Pin LOW.
            pcf.schreiben(0xFF & ~(1 << pin))
            print(
                "P{} LOW, gelesener Port: {:08b}".format(
                    pin,
                    pcf.lesen(),
                )
            )
            time.sleep_ms(400)
finally:
    pcf.schreiben(0xFF)
    print("Alle Pins HIGH/freigegeben.")
