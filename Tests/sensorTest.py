#!/usr/bin/env python3
import pigpio
import time

OUT_A = 22
OUT_B = 27
WINDOW = 0.005   # 5 ms Messfenster

pi = pigpio.pi()
if not pi.connected:
    raise SystemExit("pigpio daemon läuft nicht (sudo pigpiod starten)")

pi.set_mode(OUT_A, pigpio.INPUT)
pi.set_mode(OUT_B, pigpio.INPUT)

edges_a = 0
edges_b = 0

def cb_a(gpio, level, tick):
    global edges_a
    if level == 1:      # Rising edge
        edges_a += 1

def cb_b(gpio, level, tick):
    global edges_b
    if level == 1:
        edges_b += 1

cba = pi.callback(OUT_A, pigpio.RISING_EDGE, cb_a)
cbb = pi.callback(OUT_B, pigpio.RISING_EDGE, cb_b)

try:
    while True:
        edges_a = 0
        edges_b = 0

        start = time.time()
        time.sleep(WINDOW)
        dt = time.time() - start

        fa = edges_a / (2.0 * dt)  # 2 Flanken pro Periode
        fb = edges_b / (2.0 * dt)

        # ROH-Werte
        print(f"{fa:.0f} {fb:.0f}")

        # kannst du kleiner machen
        time.sleep(0.001)

except KeyboardInterrupt:
    cba.cancel()
    cbb.cancel()
    pi.stop()