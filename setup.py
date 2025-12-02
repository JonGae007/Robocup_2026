#!/usr/bin/env python3
import RPi.GPIO as GPIO

def setup_motor(pwm_freq=1000):
	defaults = {
		'HR_IN1': 16,
		'HR_IN2': 12,
		'VR_IN1': 13,
		'VR_IN2': 20,
		'VL_IN1': 18,
		'VL_IN2': 21,
		'HL_IN1': 26,
		'HL_IN2': 19,
	}

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	MOTOR_PINS = [
		13, 20,
		16, 12,
		18, 21,
		26, 19,
	]

	for p in MOTOR_PINS:
		GPIO.setup(p, GPIO.OUT)
		GPIO.output(p, GPIO.LOW)

	pwms = {}
	for pin in MOTOR_PINS:
		pwm = GPIO.PWM(pin, pwm_freq)
		pwm.start(0)
		pwms[pin] = pwm

	WHEELS = {
		'VR': (defaults['VR_IN1'], defaults['VR_IN2']),
		'HR': (defaults['HR_IN1'], defaults['HR_IN2']),
		'VL': (defaults['VL_IN1'], defaults['VL_IN2']),
		'HL': (defaults['HL_IN1'], defaults['HL_IN2']),
	}


