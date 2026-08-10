# Prompt 04 – Raspberry-Pi-Konfiguration

## Prompt

Sorry, ich meine „setup“.

## Antwort

Das zentrale Konfigurationsprogramm des Raspberry Pi wird so gestartet:

```bash
sudo raspi-config
```

Dort lassen sich unter anderem einstellen:

- WLAN
- SSH
- Sprache
- Zeitzone
- Tastatur
- Bootoptionen

Die installierte Betriebssystemversion kann mit folgenden Befehlen geprüft werden:

```bash
uname -a
cat /etc/os-release
```
