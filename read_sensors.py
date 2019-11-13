# Read all sensors and plot in real-time.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import time, functools, logging, calendar, math
from serial import Serial
from itertools import cycle
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np


logging.basicConfig(level=logging.WARNING)

fn = 'read_sensors_output.csv'


#cmds = cycle(['red_led_on', 'red_led_off', 'green_led_on', 'green_led_off', 'blue_led_on', 'blue_led_off'])

def q(ser, cmd, wait=True):
    """query"""
    ser.flushInput()
    ser.write(cmd.encode())
    if wait:
        return ser.readline().decode()
    return None


def dt2ts(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return calendar.timegm(dt.timetuple()) + (dt.microsecond)*(1e-6)


# find the serial port to use from user, from history, or make a guess
# if on Windows, print the list of COM ports
from common import serial_port_best_guess, save_default_port
DEFAULT_PORT = serial_port_best_guess(prompt=True)
PORT = input('PORT=? (default={}):'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT

with Serial(PORT, 115200, timeout=1) as ser,\
     open(fn, 'a', 1) as fout:

    save_default_port(PORT)

    q = functools.partial(q, ser)

    #tags = ['T_Deg\u00B0C', 'P_kPa', 'ambient_lux', 'ambient_white_lux', 'R_lux', 'G_lux', 'B_lux', 'W_lux']
    D = []
    while True:

        t, p, als_raw, als_white_raw, r, g, b, w = [float('nan')]*8

        try:
            line = q('read_temperature')
            t = float(line.replace('Deg.C', ''))
        except (IndexError, ValueError):
            print('No/invalid response (temperature)')

        try:
            line = q('read_pressure')
            p = float(line.replace('kPa', ''))
        except (IndexError, ValueError):
            print('No/invalid response (pressure)')

        try:
            line = q('read_ambient_lx')
            lux = line.split(',')[0].replace('lx', '')
            raw = line.split(',')[1]
            als_lux = float(lux)
            als_raw = int(raw)
        except (IndexError, ValueError):
            print('No/invalid response (ambient lx)')

        try:
            line = q('read_white_lx')
            lux = line.split(',')[0].replace('lx', '')
            raw = line.split(',')[1]
            als_white_lux = float(lux)
            als_white_raw = int(raw)
        except (IndexError, ValueError):
            print('No/invalid response (white lx)')

        try:
            line = q('read_rgbw')
            line = line.strip().split(',')
            r, g, b, w = [int(float(v)) for v in line]
        except (IndexError, ValueError):
            print('No/invalid response (rgbw)')

        if all(math.isnan(v) for v in [t, p, als_raw, als_white_raw, r, g, b, w]):
            continue
        #q(next(cmds), wait=False)
        #print(d)

        #ts = time.time()
        dt = datetime.now()
        tmp = [dt, t, p, als_raw, als_white_raw, r, g, b, w]
        D.append(list(tmp))
        tmp.insert(0, dt2ts(tmp[0]))
        fout.write(','.join([str(v) for v in tmp]) + '\n')
        #print(D)

        if len(D) < 1:
            continue
        
        DT, T, P, ALS_RAW, ALS_WHITE_RAW, R, G, B, W = list(zip(*D))
        
        plt.clf()

        ax1 = plt.subplot(411)
        plt.plot(DT, T, 'r.:', label='{:.3f} Deg.C'.format(t))
        #plt.annotate('{:.3f} Deg.C'.format(t), (0.6*len(D), t), size=20)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.ylabel('Deg\u00B0C')
        plt.legend(loc=2)
        plt.grid(True)

        ax2 = plt.subplot(412, sharex=ax1)
        plt.plot(DT, P, '.:', label='{:.2f} kPa'.format(p))
        #plt.annotate('{:.2f}'.format(p), (0.6*len(D), p), size=20)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.ylabel('kPa')
        plt.legend(loc=2)
        plt.grid(True)

# these are uint16, but I want to be able to use float('nan') when necessary, hence {:.0f} instead of {:d}
        ax3 = plt.subplot(413, sharex=ax1)
        plt.plot(DT, ALS_RAW, '.:', label='ALS: {:.0f} (raw)'.format(als_raw), alpha=0.5)
        #plt.annotate('{:d}'.format(als_raw), (0.5*len(D), als_raw), size=20)
        plt.plot(DT, ALS_WHITE_RAW, '.:', label='White: {:.0f} (raw)'.format(als_white_raw), alpha=0.5)
        #plt.annotate('{:d}'.format(als_white_raw), (0.6*len(D), als_white_raw), size=20)
        plt.setp(ax3.get_xticklabels(), visible=False)
        plt.ylabel('(raw count)')
        plt.legend(loc=2)
        plt.grid(True)

        plt.subplot(414, sharex=ax1)
        plt.plot(DT, R, 'r.:', label='R: {:.0f} (raw)'.format(r), alpha=0.5)
        #plt.annotate('{:d}'.format(r), (0.4*len(D), r), color='r', size=20)
        plt.plot(DT, G, 'g.:', label='G: {:.0f} (raw)'.format(g), alpha=0.5)
        #plt.annotate('{:d}'.format(g), (0.5*len(D), g), color='g', size=20)
        plt.plot(DT, B, 'b.:', label='B: {:.0f} (raw)'.format(b), alpha=0.5)
        #plt.annotate('{:d}'.format(b), (0.6*len(D), b), color='b', size=20)
        plt.plot(DT, W, 'k.:', label='W: {:.0f} (raw)'.format(w), alpha=0.2)
        #plt.annotate('{:d}'.format(w), (0.7*len(D), w), color='k', size=20)
        plt.ylabel('(raw count)')

        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(DateFormatter('%b %d %H:%M:%S'))
        #plt.xlabel('Time')
        plt.legend(loc=2)
        plt.grid(True)

        plt.pause(0.001)

        while len(D) > 1000:
            D.pop(0)
