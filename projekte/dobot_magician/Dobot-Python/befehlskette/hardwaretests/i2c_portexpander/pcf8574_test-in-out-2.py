"""Ein-/Ausgangstest für zwei PCF8574-Module an einem I2C-Bus."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
I2C_ID = 0
I2C_FREQUENZ = 100_000

# Die Adressen müssen an den beiden Modulen unterschiedlich eingestellt sein.
ADRESSE_MODUL_1 = 0x20
ADRESSE_MODUL_2 = 0x21

EINGANGSMASKE = 0x0F   # P0 bis P3
AUSGANGSMASKE = 0xF0   # P4 bis P7
AUSGANGSWECHSEL_MS = 500
SCHLEIFENPAUSE_MS = 20


def adressen_anzeigen(i2c):
    adressen = i2c.scan()
    print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])
    return adressen


class PCF8574:
    """Steuert vier Eingänge und vier Ausgänge eines PCF8574."""

    def __init__(self, i2c, adresse, name):
        self.i2c = i2c
        self.adresse = adresse
        self.name = name
        self.ausgabewert = 0xFF
        self.schreiben(self.ausgabewert)

    def schreiben(self, wert):
        # P0 bis P3 bleiben 1 und sind dadurch als Eingänge freigegeben.
        self.ausgabewert = (wert & AUSGANGSMASKE) | EINGANGSMASKE
        self.i2c.writeto(self.adresse, bytes((self.ausgabewert,)))

    def lesen(self):
        return self.i2c.readfrom(self.adresse, 1)[0]

    def eingaenge_lesen(self):
        return self.lesen() & EINGANGSMASKE

    def ausgaenge_schreiben(self, wert):
        self.schreiben((wert << 4) & AUSGANGSMASKE)


i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=I2C_FREQUENZ,
)

print("Test für zwei PCF8574-Module")

if ADRESSE_MODUL_1 == ADRESSE_MODUL_2:
    raise ValueError("Die beiden PCF8574-Module benötigen verschiedene Adressen.")

gefundene_adressen = adressen_anzeigen(i2c)

for adresse in (ADRESSE_MODUL_1, ADRESSE_MODUL_2):
    if adresse not in gefundene_adressen:
        raise OSError(
            "PCF8574 nicht unter {} gefunden. Adressbrücken prüfen.".format(
                hex(adresse)
            )
        )

module = (
    PCF8574(i2c, ADRESSE_MODUL_1, "Modul 1"),
    PCF8574(i2c, ADRESSE_MODUL_2, "Modul 2"),
)

print("Modul 1:", hex(ADRESSE_MODUL_1))
print("Modul 2:", hex(ADRESSE_MODUL_2))
print("Auf beiden Modulen: P0 bis P3 Eingänge, Taster jeweils gegen GND")
print("Auf beiden Modulen: P4 bis P7 Ausgänge")

letzte_eingaenge = [None, None]
ausgangsnummer = 0
naechster_ausgangswechsel = time.ticks_ms()

try:
    while True:
        for index, modul in enumerate(module):
            eingaenge = modul.eingaenge_lesen()

            if eingaenge != letzte_eingaenge[index]:
                print(
                    "{} ({}) - Eingänge P3..P0: {:04b}".format(
                        modul.name,
                        hex(modul.adresse),
                        eingaenge,
                    )
                )
                letzte_eingaenge[index] = eingaenge

        jetzt = time.ticks_ms()
        if time.ticks_diff(jetzt, naechster_ausgangswechsel) >= 0:
            # Modul 1 läuft von P4 nach P7.
            ausgaenge_1 = 0x0F & ~(1 << ausgangsnummer)

            # Modul 2 läuft zur besseren Unterscheidung von P7 nach P4.
            ausgangsnummer_2 = 3 - ausgangsnummer
            ausgaenge_2 = 0x0F & ~(1 << ausgangsnummer_2)

            module[0].ausgaenge_schreiben(ausgaenge_1)
            module[1].ausgaenge_schreiben(ausgaenge_2)

            print(
                "Ausgänge - Modul 1 P{} LOW, Modul 2 P{} LOW".format(
                    ausgangsnummer + 4,
                    ausgangsnummer_2 + 4,
                )
            )

            ausgangsnummer = (ausgangsnummer + 1) % 4
            naechster_ausgangswechsel = time.ticks_add(
                jetzt,
                AUSGANGSWECHSEL_MS,
            )

        time.sleep_ms(SCHLEIFENPAUSE_MS)
finally:
    for modul in module:
        modul.schreiben(0xFF)

    print("Alle Ports beider Module HIGH/freigegeben.")
