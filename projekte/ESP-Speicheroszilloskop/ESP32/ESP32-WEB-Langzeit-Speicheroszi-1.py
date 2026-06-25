# main.py
# ESP32 MicroPython Langzeit-Web-Speicheroszi

import network
import socket
import time
import json
from machine import ADC, Pin

# -----------------------------
# Einstellungen
# -----------------------------
SSID = "raspi"
PASS = "abcd1234"

MESS_PIN = 4          # ADC-Pin, z.B. GPIO4
MESSINTERVALL = 5000  # ms, z.B. 5000 = 5 Sekunden
MAX_WERTE = 200       # Anzahl gespeicherter Messwerte

# -----------------------------
# ADC vorbereiten
# -----------------------------
adc = ADC(Pin(MESS_PIN))
adc.atten(ADC.ATTN_11DB)      # Bereich bis ca. 3.3 V
adc.width(ADC.WIDTH_12BIT)    # 0...4095

werte = []
letzte_messung = 0


def wlan_verbinden():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASS)

    print("Verbinde WLAN...")
    while not wlan.isconnected():
        time.sleep(0.3)

    print("Verbunden:", wlan.ifconfig())
    return wlan.ifconfig()[0]


def messen():
    global letzte_messung

    jetzt = time.ticks_ms()

    if time.ticks_diff(jetzt, letzte_messung) >= MESSINTERVALL:
        letzte_messung = jetzt

        roh = adc.read()
        spannung = roh * 3.3 / 4095

        eintrag = {
            "t": time.time(),
            "roh": roh,
            "u": round(spannung, 3)
        }

        werte.append(eintrag)

        if len(werte) > MAX_WERTE:
            werte.pop(0)

        print("Messwert:", eintrag)


def html_seite():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 Langzeit-Speicheroszi</title>

<style>
body {
    font-family: Arial;
    margin: 20px;
    background: #f0f0f0;
}

#box {
    background: white;
    padding: 20px;
    border-radius: 12px;
    max-width: 900px;
}

#wert {
    font-size: 32px;
    font-weight: bold;
    color: #0060aa;
}

canvas {
    background: #111;
    width: 100%;
    height: 300px;
    border-radius: 8px;
}
</style>
</head>

<body>
<div id="box">
    <h1>ESP32 Langzeit-Web-Speicheroszi</h1>

    <p>Aktueller Messwert:</p>
    <div id="wert">---</div>

    <p>Letzte Aktualisierung: <span id="zeit">---</span></p>

    <canvas id="canvas" width="800" height="300"></canvas>
</div>

<script>
let daten = [];

async function aktualisieren() {
    try {
        let antwort = await fetch("/data");
        daten = await antwort.json();

        if (daten.length > 0) {
            let letzter = daten[daten.length - 1];
            document.getElementById("wert").innerHTML =
                letzter.u + " V &nbsp; (" + letzter.roh + ")";

            let jetzt = new Date();
            document.getElementById("zeit").innerHTML =
                jetzt.toLocaleTimeString();
        }

        zeichnen();
    } catch (e) {
        console.log("Fehler:", e);
    }
}

function zeichnen() {
    let c = document.getElementById("canvas");
    let ctx = c.getContext("2d");

    ctx.clearRect(0, 0, c.width, c.height);

    // Hintergrund
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, c.width, c.height);

    // Gitter
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 1;

    for (let x = 0; x < c.width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, c.height);
        ctx.stroke();
    }

    for (let y = 0; y < c.height; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(c.width, y);
        ctx.stroke();
    }

    if (daten.length < 1) return;

    ctx.strokeStyle = "#00ff66";
    ctx.lineWidth = 2;
    ctx.beginPath();

    for (let i = 0; i < daten.length; i++) {
        let x = i * c.width / (daten.length - 1);
        let y = c.height - daten[i].roh * c.height / 4095;

        if (i == 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }

    ctx.stroke();
}

// Webseite fragt regelmäßig nach neuen Daten.
// Sinnvoll: etwas schneller als das Messintervall.
setInterval(aktualisieren, 1000);
aktualisieren();
</script>

</body>
</html>
"""


def http_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Webserver läuft auf Port 80")

    while True:
        messen()

        try:
            s.settimeout(0.2)
            client, addr = s.accept()
        except OSError:
            continue

        request = client.recv(1024).decode()

        if "GET /data" in request:
            antwort = json.dumps(werte)
            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: application/json\r\n")
            client.send("Connection: close\r\n\r\n")
            client.send(antwort)

        else:
            antwort = html_seite()
            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: text/html\r\n")
            client.send("Connection: close\r\n\r\n")
            client.send(antwort)

        client.close()


# -----------------------------
# Start
# -----------------------------
ip = wlan_verbinden()
print("Aufrufen im Browser:")
print("http://" + ip)

http_server()