# Prompt 28 – Schreibzugriff verweigert

## Prompt

```text
-bash: /mnt/windows/test.txt: Permission denied
```

## Antwort

Es wurde zwischen Linux- und Windows-Berechtigungen unterschieden.

Prüfen:

```bash
mount | grep /mnt/windows
```

Direkter SMB-Test:

```bash
echo "Hallo vom Raspberry Pi" > /tmp/test.txt
smbclient //192.168.2.106/cam_bilder -U l5889
```

Danach in `smbclient`:

```text
put /tmp/test.txt
```

Auf Windows mussten sowohl Freigabeberechtigungen als auch NTFS-Sicherheitsrechte geprüft werden.
