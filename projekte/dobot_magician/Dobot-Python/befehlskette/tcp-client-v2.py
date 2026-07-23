import socket
import threading

HOST = "127.0.0.1"
PORT = 7000

programm_beenden = threading.Event()
sende_sperre = threading.Lock()
schalter_sperre = threading.Lock()
schalter_geaendert = threading.Event()

schalter = {
    "zustand": False,
}


def senden(verbindung, text):
    """Sendet eine Textzeile an den Server."""
    try:
        with sende_sperre:
            verbindung.sendall((text + "\n").encode("utf-8"))
    except (BrokenPipeError, ConnectionResetError, OSError):
        programm_beenden.set()


def schalter_setzen(zustand):
    """Setzt den Zustand des virtuellen Schalters."""
    with schalter_sperre:
        schalter["zustand"] = zustand

    schalter_geaendert.set()


def schalter_umschalten():
    """Kehrt den Zustand des virtuellen Schalters um."""
    with schalter_sperre:
        schalter["zustand"] = not schalter["zustand"]

    schalter_geaendert.set()


def schalter_thread(verbindung):
    """Zeigt Änderungen des virtuellen Schalters an."""
    schalter_geaendert.set()

    while not programm_beenden.is_set():
        if not schalter_geaendert.wait(timeout=0.2):
            continue

        schalter_geaendert.clear()

        with schalter_sperre:
            zustand = schalter["zustand"]

        text = "EIN" if zustand else "AUS"
        print(f"\n[CLIENT-SCHALTER] {text}")
        senden(verbindung, f"SCHALTERSTATUS {text}")


def server_empfangen(verbindung):
    """Empfängt Nachrichten und Befehle vom Server."""
    try:
        with verbindung.makefile("r", encoding="utf-8", newline="\n") as eingang:
            for zeile in eingang:
                if programm_beenden.is_set():
                    break

                text = zeile.strip()
                befehl = text.upper()

                if befehl == "SCHALTER EIN":
                    schalter_setzen(True)

                elif befehl == "SCHALTER AUS":
                    schalter_setzen(False)

                elif befehl == "SCHALTER UMSCHALTEN":
                    schalter_umschalten()

                elif befehl == "ENDE":
                    print("\nServer beendet die Verbindung.")
                    programm_beenden.set()
                    break

                else:
                    print(f"\nVom Server empfangen: {text}")

    except (ConnectionResetError, OSError):
        print("\nDie Verbindung zum Server wurde beendet.")
        programm_beenden.set()


print(f"TCP-Client verbindet sich mit {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as verbindung:
    verbindung.connect((HOST, PORT))

    print("Verbindung hergestellt.")
    print()
    print("Befehle:")
    print("  led ein        -> LED beim Server einschalten")
    print("  led aus        -> LED beim Server ausschalten")
    print("  led blink      -> LED beim Server blinken lassen")
    print("  schalter ein   -> eigenen Schalter einschalten")
    print("  schalter aus   -> eigenen Schalter ausschalten")
    print("  schalter um    -> eigenen Schalter umschalten")
    print("  beliebiger Text wird an den Server gesendet")
    print("  e              -> beide Programme beenden")
    print()

    empfang = threading.Thread(
        target=server_empfangen,
        args=(verbindung,),
        daemon=True,
    )
    empfang.start()

    schalter_arbeiter = threading.Thread(
        target=schalter_thread,
        args=(verbindung,),
        daemon=True,
    )
    schalter_arbeiter.start()

    while not programm_beenden.is_set():
        try:
            eingabe = input("Client > ").strip()
        except (EOFError, KeyboardInterrupt):
            eingabe = "e"

        if not eingabe:
            continue

        befehl = eingabe.lower()

        if befehl == "e":
            senden(verbindung, "ENDE")
            programm_beenden.set()

        elif befehl == "led ein":
            senden(verbindung, "LED EIN")

        elif befehl == "led aus":
            senden(verbindung, "LED AUS")

        elif befehl in ("led blink", "led blinken"):
            senden(verbindung, "LED BLINK")

        elif befehl == "schalter ein":
            schalter_setzen(True)

        elif befehl == "schalter aus":
            schalter_setzen(False)

        elif befehl in ("schalter um", "schalter umschalten"):
            schalter_umschalten()

        else:
            senden(verbindung, eingabe)

    programm_beenden.set()
    schalter_geaendert.set()
    empfang.join(timeout=1.0)
    schalter_arbeiter.join(timeout=1.0)

print("TCP-Client beendet.")
