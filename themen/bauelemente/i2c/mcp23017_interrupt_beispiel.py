"""
mcp23017_interrupt_beispiel.py

Einsatzbeispiel:
- sieben Taster an GPA0 bis GPA6 gegen GND
- interne Pull-ups des MCP23017
- sieben LEDs an GPB0 bis GPB6 über Vorwiderstände
- INTA als Open-Drain-Interrupt an ESP32-GPIO27
- I2C: SDA = GPIO21, SCL = GPIO22

Jeder Tastendruck schaltet die zugehörige LED um.
"""

from machine import Pin, I2C
from time import sleep_ms
from mcp23017 import MCP23017


SDA_PIN = 21
SCL_PIN = 22
INT_PIN = 27
ADRESSE = 0x20

i2c = I2C(
    0,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=100_000,
)

gefundene_adressen = i2c.scan()
print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in gefundene_adressen])

if ADRESSE not in gefundene_adressen:
    raise RuntimeError(
        "MCP23017 nicht unter 0x20 gefunden. "
        "Verdrahtung und Adresspins A0 bis A2 prüfen."
    )

mcp = MCP23017(i2c, address=ADRESSE)

for pin in range(0, 7):
    mcp.pin_mode(pin, MCP23017.INPUT)
    mcp.pullup(pin, True)
    mcp.interrupt_on_change(pin)

for pin in range(8, 15):
    mcp.pin_mode(pin, MCP23017.OUTPUT)
    mcp.write(pin, 0)

mcp.configure_interrupt_outputs(
    mirror=False,
    open_drain=True,
    active_high=False,
)

mcp.clear_interrupt("A")
letzter_tasterzustand = mcp.read_port("A") | 0x80
led_zustand = 0
interrupt_steht_an = False


def interrupt_handler(pin):
    """
    In einer Interruptfunktion keine I2C-Kommunikation durchführen.
    Es wird nur ein Merker gesetzt.
    """
    global interrupt_steht_an
    interrupt_steht_an = True


interrupt_eingang = Pin(INT_PIN, Pin.IN, Pin.PULL_UP)
interrupt_eingang.irq(
    trigger=Pin.IRQ_FALLING,
    handler=interrupt_handler,
)

print("Bereit: Taster an GPA0 bis GPA6 betätigen.")

while True:
    if interrupt_steht_an:
        interrupt_steht_an = False

        capture = mcp.interrupt_capture("A")

        sleep_ms(25)
        aktueller_tasterzustand = mcp.read_port("A") | 0x80

        gedrueckt = letzter_tasterzustand & (~aktueller_tasterzustand & 0xFF)

        for bit in range(7):
            if gedrueckt & (1 << bit):
                led_zustand ^= 1 << bit
                print(
                    "Taster GPA{} gedrückt – LED GPB{} ist jetzt {}.".format(
                        bit,
                        bit,
                        "EIN" if led_zustand & (1 << bit) else "AUS",
                    )
                )

        mcp.write_port("B", led_zustand)
        letzter_tasterzustand = aktueller_tasterzustand

        print(
            "INTCAPA = {:08b}, GPIOA = {:08b}, GPIOB = {:08b}".format(
                capture,
                aktueller_tasterzustand,
                led_zustand,
            )
        )

    sleep_ms(5)