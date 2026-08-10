#include <Arduino.h>
#include <BLE2902.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include "esp_camera.h"
#include <Preferences.h>
#include <WiFi.h>

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"
#include "scheduled_capture.h"

#if __has_include("wifi_secrets.h")
#include "wifi_secrets.h"
#else
#define INITIAL_WIFI_NETWORKS { "", "" }
#endif

const char *PROGRAM_VERSION = "0.9.3";
// GPIO 13 is available as long as the SD card interface is not used.
const int TASTER = 13;
const char *BLUETOOTH_NAME = "ESP32-CAM-Setup";
const char *ACCESS_POINT_PREFIX = "ESP32-CAM-Setup";
const char *ACCESS_POINT_PASSWORD = "esp32cam";
const uint8_t MAX_WIFI_NETWORKS = 8;
const unsigned long WIFI_DISCONNECT_RESTART_MS = 30000;
const uint8_t STATUS_LED_BRIGHTNESS = 2;

struct WifiCredential {
  String ssid;
  String password;
};

const WifiCredential initialWifiNetworks[] = { INITIAL_WIFI_NETWORKS };
const size_t initialWifiNetworkCount = sizeof(initialWifiNetworks) / sizeof(initialWifiNetworks[0]);

const char *BLE_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
const char *BLE_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
const char *BLE_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

BLEServer *bleServer = nullptr;
BLECharacteristic *bleTxCharacteristic = nullptr;
bool bleConnected = false;
bool bleRestartAdvertising = false;
WifiCredential wifiNetworks[MAX_WIFI_NETWORKS];
uint8_t wifiNetworkCount = 0;
String bluetoothInput;
String pendingBluetoothCommand;
bool bluetoothCommandReady = false;
bool cameraServerStarted = false;
bool bluetoothModeActive = false;
bool accessPointModeActive = false;
bool stationModeActive = false;
String accessPointName;
IPAddress configuredAccessPointIp(192, 168, 4, 1);
uint8_t statusLedPhase = 0;
unsigned long nextStatusLedChange = 0;
unsigned long wifiDisconnectedSince = 0;

void startCameraServer();
void setupLedFlash();
void loadWifiNetworks();
void saveWifiNetworks();
bool connectToKnownWifi(String preferredSsid = "");
void setupBluetoothDialog();
void handleBluetoothDialog();
void executeBluetoothCommand(String command);
bool startConfigurationAccessPoint();
bool configureAccessPointIp(const String &value, bool saveConfiguration);

bool isValidPrivateAccessPointIp(const IPAddress &address) {
  bool privateRange = address[0] == 10
    || (address[0] == 172 && address[1] >= 16 && address[1] <= 31)
    || (address[0] == 192 && address[1] == 168);
  return privateRange && address[3] > 0 && address[3] < 255;
}

bool configureAccessPointIp(const String &value, bool saveConfiguration) {
  IPAddress parsed;
  if (!parsed.fromString(value) || !isValidPrivateAccessPointIp(parsed)) {
    return false;
  }
  configuredAccessPointIp = parsed;
  if (saveConfiguration) {
    Preferences preferences;
    preferences.begin("ap-config", false);
    preferences.putString("ip", configuredAccessPointIp.toString());
    preferences.end();
  }
  return true;
}

void loadAccessPointIp() {
  Preferences preferences;
  preferences.begin("ap-config", true);
  String storedIp = preferences.getString("ip", "192.168.4.1");
  preferences.end();
  if (!configureAccessPointIp(storedIp, false)) {
    configuredAccessPointIp = IPAddress(192, 168, 4, 1);
  }
}

void saveWifiForNextBoot(const String &ssid) {
  Preferences preferences;
  preferences.begin("device-mode", false);
  preferences.putString("next-wifi", ssid);
  preferences.end();
}

String takeWifiForNextBoot() {
  Preferences preferences;
  preferences.begin("device-mode", false);
  String ssid = preferences.getString("next-wifi", "");
  preferences.remove("next-wifi");
  preferences.end();
  return ssid;
}

String takeModeRequest() {
  Preferences preferences;
  preferences.begin("device-mode", false);
  String requestedMode = preferences.getString("next-mode", "");
  if (requestedMode.isEmpty() && preferences.getBool("ble-next", false)) {
    requestedMode = "ble";
  }
  preferences.remove("next-mode");
  preferences.remove("ble-next");
  preferences.end();
  return requestedMode;
}

void saveModeForNextBoot(const String &mode) {
  Preferences preferences;
  preferences.begin("device-mode", false);
  preferences.putString("next-mode", mode);
  preferences.end();
}

void updateStatusLed() {
  if ((!bluetoothModeActive && !accessPointModeActive)
      || static_cast<long>(millis() - nextStatusLedChange) < 0) {
    return;
  }

  if (bluetoothModeActive) {
    bool ledOn = statusLedPhase == 0;
    ledcWrite(LED_GPIO_NUM, ledOn ? STATUS_LED_BRIGHTNESS : 0);
    nextStatusLedChange = millis() + (ledOn ? 20 : 2000);
    statusLedPhase = ledOn ? 1 : 0;
    return;
  }

  // Access Point: two short flashes followed by a long pause.
  static const uint16_t phaseDuration[] = { 100, 150, 100, 1650 };
  bool ledOn = statusLedPhase == 0 || statusLedPhase == 2;
  ledcWrite(LED_GPIO_NUM, ledOn ? STATUS_LED_BRIGHTNESS : 0);
  nextStatusLedChange = millis() + phaseDuration[statusLedPhase];
  statusLedPhase = (statusLedPhase + 1) % 4;
}

void handleWifiConnection() {
  if (!stationModeActive) {
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    wifiDisconnectedSince = 0;
    return;
  }

  if (wifiDisconnectedSince == 0) {
    wifiDisconnectedSince = millis();
    Serial.println("WiFi connection lost; waiting 30 seconds for reconnection");
    return;
  }

  if (millis() - wifiDisconnectedSince >= WIFI_DISCONNECT_RESTART_MS) {
    Serial.println("WiFi still unavailable; restarting for access-point fallback");
    ledcWrite(LED_GPIO_NUM, 0);
    delay(100);
    ESP.restart();
  }
}

void sendBluetoothLine(const String &text) {
  Serial.println("BT: " + text);
  if (!bleConnected || bleTxCharacteristic == nullptr) {
    return;
  }

  String output = text + "\n";
  for (size_t offset = 0; offset < output.length(); offset += 20) {
    String part = output.substring(offset, min(offset + 20, output.length()));
    bleTxCharacteristic->setValue(part.c_str());
    bleTxCharacteristic->notify();
    delay(8);
  }
}

class CameraBleServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override {
    bleConnected = true;
    Serial.println("BLE client connected");
  }

  void onDisconnect(BLEServer *server) override {
    bleConnected = false;
    bleRestartAdvertising = true;
    Serial.println("BLE client disconnected");
  }
};

class CameraBleReceiveCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) override {
    String value = characteristic->getValue();
    for (size_t i = 0; i < value.length(); i++) {
      char character = value[i];
      if (character == '\n' || character == '\r') {
        if (!bluetoothInput.isEmpty() && !bluetoothCommandReady) {
          pendingBluetoothCommand = bluetoothInput;
          bluetoothInput = "";
          bluetoothCommandReady = true;
        }
      } else if (bluetoothInput.length() < 160) {
        bluetoothInput += character;
      }
    }
  }
};

void setupBluetoothDialog() {
  BLEDevice::init(BLUETOOTH_NAME);
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new CameraBleServerCallbacks());

  BLEService *service = bleServer->createService(BLE_SERVICE_UUID);
  bleTxCharacteristic = service->createCharacteristic(BLE_TX_UUID, BLECharacteristic::PROPERTY_NOTIFY);
  bleTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic *rxCharacteristic = service->createCharacteristic(
    BLE_RX_UUID,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
  );
  rxCharacteristic->setCallbacks(new CameraBleReceiveCallbacks());

  service->start();
  bleServer->getAdvertising()->start();
}

void loadWifiNetworks() {
  Preferences preferences;
  preferences.begin("wifi-config", false);

  if (!preferences.getBool("initialized", false)) {
    preferences.putBool("initialized", true);
    preferences.putUChar("count", 0);
  }

  wifiNetworkCount = min(preferences.getUChar("count", 0), MAX_WIFI_NETWORKS);
  for (uint8_t i = 0; i < wifiNetworkCount; i++) {
    wifiNetworks[i].ssid = preferences.getString(("ssid" + String(i)).c_str(), "");
    wifiNetworks[i].password = preferences.getString(("pass" + String(i)).c_str(), "");
  }
  preferences.end();

  bool importedNetwork = false;
  for (size_t initialIndex = 0; initialIndex < initialWifiNetworkCount; initialIndex++) {
    if (initialWifiNetworks[initialIndex].ssid.isEmpty()) {
      continue;
    }

    bool alreadySaved = false;
    for (uint8_t savedIndex = 0; savedIndex < wifiNetworkCount; savedIndex++) {
      if (wifiNetworks[savedIndex].ssid == initialWifiNetworks[initialIndex].ssid) {
        alreadySaved = true;
        break;
      }
    }

    if (!alreadySaved && wifiNetworkCount < MAX_WIFI_NETWORKS) {
      wifiNetworks[wifiNetworkCount++] = initialWifiNetworks[initialIndex];
      importedNetwork = true;
      Serial.println("Imported local WiFi: " + initialWifiNetworks[initialIndex].ssid);
    }
  }

  if (importedNetwork) {
    saveWifiNetworks();
  }
}

void saveWifiNetworks() {
  Preferences preferences;
  preferences.begin("wifi-config", false);
  preferences.putBool("initialized", true);
  preferences.putUChar("count", wifiNetworkCount);

  for (uint8_t i = 0; i < MAX_WIFI_NETWORKS; i++) {
    String ssidKey = "ssid" + String(i);
    String passKey = "pass" + String(i);
    if (i < wifiNetworkCount) {
      preferences.putString(ssidKey.c_str(), wifiNetworks[i].ssid);
      preferences.putString(passKey.c_str(), wifiNetworks[i].password);
    } else {
      preferences.remove(ssidKey.c_str());
      preferences.remove(passKey.c_str());
    }
  }
  preferences.end();
}

bool connectToKnownWifi(String preferredSsid) {
  if (wifiNetworkCount == 0) {
    Serial.println("No saved WiFi network");
    return false;
  }

  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  preferredSsid.trim();
  if (!preferredSsid.isEmpty()) {
    int preferredIndex = -1;
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      if (wifiNetworks[i].ssid == preferredSsid) {
        preferredIndex = i;
        break;
      }
    }
    if (preferredIndex < 0) {
      Serial.println("Selected WiFi is not saved: " + preferredSsid);
      return false;
    }

    Serial.print("Connecting to selected WiFi: ");
    Serial.println(preferredSsid);
    WiFi.begin(
      wifiNetworks[preferredIndex].ssid.c_str(),
      wifiNetworks[preferredIndex].password.c_str()
    );
    unsigned long deadline = millis() + 12000;
    while (WiFi.status() != WL_CONNECTED && static_cast<long>(deadline - millis()) > 0) {
      delay(250);
      Serial.print(".");
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("WiFi connected, IP: ");
      Serial.println(WiFi.localIP());
      return true;
    }
    Serial.println("No connection to selected WiFi");
    return false;
  }

  int16_t rssi[MAX_WIFI_NETWORKS];
  for (uint8_t i = 0; i < wifiNetworkCount; i++) {
    rssi[i] = -32768;
  }

  int foundNetworks = WiFi.scanNetworks();
  for (int scanIndex = 0; scanIndex < foundNetworks; scanIndex++) {
    for (uint8_t savedIndex = 0; savedIndex < wifiNetworkCount; savedIndex++) {
      if (WiFi.SSID(scanIndex) == wifiNetworks[savedIndex].ssid) {
        rssi[savedIndex] = max(rssi[savedIndex], static_cast<int16_t>(WiFi.RSSI(scanIndex)));
      }
    }
  }
  WiFi.scanDelete();

  for (uint8_t attempt = 0; attempt < wifiNetworkCount; attempt++) {
    int bestIndex = -1;
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      if (rssi[i] > -32768 && (bestIndex < 0 || rssi[i] > rssi[bestIndex])) {
        bestIndex = i;
      }
    }
    if (bestIndex < 0) {
      break;
    }

    Serial.print("Connecting to WiFi: ");
    Serial.println(wifiNetworks[bestIndex].ssid);
    WiFi.begin(wifiNetworks[bestIndex].ssid.c_str(), wifiNetworks[bestIndex].password.c_str());
    unsigned long deadline = millis() + 12000;
    while (WiFi.status() != WL_CONNECTED && static_cast<long>(deadline - millis()) > 0) {
      delay(250);
      Serial.print(".");
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("WiFi connected, IP: ");
      Serial.println(WiFi.localIP());
      return true;
    }
    rssi[bestIndex] = -32768;
  }

  Serial.println("No connection to a saved WiFi network");
  return false;
}

String htmlEscape(const String &value) {
  String escaped;
  escaped.reserve(value.length() + 12);
  for (size_t i = 0; i < value.length(); i++) {
    switch (value[i]) {
      case '&': escaped += F("&amp;"); break;
      case '<': escaped += F("&lt;"); break;
      case '>': escaped += F("&gt;"); break;
      case '\"': escaped += F("&quot;"); break;
      case '\'': escaped += F("&#39;"); break;
      default: escaped += value[i]; break;
    }
  }
  return escaped;
}

String jsonEscape(const String &value) {
  String escaped;
  escaped.reserve(value.length() + 8);
  for (size_t i = 0; i < value.length(); i++) {
    char character = value[i];
    if (character == '\\' || character == '\"') {
      escaped += '\\';
      escaped += character;
    } else if (character == '\n') {
      escaped += F("\\n");
    } else if (static_cast<uint8_t>(character) >= 0x20) {
      escaped += character;
    }
  }
  return escaped;
}

int hexadecimalValue(char character) {
  if (character >= '0' && character <= '9') return character - '0';
  if (character >= 'a' && character <= 'f') return character - 'a' + 10;
  if (character >= 'A' && character <= 'F') return character - 'A' + 10;
  return -1;
}

String urlDecode(const String &value) {
  String decoded;
  decoded.reserve(value.length());
  for (size_t i = 0; i < value.length(); i++) {
    if (value[i] == '+') {
      decoded += ' ';
    } else if (value[i] == '%' && i + 2 < value.length()) {
      int high = hexadecimalValue(value[i + 1]);
      int low = hexadecimalValue(value[i + 2]);
      if (high >= 0 && low >= 0) {
        decoded += static_cast<char>((high << 4) | low);
        i += 2;
      } else {
        decoded += value[i];
      }
    } else {
      decoded += value[i];
    }
  }
  return decoded;
}

String formValue(const String &body, const String &key) {
  String prefix = key + "=";
  int start = 0;
  while (start <= static_cast<int>(body.length())) {
    int end = body.indexOf('&', start);
    if (end < 0) end = body.length();
    String field = body.substring(start, end);
    if (field.startsWith(prefix)) return urlDecode(field.substring(prefix.length()));
    start = end + 1;
  }
  return "";
}

int findSavedWifi(const String &ssid) {
  for (uint8_t i = 0; i < wifiNetworkCount; i++) {
    if (wifiNetworks[i].ssid == ssid) return i;
  }
  return -1;
}

esp_err_t wifiSettingsHandler(httpd_req_t *request) {
  int foundNetworks = WiFi.scanNetworks(false, true);
  String page;
  page.reserve(7000);
  page += F("<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>");
  page += F("<title>ESP32-CAM WLAN</title><style>body{font-family:Arial,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;background:#f4f6f8;color:#17202a}main{background:#fff;padding:1.5rem;border-radius:12px;box-shadow:0 2px 12px #0002}label{display:block;margin-top:1rem;font-weight:bold}select,input,button{box-sizing:border-box;width:100%;font:inherit;padding:.65rem;margin-top:.35rem}button{background:#1769aa;color:#fff;border:0;border-radius:6px;cursor:pointer}.hint{background:#eef5ff;padding:.8rem;border-radius:6px}code{background:#eef;padding:.2rem .35rem}</style></head><body><main>");
  page += F("<h1>WLAN-Konfiguration</h1>");
  if (accessPointModeActive) {
    page += F("<p class='hint'>Die Kamera arbeitet im eigenen WLAN <strong>");
    page += htmlEscape(accessPointName);
    page += F("</strong>. Kamera und bekannte Webfunktionen sind unter <code>http://");
    page += WiFi.softAPIP().toString();
    page += F("/</code> erreichbar.</p>");
  } else {
    page += F("<p class='hint'>Aktuell verbunden mit <strong>");
    page += htmlEscape(WiFi.SSID());
    page += F("</strong>. Ein neu gespeichertes WLAN wird nach dem Neustart verwendet.</p>");
  }
  page += F("<form action='/wifi-save' method='post'><label for='ssid'>Gefundenes WLAN</label><select id='ssid' name='ssid'><option value=''>WLAN auswählen oder unten eingeben</option>");
  for (int i = 0; i < foundNetworks; i++) {
    String ssid = WiFi.SSID(i);
    if (ssid.isEmpty()) continue;
    String safeSsid = htmlEscape(ssid);
    page += "<option value='" + safeSsid + "'>" + safeSsid + " (" + String(WiFi.RSSI(i)) + " dBm)";
    if (WiFi.encryptionType(i) == WIFI_AUTH_OPEN) page += " – offen";
    page += "</option>";
  }
  WiFi.scanDelete();
  page += F("</select><label for='manual-ssid'>WLAN-Name manuell</label><input id='manual-ssid' name='manual_ssid' maxlength='32' autocomplete='off'>");
  page += F("<label for='password'>WLAN-Passwort</label><input id='password' name='password' type='password' maxlength='63' autocomplete='new-password'><p><small>Bei einem offenen WLAN bleibt das Passwort leer. Bei einem bereits gespeicherten WLAN behält ein leeres Feld das bisherige Passwort.</small></p>");
  page += F("<button type='submit'>Speichern, verbinden und neu starten</button></form>");
  if (wifiNetworkCount > 0) {
    page += F("<h2>Gespeicherte WLANs</h2>");
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      page += F("<form action='/wifi-delete' method='post' style='display:flex;gap:.5rem;align-items:center;margin:.5rem 0'><input type='hidden' name='ssid' value='");
      page += htmlEscape(wifiNetworks[i].ssid);
      page += F("'><span style='flex:1'>");
      page += htmlEscape(wifiNetworks[i].ssid);
      page += F("</span><button type='submit' style='width:auto;background:#9b2c2c'>Löschen</button></form>");
    }
  }
  page += F("<p><a href='/'>Zur Kamera-Steuerung</a> · <a href='/photo-settings'>Zeitgesteuerte Fotos</a> · <a href='/system'>System und Betriebsart</a></p></main></body></html>");
  httpd_resp_set_type(request, "text/html; charset=utf-8");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  return httpd_resp_send(request, page.c_str(), page.length());
}

esp_err_t wifiSaveHandler(httpd_req_t *request) {
  if (request->content_len <= 0 || request->content_len > 512) {
    httpd_resp_set_status(request, "400 Bad Request");
    return httpd_resp_sendstr(request, "Ungültige WLAN-Daten");
  }
  String body;
  body.reserve(request->content_len);
  char buffer[129];
  int remaining = request->content_len;
  while (remaining > 0) {
    int received = httpd_req_recv(request, buffer, min(remaining, 128));
    if (received <= 0) return httpd_resp_send_500(request);
    body.concat(buffer, received);
    remaining -= received;
  }

  String ssid = formValue(body, "manual_ssid");
  ssid.trim();
  if (ssid.isEmpty()) {
    ssid = formValue(body, "ssid");
    ssid.trim();
  }
  String password = formValue(body, "password");
  if (ssid.isEmpty() || ssid.length() > 32 || password.length() > 63) {
    httpd_resp_set_status(request, "400 Bad Request");
    return httpd_resp_sendstr(request, "Ungültige SSID- oder Passwortlänge");
  }

  int index = findSavedWifi(ssid);
  bool newNetwork = index < 0;
  if (newNetwork) {
    if (wifiNetworkCount >= MAX_WIFI_NETWORKS) {
      httpd_resp_set_status(request, "409 Conflict");
      return httpd_resp_sendstr(request, "Es sind bereits acht WLANs gespeichert. Bitte eines über BLE löschen.");
    }
    index = wifiNetworkCount++;
  }
  wifiNetworks[index].ssid = ssid;
  if (newNetwork || !password.isEmpty() || wifiNetworks[index].password.isEmpty()) {
    wifiNetworks[index].password = password;
  }
  saveWifiNetworks();
  saveWifiForNextBoot(ssid);

  String page = F("<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>WLAN gespeichert</title></head><body style='font-family:Arial,sans-serif;max-width:680px;margin:3rem auto;padding:0 1rem'><h1>WLAN gespeichert</h1><p>Die ESP32-CAM startet neu und versucht die Verbindung mit <strong>");
  page += htmlEscape(ssid);
  page += F("</strong>.</p><p>Schlägt die Verbindung fehl, öffnet sie erneut ihr eigenes WLAN.</p></body></html>");
  httpd_resp_set_type(request, "text/html; charset=utf-8");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  esp_err_t result = httpd_resp_send(request, page.c_str(), page.length());
  Serial.println("HTTP WiFi configuration saved: " + ssid);
  delay(1200);
  ESP.restart();
  return result;
}

esp_err_t wifiDeleteHandler(httpd_req_t *request) {
  if (request->content_len <= 0 || request->content_len > 128) {
    httpd_resp_set_status(request, "400 Bad Request");
    return httpd_resp_sendstr(request, "Ungültige WLAN-Daten");
  }
  char buffer[129] = {};
  int received = httpd_req_recv(request, buffer, request->content_len);
  if (received != request->content_len) return httpd_resp_send_500(request);
  String ssid = formValue(String(buffer).substring(0, received), "ssid");
  int index = findSavedWifi(ssid);
  if (index < 0) {
    httpd_resp_set_status(request, "404 Not Found");
    return httpd_resp_sendstr(request, "WLAN nicht gefunden");
  }
  for (uint8_t i = index; i + 1 < wifiNetworkCount; i++) {
    wifiNetworks[i] = wifiNetworks[i + 1];
  }
  wifiNetworkCount--;
  saveWifiNetworks();
  httpd_resp_set_status(request, "303 See Other");
  httpd_resp_set_hdr(request, "Location", "/wifi-settings");
  return httpd_resp_send(request, nullptr, 0);
}

String activeModeName() {
  return accessPointModeActive ? "access-point" : "station";
}

String deviceName() {
  if (accessPointModeActive) return accessPointName;
  const char *hostname = WiFi.getHostname();
  return hostname == nullptr ? "ESP32-CAM" : String(hostname);
}

esp_err_t deviceInfoHandler(httpd_req_t *request) {
  String mode = activeModeName();
  String ssid = accessPointModeActive ? accessPointName : WiFi.SSID();
  String ip = accessPointModeActive ? WiFi.softAPIP().toString() : WiFi.localIP().toString();
  String json = "{\"program\":\"CameraWebServer\",\"version\":\"";
  json += jsonEscape(PROGRAM_VERSION);
  json += "\",\"mode\":\"" + jsonEscape(mode);
  json += "\",\"ssid\":\"" + jsonEscape(ssid);
  json += "\",\"ip\":\"" + jsonEscape(ip);
  json += "\",\"device\":\"" + jsonEscape(deviceName()) + "\"}";
  httpd_resp_set_type(request, "application/json; charset=utf-8");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  return httpd_resp_send(request, json.c_str(), json.length());
}

esp_err_t systemPageHandler(httpd_req_t *request) {
  String mode = activeModeName();
  String ssid = accessPointModeActive ? accessPointName : WiFi.SSID();
  String ip = accessPointModeActive ? WiFi.softAPIP().toString() : WiFi.localIP().toString();
  String page;
  page.reserve(4200);
  page += F("<!doctype html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>ESP32-CAM System</title><style>body{font-family:Arial,sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem;background:#f4f6f8;color:#17202a}main{background:#fff;padding:1.5rem;border-radius:12px;box-shadow:0 2px 12px #0002}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:.55rem;border-bottom:1px solid #ddd}button{width:100%;font:inherit;padding:.75rem;margin:.35rem 0;background:#1769aa;color:#fff;border:0;border-radius:6px;cursor:pointer}button:disabled{background:#89949e;cursor:default}.warn{background:#fff3cd;padding:.8rem;border-radius:6px}</style></head><body><main><h1>ESP32-CAM-System</h1><table>");
  page += F("<tr><th>Programm</th><td>CameraWebServer</td></tr><tr><th>Version</th><td>");
  page += htmlEscape(PROGRAM_VERSION);
  page += F("</td></tr><tr><th>Betriebsart</th><td>");
  page += htmlEscape(mode);
  page += F("</td></tr><tr><th>Gerät</th><td>");
  page += htmlEscape(deviceName());
  page += F("</td></tr><tr><th>WLAN</th><td>");
  page += htmlEscape(ssid);
  page += F("</td></tr><tr><th>IP-Adresse</th><td>");
  page += htmlEscape(ip);
  page += F("</td></tr><tr><th>Konfigurierte AP-IP</th><td>");
  page += configuredAccessPointIp.toString();
  page += F("</td></tr></table><h2>Betriebsart wechseln</h2><p class='warn'>Nach einem Wechsel wird die aktuelle Verbindung unterbrochen. Die neue Betriebsart ist nach dem Neustart erreichbar.</p>");
  page += F("<form action='/station-mode' method='post'><button type='submit'");
  if (!accessPointModeActive) page += F(" disabled");
  page += F(">Station-Modus starten</button></form><form action='/ap-mode' method='post'><button type='submit'");
  if (accessPointModeActive) page += F(" disabled");
  page += F(">Access-Point-Modus starten</button></form><form action='/ble-mode' method='post'><button type='submit'>BLE-Notbetrieb starten</button></form>");
  page += F("<p><a href='/'>Zur Kamera-Steuerung</a> · <a href='/wifi-settings'>WLAN konfigurieren</a> · <a href='/device-info'>Geräteinfo als JSON</a></p></main></body></html>");
  httpd_resp_set_type(request, "text/html; charset=utf-8");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  return httpd_resp_send(request, page.c_str(), page.length());
}

esp_err_t modeRestartResponse(httpd_req_t *request, const String &mode) {
  saveModeForNextBoot(mode);
  String json = "{\"status\":\"restarting\",\"mode\":\"" + jsonEscape(mode) + "\"}";
  httpd_resp_set_type(request, "application/json; charset=utf-8");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  esp_err_t result = httpd_resp_send(request, json.c_str(), json.length());
  Serial.println("HTTP request: restart into " + mode + " mode");
  delay(750);
  ESP.restart();
  return result;
}

esp_err_t accessPointModeHandler(httpd_req_t *request) {
  return modeRestartResponse(request, "ap");
}

esp_err_t stationModeHandler(httpd_req_t *request) {
  return modeRestartResponse(request, "station");
}

void registerWifiConfigurationHandlers(httpd_handle_t server) {
  httpd_uri_t settingsUri = {
    .uri = "/wifi-settings",
    .method = HTTP_GET,
    .handler = wifiSettingsHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t saveUri = {
    .uri = "/wifi-save",
    .method = HTTP_POST,
    .handler = wifiSaveHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t deleteUri = {
    .uri = "/wifi-delete",
    .method = HTTP_POST,
    .handler = wifiDeleteHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t deviceInfoUri = {
    .uri = "/device-info",
    .method = HTTP_GET,
    .handler = deviceInfoHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t systemUri = {
    .uri = "/system",
    .method = HTTP_GET,
    .handler = systemPageHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t accessPointModeUri = {
    .uri = "/ap-mode",
    .method = HTTP_POST,
    .handler = accessPointModeHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t stationModeUri = {
    .uri = "/station-mode",
    .method = HTTP_POST,
    .handler = stationModeHandler,
    .user_ctx = nullptr,
  };
  httpd_register_uri_handler(server, &settingsUri);
  httpd_register_uri_handler(server, &saveUri);
  httpd_register_uri_handler(server, &deleteUri);
  httpd_register_uri_handler(server, &deviceInfoUri);
  httpd_register_uri_handler(server, &systemUri);
  httpd_register_uri_handler(server, &accessPointModeUri);
  httpd_register_uri_handler(server, &stationModeUri);
}

bool startConfigurationAccessPoint() {
  uint64_t chipId = ESP.getEfuseMac();
  char suffix[7];
  snprintf(
    suffix,
    sizeof(suffix),
    "%02X%02X%02X",
    static_cast<uint8_t>((chipId >> 24) & 0xFF),
    static_cast<uint8_t>((chipId >> 32) & 0xFF),
    static_cast<uint8_t>((chipId >> 40) & 0xFF)
  );
  accessPointName = String(ACCESS_POINT_PREFIX) + "-" + suffix;
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_AP_STA);
  WiFi.setSleep(false);
  IPAddress subnetMask(255, 255, 255, 0);
  if (!WiFi.softAPConfig(configuredAccessPointIp, configuredAccessPointIp, subnetMask)) {
    Serial.println("Configuration access point IP failed");
    return false;
  }
  if (!WiFi.softAP(accessPointName.c_str(), ACCESS_POINT_PASSWORD)) {
    Serial.println("Configuration access point failed");
    return false;
  }
  accessPointModeActive = true;
  Serial.print("Configuration access point: ");
  Serial.println(accessPointName);
  Serial.print("Configuration URL: http://");
  Serial.print(WiFi.softAPIP());
  Serial.println("/wifi-settings");
  return true;
}

void executeBluetoothCommand(String command) {
  command.trim();
  String upperCommand = command;
  upperCommand.toUpperCase();

  if (upperCommand == "HILFE") {
    sendBluetoothLine("Befehle:");
    sendBluetoothLine("  STATUS");
    sendBluetoothLine("  WLAN LISTE");
    sendBluetoothLine("  WLAN HINZUFUEGEN <SSID>|<PASSWORT>");
    sendBluetoothLine("  WLAN LOESCHEN <SSID>");
    sendBluetoothLine("  WLAN VERBINDEN <SSID>");
    sendBluetoothLine("  MODUS AP [PRIVATE-IP]");
  } else if (upperCommand == "STATUS") {
    sendBluetoothLine("Bluetooth: verbunden");
    if (WiFi.status() == WL_CONNECTED) {
      sendBluetoothLine("WLAN: " + WiFi.SSID());
      sendBluetoothLine("IP: " + WiFi.localIP().toString());
    } else {
      sendBluetoothLine("WLAN: nicht verbunden");
    }
    sendBluetoothLine("AP-IP: " + configuredAccessPointIp.toString());
  } else if (upperCommand == "WLAN LISTE") {
    sendBluetoothLine("Gespeicherte WLANs: " + String(wifiNetworkCount));
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      sendBluetoothLine("  " + String(i + 1) + ": " + wifiNetworks[i].ssid);
    }
  } else if (upperCommand.startsWith("WLAN HINZUFUEGEN ")) {
    String parameters = command.substring(17);
    int separator = parameters.indexOf('|');
    if (separator <= 0) {
      sendBluetoothLine("Fehler: SSID und Passwort mit | trennen.");
      return;
    }
    String newSsid = parameters.substring(0, separator);
    String newPassword = parameters.substring(separator + 1);
    newSsid.trim();

    if (newSsid.isEmpty() || newSsid.length() > 32 || newPassword.length() > 63) {
      sendBluetoothLine("Fehler: ungueltige SSID- oder Passwortlaenge.");
      return;
    }

    int index = -1;
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      if (wifiNetworks[i].ssid == newSsid) {
        index = i;
        break;
      }
    }
    if (index < 0) {
      if (wifiNetworkCount >= MAX_WIFI_NETWORKS) {
        sendBluetoothLine("Fehler: maximal 8 WLANs koennen gespeichert werden.");
        return;
      }
      index = wifiNetworkCount++;
    }
    wifiNetworks[index].ssid = newSsid;
    wifiNetworks[index].password = newPassword;
    saveWifiNetworks();
    sendBluetoothLine("WLAN gespeichert: " + newSsid);
  } else if (upperCommand.startsWith("WLAN LOESCHEN ")) {
    String deleteSsid = command.substring(14);
    deleteSsid.trim();
    int index = -1;
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      if (wifiNetworks[i].ssid == deleteSsid) {
        index = i;
        break;
      }
    }
    if (index < 0) {
      sendBluetoothLine("WLAN nicht gefunden: " + deleteSsid);
      return;
    }
    for (uint8_t i = index; i + 1 < wifiNetworkCount; i++) {
      wifiNetworks[i] = wifiNetworks[i + 1];
    }
    wifiNetworkCount--;
    saveWifiNetworks();
    sendBluetoothLine("WLAN geloescht: " + deleteSsid);
  } else if (upperCommand == "WLAN VERBINDEN" || upperCommand.startsWith("WLAN VERBINDEN ")) {
    String selectedSsid = command.substring(14);
    selectedSsid.trim();
    if (selectedSsid.isEmpty()) {
      sendBluetoothLine("Bitte ein WLAN auswaehlen.");
      return;
    }
    bool savedNetworkFound = false;
    for (uint8_t i = 0; i < wifiNetworkCount; i++) {
      if (wifiNetworks[i].ssid == selectedSsid) {
        savedNetworkFound = true;
        break;
      }
    }
    if (!savedNetworkFound) {
      sendBluetoothLine("WLAN nicht gefunden: " + selectedSsid);
      return;
    }

    saveWifiForNextBoot(selectedSsid);
    sendBluetoothLine("Neustart; danach Verbindung mit " + selectedSsid + " ...");
    ledcWrite(LED_GPIO_NUM, 0);
    delay(750);
    ESP.restart();
  } else if (upperCommand == "MODUS AP" || upperCommand.startsWith("MODUS AP ")) {
    String requestedIp = command.substring(8);
    requestedIp.trim();
    if (!requestedIp.isEmpty() && !configureAccessPointIp(requestedIp, true)) {
      sendBluetoothLine("Fehler: private IPv4-Adresse mit Host 1 bis 254 verwenden.");
      sendBluetoothLine("Beispiel: MODUS AP 192.168.41.1");
      return;
    }
    saveModeForNextBoot("ap");
    sendBluetoothLine("Neustart in AP-Modus mit IP " + configuredAccessPointIp.toString() + " ...");
    ledcWrite(LED_GPIO_NUM, 0);
    delay(750);
    ESP.restart();
  } else {
    sendBluetoothLine("Unbekannter Befehl. HILFE zeigt alle Befehle.");
  }
}

void handleBluetoothDialog() {
  if (bleRestartAdvertising) {
    delay(100);
    bleServer->startAdvertising();
    bleRestartAdvertising = false;
  }

  if (bluetoothCommandReady) {
    String command = pendingBluetoothCommand;
    pendingBluetoothCommand = "";
    bluetoothCommandReady = false;
    executeBluetoothCommand(command);
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println("\nESP32 Cam 01");
  Serial.println("CameraWebServer.ino");
  Serial.print("Version ");
  Serial.println(PROGRAM_VERSION);
  pinMode(TASTER, INPUT_PULLUP);
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  loadWifiNetworks();
  loadAccessPointIp();
  Serial.print("Saved WiFi networks: ");
  for (uint8_t i = 0; i < wifiNetworkCount; i++) {
    if (i > 0) {
      Serial.print(",");
    }
    Serial.print(wifiNetworks[i].ssid);
  }
  Serial.println();
  String requestedMode = takeModeRequest();
  bool bluetoothModeRequested = requestedMode == "ble";
  bool accessPointModeRequested = requestedMode == "ap";
  bool bluetoothSetupMode = bluetoothModeRequested || digitalRead(TASTER) == LOW;
  bool wifiConnected = false;
  if (!bluetoothSetupMode && !accessPointModeRequested) {
    String selectedWifi = takeWifiForNextBoot();
    wifiConnected = connectToKnownWifi(selectedWifi);
  }

  if (wifiConnected || (!bluetoothSetupMode && startConfigurationAccessPoint())) {
    if (wifiConnected) {
      stationModeActive = true;
      ledcWrite(LED_GPIO_NUM, STATUS_LED_BRIGHTNESS);
      delay(150);
      ledcWrite(LED_GPIO_NUM, 0);
      synchronizeSystemTime();
    } else {
      statusLedPhase = 0;
      nextStatusLedChange = 0;
    }
    setupScheduledCapture();
    startCameraServer();
    cameraServerStarted = true;
    Serial.print("Camera Ready! Use 'http://");
    Serial.print(wifiConnected ? WiFi.localIP() : WiFi.softAPIP());
    Serial.println("' to connect");
    if (accessPointModeRequested) {
      Serial.println("Access point mode selected by HTTP request");
    }
  } else {
    bluetoothModeActive = true;
    statusLedPhase = 0;
    nextStatusLedChange = 0;
    setupBluetoothDialog();
    Serial.print("BLE configuration ready: ");
    Serial.println(BLUETOOTH_NAME);
    if (bluetoothModeRequested) {
      Serial.println("Bluetooth mode selected by HTTP request");
    } else if (bluetoothSetupMode) {
      Serial.println("Bluetooth mode selected with button on GPIO 13");
    } else {
      Serial.println("Access point failed. Use Bluetooth and HILFE to configure WiFi.");
    }
  }
}

void loop() {
  handleBluetoothDialog();
  handleScheduledCapture();
  handleWifiConnection();
  updateStatusLed();

  if (digitalRead(TASTER) == LOW) {
    Serial.println("Taster gedrückt");
  }

  delay(20);
}
