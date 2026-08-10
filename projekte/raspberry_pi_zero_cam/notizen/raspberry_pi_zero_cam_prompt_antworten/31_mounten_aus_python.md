# Prompt 31 – Windows-Freigabe mit Python mounten

## Prompt

Kann das Mounten auch aus Python erledigt werden?

## Antwort

Ja, mit `subprocess`:

```python
import subprocess

subprocess.run(
    [
        "sudo",
        "mount",
        "-t",
        "cifs",
        "//192.168.2.106/cam_bilder",
        "/mnt/windows",
        "-o",
        "username=l5889,uid=pi,gid=pi,rw,vers=3.0",
    ],
    check=True,
)
```

Empfohlen wurde jedoch eine geschützte Zugangsdaten-Datei:

```text
/etc/samba/cam-bilder.credentials
```

und langfristig ein automatisches Mounten über `/etc/fstab`:

```fstab
//192.168.2.106/cam_bilder /mnt/windows cifs credentials=/etc/samba/cam-bilder.credentials,uid=pi,gid=pi,rw,vers=3.0,file_mode=0664,dir_mode=0775,_netdev,nofail,x-systemd.automount 0 0
```
