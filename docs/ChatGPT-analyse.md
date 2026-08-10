



🔴 ~~Überprüfe https://andreas519.github.io/index.html, sowie Projekte und Themen.~~ **Überprüfe https://andreas519.github.io/index.html sowie die Bereiche „Projekte“ und „Themen“.**

## Ergebnis der Prüfung

Deine Seite ist **online, erreichbar und grundsätzlich benutzbar**. Die Startseite zeigt die Bereiche **Projekte**, **Themen**, **Über diese Seite**, **Projektkontext** und **Hinweise zur Nutzung**. citeturn515404view0

Die Bereiche **Projekte** und **Themen** sind ebenfalls erreichbar. Die Projektübersicht öffnet unter `projekte/index.html`, die Themenübersicht unter `themen/index.html`. citeturn925425view0turn925425view1

---

## 1. Startseite `index.html`

### Positiv

Die Startseite wirkt jetzt deutlich aufgeräumter. Sie führt sauber zu:

- **Projekte**
- **Themen**
- erklärendem Kontext zur AG Young Engineers
- Nutzungshinweisen

Die Formulierung zur öffentlichen Präsentationsfläche passt gut zu deinem Ziel: überarbeitete Projekte öffentlich zeigen, Arbeitsstände aber getrennt halten. citeturn515404view0

### Auffällig

Auf der öffentlich gerenderten Seite steht weiterhin:

```text
Letzte Änderung: TT.MM.JJJJ, hh:mm Uhr
```

Das bedeutet: Entweder wurde das JavaScript beim Auslesen durch das Prüfwerkzeug nicht ausgeführt, oder der Browser lädt noch eine alte Version. Der JavaScript-Code zum Setzen von `lastModified` ist in `js/script.js` vorhanden. citeturn515404view0turn787061view3

Für die echte Browserprüfung:

```text
Strg + F5
```

oder:

```text
Strg + Umschalt + R
```

---

## 2. Bereich „Projekte“

Die Projektübersicht ist erreichbar und enthält mehrere sinnvolle Einträge: 28BYJ-48, 74HC595, LED-Matrix, ESP-Speicheroszilloskop, ESP32-WLAN-Programmauswahl, Softwareinstallationen, Testseiten und Tools. citeturn925425view0

### Wichtigster Fehler: doppelte Einträge / Mischstand

In der Rohdatei `projekte/index.html` tauchen einige Dopplungen und Altstände auf:

```html
* LED-Matrix - in Arbeit / Präsentationsversion
* LED-Matrix - in Arbeit / Präsentationsversion
```

und:

```html
* ESP32-WLAN-Programmauswahl/ - in Arbeit / Präsentationsversion
* ESP32-WLAN-Programmauswahl/ - in Arbeit / Präsentationsversion
```

Diese Dopplungen sind in der Rohdatei sichtbar. citeturn787061view1

Ich würde die Projektübersicht bereinigen auf etwa:

```html
<h2>Projektübersicht</h2>

<section>
  <h3>Elektronik und Mikrocontroller</h3>
  <ul>
    <li><a href="28BYJY-48/">28BYJ-48 Schrittmotor</a> – in Arbeit / Präsentationsversion</li>
    <li><a href="74HC595/">74HC595 Schieberegister</a> – in Arbeit / Präsentationsversion</li>
    <li><a href="LED-Matrix/">LED-Matrix</a> – in Arbeit / Präsentationsversion</li>
  </ul>
</section>

<section>
  <h3>ESP32-Projekte</h3>
  <ul>
    <li><a href="ESP-Speicheroszilloskop/">ESP32-Speicheroszilloskop</a> – in Arbeit / Präsentationsversion</li>
    <li><a href="ESP32-WLAN-Programmauswahl/">ESP32-WLAN-Programmauswahl</a> – in Arbeit / Präsentationsversion</li>
    <li><a href="ESP32/pin-in-out-adc/">Test der Pins: IN, OUT, ADC</a> – in Arbeit</li>
  </ul>
</section>

<section>
  <h3>Werkzeuge und Tests</h3>
  <ul>
    <li><a href="test/">Testseiten</a></li>
    <li><a href="Tools/">Tools & Co.</a></li>
  </ul>
</section>
```

### Schreibweise

In der Projektübersicht steht:

```text
Github Desktop
```

Besser:

```text
GitHub Desktop
```

Das ist klein, aber auf einer Projektseite wirkt die offizielle Schreibweise sauberer. citeturn787061view1

---

## 3. Einzelne Projektseiten

### 28BYJ-48

Die Seite öffnet. Es gibt aber noch mehrere deutliche Textfehler. citeturn125983view0

Aktuell:

```text
Der Schrittmotor 28BYJ-48 mit Treibermodul ULN2003 - oft verwendet unseren Projekte
```

Besser:

```text
Der Schrittmotor 28BYJ-48 mit Treibermodul ULN2003 – oft verwendet in unseren Projekten
```

Aktuell:

```text
Animierte Modell zur Ansteuerung ...
```

Besser:

```text
Animiertes Modell zur Ansteuerung ...
```

Aktuell:

```text
Halbschritt und Vollschrittänderbar
```

Besser:

```text
Halbschritt und Vollschritt änderbar
```

### 74HC595

Die Seite öffnet und der Inhalt ist fachlich gut als Einstieg geeignet. Es gibt aber noch Sprachfehler. citeturn125983view1

Aktuell:

```text
Microkontollers(MC)
```

Besser:

```text
Mikrocontrollers (MC)
```

Aktuell:

```text
geschalten
```

Besser:

```text
geschaltet
```

### ESP-Speicheroszilloskop

Die Seite öffnet, aber der Seitentitel ist falsch: Sie wird als **„28BYJ – Young Engineers Projekt“** angezeigt, obwohl der Inhalt zum ESP32-Speicheroszilloskop gehört. citeturn125983view3

Korrektur im `<title>`:

```html
<title>ESP32-Speicheroszilloskop – Young Engineers Projekt</title>
```

Außerdem:

```text
verbindet sich der ESP32 mit eine vorhandenen WLAN
```

besser:

```text
verbindet sich der ESP32 mit einem vorhandenen WLAN
```

### ESP32-WLAN-Programmauswahl

Auch hier ist der Seitentitel falsch: Die Seite wird als **„28BYJ – Young Engineers Projekt“** angezeigt, obwohl sie den ESP32-WLAN-Programmstarter enthält. citeturn125983view4

Korrektur:

```html
<title>ESP32-WLAN-Programmauswahl – Young Engineers Projekt</title>
```

Außerdem ist auf der gerenderten Seite auffällig, dass drei Bildlinks offenbar ohne sichtbaren Linktext erscheinen. Das sieht in der Textauswertung so aus:

```text
Startbildschirm ... Testbildschirm ... Testbildschirm ...
```

mit leeren Linktexten. citeturn125983view4

Das ist nicht zwingend kaputt, aber für Barrierefreiheit und Übersicht besser so:

```html
<figure>
  <a href="bilder/startbildschirm.png">
    <img src="bilder/startbildschirm.png" alt="Startbildschirm des ESP32-WLAN-Programmauswahl-Projektes">
  </a>
  <figcaption>Startbildschirm des ESP32-WLAN-Programmauswahl-Projektes</figcaption>
</figure>
```

---

## 4. Bereich „Themen“

Die öffentlich gerenderte Themen-Seite zeigt im Prüfwerkzeug nur diese Überschriften:

```text
AIS-Flächenportal
Förderband
CNC-Fräse
B&R
```

Die eigentlichen Bildkarten sind aber in der Rohdatei vorhanden. Dort sind Links zu Tinkercad, Wokwi, Dobot Magician, Elektronikmodulen, 3D-Drucker, Makeblock Laserbox, Bauelementen und Robotiksystemen eingetragen. citeturn925425view1turn787061view2

Das bedeutet: **Die Themen-Seite ist vermutlich im Browser visuell viel besser als in der reinen Textauswertung.** Das Prüfwerkzeug liest Bilder ohne sichtbare Überschrift nur eingeschränkt aus.

### Meine wichtigste Empfehlung

Ergänze unter jedem Bild eine sichtbare Überschrift. Dann ist die Seite auch ohne Bilder, für Suchmaschinen und für Screenreader besser verständlich.

Beispiel:

```html
<article class="project-card">
  <a href="tinkercad/index.html">
    <img class="topic-preview-image"
         src="tinkercad/bilder/tinkercad-quer-250.png"
         width="250"
         height="141"
         alt="Tinkercad">
    <h3>Tinkercad</h3>
  </a>
</article>
```

Für alle Karten würde ich das so machen:

```html
<h3>Tinkercad</h3>
<h3>Wokwi</h3>
<h3>Dobot Magician</h3>
<h3>Elektronikmodule</h3>
<h3>3D-Drucker</h3>
<h3>Makeblock Laserbox</h3>
<h3>Bauelemente</h3>
<h3>Robotiksysteme und Fahrzeuge</h3>
```

Dann sieht man in jeder Prüfansicht sofort, was die Karte bedeutet.

---

## 5. Strukturproblem auf der Themen-Seite

In `themen/index.html` befindet sich sehr viel CSS direkt im HTML-Dokument. Die Datei hat über 300 Zeilen, davon ein großer Teil eingebettetes Styling. citeturn787061view2

Das funktioniert, ist aber langfristig unübersichtlich. Besser wäre:

```html
<link rel="stylesheet" href="../css/my.css?v=20260801-4">
<link rel="stylesheet" href="../css/themen.css?v=20260801-1">
```

Dann kommt das spezielle CSS für die Themenübersicht in:

```text
css/themen.css
```

Das ist kein Notfall, aber für dein Projekt sehr sinnvoll, weil die Seite sonst schnell schwer wartbar wird.

---

## 6. Konkrete Prioritäten

### Sofort korrigieren

```text
1. Dopplungen in projekte/index.html entfernen.
2. Falsche Seitentitel bei ESP-Speicheroszilloskop und ESP32-WLAN-Programmauswahl korrigieren.
3. Sichtbare Überschriften unter den Themen-Bildkarten ergänzen.
4. Textfehler bei 28BYJ-48 und 74HC595 korrigieren.
```

### Danach verbessern

```text
5. Spezielles CSS aus themen/index.html in eine eigene CSS-Datei auslagern.
6. Einheitliche Schreibweise verwenden: GitHub, GitHub Pages, Mikrocontroller, MicroPython.
7. Platzhalterkarten wie AIS-Flächenportal, Förderband, CNC-Fräse und B&R entweder als „in Vorbereitung“ kennzeichnen oder vorerst ausblenden.
```

## Gesamturteil

Die Seite ist auf einem guten Weg. 👍  
Die **Startseite** ist brauchbar, die **Projektübersicht** braucht Bereinigung, und die **Themenübersicht** sieht wahrscheinlich visuell gut aus, sollte aber zusätzlich sichtbare Textüberschriften bekommen. Genau das hilft dir später auch im Unterricht, weil Schüler nicht nur auf Bilder klicken, sondern sofort lesen können, wohin sie kommen.