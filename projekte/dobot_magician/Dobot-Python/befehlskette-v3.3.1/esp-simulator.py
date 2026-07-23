"""TCP-Server als Ersatz für einen ESP32.

Der Simulator wartet auf den TCP-Client aus
``befehlskette_beispiel_v3_3_1.py`` und sendet eingegebene
Steuerbefehle an die gemeinsame Steuerbefehls-Queue.

Erlaubte Eingaben:
    p oder PAUSE
    w oder WEITER
    h oder HALT
    ? oder STATUS
    q oder ENDE
"""

import socket
import threading


HOST = "127.0.0.1"
PORT = 5000

BEFEHLE = {
    "p": "PAUSE",
    "pause": "PAUSE",
    "w": "WEITER",
    "weiter": "WEITER",
    "h": "HALT",
    "halt": "HALT",
    "?": "STATUS",
    "status": "STATUS",
}


def senden(verbindung, text):
    """Sendet genau eine Textzeile."""

    verbindung.sendall(f"{text}\n".encode("utf-8"))


def empfangen(verbindung, beenden):
    """Zeigt Antworten des TCP-Clients an."""

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

            text = rohzeile.decode(
                "utf-8",
                errors="replace",
            ).rstrip("\r")

            print(f"\nPC: {text}")
            print("ESP> ", end="", flush=True)

    beenden.set()


def eingaben_senden(verbindung, beenden):
    """Liest Steuerbefehle über die Tastatur ein."""

    print()
    print("Steuerbefehle:")
    print("  p / PAUSE   = Pause")
    print("  w / WEITER  = Weiter")
    print("  h / HALT    = Halt")
    print("  ? / STATUS  = Status")
    print("  q / ENDE    = Simulator beenden")

    while not beenden.is_set():
        try:
            eingabe = input("ESP> ").strip().lower()

        except (EOFError, KeyboardInterrupt):
            eingabe = "q"

        if eingabe in ("q", "ende"):
            beenden.set()
            return

        befehl = BEFEHLE.get(eingabe)

        if befehl is None:
            print("Unbekannter Befehl.")
            continue

        try:
            senden(verbindung, befehl)
            print(f"Gesendet: {befehl}")

        except OSError as fehler:
            print(f"Senden fehlgeschlagen: {fehler}")
            beenden.set()


def main():
    """Startet den TCP-Server und wartet auf einen Client."""

    beenden = threading.Event()

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

        print(f"ESP-Simulator wartet auf {HOST}:{PORT} ...")

        verbindung, adresse = server.accept()

        with verbindung:
            print(
                f"TCP-Client verbunden: "
                f"{adresse[0]}:{adresse[1]}"
            )

            senden(verbindung, "ESP32_BEREIT")

            empfangsthread = threading.Thread(
                target=empfangen,
                args=(verbindung, beenden),
                daemon=True,
                name="ESP-Simulator-Empfang",
            )
            empfangsthread.start()

            eingaben_senden(verbindung, beenden)

            try:
                verbindung.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            empfangsthread.join(timeout=1.0)

    print("ESP-Simulator beendet.")


if __name__ == "__main__":
    main()
