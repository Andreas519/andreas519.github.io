# Prompt 38 – Datei auf dem Pi nach SCP löschen

## Prompt

Kann die Datei nach der Übertragung auf dem Pi gelöscht werden?

## Antwort

`scp` löscht die Quelle nicht. Nach erfolgreichem Kopieren kann `ssh rm` ausgeführt werden:

```python
import subprocess

subprocess.run(
    [
        r"C:\Windows\System32\OpenSSH\scp.exe",
        "pi@192.168.2.128:/home/pi/test.jpg",
        r"D:\Downloads",
    ],
    check=True,
)

subprocess.run(
    [
        r"C:\Windows\System32\OpenSSH\ssh.exe",
        "pi@192.168.2.128",
        "rm",
        "--",
        "/home/pi/test.jpg",
    ],
    check=True,
)
```

Es wurde empfohlen, vor dem Löschen die erfolgreich kopierte Windows-Datei zu prüfen.
