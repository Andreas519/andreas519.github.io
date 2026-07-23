import socket

HOST = "127.0.0.1"
PORT = 7000

print(f"COM20-Simulator verbindet sich mit {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as verbindung:
    verbindung.connect((HOST, PORT))

    print("Verbindung hergestellt.")
    print("Text eingeben; mit e beenden.\n")

    while True:
        text = input("Senden: ")

        if text.lower() == "e":
            print("Programm beendet.")
            break

        verbindung.sendall((text + "\n").encode("utf-8"))

        daten = verbindung.recv(1024)

        if not daten:
            print("Die Gegenstelle hat die Verbindung beendet.")
            break

        print("Antwort:", daten.decode("utf-8").rstrip())
