# Prompt 13 – Ist SCP ähnlich wie FTP?

## Prompt

Ist SCP so etwas wie FTP?

## Antwort

Ja, beide übertragen Dateien. SCP nutzt jedoch SSH und ist verschlüsselt.

| Merkmal | FTP | SCP |
|---|---|---|
| Dateiübertragung | ja | ja |
| Verschlüsselung | meist nein | ja |
| SSH-basiert | nein | ja |
| Raspberry-Pi-Empfehlung | eher nicht | sehr gut |

Beispiel:

```powershell
scp pi@raspi-zero-xx:/home/pi/test.jpg D:\Kamera\
```

Außerdem wurde SFTP als grafisch nutzbare Alternative erwähnt.
