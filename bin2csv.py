# Convert a flash dump (.bin) file to a CSV file.
#
# Data are taken from "[ID].bin"
# Timestamps are reconstructed from the config file "[ID].config"
# Output will be named "[ID].csv"
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import struct, math, sys, csv, json, logging
from datetime import datetime
from glob import glob
from os.path import join, exists, basename, isdir, isfile
from common import SPI_FLASH_PAGE_SIZE_BYTE, SAMPLE_INTERVAL_CODE_MAP, SAMPLE_SIZE_BYTE, ts2dt, dt2ts


def find(pattern, *_, dironly=False, fileonly=False, default=None):
    FN = sorted(glob(pattern))
    if dironly:
        FN = list(filter(lambda x: isdir(x), FN))
    if fileonly:
        FN = list(filter(lambda x: isfile(x), FN))

    if len(FN) == 0:
        logging.debug('No file/folder fits the criteria.')
        return None
    elif len(FN) == 1:
        logging.debug('Only one file/folder fits the criteria.')
        return FN[0]
    else:
        while True:
            for k,v in enumerate(FN, start=1):
                print('{}.\t{}'.format(k,v))

            if default:
                r = input('Your choice (default=last): ').strip().upper()
            else:
                r = input('Your choice: ').strip().upper()

            if 'last' == default:
                if len(r.strip()) <= 0 and len(FN) > 0:
                    return FN[-1]
                #yeah that only makes sense for .bin. Not for logger selection.

            if r not in [str(v) for v in range(1, len(FN) + 1)]:
                #r = input('Not an option. Give me the ID instead:')
                print('Not an option. I\'ll take that as part of the ID.')
                tmp = list(filter(lambda x: r in x, FN))
                if len(tmp):
                    FN = tmp
                    if 1 == len(FN):
                        return FN[0]
                else:
                    print('That\'s not in any of the remaining IDs.')
            else:
                return FN[int(r) - 1]

def construct_timestamp(logging_start_time, sample_count, interval_second):
    ts = list(range(0, sample_count))
    return [x*interval_second + logging_start_time for x in ts]

def bin2csv(fn_bin, fn_csv, config):
    logging.debug('Reading and parsing binary file...')
    D = []
    with open(fn_bin, 'rb') as fin:
        while True:
            page = fin.read(SPI_FLASH_PAGE_SIZE_BYTE)
            if len(page) < SPI_FLASH_PAGE_SIZE_BYTE:
                break

            L = list(range(0, SPI_FLASH_PAGE_SIZE_BYTE, SAMPLE_SIZE_BYTE))
            for a,b in list(zip(L[::], L[1::])):
                d = struct.unpack('ffHHHHHH', page[a:b])
                if any([math.isnan(dd) for dd in d]):
                    break
                D.append(d)

    logging.debug('Reconstructing time axis...')
    ts = construct_timestamp(config['logging_start_time'], len(D), SAMPLE_INTERVAL_CODE_MAP[config['logging_interval_code']])
    dt = [ts2dt(tmp) for tmp in ts]
    tmp = list(zip(*D))
    tmp.insert(0, ts)
    tmp.insert(0, dt)
    D = zip(*tmp)

    logging.debug('Writing to {}...'.format(fn_csv))
    with open(fn_csv, 'w', newline='') as fout:
        writer = csv.writer(fout, delimiter=',')
        fs = [str, str, lambda x: '{:.4f}'.format(x), lambda x: '{:.3f}'.format(x), str, str, str, str, str, str]
        writer.writerow(['UTC_datetime', 'posix_timestamp', 'T_DegC', 'P_kPa', 'ambient_light_hdr', 'white_light_hdr', 'red', 'green', 'blue', 'white'])
        for d in D:
            #writer.writerow([str(x) for x in d])
            writer.writerow([f(x) for f,x in zip(fs, d)])
    

if '__main__' == __name__:

    logging.basicConfig(level=logging.WARNING)

    while True:
        d = find('data/*', dironly=True)
        if d is None:
            print('No data file found. Terminating.')
            sys.exit()
        binfilename = find(join(d, '*.bin'), fileonly=True, default='last')
        if binfilename is None:
            print('No binary file found in {}. Pick another or Ctrl + C to terminate.'.format(d))
        else:
            logging.debug(binfilename)
            break
    
    #binfilename = input('Input path to binary file: ').strip()
    configfilename = binfilename.rsplit('.')[0] + '.config'
    outputfilename = configfilename.rsplit('.')[0] + '.csv'
    assert exists(binfilename)
    assert exists(configfilename)
    print('Data file: {}'.format(binfilename))
    print('Configuration file: {}'.format(configfilename))
    config = json.loads(open(configfilename).read())

    bin2csv(binfilename, outputfilename, config)

    print('Done.')
