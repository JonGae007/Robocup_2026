#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

SWITCH_PIN = 25  # dein Schalter-Pin (BCM)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# interner Pull-Up, weil Schalter nach GND geht
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        state = GPIO.input(SWITCH_PIN)

        if state == 0:
            print("GEDRÜCKT")
        else:
            print("NICHT gedrückt")

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()