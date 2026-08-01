"""
mcp23017.py
Kleine MicroPython-Bibliothek für den MCP23017 am ESP32.

Registerbelegung: IOCON.BANK = 0
Standardadresse: 0x20 bei A0 = A1 = A2 = GND

Wichtiger Hinweis:
Das aktuelle Microchip-Datenblatt DS20001952D kennzeichnet GPA7 und
GPB7 beim MCP23017 als reine Ausgänge. Ältere Datenblattstände
beschrieben diese Pins als bidirektional. Mit strict_gp7=True wird
deshalb eine Konfiguration dieser beiden Pins als Eingang verhindert.
"""


class MCP23017:
    INPUT = 1
    OUTPUT = 0

    IODIRA = 0x00
    IODIRB = 0x01
    IPOLA = 0x02
    IPOLB = 0x03
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCON = 0x0A
    GPPUA = 0x0C
    GPPUB = 0x0D
    INTFA = 0x0E
    INTFB = 0x0F
    INTCAPA = 0x10
    INTCAPB = 0x11
    GPIOA = 0x12
    GPIOB = 0x13
    OLATA = 0x14
    OLATB = 0x15

    def __init__(self, i2c, address=0x20, strict_gp7=True):
        if not 0x20 <= address <= 0x27:
            raise ValueError("Die MCP23017-Adresse muss zwischen 0x20 und 0x27 liegen.")

        self.i2c = i2c
        self.address = address
        self.strict_gp7 = strict_gp7

        self._write_register(self.IOCON, 0x00)

        self._olat = [
            self._read_register(self.OLATA),
            self._read_register(self.OLATB),
        ]

    def _write_register(self, register, value):
        self.i2c.writeto_mem(
            self.address,
            register,
            bytes((value & 0xFF,)),
        )

    def _read_register(self, register):
        return self.i2c.readfrom_mem(
            self.address,
            register,
            1,
        )[0]

    def _change_bit(self, register, bit, value):
        data = self._read_register(register)

        if value:
            data |= 1 << bit
        else:
            data &= ~(1 << bit)

        self._write_register(register, data)

    @staticmethod
    def _pin_data(pin):
        if not 0 <= pin <= 15:
            raise ValueError("Die Pinnummer muss zwischen 0 und 15 liegen.")

        port = 0 if pin < 8 else 1
        bit = pin if pin < 8 else pin - 8
        return port, bit

    @staticmethod
    def _port_index(port):
        if port in ("A", "a", 0):
            return 0
        if port in ("B", "b", 1):
            return 1
        raise ValueError("Der Port muss 'A', 'B', 0 oder 1 sein.")

    def pin_mode(self, pin, mode):
        port, bit = self._pin_data(pin)

        if mode not in (self.INPUT, self.OUTPUT):
            raise ValueError("Als Modus ist MCP23017.INPUT oder MCP23017.OUTPUT zulässig.")

        if self.strict_gp7 and mode == self.INPUT and pin in (7, 15):
            raise ValueError(
                "GPA7 und GPB7 werden nach aktuellem Datenblatt "
                "beim MCP23017 nur als Ausgänge verwendet."
            )

        self._change_bit(self.IODIRA + port, bit, mode == self.INPUT)

    def pullup(self, pin, enabled=True):
        port, bit = self._pin_data(pin)
        self._change_bit(self.GPPUA + port, bit, enabled)

    def invert_input(self, pin, enabled=True):
        port, bit = self._pin_data(pin)
        self._change_bit(self.IPOLA + port, bit, enabled)

    def write(self, pin, value):
        port, bit = self._pin_data(pin)

        if value:
            self._olat[port] |= 1 << bit
        else:
            self._olat[port] &= ~(1 << bit)

        self._write_register(self.OLATA + port, self._olat[port])

    def read(self, pin):
        port, bit = self._pin_data(pin)
        data = self._read_register(self.GPIOA + port)
        return 1 if data & (1 << bit) else 0

    def write_port(self, port, value):
        port = self._port_index(port)
        self._olat[port] = value & 0xFF
        self._write_register(self.OLATA + port, self._olat[port])

    def read_port(self, port):
        port = self._port_index(port)
        return self._read_register(self.GPIOA + port)

    def interrupt_enable(self, pin, enabled=True):
        port, bit = self._pin_data(pin)
        self._change_bit(self.GPINTENA + port, bit, enabled)

    def interrupt_on_change(self, pin):
        """Interrupt bei Änderung gegenüber dem zuvor gelesenen Zustand."""
        port, bit = self._pin_data(pin)
        self._change_bit(self.INTCONA + port, bit, False)
        self.interrupt_enable(pin, True)

    def interrupt_on_default(self, pin, default_value):
        """Interrupt bei Abweichung vom angegebenen Sollwert."""
        port, bit = self._pin_data(pin)
        self._change_bit(self.DEFVALA + port, bit, bool(default_value))
        self._change_bit(self.INTCONA + port, bit, True)
        self.interrupt_enable(pin, True)

    def configure_interrupt_outputs(
        self,
        mirror=False,
        open_drain=True,
        active_high=False,
    ):
        value = self._read_register(self.IOCON)

        value &= ~(1 << 7)

        if mirror:
            value |= 1 << 6
        else:
            value &= ~(1 << 6)

        if open_drain:
            value |= 1 << 2
        else:
            value &= ~(1 << 2)

        if active_high:
            value |= 1 << 1
        else:
            value &= ~(1 << 1)

        self._write_register(self.IOCON, value)

    def interrupt_flags(self, port):
        port = self._port_index(port)
        return self._read_register(self.INTFA + port)

    def interrupt_capture(self, port):
        """
        Liest den beim Interrupt gespeicherten Portzustand.
        Das Lesen von INTCAP löscht den Interrupt dieses Ports.
        """
        port = self._port_index(port)
        return self._read_register(self.INTCAPA + port)

    def clear_interrupt(self, port):
        return self.interrupt_capture(port)


def _selbsttest():
    """Initialisiert den MCP23017 beim direkten Start dieser Datei."""
    from machine import I2C, Pin

    SDA_PIN = 21  # GPIO21 - SDA - gelb
    SCL_PIN = 22  # GPIO22 - SCL - grün
    ADRESSE = 0x20

    i2c = I2C(
        0,
        sda=Pin(SDA_PIN),
        scl=Pin(SCL_PIN),
        freq=100_000,
    )

    print("MCP23017-Selbsttest an Adresse", hex(ADRESSE))

    try:
        mcp = MCP23017(i2c, address=ADRESSE)
        print("Initialisierung erfolgreich.")
        print("Port A: {:08b}".format(mcp.read_port("A")))
        print("Port B: {:08b}".format(mcp.read_port("B")))
    except Exception as fehler:
        print("Initialisierung fehlgeschlagen:", fehler)
        print(
            "I2C-Scan:",
            [hex(adresse) for adresse in i2c.scan()],
        )


if __name__ == "__main__":
    _selbsttest()
