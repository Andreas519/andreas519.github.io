# programme.py

import time
import machine
import gc

import ADC_Messung


aktives_programm = ""


def programm_blinken():
    print("Programm BLINKEN wurde gestartet")

    led = machine.Pin(2, machine.Pin.OUT)

    for i in range(10):
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)

    print("Programm BLINKEN beendet")


def programm_test():
    print("Programm TEST wurde gestartet")

    for i in range(5):
        print("Testlauf:", i)
        time.sleep(0.5)

    print("Programm TEST beendet")


def programm_messung():
    print("Programm MESSUNG wurde gestartet")

    for i in range(10):
        print("Messwert:", i)
        time.sleep(0.3)

    print("Programm MESSUNG beendet")


def adc_json():
    werte, sample_us = ADC_Messung.messen()

    daten = ",".join(str(v) for v in werte)

    json_text = '{{"n":{},"sample_us":{},"werte":[{}]}}'.format(
        len(werte),
        sample_us,
        daten
    )

    return json_text


def starte_programm(prog):
    global aktives_programm

    aktives_programm = prog
    gc.collect()

    if prog == "blink":
        programm_blinken()
        return "Blinkprogramm wurde ausgeführt."

    elif prog == "test":
        programm_test()
        return "Testprogramm wurde ausgeführt."

    elif prog == "messung":
        programm_messung()
        return "Messprogramm wurde ausgeführt."

    elif prog == "Digitaloszi":
        print("Starte 'Digitaloszilloskop.py'")
        import Digitaloszilloskop
        return "Digitaloszi wird ausgeführt."

    else:
        return "Unbekanntes Programm."