#
# Metadata:
# logger_name:              Logger's name given by user (maximum 15 characters).
# flash_id:                 Logger's unique hardware ID.
# logging_start_time:       Logger's RTC time when logging started. Recorded in EEPROM by logger.
# logging_stop_time:        Logger's RTC time when logging stopped. Recorded in EEPROM by logger. Read as 0 if logger is running, or if logging was stopped abnormally (power outage, reset).
# logging_interval_code:    Code representing sampling interval. A numeric code used internally by the firmware.
# start_logging_time:       User's computer time when logging started.
# stop_logging_time:        User's computer time if and when logging is stopped by user (absent if logger wasn't logging).
#
# interval codes: 0: 0.2s, 1: 1s, 2: 60s
#
# MESH Lab
# University of Hawaii
# Copyright 2018 Stanley H.I. Lio
# hlio@hawaii.edu
import logging, random, time, string, calendar
from datetime import datetime


SAMPLE_INTERVAL_CODE_MAP = {0:1/5, 1:1, 2:60}
# W25Q128JV: 128Mb, or 16MB. 65536 of 256-byte pages. Min. erase size = 1 sector = 16 pages (4096 bytes)
SPI_FLASH_SIZE_BYTE = 16*1024*1024
SPI_FLASH_PAGE_SIZE_BYTE = 256
SAMPLE_SIZE = 20    # size of one sample in byte

class InvalidResponseException(Exception):
    pass


def dt2ts(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return calendar.timegm(dt.timetuple()) + (dt.microsecond)*(1e-6)

def ts2dt(ts=None):
    if ts is None:
        ts = dt2ts()
    return datetime.utcfromtimestamp(ts)


def is_logging(ser, maxretry=10):
    logging.debug('is_logging()')
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    for i in range(maxretry):
        try:
            if i > 0:
                logging.debug('is_logging(): retrying...')
            ser.write(b'is_logging')
            #ser.reset_output_buffer()
            r = ser.readline()
            logging.debug(r)
            r = r.decode().strip().split(',')
            if len(r) == 3 and r[0] in ['0', '1']:
                return '1' == r[0]
        except (UnicodeDecodeError, IndexError, TypeError, ValueError):
            logging.debug(r)
        time.sleep(random.randint(0, 90)/100)

    raise InvalidResponseException('Invalid/no response from logger')


def stop_logging(ser, maxretry=10):
    logging.debug('stop_logging()')
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    stopped = False
    for i in range(maxretry):
        if i > 0:
            logging.debug('stop_logging(): retrying...')
        ser.write(b'stop_logging')
        time.sleep(random.randint(0, 90)/100)
        
        if not is_logging(ser):
            stopped = True
            break

    return stopped


def probably_empty(ser, maxretry=5):
    logging.debug('probably_empty()')
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    for i in range(maxretry):
        ser.write(b'is_logging')
        line = ser.readline().decode().strip()
        try:
            r = line.split(',')
            if 3 != len(r):
                continue
            if not ('0' == r[1]) and ('0' == r[2]):
                logging.debug('probably_empty(): memory indices not clean')
                return False
            else:
                break
        except IndexError:
            raise InvalidResponseException('Invalid/no response from logger: ' + line)
    
    for i in range(maxretry):
        ser.write(b'spi_flash_read_range0,ff\n')
        r = ser.readline()
        if 256+4 == len(r):
            if all([0xFF == rr for rr in r[:-4]]):
                #ser.reset_input_buffer()
                ser.readline()
                return True
            else:
                #ser.reset_input_buffer()
                ser.readline()
                return False
        else:
            #ser.reset_input_buffer()
            #ser.readline()
            pass

    ser.readline()
    return False


def get_logging_config(ser, maxretry=10):
    logging.debug('get_logger_config()')
    tags = ['logging_start_time', 'logging_stop_time', 'logging_interval_code', 'current_page_addr', 'byte_index_within_page']
    
    for i in range(maxretry):
        ser.write(b'get_logging_config')
        try:
            r = ser.readline().decode().strip().split(',')
            logging.debug(r)
            if len(r) >= 3:  # ... isn't there any simple self-descriptive format? or an ultra-intelligent parser?
                return dict(zip(tags, [int(tmp) for tmp in r]))
        except:
            logging.exception('')
        time.sleep(random.randint(0, 50)/100)
    raise InvalidResponseException('Invalid/no response from logger')


def read_vbatt(ser, maxretry=10):
    logging.debug('read_vbatt()')
    
    for i in range(maxretry):
        try:
            ser.write(b'read_sys_volt')
            r = ser.readline().decode().strip().split(',')
            logging.debug(r)
            return round(float(r[1]), 2)
        except (UnicodeDecodeError, ValueError, IndexError):
            logging.exception('')
    raise InvalidResponseException('Invalid/no response from logger')


def get_logger_name(ser, maxretry=10):
    logging.debug('get_logger_name()')
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # there's no easy way to tell whether the name is not set, the logger is not responding, or those gibberish characters really is the name
    # without proper framing and checksum in storage and in comm, any check you do here is just heuristics/guess/hack

    for i in range(maxretry):
        ser.write(b'get_logger_name')
        try:
            r = ser.readline()
            if all(['\xff' == c for c in r[:-1]]):
                # name is not set
                logging.debug('name has not been set')
                return ''
            r = r.decode().strip()
            logging.debug(r)
            if len(r) <= 0:
                logging.debug('No response...')
                time.sleep(random.randint(0, 200)/1000)
                continue
            return r
        except UnicodeDecodeError:      # the name is probably not set
            time.sleep(random.randint(0, 200)/1000)
            continue
    #raise InvalidResponseException('Invalid/no response from logger')
    return ''


def get_flash_id(ser, maxretry=10):
    logging.debug('get_flash_id()')
    ser.flushInput()
    ser.flushOutput()
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    for i in range(maxretry):
        ser.write(b'spi_flash_get_unique_id')
        try:
            r = ser.readline().decode().strip()
            if len(r) <= 0:
                continue
            logging.debug(r)
            if 16 == len(r) and r.startswith('E') and all([c in string.hexdigits for c in r]):
                #ser.reset_input_buffer()
                #ser.readline()
                return r
        except UnicodeDecodeError:
            pass
        time.sleep(random.randint(0, 50)/100)
    raise InvalidResponseException('Invalid/no response from logger: ' + r)


def get_metadata(ser, maxretry=10):
    flash_id = get_flash_id(ser, maxretry)
    logger_name = get_logger_name(ser, maxretry)
    running = is_logging(ser)
    metadata = get_logging_config(ser, maxretry)
    
    config = {}
    config['flash_id'] = flash_id
    config['logger_name'] = logger_name
    config['is_logging'] = running
    config['logging_start_time'] = metadata['logging_start_time']
    config['logging_stop_time'] = metadata['logging_stop_time']
    config['logging_interval_code'] = metadata['logging_interval_code']

    return config

def list_serial_port():
    """ doesn't work on the pi. it doesn't show /dev/ttyS0"""
    import serial.tools.list_ports
    return sorted(serial.tools.list_ports.comports(), key=lambda c: int(c.device.replace('COM', '')))

def serial_port_best_guess(prompt=False):
    import platform, glob, json
    import serial.tools.list_ports
    from os.path import exists, join, dirname

    P = platform.system()

    if 'Windows' in P:
        L = list_serial_port()
        if prompt:
            for c in L:
                print(c.description)

    # see if there's any hint
    try:
        fn = join(dirname(__file__), 'saw.tmp')
        if exists(fn):
            port = json.load(open(fn))['serialport']
            if 'Windows' in P:
                if port.lower() in [c.device.lower() for c in serial.tools.list_ports.comports()]:
                    return port
            else:
                if exists(port):
                    return port
    except Exception as e:
        logging.debug(e)

    # for whatever reason, no hint on which serial port to use
    if 'Windows' in P:
        return L[-1].device
    else:
        # cu.usbserial########
        # tty.usbserial########
        # tty.usbmodem########

        if exists('/dev'):
            L = glob.glob('/dev/ttyUSB*')       # mac, or pi with adapter
            if len(L):
                return L[-1]

            L = glob.glob('/dev/*usbserial*')   # still mac
            if len(L):
                return L[-1]

            L = glob.glob('/dev/*usbmodem*')       # mac again
            if '.' in L:
                return L[-1]

    return '/dev/ttyS0'

def save_default_port(port):
    import json
    from os.path import exists, join, dirname
    fn = join(dirname(__file__), 'saw.tmp')
    if exists(fn):
        config = json.load(open(fn))
    else:
        config = {}
    config['serialport'] = port
    json.dump(config, open(fn, 'w'))


if '__main__' == __name__:
    
    import logging
    from serial import Serial

    print(serial_port_best_guess())

    logging.basicConfig(level=logging.DEBUG)

    DEFAULT_PORT = '/dev/ttyS0'
    PORT = input('PORT=? (default={})'.format(DEFAULT_PORT)).strip()
    if '' == PORT:
        PORT = DEFAULT_PORT

    with Serial(PORT, 115200, timeout=1) as ser:
        print(get_logger_name(ser))
        print(is_logging(ser))
        print(read_vbatt(ser))
        print(probably_empty(ser))
        print(get_logging_config(ser))
    
