# Prompt 25 – `mount error(2)`

## Prompt

Das Mounten von `//192.168.2.106/cam-bilder` schlägt fehl.

## Antwort

Als mögliche Ursachen wurden genannt:

- falscher Freigabename
- Mountpunkt fehlt
- Freigabe existiert nicht

Prüfbefehle:

```bash
ls -ld /mnt/windows
smbclient -L //192.168.2.106 -U l5889
sudo dmesg | tail -20
```
