# Neuaufbau des Themenbereichs mBlock

Stand: 12. August 2026

## Ziel

Unter `themen/mblock/` soll schrittweise ein aktueller, verständlicher und praktisch geprüfter Themenbereich zu mBlock entstehen. Grundlage ist die Bestandsaufnahme der historisch gewachsenen Seiten unter <https://www.mrge.de/lehrer/sigismund/makeblock/> sowie der ausführliche Plan in [`../../docs/mblock-bestandsaufnahme-und-migrationsplan.md`](../../docs/mblock-bestandsaufnahme-und-migrationsplan.md).

## Abgrenzung

Der Ordner enthält derzeit noch keine migrierten Lerninhalte. Es wurden keine HTML-Seiten und keine Bilder, PDFs, Videos oder Programme aus dem alten Webbereich übernommen.

Für die spätere Arbeit gelten folgende Grenzen:

- Alte Inhalte sind zunächst nur Quellen und Arbeitsgrundlagen.
- Eine Anleitung gilt erst nach einem dokumentierten Praxistest als aktuell.
- Historische Materialien werden deutlich von aktuellen Lernwegen getrennt.
- Große Hersteller-PDFs, Dubletten und Fremdmaterialien mit ungeklärten Nutzungsrechten werden nicht in das Repository übernommen.
- Zusätzliche Detailseiten außerhalb der ersten Ausbaustufe werden erst später entschieden.

## Geplante Struktur der ersten Ausbaustufe

```text
themen/mblock/
├── index.html
├── einstieg.html
├── projekte-ohne-hardware.html
├── mbot/
│   ├── index.html
│   ├── verbinden-und-testen.html
│   ├── grundlagen-aufgaben.html
│   ├── datenlogger.html
│   ├── linienfolger.html
│   ├── ir-fernbedienung.html
│   └── joystick.html
├── arduino/
│   └── index.html
├── arduino-ide/
│   └── index.html
├── archiv.html
└── README.md
```

Die in der Struktur genannten HTML-Dateien sind geplant, aber noch nicht angelegt.

## Verbindliche Inhaltszustände

### Aktuell und praktisch geprüft

Eine Anleitung darf diesen Status nur erhalten, wenn sie mit dokumentierter Software-, Firmware- und Hardwareversion praktisch durchgeführt wurde. Prüfdatum, Testumgebung und bekannte Einschränkungen werden auf der Seite vermerkt.

### Noch ungeprüfter Arbeitsstand

Geeignete alte Aufgaben, Texte, Screenshots und Programme verbleiben in diesem Zustand, bis ein aktueller Praxistest abgeschlossen ist. Sie werden nicht als fertige Anleitung veröffentlicht.

### Historisch wertvoll

Materialien mit dokumentarischem Wert werden über `archiv.html` beschrieben und mit Jahr, Version, Quelle und bekannten Einschränkungen versehen. Eine Archivaufnahme bedeutet nicht, dass die ursprüngliche Datei lokal übernommen wird.

## Arbeitsphasen

1. **Entscheiden und abgrenzen:** Hardwareumfang, Rechte, fehlende Originale und externe Ersatzquellen klären.
2. **Praktisch prüfen:** mBlock, mLink, Verbindungsarten, Firmware, Cloudprojekte und Arduino-Beispiele mit festgehaltenen Versionen testen.
3. **Redaktionell planen:** Inhalte auf die festgelegten Sammel- und Lernseiten verteilen, Dubletten zusammenführen und ein einheitliches didaktisches Muster anwenden.
4. **Inhalte erstellen:** ausschließlich geprüfte Anleitungen neu formulieren; aktuelle Screenshots und eigene, zulässige Medien erzeugen.
5. **Qualität sichern:** lokale Navigation, Links, Barrierefreiheit, Downloads und praktische Durchführbarkeit prüfen.

## Prüfstatus

| Bereich | Status | Nächster Prüfschritt |
|---|---|---|
| Bestandsaufnahme der alten Website | abgeschlossen, Stichtag 12.08.2026 | vor einer Migration externe Links erneut prüfen |
| Zielstruktur der ersten Ausbaustufe | festgelegt | Seiten erst in einer später beauftragten Phase anlegen |
| mBlock-Einstieg und Veröffentlichung | ungeprüfter Arbeitsstand | aktuelle Oberfläche, Konto und Veröffentlichung praktisch testen |
| Projekte ohne Hardware | ungeprüfter Arbeitsstand | Cloudprojekte öffnen, kopieren, speichern und ausführen |
| mBot-Verbindung und Firmware | ungeprüfter Arbeitsstand | USB, Bluetooth und gegebenenfalls 2.4G praktisch testen |
| mBot-Aufgaben | ungeprüfter Arbeitsstand | jede Aufgabe mit aktueller Hardware und Software durchführen |
| Arduino mit mBlock | ungeprüfter Arbeitsstand | Verbindung, Firmware sowie Live-/Upload-Modus testen |
| Arduino IDE | ungeprüfter Arbeitsstand | Beispiele kompilieren und auf realer Hardware testen |
| Historisches Archiv | konzeptionell festgelegt | Metadaten, Quellen und Rechte prüfen; keine problematischen Dateien übernehmen |

Zum aktuellen Stand ist noch keine aus dem Altbestand abgeleitete Anleitung für die neue Website als „aktuell und praktisch geprüft“ freigegeben.
