# Prompt 37 – SCP unter Windows aus Python aufrufen

## Prompt

SCP soll unter Windows aus Python gestartet werden.

## Antwort

Beispiel:

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
```

Prüfen, ob SCP vorhanden ist:

```powershell
where.exe scp
```

Es wurde außerdem ein Modul `bildtransfer.py` mit Fehlerbehandlung vorgeschlagen.
