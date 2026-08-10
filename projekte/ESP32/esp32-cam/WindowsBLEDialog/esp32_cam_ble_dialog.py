import asyncio
import ipaddress
import json
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from bleak import BleakClient, BleakScanner


DEFAULT_DEVICE_NAME = "ESP32-CAM-Setup"
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


class BleController:
    def __init__(self, events):
        self.events = events
        self.client = None
        self.notification_buffer = ""
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _submit(self, coroutine):
        return asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    def connect(self, device_name):
        self._submit(self._connect(device_name))

    async def _connect(self, device_name):
        if self.client and self.client.is_connected:
            self.events.put(("status", "Bereits verbunden"))
            return

        if self.client:
            await self._disconnect_silently()

        self.events.put(("status", f"Suche {device_name} ..."))
        try:
            device = await BleakScanner.find_device_by_name(device_name, timeout=12.0)
            if device is None:
                raise RuntimeError(
                    "Modul nicht gefunden. Prüfe, ob der BLE-Konfigurationsmodus aktiv ist."
                )

            self.events.put(("status", "Verbinde ..."))
            self.events.put(("device_found", device.name or device_name))
            self.client = BleakClient(device, disconnected_callback=self._on_disconnected)
            await self.client.connect()

            service = self.client.services.get_service(SERVICE_UUID)
            if service is None:
                raise RuntimeError("Nordic-UART-Dienst wurde nicht gefunden.")
            if service.get_characteristic(RX_UUID) is None or service.get_characteristic(TX_UUID) is None:
                raise RuntimeError("RX- oder TX-Characteristic wurde nicht gefunden.")

            await self.client.start_notify(TX_UUID, self._on_notification)
            self.notification_buffer = ""
            self.events.put(("connected", True))
            self.events.put(("status", f"Verbunden mit {device.name or device_name}"))
            self.events.put(("console", "\n--- Verbunden ---\n"))
            self.events.put(("wifi_list_reset", None))
            await self._send("WLAN LISTE", "WLAN LISTE (automatisch)")
        except Exception as error:
            await self._disconnect_silently()
            self.events.put(("connected", False))
            self.events.put(("error", str(error)))
            self.events.put(("status", "Nicht verbunden"))

    def disconnect(self):
        self._submit(self._disconnect())

    async def _disconnect(self):
        await self._disconnect_silently()
        self.events.put(("connected", False))
        self.events.put(("status", "Nicht verbunden"))
        self.events.put(("console", "\n--- Verbindung getrennt ---\n"))

    async def _disconnect_silently(self):
        if self.client:
            try:
                if self.client.is_connected:
                    await self.client.disconnect()
            finally:
                self.client = None

    def send(self, command, display_command=None):
        if command.strip().upper() == "WLAN LISTE":
            self.events.put(("wifi_list_reset", None))
        self._submit(self._send(command, display_command))

    async def _send(self, command, display_command):
        if not self.client or not self.client.is_connected:
            self.events.put(("error", "Keine BLE-Verbindung zum ESP32-CAM."))
            return

        command = command.strip()
        if not command:
            return

        shown = display_command if display_command is not None else command
        self.events.put(("console", f"\n> {shown}\n"))
        try:
            characteristic = self.client.services.get_characteristic(RX_UUID)
            if characteristic is None:
                raise RuntimeError("BLE-Empfangskanal wurde nicht gefunden.")

            payload = (command + "\n").encode("utf-8")
            chunk_size = max(20, characteristic.max_write_without_response_size)
            for start in range(0, len(payload), chunk_size):
                await self.client.write_gatt_char(
                    characteristic,
                    payload[start : start + chunk_size],
                    response=False,
                )
        except Exception as error:
            self.events.put(("error", f"Senden fehlgeschlagen: {error}"))

    def _on_notification(self, _characteristic, data):
        self.notification_buffer += bytes(data).decode("utf-8", errors="replace")
        while "\n" in self.notification_buffer:
            line, self.notification_buffer = self.notification_buffer.split("\n", 1)
            self.events.put(("console", line + "\n"))
            number, separator, ssid = line.strip().partition(": ")
            if separator and number.isdigit() and ssid:
                self.events.put(("wifi_network", ssid))

    def _on_disconnected(self, client):
        if self.client is client:
            self.client = None
        self.events.put(("connected", False))
        self.events.put(("status", "Verbindung wurde getrennt"))
        self.events.put(("console", "\n--- ESP32-CAM getrennt ---\n"))

    def close(self):
        future = self._submit(self._disconnect_silently())
        try:
            future.result(timeout=3)
        except Exception:
            pass
        self.loop.call_soon_threadsafe(self.loop.stop)


class BleDialogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32-CAM WLAN-Konfiguration")
        self.root.geometry("760x650")
        self.root.minsize(680, 560)
        self.events = queue.Queue()
        self.controller = BleController(self.events)
        self.connected = False
        self.device_names = self._load_device_names()

        self._build_ui()
        self._set_connected(False)
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        connection = ttk.LabelFrame(outer, text="Verbindung", padding=10)
        connection.pack(fill="x")
        ttk.Label(connection, text="Modulname").pack(side="left")
        self.device_name_entry = ttk.Combobox(connection, values=self.device_names, width=24)
        self.device_name_entry.set(self.device_names[0])
        self.device_name_entry.pack(side="left", padx=(8, 12))
        self.status_label = ttk.Label(connection, text="Nicht verbunden")
        self.status_label.pack(side="left", fill="x", expand=True)
        self.connect_button = ttk.Button(
            connection,
            text="Suchen und verbinden",
            command=self._connect_device,
        )
        self.connect_button.pack(side="left", padx=(8, 0))
        self.disconnect_button = ttk.Button(connection, text="Trennen", command=self.controller.disconnect)
        self.disconnect_button.pack(side="left", padx=(8, 0))

        quick = ttk.LabelFrame(outer, text="WLAN verwalten", padding=10)
        quick.pack(fill="x", pady=(12, 0))
        ttk.Label(quick, text="WLAN-Name (SSID)").grid(row=0, column=0, sticky="w")
        ttk.Label(quick, text="Passwort").grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.ssid_entry = ttk.Combobox(quick)
        self.ssid_entry.grid(row=1, column=0, sticky="ew")
        self.password_entry = ttk.Entry(quick, show="•")
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0))
        self.add_button = ttk.Button(quick, text="WLAN speichern", command=self._add_wifi)
        self.add_button.grid(row=1, column=2, padx=(8, 0))
        self.delete_button = ttk.Button(quick, text="WLAN löschen", command=self._delete_wifi)
        self.delete_button.grid(row=1, column=3, padx=(8, 0))
        quick.columnconfigure(0, weight=1)
        quick.columnconfigure(1, weight=1)

        actions = ttk.Frame(quick)
        actions.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        self.quick_buttons = []
        for label, command in (
            ("Hilfe", "HILFE"),
            ("Status", "STATUS"),
            ("WLAN-Liste", "WLAN LISTE"),
        ):
            button = ttk.Button(actions, text=label, command=lambda value=command: self.controller.send(value))
            button.pack(side="left", padx=(0, 8))
            self.quick_buttons.append(button)
        self.connect_wifi_button = ttk.Button(
            actions,
            text="Ausgewähltes WLAN verbinden und neu starten",
            command=self._connect_wifi,
        )
        self.connect_wifi_button.pack(side="left", padx=(0, 8))
        self.quick_buttons.append(self.connect_wifi_button)

        ttk.Label(quick, text="AP-IP-Adresse").grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.ap_ip_entry = ttk.Entry(quick)
        self.ap_ip_entry.insert(0, "192.168.4.1")
        self.ap_ip_entry.grid(row=4, column=0, sticky="ew")
        self.start_ap_button = ttk.Button(
            quick,
            text="Access Point starten und neu starten",
            command=self._start_access_point,
        )
        self.start_ap_button.grid(row=4, column=1, columnspan=2, sticky="w", padx=(8, 0))
        self.quick_buttons.append(self.start_ap_button)

        terminal = ttk.LabelFrame(outer, text="Dialog", padding=10)
        terminal.pack(fill="both", expand=True, pady=(12, 0))
        text_frame = ttk.Frame(terminal)
        text_frame.pack(fill="both", expand=True)
        self.console = tk.Text(text_frame, wrap="word", state="disabled", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=scrollbar.set)
        self.console.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        command_line = ttk.Frame(terminal)
        command_line.pack(fill="x", pady=(8, 0))
        self.command_entry = ttk.Entry(command_line)
        self.command_entry.pack(side="left", fill="x", expand=True)
        self.command_entry.bind("<Return>", lambda _event: self._send_manual())
        self.send_button = ttk.Button(command_line, text="Senden", command=self._send_manual)
        self.send_button.pack(side="left", padx=(8, 0))
        self.clear_button = ttk.Button(command_line, text="Anzeige leeren", command=self._clear_console)
        self.clear_button.pack(side="left", padx=(8, 0))

    def _set_connected(self, connected):
        self.connected = connected
        state = "normal" if connected else "disabled"
        self.disconnect_button.configure(state=state)
        self.add_button.configure(state=state)
        self.delete_button.configure(state=state)
        self.send_button.configure(state=state)
        self.command_entry.configure(state=state)
        for button in self.quick_buttons:
            button.configure(state=state)
        self.connect_button.configure(state="disabled" if connected else "normal")
        self.device_name_entry.configure(state="disabled" if connected else "normal")

    @staticmethod
    def _settings_path():
        base = Path(os.environ.get("APPDATA", Path.home())) / "ESP32-CAM"
        return base / "ble_dialog.json"

    def _load_device_names(self):
        try:
            data = json.loads(self._settings_path().read_text(encoding="utf-8"))
            names = [str(name).strip() for name in data.get("device_names", []) if str(name).strip()]
        except (OSError, ValueError, TypeError):
            names = []
        if DEFAULT_DEVICE_NAME not in names:
            names.insert(0, DEFAULT_DEVICE_NAME)
        return names

    def _save_device_names(self):
        path = self._settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"device_names": self.device_names}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _remember_device_name(self, name):
        name = name.strip()
        if name and name not in self.device_names:
            self.device_names.append(name)
            self.device_name_entry.configure(values=self.device_names)
            self._save_device_names()

    def _connect_device(self):
        name = self.device_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Bluetooth LE", "Bitte einen Modulnamen eingeben oder auswählen.")
            return
        self.controller.connect(name)

    def _add_wifi(self):
        ssid = self.ssid_entry.get().strip()
        password = self.password_entry.get()
        if not ssid:
            messagebox.showwarning("WLAN speichern", "Bitte einen WLAN-Namen eingeben.")
            return
        command = f"WLAN HINZUFUEGEN {ssid}|{password}"
        self.controller.send(command, f"WLAN HINZUFUEGEN {ssid}|********")
        self.password_entry.delete(0, "end")

    def _delete_wifi(self):
        ssid = self.ssid_entry.get().strip()
        if not ssid:
            messagebox.showwarning("WLAN löschen", "Bitte den zu löschenden WLAN-Namen eingeben.")
            return
        self.controller.send(f"WLAN LOESCHEN {ssid}")

    def _connect_wifi(self):
        ssid = self.ssid_entry.get().strip()
        if not ssid:
            messagebox.showwarning("WLAN verbinden", "Bitte ein gespeichertes WLAN auswählen.")
            return
        self.controller.send(f"WLAN VERBINDEN {ssid}")

    def _start_access_point(self):
        value = self.ap_ip_entry.get().strip()
        try:
            address = ipaddress.IPv4Address(value)
        except ipaddress.AddressValueError:
            messagebox.showwarning("Access Point", "Bitte eine gültige IPv4-Adresse eingeben.")
            return
        octets = tuple(int(part) for part in value.split("."))
        private_range = (
            octets[0] == 10
            or (octets[0] == 172 and 16 <= octets[1] <= 31)
            or (octets[0] == 192 and octets[1] == 168)
        )
        if not address.is_private or not private_range or octets[3] in (0, 255):
            messagebox.showwarning(
                "Access Point",
                "Bitte eine private IPv4-Adresse mit einer Hostnummer von 1 bis 254 verwenden.",
            )
            return
        self.controller.send(f"MODUS AP {address}")

    def _send_manual(self):
        command = self.command_entry.get()
        if command.strip():
            self.controller.send(command)
            self.command_entry.delete(0, "end")

    def _append_console(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _process_events(self):
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "console":
                    self._append_console(value)
                elif event == "status":
                    self.status_label.configure(text=value)
                elif event == "connected":
                    self._set_connected(value)
                elif event == "wifi_list_reset":
                    self.ssid_entry.configure(values=())
                elif event == "wifi_network":
                    values = list(self.ssid_entry.cget("values"))
                    if value not in values:
                        values.append(value)
                        self.ssid_entry.configure(values=values)
                elif event == "device_found":
                    self._remember_device_name(value)
                elif event == "error":
                    messagebox.showerror("Bluetooth LE", value)
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)

    def _close(self):
        self.controller.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    BleDialogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
