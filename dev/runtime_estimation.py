# Storage capacity and run time calculation.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# MESH Lab
# University of Hawaii
import math

SPI_FLASH_SIZE_BYTE = 16*1024*1024
SPI_FLASH_PAGE_SIZE_BYTE = 256

SPI_FLASH_PAGE_COUNT = SPI_FLASH_SIZE_BYTE/SPI_FLASH_PAGE_SIZE_BYTE

#SAMPLE_PER_SECOND = 1/60
SAMPLE_PER_SECOND = 5


# No timestamp
sample_size_byte = 2*4 + 6*2
sample_per_page = SPI_FLASH_PAGE_SIZE_BYTE//sample_size_byte
leftover_byte = SPI_FLASH_PAGE_SIZE_BYTE - sample_per_page*sample_size_byte
sample_count = SPI_FLASH_PAGE_COUNT*sample_per_page

print('No timestamp:')
print('Sample size = {} byte'.format(sample_size_byte))
print('{} samples per page'.format(sample_per_page))
print('Capacity = {} samples'.format(int(math.floor(sample_count))))
print('{} leftover bytes per page ({:.1f}% waste)'.format(leftover_byte, leftover_byte/SPI_FLASH_PAGE_SIZE_BYTE*100))
print('Time span = {:.1f} hours at {} Hz'.format(sample_count/SAMPLE_PER_SECOND/3600, SAMPLE_PER_SECOND))
# log(786432)/log(2)... so needs 20 bits to index all samples

print()


# With uint32_t timestamp
sample_size_byte = 3*4 + 6*2
sample_per_page = SPI_FLASH_PAGE_SIZE_BYTE//sample_size_byte
leftover_byte = SPI_FLASH_PAGE_SIZE_BYTE - sample_per_page*sample_size_byte
sample_count = SPI_FLASH_PAGE_COUNT*sample_per_page

print('With uint32_t timestamp:')
print('Sample size = {} byte'.format(sample_size_byte))
print('{} samples per page'.format(sample_per_page))
print('Capacity = {} samples'.format(int(math.floor(sample_count))))
print('{} leftover bytes per page ({:.1f}% waste)'.format(leftover_byte, leftover_byte/SPI_FLASH_PAGE_SIZE_BYTE*100))
print('Time span = {:.1f} hours at {} Hz'.format(sample_count/SAMPLE_PER_SECOND/3600, SAMPLE_PER_SECOND))


# 655360... that's not a lot of samples...
