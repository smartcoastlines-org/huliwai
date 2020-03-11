# Start a new logging session.
#
# If logger is already running, it offers the option to stop it first.
# If logger memory is not empty, it won't start a new session unless it's wiped.
# If logger memory is empty, it no longer prompt for wiping memory.
# It sets the logger's clock before logging.
#
# TODO:
#   get calibration eeprom
#
# Possible intervals: 0.2s, 1s, 60s
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import time, json, sys, logging
from os import makedirs
from os.path import join, exists
from serial import Serial
from serial.serialutil import SerialException
from dev.set_rtc import set_rtc_aligned, read_rtc, ts2dt
from common import is_logging, stop_logging, find_last_used_page, get_logging_config, read_vbatt, get_flash_id, get_logger_name, InvalidResponseException, SAMPLE_INTERVAL_CODE_MAP


logging.basicConfig(level=logging.WARNING)


MAX_RETRY = 10

# find the serial port to use from user, from history, or make a guess
# if on Windows, print the list of COM ports
from common import serial_port_best_guess, save_default_port
print('Detected ports:')
DEFAULT_PORT = serial_port_best_guess(prompt=True)
print('- - -')
PORT = input('PORT=? (default={})'.format(DEFAULT_PORT)).strip()
# empty input, use default
if '' == PORT:
    PORT = DEFAULT_PORT

with Serial(PORT, 115200, timeout=1) as ser:

    try:
        logger_name = get_logger_name(ser)
        flash_id = get_flash_id(ser)
        vbatt = read_vbatt(ser)
        print('Logger "{}" (ID={})'.format(logger_name, flash_id))
        print('Battery voltage: {:.1f} V'.format(vbatt))
        if vbatt < 2.2:
            print('WARNING: Battery voltage is low.')
    except InvalidResponseException:
        logging.error('Cannot find logger. ABORT.')
        sys.exit()

    save_default_port(PORT)

    # Stop logging if necessary
    logging.debug('Stop ongoing logging if necessary...')
    try:
        if is_logging(ser):
            r = input('Logger is already logging. Stop it first? (yes/no; DEFAULT=no)')
            if r.strip().lower() in ['yes']:
                if not stop_logging(ser, maxretry=20):
                    logging.error('Logger is still logging and is not responding to stop_logging. Terminating.')
                    sys.exit()
            else:
                print('Logger must be stopped before it can be restarted. ABORT.')
                sys.exit()
    except InvalidResponseException:
        logging.error('Cannot verify logger status. Terminating.')
        sys.exit()

    # Verify that it is indeed not logging
    assert not is_logging(ser)


    # Turn off LEDs
    ser.write(b'red_led_off green_led_off blue_led_off')


    # Set RTC to current UTC time
    print('Setting logger clock to current UTC time...', flush=True)
    for i in range(MAX_RETRY):
        device_time = set_rtc_aligned(ser)
        if abs(device_time - time.time()) <= 2:
            break
    else:
        print('Cannot set logger clock. Terminating.')
        sys.exit()
    print('Logger time in UTC: {}'.format(ts2dt(device_time)))
    

    # Set sample interval
    while True:
        print('Pick a sampling interval (subject to battery capacity constraint):\n  A. 0.2 second (~43 hours)\n  B. 1 second (~9 days; default)\n  C. 60 seconds (~530 days)')
        r = input('Your choice: ')
        r = r.strip().lower()
        if r in ['a', 'b', 'c', '']:
            if '' == r:
                r = 'b'
            break
    # a numeric code, not in real time unit
    # check the C definitions for the code-to-second mapping
    # internally, logger uses {0,1,2...}
    logging_interval_code = int(ord(r) - ord('a'))
    assert logging_interval_code in SAMPLE_INTERVAL_CODE_MAP

    for i in range(MAX_RETRY):
        ser.write('set_logging_interval{}\n'.format(logging_interval_code).encode())
        c = get_logging_config(ser)
        if c['logging_interval_code'] == logging_interval_code:
            break
    else:
        print('Could not set sampling interval. ABORT.')
        sys.exit()


    # Check if memory is empty

    is_memory_empty = find_last_used_page(ser) is None

    if not is_memory_empty:
        print('Memory is not empty.')
        while True:
            r = input('Wipe memory? (yes/no; default=no)')
            if r.strip().lower() in ['', 'yes', 'no']:
                break
        if r.strip().lower() in ['yes']:
            logging.debug('User wants to wipe memory.')
            ser.write(b'clear_memory')
            THRESHOLD = 10
            cool = THRESHOLD
            while cool > 0:
                try:
                    line = ser.read(100)
                    logging.debug(line)
                    if not all([ord(b'.') == tmp for tmp in line]):
                        logging.debug('Not cool')
                        cool -= 1
                    else:
                        logging.debug('cool')
                        cool = THRESHOLD

                    print(line.decode(), end='', flush=True)
                    if 'done.' in line.decode():
                        break
                except UnicodeDecodeError:
                    pass

            if cool <= 0:
                print('Logger is not responding to clear_memory. ABORT.')
                sys.exit()
        else:
            # anything else is considered a NO (don't wipe).
            print('Logger cannot start if memory is not empty. ABORT.')
            sys.exit()
        
    # TODO: should store run number in logger so stop script can correlate start and stop configs
    # Basically a UUID for every logging session

    print('Attempting to start logging...')
    for i in range(MAX_RETRY):
        ser.write(b'start_logging')
        time.sleep(0.1)
        if is_logging(ser):
            break
        else:
            logging.debug('... still not logging...')
    else:
        print('Logger refuses to start. ABORT.')
        sys.exit()

    print('Logger is running.')

    # Record config and meta
    tmp = get_logging_config(ser)
    logging_start_time = tmp['logging_start_time']
    
    config = {'start_logging_time':time.time(),
              'flash_id':flash_id,
              'logger_name':logger_name,
              'logging_start_time': logging_start_time,
              'logging_interval_code': logging_interval_code,
              'vbatt_pre': read_vbatt(ser),
              }
    
    config = json.dumps(config, separators=(',',':'))
    logging.debug(config)
    
    fn = join('data', flash_id)
    if not exists(fn):
        makedirs(fn)
    fn = join(fn, '{}_{}.config'.format(flash_id, logging_start_time))
    open(fn, 'w', 1).write(config)
    print('Config file saved to {}'.format(fn))
