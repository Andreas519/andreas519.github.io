"""Einfacher Hardwaretest für ein PCF8575-Modul am ESP32."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
I2C_ID = 0
I2C_FREQUENZ = 100_000
ADRESSE = 0x27  # Mit A0, A1 und A2 einstellbar: 0x20 bis 0x27


def adressen_anzeigen(i2c):
    adressen = i2c.scan()
    print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])
    return adressen


class PCF8575:
    """Minimale PCF8575-Ansteuerung für den Hardwaretest."""

    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.adresse = adresse
        self.ausgabewert = 0xFFFF
        self.schreiben(self.ausgabewert)

    def schreiben(self, wert):
        self.ausgabewert = wert & 0xFFFF
        daten = bytes((
            self.ausgabewert & 0xFF,
            (self.ausgabewert >> 8) & 0xFF,
        ))
        self.i2c.writeto(self.adresse, daten)

    def lesen(self):
        daten = self.i2c.readfrom(self.adresse, 2)
        return daten[0] | (daten[1] << 8)

    def pin_schreiben(self, pin, wert):
        if not 0 <= pin <= 15:
            raise ValueError("Der Pin muss zwischen 0 und 15 liegen.")

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
print([hex(a) for a in i2c.scan()])
print("PCF8575-Test")
if ADRESSE not in adressen_anzeigen(i2c):
    raise OSError(
        "PCF8575 nicht unter {} gefunden. ADRESSE prüfen.".format(hex(ADRESSE))
    )

pcf = PCF8575(i2c, ADRESSE)
dd
try:
    while True:
        for pin in range(16):
            # Alle Pins HIGH/freigegeben, genau ein Pin LOW.
            wert = 0xFFFF & ~(1 << pin)
            pcf.schreiben(wert)
            print(
                "P{:02d} LOW, gelesener Port: {:016b}".format(
                    pin,
                    pcf.lesen(),
                )
            )
            time.sleep_ms(300)
finally:
    pcf.schreiben(0xFFFF)
    print("Alle Pins HIGH/freigegeben.")