# Set the logger's clock to UTC (using this machine's clock).
#
# ... depending on runtime, cost and accuracy of
# oscillator, the final version may not even have
# an RTC.
#
# MESH Lab
# University of Hawaii
# Copyright 2018 Stanley H.I. Lio
# hlio@hawaii.edu
import time, calendar, math
from datetime import datetime
from serial import Serial


def dt2ts(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return calendar.timegm(dt.timetuple()) + (dt.microsecond)*(1e-6)

def ts2dt(ts=None):
    if ts is None:
        ts = dt2ts()
    return datetime.utcfromtimestamp(ts)

def set_rtc(ser, t=None):
    if t is None:
        t = time.time()
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write('write_rtc{}\n'.format(math.floor(t)).encode())
    return ser.readline().decode()

def set_rtc_aligned(ser):
    # sync to the 10 millisecond? just for fun. the RTC only has 1s resolution.
    # there's no way to start/restart the RTC's internal one-second period on trigger.
    for i in range(2000):
        currenttime = time.time()
        if math.floor(currenttime*100)%100 == 0:      # it has just turned x.00y...
            #print(currenttime)
            return float(set_rtc(ser, currenttime))
        else:
            time.sleep(0.001)
    else:
        assert False, 'wut?'

def read_rtc(ser):
    ser.write(b'read_rtc')
    return float(ser.readline().decode().strip())


if '__main__' == __name__:

    # find the serial port to use from user, from history, or make a guess
    # if on Windows, print the list of COM ports
    from ..common import serial_port_best_guess, save_default_port
    DEFAULT_PORT = serial_port_best_guess(prompt=True)
    PORT = input('PORT=? (default={}):'.format(DEFAULT_PORT)).strip()
    # empty input, use default
    if '' == PORT:
        PORT = DEFAULT_PORT

    with Serial(PORT, 115200, timeout=1) as ser:
        # the simple way +/- 1s
        #currenttime = round(time.time())
        #ser.write('write_rtc{}\n'.format(currenttime).encode())

        oldrtctime = ts2dt(read_rtc(ser))
        print('Current device time: {}'.format(oldrtctime))

        set_rtc_aligned(ser)
        
        newrtctime = ts2dt(read_rtc(ser))
        print('Device time set to: {} (offset = {}s)'.format(newrtctime, (newrtctime - oldrtctime).total_seconds()))

        print('- - - - -')
        for i in range(5):
            rtctime = ts2dt(read_rtc(ser))
            print('Device time: {}'.format(rtctime))
            time.sleep(1)
