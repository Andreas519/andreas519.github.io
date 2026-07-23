import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 7000

programm_beenden = threading.Event()
sende_sperre = threading.Lock()
led_sperre = threading.Lock()

led = {
    "modus": "BLINK",   # BLINK, EIN oder AUS
    "zustand": False,
}


def senden(verbindung, text):
    """Sendet eine Textzeile an den Client."""
    try:
        with sende_sperre:
            verbindung.sendall((text + "\n").encode("utf-8"))
    except (BrokenPipeError, ConnectionResetError, OSError):
        programm_beenden.set()


def led_modus_setzen(modus):
    """Ändert den Betriebsmodus der virtuellen LED."""
    with led_sperre:
        led["modus"] = modus

        if modus == "EIN":
            led["zustand"] = True
        elif modus == "AUS":
            led["zustand"] = False


def led_thread():
    """Lässt die virtuelle LED blinken oder zeigt ihren Zustand an."""
    letzter_zustand = None

    while not programm_beenden.is_set():
        with led_sperre:
            modus = led["modus"]

            if modus == "BLINK":
                led["zustand"] = not led["zustand"]

            zustand = led["zustand"]

        if zustand != letzter_zustand or modus == "BLINK":
            text = "EIN" if zustand else "AUS"
            print(f"\n[SERVER-LED] {text}  (Modus: {modus})")
            letzter_zustand = zustand

        if modus == "BLINK":
            programm_beenden.wait(0.5)
        else:
            programm_beenden.wait(0.1)


def client_empfangen(verbindung):
    """Empfängt Nachrichten und Befehle vom Client."""
    try:
        with verbindung.makefile("r", encoding="utf-8", newline="\n") as eingang:
            for zeile in eingang:
                if programm_beenden.is_set():
                    break

                text = zeile.strip()
                befehl = text.upper()

                if befehl == "LED EIN":
                    led_modus_setzen("EIN")
                    print("\nClient schaltet die Server-LED EIN.")

                elif befehl == "LED AUS":
                    led_modus_setzen("AUS")
                    print("\nClient schaltet die Server-LED AUS.")

                elif befehl == "LED BLINK":
                    led_modus_setzen("BLINK")
                    print("\nClient schaltet die Server-LED auf BLINKEN.")

                elif befehl == "ENDE":
                    print("\nClient beendet die Verbindung.")
                    programm_beenden.set()
                    break

                else:
                    print(f"\nVom Client empfangen: {text}")

    except (ConnectionResetError, OSError):
        print("\nDie Verbindung zum Client wurde beendet.")
        programm_beenden.set()


print(f"TCP-Server wartet auf {HOST}:{PORT} ...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    verbindung, adresse = server.accept()

    with verbindung:
        print(f"Client verbunden: {adresse}")
        print()
        print("Befehle:")
        print("  schalter ein   -> Schalter beim Client einschalten")
        print("  schalter aus   -> Schalter beim Client ausschalten")
        print("  schalter um    -> Schalter beim Client umschalten")
        print("  led ein        -> eigene LED dauerhaft einschalten")
        print("  led aus        -> eigene LED dauerhaft ausschalten")
        print("  led blink      -> eigene LED blinken lassen")
        print("  beliebiger Text wird an den Client gesendet")
        print("  e              -> beide Programme beenden")
        print()

        empfang = threading.Thread(
            target=client_empfangen,
            args=(verbindung,),
            daemon=True,
        )
        empfang.start()

        led_arbeiter = threading.Thread(
            target=led_thread,
            daemon=True,
        )
        led_arbeiter.start()

        while not programm_beenden.is_set():
            try:
                eingabe = input("Server > ").strip()
            except (EOFError, KeyboardInterrupt):
                eingabe = "e"

            if not eingabe:
                continue

            befehl = eingabe.lower()

            if befehl == "e":
                senden(verbindung, "ENDE")
                programm_beenden.set()

            elif befehl == "schalter ein":
                senden(verbindung, "SCHALTER EIN")

            elif befehl == "schalter aus":
                senden(verbindung, "SCHALTER AUS")

            elif befehl in ("schalter um", "schalter umschalten"):
                senden(verbindung, "SCHALTER UMSCHALTEN")

            elif befehl == "led ein":
                led_modus_setzen("EIN")

            elif befehl == "led aus":
                led_modus_setzen("AUS")

            elif befehl in ("led blink", "led blinken"):
                led_modus_setzen("BLINK")

            else:
                senden(verbindung, eingabe)

        programm_beenden.set()
        empfang.join(timeout=1.0)
        led_arbeiter.join(timeout=1.0)

print("TCP-Server beendet.")
