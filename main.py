#!/usr/bin/env python3
import sys
import time
import traceback

import RPi.GPIO as GPIO
from motor import *
import sensor as sensors

SWITCH_PIN = 25  # Schalter-Pin (BCM)
SENSOR_LEFT_PIN = 5   # GPIO5 - entspricht Pin 16 (links) am ESP32
SENSOR_RIGHT_PIN = 6  # GPIO6 - entspricht Pin 17 (rechts) am ESP32
GRUEN_PIN = 22       # GPIO22 - entspricht Pin 22 (gruen) am ESP32
LED_PIN = 8          # GPIO8 - LED für Grün-Erkennung

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_LEFT_PIN, GPIO.IN)
GPIO.setup(SENSOR_RIGHT_PIN, GPIO.IN)
GPIO.setup(GRUEN_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

DEBOUNCE = 0.02

# Linienverfolger Konfiguration
BASE_SPEED = 20        # Grundgeschwindigkeit
TURN_SPEED = 80 #Geschwindigkeit beim Abbiegen
QUARTER_TIME = 0.5    # Zeit für eine 90° Drehung (anpassen nach Bedarf)
HALF_TIME = 1       # Zeit für eine 180° Drehung (anpassen nach Bedarf)

# Globale Variable für White-Timer
_white_start_time = None

def endzone(left, right, threshold=4.0):
    """Erkennt, wenn beide Sensoren für eine bestimmte Zeit auf Weiß sind und führt dann eine Drehung aus.
    
    Args:
        left: Sensor links Wert (0=weiß, 1=schwarz)
        right: Sensor rechts Wert (0=weiß, 1=schwarz)
        threshold: Zeit in Sekunden, nach der die Aktion ausgelöst wird (default: 1.0)
    """
    global _white_start_time
    
    if not left and not right:
        if _white_start_time is None:
            _white_start_time = time.time()
        else:
            elapsed = time.time() - _white_start_time
            forward(BASE_SPEED)
            if elapsed >= threshold:
                # Aktion: kurz stoppen, dann drehen
                stop()
                time.sleep(0.2)
                # Drehe (90°) — Richtung kann bei Bedarf angepasst werden
                turn_right(TURN_SPEED)
                time.sleep(QUARTER_TIME)
                stop()
                # Timer zurücksetzen nach Aktion
                _white_start_time = None
    else:
        _white_start_time = None

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

def check_green_and_react(left, right, gruen):
    """Prüft auf Grün-Erkennung und reagiert entsprechend.
    
    Args:
        left: Sensor links Wert
        right: Sensor rechts Wert  
        gruen: Grün-Sensor Wert
    """
    if gruen and right and not left:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)
        turn_right(TURN_SPEED)
        time.sleep(QUARTER_TIME)  # 90° anpassen nach bedarf
        time.sleep(0.2)

    if gruen and left and not right:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)
        turn_left(TURN_SPEED)
        time.sleep(QUARTER_TIME)  # 90° anpassen nach bedarf
        forward(BASE_SPEED)
        time.sleep(0.1)
        
    if gruen and left and right:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)
        turn_right(TURN_SPEED)
        time.sleep(HALF_TIME)  # 180° anpassen nach bedarf

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
            status = "Geradeaus"
            left, right, gruen = read_sensors()
            check_green_and_react(left, right, gruen)
            endzone(left, right)
        while left and not right:
            # Nur linker Sensor auf Linie -> Nach rechts korrigieren
            turn_left(TURN_SPEED)
            status = "Rechts"
            forward(BASE_SPEED)
            left, right, gruen = read_sensors()
            check_green_and_react(left, right, gruen)
            endzone(left, right)
        while not left and right:
            # Nur rechter Sensor auf Linie -> Nach links korrigieren
            turn_right(TURN_SPEED)
            status = "Links"
            left, right, gruen = read_sensors()
            check_green_and_react(left, right, gruen)
            endzone(left, right)

        # Endzone-Check auch außerhalb der while-Schleifen (für den Fall: beide Sensoren weiß)
        endzone(left, right)
        
        forward(BASE_SPEED)
        
        
        print(f"L: {left:4d} | R: {right:4d} ")

def main():
    try:
        print("Bereit. Schalter drücken zum Starten...")
        
        while True:
            if schalterGedrueckt():
                line_follow()
            else:
                stop()
                # Ultraschall-Entfernungen auslesen, wenn nicht aktiv
                try:
                    d1, d2 = sensors.read_ultrasonics()
                    print(f"US1: {d1 if d1 is not None else 'Timeout':>7} cm | US2: {d2 if d2 is not None else 'Timeout':>7} cm")
                except Exception:
                    # Bei Problemen mit GPIO/Hardware nicht abstürzen
                    pass
                time.sleep(0.5)
            
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