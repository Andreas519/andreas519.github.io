"""MCP23017-Test mit zwei interruptfähigen Eingängen am ESP32."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
INT_PIN = 16  # GPIO16 - INTB; Kabelfarbe noch festzulegen

I2C_ID = 0
I2C_FREQUENZ = 100_000
ADRESSE = 0x20

EINGANG_GPB0 = 0x01
EINGANG_GPB1 = 0x02
INTERRUPT_EINGAENGE = EINGANG_GPB0 | EINGANG_GPB1


class MCP23017:
    """Minimale MCP23017-Ansteuerung für zwei Interrupt-Eingänge."""

    IODIRB = 0x01
    GPINTENB = 0x05
    DEFVALB = 0x07
    INTCONB = 0x09
    IOCON = 0x0A
    GPPUB = 0x0D
    INTFB = 0x0F
    INTCAPB = 0x11
    GPIOB = 0x13

    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.adresse = adresse

    def register_schreiben(self, register, wert):
        self.i2c.writeto_mem(
            self.adresse,
            register,
            bytes((wert & 0xFF,)),
        )

    def register_lesen(self, register):
        return self.i2c.readfrom_mem(self.adresse, register, 1)[0]

    def interrupt_eingaenge_einrichten(self):
        # Port B bleibt vollständig Eingang; Interrupts erhalten nur GPB0/GPB1.
        self.register_schreiben(self.IODIRB, 0xFF)

        # Interne Pull-ups für GPB0 und GPB1 einschalten.
        self.register_schreiben(self.GPPUB, INTERRUPT_EINGAENGE)

        # INTB als aktives LOW-Open-Drain-Signal ausgeben.
        self.register_schreiben(self.IOCON, 0x04)

        # INTCONB = 0: Interrupt bei Änderung gegenüber dem vorherigen Wert.
        self.register_schreiben(self.INTCONB, 0x00)
        self.register_schreiben(self.DEFVALB, 0x00)

        # Interrupt nur für GPB0 und GPB1 aktivieren.
        self.register_schreiben(self.GPINTENB, INTERRUPT_EINGAENGE)

        # Ein Lesen von GPIOB löscht einen eventuell noch anstehenden Interrupt.
        self.register_lesen(self.GPIOB)

    def interrupt_auswerten(self):
        ausloeser = self.register_lesen(self.INTFB)

        # INTCAPB enthält den Portzustand im Moment der Auslösung.
        # Das Lesen löscht zugleich den Interrupt.
        eingefangener_wert = self.register_lesen(self.INTCAPB)
        return ausloeser, eingefangener_wert


i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=I2C_FREQUENZ,
)

print("MCP23017-Test mit zwei Interrupt-Eingängen")
adressen = i2c.scan()
print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])

if ADRESSE not in adressen:
    raise OSError(
        "MCP23017 nicht unter {} gefunden. ADRESSE prüfen.".format(hex(ADRESSE))
    )

mcp = MCP23017(i2c, ADRESSE)
mcp.interrupt_eingaenge_einrichten()

interrupt_ausgeloest = False


def intb_irq_handler(pin):
    """Setzt im Hardware-Interrupt nur ein Flag."""

    global interrupt_ausgeloest
    interrupt_ausgeloest = True


intb = Pin(INT_PIN, Pin.IN, Pin.PULL_UP)
intb.irq(
    trigger=Pin.IRQ_FALLING,
    handler=intb_irq_handler,
)

print("GPB0 und GPB1: Eingänge mit Pull-up, Taster jeweils gegen GND")
print("INTB: Open Drain, verbunden mit GPIO{}".format(INT_PIN))
print("Warte auf Interrupts ...")

try:
    while True:
        if interrupt_ausgeloest:
            interrupt_ausgeloest = False
            ausloeser, wert = mcp.interrupt_auswerten()

            print(
                "Interrupt: INTFB={:08b}, GPB1={}, GPB0={}".format(
                    ausloeser,
                    1 if wert & EINGANG_GPB1 else 0,
                    1 if wert & EINGANG_GPB0 else 0,
                )
            )

        time.sleep_ms(5)
finally:
    intb.irq(handler=None)
    mcp.register_schreiben(mcp.GPINTENB, 0x00)
    print("Interrupts ausgeschaltet.")
