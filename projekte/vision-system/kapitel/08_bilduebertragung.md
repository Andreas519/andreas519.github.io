# 8. Bildübertragung zwischen Raspberry Pi und Windows-PC

## 8.1 Ziel

Nach der Aufnahme soll ein Bild zuverlässig vom Raspberry Pi auf den Windows-PC gelangen. Dort kann es angezeigt, archiviert oder mit OpenCV ausgewertet werden.

In diesem Kapitel werden drei Wege betrachtet:

1. **Windows holt das Bild per SCP ab.**
2. **Der Raspberry Pi sendet das Bild per SCP an Windows.**
3. **Der Raspberry Pi schreibt in einen freigegebenen Windows-Ordner.**

Für den ersten praktischen Test wird Variante 1 empfohlen. Sie funktioniert mit dem bereits eingerichteten SSH-Zugang und erfordert auf dem Raspberry Pi keine zusätzliche Installation.

---

## 8.2 Was ist SCP?

SCP bedeutet **Secure Copy Protocol**. Es überträgt Dateien über eine verschlüsselte SSH-Verbindung.

SCP ähnelt FTP hinsichtlich seines Zwecks: Beide Verfahren übertragen Dateien zwischen Rechnern. SCP verwendet jedoch die vorhandene SSH-Verbindung und verschlüsselt Anmeldung und Nutzdaten.

```text
Windows-PC  ── SCP über SSH ──>  Raspberry Pi
       holt /home/pi/test.jpg ab
```

Wenn diese Anmeldung funktioniert,

```powershell
ssh pi@raspi-zero-xx
```

sollte in der Regel auch SCP funktionieren.

---

# Variante 1 – Windows holt das Bild per SCP

## 8.3 Voraussetzungen

- Raspberry Pi und Windows-PC befinden sich im gleichen lokalen Netz.
- SSH ist auf dem Raspberry Pi aktiviert.
- Der Windows-PC kann den Raspberry Pi per Hostname oder IP-Adresse erreichen.
- Auf dem Raspberry Pi existiert die Bilddatei `/home/pi/test.jpg`.
- Auf Windows ist der OpenSSH-Client vorhanden.

## 8.4 Testbild auf dem Raspberry Pi erzeugen

Im Terminal des Raspberry Pi:

```bash
cd /home/pi
rpicam-still --nopreview --width 1296 --height 972 -o test.jpg
ls -lh test.jpg
```

Der erste Befehl wechselt in den persönlichen Ordner des Benutzers `pi`. Der zweite nimmt das Bild auf. Der dritte prüft, ob die Datei vorhanden ist.

## 8.5 Zielordner auf Windows anlegen

In PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "D:\Kamera\Bilder"
Set-Location "D:\Kamera\Bilder"
```

Alternativ kann der Ordner im Windows-Explorer angelegt werden.

## 8.6 SSH-Verbindung zuerst prüfen

```powershell
ssh pi@raspi-zero-xx
```

Bei erfolgreicher Anmeldung erscheint die Eingabeaufforderung des Raspberry Pi. Danach mit folgendem Befehl abmelden:

```bash
exit
```

Falls der Hostname nicht gefunden wird, die IP-Adresse des Raspberry Pi ermitteln:

```bash
hostname -I
```

Beispiel:

```text
192.168.178.84
```

Dann unter Windows testen:

```powershell
ssh pi@192.168.178.84
```

## 8.7 Erstes Bild in den aktuellen Windows-Ordner holen

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg .
```

Der Punkt am Ende bedeutet: **in den aktuellen Ordner kopieren**.

Mit IP-Adresse:

```powershell
scp pi@192.168.178.84:/home/pi/test.jpg .
```

Nach der Passworteingabe sollte `test.jpg` im aktuellen Windows-Ordner liegen.

Prüfen:

```powershell
Get-Item .\test.jpg
```

Bild öffnen:

```powershell
Start-Process .\test.jpg
```

## 8.8 Direkt in einen festen Windows-Ordner kopieren

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg "D:\Kamera\Bilder\"
```

Bei Leerzeichen im Zielpfad sind Anführungszeichen erforderlich:

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg "D:\Eigene Projekte\Vision-System\Bilder\"
```

## 8.9 Bild unter einem neuen Namen speichern

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg "D:\Kamera\Bilder\aufnahme_01.jpg"
```

Das Original auf dem Raspberry Pi bleibt unverändert.

## 8.10 Mehrere Bilder übertragen

Alle JPEG-Dateien:

```powershell
scp pi@raspi-zero-xx:/home/pi/*.jpg "D:\Kamera\Bilder\"
```

Einen vollständigen Ordner rekursiv kopieren:

```powershell
scp -r pi@raspi-zero-xx:/home/pi/bilder "D:\Kamera\"
```

`-r` bedeutet **rekursiv**: Unterordner und deren Dateien werden mitkopiert.

## 8.11 Praktischer Arbeitsablauf

### Schritt A – Aufnahme per SSH auslösen

Der Windows-PC kann den Aufnahmebefehl direkt auf dem Raspberry Pi ausführen:

```powershell
ssh pi@raspi-zero-xx "rpicam-still --nopreview --width 1296 --height 972 -o /home/pi/test.jpg"
```

### Schritt B – Bild abholen

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg "D:\Kamera\Bilder\"
```

### Schritt C – Bild öffnen

```powershell
Start-Process "D:\Kamera\Bilder\test.jpg"
```

Damit kann die komplette Bedienung vom Windows-PC aus erfolgen.

## 8.12 PowerShell-Skript für Aufnahme und Übertragung

Datei: `python/beispiele/bild_holen.ps1`

```powershell
$PiHost = "raspi-zero-xx"
$PiUser = "pi"
$Breite = 1296
$Hoehe = 972
$RemoteDatei = "/home/pi/test.jpg"
$ZielOrdner = "D:\Kamera\Bilder"
$ZielDatei = Join-Path $ZielOrdner "test.jpg"

New-Item -ItemType Directory -Force -Path $ZielOrdner | Out-Null

ssh "${PiUser}@${PiHost}" "rpicam-still --nopreview --width $Breite --height $Hoehe -o $RemoteDatei"
if ($LASTEXITCODE -ne 0) {
    throw "Die Bildaufnahme auf dem Raspberry Pi ist fehlgeschlagen."
}

scp "${PiUser}@${PiHost}:${RemoteDatei}" "$ZielDatei"
if ($LASTEXITCODE -ne 0) {
    throw "Die Bildübertragung ist fehlgeschlagen."
}

Write-Host "Bild gespeichert: $ZielDatei"
Start-Process "$ZielDatei"
```

Ausführen:

```powershell
powershell -ExecutionPolicy Bypass -File .\bild_holen.ps1
```

## 8.13 Einstellbare Auflösung im PowerShell-Skript

Die Werte können am Anfang des Skripts geändert werden:

```powershell
$Breite = 640
$Hoehe = 480
```

oder:

```powershell
$Breite = 1920
$Hoehe = 1080
```

Empfohlene Stufen:

| Name | Breite | Höhe | Einsatz |
|---|---:|---:|---|
| VGA | 640 | 480 | schnelle Tests |
| HD | 1280 | 720 | Vorschau und einfache Erkennung |
| 4:3-Mittel | 1296 | 972 | guter Sensormodus der OV5647 |
| Full HD | 1920 | 1080 | detailreiche Auswertung |
| Maximum | 2592 | 1944 | Einzelbilder mit maximaler Auflösung |

## 8.14 Passwortfreie Anmeldung mit SSH-Schlüssel

Für die ersten Tests ist die Passworteingabe sinnvoll und übersichtlich. Für eine spätere automatische Verarbeitung kann ein SSH-Schlüssel eingerichtet werden.

Auf Windows in PowerShell:

```powershell
ssh-keygen -t ed25519
```

Die vorgeschlagenen Speicherorte können mit der Eingabetaste bestätigt werden.

Da `ssh-copy-id` unter Windows nicht immer vorhanden ist, kann der öffentliche Schlüssel so übertragen werden:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh pi@raspi-zero-xx "mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys"
```

Danach testen:

```powershell
ssh pi@raspi-zero-xx
```

Wichtig: Der private Schlüssel im Windows-Benutzerprofil darf nicht weitergegeben werden.

## 8.15 Typische Fehler

### Hostname kann nicht aufgelöst werden

```text
Could not resolve hostname
```

Lösung:

- Schreibweise des Hostnamens prüfen.
- IP-Adresse statt Hostname verwenden.
- Auf dem Raspberry Pi `hostname` und `hostname -I` ausführen.

### Verbindung wird verweigert

```text
Connection refused
```

Lösung:

```bash
sudo systemctl status ssh
sudo systemctl enable --now ssh
```

### Anmeldung wird abgewiesen

```text
Permission denied
```

Lösung:

- Benutzername prüfen.
- Passwort prüfen.
- kontrollieren, ob der Benutzer tatsächlich `pi` heißt.

### Datei wurde nicht gefunden

```text
No such file or directory
```

Auf dem Raspberry Pi prüfen:

```bash
ls -lh /home/pi/test.jpg
```

### Windows kennt den Befehl `scp` nicht

In PowerShell prüfen:

```powershell
Get-Command scp
```

Falls der OpenSSH-Client fehlt, kann er in Windows unter **Optionale Features** installiert werden. In verwalteten Schulnetzen können dafür Administratorrechte erforderlich sein.

### Zielordner existiert nicht

```powershell
New-Item -ItemType Directory -Force -Path "D:\Kamera\Bilder"
```

## 8.16 Sicherheits- und Praxisempfehlungen

- Das Raspberry-Pi-Passwort nicht in Skripten speichern.
- Für Automatisierung SSH-Schlüssel verwenden.
- Zunächst nur im lokalen, vertrauenswürdigen Netz arbeiten.
- Für eine feste Installation dem Raspberry Pi nach Möglichkeit eine reservierte IP-Adresse im Router zuweisen.
- Dateinamen mit Zeitstempel verhindern unbeabsichtigtes Überschreiben.

Beispiel für einen Zeitstempel in PowerShell:

```powershell
$Zeit = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$ZielDatei = "D:\Kamera\Bilder\bild_$Zeit.jpg"
```

---

# Variante 2 – Raspberry Pi sendet das Bild per SCP

## 8.17 Prinzip

Der Raspberry Pi startet die Übertragung selbst:

```bash
scp /home/pi/test.jpg windowsbenutzer@windows-pc:/zielordner/
```

Dafür muss auf Windows ein SSH-Server laufen. Das ist auf privaten Rechnern möglich, in Schulnetzen jedoch eventuell nicht erlaubt.

### Vorteile

- Der Raspberry Pi kann direkt nach jeder Aufnahme senden.
- Der Windows-PC muss den Kopiervorgang nicht anstoßen.

### Nachteile

- OpenSSH-Server muss auf Windows installiert und gestartet werden.
- Firewall und Windows-Berechtigungen müssen passen.
- Der Windows-Zielpfad ist aus Linux-Sicht weniger intuitiv.

Diese Variante wird erst nach erfolgreichem Abschluss von Variante 1 praktisch eingerichtet.

---

# Variante 3 – Freigegebener Windows-Ordner

## 8.18 Prinzip

Ein Windows-Ordner, beispielsweise `D:\Kamera`, wird im Netzwerk freigegeben. Der Raspberry Pi bindet diese SMB-Freigabe ein und kann Bilder direkt dort speichern.

Beispiel auf dem Raspberry Pi:

```bash
sudo apt install cifs-utils
sudo mkdir -p /mnt/kamera
sudo mount -t cifs //WINDOWS-PC/Kamera /mnt/kamera -o username=WINDOWS_BENUTZER
cp /home/pi/test.jpg /mnt/kamera/
```

### Vorteile

- Für viele Bilder und Videos geeignet.
- Der Zielordner erscheint auf dem Raspberry Pi wie ein lokaler Ordner.
- Python kann direkt in die Freigabe schreiben.

### Nachteile

- Windows-Freigabe, Benutzerrechte und Firewall müssen eingerichtet werden.
- Zugangsdaten sollten nicht ungeschützt in `/etc/fstab` stehen.
- Bei unterbrochener Netzwerkverbindung muss die Anwendung Fehler behandeln.

Diese Variante ist eine mögliche Dauerlösung, sobald SCP zuverlässig funktioniert.

---

## 8.19 Vergleich

| Variante | Einrichtung | Automatisierung | Eignung für den ersten Test | Eignung als Dauerlösung |
|---|:---:|:---:|:---:|:---:|
| Windows holt per SCP | gering | gut | sehr gut | gut |
| Pi sendet per SCP | mittel | sehr gut | bedingt | gut |
| Windows-Freigabe | mittel | sehr gut | bedingt | sehr gut |

## 8.20 Empfohlene Reihenfolge

1. Testbild auf dem Raspberry Pi aufnehmen.
2. SSH-Verbindung von Windows prüfen.
3. Bild mit einem einzelnen SCP-Befehl abholen.
4. Aufnahme und Übertragung mit PowerShell automatisieren.
5. Passwortfreie Anmeldung mit SSH-Schlüssel einrichten.
6. Danach entscheiden, ob SCP genügt oder eine Windows-Freigabe sinnvoller ist.

## 8.21 Praktischer Kontrollbogen

- [ ] `test.jpg` wurde auf dem Raspberry Pi erzeugt.
- [ ] SSH-Anmeldung von Windows funktioniert.
- [ ] `scp` ist auf Windows verfügbar.
- [ ] Das Bild wurde in `D:\Kamera\Bilder` gespeichert.
- [ ] Das übertragene Bild lässt sich öffnen.
- [ ] Eine andere Auflösung wurde erfolgreich getestet.
- [ ] Das PowerShell-Skript funktioniert.
- [ ] Optional: SSH-Schlüssel wurde eingerichtet.

## 8.22 Nächster Schritt

Nach erfolgreicher Übertragung folgt das Python-Modul `bildtransfer.py`. Es soll Aufnahme und Bildabruf später mit einem verständlichen Funktionsaufruf kapseln.
