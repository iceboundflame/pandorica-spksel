#!/usr/bin/python

# Control script for audio relays: turn specified channels on and others off.
#
# Copyright (C) 2013-2014 David Liu (http://iceboundflame.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

for room, onoff in enumerate(onoff_map):
	sel_pin = PIN_MAP[room][onoff]
	GPIO.output(sel_pin, GPIO.LOW)

GPIO.cleanup()
