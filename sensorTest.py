#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# ====== Pinbelegung anpassen ======
OUT_A = 22   # Sensor A OUT (anpassen falls nötig)
OUT_B = 27   # Sensor B OUT

SAMPLE_US = 5000  # wie beim ESP (5 ms)
SAMPLE_S  = SAMPLE_US / 1_000_000.0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OUT_A, GPIO.IN)
GPIO.setup(OUT_B, GPIO.IN)

BLACK = 0
WHITE = 1

def read_freq(pin, window_s=SAMPLE_S):
    """TCS-Frequenz wie beim ESP aus HIGH-Pulsdauer ableiten."""
    start = time.perf_counter()
    # Auf HIGH warten
    while GPIO.input(pin) == 0:
        if time.perf_counter() - start > window_s:
            return 0.0
    t1 = time.perf_counter()
    # Warten bis wieder LOW
    while GPIO.input(pin) == 1:
        if time.perf_counter() - t1 > window_s:
            break
    t2 = time.perf_counter()

    high_time = t2 - t1
    if high_time <= 0:
        return 0.0

    # wie 500000 / t(µs) -> 1/(2*T) angenähert
    # hier T = high_time, also f ≈ 1/(2*T)
    return 1.0 / (2.0 * high_time)

def classifyC(c):
    # wie in deinem ESP-Code: >7000 = BLACK, sonst WHITE
    if c > 7000:
        return BLACK
    return WHITE

def colorToDigit(c):
    if c == BLACK:
        return 0
    return 1  # WHITE + Fallback

try:
    while True:
        ca = read_freq(OUT_A)
        cb = read_freq(OUT_B)

        colorA = classifyC(ca)
        colorB = classifyC(cb)

        da = colorToDigit(colorA)
        db = colorToDigit(colorB)

        # Rohwerte (Frequenz in Hz) ausgeben — zwei Werte nebeneinander
        # Beispiel: "12.34 56.78"
        print(f"{ca:.2f} {cb:.2f}")

        time.sleep(0.01)  # ~100 Hz wie beim ESP (delay(10))

except KeyboardInterrupt:
    GPIO.cleanup()