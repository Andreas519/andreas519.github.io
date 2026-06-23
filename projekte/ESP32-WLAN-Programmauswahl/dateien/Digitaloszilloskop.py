from machine import Pin
import time, network, socket

# -----------------------------
# 8 digitale Eingänge
# -----------------------------
pin_list = [16, 17, 18, 19, 23, 25, 26, 27]
pins=[]
for pin in pin_list:
     pins.append(Pin(pin, Pin.IN))

# Speicher für Messwerte
samples = []
sample_count = 1000
sample_delay_us = 100   # 100 µs = 10 kHz Abtastrate ungefähr
channel_names = [
    "TRIGGER",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7"
]

def read_8bit():
    value = 0
    for i, p in enumerate(pins):
        if p.value():
            value |= (1 << i)
    return value


def capture():
    #print("capture")
    #print(make_html())
    global samples
    samples = []

    for i in range(sample_count):
        samples.append(read_8bit())
        time.sleep_us(sample_delay_us)



def make_html():
    data = ",".join(str(v) for v in samples)
    channel_names_js = ",".join('"' + name + '"' for name in channel_names)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 8-Kanal Speicheroszi</title>
<style>
body {{
    text-align: center;
    font-family: Arial, sans-serif;
}}
</style>
</head>

<body>

<h1>ESP32 8-Kanal Speicheroszilloskop</h1>
<p>Aktuelle Uhrzeit:<span id="clock"></span></p>

<script>
function updateClock() {{
    const now = new Date();
    document.getElementById("clock").innerHTML =
        now.toLocaleTimeString();
}}

updateClock();
setInterval(updateClock, 1000);
</script>

<canvas id="canvas" width="1000" height="400" style="border:1px solid black;"></canvas>
<div>
<p><button onclick="location.href='/capture'">Messung erneut starten</button></p>
</div>
<script>
    let data = [{data}];
    let channel_names = [{channel_names_js}];
    
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const w = canvas.width;
    const h = canvas.height;
    const channels = 8;
    const chHeight = h / channels;

    ctx.clearRect(0, 0, w, h);
    ctx.font = "12px Arial";
    const leftMargin = 60;

    
    for (let ch = 0; ch < channels; ch++) {{
        let y0 = ch * chHeight + chHeight / 2;
        ctx.fillText(channel_names[ch], 5, y0 - 8);

        ctx.beginPath();

        for (let i = 0; i < data.length; i++) {{
            let bit = (data[i] >> ch) & 1;
            let x = leftMargin +  i * (w - leftMargin - 10) / data.length;
            
            let y = y0 - bit * 15;

            if (i == 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}

        ctx.stroke();
    }}
</script>

</body>
</html>"""
    return html


def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # wegen OSError: [Errno 112] EADDRINUSE
    s.bind(addr)
    s.listen(1)
    print("Webserver läuft auf Port 80")
    while True:
        print("_", end="")
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        if "GET /capture" in request:
            print("Messung startet...")
            capture()
            print("Messung fertig")

        html = make_html()
        cl.send("HTTP/1.1 200 OK\r\n")
        cl.send("Content-Type: text/html\r\n")
        cl.send("Connection: close\r\n\r\n")
        cl.sendall(html.encode())
        cl.close()

