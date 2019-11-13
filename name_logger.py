# Give the logger a name.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import sys, time, logging
from serial import Serial
from common import get_logger_name, get_flash_id, is_logging, stop_logging, InvalidResponseException


logging.basicConfig(level=logging.WARNING)


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

    try:
        if is_logging(ser):
            r = input('Cannot rename logger while it is running. Stop it? (yes/no; default=no)')
            if 'yes' == r.strip():
                stop_logging(ser)
            else:
                print('Terminating.')
                sys.exit()
    except InvalidResponseException:
        print('No response from logger. Terminating.')
        sys.exit()

    try:
        name = get_logger_name(ser)
        flash_id = get_flash_id(ser)
        
        print('Current logger name: {} (ID={})'.format(name, flash_id))
    except UnicodeDecodeError:
        pass

    name = ''
    while True:
        newname = input('Enter new name (max. 15 characters): ')
        if len(newname) <= 15:
            break

    cool = False
    for i in range(10):
        ser.write('set_logger_name{}\n'.format(newname).encode())
        time.sleep(0.5)
        tmp = get_logger_name(ser)
        if newname == tmp:
            cool = True
            break

    if cool:    
        print('Logger name set to "{}"'.format(tmp))
    else:
        print('Could not rename logger. Terminating.')
        sys.exit()
    
