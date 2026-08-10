#include "scheduled_capture.h"

#include <Arduino.h>
#include "esp_camera.h"
#include <Preferences.h>
#include <WiFi.h>
#include <WiFiClient.h>

namespace {

struct ResolutionOption {
  const char *name;
  const char *label;
  framesize_t frameSize;
};

const ResolutionOption RESOLUTIONS[] = {
  { "QVGA", "320 x 240", FRAMESIZE_QVGA },
  { "VGA", "640 x 480", FRAMESIZE_VGA },
  { "SVGA", "800 x 600", FRAMESIZE_SVGA },
  { "XGA", "1024 x 768", FRAMESIZE_XGA },
  { "SXGA", "1280 x 1024", FRAMESIZE_SXGA },
  { "UXGA", "1600 x 1200", FRAMESIZE_UXGA },
};

const size_t RESOLUTION_COUNT = sizeof(RESOLUTIONS) / sizeof(RESOLUTIONS[0]);
portMUX_TYPE photoStateMux = portMUX_INITIALIZER_UNLOCKED;
uint8_t *latestPhoto = nullptr;
size_t latestPhotoLength = 0;
uint64_t latestPhotoTime = 0;
uint64_t synchronizedUnixTime = 0;
unsigned long synchronizedAtMillis = 0;
unsigned long lastTimeSyncAttempt = 0;
String selectedResolution = "VGA";
uint32_t captureIntervalSeconds = 60;
volatile bool captureRequested = true;
volatile bool photoCaptureInProgress = false;
volatile bool photoDownloadInProgress = false;
unsigned long lastCaptureMillis = 0;
bool scheduledCaptureEnabled = false;

const ResolutionOption *findResolution(const String &name) {
  for (size_t i = 0; i < RESOLUTION_COUNT; i++) {
    if (name.equalsIgnoreCase(RESOLUTIONS[i].name)) {
      return &RESOLUTIONS[i];
    }
  }
  return nullptr;
}

int64_t daysFromCivil(int year, unsigned int month, unsigned int day) {
  year -= month <= 2;
  const int era = (year >= 0 ? year : year - 399) / 400;
  const unsigned int yearOfEra = static_cast<unsigned int>(year - era * 400);
  const unsigned int dayOfYear = (153 * (month + (month > 2 ? -3 : 9)) + 2) / 5 + day - 1;
  const unsigned int dayOfEra = yearOfEra * 365 + yearOfEra / 4 - yearOfEra / 100 + dayOfYear;
  return era * 146097 + static_cast<int>(dayOfEra) - 719468;
}

void civilFromDays(int64_t days, int &year, unsigned int &month, unsigned int &day) {
  days += 719468;
  const int era = static_cast<int>((days >= 0 ? days : days - 146096) / 146097);
  const unsigned int dayOfEra = static_cast<unsigned int>(days - era * 146097);
  const unsigned int yearOfEra = (dayOfEra - dayOfEra / 1460 + dayOfEra / 36524 - dayOfEra / 146096) / 365;
  year = static_cast<int>(yearOfEra) + era * 400;
  const unsigned int dayOfYear = dayOfEra - (365 * yearOfEra + yearOfEra / 4 - yearOfEra / 100);
  const unsigned int monthPrime = (5 * dayOfYear + 2) / 153;
  day = dayOfYear - (153 * monthPrime + 2) / 5 + 1;
  month = monthPrime + (monthPrime < 10 ? 3 : -9);
  year += month <= 2;
}

unsigned int daysInMonth(int year, unsigned int month) {
  static const uint8_t lengths[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
  if (month == 2 && (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0)) {
    return 29;
  }
  return lengths[month - 1];
}

unsigned int lastSunday(int year, unsigned int month) {
  unsigned int lastDay = daysInMonth(year, month);
  int64_t days = daysFromCivil(year, month, lastDay);
  unsigned int weekDay = static_cast<unsigned int>((days + 4) % 7);
  return lastDay - weekDay;
}

uint64_t currentUnixTime() {
  if (synchronizedUnixTime == 0) {
    return 0;
  }
  return synchronizedUnixTime + (millis() - synchronizedAtMillis) / 1000UL;
}

bool isEuropeanSummerTime(uint64_t utcValue) {
  int year;
  unsigned int month;
  unsigned int day;
  civilFromDays(static_cast<int64_t>(utcValue / 86400ULL), year, month, day);
  uint64_t start = static_cast<uint64_t>(daysFromCivil(year, 3, lastSunday(year, 3))) * 86400ULL + 3600ULL;
  uint64_t end = static_cast<uint64_t>(daysFromCivil(year, 10, lastSunday(year, 10))) * 86400ULL + 3600ULL;
  return utcValue >= start && utcValue < end;
}

String formatLocalTime(uint64_t value, bool fileName = false) {
  if (value < 1700000000) {
    return "noch nicht verfügbar";
  }

  uint64_t localValue = value + (isEuropeanSummerTime(value) ? 7200ULL : 3600ULL);
  int year;
  unsigned int month;
  unsigned int day;
  civilFromDays(static_cast<int64_t>(localValue / 86400ULL), year, month, day);
  unsigned int secondsOfDay = static_cast<unsigned int>(localValue % 86400ULL);
  unsigned int hour = secondsOfDay / 3600;
  unsigned int minute = (secondsOfDay % 3600) / 60;
  unsigned int second = secondsOfDay % 60;
  char buffer[32];
  if (fileName) {
    snprintf(buffer, sizeof(buffer), "%04d%02u%02u-%02u%02u%02u", year, month, day, hour, minute, second);
  } else {
    snprintf(buffer, sizeof(buffer), "%02u.%02u.%04d %02u:%02u:%02u", day, month, year, hour, minute, second);
  }
  return String(buffer);
}

void savePhotoConfiguration() {
  Preferences preferences;
  preferences.begin("photo-config", false);
  preferences.putString("resolution", selectedResolution);
  preferences.putUInt("interval", captureIntervalSeconds);
  preferences.end();
}

void loadPhotoConfiguration() {
  Preferences preferences;
  preferences.begin("photo-config", true);
  selectedResolution = preferences.getString("resolution", "VGA");
  captureIntervalSeconds = preferences.getUInt("interval", 60);
  preferences.end();

  if (findResolution(selectedResolution) == nullptr) {
    selectedResolution = "VGA";
  }
  if (captureIntervalSeconds > 86400) {
    captureIntervalSeconds = 60;
  }
}

bool captureScheduledPhoto() {
  portENTER_CRITICAL(&photoStateMux);
  if (photoCaptureInProgress || photoDownloadInProgress) {
    portEXIT_CRITICAL(&photoStateMux);
    return false;
  }
  photoCaptureInProgress = true;
  portEXIT_CRITICAL(&photoStateMux);

  const ResolutionOption *resolution = findResolution(selectedResolution);
  sensor_t *sensor = esp_camera_sensor_get();
  if (resolution == nullptr || sensor == nullptr) {
    photoCaptureInProgress = false;
    return false;
  }

  sensor->set_framesize(sensor, resolution->frameSize);
  delay(100);
  camera_fb_t *frame = esp_camera_fb_get();
  if (frame == nullptr || frame->format != PIXFORMAT_JPEG) {
    if (frame != nullptr) {
      esp_camera_fb_return(frame);
    }
    Serial.println("Scheduled photo failed");
    photoCaptureInProgress = false;
    return false;
  }

  uint8_t *newPhoto = static_cast<uint8_t *>(ps_malloc(frame->len));
  if (newPhoto == nullptr) {
    newPhoto = static_cast<uint8_t *>(malloc(frame->len));
  }
  if (newPhoto == nullptr) {
    esp_camera_fb_return(frame);
    Serial.println("Not enough memory for scheduled photo");
    photoCaptureInProgress = false;
    return false;
  }

  memcpy(newPhoto, frame->buf, frame->len);
  size_t newPhotoLength = frame->len;
  esp_camera_fb_return(frame);

  portENTER_CRITICAL(&photoStateMux);
  uint8_t *oldPhoto = latestPhoto;
  latestPhoto = newPhoto;
  latestPhotoLength = newPhotoLength;
  latestPhotoTime = currentUnixTime();
  photoCaptureInProgress = false;
  portEXIT_CRITICAL(&photoStateMux);
  free(oldPhoto);

  Serial.printf(
    "Scheduled photo ready: %s, %u bytes, %s\n",
    selectedResolution.c_str(),
    static_cast<unsigned int>(newPhotoLength),
    formatLocalTime(latestPhotoTime).c_str()
  );
  return true;
}

esp_err_t photoSettingsHandler(httpd_req_t *request) {
  uint64_t now = currentUnixTime();
  String page;
  page.reserve(5000);
  page += F("<!doctype html><html lang='de'><head><meta charset='utf-8'>");
  page += F("<meta name='viewport' content='width=device-width,initial-scale=1'>");
  page += F("<title>Zeitgesteuerte Fotos</title><style>");
  page += F("body{font-family:Arial,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;background:#f4f6f8;color:#17202a}");
  page += F("main{background:white;padding:1.5rem;border-radius:12px;box-shadow:0 2px 12px #0002}label{display:block;margin-top:1rem;font-weight:bold}");
  page += F("select,input,button{font:inherit;padding:.6rem;margin-top:.35rem}button{background:#1769aa;color:white;border:0;border-radius:6px;cursor:pointer}");
  page += F("img{max-width:100%;height:auto;margin-top:1rem;border-radius:6px}code{background:#eef;padding:.2rem .35rem}</style></head><body><main>");
  page += F("<h1>Zeitgesteuerte Fotos</h1><p>Systemzeit: <strong>");
  page += formatLocalTime(now);
  page += F("</strong></p><form action='/photo-config' method='get'><label for='resolution'>Auflösung</label><select id='resolution' name='resolution'>");

  for (size_t i = 0; i < RESOLUTION_COUNT; i++) {
    page += "<option value='" + String(RESOLUTIONS[i].name) + "'";
    if (selectedResolution == RESOLUTIONS[i].name) {
      page += " selected";
    }
    page += ">" + String(RESOLUTIONS[i].name) + " – " + String(RESOLUTIONS[i].label) + "</option>";
  }

  page += F("</select><label for='interval'>Aufnahmeintervall in Sekunden</label>");
  page += F("<input id='interval' name='interval' type='number' min='0' max='86400' value='");
  page += String(captureIntervalSeconds);
  page += F("'><p><small>0 deaktiviert automatische Aufnahmen.</small></p><button type='submit'>Einstellungen speichern</button></form>");
  page += F("<h2>Letzte Aufnahme</h2><p>Zeitpunkt: <strong>");
  page += formatLocalTime(latestPhotoTime);
  page += F("</strong></p><p>Direkter Abruf für den PC: <code>/scheduled-photo</code></p>");
  if (latestPhotoLength > 0) {
    page += F("<p><a href='/scheduled-photo' download>Foto herunterladen</a></p><img src='/scheduled-photo' alt='Letzte zeitgesteuerte Aufnahme'>");
  } else {
    page += F("<p>Noch keine Aufnahme vorhanden.</p>");
  }
  page += F("<p><a href='/'>Zur Kamera-Steuerung</a> · <a href='/wifi-settings'>WLAN konfigurieren</a> · <a href='/system'>System und Betriebsart</a></p></main></body></html>");

  httpd_resp_set_type(request, "text/html; charset=utf-8");
  return httpd_resp_send(request, page.c_str(), page.length());
}

esp_err_t photoConfigHandler(httpd_req_t *request) {
  size_t queryLength = httpd_req_get_url_query_len(request) + 1;
  char *query = static_cast<char *>(malloc(queryLength));
  if (query == nullptr) {
    return httpd_resp_send_500(request);
  }

  char resolutionValue[16] = {};
  char intervalValue[16] = {};
  bool valid = httpd_req_get_url_query_str(request, query, queryLength) == ESP_OK
    && httpd_query_key_value(query, "resolution", resolutionValue, sizeof(resolutionValue)) == ESP_OK
    && httpd_query_key_value(query, "interval", intervalValue, sizeof(intervalValue)) == ESP_OK;
  free(query);

  const ResolutionOption *resolution = findResolution(String(resolutionValue));
  long interval = strtol(intervalValue, nullptr, 10);
  if (!valid || resolution == nullptr || interval < 0 || interval > 86400) {
    httpd_resp_set_status(request, "400 Bad Request");
    return httpd_resp_sendstr(request, "Ungültige Fotoeinstellungen");
  }

  selectedResolution = resolution->name;
  captureIntervalSeconds = static_cast<uint32_t>(interval);
  captureRequested = true;
  savePhotoConfiguration();

  httpd_resp_set_status(request, "303 See Other");
  httpd_resp_set_hdr(request, "Location", "/photo-settings");
  return httpd_resp_send(request, nullptr, 0);
}

esp_err_t scheduledPhotoHandler(httpd_req_t *request) {
  portENTER_CRITICAL(&photoStateMux);
  if (photoCaptureInProgress || latestPhoto == nullptr || latestPhotoLength == 0) {
    portEXIT_CRITICAL(&photoStateMux);
    httpd_resp_set_status(request, "503 Service Unavailable");
    return httpd_resp_sendstr(request, "Noch kein Foto verfügbar");
  }
  photoDownloadInProgress = true;
  portEXIT_CRITICAL(&photoStateMux);

  char fileName[64] = "attachment; filename=esp32-cam-photo.jpg";
  if (latestPhotoTime >= 1700000000) {
    snprintf(
      fileName,
      sizeof(fileName),
      "attachment; filename=esp32-cam-%s.jpg",
      formatLocalTime(latestPhotoTime, true).c_str()
    );
  }

  httpd_resp_set_type(request, "image/jpeg");
  httpd_resp_set_hdr(request, "Content-Disposition", fileName);
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  esp_err_t result = httpd_resp_send(
    request,
    reinterpret_cast<const char *>(latestPhoto),
    latestPhotoLength
  );
  photoDownloadInProgress = false;
  return result;
}

esp_err_t bluetoothModeHandler(httpd_req_t *request) {
  Preferences preferences;
  preferences.begin("device-mode", false);
  preferences.putString("next-mode", "ble");
  preferences.end();

  httpd_resp_set_type(request, "application/json");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  esp_err_t result = httpd_resp_sendstr(
    request,
    "{\"status\":\"restarting\",\"mode\":\"ble\"}"
  );
  Serial.println("HTTP request: restart into Bluetooth mode");
  delay(750);
  ESP.restart();
  return result;
}

}  // namespace

void setupScheduledCapture() {
  loadPhotoConfiguration();
  scheduledCaptureEnabled = true;
}

void handleScheduledCapture() {
  if (!scheduledCaptureEnabled) {
    return;
  }
  if (WiFi.status() == WL_CONNECTED
      && millis() - lastTimeSyncAttempt >= 21600000UL) {
    synchronizeSystemTime();
  }
  uint32_t interval = captureIntervalSeconds;
  bool due = interval > 0
    && (lastCaptureMillis == 0 || millis() - lastCaptureMillis >= interval * 1000UL);
  if (captureRequested || due) {
    captureRequested = false;
    if (captureScheduledPhoto()) {
      lastCaptureMillis = millis();
    }
  }
}

void synchronizeSystemTime() {
  lastTimeSyncAttempt = millis();
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  WiFiClient client;
  client.setTimeout(3000);
  if (!client.connect("www.google.com", 80)) {
    Serial.println("Time server connection failed");
    return;
  }

  client.print(
    "HEAD /generate_204 HTTP/1.1\r\n"
    "Host: www.google.com\r\n"
    "Connection: close\r\n\r\n"
  );

  uint64_t unixTime = 0;
  unsigned long deadline = millis() + 5000;
  while ((client.connected() || client.available())
         && static_cast<long>(deadline - millis()) > 0) {
    if (!client.available()) {
      delay(10);
      continue;
    }
    String line = client.readStringUntil('\n');
    line.trim();
    if (line.startsWith("Date:") && line.length() >= 31) {
      static const char *MONTH_NAMES[] = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
      };
      unsigned int day = line.substring(11, 13).toInt();
      String monthName = line.substring(14, 17);
      unsigned int month = 0;
      for (unsigned int i = 0; i < 12; i++) {
        if (monthName == MONTH_NAMES[i]) {
          month = i + 1;
          break;
        }
      }
      int year = line.substring(18, 22).toInt();
      unsigned int hour = line.substring(23, 25).toInt();
      unsigned int minute = line.substring(26, 28).toInt();
      unsigned int second = line.substring(29, 31).toInt();
      if (year >= 2024 && month > 0) {
        unixTime = static_cast<uint64_t>(daysFromCivil(year, month, day)) * 86400ULL
          + hour * 3600ULL + minute * 60ULL + second;
        break;
      }
    }
  }
  client.stop();

  if (unixTime < 1700000000) {
    Serial.println("Invalid time server response");
    return;
  }

  synchronizedUnixTime = unixTime;
  synchronizedAtMillis = millis();
  Serial.print("System time synchronized: ");
  Serial.println(formatLocalTime(currentUnixTime()));
}

void registerScheduledCaptureHandlers(httpd_handle_t server) {
  httpd_uri_t settingsUri = {
    .uri = "/photo-settings",
    .method = HTTP_GET,
    .handler = photoSettingsHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t configUri = {
    .uri = "/photo-config",
    .method = HTTP_GET,
    .handler = photoConfigHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t photoUri = {
    .uri = "/scheduled-photo",
    .method = HTTP_GET,
    .handler = scheduledPhotoHandler,
    .user_ctx = nullptr,
  };
  httpd_uri_t bluetoothModeUri = {
    .uri = "/ble-mode",
    .method = HTTP_POST,
    .handler = bluetoothModeHandler,
    .user_ctx = nullptr,
  };

  httpd_register_uri_handler(server, &settingsUri);
  httpd_register_uri_handler(server, &configUri);
  httpd_register_uri_handler(server, &photoUri);
  httpd_register_uri_handler(server, &bluetoothModeUri);
}
