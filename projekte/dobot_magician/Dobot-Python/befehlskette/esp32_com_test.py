"""Testet nur die ESP32-COM-Verbindung, ohne Dobot."""

import queue

from esp32_seriell_v1_0 import (
    ESP32SerielleSteuerung,
    serielle_ports_auflisten,
)


ESP32_PORT = "COM11"
ESP32_BAUDRATE = 115200


print("Gefundene COM-Ports:")

for port in serielle_ports_auflisten():
    print(
        f'  {port["geraet"]}: '
        f'{port["beschreibung"]}'
    )


steuerbefehle = queue.Queue()

esp32 = ESP32SerielleSteuerung(
    steuerbefehle=steuerbefehle,
    port=ESP32_PORT,
    baudrate=ESP32_BAUDRATE,
)

esp32.starten()

try:
    if not esp32.auf_verbindung_warten(5.0):
        print(
            f"Keine Verbindung über {ESP32_PORT}. "
            "Der Thread versucht es weiter."
        )

    print()
    print("ESP32-Befehle werden jetzt angezeigt.")
    print("Beenden mit Strg+C.")

    while True:
        befehl, quelle = steuerbefehle.get()
        print(
            f"Empfangen von {quelle}: {befehl!r}"
        )

except KeyboardInterrupt:
    print("\nTest beendet.")

finally:
    esp32.beenden()
