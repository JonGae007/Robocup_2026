#!/usr/bin/env python3
import sys
import time
import traceback

import RPi.GPIO as GPIO
from motor import *
import sensor

SWITCH_PIN = 25  # Schalter-Pin (BCM)

SENSOR_LEFT_PIN = 5   # GPIO5 - entspricht Pin 16 (links) am ESP32
SENSOR_RIGHT_PIN = 6  # GPIO6 - entspricht Pin 17 (rechts) am ESP32
GRUEN_PIN = 22       # GPIO22 - entspricht Pin 22 (gruen) am ESP32

TRIG = 23   # BCM
ECHO = 24   # BCM

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_LEFT_PIN, GPIO.IN)
GPIO.setup(SENSOR_RIGHT_PIN, GPIO.IN)
GPIO.setup(GRUEN_PIN, GPIO.IN)

# Setup für Ultraschall-Pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)

DEBOUNCE = 0.02

# Linienverfolger Konfiguration
BASE_SPEED = 10        # Grundgeschwindigkeit
TURN_SPEED = 50        # Geschwindigkeit beim Abbiegen

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

def line_follow():
    """Hauptschleife für Linienverfolgung."""
    print("Linienverfolger aktiv")
    
    while schalterGedrueckt():
        left, right, gruen = read_sensors()

        # Ultraschall prüfen: Priorität vor Fahrbefehlen
        dist = measure_distance()
        if dist is not None:
            print(f"{dist:.1f} cm")
        else:
            print("Messfehler")
        time.sleep(0.05)
        if dist is not None and dist < 5.0:
            print(f"Hindernis in {dist:.1f} cm — fahre rückwärts")
            backward(40)
            time.sleep(0.5)
            stop()
            continue
        
    
        if gruen and left:
            
            if gruen and right:
                turn_left(TURN_SPEED)
                time.sleep(1.0)
            else:
                turn_left(TURN_SPEED)
                time.sleep(0.4)

        if gruen and right:
            
            if gruen and left:
                turn_left(TURN_SPEED)
                time.sleep(1.0)
            else:
                turn_right(TURN_SPEED)
                time.sleep(0.4)

        if gruen and left and right:
            turn_left(TURN_SPEED)
            time.sleep(1.0)

                

        if left is None or right is None:
            continue  # ungültige Daten, nächster Durchlauf
        
        # Steuerungslogik
        if left and right:
            # Beide Sensoren auf Linie -> Geradeaus
            forward(BASE_SPEED)
            status = "Geradeaus"
            
        elif left and not right:
            # Nur linker Sensor auf Linie -> Nach links korrigieren
            turn_left(TURN_SPEED)
            status = "Links"
        elif not left and right:
            # Nur rechter Sensor auf Linie -> Nach rechts korrigieren
            turn_right(TURN_SPEED)
            status = "Rechts"
        else:
            # Keine Linie erkannt -> Stoppen oder langsam weiterfahren
            forward(BASE_SPEED // 2)
            status = "Linie verloren"
        
        print(f"L: {left:4d} | R: {right:4d} | {status}")

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
        try:
            sensor.GPIO.cleanup()
        except Exception:
            pass
        cleanup()

if __name__ == '__main__':
    main()
