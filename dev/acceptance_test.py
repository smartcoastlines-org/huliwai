# Test the hardware of a logger.
#
# TODO: add SPI flash read write test
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESH Lab
# University of Hawaii
import time, functools, sys
sys.path.append('..')
from datetime import datetime
from serial import Serial
from common import serial_port_best_guess, save_default_port
from dev.set_rtc import set_rtc


def q(ser, cmd, wait_second=0):
    """query"""
    ser.flushInput()
    ser.write(cmd.encode())
    time.sleep(wait_second)
    return ser.readline().decode()

def qr(cmd, expected_response):
    """query-respond"""
    return q(cmd).strip() == expected_response

def check(cmd, test):
    if test(q(cmd)):
        print('PASS')
    else:
        print('FAIL! ({})'.format(cmd))


print('Detected ports:')
DEFAULT_PORT = serial_port_best_guess(prompt=True)
print('- - -')
PORT = input('Which one to use? (default={})'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT
print(PORT)

with Serial(PORT, 115200, timeout=1) as ser:

    q = functools.partial(q, ser)

    #check('spi_flash_get_jedec_id', lambda r: r.strip() == '4018')
    #check('spi_flash_get_manufacturer_id', lambda r: r.strip() == 'EF')
    #check('spi_flash_get_device_id', lambda r: r.strip() == '17')

    def ct(t):
        t = float(t.replace('Deg.C',''))
        return t > 10 and t < 40
    check('read_temperature', ct)


    def cp(p):
        p = float(p.replace('kPa',''))
        return p > 95 and p < 105
    check('read_pressure', cp)
    

    #ser.write('red_led_on'.encode())
    #ser.write('green_led_on'.encode())
    #ser.write('blue_led_on'.encode())
    time.sleep(0.1)
    def cl(lx):
        #print(lx)
        lx = float(lx.strip().split(',')[0].replace('lx',''))
        return lx >= 0 and lx <= 130e3
    check('read_ambient_lx', cl)

    
    def crgbw(r):
        #print(r)
        r = [float(v) for v in r.strip().split(',')]
        return all([rr >= 0 for rr in r])
    check('read_rgbw', crgbw)

    set_rtc(ser)

    def f(r):
        #print(datetime.fromtimestamp(int(r.strip())))
        return abs(float(r) - time.time()) < 5
    check('read_rtc', f)


    def f(r):
        Vcc, Vbatt = r.split(',')
        Vcc = float(Vcc)
        Vbatt = float(Vbatt)
        #print('Vcc = {}V, Vbatt = {}V'.format(Vcc, Vbatt))
        return abs(Vcc - 3.3)/3.3 < 0.1 and Vbatt >= 1.8
    check('read_sys_volt', f)

    
    ser.write('red_led_on'.encode())
    time.sleep(0.2)
    ser.write('red_led_off'.encode())
    
    ser.write('green_led_on'.encode())
    time.sleep(0.2)
    ser.write('green_led_off'.encode())
    
    ser.write('blue_led_on'.encode())
    time.sleep(0.2)
    ser.write('blue_led_off'.encode())

