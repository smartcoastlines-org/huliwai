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
        return t > 20 and t < 40
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


    # not foolproof, but takes little work.
    C = ['red', 'green', 'blue']
    good = True
    for k,c in enumerate(C):
        ser.write('{}_led_on'.format(c).encode())
        time.sleep(0.1)
        ser.write(b'read_rgbw')
        a = float(ser.readline().decode().strip().split(',')[k])
        ser.write('{}_led_off'.format(c).encode())
        time.sleep(0.1)
        ser.write(b'read_rgbw')
        b = float(ser.readline().decode().strip().split(',')[k])
        good &= a > 1.1*b
    print('PASS' if good else 'FAIL! (rgb)')
    

    ser.write(b'red_led_on')
    ser.write(b'green_led_on')
    ser.write(b'blue_led_on')
    time.sleep(0.1)
    ser.write(b'read_ambient_lx')
    a = float(ser.readline().decode().strip().split(',')[0].split(' ')[0])
    ser.write(b'red_led_off')
    ser.write(b'green_led_off')
    ser.write(b'blue_led_off')
    time.sleep(0.1)
    ser.write(b'read_ambient_lx')
    b = float(ser.readline().decode().strip().split(',')[0].split(' ')[0])
    print('PASS' if a > 1.1*b else 'FAIL! (ambient light)')


    '''ser.write(b'clear_memory')
    for _ in range(200):
        time.sleep(0.1)
        r = ser.readline().decode().strip()
        if len(r):
            print(r, end='')
        else:
            break'''


    ser.write(b'set_logging_interval0\n')
    time.sleep(0.5)
    ser.write(b'start_logging')
    for _ in range(5):
        ser.write(b'is_logging')
        if not ser.readline().decode().strip().startswith('1'):
            print('FAIL! (start_logging)')
            break
        time.sleep(1)
    ser.write(b'stop_logging')
    print('PASS')    
