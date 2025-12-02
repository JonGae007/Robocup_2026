#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys
import tty
import termios
import select

# Motor-Pins (BCM)
HR_IN1 = 16 # vorne rechts (getauscht)
HR_IN2 = 12
VR_IN1 = 13  # hinten rechts (getauscht)
VR_IN2 = 20
VL_IN1 = 18  # vorne links (getauscht)
VL_IN2 = 21
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

PWM_FREQ = 1000
SPEED = 40  # DutyCycle

pwms = {}
# Create PWM objects for both IN pins so we can PWM forward or reverse
for pin in MOTOR_PINS:
    pwms[pin] = GPIO.PWM(pin, PWM_FREQ)
    pwms[pin].start(0)

# Map wheel names to their pin pairs (in1, in2)
WHEELS = {
    'VR': (VR_IN1, VR_IN2),
    'HR': (HR_IN1, HR_IN2),
    'VL': (VL_IN1, VL_IN2),
    'HL': (HL_IN1, HL_IN2),
}

# Current and target speeds for each wheel (percent, -100..100)
current_speeds = {w: 0 for w in WHEELS}
target_speeds = {w: 0 for w in WHEELS}

# Ramping settings
RAMP_STEP = 5        # percent per update step
RAMP_DELAY = 0.02    # seconds between ramp steps

# Hold time for keyboard (so key-repeat gaps don't cause instant stop)
HOLD_TIME = 0.18  # seconds


# -------- Motorfunktionen (smooth) --------

def set_wheel_speed(wheel, percent):
    """Set wheel speed in percent (-100..100). Positive -> IN1 PWM, Negative -> IN2 PWM."""
    in1, in2 = WHEELS[wheel]
    pct = max(-100, min(100, int(percent)))
    if pct >= 0:
        pwms[in1].ChangeDutyCycle(pct)
        pwms[in2].ChangeDutyCycle(0)
    else:
        pwms[in1].ChangeDutyCycle(0)
        pwms[in2].ChangeDutyCycle(-pct)


def update_speeds_once():
    """Move current_speeds towards target_speeds by RAMP_STEP and apply to hardware."""
    changed = False
    for w in current_speeds:
        cur = current_speeds[w]
        tgt = target_speeds[w]
        if cur == tgt:
            continue
        changed = True
        if cur < tgt:
            cur = min(tgt, cur + RAMP_STEP)
        else:
            cur = max(tgt, cur - RAMP_STEP)
        current_speeds[w] = cur
        set_wheel_speed(w, cur)
    if changed:
        time.sleep(RAMP_DELAY)


def set_targets_for_command(cmd):
    """Set target_speeds dict according to a command key."""
    if cmd == 'w':
        for w in target_speeds:
            target_speeds[w] = SPEED
    elif cmd == 'a':
        # rotate left: right wheels forward, left wheels backward
        target_speeds['VR'] = SPEED
        target_speeds['HR'] = SPEED
        target_speeds['VL'] = -SPEED
        target_speeds['HL'] = -SPEED
    elif cmd == 'd':
        # rotate right: left wheels forward, right wheels backward
        target_speeds['VR'] = -SPEED
        target_speeds['HR'] = -SPEED
        target_speeds['VL'] = SPEED
        target_speeds['HL'] = SPEED
    else:
        # stop
        for w in target_speeds:
            target_speeds[w] = 0


def stop_all():
    for w in target_speeds:
        target_speeds[w] = 0
    # ramp down to zero immediately
    while any(current_speeds[w] != 0 for w in current_speeds):
        update_speeds_once()


# -------- Tastenerkennung --------

def read_key_timeout(timeout=0.05):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if r:
            return sys.stdin.read(1)
        else:
            return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# -------- Hauptprogramm --------

def main():
    print("Steuerung:")
    print("  W = vorwärts")
    print("  A = links drehen")
    print("  D = rechts drehen")
    print("  Q = beenden\n")

    key = None
    last_key = None
    last_key_time = 0

    try:
        while True:
            ch = read_key_timeout(0.05)
            now = time.time()

            if ch is not None:
                if ch.lower() == 'q':
                    print("Beende...")
                    break
                last_key = ch.lower()
                last_key_time = now
            else:
                # keep last key for a short HOLD_TIME to avoid jitter from key repeats
                if last_key is not None and (now - last_key_time) <= HOLD_TIME:
                    pass
                else:
                    last_key = None

            # set targets and ramp once
            set_targets_for_command(last_key)
            update_speeds_once()

            # small idle to yield
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        stop_all()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
    #put motorTest.py