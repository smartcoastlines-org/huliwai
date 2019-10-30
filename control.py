# Just for fun.
#
#http://effbot.org/tkinterbook/tkinter-classes.htm
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import tkinter as tk
import logging, time, sys
from functools import partial
from serial import Serial
from common import get_logger_name, get_flash_id, read_vbatt
from common import serial_port_best_guess, save_default_port
from dev.set_rtc import set_rtc, read_rtc, ts2dt


print('Detected ports:')
DEFAULT_PORT = serial_port_best_guess(prompt=True)
print('- - -')
PORT = input('Which one to use? (default={})'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT
print(PORT)

with Serial(PORT, 115200, timeout=1) as ser:
    save_default_port(PORT)


def get_name(ent):
    logging.debug('get_name')
    with Serial(PORT, 115200, timeout=1) as ser:
        ent.delete(0, tk.END)
        ent.insert(0, get_logger_name(ser))

def get_id(ent):
    logging.debug('get_id')
    with Serial(PORT, 115200, timeout=1) as ser:
        ent.delete(0, tk.END)
        ent.insert(0, get_flash_id(ser))

def read_battery_voltage(ent):
    logging.debug('get_vbatt')
    with Serial(PORT, 115200, timeout=1) as ser:
        ent.delete(0, tk.END)
        ent.insert(0, '{} V'.format(read_vbatt(ser)))

def read_clock(ent):
    logging.debug('read_clock')
    with Serial(PORT, 115200, timeout=1) as ser:
        ent.delete(0, tk.END)
        ent.insert(0, '{}'.format(ts2dt(read_rtc(ser))))

def set_clock(ent):
    logging.debug('set_clock')
    with Serial(PORT, 115200, timeout=1) as ser:
        set_rtc(ser)

def read_temperature(ent):
    logging.debug('read_temperature')
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'read_temperature')
        ent.delete(0, tk.END)
        v = ser.readline().decode().strip()
        v = v.split(' ')[0]
        ent.insert(0, '{} \u00b0C'.format(v))

def read_pressure(ent):
    logging.debug('read_pressure')
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'read_pressure')
        ent.delete(0, tk.END)
        v = ser.readline().decode().strip()
        ent.insert(0, v)

def read_ambient_lx(ent):
    logging.debug('read_ambient_lx')
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'read_ambient_lx')
        ent.delete(0, tk.END)
        ent.insert(0, ser.readline().decode().strip().split(',')[0])

def read_rgbw(ent):
    logging.debug('read_rgbw')
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'read_rgbw')
        ent.delete(0, tk.END)
        ent.insert(0, ser.readline().decode().strip())

def led_red(ent):
    logging.debug('led_red')
    if 'on' not in led_red.__dict__: led_red.on = True
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'red_led_on' if led_red.on else b'red_led_off')
    led_red.on = not led_red.on

def led_green(ent):
    logging.debug('led_green')
    if 'on' not in led_green.__dict__: led_green.on = True
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'green_led_on' if led_green.on else b'green_led_off')
    led_green.on = not led_green.on

def led_blue(ent):
    logging.debug('led_blue')
    if 'on' not in led_blue.__dict__: led_blue.on = True
    with Serial(PORT, 115200, timeout=1) as ser:
        ser.write(b'blue_led_on' if led_blue.on else b'blue_led_off')
    led_blue.on = not led_blue.on


class App:
    def __init__(self, master):
        self.B = [['READ NAME', get_name, True],
                  ['READ ID', get_id, True],
                  ['READ BATTERY VOLTAGE', read_battery_voltage, True],
                  ['READ CLOCK', read_clock, True],
                  ['SET CLOCK', set_clock, False],
                  ['READ TEMPERATURE', read_temperature, True],
                  ['READ PRESSURE', read_pressure, True],
                  ['READ LIGHT', read_ambient_lx, True],
                  ['READ RGB+W', read_rgbw, True],
                  ['RED', led_red, False],
                  ['GREEN', led_green, False],
                  ['BLUE', led_blue, False],
                  ]

        for b in self.B:
            row = tk.Frame(master)
            ent = None
            if b[2]:
                ent = tk.Entry(row)
            # lambda is late-binding. This won't fly.
            #btn = tk.Button(row, text=b[0], width=24, command=lambda ent=ent: b[1](ent))
            btn = tk.Button(row, text=b[0], width=24, command=partial(b[1], ent))
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            btn.pack(side=tk.LEFT)
            if b[2]:
                ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

    def read_memory(self):
        logging.debug('read_memory')

    def clear_memory(self):
        logging.debug('clear_memory')

    def start_logging(self):
        logging.debug('start_logging')

    def stop_logging(self):
        logging.debug('stop_logging')

    def set_logging_interval(self):
        print(self.v.get())

    def set_clock(self):
        logging.debug('set_rtc')
        with Serial(PORT, 115200, timeout=1) as ser:
            set_rtc(ser, time.time())
            self.label1.set(read_rtc(ser))

    def red_led_on(self):
        logging.debug('red_led_on')
        Serial(PORT, 115200, timeout=1).write(b'red_led_on')

    def red_led_off(self):
        logging.debug('red_led_off')
        Serial(PORT, 115200, timeout=1).write(b'red_led_off')

    def green_led_on(self):
        logging.debug('green_led_on')
        Serial(PORT, 115200, timeout=1).write(b'green_led_on')

    def green_led_off(self):
        logging.debug('green_led_off')
        Serial(PORT, 115200, timeout=1).write(b'green_led_off')

    def blue_led_on(self):
        logging.debug('blue_led_on')
        Serial(PORT, 115200, timeout=1).write(b'blue_led_on')

    def blue_led_off(self):
        logging.debug('blue_led_off')
        Serial(PORT, 115200, timeout=1).write(b'blue_led_off')


logging.basicConfig(level=logging.DEBUG)

root = tk.Tk()
app = App(root)
root.mainloop()
#root.destroy()
