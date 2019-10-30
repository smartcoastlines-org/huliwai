# fun with LEDs
#
#
# MESH Lab
# University of Hawaii
# Copyright 2018 Stanley H.I. Lio
# hlio@hawaii.edu
import time
from itertools import cycle
from serial import Serial


cmds = cycle(['red_led_on', 'red_led_off', 'green_led_on', 'green_led_off', 'blue_led_on', 'blue_led_off'])


# find the serial port to use from user, from history, or make a guess
# if on Windows, print the list of COM ports
from common import serial_port_best_guess, save_default_port
DEFAULT_PORT = serial_port_best_guess(prompt=True)
PORT = input('PORT=? (default={}):'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT

with Serial(PORT, 115200, timeout=1) as ser:

    save_default_port(PORT)

    while True:
        ser.write(next(cmds).encode())
        time.sleep(0.1)
