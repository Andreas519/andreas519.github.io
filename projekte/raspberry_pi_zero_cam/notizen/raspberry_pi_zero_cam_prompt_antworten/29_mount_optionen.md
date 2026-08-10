# Prompt 29 – Mount ist `rw`, aber `uid=0`

## Prompt

Die Ausgabe zeigt:

```text
rw
uid=0
gid=0
```

## Antwort

`rw` bedeutet grundsätzlich Lesen und Schreiben. `uid=0` und `gid=0` zeigen jedoch, dass die Freigabe unter Linux `root` zugeordnet ist.

Test:

```bash
sudo touch /mnt/windows/test.txt
```

Empfohlener neuer Mount:

```bash
sudo umount /mnt/windows

sudo mount -t cifs   //192.168.2.106/cam_bilder   /mnt/windows   -o username=l5889,uid=pi,gid=pi,file_mode=0664,dir_mode=0775
```
