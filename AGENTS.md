# AGENTS.md

Diese Hinweise helfen Coding-Agents (inkl. Codex) bei schneller, konsistenter Arbeit in diesem Repository.

## Projektkontext

- Statische GitHub-Pages-Website mit HTML, CSS und JavaScript.
- Inhalte sind didaktische Technik-/Informatik-Projekte (Young Engineers).
- Es gibt keinen Build-Prozess, kein Framework und keine Paketverwaltung im Root.

Siehe Kontext in [README.md](README.md) und Projektliste in [projekte/README.md](projekte/README.md).

## Wichtige Struktur

- Startseiten: [index.html](index.html), [projekte/index.html](projekte/index.html), [themen/index.html](themen/index.html)
- Globales Styling: [css/my.css](css/my.css)
- Gemeinsame JS-Helfer: [js/script.js](js/script.js)
- Hilfsskripte: [tmp_check_links.py](tmp_check_links.py), [remove_bg_esp32.py](remove_bg_esp32.py)

## Arbeitsweise für Änderungen

- Bevorzuge kleine, lokale Änderungen in bestehenden Dateien statt großem Umbau.
- Behalte bestehende Sprache und Tonalität (Deutsch) bei.
- Nutze bestehende CSS-Klassen und Variablen in [css/my.css](css/my.css), statt neue Stilwelten einzuführen.
- Dedupliziere JS: wiederverwendbare Logik gehört in [js/script.js](js/script.js), nicht als Kopie in viele HTML-Dateien.

## HTML-Konventionen

- Seiten bleiben einfache, statische HTML-Dateien mit relativen Pfaden.
- Achte auf korrekte Tiefe bei Pfaden zu CSS/JS/Bildern (z. B. ../ vs. ../../).
- Übliche Meta-Basis beibehalten: charset, viewport, author/publisher/project (siehe [index.html](index.html)).
- Footer-Muster mit lastModified-Anzeige möglichst konsistent halten.

## Markdown- und Code-Darstellung

- Markdown-Inhalte werden teils dynamisch geladen (siehe Funktionen in [js/script.js](js/script.js)).
- Prism/Codeblöcke werden zentral behandelt; Änderungen dort auf bestehende Selektoren und Klassen abstimmen.
- Bestehende Dokumentation verlinken statt Inhalte zu kopieren, z. B. [projekte/74HC595/schieberegister.md](projekte/74HC595/schieberegister.md) oder [projekte/28BYJY-48/inhalt.md](projekte/28BYJY-48/inhalt.md).

## Lokales Prüfen

- Da statische Seite: lokal per einfachem HTTP-Server testen (vom Repo-Root), z. B. Python http.server.
- Links nach Änderungen prüfen mit [tmp_check_links.py](tmp_check_links.py).
- Nach Pfadänderungen immer betroffene Unterseiten manuell öffnen und Navigation testen.

## Python-Hilfsskripte

- [tmp_check_links.py](tmp_check_links.py): validiert relative Links in HTML-Dateien.
- [remove_bg_esp32.py](remove_bg_esp32.py): Bildbearbeitung via Pillow; nur für Assets, nicht für Web-Logik.
- Bei Dateischreibzugriffen Encoding bewusst behandeln (historisch gemischte Dateien möglich).

## Was Agents vermeiden sollen

- Keine Einführung neuer Toolchains (Bundler, Frameworks, Node-Pflicht), wenn nicht explizit gewünscht.
- Keine großflächigen Umformatierungen ohne funktionalen Nutzen.
- Keine stillen Pfadänderungen an vielen Dateien ohne anschließende Link-Prüfung.

## Wenn unklar

- Erst kurz die Zielseite und ihre Nachbarseiten lesen.
- Dann minimalen Patch umsetzen.
- Danach Links/Funktionen prüfen und nur relevante Folgeanpassungen vornehmen.
