import socket
import threading

HOST = "127.0.0.1"
PORT = 7000


def befehle_senden(verbindung):
    """Liest Befehle von der Tastatur und sendet sie an den Client."""
    while True:
        try:
            befehl = input("Befehl an Client: ")

            if befehl.lower() == "e":
                verbindung.sendall(b"ENDE\n")
                print("Server wird beendet.")
                verbindung.shutdown(socket.SHUT_RDWR)
                verbindung.close()
                break

            verbindung.sendall((befehl + "\n").encode("utf-8"))

        except (BrokenPipeError, ConnectionResetError, OSError):
            break


print(f"TCP-Server wartet auf {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    verbindung, adresse = server.accept()

    print(f"Client verbunden: {adresse}")
    print("Befehle eingeben; mit e beenden.\n")

    sende_thread = threading.Thread(
        target=befehle_senden,
        args=(verbindung,),
        daemon=True,
    )
    sende_thread.start()

    try:
        while True:
            daten = verbindung.recv(1024)

            if not daten:
                print("Client hat die Verbindung beendet.")
                break

            text = daten.decode("utf-8").rstrip()
            print(f"\nVom Client empfangen: {text}")

    except (ConnectionResetError, OSError):
        print("Verbindung wurde beendet.")
