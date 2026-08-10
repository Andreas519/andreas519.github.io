🔴 Erstelle eine Zusammenfassung unseres Dialogs ab meinem Prompt → **Erstelle eine Zusammenfassung unseres Dialogs ab meinem Prompt:**

# Zusammenfassung des Dialogs

## Ab dem Prompt:

> *„Wir konzentrieren uns aktuell auf 'Vorbereitung des Pi' und 'Datenübertragung Pi - PC'. Danach 'Bilderkennung auf dem Pi bzw. PC'. Je nach Anwendungsfall ist das interessant.“*

---

# 1. Projektziel eingegrenzt

Wir haben bewusst entschieden, das Projekt **nicht zu breit** anzulegen.

Statt viele technische Möglichkeiten gleichzeitig zu betrachten, konzentrieren wir uns zunächst auf drei klar voneinander getrennte Phasen:

1. **Vorbereitung des Raspberry Pi**
2. **Datenübertragung zwischen Raspberry Pi und Windows-PC**
3. **Bilderkennung** (je nach Anwendungsfall auf dem Raspberry Pi oder dem Windows-PC)

Die eigentliche Bildverarbeitung soll erst beginnen, wenn die ersten beiden Phasen zuverlässig funktionieren.

---

# 2. Vorbereitung des Raspberry Pi

Ein wichtiger Grundsatz wurde festgelegt:

> **Der Raspberry Pi und der Windows-PC gelten vor Beginn eines Projektes als vollständig vorbereitet.**

Die Einrichtung des Raspberry Pi gehört **nicht** zum eigentlichen Projekt.

Dazu gehören beispielsweise:

* Raspberry Pi OS
* WLAN
* SSH
* Kamera
* benötigte Schnittstellen
* Start ohne grafische Benutzeroberfläche

Diese Arbeiten werden einmal durchgeführt und anschließend getestet.

Erst danach beginnt das eigentliche Projekt.

---

# 3. Start ohne grafische Benutzeroberfläche

Der Raspberry Pi wird grundsätzlich

> **ohne grafische Benutzeroberfläche**

gestartet.

Dadurch

* startet der Pi schneller,
* benötigt weniger Speicher,
* arbeitet stabiler.

Bei Bedarf kann jederzeit

```bash
startx
```

aufgerufen werden.

Falls der Raspberry Pi einmal nicht über das Netzwerk erreichbar ist, wird **nicht lange nach Fehlern gesucht**.

Dann werden

* Monitor,
* Tastatur und
* Maus

angeschlossen und die Einrichtung direkt am Raspberry Pi überprüft.

Dieses Verfahren wurde als besonders zuverlässig angesehen.

---

# 4. Verbindung zum Raspberry Pi

Der typische Ablauf wurde festgelegt:

1. Raspberry Pi einschalten.
2. Verbindung mit dem WLAN herstellen lassen.
3. Mit **Advanced IP Scanner** die IP-Adresse ermitteln.
4. Erste SSH-Verbindung herstellen.
5. Host-Schlüssel akzeptieren.
6. Danach erfolgen alle weiteren Arbeiten per SSH.

Der Advanced IP Scanner dient dabei ausschließlich zum Auffinden des Raspberry Pi.

Der eigentliche SSH-Schlüsselaustausch erfolgt erst beim ersten Verbindungsaufbau.

---

# 5. Datenübertragung Raspberry Pi ↔ Windows-PC

Es wurde beschlossen, **nicht möglichst viele Übertragungswege** zu unterstützen.

Stattdessen sollen lediglich zwei Verfahren verwendet werden.

## Variante A

Der Raspberry Pi speichert Bilder direkt in eine eingebundene Windows-Freigabe.

Dabei erhält jedes Bild einen eindeutigen Zeitstempel.

Beispielsweise:

```text
2026-08-01_23-18-42.jpg
```

Der Windows-PC kann jederzeit auf das aktuellste Bild zugreifen.

Diese Variante eignet sich insbesondere für:

* Zeitraffer
* kontinuierliche Bildaufnahme
* Maschinenbeobachtung
* Dokumentation

---

## Variante B

Der Windows-PC steuert den Ablauf.

Er fordert ein neues Bild an oder holt ein vorhandenes Bild per SSH/SCP ab.

Danach wird das nächste Bild aufgenommen.

Diese Variante eignet sich besonders für:

* OpenCV
* Robotik
* Dobot
* gezielte Bildauswertung

---

# 6. SSH und SCP

Wir kamen überein, dass

> **SSH und SCP nach der Vorbereitung des Raspberry Pi ohne Passwortabfrage funktionieren sollen.**

Dazu gehört das einmalige Einrichten einer SSH-Schlüsselanmeldung.

Die Passwortabfrage gehört **nicht** mehr zum späteren Unterricht.

---

# 7. Didaktische Grundsätze

Im weiteren Verlauf entstand eine grundsätzliche Diskussion über den Aufbau der Projekte.

Ein wesentlicher Gedanke war:

> Schülerinnen und Schüler sollen sich jeweils nur mit **einer neuen Schwierigkeit gleichzeitig** beschäftigen.

Beispielsweise:

Ist das Thema

> Bildübertragung,

dann funktionieren

* Raspberry Pi,
* WLAN,
* SSH,
* Kamera

bereits zuverlässig.

Die Schülerinnen und Schüler beschäftigen sich ausschließlich mit der Bildübertragung.

---

# 8. Unterricht statt Technik

Es wurde festgestellt, dass viele Jugendliche und auch Lehrkräfte nicht die Erfahrung besitzen, alle technischen Probleme gleichzeitig zu lösen.

Deshalb soll die Technik

> möglichst vollständig vorbereitet sein.

Erst wenn man die Lernenden besser kennt, können ihnen nach und nach weitergehende technische Aufgaben übertragen werden.

---

# 9. Dokumentation

Ein wichtiger Gedanke war die Trennung verschiedener Dokumentationsarten.

Nicht jede Dokumentation richtet sich an dieselbe Zielgruppe.

Es wurden drei Ebenen unterschieden:

## Einrichtungsanleitung

Für Betreuer.

Beschreibt die vollständige Vorbereitung eines Raspberry Pi.

---

## Arbeitsanleitung

Für Schülerinnen und Schüler.

Sie beginnt mit einem vollständig vorbereiteten Raspberry Pi.

---

## Hintergrundwissen

Für Interessierte.

Hier werden technische Zusammenhänge und weiterführende Informationen erklärt.

---

# 10. Ziel des Projektes

Zum Abschluss wurde deutlich, dass wir uns derzeit

> **nicht in der Erstellung von Unterrichtsmaterial**

befinden.

Vielmehr suchen wir zunächst

> **den einfachsten, zuverlässigsten und reproduzierbaren Arbeitsweg.**

Erst wenn dieser gefunden ist,

entstehen daraus

* Arbeitsanleitungen,
* Schüleraufgaben,
* Unterrichtsmaterialien.

---

# Fazit

Im Verlauf des Dialogs wurde deutlich, dass der Schwerpunkt des Projektes nicht auf möglichst vielen technischen Möglichkeiten liegt.

Vielmehr sollen

* zuverlässige,
* leicht nachvollziehbare und
* für den Unterricht geeignete

Arbeitsabläufe entwickelt werden.

Der Raspberry Pi und der Windows-PC gelten dabei als vorbereitete Werkzeuge.

Die Schülerinnen und Schüler sollen sich in jeder Unterrichtseinheit auf genau **eine neue Aufgabe** konzentrieren können und diese innerhalb der AG erfolgreich abschließen.

Diese Vorgehensweise bildet die Grundlage für die weitere Entwicklung des Projekts **Vision-System** und der daraus entstehenden Unterrichtsmaterialien.

🔴 Wir verfügen in der Schule in der Regel nicht über ~~Administratoren-Rechte~~ **Administratorrechte**.
🔴 Wir nutzen das Verzeichnis `C:\Users\Public\Programme`, ~~indem~~ **in dem** wir unsere Programme hinterlegen.

Das ist eine wichtige Rahmenbedingung und sollte für alle Schulprojekte gelten:

> **Die Arbeitsumgebung muss ohne Administratorrechte funktionieren.**

## Konsequenzen für unser Vorgehen

### OpenSSH Server unter Windows entfällt

Die Installation des Windows-Dienstes **OpenSSH Server** benötigt Administratorrechte. Deshalb verwenden wir diesen Weg nicht.

Der Raspberry Pi muss den Windows-PC also nicht per SSH erreichen.

Stattdessen nutzen wir die bereits möglichen Richtungen:

```text
Windows-PC ── SSH/SCP ──► Raspberry Pi
Raspberry Pi ── Windows-Freigabe ──► Windows-PC
```

Damit benötigen wir auf Windows keinen zusätzlichen Server.

### Zugriff vom Windows-PC auf den Pi

Windows nutzt den vorhandenen SSH-Client:

```powershell
ssh pi@192.168.2.128
```

Für Dateien:

```powershell
scp pi@192.168.2.128:/home/pi/test.jpg C:\Users\Public\Bilder\
```

Nach eingerichteter Schlüsselanmeldung kann dies ohne Passwortabfrage erfolgen.

### Übertragung vom Pi zum PC

Der Raspberry Pi schreibt direkt in eine vorbereitete Windows-Freigabe:

```text
/mnt/windows
```

Beispiel:

```bash
rpicam-still --nopreview -o /mnt/windows/test.jpg
```

Auch hierfür ist kein Windows-SSH-Server erforderlich.

## Portable Programme

Der **Advanced IP Scanner** kann ohne Installation gestartet werden. Er kann bereitliegen:

```text
C:\Users\Public\Programme\Advanced-IP-Scanner\
```

oder auf:

* einem Netzlaufwerk,
* einem USB-Stick,
* einem gemeinsamen Schulordner.

Das passt gut zur schulischen Umgebung, weil keine Installation und keine Änderung am Windows-System notwendig sind.

## Gemeinsames Programmverzeichnis

Euer Ordner

```text
C:\Users\Public\Programme
```

ist dafür sehr geeignet:

* alle Benutzer können darauf zugreifen,
* ihr besitzt dort Schreibrechte,
* portable Programme können gemeinsam genutzt werden,
* Programme bleiben unabhängig vom jeweils angemeldeten Benutzer.

Eine mögliche Struktur wäre:

```text
C:\Users\Public\Programme\
├── Advanced-IP-Scanner\
├── Thonny\
├── Python\
├── VSCode\
├── Git\
└── Vision-System\
```

Für Projektdateien könnte ergänzend ein eigener gemeinsamer Ordner dienen:

```text
C:\Users\Public\Projekte\
└── raspberry_pi_zero_cam\
    ├── bilder\
    ├── python\
    └── dokumentation\
```

Damit ist unser einfacher Standardweg klar:

1. Pi und PC werden einmal vorbereitet.
2. Der Pi wird mit dem Advanced IP Scanner gefunden.
3. Windows greift per SSH oder SCP auf den Pi zu.
4. Der Pi schreibt bei Bedarf in eine Windows-Freigabe.
5. Alle benötigten Programme liegen portabel unter `C:\Users\Public\Programme`.

Das ist für die Schule deutlich brauchbarer als Lösungen, die Administratorrechte voraussetzen. 👍
