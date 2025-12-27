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
speed = 2
speedt = 2

def schalterGedrueckt():
    state = GPIO.input(SWITCH_PIN)
    time.sleep(DEBOUNCE)  # Entprelslung
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def main():
    try:
        print("Bereit")
        while True:
            while schalterGedrueckt():
                forward(speed)
                links = get_sensor('l') 
                rechts = get_sensor('r')
                print(f"Links: {links}, Rechts: {rechts}")

                if(links > 650):
                    turn_left(speedt)
                    time.sleep(0.1)
                if(rechts >650):
                    turn_right(speedt)
                    time.sleep(0.1)
                stop()
                time.sleep(0.5)
            stop()
    except KeyboardInterrupt:
        stop()
        cleanup()

if __name__ == '__main__':
    main()