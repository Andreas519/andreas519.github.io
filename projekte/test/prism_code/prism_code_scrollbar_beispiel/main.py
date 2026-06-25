from machine import Pin
import time

# Beispielprogramm für den ESP32
# Die eingebaute LED wird im Sekundentakt umgeschaltet.

led = Pin(2, Pin.OUT)

def blinke_led(anzahl, pause):
    for i in range(anzahl):
        led.value(1)
        time.sleep(pause)
        led.value(0)
        time.sleep(pause)

def kurze_pause():
    time.sleep(1)

while True:
    blinke_led(3, 0.2)
    kurze_pause()
    blinke_led(1, 0.8)
    kurze_pause()
