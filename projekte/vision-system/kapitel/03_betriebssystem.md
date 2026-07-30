# 3. Betriebssystem

## Auswahl und Installation

Empfohlen wird Raspberry Pi OS mit Desktop, damit sowohl Terminalarbeit als auch grafische Werkzeuge zur Verfügung stehen. Die Installation erfolgt mit dem Raspberry Pi Imager auf einer MicroSD-Karte.

Im Imager sollten vor dem Schreiben der Karte eingerichtet werden:

- Hostname, zum Beispiel `raspi-zero-xx`
- Benutzername und Passwort
- WLAN-Zugang
- Zeitzone und Tastaturlayout
- SSH-Zugriff

## Installierte Version prüfen

```bash
cat /etc/os-release
```

Im praktisch getesteten System wurde ausgegeben:

```text
PRETTY_NAME="Raspbian GNU/Linux 13 (trixie)"
VERSION_ID="13"
VERSION_CODENAME=trixie
```

## System aktualisieren

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
```

Danach bei Bedarf neu starten:

```bash
sudo reboot
```

## Raspberry Pi konfigurieren

```bash
sudo raspi-config
```

Dort können unter anderem Sprache, Zeitzone, Netzwerk, SSH und Bootverhalten kontrolliert werden.
