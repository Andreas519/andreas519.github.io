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

#if __has_include("wifi_secrets.h")
#include "wifi_secrets.h"
#else
#define INITIAL_WIFI_NETWORKS { "", "" }
#endif

const char *PROGRAM_VERSION = "0.4.0";
// GPIO 13 is available as long as the SD card interface is not used.
const int TASTER = 13;
const char *BLUETOOTH_NAME = "ESP32-CAM-Setup";
const uint8_t MAX_WIFI_NETWORKS = 8;

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

void startCameraServer();
void setupLedFlash();
void loadWifiNetworks();
void saveWifiNetworks();
bool connectToKnownWifi();
void setupBluetoothDialog();
void handleBluetoothDialog();
void executeBluetoothCommand(String command);

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

bool connectToKnownWifi() {
  if (wifiNetworkCount == 0) {
    Serial.println("No saved WiFi network");
    return false;
  }

  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

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
    sendBluetoothLine("  WLAN VERBINDEN");
  } else if (upperCommand == "STATUS") {
    sendBluetoothLine("Bluetooth: verbunden");
    if (WiFi.status() == WL_CONNECTED) {
      sendBluetoothLine("WLAN: " + WiFi.SSID());
      sendBluetoothLine("IP: " + WiFi.localIP().toString());
    } else {
      sendBluetoothLine("WLAN: nicht verbunden");
    }
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
  } else if (upperCommand == "WLAN VERBINDEN") {
    sendBluetoothLine("WLAN-Verbindung wird aufgebaut ...");
    if (connectToKnownWifi()) {
      sendBluetoothLine("Verbunden mit " + WiFi.SSID());
      sendBluetoothLine("IP: " + WiFi.localIP().toString());
      if (!cameraServerStarted) {
        startCameraServer();
        cameraServerStarted = true;
      }
    } else {
      sendBluetoothLine("Keine Verbindung moeglich.");
    }
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
  Serial.print("Saved WiFi networks: ");
  Serial.println(wifiNetworkCount);
  bool wifiConnected = connectToKnownWifi();

  setupBluetoothDialog();
  Serial.print("BLE ready: ");
  Serial.println(BLUETOOTH_NAME);

  if (wifiConnected) {
    startCameraServer();
    cameraServerStarted = true;
    Serial.print("Camera Ready! Use 'http://");
    Serial.print(WiFi.localIP());
    Serial.println("' to connect");
  } else {
    Serial.println("Use Bluetooth and the command HILFE to configure WiFi.");
  }
}

void loop() {
  handleBluetoothDialog();

  if (digitalRead(TASTER) == LOW) {
    Serial.println("Taster gedrückt");
  }

  delay(20);
}
