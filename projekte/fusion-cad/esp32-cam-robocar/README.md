# ESP32-CAM-Adapter für den Makeblock mBot

Das Projekt stellt einen parametrischen, gedruckten und praktisch geprüften Frontkamera-Adapter bereit. Der feste Adapter V3 nimmt ein ESP32-CAM-Modul oberhalb des Ultraschallsensors eines Makeblock mBot auf. Eine separat gedruckte Frontblende V3 fixiert Kamera und Platine.

## Aktueller Stand

Adapter V3 und Frontblende V3 wurden gedruckt, mit dem realen ESP32-CAM-Modul montiert und als fest sitzend bestätigt. Objektiv, Blitz-LED, Elektronik und Pinreihen bleiben entsprechend ihrer Funktion sichtbar beziehungsweise zugänglich.

Der Dummy mit abgerundeter Platine, 2 × 8 detaillierten Pins, Kunststoffträgern, Steckerleiste, Blitz-LED, Schriftzug und vierstufigem Kameraaufbau wurde in Autodesk Fusion visuell geprüft und als geeigneter Einbau-Dummy bestätigt. Ein älterer Entwurf für Kamerarahmen und U-Bügel bleibt im Generator erhalten, ist aber in `parameter.json` deaktiviert.

## Bestätigte Modulmaße

| Bezeichnung | Maß |
| --- | ---: |
| Platinenlänge | 40 mm |
| Platinenbreite | 27 mm |
| Platinendicke | 2 mm |
| Eckradius der Platine | 2 mm |
| Unterseite Platine bis Pin-Ende | 8 mm |
| Pinreihenabstand, Mitte zu Mitte | 22,5 mm |
| Stifte je Reihe | 8 |
| Stiftraster | 2,54 mm |
| Kunststoffträger ab unterer Platinenkante | 16,18 mm |
| weiße Kamerasteckerleiste | 19 × 4 × 1,5 mm, Mitte 13 mm ab Unterkante |
| angedeutete Blitz-LED | 3,5 × 3,5 × 1,2 mm, Mitte bei 24 × 7,5 mm |
| Kamera-Oberseite über Platinenoberseite | 8 mm |
| Mitte des 8-mm-Objektivsockels ab oberer Platinenkante | 9 mm |

Die obere Platinenkante liegt gegenüber dem Schriftzug `ESP32-CAM`. Die beiden 20,32 mm langen Pinreihen reichen von 16,18 bis 36,50 mm. Ihre Kunststoffträger enden damit 3,5 mm unterhalb der oberen Platinenkante und liegen auf der Platinenrückseite unter dem Kamerabereich. Die Querposition der Kamera wird zunächst mittig bei 13,5 mm angesetzt. Befestigungsbohrungen sind nicht vorhanden.

## Modellkonzept

- Dummy mit an allen vier Ecken um 2 mm abgerundeter Platine, zwei Kunststoffträgern und 16 einzelnen Vierkantstiften
- Schriftzug `ESP32-CAM`, weiße Kamerasteckerleiste und gelbe Blitz-LED als vereinfachte Orientierungskörper auf der Kameraseite
- Pin-Ende bis Platinenunterseite 8 mm, Platine 2 mm und Kameraaufbau 8 mm
- 15 × 15 × 2 mm großer Kameraunterbau bündig mit der oberen Platinenkante
- 8 × 8 × 2 mm großer Objektivsockel, dessen Oberkante 5 mm von der oberen Platinenkante entfernt liegt
- Kameraunterbau als Quader 15 × 15 × 2 mm
- Objektivsockel als Quader 8 × 8 × 2 mm
- mittlere Objektivstufe als Zylinder Ø 8 × 2 mm
- obere Objektivstufe als Zylinder Ø 7 × 2 mm
- offener Rahmen mit 0,4 mm Nennspiel um die Platine und 4 mm breiten Seiten für die M3-Drehbohrungen
- rückseitige Öffnung und zwei Freiräume für die herausstehenden Pinreihen
- Kamerabereich und Antennenseite bleiben frei
- Drehachse quer zur Platine auf Höhe der Kameramitte
- einteiliger U-Bügel hinter dem Kamerarahmen
- M4-Bohrung im unteren Bügelsteg zur Befestigung am Beam0412

Die Probedrucke bestätigten die Platinenpassung, Haltekanten, Pinfreiräume und den Kamerafreiraum. Die zunächst vorgesehene universelle Schwenkhalterung wurde zugunsten des kompakten festen mBot-Adapters zurückgestellt.

## Erster mBot-Adapter

Der Kamera-Dummy wurde mittig und senkrecht über dem Ultraschallsensor eines Makeblock mBot positioniert. Der erste breite Adapterentwurf wurde verworfen, weil die Halterung zwischen den beiden Ultraschallzylindern hindurchgeführt werden muss.

| Bezeichnung | Maß |
| --- | ---: |
| Befestigungsabstand, Lochmitte zu Lochmitte | 16 mm |
| vorhandene Durchgangsbohrung | 3,24 mm |
| konstruktiver Bohrungsdurchmesser | 3,4 mm |
| Schraubenkopfdurchmesser | 7,5 mm |
| oberer Schraubenkopfrand bis Oberkante Sonic-Modul | 28,25 mm |
| Lochmittellinie bis Oberkante Sonic-Modul | 32 mm, abgeleitet |
| Abstand Sonic-Modul bis untere Platinenkante | 5 mm |
| Lochmittellinie bis untere Platinenkante | 37 mm, abgeleitet |
| Mittenabstand der Sonic-Zylinder | 31,6 mm |
| freier Abstand zwischen den Sonic-Zylindern | 15,6 mm |
| Breite des schmalen Adapterhalses | 13,5 mm nach Probedruck |
| Ebenenversatz Sensorhalter zu Platine | 0,5 mm |
| Adapterbreite | 31 mm |

Der überarbeitete Entwurf besteht aus einem 4 mm starken unteren Schraubflansch, einer Verjüngung auf einen 13,5 mm breiten Hals zwischen den Sonic-Zylindern und einer Aufweitung auf 31 mm oberhalb des Sensors. In V3 reichen die Seitenführungen mit 42 mm um 2 mm über die Platine hinaus. Getrennte untere und obere Vorderlippen sowie zwei obere Rastnasen sichern das Modul gegen Herauskippen.

## Anpassung nach dem ersten Probedruck

Die Platine passt in die Aufnahme, konnte durch die nur 10 mm hohen Führungen aber nach vorne und hinten kippen. Außerdem federte der lange, 12 mm breite und 3 mm starke Adapterhals. Für den zweiten Probedruck wurden deshalb folgende Maßnahmen umgesetzt:

- Adapterstärke von 3 auf 4 mm erhöht
- Hals von 12 auf 13,5 mm verbreitert; im 15,6-mm-Zylinderabstand verbleiben nominell 1,05 mm Luft je Seite
- Seitenführungen von 10 auf 34 mm verlängert
- untere Halterippen weiterhin nur 10 mm hoch
- zusätzliche obere Sicherungslippen von 28 bis 33 mm ab Platinenunterkante
- mittlerer Bereich der Platinenkanten für Pinleisten und Lötstellen offen gehalten
- beide 90-Grad-Übergänge zur Platinenführung mit rückseitigen Dreiecksrippen von 8 × 14 × 2,4 mm verstärkt
- Rippen jeweils 1,2 mm über Aufweitung und Seitenführung gelegt und mit beiden Körpern vereinigt
- beide Rippen mit 2,4 mm breiten Freiräumen für die rückseitig herausstehenden Pinreihen versehen
- nach erneutem Passungstest auf praktisch spielfreie Aufnahme mit 0,05 mm Seitenspiel je Platinenkante und 0,1 mm Tiefenspiel zurückgeführt
- obere 3 mm der Seitenführungen mit 0,6 mm Einführungsschräge versehen

### Adapter V3

- die im Probedruck als passend bestätigte Aufnahme mit 0,05 mm Seitenspiel je Kante und 0,1 mm Tiefenspiel beibehalten
- Seitenführungen von 34 auf 42 mm verlängert
- je Seite eine 1 mm nach innen ragende Rastnase mit Einführungsschräge ergänzt
- obere Vorderlippen von 28–33 mm auf 35–40 mm verschoben, damit die Pinbeschriftungen sichtbar bleiben
- rückseitige Übergangsrippen ohne Pinfreiräume ausgeführt

## Fusion-Skript

`fusion/esp32_cam_holder_generator.py` liest `fusion/parameter.json` aus demselben Ordner. Mit `target: "ask"` fragt das Skript bei jedem Lauf, ob ausschließlich der Kamera-Dummy oder ausschließlich die mBot-Halterung erzeugt werden soll. So lassen sich beide Komponenten getrennt in die mBot-Baugruppe einfügen und prüfen. Kamerarahmen und U-Bügel für eine spätere universelle Variante bleiben mit `create_holder: false` deaktiviert.

Die erzeugte mBot-Komponente enthält zusätzlich die sichtbare `mBot Master-Skizze`. Sie zeigt Adapterkontur, M3-Bohrungen, Seitenführungen, Vorderlippen, Verstärkungsrippen und Mittellinie gemeinsam auf einer Ebene. Halsbreite, Lochabstand, Führungshöhe und Bohrungsdurchmesser sind als nicht treibende Kontrollmaße eingetragen.

## Aufschiebbare Frontblende

Beim Erzeugen der mBot-Halterung wird zusätzlich die separate Komponente `ESP32-CAM Frontblende` angelegt. Der erste Entwurf mit 31,60 mm Innenbreite saß auf der 31,00 mm breiten Halterung zu locker. Die seitlichen Flügel stehen nun nominell je 0,10 mm in das Halterungsmaß hinein. Das Innenmaß beträgt dadurch 30,80 mm und erzeugt beim Aufschieben eine leichte Klemmung.

Die Rückseite der Blende schließt bündig mit der Vorderseite des quadratischen Objektivsockels ab. Eine kreisförmige Öffnung mit 8,5 mm Durchmesser lässt nur den oberen runden Objektivteil hindurch. Bei V3 beginnt die Blende 14 mm über der unteren Platinenkante. Zwischen 14 und 17 mm bildet sie einen 3 mm hohen unteren Quersteg auf Höhe der weißen Kamerasteckerleiste. Der Steg stabilisiert den Rahmen gegen Kippeln, während der darunterliegende Teil des CAM-Moduls sichtbar bleibt. Klemmmaß und Objektivöffnung entsprechen weiterhin der im Probedruck hervorragend passenden V2. Die Blende ist eine eigene Komponente und kann deshalb separat als STL exportiert und gedruckt werden. Mit `generation.create_faceplate: false` lässt sich ihre Erzeugung abschalten.

## Kompakter U-Kamera-Clip

Der kompakte U-Kamera-Clip passte im Probedruck nicht über die Halterung und wird deshalb nicht mehr standardmäßig erzeugt (`generation.create_camera_clip: false`). Der Code bleibt vorerst als verworfene, optional aktivierbare Versuchsvariante erhalten.

Die weitere Erprobung konzentriert sich auf die große Adapterblende.

## Versionsprägung

Adapter und Frontblende erhalten beim Erzeugen unabhängige erhabene Versionskennungen. Aktuell stehen `generation.adapter_version` und `generation.faceplate_version` auf `V3`. Am Adapter sitzt die Prägung leserichtig auf der als Rückseite definierten, in Drucklage oberen Fläche des unteren Schraubflansches. Bei der verkürzten Frontblende liegt sie auf der dem Druckbett abgewandten Fläche rechts oberhalb des Objektivs. Die Buchstaben sind etwa 2 mm hoch und 0,5 mm erhaben.

## Ausblick: modularer Sensor-Turm

Der feste ESP32-CAM-Adapter bildet die Grundlage für eine spätere schwenkbare Sensorbaugruppe. Geplant ist ein Servo-Sensorturm, der Kamera und weitere richtungsabhängige Sensoren gemeinsam ausrichten kann. Austauschbare Sensoraufnahmen und fahrzeugspezifische Adapter sollen dieselbe Baugruppe am mBot und an weiteren Roboterfahrzeugen nutzbar machen.

Mögliche Module sind:

- ESP32-CAM oder andere Kameramodule
- Ultraschall-Abstandssensoren
- ToF-Abstandssensoren
- IR- und weitere richtungsabhängige Sensoren

## Mitwirkende und Entstehung

- **Andreas Sigismund:** Idee, Anforderungen, Maßaufnahme, konstruktive Entscheidungen, Probedrucke, Montage und praktische Erprobung; verantwortlicher Autor und Herausgeber.
- **OpenAI Codex:** KI-gestützte Entwicklungsunterstützung bei der parametrischen Fusion-Konstruktion, dem Python-Generator und der Aufbereitung der Projektdokumentation.

Die technische Verantwortung, Freigabe und Veröffentlichung des Projekts liegen bei Andreas Sigismund.

## Projektordner

- `fusion/`: Fusion-API-Skript und Parameter
- `models/`: Modellquellen und Referenzgeometrie
- `exports/`: STEP, STL und 3MF
- `bilder/`: Fotos, Maßskizzen, Renderings und Probedrucke
