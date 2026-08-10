# Prompt 26 – Mountpunkt ist vorhanden

## Prompt

`/mnt/windows` existiert bereits.

## Antwort

Damit wurde der Mountpunkt als Fehlerursache ausgeschlossen. Als nächster Schritt wurde empfohlen:

```bash
smbclient -L //192.168.2.106 -U l5889
```

Außerdem sollte der exakte Windows-Freigabename geprüft werden.
