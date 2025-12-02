#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

TRIG = 23   # BCM
ECHO = 24   # BCM

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Trigger-Puls: 10 µs HIGH
    GPIO.output(TRIG, False)
    time.sleep(0.0002)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Auf steigende Flanke warten (Start)
    start_time = time.time()
    timeout = start_time + 0.02  # 20 ms Timeout
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if start_time > timeout:
            return None

    # Auf fallende Flanke warten (Ende)
    stop_time = time.time()
    timeout = stop_time + 0.02
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if stop_time > timeout:
            return None

    # Zeitdifferenz
    elapsed = stop_time - start_time
    # Schallgeschwindigkeit ~34300 cm/s, hin und zurück -> /2
    distance_cm = (elapsed * 34300) / 2.0
    return distance_cm

try:
    while True:
        dist = measure_distance()
        if dist is not None:
            print(f"{dist:.1f} cm")
        else:
            print("Messfehler")
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()