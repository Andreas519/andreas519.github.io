"""ESP32-Kommunikation wahlweise über COM oder TCP.

Version 1.4

Zwei getrennte Queues werden verwendet:

``steuerbefehle``
    PAUSE, WEITER, HALT und STATUS.

``meldungen``
    Beliebige andere Textzeilen, zum Beispiel FREIGABE oder FERTIG.
    Diese Meldungen können von ``warte_bis`` ausgewertet werden.

``werte``
    Dauerhaft gespeicherte ESP-Werte aus Zeilen wie
    ``WERT;POSITION;POS_A`` oder ``WERT;TEMPERATUR;23.7``.
    Der Empfangsthread aktualisiert diese Werte unabhängig von der
    laufenden Befehlskette.
"""

import socket
import sys
import threading
import time


VERSION = "1.4"
VERSIONSDATUM = "23.07.2026"

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
        f"esp32_kommunikation_v1_4.py Version {VERSION} "
        f"vom {VERSIONSDATUM}"
    )


def _befehl_normalisieren(text):
    """Übersetzt eine Textzeile in p, w, h oder ?."""

    return BEFEHLE.get(str(text).strip().lower())


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

    return [
        {
            "geraet": port.device,
            "beschreibung": port.description,
            "hardware_id": port.hwid,
        }
        for port in list_ports.comports()
    ]




def _wert_umwandeln(text):
    """Wandelt empfangene Zahlen in int oder float um."""

    text = str(text).strip()

    try:
        return int(text)
    except ValueError:
        pass

    try:
        return float(text.replace(",", "."))
    except ValueError:
        return text


class ESPWerteSpeicher:
    """Thread-sicherer Speicher für dauerhaft empfangene ESP-Werte."""

    def __init__(self):
        self._werte = {}
        self._lock = threading.RLock()
        self._aenderungsnummer = 0

    @staticmethod
    def _name_normalisieren(name):
        name = str(name).strip()

        if not name:
            raise ValueError("Der Name eines ESP-Wertes darf nicht leer sein.")

        return name.casefold()

    def setzen(self, name, wert, quelle="extern"):
        """Speichert einen Wert und gibt den neuen Eintrag zurück."""

        name_original = str(name).strip()
        name_norm = self._name_normalisieren(name_original)

        with self._lock:
            self._aenderungsnummer += 1
            eintrag = {
                "name": name_original,
                "wert": wert,
                "quelle": str(quelle),
                "zeit": time.time(),
                "aenderungsnummer": self._aenderungsnummer,
            }
            self._werte[name_norm] = eintrag
            return dict(eintrag)

    def lesen(self, name, standard=None):
        """Liest nur den Wert oder gibt ``standard`` zurück."""

        name_norm = self._name_normalisieren(name)

        with self._lock:
            eintrag = self._werte.get(name_norm)
            return standard if eintrag is None else eintrag["wert"]

    def eintrag_lesen(self, name):
        """Liest Wert, Quelle und Empfangszeit als Kopie."""

        name_norm = self._name_normalisieren(name)

        with self._lock:
            eintrag = self._werte.get(name_norm)
            return None if eintrag is None else dict(eintrag)

    def vorhanden(self, name):
        """Prüft, ob bereits ein Wert mit diesem Namen vorliegt."""

        return self.eintrag_lesen(name) is not None

    def alle_lesen(self):
        """Gibt eine Kopie aller gespeicherten Einträge zurück."""

        with self._lock:
            return {
                eintrag["name"]: dict(eintrag)
                for eintrag in self._werte.values()
            }


class _ESP32SteuerungBasis:
    """Gemeinsame Verarbeitung der ESP32-Textnachrichten."""

    def __init__(
        self,
        steuerbefehle,
        meldungen=None,
        werte=None,
        name="ESP32",
    ):
        self.steuerbefehle = steuerbefehle
        self.meldungen = meldungen
        self.werte = werte if werte is not None else ESPWerteSpeicher()
        self.name = str(name)
        self._beenden = threading.Event()
        self._verbunden = threading.Event()
        self._thread = None
        self._sende_lock = threading.Lock()

    def ist_verbunden(self):
        """Gibt True zurück, solange eine Verbindung besteht."""

        return self._verbunden.is_set()

    def auf_verbindung_warten(self, timeout=5.0):
        """Wartet höchstens ``timeout`` Sekunden auf die Verbindung."""

        return self._verbunden.wait(timeout=float(timeout))

    def _nachricht_auswerten(self, text, senden, quelle):
        """Verarbeitet genau eine empfangene Textzeile."""

        nachricht = str(text).strip()

        if not nachricht:
            return

        gross = nachricht.upper()

        if gross == "ESP32_BEREIT":
            print(f"{quelle} meldet: bereit.")
            senden("PC_BEREIT")
            return

        if gross == "PING":
            senden("PONG")
            return

        teile = nachricht.split(";", 2)

        if len(teile) == 3 and teile[0].strip().casefold() == "wert":
            name = teile[1].strip()
            wert = _wert_umwandeln(teile[2])

            try:
                eintrag = self.werte.setzen(name, wert, quelle)
            except ValueError as fehler:
                print(f"Ungültiger ESP-Wert von {quelle}: {fehler}")
                senden(f"FEHLER {fehler}")
                return

            print(
                f"ESP32-Wert aktualisiert: "
                f"{eintrag['name']} = {eintrag['wert']!r} "
                f"von {quelle}"
            )
#             senden(f"EMPFANGEN WERT;{eintrag['name']};{eintrag['wert']}")  # Erzeugt eventuell Rückkopplungen bei "UNBEKANNTER_BEFEHL"            return

        steuerbefehl = _befehl_normalisieren(nachricht)

        if steuerbefehl is not None:
            self.steuerbefehle.put((steuerbefehl, quelle))
            print(
                f"ESP32-Steuerbefehl empfangen: "
                f"{gross} von {quelle}"
            )
#            senden(f"EMPFANGEN {gross}") # Verursacht mit die Rückkopplung der Fehlermeldung " 'UNBEKANNTER_BEFEHL;EMPFANGEN UNBEKANNTE"
            return

        if self.meldungen is None:
            print(
                f"Unbekannte Nachricht von {quelle}: "
                f"{nachricht!r}"
            )
            senden(f"UNBEKANNT {nachricht}")
            return

        self.werte.setzen("LETZTE_NACHRICHT", nachricht, quelle)
        self.meldungen.put((nachricht, quelle))
        print(
            f"ESP32-Kommunikationsmeldung empfangen: "
            f"{nachricht!r} von {quelle}"
        )
        senden(f"EMPFANGEN {nachricht}")


class ESP32SerielleSteuerung(_ESP32SteuerungBasis):
    """Empfängt ESP32-Befehle über eine COM-Schnittstelle."""

    def __init__(
        self,
        steuerbefehle,
        meldungen=None,
        werte=None,
        port="COM1",
        baudrate=115200,
        lese_timeout=0.2,
        wiederverbinden=True,
        wiederholzeit=2.0,
        name="ESP32-COM",
    ):
        super().__init__(steuerbefehle, meldungen, werte, name)

        self.port = str(port)
        self.baudrate = int(baudrate)
        self.lese_timeout = float(lese_timeout)
        self.wiederverbinden = bool(wiederverbinden)
        self.wiederholzeit = float(wiederholzeit)

        self._serial = None
        self._serial_lock = threading.Lock()

    def starten(self):
        """Startet den seriellen Empfangsthread."""

        if self._thread is not None and self._thread.is_alive():
            return self._thread

        self._beenden.clear()
        self._verbunden.clear()

        self._thread = threading.Thread(
            target=self._empfangsschleife,
            daemon=True,
            name="ESP32-COM-Steuerung",
        )
        self._thread.start()
        return self._thread

    def senden(self, text):
        """Sendet eine Textzeile an den ESP32.

        Gibt ``True`` zurück, wenn die Nachricht gesendet wurde.
        Ohne bestehende Verbindung wird ``False`` zurückgegeben.
        """

        with self._serial_lock:
            ser = self._serial

        if ser is None or not ser.is_open:
            return False

        try:
            with self._sende_lock:
                self._senden(ser, text)
            return True
        except Exception:
            return False

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
            self._thread.join(timeout=1.5)

    @staticmethod
    def _senden(ser, text):
        """Sendet eine mit Zeilenende abgeschlossene Nachricht."""

        ser.write(f"{text}\n".encode("utf-8"))
        ser.flush()

    def _empfangsschleife(self):
        """Öffnet den Port und liest fortlaufend Textzeilen."""

        try:
            serial, _ = _pyserial_laden()
        except RuntimeError as fehler:
            print(f"\nFEHLER ESP32-COM: {fehler}", file=sys.stderr)
            return

        while not self._beenden.is_set():
            ser = None

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
                    f"{self.name} über {self.port} mit "
                    f"{self.baudrate} Baud verbunden."
                )

                try:
                    ser.reset_input_buffer()
                except Exception:
                    pass

                self.senden("PC_BEREIT")

                while not self._beenden.is_set() and ser.is_open:
                    rohzeile = ser.readline()

                    if not rohzeile:
                        continue

                    text = rohzeile.decode(
                        "utf-8",
                        errors="replace",
                    ).rstrip("\r\n")

                    self._nachricht_auswerten(
                        text,
                        self.senden,
                        self.name,
                    )

            except (serial.SerialException, OSError) as fehler:
                if not self._beenden.is_set():
                    print(
                        f"\nFEHLER ESP32-COM auf "
                        f"{self.port}: {fehler}",
                        file=sys.stderr,
                    )

            finally:
                self._verbunden.clear()

                with self._serial_lock:
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
                    f"Neuer COM-Verbindungsversuch in "
                    f"{self.wiederholzeit:.1f} Sekunden ..."
                )
                self._beenden.wait(self.wiederholzeit)


class ESP32TCPSteuerung(_ESP32SteuerungBasis):
    """Empfängt ESP32-Befehle als TCP-Client."""

    def __init__(
        self,
        steuerbefehle,
        meldungen=None,
        werte=None,
        host="127.0.0.1",
        port=5000,
        socket_timeout=0.2,
        wiederverbinden=True,
        wiederholzeit=2.0,
        name="ESP32-TCP",
    ):
        super().__init__(steuerbefehle, meldungen, werte, name)

        self.host = str(host)
        self.port = int(port)
        self.socket_timeout = float(socket_timeout)
        self.wiederverbinden = bool(wiederverbinden)
        self.wiederholzeit = float(wiederholzeit)

        self._socket = None
        self._socket_lock = threading.Lock()

    def starten(self):
        """Startet den TCP-Client-Thread."""

        if self._thread is not None and self._thread.is_alive():
            return self._thread

        self._beenden.clear()
        self._verbunden.clear()

        self._thread = threading.Thread(
            target=self._empfangsschleife,
            daemon=True,
            name="ESP32-TCP-Steuerung",
        )
        self._thread.start()
        return self._thread

    def senden(self, text):
        """Sendet eine Textzeile an den TCP-Server.

        Gibt ``True`` zurück, wenn die Nachricht gesendet wurde.
        Ohne bestehende Verbindung wird ``False`` zurückgegeben.
        """

        with self._socket_lock:
            verbindung = self._socket

        if verbindung is None:
            return False

        try:
            with self._sende_lock:
                self._senden(verbindung, text)
            return True
        except OSError:
            return False

    def beenden(self):
        """Beendet den Thread und schließt die TCP-Verbindung."""

        self._beenden.set()

        with self._socket_lock:
            verbindung = self._socket

        if verbindung is not None:
            try:
                verbindung.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                verbindung.close()
            except OSError:
                pass

        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._thread is not threading.current_thread()
        ):
            self._thread.join(timeout=1.5)

    @staticmethod
    def _senden(verbindung, text):
        """Sendet eine mit Zeilenende abgeschlossene Nachricht."""

        verbindung.sendall(f"{text}\n".encode("utf-8"))

    def _verbindung_bearbeiten(self, verbindung):
        """Liest zeilenorientierte Nachrichten vom TCP-Server."""

        puffer = bytearray()
        verbindung.settimeout(self.socket_timeout)

        while not self._beenden.is_set():
            try:
                daten = verbindung.recv(1024)
            except socket.timeout:
                continue

            if not daten:
                raise ConnectionError(
                    "Der TCP-Server hat die Verbindung beendet."
                )

            puffer.extend(daten)

            while b"\n" in puffer:
                rohzeile, _, rest = puffer.partition(b"\n")
                puffer = bytearray(rest)

                text = rohzeile.decode(
                    "utf-8",
                    errors="replace",
                ).rstrip("\r")

                self._nachricht_auswerten(
                    text,
                    self.senden,
                    self.name,
                )

    def _empfangsschleife(self):
        """Verbindet sich wiederholt mit dem TCP-Server."""

        while not self._beenden.is_set():
            verbindung = None

            try:
                verbindung = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                )
                verbindung.settimeout(2.0)
                verbindung.connect((self.host, self.port))

                with self._socket_lock:
                    self._socket = verbindung

                self._verbunden.set()

                print(
                    f"{self.name} mit "
                    f"{self.host}:{self.port} verbunden."
                )

                self._verbindung_bearbeiten(verbindung)

            except (ConnectionError, OSError) as fehler:
                if not self._beenden.is_set():
                    print(
                        f"\nFEHLER ESP32-TCP zu "
                        f"{self.host}:{self.port}: {fehler}",
                        file=sys.stderr,
                    )

            finally:
                self._verbunden.clear()

                with self._socket_lock:
                    self._socket = None

                if verbindung is not None:
                    try:
                        verbindung.close()
                    except OSError:
                        pass

            if not self.wiederverbinden:
                break

            if not self._beenden.is_set():
                print(
                    f"Neuer TCP-Verbindungsversuch in "
                    f"{self.wiederholzeit:.1f} Sekunden ..."
                )
                self._beenden.wait(self.wiederholzeit)
