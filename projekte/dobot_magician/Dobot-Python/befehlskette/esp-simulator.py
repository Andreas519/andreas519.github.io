import serial


SIMULATOR_PORT = "COM25"
SIMULATOR_BAUDRATE = 115200


befehle = {
    "1": "PAUSE",
    "2": "WEITER",
    "3": "HALT",
    "4": "STATUS",
    "5": "ESP32_BEREIT",
}


with serial.Serial(
    SIMULATOR_PORT,
    SIMULATOR_BAUDRATE,
    timeout=0.2,
) as verbindung:

    print(
        f"ESP32-Simulator über "
        f"{SIMULATOR_PORT} verbunden."
    )

    while True:
        print()
        print("1 = PAUSE")
        print("2 = WEITER")
        print("3 = HALT")
        print("4 = STATUS")
        print("5 = ESP32_BEREIT")
        print("0 = Ende")

        auswahl = input("Auswahl: ").strip()

        if auswahl == "0":
            break

        if auswahl not in befehle:
            print("Unbekannte Eingabe.")
            continue

        nachricht = befehle[auswahl]

        verbindung.write(
            f"{nachricht}\n".encode("utf-8")
        )
        verbindung.flush()

        print(f"Gesendet: {nachricht}")

        antwort = verbindung.readline().decode(
            "utf-8",
            errors="replace",
        ).strip()

        if antwort:
            print(f"Antwort vom Steuerprogramm: {antwort}")