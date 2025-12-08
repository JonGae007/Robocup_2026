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

def schalterGedrueckt():
    state = GPIO.input(SWITCH_PIN)
    time.sleep(DEBOUNCE)  # Entprellung
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def main():
    try:
        while True:
            while schalterGedrueckt():
                forward(80)
            stop()
            freq_links = get_sensor('l')
            freq_rechts = get_sensor('r')
            print(f"Links: {freq_links:.0f} Hz, Rechts: {freq_rechts:.0f} Hz")
            time.sleep(0.01)
    except KeyboardInterrupt:
        stop()
        cleanup()

if __name__ == '__main__':
    main()