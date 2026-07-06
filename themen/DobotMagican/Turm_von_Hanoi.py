"""
Türme von Hanoi - Bildschirm-Animation
========================================

Dies ist die "virtuelle Zwillings-Version" von dobot_hanoi.py:
Die gleiche Hanoi-Logik (hanoi_moves) und die gleiche Programmstruktur
(pick_disc / place_disc / execute_hanoi) wie beim echten Dobot-Programm -
nur dass statt device.move_to(...) eine Matplotlib-Animation auf dem
Bildschirm gezeichnet wird.

Praktisch fuer:
    - Vorfuehrungen/Erklaerungen OHNE angeschlossenen Roboter
    - Schnelles Testen der Logik mit vielen Scheiben (der Dobot waere bei
      z.B. 10 Scheiben und 1023 Zuegen ewig beschaeftigt)
    - Projektion neben dem echten Dobot auf der Messe ("hier siehst du,
      was der Roboter gerade denkt")

Voraussetzungen:
    pip install matplotlib

Verwendung:
    python hanoi_animation.py                 # Standard: 3 Scheiben
    python hanoi_animation.py -n 6             # 6 Scheiben
    python hanoi_animation.py -n 5 --speed 0.3 # schnellere Animation
"""

import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation


# ---------------------------------------------------------------------------
# HANOI-ALGORITHMUS
# Identisch zu dobot_hanoi.py - das ist bewusst 1:1 derselbe Code!
# ---------------------------------------------------------------------------

def hanoi_moves(n, source, target, auxiliary, moves):
    """Erzeugt rekursiv die Liste der Zuege (from_peg, to_peg) fuer n Scheiben."""
    if n == 0:
        return
    hanoi_moves(n - 1, source, auxiliary, target, moves)
    moves.append((source, target))
    hanoi_moves(n - 1, auxiliary, target, source, moves)


# ---------------------------------------------------------------------------
# VISUELLE KONFIGURATION
# ---------------------------------------------------------------------------

PEG_X = {"A": 2, "B": 5, "C": 8}   # horizontale Position der drei Tuerme
PEG_BASE_Y = 0                      # Y-Position der Turmbasis
DISC_HEIGHT = 1                     # Hoehe einer Scheibe in Zeichnungs-Einheiten
PEG_HEIGHT = 8                      # Hoehe der Turmstangen (visuell)

# Farben fuer die Scheiben (werden bei Bedarf wiederholt/erweitert)
DISC_COLORS = [
    "#e63946", "#f1a208", "#2a9d8f", "#264653",
    "#e76f51", "#8ecae6", "#ffb703", "#6a994e",
    "#9b5de5", "#00b4d8",
]


# ---------------------------------------------------------------------------
# ANIMATIONS-ZUSTAND
# Entspricht funktional den "stack_heights" im Dobot-Programm, nur dass wir
# hier zusaetzlich die tatsaechlichen Scheiben-Objekte (matplotlib patches)
# je Turm verwalten, um sie zeichnen/verschieben zu koennen.
# ---------------------------------------------------------------------------

class HanoiAnimation:
    def __init__(self, num_discs, speed=0.6):
        self.num_discs = num_discs
        self.speed = speed  # Sekunden "gedachte" Dauer pro Teilschritt (fuer Frame-Anzahl)

        # Zugfolge berechnen - GENAU WIE beim Dobot-Programm
        self.moves = []
        hanoi_moves(num_discs, "A", "C", "B", self.moves)
        self.total_moves = len(self.moves)

        # Stapelinhalte: Liste von Scheiben-Groessen pro Turm, unten -> oben
        # Start: alle Scheiben auf A, groesste unten (Groesse = num_discs .. 1)
        self.stacks = {
            "A": list(range(num_discs, 0, -1)),
            "B": [],
            "C": [],
        }

        # Matplotlib-Setup
        self.fig, self.ax = plt.subplots(figsize=(9, 6))
        self._setup_axes()

        # Patch-Objekte pro Scheibe (key = Scheibengroesse, value = Rectangle)
        self.disc_patches = {}
        self._draw_initial_state()

        # Fortschritts-Zaehler durch die Zugfolge
        self.move_index = 0

        # Aktuell "in der Luft" befindliche Scheibe (fuer die Zwischenanimation)
        self.flying_disc = None
        self.flight_progress = 0.0  # 0.0 -> 1.0 waehrend eines Zuges
        self.flight_from = None
        self.flight_to = None
        self.flight_disc_size = None
        self.flight_start_height = 0
        self.flight_target_height = 0

        self.status_text = self.ax.text(
            0.5, 0.95, "", transform=self.ax.transAxes,
            ha="center", va="top", fontsize=12
        )

    # -- Zeichnungs-Hilfsfunktionen ---------------------------------------

    def _setup_axes(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-1, PEG_HEIGHT + 1)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_title(
            f"Türme von Hanoi – {self.num_discs} Scheiben "
            f"({2**self.num_discs - 1} Züge)"
        )

        # Turmstangen und Basis zeichnen
        for peg, x in PEG_X.items():
            self.ax.plot([x, x], [PEG_BASE_Y, PEG_BASE_Y + PEG_HEIGHT],
                         color="gray", linewidth=4, zorder=1)
            self.ax.text(x, PEG_BASE_Y - 0.5, peg, ha="center",
                         fontsize=14, fontweight="bold")

        # Grundplatte
        self.ax.plot([0.5, 9.5], [PEG_BASE_Y, PEG_BASE_Y],
                     color="saddlebrown", linewidth=8, zorder=0)

    def _disc_width(self, size):
        """Groessere Scheiben (kleinere Nummer im Sinne 'unterste=groesste')
        sollen breiter gezeichnet werden. size=num_discs ist die groesste."""
        min_width, max_width = 0.8, 2.6
        span = max_width - min_width
        # size reicht von 1 (kleinste) bis num_discs (groesste)
        fraction = (size - 1) / max(1, self.num_discs - 1)
        return min_width + fraction * span

    def _disc_color(self, size):
        return DISC_COLORS[(size - 1) % len(DISC_COLORS)]

    def _draw_initial_state(self):
        """Zeichnet alle Scheiben an ihrer Startposition (Turm A)."""
        for level, size in enumerate(self.stacks["A"]):
            self._create_disc_patch(size, "A", level)

    def _create_disc_patch(self, size, peg, level):
        width = self._disc_width(size)
        x_center = PEG_X[peg]
        y = PEG_BASE_Y + level * DISC_HEIGHT
        rect = patches.Rectangle(
            (x_center - width / 2, y), width, DISC_HEIGHT * 0.9,
            facecolor=self._disc_color(size), edgecolor="black", zorder=3
        )
        self.ax.add_patch(rect)
        self.disc_patches[size] = rect

    def _set_disc_position(self, size, x_center, y_bottom):
        rect = self.disc_patches[size]
        width = rect.get_width()
        rect.set_xy((x_center - width / 2, y_bottom))

    # -- Animations-Logik ---------------------------------------------------
    # Diese Methoden entsprechen konzeptionell pick_disc()/place_disc() aus
    # dem Dobot-Programm: statt Saugnapf an/aus wird die Scheibe hier per
    # Interpolation "geflogen".

    def _start_next_move(self):
        """Startet den naechsten Zug aus der vorab berechneten Zugfolge."""
        if self.move_index >= self.total_moves:
            return False  # fertig

        src, dst = self.moves[self.move_index]
        disc_size = self.stacks[src][-1]  # oberste Scheibe des Quellturms

        self.flight_disc_size = disc_size
        self.flight_from = src
        self.flight_to = dst
        self.flight_start_height = (len(self.stacks[src]) - 1) * DISC_HEIGHT
        self.flight_target_height = len(self.stacks[dst]) * DISC_HEIGHT
        self.flight_progress = 0.0

        # Scheibe logisch schon vom Quellturm entfernen (wird erst am Ende
        # dem Zielturm hinzugefuegt) - analog zu stack_heights im Dobot-Code
        self.stacks[src].pop()

        return True

    def _finish_current_move(self):
        """Schliesst den aktuellen Zug ab: Scheibe liegt jetzt auf dem Zielturm."""
        self.stacks[self.flight_to].append(self.flight_disc_size)
        self._set_disc_position(
            self.flight_disc_size,
            PEG_X[self.flight_to],
            len(self.stacks[self.flight_to]) - 1
        )
        self.move_index += 1
        self.flight_disc_size = None

    def update_frame(self, frame):
        """Wird von FuncAnimation pro Frame aufgerufen - entspricht grob
        einem 'Tick' der Roboterbewegung zwischen zwei move_to()-Aufrufen."""

        if self.flight_disc_size is None:
            started = self._start_next_move()
            if not started:
                self.status_text.set_text(
                    f"Fertig! {self.total_moves} Züge ausgeführt."
                )
                return list(self.disc_patches.values()) + [self.status_text]

        # Bahnkurve: hoch -> horizontal -> runter (wie SAFE_Z beim Dobot)
        self.flight_progress += self.speed
        t = min(self.flight_progress, 1.0)

        lift_height = PEG_HEIGHT * 0.85  # entspricht SAFE_Z beim echten Dobot

        x_src = PEG_X[self.flight_from]
        x_dst = PEG_X[self.flight_to]

        if t < 0.25:
            # Phase 1: anheben
            phase_t = t / 0.25
            x = x_src
            y = self.flight_start_height + phase_t * (lift_height - self.flight_start_height)
        elif t < 0.75:
            # Phase 2: horizontal zum Zielturm fliegen
            phase_t = (t - 0.25) / 0.5
            x = x_src + phase_t * (x_dst - x_src)
            y = lift_height
        else:
            # Phase 3: absenken auf Zielhoehe
            phase_t = (t - 0.75) / 0.25
            x = x_dst
            y = lift_height + phase_t * (self.flight_target_height - lift_height)

        self._set_disc_position(self.flight_disc_size, x, y)

        move_num = self.move_index + 1
        self.status_text.set_text(
            f"Zug {move_num}/{self.total_moves}: "
            f"{self.flight_from} → {self.flight_to}"
        )

        if t >= 1.0:
            self._finish_current_move()

        return list(self.disc_patches.values()) + [self.status_text]

    def run(self):
        # interval in ms zwischen Frames; frames="unendlich" da wir selbst
        # per move_index/total_moves erkennen, wann Schluss ist
        anim = FuncAnimation(
            self.fig, self.update_frame, interval=30, blit=False,
            cache_frame_data=False
        )
        plt.show()
        return anim  # Referenz halten, damit die Animation nicht vom GC entfernt wird


# ---------------------------------------------------------------------------
# KOMMANDOZEILE / HAUPTPROGRAMM
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Türme von Hanoi als Bildschirm-Animation (Begleitprogramm "
                    "zum Dobot-Programm dobot_hanoi.py)."
    )
    parser.add_argument(
        "-n", "--num-discs", type=int, default=3,
        help="Anzahl der Scheiben (Standard: 3)."
    )
    parser.add_argument(
        "--speed", type=float, default=0.02,
        help="Fortschritt pro Frame (0.0-1.0, Standard 0.02). "
             "Größere Werte = schnellere Animation."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.num_discs < 1:
        print("FEHLER: Anzahl der Scheiben muss mindestens 1 sein.")
        sys.exit(1)

    print(f"Starte Animation mit {args.num_discs} Scheiben "
          f"({2**args.num_discs - 1} Züge)...")

    animation = HanoiAnimation(num_discs=args.num_discs, speed=args.speed)
    anim_ref = animation.run()


if __name__ == "__main__":
    main()