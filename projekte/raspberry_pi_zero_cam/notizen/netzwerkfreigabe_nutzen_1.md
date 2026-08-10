🔴 Kann ich unter Python auf dem Pi auch das ~~Mounten~~ **Einbinden** der Windows-Freigabe mit erledigen?

Ja. Python kann den Linux-Befehl `mount` über `subprocess` ausführen. Dabei gibt es aber einen wichtigen Punkt: Das Einbinden benötigt normalerweise **Root-Rechte**.

## Einfache Python-Variante

```python
import subprocess
from pathlib import Path


FREIGABE = "//192.168.2.106/cam_bilder"
MOUNT_PUNKT = Path("/mnt/windows")
WINDOWS_BENUTZER = "l5889"


def ist_eingebunden(mount_punkt: Path) -> bool:
    """Prüft, ob der Mount-Punkt bereits eingebunden ist."""
    return mount_punkt.is_mount()


def windows_freigabe_mounten() -> bool:
    """Bindet die Windows-Freigabe ein."""

    MOUNT_PUNKT.mkdir(parents=True, exist_ok=True)

    if ist_eingebunden(MOUNT_PUNKT):
        print("Die Windows-Freigabe ist bereits eingebunden.")
        return True

    befehl = [
        "sudo",
        "mount",
        "-t",
        "cifs",
        FREIGABE,
        str(MOUNT_PUNKT),
        "-o",
        f"username={WINDOWS_BENUTZER},uid=pi,gid=pi,rw,vers=3.0",
    ]

    try:
        subprocess.run(befehl, check=True)
        print("Die Windows-Freigabe wurde erfolgreich eingebunden.")
        return True

    except subprocess.CalledProcessError as fehler:
        print("Die Windows-Freigabe konnte nicht eingebunden werden.")
        print(f"Fehlercode: {fehler.returncode}")
        return False


if __name__ == "__main__":
    windows_freigabe_mounten()
```

Beim Start fragt `sudo` nach dem Linux-Passwort und `mount.cifs` anschließend nach dem Windows-Passwort.

Das funktioniert interaktiv, ist für ein automatisch gestartetes Kameraprogramm aber nicht ideal.

---

# Besser: Zugangsdaten in einer geschützten Datei

## 1. Datei anlegen

Auf dem Raspberry Pi:

```bash
sudo nano /etc/samba/cam-bilder.credentials
```

Inhalt:

```text
username=l5889
password=DEIN_WINDOWS_PASSWORT
```

Falls der Windows-PC eine Domäne oder Arbeitsgruppe benötigt:

```text
domain=WORKGROUP
```

## 2. Datei schützen

```bash
sudo chmod 600 /etc/samba/cam-bilder.credentials
```

Damit darf nur `root` die Datei lesen.

**Das Passwort sollte niemals direkt im Python-Programm stehen.**

## 3. Mount-Befehl testen

```bash
sudo mount -t cifs \
  //192.168.2.106/cam_bilder \
  /mnt/windows \
  -o credentials=/etc/samba/cam-bilder.credentials,uid=pi,gid=pi,rw,vers=3.0,file_mode=0664,dir_mode=0775
```

---

# Python-Programm mit Zugangsdaten-Datei

```python
import shutil
import subprocess
from pathlib import Path


FREIGABE = "//192.168.2.106/cam_bilder"
MOUNT_PUNKT = Path("/mnt/windows")
ZUGANGSDATEN = "/etc/samba/cam-bilder.credentials"


def ist_eingebunden() -> bool:
    return MOUNT_PUNKT.is_mount()


def freigabe_mounten() -> bool:
    MOUNT_PUNKT.mkdir(parents=True, exist_ok=True)

    if ist_eingebunden():
        print("Windows-Freigabe ist bereits eingebunden.")
        return True

    optionen = (
        f"credentials={ZUGANGSDATEN},"
        "uid=pi,gid=pi,"
        "rw,vers=3.0,"
        "file_mode=0664,dir_mode=0775"
    )

    befehl = [
        "sudo",
        "mount",
        "-t",
        "cifs",
        FREIGABE,
        str(MOUNT_PUNKT),
        "-o",
        optionen,
    ]

    try:
        subprocess.run(
            befehl,
            check=True,
            capture_output=True,
            text=True,
        )

        print("Windows-Freigabe erfolgreich eingebunden.")
        return True

    except subprocess.CalledProcessError as fehler:
        print("Fehler beim Einbinden der Windows-Freigabe.")

        if fehler.stderr:
            print(fehler.stderr.strip())

        return False


def bild_kopieren(
    quelldatei: str = "test.jpg",
    unterordner: str = "bilder",
) -> bool:
    if not freigabe_mounten():
        return False

    quelle = Path(quelldatei)

    if not quelle.is_file():
        print(f"Die Bilddatei wurde nicht gefunden: {quelle}")
        return False

    zielordner = MOUNT_PUNKT / unterordner
    zielordner.mkdir(parents=True, exist_ok=True)

    ziel = zielordner / quelle.name

    try:
        shutil.copy2(quelle, ziel)
        print(f"Bild erfolgreich kopiert: {ziel}")
        return True

    except OSError as fehler:
        print(f"Fehler beim Kopieren: {fehler}")
        return False


if __name__ == "__main__":
    bild_kopieren("test.jpg")
```

Der Ablauf ist dann:

```text
Programm starten
      ↓
Ist /mnt/windows bereits eingebunden?
      ↓
Nein → Freigabe einbinden
      ↓
Unterordner bilder prüfen/anlegen
      ↓
test.jpg kopieren
```

---

# Das Problem mit `sudo`

Ein normales Python-Programm kann `sudo mount` nur ausführen, wenn das Passwort interaktiv eingegeben wird oder eine gezielte `sudo`-Regel eingerichtet wurde.

Eine pauschale Freigabe wie

```text
pi ALL=(ALL) NOPASSWD: ALL
```

wäre **zu unsicher** und sollte nicht verwendet werden.

Für ein automatisches Programm ist es besser, nur das Einbinden genau dieser Freigabe zu erlauben. Noch sauberer ist jedoch die folgende Lösung.

# Meine Empfehlung: Mounten vom Betriebssystem erledigen lassen

Das Kameraprogramm sollte sich möglichst nicht selbst um Administratoraufgaben kümmern. Besser ist:

1. Linux bindet die Freigabe beim Zugriff automatisch ein.
2. Python prüft nur, ob `/mnt/windows` verfügbar ist.
3. Python speichert oder kopiert anschließend das Bild.

Dafür kann ein Eintrag in `/etc/fstab` verwendet werden:

```fstab
//192.168.2.106/cam_bilder /mnt/windows cifs credentials=/etc/samba/cam-bilder.credentials,uid=pi,gid=pi,rw,vers=3.0,file_mode=0664,dir_mode=0775,_netdev,nofail,x-systemd.automount 0 0
```

Danach:

```bash
sudo systemctl daemon-reload
sudo mount -a
```

Prüfen:

```bash
mount | grep /mnt/windows
```

Mit

```text
x-systemd.automount
```

wird die Freigabe bei Bedarf eingebunden, sobald ein Programm auf `/mnt/windows` zugreift. Mit

```text
nofail
```

startet der Raspberry Pi auch dann weiter, wenn der Windows-PC ausgeschaltet ist.

## Python wird dadurch sehr einfach

```python
import shutil
from pathlib import Path


quelle = Path("/home/pi/test.jpg")
zielordner = Path("/mnt/windows/bilder")
zielordner.mkdir(parents=True, exist_ok=True)

shutil.copy2(quelle, zielordner / quelle.name)

print("Bild wurde auf den Windows-PC übertragen.")
```

**Für das Vision-System empfehle ich daher:**

* Das Betriebssystem übernimmt das Mounten über `/etc/fstab`.
* `kamera.py` nimmt das Bild auf.
* `bildtransfer.py` prüft die Freigabe und kopiert das Bild.
* Bei nicht erreichbarem Windows-PC wird das Bild zunächst lokal gespeichert.

Das trennt Systemverwaltung und Kameraprogramm sauber voneinander. 🔧📷
