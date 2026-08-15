# Fusion – Zusammenarbeit mit ChatGPT

Autodesk Fusion ist das eigentliche Werkzeug für die Konstruktion. ChatGPT kann die Arbeit mit Fusion jedoch an vielen Stellen unterstützen: bei der Entwicklung einer Idee, bei Fragen zur Bedienung, beim Bewerten von Konstruktionsvarianten oder bei der Fehlersuche.

Bei unserer bisherigen Arbeit hat sich dabei eine einfache Rollenverteilung bewährt:

**Der Konstrukteur arbeitet selbst in Autodesk Fusion. ChatGPT begleitet die Arbeit als technischer Ratgeber und zweiter Blick.**

## Fusion bleibt das Konstruktionswerkzeug

Die eigentliche CAD-Konstruktion findet in Autodesk Fusion statt.

Dort werden unter anderem:

* Skizzen erstellt,
* Maße festgelegt,
* Körper und Komponenten konstruiert,
* Baugruppen zusammengesetzt,
* Bauteile ausgerichtet,
* Passungen überprüft,
* Modelle für den 3D-Druck vorbereitet.

ChatGPT ersetzt diese Arbeit nicht.

Eine von einer KI erzeugte 3D-Darstellung kann beispielsweise sehr anschaulich zeigen, wie ein Bauteil aussehen könnte. Sie ist aber noch kein echtes CAD-Modell und kann nicht einfach als bearbeitbarer Körper in Fusion verwendet werden.

## ChatGPT als technischer Ratgeber

Besonders hilfreich ist ChatGPT, wenn während der Arbeit in Fusion eine konkrete Frage entsteht.

Zum Beispiel:

* Welche Fusion-Funktion eignet sich für den nächsten Schritt?
* Wie können zwei Komponenten ausgerichtet werden?
* Warum lässt sich eine Komponente nicht wie erwartet bearbeiten?
* Wie können mehrere Körper vereinigt werden?
* Welche konstruktiven Möglichkeiten gibt es für ein Gelenk?
* Wie könnte ein Bauteil druckgerechter gestaltet werden?
* Welche Maße sind für einen ersten Prototyp sinnvoll?

Dabei muss nicht zuerst eine vollständige Konstruktion geplant werden. Oft ist es sinnvoller, immer nur den nächsten überschaubaren Schritt zu betrachten.

## Screenshots aus Fusion

Für die Zusammenarbeit mit ChatGPT sind Screenshots besonders hilfreich.

Ein Screenshot kann beispielsweise zeigen:

* den aktuellen Aufbau einer Baugruppe,
* den Fusion-Browser mit seinen Komponenten und Körpern,
* eine geöffnete Skizze,
* einen Dialog für Gelenke oder Ausrichtungen,
* eine problematische Geometrie,
* das Ergebnis eines Konstruktionsschrittes.

Damit kann sich die Beratung auf den tatsächlichen Stand der Konstruktion beziehen.

Das ist oft wesentlich hilfreicher als eine lange allgemeine Anleitung, die möglicherweise gar nicht zur aktuellen Situation passt.

## Schrittweise arbeiten

Bei unseren Konstruktionen hat sich eine schrittweise Vorgehensweise bewährt.

Ein typischer Ablauf sieht so aus:

**Idee → Lösung diskutieren → in Fusion konstruieren → Ergebnis prüfen → Screenshot oder Frage an ChatGPT → Konstruktion anpassen → Probedruck → reales Bauteil testen → gegebenenfalls verbessern**

Dabei wird nicht versucht, von Anfang an jedes Detail theoretisch festzulegen.

Gerade beim 3D-Druck ist ein früher Prototyp oft aussagekräftiger als eine lange Diskussion über mögliche Toleranzen.

## Beispiel: Muffe für MakerBeam

Ein Beispiel dafür ist eine Verbindungsmuffe für MakerBeam-Profile mit einem Querschnitt von 10 × 10 mm.

Als Grundlage wurde das offizielle CAD-Modell des MakerBeam-Profils in Autodesk Fusion verwendet.

Für einen ersten Prototyp wurden unter anderem folgende Maße festgelegt:

* Innenmaß der Muffe: 10,3 × 10,3 mm
* Außenmaß: 15,3 × 15,3 mm
* Länge: 50 mm
* Befestigung mit M3-Schrauben
* Bohrungen für die Schrauben: 2,8 mm

Die Muffe wurde anschließend gedruckt und mit den realen MakerBeam-Profilen getestet.

Das Ergebnis war überzeugend:

* Die Profile ließen sich gut einschieben.
* Ohne Schrauben war nur minimales Spiel vorhanden.
* M3-Metallschrauben ließen sich direkt in die gedruckten Bohrungen einschrauben.
* Die Profile konnten zuverlässig geklemmt werden.

Damit war eine wichtige Entscheidung gefallen:

**Die erprobten Maße funktionieren und müssen nicht allein aufgrund theoretischer Überlegungen weiter verändert werden.**

Aus der zunächst einfachen Muffe entstanden anschließend weitere Bauteile für eine Kamerahalterung auf der Lochrasterplatte des Dobot Magician.

## Original-CAD-Daten verwenden

Wenn Hersteller CAD-Dateien ihrer Produkte zur Verfügung stellen, sollten diese möglichst als Grundlage verwendet werden.

Beim MakerBeam-System konnten die offiziellen STEP-Dateien direkt in Fusion eingebunden werden.

Das hat mehrere Vorteile:

* Abmessungen müssen nicht geschätzt werden.
* Die tatsächliche Geometrie des Bauteils steht zur Verfügung.
* Eigene Halterungen können direkt an das Originalmodell angepasst werden.
* Kollisionen und Passungen lassen sich bereits in Fusion prüfen.

Diese Vorgehensweise eignet sich nicht nur für MakerBeam, sondern beispielsweise auch für Roboter, Servos, Kameramodule, Mikrocontroller oder andere technische Bauteile.

## 3D-Konzeptdarstellungen

ChatGPT kann vor der eigentlichen CAD-Konstruktion auch 3D-Konzeptdarstellungen erzeugen.

Sie können helfen:

* eine Idee sichtbar zu machen,
* unterschiedliche Varianten miteinander zu vergleichen,
* die Funktionsweise eines Gelenks zu diskutieren,
* Missverständnisse früh zu erkennen,
* ungeeignete Lösungen zu verwerfen.

Gerade dabei zeigte sich aber auch eine wichtige Grenze.

Eine zunächst erzeugte Darstellung für eine drehbare MakerBeam-Verbindung entsprach nicht der gewünschten Mechanik. Erst durch eine genauere Beschreibung der Bewegung konnte eine passendere Variante dargestellt werden.

Solche Konzeptbilder sind deshalb **Hilfsmittel zum Denken und Diskutieren**.

Sie sind keine fertigen CAD-Konstruktionen.

## ChatGPT kann sich irren

Die Vorschläge von ChatGPT sollten nicht ungeprüft übernommen werden.

Auch bei unserer Arbeit gab es Situationen, in denen:

* eine Fusion-Funktion anders arbeitete als zunächst angenommen,
* ein vorgeschlagener Weg unnötig kompliziert war,
* eine Ursache zunächst falsch eingeschätzt wurde,
* die gewünschte Mechanik missverstanden wurde.

In solchen Fällen helfen Rückfragen, Screenshots und vor allem die Überprüfung direkt in Fusion.

Eine wichtige Regel lautet deshalb:

**ChatGPT schlägt Lösungen vor – der Konstrukteur prüft sie.**

Das gilt besonders für:

* Maße,
* Passungen,
* mechanische Belastungen,
* Materialeigenschaften,
* Drucktoleranzen,
* sicherheitsrelevante Konstruktionen.

## Das reale Bauteil entscheidet

Eine Konstruktion kann am Bildschirm sehr gut aussehen und trotzdem beim Drucken oder bei der Montage Probleme verursachen.

Deshalb gehören reale Tests zum Entwicklungsprozess.

Bei unseren Projekten ergibt sich häufig dieser Kreislauf:

**Konstruieren → Drucken → Ausprobieren → Bewerten → Verbessern**

Dabei können reale Messergebnisse wieder in die weitere Beratung mit ChatGPT einfließen.

So wird aus einer zunächst theoretischen Lösung schrittweise eine praktisch erprobte Konstruktion.

## Lernen mit Fusion und ChatGPT

Für Schüler bietet diese Arbeitsweise einen zusätzlichen Vorteil.

ChatGPT nimmt ihnen das Konstruieren nicht ab. Stattdessen müssen sie weiterhin selbst überlegen:

* Was soll das Bauteil können?
* Welche Maße werden benötigt?
* Wie müssen die Teile zueinander angeordnet werden?
* Welche Bewegung soll möglich sein?
* Ist das Bauteil druckbar?
* Funktioniert das gedruckte Teil tatsächlich?

ChatGPT kann bei diesen Fragen unterstützen und alternative Lösungswege zeigen.

Das Ziel sollte deshalb nicht sein, die Konstruktion möglichst vollständig von einer KI erzeugen zu lassen.

Viel sinnvoller ist es, die KI als Gesprächspartner einzusetzen, der beim eigenen Denken, Konstruieren und Prüfen hilft.

## Unsere Arbeitsweise

Für unsere Projekte hat sich inzwischen folgende Aufteilung bewährt:

**Autodesk Fusion**
für die eigentliche Konstruktion und den Zusammenbau.

**ChatGPT**
für Beratung, Erklärungen, Ideen, Analyse von Screenshots und Diskussion von Varianten.

**3D-Druck**
für den praktischen Test der konstruierten Bauteile.

**GitHub und unsere Webseite**
für die Dokumentation und Bereitstellung der Ergebnisse.

**Codex**
für klar begrenzte Änderungen und Ergänzungen an unserem GitHub-Repository.

So entsteht ein durchgängiger Arbeitsablauf von der ersten Idee bis zum dokumentierten und praktisch erprobten Bauteil.

## Fazit

Die bisherige Erfahrung lässt sich in einem Satz zusammenfassen:

**Wir konstruieren selbst in Autodesk Fusion – ChatGPT sitzt gewissermaßen daneben.**

Gerade diese Rollenverteilung hat sich als hilfreich erwiesen. ChatGPT kann schnell erklären, Ideen entwickeln und einen zweiten Blick auf ein Problem werfen. Die eigentliche Konstruktion, die Kontrolle der Maße und die Bewertung des realen Ergebnisses bleiben jedoch Aufgabe des Menschen.
