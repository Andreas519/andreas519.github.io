import network
import socket
import time
from machine import ADC, Pin

# =========================
# WLAN-Zugangsdaten
# =========================
SSID = "raspi"
PASSWORD = "1234abcd"

# =========================
# ADC-Einstellung
# =========================
adc_pin = ADC(Pin(4))          # ADC-Pin, z.B. GPIO34
adc_pin.atten(ADC.ATTN_11DB)    # Bereich ungefähr 0...3,3 V
adc_pin.width(ADC.WIDTH_12BIT)  # Werte 0...4095

# =========================
# Messspeicher
# =========================
MAX_N = 2000
N = 300
DT_US = 100                    # Standard-Messintervall in Mikrosekunden
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
# Beispiel: /messen?n=500&dt=100
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
# dt_us = Abstand zwischen zwei Messwerten in Mikrosekunden
# =========================
def messen(anzahl, dt_us):
    global N, DT_US, werte

    if anzahl < 1:
        anzahl = 1

    if anzahl > MAX_N:
        anzahl = MAX_N

    if dt_us < 0:
        dt_us = 0

    N = anzahl
    DT_US = dt_us
    werte = [0] * N

    print("Messung startet")
    print("N     =", N)
    print("dt_us =", DT_US)

    t_start = time.ticks_us()

    if DT_US == 0:
        # so schnell wie möglich messen
        for i in range(N):
            werte[i] = adc_pin.read()
    else:
        # Messung mit festem Zeitraster
        t_next = time.ticks_us()

        for i in range(N):
            werte[i] = adc_pin.read()

            t_next = time.ticks_add(t_next, DT_US)

            while time.ticks_diff(t_next, time.ticks_us()) > 0:
                pass

    t_ende = time.ticks_us()
    messzeit_us = time.ticks_diff(t_ende, t_start)

    print("Messung abgeschlossen")
    print("Messzeit:", messzeit_us, "us")

    return messzeit_us


# =========================
# Messwerte als CSV
# Format:
# Zeit_in_us ; ADC-Wert
# =========================
# def werte_als_csv():
#     text = ""
# 
#     for i in range(N):
#         zeit = i * DT_US
#         text += str(zeit) + ";" + str(werte[i]) + "\n"
# 
#     return text
def sende_werte_csv(client):
    header = "HTTP/1.1 200 OK\r\n"
    header += "Content-Type: text/plain; charset=utf-8\r\n"
    header += "Connection: close\r\n\r\n"

    client.send(header.encode("utf-8"))

    for i in range(N):
        zeit = i * DT_US
        zeile = str(zeit) + ";" + str(werte[i]) + "\n"
        client.send(zeile.encode("utf-8"))

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
        margin-right: 8px;
    }

    input {
        font-size: 18px;
        padding: 6px;
        width: 130px;
        margin-right: 15px;
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

    <p>
        <label>Anzahl Messwerte:</label>
        <input id="anzahl" type="number" value="300" min="1" max="2000">

        <label>Intervall in µs:</label>
        <input id="intervall" type="number" value="100" min="0" max="1000000">
    </p>

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
let aktuelleZeiten = [];

async function messenUndZeichnen() {
    let n = document.getElementById("anzahl").value;
    let dt = document.getElementById("intervall").value;

    document.getElementById("status").textContent = "Messung läuft ...";
    document.getElementById("csv").value = "";

    try {
        let url = "/messen?n=" + encodeURIComponent(n) + "&dt=" + encodeURIComponent(dt);

        let r1 = await fetch(url);
        let antwort = await r1.text();

        document.getElementById("status").textContent = antwort + " / Lade Messwerte ...";

        let r2 = await fetch("/werte");
        let csv = await r2.text();

        document.getElementById("csv").value = csv;

        let datenObjekt = csvZuArrays(csv);
        aktuelleZeiten = datenObjekt.zeiten;
        aktuelleDaten = datenObjekt.werte;

        zeichneDiagramm(aktuelleZeiten, aktuelleDaten);

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

        let datenObjekt = csvZuArrays(csv);
        aktuelleZeiten = datenObjekt.zeiten;
        aktuelleDaten = datenObjekt.werte;

        zeichneDiagramm(aktuelleZeiten, aktuelleDaten);

        document.getElementById("status").textContent =
            "CSV geladen: " + aktuelleDaten.length + " Messwerte";
    }
    catch (err) {
        document.getElementById("status").textContent = "Fehler: " + err;
    }
}


function csvZuArrays(csv) {
    let zeilen = csv.trim().split("\\n");
    let zeiten = [];
    let werte = [];

    for (let i = 0; i < zeilen.length; i++) {
        let teile = zeilen[i].split(";");

        if (teile.length >= 2) {
            let zeit = Number(teile[0]);
            let wert = Number(teile[1]);

            if (!isNaN(zeit) && !isNaN(wert)) {
                zeiten.push(zeit);
                werte.push(wert);
            }
        }
    }

    return {
        zeiten: zeiten,
        werte: werte
    };
}


function zeichneDiagramm(zeiten, daten) {
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

    const left = 65;
    const right = 25;
    const top = 25;
    const bottom = 45;

    const pw = w - left - right;
    const ph = h - top - bottom;

    let minv = Math.min(...daten);
    let maxv = Math.max(...daten);

    if (maxv == minv) {
        maxv = minv + 1;
    }

    let t_min = zeiten[0];
    let t_max = zeiten[zeiten.length - 1];

    if (t_max == t_min) {
        t_max = t_min + daten.length - 1;
    }

    // Hintergrund
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);

    // Gitternetz
    ctx.strokeStyle = "#dddddd";
    ctx.lineWidth = 1;

    for (let i = 0; i <= 10; i++) {
        let y = top + i * ph / 10;
        ctx.beginPath();
        ctx.moveTo(left, y);
        ctx.lineTo(w - right, y);
        ctx.stroke();
    }

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

    ctx.fillText(maxv, 8, top + 5);
    ctx.fillText(minv, 8, h - bottom);

    ctx.fillText(t_min + " µs", left - 10, h - 15);
    ctx.fillText(t_max + " µs", w - right - 80, h - 15);

    // Kurve
    ctx.strokeStyle = "blue";
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < daten.length; i++) {
        let x = left + (zeiten[i] - t_min) * pw / (t_max - t_min);
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

    let dauer_us = t_max - t_min;
    let dauer_ms = dauer_us / 1000.0;

    ctx.fillText("ADC-Min: " + minv + "   ADC-Max: " + maxv, left, 18);
    ctx.fillText("Messdauer: " + dauer_us + " µs = " + dauer_ms.toFixed(3) + " ms", left + 320, 18);
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

            erste_zeile = request.split("\r\n")[0]
            teile = erste_zeile.split(" ")

            if len(teile) < 2:
                client.close()
                continue

            pfad = teile[1]
            print("Anfrage:", pfad)

            # -------------------------
            # Messung starten
            # Beispiel:
            # /messen?n=500&dt=100
            # -------------------------
            if pfad.startswith("/messen"):
                n_text = hole_parameter(pfad, "n")
                dt_text = hole_parameter(pfad, "dt")

                try:
                    anzahl = int(n_text)
                except:
                    anzahl = N

                try:
                    dt_us = int(dt_text)
                except:
                    dt_us = DT_US

                messzeit_us = messen(anzahl, dt_us)

                antwort = "Messung abgeschlossen: "
                antwort += str(N) + " Werte, "
                antwort += "Intervall " + str(DT_US) + " µs, "
                antwort += "reale Messzeit " + str(messzeit_us) + " µs"

                sende_antwort(client, antwort)

            # -------------------------
            # Messwerte senden
            # -------------------------
            elif pfad.startswith("/werte"):
                sende_werte_csv(client)

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