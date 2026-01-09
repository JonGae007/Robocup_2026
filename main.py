#!/usr/bin/env python3
import sys
import time
import traceback

import RPi.GPIO as GPIO
from motor import *

SWITCH_PIN = 25  # Schalter-Pin (BCM)
SENSOR_LEFT_PIN = 5   # GPIO5 - entspricht Pin 16 (links) am ESP32
SENSOR_RIGHT_PIN = 6  # GPIO6 - entspricht Pin 17 (rechts) am ESP32
GRUEN_PIN = 22       # GPIO22 - entspricht Pin 22 (gruen) am ESP32

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_LEFT_PIN, GPIO.IN)
GPIO.setup(SENSOR_RIGHT_PIN, GPIO.IN)
GPIO.setup(GRUEN_PIN, GPIO.IN)

DEBOUNCE = 0.02

# Linienverfolger Konfiguration
BASE_SPEED = 20        # Grundgeschwindigkeit
TURN_SPEED = 80 #Geschwindigkeit beim Abbiegen
HALF_TIME = 0.5      # Zeit für eine 180° Drehung (anpassen nach Bedarf)
QUARTER_TIME = 0.25    # Zeit für eine 90° Drehung (anpassen nach Bedarf)

def schalterGedrueckt():
    state = GPIO.input(SWITCH_PIN)
    time.sleep(DEBOUNCE)
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def read_sensors():
    """Liest die beiden Sensordaten vom ESP32 über GPIO.
    
    Returns:
        tuple: (sensor_left, sensor_right) - 0 für weiß/keine Linie, 1 für schwarz/Linie
    """
    try:
        sensor_left = GPIO.input(SENSOR_LEFT_PIN)   # 0 = weiß, 1 = schwarz
        sensor_right = GPIO.input(SENSOR_RIGHT_PIN)  # 0 = weiß, 1 = schwarz
        gruen = GPIO.input(GRUEN_PIN)  # 1 = gruen
        return sensor_left, sensor_right, gruen
    except ValueError:
        return None, None, None

def check_green():
    left, right, gruen = read_sensors()
    if gruen and right and not left:
        turn_right(TURN_SPEED)
        time.sleep(QUARTER_TIME) #90° anpassen nach bedarf

    if gruen and left and not right:
        turn_left(TURN_SPEED)
        time.sleep(QUARTER_TIME) #90° anpassen nach bedarf
        
    if gruen and left and right:
        forward(BASE_SPEED)
        time.sleep(HALF_TIME) #180° anpassen nach bedarf

def line_follow():
    """Hauptschleife für Linienverfolgung."""
    print("Linienverfolger aktiv")
    
    while schalterGedrueckt():
        left, right, gruen = read_sensors()
        
        while left is None or right is None:
            continue  # ungültige Daten, nächster Durchlauf
        
        # Steuerungslogik
        while left and right:
            # Beide Sensoren auf Linie -> Geradeaus
            forward(BASE_SPEED)
            left, right, gruen = read_sensors()
            check_green()
        while left and not right:
            # Nur linker Sensor auf Linie -> Nach rechts korrigieren
            turn_left(TURN_SPEED)
            forward(BASE_SPEED)
            left, right, gruen = read_sensors()
            check_green
        while not left and right:
            # Nur rechter Sensor auf Linie -> Nach links korrigieren
            turn_right(TURN_SPEED)
            left, right, gruen = read_sensors()
            check_green

        forward(BASE_SPEED)
        
        print(f"L: {left:4d} | R: {right:4d}")

        if gruen and right:
            turn_right(TURN_SPEED)
            time.sleep(QUARTER_TIME) #90° anpassen nach bedarf

        if gruen and left:
            turn_left(TURN_SPEED)
            time.sleep(QUARTER_TIME) #90° anpassen nach bedarf 
        
        if gruen and left and right:
            forward(BASE_SPEED)
            time.sleep(HALF_TIME) #180° anpassen nach bedarf
                

def main():
    try:
        print("Bereit. Schalter drücken zum Starten...")
        
        while True:
            if schalterGedrueckt():
                line_follow()
            else:
                stop()
                time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nBeendet durch Benutzer (STRG+C).")
    except Exception as exc:
        print(f"Fehler aufgetreten: {exc}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            stop()
        except:
            pass
        cleanup()

if __name__ == '__main__':
    main()
