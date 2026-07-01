from machine import ADC, Pin
from time import ticks_us, ticks_diff

ADC_PIN = 34
N = 1000   # erstmal 1000 statt 2000, das ist speicherschonender

def messen():
    adc = ADC(Pin(ADC_PIN))
    adc.atten(ADC.ATTN_11DB)      # ungefähr 0...3,3 V
    adc.width(ADC.WIDTH_12BIT)    # 0...4095

    werte = [0] * N

    t0 = ticks_us()
    for i in range(N):
        werte[i] = adc.read()
    t1 = ticks_us()

    sample_us = ticks_diff(t1, t0) / N
    return werte, sample_us