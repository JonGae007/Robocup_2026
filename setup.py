#!/usr/bin/env python3
import RPi.GPIO as GPIO

class MotorController:
	def __init__(self, pwm_freq=1000, defaults=None):
		if defaults is None:
			defaults = {
				'HR_IN1': 16,
				'HR_IN2': 12,
				'VR_IN1': 20,
				'VR_IN2': 13,
				'VL_IN1': 18,
				'VL_IN2': 21,
				'HL_IN1': 26,
				'HL_IN2': 19,
			}
		self.defaults = defaults
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		# unique motor pins
		motor_pins = list({v for v in self.defaults.values()})
		for p in motor_pins:
			GPIO.setup(p, GPIO.OUT)
			GPIO.output(p, GPIO.LOW)

		self.pwms = {}
		for pin in motor_pins:
			pwm = GPIO.PWM(pin, pwm_freq)
			pwm.start(0)
			self.pwms[pin] = pwm

		self.WHEELS = {
			'VR': (self.defaults['VR_IN1'], self.defaults['VR_IN2']),
			'HR': (self.defaults['HR_IN1'], self.defaults['HR_IN2']),
			'VL': (self.defaults['VL_IN1'], self.defaults['VL_IN2']),
			'HL': (self.defaults['HL_IN1'], self.defaults['HL_IN2']),
		}

	def set_wheel(self, wheel, speed):
		"""Set a single wheel speed.

		speed: -100..100 (negative = reverse)
		"""
		if wheel not in self.WHEELS:
			raise ValueError(f'Unknown wheel: {wheel}')
		p1, p2 = self.WHEELS[wheel]
		speed = int(max(-100, min(100, speed)))
		if speed > 0:
			self.pwms[p1].ChangeDutyCycle(speed)
			self.pwms[p2].ChangeDutyCycle(0)
		elif speed < 0:
			self.pwms[p1].ChangeDutyCycle(0)
			self.pwms[p2].ChangeDutyCycle(-speed)
		else:
			self.pwms[p1].ChangeDutyCycle(0)
			self.pwms[p2].ChangeDutyCycle(0)

	def stop(self):
		for pwm in self.pwms.values():
			pwm.ChangeDutyCycle(0)

	def cleanup(self):
		for pwm in self.pwms.values():
			pwm.stop()
		GPIO.cleanup()


def setup_motor(pwm_freq=1000, defaults=None):
	"""Return a pre-configured MotorController instance."""
	return MotorController(pwm_freq, defaults)


