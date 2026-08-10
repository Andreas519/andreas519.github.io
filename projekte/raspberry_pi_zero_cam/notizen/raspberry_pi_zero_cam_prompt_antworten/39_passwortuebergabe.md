# Prompt 39 – Wo wird das Passwort übergeben?

## Prompt

Wo ist die Übergabe des Passworts zu sehen?

## Antwort

Im Python-Code wird kein Passwort übergeben. `scp.exe` fragt es interaktiv im Terminal ab:

```text
pi@192.168.2.128's password:
```

Für automatische Abläufe wurde SSH-Schlüsselauthentifizierung empfohlen:

```powershell
ssh-keygen
```

Öffentlichen Schlüssel übertragen:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh pi@192.168.2.128 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```
