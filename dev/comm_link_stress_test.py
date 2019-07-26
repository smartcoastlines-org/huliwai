import sys, logging, time, json
from serial import Serial



PORT = 'COM18'


with Serial(PORT, 115200, timeout=1) as ser:
    s = 'read_temperature read_pressure read_ambient_lx read_white_lx read_rgbw get_logger_name spi_flash_get_unique_id read_rtc_time read_sys_volt get_logging_config is_logging\n'
    s = s.split(' ')
    for i in range(200):
        for cmd in s:
            ser.write(cmd.encode())
            #for ss in cmd:
            #    ser.write(ss.encode())
                #print(ss, end='')
                #time.sleep(0.00001)
        
    while True:
        r = ser.read()
        if len(r):
            try:
                print(r.decode(), end='')
            except UnicodeDecodeError:
                logging.error(r)

sys.exit()



with Serial(PORT, 115200, timeout=1) as ser:

    # 625~1250
    # 625~938
    # 625~782
    # 704~782
    # 743~782
    # 763~782 (763, can recover)
    # 773~782 (773, can recover)
    # 782 takes a while to recover

    ser.write(('gibberish'*1000).encode())

    #while True:
    #    ser.write(b'red_led_off red_led_on')

print('done.')
