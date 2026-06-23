import network
import socket
import time
from machine import ADC, Pin

# ============================================================
# WLAN-Zugangsdaten
# ============================================================
SSID = "raspi";  PASSWORD = "abcd1234"
ADC_Pin = 4
# ============================================================
# ADC-Einstellung
# ============================================================
adc_pin = ADC(Pin(ADC_Pin))          # ADC-Pin, z.B. GPIO34
adc_pin.atten(ADC.ATTN_11DB)    # Bereich ungefähr 0...3,3 V
adc_pin.width(ADC.WIDTH_12BIT)  # Werte 0...4095

# ============================================================
# Messspeicher und Grundeinstellungen
# ============================================================
MAX_N = 2000                    # Sicherheitsgrenze
N = 300                         # Standard-Anzahl Messwerte
DT_US = 100                     # Standard-Messintervall in Mikrosekunden

TRIGGER_LEVEL = 2000
TRIGGER_MODE = "none"           # none, rising, falling
TRIGGER_TIMEOUT_MS = 5000       # maximal 5 Sekunden auf Trigger warten

werte = [0] * N


# ============================================================
# WLAN verbinden
# ============================================================
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


# ============================================================
# einfache URL-Decodierung
# ============================================================
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


# ============================================================
# Query-Parameter aus URL holen
# Beispiel:
# /messen?n=500&dt=100&trig=2000&mode=rising
# ============================================================
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


# ============================================================
# Warten auf Trigger
# ============================================================
def warten_auf_trigger(trigger_level, trigger_mode, timeout_ms):
    if trigger_mode == "none":
        return True, adc_pin.read()

    print("Warte auf Flankentrigger ...")
    print("Triggerlevel:", trigger_level)
    print("Triggermodus:", trigger_mode)

    start = time.ticks_ms()

    # --------------------------------------------------------
    # Steigende Flanke:
    # 1. erst warten, bis Signal UNTER Triggerlevel ist
    # 2. dann warten, bis Signal Triggerlevel UEBERSCHREITET
    # --------------------------------------------------------
    if trigger_mode == "rising":
        print("Phase 1: Warte auf ADC < Triggerlevel")

        while True:
            wert = adc_pin.read()

            if wert < trigger_level:
                print("Signal ist unter Triggerlevel:", wert)
                break

            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Trigger-Timeout in Phase 1")
                return False, wert

        print("Phase 2: Warte auf steigende Flanke")

        while True:
            wert = adc_pin.read()

            if wert >= trigger_level:
                print("Steigende Flanke ausgeloest:", wert)
                return True, wert

            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Trigger-Timeout in Phase 2")
                return False, wert

    # --------------------------------------------------------
    # Fallende Flanke:
    # 1. erst warten, bis Signal UEBER Triggerlevel ist
    # 2. dann warten, bis Signal Triggerlevel UNTERSCHREITET
    # --------------------------------------------------------
    elif trigger_mode == "falling":
        print("Phase 1: Warte auf ADC > Triggerlevel")

        while True:
            wert = adc_pin.read()

            if wert > trigger_level:
                print("Signal ist ueber Triggerlevel:", wert)
                break

            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Trigger-Timeout in Phase 1")
                return False, wert

        print("Phase 2: Warte auf fallende Flanke")

        while True:
            wert = adc_pin.read()

            if wert <= trigger_level:
                print("Fallende Flanke ausgeloest:", wert)
                return True, wert

            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                print("Trigger-Timeout in Phase 2")
                return False, wert

    else:
        return True, adc_pin.read()


# ============================================================
# Messung durchführen
# ============================================================
def messen(anzahl, dt_us, trigger_level, trigger_mode):
    global N, DT_US, werte
    global TRIGGER_LEVEL, TRIGGER_MODE

    # Grenzen prüfen
    if anzahl < 1:
        anzahl = 1

    if anzahl > MAX_N:
        anzahl = MAX_N

    if dt_us < 0:
        dt_us = 0

    if trigger_level < 0:
        trigger_level = 0

    if trigger_level > 4095:
        trigger_level = 4095

    if trigger_mode not in ("none", "rising", "falling"):
        trigger_mode = "none"

    # globale Werte aktualisieren
    N = anzahl
    DT_US = dt_us
    TRIGGER_LEVEL = trigger_level
    TRIGGER_MODE = trigger_mode

    # Speicher neu anlegen
    werte = [0] * N

    print("Messung vorbereitet")
    print("N =", N)
    print("dt_us =", DT_US)
    print("Triggerlevel =", TRIGGER_LEVEL)
    print("Triggermodus =", TRIGGER_MODE)

    # auf Trigger warten
    ok, trigger_wert = warten_auf_trigger(
        TRIGGER_LEVEL,
        TRIGGER_MODE,
        TRIGGER_TIMEOUT_MS
    )

    if not ok:
        return False, 0, trigger_wert

    print("Messung startet")

    t_start = time.ticks_us()

    if DT_US == 0:
        # so schnell wie möglich messen
        for i in range(N):
            werte[i] = adc_pin.read()

    else:
        # Messung mit Zeitraster
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

    return True, messzeit_us, trigger_wert


# ============================================================
# HTML-Seite
# ============================================================
def html_seite():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 Web-Speicheroszi V4</title>

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
        max-width: 1050px;
        box-shadow: 0px 0px 8px #aaa;
    }

    h1 {
        margin-top: 0;
    }

    label {
        font-size: 18px;
        margin-right: 8px;
    }

    input, select {
        font-size: 18px;
        padding: 6px;
        margin-right: 15px;
    }

    input {
        width: 130px;
    }

    select {
        width: 190px;
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

    .hinweis {
        color: #555;
        font-size: 15px;
    }
</style>
</head>

<body>
<div class="box">
    <h1>ESP32 Web-Speicheroszi V4</h1>

    <p>
        <label>Anzahl Messwerte:</label>
        <input id="anzahl" type="number" value="300" min="1" max="2000">

        <label>Intervall in us:</label>
        <input id="intervall" type="number" value="100" min="0" max="1000000">
    </p>

    <p>
        <label>Triggerlevel:</label>
        <input id="triggerlevel" type="number" value="2000" min="0" max="4095">

        <label>Triggerart:</label>
        <select id="triggermode">
            <option value="none">kein Trigger</option>
            <option value="rising">steigende Flanke</option>
            <option value="falling">fallende Flanke</option>
        </select>
    </p>

    <p class="hinweis">
        ADC-Bereich: 0 bis 4095.
        Steigende Flanke: erst ADC &lt; Triggerlevel, dann ADC &gt;= Triggerlevel.
        Fallende Flanke: erst ADC &gt; Triggerlevel, dann ADC &lt;= Triggerlevel.
    </p>

    <button onclick="messenUndZeichnen()">Messung starten</button>
    <button onclick="csvAnzeigen()">CSV anzeigen</button>
    <button onclick="diagrammLoeschen()">Diagramm loeschen</button>

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
    let trig = document.getElementById("triggerlevel").value;
    let mode = document.getElementById("triggermode").value;

    document.getElementById("status").textContent = "Warte auf Trigger / Messung laeuft ...";
    document.getElementById("csv").value = "";

    try {
        let url = "/messen?n=" + encodeURIComponent(n)
                + "&dt=" + encodeURIComponent(dt)
                + "&trig=" + encodeURIComponent(trig)
                + "&mode=" + encodeURIComponent(mode);

        let r1 = await fetch(url);
        let antwort = await r1.text();

        document.getElementById("status").textContent = antwort;

        if (antwort.startsWith("Kein Trigger")) {
            return;
        }

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

    ctx.fillText(t_min + " us", left - 10, h - 15);
    ctx.fillText(t_max + " us", w - right - 80, h - 15);

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
    ctx.fillText("Messdauer: " + dauer_us + " us = " + dauer_ms.toFixed(3) + " ms", left + 320, 18);
}


function diagrammLoeschen() {
    const canvas = document.getElementById("plot");
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById("status").textContent = "Diagramm geloescht";
}
</script>

</body>
</html>
"""


# ============================================================
# HTTP-Antwort senden
# ============================================================
def sende_antwort(client, content, content_type="text/plain; charset=utf-8"):
    header = "HTTP/1.1 200 OK\r\n"
    header += "Content-Type: " + content_type + "\r\n"
    header += "Connection: close\r\n\r\n"

    client.send(header.encode("utf-8"))

    if isinstance(content, str):
        client.send(content.encode("utf-8"))
    else:
        client.send(content)


# ============================================================
# CSV-Werte zeilenweise senden
# wichtig: kein riesiger String im ESP-RAM
# ============================================================
def sende_werte_csv(client):
    header = "HTTP/1.1 200 OK\r\n"
    header += "Content-Type: text/plain; charset=utf-8\r\n"
    header += "Connection: close\r\n\r\n"

    client.send(header.encode("utf-8"))

    for i in range(N):
        if DT_US == 0:
            zeit = i
        else:
            zeit = i * DT_US

        zeile = str(zeit) + ";" + str(werte[i]) + "\n"
        client.send(zeile.encode("utf-8"))


# ============================================================
# Webserver
# ============================================================
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

            # ------------------------------------------------
            # Messung starten
            # Beispiel:
            # /messen?n=500&dt=100&trig=2000&mode=rising
            # ------------------------------------------------
            if pfad.startswith("/messen"):
                n_text = hole_parameter(pfad, "n")
                dt_text = hole_parameter(pfad, "dt")
                trig_text = hole_parameter(pfad, "trig")
                mode_text = hole_parameter(pfad, "mode")

                try:
                    anzahl = int(n_text)
                except:
                    anzahl = N

                try:
                    dt_us = int(dt_text)
                except:
                    dt_us = DT_US

                try:
                    trigger_level = int(trig_text)
                except:
                    trigger_level = TRIGGER_LEVEL

                if mode_text is None:
                    trigger_mode = "none"
                else:
                    trigger_mode = mode_text

                ok, messzeit_us, trigger_wert = messen(
                    anzahl,
                    dt_us,
                    trigger_level,
                    trigger_mode
                )

                if ok:
                    antwort = "Messung abgeschlossen: "
                    antwort += str(N) + " Werte, "
                    antwort += "Intervall " + str(DT_US) + " us, "
                    antwort += "Triggerwert " + str(trigger_wert) + ", "
                    antwort += "reale Messzeit " + str(messzeit_us) + " us"
                else:
                    antwort = "Kein Trigger innerhalb von "
                    antwort += str(TRIGGER_TIMEOUT_MS)
                    antwort += " ms. Letzter ADC-Wert: "
                    antwort += str(trigger_wert)

                sende_antwort(client, antwort)

            # ------------------------------------------------
            # Messwerte senden
            # ------------------------------------------------
            elif pfad.startswith("/werte"):
                sende_werte_csv(client)

            # ------------------------------------------------
            # Hauptseite senden
            # ------------------------------------------------
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


# ============================================================
# Start
# ============================================================
webserver_starten()