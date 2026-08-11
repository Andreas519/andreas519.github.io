# Plan: ESP32 seriell mit mBot (mCore) koppeln

## Ziel

Ein ESP32-Modul wird über die serielle Schnittstelle mit dem mBot (mCore, Arduino-basiert) verbunden.  
Der ESP32 kann damit Befehle senden/empfangen und als WLAN-Bridge, Sensorknoten oder Steuereinheit dienen.

---

## Hardware

| Komponente | Hinweis |
|---|---|
| mBot (mCore, ATmega328-AU) | oben: **P3 Header 4** = WLAN-Steckplatz (Hardware-UART); RJ25-Port 4 → S1/S2 als SoftwareSerial |
| ESP32-Modul | 3,3 V-Logik |
| RJ25-Dupont-Wire-Kabel | nur für Anschlussweg B (RJ25-Port 4) |
| Bidirektionaler Level-Shifter | 5 V (mCore) ↔ 3,3 V (ESP32) zwingend erforderlich |

### Anschlussweg A: WLAN-Modul-Steckplatz (bevorzugt)

Der mBot hat auf der Oberseite **P3 Header 4** — einen 4-Pin-Steckplatz für das Makeblock
**„Me WiFi"-Modul** (original: ESP8266-basiert). Laut Schaltplan ist dieser direkt mit dem
**Hardware-UART** des ATmega328-AU verbunden (D0=RXD/PD0, D1=TXD/PD1), denselben Leitungen,
die auch der USB-Chip **CH340G (U5)** nutzt.

> Nicht verwechseln mit **P4 Header 3** (ebenfalls oben rechts) — das ist der Programmier-/Reset-Header
> mit den Signalen DTR, 5V und RESET.

> ⚠️ **Wichtig:** Der Hardware-UART ist derselbe, den der USB-Chip (CH340G) nutzt.  
> Während der ESP32 am WLAN-Steckplatz angeschlossen ist, **kann nicht gleichzeitig per USB
> hochgeladen oder der serielle Monitor geöffnet werden**. ESP32 vorher abstecken.

Der ESP32 wird per **Dupont-Kabel** direkt an die Pins des Steckplatzes angeschlossen.
Der Level-Shifter bleibt erforderlich, da der mCore mit 5 V arbeitet.

- Vorteil: kein RJ25-Kabel nötig, RJ25-Ports bleiben frei, Hardware-UART (stabiler als SoftSerial)
- Nachteil: kein gleichzeitiges USB-Debugging möglich

#### Pinbelegung WLAN-Steckplatz (P3 Header 4, mCore)

| Pin | mCore-Signal | Richtung |
|---|---|---|
| 1 | VCC 5 V | → Level-Shifter HV |
| 2 | GND | |
| 3 | TXD / D1 (PD1, ATmega328) | mCore → ESP32 RX |
| 4 | RXD / D0 (PD0, ATmega328) | ESP32 TX → mCore |

> Pinreihenfolge am physischen Steckplatz vor der Verdrahtung mit Multimeter verifizieren.

#### Verdrahtung mit Level-Shifter (Anschlussweg A)

```
mCore TXD (PD1) → HV-Seite HB1 → LV-Seite LB1 → ESP32 RX (z. B. GPIO16)
mCore RXD (PD0) ← HV-Seite HB2 ← LV-Seite LB2 ← ESP32 TX (z. B. GPIO17)
mCore GND       → GND Level-Shifter
mCore 5 V       → HV Level-Shifter
ESP32 3,3 V     → LV Level-Shifter
```

### Anschlussweg B: RJ25-Port 4 (SoftwareSerial, mit Kabel)

Alternativ: Verbindung über RJ25-Port 4 (A0/A1 als SoftwareSerial).  
Vorteil: USB bleibt gleichzeitig nutzbar. Nachteil: RJ25-Kabel + Dupont-Adapter nötig.

#### Pinbelegung RJ25-Port 4 / J4 (mCore)

| RJ25-Pin | mCore-Signal | Richtung |
|---|---|---|
| 1 | SCL (I2C) | |
| 2 | SDA (I2C) | |
| 3 | GND | |
| 4 | VCC 5 V | |
| 5 | S1 → A0 (PC4, SoftSerial RX mCore) | ESP32 TX → mCore |
| 6 | S2 → A1 (PC5, SoftSerial TX mCore) | mCore → ESP32 RX |

#### Verdrahtung mit Level-Shifter (Anschlussweg B)

```
mCore A0 (RX)  ← LV-Seite LB1 ← HV-Seite HB1 ← ESP32 TX (z. B. GPIO17)
mCore A1 (TX)  → LV-Seite LB2 → HV-Seite HB2 → ESP32 RX (z. B. GPIO16)
mCore GND      → GND Level-Shifter
mCore 5 V      → HV Level-Shifter
ESP32 3,3 V    → LV Level-Shifter
```

---

## Software mBot (Arduino IDE mit MeMCore-Bibliothek)

**Anschlussweg A** (WLAN-Steckplatz): `Serial` direkt verwenden — kein SoftwareSerial nötig.  
**Anschlussweg B** (RJ25-Port 4): `SoftwareSerial` auf A0/A1 verwenden.

### Ausgangspunkt

Vorhandene Datei: `mCore-SoftSerial-Port4.ino`  
(Quelle: Young-Engineers-Archiv, mBot-Themenbereich)

### Aufgaben

1. Basissketch laden und auf mBot übertragen
2. Im seriellen Monitor (9600 Baud) Verbindung testen
3. Befehlsprotokoll definieren (z. B. `F` = vorwärts, `B` = rückwärts, `L/R` = drehen, `S` = stop)
4. `zeichen_auswerten.ino` / `zeichenfolge_auswerten.ino` als Vorlage für Befehlsauswertung verwenden

---

## Software ESP32 (Arduino IDE oder MicroPython)

### Schritt 1 – SoftwareSerial-Test

Sketch: `ESP32-SoftSerial-mCore-Test.ino`

- Hardware-Serial2 des ESP32 auf RX=GPIO16, TX=GPIO17
- 9600 Baud
- Testnachrichten senden und empfangen

### Schritt 2 – Steuerung über WLAN (WLAN-Bridge)

- ESP32 öffnet einen einfachen TCP- oder UDP-Server (Port z. B. 1234)
- Empfangene Zeichen werden direkt an mCore weitergeleitet
- Antworten des mCore werden zurückgesendet

### Schritt 3 – ESP-Now (optional, drahtlose Erweiterung)

Vorhandene Basis: `ESP32-espnow-sender-receiver.py` (MicroPython)  
→ ESP32 empfängt ESP-Now-Pakete von zweitem ESP32/ESP8266 und leitet Befehle seriell weiter

---

## Teststufen

| Stufe | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| 1 | mCore ↔ PC (USB) mit seriellem Monitor | Zeichen werden korrekt übertragen |
| 2 | ESP32 ↔ PC (USB) | Serial2 sendet/empfängt |
| 3 | ESP32 ↔ mCore (Kabel + Level-Shifter) | Befehle steuern mBot |
| 4 | Smartphone / Browser → WLAN → ESP32 → mCore | mBot fährt auf WLAN-Befehl |

---

## Dateistruktur (geplant)

```
projekte/robokits/Makeblock/mBot/
├── plan.md                          ← diese Datei
├── index.html                       ← Projektseite (später)
├── arduino/
│   ├── mCore-SoftSerial-Port4/      ← mBot-Firmware
│   └── ESP32-SoftSerial-mCore/      ← ESP32-Firmware
└── bilder/
```

---

## Offene Fragen / nächste Schritte

- [ ] Welche ESP32-Variante wird eingesetzt? (DevKit, ESP32-CAM, …)
- [ ] Steuerung per Browser (Webserver auf ESP32) oder per zweitem Gerät (ESP-Now)?
- [ ] Soll der mBot auch Sensorwerte (Ultraschall, Linie) zurücksenden?
- [ ] Befehlsprotokoll festlegen (Einzelzeichen oder Zeichenkette)
