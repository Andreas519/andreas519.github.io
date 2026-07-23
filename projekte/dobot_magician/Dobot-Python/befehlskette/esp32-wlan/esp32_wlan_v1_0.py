"""WLAN-Steuerbefehle von einem ESP32 empfangen.

Version 1.0

Der PC arbeitet als TCP-Server.
Ein ESP32 verbindet sich als TCP-Client mit dem PC.

Der WLAN-Thread greift niemals auf die Dobot-API zu.
Er schreibt nur Steuerbefehle in eine gemeinsame queue.Queue.

Erkannte Zeilen:
    P oder PAUSE
    W oder WEITER
    H oder HALT
    ? oder STATUS
"""

import socket
import sys
import threading


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
        f"esp32_wlan_v1_0.py Version {VERSION} "
        f"vom {VERSIONSDATUM}"
    )


def lokale_ipv4_adressen():
    """Ermittelt die bekannten lokalen IPv4-Adressen des PCs."""

    adressen = set()

    try:
        hostname = socket.gethostname()

        for eintrag in socket.getaddrinfo(
            hostname,
            None,
            family=socket.AF_INET,
        ):
            adresse = eintrag[4][0]

            if adresse and not adresse.startswith("127."):
                adressen.add(adresse)

    except OSError:
        pass

    # Häufig zuverlässiger für die aktuell verwendete Netzwerkschnittstelle.
    try:
        test_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        try:
            test_socket.connect(("8.8.8.8", 80))
            adresse = test_socket.getsockname()[0]

            if adresse and not adresse.startswith("127."):
                adressen.add(adresse)

        finally:
            test_socket.close()

    except OSError:
        pass

    return sorted(adressen)


def _befehl_normalisieren(text):
    """Übersetzt eine Textzeile in p, w, h oder ?."""

    return BEFEHLE.get(str(text).strip().lower())


class ESP32WLANSteuerung:
    """Empfängt Steuerbefehle über einen TCP-Server-Thread.

    Die Klasse ist zunächst für genau einen gleichzeitig verbundenen
    ESP32 vorgesehen. Nach einem Verbindungsabbruch kann sich derselbe
    oder ein anderer ESP32 erneut verbinden.
    """

    def __init__(
        self,
        steuerbefehle,
        host="0.0.0.0",
        port=8765,
        name="ESP32-WLAN",
        socket_timeout=0.5,
    ):
        self.steuerbefehle = steuerbefehle
        self.host = str(host)
        self.port = int(port)
        self.name = str(name)
        self.socket_timeout = float(socket_timeout)

        self._beenden = threading.Event()
        self._server_bereit = threading.Event()
        self._client_verbunden = threading.Event()

        self._thread = None
        self._server_socket = None
        self._client_socket = None
        self._socket_lock = threading.Lock()

    def starten(self):
        """Startet den TCP-Server als Daemon-Thread."""

        if self._thread is not None and self._thread.is_alive():
            return self._thread

        self._beenden.clear()
        self._server_bereit.clear()
        self._client_verbunden.clear()

        self._thread = threading.Thread(
            target=self._server_schleife,
            daemon=True,
            name="ESP32-WLAN-Steuerung",
        )

        self._thread.start()

        return self._thread

    def beenden(self):
        """Beendet den Server-Thread und schließt alle Sockets."""

        self._beenden.set()

        with self._socket_lock:
            client = self._client_socket
            server = self._server_socket

        for sock in (client, server):
            if sock is None:
                continue

            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                sock.close()
            except OSError:
                pass

        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._thread is not threading.current_thread()
        ):
            self._thread.join(timeout=1.5)

    def server_ist_bereit(self):
        """Gibt True zurück, sobald der TCP-Server lauscht."""

        return self._server_bereit.is_set()

    def auf_server_warten(self, timeout=5.0):
        """Wartet höchstens ``timeout`` Sekunden auf den Serverstart."""

        return self._server_bereit.wait(float(timeout))

    def client_ist_verbunden(self):
        """Gibt True zurück, wenn gerade ein ESP32 verbunden ist."""

        return self._client_verbunden.is_set()

    def auf_client_warten(self, timeout=10.0):
        """Wartet höchstens ``timeout`` Sekunden auf einen ESP32."""

        return self._client_verbunden.wait(float(timeout))

    def _senden(self, client, text):
        """Sendet eine Textzeile an den verbundenen ESP32."""

        client.sendall(
            f"{text}\n".encode("utf-8")
        )

    def _nachricht_verarbeiten(
        self,
        client,
        text,
        client_adresse,
    ):
        """Verarbeitet genau eine empfangene Textzeile."""

        nachricht = text.strip()

        if not nachricht:
            return

        gross = nachricht.upper()

        if gross == "ESP32_BEREIT":
            print(
                f"{self.name} meldet: bereit "
                f"({client_adresse[0]})."
            )
            self._senden(client, "PC_BEREIT")
            return

        if gross == "PING":
            self._senden(client, "PONG")
            return

        steuerbefehl = _befehl_normalisieren(nachricht)

        if steuerbefehl is None:
            print(
                f"Unbekannte WLAN-Nachricht von "
                f"{client_adresse[0]}: {nachricht!r}"
            )
            self._senden(
                client,
                f"UNBEKANNT {nachricht}",
            )
            return

        quelle = (
            f"{self.name} "
            f"({client_adresse[0]})"
        )

        self.steuerbefehle.put(
            (steuerbefehl, quelle)
        )

        print(
            f"WLAN-Steuerbefehl empfangen: "
            f"{nachricht.upper()} "
            f"von {client_adresse[0]}"
        )

        # Bestätigt nur den Empfang durch den PC.
        self._senden(
            client,
            f"EMPFANGEN {nachricht.upper()}",
        )

    def _client_bearbeiten(
        self,
        client,
        client_adresse,
    ):
        """Liest zeilenorientierte Nachrichten eines ESP32."""

        puffer = bytearray()

        client.settimeout(self.socket_timeout)

        self._client_verbunden.set()

        print(
            f"{self.name} verbunden: "
            f"{client_adresse[0]}:{client_adresse[1]}"
        )

        self._senden(client, "PC_BEREIT")

        try:
            while not self._beenden.is_set():
                try:
                    daten = client.recv(1024)

                except socket.timeout:
                    continue

                if not daten:
                    break

                puffer.extend(daten)

                while b"\n" in puffer:
                    rohzeile, _, rest = puffer.partition(b"\n")
                    puffer = bytearray(rest)

                    text = rohzeile.decode(
                        "utf-8",
                        errors="replace",
                    ).rstrip("\r")

                    self._nachricht_verarbeiten(
                        client,
                        text,
                        client_adresse,
                    )

        finally:
            self._client_verbunden.clear()

            print(
                f"{self.name} getrennt: "
                f"{client_adresse[0]}:{client_adresse[1]}"
            )

    def _server_schleife(self):
        """Öffnet den TCP-Server und akzeptiert wiederholt Clients."""

        server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server.settimeout(self.socket_timeout)

        with self._socket_lock:
            self._server_socket = server

        try:
            server.bind((self.host, self.port))
            server.listen(1)

            self._server_bereit.set()

            print(
                f"ESP32-WLAN-Server wartet auf "
                f"{self.host}:{self.port}."
            )

            while not self._beenden.is_set():
                try:
                    client, client_adresse = server.accept()

                except socket.timeout:
                    continue

                except OSError:
                    if self._beenden.is_set():
                        break
                    raise

                with self._socket_lock:
                    self._client_socket = client

                try:
                    self._client_bearbeiten(
                        client,
                        client_adresse,
                    )

                except (
                    ConnectionError,
                    OSError,
                ) as fehler:
                    if not self._beenden.is_set():
                        print(
                            f"\nFEHLER WLAN-Verbindung: "
                            f"{fehler}",
                            file=sys.stderr,
                        )

                finally:
                    with self._socket_lock:
                        self._client_socket = None

                    try:
                        client.close()
                    except OSError:
                        pass

        except OSError as fehler:
            print(
                f"\nFEHLER WLAN-Server auf "
                f"{self.host}:{self.port}: {fehler}",
                file=sys.stderr,
            )

        finally:
            self._server_bereit.clear()
            self._client_verbunden.clear()

            with self._socket_lock:
                self._server_socket = None
                self._client_socket = None

            try:
                server.close()
            except OSError:
                pass
