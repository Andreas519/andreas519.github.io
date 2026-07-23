import queue
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

HOST = "127.0.0.1"
PORT = 7000


class TCPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP-Client – 127.0.0.1:7000")
        self.root.geometry("760x610")
        self.root.minsize(680, 540)

        self.stop_event = threading.Event()
        self.ui_queue = queue.Queue()
        self.switch_commands = queue.Queue()

        self.connection = None
        self.connection_lock = threading.Lock()
        self.send_lock = threading.Lock()

        self.switch_state = False

        self.server_led_state = False
        self.server_led_mode = "AUS"

        self.create_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.close_program)
        self.root.after(100, self.process_ui_queue)

        threading.Thread(
            target=self.network_thread,
            name="Netzwerk-Thread",
            daemon=True,
        ).start()

        threading.Thread(
            target=self.switch_thread,
            name="Schalter-Thread",
            daemon=True,
        ).start()

    def create_gui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(
            main,
            text="TCP-Client",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(anchor="w")

        self.status_label = ttk.Label(
            main,
            text=f"Verbinde mit {HOST}:{PORT} …",
        )
        self.status_label.pack(anchor="w", pady=(0, 10))

        device_frame = ttk.Frame(main)
        device_frame.pack(fill="x", pady=(0, 10))
        device_frame.columnconfigure(0, weight=1)
        device_frame.columnconfigure(1, weight=1)

        # Steuerung der Server-LED
        led_frame = ttk.LabelFrame(
            device_frame,
            text="LED beim Server",
            padding=10,
        )
        led_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.led_canvas = tk.Canvas(
            led_frame,
            width=110,
            height=80,
            highlightthickness=0,
        )
        self.led_canvas.pack()
        self.led_shape = self.led_canvas.create_oval(
            25, 10, 85, 70,
            fill="#555555",
            outline="#222222",
            width=2,
        )

        self.led_text = ttk.Label(
            led_frame,
            text="Steuerung der Server-LED",
        )
        self.led_text.pack(pady=(0, 8))

        led_buttons = ttk.Frame(led_frame)
        led_buttons.pack()

        ttk.Button(
            led_buttons,
            text="EIN",
            command=lambda: self.send_command("LED EIN"),
        ).grid(row=0, column=0, padx=3)

        ttk.Button(
            led_buttons,
            text="AUS",
            command=lambda: self.send_command("LED AUS"),
        ).grid(row=0, column=1, padx=3)

        ttk.Button(
            led_buttons,
            text="BLINKEN",
            command=lambda: self.send_command("LED BLINK"),
        ).grid(row=0, column=2, padx=3)

        # Virtueller Schalter des Clients
        switch_frame = ttk.LabelFrame(
            device_frame,
            text="Virtueller Client-Schalter",
            padding=10,
        )
        switch_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.switch_canvas = tk.Canvas(
            switch_frame,
            width=150,
            height=80,
            highlightthickness=0,
        )
        self.switch_canvas.pack()
        self.switch_body = self.switch_canvas.create_rectangle(
            30, 20, 120, 60,
            fill="#777777",
            outline="#222222",
            width=2,
        )
        self.switch_knob = self.switch_canvas.create_oval(
            36, 25, 66, 55,
            fill="#eeeeee",
            outline="#333333",
        )

        self.switch_text = ttk.Label(switch_frame, text="AUS")
        self.switch_text.pack(pady=(0, 8))

        switch_buttons = ttk.Frame(switch_frame)
        switch_buttons.pack()

        ttk.Button(
            switch_buttons,
            text="EIN",
            command=lambda: self.switch_commands.put("EIN"),
        ).grid(row=0, column=0, padx=3)

        ttk.Button(
            switch_buttons,
            text="AUS",
            command=lambda: self.switch_commands.put("AUS"),
        ).grid(row=0, column=1, padx=3)

        ttk.Button(
            switch_buttons,
            text="UMSCHALTEN",
            command=lambda: self.switch_commands.put("UMSCHALTEN"),
        ).grid(row=0, column=2, padx=3)

        # Nachrichtenbereich
        message_frame = ttk.LabelFrame(
            main,
            text="Bidirektionale Kommunikation",
            padding=10,
        )
        message_frame.pack(fill="both", expand=True)

        input_frame = ttk.Frame(message_frame)
        input_frame.pack(fill="x")

        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side="left", fill="x", expand=True)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        ttk.Button(
            input_frame,
            text="Senden",
            command=self.send_message,
        ).pack(side="left", padx=(8, 0))

        self.log = scrolledtext.ScrolledText(
            message_frame,
            height=14,
            state="disabled",
            wrap="word",
            font=("Consolas", 10),
        )
        self.log.pack(fill="both", expand=True, pady=(10, 0))

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(10, 0))

        ttk.Button(
            bottom,
            text="Programm beenden",
            command=self.close_program,
        ).pack(side="right")

    def post_ui(self, action, *values):
        self.ui_queue.put((action, values))

    def process_ui_queue(self):
        while True:
            try:
                action, values = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if action == "log":
                self.append_log(values[0])

            elif action == "status":
                self.status_label.config(text=values[0])

            elif action == "switch":
                self.update_switch_display(values[0])

            elif action == "led":
                self.update_server_led_display(values[0], values[1])

        if not self.stop_event.is_set():
            self.root.after(100, self.process_ui_queue)

    def append_log(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def update_switch_display(self, state):
        if state:
            self.switch_canvas.itemconfig(self.switch_body, fill="#58b957")
            self.switch_canvas.coords(self.switch_knob, 84, 25, 114, 55)
            self.switch_text.config(text="EIN")
        else:
            self.switch_canvas.itemconfig(self.switch_body, fill="#777777")
            self.switch_canvas.coords(self.switch_knob, 36, 25, 66, 55)
            self.switch_text.config(text="AUS")

    def update_server_led_display(self, state, mode):
        color = "#ff3030" if state else "#555555"
        state_text = "EIN" if state else "AUS"
        self.led_canvas.itemconfig(self.led_shape, fill=color)
        self.led_text.config(text=f"{state_text} – Modus: {mode}")

    def network_thread(self):
        self.post_ui(
            "status",
            f"Verbinde mit {HOST}:{PORT} …",
        )
        self.post_ui("log", "Verbindungsaufbau gestartet.")

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            connection.connect((HOST, PORT))

            with self.connection_lock:
                self.connection = connection

            self.post_ui(
                "status",
                f"Mit Server {HOST}:{PORT} verbunden.",
            )
            self.post_ui("log", "Verbindung zum Server hergestellt.")

            with connection:
                with connection.makefile(
                    "r",
                    encoding="utf-8",
                    newline="\n",
                ) as input_stream:
                    for line in input_stream:
                        if self.stop_event.is_set():
                            break

                        text = line.rstrip("\r\n")
                        self.handle_received_text(text)

        except ConnectionRefusedError:
            self.post_ui(
                "status",
                "Keine Verbindung – zuerst den Server starten.",
            )
            self.post_ui(
                "log",
                "Verbindung abgelehnt. Bitte zuerst tcp-server-gui.py starten.",
            )

        except OSError as error:
            if not self.stop_event.is_set():
                self.post_ui("status", "Verbindungsfehler")
                self.post_ui("log", f"Verbindungsfehler: {error}")

        finally:
            with self.connection_lock:
                self.connection = None

            try:
                connection.close()
            except OSError:
                pass

            if not self.stop_event.is_set():
                self.post_ui("status", "Serververbindung beendet.")
                self.post_ui("log", "Serververbindung beendet.")

    def handle_received_text(self, text):
        command = text.upper()

        if command.startswith("LEDSTATUS "):
            teile = command.split()

            if len(teile) >= 3:
                zustand = teile[1] == "EIN"
                modus = teile[2]

                self.server_led_state = zustand
                self.server_led_mode = modus
                self.post_ui("led", zustand, modus)

        elif command == "SCHALTER EIN":
            self.switch_commands.put("EIN")
            self.post_ui("log", "Server schaltet den Client-Schalter EIN.")

        elif command == "SCHALTER AUS":
            self.switch_commands.put("AUS")
            self.post_ui("log", "Server schaltet den Client-Schalter AUS.")

        elif command == "SCHALTER UMSCHALTEN":
            self.switch_commands.put("UMSCHALTEN")
            self.post_ui("log", "Server schaltet den Client-Schalter um.")

        elif command == "ENDE":
            self.post_ui("log", "Server beendet die Verbindung.")

        else:
            self.post_ui("log", f"Server → Client: {text}")

    def switch_thread(self):
        self.post_ui("switch", self.switch_state)

        while not self.stop_event.is_set():
            try:
                command = self.switch_commands.get(timeout=0.2)
            except queue.Empty:
                continue

            if command == "EIN":
                self.switch_state = True

            elif command == "AUS":
                self.switch_state = False

            elif command == "UMSCHALTEN":
                self.switch_state = not self.switch_state

            self.post_ui("switch", self.switch_state)

            state_text = "EIN" if self.switch_state else "AUS"
            self.post_ui("log", f"Client-Schalter: {state_text}")
            self.send_text(f"SCHALTERSTATUS {state_text}")

    def send_text(self, text):
        with self.connection_lock:
            connection = self.connection

        if connection is None:
            self.post_ui("log", "Senden nicht möglich: Keine Serververbindung.")
            return False

        try:
            with self.send_lock:
                connection.sendall((text + "\n").encode("utf-8"))

            return True

        except OSError as error:
            self.post_ui("log", f"Sendefehler: {error}")
            return False

    def send_command(self, command):
        if self.send_text(command):
            self.post_ui("log", f"Client → Server: {command}")

    def send_message(self):
        text = self.message_entry.get().strip()

        if not text:
            return

        if self.send_text(text):
            self.post_ui("log", f"Client → Server: {text}")
            self.message_entry.delete(0, "end")

    def close_program(self):
        if self.stop_event.is_set():
            return

        self.send_text("ENDE")
        self.stop_event.set()

        with self.connection_lock:
            connection = self.connection

        if connection is not None:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                connection.close()
            except OSError:
                pass

        self.root.after(100, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = TCPClientGUI(root)
    root.mainloop()
