/*
  ESP32 WLAN-Speicheroszilloskop
  --------------------------------
  - 2 analoge Eingänge
  - Triggerfunktion
  - Datenübertragung per WLAN
  - grafische Darstellung im Browser
  - Buttonstatus: "Messung läuft ..."
  - Onboard-LED als Statusanzeige
  - Verbindungsanzeige per /ping

  Status-LED:
  - bereit: 0,25 Hz, also 2 s EIN / 2 s AUS
  - Messung läuft: dauerhaft EIN

  Standardpins:
  Kanal 1: GPIO34 / ADC1
  Kanal 2: GPIO35 / ADC1

  Browser:
  http://192.168.4.1
*/

#include <WiFi.h>
#include <WebServer.h>

// ------------------------------------------------------------
// WLAN Access Point
// ------------------------------------------------------------
const char* ssid = "ESP32-Oszilloskop";
const char* password = "12345678";   // mindestens 8 Zeichen

WebServer server(80);

// ------------------------------------------------------------
// Hardware
// ------------------------------------------------------------
const int LED_PIN = 2;

const int CH1_PIN = 34;   // ADC1, Eingang
const int CH2_PIN = 35;   // ADC1, Eingang

// ------------------------------------------------------------
// Status-LED
// ------------------------------------------------------------
bool measurementRunning = false;
unsigned long lastBlinkMillis = 0;
bool ledState = false;

const unsigned long READY_BLINK_INTERVAL_MS = 2000;
// 2000 ms EIN + 2000 ms AUS = 4 s Periodendauer = 0,25 Hz

// ------------------------------------------------------------
// Messspeicher
// ------------------------------------------------------------
const int MAX_SAMPLES = 2000;

uint16_t ch1Values[MAX_SAMPLES];
uint16_t ch2Values[MAX_SAMPLES];
uint32_t timeValues[MAX_SAMPLES];

int lastSampleCount = 0;
uint32_t lastCaptureTime_us = 0;
bool lastTriggered = false;

// ------------------------------------------------------------
// HTML-Seite
// ------------------------------------------------------------
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ESP32 Speicheroszilloskop</title>
<style>
  :root {
    --bg: #f4f7fb;
    --card: #ffffff;
    --text: #1f2933;
    --muted: #5f6c7b;
    --accent: #2563eb;
    --accent-dark: #1e40af;
    --border: #d8dee9;
  }

  body {
    font-family: Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 0;
  }

  header {
    background: linear-gradient(135deg, #1e40af, #2563eb);
    color: white;
    padding: 24px;
    text-align: center;
  }

  header h1 {
    margin: 0 0 8px 0;
  }

  header p {
    margin: 0;
  }

  main {
    max-width: 1100px;
    margin: 20px auto;
    padding: 0 16px;
  }

  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }

  .top-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
  }

  .connection-box {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: bold;
    border: 1px solid #ccc;
  }

  .connection-box.connected {
    background: #dcfce7;
    color: #166534;
    border-color: #86efac;
  }

  .connection-box.disconnected {
    background: #fee2e2;
    color: #991b1b;
    border-color: #fca5a5;
  }

  .connection-box.checking {
    background: #fef9c3;
    color: #854d0e;
    border-color: #fde047;
  }

  .small-info {
    color: var(--muted);
    font-size: 0.9rem;
  }

  .controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    align-items: end;
  }

  label {
    display: block;
    font-size: 0.9rem;
    color: var(--muted);
    margin-bottom: 4px;
  }

  input, select, button {
    width: 100%;
    box-sizing: border-box;
    padding: 8px;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
  }

  button {
    background: var(--accent);
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
  }

  button:hover:not(:disabled) {
    background: var(--accent-dark);
  }

  button:disabled {
    background: #64748b;
    cursor: wait;
  }

  canvas {
    width: 100%;
    height: 480px;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 10px;
  }

  .status {
    font-family: Consolas, monospace;
    background: #f8fafc;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    white-space: pre-wrap;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 8px;
    font-weight: bold;
  }

  .ch1 { color: #2563eb; }
  .ch2 { color: #dc2626; }
  .trig { color: #16a34a; }
</style>
</head>
<body>

<header>
  <h1>ESP32 2-Kanal Speicheroszilloskop</h1>
  <p>WLAN · Trigger · grafische Darstellung · Verbindungsanzeige</p>
</header>

<main>

<div class="card">
  <div class="top-row">
    <div id="connectionBox" class="connection-box disconnected">
      Verbindung: getrennt
    </div>
    <div id="lastPingInfo" class="small-info">
      Letzte Antwort: -
    </div>
  </div>
</div>

<div class="card">
  <div class="controls">
    <div>
      <label>Anzahl Messpunkte</label>
      <input id="samples" type="number" min="50" max="2000" value="800">
    </div>

    <div>
      <label>Abtastintervall in µs</label>
      <input id="interval" type="number" min="100" max="1000000" value="500">
    </div>

    <div>
      <label>Triggerkanal</label>
      <select id="trigCh">
        <option value="0">kein Trigger</option>
        <option value="1">Kanal 1</option>
        <option value="2">Kanal 2</option>
      </select>
    </div>

    <div>
      <label>Triggerflanke</label>
      <select id="edge">
        <option value="rising">steigend</option>
        <option value="falling">fallend</option>
      </select>
    </div>

    <div>
      <label>Triggerlevel ADC 0...4095</label>
      <input id="level" type="number" min="0" max="4095" value="2000">
    </div>

    <div>
      <label>Trigger-Timeout in ms</label>
      <input id="timeout" type="number" min="10" max="10000" value="2000">
    </div>

    <div>
      <button id="startButton" onclick="startCapture()">Messung starten</button>
    </div>
  </div>
</div>

<div class="card">
  <canvas id="scope" width="1000" height="480"></canvas>
  <div class="legend">
    <span class="ch1">Kanal 1</span>
    <span class="ch2">Kanal 2</span>
    <span class="trig">Triggerlevel</span>
  </div>
</div>

<div class="card">
  <div id="status" class="status">Bereit.</div>
</div>

</main>

<script>
const canvas = document.getElementById("scope");
const ctx = canvas.getContext("2d");

let failedPings = 0;
let measurementActiveInBrowser = false;

function getTimeString() {
  const now = new Date();
  return now.toLocaleTimeString("de-DE");
}

function drawGrid() {
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  ctx.strokeStyle = "#e5e7eb";
  ctx.lineWidth = 1;

  for (let x = 0; x <= w; x += w / 10) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }

  for (let y = 0; y <= h; y += h / 8) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  ctx.strokeStyle = "#9ca3af";
  ctx.beginPath();
  ctx.moveTo(0, h / 2);
  ctx.lineTo(w, h / 2);
  ctx.stroke();
}

function drawSignal(values, color) {
  const w = canvas.width;
  const h = canvas.height;

  if (!values || values.length < 2) return;

  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();

  for (let i = 0; i < values.length; i++) {
    const x = i * w / (values.length - 1);
    const y = h - (values[i] / 4095.0) * h;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }

  ctx.stroke();
}

function drawTriggerLevel(level) {
  const w = canvas.width;
  const h = canvas.height;
  const y = h - (level / 4095.0) * h;

  ctx.strokeStyle = "#16a34a";
  ctx.lineWidth = 1;
  ctx.setLineDash([8, 6]);

  ctx.beginPath();
  ctx.moveTo(0, y);
  ctx.lineTo(w, y);
  ctx.stroke();

  ctx.setLineDash([]);
}

function drawData(data) {
  drawGrid();

  const level = Number(document.getElementById("level").value);
  drawTriggerLevel(level);

  drawSignal(data.ch1, "#2563eb");
  drawSignal(data.ch2, "#dc2626");
}

async function checkConnection() {
  const box = document.getElementById("connectionBox");
  const info = document.getElementById("lastPingInfo");

  try {
    const response = await fetch("/ping", { cache: "no-store" });

    if (!response.ok) {
      throw new Error("Ping fehlgeschlagen");
    }

    const text = await response.text();

    if (text.trim() !== "OK") {
      throw new Error("Falsche Antwort");
    }

    failedPings = 0;
    box.textContent = "Verbindung: verbunden ✓";
    box.className = "connection-box connected";
    info.textContent = "Letzte Antwort: " + getTimeString();

  } catch (err) {
    failedPings++;

    if (measurementActiveInBrowser || failedPings < 4) {
      box.textContent = "Verbindung: wartet ...";
      box.className = "connection-box checking";
      info.textContent = "Letzte Antwort: wartet auf ESP";
    } else {
      box.textContent = "Verbindung: getrennt ✗";
      box.className = "connection-box disconnected";
      info.textContent = "Letzte Antwort: keine aktuelle Antwort";
    }
  }
}

async function startCapture() {
  const startButton = document.getElementById("startButton");
  const status = document.getElementById("status");

  measurementActiveInBrowser = true;
  startButton.textContent = "Messung läuft ...";
  startButton.disabled = true;
  status.textContent = "Messung läuft ...";

  const samples = document.getElementById("samples").value;
  const interval = document.getElementById("interval").value;
  const trigCh = document.getElementById("trigCh").value;
  const edge = document.getElementById("edge").value;
  const level = document.getElementById("level").value;
  const timeout = document.getElementById("timeout").value;

  const url = `/data?samples=${samples}&interval=${interval}&trigCh=${trigCh}&edge=${edge}&level=${level}&timeout=${timeout}`;

  try {
    const response = await fetch(url, { cache: "no-store" });
    const data = await response.json();

    drawData(data);

    const duration_ms = data.captureTime_us / 1000.0;

    status.textContent =
      "Messung beendet\n" +
      "Messpunkte: " + data.samples + "\n" +
      "Abtastintervall Soll: " + data.interval_us + " µs\n" +
      "Aufnahmedauer Ist: " + data.captureTime_us + " µs (" + duration_ms.toFixed(2) + " ms)\n" +
      "Trigger ausgelöst: " + (data.triggered ? "ja" : "nein / Timeout") + "\n" +
      "Triggerkanal: " + data.trigCh + "\n" +
      "Triggerflanke: " + data.edge + "\n" +
      "Triggerlevel: " + data.level + "\n" +
      "ADC-Bereich: 0 ... 4095";

  } catch (err) {
    status.textContent = "Fehler beim Abrufen der Daten:\n" + err;
  }

  measurementActiveInBrowser = false;
  startButton.textContent = "Messung starten";
  startButton.disabled = false;
  checkConnection();
}

drawGrid();
checkConnection();
setInterval(checkConnection, 1000);
</script>

</body>
</html>
)rawliteral";

// ------------------------------------------------------------
// Status-LED aktualisieren
// ------------------------------------------------------------
void updateStatusLed() {
  if (measurementRunning) {
    digitalWrite(LED_PIN, HIGH);   // Messung läuft: LED dauerhaft EIN
    return;
  }

  unsigned long now = millis();

  if (now - lastBlinkMillis >= READY_BLINK_INTERVAL_MS) {
    lastBlinkMillis = now;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  }
}

// ------------------------------------------------------------
// Hilfsfunktionen
// ------------------------------------------------------------
int readTriggerPin(int trigCh) {
  if (trigCh == 1) return analogRead(CH1_PIN);
  if (trigCh == 2) return analogRead(CH2_PIN);
  return 0;
}

bool triggerDetected(int oldValue, int newValue, int level, String edge) {
  if (edge == "rising") {
    return oldValue < level && newValue >= level;
  }

  if (edge == "falling") {
    return oldValue > level && newValue <= level;
  }

  return true;
}

// ------------------------------------------------------------
// Messung durchführen
// ------------------------------------------------------------
void captureData(int samples, int interval_us, int trigCh, int level, String edge, int timeout_ms) {
  measurementRunning = true;
  digitalWrite(LED_PIN, HIGH);   // Messung läuft: LED EIN

  samples = constrain(samples, 50, MAX_SAMPLES);
  interval_us = constrain(interval_us, 100, 1000000);
  timeout_ms = constrain(timeout_ms, 10, 10000);

  lastSampleCount = samples;
  lastTriggered = false;

  // ----------------------------------------------------------
  // Trigger suchen
  // ----------------------------------------------------------
  if (trigCh == 1 || trigCh == 2) {
    uint32_t startWait = millis();

    int oldValue = readTriggerPin(trigCh);

    while ((millis() - startWait) < (uint32_t)timeout_ms) {
      int newValue = readTriggerPin(trigCh);

      if (triggerDetected(oldValue, newValue, level, edge)) {
        lastTriggered = true;
        break;
      }

      oldValue = newValue;
      delayMicroseconds(50);
    }
  } else {
    lastTriggered = true;
  }

  // ----------------------------------------------------------
  // Daten aufnehmen
  // ----------------------------------------------------------
  uint32_t t0 = micros();

  for (int i = 0; i < samples; i++) {
    timeValues[i] = micros() - t0;
    ch1Values[i] = analogRead(CH1_PIN);
    ch2Values[i] = analogRead(CH2_PIN);

    delayMicroseconds(interval_us);
  }

  lastCaptureTime_us = micros() - t0;

  measurementRunning = false;
  ledState = false;
  lastBlinkMillis = millis();
  digitalWrite(LED_PIN, LOW);
}

// ------------------------------------------------------------
// JSON-Daten senden
// ------------------------------------------------------------
void sendDataAsJson(int samples, int interval_us, int trigCh, int level, String edge) {
  server.setContentLength(CONTENT_LENGTH_UNKNOWN);
  server.send(200, "application/json", "");

  server.sendContent("{");

  server.sendContent("\"samples\":");
  server.sendContent(String(samples));
  server.sendContent(",");

  server.sendContent("\"interval_us\":");
  server.sendContent(String(interval_us));
  server.sendContent(",");

  server.sendContent("\"captureTime_us\":");
  server.sendContent(String(lastCaptureTime_us));
  server.sendContent(",");

  server.sendContent("\"triggered\":");
  server.sendContent(lastTriggered ? "true" : "false");
  server.sendContent(",");

  server.sendContent("\"trigCh\":");
  server.sendContent(String(trigCh));
  server.sendContent(",");

  server.sendContent("\"level\":");
  server.sendContent(String(level));
  server.sendContent(",");

  server.sendContent("\"edge\":\"");
  server.sendContent(edge);
  server.sendContent("\",");

  server.sendContent("\"time\":[");
  for (int i = 0; i < samples; i++) {
    if (i > 0) server.sendContent(",");
    server.sendContent(String(timeValues[i]));
  }
  server.sendContent("],");

  server.sendContent("\"ch1\":[");
  for (int i = 0; i < samples; i++) {
    if (i > 0) server.sendContent(",");
    server.sendContent(String(ch1Values[i]));
  }
  server.sendContent("],");

  server.sendContent("\"ch2\":[");
  for (int i = 0; i < samples; i++) {
    if (i > 0) server.sendContent(",");
    server.sendContent(String(ch2Values[i]));
  }
  server.sendContent("]");

  server.sendContent("}");
}

// ------------------------------------------------------------
// Webserver-Routen
// ------------------------------------------------------------
void handleRoot() {
  server.send_P(200, "text/html", INDEX_HTML);
}

void handlePing() {
  server.send(200, "text/plain", "OK");
}

void handleData() {
  int samples = server.arg("samples").toInt();
  int interval_us = server.arg("interval").toInt();
  int trigCh = server.arg("trigCh").toInt();
  int level = server.arg("level").toInt();
  int timeout_ms = server.arg("timeout").toInt();
  String edge = server.arg("edge");

  if (samples <= 0) samples = 800;
  if (interval_us <= 0) interval_us = 500;
  if (level < 0 || level > 4095) level = 2000;
  if (timeout_ms <= 0) timeout_ms = 2000;
  if (edge != "rising" && edge != "falling") edge = "rising";

  samples = constrain(samples, 50, MAX_SAMPLES);

  captureData(samples, interval_us, trigCh, level, edge, timeout_ms);
  sendDataAsJson(samples, interval_us, trigCh, level, edge);
}

void handleNotFound() {
  server.send(404, "text/plain", "Nicht gefunden");
}

// ------------------------------------------------------------
// Setup
// ------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println();
  Serial.println("ESP32 WLAN-Speicheroszilloskop startet ...");

  analogReadResolution(12);

  // Fuer ESP32: ungefaehr Messbereich bis ca. 3,3 V
  analogSetPinAttenuation(CH1_PIN, ADC_11db);
  analogSetPinAttenuation(CH2_PIN, ADC_11db);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  IPAddress ip = WiFi.softAPIP();

  Serial.print("Access Point gestartet: ");
  Serial.println(ssid);

  Serial.print("IP-Adresse: ");
  Serial.println(ip);

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.on("/ping", handlePing);
  server.onNotFound(handleNotFound);

  server.begin();

  Serial.println("Webserver gestartet.");
  Serial.println("Browser oeffnen: http://192.168.4.1");
}

// ------------------------------------------------------------
// Loop
// ------------------------------------------------------------
void loop() {
  server.handleClient();
  updateStatusLed();
}
