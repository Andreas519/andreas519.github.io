"""TCP-Server als Ersatz für einen ESP32.

Simulator-Version 1.3
Passend zu:
    befehlskette_v3_3_5.py
    esp32_dobot_steuerung_v1_3.py

Der Simulator kann:

- Steuerbefehle und Werte an das PC-Programm senden,
- Befehle des PC-Programms verarbeiten,
- den Zustand einer gelben LED verwalten,
- die gelbe LED in zufälligen Abständen umschalten,
- Zustandsänderungen als WERT;LED_gelb;0/1 melden,
- Status, Hilfe, Bestätigungen und Fehlermeldungen senden.
"""

import random
import socket
import threading
import time


VERSION = "1.3"
VERSIONSDATUM = "24.07.2026"

HOST = "127.0.0.1"
PORT = 5000

STEUERBEFEHLE = {
    "p": "PAUSE",                   "pause": "PAUSE",
    "w": "WEITER",                  "weiter": "WEITER",
    "h": "HALT",                    "halt": "HALT",
    "?": "STATUS",                  "status": "STATUS",
    "a": "WERT;POSITION;POS_A",     "pos_a": "WERT;POSITION;POS_A",
    "b": "WERT;POSITION;POS_B",     "pos_b": "WERT;POSITION;POS_B",
    "f": "FREIGABE",                "freigabe": "FREIGABE",
    "f1": "FREI_1",                 "frei_1": "FREI_1",
    "f2": "FREI_2",                 "frei_2": "FREI_2",
    "t1": "WERT;TASTER;1",          "taster_ein": "WERT;TASTER;1",
    "t0": "WERT;TASTER;0",          "taster_aus": "WERT;TASTER;0",
    "temp25": "WERT;TEMPERATUR;25", "temp35": "WERT;TEMPERATUR;35",
}

AUTOMATISCHE_PC_STATUSMELDUNGEN = (
    "BEFEHLSKETTE_GEPRUEFT",
    "PROGRAMM_GESTARTET",
    "BEFEHL_GESTARTET",
    "BEFEHL_FERTIG",
    "MARKE",
    "SPRUNG",
    "WARTE_AUF",
    "BEDINGUNG",
    "BEFEHLSKETTE_BEENDET",
    "PROGRAMM_BEENDET",
)


class SimulatorZustand:
    """Speichert die simulierten Ein- und Ausgangszustände."""

    def __init__(self):
        self.lock = threading.Lock()
        self.led_blau = 0
        self.led_gelb = 1
        self.simulation_aktiv = False
        self.simulation_min_sekunden = 30
        self.simulation_max_sekunden = 60
        self.naechste_aenderung = None
        self.letzte_pc_statusmeldung = ""

    def led_gelb_setzen(self, wert):
        with self.lock:
            self.led_gelb = int(bool(wert))
            return self.led_gelb

    def led_gelb_umschalten(self):
        with self.lock:
            self.led_gelb = int(not self.led_gelb)
            return self.led_gelb

    def status_lesen(self):
        with self.lock:
            return {
                "led_blau": self.led_blau,
                "led_gelb": self.led_gelb,
                "simulation_aktiv": self.simulation_aktiv,
                "simulation_min": self.simulation_min_sekunden,
                "simulation_max": self.simulation_max_sekunden,
                "letzte_pc_statusmeldung": self.letzte_pc_statusmeldung,
            }

    def simulation_starten(self, min_sekunden=30, max_sekunden=60):
        if min_sekunden <= 0 or max_sekunden < min_sekunden:
            raise ValueError("Ungültiger Zeitbereich.")

        with self.lock:
            self.simulation_min_sekunden = int(min_sekunden)
            self.simulation_max_sekunden = int(max_sekunden)
            self.simulation_aktiv = True
            self.naechste_aenderung = (
                time.monotonic()
                + random.randint(
                    self.simulation_min_sekunden,
                    self.simulation_max_sekunden,
                )
            )

    def simulation_beenden(self):
        with self.lock:
            self.simulation_aktiv = False
            self.naechste_aenderung = None

    def simulation_pruefen(self):
        """Gibt den neuen LED-Wert zurück, wenn umgeschaltet wurde."""

        with self.lock:
            if not self.simulation_aktiv:
                return None

            if self.naechste_aenderung is None:
                return None

            jetzt = time.monotonic()

            if jetzt < self.naechste_aenderung:
                return None

            self.led_gelb = int(not self.led_gelb)
            self.naechste_aenderung = (
                jetzt
                + random.randint(
                    self.simulation_min_sekunden,
                    self.simulation_max_sekunden,
                )
            )

            return self.led_gelb


def senden(verbindung, sende_lock, text):
    """Sendet thread-sicher genau eine Textzeile."""

    daten = f"{text}\n".encode("utf-8")

    with sende_lock:
        verbindung.sendall(daten)


def led_gelb_wert_senden(verbindung, sende_lock, zustand):
    """Sendet den aktuellen Zustand der simulierten gelben LED."""

    wert = zustand.status_lesen()["led_gelb"]
    senden(
        verbindung,
        sende_lock,
        f"WERT;LED_gelb;{wert}",
    )


def esp32_status_senden(verbindung, sende_lock, zustand):
    """Sendet einen kompakten Simulatorstatus."""

    status = zustand.status_lesen()

    senden(
        verbindung,
        sende_lock,
        "ESP32_STATUS;"
        f"VERSION={VERSION}-SIMULATOR;"
        f"LED_BLAU={status['led_blau']};"
        f"LED_GELB={status['led_gelb']};"
        f"SIMULATION={int(status['simulation_aktiv'])}",
    )


def hilfe_senden(verbindung, sende_lock):
    """Sendet die unterstützten PC-Befehle."""

    senden(
        verbindung,
        sende_lock,
        "ESP32_BEFEHLE;"
        "LED_GELB_EIN;"
        "LED_GELB_AUS;"
        "LED_GELB_UMSCHALTEN;"
        "LED_GELB_STATUS;"
        "SIMULATION_LED_START;min;max;"
        "SIMULATION_LED_STOP;"
        "ESP32_STATUS;"
        "PING;"
        "HILFE",
    )


def pc_nachricht_verarbeiten(
    verbindung,
    sende_lock,
    zustand,
    nachricht,
):
    """Verarbeitet genau eine vom PC empfangene Nachricht."""

    if not nachricht:
        return

    teile = nachricht.split(";")
    befehl = teile[0].strip().upper()
    parameter = [teil.strip() for teil in teile[1:]]

    if befehl == "PC_BEREIT":
        with zustand.lock:
            zustand.led_blau = 1

        senden(
            verbindung,
            sende_lock,
            "PC_BEREIT_BESTAETIGT",
        )
        return

    if befehl == "PING":
        senden(verbindung, sende_lock, "PONG")
        return

    if befehl == "LED_GELB_EIN":
        zustand.simulation_beenden()
        zustand.led_gelb_setzen(1)
        senden(
            verbindung,
            sende_lock,
            "BEFEHL_AUSGEFUEHRT;LED_GELB_EIN",
        )
        led_gelb_wert_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return

    if befehl == "LED_GELB_AUS":
        zustand.simulation_beenden()
        zustand.led_gelb_setzen(0)
        senden(
            verbindung,
            sende_lock,
            "BEFEHL_AUSGEFUEHRT;LED_GELB_AUS",
        )
        led_gelb_wert_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return

    if befehl == "LED_GELB_UMSCHALTEN":
        zustand.simulation_beenden()
        zustand.led_gelb_umschalten()
        senden(
            verbindung,
            sende_lock,
            "BEFEHL_AUSGEFUEHRT;LED_GELB_UMSCHALTEN",
        )
        led_gelb_wert_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return

    if befehl == "LED_GELB_STATUS":
        led_gelb_wert_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return

    if befehl == "SIMULATION_LED_STOP":
        zustand.simulation_beenden()
        senden(
            verbindung,
            sende_lock,
            "BEFEHL_AUSGEFUEHRT;SIMULATION_LED_STOP",
        )
        return

    if befehl == "SIMULATION_LED_START":
        if len(parameter) == 0:
            min_sekunden = 30
            max_sekunden = 60

        elif len(parameter) == 2:
            try:
                min_sekunden = int(parameter[0])
                max_sekunden = int(parameter[1])
            except ValueError:
                senden(
                    verbindung,
                    sende_lock,
                    "BEFEHL_FEHLER;"
                    "SIMULATION_LED_START;"
                    "Zeitwerte müssen ganze Zahlen sein",
                )
                return

        else:
            senden(
                verbindung,
                sende_lock,
                "BEFEHL_FEHLER;"
                "SIMULATION_LED_START;"
                "Syntax: SIMULATION_LED_START;min;max",
            )
            return

        try:
            zustand.simulation_starten(
                min_sekunden,
                max_sekunden,
            )
        except ValueError as fehler:
            senden(
                verbindung,
                sende_lock,
                "BEFEHL_FEHLER;"
                f"SIMULATION_LED_START;{fehler}",
            )
            return

        senden(
            verbindung,
            sende_lock,
            "BEFEHL_AUSGEFUEHRT;"
            f"SIMULATION_LED_START;"
            f"{min_sekunden};{max_sekunden}",
        )
        return

    if befehl == "ESP32_STATUS":
        esp32_status_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return

    if befehl == "HILFE":
        hilfe_senden(verbindung, sende_lock)
        return

    if befehl in AUTOMATISCHE_PC_STATUSMELDUNGEN:
        with zustand.lock:
            zustand.letzte_pc_statusmeldung = nachricht
        return

    senden(
        verbindung,
        sende_lock,
        f"UNBEKANNTER_BEFEHL;{nachricht}",
    )


def steuerbefehle_anzeigen():
    """Gibt die Kurz- und Langbefehle paarweise aus."""

    eintraege = list(STEUERBEFEHLE.items())

    print("Verfügbare Kurz- und Langbefehle:")

    for position in range(0, len(eintraege), 2):
        links = eintraege[position]
        rechts = (
            eintraege[position + 1]
            if position + 1 < len(eintraege)
            else None
        )

        links_text = f"{links[0]!r} -> {links[1]}"
        rechts_text = (
            ""
            if rechts is None
            else f"{rechts[0]!r} -> {rechts[1]}"
        )

        print(f"  {links_text:<40} {rechts_text}")


def pc_meldung_anzeigen(text):
    """Zeigt wichtige PC-Zustandsmeldungen verständlich an."""

    if (
        text.startswith("PROGRAMM_BEENDET;")
        or text.startswith("BEFEHLSKETTE_BEENDET;")
    ):
        grund = text.rsplit(";", 1)[-1]
        beschreibungen = {
            "HALT": "Die Ausführung wurde durch HALT beendet.",
            "NORMAL": "Die Ausführung wurde normal beendet.",
            "TASTATURABBRUCH": "Das PC-Programm wurde mit Strg+C abgebrochen.",
            "ABBRUCH_VOR_START": "Das PC-Programm wurde vor dem Start abgebrochen.",
            "FEHLER": "Die Ausführung wurde wegen eines Fehlers beendet.",
        }
        print(
            "*** "
            + beschreibungen.get(grund, text)
            + " ***"
        )

    elif text.startswith("BEFEHL_GESTARTET;"):
        teile = text.split(";", 4)
        if len(teile) >= 4:
            print(
                f"*** Befehl {teile[1]} gestartet: "
                f"{teile[2]} ***"
            )

    elif text.startswith("BEFEHL_FERTIG;"):
        teile = text.split(";", 3)
        if len(teile) >= 3:
            print(
                f"*** Befehl {teile[1]} fertig: "
                f"{teile[2]} ***"
            )

    elif text.startswith("WARTE_AUF;"):
        print(
            "*** PC wartet: "
            + text.partition(";")[2]
            + " ***"
        )

    elif text.startswith("BEDINGUNG;"):
        print(
            "*** Bedingung ausgewertet: "
            + text.partition(";")[2]
            + " ***"
        )


def empfangen(
    verbindung,
    sende_lock,
    zustand,
    beenden,
):
    """Empfängt und verarbeitet Nachrichten des TCP-Clients."""

    puffer = bytearray()
    verbindung.settimeout(0.5)

    while not beenden.is_set():
        try:
            daten = verbindung.recv(1024)
        except socket.timeout:
            continue
        except OSError:
            break

        if not daten:
            break

        puffer.extend(daten)

        while b"\n" in puffer:
            rohzeile, _, rest = puffer.partition(b"\n")
            puffer = bytearray(rest)

            text = (
                rohzeile
                .decode("utf-8", errors="replace")
                .rstrip("\r")
            )

            print(f"\nPC: {text}")
            pc_meldung_anzeigen(text)

            try:
                pc_nachricht_verarbeiten(
                    verbindung,
                    sende_lock,
                    zustand,
                    text,
                )
            except OSError:
                beenden.set()
                break

            print("ESP> ", end="", flush=True)

    beenden.set()


def simulation_ausfuehren(
    verbindung,
    sende_lock,
    zustand,
    beenden,
):
    """Schaltet die simulierte LED zu den Zufallszeiten um."""

    while not beenden.is_set():
        neuer_wert = zustand.simulation_pruefen()

        if neuer_wert is not None:
            try:
                senden(
                    verbindung,
                    sende_lock,
                    f"WERT;LED_gelb;{neuer_wert}",
                )
                print(
                    f"\nSIMULATION: LED_gelb = {neuer_wert}"
                )
                print("ESP> ", end="", flush=True)
            except OSError:
                beenden.set()
                return

        beenden.wait(0.1)


def lokalen_led_befehl_verarbeiten(
    verbindung,
    sende_lock,
    zustand,
    eingabe,
):
    """Verarbeitet lokale Befehle für die simulierte LED."""

    befehl = eingabe.lower()

    if befehl in ("g1", "gelb_ein"):
        zustand.simulation_beenden()
        wert = zustand.led_gelb_setzen(1)
        senden(
            verbindung,
            sende_lock,
            f"WERT;LED_gelb;{wert}",
        )
        return True

    if befehl in ("g0", "gelb_aus"):
        zustand.simulation_beenden()
        wert = zustand.led_gelb_setzen(0)
        senden(
            verbindung,
            sende_lock,
            f"WERT;LED_gelb;{wert}",
        )
        return True

    if befehl in ("gu", "gelb_umschalten"):
        zustand.simulation_beenden()
        wert = zustand.led_gelb_umschalten()
        senden(
            verbindung,
            sende_lock,
            f"WERT;LED_gelb;{wert}",
        )
        return True

    if befehl in ("gs", "gelb_status"):
        led_gelb_wert_senden(
            verbindung,
            sende_lock,
            zustand,
        )
        return True

    if befehl.startswith("sim "):
        teile = eingabe.split()

        if len(teile) != 3:
            print("Syntax: sim MIN MAX")
            return True

        try:
            min_sekunden = int(teile[1])
            max_sekunden = int(teile[2])
            zustand.simulation_starten(
                min_sekunden,
                max_sekunden,
            )
        except ValueError as fehler:
            print(f"Simulation nicht gestartet: {fehler}")
            return True

        print(
            "LED-Simulation gestartet: "
            f"{min_sekunden} bis {max_sekunden} Sekunden"
        )
        return True

    if befehl in ("sim_stop", "simulation_stop"):
        zustand.simulation_beenden()
        print("LED-Simulation beendet.")
        return True

    return False


def eingaben_senden(
    verbindung,
    sende_lock,
    zustand,
    beenden,
):
    """Liest Steuerbefehle, Ereignisse und Werte ein."""

    print()
    steuerbefehle_anzeigen()
    print()
    print("Lokale LED-Simulation:")
    print("  g1 / gelb_ein          -> LED_gelb = 1 senden")
    print("  g0 / gelb_aus          -> LED_gelb = 0 senden")
    print("  gu / gelb_umschalten   -> LED_gelb umschalten")
    print("  gs / gelb_status       -> LED_gelb-Status senden")
    print("  sim 3 6                -> Zufallssimulation starten")
    print("  sim_stop               -> Zufallssimulation beenden")
    print()
    print("  q / ende               -> Simulator beenden")
    print()
    print("Beliebige ESP-Nachrichten können direkt eingegeben werden.")

    while not beenden.is_set():
        try:
            eingabe = input("ESP> ").strip()
        except (EOFError, KeyboardInterrupt):
            eingabe = "q"

        if eingabe.lower() in ("q", "ende"):
            beenden.set()
            return

        if not eingabe:
            continue

        try:
            if lokalen_led_befehl_verarbeiten(
                verbindung,
                sende_lock,
                zustand,
                eingabe,
            ):
                continue

            nachricht = STEUERBEFEHLE.get(
                eingabe.lower(),
                eingabe,
            )

            senden(
                verbindung,
                sende_lock,
                nachricht,
            )
            print(f"Gesendet: {nachricht}")

        except OSError as fehler:
            print(f"Senden fehlgeschlagen: {fehler}")
            beenden.set()


def main():
    """Startet den TCP-Server und wartet auf einen Client."""

    beenden = threading.Event()
    sende_lock = threading.Lock()
    zustand = SimulatorZustand()

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )
        server.bind((HOST, PORT))
        server.listen(1)

        print(
            f"ESP-Simulator {VERSION} wartet "
            f"auf {HOST}:{PORT} ..."
        )

        verbindung, adresse = server.accept()

        with verbindung:
            print(
                "TCP-Client verbunden: "
                f"{adresse[0]}:{adresse[1]}"
            )

            senden(
                verbindung,
                sende_lock,
                "ESP32_BEREIT",
            )

            empfangsthread = threading.Thread(
                target=empfangen,
                args=(
                    verbindung,
                    sende_lock,
                    zustand,
                    beenden,
                ),
                daemon=True,
                name="ESP-Simulator-Empfang",
            )

            simulationsthread = threading.Thread(
                target=simulation_ausfuehren,
                args=(
                    verbindung,
                    sende_lock,
                    zustand,
                    beenden,
                ),
                daemon=True,
                name="ESP-Simulator-LED",
            )

            empfangsthread.start()
            simulationsthread.start()

            eingaben_senden(
                verbindung,
                sende_lock,
                zustand,
                beenden,
            )

            try:
                verbindung.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            empfangsthread.join(timeout=1.0)
            simulationsthread.join(timeout=1.0)

    print("ESP-Simulator beendet.")


if __name__ == "__main__":
    main()
