# Prompt 27 – SMB-Freigaben wurden gefunden

## Prompt

`smbclient` zeigt die Freigabe:

```text
cam_bilder
```

## Antwort

Der Fehler wurde gefunden:

Falsch:

```text
cam-bilder
```

Richtig:

```text
cam_bilder
```

Der korrigierte Mount-Befehl:

```bash
sudo mount -t cifs   //192.168.2.106/cam_bilder   /mnt/windows   -o username=l5889
```
