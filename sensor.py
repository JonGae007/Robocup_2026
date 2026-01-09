#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

OUT_A = 22  # Ausgang Sensor links
OUT_B = 27  # Ausgang Sensor rechts

# Neue Pinbelegung (BCM) für zwei TCS230/TCS3200-Module, je 4 Steuerleitungen:
# Sensor links:  S0=4, S1=5, S2=6, S3=7
# Sensor rechts: S0=8, S1=9, S2=10, S3=11
# Falls du andere Pins nutzt, hier anpassen; None lassen, wenn extern (z.B. ESP).
LEFT_PINS = {"S0": 4, "S1": 5, "S2": 6, "S3": 7}
RIGHT_PINS = {"S0": 8, "S1": 9, "S2": 10, "S3": 11}

WINDOW = 0.002   # kürzeres Messfenster für schnellere Abtastrate

# Frequenz-Scaling-Kombinationen für S0/S1:
# HIGH/HIGH = 100 %, HIGH/LOW = 20 %, LOW/HIGH = 2 %, LOW/LOW = Power-Down
SCALING = {
    "100": (GPIO.HIGH, GPIO.HIGH),
    "20": (GPIO.HIGH, GPIO.LOW),
    "2": (GPIO.LOW, GPIO.HIGH),
    "off": (GPIO.LOW, GPIO.LOW),
}

# Farbfilter-Kombinationen für S2/S3:
# S2 LOW,  S3 LOW  -> Rot
# S2 LOW,  S3 HIGH -> Blau
# S2 HIGH, S3 LOW  -> Klar (ohne Filter)
# S2 HIGH, S3 HIGH -> Grün
COLOR_FILTERS = {
    "r": (GPIO.LOW, GPIO.LOW),
    "g": (GPIO.HIGH, GPIO.HIGH),
    "b": (GPIO.LOW, GPIO.HIGH),
    "c": (GPIO.HIGH, GPIO.LOW),
}

GPIO.setmode(GPIO.BCM)
GPIO.setup(OUT_A, GPIO.IN)
GPIO.setup(OUT_B, GPIO.IN)

def _setup_control_pins(mapping):
    for pin in mapping.values():
        if pin is not None:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

_setup_control_pins(LEFT_PINS)
_setup_control_pins(RIGHT_PINS)

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

def _measure_window():
    """Misst beide Sensor-Ausgänge parallel im vorgegebenen Zeitfenster."""
    global edges_a, edges_b
    edges_a = 0
    edges_b = 0
    start = time.perf_counter()
    time.sleep(WINDOW)
    dt = time.perf_counter() - start
    freq_left = edges_a / (2.0 * dt)
    freq_right = edges_b / (2.0 * dt)
    return freq_left, freq_right

def _set_scaling(scale="100"):
    """Setzt S0/S1 auf das gewünschte Frequenz-Scaling (beide Sensoren)."""
    if scale not in SCALING:
        raise ValueError("Scaling muss '100', '20', '2' oder 'off' sein")
    s0s1 = SCALING[scale]
    for mapping in (LEFT_PINS, RIGHT_PINS):
        if mapping["S0"] is None or mapping["S1"] is None:
            continue
        GPIO.output(mapping["S0"], s0s1[0])
        GPIO.output(mapping["S1"], s0s1[1])

def _set_filter(color):
    """Schaltet S2/S3 auf den gewünschten Filter für beide Sensoren."""
    if color not in COLOR_FILTERS:
        raise ValueError("Farbe muss 'r', 'g', 'b' oder 'c' sein")
    s2_state, s3_state = COLOR_FILTERS[color]
    for mapping in (LEFT_PINS, RIGHT_PINS):
        if mapping["S2"] is None or mapping["S3"] is None:
            continue
        GPIO.output(mapping["S2"], s2_state)
        GPIO.output(mapping["S3"], s3_state)
    time.sleep(0.0005)  # kurze Settling-Zeit nach Umschalten

def read_color(color):
    """
    Liefert Frequenzen für links/rechts bei gesetztem Farbfilter.

    Args:
        color (str): 'r', 'g', 'b' oder 'c' (clear)

    Returns:
        tuple: (freq_links, freq_rechts) in Hz
    """
    _set_filter(color)
    return _measure_window()

def read_all_colors(order=("r", "g", "b", "c")):
    """
    Liest nacheinander alle gewünschten Farbfilter aus und gibt ein Dict zurück.

    Returns:
        dict: z.B. {"r": (l, r), "g": (l, r), ...}
    """
    results = {}
    for color in order:
        results[color] = read_color(color)
    return results

def set_scaling(scale="100"):
    """Öffentliche API, um S0/S1-Scaling einzustellen."""
    _set_scaling(scale)

# --- Ultraschall (HC-SR04) Unterstützung ---
# Pins (BCM) wie vom Benutzer angegeben
US1_TRIG = 23
US1_ECHO = 24
US2_TRIG = 17
US2_ECHO = 27

# Setup der Ultraschall-Pins
GPIO.setup(US1_TRIG, GPIO.OUT)
GPIO.setup(US1_ECHO, GPIO.IN)
GPIO.setup(US2_TRIG, GPIO.OUT)
GPIO.setup(US2_ECHO, GPIO.IN)
GPIO.output(US1_TRIG, GPIO.LOW)
GPIO.output(US2_TRIG, GPIO.LOW)

def _pulse_high(pin, duration=0.00001):
    """Sendet einen kurzen HIGH-Puls auf `pin` (Trigger)."""
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

def _measure_distance(trigger_pin, echo_pin, timeout=0.02):
    """Misst die Entfernung in cm für einen einzelnen HC-SR04.

    Gibt `None` zurück, wenn kein Echo innerhalb des Timeouts empfangen wird.
    """
    # Trigger senden
    _pulse_high(trigger_pin)

    start_time = time.time()
    # Warte auf steigende Flanke (Echo beginnt)
    while GPIO.input(echo_pin) == 0:
        if time.time() - start_time > timeout:
            return None
    t_start = time.time()

    # Warte auf fallende Flanke (Echo endet)
    while GPIO.input(echo_pin) == 1:
        if time.time() - t_start > timeout:
            return None
    t_end = time.time()

    dt = t_end - t_start
    # Schallgeschwindigkeit ~34300 cm/s; Strecke hin+zurück => /2
    distance_cm = (dt * 34300.0) / 2.0
    return distance_cm

def read_ultrasonics():
    """Liest beide Ultraschall-Sensoren und gibt ein Tupel (d1, d2) zurück.

    Werte sind in cm oder `None` bei Timeouts.
    """
    d1 = _measure_distance(US1_TRIG, US1_ECHO)
    time.sleep(0.01)
    d2 = _measure_distance(US2_TRIG, US2_ECHO)
    return d1, d2

# Beispiel für die Verwendung:
if __name__ == "__main__":
    try:
        _set_scaling("100")  # 100 % Output-Scaling; nach Bedarf anpassen
        while True:
            all_values = read_all_colors()
            print(
                f"R L/R: {all_values['r'][0]:.0f}/{all_values['r'][1]:.0f} Hz | "
                f"G L/R: {all_values['g'][0]:.0f}/{all_values['g'][1]:.0f} Hz | "
                f"B L/R: {all_values['b'][0]:.0f}/{all_values['b'][1]:.0f} Hz | "
                f"C L/R: {all_values['c'][0]:.0f}/{all_values['c'][1]:.0f} Hz"
            )
            time.sleep(0.01)

    except KeyboardInterrupt:
        GPIO.cleanup()
