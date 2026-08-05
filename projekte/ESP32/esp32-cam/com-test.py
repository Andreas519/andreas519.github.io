import time
import serial
from serial.tools import list_ports


PORT = "COM6"
BAUDRATE = 115200
TESTBEFEHL = "STATUS"


def com_ports_anzeigen():
    print("Verfügbare serielle Schnittstellen:")

    ports = list(list_ports.comports())

    if not ports:
        print(" ❌ Keine COM-Schnittstelle gefunden. ⚠️")
        return

    for port in ports:
        print(f" ✅ {port.device}: {port.description}")


def main():
    com_ports_anzeigen()
    print()

    verbindung = None

    try:
        verbindung = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,
            write_timeout=1,
        )

        print(f"{PORT} wurde mit {BAUDRATE} Baud geöffnet.")

        # Viele Mikrocontroller starten beim Öffnen der Schnittstelle neu.
        time.sleep(7)

        # Bereits vorhandene Daten verwerfen.
        verbindung.reset_input_buffer()

        nachricht = TESTBEFEHL + "\n"
        verbindung.write(nachricht.encode("utf-8"))

        print(f"Gesendet: {TESTBEFEHL}")
        print("Empfangene Daten:")

        startzeit = time.time()
        verbindung.reset_input_buffer()
        while time.time() - startzeit < 59:
            if verbindung.in_waiting > 0:
                antwort = verbindung.readline().decode(
                    "utf-8",
                    errors="replace",
                ).strip()

                if antwort:
                    print(f"  {antwort}")

        print("Empfangstest beendet.")

    except serial.SerialException as fehler:
        print(f"Fehler an {PORT}: {fehler}")
        print("Möglicherweise wird COM6 bereits von einem anderen Programm benutzt.")

    except KeyboardInterrupt:
        print("\nProgramm wurde abgebrochen.")

    finally:
        if verbindung is not None and verbindung.is_open:
            verbindung.close()
            print(f"{PORT} wurde geschlossen.")


if __name__ == "__main__":
    main()