import socket
import threading

HOST = "127.0.0.1"
PORT = 7000


def server_befehle_empfangen(verbindung):
    """Empfängt jederzeit Befehle vom Server."""
    while True:
        try:
            daten = verbindung.recv(1024)

            if not daten:
                print("\nServer hat die Verbindung beendet.")
                break

            befehl = daten.decode("utf-8").rstrip()

            if befehl == "ENDE":
                print("\nServer hat ENDE gesendet.")
                break

            print(f"\nBefehl vom Server: {befehl}")

        except (ConnectionResetError, OSError):
            break


print(f"TCP-Client verbindet sich mit {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as verbindung:
    verbindung.connect((HOST, PORT))

    print("Verbindung hergestellt.")
    print("Nachrichten eingeben; mit e beenden.\n")

    empfangs_thread = threading.Thread(
        target=server_befehle_empfangen,
        args=(verbindung,),
        daemon=True,
    )
    empfangs_thread.start()

    while True:
        nachricht = input("Nachricht an Server: ")

        if nachricht.lower() == "e":
            print("Client wird beendet.")
            break

        try:
            verbindung.sendall((nachricht + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Verbindung zum Server ist beendet.")
            break
