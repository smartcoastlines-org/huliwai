#http://effbot.org/tkinterbook/tkinter-classes.htm
from tkinter import *
import logging, time
from serial import Serial
from common import get_logger_name, get_flash_id, read_vbatt
from common import serial_port_best_guess, save_default_port
from dev.set_rtc import set_rtc, read_rtc


print('Detected ports:')
DEFAULT_PORT = serial_port_best_guess(prompt=True)
print('- - -')
PORT = input('PORT=? (default={})'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT
print(PORT)

with Serial(PORT, 115200, timeout=1) as ser:
    save_default_port(PORT)


class App:
    def __init__(self, master):
        
        row1 = Frame(master)
        row1.pack()

        row_status = Frame(master)
        row_status.pack()

        row_sensors = Frame(master)
        row_sensors.pack()
        
        row_memory = Frame(master)
        row_memory.pack()

        row_led = Frame(master)
        row_led.pack()

        row_config = Frame(master)
        row_config.pack()

        row_logging = Frame(master)
        row_logging.pack()

        self.label1 = StringVar()
        self.label = Label(row1, textvariable=self.label1)
        self.label.pack(side=LEFT)

        self.get_name = Button(row_status, text='GET NAME', command=self.get_name)
        self.get_name.pack(side=LEFT)

        self.get_id = Button(row_status, text='GET ID', command=self.get_id)
        self.get_id.pack(side=LEFT)

        self.get_vbatt = Button(row_status, text='READ BATTERY VOLTAGE', command=self.get_vbatt)
        self.get_vbatt.pack(side=LEFT)

        self.read_temperature = Button(row_sensors, text='READ TEMPERATURE', command=self.read_temperature)
        self.read_temperature.pack(side=LEFT)

        self.read_pressure = Button(row_sensors, text='READ PRESSURE', command=self.read_pressure)
        self.read_pressure.pack(side=LEFT)

        self.read_ambient_lx = Button(row_sensors, text='READ AMBIENT', command=self.read_ambient_lx)
        self.read_ambient_lx.pack(side=LEFT)

        self.read_memory = Button(row_memory, text='EXTRACT DATA', command=self.read_memory)
        self.read_memory.pack(side=LEFT)

        self.clear_memory = Button(row_memory, text='CLEAR MEMORY', command=self.clear_memory)
        self.clear_memory.pack(side=LEFT)

        self.red_led_on = Button(row_led, text='RED ON', fg='red', command=self.red_led_on)
        self.red_led_on.pack(side=LEFT)

        self.red_led_off = Button(row_led, text='RED OFF', command=self.red_led_off)
        self.red_led_off.pack(side=LEFT)

        self.green_led_on = Button(row_led, text='GREEN ON', fg='green', command=self.green_led_on)
        self.green_led_on.pack(side=LEFT)

        self.green_led_off = Button(row_led, text='GREEN OFF', command=self.green_led_off)
        self.green_led_off.pack(side=LEFT)

        self.blue_led_on = Button(row_led, text='BLUE ON', fg='blue', command=self.blue_led_on)
        self.blue_led_on.pack(side=LEFT)

        self.blue_led_off = Button(row_led, text='BLUE OFF', command=self.blue_led_off)
        self.blue_led_off.pack(side=LEFT)


        self.v = IntVar()
        self.v.set(2)
        self.radio1 = Radiobutton(row_config, text='0.2 second', variable=self.v, value=0)
        self.radio1.pack(anchor=W)
        self.radio2 = Radiobutton(row_config, text='1 second', variable=self.v, value=1)
        self.radio2.pack(anchor=W)
        self.radio3 = Radiobutton(row_config, text='60 second', variable=self.v, value=2)
        self.radio3.pack(anchor=W)

        self.set_logging_interval = Button(row_config, text='SET SAMPLING INTERVAL', command=self.set_logging_interval)
        self.set_logging_interval.pack(side=LEFT)
        
        self.set_clock = Button(row_logging, text='SET CLOCK', command=self.set_clock)
        self.set_clock.pack(side=LEFT)

        self.start_logging = Button(row_logging, text='START Logging', command=self.start_logging)
        self.start_logging.pack(side=LEFT)

        self.stop_logging = Button(row_logging, text='STOP Logging', command=self.stop_logging)
        self.stop_logging.pack(side=LEFT)

        #self.button = Button(row_status, text='QUIT', fg='red', command=row.quit)
        #self.button.pack(side=LEFT)

        #self.text = Text(row_logging)
        #self.text.pack(side=LEFT)

    def get_name(self):
        logging.debug('get_name')
        with Serial(PORT, 115200, timeout=1) as ser:
            self.label1.set(get_logger_name(ser))

    def get_id(self):
        logging.debug('get_id')
        with Serial(PORT, 115200, timeout=1) as ser:
            self.label1.set(get_flash_id(ser))
    
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

    def get_vbatt(self):
        logging.debug('get_vbatt')
        with Serial(PORT, 115200, timeout=1) as ser:
            self.label1.set(str(read_vbatt(ser)) + 'V')

    def read_temperature(self):
        logging.debug('read_temperature')
        with Serial(PORT, 115200, timeout=1) as ser:
            ser.write(b'read_temperature')
            self.label1.set(ser.readline().decode().strip())

    def read_pressure(self):
        logging.debug('read_pressure')
        with Serial(PORT, 115200, timeout=1) as ser:
            ser.write(b'read_pressure')
            self.label1.set(ser.readline().decode().strip())

    def read_ambient_lx(self):
        logging.debug('read_ambient_lx')
        with Serial(PORT, 115200, timeout=1) as ser:
            ser.write(b'read_ambient_lx')
            r = ser.readline().decode().strip().split(',')[0]
            self.label1.set(r)

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

root = Tk()

app = App(root)

root.mainloop()
#root.destroy()




