"""Hardwaretest für ein PCA9685-PWM-Modul am ESP32."""

from machine import I2C, Pin
import time


# Kabelfarben: VCC - rot, GND - blau
SDA_PIN = 21  # GPIO21 - SDA - gelb
SCL_PIN = 22  # GPIO22 - SCL - grün
I2C_ID = 0
I2C_FREQUENZ = 100_000
ADRESSE = 0x40
PWM_FREQUENZ = 100
TESTKANAL = 0


class PCA9685:
    """Minimale PCA9685-Ansteuerung für PWM-Werte von 0 bis 4095."""

    MODE1 = 0x00
    MODE2 = 0x01
    LED0_ON_L = 0x06
    PRESCALE = 0xFE

    def __init__(self, i2c, adresse):
        self.i2c = i2c
        self.adresse = adresse
        # Auto-Increment aktivieren, Ausgänge als normale Totem-Pole-Ausgänge.
        self._register_schreiben(self.MODE1, 0x20)
        self._register_schreiben(self.MODE2, 0x04)
        time.sleep_ms(1)

    def _register_schreiben(self, register, wert):
        self.i2c.writeto_mem(
            self.adresse,
            register,
            bytes((wert & 0xFF,)),
        )

    def _register_lesen(self, register):
        return self.i2c.readfrom_mem(self.adresse, register, 1)[0]

    def frequenz_setzen(self, frequenz):
        if not 24 <= frequenz <= 1526:
            raise ValueError("Frequenz muss zwischen 24 und 1526 Hz liegen.")

        prescale = round(25_000_000 / (4096 * frequenz)) - 1
        alter_mode1 = self._register_lesen(self.MODE1)

        # Für das Schreiben von PRESCALE muss der Oszillator schlafen.
        self._register_schreiben(self.MODE1, (alter_mode1 & 0x7F) | 0x10)
        self._register_schreiben(self.PRESCALE, prescale)
        self._register_schreiben(self.MODE1, alter_mode1)
        time.sleep_ms(1)
        self._register_schreiben(self.MODE1, alter_mode1 | 0xA0)

    def kanal_setzen(self, kanal, wert):
        if not 0 <= kanal <= 15:
            raise ValueError("Der Kanal muss zwischen 0 und 15 liegen.")
        if not 0 <= wert <= 4095:
            raise ValueError("Der PWM-Wert muss zwischen 0 und 4095 liegen.")

        register = self.LED0_ON_L + 4 * kanal
        daten = bytes((
            0,
            0,
            wert & 0xFF,
            (wert >> 8) & 0x0F,
        ))
        self.i2c.writeto_mem(self.adresse, register, daten)

    def kanal_aus(self, kanal):
        if not 0 <= kanal <= 15:
            raise ValueError("Der Kanal muss zwischen 0 und 15 liegen.")

        register = self.LED0_ON_L + 4 * kanal
        # FULL-OFF-Bit im LEDn_OFF_H-Register setzen.
        self.i2c.writeto_mem(
            self.adresse,
            register,
            bytes((0, 0, 0, 0x10)),
        )


i2c = I2C(
    I2C_ID,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=I2C_FREQUENZ,
)

adressen = i2c.scan()
print("PCA9685-Test")
print("Gefundene I2C-Adressen:", [hex(adresse) for adresse in adressen])

if ADRESSE not in adressen:
    raise OSError(
        "PCA9685 nicht unter {} gefunden. ADRESSE prüfen.".format(hex(ADRESSE))
    )

pwm = PCA9685(i2c, ADRESSE)
pwm.frequenz_setzen(PWM_FREQUENZ)

try:
    while True:
        for wert in range(0, 4096, 128):
            pwm.kanal_setzen(TESTKANAL, wert)
            print("Kanal {}: {:4d} / 4095".format(TESTKANAL, wert))
            time.sleep_ms(40)

        for wert in range(4095, -1, -128):
            pwm.kanal_setzen(TESTKANAL, wert)
            print("Kanal {}: {:4d} / 4095".format(TESTKANAL, wert))
            time.sleep_ms(40)
finally:
    pwm.kanal_aus(TESTKANAL)
    print("Testkanal ausgeschaltet.")
