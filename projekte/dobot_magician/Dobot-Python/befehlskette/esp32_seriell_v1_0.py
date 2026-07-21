"""Serielle Steuerbefehle von einem ESP32 empfangen.

Version 1.0

Der ESP32-Thread greift niemals auf die Dobot-API zu.
Er schreibt nur Steuerbefehle in eine gemeinsame queue.Queue.

Erkannte Zeilen vom ESP32:
    P oder PAUSE
    W oder WEITER
    H oder HALT
    ? oder STATUS
"""

import sys
import threading
import time


VERSION = "1.0"
VERSIONSDATUM = "21.07.2026"

BEFEHLE = {
    "p": "p",
    "pause": "p",
    "w": "w",
    "weiter": "w",
    "h": "h",
    "halt": "h",
    "?": "?",
    "status": "?",
}


def version():
    """Gibt die Versionsinformation zurück."""

    return (
        f"esp32_seriell_v1_0.py Version {VERSION} "
        f"vom {VERSIONSDATUM}"
    )


def _pyserial_laden():
    """Importiert pySerial und erzeugt eine verständliche Meldung."""

    try:
        import serial
        from serial.tools import list_ports

    except ImportError as fehler:
        raise RuntimeError(
            "Das Python-Paket 'pyserial' ist nicht installiert.\n"
            "Installiere in Thonny unter "
            "'Extras -> Pakete verwalten' das Paket 'pyserial'."
        ) from fehler

    return serial, list_ports


def serielle_ports_auflisten():
    """Gibt die von pySerial gefundenen COM-Ports zurück."""

    _, list_ports = _pyserial_laden()

    ergebnis = []

    for port in list_ports.comports():
        ergebnis.append(
            {
                "geraet": port.device,
                "beschreibung": port.description,
                "hardware_id": port.hwid,
            }
        )

    return ergebnis


def _befehl_normalisieren(text):
    """Übersetzt eine empfangene Textzeile in p, w, h oder ?."""

    return BEFEHLE.get(str(text).strip().lower())


class ESP32SerielleSteuerung:
    """Empfängt ESP32-Steuerbefehle in einem Daemon-Thread."""

    def __init__(
        self,
        steuerbefehle,
        port,
        baudrate=115200,
        lese_timeout=0.2,
        wiederverbinden=True,
        wiederholzeit=2.0,
    ):
        self.steuerbefehle = steuerbefehle
        self.port = str(port)
        self.baudrate = int(baudrate)
        self.lese_timeout = float(lese_timeout)
        self.wiederverbinden = bool(wiederverbinden)
        self.wiederholzeit = float(wiederholzeit)

        self._beenden = threading.Event()
        self._verbunden = threading.Event()
        self._thread = None
        self._serial = None
        self._serial_lock = threading.Lock()

    def starten(self):
        """Startet den seriellen Empfangsthread."""

        if self._thread is not None and self._thread.is_alive():
            return self._thread

        self._beenden.clear()

        self._thread = threading.Thread(
            target=self._empfangsschleife,
            daemon=True,
            name="ESP32-COM-Steuerung",
        )
        self._thread.start()

        return self._thread

    def beenden(self):
        """Beendet den Thread und schließt die COM-Schnittstelle."""

        self._beenden.set()

        with self._serial_lock:
            ser = self._serial

        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass

        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._thread is not threading.current_thread()
        ):
            self._thread.join(timeout=1.0)

    def ist_verbunden(self):
        """Gibt True zurück, wenn die COM-Verbindung geöffnet ist."""

        return self._verbunden.is_set()

    def auf_verbindung_warten(self, timeout=5.0):
        """Wartet höchstens ``timeout`` Sekunden auf die Verbindung."""

        return self._verbunden.wait(timeout=float(timeout))

    def _senden(self, ser, text):
        """Sendet eine mit Zeilenende abgeschlossene Antwort."""

        nachricht = f"{text}\n".encode("utf-8")
        ser.write(nachricht)
        ser.flush()

    def _nachricht_verarbeiten(self, ser, text):
        """Verarbeitet genau eine empfangene Textzeile."""

        nachricht = text.strip()

        if not nachricht:
            return

        gross = nachricht.upper()

        if gross == "ESP32_BEREIT":
            print("ESP32 meldet: bereit.")
            self._senden(ser, "PC_BEREIT")
            return

        if gross == "PING":
            self._senden(ser, "PONG")
            return

        steuerbefehl = _befehl_normalisieren(nachricht)

        if steuerbefehl is None:
            print(
                f"Unbekannte ESP32-Nachricht: {nachricht!r}"
            )
            self._senden(
                ser,
                f"UNBEKANNT {nachricht}",
            )
            return

        self.steuerbefehle.put(
            (steuerbefehl, "ESP32")
        )

        print(
            f"ESP32-Steuerbefehl empfangen: "
            f"{nachricht.upper()}"
        )

        # Diese Antwort bestätigt nur den Empfang durch den PC.
        self._senden(
            ser,
            f"EMPFANGEN {nachricht.upper()}",
        )

    def _empfangsschleife(self):
        """Öffnet den Port und liest fortlaufend Textzeilen."""

        try:
            serial, _ = _pyserial_laden()

        except RuntimeError as fehler:
            print(
                f"\nFEHLER ESP32-COM: {fehler}",
                file=sys.stderr,
            )
            return

        while not self._beenden.is_set():
            try:
                ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.lese_timeout,
                    write_timeout=1.0,
                )

                with self._serial_lock:
                    self._serial = ser

                self._verbunden.set()

                print(
                    f"ESP32 über {self.port} mit "
                    f"{self.baudrate} Baud verbunden."
                )

                try:
                    ser.reset_input_buffer()
                except Exception:
                    pass

                self._senden(ser, "PC_BEREIT")

                while (
                    not self._beenden.is_set()
                    and ser.is_open
                ):
                    rohzeile = ser.readline()

                    if not rohzeile:
                        continue

                    text = rohzeile.decode(
                        "utf-8",
                        errors="replace",
                    ).strip()

                    self._nachricht_verarbeiten(
                        ser,
                        text,
                    )

            except serial.SerialException as fehler:
                if not self._beenden.is_set():
                    print(
                        f"\nFEHLER ESP32-COM auf "
                        f"{self.port}: {fehler}",
                        file=sys.stderr,
                    )

            except OSError as fehler:
                if not self._beenden.is_set():
                    print(
                        f"\nFEHLER ESP32-COM auf "
                        f"{self.port}: {fehler}",
                        file=sys.stderr,
                    )

            finally:
                self._verbunden.clear()

                with self._serial_lock:
                    ser = self._serial
                    self._serial = None

                if ser is not None:
                    try:
                        ser.close()
                    except Exception:
                        pass

            if not self.wiederverbinden:
                break

            if not self._beenden.is_set():
                print(
                    f"Neuer ESP32-Verbindungsversuch in "
                    f"{self.wiederholzeit:.1f} Sekunden ..."
                )
                self._beenden.wait(
                    timeout=self.wiederholzeit
                )
