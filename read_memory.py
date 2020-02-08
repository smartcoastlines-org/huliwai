# Extract data from logger into a CSV and a binary file.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import time, logging, sys, json
from os import makedirs
from os.path import join, exists
from serial import Serial
from serial.serialutil import SerialException
from common import SPI_FLASH_SIZE_BYTE, SPI_FLASH_PAGE_SIZE_BYTE, SAMPLE_INTERVAL_CODE_MAP,\
     is_logging, stop_logging, get_logging_config, read_vbatt, get_logger_name, get_flash_id, read_range_core,\
     InvalidResponseException
from bin2csv import bin2csv


logging.basicConfig(level=logging.WARNING)


# Read memory range (in byte) from here...
BEGIN = 0
# ... to here
END = SPI_FLASH_SIZE_BYTE - 1
# Request this many bytes each time
# The response will be 4-byte longer (CRC32 at the end of the response)
CHUNK_SIZE = 16*SPI_FLASH_PAGE_SIZE_BYTE
# Stop reading if the response is all empty (0xff for NOR flash)
STOP_ON_EMPTY = True


def split_range(begin, end, pkt_size):
    assert end >= begin
    A = tuple(range(begin, end, pkt_size))
    B = [x + pkt_size - 1 for x in A]
    return list(zip(A, B))


if '__main__' == __name__:

    # find the serial port to use from user, from history, or make a guess
    # if on Windows, print the list of COM ports
    from common import serial_port_best_guess, save_default_port
    
    DEFAULT_PORT = serial_port_best_guess(prompt=True)
    PORT = input('PORT=? (default={}):'.format(DEFAULT_PORT)).strip()
    # empty input, use default
    if '' == PORT:
        PORT = DEFAULT_PORT

    with Serial(PORT, 115200, timeout=2) as ser:

        save_default_port(PORT)

        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(b'\n\n\n')

        stop_logging_time = None

        if is_logging(ser):
            r = input('Logger is still logging. Stop logging? (yes/no; default=no)')
            if r.strip().lower() == 'yes':
                if not stop_logging(ser):
                    print('Could not stop logger. Terminating.')
                    sys.exit()

                stop_logging_time = time.time()
            else:
                print('No change made. Terminating.')
                sys.exit()

        try:
            logger_name = get_logger_name(ser)
            print('Name: {}'.format(logger_name))
            flash_id = get_flash_id(ser)
            print('ID: {}'.format(flash_id))
        except InvalidResponseException:
            print('Cannot read logger name/ID. Terminating.')
            sys.exit()

        makedirs(join('data', flash_id), exist_ok=True)

        # An existing .config file is not required to generate the final CSV, but there are
        # a few things like vbatt_pre that I want to preserve if it's there.
        metadata = get_logging_config(ser)
        logging.debug(metadata)

        configfilename = '{}_{}.config'.format(flash_id, metadata['logging_start_time'])
        configfilename = join('data', flash_id, configfilename)
        config = {}
        if exists(configfilename):
            config = json.loads(open(configfilename).read())
        else:
            logging.warning('No existing config file.')
        config['logger_name'] = logger_name
        config['flash_id'] = flash_id
        config['logging_start_time'] = metadata['logging_start_time']
        config['logging_stop_time'] = metadata['logging_stop_time']
        config['logging_interval_code'] = metadata['logging_interval_code']
        if stop_logging_time is not None:
            config['stop_logging_time'] = stop_logging_time
        else:
            if 'stop_logging_time' in config:
                del config['stop_logging_time']     # remove old record if any
        config['vbatt_post'] = read_vbatt(ser)
        logging.debug(config)
        open(configfilename, 'w').write(json.dumps(config, separators=(',', ':')))

        print('Sample interval = {} second'.format(SAMPLE_INTERVAL_CODE_MAP[config['logging_interval_code']]))

        fn_bin = '{}_{}.bin'.format(flash_id, metadata['logging_start_time'])
        fn_bin = join('data', flash_id, fn_bin)
        if exists(fn_bin):
            r = input(fn_bin + ' already exists. Overwrite? (yes/no; default=no)')
            if r.strip().lower() != 'yes':
                print('No change made. Terminating.')
                sys.exit()

        starttime = time.time()
        with open(fn_bin, 'wb') as fout:
            for begin, end in split_range(BEGIN, END, CHUNK_SIZE):
                print('Reading {:X} to {:X} ({:.2f}% of total capacity)'.format(begin, end, end/SPI_FLASH_SIZE_BYTE*100))
                line = read_range_core(ser, begin, end)
                if len(line) <= 0:
                    raise RuntimeError('wut?')
                if STOP_ON_EMPTY and all([0xFF == b for b in line]):
                    print('Reached empty section in memory. Terminating.')
                    break
                fout.write(line)
        endtime = time.time()

    # - - - - -
    fn_csv = fn_bin.rsplit('.')[0] + '.csv'
    bin2csv(fn_bin, fn_csv, config)
    print('Output CSV file: {}'.format(fn_csv))
    print('Output binary file: {}'.format(fn_bin))
    print('Took {:.1f} minutes.'.format((endtime - starttime)/60))
    print('Save/copy this, you will need it if you want to run plot_csv.py: {}'.format(flash_id))
    
