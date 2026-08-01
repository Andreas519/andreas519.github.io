# Raspberry Pi Zero  
## Übersicht zur Beschaltung, Inbetriebnahme und Nutzung

**Stand:** 30. Juli 2026  
**Geeignet für:** Raspberry Pi Zero, Zero W, Zero WH und Zero 2 W

---

## 1. Was ist ein Raspberry Pi Zero?

Der Raspberry Pi Zero ist ein sehr kleiner Einplatinencomputer. Anders als ein
Mikrocontroller führt er ein vollständiges Betriebssystem aus. Dadurch kann er
unter anderem:

- Python-Programme ausführen,
- Bildschirme, Tastaturen und Mäuse verwenden,
- über WLAN und Bluetooth kommunizieren,
- Sensoren und Aktoren über GPIO-Pins ansteuern,
- eine Raspberry-Pi-Kamera betreiben,
- als kleiner Webserver, Messrechner oder Steuercomputer arbeiten.

### 1.1 Unterschiede der wichtigsten Modelle

| Modell | Prozessor | WLAN | Bluetooth | GPIO-Stiftleiste |
|---|---:|---:|---:|---|
| Raspberry Pi Zero | 1 Kern, 1 GHz | nein | nein | meist nicht bestückt |
| Raspberry Pi Zero W | 1 Kern, 1 GHz | 2,4 GHz | ja | meist nicht bestückt |
| Raspberry Pi Zero WH | 1 Kern, 1 GHz | 2,4 GHz | ja | bereits eingelötet |
| Raspberry Pi Zero 2 W | 4 Kerne, 1 GHz | 2,4 GHz | ja | je nach Ausführung |

Der **Raspberry Pi Zero 2 W** ist für neue Projekte meist die sinnvollste
Variante. Er ist wesentlich schneller als der ursprüngliche Raspberry Pi Zero,
besitzt aber dieselben kompakten Abmessungen von etwa 65 mm × 30 mm.

> **Hinweis:** Bei Modellen ohne den Buchstaben **H** ist die 40-polige
> GPIO-Stiftleiste normalerweise nicht eingelötet.

---

## 2. Benötigte Grundausstattung

Für die erste Inbetriebnahme werden benötigt:

- Raspberry Pi Zero,
- microSD-Karte, sinnvollerweise 16 GB oder größer,
- stabiles 5-V-Netzteil mit Micro-USB-Stecker,
- Mini-HDMI-auf-HDMI-Adapter oder passendes Kabel,
- USB-OTG-Adapter für den Datenanschluss,
- Tastatur und Maus oder ein USB-Hub,
- Computer zum Vorbereiten der microSD-Karte,
- optional: WLAN-Zugang,
- optional: 2×20-polige GPIO-Stiftleiste,
- optional: Gehäuse,
- optional: Raspberry-Pi-Kamera mit passendem Zero-Kamerakabel.

### 2.1 Empfohlene Stromversorgung

Für einen zuverlässigen Betrieb ist ein gutes **5-V-Netzteil** wichtig. Für den
Zero 2 W ist ein Netzteil mit ausreichender Reserve sinnvoll, besonders wenn
USB-Geräte, eine Kamera oder Zusatzmodule angeschlossen werden.

Billige oder sehr dünne USB-Kabel verursachen häufig:

- Startprobleme,
- spontane Neustarts,
- Abstürze,
- Fehler beim Schreiben auf die microSD-Karte,
- Unterspannungswarnungen.

---

## 3. Anschlüsse des Raspberry Pi Zero

### 3.1 Übersicht

| Anschluss | Aufgabe |
|---|---|
| **PWR IN** | Stromversorgung über Micro USB |
| **USB** | USB-OTG-Datenanschluss für Tastatur, Maus, Hub oder PC |
| **Mini HDMI** | Bild- und Tonausgabe |
| **microSD** | Betriebssystem und Datenspeicher |
| **CSI-Kameraanschluss** | Anschluss einer Raspberry-Pi-Kamera |
| **40-poliges GPIO-Feld** | Sensoren, LEDs, Taster, Busmodule und Aktoren |
| **RUN-Pads** | Reset beziehungsweise Neustart durch kurzen Kontakt |
| **TV-Pads** | analoger Composite-Videoausgang bei einigen Modellen |

### 3.2 PWR IN und USB nicht verwechseln

Der Raspberry Pi Zero besitzt zwei Micro-USB-Buchsen:

1. **PWR IN**  
   Diese Buchse dient hauptsächlich der Stromversorgung.

2. **USB**  
   Diese Buchse ist der USB-Datenanschluss. Hier werden ein OTG-Adapter, ein
   USB-Hub, eine Tastatur, eine Maus oder ein anderer Computer angeschlossen.

> Für Tastatur, Maus oder USB-Stick muss der Anschluss **USB** verwendet werden,
> nicht nur **PWR IN**.

### 3.3 Mini-HDMI-Anschluss

Der Raspberry Pi Zero verwendet **Mini HDMI**, nicht Micro HDMI und nicht den
normalen großen HDMI-Stecker.

Benötigt wird daher entweder:

- ein Mini-HDMI-auf-HDMI-Kabel oder
- ein Mini-HDMI-auf-HDMI-Adapter mit normalem HDMI-Kabel.

### 3.4 Kameraanschluss

Alle neueren Zero-Modelle besitzen einen kleinen **22-poligen CSI-Anschluss**.
Die üblichen Raspberry-Pi-Kameras haben auf der Kameraseite einen
15-poligen Anschluss. Deshalb wird ein spezielles
**15-auf-22-poliges Standard-Mini-Kamerakabel** benötigt.

> Kamera und Flachbandkabel nur bei ausgeschalteter und stromloser Platine
> einstecken oder entfernen.

---

## 4. GPIO-Grundlagen

GPIO bedeutet **General Purpose Input/Output**. Die GPIO-Pins können durch ein
Programm als Ein- oder Ausgang verwendet werden.

Typische Anwendungen:

- LED ein- und ausschalten,
- Taster abfragen,
- Temperatursensor auslesen,
- Relais über einen Treiber schalten,
- Servomotor steuern,
- I²C-, SPI- oder UART-Module anschließen.

### 4.1 Wichtige Sicherheitsregeln

1. Die GPIO-Logik arbeitet mit **3,3 V**.
2. GPIO-Eingänge sind **nicht 5-V-tolerant**.
3. Niemals 5 V direkt auf einen GPIO-Eingang legen.
4. Vor Änderungen an der Verdrahtung den Raspberry Pi herunterfahren und vom
   Netzteil trennen.
5. LEDs immer mit Vorwiderstand betreiben.
6. Motoren, Relais, Magnetventile und leistungsstarke Verbraucher niemals
   direkt über GPIO-Pins versorgen.
7. Für größere Lasten Transistoren, MOSFETs, Treiberbausteine oder Relaismodule
   mit geeigneter Eingangsschaltung verwenden.
8. Bei externer Stromversorgung normalerweise die Masseleitungen
   (**GND**) miteinander verbinden.
9. Die 3,3-V- und 5-V-Pins sind Versorgungsanschlüsse und keine normalen GPIOs.
10. Kurzschlüsse zwischen 3,3 V, 5 V und GND können den Raspberry Pi zerstören.

> Für Unterrichtsaufbauten ist es sinnvoll, GPIO-Ausgänge nur mit wenigen
> Milliampere zu belasten und Leistungsstufen konsequent über Treiber
> aufzubauen.

---

## 5. Nummerierung der GPIO-Pins

Es existieren zwei Nummerierungssysteme:

### BCM-Nummerierung

Sie verwendet die Bezeichnungen des Prozessors, zum Beispiel:

- GPIO17,
- GPIO27,
- GPIO22.

Diese Nummerierung wird von `gpiozero` verwendet.

### Physische Nummerierung

Sie zählt die Kontakte der Stiftleiste von 1 bis 40.

Beispiel:

- physischer Pin 11 = GPIO17,
- physischer Pin 13 = GPIO27,
- physischer Pin 15 = GPIO22.

> In Programmen und Schaltplänen immer angeben, welches Nummerierungssystem
> verwendet wird. In dieser Übersicht wird für Programme die
> **BCM-Nummerierung** benutzt.

Auf dem Raspberry Pi kann die Belegung im Terminal angezeigt werden:

```bash
pinout
```

---

## 6. Vollständige Belegung der 40-poligen Stiftleiste

| Physischer Pin | Hauptfunktion | Typische Zusatzfunktion |
|---:|---|---|
| 1 | 3,3 V | Versorgung |
| 2 | 5 V | Versorgung |
| 3 | GPIO2 | I²C SDA |
| 4 | 5 V | Versorgung |
| 5 | GPIO3 | I²C SCL |
| 6 | GND | Masse |
| 7 | GPIO4 | GPCLK0 |
| 8 | GPIO14 | UART TXD |
| 9 | GND | Masse |
| 10 | GPIO15 | UART RXD |
| 11 | GPIO17 | universeller GPIO |
| 12 | GPIO18 | PWM0 / PCM CLK |
| 13 | GPIO27 | universeller GPIO |
| 14 | GND | Masse |
| 15 | GPIO22 | universeller GPIO |
| 16 | GPIO23 | universeller GPIO |
| 17 | 3,3 V | Versorgung |
| 18 | GPIO24 | universeller GPIO |
| 19 | GPIO10 | SPI MOSI |
| 20 | GND | Masse |
| 21 | GPIO9 | SPI MISO |
| 22 | GPIO25 | universeller GPIO |
| 23 | GPIO11 | SPI SCLK |
| 24 | GPIO8 | SPI CE0 |
| 25 | GND | Masse |
| 26 | GPIO7 | SPI CE1 |
| 27 | GPIO0 | ID_SD, reserviert |
| 28 | GPIO1 | ID_SC, reserviert |
| 29 | GPIO5 | universeller GPIO |
| 30 | GND | Masse |
| 31 | GPIO6 | universeller GPIO |
| 32 | GPIO12 | PWM0 |
| 33 | GPIO13 | PWM1 |
| 34 | GND | Masse |
| 35 | GPIO19 | PWM1 / PCM FS |
| 36 | GPIO16 | universeller GPIO |
| 37 | GPIO26 | universeller GPIO |
| 38 | GPIO20 | PCM DIN |
| 39 | GND | Masse |
| 40 | GPIO21 | PCM DOUT |

### 6.1 Häufig verwendete Schnittstellen

#### I²C

| Signal | GPIO | Physischer Pin |
|---|---:|---:|
| SDA | GPIO2 | 3 |
| SCL | GPIO3 | 5 |
| 3,3 V | – | 1 oder 17 |
| GND | – | zum Beispiel 6 |

#### SPI

| Signal | GPIO | Physischer Pin |
|---|---:|---:|
| MOSI | GPIO10 | 19 |
| MISO | GPIO9 | 21 |
| SCLK | GPIO11 | 23 |
| CE0 | GPIO8 | 24 |
| CE1 | GPIO7 | 26 |
| GND | – | zum Beispiel 20 oder 25 |

#### UART

| Signal | GPIO | Physischer Pin |
|---|---:|---:|
| TXD | GPIO14 | 8 |
| RXD | GPIO15 | 10 |
| GND | – | zum Beispiel 6 |

> Bei einer UART-Verbindung gilt normalerweise:  
> TX des Raspberry Pi an RX des anderen Geräts und RX des Raspberry Pi an TX
> des anderen Geräts. Beide Geräte benötigen eine gemeinsame Masse.

---

## 7. Betriebssystem vorbereiten

### 7.1 Raspberry Pi Imager installieren

Auf einem Windows-PC, Mac oder Linux-Rechner wird der
**Raspberry Pi Imager** installiert.

Mit dem Imager wird Raspberry Pi OS auf die microSD-Karte geschrieben.

### 7.2 Betriebssystem auswählen

Im Imager:

1. Raspberry-Pi-Modell auswählen.
2. Betriebssystem auswählen.
3. microSD-Karte auswählen.
4. Einstellungen bearbeiten.
5. Betriebssystem schreiben.

Für einen Betrieb mit Bildschirm eignet sich:

- **Raspberry Pi OS mit Desktop**

Für einen Betrieb ohne Bildschirm eignet sich:

- **Raspberry Pi OS Lite**

Für den ursprünglichen Raspberry Pi Zero beziehungsweise Zero W sollte eine
passende 32-Bit-Ausgabe gewählt werden. Am einfachsten ist es, im Imager zuerst
das genaue Modell auszuwählen und anschließend die empfohlene Ausgabe zu
verwenden.

### 7.3 Einstellungen bereits im Imager festlegen

Vor dem Schreiben der Karte können folgende Angaben gesetzt werden:

- Rechnername, zum Beispiel `pi-zero`,
- Benutzername,
- sicheres Kennwort,
- WLAN-Name,
- WLAN-Kennwort,
- WLAN-Land `DE`,
- Zeitzone `Europe/Berlin`,
- Tastaturlayout `de`,
- SSH aktivieren.

Diese Voreinstellungen sind besonders wichtig, wenn der Raspberry Pi ohne
Monitor betrieben werden soll.

### 7.4 microSD-Karte einsetzen

1. Imager vollständig beenden.
2. microSD-Karte sicher vom Computer auswerfen.
3. Karte in den Raspberry Pi Zero einsetzen.
4. Kabel und Peripherie anschließen.
5. Erst zuletzt das Netzteil verbinden.

---

## 8. Erste Inbetriebnahme mit Bildschirm

### 8.1 Reihenfolge der Anschlüsse

1. microSD-Karte einsetzen.
2. Mini-HDMI-Kabel anschließen.
3. Tastatur und Maus über USB-OTG-Adapter oder USB-Hub anschließen.
4. Bildschirm einschalten.
5. Netzteil an **PWR IN** anschließen.

Der Raspberry Pi besitzt normalerweise keinen Ein-/Ausschalter. Er startet,
sobald die Stromversorgung angeschlossen wird.

### 8.2 Erste Schritte

Nach dem ersten Start:

1. Benutzerkonto prüfen oder einrichten.
2. Sprache, Tastatur und Zeitzone kontrollieren.
3. WLAN verbinden.
4. Terminal öffnen.
5. System aktualisieren.

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

### 8.3 Systeminformationen anzeigen

```bash
hostname
hostname -I
uname -a
cat /etc/os-release
```

Temperatur anzeigen:

```bash
vcgencmd measure_temp
```

GPIO-Belegung anzeigen:

```bash
pinout
```

---

## 9. Inbetriebnahme ohne Bildschirm

Ein Raspberry Pi Zero W oder Zero 2 W kann vollständig über WLAN eingerichtet
werden.

Voraussetzungen:

- WLAN-Daten wurden im Raspberry Pi Imager eingetragen.
- SSH wurde im Imager aktiviert.
- Raspberry Pi und Steuercomputer befinden sich im selben Netzwerk.

Verbindung von Windows, macOS oder Linux:

```bash
ssh BENUTZERNAME@pi-zero.local
```

Beispiel:

```bash
ssh andreas@pi-zero.local
```

Falls der Rechnername nicht gefunden wird, die IP-Adresse verwenden:

```bash
ssh BENUTZERNAME@192.168.1.50
```

Die IP-Adresse kann unter anderem im Router nachgesehen werden. Auf dem
Raspberry Pi selbst zeigt folgender Befehl die lokale Adresse:

```bash
hostname -I
```

---

## 10. Raspberry Pi richtig ausschalten

Die Stromversorgung darf nicht einfach während eines Schreibvorgangs getrennt
werden. Dadurch kann das Dateisystem der microSD-Karte beschädigt werden.

Richtig herunterfahren:

```bash
sudo shutdown -h now
```

oder:

```bash
sudo poweroff
```

Neustart:

```bash
sudo reboot
```

Erst nachdem das System heruntergefahren ist und keine Aktivität mehr erkennbar
ist, das Netzteil abziehen.

---

## 11. Schnittstellen aktivieren

Viele Schnittstellen können über die Systemeinstellungen oder über
`raspi-config` aktiviert werden:

```bash
sudo raspi-config
```

Dort den Bereich für Schnittstellen öffnen und bei Bedarf aktivieren:

- I²C,
- SPI,
- serielle Schnittstelle,
- SSH,
- VNC.

Danach ist häufig ein Neustart sinnvoll:

```bash
sudo reboot
```

---

## 12. Python und Thonny

Raspberry Pi OS enthält in der Desktop-Ausgabe normalerweise Python 3 und
Thonny.

Thonny starten:

1. Raspberry-Pi-Menü öffnen.
2. Bereich **Programmierung** auswählen.
3. **Thonny** starten.
4. Programm eingeben.
5. Datei mit der Endung `.py` speichern.
6. Mit der grünen Startschaltfläche ausführen.

Python-Version prüfen:

```bash
python3 --version
```

Ein Programm im Terminal ausführen:

```bash
python3 mein_programm.py
```

---

## 13. Erstes Schaltungsbeispiel: LED

### 13.1 Bauteile

- 1 LED,
- 1 Widerstand mit 220 Ω bis 470 Ω,
- Steckbrett,
- Verbindungskabel.

### 13.2 Beschaltung

```text
GPIO17, physischer Pin 11
        |
        |
     Vorwiderstand
     220–470 Ω
        |
        |
      Anode LED
        >| 
      Kathode
        |
        |
GND, physischer Pin 6
```

Bei einer üblichen LED ist:

- längeres Bein = Anode,
- kürzeres Bein = Kathode,
- abgeflachte Gehäuseseite = Kathode.

### 13.3 Python-Programm mit gpiozero

```python
from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    led.on()
    sleep(1)

    led.off()
    sleep(1)
```

Speichern, zum Beispiel als:

```text
led_blinken.py
```

Start:

```bash
python3 led_blinken.py
```

Beenden mit:

```text
Strg + C
```

### 13.4 Kürzere Variante

```python
from gpiozero import LED
from signal import pause

led = LED(17)
led.blink(on_time=1, off_time=1)

pause()
```

---

## 14. Zweites Schaltungsbeispiel: Taster

### 14.1 Beschaltung mit internem Pull-up-Widerstand

```text
GPIO27, physischer Pin 13 ---- Taster ---- GND, physischer Pin 14
```

Ein externer Widerstand ist in diesem Beispiel nicht erforderlich, weil
`gpiozero` standardmäßig den internen Pull-up-Widerstand verwendet.

### 14.2 Python-Programm

```python
from gpiozero import Button
from signal import pause

taster = Button(27)

def gedrueckt():
    print("Taster gedrückt")

def losgelassen():
    print("Taster losgelassen")

taster.when_pressed = gedrueckt
taster.when_released = losgelassen

pause()
```

---

## 15. LED mit Taster steuern

### 15.1 Beschaltung

LED:

```text
GPIO17 -- 330 Ω -- LED -- GND
```

Taster:

```text
GPIO27 -- Taster -- GND
```

### 15.2 Programm

```python
from gpiozero import LED, Button
from signal import pause

led = LED(17)
taster = Button(27)

taster.when_pressed = led.on
taster.when_released = led.off

pause()
```

---

## 16. I²C-Modul anschließen

Viele Sensoren und Displays nutzen I²C.

### 16.1 Grundbeschaltung eines 3,3-V-I²C-Moduls

| Modul | Raspberry Pi Zero |
|---|---|
| VCC | 3,3 V, Pin 1 |
| GND | GND, Pin 6 |
| SDA | GPIO2, Pin 3 |
| SCL | GPIO3, Pin 5 |

> Vor dem Anschluss prüfen, ob das konkrete Modul und seine Pull-up-Widerstände
> mit 3,3-V-Logik arbeiten. Manche Breakout-Boards werden mit 5 V versorgt,
> geben aber ebenfalls 5 V auf SDA und SCL aus. Das wäre für den Raspberry Pi
> gefährlich.

### 16.2 I²C aktivieren

```bash
sudo raspi-config
```

Danach I²C unter den Schnittstellen aktivieren und neu starten.

Werkzeuge installieren:

```bash
sudo apt install -y i2c-tools
```

Geräte suchen:

```bash
i2cdetect -y 1
```

In der Tabelle erscheint die erkannte I²C-Adresse, zum Beispiel `3c`, `20` oder
`27`.

---

## 17. Serielle Schnittstelle verwenden

### 17.1 Beschaltung zu einem 3,3-V-Gerät

| Raspberry Pi Zero | Anderes Gerät |
|---|---|
| GPIO14 / TXD, Pin 8 | RX |
| GPIO15 / RXD, Pin 10 | TX |
| GND | GND |

> Nur Geräte mit **3,3-V-UART-Pegel** direkt verbinden. Für 5-V-UART-Geräte ist
> mindestens am RX-Eingang des Raspberry Pi eine geeignete Pegelanpassung
> erforderlich.

### 17.2 Serielle Schnittstelle aktivieren

```bash
sudo raspi-config
```

Bei der Abfrage:

- Login-Shell über die serielle Schnittstelle: normalerweise **Nein**,
- serielle Hardware aktivieren: **Ja**.

---

## 18. Raspberry-Pi-Kamera anschließen

### 18.1 Benötigte Teile

- Raspberry-Pi-Kamera,
- spezielles Standard-Mini-Kamerakabel für Zero-Modelle,
- Raspberry Pi Zero ab Version 1.3, Zero W oder Zero 2 W.

### 18.2 Vorgehensweise

1. Raspberry Pi herunterfahren.
2. Netzteil trennen.
3. Verriegelung des CSI-Anschlusses vorsichtig öffnen.
4. Flachbandkabel gerade einschieben.
5. Auf richtige Kontaktseite achten.
6. Verriegelung schließen.
7. Kabel an der Kamera kontrollieren.
8. Raspberry Pi wieder einschalten.

Die genaue Orientierung hängt vom Kabel und vom Kameramodul ab. Entscheidend
ist, dass die metallischen Kontakte in Richtung der Kontakte im jeweiligen
Steckverbinder zeigen.

### 18.3 Kamera testen

Vorschau für einige Sekunden:

```bash
rpicam-hello
```

Foto aufnehmen:

```bash
rpicam-still -o testbild.jpg
```

Bilddatei prüfen:

```bash
ls -l testbild.jpg
```

### 18.4 Einfaches Python-Beispiel mit Picamera2

```python
from picamera2 import Picamera2
from time import sleep

kamera = Picamera2()
kamera.start()

sleep(2)
kamera.capture_file("aufnahme.jpg")

kamera.stop()
print("Bild gespeichert: aufnahme.jpg")
```

Falls Picamera2 fehlt:

```bash
sudo apt update
sudo apt install -y python3-picamera2
```

---

## 19. USB-OTG-Nutzung

Der Datenanschluss des Raspberry Pi Zero unterstützt USB-OTG.

Mögliche Betriebsarten:

- Anschluss einer Tastatur oder Maus,
- Anschluss eines USB-Hubs,
- Anschluss eines USB-Sticks,
- Verbindung mit einem Computer,
- Betrieb als virtuelles USB-Netzwerkgerät,
- Betrieb als virtuelle serielle Schnittstelle,
- Betrieb als USB-Massenspeicher in speziellen Projekten.

Für die normale Nutzung mit Tastatur und Maus wird ein
**Micro-USB-OTG-Adapter** benötigt.

Bei mehreren USB-Geräten ist ein aktiver USB-Hub empfehlenswert, damit die
Stromversorgung des Raspberry Pi nicht überlastet wird.

---

## 20. Netzwerkzugriff

### 20.1 IP-Adresse anzeigen

```bash
hostname -I
```

### 20.2 Erreichbarkeit prüfen

Von einem anderen Computer:

```bash
ping pi-zero.local
```

### 20.3 SSH

```bash
ssh BENUTZERNAME@pi-zero.local
```

### 20.4 Dateien mit SCP übertragen

Vom Computer zum Raspberry Pi:

```bash
scp mein_programm.py BENUTZERNAME@pi-zero.local:/home/BENUTZERNAME/
```

Vom Raspberry Pi zum Computer:

```bash
scp BENUTZERNAME@pi-zero.local:/home/BENUTZERNAME/messwerte.csv .
```

### 20.5 Grafischer Fernzugriff

Für einen grafischen Fernzugriff können verwendet werden:

- VNC innerhalb des lokalen Netzwerks,
- Raspberry Pi Connect,
- eine Remotedesktop-Lösung.

Auf dem Zero 2 W ist ein grafischer Fernzugriff deutlich angenehmer als auf dem
ursprünglichen Zero W.

---

## 21. Programm automatisch starten

Für dauerhafte Steuerungsaufgaben ist ein `systemd`-Dienst sinnvoll.

Beispielprogramm:

```text
/home/andreas/projekte/steuerung.py
```

Dienstdatei anlegen:

```bash
sudo nano /etc/systemd/system/steuerung.service
```

Inhalt:

```ini
[Unit]
Description=Python-Steuerung
After=network.target

[Service]
Type=simple
User=andreas
WorkingDirectory=/home/andreas/projekte
ExecStart=/usr/bin/python3 /home/andreas/projekte/steuerung.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Der Benutzername und die Pfade müssen an das eigene System angepasst werden.

Dienst neu einlesen und aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable steuerung.service
sudo systemctl start steuerung.service
```

Status prüfen:

```bash
systemctl status steuerung.service
```

Ausgaben anzeigen:

```bash
journalctl -u steuerung.service
```

Dienst stoppen:

```bash
sudo systemctl stop steuerung.service
```

---

## 22. Fehlersuche

### 22.1 Raspberry Pi startet nicht

Prüfen:

- Ist Raspberry Pi OS korrekt auf die microSD-Karte geschrieben?
- Ist die Karte vollständig eingesetzt?
- Ist das Netzteil am Anschluss **PWR IN**?
- Liefert das Netzteil stabile 5 V?
- Wurde das richtige Raspberry-Pi-Modell im Imager ausgewählt?
- Ist die microSD-Karte fehlerhaft?

### 22.2 Kein Bild

Prüfen:

- Mini-HDMI-Adapter richtig angeschlossen?
- Bildschirm vor dem Raspberry Pi eingeschaltet?
- Richtiger HDMI-Eingang gewählt?
- anderes HDMI-Kabel testen,
- Betriebssystem vollständig gestartet?
- Netzteil ausreichend?

### 22.3 Tastatur oder Maus funktioniert nicht

Prüfen:

- Gerät am Anschluss **USB**, nicht nur an **PWR IN**?
- OTG-Adapter geeignet?
- USB-Hub benötigt?
- USB-Gerät benötigt zu viel Strom?
- aktiven USB-Hub testen.

### 22.4 WLAN funktioniert nicht

Prüfen:

- Modell besitzt WLAN?
- 2,4-GHz-WLAN verfügbar?
- SSID und Kennwort richtig?
- WLAN-Land auf `DE` gesetzt?
- WLAN-Antenne nicht durch Metall abgeschirmt?
- Signalstärke ausreichend?

### 22.5 SSH funktioniert nicht

Prüfen:

- SSH im Imager oder in `raspi-config` aktiviert?
- Raspberry Pi und Computer im selben Netzwerk?
- richtiger Benutzername?
- richtiger Rechnername?
- IP-Adresse statt `.local`-Namen testen?

### 22.6 GPIO-Schaltung funktioniert nicht

Prüfen:

- BCM- und physische Nummerierung verwechselt?
- gemeinsame Masse vorhanden?
- LED richtig gepolt?
- Vorwiderstand vorhanden?
- richtige Versorgungsspannung?
- I²C, SPI oder UART aktiviert?
- Pins bereits von einer anderen Funktion belegt?

### 22.7 Unterspannung prüfen

```bash
vcgencmd get_throttled
```

Eine Ausgabe von:

```text
throttled=0x0
```

bedeutet, dass aktuell und seit dem letzten Start keine entsprechende Warnung
gespeichert wurde. Andere Werte können auf Unterspannung oder
Taktreduzierung hinweisen.

### 22.8 Kamera wird nicht gefunden

Prüfen:

- richtiges Standard-Mini-Kabel verwendet?
- Kabel gerade und vollständig eingesteckt?
- Kontaktseite richtig ausgerichtet?
- Kamera bei ausgeschaltetem Gerät angeschlossen?
- System aktualisiert?
- `rpicam-hello` statt alter `raspistill`-Befehle verwendet?

---

## 23. Typische Projekte

Der Raspberry Pi Zero eignet sich unter anderem für:

- einfache Bilderkennung mit Kamera,
- Zeitrafferkamera,
- Überwachungskamera,
- Messwerterfassung,
- Wetterstation,
- Datenlogger,
- kleiner Webserver,
- MQTT-Teilnehmer,
- Home-Automation,
- Robotersteuerung,
- USB-Gadget,
- Bluetooth-Lautsprecher,
- Steuerung von LEDs und Displays,
- Kommunikation mit ESP32, Arduino oder Dobot-Steuerungen,
- Unterrichtsprojekte mit Python und GPIO.

### 23.1 Grenzen des ursprünglichen Zero

Der ursprüngliche Zero und Zero W haben nur einen Prozessorkern und 512 MB
Arbeitsspeicher. Sie sind gut für:

- einfache Python-Programme,
- GPIO-Steuerungen,
- kleine Server,
- Messwerterfassung,
- kompakte Embedded-Anwendungen.

Für eine grafische Desktop-Nutzung, umfangreiche Bildverarbeitung oder mehrere
gleichzeitige Dienste ist der **Zero 2 W** deutlich geeigneter.

---

## 24. Sinnvolle Reihenfolge für ein Unterrichtsprojekt

1. Raspberry Pi OS mit Imager installieren.
2. Mit Bildschirm, Tastatur und Maus starten.
3. Terminal kennenlernen.
4. System aktualisieren.
5. Thonny starten.
6. LED blinken lassen.
7. Taster abfragen.
8. LED mit Taster steuern.
9. I²C-Gerät anschließen.
10. Messwerte auslesen.
11. WLAN und SSH nutzen.
12. Kamera anschließen.
13. Programm automatisch starten.
14. Eigenständiges Projekt entwickeln.

---

## 25. Kurze Checkliste vor dem Einschalten

- [ ] microSD-Karte eingesetzt
- [ ] Betriebssystem installiert
- [ ] keine Kurzschlüsse auf dem Steckbrett
- [ ] GPIO-Eingänge erhalten höchstens 3,3 V
- [ ] LEDs besitzen Vorwiderstände
- [ ] Motoren und Relais besitzen Treiber
- [ ] Masseverbindungen kontrolliert
- [ ] HDMI und USB-OTG richtig angeschlossen
- [ ] Netzteil steckt in **PWR IN**
- [ ] Kamera nur im stromlosen Zustand angeschlossen

---

## 26. Weiterführende offizielle Quellen

- [Raspberry Pi Zero 2 W – Produktseite](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [Raspberry Pi Zero – Produktseite](https://www.raspberrypi.com/products/raspberry-pi-zero/)
- [Erste Schritte mit Raspberry Pi](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi OS](https://www.raspberrypi.com/documentation/computers/os.html)
- [Raspberry-Pi-Hardware und GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Kameradokumentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Kamerasoftware und rpicam-Befehle](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- [Fernzugriff über SSH, VNC und Raspberry Pi Connect](https://www.raspberrypi.com/documentation/remote-access/)
