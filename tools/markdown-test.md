# markdown-test.md

<table>
  <thead>
    <tr>
      <th colspan="2">Linke Pinreihe</th>
      <th colspan="2">rechte Pinreihe 1</th>
      <th colspan="2">rechte Pinreihe 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Spalte 1</td>
      <td>Spalte 2</td>
      <td>Spalte 3</td>
      <td>Spalte 4</td>
      <td>Spalte 5</td>
      <td>Spalte 6</td>
    </tr>
    <tr>
      <td>Inhalt</td>
      <td>Inhalt</td>
      <td>Inhalt</td>
      <td>Inhalt</td>
      <td>Inhalt</td>
      <td>Inhalt</td>
    </tr>
  </tbody>
</table>

| Spalte 1 | Spalte 2 | Spalte 3 | Spalte 4 | Spalte 5 | Spalte 6 |
|---|---|---|---|---|---|
|-Pin-|-Bemerkungen-|-Pin-|-Bemerkungen-|-Pin-|-Bemerkungen-|
| a1  | b2  | c3  | d4  | d5  | e6  |




 
## Pinbelegung des CJMCU-Moduls

### Linke Anschlussreihe

Von oben nach unten:

| Modulbeschriftung | MCP23017-Funktion | Verwendung bei I²C |
|---|---|---|
| `A2` | Adressbit 2 | LOW oder HIGH |
| `A1` | Adressbit 1 | LOW oder HIGH |
| `A0` | Adressbit 0 | LOW oder HIGH |
| `RESET` | Reset-Eingang, aktiv LOW | Über etwa 10 kΩ mit 3,3 V verbinden |
| `NC/SO` | SPI-Datenausgang | Bei I²C nicht belegt |
| `NC/CS` | SPI-Chip-Select | Bei I²C nicht belegt |
| `SDA/SI` | I²C-Datenleitung / SPI-Dateneingang | SDA mit ESP32-GPIO21 verbinden |
| `SCL/SCK` | I²C-Takt / SPI-Takt | SCL mit ESP32-GPIO22 verbinden |
| `GND` | Masse | Mit ESP32-GND verbinden |
| `VCC` | Versorgung | Mit 3,3 V verbinden |

### Rechte doppelte Anschlussreihe

Von oben nach unten:

| Linke Beschriftung | Rechte Beschriftung | Bedeutung |
|---|---|---|
| `VCC` | `GND` | Versorgung und Masse |
| `ITB` | `ITA` | Gemeint sind vermutlich `INTB` und `INTA` |
| `B0` | `A0` | GPB0 und GPA0 |
| `B1` | `A1` | GPB1 und GPA1 |
| `B2` | `A2` | GPB2 und GPA2 |
| `B3` | `A3` | GPB3 und GPA3 |
| `B4` | `A4` | GPB4 und GPA4 |
| `B5` | `A5` | GPB5 und GPA5 |
| `B6` | `A6` | GPB6 und GPA6 |
| `B7` | `A7` | GPB7 und GPA7 |

### Anschlüsse für unseren Interrupt-Test

| Modulanschluss | Verbindung |
|---|---|
| `VCC` | 3,3 V, rot |
| `GND` | ESP32-GND, blau |
| `SDA/SI` | ESP32-GPIO21, gelb |
| `SCL/SCK` | ESP32-GPIO22, grün |
| `RESET` | Über etwa 10 kΩ an 3,3 V |
| `A2`, `A1`, `A0` | GND für Adresse `0x20` |
| `ITB` beziehungsweise `INTB` | ESP32-GPIO16 |
| `B0` beziehungsweise `GPB0` | Taster gegen GND |
| `B1` beziehungsweise `GPB1` | Taster gegen GND |
| `NC/SO` | Nicht verbinden |
| `NC/CS` | Nicht verbinden |