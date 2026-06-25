from machine import Pin, ADC
from time import sleep

print("ESP32 Pin-Test GPIO 0 bis 40")
print()

out_pins = []
in_pins = []
adc_pins = []
fehler = []
nicht_testen = [0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 15]

for nr in range(1, 41):
    if nr in nicht_testen:
        print("GPIO", nr, "übersprungen")
        continue
    print("Teste GPIO", nr, "...", end=" ")

    result = []

    # Ausgang testen
    try:
        p = Pin(nr, Pin.OUT)
        p.value(1)
        sleep(0.01)
        p.value(0)
        result.append("OUT")
        out_pins.append(nr)
    except Exception as e:
        pass

    # Eingang testen
    try:
        p = Pin(nr, Pin.IN)
        wert = p.value()
        result.append("IN")
        in_pins.append(nr)
    except Exception as e:
        pass

    # ADC testen
    try:
        adc = ADC(Pin(nr))
        wert = adc.read()
        result.append("ADC")
        adc_pins.append(nr)
    except Exception as e:
        pass

    if result:
        print(", ".join(result))
    else:
        print("nicht nutzbar")
        fehler.append(nr)

print()
print("=" * 40)
print("Nutzbare Ausgangs-Pins:")
print(out_pins)

print()
print("Nutzbare Eingangs-Pins:")
print(in_pins)

print()
print("Nutzbare ADC-Pins:")
print(adc_pins)

print()
print("Nicht nutzbar / Fehler:")
print(fehler)
