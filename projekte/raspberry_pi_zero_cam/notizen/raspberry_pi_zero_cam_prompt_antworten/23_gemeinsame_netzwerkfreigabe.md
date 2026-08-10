# Prompt 23 – Variante 3: Gemeinsame Netzwerkfreigabe

## Prompt

Zeige ein Beispielvorgehen.

## Antwort

Vorgeschlagener Ablauf:

1. Windows-Ordner anlegen.
2. Ordner freigeben.
3. Freigabe- und NTFS-Berechtigungen setzen.
4. Windows-IP mit `ipconfig` feststellen.
5. Auf dem Pi `cifs-utils` installieren.
6. Mountpunkt anlegen:

```bash
sudo mkdir /mnt/windows
```

7. Freigabe einbinden:

```bash
sudo mount -t cifs   //WINDOWS-IP/FREIGABE   /mnt/windows   -o username=BENUTZER
```

8. Testen:

```bash
ls /mnt/windows
cp test.jpg /mnt/windows/
```
