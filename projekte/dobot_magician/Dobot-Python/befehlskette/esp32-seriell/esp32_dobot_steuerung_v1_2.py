"""ESP32-Steuerung für die Dobot-Befehlskette.

MicroPython-Version 1.2

Sechs Taster senden über die USB-COM-Schnittstelle:

    GPIO 25 -> PAUSE
    GPIO 26 -> WEITER
    GPIO 27 -> HALT
    GPIO 33 -> STATUS
    GPIO 18 -> PIN_FREI1
    GPIO 32 -> PIN_FREI2
Zwei Led    
    GPIO 02 -> PIN_LED ( blaue Online-LED neben der roten Power-LED)
    GPIO 19 -> PIN_LED_GELB
    
Jeder Taster wird zwischen dem GPIO und GND angeschlossen.
Pin.PULL_UP aktiviert den internen Pull-up-Widerstand.

Die LED an GPIO 2 leuchtet, sobald der PC die Nachricht
PC_BEREIT gesendet hat.

Achtung:
HALT bricht die laufende Dobot-Aufgabe endgültig ab.

Hinweis:
Zum Testen der Taster braucht keine Verbindung zum Steuerung des Dobot bestehen.
Somit kann die Verbindung mit Thonny bleiben.
Sonst muß Thonny auf einen anderen Port oder WebREPL gestellt und
der ESP per RESET-Knopf neu gestartet werden.
"""

from machine import Pin
import sys
import time
import random


try:
    import uselect as select
except ImportError:
    import select


VERSION = "1.2"
VERSIONSDATUM = "24.07.2026"


# ------------------------------------------------------------
# Anschlüsse
# ------------------------------------------------------------

PIN_PAUSE = 25
PIN_WEITER = 26
PIN_HALT = 27
PIN_STATUS = 33
PIN_FREI1 = 18   # 35 geht nicht
PIN_FREI2 = 32
PIN_LED = 2
PIN_LED_GELB = 19

led = Pin(PIN_LED, Pin.OUT)
led.off()

led_gelb = Pin(PIN_LED_GELB, Pin.OUT)
led_gelb.on()


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

# ------------------------------------------------------------
# Überwachung der Ein- und Ausgänge
# ------------------------------------------------------------
tasten = [
    Taste(PIN_PAUSE, "PAUSE"),
    Taste(PIN_WEITER, "WEITER"),
    Taste(PIN_HALT, "HALT"),
    Taste(PIN_STATUS, "STATUS"),
    Taste(PIN_FREI1, "FREI_1"),
    Taste(PIN_FREI2, "FREI_2"),
]


UEBERWACHTE_SIGNALE = {
    "LED_gelb":      (led_gelb, 0),  # 0 keine Entprellung, 40 für 40 ms Entprellung
}

letzte_rohwerte = {}
stabile_werte = {}
aenderungszeiten = {}

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


simulation_led_aktiv = False
simulation_led_min_ms = 0
simulation_led_max_ms = 0
simulation_led_naechste_aenderung = 0


def simulation_led_aendert_sich(min_sekunden, max_sekunden):
    """Startet die nicht blockierende Simulation der gelben LED."""

    global simulation_led_aktiv
    global simulation_led_min_ms
    global simulation_led_max_ms
    global simulation_led_naechste_aenderung

    if min_sekunden <= 0 or max_sekunden < min_sekunden:
        raise ValueError("Ungültiger Zeitbereich.")

    simulation_led_min_ms = int(min_sekunden * 1000)
    simulation_led_max_ms = int(max_sekunden * 1000)
    simulation_led_aktiv = True

    wartezeit_ms = random.randint(
        simulation_led_min_ms,
        simulation_led_max_ms,
    )

    simulation_led_naechste_aenderung = time.ticks_add(
        time.ticks_ms(),
        wartezeit_ms,
    )


def simulation_led_pruefen():
    """Ändert die LED, sobald die nächste Zufallszeit erreicht ist."""

    global simulation_led_naechste_aenderung

    if not simulation_led_aktiv:
        return

    jetzt = time.ticks_ms()

    if time.ticks_diff(
        jetzt,
        simulation_led_naechste_aenderung,
    ) < 0:
        return

    led_gelb.value(not led_gelb.value())

    wartezeit_ms = random.randint(
        simulation_led_min_ms,
        simulation_led_max_ms,
    )

    simulation_led_naechste_aenderung = time.ticks_add(
        jetzt,
        wartezeit_ms,
    )


def ueberwachung_initialisieren():
    """Speichert die aktuellen Anfangszustände aller Signale."""

    jetzt = time.ticks_ms()

    for name, signal in UEBERWACHTE_SIGNALE.items():
        pin, entprellzeit = signal
        wert = pin.value()

        letzte_rohwerte[name] = wert
        stabile_werte[name] = wert
        aenderungszeiten[name] = jetzt


def ueberwache():
    jetzt = time.ticks_ms()

    for name, signal in UEBERWACHTE_SIGNALE.items():
        pin, entprellzeit = signal
        aktueller_wert = pin.value()

        # Eine mögliche Änderung wurde erkannt.
        if aktueller_wert != letzte_rohwerte[name]:
            letzte_rohwerte[name] = aktueller_wert
            aenderungszeiten[name] = jetzt

        # Der neue Zustand muss lange genug stabil sein.
        zeit_stabil = time.ticks_diff(
            jetzt,
            aenderungszeiten[name],
        )

        if (
            aktueller_wert != stabile_werte[name]
            and zeit_stabil >= entprellzeit
        ):
            stabile_werte[name] = aktueller_wert

            zeile_senden(
                f"WERT;{name};{aktueller_wert}"
            )

def simulation_led_beenden():
    global simulation_led_aktiv
    simulation_led_aktiv = False    

def hauptprogramm():
    """Startet die dauerhafte Taster- und COM-Abfrage."""

    time.sleep_ms(STARTWARTEZEIT_MS)

    ueberwachung_initialisieren()
    zeile_senden("ESP32_BEREIT")

    simulation_led_aendert_sich(30, 60)
    
    while True:
        tasten_pruefen()          # speziell für Taster und Schalter
        simulation_led_pruefen()  # zufällige LED-Änderung prüfen
        ueberwache()              # allgemeine Ein- und Ausgänge
        pc_nachrichten_lesen()
        time.sleep_ms(SCHLEIFENPAUSE_MS)

def Tasten_testen():
    while True:
        for taste in tasten:
            befehl = taste.pruefen()
            if befehl is not None:
                print(befehl)
                led.value(not led.value())
            else:
                pass

try:
    hauptprogramm()

except KeyboardInterrupt:
    led.off()
    simulation_led_beenden()
    led_gelb.off()
