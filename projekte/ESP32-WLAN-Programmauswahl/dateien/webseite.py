# webseite.py

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

        <form class="buttonzeile" action="/start" method="get">
            <button name="prog" value="blink">Blinkprogramm</button>
            <button name="prog" value="test">Testprogramm</button>
            <button name="prog" value="messung">Messung</button>
            <button name="prog" value="Digitaloszi">Digitaloszi</button>
            <button id="adc_button" type="button" onclick="adc_messung()">ADC-Messung</button>
        </form>

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

            let links = 40;
            let rechts = 10;
            let oben = 10;
            let unten = 20;

            ctx.beginPath();
            ctx.moveTo(links, oben);
            ctx.lineTo(links, h - unten);
            ctx.lineTo(w - rechts, h - unten);
            ctx.stroke();

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