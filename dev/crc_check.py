# CRC calculation stuff.
#
# MESH Lab
# University of Hawaii
# Copyright 2018 Stanley H.I. Lio
# hlio@hawaii.edu
import struct, binascii
from serial import Serial


def check_page(buf):
    SPI_FLASH_PAGE_SIZE = 256
    expected = binascii.crc32(buf[:SPI_FLASH_PAGE_SIZE-4])
    actual = int.from_bytes(buf[SPI_FLASH_PAGE_SIZE-4:], byteorder='big')
    return actual == expected

def check_response(r):
    expected = binascii.crc32(r[:len(r) - 4])
    actual = int.from_bytes(r[len(r) - 4:], byteorder='little')
    return actual == expected
    

if '__main__' == __name__:

    with Serial('COM4', 115200, timeout=1) as ser:

        startaddr = 0
        endaddr = 0xFF

        ser.write('read_page{:x},{:x}\n'.format(startaddr, endaddr).encode())
        r = ser.read(endaddr - startaddr + 1)

        #print(len(r))
        #print(r)
        #print(binascii.crc32(r))
        #print(binascii.crc32(r[:256-4]))
        #print(int.from_bytes(r[256-4:], byteorder='big'))
        print(check_page(r))
