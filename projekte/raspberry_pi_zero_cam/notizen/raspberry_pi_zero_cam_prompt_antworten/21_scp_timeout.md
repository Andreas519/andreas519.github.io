# Prompt 21 – SCP-Verbindung läuft in Timeout

## Prompt

```text
ssh: connect to host raspi-zero-xx port 22: Connection timed out
```

## Antwort

`raspi-zero-xx` wurde als Platzhalter erkannt. Empfohlen wurde:

```bash
hostname
hostname -I
```

Danach unter Windows:

```powershell
ping IP-ADRESSE
ssh pi@IP-ADRESSE
scp pi@IP-ADRESSE:/home/pi/test.jpg D:\Downloads\
```
