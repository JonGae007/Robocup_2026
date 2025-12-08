#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

OUT_A = 22
OUT_B = 27
WINDOW = 0.005   # 5 ms Messfenster

GPIO.setmode(GPIO.BCM)
GPIO.setup(OUT_A, GPIO.IN)
GPIO.setup(OUT_B, GPIO.IN)

edges_a = 0
edges_b = 0

def cb_a(channel):
    global edges_a 
    edges_a += 1

def cb_b(channel):
    global edges_b
    edges_b += 1

GPIO.add_event_detect(OUT_A, GPIO.RISING, callback=cb_a)
GPIO.add_event_detect(OUT_B, GPIO.RISING, callback=cb_b)

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
    GPIO.cleanup()