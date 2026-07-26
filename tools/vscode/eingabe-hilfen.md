# Hilfen zu Visual Studio Code

## Inhaltsverzeichnis

- [ **Visual Studio** vs. **Visual Studio Code (VS Code)](#vs-code)
- [Zwischen Vorschlägen wechseln](Tastaurkürzel)
- [Eigene Tastenkürzel festlegen](#eigene-tastenkürzel-festlegen)

<a id="vs_code"></a>
## **Visual Studio** vs. **Visual Studio Code (VS Code)** 
**Visual Studio** und **Visual Studio Code (VS Code)** sind zwei eigenständige Programme von Microsoft.

| Eigenschaft | Visual Studio | Visual Studio Code |
|---|---|---|
| Art | Vollständige Entwicklungsumgebung (IDE) | Leichter Code-Editor |
| Schwerpunkt | .NET, C#, C++, Windows-Anwendungen | Viele Sprachen und allgemeine Projektarbeit |
| Installation | Mehrere Gigabyte, auswählbare Workloads | Relativ klein und schnell installiert |
| Funktionen | Compiler, Debugger, Designer und Testwerkzeuge integriert | Viele Funktionen werden über Erweiterungen ergänzt |
| Betriebssysteme | Vor allem Windows; Visual Studio for Mac wurde eingestellt | Windows, Linux und macOS |
| Oberfläche | Umfangreich und projektspezifisch | Schlank und flexibel |
| Typische Projekte | C#/.NET, ASP.NET, C++, Desktop- und Unternehmenssoftware | Python, JavaScript, Webentwicklung, MicroPython, Konfigurationsdateien |
| Preis | Community kostenlos; Professional und Enterprise kostenpflichtig | Kostenlos |

Für dein ESP32-/MicroPython-Projekt wäre normalerweise **Visual Studio Code** geeigneter:

- Python- und MicroPython-Dateien lassen sich bequem bearbeiten.
- Die serielle Kommunikation kann über Erweiterungen oder ein Terminal erfolgen.
- Git ist gut integriert.
- VS Code benötigt deutlich weniger Ressourcen als Visual Studio.

**Thonny** bleibt für MicroPython besonders praktisch, weil das Übertragen und direkte Ausführen auf dem ESP32 schon eingebaut ist. Eine sinnvolle Kombination wäre daher:

- **VS Code** für umfangreiches Bearbeiten, Suchen und Versionsverwaltung
- **Thonny** für Übertragung, Ausführung und Tests auf dem ESP32
- **Visual Studio** nur, wenn du beispielsweise eine größere Windows- oder .NET-Anwendung entwickelst

Übrigens wird der Name als `Visual Studio Code` oder kurz `VS Code` geschrieben. Das Backtick-Zeichen zur Codeauszeichnung muss am Anfang und Ende gleich sein.


## Tastaturkürzel 

Auf einer deutschen Tastatur kollidieren `Alt` + `[` und `Alt` + `]` mit der Eingabe von eckigen Klammern über `AltGr`. Lege deshalb eigene Tastenkürzel fest:

1. Öffne mit `Strg` + `K`, danach `Strg` + `S` die **Tastenkombinationen**.
2. Suche nach `inline suggestion`.
3. Suche diese Befehle:
   - **Show Next Inline Suggestion** (`editor.action.inlineSuggest.showNext`)
   - **Show Previous Inline Suggestion** (`editor.action.inlineSuggest.showPrevious`)
4. Klicke auf das Stiftsymbol und vergebe beispielsweise:
   - Nächster Vorschlag: `Strg` + `Alt` + `N`
   - Vorheriger Vorschlag: `Strg` + `Alt` + `P`

Alternativ kannst du mit `Strg` + `Umschalt` + `P` die Befehlspalette öffnen und dort nach **Inline Suggestion** suchen. Das funktioniert unabhängig vom Tastaturlayout.