# Bestandsaufnahme und Migrationsplan der alten mBlock-Seiten

Stand der Prüfung: 12. August 2026  
Quellbereich: <https://www.mrge.de/lehrer/sigismund/makeblock/>  
Vorgesehener Zielbereich: `themen/mblock/`

## Auftrag und Abgrenzung

Diese Dokumentation erfasst den über die HTML-Navigation erreichbaren Bestand des alten Makeblock-/mBlock-Bereichs. Untersucht wurden Seiten, Bilder, PDFs, Videos, Arduino-Programme, sonstige Downloads sowie interne und externe Links. Die eigentliche Migration ist ausdrücklich noch nicht Bestandteil dieses Arbeitsschritts.

Die **erste Ausbaustufe** ist bewusst auf wenige Sammel- und Lernseiten begrenzt. Weitere Unterseiten, Downloadbereiche und Komponentenseiten werden zunächst nicht angelegt. Es werden in dieser Planungsphase keine Inhalte oder Dateien aus dem alten Webbereich in das Repository kopiert.

Die Bestandsaufnahme ist vollständig bezüglich der am Stichtag von einer erreichbaren Seite aus verlinkten Ressourcen. Nicht verlinkte Dateien auf dem alten Webserver können ohne ein Server-Dateiverzeichnis nicht zuverlässig gefunden werden. Dynamische Zielseiten, insbesondere mBlock-Projekte, wurden auf Erreichbarkeit geprüft; ihre dauerhafte Verfügbarkeit und inhaltliche Funktionsfähigkeit muss während der Migration erneut im Browser getestet werden.

## Kurzfazit

- Der Crawl fand **24 redaktionelle HTML-Seiten**, **11 als HTML ausgelieferte Arduino-Beispiele**, **69 Bilder** (20 PNG, 22 JPG und 27 GIF), **13 PDF-Dateien**, **3 MP4-Dateien**, **2 CSS-Dateien** und **1 JavaScript-Datei**. Innerhalb des Quellpfads wurden insgesamt 123 Dateien mit rund 303 MB lokal analysiert; `wget` meldete einschließlich eines außerhalb des Pfads eingebundenen Stylesheets 125 Downloads.
- Die 13 PDF-Pfade enthalten nur **10 unterschiedliche Dateien**. Drei große PDFs liegen jeweils doppelt vor. Allein das englische mBlock-Lehrbuch ist etwa 125 MB groß und belegt durch die Dublette rund 250 MB.
- Inhaltlich wertvoll sind vor allem die selbst erstellten mBot-Aufgaben, Datenlogger-, Linienfolger-, Joystick- und IR-Unterlagen sowie die technischen Gerätebilder und Arduino-Beispiele.
- Fast alle Anleitungen verwenden mBlock 5.3.5 (2021), ältere mBlock-/Scratch-2-Oberflächen oder die damalige Makeblock-Arduino-Bibliothek. Sie dürfen erst nach einem Praxistest mit der aktuellen Software als aktuelle Anleitung veröffentlicht werden.
- Sämtliche zwölf geprüften Links unter `docs.makeblock.com/diy-platform/...` liefern 404. Weitere lokale Links zu einem PDF, drei Arduino-Dateien, einem mBlock-Projekt, einer Vorbereitungsseite und einem Bild sind defekt.
- Zeichencodierung, Rechtschreibung, uneinheitliche Begriffe sowie schul- und kursbezogene Handlungsanweisungen müssen redaktionell überarbeitet werden.
- **Große Hersteller-PDFs, Dubletten und Fremdmaterialien mit ungeklärten Nutzungsrechten werden nicht in das Repository übernommen.** Sie können nach fachlicher Prüfung und Rechteklärung allenfalls extern verlinkt oder bibliografisch im Archiv dokumentiert werden.

## Kennzeichnung

| Kürzel | Bedeutung |
|---|---|
| **G** | weiterhin geeigneter Inhalt; fachlich übernehmen bzw. als Grundlage nutzen |
| **S** | sprachlich/redaktionell überarbeiten |
| **T** | technisch veraltet oder vor Veröffentlichung zwingend neu testen |
| **U** | unvollständig; ergänzen oder mit einem anderen Inhalt zusammenführen |
| **D** | Dublette bzw. weitgehend doppelter Inhalt |
| **L** | fehlerhafter, unsicherer oder veralteter Link |
| **H** | historisch wertvoll; im Archivkontext erhalten, nicht als aktuelle Anleitung ausgeben |
| **R** | Rechte/Lizenz oder erlaubte Weiterveröffentlichung vor Übernahme klären |

## Zielstruktur der ersten Ausbaustufe

Die reduzierte erste Ausbaustufe trennt Einstieg, Projekte ohne Hardware, den ausgearbeiteten mBot-Lernpfad, zwei vorläufige Arduino-Sammelseiten und ein klar gekennzeichnetes Archiv. Weitere Spezialseiten werden erst in einer späteren Ausbaustufe entschieden.

```text
themen/mblock/
├── index.html
├── einstieg.html
├── projekte-ohne-hardware.html
├── mbot/
│   ├── index.html
│   ├── verbinden-und-testen.html
│   ├── grundlagen-aufgaben.html
│   ├── datenlogger.html
│   ├── linienfolger.html
│   ├── ir-fernbedienung.html
│   └── joystick.html
├── arduino/
│   └── index.html
├── arduino-ide/
│   └── index.html
├── archiv.html
└── README.md
```

| Zielseite | Zweck |
|---|---|
| `themen/mblock/index.html` | Einstieg, Voraussetzungen, Lernpfade und aktuelle Softwarelinks |
| `themen/mblock/einstieg.html` | mBlock-Oberfläche, Konto, Speichern, Veröffentlichen, Live-/Upload-Modus |
| `themen/mblock/projekte-ohne-hardware.html` | Panda, Zahlenschloss, Schalter/Taster/Lampen und Fußgängerampel |
| `themen/mblock/mbot/index.html` | mBot-Hardware, mCore, Sensoren/Aktoren und Lernpfad |
| `themen/mblock/mbot/verbinden-und-testen.html` | sichere Inbetriebnahme, Verbindung, Firmware, Ausgangstest |
| `themen/mblock/mbot/grundlagen-aufgaben.html` | LEDs, Taster, Licht, Motor, Ultraschall und erste Fahrprogramme |
| `themen/mblock/mbot/datenlogger.html` | Messwerte, Diagramm, Mittel-/Minimal-/Maximalwert |
| `themen/mblock/mbot/linienfolger.html` | Linienverfolgung und Teststrecke |
| `themen/mblock/mbot/ir-fernbedienung.html` | IR-Steuerung und Programmstruktur |
| `themen/mblock/mbot/joystick.html` | externer Joystick am Port 4 |
| `themen/mblock/arduino/index.html` | Sammelseite für Arduino Uno mit mBlock einschließlich Blinken und Multifunktionsshield |
| `themen/mblock/arduino-ide/index.html` | Sammelseite für den vorerst ungeprüften C/C++-Lernpfad; mBot, Starter, Ranger und Komponenten nur nach Praxistest |
| `themen/mblock/archiv.html` | alte Oberflächen, Handbücher und historische Unterrichtsmaterialien |
| `themen/mblock/README.md` | interne Projektabgrenzung, Struktur, Arbeitsphasen und Prüfstatus |

## Verbindlicher Prüfstatus

Die spätere Darstellung muss drei Zustände klar und sichtbar trennen:

### Aktuell und praktisch geprüft

- Nur Anleitungen, die mit dokumentierter Software-, Firmware- und Hardwareversion praktisch durchgeführt wurden, dürfen als aktuell erscheinen.
- Der Prüfvermerk nennt mindestens Prüfdatum, Testumgebung, Hardwaregeneration und bekannte Einschränkungen.
- Zum Stand dieser Bestandsaufnahme ist **noch keine alte Anleitung für die neue Website als aktuell und praktisch geprüft freigegeben**.

### Noch ungeprüfter Arbeitsstand

- Inhaltlich geeignete alte Aufgaben, Texte, Screenshots und Programme gelten zunächst ausschließlich als Arbeitsgrundlage.
- HTTP-Erreichbarkeit, frühere Unterrichtserfahrung oder erfolgreiches Lesen eines Dokuments ersetzen keinen aktuellen Praxistest.
- Ungeprüfte Arbeitsstände werden nicht als fertige Anleitung veröffentlicht und dürfen nicht unmarkiert in aktuelle Lernpfade gelangen.

### Historisch wertvoll

- Materialien mit dokumentarischem Wert werden inhaltlich beschrieben und über `archiv.html` eingeordnet.
- Historisches Material erhält Jahr/Version, Quelle, bekannte Einschränkungen und einen deutlichen Hinweis, dass es keine aktuelle Anleitung ist.
- Große Hersteller-PDFs, Dubletten und ungeklärte Fremdmaterialien werden auch zu Archivzwecken **nicht in das Repository kopiert**. Falls sinnvoll, werden lediglich Metadaten und ein geprüfter externer Verweis aufgenommen.

## Zuordnung der redaktionellen Seiten

| Alter Inhalt | Kurzinhalt | Bewertung | Vorgeschlagenes Ziel |
|---|---|---|---|
| `index.html` | Makeblock/mBlock-Einstieg, Roboter, Arduino IDE, Module, Katalog | G, S, T, L | `index.html`; historische Hersteller-/Kataloglinks ins `archiv.html` |
| `mblock.html` | mBlock 5.3.5, Veröffentlichung, Aufgabenübersicht, Binärzähler | G, S, T, U, L | `einstieg.html`, `projekte-ohne-hardware.html`; Binärzähler erst nach Wiederbeschaffung |
| `mblock/taster+schalter+lampen.php` | Schalter, Taster, Wechsel-/Stromstoßschaltung, Treppenlicht | G, S, T | `projekte-ohne-hardware.html` |
| `mblock/panda-rennt.php` | Sprite-Steuerung und Spielaufgabe | G, S, T | `projekte-ohne-hardware.html` |
| `mblock/panda-fangen.php` | Reaktionsspiel, Variablen, Zeitmessung | G, S, T | `projekte-ohne-hardware.html` |
| `mblock/fampel.php` | Fußgängerampel, Zustände, Objektkommunikation | G, S, T | als Abschnitt in `projekte-ohne-hardware.html` |
| `mblock/zahlenschloss.php` | Sequenz, Eingabe, Fehler-/Alarmbehandlung | G, S, T | `projekte-ohne-hardware.html` |
| `mblock/videos/mblock.html` | Camtasia-Player für „Projekt freigeben“ | T, U, H | Inhalt neu aufnehmen und in `einstieg.html` integrieren; Player nicht migrieren |
| `mblock/arduino.html` | sehr knapper Arduino-mit-mBlock-Einstieg | U, D | mit `arduino/index.html` zusammenführen |
| `mblock/arduino/pur.html` | Blinken, Frequenz und An-/Aus-Verhältnis | G, S, D | als Abschnitt in `arduino/index.html` |
| `mblock/arduino/blinken.html` | fast derselbe Blinken-Inhalt mit Bildfolge | G, S, D | mit `pur.html` in `arduino/index.html` zusammenführen |
| `mblock/arduino/mfs/index.html` | MFS-Grundprogramm, LEDs, Taster, Panda | G, S, T, U | als Abschnitt in `arduino/index.html`; Buzzer, Anzeige und Potentiometer ergänzen |
| `mblock/mbot.html` | mBot/mCore-Einführung und Materialsammlung | G, S | `mbot/index.html`; zulässige Downloads direkt bei der passenden Seite planen |
| `mblock/mbot/checklist.html` | Verbindung über Browser/mLink2, Firmware, 2.4G-Dongle | G, S, T, H | neu getestet in `mbot/verbinden-und-testen.html`; alte 2.4G-Erfahrung ins Archiv |
| `mblock/mbot/datenlogger.html` | Lichtsensor, Diagramm, Statistik, Video | G, S, T | `mbot/datenlogger.html` |
| `arduino-ide/index.html` | Übersicht mBot, Starter, Ranger, Ultimate, Shield | G, S, T, U, L | `arduino-ide/index.html`; nur tatsächlich ausgearbeitete Plattformen prominent |
| `arduino-ide/vorbereitung.html` | Bibliothek installieren, Header/Boards zuordnen | G, S, T | nach Test in `arduino-ide/index.html` integrieren |
| `arduino-ide/mbot.html` | mCore-Pins, Bibliothek, Beispiele, Module/Motor | G, S, T, L | vorerst als ungeprüfter Arbeitsstand in `arduino-ide/index.html` bündeln |
| `arduino-ide/starter.html` | Orion/Starter, Board-Auswahl | G, S, T, U, L | vorerst nur in `arduino-ide/index.html` einordnen; Detailausbau zurückstellen |
| `arduino-ide/ranger.html` | Auriga/Ranger, Board, RGB-LED, Schaltbild | G, S, T, U, L | vorerst nur in `arduino-ide/index.html` einordnen; Detailausbau zurückstellen |
| `parts/Me_Line_Follower_Array_V1.0.html` | Reverse-Engineering, 1-Wire, Bauteile, Beispiel | G, S, T, L, H | historisch in `archiv.html` dokumentieren; mögliche spätere Ausbaustufe |

Die vom Videoplayer erzeugte Seite `mblock/videos/mblock_player.html?embedIFrameId=embeddedSmartPlayerInstance` ist kein eigener redaktioneller Inhalt. Sie gehört technisch zum veralteten Camtasia-Export und wird nicht als Zielseite migriert.

## Zuordnung der Arduino-Programme

Die Dateien werden auf dem alten Server mit `.ino` im Namen, aber als HTML/Text ausgeliefert. In der ersten Ausbaustufe werden sie **nicht kopiert**. Sie bleiben ungeprüfte Arbeitsgrundlagen für `arduino-ide/index.html`. Erst nach Kompilierung mit aktueller Arduino IDE, aktuellem Boardpaket, fest dokumentierter Makeblock-Bibliothek und einem Test am Gerät kann später über echte UTF-8-`.ino`-Downloads entschieden werden.

| Altes Programm | Thema | Bewertung | Ziel |
|---|---|---|---|
| `arduino-ide/mbot/blinken.ino` | beide RGB-LEDs, drei Farben | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/blink.ino` | schneller werdender Farbwechsel | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/buzzer.ino` | Töne | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/Button-Onboard.ino` | Taster, Analogwert | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/Button-Onboard-erweitert.ino` | Flankenerkennung | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/lightSensor.ino` | Lichtsensor | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/linefinder.ino` | vier Sensorzustände | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/motor.ino` | Motoren vor/zurück/stop | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/ultrasonic-distance.ino` | Abstandsmessung | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/basic-line-following.ino` | einfacher Linienfolger | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/mbot/ir-sensor.ino` | IR-Tasten dekodieren | G, T | Arbeitsgrundlage für `arduino-ide/index.html` |
| `arduino-ide/ranger/blink.ino` | Beispiel referenziert mCore-Pins statt Auriga-Ring | T, möglicherweise fehlerhaft | nicht übernehmen; erst korrigieren und testen |
| `parts/Me_Line_Follower_Array_V1.0/beispiel.ino` | eigenes Auslesen des Sensorprotokolls | G, T, H | in `archiv.html` dokumentieren; nicht übernehmen |

Im Linktext angekündigte, aber fehlende Programme:

- `arduino-ide/mbot/ultrasonic-lamp-timer.ino` - 404; der Code ist jedoch in `Makeblock mBot Input Output Functions.pdf` auf Seiten 10-11 enthalten und kann nach Test rekonstruiert werden.
- `arduino-ide/starter/blinken.ino` - 404; aus dem mBot-Beispiel ableitbar, aber erst mit `MeOrion.h` und echter Starter-Hardware testen.
- `arduino-ide/ranger/distance+ton.ino` - nur als sichtbar gewordener fehlerhafter HTML-Rest vorhanden, nicht als funktionierender Link/Download.

## Zuordnung der PDFs und Downloads

| Datei | Umfang/Größe | Bewertung und Inhalt | Ziel/Entscheidung |
|---|---:|---|---|
| `mblock/mbot/aufgaben.pdf` | 3 S., 678 KB | G, S, T; eigene Aufgaben zu LEDs und Lichtsensor | Inhalte modernisieren und in `mbot/grundlagen-aufgaben.html` überführen; Original optional im Archiv |
| `mblock/mbot/mBot-Linienverfolgung.pdf` | 3 S., 337 KB | G, S, T; eigener Lernweg Live-/Upload-Modus und Linie | Grundlage für `mbot/linienfolger.html`; Screenshots neu erstellen |
| `mblock/mbot/IR-Fernbedienung.pdf` | 4 S., 573 KB | G, S, T; eigene IR-Aufgaben, verschachtelte Auswahl, Laufzeit | Grundlage für `mbot/ir-fernbedienung.html`; Screenshots neu erstellen |
| `mblock/mbot/joystick.pdf` | 3 S., 568 KB | G, S, T; eigenes Material vom 12.06.2022 | Grundlage für `mbot/joystick.html`; Erweiterungsname und Werte neu testen |
| `mblock/mbot/20160420_mbot_aufgaben.pdf` | 8 S., 560 KB | G, T, H, R; externes Material des Instituts ICT & Medien, ältere mBlock-Oberfläche | nicht übernehmen; in `archiv.html` nur bibliografisch dokumentieren, Aufgaben ggf. eigenständig neu formulieren |
| `mblock/20160420_mbot_aufgaben.pdf` | identisch | D | nicht migrieren; exakt dieselbe SHA-256 wie obige Datei |
| `mblock/mbot/mBlock Kids maker rocks with the robots.pdf` | 50 S., 125.4 MB | T, H, R; englisches Hersteller-Lehrbuch für Scratch 2/mBlock, teils chinesische Reste | nicht übernehmen; externe aktuelle Quelle suchen und höchstens bibliografisch im Archiv nennen |
| `mblock/mBlock Kids maker rocks with the robots.pdf` | identisch | D | nicht migrieren |
| `mblock/mbot/mBot instruction.pdf` | 8 S., 9.6 MB | G, H, R; englische alte Schnell-/Montageanleitung | nicht übernehmen; aktuelle offizielle Anleitung extern verlinken oder Altversion bibliografisch dokumentieren |
| `mblock/mbot/mBot-V1.1-Blue_DE_D1.1.5_Edit.pdf` | 25 S., 13.3 MB | G, H, R; deutsche mBot-V1.1-Anleitung | nicht übernehmen; aktuelle offizielle Anleitung suchen, Altversion nur bibliografisch dokumentieren |
| `mblock/mBot-V1.1-Blue_DE_D1.1.5_Edit.pdf` | identisch | D | nicht migrieren |
| `arduino-ide/Makeblock mBot Input Output Functions.pdf` | 11 S., 199 KB | G, T, H, R; Pinmapping und C++-Beispiele; Quelle/Autor im PDF nicht eindeutig | nicht übernehmen; nur als interne Arbeitsquelle bewerten, Code eigenständig testen |
| `arduino-ide/ranger/MeAurigaSchaltbild.pdf` | 1 S., 1.08 MB | G, H, R; Schaltplan | nicht übernehmen; Herkunft/Rechte klären und höchstens externe Quelle dokumentieren |

Für die erste Ausbaustufe gilt verbindlich: **Große Hersteller-PDFs, sämtliche Dubletten und alle Fremdmaterialien mit ungeklärten Rechten werden nicht in das Repository übernommen.** Eine historische Einordnung in `archiv.html` bedeutet nur Beschreibung, Metadaten und gegebenenfalls einen geprüften externen Link, nicht das lokale Ablegen der Datei.

Defekte oder fehlende Downloads:

- `MINT-Coding im Unterricht.pdf` - 404. Der Link bezeichnet einen Auszug aus einem Gesamtkatalog 2018/19; neu beschaffen oder streichen.
- `makeblock/mblock/binaerzaehler.mblock` - 404 durch doppelte Pfadkomponente. Auch unter dem naheliegenden Pfad wurde beim Crawl keine Datei gefunden; Originalprojekt suchen.

## Zuordnung der Videos und Player-Dateien

| Datei | Bewertung | Ziel |
|---|---|---|
| `mblock/mbot/datenlogger/v1.mp4` | G, T; Demonstration des Variablen-/Zeitverhaltens | nach Sicht- und Aktualitätsprüfung in `mbot/datenlogger.html` |
| `mblock/videos/Wechselschaltung-mBlock.mp4` | G, T | nach Neuprüfung in `projekte-ohne-hardware.html`; besser neu aufnehmen |
| `mblock/videos/Taster+Lampe-1.mp4` | G, T | nach Neuprüfung in `projekte-ohne-hardware.html`; besser neu aufnehmen |
| `mblock/videos/Wechselschaltung-mBlock.png` | G, T; Vorschaubild | gemeinsam mit aktualisiertem Video verwenden oder ersetzen |
| `mblock/videos/mblock_embed.css`, `mblock/videos/skins/remix/techsmith-smart-player.min.css`, `mblock/videos/scripts/config_xml.js`, `mblock/videos/mblock_player...html` | T, D; alter TechSmith/Camtasia-Smart-Player | nicht migrieren; MP4 nativ per HTML5 einbetten |

Der Player verweist auf eine Anleitung „mBlock-Projekt freigeben“, die eigentliche Mediendatei wurde im Crawl jedoch nicht als eigenständiges Video gefunden. Der Inhalt ist daher **unvollständig** und sollte neu erstellt werden.

## Zuordnung sämtlicher Bildressourcen

Vollbilder und Miniaturansichten sollen bei der Migration nicht doppelt gepflegt werden. Wo beide Varianten existieren, wird nur das geeignet aufbereitete Original übernommen; responsive Größen kann der Browser beziehungsweise eine spätere Asset-Aufbereitung bereitstellen.

| Alte Dateien | Inhalt/Bewertung | Ziel |
|---|---|---|
| `logo.png` | Makeblock-Logo; R | `index.html`, nur bei erlaubter Markennutzung |
| `makeblock-Ports.png`, `makeblock-Ports-200.png` | D; Portfarben | `mbot/index.html` oder `arduino-ide/index.html`; nur eine Quelldatei |
| `mblock/panda-fangen-1.gif` | G, T; animierte Projektdemo | `projekte-ohne-hardware.html`, nach Aktualitätsprüfung |
| `mblock/projekte/fampel/Fussgaenger_Signalanforderung.jpg`, `ampel-phasen.jpg`, `ampel_anlage-fussgangeruberweg.jpg`, `ampel_anlage-fussgangeruberweg-mini.jpg` | G, S, D; Projektvorlagen und Phasen | späterer Abschnitt in `projekte-ohne-hardware.html`; Miniatur nicht übernehmen |
| `mblock/mbot/bilder/ansicht.png`, `ansicht-mini.png`, `mCoreLayout.png`, `mCoreLayout-mini.png`, `mCoreAnsicht.jpg`, `mCoreAnsicht-mini.jpg`, `mbot-grund-0.png` | G, D, teils R; mBot/mCore-Ansichten | `mbot/index.html` bzw. `verbinden-und-testen.html`; Miniaturen entfernen, Herkunft klären |
| `mblock/mbot/datenlogger/img7.jpg`, `img8.jpg`, `img9.jpg`, `imgA.jpg`, `imgB.jpg`, `imgD.jpg`, `imgE.jpg`, `runden.jpg`, `Fertig.jpg` | G, T; alte Block-Screenshots | als fachliche Vorlage für `mbot/datenlogger.html`; mit aktueller Oberfläche neu erstellen |
| `mblock/arduino/blinken/blinken-01.gif`, `blinken-01-min.gif`, `blinken-02-a.gif`, `-02-a-min.gif`, `-02-b.gif`, `-02-b-min.gif`, `-02-c.gif`, `-02-c-min.gif`, `-02-e.gif`, `-02-e-min.gif`, `-02-f.gif`, `-02-f-min.gif`, `-02-g.gif`, `-02-g-min.gif`, `-02-h.gif`, `-02-h-min.gif` | G, T, D; Blockfolgen für Blinkaufgaben; die Bezeichnung `02-d` fehlt | später in aktueller Oberfläche für `arduino/index.html` neu erzeugen; Altdateien jetzt nicht kopieren |
| `mblock/arduino/mfs/analog-digital.png`, `mfs-start.png`, `mfs-grundprogramm.png`, `mfs-grundprogramm-mini.png`, `mfs-leds.png`, `mfs-leds-mini.png`, `mfs-schaltplan.jpg`, `mfs-schaltplan-mini.jpg`, `uno+mfs.jpg`, `uno+mfs-mini.jpg` | G, T, D; Aufbau, Schaltplan und alte Blöcke | später für `arduino/index.html` prüfen; Screenshots erneuern, Altdateien jetzt nicht kopieren |
| `arduino-ide/aktoren/ME130-Motor-Daten.png`, `Me130_motor-Schaltbild.jpg`, `Me130_motor-oben.jpg`, `Me130_motor-unten.jpg` | G, R; technische Motordaten/-fotos | vorerst nur in `arduino-ide/index.html` einordnen; Quelle/Rechte klären |
| `arduino-ide/starter/starter.gif`, `starter-min.gif`, `orion.png`, `orion-min.png`, `orion-schaltbild.gif`, `orion-schaltbild-min.gif` | G, D, R | spätere Ausbaustufe; Rechte klären, jetzt nicht kopieren |
| `arduino-ide/ranger/ranger.gif`, `ranger-min.gif`, `MeAuriga.gif`, `MeAuriga-min.gif`, `MeAuriga-Schaltbild-min.gif`, `auriga-mainboad.gif` | G, D, R | spätere Ausbaustufe; Rechte klären, jetzt nicht kopieren |
| `parts/Me_Line_Follower_Array_V1.0/sicht-1.png`, `sicht-1-200.png` | G, D, H; eigene/technische Bauteilansicht | in `archiv.html` dokumentieren; jetzt nicht kopieren |

Das in `mblock/taster+schalter+lampen.php` referenzierte Bild `../../tinkercad/bilder/Stromstossrelais.gif` liegt außerhalb des untersuchten Makeblock-Pfads. Der Link ist erreichbarheitsseitig im Seitenkontext zu prüfen und soll langfristig nicht pfadübergreifend eingebunden werden; besser ist eine eigene, rechtegeklärte Abbildung oder ein Link zur vorhandenen Tinkercad-Seite.

## Interne Linkprobleme

Am Stichtag sicher fehlerhaft:

| Link/Ziel | Status | Maßnahme |
|---|---:|---|
| `MINT-Coding im Unterricht.pdf` | 404 | neu beschaffen oder Link entfernen |
| `makeblock/mblock/binaerzaehler.mblock` | 404 | Original suchen; Pfad enthält vermutlich irrtümliche Verdopplung |
| `arduino-ide/mbot/ultrasonic-lamp-timer.ino` | 404 | aus PDF rekonstruieren und testen |
| `arduino-ide/starter/blinken.ino` | 404 | neu erstellen und testen |
| `arduino-ide/ranger/auriga-mainboad-min\t.gif` | 404 | Tabulator im Dateinamen/Link; vorhandenes `auriga-mainboad.gif` nutzen oder neue Vorschau erzeugen |
| `/makeblock/vorbereitung.html` aus drei Arduino-IDE-Seiten | 404 | korrekt wäre damals `arduino-ide/vorbereitung.html`; in neuer Struktur direkt integrieren |
| sichtbarer Rest `ranger/distance+ton.ino` | kein funktionierender Link | Beispiel beschaffen/erstellen oder Text entfernen |

Außerdem uneinheitlich bzw. fehleranfällig:

- PHP-Seiten werden auf dem alten Server dynamisch ausgeliefert; im neuen statischen Bereich nur `.html` verwenden.
- Dateinamen enthalten Leerzeichen, Pluszeichen, Groß-/Kleinschreibung und sogar einen Query-String im lokalen Player-Dateinamen. Neue Namen ausschließlich klein, ASCII-nah und mit Bindestrichen.
- Mehrere Links zeigen mit absoluten URLs zurück in den alten Bereich, obwohl relative Ziele gemeint sind.
- `mblock/arduino.html` verlinkt nur die Unterseite, erklärt selbst aber kaum etwas.

## Externe Links: Prüfung am 12. August 2026

HTTP-Status allein beweist nicht die fachliche Richtigkeit. Besonders Projektseiten können mit Status 200 eine generische App-Hülle ausliefern; sie müssen während der Migration interaktiv geöffnet werden.

### Erreichbar, aber erneut fachlich prüfen

- `https://ide.mblock.cc/` - 200; derzeit sinnvoller Primärlink.
- `https://www.makeblock.com/` - 200.
- `https://www.makeblock.com/software/` - Weiterleitung auf eine erreichbare Softwareseite (200).
- GitHub-Repository und ZIP der `Makeblock-Libraries` - 200; dennoch letzte Version, Bibliotheksname und Arduino-Kompatibilität dokumentieren.
- Acht mBlock-Projekte unter `planet.mblock.cc` (`535772`, `558968`, `599385`, `610811`, `625029`, `1275523`, `1275524`, `1275711`) sowie zusätzlich das auf der Ampelseite gefundene Projekt `1351827` - HTTP 200; Projektinhalt, Remix-/Kopierbarkeit und Anmeldung einzeln testen.
- Wikipedia zu 1-Wire, Wechsel- und Stromstoßschaltung - 200.
- Google-Dokument zur Makeblock-Arduino-Programmierung - 200; Zugriffsrechte, Urheberschaft und Eignung als Quelle klären.
- STC15W201S-Datenblatt - 200.
- beide YouTube-Videos (`K8G0136gYqc`, `kbrvulEfuKA`) - 200; Inhalt, Datenschutz und Einbettung prüfen.
- Yumpu-Produktkatalog - 200; historisch und kommerziell, höchstens im Archiv verlinken.
- alte Tinkercad-Wechselschaltungs-Simulation im mrge-Bereich - 200; kann nach eigener Funktionsprüfung verlinkt werden.
- Google-Fonts-Stylesheet - reine Abhängigkeit des alten Players; nicht übernehmen, da der Player entfällt und die neue Seite das globale Repository-Styling nutzt.

### Fehlerhaft, entfernt oder ungeeignet

- Alle zwölf erfassten Links unter `http://docs.makeblock.com/diy-platform/...` - 404. Dazu gehören Übersichten, mCore, Orion, Auriga, MegaPi, Uno Shield, RGB Line Follower, Beschleunigungs-/Gyrosensor und das mCore-Bild. Durch aktuelle Herstellerdokumentation ersetzen.
- `https://mblock.makeblock.com/en-us/` - 404; durch `https://ide.mblock.cc/` beziehungsweise die aktuelle mBlock-Produktseite ersetzen.
- Store-Link `.../collections/diy-robit-kits` - Tippfehler und nach Weiterleitung 404. Nicht übernehmen; falls benötigt aktuelle Produktübersicht neu suchen.
- Ardubotics-Seite zum Me Line Follower Array - 404.
- Download des Hersteller-Beispielprogramms zum Line Follower Array - Weiterleitung, anschließend Status 526; nicht als verlässliche Quelle nutzen.
- Reichelt-Produktseite zum Me-130-Motor - nach Weiterleitung 410 (entfernt).
- Alldatasheet-Link zum LMV393I - 403 bei automatischer Prüfung; besser direkt auf ein Herstellerdatenblatt verlinken.

## Sprachliche und redaktionelle Befunde

Alle alten Seiten benötigen mindestens eine leichte Redaktion. Wiederkehrende Probleme:

- Zeichenkodierungsfehler (`FÃ¼...`, `f�r`) auf mehreren alten Seiten;
- Tipp- und Grammatikfehler, etwa „Mikroconroller“, „Frequeen“, „Por“, „denn Arduinoo“, „Ationen“, „Panad“, „Veröffenliche“, „mindesten“;
- uneinheitliche Schreibweisen: Makeblock/makeblock, mBot/mbot, LED/LEDs, Live-Modus/Hochladen-Modus;
- alte oder lokale Schulkontexte („Startmenü - 1. Unterricht“, Lernsax-Kursordner, Mail an Herrn Sigismund, Klassenbezeichnungen) vom dauerhaft nutzbaren Fachinhalt trennen;
- teilweise lange Arbeitsaufträge ohne Lernziel, Materialliste, erwartetes Ergebnis oder Lösungshinweis;
- Sicherheitsanweisungen sind vorhanden („aufgebockt“, Räder ohne Bodenkontakt), sollten aber einheitlich und sichtbar auf allen Fahr-/Motorseiten erscheinen;
- fremde Materialien wechseln zwischen deutscher und englischer Sprache und verwenden andere Anredeformen.

Empfohlener Standard je Lernseite:

1. Lernziele und Voraussetzungen,
2. benötigte Hard-/Software mit Versionsstand,
3. Sicherheits- und Verbindungscheck,
4. kleinschrittiger Grundversuch,
5. Aufgaben in drei Niveaustufen,
6. Test-/Fehlersuche,
7. Reflexionsfragen,
8. Downloads, Quellen, Lizenz und Aktualisierungsdatum.

## Technische Aktualitätsprüfung vor der Migration

Folgende Aussagen dürfen nicht ungeprüft übernommen werden:

- mBlock-PC-Version 5.3.5 vom 18.06.2021;
- Start und Zusammenspiel von mLink2, Browser-IDE, USB, Bluetooth und 2.4G-Dongle;
- Gerät, das ein neues mBlock-Projekt standardmäßig enthält (alt: CyberPi/Codey);
- Bezeichnungen und Positionen von Live-Modus, Upload-Modus, Firmware-Aktualisierung und Erweiterungen;
- Verfügbarkeit der Erweiterung „Maker's Platform“ für den Joystick;
- aktuelle mBot-Firmware und Verhalten nach Firmware-Update;
- Makeblock-Library, `MakeBlockDrive`, Headernamen und Arduino-Boardauswahl;
- Kompilierbarkeit aller Beispiele sowie Pinbelegungen für mCore, Orion und Auriga;
- Unterschied zwischen mBot-Hardwaregenerationen und den dazu passenden Anleitungen;
- Kopieren/Remixen/Veröffentlichen der verlinkten `planet.mblock.cc`-Projekte.

## Unvollständige Themen

- **mBlock-Einstieg:** Es fehlt eine aktuelle, eigenständige Einführung in Oberfläche, Dateiformat, Konto/Datenschutz und Fehlersuche.
- **Binärzähler:** Projektdatei fehlt vollständig.
- **Projekt veröffentlichen:** Player vorhanden, eigentlicher Lehrinhalt bzw. Video nicht vollständig auffindbar.
- **Arduino mit mBlock:** Übersichtsseite ist nur ein Fragment; Verbindung, Firmware, Live-/Upload-Modus und Fehlersuche müssen ergänzt werden.
- **Multifunktionsshield:** Buzzer, 7-Segment-Anzeige, Schieberegister und Potentiometer werden angekündigt, aber nicht ausgearbeitet.
- **Starter und Ranger:** nur kurze Inbetriebnahme; fehlende/defekte Beispiele und keine systematische Sensor-/Aktorfolge.
- **Ultimate, MegaPi und Uno Shield:** nur auf der Übersicht erwähnt, ohne eigene Inhalte. Entweder später ausarbeiten oder aus der Hauptnavigation entfernen.
- **Line Follower Array:** Schaltplan/Herkunft und Protokollbeschreibung sind unvollständig; eigene Messungen und Quellennachweis ergänzen.
- **Barrierefreiheit:** Alt-Texte, Transkripte/Untertitel, Tastaturbedienung und verständliche Linktexte fehlen weitgehend.
- **Lösungen/Lehrkraftmaterial:** keine klare Trennung zwischen Schülerauftrag, Erwartungshorizont und Lösung.

## Historisch wertvolle Inhalte

Folgende Materialien sollten erhalten bleiben, aber klar als historisch markiert werden:

- eigene Arbeitsblätter und Screenshots als Dokumentation der mBlock-Unterrichtsentwicklung;
- die 2.4G-Verbindungsbeschreibung als zeittypische Problemlösung;
- alte mBlock-/Scratch-2-Handbücher und Herstelleranleitungen mit Versionsangabe;
- technische Schaltbilder und Bilder inzwischen schlecht dokumentierter Makeblock-Komponenten;
- das selbst untersuchte Me Line Follower Array V1.0 einschließlich Beispielcode;
- die ursprünglichen Projektideen und Lernprogression (LED, Sensor, Steuerung, autonomes Fahren, Datenlogger).

Das Archiv soll Suchende nicht versehentlich in veraltete Arbeitsschritte führen. Jede Archivressource benötigt einen sichtbaren Hinweis „historischer Stand“, Jahr/Version, bekannte Einschränkungen, Quelle und gegebenenfalls Lizenz.

## Konkreter Migrationsplan

### Phase 1 - Entscheidungen und Sicherung

1. Die Bestandsaufnahme und vorhandenen Prüfsummen als Arbeitsnachweis bewahren; in dieser Phase keine Quelldateien aus dem alten Webbereich ins Repository kopieren.
2. Urheberschaft/Lizenz aller Hersteller- und Dritt-PDFs, Logos, Produktbilder, Schaltpläne und fremden Arbeitsblätter klären.
3. Entscheiden, welche Hardwaregenerationen tatsächlich noch im Unterricht eingesetzt werden: mBot, Starter/Orion, Ranger/Auriga, MFS, Line Follower Array.
4. Fehlende Originale suchen: Binärzähler, MINT-Katalogauszug, drei Arduino-Beispiele und Veröffentlichungsvideo.
5. Große Hersteller-PDFs durch aktuelle offizielle Links ersetzen; Dubletten und ungeklärte Fremdmaterialien grundsätzlich nicht übernehmen.

### Phase 2 - Technischer Labortest

1. Aktuelle mBlock-Web-/Desktop-Version und mLink unter den in der Schule verwendeten Betriebssystemen dokumentieren.
2. USB, Bluetooth und gegebenenfalls 2.4G mit jedem vorhandenen Gerät testen.
3. Live- und Upload-Modus, Firmware-Update und Projektveröffentlichung nachvollziehen.
4. Alle mBlock-Projekte öffnen, kopieren, speichern und ausführen; defekte Cloudprojekte lokal rekonstruieren.
5. Arduino-Beispiele mit festgehaltener IDE-/Library-Version kompilieren und auf echter Hardware testen.
6. Messergebnisse, Abweichungen zwischen Hardwareversionen und typische Fehler protokollieren.

### Phase 3 - Redaktion und Informationsarchitektur

1. Ausschließlich die für die erste Ausbaustufe festgelegten Seiten konzipieren; keine zusätzlichen Detailseiten anlegen.
2. Inhalte anhand der Zuordnungstabellen zusammenführen; Dubletten nicht seitenweise kopieren.
3. Einheitliches didaktisches Seitenmuster verwenden und Schulorganisation aus den allgemeinen Fachseiten herauslösen.
4. Screenshots mit aktueller Oberfläche neu aufnehmen; alte Ansichten nur im Archiv belassen.
5. Jede Anleitung sichtbar als „aktuell und praktisch geprüft“, „noch ungeprüfter Arbeitsstand“ oder „historisch wertvoll“ kennzeichnen.
6. Quellen, Versionen, Dateigrößen, Lizenzen, Prüf- und Aktualisierungsdatum sichtbar ausweisen.

### Phase 4 - Assets und Downloads

1. Erst nach abgeschlossenem Praxistest über benötigte neue oder zulässige eigene Bilder entscheiden; Altdateien nicht pauschal kopieren.
2. Bilder sinnvoll benennen, komprimieren und mit aussagekräftigen Alt-Texten versehen.
3. Videos nach Möglichkeit neu aufnehmen, komprimieren, mit Untertiteln/Transkript versehen und nativ einbetten.
4. Programme als echte `.ino`-Dateien sowie optional als ZIP-Paket anbieten; Quelltext zusätzlich auf der Seite zeigen.
5. Große Hersteller-PDFs, Dubletten und ungeklärte Fremdmaterialien nicht übernehmen. Eigene PDFs möglichst in zugängliches HTML überführen.

### Phase 5 - Umsetzung und Qualitätssicherung

1. Zielseiten schrittweise als statische HTML-Dateien unter `themen/mblock/` anlegen und vorhandene globale CSS-/JS-Strukturen nutzen.
2. Relative Pfade, Navigation, Downloads, Medien und externe Links lokal per HTTP-Server prüfen.
3. `tmp_check_links.py` ausführen und anschließend alle externen Links erneut prüfen.
4. Jede Anleitung von einer zweiten Person oder einer Lerngruppe praktisch durchführen lassen.
5. Erst nach vollständiger Abnahme Weiterleitungen von den alten URLs planen; historische URLs nicht ohne Ersatz abschalten.

## Empfohlene Priorität

1. **P0:** Einstieg, Verbindung/Firmware, mBot-Grundlagen und defekte Links.
2. **P1:** eigene mBot-PDFs in zugängliche HTML-Lernseiten überführen; Datenlogger, Linienfolger, IR und Joystick.
3. **P1:** Projekte ohne Hardware einschließlich Fußgängerampel auf einer gemeinsamen Seite aktualisieren.
4. **P2:** Arduino mit mBlock und Multifunktionsshield auf der Sammelseite `arduino/index.html` vervollständigen.
5. **P2:** Arduino-IDE-/C++-Bestand testen und zunächst auf `arduino-ide/index.html` bündeln.
6. **P3:** Starter, Ranger, seltene Komponenten und zusätzliche Detailseiten erst in einer späteren Ausbaustufe prüfen.
7. **P3:** Historisches nur beschreiben oder extern verlinken; keine großen Hersteller-PDFs, Dubletten oder ungeklärten Fremdmaterialien ablegen.

## Abnahmekriterien für die spätere Migration

- Jeder übernommene Inhalt ist genau einer aktuellen Zielseite oder dem Archiv zugeordnet.
- Jede Anleitung trägt einen eindeutigen Prüfstatus; als aktuell bezeichnete Anleitungen wurden praktisch getestet.
- Keine identischen Binärdateien liegen doppelt im neuen Bereich.
- Kein aktueller Lernweg verweist auf einen bekannten 4xx-/5xx-Link.
- Software-, Firmware-, Bibliotheks- und Hardwareversionen sind angegeben.
- Alle Programme wurden kompiliert und praktisch getestet.
- Alle mBlock-Cloudprojekte wurden interaktiv geprüft und besitzen möglichst eine lokale, exportierte Sicherung.
- Fremdmaterial besitzt Quellen- und Lizenzangaben oder wird nur verlinkt.
- Große Hersteller-PDFs, Dubletten und ungeklärte Fremdmaterialien befinden sich nicht im Repository.
- Bilder haben Alt-Texte; Videos haben Untertitel oder Transkript; PDFs haben eine HTML-Alternative oder einen begründeten Zweck.
- Alte Screenshots und Anleitungen sind eindeutig als historisch gekennzeichnet.
- Navigation, relative Pfade und Downloads bestehen den lokalen Linkcheck.

## Prüfnachweis

Für diese Bestandsaufnahme wurde der Quellbereich rekursiv ohne Überschreiten des Elternpfads gespiegelt. Alle erreichbaren HTML-Dateien wurden textuell und hinsichtlich ihrer Verweise ausgewertet. PDFs wurden über Metadaten, Prüfsummen, Seitenzahl, Textextraktion und stichprobenartige visuelle Darstellung geprüft. Externe und absolute interne Links wurden mit Weiterleitungsverfolgung und Zeitlimit abgefragt. Die Statuswerte sind Momentaufnahmen vom 12. August 2026 und müssen unmittelbar vor der Migration erneut validiert werden.
