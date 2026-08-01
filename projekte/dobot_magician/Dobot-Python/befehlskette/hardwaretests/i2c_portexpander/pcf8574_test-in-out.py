"""PCF8574-Test mit vier Eingängen und vier Ausgängen am ESP32."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
I2C_ID = 0
I2C_FREQUENZ = 100_000
ADRESSE = 0x20  # PCF8574 häufig 0x20 bis 0x27; PCF8574A: 0x38 bis 0x3F

EINGANGSMASKE = 0x0F   # P0 bis P3
AUSGANGSMASKE = 0xF0   # P4 bis P7
AUSGANGSWECHSEL_MS = 500
SCHLEIFENPAUSE_MS = 20


def adressen_anzeigen(i2c):
    adressen = i2c.scan()
    print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])
    return adressen


class PCF8574:
    """Minimale PCF8574-Ansteuerung für vier Eingänge und vier Ausgänge."""

    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.adresse = adresse
        self.ausgabewert = 0xFF
        self.schreiben(self.ausgabewert)

    def schreiben(self, wert):
        # P0 bis P3 müssen 1 bleiben, damit sie als Eingänge arbeiten.
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

print("PCF8574 Ein-/Ausgangstest")
if ADRESSE not in adressen_anzeigen(i2c):
    raise OSError(
        "PCF8574 nicht unter {} gefunden. ADRESSE prüfen.".format(hex(ADRESSE))
    )

pcf = PCF8574(i2c, ADRESSE)

print("P0 bis P3: Eingänge, Taster jeweils gegen GND")
print("P4 bis P7: Ausgänge, ein LOW-Signal läuft durch")

letzte_eingaenge = None
ausgangsnummer = 0
naechster_ausgangswechsel = time.ticks_ms()

try:
    while True:
        eingaenge = pcf.eingaenge_lesen()

        if eingaenge != letzte_eingaenge:
            print("Eingänge P3..P0: {:04b}".format(eingaenge))
            letzte_eingaenge = eingaenge

        jetzt = time.ticks_ms()
        if time.ticks_diff(jetzt, naechster_ausgangswechsel) >= 0:
            # Alle vier Ausgänge HIGH, genau einen Ausgang auf LOW setzen.
            ausgaenge = 0x0F & ~(1 << ausgangsnummer)
            pcf.ausgaenge_schreiben(ausgaenge)
            print(
                "Ausgänge P7..P4: {:04b} - P{} LOW".format(
                    ausgaenge,
                    ausgangsnummer + 4,
                )
            )

            ausgangsnummer = (ausgangsnummer + 1) % 4
            naechster_ausgangswechsel = time.ticks_add(
                jetzt,
                AUSGANGSWECHSEL_MS,
            )

        time.sleep_ms(SCHLEIFENPAUSE_MS)
finally:
    # Eingänge freigeben und alle Ausgänge auf HIGH setzen.
    pcf.schreiben(0xFF)
    print("Alle Ports HIGH/freigegeben.")
