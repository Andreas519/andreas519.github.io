"""ESP32-Steuerung für die Dobot-Befehlskette.

MicroPython-Version 1.0

Vier Taster senden über die USB-COM-Schnittstelle:

    GPIO 25 -> PAUSE
    GPIO 26 -> WEITER
    GPIO 27 -> HALT
    GPIO 33 -> STATUS

Jeder Taster wird zwischen dem GPIO und GND angeschlossen.
Pin.PULL_UP aktiviert den internen Pull-up-Widerstand.

Die LED an GPIO 2 leuchtet, sobald der PC die Nachricht
PC_BEREIT gesendet hat.

Achtung:
HALT bricht die laufende Dobot-Aufgabe endgültig ab.
"""

from machine import Pin
import sys
import time

try:
    import uselect as select
except ImportError:
    import select


VERSION = "1.0"
VERSIONSDATUM = "22.07.2026"


# ------------------------------------------------------------
# Anschlüsse
# ------------------------------------------------------------

PIN_PAUSE = 25
PIN_WEITER = 26
PIN_HALT = 27
PIN_STATUS = 33

PIN_LED = 2


# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

ENTPRELLZEIT_MS = 50
SCHLEIFENPAUSE_MS = 5
STARTWARTEZEIT_MS = 1000


class Taste:
    """Speichert Zustand und Entprellung eines Tasters."""

    def __init__(self, pin_nummer, befehl):
        self.pin = Pin(
            pin_nummer,
            Pin.IN,
            Pin.PULL_UP,
        )
        self.befehl = befehl

        aktueller_zustand = self.pin.value()

        self.letzter_rohzustand = aktueller_zustand
        self.stabiler_zustand = aktueller_zustand
        self.letzte_aenderung = time.ticks_ms()

    def pruefen(self):
        """Gibt beim Drücken den zugehörigen Befehl zurück."""

        jetzt = time.ticks_ms()
        rohzustand = self.pin.value()

        if rohzustand != self.letzter_rohzustand:
            self.letzte_aenderung = jetzt
            self.letzter_rohzustand = rohzustand

        lange_genug_stabil = (
            time.ticks_diff(
                jetzt,
                self.letzte_aenderung,
            )
            >= ENTPRELLZEIT_MS
        )

        if (
            lange_genug_stabil
            and rohzustand != self.stabiler_zustand
        ):
            self.stabiler_zustand = rohzustand

            # Durch Pin.PULL_UP bedeutet 0:
            # Der Taster ist gedrückt.
            if rohzustand == 0:
                return self.befehl

        return None


led = Pin(PIN_LED, Pin.OUT)
led.off()


tasten = [
    Taste(PIN_PAUSE, "PAUSE"),
    Taste(PIN_WEITER, "WEITER"),
    Taste(PIN_HALT, "HALT"),
    Taste(PIN_STATUS, "STATUS"),
]


eingabe_poll = select.poll()
eingabe_poll.register(
    sys.stdin,
    select.POLLIN,
)


def zeile_senden(text):
    """Sendet genau eine Textzeile an den PC."""

    sys.stdout.write(str(text) + "\n")

    try:
        sys.stdout.flush()
    except AttributeError:
        pass


def tasten_pruefen():
    """Prüft alle Taster und sendet neue Befehle."""

    for taste in tasten:
        befehl = taste.pruefen()

        if befehl is not None:
            zeile_senden(befehl)


def pc_nachrichten_lesen():
    """Liest vorhandene Textzeilen vom PC ohne Blockieren."""

    while eingabe_poll.poll(0):
        zeile = sys.stdin.readline()

        if not zeile:
            return

        nachricht = zeile.strip()

        if nachricht == "PC_BEREIT":
            led.on()


def hauptprogramm():
    """Startet die dauerhafte Taster- und COM-Abfrage."""

    time.sleep_ms(STARTWARTEZEIT_MS)
    zeile_senden("ESP32_BEREIT")

    while True:
        tasten_pruefen()
        pc_nachrichten_lesen()
        time.sleep_ms(SCHLEIFENPAUSE_MS)


try:
    hauptprogramm()

except KeyboardInterrupt:
    led.off()
