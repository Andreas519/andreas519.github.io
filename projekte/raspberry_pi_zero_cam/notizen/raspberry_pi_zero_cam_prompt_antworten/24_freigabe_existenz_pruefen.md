# Prompt 24 – Existiert eine Windows-Freigabe?

## Prompt

Wie kann der Raspberry Pi feststellen, ob eine Windows-Freigabe existiert?

## Antwort

Empfohlen wurde `smbclient`:

```bash
sudo apt install smbclient
smbclient -L //192.168.2.100 -U Andreas
```

Weitere Möglichkeiten:

```bash
ping WINDOWS-IP
nmap WINDOWS-IP
sudo mount -t cifs ...
df -h
mount
```

`SMB`-Port 445 zeigt, dass der Windows-Dateidienst erreichbar ist.
