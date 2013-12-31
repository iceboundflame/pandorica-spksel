#!/usr/bin/python

import sys

PIN_MAP = [ [11, 7], [12, 13], [15, 16], [22, 18], [24, 26] ]
PULSE_TIME = 0.050 # seconds

#
# Parse input parameters into onoff_map (list of 0/1=off/on for each room)
#

onoff_map = [0] * len(PIN_MAP)
for room in sys.argv[1:]:
	room = int(room)
	assert room >= 0 and room < len(PIN_MAP)
	onoff_map[room] = 1


#
# input validated, now pulse pins
#

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
for group in PIN_MAP:
	for pin in group:
		GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

for room, onoff in enumerate(onoff_map):
	sel_pin = PIN_MAP[room][onoff]
	print "Pulsing IO pin", sel_pin

	GPIO.output(sel_pin, GPIO.HIGH)
	time.sleep(PULSE_TIME)
	GPIO.output(sel_pin, GPIO.LOW)

GPIO.cleanup()
