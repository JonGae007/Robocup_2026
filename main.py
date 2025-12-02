#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO
import setup # eigene setup Datei

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
    while True:
        if schalterGedrueckt():
            try: # Main Programm
                print("GEDRÜCKT")
                time.sleep(0.5)
            except KeyboardInterrupt:
                GPIO.cleanup()

if __name__ == '__main__':
    main()
    #put main.py