"""Testprogramm für Dobot und ESP32.

COM_MODUS:
    "serial"  USB-COM-Verbindung zum ESP32
    "tcp"     TCP-Verbindung zum ESP-Simulator

Neue Befehle:
    warte_bis
    marke
    gehe_zu_befehl
    home
    geschwindigkeit
    wenn_wert
    warte_bis_wert
    wert_anzeigen
    esp_senden

Weitere Funktionen:
    vollständige Prüfung vor der Dobot-Verbindung
    Vergleichsoperatoren ==, !=, <, <=, >, >=
    laufende Zustandsmeldungen an ESP32 oder Simulator

    esp_senden überträgt frei wählbare Texte an den ESP32
    Startmenü mit Start, Abbruch und Sendetest
    Im Sendetest werden Texte bis zur Eingabe q übertragen

ESP-Werte werden als Textzeilen empfangen, zum Beispiel:
    WERT;POSITION;POS_A
    WERT;TEMPERATUR;23.7
"""

from pathlib import Path
import os
import queue
import sys


# ------------------------------------------------------------
# Diese Zeilen anpassen
# ------------------------------------------------------------

COM_MODUS = "tcp"  # "serial" oder "tcp"

DOBOT_PORT = "COM10"
DOBOT_BAUDRATE = 115200

ESP32_COM_AKTIV = False
ESP32_TCP_AKTIV = False

if COM_MODUS == "serial":
    ESP32_COM_AKTIV = True
    ESP32_COM_PORT = "COM26"
    ESP32_COM_BAUDRATE = 115200
    ESP32_COM_VERBINDUNGS_TIMEOUT = 5.0

elif COM_MODUS == "tcp":
    ESP32_TCP_AKTIV = True
    ESP32_TCP_HOST = "127.0.0.1"
    ESP32_TCP_PORT = 5000
    ESP32_TCP_VERBINDUNGS_TIMEOUT = 5.0

else:
    raise ValueError("COM_MODUS muss 'serial' oder 'tcp' sein.")

STANDARD_PAUSE_MS = 500
TIMEOUT_SEKUNDEN = 90.0
MAX_SCHRITTE = 1000

PROGRAMM_VERSION = "3.3.5.2"
PROGRAMM_VERSIONSDATUM = "26.07.2026, 10:32 Uhr"
ERWARTETE_BEFEHLSKETTENVERSION = "3.3.5.1"
ERWARTETE_ESP32_MODULVERSION = "1.4.2"


# Die Meldung FREIGABE wird im TCP-Simulator einfach eingetippt.
# Im seriellen Betrieb muss der ESP32 die Zeile FREIGABE senden.
befehle = [
    ("geschwindigkeit", 40, 40, "Geschwindigkeit und Beschleunigung auf 40 % setzen", 0),
    ("home", "HOME-Fahrt ausführen", 500),
    ("marke", "auf_freigabe_warten"),
    ("warte_bis", "FREIGABE", "Warte auf FREIGABE vom COM-/TCP-Client", None),
    ("wert_anzeigen", "TEMPERATUR", "Vom ESP gespeicherte Temperatur anzeigen"),
    ("wenn_wert", "TEMPERATUR", ">=", 30, ("wert_anzeigen", "TEMPERATUR", "Temperaturwarnung: mindestens 30 °C"), ("wert_anzeigen", "TEMPERATUR", "Temperatur liegt unter 30 °C")),
    ("wert_anzeigen", "POSITION", "Vom ESP gespeicherte Position anzeigen"),
    ("wenn_wert", "POSITION", "==", "POS_A", ("fahre_zu", 240, 140, 70, 0, "Fahre zu Position A", 500), ("gehe_zu_befehl", "POS_B")),
    ("gehe_zu_befehl", "POSITION_ENDE"),
    ("marke", "POS_B"),
    ("fahre_zu", 180, 160, 50, 0, "Fahre zu Position B", 500),
    ("marke", "POSITION_ENDE"),
    ("gehe_zu_befehl", "auf_freigabe_warten"),
]

# Weitere mögliche Befehle:
# ("warte_bis_wert", "TASTER", "==", 1, "Warte auf gedrückten Taster", None)
# ("wenn_wert", "TEMPERATUR", "<", 10, Wahr-Befehl, Falsch-Befehl)
# ("esp_senden", "LED_GELB_EIN", "Gelbe LED am ESP32 einschalten")
# ("esp_senden", "DISPLAY;Dobot arbeitet", "Text an ESP32-Display senden")


# ------------------------------------------------------------
# Ab hier nichts mehr ändern
# ------------------------------------------------------------

PROJEKTORDNER = Path(__file__).resolve().parent
HAUPTORDNER = PROJEKTORDNER.parent
SDK_ORDNER = HAUPTORDNER / "sdk64"
DLL_DATEI = SDK_ORDNER / "DobotDll.dll"


if (
    ESP32_COM_AKTIV
    and DOBOT_PORT.upper() == ESP32_COM_PORT.upper()
):
    raise ValueError(
        "Dobot und ESP32 benötigen verschiedene COM-Ports."
    )

if not SDK_ORDNER.exists():
    raise FileNotFoundError(
        f"Der SDK-Ordner wurde nicht gefunden:\n{SDK_ORDNER}"
    )

if not DLL_DATEI.exists():
    raise FileNotFoundError(
        f"Die Dobot-DLL wurde nicht gefunden:\n{DLL_DATEI}"
    )

# Der Ordner des gestarteten Programms ist bereits automatisch im
# Python-Suchpfad. Ergänzt wird nur der übergeordnete Ordner für sdk64.
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))


dll_verzeichnis_handle = None

if os.name == "nt":
    dll_verzeichnis_handle = os.add_dll_directory(str(SDK_ORDNER))


from sdk64 import DobotDllType as dType

from befehlskette_v3_3_5 import (
    VERSION as BEFEHLSKETTENVERSION,
    VERSIONSDATUM as BEFEHLSKETTENDATUM,
    ZUSTAND_HALT,
    befehlskette_pruefen,
    befehlskette_anzeigen,
    befehlskette_ausfuehren_steuerbar,
)

from esp32_kommunikation_v1_4 import (
    VERSION as ESP32_MODULVERSION,
    ESP32SerielleSteuerung,
    ESPWerteSpeicher,
    ESP32TCPSteuerung,
    serielle_ports_auflisten,
)


if BEFEHLSKETTENVERSION != ERWARTETE_BEFEHLSKETTENVERSION:
    raise RuntimeError(
        "Versionskonflikt beim Befehlskettenmodul: "
        f"erwartet {ERWARTETE_BEFEHLSKETTENVERSION}, "
        f"geladen {BEFEHLSKETTENVERSION}."
    )

if ESP32_MODULVERSION != ERWARTETE_ESP32_MODULVERSION:
    raise RuntimeError(
        "Versionskonflikt beim ESP32-Kommunikationsmodul: "
        f"erwartet {ERWARTETE_ESP32_MODULVERSION}, "
        f"geladen {ESP32_MODULVERSION}."
    )


# Die gesamte Befehlskette wird geprüft, bevor eine Verbindung
# zum Dobot aufgebaut wird.
programm = befehlskette_pruefen(
    befehle,
    standard_pause_ms=STANDARD_PAUSE_MS,
)

print(
    f"Testprogramm Version {PROGRAMM_VERSION} "
    f"vom {PROGRAMM_VERSIONSDATUM}"
)
print(f"Kommunikationsmodus: {COM_MODUS}")
print(
    f"Befehlskettenmodul Version "
    f"{BEFEHLSKETTENVERSION} vom {BEFEHLSKETTENDATUM}"
)
print(f"ESP32-Kommunikationsmodul Version {ESP32_MODULVERSION}")
print("Programmordner:", PROJEKTORDNER)
print("Hauptordner:   ", HAUPTORDNER)
print("SDK-Ordner:    ", SDK_ORDNER)
print("DobotDllType:  ", Path(dType.__file__).resolve())
print("DLL-Datei:     ", DLL_DATEI)
print(f"\nBefehlskette erfolgreich geprüft: {len(programm['befehle'])} Befehle.")
befehlskette_anzeigen(programm)


steuerbefehle = queue.Queue()
kommunikationsmeldungen = queue.Queue()
esp_werte = ESPWerteSpeicher()

esp32 = None
api = None
dobot_verbunden = False
abschlussgrund = None


def esp32_abschluss_melden(grund):
    """Informiert ESP32 oder Simulator über das Programmende."""

    if esp32 is None:
        return False

    nachricht = f"PROGRAMM_BEENDET;{grund}"
    gesendet = esp32.senden(nachricht)

    if gesendet:
        print(f"ESP32/Simulator informiert: {nachricht}")
    else:
        print("ESP32/Simulator konnte nicht informiert werden.")

    return gesendet


def queue_leeren(daten_queue):
    """Entfernt alle vorhandenen Einträge aus einer Queue."""

    anzahl = 0

    while True:
        try:
            daten_queue.get_nowait()
            anzahl += 1
        except queue.Empty:
            return anzahl


def esp32_senden_testen():
    """Sendet Texte an den ESP32, bis ``q`` eingegeben wird."""

    if esp32 is None:
        print("\nDie ESP32-Kommunikation ist nicht aktiviert.")
        return

    alte_steuerbefehle = queue_leeren(steuerbefehle)
    alte_meldungen = queue_leeren(kommunikationsmeldungen)

    print()
    print("=" * 64)
    print("Texte an den ESP32 senden")
    print("=" * 64)
    print("Jede Eingabe wird als vollständige Textzeile gesendet.")
    print("Antworten und Meldungen des ESP32 zeigt der Empfangsthread an.")
    print("Mit q und Enter geht es zurück zum Startmenü.")

    if alte_steuerbefehle or alte_meldungen:
        print(
            f"Vor dem Test entfernt: {alte_steuerbefehle} "
            f"Steuerbefehl(e), {alte_meldungen} Meldung(en)."
        )

    while True:
        text = input("Text an ESP32 (q = zurück): ").strip()

        if text.casefold() == "q":
            break

        if not text:
            print("Leere Eingaben werden nicht gesendet.")
            continue

        if esp32.senden(text):
            print(f"Gesendet: {text!r}")
        else:
            print(
                "Der Text konnte nicht gesendet werden. "
                "Bitte die ESP32-Verbindung prüfen."
            )

    anzahl_steuerbefehle = queue_leeren(steuerbefehle)
    anzahl_meldungen = queue_leeren(kommunikationsmeldungen)

    print()
    print("Sendetest beendet. Rückkehr zum Startmenü.")
    print(
        f"Entfernt: {anzahl_steuerbefehle} Steuerbefehl(e), "
        f"{anzahl_meldungen} Kommunikationsmeldung(en)."
    )
    print("Dauerhaft gespeicherte ESP32-Werte bleiben erhalten.")


def startmenue_anzeigen():
    """Fragt Start, Abbruch oder ESP32-Sendetest ab."""

    while True:
        eingabe = input(
            "\nBefehlskette starten?\n"
            "  s = Start\n"
            "  a = Abbruch\n"
            "  t = Testen\n"
            "Eingabe: "
        ).strip().lower()

        if eingabe in ("s", "start"):
            return True

        if eingabe in ("a", "abbruch"):
            return False

        if eingabe in ("t", "test"):
            esp32_senden_testen()
            continue

        print("Ungültige Eingabe. Bitte 's', 'a' oder 't' eingeben.")


try:
    if ESP32_COM_AKTIV:
        print("\nVon pySerial gefundene COM-Ports:")

        for port in serielle_ports_auflisten():
            print(
                f'  {port["geraet"]}: '
                f'{port["beschreibung"]}'
            )

        esp32 = ESP32SerielleSteuerung(
            steuerbefehle=steuerbefehle,
            meldungen=kommunikationsmeldungen,
            werte=esp_werte,
            port=ESP32_COM_PORT,
            baudrate=ESP32_COM_BAUDRATE,
        )

        esp32.starten()

        if not esp32.auf_verbindung_warten(
            ESP32_COM_VERBINDUNGS_TIMEOUT
        ):
            print(
                f"\nWARNUNG: Der ESP32 wurde über "
                f"{ESP32_COM_PORT} noch nicht verbunden."
            )
            print(
                "Der ESP32-Thread versucht die Verbindung weiter."
            )

    elif ESP32_TCP_AKTIV:
        print(
            f"\nTCP-Verbindung zum ESP-Simulator: "
            f"{ESP32_TCP_HOST}:{ESP32_TCP_PORT}"
        )

        esp32 = ESP32TCPSteuerung(
            steuerbefehle=steuerbefehle,
            meldungen=kommunikationsmeldungen,
            werte=esp_werte,
            host=ESP32_TCP_HOST,
            port=ESP32_TCP_PORT,
        )

        esp32.starten()

        if not esp32.auf_verbindung_warten(
            ESP32_TCP_VERBINDUNGS_TIMEOUT
        ):
            print(
                f"\nWARNUNG: Der TCP-Server unter "
                f"{ESP32_TCP_HOST}:{ESP32_TCP_PORT} "
                "ist noch nicht verbunden."
            )
            print(
                "Starte esp-simulator.py. Der TCP-Thread "
                "versucht die Verbindung weiter."
            )

    if esp32 is not None:
        esp32.senden(f"BEFEHLSKETTE_GEPRUEFT;{len(programm['befehle'])}")

    if startmenue_anzeigen():
        # Ereignisse aus einem vorherigen Sendetest dürfen
        # die Befehlskette nicht unbeabsichtigt beeinflussen.
        queue_leeren(steuerbefehle)
        queue_leeren(kommunikationsmeldungen)

        api = dType.load()

        verbindung = dType.ConnectDobot(
            api,
            DOBOT_PORT,
            DOBOT_BAUDRATE,
        )

        print(f"\nVerbindungsrückgabe Dobot: {verbindung}")

        if verbindung[0] != dType.DobotConnect.DobotConnect_NoError:
            raise ConnectionError(
                "Der Dobot konnte nicht verbunden werden."
            )

        dobot_verbunden = True
        print("Dobot erfolgreich verbunden.")

        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdClear(api)

        ergebnis = befehlskette_ausfuehren_steuerbar(
            api,
            programm,
            timeout=TIMEOUT_SEKUNDEN,
            steuerbefehle=steuerbefehle,
            meldungen=kommunikationsmeldungen,
            esp_werte=esp_werte,
            tastatur=True,
            max_schritte=MAX_SCHRITTE,
            status_senden=None if esp32 is None else esp32.senden,
        )

        print(f"\nErgebnis der Ausführung: {ergebnis}")

        if ergebnis == ZUSTAND_HALT:
            abschlussgrund = "HALT"
            print()
            print(
                "Vor einem Neustart müssen Arbeitsplatte "
                "und Dobot kontrolliert werden."
            )
        else:
            abschlussgrund = "NORMAL"

    else:
        abschlussgrund = "ABBRUCH_VOR_START"
        print("\nDie Befehlskette wurde vor dem Start abgebrochen.")


except KeyboardInterrupt:
    abschlussgrund = "TASTATURABBRUCH"
    print("\nProgrammabbruch über die Tastatur.")

    if api is not None and dobot_verbunden:
        if hasattr(dType, "SetQueuedCmdForceStopExec"):
            dType.SetQueuedCmdForceStopExec(api)
        else:
            dType.SetQueuedCmdStopExec(api)


except Exception:
    abschlussgrund = "FEHLER"
    raise


finally:
    if abschlussgrund is not None:
        esp32_abschluss_melden(abschlussgrund)

    if esp32 is not None:
        esp32.beenden()
        print(f"ESP32-{COM_MODUS}-Thread beendet.")

    if api is not None and dobot_verbunden:
        dType.SetQueuedCmdStopExec(api)
        dType.DisconnectDobot(api)
        print("Verbindung zum Dobot getrennt.")
