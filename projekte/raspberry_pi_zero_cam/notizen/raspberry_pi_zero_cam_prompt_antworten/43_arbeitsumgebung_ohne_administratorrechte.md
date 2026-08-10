# Prompt 43 – Arbeitsumgebung ohne Administratorrechte

## Prompt
Wir verfügen in der Schule in der Regel nicht über Administratorrechte.
Wir nutzen das Verzeichnis `C:\Users\Public\Programme`,in dem wir unsere Programme hinterlegen.
## Antwort
Das ist eine wichtige Rahmenbedingung und sollte für alle Schulprojekte gelten:

> **Die Arbeitsumgebung muss ohne Administratorrechte funktionieren.**

## Konsequenzen für unser Vorgehen

### OpenSSH Server unter Windows entfällt

Die Installation des Windows-Dienstes **OpenSSH Server** benötigt Administratorrechte. Deshalb verwenden wir diesen Weg nicht.

Der Raspberry Pi muss den Windows-PC also nicht per SSH erreichen.

Stattdessen nutzen wir die bereits möglichen Richtungen:

```text
Windows-PC ── SSH/SCP ──► Raspberry Pi
Raspberry Pi ── Windows-Freigabe ──► Windows-PC
```

Damit benötigen wir auf Windows keinen zusätzlichen Server.

### Zugriff vom Windows-PC auf den Pi

Windows nutzt den vorhandenen SSH-Client:

```powershell
ssh pi@192.168.2.128
```

Für Dateien:

```powershell
scp pi@192.168.2.128:/home/pi/test.jpg C:\Users\Public\Bilder\
```

Nach eingerichteter Schlüsselanmeldung kann dies ohne Passwortabfrage erfolgen.

### Übertragung vom Pi zum PC

Der Raspberry Pi schreibt direkt in eine vorbereitete Windows-Freigabe:

```text
/mnt/windows
```

Beispiel:

```bash
rpicam-still --nopreview -o /mnt/windows/test.jpg
```

Auch hierfür ist kein Windows-SSH-Server erforderlich.

## Portable Programme

Der **Advanced IP Scanner** kann ohne Installation gestartet werden. Er kann bereitliegen:

```text
C:\Users\Public\Programme\Advanced-IP-Scanner\
```

oder auf:

* einem Netzlaufwerk,
* einem USB-Stick,
* einem gemeinsamen Schulordner.

Das passt gut zur schulischen Umgebung, weil keine Installation und keine Änderung am Windows-System notwendig sind.

## Gemeinsames Programmverzeichnis

Euer Ordner

```text
C:\Users\Public\Programme
```

ist dafür sehr geeignet:

* alle Benutzer können darauf zugreifen,
* ihr besitzt dort Schreibrechte,
* portable Programme können gemeinsam genutzt werden,
* Programme bleiben unabhängig vom jeweils angemeldeten Benutzer.

Eine mögliche Struktur wäre:

```text
C:\Users\Public\Programme\
├── Advanced-IP-Scanner\
├── Thonny\
├── Python\
├── VSCode\
├── Git\
└── Vision-System\
```

Für Projektdateien könnte ergänzend ein eigener gemeinsamer Ordner dienen:

```text
C:\Users\Public\Projekte\
└── raspberry_pi_zero_cam\
    ├── bilder\
    ├── python\
    └── dokumentation\
```

Damit ist unser einfacher Standardweg klar:

1. Pi und PC werden einmal vorbereitet.
2. Der Pi wird mit dem Advanced IP Scanner gefunden.
3. Windows greift per SSH oder SCP auf den Pi zu.
4. Der Pi schreibt bei Bedarf in eine Windows-Freigabe.
5. Alle benötigten Programme liegen portabel unter `C:\Users\Public\Programme`.

Das ist für die Schule deutlich brauchbarer als Lösungen, die Administratorrechte voraussetzen. 👍
