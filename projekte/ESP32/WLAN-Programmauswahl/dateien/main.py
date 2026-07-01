import network
import socket
import time
import machine
import gc

import ADC_Messung
import Digitaloszilloskop
aktives_programm = ""
# ------------------------------------------------------------
# WLAN Access Point starten
# ------------------------------------------------------------

ssid = "ESP32-Datenlogger"
password = "12345678"   # mindestens 8 Zeichen

ap = network.WLAN(network.AP_IF)
ap.active(True)
#ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
ap.config(essid=ssid, authmode=network.AUTH_OPEN)

while not ap.active():
    time.sleep(0.1)

print("Access Point aktiv")
print(ap.ifconfig())


# ------------------------------------------------------------
# Beispiel-Programme / Funktionen
# ------------------------------------------------------------

def programm_blinken():
    print("Programm BLINKEN wurde gestartet")

    led = machine.Pin(2, machine.Pin.OUT)

    for i in range(10):
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)

    print("Programm BLINKEN beendet")


def programm_test():
    print("Programm TEST wurde gestartet")

    for i in range(5):
        print("Testlauf:", i)
        time.sleep(0.5)

    print("Programm TEST beendet")


def programm_messung():
    print("Programm MESSUNG wurde gestartet")

    # Hier kommt später dein Messprogramm rein
    for i in range(10):
        print("Messwert:", i)
        time.sleep(0.3)

    print("Programm MESSUNG beendet")

    
def adc_json():
    werte, sample_us = ADC_Messung.messen()

    daten = ",".join(str(v) for v in werte)

    json_text = '{{"n":{},"sample_us":{},"werte":[{}]}}'.format(
        len(werte), sample_us, daten
    )

    return json_text

# ------------------------------------------------------------
# HTML-Seite
# ------------------------------------------------------------
def html_seite(meldung=""):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ESP32 Programmauswahl</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f0f0;
            margin: 40px;
        }}

        h1 {{
            color: #204060;
        }}

        .box {{
            background-color: white;
            padding: 25px;
            border-radius: 12px;
            display: inline-block;
            box-shadow: 0px 0px 12px #aaa;
        }}
        
        .buttonzeile {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        button {{
            width: 120px;
            height: 40px;
            margin: 10px;
            font-size: 14px;
            border-radius: 8px;
            border: none;
            background-color: #2d89ef;
            color: white;
            cursor: pointer;
        }}

        button:hover {{
            background-color: #1b5fa7;
        }}

        button.aktiv {{
            background-color: #003b7a;
        }}

        .meldung {{
            margin-top: 20px;
            color: green;
            font-size: 18px;
        }}

        .uhr {{
            font-size: 22px;
            font-weight: bold;
            color: #204060;
            margin: 15px;
        }}

        canvas {{
            margin-top: 20px;
            border: 1px solid #999;
            background: white;
        }}
    </style>
</head>

<body>
    <div class="box">
        <h1>ESP32 Programmauswahl</h1>
        <div class="buttonzeile">
        <form action="/start" method="get">

                <button name="prog" value="blink">Blinkprogramm</button>
                <button name="prog" value="test">Testprogramm</button>
                <button name="prog" value="messung">Messung</button>
                <button name="prog" value="Digitaloszi">Digitaloszi</button>
                <button id="adc_button" type="button" onclick="adc_messung()">ADC-Messung</button>
        </form>
        </div>
        <div class="meldung">{meldung}</div>

        <div class="uhr">
            Uhrzeit: <span id="uhrzeit">--:--:--</span>
        </div>

        <p>Status: <span id="status">bereit</span></p>
        <p>N = <span id="anzahl">-</span> &nbsp;&nbsp; sample_us = <span id="sample_us">-</span></p>

        <canvas id="diagramm" width="800" height="300"></canvas>
    </div>

    <script>
        function uhr_aktualisieren() {{
            let jetzt = new Date();
            let h = String(jetzt.getHours()).padStart(2, "0");
            let m = String(jetzt.getMinutes()).padStart(2, "0");
            let s = String(jetzt.getSeconds()).padStart(2, "0");
            document.getElementById("uhrzeit").innerHTML = h + ":" + m + ":" + s;
        }}

        setInterval(uhr_aktualisieren, 1000);
        uhr_aktualisieren();

        async function adc_messung() {{
            let btn = document.getElementById("adc_button");
            btn.classList.add("aktiv");
            document.getElementById("status").innerHTML = "Messung läuft ...";

            try {{
                let response = await fetch("/adc");
                let daten = await response.json();

                document.getElementById("anzahl").innerHTML = daten.n;
                document.getElementById("sample_us").innerHTML = daten.sample_us.toFixed(2) + " µs";
                document.getElementById("status").innerHTML = "Messung fertig";

                zeichneDiagramm(daten.werte);
            }}
            catch(e) {{
                document.getElementById("status").innerHTML = "Fehler: " + e;
            }}

            btn.classList.remove("aktiv");
        }}

        function zeichneDiagramm(werte) {{
            let canvas = document.getElementById("diagramm");
            let ctx = canvas.getContext("2d");

            let w = canvas.width;
            let h = canvas.height;

            ctx.clearRect(0, 0, w, h);

            // Rand
            let links = 40;
            let rechts = 10;
            let oben = 10;
            let unten = 20;

            // Achsen
            ctx.beginPath();
            ctx.moveTo(links, oben);
            ctx.lineTo(links, h - unten);
            ctx.lineTo(w - rechts, h - unten);
            ctx.stroke();

            // ADC-Bereich 0..4095
            let ymin = 0;
            let ymax = 4095;

            if (werte.length < 2) return;

            ctx.beginPath();

            for (let i = 0; i < werte.length; i++) {{
                let x = links + i * (w - links - rechts) / (werte.length - 1);
                let y = oben + (ymax - werte[i]) * (h - oben - unten) / (ymax - ymin);

                if (i == 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }}

            ctx.strokeStyle = "blue";
            ctx.stroke();
        }}
    </script>
</body>
</html>
"""
    return html

# ------------------------------------------------------------
# Programm-Auswahl auswerten
# ------------------------------------------------------------

def starte_programm(prog):
    global aktives_programm

    aktives_programm = prog
    gc.collect()

    if prog == "blink":
        programm_blinken()
        return "Blinkprogramm wurde ausgeführt."

    elif prog == "test":
        programm_test()
        return "Testprogramm wurde ausgeführt."

    elif prog == "messung":
        programm_messung()
        return "Messprogramm wurde ausgeführt."
#     
#     elif prog == "ADC-Messung":
#         print("Starte 'Digitaloszilloskop.py'")
#         import Digitaloszilloskop
#         return "ADC-Messung wurde ausgeführt."

    elif prog == "Digitaloszi":
        print("Starte 'Digitaloszilloskop.py'")
        import Digitaloszilloskop
        return "Digitaloszi wir ausgeführt."

    else:
        return "Unbekanntes Programm."


# ------------------------------------------------------------
# Webserver
# ------------------------------------------------------------

def webserver():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Webserver läuft auf:")
    print("http://192.168.4.1")

    while True:
        conn, addr = s.accept()
        print("\nVerbindung von", addr)

        try:
            request = conn.recv(1024).decode()
#             suchtext = "Referer: "
#             pos = request.find(suchtext)
#             if pos != -1:
#                 start = pos + len(suchtext)
#                 ende = request.find("\n", start)
#                 referer = request[start:ende].strip()
#                 print(referer)
#             else:
#                 referer = ""
#                 print("Kein Referer gefunden")

            meldung = ""
            erste_zeile = request.split("\r\n")[0]
            print("Erste Zeile:", erste_zeile)

            if erste_zeile.startswith("GET /adc "):
                print("ADC-Messung wird ausgeführt")
                response = adc_json()

                conn.send("HTTP/1.1 200 OK\r\n")
                conn.send("Content-Type: application/json\r\n")
                conn.send("Connection: close\r\n")
                conn.send("\r\n")
                conn.sendall(response.encode())
                conn.close()
                continue
            # Beispiel:
            # GET /start?prog=blink HTTP/1.1
            if "GET /start?prog=" in request:
                start = request.find("GET /start?prog=") + len("GET /start?prog=")
                ende = request.find(" ", start)
                prog = request[start:ende]

                print("Gewähltes Programm:", prog)
                meldung = starte_programm(prog)

            response = html_seite(meldung)

            conn.send("HTTP/1.1 200 OK\r\n")
            conn.send("Content-Type: text/html; charset=utf-8\r\n")
            conn.send("Connection: close\r\n")
            conn.send("\r\n")
            conn.sendall(response.encode())

        except Exception as e:
            print("Fehler:", e)

        finally:
            conn.close()


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

webserver()