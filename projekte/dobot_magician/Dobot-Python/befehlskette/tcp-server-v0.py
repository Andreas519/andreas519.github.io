import socket

HOST = "127.0.0.1"
PORT = 7000

print(f"COM21-Simulator wartet auf {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    verbindung, adresse = server.accept()

    with verbindung:
        print("Verbindung hergestellt.")
        print("Mit Strg+C beenden.\n")

        while True:
            daten = verbindung.recv(1024)

            if not daten:
                print("Die Gegenstelle hat die Verbindung beendet.")
                break

            text = daten.decode("utf-8").rstrip()
            print(f"Empfangen: {text}")

            antwort = f"COM21 bestätigt: {text}\n"
            verbindung.sendall(antwort.encode("utf-8"))
