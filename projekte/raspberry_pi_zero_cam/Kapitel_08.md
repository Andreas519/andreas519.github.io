# Kapitel 8 – Bildübertragung zwischen Raspberry Pi und Windows-PC

---

# Lernziel

Nach diesem Kapitel kannst du

- Bilder vom Raspberry Pi auf den Windows-PC übertragen,
- den Vorgang vollständig verstehen,
- die Übertragung automatisieren,
- die Technik später in Python verwenden.

---

# Ausgangssituation

Der Raspberry Pi nimmt Bilder auf.

Beispiel:

```

/home/pi/test.jpg

```

Nun sollen diese Bilder auf dem Windows-PC weiterverarbeitet werden.

Zum Beispiel

- OpenCV
- Dobot
- Dokumentation
- Archivierung

---

# Warum nicht einfach einen USB-Stick benutzen?

Natürlich wäre das möglich.

Der Ablauf wäre jedoch:

- Raspberry ausschalten
- Speicherkarte entnehmen
- am PC einstecken
- Bild kopieren
- Speicherkarte zurückstecken

Für ein einzelnes Testbild wäre das akzeptabel.

Für mehrere hundert Bilder oder eine automatische Bilderkennung ist dieser Weg ungeeignet.

Deshalb erfolgt die Übertragung über das Netzwerk.

---

# Warum verwenden wir SCP?

SCP bedeutet

**Secure Copy Protocol**

Es dient zum sicheren Kopieren von Dateien.

SCP nutzt dieselbe verschlüsselte Verbindung wie SSH.

Das bedeutet:

Wenn eine SSH-Verbindung funktioniert,

funktioniert fast immer auch SCP.

Ein zusätzlicher Server muss nicht installiert werden.

---

# Voraussetzungen

Vor Beginn sollten folgende Punkte erfüllt sein.

✓ Raspberry Pi eingeschaltet

✓ Raspberry Pi im WLAN

✓ SSH aktiviert

✓ Windows-PC im gleichen Netzwerk

✓ Testbild vorhanden

```

/home/pi/test.jpg

```

---

# Verbindung testen

Öffne auf dem Windows-PC

PowerShell

und gib ein

```powershell
ssh pi@raspi-zero-xx
```

Statt

```

raspi-zero-xx

```

kann auch die IP-Adresse verwendet werden.

Beispiel

```powershell
ssh pi@192.168.178.84
```

Nach Eingabe des Passwortes sollte die Linux-Konsole erscheinen.

Erst wenn dies funktioniert,

macht der nächste Schritt Sinn.

---

# Erstes Bild kopieren

Die allgemeine Form lautet

```powershell
scp Benutzer@Rechner:Datei Ziel
```

In unserem Beispiel

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg .
```

Der Punkt

```

.

```

bedeutet

> Speichere die Datei im aktuellen Windows-Ordner.

---

# Was passiert dabei?

```
              WLAN

     Raspberry Pi
     /home/pi/test.jpg
             │
             │
          SCP über SSH
             │
             ▼
      Windows-PC
```

Der Raspberry Pi sendet die Datei.

Windows speichert sie.

---

# Eigenen Zielordner verwenden

Praktischer ist ein fester Ordner.

Zum Beispiel

```

D:\Kamera

```

Dann lautet der Befehl

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg D:\Kamera\
```

Nach wenigen Sekunden befindet sich

```

test.jpg

```

im Ordner

```

D:\Kamera

```

---

# Unterordner anlegen

Ich empfehle folgende Struktur.

```
D:\
└── Kamera
    ├── Bilder
    ├── Videos
    ├── OpenCV
    └── Testbilder
```

Damit bleiben spätere Projekte übersichtlich.

---

# Bilder automatisch überschreiben

Während der Entwicklung genügt oft

```

test.jpg

```

Dieses Bild wird bei jeder Aufnahme ersetzt.

Vorteil

Immer nur ein aktuelles Bild.

---

# Bilder mit Zeitstempel speichern

Für Dokumentationen empfiehlt sich

```
2026-07-30_14-25-18.jpg
```

Dadurch bleibt jedes Bild erhalten.

---

# Häufige Fehlermeldungen

## Host nicht gefunden

```
Could not resolve hostname
```

Der Rechnername ist falsch.

Abhilfe

IP-Adresse verwenden.

---

## Verbindung verweigert

```
Connection refused
```

SSH ist nicht aktiviert.

---

## Passwort falsch

```
Permission denied
```

Benutzername oder Passwort überprüfen.

---

## Datei nicht gefunden

```
No such file
```

Pfad kontrollieren.

Mit

```bash
ls
```

bzw.

```bash
pwd
```

kann der aktuelle Ordner angezeigt werden.

---

# Automatisierung

Der Kopiervorgang lässt sich später vollständig automatisieren.

Dazu genügt beispielsweise eine Batch-Datei.

```batch
@echo off

scp pi@raspi-zero-xx:/home/pi/test.jpg D:\Kamera\
```

Ein Doppelklick genügt.

---

# Noch komfortabler

Später übernimmt

```
bildtransfer.py
```

die komplette Übertragung.

Der Anwender schreibt dann nur noch

```python
bildtransfer.hole_bild()
```

Intern verwendet das Modul

```
scp
```

Der Benutzer muss sich darum nicht mehr kümmern.

---

# Vorteile dieser Lösung

✓ keine zusätzliche Software

✓ verschlüsselte Übertragung

✓ einfach einzurichten

✓ leicht automatisierbar

✓ ideal für Unterricht

✓ funktioniert mit jedem Raspberry Pi

✓ funktioniert auch für andere Dateien

---

# Zusammenfassung

Für unser Kameraprojekt ist SCP die einfachste und zuverlässigste Möglichkeit, Bilder zwischen Raspberry Pi und Windows-PC zu übertragen.

Da SCP auf SSH basiert, ist keine zusätzliche Software auf dem Raspberry Pi erforderlich.

Die spätere Python-Bibliothek `bildtransfer.py` wird diese Technik vollständig kapseln, sodass Programme und Unterrichtsbeispiele unabhängig von der eigentlichen Übertragungsmethode bleiben.

---

# Nächster Schritt

Im nächsten Kapitel entwickeln wir das Python-Modul

```

kamera.py

```

Es übernimmt

- Bild aufnehmen
- Auflösung einstellen
- Dateinamen vergeben
- Aufnahmezeit festlegen
- Bild speichern

Die Übertragung erfolgt anschließend automatisch über

```

bildtransfer.py

```