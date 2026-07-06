import tkinter as tk
import time
import math

# ------------------------------------------------------------
# Dobot-Containerlager Simulation
# Lochrasterplatte: 40 x 25 Löcher
# ------------------------------------------------------------

GRID_COLS = 40
GRID_ROWS = 25

HOLE_DISTANCE = 20      # Pixelabstand zwischen Löchern
MARGIN = 50

CONTAINER_SIZE = 2      # Container nutzt 2 Lochabstände
ANIMATION_DELAY = 0.01


class DobotLagerSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Dobot Magician - Containerlager Simulation")

        width = MARGIN * 2 + (GRID_COLS - 1) * HOLE_DISTANCE
        height = MARGIN * 2 + (GRID_ROWS - 1) * HOLE_DISTANCE + 120

        self.canvas = tk.Canvas(root, width=width, height=height, bg="white")
        self.canvas.pack()

        self.status = tk.Label(root, text="Bereit", font=("Arial", 12))
        self.status.pack(pady=5)

        self.containers = {}
        self.carried_container = None

        self.robot_x, self.robot_y = self.grid_to_pixel(1, 1)

        self.draw_plate()
        self.draw_robot()

    # --------------------------------------------------------
    # Umrechnung Rasterkoordinaten -> Bildschirmkoordinaten
    # --------------------------------------------------------
    def grid_to_pixel(self, col, row):
        x = MARGIN + (col - 1) * HOLE_DISTANCE
        y = MARGIN + (row - 1) * HOLE_DISTANCE
        return x, y

    # --------------------------------------------------------
    # Zeichenfunktionen
    # --------------------------------------------------------
    def draw_plate(self):
        self.canvas.create_text(
            MARGIN,
            20,
            anchor="w",
            text="Lochrasterplatte 40 x 25",
            font=("Arial", 14, "bold")
        )

        for row in range(1, GRID_ROWS + 1):
            for col in range(1, GRID_COLS + 1):
                x, y = self.grid_to_pixel(col, row)
                self.canvas.create_oval(
                    x - 3, y - 3, x + 3, y + 3,
                    fill="lightgray",
                    outline="gray"
                )

        # Achsenbeschriftung
        for col in range(1, GRID_COLS + 1, 5):
            x, y = self.grid_to_pixel(col, 1)
            self.canvas.create_text(x, y - 18, text=str(col), font=("Arial", 8))

        for row in range(1, GRID_ROWS + 1, 5):
            x, y = self.grid_to_pixel(1, row)
            self.canvas.create_text(x - 22, y, text=str(row), font=("Arial", 8))

    def draw_robot(self):
        x = self.robot_x
        y = self.robot_y

        self.robot_items = []

        # Greifer-Kreis
        self.robot_items.append(
            self.canvas.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill="red",
                outline="black"
            )
        )

        # Faden / Z-Achse symbolisch
        self.robot_items.append(
            self.canvas.create_line(
                x, y - 35, x, y - 10,
                width=3
            )
        )

        # Beschriftung
        self.robot_items.append(
            self.canvas.create_text(
                x + 30, y - 20,
                text="Dobot",
                font=("Arial", 10, "bold")
            )
        )

    def update_robot_position(self):
        for item in self.robot_items:
            self.canvas.delete(item)

        self.draw_robot()

        if self.carried_container is not None:
            self.move_container_graphics(
                self.carried_container,
                self.robot_x,
                self.robot_y
            )

        self.root.update()

    def draw_container(self, name, col, row, color="orange"):
        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)

        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="black",
            width=2
        )

        text = self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=name,
            font=("Arial", 10, "bold")
        )

        # Vier Zapfen
        peg_items = []
        for c, r in [
            (col, row),
            (col + CONTAINER_SIZE, row),
            (col, row + CONTAINER_SIZE),
            (col + CONTAINER_SIZE, row + CONTAINER_SIZE),
        ]:
            px, py = self.grid_to_pixel(c, r)
            peg = self.canvas.create_oval(
                px - 5, py - 5, px + 5, py + 5,
                fill="brown",
                outline="black"
            )
            peg_items.append(peg)

        self.containers[name] = {
            "col": col,
            "row": row,
            "items": [rect, text] + peg_items
        }

    def move_container_graphics(self, name, center_x, center_y):
        container = self.containers[name]
        items = container["items"]

        size = CONTAINER_SIZE * HOLE_DISTANCE
        x1 = center_x - size / 2
        y1 = center_y - size / 2
        x2 = center_x + size / 2
        y2 = center_y + size / 2

        # Rechteck
        self.canvas.coords(items[0], x1, y1, x2, y2)

        # Text
        self.canvas.coords(items[1], center_x, center_y)

        # Zapfenpositionen
        peg_positions = [
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2),
        ]

        for peg, (px, py) in zip(items[2:], peg_positions):
            self.canvas.coords(peg, px - 5, py - 5, px + 5, py + 5)

    # --------------------------------------------------------
    # Dobot-ähnliche Bewegungsbefehle
    # --------------------------------------------------------
    def set_status(self, text):
        self.status.config(text=text)
        self.root.update()

    def home(self):
        self.set_status("HOME: Dobot fährt zur Startposition")
        x, y = self.grid_to_pixel(1, 1)
        self.move_to_pixel(x, y)

    def move_to_pixel(self, target_x, target_y):
        steps = 60

        start_x = self.robot_x
        start_y = self.robot_y

        for i in range(1, steps + 1):
            t = i / steps
            self.robot_x = start_x + (target_x - start_x) * t
            self.robot_y = start_y + (target_y - start_y) * t
            self.update_robot_position()
            time.sleep(ANIMATION_DELAY)

    def move_to_slot(self, col, row):
        self.set_status(f"MOVE: Fahre zu Lagerplatz ({col}, {row})")
        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        self.move_to_pixel(center_x, center_y)

    def suction_on(self):
        self.set_status("SuctionCup ON: Container angesaugt")
        time.sleep(0.4)

    def suction_off(self):
        self.set_status("SuctionCup OFF: Container losgelassen")
        time.sleep(0.4)

    def pick(self, name):
        if name not in self.containers:
            self.set_status(f"Fehler: Container {name} existiert nicht")
            return

        container = self.containers[name]
        col = container["col"]
        row = container["row"]

        self.set_status(f"PICK: Container {name} aufnehmen")
        self.move_to_slot(col, row)
        self.suction_on()
        self.carried_container = name

    def place(self, name, col, row):
        if self.carried_container != name:
            self.set_status(f"Fehler: Container {name} wird nicht getragen")
            return

        self.set_status(f"PLACE: Container {name} ablegen auf ({col}, {row})")
        self.move_to_slot(col, row)

        self.containers[name]["col"] = col
        self.containers[name]["row"] = row

        self.suction_off()
        self.carried_container = None

        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)
        self.move_container_graphics(name, (x1 + x2) / 2, (y1 + y2) / 2)

    # --------------------------------------------------------
    # Beispielprogramm
    # --------------------------------------------------------
    def demo(self):
        self.home()

        self.pick("C1")
        self.place("C1", 15, 8)

        self.pick("C2")
        self.place("C2", 25, 15)

        self.pick("C3")
        self.place("C3", 35, 20)

        self.home()

        self.set_status("Demo beendet")


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    sim = DobotLagerSimulation(root)

    # Startcontainer
    sim.draw_container("C1", 4, 4, "orange")
    sim.draw_container("C2", 4, 9, "skyblue")
    sim.draw_container("C3", 4, 14, "lightgreen")

    # Demo nach kurzer Pause starten
    root.after(1000, sim.demo)

    root.mainloop()