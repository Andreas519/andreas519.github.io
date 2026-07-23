"""Testet nur die ESP32-WLAN-Verbindung, ohne Dobot."""

import queue

from esp32_wlan_v1_0 import (
    ESP32WLANSteuerung,
    lokale_ipv4_adressen,
)


WLAN_HOST = "0.0.0.0"
WLAN_PORT = 8765


print("Lokale IPv4-Adressen dieses PCs:")

adressen = lokale_ipv4_adressen()

if adressen:
    for adresse in adressen:
        print(f"  {adresse}")
else:
    print("  Keine Adresse automatisch ermittelt.")

print()
print(
    "Trage eine dieser Adressen im ESP32-Programm "
    "als PC_IP ein."
)


steuerbefehle = queue.Queue()

wlan = ESP32WLANSteuerung(
    steuerbefehle=steuerbefehle,
    host=WLAN_HOST,
    port=WLAN_PORT,
    name="ESP32-WLAN-Test",
)

wlan.starten()

try:
    if not wlan.auf_server_warten(5.0):
        raise RuntimeError(
            "Der WLAN-Server konnte nicht gestartet werden."
        )

    print()
    print(
        f"Der PC wartet auf Port {WLAN_PORT} "
        "auf den ESP32."
    )
    print(
        "Beim ersten Start kann die Windows-Firewall "
        "nach einer Freigabe fragen."
    )
    print("Beenden mit Strg+C.")

    if not wlan.auf_client_warten(15.0):
        print()
        print(
            "Noch kein ESP32 verbunden. "
            "Der Server wartet weiter."
        )

    while True:
        befehl, quelle = steuerbefehle.get()

        print(
            f"Empfangen von {quelle}: {befehl!r}"
        )

except KeyboardInterrupt:
    print("\nWLAN-Test beendet.")

finally:
    wlan.beenden()
