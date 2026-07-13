"""
Virtueller Dobot Magician auf einer 70 x 50 cm Lochrasterplatte.

Dieses Programm zeigt eine Draufsicht ohne Maus-/Slider-Bedienung.
Die Steuerung erfolgt durch echten Python-Code in der Funktion
`user_program(dobot)`.

Start:
    python dobot_virtual_python.py

Der wichtige Bereich fuer eigene Experimente steht ganz unten.
"""

import math
import time
import tkinter as tk


SCALE = 1.25
PLATE_W = 700
PLATE_H = 500
PITCH = 16
HOLE_COLS = 40
HOLE_ROWS = 26
HOLE_START_X = (PLATE_W - (HOLE_COLS - 1) * PITCH) / 2
HOLE_START_Y = (PLATE_H - (HOLE_ROWS - 1) * PITCH) / 2


def mm(value):
    return value * SCALE


def clamp(value, low, high):
    return max(low, min(high, value))


class Cube:
    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        self.level = 0


class VirtualDobot:
    def __init__(self, scene):
        self.scene = scene
        self.base_x = 350
        self.base_y = 380
        self.joint1 = 0
        self.joint2 = 35
        self.joint3 = 35
        self.joint4 = 0
        self.suction_on = False
        self.attached_cube = None

        self.min_reach = 80
        self.max_reach = 315
        self.column_offset = 82
        self.upper_arm = 135
        self.fore_arm = 160
        self.wrist_length = 34

    def movej(self, joint1=None, joint2=None, joint3=None, joint4=None, pause=0.25):
        if joint1 is not None:
            self.joint1 = clamp(joint1, -135, 135)
        if joint2 is not None:
            self.joint2 = clamp(joint2, -10, 85)
        if joint3 is not None:
            self.joint3 = clamp(joint3, -20, 95)
        if joint4 is not None:
            self.joint4 = clamp(joint4, -180, 180)
        self.render()
        self.wait(pause)

    def move_xy(self, x, y, pause=0.25):
        dx = x - self.base_x
        dy = y - self.base_y
        distance = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx))
        self.joint1 = clamp(angle, -135, 135)
        target_reach = clamp(distance, self.min_reach, self.max_reach)
        self.joint3 = clamp(self._joint3_for_reach(self.joint2, target_reach), -20, 95)
        self.render()
        self.wait(pause)

    def suction(self, enabled, pause=0.2):
        enabled = bool(enabled)
        if enabled and not self.suction_on:
            self.attached_cube = self.scene.find_top_cube_near(*self.tool_position())
        if not enabled and self.suction_on:
            self.scene.release_cube(self.attached_cube, *self.tool_position())
            self.attached_cube = None
        self.suction_on = enabled
        self.render()
        self.wait(pause)

    def wait(self, seconds):
        self.scene.root.update()
        time.sleep(seconds)

    def home(self):
        self.base_x = 350
        self.base_y = 380
        self.joint1 = 0
        self.joint2 = 35
        self.joint3 = 35
        self.joint4 = 0
        self.suction(False, pause=0.1)
        self.render()

    def tool_position(self):
        return self.forward_kinematics()["tool"]

    def forward_kinematics(self):
        a = math.radians(self.joint1)
        j2 = math.radians(self.joint2)
        j23 = math.radians(self.joint2 + self.joint3)

        elbow_reach = self.column_offset + self.upper_arm * math.cos(j2)
        wrist_reach = elbow_reach + self.fore_arm * math.cos(j23)
        reach = clamp(wrist_reach + self.wrist_length, self.min_reach, self.max_reach)

        def radial(distance):
            return (
                self.base_x + math.cos(a) * distance,
                self.base_y + math.sin(a) * distance,
            )

        return {
            "base": (self.base_x, self.base_y),
            "shoulder": radial(self.column_offset),
            "elbow": radial(elbow_reach),
            "wrist": radial(wrist_reach),
            "tool": radial(reach),
            "angle": a,
        }

    def _joint3_for_reach(self, joint2, desired_reach):
        local_reach = clamp(
            desired_reach - self.column_offset - self.wrist_length,
            -self.upper_arm - self.fore_arm,
            self.upper_arm + self.fore_arm,
        )
        j2 = math.radians(joint2)
        fore_projection = local_reach - self.upper_arm * math.cos(j2)
        cos_j23 = clamp(fore_projection / self.fore_arm, -1, 1)
        return math.degrees(math.acos(cos_j23)) - joint2

    def render(self):
        if self.attached_cube:
            self.attached_cube.x, self.attached_cube.y = self.tool_position()
            self.attached_cube.level = 0
        self.scene.draw()


class Scene:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Virtueller Dobot Magician")
        self.canvas = tk.Canvas(
            self.root,
            width=int(mm(PLATE_W + 80)),
            height=int(mm(PLATE_H + 90)),
            bg="#edf1f5",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.cubes = [
            Cube("rot", "#d84a3a", 182, 162),
            Cube("blau", "#2f73d0", 246, 162),
            Cube("gelb", "#e5b73d", 310, 162),
        ]
        self.dobot = VirtualDobot(self)

    def sx(self, x):
        return mm(x + 40)

    def sy(self, y):
        return mm(y + 50)

    def draw(self):
        self.canvas.delete("all")
        self._draw_plate()
        self._draw_reach()
        self._draw_cubes()
        self._draw_dobot()
        self.root.update()

    def _draw_plate(self):
        self.canvas.create_rectangle(
            self.sx(0),
            self.sy(0),
            self.sx(PLATE_W),
            self.sy(PLATE_H),
            fill="#fbfbf8",
            outline="#222831",
            width=2,
        )
        self.canvas.create_text(
            self.sx(PLATE_W / 2),
            self.sy(-22),
            text="Lochrasterplatte 70 x 50 cm, 40 x 26 Loecher, Raster 16 mm",
            fill="#365f93",
            font=("Arial", 10, "bold"),
        )
        for row in range(HOLE_ROWS):
            for col in range(HOLE_COLS):
                x = HOLE_START_X + col * PITCH
                y = HOLE_START_Y + row * PITCH
                r = mm(2.8)
                self.canvas.create_oval(
                    self.sx(x) - r,
                    self.sy(y) - r,
                    self.sx(x) + r,
                    self.sy(y) + r,
                    fill="#17191c",
                    outline="",
                )

    def _draw_reach(self):
        d = self.dobot
        for radius, color in [(d.max_reach, "#2d8a5c"), (d.min_reach, "#d04a3a")]:
            self.canvas.create_oval(
                self.sx(d.base_x - radius),
                self.sy(d.base_y - radius),
                self.sx(d.base_x + radius),
                self.sy(d.base_y + radius),
                outline=color,
                dash=(5, 4),
            )

    def _draw_dobot(self):
        d = self.dobot
        fk = d.forward_kinematics()
        bx, by = fk["base"]
        sx, sy = fk["shoulder"]
        ex, ey = fk["elbow"]
        wx, wy = fk["wrist"]
        tx, ty = fk["tool"]

        self.canvas.create_rectangle(
            self.sx(bx - 80),
            self.sy(by - 80),
            self.sx(bx + 80),
            self.sy(by + 80),
            fill="#edf1f5",
            outline="#546170",
            width=2,
        )
        self._circle(bx, by, 42, "#cfd8e1", "#52606f", 2)
        self._circle(bx, by, 15, "#3f4b59", "")

        self._line(sx, sy, ex, ey, "#2f5f8e", 34)
        self._line(sx, sy, ex, ey, "#7bb8ec", 22)
        self._line(ex, ey, wx, wy, "#986025", 30)
        self._line(ex, ey, wx, wy, "#f0a24a", 18)

        self._circle(sx, sy, 19, "#edf2f6", "#586674", 2)
        self._circle(ex, ey, 24, "#e8eef4", "#586674", 2)
        self._circle(ex, ey, 8, "#2f3d4f", "")
        self._circle(tx, ty, 18, "#f4f7f9", "#586674", 2)
        self._circle(tx, ty, 20 if d.suction_on else 17, "#2d8a5c" if d.suction_on else "#d04a3a", "#873327", 2)

        self.canvas.create_text(
            self.sx(12),
            self.sy(PLATE_H + 24),
            anchor="w",
            text=f"joint1={d.joint1:.0f}  joint2={d.joint2:.0f}  joint3={d.joint3:.0f}  J4={d.joint4:.0f}  Sauger={'an' if d.suction_on else 'aus'}",
            fill="#1b2430",
            font=("Consolas", 10),
        )

    def _draw_cubes(self):
        for cube in sorted(self.cubes, key=lambda item: item.level):
            offset = -5 * cube.level
            x = cube.x + offset
            y = cube.y + offset
            size = 40
            self.canvas.create_rectangle(
                self.sx(x - size / 2),
                self.sy(y - size / 2),
                self.sx(x + size / 2),
                self.sy(y + size / 2),
                fill=cube.color,
                outline="#233041",
                width=2,
            )
            for dx in (-16, 0, 16):
                for dy in (-16, 0, 16):
                    if dx == 0 and dy == 0:
                        continue
                    self._circle(x + dx, y + dy, 3.4, "#f7fafc", "#233041", 1)

    def _circle(self, x, y, r, fill, outline, width=1):
        self.canvas.create_oval(
            self.sx(x - r),
            self.sy(y - r),
            self.sx(x + r),
            self.sy(y + r),
            fill=fill,
            outline=outline,
            width=width,
        )

    def _line(self, x1, y1, x2, y2, color, width):
        self.canvas.create_line(
            self.sx(x1),
            self.sy(y1),
            self.sx(x2),
            self.sy(y2),
            fill=color,
            width=mm(width),
            capstyle=tk.ROUND,
        )

    def find_top_cube_near(self, x, y, radius=24):
        candidates = [
            cube for cube in self.cubes
            if math.hypot(cube.x - x, cube.y - y) <= radius and self.is_top_cube(cube)
        ]
        if not candidates:
            print("Kein Wuerfel unter dem Sauggreifer.")
            return None
        return max(candidates, key=lambda cube: cube.level)

    def is_top_cube(self, cube):
        return not any(
            other is not cube
            and math.hypot(other.x - cube.x, other.y - cube.y) < 2
            and other.level > cube.level
            for other in self.cubes
        )

    def release_cube(self, cube, x, y):
        if cube is None:
            return
        snapped_x = self.snap_to_raster(x, "x")
        snapped_y = self.snap_to_raster(y, "y")
        stack = self.find_stack_near(snapped_x, snapped_y, ignore=cube)
        if stack:
            cube.x = stack.x
            cube.y = stack.y
            cube.level = self.stack_height(stack.x, stack.y)
        else:
            cube.x = snapped_x
            cube.y = snapped_y
            cube.level = 0

    def snap_to_raster(self, value, axis):
        first = HOLE_START_X if axis == "x" else HOLE_START_Y
        limit = (PLATE_W if axis == "x" else PLATE_H) - 20
        return clamp(first + round((value - first) / PITCH) * PITCH, 20, limit)

    def find_stack_near(self, x, y, ignore=None, radius=30):
        candidates = [
            cube for cube in self.cubes
            if cube is not ignore and math.hypot(cube.x - x, cube.y - y) <= radius
        ]
        return max(candidates, key=lambda cube: cube.level) if candidates else None

    def stack_height(self, x, y):
        return len([cube for cube in self.cubes if math.hypot(cube.x - x, cube.y - y) < 2])


def user_program(dobot):
    """
    HIER eigenen Python-Code eintragen.

    Verfuegbare Befehle:
        dobot.home()
        dobot.move_xy(x, y)
        dobot.movej(joint1=..., joint2=..., joint3=..., joint4=...)
        dobot.suction(True / False)
        dobot.wait(sekunden)
    """

    # Beispiel: roten Wuerfel aufnehmen und auf den blauen Wuerfel stapeln.
    dobot.home()
    dobot.move_xy(182, 162)
    dobot.suction(True)
    dobot.wait(0.4)
    dobot.move_xy(246, 162)
    dobot.suction(False)

    # Beispiel fuer echte Python-Kontrollstrukturen:
    for angle in [-35, -10, 15, 40, 15, -10, -35]:
        dobot.movej(joint1=angle)
        dobot.wait(0.15)


def run(program=None):
    """Startet die Simulation und fuehrt danach das uebergebene Programm aus."""
    scene = Scene()
    scene.draw()
    active_program = program or user_program
    scene.root.after(500, lambda: active_program(scene.dobot))
    scene.root.mainloop()


def main():
    run(user_program)


if __name__ == "__main__":
    main()
