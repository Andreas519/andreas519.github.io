# Porterweiterungen am ESP32 testen

**Version:** 1.6  
**Stand:** 28.07.2026, 05:01 Uhr

## Belegte ESP32-Ports

Die gegenwärtigen Einzeltests verwenden insgesamt fünf GPIO-Ports:

| GPIO | Verwendung | Testprogramme |
| --- | --- | --- |
| GPIO 16 | serielle Daten zum 74HC595 | `74hc595_test.py` |
| GPIO 17 | Schiebetakt des 74HC595 | `74hc595_test.py` |
| GPIO 21 | I²C-Datenleitung SDA | `pcf8574_test.py`, `pcf8575_test.py`, `mcp23017_test.py`, `pca9685_test.py` |
| GPIO 22 | I²C-Taktleitung SCL | `pcf8574_test.py`, `pcf8575_test.py`, `mcp23017_test.py`, `pca9685_test.py` |
| GPIO 23 | Speichertakt des 74HC595 | `74hc595_test.py` |

Die Portnummern stehen jeweils am Anfang der Testprogramme und können dort
geändert werden. Vor der späteren Übernahme in
`esp32_dobot_steuerung_v1_3.py` muss die Belegung mit den dort bereits
verwendeten GPIO-Ports abgeglichen werden.

## Verbindliche Kabelfarben

Für die Testaufbauten und die spätere Erweiterung der Dobot-Steuerung verwenden
wir folgende einheitliche Farbzuordnung:

| Farbe | Signal | Bedeutung |
| --- | --- | --- |
| Blau | GND | Masse |
| Rot | VCC | Versorgungsspannung |
| Gelb | SDA | I²C-Datenleitung |
| Grün | SCL | I²C-Taktleitung |
| Braun | DS | serielle Daten zum 74HC595 |
| Schwarz | SHCP | Schiebetakt des 74HC595 |
| Weiß | STCP | Speichertakt des 74HC595 |

Diese Farbzuordnung gilt für alle zu diesem Projekt gehörenden Schalt- und
Versuchsaufbauten. Vor dem Einschalten wird trotzdem immer die tatsächliche
Verbindung am ESP32 und am jeweiligen Baustein kontrolliert. Die Farbe allein
ist kein Schutz vor einer vertauschten Leitung.

Diese Programme testen typische Erweiterungsmodule zunächst unabhängig von der
Dobot-Steuerung:

| Modul | Aufgabe | Testprogramm |
| --- | --- | --- |
| I²C-Bus | fortlaufend nur die gefundenen Adressen anzeigen | `i2c-scanner.py` |
| PCF8574 | einfacher 8-Bit-Portexpander | `pcf8574_test.py` |
| PCF8574 | vier Eingänge und vier Ausgänge | `pcf8574_test-in-out.py` |
| zwei PCF8574 | je vier Eingänge und vier Ausgänge | `pcf8574_test-in-out-2.py` |
| PCF8575 | einfacher 16-Bit-Portexpander | `pcf8575_test.py` |
| MCP23017 | leistungsfähiger 16-Bit-Portexpander | `mcp23017_test.py` |
| MCP23017 | zwei Eingänge mit Interrupt | `mcp23017_test-interrupt.py` |
| PCA9685 | 16 PWM-Ausgänge | `pca9685_test.py` |
| 74HC595 | klassisches 8-Bit-Schieberegister | `74hc595_test.py` |

Die Programme sind für MicroPython auf einem ESP32 geschrieben. Sie benötigen
keine zusätzliche Bibliothek.

PCF8574, PCF8575, MCP23017 und PCA9685 arbeiten am I²C-Bus. Der 74HC595 ist
dagegen ein serielles Schieberegister. Er benötigt drei GPIO-Leitungen, aber
keine I²C-Adresse.

> **Verbindliche Testregel:** Vor dem Test jedes I²C-Moduls wird immer zuerst
> `i2c-scanner.py` ausgeführt. Das modulspezifische Testprogramm startet erst,
> wenn der Scanner das angeschlossene Modul unter der erwarteten Adresse findet.

## Anschluss der I²C-Module

| ESP32 | I²C-Modul |
| --- | --- |
| GPIO 21 | SDA |
| GPIO 22 | SCL |
| 3,3 V | VCC beziehungsweise Logikversorgung |
| GND | GND |

Vor dem Einschalten muss geprüft werden, ob das konkrete Modul für 3,3-V-Logik
geeignet ist. ESP32-Eingänge sind nicht 5-V-tolerant.

## Vorgehen

1. Zunächst nur **ein** I²C-Modul anschließen.
2. **Immer zuerst** `i2c-scanner.py` in Thonny öffnen und auf dem ESP32 ausführen.
3. Prüfen, ob der Scanner genau die erwartete Moduladresse anzeigt.
4. Falls die angezeigte Adresse abweicht, `ADRESSE` am Programmanfang ändern.
5. Anschließend das passende Modultestprogramm ausführen.
6. Erst nach einem erfolgreichen Einzeltest weitere Hardware anschließen.

PCF8574, PCF8575 und MCP23017 können abhängig von ihrer Beschaltung dieselben
Adressen im Bereich `0x20` bis `0x27` verwenden. Der PCF8574 kann je nach
Variante außerdem im Bereich `0x38` bis `0x3F` liegen. Der PCA9685 verwendet
standardmäßig `0x40`. Zwei Module mit derselben Adresse dürfen nicht gleichzeitig
am Bus betrieben werden. In diesem Fall muss die Adresse eines Moduls über
dessen Adressbrücken geändert werden.

## PCF8574-Adressbrücken

Die drei Adressleitungen A2, A1 und A0 bestimmen die I²C-Adresse. LOW bedeutet
eine Verbindung zu GND, HIGH eine Verbindung zu VCC. Bei Modulen mit
dreipoligen Jumperleisten wird der Jumper entsprechend zur beschrifteten
GND-/Minus- oder VCC-/Plus-Seite gesteckt.

| A2 | A1 | A0 | I²C-Adresse |
| --- | --- | --- | --- |
| LOW | LOW | LOW | `0x20` |
| LOW | LOW | HIGH | `0x21` |
| LOW | HIGH | LOW | `0x22` |
| LOW | HIGH | HIGH | `0x23` |
| HIGH | LOW | LOW | `0x24` |
| HIGH | LOW | HIGH | `0x25` |
| HIGH | HIGH | LOW | `0x26` |
| HIGH | HIGH | HIGH | `0x27` |

Für `pcf8574_test-in-out-2.py` gilt:

- Modul 1 unter `0x20`: A2 = LOW, A1 = LOW, A0 = LOW
- Modul 2 unter `0x21`: A2 = LOW, A1 = LOW, A0 = HIGH

Die konkrete Richtung des Jumpers ist nicht bei jeder Modulplatine gleich.
Deshalb gelten die Beschriftungen auf der Platine und anschließend die Ausgabe
des I²C-Scans. Erwartet werden `0x20` und `0x21`.

## Testaufbauten

### PCF8574

Das Programm schaltet P0 bis P7 nacheinander auf LOW. Für einen sichtbaren Test
kann je eine LED mit Vorwiderstand zwischen 3,3 V und einen Portpin geschaltet
werden. Der PCF8574 besitzt quasi-bidirektionale Anschlüsse: Eine geschriebene
`1` gibt einen Pin für die Nutzung als Eingang frei.

Nach dem erfolgreichen Grundtest kann `pcf8574_test-in-out.py` verwendet werden.
P0 bis P3 arbeiten darin als Eingänge und bleiben durch eine geschriebene `1`
freigegeben. Taster werden jeweils zwischen Eingang und GND angeschlossen.
P4 bis P7 sind Ausgänge; ein LOW-Signal läuft nacheinander durch diese vier
Ports.

`pcf8574_test-in-out-2.py` erweitert diesen Test auf zwei Module. Beide Module
liegen am gemeinsamen I²C-Bus, benötigen aber unterschiedliche Adressen. Das
Programm erwartet zunächst `0x20` und `0x21`. Auf beiden Modulen arbeiten P0 bis
P3 als Eingänge und P4 bis P7 als Ausgänge. Die LOW-Signale laufen auf den
Modulen in entgegengesetzter Richtung, damit sie leicht unterschieden werden
können.

Auch wenn die Module über ihre Steckverbinder hintereinander verbunden sind,
liegen SDA und SCL elektrisch gemeinsam am selben Bus. Vor dem Start müssen die
Adressbrücken deshalb so gesetzt sein, dass der I²C-Scan zwei verschiedene
Adressen findet.

### PCF8575

Der PCF8575 arbeitet nach demselben quasi-bidirektionalen Prinzip wie der
PCF8574, stellt aber 16 Anschlüsse bereit. Das Testprogramm schaltet P0 bis P15
nacheinander auf LOW. Für die Nutzung als Eingang muss der betreffende Pin
zuvor mit einer `1` freigegeben werden.

### MCP23017

Port A wird als Ausgang verwendet und lässt ein LOW-Signal über alle acht Pins
wandern. Port B wird als Eingang mit internen Pull-up-Widerständen eingerichtet.
Ein Taster kann einen PB-Pin mit GND verbinden. Änderungen werden in Thonny als
Binärwert angezeigt.

Für den Interrupt-Test dient `mcp23017_test-interrupt.py`. GPB0 und GPB1 sind
Eingänge mit internen Pull-up-Widerständen; die Taster werden jeweils zwischen
Eingang und GND angeschlossen. Beide Eingänge lösen bei jeder Zustandsänderung
einen Interrupt über INTB aus.

| MCP23017 | ESP32 | Funktion |
| --- | --- | --- |
| SDA | GPIO21 | I²C-Datenleitung, gelb |
| SCL | GPIO22 | I²C-Taktleitung, grün |
| INTB beziehungsweise IB | GPIO16 | Interruptleitung, Kabelfarbe noch festzulegen |

INTB wird als aktives LOW-Open-Drain-Signal konfiguriert. Der ESP32 aktiviert
deshalb an GPIO16 seinen internen Pull-up-Widerstand. Die Interrupt-Funktion
führt keine I²C-Kommunikation aus, sondern setzt nur ein Flag. Die Auswertung
erfolgt anschließend sicher in der Hauptschleife.

### PCA9685

Kanal 0 ändert seine Pulsweite langsam von 0 bis 100 Prozent und zurück.
Angeschlossene Lasten dürfen nicht direkt aus einem PWM-Ausgang versorgt werden.
Für Motoren, Lampen oder andere größere Lasten ist eine geeignete Treiberstufe
notwendig.

Zum ersten Test ist eine LED mit Vorwiderstand geeignet. Bei einem Servotest
müssen Servoversorgung und Masseführung passend zum verwendeten Modul aufgebaut
werden.

### 74HC595

Der Test verwendet diese frei änderbare Zuordnung:

| ESP32 | 74HC595 | Bedeutung |
| --- | --- | --- |
| GPIO 16 | DS, Pin 14 | serielle Daten |
| GPIO 17 | SHCP, Pin 11 | Schiebetakt |
| GPIO 23 | STCP, Pin 12 | Speichertakt |
| 3,3 V | VCC, Pin 16 | Versorgung |
| GND | GND, Pin 8 | gemeinsame Masse |
| 3,3 V | MR, Pin 10 | Reset inaktiv |
| GND | OE, Pin 13 | Ausgänge aktiviert |

Q0 bis Q7 können jeweils über eine LED mit Vorwiderstand getestet werden. Das
Programm lässt zunächst ein einzelnes HIGH-Bit und anschließend ein einzelnes
LOW-Bit durch alle Ausgänge laufen.

Für weitere Ausgänge wird Q7S, Pin 9, mit DS des nächsten 74HC595 verbunden.
Schiebe- und Speichertakt werden von allen Bausteinen gemeinsam genutzt. Die
Anzahl der ESP32-Steuerleitungen bleibt dadurch bei drei.

Der 74HC595 stellt nur Ausgänge bereit. Taster oder andere Eingangssignale
können damit nicht eingelesen werden. Größere Lasten benötigen auch hier eine
geeignete Treiberstufe.

## Grundlage für die spätere Integration

Die fünf Programme kapseln die modulspezifischen Zugriffe jeweils in
einer kleinen Klasse. Nach erfolgreichem Hardwaretest können diese Klassen in
eigene Treiberdateien verschoben und anschließend von
`esp32_dobot_steuerung_v1_3.py` genutzt werden. Das bestehende Steuerprogramm
wird erst geändert, wenn Modul, Adresse und gewünschte Dobot-Befehle praktisch
geprüft sind.
