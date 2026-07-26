# Markdown Hilfen

## Wie zeichne ich hier Programcode aus?

Programmcode kannst du hier mit Backticks auszeichnen.
Für kurzen Code innerhalb eines Satzes verwendest du jeweils einen Backtick:
Der Befehl `led.off()` schaltet die LED aus.
Das erscheint als: Der Befehl led.off() schaltet die LED aus.
Für mehrere Codezeilen verwendest du drei Backticks vor und nach dem Code. Hinter den ersten Backticks kannst du die Programmiersprache angeben:
```python
if befehl == "Q":
    zeile_senden("PROGRAMM_BEENDET")
    raise KeyboardInterrupt
```
Das wird so dargestellt:
if befehl == "Q":
    zeile_senden("PROGRAMM_BEENDET")
    raise KeyboardInterrupt
Für die Thonny-Ausgabe kannst du text verwenden:
```text
ESP32_BEREIT
WERT;LED_gelb;0
```
Wichtig: Die abschließenden drei Backticks müssen in einer eigenen Zeile stehen.


## Wie kopiere ich ..
Am zuverlässigsten geht es so:
Markiere den gewünschten Text im Chat mit der Maus.
Kopiere ihn mit Strg+C.
Füge ihn mit Strg+V in einen Markdown-Editor ein.
Bei normalen Antworten wird dabei allerdings möglicherweise nur der dargestellte Text kopiert, nicht immer die zugrunde liegenden Markdown-Zeichen.
Für unverändertes Markdown kannst du mich bitten:
Gib deine vorherige Antwort als Markdown-Quelltext in einem Codeblock aus.

Ich liefere sie dann beispielsweise so:
## Überschrift

Der Befehl `led.off()` schaltet die LED aus.

```python
if befehl == "Q":
    raise KeyboardInterrupt
```