import io
import json
import os
import queue
import threading
import tkinter as tk
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk


class PhotoClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32-CAM Fotoabruf")
        self.root.geometry("980x760")
        self.root.minsize(720, 560)
        self.events = queue.Queue()
        self.photo_bytes = None
        self.photo_image = None
        self.suggested_filename = "esp32-cam-photo.jpg"
        self.addresses = self._load_addresses()

        self._build_ui()
        self.root.after(100, self._process_events)

    @staticmethod
    def _settings_path():
        base = Path(os.environ.get("APPDATA", Path.home())) / "ESP32-CAM"
        return base / "photo_client.json"

    def _load_addresses(self):
        try:
            data = json.loads(self._settings_path().read_text(encoding="utf-8"))
            return [str(value).strip() for value in data.get("addresses", []) if str(value).strip()]
        except (OSError, ValueError, TypeError):
            return []

    def _save_addresses(self):
        path = self._settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"addresses": self.addresses}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _remember_address(self, address):
        if address not in self.addresses:
            self.addresses.append(address)
            self.address_entry.configure(values=self.addresses)
            self._save_addresses()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        controls = ttk.LabelFrame(outer, text="ESP32-CAM", padding=10)
        controls.pack(fill="x")
        ttk.Label(controls, text="IP-Adresse oder Name").pack(side="left")
        self.address_entry = ttk.Combobox(controls, values=self.addresses, width=30)
        if self.addresses:
            self.address_entry.set(self.addresses[0])
        self.address_entry.pack(side="left", padx=(8, 10))
        self.capture_button = ttk.Button(controls, text="Neues Foto aufnehmen", command=self._capture)
        self.capture_button.pack(side="left")
        self.save_button = ttk.Button(controls, text="Foto speichern unter ...", command=self._save, state="disabled")
        self.save_button.pack(side="left", padx=(8, 0))

        self.status_label = ttk.Label(outer, text="Bereit", anchor="w")
        self.status_label.pack(fill="x", pady=(10, 6))

        preview = ttk.LabelFrame(outer, text="Empfangenes Foto", padding=10)
        preview.pack(fill="both", expand=True)
        self.image_label = ttk.Label(preview, text="Noch kein Foto empfangen", anchor="center")
        self.image_label.pack(fill="both", expand=True)

    @staticmethod
    def _capture_url(address):
        address = address.strip().rstrip("/")
        if not address.startswith(("http://", "https://")):
            address = "http://" + address
        return address + "/photo-capture"

    def _capture(self):
        address = self.address_entry.get().strip()
        if not address:
            messagebox.showwarning("Foto aufnehmen", "Bitte die IP-Adresse des ESP32-CAM eingeben.")
            return
        self.capture_button.configure(state="disabled")
        self.status_label.configure(text="Das Modul nimmt ein Foto auf ...")
        threading.Thread(target=self._download_photo, args=(address,), daemon=True).start()

    def _download_photo(self, address):
        try:
            request = urllib.request.Request(
                self._capture_url(address),
                headers={"Cache-Control": "no-cache", "User-Agent": "ESP32-CAM-PhotoClient/1.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
                content_type = response.headers.get_content_type()
            if content_type != "image/jpeg" or not data.startswith(b"\xff\xd8"):
                raise RuntimeError("Das Modul hat keine gültige JPEG-Datei gesendet.")
            Image.open(io.BytesIO(data)).verify()
            self.events.put(("photo", (address, data)))
        except (OSError, urllib.error.URLError, RuntimeError) as error:
            self.events.put(("error", str(error)))

    def _show_photo(self, data):
        image = Image.open(io.BytesIO(data))
        image.thumbnail((900, 620), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.photo_image, text="")

    def _save(self):
        if not self.photo_bytes:
            return
        path = filedialog.asksaveasfilename(
            title="Foto speichern",
            defaultextension=".jpg",
            initialfile=self.suggested_filename,
            filetypes=(("JPEG-Bild", "*.jpg"), ("Alle Dateien", "*.*")),
        )
        if not path:
            return
        try:
            Path(path).write_bytes(self.photo_bytes)
            self.status_label.configure(text=f"Foto gespeichert: {path}")
        except OSError as error:
            messagebox.showerror("Foto speichern", str(error))

    def _process_events(self):
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "photo":
                    address, self.photo_bytes = value
                    self._remember_address(address)
                    self.suggested_filename = datetime.now().strftime("esp32-cam-%Y%m%d-%H%M%S.jpg")
                    self._show_photo(self.photo_bytes)
                    self.status_label.configure(
                        text=f"Foto empfangen: {len(self.photo_bytes):,} Bytes"
                    )
                    self.save_button.configure(state="normal")
                    self.capture_button.configure(state="normal")
                elif event == "error":
                    self.capture_button.configure(state="normal")
                    self.status_label.configure(text="Foto konnte nicht empfangen werden")
                    messagebox.showerror("Foto aufnehmen", value)
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)


def main():
    root = tk.Tk()
    PhotoClientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
