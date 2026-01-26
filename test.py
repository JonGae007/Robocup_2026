#!/usr/bin/env python3
"""Testprogramm: Motoren langsam beschleunigen und abbremsen"""

import time
from motor import speedcontrol, stop, cleanup

def motor_ramp_test():
    """Motoren mit konstanten Geschwindigkeiten testen"""
    try:
        print("Motor Test startet...")
        print("Links: 60% | Rechts: 1%")
        
        # Links 60%, Rechts 1%
        speedcontrol(60, 10)
        
        # Laufen lassen (Strg+C zum Beenden)
        print("Motoren laufen... (Strg+C zum Beenden)")
        while True:
            time.sleep(1)
        
        print("\nTest abgeschlossen!")
        
    except KeyboardInterrupt:
        print("\nTest durch Benutzer abgebrochen")
    
    finally:
        # Motoren stoppen und aufräumen
        stop()
        cleanup()
        print("Motoren gestoppt")

if __name__ == "__main__":
    motor_ramp_test()
