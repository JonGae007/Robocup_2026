#!/usr/bin/env python3
"""
Testskript für beide HC-SR04 Ultraschall-Sensoren.
Zeigt kontinuierlich die Distanzen beider Sensoren an.
"""
import sys
import time
import os
import RPi.GPIO as GPIO

# Füge das Hauptverzeichnis zum Pfad hinzu, um sensor.py zu importieren
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sensor

# Schalter-Pin für Start/Stop
SWITCH_PIN = 25
DEBOUNCE = 0.02

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def schalter_gedrueckt():
    """Prüft ob der Schalter gedrückt ist (mit Entprellung)."""
    state = GPIO.input(SWITCH_PIN)
    time.sleep(DEBOUNCE)
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def test_ultrasonics_continuous():
    """Liest kontinuierlich beide Ultraschall-Sensoren aus und zeigt die Werte an."""
    print("=" * 60)
    print("Ultraschall-Sensor Test")
    print("=" * 60)
    print("Sensor 1 (vorne): TRIG=GPIO23, ECHO=GPIO24")
    print("Sensor 2 (rechts): TRIG=GPIO17, ECHO=GPIO27")
    print("Drücke STRG+C zum Beenden")
    print("=" * 60)
    print()
    
    try:
        while True:
            # Lese beide Sensoren
            distance_vorne, distance_rechts = sensor.read_ultrasonics()
            
            # Formatiere Ausgabe
            d1_str = f"{distance_vorne:6.2f} cm" if distance_vorne is not None else "  Timeout"
            d2_str = f"{distance_rechts:6.2f} cm" if distance_rechts is not None else "  Timeout"
            
            print(f"Vorne: {d1_str} | Rechts: {d2_str}")
            
            time.sleep(0.1)  # 10 Hz Abtastrate
            
    except KeyboardInterrupt:
        print("\n\nTest beendet durch Benutzer (STRG+C).")

def test_ultrasonics_with_switch():
    """Testet Ultraschall-Sensoren mit Schalter-Steuerung."""
    print("=" * 60)
    print("Ultraschall-Sensor Test (Schalter-Steuerung)")
    print("=" * 60)
    print("Drücke den Schalter zum Starten/Stoppen")
    print("Drücke STRG+C zum Beenden")
    print("=" * 60)
    print()
    
    running = False
    
    try:
        while True:
            if schalter_gedrueckt():
                running = not running
                if running:
                    print("\n>>> Messung gestartet <<<\n")
                else:
                    print("\n>>> Messung gestoppt <<<\n")
                time.sleep(0.3)  # Entprellung
            
            if running:
                distance_vorne, distance_rechts = sensor.read_ultrasonics()
                
                d1_str = f"{distance_vorne:6.2f} cm" if distance_vorne is not None else "  Timeout"
                d2_str = f"{distance_rechts:6.2f} cm" if distance_rechts is not None else "  Timeout"
                
                print(f"Vorne: {d1_str} | Rechts: {d2_str}")
                time.sleep(0.1)
            else:
                time.sleep(0.05)
                
    except KeyboardInterrupt:
        print("\n\nTest beendet durch Benutzer (STRG+C).")

def test_ultrasonics_single():
    """Führt einen einzelnen Test beider Sensoren durch."""
    print("=" * 60)
    print("Ultraschall-Sensor Einzelmessung")
    print("=" * 60)
    
    distance_vorne, distance_rechts = sensor.read_ultrasonics()
    
    print(f"\nSensor 1 (vorne):  {distance_vorne if distance_vorne is not None else 'Timeout'} cm")
    print(f"Sensor 2 (rechts): {distance_rechts if distance_rechts is not None else 'Timeout'} cm")
    print()

def main():
    """Hauptmenü für verschiedene Testmodi."""
    try:
        print("\n" + "=" * 60)
        print("Ultraschall-Sensor Testmenü")
        print("=" * 60)
        print("1: Kontinuierliche Messung")
        print("2: Messung mit Schalter-Steuerung")
        print("3: Einzelmessung")
        print("=" * 60)
        
        choice = input("\nWähle einen Modus (1-3): ").strip()
        
        if choice == "1":
            test_ultrasonics_continuous()
        elif choice == "2":
            test_ultrasonics_with_switch()
        elif choice == "3":
            test_ultrasonics_single()
        else:
            print("Ungültige Auswahl!")
            
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        GPIO.cleanup()
        print("GPIO bereinigt.")

if __name__ == "__main__":
    main()
