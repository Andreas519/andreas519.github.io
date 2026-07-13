"""Live-Anzeige für das Containerlager auf der 40-x-27-Lochplatte.

Die grafische Oberfläche läuft im tkinter-Hauptthread. Roboterfunktionen
können aus einem Arbeitsthread gefahrlos Aktualisierungen über eine Queue
an die Anzeige senden.
"""

from __future__ import annotations

import queue
import tkinter as tk
from tkinter import messagebox
from typing import Any


VERSION = "1.0"


class LochplattenAnzeige:
    """Zeigt Lochplatte, Lagerplätze, Belegung und Roboterziel an."""

    PLATTENRAND = 44
    RASTER = 19
    LOCHRADIUS = 2.2

    FARBE_PLATTE = "#f4f1e8"
    FARBE_RAND = "#706f6a"
    FARBE_LOCH = "#555555"
    FARBE_FREI = ""
    FARBE_BELEGT = {
        1: "#cfe8cf",
        2: "#91c991",
        3: "#4f9d69",
    }
    FARBE_LAGERPLATZ = "#356a9a"
    FARBE_ZIEL = "#d62828"
    FARBE_ROBOTER = "#f28c28"

    def __init__(self, lager_modul: Any, titel: str = "Dobot-Containerlager") -> None:
        self.lager = lager_modul
        self._befehle: queue.Queue[tuple[str, tuple[Any, ...]]] = queue.Queue()
        self._geschlossen = False
        self._programm_laeuft = False
        self._ziel: tuple[int, int] | None = None
        self._zielname = ""
        self._roboterposition: tuple[int, int] | None = None
        self._status = "Anzeige bereit"

        self.root = tk.Tk()
        self.root.title(titel)
        self.root.protocol("WM_DELETE_WINDOW", self._fenster_schliessen)

        self._canvas_breite = (
            2 * self.PLATTENRAND
            + (self.lager.PLATTE_SPALTEN - 1) * self.RASTER
        )
        self._canvas_hoehe = (
            2 * self.PLATTENRAND
            + (self.lager.PLATTE_ZEILEN - 1) * self.RASTER
        )

        self._oberflaeche_erzeugen()
        self._statische_platte_zeichnen()
        self._dynamische_elemente_zeichnen()
        self._seitenleiste_aktualisieren()

    # ------------------------------------------------------------------
    # Öffentliche, thread-sichere Schnittstelle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Startet die Ereignisschleife der Anzeige."""

        self.root.after(40, self._befehle_verarbeiten)
        self.root.mainloop()

    def status_setzen(self, text: str, protokollieren: bool = True) -> None:
        self._befehl("status", str(text), bool(protokollieren))

    def ziel_setzen(
        self,
        spalte: int,
        zeile: int,
        name: str = "",
    ) -> None:
        self._befehl("ziel", int(spalte), int(zeile), str(name))

    def ziel_loeschen(self) -> None:
        self._befehl("ziel_loeschen")

    def roboterposition_setzen(self, spalte: int, zeile: int) -> None:
        self._befehl("roboterposition", int(spalte), int(zeile))

    def lager_aktualisieren(self) -> None:
        self._befehl("lager_aktualisieren")

    def fehler_anzeigen(self, text: str) -> None:
        self._befehl("fehler", str(text))

    def programm_laeuft_setzen(self, laeuft: bool) -> None:
        self._befehl("programm_laeuft", bool(laeuft))

    # ------------------------------------------------------------------
    # Oberfläche
    # ------------------------------------------------------------------

    def _oberflaeche_erzeugen(self) -> None:
        hauptbereich = tk.Frame(self.root, padx=8, pady=8)
        hauptbereich.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        hauptbereich.columnconfigure(0, weight=1)
        hauptbereich.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            hauptbereich,
            width=self._canvas_breite,
            height=self._canvas_hoehe,
            background="white",
            highlightthickness=1,
            highlightbackground="#b0b0b0",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        seite = tk.Frame(hauptbereich, width=300, padx=12)
        seite.grid(row=0, column=1, sticky="ns")
        seite.grid_propagate(False)

        tk.Label(
            seite,
            text="Containerlager",
            font=("TkDefaultFont", 15, "bold"),
        ).pack(anchor="w", pady=(2, 3))

        self.versions_label = tk.Label(
            seite,
            text=(
                f"Anzeige {VERSION} · "
                f"Lager {getattr(self.lager, 'VERSION', '?')}"
            ),
            foreground="#555555",
        )
        self.versions_label.pack(anchor="w", pady=(0, 12))

        tk.Label(seite, text="Status", font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w"
        )
        self.status_label = tk.Label(
            seite,
            text=self._status,
            justify="left",
            anchor="nw",
            wraplength=280,
            relief="groove",
            padx=7,
            pady=7,
            height=3,
        )
        self.status_label.pack(fill="x", pady=(3, 12))

        tk.Label(
            seite,
            text="Lagerplätze",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w")

        self.lager_text = tk.Text(
            seite,
            width=37,
            height=15,
            wrap="word",
            state="disabled",
        )
        self.lager_text.pack(fill="both", expand=False, pady=(3, 12))

        tk.Label(
            seite,
            text="Aktionsprotokoll",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w")

        self.protokoll_text = tk.Text(
            seite,
            width=37,
            height=12,
            wrap="word",
            state="disabled",
        )
        self.protokoll_text.pack(fill="both", expand=True, pady=(3, 10))

        self.schliessen_button = tk.Button(
            seite,
            text="Fenster schließen",
            command=self._fenster_schliessen,
        )
        self.schliessen_button.pack(fill="x")

        self._protokoll_hinzufuegen("Anzeige gestartet")

    def _statische_platte_zeichnen(self) -> None:
        self.canvas.delete("statisch")

        x1 = self._x(1) - self.RASTER * 0.55
        y1 = self._y(1) - self.RASTER * 0.55
        x2 = self._x(self.lager.PLATTE_SPALTEN) + self.RASTER * 0.55
        y2 = self._y(self.lager.PLATTE_ZEILEN) + self.RASTER * 0.55

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=self.FARBE_PLATTE,
            outline=self.FARBE_RAND,
            width=2,
            tags="statisch",
        )

        for spalte in range(1, self.lager.PLATTE_SPALTEN + 1):
            self.canvas.create_text(
                self._x(spalte),
                self._y(1) - 20,
                text=str(spalte),
                font=("TkDefaultFont", 7),
                tags="statisch",
            )

        for zeile in range(1, self.lager.PLATTE_ZEILEN + 1):
            self.canvas.create_text(
                self._x(1) - 22,
                self._y(zeile),
                text=str(zeile),
                font=("TkDefaultFont", 7),
                tags="statisch",
            )

        for zeile in range(1, self.lager.PLATTE_ZEILEN + 1):
            for spalte in range(1, self.lager.PLATTE_SPALTEN + 1):
                x = self._x(spalte)
                y = self._y(zeile)
                r = self.LOCHRADIUS
                self.canvas.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill=self.FARBE_LOCH,
                    outline="",
                    tags="statisch",
                )

        self.canvas.create_text(
            self._x(1),
            self._y(1) - 35,
            text="Spalten",
            anchor="w",
            font=("TkDefaultFont", 9, "bold"),
            tags="statisch",
        )
        self.canvas.create_text(
            self._x(1) - 34,
            self._y(1),
            text="Zeilen",
            anchor="s",
            angle=90,
            font=("TkDefaultFont", 9, "bold"),
            tags="statisch",
        )

    def _dynamische_elemente_zeichnen(self) -> None:
        self.canvas.delete("dynamisch")

        for nummer, (name, platz) in enumerate(self.lager.LAGERPLAETZE.items(), start=1):
            spalte, zeile = platz["mittelloch"]
            stapel = platz["stapel"]
            anzahl = sum(container is not None for container in stapel)
            oberster = next(
                (container for container in reversed(stapel) if container is not None),
                None,
            )

            x = self._x(spalte)
            y = self._y(zeile)
            halbe_breite = self.RASTER * 1.42
            fuellung = self.FARBE_BELEGT.get(anzahl, self.FARBE_FREI)

            tags = ("dynamisch", f"lagerplatz_{nummer}")
            self.canvas.create_rectangle(
                x - halbe_breite,
                y - halbe_breite,
                x + halbe_breite,
                y + halbe_breite,
                fill=fuellung,
                outline=self.FARBE_LAGERPLATZ,
                width=2,
                tags=tags,
            )

            kurzname = name if len(name) <= 14 else name[:12] + "…"
            self.canvas.create_text(
                x,
                y - self.RASTER * 0.72,
                text=kurzname,
                font=("TkDefaultFont", 7, "bold"),
                tags=tags,
            )

            inhalt = "frei" if anzahl == 0 else f"{anzahl}×\n{oberster}"
            self.canvas.create_text(
                x,
                y + 3,
                text=inhalt,
                justify="center",
                font=("TkDefaultFont", 8),
                tags=tags,
            )

            self.canvas.create_text(
                x,
                y + self.RASTER * 0.78,
                text=f"({spalte}, {zeile})",
                font=("TkDefaultFont", 7),
                tags=tags,
            )

            self.canvas.tag_bind(
                f"lagerplatz_{nummer}",
                "<Enter>",
                lambda _event, n=name: self._lagerplatz_hover(n),
            )

        if self._ziel is not None:
            spalte, zeile = self._ziel
            x = self._x(spalte)
            y = self._y(zeile)
            r = self.RASTER * 1.62
            self.canvas.create_rectangle(
                x - r,
                y - r,
                x + r,
                y + r,
                outline=self.FARBE_ZIEL,
                width=3,
                dash=(6, 3),
                tags="dynamisch",
            )
            self.canvas.create_line(
                x - 8,
                y,
                x + 8,
                y,
                fill=self.FARBE_ZIEL,
                width=2,
                tags="dynamisch",
            )
            self.canvas.create_line(
                x,
                y - 8,
                x,
                y + 8,
                fill=self.FARBE_ZIEL,
                width=2,
                tags="dynamisch",
            )

        if self._roboterposition is not None:
            spalte, zeile = self._roboterposition
            x = self._x(spalte)
            y = self._y(zeile)
            r = 8
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                outline=self.FARBE_ROBOTER,
                width=4,
                tags="dynamisch",
            )

    # ------------------------------------------------------------------
    # Befehlsverarbeitung im tkinter-Hauptthread
    # ------------------------------------------------------------------

    def _befehl(self, name: str, *argumente: Any) -> None:
        if not self._geschlossen:
            self._befehle.put((name, argumente))

    def _befehle_verarbeiten(self) -> None:
        if self._geschlossen:
            return

        neu_zeichnen = False
        seitenleiste_neu = False

        try:
            while True:
                name, argumente = self._befehle.get_nowait()

                if name == "status":
                    text, protokollieren = argumente
                    self._status = text
                    self.status_label.config(text=text, foreground="black")
                    if protokollieren:
                        self._protokoll_hinzufuegen(text)

                elif name == "ziel":
                    spalte, zeile, zielname = argumente
                    self._ziel = (spalte, zeile)
                    self._zielname = zielname
                    neu_zeichnen = True

                elif name == "ziel_loeschen":
                    self._ziel = None
                    self._zielname = ""
                    neu_zeichnen = True

                elif name == "roboterposition":
                    spalte, zeile = argumente
                    self._roboterposition = (spalte, zeile)
                    neu_zeichnen = True

                elif name == "lager_aktualisieren":
                    neu_zeichnen = True
                    seitenleiste_neu = True

                elif name == "fehler":
                    (text,) = argumente
                    self._status = text
                    self.status_label.config(text=text, foreground="#a00000")
                    self._protokoll_hinzufuegen("FEHLER: " + text)

                elif name == "programm_laeuft":
                    (self._programm_laeuft,) = argumente
                    if self._programm_laeuft:
                        self.schliessen_button.config(text="Programm läuft …")
                    else:
                        self.schliessen_button.config(text="Fenster schließen")

        except queue.Empty:
            pass

        if neu_zeichnen:
            self._dynamische_elemente_zeichnen()
        if seitenleiste_neu:
            self._seitenleiste_aktualisieren()

        self.root.after(40, self._befehle_verarbeiten)

    # ------------------------------------------------------------------
    # Hilfsfunktionen
    # ------------------------------------------------------------------

    def _x(self, spalte: int) -> float:
        return self.PLATTENRAND + (spalte - 1) * self.RASTER

    def _y(self, zeile: int) -> float:
        return self.PLATTENRAND + (zeile - 1) * self.RASTER

    def _lagerplatz_hover(self, name: str) -> None:
        try:
            platz = self.lager.LAGERPLAETZE[name]
        except KeyError:
            return

        spalte, zeile = platz["mittelloch"]
        stapel = ["frei" if x is None else str(x) for x in platz["stapel"]]
        self.status_label.config(
            text=(
                f"{name}\nMittelloch ({spalte}, {zeile})\n"
                f"unten → oben: {', '.join(stapel)}"
            ),
            foreground="black",
        )

    def _seitenleiste_aktualisieren(self) -> None:
        zeilen: list[str] = []

        if not self.lager.LAGERPLAETZE:
            zeilen.append("Noch keine Lagerplätze angelegt.")
        else:
            for name, platz in self.lager.LAGERPLAETZE.items():
                spalte, zeile = platz["mittelloch"]
                stapel = [
                    "–" if container is None else str(container)
                    for container in platz["stapel"]
                ]
                zeilen.append(
                    f"{name}\n  ({spalte}, {zeile})  "
                    f"[{', '.join(stapel)}]"
                )

        self.lager_text.config(state="normal")
        self.lager_text.delete("1.0", "end")
        self.lager_text.insert("1.0", "\n\n".join(zeilen))
        self.lager_text.config(state="disabled")

    def _protokoll_hinzufuegen(self, text: str) -> None:
        self.protokoll_text.config(state="normal")
        self.protokoll_text.insert("end", str(text) + "\n")
        self.protokoll_text.see("end")
        self.protokoll_text.config(state="disabled")

    def _fenster_schliessen(self) -> None:
        if self._programm_laeuft:
            messagebox.showwarning(
                "Roboterprogramm läuft",
                "Das Fenster bleibt geöffnet, solange das Roboterprogramm "
                "läuft. So wird der Ablauf nicht versehentlich unterbrochen.",
                parent=self.root,
            )
            return

        self._geschlossen = True
        self.root.destroy()


if __name__ == "__main__":
    # Kleine Anzeigeprobe ohne Dobot.
    import containerlager as demo_lager

    demo_lager.LAGERPLAETZE.clear()
    demo_lager.lagerplatz_hinzufuegen("Wareneingang", 5, 4)
    demo_lager.lagerplatz_hinzufuegen("Lager links", 8, 4)
    demo_lager.lagerplatz_hinzufuegen("Lager rechts", 11, 4)
    demo_lager.lagerplatz_hinzufuegen("Warenausgang", 14, 4)
    demo_lager.einlagern("W01", "Wareneingang")
    demo_lager.einlagern("W02", "Lager rechts")
    demo_lager.einlagern("W03", "Lager rechts")

    demo = LochplattenAnzeige(demo_lager, "Anzeigeprobe Containerlager")
    demo.ziel_setzen(8, 4, "Lager links")
    demo.roboterposition_setzen(5, 4)
    demo.status_setzen("Anzeigeprobe ohne angeschlossenen Dobot")
    demo.start()
