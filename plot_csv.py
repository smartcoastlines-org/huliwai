# Plot a CSV file given a logger's unique ID.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESHLAB, UH Manoa
import struct, math, sys, csv, logging, json
from os.path import join, exists
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
#from scipy.stats import describe
from bin2csv import find
from common import ts2dt, dt2ts


def get_logger_name(fn):
    # find the name of the logger, if possible
    logger_name = None
    configfilename = fn.split('.')[0] + '.config'
    if exists(configfilename):
        logging.debug('Found config file {}'.format(configfilename))
        config = json.load(open(configfilename))
        logger_name = config.get('logger_name', None)
    return logger_name


def read_and_parse_data(fn):
    
    # Cory wants a human time column
    line = open(fn).readline().split(',')
    has_human_time = 10 == len(line)

    D = []
    for line in open(fn):
        try:        # ignore parse error, effectively skipping header, if any
            if has_human_time:
                D.append([float(x) for x in line.split(',')[1:]])   # ignore the first column
            else:
                D.append([float(x) for x in line.split(',')])
        except ValueError:
            pass
    return zip(*D)


if '__main__' == __name__:

    logging.basicConfig(level=logging.WARNING)

    #fn = UNIQUE_ID + '.csv'
    #fn = input('Path to the CSV file: ').strip()

    d = find('data/*', dironly=True)
    fn = find(join(d, '*.csv'), fileonly=True, default='last')
    if fn is None:
        print('No CSV file found. Have you run bin2csv.py? Terminating.')
        sys.exit()

    logger_name = get_logger_name(fn)

    ts, t,p, als,white, r,g,b,w = read_and_parse_data(fn)
    begin, end = ts2dt(min(ts)), ts2dt(max(ts))
    print('{} samples from {} to {} spanning {}, average interval {:.3}s'.format(
        len(ts),
        begin,
        end,
        end - begin,
        np.mean(np.diff(ts))))

    # - - -

    #print(describe(p))

    # also PSD... TODO

    '''print('Calculating Temperature statistics...')
    plt.figure(figsize=(16, 9))

    ax = plt.subplot(211)
    ax.hist(np.diff(t), color='r', bins='auto')
    if logger_name is not None:
        logger_name = logger_name.strip()
        if len(logger_name):
            ax.set_title('Step Size Distribution (Temperature; "{}")'.format(logger_name))
    else:
        ax.set_title('Step Size Distribution (Temperature)')
    ax.set_xlabel('Deg.C')
    ax.set_ylabel('(count)')
    ax.grid(True)

    print('Calculating Pressure statistics...')
    ax = plt.subplot(212)
    ax.hist(np.diff(p), bins='auto')
    if logger_name is not None:
        logger_name = logger_name.strip()
        if len(logger_name):
            ax.set_title('Step Size Distribution (Pressure; "{}")'.format(logger_name))
    else:
        ax.set_title('Step Size Distribution (Pressure)')
    ax.set_xlabel('kPa')
    ax.set_ylabel('(count)')
    ax.grid(True)

    plt.tight_layout()'''


    #print('Step sizes: ', end='')
    #print(sorted(np.unique(tmp)))

    dt = [ts2dt(tmp) for tmp in ts]

    print('Plotting time series...')
    plt.figure(figsize=(16, 9))
    ax1 = plt.subplot(411)
    ax2 = plt.subplot(412, sharex=ax1)
    ax3 = plt.subplot(413, sharex=ax1)
    ax4 = plt.subplot(414, sharex=ax1)
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)

    ax4.set_xlabel('UTC Time')
    
    if logger_name is not None:
        logger_name = logger_name.strip()
        if len(logger_name):
            ax1.set_title(fn + ' ("{}")'.format(logger_name))
    else:
        ax1.set_title(fn)

    ax1.plot_date(dt, t, 'r.:', label='Deg.C')
    ax1.legend(loc=2)
    ax1.grid(True)

    ax2.plot_date(dt, p, '.:', label='kPa')
    ax2.legend(loc=2)
    ax2.grid(True)

    ax3.plot_date(dt, als, '.:', label='als', alpha=0.5)
    ax3.plot_date(dt, white, '.:', label='white', alpha=0.5)
    ax3.legend(loc=2)
    ax3.grid(True)

    ax4.plot_date(dt, r, 'r.:', label='r', alpha=0.5)
    ax4.plot_date(dt, g, 'g.:', label='g', alpha=0.5)
    ax4.plot_date(dt, b, 'b.:', label='b', alpha=0.5)
    ax4.plot_date(dt, w, 'k.:', label='w', alpha=0.2)
    ax4.legend(loc=2)
    ax4.grid(True)

    ax4.xaxis.set_major_formatter(DateFormatter('%b %d %H:%M:%S'))
    plt.tight_layout()
    plt.gcf().autofmt_xdate()

    print('Saving plot to disk...')
    plt.savefig(fn.split('.')[0] + '.png', dpi=300)
    plt.show()
