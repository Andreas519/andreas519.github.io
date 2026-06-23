import network
import socket
import time
from machine import ADC, Pin

# =========================
# WLAN-Zugangsdaten
# =========================
SSID = "raspi"
PASSWORD = "abcd1234"

# =========================
# ADC-Einstellung
# =========================
adc_pin = ADC(Pin(4))          # ADC-Pin, z.B. GPIO34
adc_pin.atten(ADC.ATTN_11DB)    # Bereich ungefähr 0...3,3 V
adc_pin.width(ADC.WIDTH_12BIT)  # Werte 0...4095

# =========================
# Messspeicher
# =========================
MAX_N = 2000                    # Sicherheitsgrenze
N = 300                         # Standardwert
werte = [0] * N


# =========================
# WLAN verbinden
# =========================
def wlan_verbinden():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Verbinde mit WLAN ...")
        wlan.connect(SSID, PASSWORD)

        for i in range(20):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(1)

    print()

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WLAN verbunden")
        print("IP-Adresse:", ip)
        return ip
    else:
        print("Keine WLAN-Verbindung")
        return None


# =========================
# einfache URL-Decodierung
# =========================
def url_decode(text):
    text = text.replace("+", " ")
    result = ""
    i = 0

    while i < len(text):
        if text[i] == "%" and i + 2 < len(text):
            try:
                result += chr(int(text[i+1:i+3], 16))
                i += 3
            except:
                result += text[i]
                i += 1
        else:
            result += text[i]
            i += 1

    return result


# =========================
# Query-Parameter aus URL holen
# Beispiel: /messen?n=500
# =========================
def hole_parameter(pfad, name):
    suchtext = name + "="
    pos = pfad.find(suchtext)

    if pos == -1:
        return None

    start = pos + len(suchtext)
    ende = pfad.find("&", start)

    if ende == -1:
        ende = len(pfad)

    return url_decode(pfad[start:ende])


# =========================
# Messung durchführen
# =========================
def messen(anzahl):
    global N, werte

    if anzahl < 1:
        anzahl = 1

    if anzahl > MAX_N:
        anzahl = MAX_N

    N = anzahl
    werte = [0] * N

    print("Messung startet, N =", N)

    t_start = time.ticks_us()

    for i in range(N):
        werte[i] = adc_pin.read()

    t_ende = time.ticks_us()
    messzeit_us = time.ticks_diff(t_ende, t_start)

    print("Messung abgeschlossen")
    print("Messzeit:", messzeit_us, "us")

    return messzeit_us


# =========================
# Messwerte als CSV
# =========================
def werte_als_csv():
    text = ""

    for i in range(N):
        text += str(i) + ";" + str(werte[i]) + "\n"

    return text


# =========================
# HTML-Seite
# =========================
def html_seite():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 Web-Speicheroszi</title>

<style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        background: #eeeeee;
    }

    .box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        max-width: 1000px;
        box-shadow: 0px 0px 8px #aaa;
    }

    h1 {
        margin-top: 0;
    }

    label {
        font-size: 18px;
    }

    input {
        font-size: 18px;
        padding: 6px;
        width: 120px;
    }

    button {
        font-size: 18px;
        padding: 8px 16px;
        margin: 5px;
    }

    #status {
        margin: 12px 0;
        font-size: 18px;
        color: darkblue;
    }

    canvas {
        border: 1px solid #555;
        background: white;
        margin-top: 10px;
    }

    textarea {
        width: 900px;
        height: 180px;
        font-family: monospace;
        font-size: 14px;
        margin-top: 10px;
    }
</style>
</head>

<body>
<div class="box">
    <h1>ESP32 Web-Speicheroszi</h1>

    <label>Anzahl Messwerte:</label>
    <input id="anzahl" type="number" value="300" min="1" max="2000">

    <button onclick="messenUndZeichnen()">Messung starten</button>
    <button onclick="csvAnzeigen()">CSV anzeigen</button>
    <button onclick="diagrammLoeschen()">Diagramm löschen</button>

    <div id="status">Bereit</div>

    <canvas id="plot" width="900" height="420"></canvas>

    <h3>CSV-Daten</h3>
    <textarea id="csv" placeholder="Hier erscheinen die Messwerte als CSV ..."></textarea>
</div>

<script>
let aktuelleDaten = [];

async function messenUndZeichnen() {
    let n = document.getElementById("anzahl").value;

    document.getElementById("status").textContent = "Messung läuft ...";
    document.getElementById("csv").value = "";

    try {
        let r1 = await fetch("/messen?n=" + encodeURIComponent(n));
        let antwort = await r1.text();

        document.getElementById("status").textContent = antwort + " / Lade Messwerte ...";

        let r2 = await fetch("/werte");
        let csv = await r2.text();

        document.getElementById("csv").value = csv;

        aktuelleDaten = csvZuArray(csv);
        zeichneDiagramm(aktuelleDaten);

        document.getElementById("status").textContent =
            "Diagramm angezeigt: " + aktuelleDaten.length + " Messwerte";
    }
    catch (err) {
        document.getElementById("status").textContent = "Fehler: " + err;
    }
}


async function csvAnzeigen() {
    try {
        let r = await fetch("/werte");
        let csv = await r.text();

        document.getElementById("csv").value = csv;

        aktuelleDaten = csvZuArray(csv);
        zeichneDiagramm(aktuelleDaten);

        document.getElementById("status").textContent =
            "CSV geladen: " + aktuelleDaten.length + " Messwerte";
    }
    catch (err) {
        document.getElementById("status").textContent = "Fehler: " + err;
    }
}


function csvZuArray(csv) {
    let zeilen = csv.trim().split("\\n");
    let daten = [];

    for (let i = 0; i < zeilen.length; i++) {
        let teile = zeilen[i].split(";");

        if (teile.length >= 2) {
            let wert = Number(teile[1]);

            if (!isNaN(wert)) {
                daten.push(wert);
            }
        }
    }

    return daten;
}


function zeichneDiagramm(daten) {
    const canvas = document.getElementById("plot");
    const ctx = canvas.getContext("2d");

    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    if (daten.length < 2) {
        ctx.font = "20px Arial";
        ctx.fillText("Zu wenige Daten", 50, 50);
        return;
    }

    const left = 55;
    const right = 20;
    const top = 20;
    const bottom = 40;

    const pw = w - left - right;
    const ph = h - top - bottom;

    let minv = Math.min(...daten);
    let maxv = Math.max(...daten);

    if (maxv == minv) {
        maxv = minv + 1;
    }

    // Hintergrund
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);

    // Gitternetz horizontal
    ctx.strokeStyle = "#dddddd";
    ctx.lineWidth = 1;

    for (let i = 0; i <= 10; i++) {
        let y = top + i * ph / 10;
        ctx.beginPath();
        ctx.moveTo(left, y);
        ctx.lineTo(w - right, y);
        ctx.stroke();
    }

    // Gitternetz vertikal
    for (let i = 0; i <= 10; i++) {
        let x = left + i * pw / 10;
        ctx.beginPath();
        ctx.moveTo(x, top);
        ctx.lineTo(x, h - bottom);
        ctx.stroke();
    }

    // Achsen
    ctx.strokeStyle = "black";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(left, top);
    ctx.lineTo(left, h - bottom);
    ctx.lineTo(w - right, h - bottom);
    ctx.stroke();

    // Beschriftung
    ctx.fillStyle = "black";
    ctx.font = "14px Arial";

    ctx.fillText(maxv, 5, top + 5);
    ctx.fillText(minv, 5, h - bottom);
    ctx.fillText("0", left - 5, h - 15);
    ctx.fillText(daten.length - 1, w - right - 30, h - 15);

    // Kurve
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < daten.length; i++) {
        let x = left + i * pw / (daten.length - 1);
        let y = top + (maxv - daten[i]) * ph / (maxv - minv);

        if (i == 0) {
            ctx.moveTo(x, y);
        }
        else {
            ctx.lineTo(x, y);
        }
    }

    ctx.stroke();

    // Info
    ctx.fillStyle = "black";
    ctx.font = "14px Arial";
    ctx.fillText("ADC-Min: " + minv + "   ADC-Max: " + maxv, left, 18);
}


function diagrammLoeschen() {
    const canvas = document.getElementById("plot");
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById("status").textContent = "Diagramm gelöscht";
}
</script>

</body>
</html>
"""


# =========================
# HTTP-Antwort senden
# =========================
def sende_antwort(client, content, content_type="text/plain; charset=utf-8"):
    header = "HTTP/1.1 200 OK\r\n"
    header += "Content-Type: " + content_type + "\r\n"
    header += "Connection: close\r\n\r\n"

    client.send(header.encode("utf-8"))

    if isinstance(content, str):
        client.send(content.encode("utf-8"))
    else:
        client.send(content)


# =========================
# Webserver
# =========================
def webserver_starten():
    ip = wlan_verbinden()

    if ip is None:
        print("Webserver nicht gestartet.")
        return

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Webserver läuft")
    print("Browser öffnen: http://" + ip)

    while True:
        client = None

        try:
            client, addr = s.accept()
            request = client.recv(1024).decode("utf-8")

            # Erste Zeile der HTTP-Anfrage holen
            erste_zeile = request.split("\r\n")[0]
            teile = erste_zeile.split(" ")

            if len(teile) < 2:
                client.close()
                continue

            pfad = teile[1]
            print("Anfrage:", pfad)

            # -------------------------
            # Messung starten
            # -------------------------
            if pfad.startswith("/messen"):
                n_text = hole_parameter(pfad, "n")

                try:
                    anzahl = int(n_text)
                except:
                    anzahl = N

                messzeit_us = messen(anzahl)

                antwort = "Messung abgeschlossen: "
                antwort += str(N) + " Werte, "
                antwort += str(messzeit_us) + " us"

                sende_antwort(client, antwort)

            # -------------------------
            # Messwerte senden
            # -------------------------
            elif pfad.startswith("/werte"):
                csv = werte_als_csv()
                sende_antwort(client, csv, "text/plain; charset=utf-8")

            # -------------------------
            # Hauptseite senden
            # -------------------------
            else:
                seite = html_seite()
                sende_antwort(client, seite, "text/html; charset=utf-8")

            client.close()

        except Exception as e:
            print("Fehler:", e)

            if client:
                try:
                    client.close()
                except:
                    pass


# =========================
# Start
# =========================
webserver_starten()