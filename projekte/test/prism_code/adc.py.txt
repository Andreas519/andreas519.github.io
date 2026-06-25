from machine import Pin
import time

# Beispielprogramm für den ESP32
# Die eingebaute LED wird im Sekundentakt umgeschaltet.

led = Pin(2, Pin.OUT)

while True:
    led.value(not led.value())
    time.sleep(0.5)

import network, socket, time
from machine import ADC, Pin
# WLAN-Zugangsdaten
SSID = "raspi"
PASSWORD = "abcd1234"
# ADC-Einstellung
adc_pin = ADC(Pin(4))          # ADC-Pin, z.B. GPIO34
adc_pin.atten(ADC.ATTN_11DB)    # Bereich ungefähr 0...3,3 V
adc_pin.width(ADC.WIDTH_12BIT)  # Werte 0...4095
# Messspeicher
MAX_N = 2000                    # Sicherheitsgrenze
N = 300                         # Standardwert
werte = [0] * N

import network, socket, time
from machine import ADC, Pin
# WLAN-Zugangsdaten
SSID = "raspi"
PASSWORD = "abcd1234"
# ADC-Einstellung
adc_pin = ADC(Pin(4))          # ADC-Pin, z.B. GPIO34
adc_pin.atten(ADC.ATTN_11DB)    # Bereich ungefähr 0...3,3 V
adc_pin.width(ADC.WIDTH_12BIT)  # Werte 0...4095
# Messspeicher
MAX_N = 2000                    # Sicherheitsgrenze
N = 300                         # Standardwert
werte = [0] * N