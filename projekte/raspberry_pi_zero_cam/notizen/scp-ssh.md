**Wo ist die Übergabe des Passworts zu sehen?**

In dem Beispiel **nirgends**. Das Passwort wird nicht im Python-Code übergeben.

Bei diesem Aufruf:

```python
subprocess.run(
    [
        SCP,
        f"{pi_benutzer}@{pi_adresse}:{pi_datei}",
        windows_ziel,
    ],
    check=True,
)
```

startet Python nur `scp.exe`. Danach fragt `scp` selbst im Terminal nach dem Passwort:

```text
pi@192.168.2.128's password:
```

Du gibst es dann manuell ein.

## Warum nicht direkt im Code?

`scp` besitzt bewusst keinen einfachen Parameter wie:

```text
--password geheim
```

Das wäre unsicher, weil das Passwort dann

* im Quelltext steht,
* möglicherweise im Prozessspeicher sichtbar ist,
* leicht versehentlich auf GitHub landet.

## Für automatische Übertragung: SSH-Schlüssel

Die saubere Lösung ist eine Anmeldung ohne Passwortabfrage über einen SSH-Schlüssel.

Unter Windows in PowerShell:

```powershell
ssh-keygen
```

Meist kannst du die Vorgaben mit Enter übernehmen.

Hier ein Beispieldialog:

```powershell
ssh-keygen
Generating public/private ed25519 key pair.
Enter file in which to save the key (C:\Users\nutzer/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in C:\Users\nutzer/.ssh/id_ed25519
Your public key has been saved in C:\Users\nutzer/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:2boSA+l8WGgYYwWoTY5XNJ3IpW9ZDFxxpCUFju1oQQk l5889@DESKTOP-96CQUB0
The key's randomart image is:
+--[ED25519 256]--+
| ..=E*++===      |
|. = ++=* =       |
|.* =.oo *        |
|o = =..* o       |
| . + +* S .      |
|    +o+  .       |
|     . o.        |
|      .  .       |
|       ..        |
+----[SHA256]-----+
```
Danach den öffentlichen Schlüssel auf den Pi übertragen:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh pi@192.168.2.128 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Dabei musst du das Pi-Passwort noch einmal eingeben.

Danach testen:

```powershell
ssh pi@192.168.2.128
```

Wenn keine Passwortabfrage mehr kommt, funktionieren auch `scp` und dein Python-Programm automatisch:

```python
subprocess.run(
    [
        SCP,
        "pi@192.168.2.128:/home/pi/test.jpg",
        r"D:\Downloads",
    ],
    check=True,
)
```

Das Passwort wird dann nicht mehr übergeben, weil der SSH-Schlüssel die Anmeldung übernimmt. 🔐
