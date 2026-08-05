#pragma once

#include "esp_http_server.h"

void setupScheduledCapture();
void handleScheduledCapture();
void synchronizeSystemTime();
void registerScheduledCaptureHandlers(httpd_handle_t server);
