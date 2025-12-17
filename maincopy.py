#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO
from motor import *
from sensor import get_sensor

SWITCH_PIN = 25  # Schalter-Pin (BCM)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# interner Pull-Up, weil Schalter nach GND geht
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DEBOUNCE = 0.02
speed = 10
speedt = 10

def schalterGedrueckt():
    state = GPIO.input(SWITCH_PIN)
    time.sleep(DEBOUNCE)  # Entprelslung
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def main():
    try:
        print("Bereit")
        while True:
            while schalterGedrueckt():
                turn_right(10)
            stop()
    except KeyboardInterrupt:
        stop()
        cleanup()

if __name__ == '__main__':
    main()