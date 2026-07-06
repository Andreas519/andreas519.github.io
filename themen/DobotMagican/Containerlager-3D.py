import tkinter as tk
import time

# ------------------------------------------------------------
# Dobot-Containerlager Simulation
# Lochrasterplatte: 40 x 25 Löcher
# Container mit vier Zapfen
# Stapeln über Ebene / level
# ------------------------------------------------------------

GRID_COLS = 40
GRID_ROWS = 25

HOLE_DISTANCE = 20       # Pixelabstand zwischen Löchern
MARGIN = 50

CONTAINER_SIZE = 2       # Container nutzt 2 Lochabstände
LEVEL_OFFSET = 10        # optischer Höhenversatz pro Stapel-Ebene
MAX_LEVEL = 3            # erlaubt: 0, 1, 2, 3

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

    def level_shift(self, level):
        return -level * LEVEL_OFFSET

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

        # Spaltenbeschriftung
        for col in range(1, GRID_COLS + 1, 5):
            x, y = self.grid_to_pixel(col, 1)
            self.canvas.create_text(
                x,
                y - 18,
                text=str(col),
                font=("Arial", 8)
            )

        # Zeilenbeschriftung
        for row in range(1, GRID_ROWS + 1, 5):
            x, y = self.grid_to_pixel(1, row)
            self.canvas.create_text(
                x - 22,
                y,
                text=str(row),
                font=("Arial", 8)
            )

    def draw_robot(self):
        x = self.robot_x
        y = self.robot_y

        self.robot_items = []

        # symbolischer Greifer
        self.robot_items.append(
            self.canvas.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill="red",
                outline="black"
            )
        )

        # symbolische Z-Achse
        self.robot_items.append(
            self.canvas.create_line(
                x, y - 35, x, y - 10,
                width=3
            )
        )

        self.robot_items.append(
            self.canvas.create_text(
                x + 30,
                y - 20,
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

    def draw_container(self, name, col, row, level=0, color="orange"):
        if level < 0 or level > MAX_LEVEL:
            self.set_status(f"Fehler: Ebene {level} ist nicht erlaubt")
            return

        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)

        shift = self.level_shift(level)
        y1 += shift
        y2 += shift

        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="black",
            width=2
        )

        text = self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=f"{name}\nE{level}",
            font=("Arial", 9, "bold")
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
            py += shift

            peg = self.canvas.create_oval(
                px - 5, py - 5, px + 5, py + 5,
                fill="brown",
                outline="black"
            )
            peg_items.append(peg)

        self.containers[name] = {
            "col": col,
            "row": row,
            "level": level,
            "color": color,
            "items": [rect, text] + peg_items
        }

        # Container mit höherem Level nach vorne holen
        self.bring_container_to_front(name)

    def bring_container_to_front(self, name):
        for item in self.containers[name]["items"]:
            self.canvas.tag_raise(item)

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
        level = container["level"]
        self.canvas.coords(items[1], center_x, center_y)
        self.canvas.itemconfig(items[1], text=f"{name}\nE{level}")

        # Zapfen
        peg_positions = [
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2),
        ]

        for peg, (px, py) in zip(items[2:], peg_positions):
            self.canvas.coords(peg, px - 5, py - 5, px + 5, py + 5)

        self.bring_container_to_front(name)

    def snap_container_to_slot(self, name):
        container = self.containers[name]

        col = container["col"]
        row = container["row"]
        level = container["level"]

        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)

        shift = self.level_shift(level)

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2 + shift

        self.move_container_graphics(name, center_x, center_y)

    # --------------------------------------------------------
    # Lagerlogik
    # --------------------------------------------------------
    def containers_at_slot(self, col, row):
        found = []

        for name, data in self.containers.items():
            if data["col"] == col and data["row"] == row:
                found.append((data["level"], name))

        found.sort()
        return found

    def is_level_free(self, col, row, level):
        for data in self.containers.values():
            if data["col"] == col and data["row"] == row and data["level"] == level:
                return False
        return True

    def can_place_at(self, col, row, level):
        if level < 0 or level > MAX_LEVEL:
            return False, f"Ebene {level} ist nicht erlaubt"

        if not self.is_level_free(col, row, level):
            return False, f"Platz ({col}, {row}, Ebene {level}) ist belegt"

        # Ebene 0 darf immer belegt werden
        if level == 0:
            return True, "OK"

        # Für Ebene > 0 muss darunter ein Container liegen
        if self.is_level_free(col, row, level - 1):
            return False, f"Ebene {level} braucht darunter einen Container auf Ebene {level - 1}"

        return True, "OK"

    def top_level_at(self, col, row):
        found = self.containers_at_slot(col, row)

        if not found:
            return None

        return found[-1]

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

    def move_to_slot(self, col, row, level=0):
        self.set_status(f"MOVE: Fahre zu Lagerplatz ({col}, {row}), Ebene {level}")

        x1, y1 = self.grid_to_pixel(col, row)
        x2, y2 = self.grid_to_pixel(col + CONTAINER_SIZE, row + CONTAINER_SIZE)

        shift = self.level_shift(level)

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2 + shift

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
            return False

        if self.carried_container is not None:
            self.set_status("Fehler: Dobot trägt bereits einen Container")
            return False

        container = self.containers[name]
        col = container["col"]
        row = container["row"]
        level = container["level"]

        top = self.top_level_at(col, row)

        if top is not None:
            top_level, top_name = top
            if top_name != name:
                self.set_status(
                    f"Fehler: Container {name} ist blockiert durch {top_name}"
                )
                return False

        self.set_status(f"PICK: Container {name} aufnehmen")
        self.move_to_slot(col, row, level)
        self.suction_on()

        self.carried_container = name
        return True

    def place(self, name, col, row, level=0):
        if self.carried_container != name:
            self.set_status(f"Fehler: Container {name} wird nicht getragen")
            return False

        ok, message = self.can_place_at(col, row, level)
        if not ok:
            self.set_status("Fehler: " + message)
            return False

        self.set_status(f"PLACE: Container {name} ablegen auf ({col}, {row}), Ebene {level}")
        self.move_to_slot(col, row, level)

        self.containers[name]["col"] = col
        self.containers[name]["row"] = row
        self.containers[name]["level"] = level

        self.suction_off()
        self.carried_container = None

        self.snap_container_to_slot(name)
        self.redraw_stack_order(col, row)

        return True

    def redraw_stack_order(self, col, row):
        stack = self.containers_at_slot(col, row)

        for level, name in stack:
            self.bring_container_to_front(name)

    # --------------------------------------------------------
    # Beispielprogramm
    # --------------------------------------------------------
    def demo(self):
        self.home()

        # Drei Container zu einem Stapel bringen
        if self.pick("C1"):
            self.place("C1", 15, 8, level=0)

        if self.pick("C2"):
            self.place("C2", 15, 8, level=1)

        if self.pick("C3"):
            self.place("C3", 15, 8, level=2)

        # Einen weiteren Container daneben ablegen
        if self.pick("C4"):
            self.place("C4", 22, 8, level=0)

        # Obersten Container vom Stapel wieder wegnehmen
        if self.pick("C3"):
            self.place("C3", 30, 15, level=0)

        self.home()
        self.set_status("Demo beendet")


# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    sim = DobotLagerSimulation(root)

    # Startcontainer am Wareneingang
    sim.draw_container("C1", 4, 4, level=0, color="orange")
    sim.draw_container("C2", 4, 9, level=0, color="skyblue")
    sim.draw_container("C3", 4, 14, level=0, color="lightgreen")
    sim.draw_container("C4", 4, 19, level=0, color="khaki")

    # Demo nach kurzer Pause starten
    root.after(1000, sim.demo)

    root.mainloop()