"""Einfacher Hardwaretest für einen 74HC595 am ESP32."""

from machine import Pin
import time


# Kabelfarben: VCC - rot, GND - blau
PIN_DATEN = 16          # GPIO16 - DS, Pin 14 am 74HC595 - braun
PIN_SCHIEBETAKT = 17    # GPIO17 - SHCP, Pin 11 am 74HC595 - schwarz
PIN_SPEICHERTAKT = 23   # GPIO23 - STCP, Pin 12 am 74HC595 - weiß


class HC595:
    """Steuert einen oder mehrere hintereinandergeschaltete 74HC595."""

    def __init__(
        self,
        pin_daten,
        pin_schiebetakt,
        pin_speichertakt,
        anzahl=1,
    ):
        if anzahl < 1:
            raise ValueError("Es muss mindestens ein 74HC595 vorhanden sein.")

        self.daten = Pin(pin_daten, Pin.OUT, value=0)
        self.schiebetakt = Pin(pin_schiebetakt, Pin.OUT, value=0)
        self.speichertakt = Pin(pin_speichertakt, Pin.OUT, value=0)
        self.anzahl = anzahl
        self.anzahl_bits = 8 * anzahl
        self.maximalwert = (1 << self.anzahl_bits) - 1

        self.schreiben(0)

    @staticmethod
    def _impuls(pin):
        pin.on()
        pin.off()

    def schreiben(self, wert):
        """Schiebt einen Gesamtwert MSB zuerst in die Register."""

        if not 0 <= wert <= self.maximalwert:
            raise ValueError(
                "Der Wert muss zwischen 0 und {} liegen.".format(
                    self.maximalwert
                )
            )

        self.speichertakt.off()

        for bitnummer in range(self.anzahl_bits - 1, -1, -1):
            self.daten.value((wert >> bitnummer) & 1)
            self._impuls(self.schiebetakt)

        # Erst jetzt erscheinen alle neuen Zustände gleichzeitig an Q0 bis Q7.
        self._impuls(self.speichertakt)

    def alle_aus(self):
        self.schreiben(0)


register = HC595(
    PIN_DATEN,
    PIN_SCHIEBETAKT,
    PIN_SPEICHERTAKT,
)

print("74HC595-Test")
print(
    "Daten GPIO {}, Schiebetakt GPIO {}, Speichertakt GPIO {}".format(
        PIN_DATEN,
        PIN_SCHIEBETAKT,
        PIN_SPEICHERTAKT,
    )
)

try:
    while True:
        print("Ein HIGH-Bit läuft von Q0 bis Q7.")
        for bitnummer in range(register.anzahl_bits):
            register.schreiben(1 << bitnummer)
            print("Ausgänge: {:08b}".format(1 << bitnummer))
            time.sleep_ms(300)

        print("Ein LOW-Bit läuft von Q0 bis Q7.")
        for bitnummer in range(register.anzahl_bits):
            wert = register.maximalwert & ~(1 << bitnummer)
            register.schreiben(wert)
            print("Ausgänge: {:08b}".format(wert))
            time.sleep_ms(300)
finally:
    register.alle_aus()
    print("Alle Ausgänge ausgeschaltet.")
