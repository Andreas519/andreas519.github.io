🔴 `Variante 3 – Gemeinsame Netzwerkfreigabe` → **Variante 3 – Gemeinsame Netzwerkfreigabe** ✅

Ich halte diese Variante **langfristig für die eleganteste Lösung**. Vor allem, wenn später viele Bilder aufgenommen werden oder OpenCV direkt auf dem Windows-PC arbeitet.

---

# Grundidee

Der Windows-PC stellt einen Ordner im Netzwerk bereit.

Zum Beispiel:

```text
D:\Vision-System\bilder
```

Der Raspberry Pi bindet diesen Ordner als Laufwerk ein.

Dann genügt später:

```bash
cp test.jpg /mnt/windows/
```

oder direkt aus Python:

```python
shutil.copy("test.jpg", "/mnt/windows/")
```

Der Windows-PC erhält das Bild sofort – ganz ohne `scp`.

---

# Schritt 1 – Windows-Ordner anlegen

Ich würde gleich eine saubere Projektstruktur wählen.

```text
D:\
└── Vision-System
    ├── bilder
    ├── videos
    ├── opencv
    ├── python
    └── dokumentation
```

Freigegeben wird später nur

```text
D:\Vision-System
```

---

# Schritt 2 – Ordner freigeben

Unter Windows:

Rechtsklick

```
Eigenschaften
```

↓

```
Freigabe
```

↓

```
Erweiterte Freigabe
```

↓

✔ Diesen Ordner freigeben

Freigabename

```
Vision-System
```

---

# Schritt 3 – Berechtigungen

Zum Testen:

```
Jeder
```

Lesen

und

Schreiben

Später kann man das wieder einschränken.

---

# Schritt 4 – Windows-IP feststellen

PowerShell

```powershell
ipconfig
```

Beispiel

```
IPv4-Adresse

192.168.2.100
```

---

# Schritt 5 – Raspberry vorbereiten

Benötigte Software installieren

```bash
sudo apt update

sudo apt install cifs-utils
```

---

# Schritt 6 – Einhängepunkt erzeugen

```bash
sudo mkdir /mnt/windows
```

---

# Schritt 7 – Netzwerkfreigabe verbinden

Angenommen

Windows

```
192.168.2.100
```

Freigabe

```
Vision-System
```

Benutzer

```
Andreas
```

Dann

```bash
sudo mount -t cifs \
   //192.168.2.100/Vision-System \
   /mnt/windows \
   -o username=Andreas
```

Windows fragt anschließend nach dem Kennwort.

---

# Schritt 8 – Test

```bash
ls /mnt/windows
```

Jetzt solltest du

```
bilder

videos

python
```

sehen.

---

# Schritt 9 – Bild kopieren

```bash
cp test.jpg /mnt/windows/bilder/
```

Fertig.

Auf dem Windows-PC erscheint sofort

```
D:\Vision-System\bilder\test.jpg
```

---

# Noch eleganter

Das Kameraprogramm speichert gleich dort.

```python
bild = "/mnt/windows/bilder/test.jpg"
```

Dann entfällt sogar das Kopieren.

---

# Python

```python
import shutil

shutil.copy(
    "test.jpg",
    "/mnt/windows/bilder/"
)
```

oder

```python
bild = "/mnt/windows/bilder/test.jpg"

kamera.foto(bild)
```

---

# Vorteile

```
Raspberry Pi

nimmt Bild auf

↓

speichert direkt

↓

Windows-Ordner

↓

OpenCV

↓

Dobot
```

Es gibt keinen zusätzlichen Kopiervorgang mehr.

---

# Ein weiterer Vorteil

Später könnte auch der Dobot dort seine Dateien ablegen.

Oder OpenCV.

Oder der ESP32.

Alle Programme greifen auf denselben Projektordner zu.

---

# Meine Empfehlung

Für die **erste Projektphase** würde ich bei **SCP** bleiben. Es ist schnell eingerichtet und wir wissen jetzt, dass es zuverlässig funktioniert.

Für die **zweite Projektphase** würde ich diese Netzwerkfreigabe einrichten. Dann können wir die Python-Programme so entwickeln, dass sie Bilder direkt im Projektordner `D:\Vision-System\bilder` speichern oder lesen.

## Ich habe noch eine Idee 💡

Da wir bereits das Projekt **Vision-System** aufgebaut haben, würde ich den gemeinsamen Ordner nicht einfach `bilder` nennen, sondern die komplette Projektstruktur auf dem Windows-PC spiegeln:

```text
D:\Vision-System
│
├── bilder
├── videos
├── python
├── dokumentation
├── opencv
└── ki
```

Auf dem Raspberry Pi würden wir genau **diesen Projektordner** unter `/mnt/vision-system` einhängen:

```bash
sudo mkdir /mnt/vision-system
```

Dadurch arbeiten Windows und Raspberry Pi später praktisch im selben Projekt. Bilder, Python-Programme und Dokumentationen liegen immer an derselben Stelle und müssen nicht mehr zwischen verschiedenen Ordnern synchronisiert werden. Ich halte das für die sauberste und langfristig wartungsärmste Lösung. 🚀
