#!/usr/bin/env python3
"""Simple motor command API.

Use `forward(speed)`, `backward(speed)`, `turn_left(speed)`,
`turn_right(speed)`, and `stop()` from your main program.

Speeds are in range 0..100 (percent). Negative values work for
`set_wheel` but the convenience functions accept positive speeds.
"""
from setup import setup_motor

# create controller on import; you can override by calling
# `setup_motor` yourself with custom pin defaults or pwm_freq.
controller = setup_motor()

WHEELS = ['VR', 'HR', 'VL', 'HL']

def set_wheel(wheel, speed):
	controller.set_wheel(wheel, speed)

def forward(speed=80):
	for w in WHEELS:
		controller.set_wheel(w, speed)

def backward(speed=80):
	for w in WHEELS:
		controller.set_wheel(w, -speed)

def turn_right(speed=60):
	# right side reverse, left side forward -> turn right (clockwise)
	controller.set_wheel('VR', -speed)
	controller.set_wheel('HR', -speed)
	controller.set_wheel('VL', speed)
	controller.set_wheel('HL', speed)

def turn_left(speed=60):
	# left side reverse, right side forward -> turn left (counter-clockwise)
	controller.set_wheel('VR', speed)
	controller.set_wheel('HR', speed)
	controller.set_wheel('VL', -speed)
	controller.set_wheel('HL', -speed)

def stop():
	controller.stop()

def cleanup():
	controller.cleanup()
