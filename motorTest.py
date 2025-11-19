#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import threading
import sys
import tty
import termios

# Motor-Pins (BCM)
# VR = vorne rechts, HR = hinten rechts, VL = vorne links, HL = hinten links
HR_IN1 = 16  # vorne rechts (getauscht)
HR_IN2 = 12
VR_IN1 = 20  # hinten rechts (getauscht)
VR_IN2 = 13
VL_IN1 = 21  # vorne links (getauscht)
VL_IN2 = 18
HL_IN1 = 26  # hinten links (getauscht)
HL_IN2 = 19


MOTOR_PINS = [VR_IN1, VR_IN2,
              HR_IN1, HR_IN2,
              VL_IN1, VL_IN2,
              HL_IN1, HL_IN2]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pins als Output initialisieren
for p in MOTOR_PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, GPIO.LOW)

# PWM-Objekte (auf IN1 pins) erstellen
PWM_FREQ = 1000
pwms = {}
for pin in (VR_IN1, HR_IN1, VL_IN1, HL_IN1):
    pwms[pin] = GPIO.PWM(pin, PWM_FREQ)
    pwms[pin].start(0)

# Mapping von Tasten zu Motor-Pins
# 1 -> vorne links (VL), 2 -> vorne rechts (VR), 3 -> hinten links (HL), 4 -> hinten rechts (HR)
KEY_TO_MOTOR = {
    '1': (VL_IN1, VL_IN2),
    '2': (VR_IN1, VR_IN2),
    '3': (HL_IN1, HL_IN2),
    '4': (HR_IN1, HR_IN2),
}

_ramp_thread = None
_ramp_stop_event = None
_ramp_lock = threading.Lock()

def _set_forward(pin_in1, pin_in2):
    GPIO.output(pin_in2, GPIO.LOW)

def _stop_motor(pin_in1, pin_in2):
    # duty 0 + beide low
    pwms[pin_in1].ChangeDutyCycle(0)
    GPIO.output(pin_in1, GPIO.LOW)
    GPIO.output(pin_in2, GPIO.LOW)

def stop_all():
    global _ramp_stop_event
    # stop background ramp
    if _ramp_stop_event is not None:
        _ramp_stop_event.set()
    for (in1, in2) in KEY_TO_MOTOR.values():
        _stop_motor(in1, in2)

def _ramp_speed_loop(pin_in1, pin_in2, stop_event, min_duty=10, max_duty=90, step=2, delay=0.05):
    # sorgt dafür, dass IN2 low ist (Vorwärts) und variiert DutyCycle vorwärts
    _set_forward(pin_in1, pin_in2)
    duty = min_duty
    up = True
    while not stop_event.is_set():
        pwms[pin_in1].ChangeDutyCycle(duty)
        if up:
            duty += step
            if duty >= max_duty:
                duty = max_duty
                up = False
        else:
            duty -= step
            if duty <= min_duty:
                duty = min_duty
                up = True
        time.sleep(delay)
    # Ende: Motor sicher stoppen
    _stop_motor(pin_in1, pin_in2)

def start_ramp_for_key(key):
    global _ramp_thread, _ramp_stop_event
    if key not in KEY_TO_MOTOR:
        return
    in1, in2 = KEY_TO_MOTOR[key]
    with _ramp_lock:
        # stoppe existierenden Thread
        if _ramp_stop_event is not None:
            _ramp_stop_event.set()
        _ramp_stop_event = threading.Event()
        _ramp_thread = threading.Thread(target=_ramp_speed_loop, args=(in1, in2, _ramp_stop_event), daemon=True)
        _ramp_thread.start()

def read_single_key():
    # Liest eine einzelne Taste ohne Enter (Unix)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def print_instructions():
    print("Wähle per Taste:")
    print("  1 - vorne links (rhythmisch schneller/langsamer vorwärts)")
    print("  2 - vorne rechts")
    print("  3 - hinten links")
    print("  4 - hinten rechts")
    print("  5 - alle stoppen")
    print("  q - beenden")
    print("Drücke die Taste (ohne Enter).\n")

def main_loop():
    print_instructions()
    try:
        while True:
            print("Taste:", end=' ', flush=True)
            try:
                ch = read_single_key()
            except Exception:
                # Fallback: Eingabe mit Enter
                ch = input().strip()[:1]
            print(ch)
            if ch in ('q', 'Q'):
                print("Beende...")
                break
            if ch in ('1','2','3','4'):
                print(f"Starte Motor für Taste {ch}...")
                start_ramp_for_key(ch)
            elif ch == '5':
                print("Stoppe alle Motoren...")
                stop_all()
            else:
                print("Unbekannte Taste. Nutze 1-5 oder q.")
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer")
    finally:
        stop_all()
        GPIO.cleanup()

if __name__ == '__main__':
    main_loop()