#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

OUT_A = 22
OUT_B = 27
WINDOW = 0.005   # 5 ms Messfenster

GPIO.setmode(GPIO.BCM)
GPIO.setup(OUT_A, GPIO.IN)
GPIO.setup(OUT_B, GPIO.IN)

edges_a = 0
edges_b = 0

def cb_a(channel):
    global edges_a 
    edges_a += 1

def cb_b(channel):
    global edges_b
    edges_b += 1

GPIO.add_event_detect(OUT_A, GPIO.RISING, callback=cb_a)
GPIO.add_event_detect(OUT_B, GPIO.RISING, callback=cb_b)

def get_sensor(sensor):
    """
    Liest die Frequenz eines Sensors aus.
    
    Args:
        sensor (str): 'links' oder 'rechts'
    
    Returns:
        float: Gemessene Frequenz in Hz
    """
    global edges_a, edges_b
    
    if sensor.lower() == 'l':
        edges_a = 0
        start = time.time()
        time.sleep(WINDOW)
        dt = time.time() - start
        return edges_a / (2.0 * dt)
    
    elif sensor.lower() == 'r':
        edges_b = 0
        start = time.time()
        time.sleep(WINDOW)
        dt = time.time() - start
        return edges_b / (2.0 * dt)
    
    else:
        raise ValueError("Sensor muss 'l' oder 'r' sein")

# Beispiel für die Verwendung:
if __name__ == "__main__":
    try:
        while True:
            # Beide Sensoren einzeln abfragen
            freq_links = get_sensor('l')
            freq_rechts = get_sensor('r')
            
            print(f"Links: {freq_links:.0f} Hz, Rechts: {freq_rechts:.0f} Hz")
            
            time.sleep(0.001)

    except KeyboardInterrupt:
        GPIO.cleanup()
